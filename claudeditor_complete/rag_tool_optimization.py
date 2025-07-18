#!/usr/bin/env python3
"""
PowerAutomation RAG + 工具調用能力優化系統
重點提升K2模型的RAG檢索和工具交互能力，達到Claude水準
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import sqlite3
from datetime import datetime
import inspect

logger = logging.getLogger(__name__)

@dataclass
class ToolFunction:
    """工具函數定義"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    examples: List[str]
    category: str

@dataclass
class RAGDocument:
    """RAG文檔結構"""
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    relevance_score: float = 0.0

class EnhancedRAGSystem:
    """增強的RAG系統 - 針對開發者場景優化"""
    
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.vector_store = None
        self.document_store = {}
        self.query_cache = {}
        
        # 專業知識庫
        self.knowledge_bases = {
            "code_patterns": CodePatternKB(),
            "frameworks": FrameworkKB(), 
            "best_practices": BestPracticeKB(),
            "troubleshooting": TroubleshootingKB()
        }
        
        logger.info("🧠 增強RAG系統初始化完成")
    
    async def initialize_vector_store(self, documents: List[RAGDocument]):
        """初始化向量存儲"""
        try:
            # 生成文檔嵌入
            texts = [doc.content for doc in documents]
            embeddings = self.embedding_model.encode(texts)
            
            # 創建FAISS索引
            dimension = embeddings.shape[1]
            self.vector_store = faiss.IndexFlatIP(dimension)  # 內積搜索
            self.vector_store.add(embeddings.astype('float32'))
            
            # 存儲文檔映射
            for i, doc in enumerate(documents):
                doc.embedding = embeddings[i]
                self.document_store[i] = doc
            
            logger.info(f"✅ 向量存儲初始化完成: {len(documents)}個文檔")
            
        except Exception as e:
            logger.error(f"❌ 向量存儲初始化失敗: {e}")
            raise
    
    async def smart_retrieval(self, query: str, context: Dict[str, Any], top_k: int = 10) -> List[RAGDocument]:
        """智能檢索 - 結合上下文的多層次檢索"""
        try:
            # 查詢分析和重寫
            enhanced_query = await self._enhance_query(query, context)
            
            # 多層次檢索策略
            retrieval_results = []
            
            # 1. 語義檢索
            semantic_docs = await self._semantic_search(enhanced_query, top_k // 2)
            retrieval_results.extend(semantic_docs)
            
            # 2. 關鍵詞檢索  
            keyword_docs = await self._keyword_search(query, top_k // 4)
            retrieval_results.extend(keyword_docs)
            
            # 3. 上下文相關檢索
            context_docs = await self._context_aware_search(query, context, top_k // 4)
            retrieval_results.extend(context_docs)
            
            # 去重和重排序
            unique_docs = self._deduplicate_and_rerank(retrieval_results, query, context)
            
            return unique_docs[:top_k]
            
        except Exception as e:
            logger.error(f"❌ 智能檢索失敗: {e}")
            return []
    
    async def _enhance_query(self, query: str, context: Dict[str, Any]) -> str:
        """查詢增強 - 基於上下文豐富查詢"""
        enhanced_parts = [query]
        
        # 添加技術棧上下文
        if "tech_stack" in context:
            tech_context = " ".join(context["tech_stack"])
            enhanced_parts.append(f"使用技術棧: {tech_context}")
        
        # 添加項目上下文
        if "project_type" in context:
            enhanced_parts.append(f"項目類型: {context['project_type']}")
        
        # 添加用戶角色上下文
        if "user_role" in context:
            enhanced_parts.append(f"用戶角色: {context['user_role']}")
        
        return " ".join(enhanced_parts)
    
    async def _semantic_search(self, query: str, k: int) -> List[RAGDocument]:
        """語義搜索"""
        if not self.vector_store:
            return []
        
        # 查詢向量化
        query_embedding = self.embedding_model.encode([query])
        
        # FAISS搜索
        scores, indices = self.vector_store.search(query_embedding.astype('float32'), k)
        
        # 構建結果
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx in self.document_store:
                doc = self.document_store[idx]
                doc.relevance_score = float(score)
                results.append(doc)
        
        return results
    
    async def _keyword_search(self, query: str, k: int) -> List[RAGDocument]:
        """關鍵詞搜索"""
        # 簡化的關鍵詞匹配
        query_terms = set(query.lower().split())
        scored_docs = []
        
        for doc in self.document_store.values():
            doc_terms = set(doc.content.lower().split())
            overlap = len(query_terms.intersection(doc_terms))
            
            if overlap > 0:
                score = overlap / len(query_terms)
                doc_copy = RAGDocument(
                    doc_id=doc.doc_id,
                    content=doc.content,
                    metadata=doc.metadata,
                    relevance_score=score
                )
                scored_docs.append(doc_copy)
        
        # 按分數排序
        scored_docs.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored_docs[:k]
    
    async def _context_aware_search(self, query: str, context: Dict[str, Any], k: int) -> List[RAGDocument]:
        """上下文感知搜索"""
        # 基於上下文的專業知識庫搜索
        context_docs = []
        
        # 根據查詢類型選擇合適的知識庫
        if "code" in query.lower() or "function" in query.lower():
            kb_docs = await self.knowledge_bases["code_patterns"].search(query, k//2)
            context_docs.extend(kb_docs)
        
        if any(fw in query.lower() for fw in ["react", "vue", "angular", "fastapi", "django"]):
            kb_docs = await self.knowledge_bases["frameworks"].search(query, k//2)
            context_docs.extend(kb_docs)
        
        return context_docs
    
    def _deduplicate_and_rerank(self, docs: List[RAGDocument], query: str, context: Dict[str, Any]) -> List[RAGDocument]:
        """去重和重排序"""
        # 基於doc_id去重
        seen_ids = set()
        unique_docs = []
        
        for doc in docs:
            if doc.doc_id not in seen_ids:
                seen_ids.add(doc.doc_id)
                unique_docs.append(doc)
        
        # 重排序 - 綜合相關性和上下文匹配度
        for doc in unique_docs:
            context_bonus = self._calculate_context_bonus(doc, context)
            doc.relevance_score += context_bonus
        
        # 按最終分數排序
        unique_docs.sort(key=lambda x: x.relevance_score, reverse=True)
        return unique_docs
    
    def _calculate_context_bonus(self, doc: RAGDocument, context: Dict[str, Any]) -> float:
        """計算上下文獎勵分數"""
        bonus = 0.0
        
        # 技術棧匹配獎勵
        if "tech_stack" in context:
            for tech in context["tech_stack"]:
                if tech.lower() in doc.content.lower():
                    bonus += 0.1
        
        # 項目類型匹配獎勵
        if "project_type" in context and context["project_type"].lower() in doc.content.lower():
            bonus += 0.2
        
        # 文檔新鮮度獎勵
        if "last_updated" in doc.metadata:
            days_old = (datetime.now() - datetime.fromisoformat(doc.metadata["last_updated"])).days
            freshness_bonus = max(0, 0.1 - days_old * 0.001)  # 越新獎勵越高
            bonus += freshness_bonus
        
        return bonus

class AdvancedToolCallSystem:
    """高級工具調用系統 - 智能工具選擇和組合"""
    
    def __init__(self):
        self.tools = {}
        self.tool_categories = {}
        self.execution_history = []
        self.tool_performance_stats = {}
        
        # 註冊基礎工具
        self._register_default_tools()
        
        logger.info("🔧 高級工具調用系統初始化完成")
    
    def _register_default_tools(self):
        """註冊默認工具集"""
        
        # 代碼執行工具
        self.register_tool(ToolFunction(
            name="execute_python",
            description="執行Python代碼並返回結果",
            parameters={
                "code": {"type": "string", "description": "要執行的Python代碼"},
                "timeout": {"type": "integer", "description": "執行超時時間(秒)", "default": 30}
            },
            function=self._execute_python_code,
            examples=[
                "計算斐波那契數列",
                "數據分析和可視化",
                "API測試腳本"
            ],
            category="code_execution"
        ))
        
        # 文件操作工具
        self.register_tool(ToolFunction(
            name="read_file",
            description="讀取文件內容",
            parameters={
                "file_path": {"type": "string", "description": "文件路徑"},
                "encoding": {"type": "string", "description": "文件編碼", "default": "utf-8"}
            },
            function=self._read_file,
            examples=[
                "讀取配置文件",
                "分析日誌文件",
                "檢查代碼文件"
            ],
            category="file_operations"
        ))
        
        # Web請求工具
        self.register_tool(ToolFunction(
            name="web_request",
            description="發送HTTP請求",
            parameters={
                "url": {"type": "string", "description": "請求URL"},
                "method": {"type": "string", "description": "HTTP方法", "default": "GET"},
                "headers": {"type": "object", "description": "請求頭", "default": {}},
                "data": {"type": "object", "description": "請求數據", "default": {}}
            },
            function=self._web_request,
            examples=[
                "API接口測試",
                "獲取網頁內容",
                "調用第三方服務"
            ],
            category="web_requests"
        ))
        
        # 數據庫查詢工具
        self.register_tool(ToolFunction(
            name="database_query",
            description="執行數據庫查詢",
            parameters={
                "query": {"type": "string", "description": "SQL查詢語句"},
                "connection_string": {"type": "string", "description": "數據庫連接字符串"}
            },
            function=self._database_query,
            examples=[
                "查詢用戶數據",
                "分析業務指標",
                "數據庫性能檢查"
            ],
            category="database"
        ))
    
    def register_tool(self, tool: ToolFunction):
        """註冊新工具"""
        self.tools[tool.name] = tool
        
        if tool.category not in self.tool_categories:
            self.tool_categories[tool.category] = []
        self.tool_categories[tool.category].append(tool.name)
        
        # 初始化性能統計
        self.tool_performance_stats[tool.name] = {
            "total_calls": 0,
            "success_rate": 1.0,
            "avg_execution_time": 0.0,
            "user_satisfaction": 0.0
        }
        
        logger.info(f"🔧 工具已註冊: {tool.name}")
    
    async def intelligent_tool_selection(self, query: str, context: Dict[str, Any]) -> List[str]:
        """智能工具選擇"""
        try:
            # 分析查詢意圖
            intent = await self._analyze_query_intent(query)
            
            # 基於意圖選擇工具類別
            relevant_categories = self._map_intent_to_categories(intent)
            
            # 從相關類別中選擇最佳工具
            selected_tools = []
            for category in relevant_categories:
                if category in self.tool_categories:
                    # 根據性能統計選擇最佳工具
                    best_tool = self._select_best_tool_in_category(category, context)
                    if best_tool:
                        selected_tools.append(best_tool)
            
            # 工具組合優化
            optimized_tools = self._optimize_tool_combination(selected_tools, query)
            
            return optimized_tools
            
        except Exception as e:
            logger.error(f"❌ 智能工具選擇失敗: {e}")
            return []
    
    async def _analyze_query_intent(self, query: str) -> Dict[str, float]:
        """分析查詢意圖"""
        intent_keywords = {
            "code_execution": ["執行", "運行", "測試", "計算", "處理"],
            "file_operations": ["讀取", "寫入", "文件", "保存", "加載"],
            "web_requests": ["請求", "API", "下載", "爬取", "調用"],
            "database": ["查詢", "數據庫", "SQL", "數據", "表"],
            "analysis": ["分析", "統計", "報告", "圖表", "可視化"]
        }
        
        intent_scores = {}
        query_lower = query.lower()
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            intent_scores[intent] = score / len(keywords)
        
        return intent_scores
    
    def _map_intent_to_categories(self, intent_scores: Dict[str, float]) -> List[str]:
        """將意圖映射到工具類別"""
        # 選擇分數最高的意圖
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        
        relevant_categories = []
        for intent, score in sorted_intents:
            if score > 0:
                relevant_categories.append(intent)
        
        return relevant_categories
    
    def _select_best_tool_in_category(self, category: str, context: Dict[str, Any]) -> Optional[str]:
        """在類別中選擇最佳工具"""
        if category not in self.tool_categories:
            return None
        
        category_tools = self.tool_categories[category]
        
        # 基於性能統計選擇
        best_tool = None
        best_score = 0
        
        for tool_name in category_tools:
            stats = self.tool_performance_stats[tool_name]
            # 綜合成功率、執行時間和用戶滿意度
            score = (stats["success_rate"] * 0.4 + 
                    (1 / max(stats["avg_execution_time"], 0.1)) * 0.3 + 
                    stats["user_satisfaction"] * 0.3)
            
            if score > best_score:
                best_score = score
                best_tool = tool_name
        
        return best_tool
    
    def _optimize_tool_combination(self, tools: List[str], query: str) -> List[str]:
        """優化工具組合"""
        # 簡化版本：去重並按優先級排序
        unique_tools = list(dict.fromkeys(tools))  # 保持順序的去重
        
        # 根據查詢複雜度限制工具數量
        max_tools = 3 if len(query) > 100 else 2
        
        return unique_tools[:max_tools]
    
    async def execute_tool_chain(self, tools: List[str], query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行工具鏈"""
        results = {}
        execution_context = context.copy()
        
        for tool_name in tools:
            if tool_name not in self.tools:
                continue
            
            try:
                start_time = time.time()
                
                # 智能參數提取
                parameters = await self._extract_tool_parameters(tool_name, query, execution_context)
                
                # 執行工具
                tool = self.tools[tool_name]
                result = await tool.function(**parameters)
                
                # 記錄執行時間
                execution_time = time.time() - start_time
                
                # 更新性能統計
                self._update_tool_performance(tool_name, True, execution_time)
                
                # 將結果添加到上下文
                results[tool_name] = result
                execution_context[f"{tool_name}_result"] = result
                
                logger.info(f"✅ 工具執行成功: {tool_name}")
                
            except Exception as e:
                logger.error(f"❌ 工具執行失敗: {tool_name} - {e}")
                self._update_tool_performance(tool_name, False, 0)
                results[tool_name] = {"error": str(e)}
        
        return results
    
    async def _extract_tool_parameters(self, tool_name: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """智能提取工具參數"""
        tool = self.tools[tool_name]
        parameters = {}
        
        # 簡化的參數提取邏輯
        for param_name, param_info in tool.parameters.items():
            if param_name in context:
                parameters[param_name] = context[param_name]
            elif "default" in param_info:
                parameters[param_name] = param_info["default"]
            else:
                # 從查詢中提取參數（簡化版）
                extracted_value = self._extract_from_query(param_name, query, param_info)
                if extracted_value is not None:
                    parameters[param_name] = extracted_value
        
        return parameters
    
    def _extract_from_query(self, param_name: str, query: str, param_info: Dict[str, Any]) -> Any:
        """從查詢中提取參數值"""
        # 這裡應該有更複雜的NLP邏輯，現在用簡化版本
        if param_name == "code" and "```python" in query:
            # 提取代碼塊
            start = query.find("```python") + 9
            end = query.find("```", start)
            if end > start:
                return query[start:end].strip()
        
        return None
    
    def _update_tool_performance(self, tool_name: str, success: bool, execution_time: float):
        """更新工具性能統計"""
        stats = self.tool_performance_stats[tool_name]
        
        stats["total_calls"] += 1
        
        # 更新成功率
        old_success_rate = stats["success_rate"]
        new_success_rate = (old_success_rate * (stats["total_calls"] - 1) + (1 if success else 0)) / stats["total_calls"]
        stats["success_rate"] = new_success_rate
        
        # 更新平均執行時間
        if success and execution_time > 0:
            old_avg_time = stats["avg_execution_time"]
            successful_calls = stats["total_calls"] * old_success_rate
            new_avg_time = (old_avg_time * (successful_calls - 1) + execution_time) / successful_calls
            stats["avg_execution_time"] = new_avg_time
    
    # 工具實現方法
    async def _execute_python_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """執行Python代碼"""
        # 安全的代碼執行環境
        try:
            # 這裡應該使用沙盒環境
            # 現在用簡化的exec實現
            local_vars = {}
            exec(code, {"__builtins__": {}}, local_vars)
            return {"success": True, "result": local_vars}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """讀取文件"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _web_request(self, url: str, method: str = "GET", headers: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """發送Web請求"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, json=data) as response:
                    result_data = await response.text()
                    return {
                        "success": True,
                        "status": response.status,
                        "data": result_data
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _database_query(self, query: str, connection_string: str) -> Dict[str, Any]:
        """執行數據庫查詢"""
        try:
            # 這裡應該根據connection_string類型選擇不同的數據庫驅動
            # 現在用SQLite作為示例
            import sqlite3
            conn = sqlite3.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

# 知識庫類定義
class CodePatternKB:
    """代碼模式知識庫"""
    async def search(self, query: str, k: int) -> List[RAGDocument]:
        # 模擬代碼模式搜索
        return []

class FrameworkKB:
    """框架知識庫"""
    async def search(self, query: str, k: int) -> List[RAGDocument]:
        # 模擬框架知識搜索
        return []

class BestPracticeKB:
    """最佳實踐知識庫"""
    async def search(self, query: str, k: int) -> List[RAGDocument]:
        # 模擬最佳實踐搜索
        return []

class TroubleshootingKB:
    """故障排除知識庫"""
    async def search(self, query: str, k: int) -> List[RAGDocument]:
        # 模擬故障排除搜索
        return []

# 主要集成類
class PowerAutomationRAGToolSystem:
    """PowerAutomation RAG + 工具調用集成系統"""
    
    def __init__(self):
        self.rag_system = EnhancedRAGSystem()
        self.tool_system = AdvancedToolCallSystem()
        self.integration_stats = {
            "total_queries": 0,
            "rag_enhanced_queries": 0,
            "tool_assisted_queries": 0,
            "avg_response_quality": 0.0
        }
        
        logger.info("🚀 PowerAutomation RAG+工具調用系統初始化完成")
    
    async def process_enhanced_query(self, query: str, context: Dict[str, Any], k2_model_client) -> Dict[str, Any]:
        """處理增強查詢 - RAG + 工具調用 + K2模型"""
        try:
            start_time = time.time()
            
            # 1. RAG檢索增強
            rag_documents = await self.rag_system.smart_retrieval(query, context, top_k=10)
            rag_context = self._build_rag_context(rag_documents)
            
            # 2. 智能工具選擇
            relevant_tools = await self.tool_system.intelligent_tool_selection(query, context)
            
            # 3. 構建增強的提示
            enhanced_prompt = self._build_enhanced_prompt(query, rag_context, relevant_tools, context)
            
            # 4. K2模型調用
            k2_response = await k2_model_client.chat_completion(enhanced_prompt)
            
            # 5. 工具執行（如果需要）
            tool_results = {}
            if relevant_tools and self._should_execute_tools(k2_response):
                tool_results = await self.tool_system.execute_tool_chain(relevant_tools, query, context)
            
            # 6. 結果整合
            final_response = self._integrate_results(k2_response, tool_results, rag_documents)
            
            # 7. 更新統計
            processing_time = time.time() - start_time
            await self._update_system_stats(query, rag_documents, tool_results, processing_time)
            
            return {
                "success": True,
                "response": final_response,
                "rag_sources": len(rag_documents),
                "tools_used": list(tool_results.keys()),
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"❌ 增強查詢處理失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，處理您的請求時出現錯誤。"
            }
    
    def _build_rag_context(self, documents: List[RAGDocument]) -> str:
        """構建RAG上下文"""
        if not documents:
            return ""
        
        context_parts = ["# 相關知識和參考資料\n"]
        
        for i, doc in enumerate(documents[:5]):  # 只使用前5個最相關的文檔
            context_parts.append(f"## 參考資料 {i+1} (相關度: {doc.relevance_score:.2f})")
            context_parts.append(doc.content[:500] + "..." if len(doc.content) > 500 else doc.content)
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _build_enhanced_prompt(self, query: str, rag_context: str, tools: List[str], context: Dict[str, Any]) -> str:
        """構建增強提示"""
        prompt_parts = []
        
        # 系統提示
        prompt_parts.append("""你是PowerAutomation的高級AI助手，專門幫助開發者解決編程和開發問題。

你的能力包括：
1. 基於豐富的知識庫提供準確的技術建議
2. 調用各種工具來執行實際操作
3. 生成高質量的代碼和解決方案
4. 提供詳細的解釋和最佳實踐

請根據提供的上下文信息和可用工具，給出完整、準確、實用的回答。""")
        
        # RAG上下文
        if rag_context:
            prompt_parts.append(f"\n{rag_context}")
        
        # 可用工具信息
        if tools:
            tool_info = []
            for tool_name in tools:
                if tool_name in self.tool_system.tools:
                    tool = self.tool_system.tools[tool_name]
                    tool_info.append(f"- {tool_name}: {tool.description}")
            
            if tool_info:
                prompt_parts.append(f"\n# 可用工具\n" + "\n".join(tool_info))
        
        # 用戶查詢
        prompt_parts.append(f"\n# 用戶問題\n{query}")
        
        # 上下文信息
        if context:
            context_info = []
            for key, value in context.items():
                if key not in ["tech_stack", "project_type", "user_role"]:
                    continue
                context_info.append(f"- {key}: {value}")
            
            if context_info:
                prompt_parts.append(f"\n# 上下文信息\n" + "\n".join(context_info))
        
        return "\n".join(prompt_parts)
    
    def _should_execute_tools(self, k2_response: str) -> bool:
        """判斷是否需要執行工具"""
        # 簡化的判斷邏輯
        tool_indicators = ["執行", "運行", "測試", "查詢", "檢查", "調用"]
        response_lower = k2_response.lower()
        
        return any(indicator in response_lower for indicator in tool_indicators)
    
    def _integrate_results(self, k2_response: str, tool_results: Dict[str, Any], rag_docs: List[RAGDocument]) -> str:
        """整合結果"""
        result_parts = [k2_response]
        
        # 添加工具執行結果
        if tool_results:
            result_parts.append("\n## 執行結果")
            for tool_name, result in tool_results.items():
                if result.get("success"):
                    result_parts.append(f"### {tool_name}")
                    result_parts.append(f"```\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```")
                else:
                    result_parts.append(f"### {tool_name} (執行失敗)")
                    result_parts.append(f"錯誤: {result.get('error', '未知錯誤')}")
        
        # 添加參考資料
        if rag_docs:
            result_parts.append(f"\n## 參考資料來源")
            for i, doc in enumerate(rag_docs[:3]):
                result_parts.append(f"{i+1}. {doc.metadata.get('title', '相關文檔')} (相關度: {doc.relevance_score:.2f})")
        
        return "\n".join(result_parts)
    
    async def _update_system_stats(self, query: str, rag_docs: List[RAGDocument], tool_results: Dict[str, Any], processing_time: float):
        """更新系統統計"""
        self.integration_stats["total_queries"] += 1
        
        if rag_docs:
            self.integration_stats["rag_enhanced_queries"] += 1
        
        if tool_results:
            self.integration_stats["tool_assisted_queries"] += 1
        
        # 這裡可以添加更複雜的質量評估邏輯
        estimated_quality = self._estimate_response_quality(query, rag_docs, tool_results, processing_time)
        
        total_queries = self.integration_stats["total_queries"]
        current_avg = self.integration_stats["avg_response_quality"]
        new_avg = (current_avg * (total_queries - 1) + estimated_quality) / total_queries
        self.integration_stats["avg_response_quality"] = new_avg
    
    def _estimate_response_quality(self, query: str, rag_docs: List[RAGDocument], tool_results: Dict[str, Any], processing_time: float) -> float:
        """估算回應質量"""
        quality_score = 5.0  # 基礎分數
        
        # RAG增強獎勵
        if rag_docs:
            quality_score += min(len(rag_docs) * 0.5, 2.0)
        
        # 工具使用獎勵
        if tool_results:
            successful_tools = sum(1 for result in tool_results.values() if result.get("success"))
            quality_score += successful_tools * 0.5
        
        # 處理時間懲罰
        if processing_time > 10:
            quality_score -= (processing_time - 10) * 0.1
        
        return min(max(quality_score, 0), 10)  # 限制在0-10範圍內

# 使用示例
async def main():
    """主函數示例"""
    # 初始化系統
    system = PowerAutomationRAGToolSystem()
    
    # 模擬文檔初始化
    sample_docs = [
        RAGDocument(
            doc_id="doc_001",
            content="React組件最佳實踐包括使用函數式組件、適當的狀態管理、性能優化等...",
            metadata={"title": "React最佳實踐", "category": "frontend", "last_updated": "2024-01-15"}
        ),
        RAGDocument(
            doc_id="doc_002", 
            content="Python異步編程使用async/await語法，可以大大提高I/O密集型任務的性能...",
            metadata={"title": "Python異步編程", "category": "backend", "last_updated": "2024-01-10"}
        )
    ]
    
    await system.rag_system.initialize_vector_store(sample_docs)
    
    # 模擬查詢
    query = "如何優化React組件的性能？"
    context = {
        "tech_stack": ["react", "javascript"],
        "project_type": "web_frontend",
        "user_role": "frontend_developer"
    }
    
    # 模擬K2客戶端
    class MockK2Client:
        async def chat_completion(self, prompt):
            return "根據您的查詢，這裡是關於React性能優化的建議..."
    
    k2_client = MockK2Client()
    
    # 處理查詢
    result = await system.process_enhanced_query(query, context, k2_client)
    
    print("查詢結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())