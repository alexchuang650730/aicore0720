#!/usr/bin/env python3
"""
K2+DeepSWE+MemoryRAG 真實推理引擎
使用 Groq API 和 Kimi K2 模型
"""

import json
import os
import logging
from typing import Dict, List, Optional
from groq import Groq
import asyncio
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class K2GroqInferenceEngine:
    """使用 Groq API 的 K2 推理引擎"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "moonshotai/kimi-k2-instruct"
        
        # 記憶庫
        self.memory_bank = []
        self.max_memories = 100
        
        # 工具映射
        self.tool_mapping = {
            "Read": "讀取文件內容",
            "Write": "寫入文件",
            "Edit": "編輯文件",
            "MultiEdit": "批量編輯文件",
            "Grep": "搜索文件內容",
            "Glob": "查找文件",
            "LS": "列出目錄",
            "Task": "執行任務搜索",
            "Bash": "執行shell命令",
            "TodoWrite": "管理待辦事項"
        }
        
        logger.info(f"✅ K2 Groq 推理引擎初始化完成")
        
    def generate_response(self, 
                         prompt: str, 
                         context: Optional[List[Dict]] = None,
                         temperature: float = 0.6,
                         max_tokens: int = 1024) -> str:
        """生成回應"""
        
        # 構建消息
        messages = []
        
        # 添加上下文
        if context:
            for ctx in context[-5:]:  # 最近5條上下文
                messages.append(ctx)
        
        # 添加記憶檢索
        relevant_memories = self._retrieve_memories(prompt)
        if relevant_memories:
            memory_context = "\n相關記憶:\n" + "\n".join(relevant_memories)
            messages.append({
                "role": "system",
                "content": memory_context
            })
        
        # 添加當前提示
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            # 調用 K2 模型
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=1,
                stream=False
            )
            
            response = completion.choices[0].message.content
            
            # 更新記憶
            self._update_memory(prompt, response)
            
            return response
            
        except Exception as e:
            logger.error(f"生成回應失敗: {e}")
            return f"抱歉，生成回應時發生錯誤: {str(e)}"
    
    def generate_with_tools(self, 
                           prompt: str,
                           available_tools: List[str] = None) -> Dict:
        """生成包含工具調用的回應"""
        
        # 構建工具提示
        if available_tools is None:
            available_tools = list(self.tool_mapping.keys())
        
        tool_prompt = f"""
你是一個強大的 AI 助手，可以使用以下工具:
{', '.join([f'{tool}({self.tool_mapping[tool]})' for tool in available_tools])}

當需要使用工具時，請使用以下格式:
<function_calls>
<invoke name="工具名">
<parameter name="參數名">參數值</parameter>
</invoke>
</function_calls>

用戶請求: {prompt}
"""
        
        response = self.generate_response(tool_prompt)
        
        # 解析工具調用
        tool_calls = self._parse_tool_calls(response)
        
        return {
            "response": response,
            "tool_calls": tool_calls,
            "has_tools": len(tool_calls) > 0
        }
    
    def _retrieve_memories(self, query: str, top_k: int = 3) -> List[str]:
        """檢索相關記憶"""
        if not self.memory_bank:
            return []
        
        # 簡單的關鍵詞匹配（實際應用中應使用向量相似度）
        relevant = []
        query_words = set(query.lower().split())
        
        for memory in self.memory_bank:
            memory_words = set(memory['content'].lower().split())
            overlap = len(query_words & memory_words)
            if overlap > 0:
                relevant.append((overlap, memory['content']))
        
        # 排序並返回top-k
        relevant.sort(reverse=True, key=lambda x: x[0])
        return [mem[1] for mem in relevant[:top_k]]
    
    def _update_memory(self, query: str, response: str):
        """更新記憶庫"""
        memory_entry = {
            "timestamp": time.time(),
            "query": query,
            "response": response,
            "content": f"Q: {query[:100]}... A: {response[:100]}..."
        }
        
        self.memory_bank.append(memory_entry)
        
        # 保持記憶庫大小
        if len(self.memory_bank) > self.max_memories:
            self.memory_bank.pop(0)
    
    def _parse_tool_calls(self, response: str) -> List[Dict]:
        """解析工具調用"""
        import re
        
        tool_calls = []
        
        # 查找 function_calls 塊
        function_blocks = re.findall(
            r'<function_calls>(.*?)</function_calls>', 
            response, 
            re.DOTALL
        )
        
        for block in function_blocks:
            # 解析每個 invoke
            invokes = re.findall(
                r'<invoke name="([^"]+)">(.*?)</invoke>', 
                block, 
                re.DOTALL
            )
            
            for tool_name, params_content in invokes:
                # 解析參數
                params = {}
                param_matches = re.findall(
                    r'<parameter name="([^"]+)">([^<]*)</parameter>',
                    params_content
                )
                
                for param_name, param_value in param_matches:
                    params[param_name] = param_value
                
                tool_calls.append({
                    "tool": tool_name,
                    "parameters": params
                })
        
        return tool_calls


class K2ComparisonTester:
    """K2 模型對比測試器"""
    
    def __init__(self, api_key: str):
        self.engine = K2GroqInferenceEngine(api_key)
        
    def test_semantic_similarity(self, test_prompts: List[str]):
        """測試語義相似度"""
        logger.info("🧪 開始K2語義相似度測試...")
        
        results = []
        
        for prompt in test_prompts:
            logger.info(f"\n📝 測試提示: {prompt}")
            
            # 生成 K2 回應
            k2_response = self.engine.generate_response(prompt)
            
            logger.info(f"💬 K2 回應: {k2_response[:200]}...")
            
            results.append({
                "prompt": prompt,
                "k2_response": k2_response
            })
        
        return results
    
    def test_tool_calling(self, tool_prompts: List[str]):
        """測試工具調用能力"""
        logger.info("\n🔧 開始K2工具調用測試...")
        
        results = []
        
        for prompt in tool_prompts:
            logger.info(f"\n📝 測試提示: {prompt}")
            
            # 生成包含工具的回應
            result = self.engine.generate_with_tools(prompt)
            
            logger.info(f"🛠️ 工具調用: {result['tool_calls']}")
            
            results.append({
                "prompt": prompt,
                "response": result['response'],
                "tool_calls": result['tool_calls'],
                "has_tools": result['has_tools']
            })
        
        return results


def main():
    """主測試函數"""
    
    # 使用提供的 API key
    api_key = "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"
    
    # 創建測試器
    tester = K2ComparisonTester(api_key)
    
    # 測試提示
    test_prompts = [
        "請解釋一下什麼是機器學習",
        "如何優化 Python 代碼的性能？",
        "寫一個快速排序算法"
    ]
    
    tool_prompts = [
        "請幫我讀取 config.json 文件",
        "搜索所有包含 TODO 的 Python 文件",
        "創建一個新的測試文件 test.py"
    ]
    
    # 執行測試
    logger.info("🚀 開始 K2 模型測試...\n")
    
    # 語義測試
    semantic_results = tester.test_semantic_similarity(test_prompts)
    
    # 工具測試
    tool_results = tester.test_tool_calling(tool_prompts)
    
    # 保存結果
    results = {
        "semantic_tests": semantic_results,
        "tool_tests": tool_results,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("k2_groq_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info("\n✅ 測試完成！結果已保存到 k2_groq_test_results.json")


if __name__ == "__main__":
    main()