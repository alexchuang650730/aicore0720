#!/usr/bin/env python3
"""
PowerAutomation 完整數據收集系統
包含 Manus Replay、封閉測試、實時使用數據收集
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import aiohttp
from abc import ABC, abstractmethod
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCollector(ABC):
    """數據收集器基類"""
    
    @abstractmethod
    async def collect(self) -> Dict[str, Any]:
        """收集數據"""
        pass
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理數據"""
        pass
    
    @abstractmethod
    async def save(self, data: Dict[str, Any]) -> str:
        """保存數據"""
        pass


class ManusReplayCollector(DataCollector):
    """Manus Replay 數據收集器"""
    
    def __init__(self, replay_urls: List[str], output_dir: str = "./data/manus_replays"):
        self.replay_urls = replay_urls
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collected_data = []
        
    async def collect(self) -> Dict[str, Any]:
        """批量收集 Manus replay 數據"""
        logger.info(f"開始收集 {len(self.replay_urls)} 個 Manus replays")
        
        # 使用之前創建的 ManusReplayExtractor
        from ..training.manus_replay_extractor import ManusReplayExtractor
        
        extractor = ManusReplayExtractor(str(self.output_dir))
        results = await extractor.process_batch(self.replay_urls)
        
        await extractor.close()
        
        return {
            "source": "manus_replay",
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "data_path": str(self.output_dir)
        }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理收集的數據，準備訓練格式"""
        training_pairs = []
        
        # 讀取提取的訓練數據
        dataset_path = Path(data["data_path"]) / "training_dataset.json"
        if dataset_path.exists():
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
                training_pairs = dataset.get('pairs', [])
        
        # 增強數據質量
        enhanced_pairs = []
        for pair in training_pairs:
            enhanced = self._enhance_training_pair(pair)
            enhanced_pairs.append(enhanced)
        
        return {
            "processed_pairs": len(enhanced_pairs),
            "enhanced_data": enhanced_pairs,
            "quality_distribution": self._analyze_quality_distribution(enhanced_pairs)
        }
    
    def _enhance_training_pair(self, pair: Dict[str, Any]) -> Dict[str, Any]:
        """增強訓練對質量"""
        # 添加 K2 優化提示
        if pair['type'] == 'code_generation':
            pair['k2_optimized_prompt'] = self._create_k2_optimized_prompt(pair['input'])
        
        # 添加思考鏈
        if not pair.get('deepswe_format', {}).get('metadata', {}).get('has_thinking'):
            pair['synthetic_thinking'] = self._generate_synthetic_thinking(pair)
        
        return pair
    
    def _create_k2_optimized_prompt(self, user_input: str) -> str:
        """創建 K2 優化的提示"""
        return f"""<context>
任務類型：代碼生成
優先級：高質量、可維護性
</context>

<thinking>
用戶需求分析：
1. 核心功能需求
2. 技術約束條件
3. 最佳實踐考慮
</thinking>

{user_input}

請確保：
- 代碼遵循最佳實踐
- 包含完整的錯誤處理
- 提供清晰的註釋
- 考慮邊界情況
"""
    
    def _generate_synthetic_thinking(self, pair: Dict[str, Any]) -> str:
        """生成合成的思考過程"""
        task_type = pair['type']
        
        thinking_templates = {
            'code_generation': "需要分析需求的核心功能，選擇合適的技術方案，確保代碼的可維護性。",
            'error_fixing': "首先定位錯誤原因，分析影響範圍，然後設計最小化的修復方案。",
            'optimization': "識別性能瓶頸，評估優化方案的成本效益，保持代碼可讀性。",
            'explanation': "理解代碼的設計意圖，分析實現細節，用清晰的語言解釋。"
        }
        
        return thinking_templates.get(task_type, "分析問題，設計解決方案。")
    
    def _analyze_quality_distribution(self, pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析數據質量分布"""
        quality_scores = [p.get('quality_score', 0) for p in pairs]
        
        return {
            "high_quality": len([s for s in quality_scores if s > 0.8]),
            "medium_quality": len([s for s in quality_scores if 0.5 <= s <= 0.8]),
            "low_quality": len([s for s in quality_scores if s < 0.5]),
            "average_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0
        }
    
    async def save(self, data: Dict[str, Any]) -> str:
        """保存處理後的數據"""
        output_file = self.output_dir / f"processed_manus_data_{int(time.time())}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"數據已保存到: {output_file}")
        return str(output_file)


