#!/usr/bin/env python3
"""
K2數據整合引擎
整合511個Manus replay數據 + Claude實時對話收集數據
生成統一的K2+DeepSWE訓練數據集
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingDataPoint:
    """統一的訓練數據格式"""
    instruction: str
    input: str
    output: str
    thinking: Optional[str] = None
    context: str = ""
    tools_used: List[str] = None
    quality_score: float = 0.0
    metadata: Dict[str, Any] = None
    source: str = ""

class K2DataIntegrationEngine:
    """K2數據整合引擎"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.output_dir = self.data_dir / "integrated_training"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 數據源路徑
        self.sources = {
            "manus_replays": self.data_dir / "replay_analysis",
            "claude_conversations": self.data_dir / "claude_conversations", 
            "claude_realtime": self.data_dir / "claude_realtime_mcp",
            "manus_advanced": self.data_dir / "manus_advanced_analysis",
            "existing_k2": self.data_dir / "k2_training_data"
        }
        
        self.stats = {
            "total_processed": 0,
            "manus_replay_count": 0,
            "claude_conversation_count": 0,
            "claude_realtime_count": 0,
            "high_quality_count": 0,
            "sources_processed": []
        }
        
    async def integrate_all_data(self) -> Dict[str, Any]:
        """整合所有數據源"""
        logger.info("🚀 開始K2數據整合...")
        start_time = time.time()
        
        all_training_data = []
        
        # 1. 處理511個Manus replay數據
        logger.info("📊 處理Manus replay數據...")
        replay_data = await self._process_manus_replays()
        all_training_data.extend(replay_data)
        self.stats["manus_replay_count"] = len(replay_data)
        
        # 2. 處理Claude實時對話數據
        logger.info("💬 處理Claude對話數據...")
        claude_data = await self._process_claude_conversations()
        all_training_data.extend(claude_data)
        self.stats["claude_conversation_count"] = len(claude_data)
        
        # 3. 處理實時收集數據
        logger.info("⚡ 處理實時收集數據...")
        realtime_data = await self._process_realtime_data()
        all_training_data.extend(realtime_data)
        self.stats["claude_realtime_count"] = len(realtime_data)
        
        # 4. 質量過濾和增強
        logger.info("🔍 質量過濾和增強...")
        high_quality_data = await self._quality_filter_and_enhance(all_training_data)
        self.stats["high_quality_count"] = len(high_quality_data)
        
        # 5. 生成多種格式
        logger.info("📦 生成訓練數據集...")
        output_files = await self._generate_training_datasets(high_quality_data)
        
        total_time = time.time() - start_time
        self.stats["total_processed"] = len(all_training_data)
        self.stats["processing_time"] = total_time
        
        # 6. 生成報告
        await self._generate_integration_report(output_files)
        
        logger.info("✅ K2數據整合完成！")
        return {
            "statistics": self.stats,
            "output_files": output_files,
            "processing_time": total_time
        }
    
    async def _process_manus_replays(self) -> List[TrainingDataPoint]:
        """處理Manus replay數據"""
        training_data = []
        replay_dir = self.sources["manus_replays"]
        
        if not replay_dir.exists():
            logger.warning(f"Manus replay目錄不存在: {replay_dir}")
            return training_data
        
        # 處理所有replay JSON文件
        for file_path in replay_dir.glob("raw_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    replay_data = json.load(f)
                
                # 轉換replay數據為訓練格式
                converted = await self._convert_replay_to_training(replay_data, str(file_path))
                training_data.extend(converted)
                
            except Exception as e:
                logger.error(f"處理replay文件失敗 {file_path}: {e}")
        
        logger.info(f"✅ 從Manus replays生成 {len(training_data)} 個訓練樣本")
        return training_data
    
    async def _process_claude_conversations(self) -> List[TrainingDataPoint]:
        """處理Claude對話數據"""
        training_data = []
        claude_dir = self.sources["claude_conversations"]
        
        if not claude_dir.exists():
            logger.warning(f"Claude對話目錄不存在: {claude_dir}")
            return training_data
        
        # 處理JSONL文件
        for file_path in claude_dir.glob("*.jsonl"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            converted = await self._convert_claude_to_training(data, str(file_path))
                            if converted:
                                training_data.append(converted)
                                
            except Exception as e:
                logger.error(f"處理Claude對話文件失敗 {file_path}: {e}")
        
        logger.info(f"✅ 從Claude對話生成 {len(training_data)} 個訓練樣本")
        return training_data
    
    async def _process_realtime_data(self) -> List[TrainingDataPoint]:
        """處理實時收集數據"""
        training_data = []
        realtime_dir = self.sources["claude_realtime"]
        
        if not realtime_dir.exists():
            logger.warning(f"實時數據目錄不存在: {realtime_dir}")
            return training_data
        
        # 這裡可以添加實時數據處理邏輯
        # 目前返回空列表
        logger.info(f"✅ 從實時數據生成 {len(training_data)} 個訓練樣本")
        return training_data
    
    async def _convert_replay_to_training(self, replay_data: Dict[str, Any], source: str) -> List[TrainingDataPoint]:
        """將replay數據轉換為訓練格式"""
        training_points = []
        
        try:
            messages = replay_data.get("conversations", [])
            if not messages:
                return training_points
            
            # 分析對話模式
            for i, message in enumerate(messages):
                if message.get("role") == "user":
                    user_input = message.get("content", "")
                    
                    # 找下一個assistant回應
                    assistant_output = ""
                    thinking = ""
                    tools_used = []
                    
                    if i + 1 < len(messages) and messages[i + 1].get("role") == "assistant":
                        assistant_msg = messages[i + 1]
                        assistant_output = assistant_msg.get("content", "")
                        
                        # 提取thinking和tools
                        if "<thinking>" in assistant_output:
                            thinking_match = assistant_output.split("<thinking>")[1].split("</thinking>")[0] if "</thinking>" in assistant_output else ""
                            thinking = thinking_match.strip()
                        
                        # 提取工具使用
                        if "使用工具:" in assistant_output:
                            tools_line = [line for line in assistant_output.split('\n') if "使用工具:" in line]
                            if tools_line:
                                tools_used = [t.strip() for t in tools_line[0].replace("使用工具:", "").split(",")]
                    
                    if user_input and assistant_output:
                        training_point = TrainingDataPoint(
                            instruction="分析並執行任務",
                            input=user_input,
                            output=assistant_output,
                            thinking=thinking if thinking else None,
                            context="包含多輪對話上下文",
                            tools_used=tools_used,
                            quality_score=self._calculate_quality_score(user_input, assistant_output),
                            metadata={
                                "source": source,
                                "timestamp": replay_data.get("timestamp", ""),
                                "length": len(assistant_output),
                                "domain": "software_engineering"
                            },
                            source="manus_replay"
                        )
                        training_points.append(training_point)
                        
        except Exception as e:
            logger.error(f"轉換replay數據失敗: {e}")
        
        return training_points
    
    async def _convert_claude_to_training(self, claude_data: Dict[str, Any], source: str) -> Optional[TrainingDataPoint]:
        """將Claude對話數據轉換為訓練格式"""
        try:
            return TrainingDataPoint(
                instruction=claude_data.get("instruction", "分析並執行任務"),
                input=claude_data.get("input", ""),
                output=claude_data.get("output", ""),
                thinking=claude_data.get("thinking"),
                context=claude_data.get("context", ""),
                tools_used=claude_data.get("tools_used", []),
                quality_score=claude_data.get("confidence", 0.7),
                metadata=claude_data.get("metadata", {}),
                source="claude_conversation"
            )
        except Exception as e:
            logger.error(f"轉換Claude數據失敗: {e}")
            return None
    
    def _calculate_quality_score(self, user_input: str, assistant_output: str) -> float:
        """計算質量分數"""
        score = 0.6  # 基礎分數
        
        # 長度加分
        if 50 <= len(assistant_output) <= 3000:
            score += 0.1
        
        # 技術內容加分
        tech_keywords = ["代碼", "function", "class", "method", "algorithm", "bug", "test", "deploy"]
        if any(keyword in user_input + assistant_output for keyword in tech_keywords):
            score += 0.15
        
        # 工具使用加分
        if "使用工具:" in assistant_output:
            score += 0.1
        
        # thinking過程加分
        if "<thinking>" in assistant_output:
            score += 0.05
        
        return min(score, 0.95)
    
    async def _quality_filter_and_enhance(self, training_data: List[TrainingDataPoint]) -> List[TrainingDataPoint]:
        """質量過濾和增強"""
        high_quality = []
        
        for data_point in training_data:
            # 基本質量檢查
            if (len(data_point.input) >= 10 and 
                len(data_point.output) >= 20 and 
                data_point.quality_score >= 0.6):
                high_quality.append(data_point)
        
        logger.info(f"質量過濾: {len(training_data)} -> {len(high_quality)} (保留率: {len(high_quality)/len(training_data)*100:.1f}%)")
        return high_quality
    
    async def _generate_training_datasets(self, training_data: List[TrainingDataPoint]) -> Dict[str, str]:
        """生成多種格式的訓練數據集"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = {}
        
        # 1. K2格式 (對話格式)
        k2_file = self.output_dir / f"k2_integrated_training_{timestamp}.jsonl"
        with open(k2_file, 'w', encoding='utf-8') as f:
            for data_point in training_data:
                k2_format = {
                    "messages": [
                        {"role": "system", "content": "你是K2優化器，專門協助用戶完成軟件工程和自動化任務。"},
                        {"role": "user", "content": data_point.input},
                        {"role": "assistant", "content": data_point.output}
                    ],
                    "quality_score": data_point.quality_score,
                    "context": data_point.context,
                    "metadata": data_point.metadata
                }
                f.write(json.dumps(k2_format, ensure_ascii=False) + '\n')
        
        output_files["k2_format"] = str(k2_file)
        
        # 2. DeepSWE格式
        deepswe_file = self.output_dir / f"deepswe_integrated_training_{timestamp}.jsonl"
        with open(deepswe_file, 'w', encoding='utf-8') as f:
            for data_point in training_data:
                deepswe_format = {
                    "instruction": data_point.instruction,
                    "input": data_point.input,
                    "output": data_point.output,
                    "thinking": data_point.thinking,
                    "tools_used": data_point.tools_used or [],
                    "metadata": {
                        "category": "software_engineering",
                        "quality_score": data_point.quality_score,
                        "has_thinking": data_point.thinking is not None,
                        **data_point.metadata
                    }
                }
                f.write(json.dumps(deepswe_format, ensure_ascii=False) + '\n')
        
        output_files["deepswe_format"] = str(deepswe_file)
        
        # 3. 統計文件
        stats_file = self.output_dir / f"integration_stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        output_files["statistics"] = str(stats_file)
        
        logger.info(f"✅ 生成訓練數據集: {len(training_data)} 個樣本")
        logger.info(f"   K2格式: {k2_file}")
        logger.info(f"   DeepSWE格式: {deepswe_file}")
        
        return output_files
    
    async def _generate_integration_report(self, output_files: Dict[str, str]):
        """生成整合報告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"integration_report_{timestamp}.md"
        
        report_content = f"""# K2數據整合報告
生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 數據統計
- 總處理樣本: {self.stats['total_processed']}
- Manus Replay樣本: {self.stats['manus_replay_count']}
- Claude對話樣本: {self.stats['claude_conversation_count']} 
- 實時收集樣本: {self.stats['claude_realtime_count']}
- 高質量樣本: {self.stats['high_quality_count']}
- 質量保留率: {self.stats['high_quality_count']/max(self.stats['total_processed'], 1)*100:.1f}%

## 📁 輸出文件
- K2格式: {output_files.get('k2_format', 'N/A')}
- DeepSWE格式: {output_files.get('deepswe_format', 'N/A')}
- 統計數據: {output_files.get('statistics', 'N/A')}

## 🎯 數據用途
1. **K2格式**: 用於K2優化器模型訓練
2. **DeepSWE格式**: 用於軟件工程任務專項訓練
3. **混合訓練**: 支持兩種格式的混合訓練策略

## ✅ 整合完成
數據已準備就緒，可用於模型訓練。建議優先使用高質量樣本進行訓練。
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"📋 整合報告已生成: {report_file}")

async def main():
    """主函數"""
    integration_engine = K2DataIntegrationEngine()
    result = await integration_engine.integrate_all_data()
    
    print("\n🎉 K2數據整合完成!")
    print(f"📊 總處理樣本: {result['statistics']['total_processed']}")
    print(f"✨ 高質量樣本: {result['statistics']['high_quality_count']}")
    print(f"⏱️ 處理時間: {result['processing_time']:.2f}秒")
    print(f"📁 輸出文件: {len(result['output_files'])} 個")

if __name__ == "__main__":
    asyncio.run(main())