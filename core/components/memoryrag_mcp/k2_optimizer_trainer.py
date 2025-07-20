#!/usr/bin/env python3
"""
K2 優化器訓練系統
整合 Claude 對話數據和 Manus 分析結果進行模型訓練
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass, asdict
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """訓練配置"""
    model_name: str = "k2-optimizer"
    base_model: str = "gpt-3.5-turbo"  # 基礎模型
    learning_rate: float = 1e-5
    batch_size: int = 16
    epochs: int = 3
    max_length: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    
    # K2 定價配置
    input_price_per_million: float = 2.0  # 2元/M tokens
    output_price_per_million: float = 8.0  # 8元/M tokens

@dataclass
class TrainingSample:
    """訓練樣本"""
    instruction: str
    input: str
    output: str
    category: str  # thinking/observation/action
    tools_used: List[str]
    confidence: float
    source: str  # claude/manus

class K2OptimizerTrainer:
    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.training_data = []
        self.validation_data = []
        self.test_data = []
        
    def load_claude_data(self, file_path: str):
        """載入 Claude 對話數據"""
        logger.info(f"載入 Claude 訓練數據: {file_path}")
        
        if not Path(file_path).exists():
            logger.error(f"文件不存在: {file_path}")
            return 0
        
        loaded = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        sample = json.loads(line)
                        training_sample = TrainingSample(
                            instruction=sample.get('instruction', ''),
                            input=sample.get('input', ''),
                            output=sample.get('output', ''),
                            category='thinking',  # Claude 數據默認為思考類
                            tools_used=sample.get('tools_used', []),
                            confidence=0.8,
                            source='claude'
                        )
                        self.training_data.append(training_sample)
                        loaded += 1
                    except Exception as e:
                        logger.warning(f"解析錯誤: {e}")
        
        logger.info(f"成功載入 {loaded} 條 Claude 數據")
        return loaded
    
    def load_manus_data(self, analysis_dir: str):
        """載入 Manus 分析數據"""
        logger.info(f"載入 Manus 分析數據: {analysis_dir}")
        
        analysis_path = Path(analysis_dir)
        if not analysis_path.exists():
            logger.warning(f"目錄不存在: {analysis_dir}")
            return 0
        
        loaded = 0
        # 查找所有分析文件
        pattern_files = list(analysis_path.glob("manus_analysis_*.json")) + list(analysis_path.glob("manus_raw_data_*.json"))
        logger.info(f"找到 {len(pattern_files)} 個 Manus 文件")
        
        for analysis_file in pattern_files:
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 處理不同的數據格式
                if 'categories' in data:
                    # 分析格式的數據
                    categories = data.get('categories', {})
                    for category, messages in categories.items():
                        for msg in messages:
                            if msg.get('content'):
                                training_sample = TrainingSample(
                                    instruction="分析並執行任務",
                                    input=msg['content'][:500],
                                    output=self._generate_response(msg, category),
                                    category=category,
                                    tools_used=self._extract_tools(msg),
                                    confidence=msg.get('confidence', 0.5),
                                    source='manus'
                                )
                                self.training_data.append(training_sample)
                                loaded += 1
                elif 'messages' in data:
                    # 原始消息格式的數據
                    messages = data.get('messages', [])
                    for msg in messages:
                        # 構建訓練樣本
                        if msg.get('content'):
                            # 根據內容推斷類別
                            category = self._infer_category(msg)
                            training_sample = TrainingSample(
                                instruction="分析並執行任務",
                                input=msg['content'][:500],
                                output=self._generate_response(msg, category),
                                category=category,
                                tools_used=self._extract_tools(msg),
                                confidence=0.6,
                                source='manus'
                            )
                            self.training_data.append(training_sample)
                            loaded += 1
            
            except Exception as e:
                logger.warning(f"處理文件 {analysis_file} 時出錯: {e}")
        
        logger.info(f"成功載入 {loaded} 條 Manus 數據")
        return loaded
    
    def _generate_response(self, msg: Dict, category: str) -> str:
        """根據消息生成響應"""
        if category == 'thinking':
            return f"基於分析，我理解這個任務需要: {msg['content'][:200]}"
        elif category == 'observation':
            return f"觀察結果顯示: {msg['content'][:200]}"
        elif category == 'action':
            return f"執行操作: {msg['content'][:200]}"
        else:
            return msg['content'][:300]
    
    def _extract_tools(self, msg: Dict) -> List[str]:
        """提取工具使用"""
        tools = []
        content = msg.get('content', '').lower()
        
        tool_keywords = {
            'git': ['git ', 'github'],
            'npm': ['npm ', 'node_modules'],
            'python': ['python ', 'pip ', 'pytest'],
            'docker': ['docker ', 'dockerfile'],
            'api': ['api', 'request', 'endpoint'],
            'file': ['file', 'create', 'write', 'read']
        }
        
        for tool, keywords in tool_keywords.items():
            if any(keyword in content for keyword in keywords):
                tools.append(tool)
        
        return tools
    
    def _infer_category(self, msg: Dict) -> str:
        """根據消息內容推斷類別"""
        content = msg.get('content', '').lower()
        
        # 思考類關鍵詞
        thinking_keywords = ['分析', '理解', '需要', '應該', '可以', '思考', 'think', 'analyze']
        # 觀察類關鍵詞
        observation_keywords = ['顯示', '看到', '發現', '結果', '狀態', 'show', 'display', 'result']
        # 動作類關鍵詞
        action_keywords = ['執行', '運行', '創建', '修改', 'git', 'python', '命令']
        
        thinking_score = sum(1 for kw in thinking_keywords if kw in content)
        observation_score = sum(1 for kw in observation_keywords if kw in content)
        action_score = sum(1 for kw in action_keywords if kw in content)
        
        if action_score > max(thinking_score, observation_score):
            return 'action'
        elif observation_score > thinking_score:
            return 'observation'
        else:
            return 'thinking'
    
    def prepare_datasets(self, train_ratio: float = 0.8, val_ratio: float = 0.1):
        """準備訓練、驗證和測試數據集"""
        logger.info("準備數據集...")
        
        # 打亂數據
        random.shuffle(self.training_data)
        
        total = len(self.training_data)
        train_size = int(total * train_ratio)
        val_size = int(total * val_ratio)
        
        self.training_data = self.training_data[:train_size]
        self.validation_data = self.training_data[train_size:train_size + val_size]
        self.test_data = self.training_data[train_size + val_size:]
        
        logger.info(f"數據集分配:")
        logger.info(f"  訓練集: {len(self.training_data)}")
        logger.info(f"  驗證集: {len(self.validation_data)}")
        logger.info(f"  測試集: {len(self.test_data)}")
    
    def generate_training_files(self, output_dir: str = "./k2_training_data"):
        """生成訓練文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 生成訓練集
        train_file = output_path / f"k2_train_{timestamp}.jsonl"
        self._save_dataset(self.training_data, train_file)
        
        # 生成驗證集
        val_file = output_path / f"k2_validation_{timestamp}.jsonl"
        self._save_dataset(self.validation_data, val_file)
        
        # 生成測試集
        test_file = output_path / f"k2_test_{timestamp}.jsonl"
        self._save_dataset(self.test_data, test_file)
        
        # 生成配置文件
        config_file = output_path / f"k2_config_{timestamp}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.config), f, ensure_ascii=False, indent=2)
        
        # 生成訓練報告
        report = self.generate_training_report()
        report_file = output_path / f"k2_training_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"訓練文件已生成:")
        logger.info(f"  訓練集: {train_file}")
        logger.info(f"  驗證集: {val_file}")
        logger.info(f"  測試集: {test_file}")
        logger.info(f"  配置: {config_file}")
        logger.info(f"  報告: {report_file}")
        
        return {
            'train': str(train_file),
            'validation': str(val_file),
            'test': str(test_file),
            'config': str(config_file),
            'report': str(report_file)
        }
    
    def _save_dataset(self, dataset: List[TrainingSample], file_path: Path):
        """保存數據集"""
        with open(file_path, 'w', encoding='utf-8') as f:
            for sample in dataset:
                # 轉換為訓練格式
                training_format = {
                    "messages": [
                        {"role": "system", "content": "你是 K2 優化器，擅長分析任務並提供最佳解決方案。"},
                        {"role": "user", "content": sample.instruction + "\n" + sample.input},
                        {"role": "assistant", "content": sample.output}
                    ],
                    "metadata": {
                        "category": sample.category,
                        "tools": sample.tools_used,
                        "confidence": sample.confidence,
                        "source": sample.source
                    }
                }
                f.write(json.dumps(training_format, ensure_ascii=False) + '\n')
    
    def generate_training_report(self) -> str:
        """生成訓練報告"""
        report = []
        report.append("# K2 優化器訓練報告")
        report.append(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 配置信息
        report.append("\n## 訓練配置")
        report.append(f"- 模型名稱: {self.config.model_name}")
        report.append(f"- 基礎模型: {self.config.base_model}")
        report.append(f"- 學習率: {self.config.learning_rate}")
        report.append(f"- 批次大小: {self.config.batch_size}")
        report.append(f"- 訓練輪數: {self.config.epochs}")
        report.append(f"- 最大長度: {self.config.max_length}")
        
        # 定價信息
        report.append("\n## K2 定價")
        report.append(f"- 輸入: {self.config.input_price_per_million} 元/M tokens")
        report.append(f"- 輸出: {self.config.output_price_per_million} 元/M tokens")
        
        # 數據統計
        all_data = self.training_data + self.validation_data + self.test_data
        report.append(f"\n## 數據統計")
        report.append(f"- 總樣本數: {len(all_data)}")
        
        # 數據來源分布
        source_dist = {}
        for sample in all_data:
            source_dist[sample.source] = source_dist.get(sample.source, 0) + 1
        
        report.append("\n### 數據來源")
        for source, count in source_dist.items():
            report.append(f"- {source}: {count} ({count/len(all_data)*100:.1f}%)")
        
        # 類別分布
        category_dist = {}
        for sample in all_data:
            category_dist[sample.category] = category_dist.get(sample.category, 0) + 1
        
        report.append("\n### 類別分布")
        for category, count in category_dist.items():
            emoji = {'thinking': '🧠', 'observation': '👁️', 'action': '🎯'}.get(category, '📝')
            report.append(f"- {emoji} {category}: {count} ({count/len(all_data)*100:.1f}%)")
        
        # 工具使用統計
        tool_usage = {}
        for sample in all_data:
            for tool in sample.tools_used:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        if tool_usage:
            report.append("\n### 工具使用頻率")
            for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:10]:
                report.append(f"- {tool}: {count}")
        
        # 置信度分析
        confidences = [sample.confidence for sample in all_data]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            report.append(f"\n### 平均置信度")
            report.append(f"- 整體: {avg_confidence:.2f}")
            
            # 按類別的置信度
            for category in ['thinking', 'observation', 'action']:
                cat_confidences = [s.confidence for s in all_data if s.category == category]
                if cat_confidences:
                    avg = sum(cat_confidences) / len(cat_confidences)
                    report.append(f"- {category}: {avg:.2f}")
        
        # 訓練建議
        report.append("\n## 訓練建議")
        if len(all_data) < 1000:
            report.append("- ⚠️ 數據量較少，建議收集更多訓練數據")
        
        if 'thinking' in category_dist and category_dist['thinking'] / len(all_data) > 0.6:
            report.append("- 思考類數據較多，模型可能偏向分析而非執行")
        elif 'action' in category_dist and category_dist['action'] / len(all_data) > 0.6:
            report.append("- 動作類數據較多，模型可能偏向執行而非分析")
        
        report.append("\n## 下一步")
        report.append("1. 使用生成的訓練文件進行模型微調")
        report.append("2. 在驗證集上評估模型性能")
        report.append("3. 使用測試集進行最終評估")
        report.append("4. 部署 K2 優化器並實現定價系統")
        
        return "\n".join(report)
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """計算 K2 使用成本"""
        input_cost = (input_tokens / 1_000_000) * self.config.input_price_per_million
        output_cost = (output_tokens / 1_000_000) * self.config.output_price_per_million
        total_cost = input_cost + output_cost
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': round(input_cost, 4),
            'output_cost': round(output_cost, 4),
            'total_cost': round(total_cost, 4),
            'currency': 'CNY'
        }

