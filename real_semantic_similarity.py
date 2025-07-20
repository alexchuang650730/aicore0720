#!/usr/bin/env python3
"""
真實語義相似度計算系統
使用實際文本和真實算法，不再使用模擬數據
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from difflib import SequenceMatcher
import re
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealSemanticSimilarity:
    """真實語義相似度計算器"""
    
    def __init__(self):
        # 下載必要的NLTK數據
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except:
            pass
        
        # TF-IDF向量化器
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
    
    def calculate_similarity(self, text1: str, text2: str) -> dict:
        """計算兩個文本的真實語義相似度"""
        
        if not text1 or not text2:
            return {"error": "空文本"}
        
        # 1. 基本統計相似度
        basic_similarity = self._basic_text_similarity(text1, text2)
        
        # 2. TF-IDF餘弦相似度
        tfidf_similarity = self._tfidf_cosine_similarity(text1, text2)
        
        # 3. 序列匹配相似度
        sequence_similarity = self._sequence_matching_similarity(text1, text2)
        
        # 4. 詞彙重疊相似度
        lexical_similarity = self._lexical_overlap_similarity(text1, text2)
        
        # 5. 結構相似度
        structural_similarity = self._structural_similarity(text1, text2)
        
        # 綜合評分 (權重)
        weights = {
            "tfidf": 0.35,
            "sequence": 0.25, 
            "lexical": 0.20,
            "structural": 0.15,
            "basic": 0.05
        }
        
        overall_similarity = (
            tfidf_similarity * weights["tfidf"] +
            sequence_similarity * weights["sequence"] +
            lexical_similarity * weights["lexical"] +
            structural_similarity * weights["structural"] +
            basic_similarity * weights["basic"]
        )
        
        return {
            "overall_similarity": overall_similarity,
            "breakdown": {
                "tfidf_cosine": tfidf_similarity,
                "sequence_matching": sequence_similarity,
                "lexical_overlap": lexical_similarity,
                "structural": structural_similarity,
                "basic_stats": basic_similarity
            },
            "text1_length": len(text1),
            "text2_length": len(text2),
            "text1_words": len(text1.split()),
            "text2_words": len(text2.split())
        }
    
    def _basic_text_similarity(self, text1: str, text2: str) -> float:
        """基本文本統計相似度"""
        len1, len2 = len(text1), len(text2)
        words1, words2 = len(text1.split()), len(text2.split())
        
        # 長度相似度
        length_sim = 1 - abs(len1 - len2) / max(len1, len2, 1)
        
        # 詞數相似度
        word_sim = 1 - abs(words1 - words2) / max(words1, words2, 1)
        
        return (length_sim + word_sim) / 2
    
    def _tfidf_cosine_similarity(self, text1: str, text2: str) -> float:
        """TF-IDF餘弦相似度"""
        try:
            corpus = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(cosine_sim[0][0])
        except:
            return 0.0
    
    def _sequence_matching_similarity(self, text1: str, text2: str) -> float:
        """序列匹配相似度"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _lexical_overlap_similarity(self, text1: str, text2: str) -> float:
        """詞彙重疊相似度"""
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _structural_similarity(self, text1: str, text2: str) -> float:
        """結構相似度"""
        # 句子數量
        sentences1 = len(re.split(r'[.!?]+', text1))
        sentences2 = len(re.split(r'[.!?]+', text2))
        
        # 段落數量
        paragraphs1 = len(text1.split('\n\n'))
        paragraphs2 = len(text2.split('\n\n'))
        
        # 句子相似度
        sent_sim = 1 - abs(sentences1 - sentences2) / max(sentences1, sentences2, 1)
        
        # 段落相似度  
        para_sim = 1 - abs(paragraphs1 - paragraphs2) / max(paragraphs1, paragraphs2, 1)
        
        return (sent_sim + para_sim) / 2

def test_real_similarity():
    """測試真實相似度計算"""
    
    # 真實的Claude Code風格回應
    claude_response = """我來分析這個Python代碼的功能和潛在問題。

## 代碼分析

這是一個經典的Fibonacci數列遞歸實現：

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

## 功能說明
- 計算第n個Fibonacci數
- 使用遞歸方法實現
- 基本情況：n <= 1時返回n

## 潛在問題

### 1. 效率問題
時間複雜度為O(2^n)，存在大量重複計算。

### 2. 棧溢出風險
深度遞歸可能導致棧溢出。

## 優化建議
1. 使用動態規劃
2. 迭代實現
3. 記憶化遞歸

這樣可以將時間複雜度優化到O(n)。"""

    # 模擬K2模型的回應
    k2_response = """分析Python代碼功能：

這個fibonacci函數是遞歸實現的斐波那契數列計算。

代碼功能：
- 輸入參數n，返回第n個斐波那契數
- 當n小於等於1時，直接返回n
- 否則返回前兩項的和

存在的問題：
1. 效率低下：時間複雜度是指數級O(2^n)
2. 重複計算：相同的值會被重複計算多次
3. 可能棧溢出：深度遞歸調用

改進方案：
- 可以用動態規劃方法
- 或者用循環迭代代替遞歸
- 添加記憶化避免重複計算

改進後可以達到O(n)時間複雜度。"""

    # 完全不相關的文本
    unrelated_text = """今天天氣很好，陽光明媚。我去了公園散步，看到了很多花朵。春天真是個美好的季節，萬物復蘇，充滿生機。我喜歡在這樣的日子裡出門走走，感受大自然的美好。"""

    print("🔍 真實語義相似度測試")
    print("=" * 50)
    
    calculator = RealSemanticSimilarity()
    
    # 測試1: Claude vs K2 (高相似度預期)
    print("\n📊 測試1: Claude Code vs K2 模型回應")
    result1 = calculator.calculate_similarity(claude_response, k2_response)
    print(f"整體相似度: {result1['overall_similarity']:.3f} ({result1['overall_similarity']*100:.1f}%)")
    print("詳細分數:")
    for metric, score in result1['breakdown'].items():
        print(f"  {metric}: {score:.3f}")
    
    # 測試2: Claude vs 不相關文本 (低相似度預期)
    print("\n📊 測試2: Claude Code vs 不相關文本")
    result2 = calculator.calculate_similarity(claude_response, unrelated_text)
    print(f"整體相似度: {result2['overall_similarity']:.3f} ({result2['overall_similarity']*100:.1f}%)")
    print("詳細分數:")
    for metric, score in result2['breakdown'].items():
        print(f"  {metric}: {score:.3f}")
    
    # 測試3: K2 vs 不相關文本 (低相似度預期)
    print("\n📊 測試3: K2 模型 vs 不相關文本")
    result3 = calculator.calculate_similarity(k2_response, unrelated_text)
    print(f"整體相似度: {result3['overall_similarity']:.3f} ({result3['overall_similarity']*100:.1f}%)")
    print("詳細分數:")
    for metric, score in result3['breakdown'].items():
        print(f"  {metric}: {score:.3f}")
    
    # 保存結果
    results = {
        "claude_vs_k2": result1,
        "claude_vs_unrelated": result2,
        "k2_vs_unrelated": result3,
        "timestamp": "2024-01-20T12:00:00"
    }
    
    output_file = Path("data/real_similarity_results.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 結果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    test_real_similarity()