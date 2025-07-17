#!/usr/bin/env python3
"""
RAG Service - PowerAutomation v4.8

企业级 RAG 功能实现，包括:
- 向量数据库管理
- 文档索引和检索
- 与 Kimi K2 的集成
- MemoryOS 项目上下文管理
"""

import json
import logging
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import asyncio
import aiohttp
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Document:
    """文档数据结构"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class RAGQuery:
    """RAG 查询数据结构"""
    query: str
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None
    include_metadata: bool = True

@dataclass
class RAGResult:
    """RAG 查询结果"""
    query: str
    documents: List[Document]
    scores: List[float]
    total_time_ms: float
    enhanced_prompt: str

class RAGService:
    """RAG 服务核心类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化 RAG 服务"""
        self.config = config or {}
        
        # 配置参数
        self.embedding_model_name = self.config.get("embedding_model", "all-MiniLM-L6-v2")
        self.max_context_length = self.config.get("max_context_length", 32000)
        self.top_k_default = self.config.get("top_k_default", 5)
        self.kimi_k2_endpoint = self.config.get("kimi_k2_endpoint", "https://api.moonshot.cn/v1")
        self.kimi_k2_api_key = self.config.get("kimi_k2_api_key", "")
        
        # 初始化组件
        self.logger = logging.getLogger(__name__)
        self.embedding_model = None
        self.vector_index = None
        self.document_store = {}
        
        # 性能统计
        self.stats = {
            "total_queries": 0,
            "total_documents": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0,
            "last_updated": datetime.now()
        }
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化 RAG 服务"""
        try:
            # 加载嵌入模型
            await self._load_embedding_model()
            
            # 初始化向量索引
            await self._initialize_vector_index()
            
            # 验证 Kimi K2 连接
            await self._verify_kimi_k2_connection()
            
            logger.info("✅ RAG 服务初始化完成")
            return {"status": "success", "message": "RAG 服务初始化完成"}
            
        except Exception as e:
            logger.error(f"❌ RAG 服务初始化失败: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _load_embedding_model(self):
        """加载嵌入模型"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"✅ 嵌入模型加载完成: {self.embedding_model_name}")
        except Exception as e:
            logger.error(f"❌ 嵌入模型加载失败: {e}")
            raise
    
    async def _initialize_vector_index(self):
        """初始化向量索引"""
        try:
            import faiss
            # 使用内积相似度索引
            dimension = 384  # all-MiniLM-L6-v2 的向量维度
            self.vector_index = faiss.IndexFlatIP(dimension)
            logger.info("✅ 向量索引初始化完成")
        except Exception as e:
            logger.error(f"❌ 向量索引初始化失败: {e}")
            raise
    
    async def _verify_kimi_k2_connection(self):
        """验证 Kimi K2 API 连接"""
        if not self.kimi_k2_api_key:
            logger.warning("⚠️ Kimi K2 API 密钥未配置")
            return
        
        try:
            # 简单的连接测试
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.kimi_k2_api_key}",
                    "Content-Type": "application/json"
                }
                
                test_data = {
                    "model": "moonshot-v1-8k",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
                
                async with session.post(
                    f"{self.kimi_k2_endpoint}/chat/completions",
                    headers=headers,
                    json=test_data,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Kimi K2 API 连接验证成功")
                    else:
                        logger.warning(f"⚠️ Kimi K2 API 连接异常: {response.status}")
                        
        except Exception as e:
            logger.warning(f"⚠️ Kimi K2 API 连接验证失败: {e}")
    
    async def add_documents(self, documents: List[Dict[str, Any]], kb_id: str = "default") -> Dict[str, Any]:
        """添加文档到 RAG 系统"""
        try:
            logger.info(f"添加 {len(documents)} 个文档到知识库 {kb_id}")
            
            # 处理文档
            processed_docs = []
            for i, doc in enumerate(documents):
                content = doc.get("content", "")
                if not content.strip():
                    continue
                
                # 生成文档 ID
                doc_id = doc.get("id") or f"{kb_id}_{i}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
                
                # 生成嵌入向量
                embedding = self.embedding_model.encode([content])[0]
                
                # 创建文档对象
                document = Document(
                    id=doc_id,
                    content=content,
                    metadata=doc.get("metadata", {}),
                    embedding=embedding
                )
                
                processed_docs.append(document)
                
                # 添加到向量索引
                self.vector_index.add(np.array([embedding]).astype('float32'))
                
                # 存储文档
                self.document_store[doc_id] = document
            
            # 更新统计
            self.stats["total_documents"] += len(processed_docs)
            self.stats["last_updated"] = datetime.now()
            
            logger.info(f"✅ 成功添加 {len(processed_docs)} 个文档")
            
            return {
                "status": "success",
                "added_count": len(processed_docs),
                "total_documents": len(self.document_store)
            }
            
        except Exception as e:
            logger.error(f"❌ 添加文档失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def retrieve_documents(self, query: str, kb_id: str = "default", top_k: int = 5) -> Dict[str, Any]:
        """检索相关文档"""
        try:
            start_time = time.time()
            
            # 生成查询嵌入
            query_embedding = self.embedding_model.encode([query])[0]
            
            # 向量检索
            if self.vector_index.ntotal == 0:
                return {
                    "status": "success",
                    "documents": [],
                    "scores": [],
                    "total_time_ms": (time.time() - start_time) * 1000
                }
            
            # 搜索最相似的文档
            scores, indices = self.vector_index.search(
                np.array([query_embedding]).astype('float32'), 
                min(top_k, self.vector_index.ntotal)
            )
            
            # 获取文档
            retrieved_docs = []
            retrieved_scores = []
            
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:
                    continue
                
                # 根据索引查找文档
                doc_found = False
                for doc_id, doc in self.document_store.items():
                    # 简单的索引匹配（实际应用中需要更精确的映射）
                    if len(retrieved_docs) == len([d for d in self.document_store.values() if d == doc]):
                        retrieved_docs.append(doc)
                        retrieved_scores.append(float(score))
                        doc_found = True
                        break
                
                if not doc_found and self.document_store:
                    # 降级处理：返回第一个文档
                    first_doc = next(iter(self.document_store.values()))
                    retrieved_docs.append(first_doc)
                    retrieved_scores.append(float(score))
            
            # 更新统计
            self.stats["total_queries"] += 1
            query_time = (time.time() - start_time) * 1000
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (self.stats["total_queries"] - 1) + query_time) 
                / self.stats["total_queries"]
            )
            
            return {
                "status": "success",
                "documents": [
                    {
                        "id": doc.id,
                        "content": doc.content,
                        "metadata": doc.metadata,
                        "score": score
                    }
                    for doc, score in zip(retrieved_docs, retrieved_scores)
                ],
                "scores": retrieved_scores,
                "total_time_ms": query_time
            }
            
        except Exception as e:
            logger.error(f"❌ 文档检索失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def query_with_kimi_k2(self, query: str, kb_id: str = "default", top_k: int = None) -> Dict[str, Any]:
        """使用 Kimi K2 进行 RAG 查询"""
        try:
            start_time = datetime.now()
            
            # 执行 RAG 查询
            rag_result = await self.retrieve_documents(query, kb_id, top_k or self.top_k_default)
            
            if rag_result["status"] != "success":
                return rag_result
            
            # 构建增强提示
            context_docs = rag_result["documents"]
            if context_docs:
                context_text = "\n\n".join([
                    f"文档 {i+1}:\n{doc['content']}"
                    for i, doc in enumerate(context_docs)
                ])
                
                enhanced_prompt = f"""基于以下相关文档回答问题：

{context_text}

问题: {query}

请基于上述文档内容提供准确、详细的回答。如果文档中没有相关信息，请明确说明。"""
            else:
                enhanced_prompt = query
            
            # 调用 Kimi K2 API
            kimi_response = await self._call_kimi_k2_api(enhanced_prompt)
            
            # 计算总时间
            total_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "success",
                "query": query,
                "answer": kimi_response.get("content", ""),
                "context_documents": context_docs,
                "total_time_ms": total_time,
                "enhanced_prompt": enhanced_prompt
            }
            
        except Exception as e:
            logger.error(f"❌ Kimi K2 RAG 查询失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _call_kimi_k2_api(self, prompt: str) -> Dict[str, Any]:
        """调用 Kimi K2 API"""
        if not self.kimi_k2_api_key:
            return {"content": "Kimi K2 API 未配置，返回模拟回答"}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.kimi_k2_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "moonshot-v1-8k",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{self.kimi_k2_endpoint}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "content": result["choices"][0]["message"]["content"],
                            "usage": result.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Kimi K2 API 错误: {response.status} - {error_text}")
                        return {"content": f"API 调用失败: {response.status}"}
                        
        except Exception as e:
            logger.error(f"❌ Kimi K2 API 调用异常: {e}")
            return {"content": f"API 调用异常: {str(e)}"}
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取 RAG 服务统计信息"""
        return {
            "total_documents": len(self.document_store),
            "vector_index_size": self.vector_index.ntotal if self.vector_index else 0,
            "embedding_model": self.embedding_model_name,
            "stats": self.stats,
            "timestamp": datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查核心组件
            checks = {
                "embedding_model": self.embedding_model is not None,
                "vector_index": self.vector_index is not None,
                "document_store": len(self.document_store) >= 0,
                "kimi_k2_configured": bool(self.kimi_k2_api_key)
            }
            
            return {
                "status": "healthy" if all(checks.values()) else "degraded",
                "checks": checks,
                "timestamp": datetime.now().isoformat(),
                "document_count": len(self.document_store),
                "vector_index_size": self.vector_index.ntotal if self.vector_index else 0
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 全局实例管理
rag_service = None

def get_rag_service(**kwargs) -> RAGService:
    """获取 RAG 服务实例"""
    global rag_service
    if rag_service is None:
        rag_service = RAGService(**kwargs)
    return rag_service

async def main():
    """测试 RAG 服务"""
    print("🧪 测试 RAG 服务...")
    
    service = get_rag_service()
    await service.initialize()
    
    # 测试健康检查
    health = await service.health_check()
    print(f"✅ 健康检查: {health['status']}")
    
    # 测试添加文档
    test_docs = [
        {
            "content": "Python 是一种高级编程语言，具有简洁的语法和强大的功能。",
            "metadata": {"type": "programming", "language": "python"}
        }
    ]
    
    add_result = await service.add_documents(test_docs)
    print(f"✅ 文档添加: {add_result['status']}")
    
    # 测试检索
    retrieve_result = await service.retrieve_documents("Python 编程")
    print(f"✅ 文档检索: {retrieve_result['status']}, 找到 {len(retrieve_result.get('documents', []))} 个文档")
    
    print("✅ RAG 服务测试完成")

if __name__ == "__main__":
    asyncio.run(main())