class BetaTestDataCollector(DataCollector):
    """封閉測試數據收集器"""
    
    def __init__(self, test_users: List[str], collection_endpoint: str):
        self.test_users = test_users
        self.collection_endpoint = collection_endpoint
        self.collected_sessions = []
        
    async def collect(self) -> Dict[str, Any]:
        """收集封閉測試用戶數據"""
        logger.info(f"開始收集 {len(self.test_users)} 個測試用戶的數據")
        
        sessions = []
        for user_id in self.test_users:
            user_sessions = await self._collect_user_sessions(user_id)
            sessions.extend(user_sessions)
        
        return {
            "source": "beta_test",
            "timestamp": datetime.now().isoformat(),
            "user_count": len(self.test_users),
            "session_count": len(sessions),
            "sessions": sessions
        }
    
    async def _collect_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """收集單個用戶的會話數據"""
        # 這裡模擬 API 調用
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.collection_endpoint}/users/{user_id}/sessions",
                    headers={"Authorization": "Bearer YOUR_API_KEY"}
                ) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception as e:
                logger.error(f"收集用戶 {user_id} 數據失敗: {e}")
        
        return []
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理測試用戶數據"""
        sessions = data.get('sessions', [])
        
        # 提取有價值的交互
        valuable_interactions = []
        for session in sessions:
            interactions = self._extract_valuable_interactions(session)
            valuable_interactions.extend(interactions)
        
        # 分析使用模式
        usage_patterns = self._analyze_usage_patterns(sessions)
        
        return {
            "processed_sessions": len(sessions),
            "valuable_interactions": len(valuable_interactions),
            "interactions": valuable_interactions,
            "usage_patterns": usage_patterns
        }
    
    def _extract_valuable_interactions(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取有價值的交互"""
        interactions = []
        messages = session.get('messages', [])
        
        for i in range(len(messages) - 1):
            if messages[i]['role'] == 'user' and messages[i + 1]['role'] == 'assistant':
                # 評估交互價值
                value_score = self._evaluate_interaction_value(
                    messages[i]['content'],
                    messages[i + 1]['content']
                )
                
                if value_score > 0.6:  # 高價值閾值
                    interactions.append({
                        'user_input': messages[i]['content'],
                        'assistant_output': messages[i + 1]['content'],
                        'value_score': value_score,
                        'user_feedback': session.get('feedback', {}),
                        'session_metadata': {
                            'duration': session.get('duration'),
                            'success': session.get('success', True)
                        }
                    })
        
        return interactions
    
    def _evaluate_interaction_value(self, user_input: str, assistant_output: str) -> float:
        """評估交互的訓練價值"""
        score = 0.5
        
        # 長度適中
        if 50 < len(user_input) < 500 and 100 < len(assistant_output) < 2000:
            score += 0.1
        
        # 包含代碼
        if '```' in assistant_output:
            score += 0.2
        
        # 有具體需求
        if any(keyword in user_input for keyword in ['實現', '創建', '修復', '優化']):
            score += 0.1
        
        # 有詳細解釋
        if len(assistant_output.split('\n')) > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _analyze_usage_patterns(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析使用模式"""
        total_duration = sum(s.get('duration', 0) for s in sessions)
        successful_sessions = len([s for s in sessions if s.get('success', False)])
        
        # 提取常見任務類型
        task_types = {}
        for session in sessions:
            task_type = session.get('task_type', 'unknown')
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        return {
            "total_duration_hours": total_duration / 3600,
            "success_rate": successful_sessions / len(sessions) if sessions else 0,
            "common_tasks": sorted(task_types.items(), key=lambda x: x[1], reverse=True)[:5],
            "average_session_duration": total_duration / len(sessions) if sessions else 0
        }
    
    async def save(self, data: Dict[str, Any]) -> str:
        """保存處理後的數據"""
        output_dir = Path("./data/beta_test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"beta_test_data_{int(time.time())}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"測試數據已保存到: {output_file}")
        return str(output_file)


class RealTimeUsageCollector(DataCollector):
    """實時使用數據收集器"""
    
    def __init__(self, kafka_config: Optional[Dict[str, Any]] = None):
        self.kafka_config = kafka_config or {}
        self.buffer = []
        self.buffer_size = 100
        
    async def collect(self) -> Dict[str, Any]:
        """實時收集使用數據"""
        # 這裡可以連接到 Kafka、Redis 或其他實時數據流
        logger.info("開始實時數據收集...")
        
        # 模擬實時數據收集
        collected_events = []
        
        # 在實際實現中，這裡會連接到消息隊列
        # async for event in self.kafka_consumer:
        #     collected_events.append(event)
        
        return {
            "source": "realtime",
            "timestamp": datetime.now().isoformat(),
            "event_count": len(collected_events),
            "events": collected_events
        }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理實時數據"""
        events = data.get('events', [])
        
        # 聚合有用的模式
        patterns = self._aggregate_patterns(events)
        
        # 識別異常或有趣的使用案例
        anomalies = self._detect_anomalies(events)
        
        return {
            "processed_events": len(events),
            "patterns": patterns,
            "anomalies": anomalies
        }
    
    def _aggregate_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚合使用模式"""
        # 實現模式識別邏輯
        return {
            "common_workflows": [],
            "error_patterns": [],
            "optimization_opportunities": []
        }
    
    def _detect_anomalies(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """檢測異常使用模式"""
        # 實現異常檢測邏輯
        return []
    
    async def save(self, data: Dict[str, Any]) -> str:
        """保存處理後的數據"""
        output_dir = Path("./data/realtime")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"realtime_data_{int(time.time())}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return str(output_file)


class DataCollectionOrchestrator:
    """數據收集協調器"""
    
    def __init__(self):
        self.collectors = []
        self.collected_data = {}
        self.training_dataset_path = Path("./data/training_dataset")
        self.training_dataset_path.mkdir(parents=True, exist_ok=True)
        
    def add_collector(self, collector: DataCollector):
        """添加數據收集器"""
        self.collectors.append(collector)
        
    async def run_collection(self) -> Dict[str, Any]:
        """運行所有數據收集器"""
        logger.info("🚀 開始完整數據收集流程")
        
        results = {}
        
        for collector in self.collectors:
            collector_name = collector.__class__.__name__
            logger.info(f"運行收集器: {collector_name}")
            
            try:
                # 收集
                raw_data = await collector.collect()
                
                # 處理
                processed_data = await collector.process(raw_data)
                
                # 保存
                saved_path = await collector.save(processed_data)
                
                results[collector_name] = {
                    "status": "success",
                    "raw_data": raw_data,
                    "processed_data": processed_data,
                    "saved_path": saved_path
                }
                
            except Exception as e:
                logger.error(f"收集器 {collector_name} 失敗: {e}")
                results[collector_name] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # 合併所有數據創建統一的訓練數據集
        unified_dataset = await self._create_unified_dataset(results)
        
        return {
            "collection_results": results,
            "unified_dataset": unified_dataset,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _create_unified_dataset(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """創建統一的訓練數據集"""
        all_training_pairs = []
        
        for collector_name, result in results.items():
            if result['status'] == 'success':
                processed_data = result.get('processed_data', {})
                
                # 提取訓練對
                if 'enhanced_data' in processed_data:
                    all_training_pairs.extend(processed_data['enhanced_data'])
                elif 'interactions' in processed_data:
                    all_training_pairs.extend(processed_data['interactions'])
        
        # 去重和質量篩選
        unique_pairs = self._deduplicate_pairs(all_training_pairs)
        high_quality_pairs = [p for p in unique_pairs if p.get('quality_score', 0) > 0.7]
        
        # 創建不同格式的數據集
        datasets = {
            "standard": self._create_standard_dataset(high_quality_pairs),
            "deepswe": self._create_deepswe_dataset(high_quality_pairs),
            "k2_optimized": self._create_k2_optimized_dataset(high_quality_pairs)
        }
        
        # 保存數據集
        for format_name, dataset in datasets.items():
            output_file = self.training_dataset_path / f"unified_{format_name}_dataset.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存 {format_name} 格式數據集: {output_file}")
        
        return {
            "total_pairs": len(all_training_pairs),
            "unique_pairs": len(unique_pairs),
            "high_quality_pairs": len(high_quality_pairs),
            "datasets": {k: len(v['data']) for k, v in datasets.items()},
            "dataset_paths": {k: str(self.training_dataset_path / f"unified_{k}_dataset.json") 
                            for k in datasets.keys()}
        }
    
    def _deduplicate_pairs(self, pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重訓練對"""
        seen = set()
        unique_pairs = []
        
        for pair in pairs:
            # 使用輸入的哈希作為唯一標識
            pair_hash = hashlib.md5(pair.get('input', '').encode()).hexdigest()
            
            if pair_hash not in seen:
                seen.add(pair_hash)
                unique_pairs.append(pair)
        
        return unique_pairs
    
    def _create_standard_dataset(self, pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """創建標準格式數據集"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "format": "standard",
            "data": [
                {
                    "instruction": p.get('input', ''),
                    "output": p.get('output', ''),
                    "metadata": {
                        "source": p.get('source', 'unknown'),
                        "type": p.get('type', 'general'),
                        "quality_score": p.get('quality_score', 0)
                    }
                }
                for p in pairs
            ]
        }
    
    def _create_deepswe_dataset(self, pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """創建 DeepSWE 格式數據集"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "format": "deepswe",
            "data": [
                {
                    "prompt": p.get('deepswe_format', {}).get('prompt', ''),
                    "completion": p.get('deepswe_format', {}).get('completion', ''),
                    "thinking": p.get('synthetic_thinking', ''),
                    "metadata": p.get('deepswe_format', {}).get('metadata', {})
                }
                for p in pairs
                if 'deepswe_format' in p
            ]
        }
    
    def _create_k2_optimized_dataset(self, pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """創建 K2 優化格式數據集"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "format": "k2_optimized",
            "data": [
                {
                    "original_prompt": p.get('input', ''),
                    "optimized_prompt": p.get('k2_optimized_prompt', ''),
                    "expected_output": p.get('output', ''),
                    "optimization_hints": {
                        "task_type": p.get('type', 'general'),
                        "thinking_required": 'thinking' in p.get('output', ''),
                        "code_generation": '```' in p.get('output', '')
                    }
                }
                for p in pairs
                if 'k2_optimized_prompt' in p
            ]
        }


async def main():
    """主函數示例"""
    # 1. 準備 Manus replay URLs（從文件讀取）
    with open('manus_replay_urls.txt', 'r') as f:
        replay_urls = [line.strip() for line in f if line.strip()]
    
    # 2. 準備測試用戶列表
    test_users = [
        "user_001", "user_002", "user_003", # ... 更多測試用戶
    ]
    
    # 3. 創建協調器
    orchestrator = DataCollectionOrchestrator()
    
    # 4. 添加收集器
    orchestrator.add_collector(
        ManusReplayCollector(replay_urls[:100])  # 先處理前 100 個
    )
    
    orchestrator.add_collector(
        BetaTestDataCollector(
            test_users,
            "https://api.powerautomation.ai/v1/data"
        )
    )
    
    orchestrator.add_collector(
        RealTimeUsageCollector()
    )
    
    # 5. 運行收集
    results = await orchestrator.run_collection()
    
    # 6. 輸出結果
    print("\n" + "="*50)
    print("📊 數據收集完成報告")
    print("="*50)
    
    for collector_name, result in results['collection_results'].items():
        print(f"\n{collector_name}:")
        print(f"  狀態: {result['status']}")
        if result['status'] == 'success':
            print(f"  保存路徑: {result['saved_path']}")
    
    print(f"\n統一數據集:")
    unified = results['unified_dataset']
    print(f"  總訓練對: {unified['total_pairs']}")
    print(f"  去重後: {unified['unique_pairs']}")
    print(f"  高質量: {unified['high_quality_pairs']}")
    print(f"\n數據集路徑:")
    for format_name, path in unified['dataset_paths'].items():
        print(f"  {format_name}: {path}")


if __name__ == "__main__":
    asyncio.run(main())