def main():
    """主函數"""
    logger.info("🚀 啟動 K2 優化器訓練系統")
    
    # 創建訓練器
    trainer = K2OptimizerTrainer()
    
    # 獲取基礎目錄
    base_dir = Path(__file__).parent.parent.parent.parent  # 回到 aicore0720 根目錄
    
    # 載入 Claude 數據 - 使用絕對路徑
    claude_files = [
        str(base_dir / 'data/claude_conversations/training_examples_20250719_054254.jsonl')
    ]
    
    print(f"Debug: 檢查 Claude 文件:")
    for cfile in claude_files:
        print(f"  {cfile} - 存在: {Path(cfile).exists()}")
    
    for file in claude_files:
        if Path(file).exists():
            trainer.load_claude_data(file)
    
    # 載入 Manus 數據 - 使用絕對路徑
    base_dir = Path(__file__).parent.parent.parent.parent  # 回到 aicore0720 根目錄
    manus_dirs = [
        str(base_dir / 'data/manus_test_output'),
        str(base_dir / 'data/manus_advanced_analysis'),
        str(base_dir / 'data/manus_complete_collection'),
    ]
    
    print(f"Debug: 當前工作目錄: {os.getcwd()}")
    print(f"Debug: 基礎目錄: {base_dir}")
    for mdir in manus_dirs:
        print(f"Debug: 檢查目錄: {mdir} - 存在: {Path(mdir).exists()}")
    
    for dir in manus_dirs:
        if Path(dir).exists():
            trainer.load_manus_data(dir)
    
    # 準備數據集
    trainer.prepare_datasets()
    
    # 生成訓練文件
    output_files = trainer.generate_training_files()
    
    # 顯示成本計算示例
    print("\n💰 K2 定價示例:")
    example_cost = trainer.calculate_cost(input_tokens=10000, output_tokens=5000)
    print(f"輸入 {example_cost['input_tokens']} tokens: {example_cost['input_cost']} 元")
    print(f"輸出 {example_cost['output_tokens']} tokens: {example_cost['output_cost']} 元")
    print(f"總計: {example_cost['total_cost']} 元")
    
    print("\n✅ K2 優化器訓練準備完成！")

if __name__ == "__main__":
    main()