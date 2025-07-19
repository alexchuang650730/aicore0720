#!/usr/bin/env python3
"""
整合數據收集系統
結合 MemoryRAG、Manus Replay 和 Claude 對話數據
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class IntegratedDataCollectionSystem:
    """整合的數據收集系統"""
    
    def __init__(self):
        self.output_dir = Path("./data/integrated_training")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def collect_all_data(self) -> Dict[str, Any]:
        """收集所有可用數據"""
        print("🚀 開始整合數據收集...")
        
        results = {
            'memoryrag_data': None,
            'manus_replays': None,
            'claude_conversations': None,
            'total_training_pairs': 0,
            'collection_time': datetime.now().isoformat()
        }
        
        # 1. 從 MemoryRAG 收集
        print("\n📊 收集 MemoryRAG 數據...")
        try:
            from core.data_collection.memoryrag_data_extractor import MemoryRAGDataExtractor
            extractor = MemoryRAGDataExtractor()
            memoryrag_data = extractor.extract_all_conversations()
            results['memoryrag_data'] = memoryrag_data
            print(f"✅ MemoryRAG: {len(memoryrag_data.get('training_pairs', []))} 個訓練對")
        except Exception as e:
            print(f"❌ MemoryRAG 收集失敗: {e}")
            
        # 2. 收集 Manus Replays（如果有 URLs）
        print("\n🔗 收集 Manus Replay 數據...")
        replay_urls_file = Path("replay_urls.txt")
        if replay_urls_file.exists():
            try:
                with open(replay_urls_file, 'r') as f:
                    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                if urls:
                    from core.training.manus_replay_extractor import ManusReplayExtractor
                    extractor = ManusReplayExtractor()
                    manus_data = await extractor.process_batch(urls[:10])  # 先處理前10個
                    await extractor.close()
                    results['manus_replays'] = manus_data
                    print(f"✅ Manus: {manus_data.get('total_training_pairs', 0)} 個訓練對")
                else:
                    print("⚠️ 沒有找到 Manus replay URLs")
            except Exception as e:
                print(f"❌ Manus 收集失敗: {e}")
        else:
            print("⚠️ replay_urls.txt 不存在")
            
        # 3. 處理 Claude 對話數據（從 MemoryRAG 和當前對話）
        print("\n💬 處理 Claude 對話數據...")
        
        # 3a. 從 MemoryRAG 提取的 Claude 數據已經在步驟1中處理
        
        # 3b. 處理當前對話（如果有）
        conversation_file = Path("conversation.txt")
        if conversation_file.exists():
            try:
                from core.data_collection.claude_conversation_collector import ClaudeConversationCollector
                collector = ClaudeConversationCollector()
                with open(conversation_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                claude_data = collector.process_current_conversation(text)
                results['claude_conversations'] = claude_data
                print(f"✅ Claude: {claude_data.get('programming_pairs', 0)} 個編程對話對")
            except Exception as e:
                print(f"❌ Claude 收集失敗: {e}")
        else:
            print("⚠️ conversation.txt 不存在")
            
        # 4. 整合所有數據
        all_training_pairs = self._merge_all_training_data(results)
        results['total_training_pairs'] = len(all_training_pairs)
        
        # 5. 創建統一的訓練數據集
        unified_dataset = self._create_unified_dataset(all_training_pairs)
        
        # 6. 保存結果
        self._save_integrated_results(results, unified_dataset)
        
        print(f"\n✅ 數據收集完成！")
        print(f"總訓練對: {results['total_training_pairs']}")
        
        return results
        
    def _merge_all_training_data(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """合併所有訓練數據"""
        all_pairs = []
        
        # MemoryRAG 數據
        if results['memoryrag_data']:
            pairs = results['memoryrag_data'].get('training_pairs', [])
            for pair in pairs:
                all_pairs.append({
                    'source': 'memoryrag',
                    'input': pair['input'],
                    'output': pair['output'],
                    'type': pair.get('type', 'general'),
                    'quality_score': pair.get('quality_score', 0.5),
                    'metadata': pair
                })
                
        # Manus 數據
        if results['manus_replays']:
            training_data_path = Path(results['manus_replays'].get('training_data_path', ''))
            if training_data_path.exists():
                with open(training_data_path, 'r', encoding='utf-8') as f:
                    manus_data = json.load(f)
                    for pair in manus_data.get('pairs', []):
                        all_pairs.append({
                            'source': 'manus',
                            'input': pair['input'],
                            'output': pair['output'],
                            'type': pair.get('type', 'general'),
                            'quality_score': pair.get('quality_score', 0.5),
                            'metadata': pair
                        })
                        
        # Claude 數據
        if results['claude_conversations']:
            training_data = results['claude_conversations'].get('training_data', [])
            for item in training_data:
                base = item.get('base', {})
                all_pairs.append({
                    'source': 'claude',
                    'input': base.get('instruction', ''),
                    'output': base.get('response', ''),
                    'type': base.get('metadata', {}).get('type', 'general'),
                    'quality_score': 0.8,  # Claude 對話通常質量較高
                    'metadata': base
                })
                
        return all_pairs
        
    def _create_unified_dataset(self, all_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """創建統一的數據集"""
        # 按質量排序
        high_quality_pairs = [p for p in all_pairs if p['quality_score'] > 0.7]
        high_quality_pairs.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # 創建不同格式
        datasets = {
            'standard': [],
            'k2_optimized': [],
            'deepswe': []
        }
        
        for pair in high_quality_pairs:
            # 標準格式
            datasets['standard'].append({
                'instruction': pair['input'],
                'response': pair['output'],
                'source': pair['source'],
                'type': pair['type']
            })
            
            # K2 優化格式
            datasets['k2_optimized'].append({
                'prompt': self._create_k2_prompt(pair),
                'completion': pair['output']
            })
            
            # DeepSWE 格式
            datasets['deepswe'].append({
                'prompt': pair['input'],
                'thinking': self._extract_or_generate_thinking(pair),
                'response': pair['output']
            })
            
        return {
            'total_pairs': len(all_pairs),
            'high_quality_pairs': len(high_quality_pairs),
            'datasets': datasets,
            'statistics': self._calculate_statistics(all_pairs)
        }
        
    def _create_k2_prompt(self, pair: Dict[str, Any]) -> str:
        """創建 K2 優化提示"""
        return f"""<context>
