#!/usr/bin/env python3
"""
Claude Code相似度計算系統
精確計算K2模型與Claude Code的相似度，提供詳細公式和數據支撐
"""

import os
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Any, Tuple
import subprocess
import re
from difflib import SequenceMatcher
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeSimilarityCalculator:
    """Claude Code相似度精確計算器"""
    
    def __init__(self):
        self.data_dir = Path("data/similarity_analysis")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化評估數據庫
        self.db_path = self.data_dir / "similarity_scores.db"
        self._init_database()
        
        # 相似度計算配置
        self.similarity_config = {
            "evaluation_metrics": {
                "semantic_similarity": 0.35,      # 語義相似度權重
                "structural_similarity": 0.25,    # 結構相似度權重
                "response_quality": 0.20,         # 回應質量權重
                "tool_usage_accuracy": 0.20       # 工具使用準確性權重
            },
            "test_scenarios": [
                "code_analysis", "file_operations", "debugging",
                "explanation", "problem_solving", "tool_usage"
            ],
            "benchmark_prompts": []
        }
        
        # 載入或創建基準測試集
        self._load_benchmark_prompts()
        
        # TF-IDF向量化器
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'
        )
    
    def _init_database(self):
        """初始化相似度評分數據庫"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS similarity_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT,
                    claude_response TEXT,
                    k2_response TEXT,
                    semantic_score REAL,
                    structural_score REAL,
                    quality_score REAL,
                    tool_accuracy_score REAL,
                    overall_similarity REAL,
                    timestamp TEXT,
                    category TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    model_version TEXT,
                    test_date TEXT,
                    overall_similarity REAL,
                    semantic_avg REAL,
                    structural_avg REAL,
                    quality_avg REAL,
                    tool_accuracy_avg REAL,
                    total_tests INTEGER,
                    improvement_rate REAL
                )
            """)
    
    def _load_benchmark_prompts(self):
        """載入基準測試提示集"""
        benchmark_file = self.data_dir / "benchmark_prompts.json"
        
        if benchmark_file.exists():
            with open(benchmark_file, 'r', encoding='utf-8') as f:
                self.similarity_config["benchmark_prompts"] = json.load(f)
        else:
            # 創建預設基準測試集
            self.similarity_config["benchmark_prompts"] = self._create_default_benchmarks()
            with open(benchmark_file, 'w', encoding='utf-8') as f:
                json.dump(self.similarity_config["benchmark_prompts"], f, 
                         ensure_ascii=False, indent=2)
    
    def _create_default_benchmarks(self) -> List[Dict]:
        """創建預設基準測試集"""
        return [
            {
                "id": "code_analysis_1",
                "category": "code_analysis",
                "prompt": "請分析這段Python代碼的功能和潛在問題：\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```",
                "expected_elements": [
                    "遞歸實現", "時間複雜度", "效率問題", "優化建議", "基本情況"
                ]
            },
            {
                "id": "file_ops_1", 
                "category": "file_operations",
                "prompt": "請讀取當前目錄下的README.md文件並總結其內容",
                "expected_elements": [
                    "使用Read工具", "文件路徑", "內容摘要", "結構化回應"
                ]
            },
            {
                "id": "debugging_1",
                "category": "debugging", 
                "prompt": "這個錯誤是什麼原因：IndexError: list index out of range",
                "expected_elements": [
                    "錯誤原因", "常見場景", "修復方法", "預防措施"
                ]
            },
            {
                "id": "explanation_1",
                "category": "explanation",
                "prompt": "請解釋什麼是機器學習中的過擬合問題",
                "expected_elements": [
                    "定義", "原因", "症狀", "解決方法", "實例"
                ]
            },
            {
                "id": "problem_solving_1",
                "category": "problem_solving",
                "prompt": "如何優化一個慢查詢的SQL語句？",
                "expected_elements": [
                    "問題診斷", "索引優化", "查詢重寫", "性能監控"
                ]
            },
            {
                "id": "tool_usage_1",
                "category": "tool_usage",
                "prompt": "請使用Bash工具查看當前系統的Python版本",
                "expected_elements": [
                    "Bash工具調用", "python --version", "結果解析"
                ]
            }
        ]
    
    async def evaluate_k2_vs_claude(self, k2_model_path: str = None) -> Dict:
        """評估K2模型與Claude Code的相似度"""
        logger.info("🎯 開始K2 vs Claude Code相似度評估...")
        
        evaluation_results = []
        
        # 對每個基準測試進行評估
        for benchmark in self.similarity_config["benchmark_prompts"]:
            logger.info(f"📝 測試: {benchmark['id']} ({benchmark['category']})")
            
            # 獲取Claude Code基準回應（模擬）
            claude_response = self._get_claude_baseline_response(benchmark)
            
            # 獲取K2模型回應
            k2_response = await self._get_k2_response(benchmark, k2_model_path)
            
            # 計算相似度分數
            similarity_scores = self._calculate_similarity_scores(
                benchmark, claude_response, k2_response
            )
            
            # 保存評估結果
            evaluation_result = {
                "prompt_id": benchmark["id"],
                "category": benchmark["category"],
                "claude_response": claude_response,
                "k2_response": k2_response,
                **similarity_scores,
                "timestamp": datetime.now().isoformat()
            }
            
            evaluation_results.append(evaluation_result)
            
            # 保存到數據庫
            self._save_evaluation_result(evaluation_result)
        
        # 計算總體相似度
        overall_similarity = self._calculate_overall_similarity(evaluation_results)
        
        # 生成詳細報告
        report = self._generate_similarity_report(evaluation_results, overall_similarity)
        
        return report
    
    def _get_claude_baseline_response(self, benchmark: Dict) -> str:
        """獲取Claude Code基準回應（基於實際Claude Code行為模式）"""
        
        category = benchmark["category"]
        prompt = benchmark["prompt"]
        
        # 基於Claude Code的典型回應模式生成基準
        if category == "code_analysis":
            return self._generate_claude_code_analysis_response(prompt)
        elif category == "file_operations":
            return self._generate_claude_file_ops_response(prompt)
        elif category == "debugging":
            return self._generate_claude_debugging_response(prompt)
        elif category == "explanation":
            return self._generate_claude_explanation_response(prompt)
        elif category == "problem_solving":
            return self._generate_claude_problem_solving_response(prompt)
        elif category == "tool_usage":
            return self._generate_claude_tool_usage_response(prompt)
        else:
            return self._generate_claude_general_response(prompt)
    
    def _generate_claude_code_analysis_response(self, prompt: str) -> str:
        """生成Claude Code風格的代碼分析回應"""
        return """我來分析這段Fibonacci遞歸實現：

## 功能分析
這是一個經典的Fibonacci數列遞歸實現，計算第n個Fibonacci數。

## 代碼結構
- 基本情況：n <= 1時直接返回n
- 遞歸情況：返回前兩項之和

## 潛在問題

### 1. 效率問題
時間複雜度為O(2^n)，存在大量重複計算。例如計算fib(5)時：
- fib(4) + fib(3)
- fib(3) + fib(2) + fib(2) + fib(1)
- 重複計算了多次fib(3)、fib(2)等

### 2. 棧溢出風險
深度遞歸可能導致棧溢出，特別是n較大時。

## 優化建議

1. **動態規劃**：使用備忘化或底向上方法
2. **迭代實現**：避免遞歸調用
3. **矩陣快速冪**：O(log n)時間複雜度

```python
# 優化版本 - 動態規劃
def fibonacci_dp(n):
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```

這個優化版本時間複雜度為O(n)，空間複雜度為O(1)。"""
    
    def _generate_claude_file_ops_response(self, prompt: str) -> str:
        """生成Claude Code風格的文件操作回應"""
        return """我來讀取README.md文件並總結內容。

<function_calls>
<invoke name="Read">
<parameter name="file_path">README.md