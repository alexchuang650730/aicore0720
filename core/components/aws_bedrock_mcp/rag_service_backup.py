"""
RAG Service - PowerAutomation v4.8

企业级 RAG 功能实现，包括:
- 向量数据库管理
- 文档索引和检索
- 与 Kimi K2 的集成
- MemoryOS 项目上下文管理

设计原则:
- 使用 AWS S3 作为向量存储后端
- 与 Kimi K2 配合实现零余额消耗
- 支持多种文档格式和代码文件
- 智能上下文管理和检索优化
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
from sentence_transformers import SentenceTransformer
import faiss
import pickle

from .bedrock_manager import BedrockManager

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
    
    def __init__(self, bedrock_manager: BedrockManager, config: Dict[str, Any] = None):
        """
        初始化 RAG 服务
        
        Args:
            bedrock_manager: AWS Bedrock 管理器实例
            config: RAG 服务配置
        """
        self.bedrock_manager = bedrock_manager
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
            self.logger.info("初始化 RAG 服务...")
            
            # 1. 加载嵌入模型
            await self._load_embedding_model()
            
            # 2. 初始化向量索引
            await self._initialize_vector_index()
            
            # 3. 加载现有文档
            await self._load_existing_documents()
            
            # 4. 验证 Kimi K2 连接
            await self._verify_kimi_k2_connection()
            
            result = {
                "status": "success",
                "embedding_model": self.embedding_model_name,
                "vector_dimension": self.embedding_model.get_sentence_embedding_dimension(),
                "documents_loaded": len(self.document_store),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"RAG 服务初始化完成: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"RAG 服务初始化失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _load_embedding_model(self):
        """加载嵌入模型"""
        try:
            self.logger.info(f"加载嵌入模型: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.logger.info("嵌入模型加载成功")
        except Exception as e:
            self.logger.error(f"嵌入模型加载失败: {str(e)}")
            raise
    
    async def _initialize_vector_index(self):
        """初始化向量索引"""
        try:
            # 获取嵌入维度
            dimension = self.embedding_model.get_sentence_embedding_dimension()
            
            # 创建 FAISS 索引 (使用 IndexFlatIP 进行余弦相似度搜索)
            self.vector_index = faiss.IndexFlatIP(dimension)
            
            self.logger.info(f"向量索引初始化完成，维度: {dimension}")
        except Exception as e:
            self.logger.error(f"向量索引初始化失败: {str(e)}")
            raise
    
    async def _load_existing_documents(self):
        """从 S3 加载现有文档"""
        try:
            # 尝试从 S3 加载文档存储
            result = await self.bedrock_manager.download_rag_data("document_store.pkl")
            
            if result["status"] == "success":
                self.document_store = pickle.loads(result["data"])
                
                # 重建向量索引
                if self.document_store:
                    embeddings = []
                    for doc in self.document_store.values():
                        if doc.embedding is not None:
                            embeddings.append(doc.embedding)
                    
                    if embeddings:
                        embeddings_array = np.array(embeddings).astype('float32')
                        # 归一化向量以支持余弦相似度
                        faiss.normalize_L2(embeddings_array)
                        self.vector_index.add(embeddings_array)
                
                self.logger.info(f"加载了 {len(self.document_store)} 个现有文档")
            else:
                self.logger.info("未找到现有文档存储，从空开始")
                
        except Exception as e:
            self.logger.warning(f"加载现有文档失败: {str(e)}，从空开始")
            self.document_store = {}
    
    async def _verify_kimi_k2_connection(self):
        """验证 Kimi K2 API 连接"""
        try:
            if not self.kimi_k2_api_key:
                self.logger.warning("Kimi K2 API 密钥未配置")
                return
            
            # 测试 API 连接
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.kimi_k2_api_key}",
                    "Content-Type": "application/json"
                }
                
                test_payload = {
                    "model": "moonshot-v1-8k",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                }
                
                async with session.post(
                    f"{self.kimi_k2_endpoint}/chat/completions",
                    headers=headers,
                    json=test_payload,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        self.logger.info("Kimi K2 API 连接验证成功")
                    else:
                        self.logger.warning(f"Kimi K2 API 连接验证失败: {response.status}")
                        
        except Exception as e:
            self.logger.warning(f"Kimi K2 API 连接验证失败: {str(e)}")
    
    async def add_document(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        添加文档到 RAG 系统
        
        Args:
            content: 文档内容
            metadata: 文档元数据
            
        Returns:
            添加结果
        """
        try:
            start_time = datetime.now()
            
            # 生成文档 ID
            doc_id = hashlib.md5(content.encode()).hexdigest()
            
            # 检查文档是否已存在
            if doc_id in self.document_store:
                return {
                    "status": "exists",
                    "document_id": doc_id,
                    "message": "文档已存在"
                }
            
            # 生成嵌入向量
            embedding = self.embedding_model.encode(content, convert_to_numpy=True)
            embedding = embedding.astype('float32')
            
            # 创建文档对象
            document = Document(
                id=doc_id,
                content=content,
                metadata=metadata or {},
                embedding=embedding,
                timestamp=datetime.now()
            )
            
            # 添加到文档存储
            self.document_store[doc_id] = document
            
            # 添加到向量索引
            embedding_normalized = embedding.copy()
            faiss.normalize_L2(embedding_normalized.reshape(1, -1))
            self.vector_index.add(embedding_normalized.reshape(1, -1))
            
            # 保存到 S3
            await self._save_document_store()
            
            # 更新统计
            self.stats["total_documents"] = len(self.document_store)
            self.stats["last_updated"] = datetime.now()
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = {
                "status": "success",
                "document_id": doc_id,
                "content_length": len(content),
                "processing_time_ms": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"文档添加成功: {doc_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"文档添加失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def query_rag(self, query: RAGQuery) -> RAGResult:
        """
        执行 RAG 查询
        
        Args:
            query: RAG 查询对象
            
        Returns:
            RAG 查询结果
        """
        try:
            start_time = datetime.now()
            
            # 生成查询嵌入
            query_embedding = self.embedding_model.encode(query.query, convert_to_numpy=True)
            query_embedding = query_embedding.astype('float32')
            
            # 归一化查询向量
            faiss.normalize_L2(query_embedding.reshape(1, -1))
            
            # 执行向量搜索
            scores, indices = self.vector_index.search(
                query_embedding.reshape(1, -1), 
                min(query.top_k, len(self.document_store))
            )
            
            # 获取匹配的文档
            matched_documents = []
            matched_scores = []
            
            doc_list = list(self.document_store.values())
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0 and idx < len(doc_list):
                    doc = doc_list[idx]
                    
                    # 应用过滤器
                    if query.filters:
                        if not self._apply_filters(doc, query.filters):
                            continue
                    
                    matched_documents.append(doc)
                    matched_scores.append(float(score))
            
            # 生成增强提示
            enhanced_prompt = await self._generate_enhanced_prompt(query.query, matched_documents)
            
            # 更新统计
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self.stats["total_queries"] += 1
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (self.stats["total_queries"] - 1) + processing_time) 
                / self.stats["total_queries"]
            )
            
            result = RAGResult(
                query=query.query,
                documents=matched_documents,
                scores=matched_scores,
                total_time_ms=processing_time,
                enhanced_prompt=enhanced_prompt
            )
            
            self.logger.info(f"RAG 查询完成: {len(matched_documents)} 个匹配文档")
            return result
            
        except Exception as e:
            self.logger.error(f"RAG 查询失败: {str(e)}")
            raise
    
    def _apply_filters(self, document: Document, filters: Dict[str, Any]) -> bool:
        """应用文档过滤器"""
        try:
            for key, value in filters.items():
                if key not in document.metadata:
                    return False
                
                doc_value = document.metadata[key]
                
                if isinstance(value, list):
                    if doc_value not in value:
                        return False
                elif doc_value != value:
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def _generate_enhanced_prompt(self, query: str, documents: List[Document]) -> str:
        """生成增强的提示，包含相关上下文"""
        try:
            if not documents:
                return query
            
            # 构建上下文
            context_parts = []
            total_length = 0
            max_context = self.max_context_length - len(query) - 500  # 预留空间
            
            for doc in documents:
                content_snippet = doc.content[:1000]  # 限制每个文档的长度
                
                if total_length + len(content_snippet) > max_context:
                    break
                
                context_parts.append(f"[文档 {doc.id[:8]}]\n{content_snippet}")
                total_length += len(content_snippet)
            
            if not context_parts:
                return query
            
            # 构建增强提示
            enhanced_prompt = f"""基于以下相关文档回答问题：

相关文档:
{chr(10).join(context_parts)}

问题: {query}

请基于上述文档内容提供准确、详细的回答。如果文档中没有相关信息，请明确说明。"""
            
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"增强提示生成失败: {str(e)}")
            return query
    
    async def add_documents(self, documents: List[Dict[str, Any]], kb_id: str = "default") -> Dict[str, Any]:
        """添加文档到 RAG 系统
        
        Args:
            documents: 文档列表，每个文档包含 content 和 metadata
            kb_id: 知识库 ID
            
        Returns:
            添加结果
        """
        try:
            logger.info(f"添加 {len(documents)} 个文档到知识库 {kb_id}")
            
            # 处理文档
            processed_docs = []
            for i, doc in enumerate(documents):
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                if not content.strip():
                    continue
                    
                # 生成嵌入向量
                embedding = self.embedding_model.encode([content])[0]
                
                # 添加到向量索引
                doc_id = f"{kb_id}_{i}_{int(time.time())}"
                self.vector_index.add(np.array([embedding]).astype('float32'))
                
                # 存储文档信息
                doc_info = {
                    "id": doc_id,
                    "content": content,
                    "metadata": metadata,
                    "kb_id": kb_id,
                    "embedding_id": self.vector_index.ntotal - 1,
                    "timestamp": time.time()
                }
                
                self.documents[doc_id] = doc_info
                processed_docs.append(doc_info)
            
            # 保存到存储
            await self._save_documents()
            
            logger.info(f"成功添加 {len(processed_docs)} 个文档")
            
            return {
                "status": "success",
                "processed_documents": len(processed_docs),
                "kb_id": kb_id,
                "document_ids": [doc["id"] for doc in processed_docs]
            }
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def retrieve_documents(self, query: str, kb_id: str = "default", top_k: int = 5) -> Dict[str, Any]:
        """检索相关文档
        
        Args:
            query: 查询文本
            kb_id: 知识库 ID
            top_k: 返回文档数量
            
        Returns:
            检索结果
        """
        try:
            start_time = time.time()
            
            # 生成查询嵌入
            query_embedding = self.embedding_model.encode([query])[0]
            
            # 向量搜索
            distances, indices = self.vector_index.search(
                np.array([query_embedding]).astype('float32'), 
                min(top_k, self.vector_index.ntotal)
            )
            
            # 获取相关文档
            relevant_docs = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # FAISS 返回 -1 表示无效索引
                    continue
                    
                # 查找对应的文档
                for doc_id, doc_info in self.documents.items():
                    if doc_info.get("embedding_id") == idx and doc_info.get("kb_id") == kb_id:
                        relevant_docs.append({
                            "id": doc_id,
                            "content": doc_info["content"],
                            "metadata": doc_info["metadata"],
                            "similarity": float(1.0 / (1.0 + distance)),  # 转换为相似度分数
                            "rank": i + 1
                        })
                        break
            
            query_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            logger.info(f"检索到 {len(relevant_docs)} 个相关文档，耗时 {query_time:.2f}ms")
            
            return {
                "status": "success",
                "documents": relevant_docs,
                "query": query,
                "kb_id": kb_id,
                "query_time_ms": query_time,
                "total_documents": len(relevant_docs)
            }
            
        except Exception as e:
            logger.error(f"文档检索失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "documents": []
            }

    async def query_with_context(self, query: str, kb_id: str = "default", top_k: int = 5) -> Dict[str, Any]:       使用 Kimi K2 执行 RAG 增强查询
        
        Args:
            query: 用户查询
            top_k: 返回的相关文档数量
            
        Returns:
            Kimi K2 的回答结果
        """
        try:
            start_time = datetime.now()
            
            # 执行 RAG 查询
            rag_query = RAGQuery(query=query, top_k=top_k or self.top_k_default)
            rag_result = await self.query_rag(rag_query)
            
            # 调用 Kimi K2 API
            kimi_response = await self._call_kimi_k2_api(rag_result.enhanced_prompt)
            
            total_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = {
                "status": "success",
                "query": query,
                "rag_documents_found": len(rag_result.documents),
                "kimi_response": kimi_response,
                "total_time_ms": total_time,
                "rag_time_ms": rag_result.total_time_ms,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Kimi K2 RAG 查询完成: {query[:50]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"Kimi K2 RAG 查询失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    async def _call_kimi_k2_api(self, prompt: str) -> Dict[str, Any]:
        """调用 Kimi K2 API"""
        try:
            if not self.kimi_k2_api_key:
                return {
                    "status": "error",
                    "error": "Kimi K2 API 密钥未配置"
                }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.kimi_k2_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "moonshot-v1-32k",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 4000
                }
                
                async with session.post(
                    f"{self.kimi_k2_endpoint}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "content": data["choices"][0]["message"]["content"],
                            "model": data["model"],
                            "usage": data.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error": f"API 调用失败: {response.status} - {error_text}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": f"API 调用异常: {str(e)}"
            }
    
    async def _save_document_store(self):
        """保存文档存储到 S3"""
        try:
            # 序列化文档存储
            serialized_data = pickle.dumps(self.document_store)
            
            # 上传到 S3
            await self.bedrock_manager.upload_rag_data(
                data=serialized_data,
                key="document_store.pkl",
                metadata={
                    "type": "document_store",
                    "document_count": str(len(self.document_store)),
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            self.logger.info("文档存储已保存到 S3")
            
        except Exception as e:
            self.logger.error(f"文档存储保存失败: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取 RAG 服务统计信息"""
        return {
            "service_stats": self.stats.copy(),
            "document_count": len(self.document_store),
            "vector_index_size": self.vector_index.ntotal if self.vector_index else 0,
            "embedding_model": self.embedding_model_name,
            "timestamp": datetime.now().isoformat()
          async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查核心组件
            checks = {
                "embedding_model": self.embedding_model is not None,
                "vector_index": self.vector_index is not None,
                "document_store": len(self.document_store) >= 0,
                "bedrock_manager": self.bedrock_manager is not None
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
            }g_service(**kwargs) -> RAGService:
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
    
    print("✅ RAG 服务测试完成")

if __name__ == "__main__":
    asyncio.run(main())