數據來源: {pair['source']}
任務類型: {pair['type']}
項目: PowerAutomation
</context>

<task>
{pair['input']}
</task>

請提供高質量的解決方案。"""
        
    def _extract_or_generate_thinking(self, pair: Dict[str, Any]) -> str:
        """提取或生成思考過程"""
        output = pair['output']
        
        # 嘗試提取現有的思考過程
        import re
        thinking_patterns = [
            r'(讓我.*?[。\n])',
            r'(首先.*?[。\n])',
            r'(我需要.*?[。\n])'
        ]
        
        for pattern in thinking_patterns:
            matches = re.findall(pattern, output)
            if matches:
                return ' '.join(matches)
                
        # 生成默認思考過程
        return f"分析{pair['type']}任務，設計解決方案。"
        
    def _calculate_statistics(self, all_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """計算統計信息"""
        stats = {
            'by_source': {},
            'by_type': {},
            'quality_distribution': {
                'high': len([p for p in all_pairs if p['quality_score'] > 0.8]),
                'medium': len([p for p in all_pairs if 0.5 <= p['quality_score'] <= 0.8]),
                'low': len([p for p in all_pairs if p['quality_score'] < 0.5])
            }
        }
        
        # 按來源統計
        for pair in all_pairs:
            source = pair['source']
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
            
            task_type = pair['type']
            stats['by_type'][task_type] = stats['by_type'].get(task_type, 0) + 1
            
        return stats
        
    def _save_integrated_results(self, results: Dict[str, Any], unified_dataset: Dict[str, Any]):
        """保存整合結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存完整報告
        report_file = self.output_dir / f"integration_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'results': results,
                'unified_dataset_stats': {
                    'total_pairs': unified_dataset['total_pairs'],
                    'high_quality_pairs': unified_dataset['high_quality_pairs'],
                    'statistics': unified_dataset['statistics']
                }
            }, f, ensure_ascii=False, indent=2)
            
        # 保存各種格式的數據集
        for format_name, dataset in unified_dataset['datasets'].items():
            if dataset:
                dataset_file = self.output_dir / f"{format_name}_dataset_{timestamp}.jsonl"
                with open(dataset_file, 'w', encoding='utf-8') as f:
                    for item in dataset:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
                print(f"💾 {format_name} 數據集: {dataset_file} ({len(dataset)} 條)")
                
    async def setup_continuous_collection(self):
        """設置持續數據收集"""
        print("🔄 設置持續數據收集...")
        
        # 1. 啟動 MemoryRAG 的 DeepSWE 學習適配器
        try:
            from core.memoryrag.memory_os import MemoryRAG
            from core.memoryrag.deepswe_learning_adapter import DeepSWELearningAdapter
            
            memoryrag = MemoryRAG()
            adapter = DeepSWELearningAdapter(memoryrag)
            
            # 啟動持續學習
            asyncio.create_task(adapter.continuous_learning())
            print("✅ DeepSWE 持續學習已啟動")
        except Exception as e:
            print(f"❌ 無法啟動持續學習: {e}")
            
        # 2. 定期收集新數據
        while True:
            await asyncio.sleep(3600)  # 每小時
            try:
                await self.collect_all_data()
            except Exception as e:
                print(f"❌ 定期收集失敗: {e}")


async def main():
    """主函數"""
    system = IntegratedDataCollectionSystem()
    
    # 執行一次性數據收集
    results = await system.collect_all_data()
    
    # 生成使用建議
    print("\n" + "="*60)
    print("📚 數據使用建議")
    print("="*60)
    print("\n1. 使用 K2 優化數據集訓練提示優化器:")
    print("   python train_k2_optimizer.py --data ./data/integrated_training/k2_optimized_dataset_*.jsonl")
    print("\n2. 使用 DeepSWE 格式訓練思考鏈模型:")
    print("   python train_deepswe_model.py --data ./data/integrated_training/deepswe_dataset_*.jsonl")
    print("\n3. 啟動持續學習:")
    print("   python integrated_data_collection.py --continuous")
    print("\n4. 查看數據統計:")
    print("   cat ./data/integrated_training/integration_report_*.json | jq '.unified_dataset_stats'")
    
    # 如果需要持續收集
    # await system.setup_continuous_collection()


if __name__ == "__main__":
    import sys
    
    if '--continuous' in sys.argv:
        # 持續模式
        asyncio.run(IntegratedDataCollectionSystem().setup_continuous_collection())
    else:
        # 一次性收集
        asyncio.run(main())