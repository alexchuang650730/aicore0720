#!/usr/bin/env python3
"""
準備K2+DeepSWE+MemoryRAG訓練數據
將Manus對話和工具調用轉換為統一訓練格式
"""

import json
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import random
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingDataPreparer:
    """訓練數據準備器"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.output_dir = Path("data/training_ready")
        self.output_dir.mkdir(exist_ok=True)
        
        # MCP工具映射
        self.tool_mapping = {
            "Read": 0, "Write": 1, "Edit": 2, "MultiEdit": 3,
            "Grep": 4, "Glob": 5, "LS": 6, "Task": 7,
            "Bash": 8, "TodoWrite": 9, "NotebookRead": 10,
            "NotebookEdit": 11, "WebFetch": 12, "WebSearch": 13,
            "exit_plan_mode": 14, "create_file": 15, "delete_file": 16,
            "rename_file": 17, "move_file": 18, "copy_file": 19
        }
        
        # 統計信息
        self.stats = defaultdict(int)
        
    def prepare_all_data(self):
        """準備所有訓練數據"""
        logger.info("🚀 開始準備訓練數據...")
        
        all_samples = []
        
        # 1. 處理Manus對話數據
        manus_samples = self._process_manus_conversations()
        all_samples.extend(manus_samples)
        logger.info(f"✅ 處理了 {len(manus_samples)} 個Manus對話樣本")
        
        # 2. 創建合成的工具調用數據
        tool_samples = self._create_synthetic_tool_data()
        all_samples.extend(tool_samples)
        logger.info(f"✅ 創建了 {len(tool_samples)} 個工具調用樣本")
        
        # 3. 創建程式理解數據
        code_samples = self._create_code_understanding_data()
        all_samples.extend(code_samples)
        logger.info(f"✅ 創建了 {len(code_samples)} 個程式理解樣本")
        
        # 4. 創建記憶增強數據
        memory_samples = self._create_memory_augmented_data()
        all_samples.extend(memory_samples)
        logger.info(f"✅ 創建了 {len(memory_samples)} 個記憶增強樣本")
        
        # 打亂數據
        random.shuffle(all_samples)
        
        # 分割訓練集和驗證集
        split_point = int(len(all_samples) * 0.9)
        train_samples = all_samples[:split_point]
        val_samples = all_samples[split_point:]
        
        # 保存數據
        self._save_dataset(train_samples, "train.json")
        self._save_dataset(val_samples, "val.json")
        
        # 打印統計信息
        self._print_statistics()
        
        return train_samples, val_samples
    
    def _process_manus_conversations(self):
        """處理Manus對話數據"""
        samples = []
        chat_dir = self.data_dir / "enhanced_extracted_chats"
        
        if not chat_dir.exists():
            logger.warning(f"找不到對話目錄: {chat_dir}")
            return samples
        
        for json_file in chat_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                conversation = data.get("conversation", [])
                
                # 構建上下文對話
                for i in range(0, len(conversation) - 1, 2):
                    if i + 1 < len(conversation):
                        user_msg = conversation[i]
                        assistant_msg = conversation[i + 1]
                        
                        if user_msg.get("role") == "user" and assistant_msg.get("role") == "assistant":
                            # 檢查是否包含工具調用
                            tool_calls = self._extract_tool_calls(assistant_msg["content"])
                            
                            sample = {
                                "input": user_msg["content"],
                                "output": assistant_msg["content"],
                                "type": "conversation",
                                "has_tool_calls": len(tool_calls) > 0,
                                "tool_calls": tool_calls,
                                "context": self._get_conversation_context(conversation, i),
                                "metadata": {
                                    "source": "manus",
                                    "url": data.get("url", ""),
                                    "timestamp": data.get("timestamp", ""),
                                    "message_count": len(conversation)
                                }
                            }
                            
                            samples.append(sample)
                            self.stats["manus_conversations"] += 1
                            
                            if tool_calls:
                                self.stats["conversations_with_tools"] += 1
            
            except Exception as e:
                logger.warning(f"處理文件失敗 {json_file}: {e}")
        
        return samples
    
    def _extract_tool_calls(self, content):
        """從回覆中提取工具調用"""
        tool_calls = []
        
        # 查找 <function_calls> 標籤
        function_call_pattern = r'<function_calls>(.*?)</function_calls>'
        matches = re.findall(function_call_pattern, content, re.DOTALL)
        
        for match in matches:
            # 提取每個 invoke
            invoke_pattern = r'<invoke name="([^"]+)">(.*?)</invoke>'
            invokes = re.findall(invoke_pattern, match, re.DOTALL)
            
            for tool_name, params_content in invokes:
                if tool_name in self.tool_mapping:
                    # 提取參數
                    param_pattern = r'<parameter name="([^"]+)">([^<]*)</parameter>'
                    params = dict(re.findall(param_pattern, params_content))
                    
                    tool_calls.append({
                        "tool": tool_name,
                        "tool_id": self.tool_mapping[tool_name],
                        "parameters": params
                    })
                    
                    self.stats[f"tool_{tool_name}"] += 1
        
        return tool_calls
    
    def _get_conversation_context(self, conversation, current_idx, context_window=2):
        """獲取對話上下文"""
        context = []
        start_idx = max(0, current_idx - context_window * 2)
        
        for i in range(start_idx, current_idx):
            if i < len(conversation):
                msg = conversation[i]
                context.append({
                    "role": msg.get("role", ""),
                    "content": msg.get("content", "")[:200]  # 截斷以節省空間
                })
        
        return context
    
    def _create_synthetic_tool_data(self):
        """創建合成的工具調用訓練數據"""
        samples = []
        
        # 工具使用場景模板
        tool_scenarios = [
            # Read工具場景
            {
                "tool": "Read",
                "scenarios": [
                    {
                        "input": "請幫我查看 {file} 文件的內容",
                        "params": {"file_path": "{file}"},
                        "response": "我將為您讀取 {file} 文件的內容。"
                    },
                    {
                        "input": "顯示 {file} 的前 {n} 行",
                        "params": {"file_path": "{file}", "limit": "{n}"},
                        "response": "我將顯示 {file} 文件的前 {n} 行。"
                    }
                ]
            },
            # Write工具場景
            {
                "tool": "Write",
                "scenarios": [
                    {
                        "input": "創建一個新的 {type} 文件叫 {file}",
                        "params": {"file_path": "{file}", "content": ""},
                        "response": "我將為您創建新的 {type} 文件 {file}。"
                    }
                ]
            },
            # Edit工具場景
            {
                "tool": "Edit",
                "scenarios": [
                    {
                        "input": "將 {file} 中的 {old} 替換為 {new}",
                        "params": {"file_path": "{file}", "old_string": "{old}", "new_string": "{new}"},
                        "response": "我將在 {file} 中將 {old} 替換為 {new}。"
                    }
                ]
            },
            # Grep工具場景
            {
                "tool": "Grep",
                "scenarios": [
                    {
                        "input": "搜索所有包含 {pattern} 的 {ext} 文件",
                        "params": {"pattern": "{pattern}", "glob": "*.{ext}"},
                        "response": "我將搜索所有包含 {pattern} 的 {ext} 文件。"
                    }
                ]
            },
            # Bash工具場景
            {
                "tool": "Bash",
                "scenarios": [
                    {
                        "input": "執行 {command} 命令",
                        "params": {"command": "{command}", "description": "執行命令"},
                        "response": "我將執行 {command} 命令。"
                    }
                ]
            }
        ]
        
        # 生成樣本
        file_types = ["Python", "JavaScript", "配置", "文檔", "測試"]
        file_names = ["main.py", "config.json", "utils.js", "README.md", "test.py"]
        patterns = ["TODO", "FIXME", "import", "function", "class"]
        commands = ["pytest", "npm test", "git status", "ls -la", "python script.py"]
        
        for tool_info in tool_scenarios:
            tool_name = tool_info["tool"]
            
            for scenario in tool_info["scenarios"]:
                # 生成多個變體
                for _ in range(20):  # 每個場景生成20個樣本
                    # 隨機填充模板
                    replacements = {
                        "{file}": random.choice(file_names),
                        "{type}": random.choice(file_types),
                        "{n}": str(random.randint(10, 100)),
                        "{old}": f"old_{random.randint(1, 100)}",
                        "{new}": f"new_{random.randint(1, 100)}",
                        "{pattern}": random.choice(patterns),
                        "{ext}": random.choice(["py", "js", "json", "md"]),
                        "{command}": random.choice(commands)
                    }
                    
                    # 構建輸入輸出
                    input_text = scenario["input"]
                    params = {}
                    response = scenario["response"]
                    
                    for key, value in replacements.items():
                        input_text = input_text.replace(key, value)
                        response = response.replace(key, value)
                        
                        # 處理參數
                        for param_key, param_value in scenario["params"].items():
                            if key in param_value:
                                params[param_key] = param_value.replace(key, value)
                    
                    # 構建工具調用XML
                    params_xml = ""
                    for param_name, param_value in params.items():
                        params_xml += f'\n<parameter name="{param_name}">{param_value}</parameter>'
                    
                    output_text = f"{response}\n\n<function_calls>\n<invoke name=\"{tool_name}\">{params_xml}\n</invoke>\n</function_calls>"
                    
                    sample = {
                        "input": input_text,
                        "output": output_text,
                        "type": "tool_call",
                        "has_tool_calls": True,
                        "tool_calls": [{
                            "tool": tool_name,
                            "tool_id": self.tool_mapping[tool_name],
                            "parameters": params
                        }],
                        "context": [],
                        "metadata": {
                            "source": "synthetic",
                            "tool": tool_name
                        }
                    }
                    
                    samples.append(sample)
                    self.stats["synthetic_tool_calls"] += 1
        
        return samples
    
    def _create_code_understanding_data(self):
        """創建程式理解訓練數據"""
        samples = []
        
        # 程式理解場景
        code_scenarios = [
            {
                "input": "這段代碼的功能是什麼？\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```",
                "output": "這段代碼實現了斐波那契數列的遞歸計算。函數接受一個整數 n 作為參數，返回第 n 個斐波那契數。當 n 小於等於 1 時直接返回 n，否則返回前兩個斐波那契數的和。",
                "type": "code_explanation"
            },
            {
                "input": "請幫我優化這段代碼的性能",
                "output": "我會分析代碼並提供性能優化建議。讓我先查看您的代碼。\n\n<function_calls>\n<invoke name=\"Read\">\n<parameter name=\"file_path\">main.py</parameter>\n</invoke>\n</function_calls>",
                "type": "code_optimization"
            },
            {
                "input": "這個錯誤是什麼意思？TypeError: 'NoneType' object is not iterable",
                "output": "這個錯誤表示您嘗試迭代一個 None 對象。通常發生在函數沒有返回值（默認返回 None）或變量被設置為 None 時，卻被當作可迭代對象使用。請檢查相關變量是否正確初始化。",
                "type": "error_explanation"
            }
        ]
        
        # 生成更多變體
        for scenario in code_scenarios:
            for i in range(30):  # 每個場景30個變體
                sample = {
                    "input": scenario["input"],
                    "output": scenario["output"],
                    "type": "code_understanding",
                    "has_tool_calls": "function_calls" in scenario["output"],
                    "tool_calls": self._extract_tool_calls(scenario["output"]),
                    "context": [],
                    "metadata": {
                        "source": "synthetic",
                        "understanding_type": scenario["type"]
                    }
                }
                samples.append(sample)
                self.stats["code_understanding_samples"] += 1
        
        return samples
    
    def _create_memory_augmented_data(self):
        """創建記憶增強訓練數據"""
        samples = []
        
        # 需要記憶的場景
        memory_scenarios = [
            {
                "context": [
                    {"role": "user", "content": "我的項目使用 Python 3.9"},
                    {"role": "assistant", "content": "了解，您的項目使用 Python 3.9。"}
                ],
                "input": "幫我創建一個兼容的 requirements.txt",
                "output": "基於您之前提到的 Python 3.9 環境，我將創建一個兼容的 requirements.txt 文件。",
                "requires_memory": True
            },
            {
                "context": [
                    {"role": "user", "content": "我們的編碼規範要求使用 4 個空格縮進"},
                    {"role": "assistant", "content": "好的，我會遵循 4 個空格的縮進規範。"}
                ],
                "input": "幫我格式化這個文件",
                "output": "我將按照您之前提到的編碼規範（4 個空格縮進）來格式化文件。",
                "requires_memory": True
            }
        ]
        
        for scenario in memory_scenarios:
            for i in range(25):
                sample = {
                    "input": scenario["input"],
                    "output": scenario["output"],
                    "type": "memory_augmented",
                    "has_tool_calls": False,
                    "tool_calls": [],
                    "context": scenario["context"],
                    "metadata": {
                        "source": "synthetic",
                        "requires_memory": scenario["requires_memory"]
                    }
                }
                samples.append(sample)
                self.stats["memory_augmented_samples"] += 1
        
        return samples
    
    def _save_dataset(self, samples, filename):
        """保存數據集"""
        output_path = self.output_dir / filename
        
        # 轉換為訓練格式
        processed_samples = []
        for sample in samples:
            processed = {
                "id": f"{sample['type']}_{len(processed_samples)}",
                "input": sample["input"],
                "output": sample["output"],
                "type": sample["type"],
                "has_tool_calls": sample["has_tool_calls"],
                "tool_labels": [tc["tool_id"] for tc in sample["tool_calls"]] if sample["tool_calls"] else [],
                "context": sample["context"],
                "metadata": sample["metadata"]
            }
            processed_samples.append(processed)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_samples, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 保存了 {len(processed_samples)} 個樣本到 {output_path}")
    
    def _print_statistics(self):
        """打印統計信息"""
        logger.info("\n📊 數據統計:")
        logger.info("="*50)
        
        total_samples = sum(v for k, v in self.stats.items() if k.endswith("_samples") or k == "manus_conversations")
        logger.info(f"總樣本數: {total_samples}")
        
        logger.info("\n按類型分佈:")
        logger.info(f"  - Manus對話: {self.stats['manus_conversations']}")
        logger.info(f"  - 合成工具調用: {self.stats['synthetic_tool_calls']}")
        logger.info(f"  - 程式理解: {self.stats['code_understanding_samples']}")
        logger.info(f"  - 記憶增強: {self.stats['memory_augmented_samples']}")
        
        logger.info("\n工具使用統計:")
        for tool_name in self.tool_mapping.keys():
            count = self.stats.get(f"tool_{tool_name}", 0)
            if count > 0:
                logger.info(f"  - {tool_name}: {count}")
        
        logger.info("\n其他統計:")
        logger.info(f"  - 包含工具調用的對話: {self.stats['conversations_with_tools']}")

def main():
    """主函數"""
    preparer = TrainingDataPreparer()
    train_data, val_data = preparer.prepare_all_data()
    
    logger.info(f"\n✅ 數據準備完成!")
    logger.info(f"訓練集: {len(train_data)} 樣本")
    logger.info(f"驗證集: {len(val_data)} 樣本")

if __name__ == "__main__":
    main()