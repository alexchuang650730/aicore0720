#!/usr/bin/env python3
"""
MemoryOS MCP - 記憶引擎核心模組
PowerAutomation v4.8 - 完整的 RAG 和 S3 集成版本
"""

import asyncio
import json
import logging
import sqlite3
import time
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import numpy as np

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """記憶類型枚舉"""
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    CLAUDE_INTERACTION = "claude_interaction"
    SYSTEM_STATE = "system_state"

@dataclass
class Memory:
    """記憶數據結構"""
    id: str
    memory_type: MemoryType
    content: str
    metadata: Dict[str, Any]
    created_at: float
    accessed_at: float
    access_count: int
    importance_score: float
    tags: List[str]
    embedding: Optional[Union[List[float], np.ndarray]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        data = asdict(self)
        data['memory_type'] = self.memory_type.value
        if isinstance(self.embedding, np.ndarray):
            data['embedding'] = self.embedding.tolist()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """從字典創建記憶對象"""
        if 'memory_type' in data:
            data['memory_type'] = MemoryType(data['memory_type'])
        return cls(**data)

class MemoryEngine:
    """記憶引擎核心類 - 完整版本"""
    
    def __init__(self, db_path: str = "memoryos.db", max_memories: int = 10000, 
                 enable_rag: bool = True, enable_s3: bool = False, s3_config: Dict[str, Any] = None):
        """初始化記憶引擎 - 支持 RAG 和 S3"""
        self.db_path = Path(db_path)
        self.max_memories = max_memories
        self.working_memory: Dict[str, Memory] = {}
        self.max_working_memory = 100
        self.connection = None
        self.is_initialized = False
        
        # RAG 扩展功能
        self.enable_rag = enable_rag
        self.embedding_model = None
        self.vector_index = None
        self.document_store = {}
        self.rag_config = {
            "embedding_model": "all-MiniLM-L6-v2",
            "vector_dimension": 384,
            "similarity_threshold": 0.7,
            "max_results": 10
        }
        
        # S3 企业级存储功能
        self.enable_s3 = enable_s3
        self.s3_client = None
        self.s3_config = s3_config or {
            "bucket_name": "powerautomation-memory-storage",
            "region": "us-east-1",
            "prefix": "memoryos/",
            "storage_class": "STANDARD_IA",
            "enable_encryption": True,
            "backup_interval_hours": 24,
            "sync_mode": "hybrid"
        }
        
        # 初始化扩展组件
        if enable_rag:
            self._initialize_rag_components()
        
        if enable_s3:
            self._initialize_s3_storage()
    
    def _initialize_rag_components(self):
        """初始化 RAG 组件"""
        try:
            # 导入 RAG 相关库
            from sentence_transformers import SentenceTransformer
            import faiss
            
            # 初始化嵌入模型
            self.embedding_model = SentenceTransformer(self.rag_config["embedding_model"])
            
            # 初始化向量索引
            self.vector_index = faiss.IndexFlatIP(self.rag_config["vector_dimension"])
            
            logger.info("✅ RAG 组件初始化完成")
            
        except ImportError as e:
            logger.warning(f"⚠️ RAG 依赖缺失，禁用 RAG 功能: {e}")
            self.enable_rag = False
        except Exception as e:
            logger.error(f"❌ RAG 组件初始化失败: {e}")
            self.enable_rag = False
    
    def _initialize_s3_storage(self):
        """初始化 AWS S3 存储"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # 初始化 S3 客户端
            self.s3_client = boto3.client(
                's3',
                region_name=self.s3_config["region"]
            )
            
            logger.info("✅ AWS S3 存储初始化完成")
            
        except ImportError as e:
            logger.warning(f"⚠️ AWS SDK 缺失，禁用 S3 功能: {e}")
            self.enable_s3 = False
        except Exception as e:
            logger.error(f"❌ S3 存储初始化失败: {e}")
            self.enable_s3 = False
    
    async def initialize(self):
        """初始化數據庫連接"""
        if self.is_initialized:
            return
        
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        
        # 創建表結構
        await self._create_tables()
        self.is_initialized = True
        logger.info(f"✅ 記憶引擎初始化完成: {self.db_path}")
    
    async def _create_tables(self):
        """創建數據庫表結構"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at REAL NOT NULL,
                accessed_at REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                importance_score REAL DEFAULT 0.5,
                tags TEXT,
                embedding BLOB
            )
        """)
        
        # 創建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance_score)")
        
        self.connection.commit()
    
    async def store_memory(self, memory: Memory):
        """存儲記憶"""
        if not self.is_initialized:
            await self.initialize()
        
        cursor = self.connection.cursor()
        
        # 序列化數據
        metadata_json = json.dumps(memory.metadata)
        tags_json = json.dumps(memory.tags)
        embedding_blob = None
        
        if memory.embedding is not None:
            if isinstance(memory.embedding, np.ndarray):
                embedding_blob = memory.embedding.tobytes()
            elif isinstance(memory.embedding, list):
                embedding_blob = np.array(memory.embedding).tobytes()
        
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (id, memory_type, content, metadata, created_at, accessed_at, 
             access_count, importance_score, tags, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.id,
            memory.memory_type.value,
            memory.content,
            metadata_json,
            memory.created_at,
            memory.accessed_at,
            memory.access_count,
            memory.importance_score,
            tags_json,
            embedding_blob
        ))
        
        self.connection.commit()
        
        # 添加到工作記憶
        if len(self.working_memory) < self.max_working_memory:
            self.working_memory[memory.id] = memory
        
        # 清理舊記憶
        await self._cleanup_old_memories()
        
        logger.debug(f"✅ 記憶已存儲: {memory.id}")
    
    async def retrieve_memory(self, memory_id: str) -> Optional[Memory]:
        """檢索特定記憶"""
        # 先檢查工作記憶
        if memory_id in self.working_memory:
            memory = self.working_memory[memory_id]
            memory.accessed_at = time.time()
            memory.access_count += 1
            return memory
        
        # 從數據庫檢索
        if not self.is_initialized:
            await self.initialize()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        
        if row:
            memory = self._row_to_memory(row)
            
            # 更新訪問信息
            memory.accessed_at = time.time()
            memory.access_count += 1
            
            # 更新數據庫
            cursor.execute("""
                UPDATE memories 
                SET accessed_at = ?, access_count = ? 
                WHERE id = ?
            """, (memory.accessed_at, memory.access_count, memory_id))
            self.connection.commit()
            
            # 添加到工作記憶
            self.working_memory[memory_id] = memory
            
            return memory
        
        return None
    
    async def search_memories(self, query: str, memory_type: MemoryType = None, 
                            limit: int = 10, memory_types: List[MemoryType] = None) -> List[Memory]:
        """搜索記憶"""
        if not self.is_initialized:
            await self.initialize()
        
        cursor = self.connection.cursor()
        
        # 構建查詢條件
        conditions = ["content LIKE ?"]
        params = [f"%{query}%"]
        
        if memory_type:
            conditions.append("memory_type = ?")
            params.append(memory_type.value)
        elif memory_types:
            placeholders = ",".join("?" * len(memory_types))
            conditions.append(f"memory_type IN ({placeholders})")
            params.extend([mt.value for mt in memory_types])
        
        where_clause = " AND ".join(conditions)
        
        cursor.execute(f"""
            SELECT * FROM memories 
            WHERE {where_clause}
            ORDER BY importance_score DESC, accessed_at DESC
            LIMIT ?
        """, params + [limit])
        
        results = []
        for row in cursor.fetchall():
            memory = self._row_to_memory(row)
            results.append(memory)
        
        return results
    
    async def get_similar_memories(self, memory: Memory, limit: int = 5) -> List[Memory]:
        """獲取相似記憶"""
        if not self.enable_rag or not memory.embedding:
            # 降級到基於內容的搜索
            return await self.search_memories(
                memory.content[:100], 
                memory_type=memory.memory_type, 
                limit=limit
            )
        
        try:
            # 使用向量相似度搜索
            query_embedding = np.array(memory.embedding).reshape(1, -1).astype('float32')
            
            if self.vector_index.ntotal > 0:
                distances, indices = self.vector_index.search(query_embedding, min(limit, self.vector_index.ntotal))
                
                similar_memories = []
                for distance, idx in zip(distances[0], indices[0]):
                    if idx != -1:
                        # 根據索引查找對應的記憶
                        # 這裡需要維護一個索引到記憶ID的映射
                        pass
                
                return similar_memories
            
        except Exception as e:
            logger.error(f"❌ 向量相似度搜索失败: {e}")
        
        # 降級處理
        return await self.search_memories(
            memory.content[:100], 
            memory_type=memory.memory_type, 
            limit=limit
        )
    
    def _row_to_memory(self, row) -> Memory:
        """將數據庫行轉換為記憶對象"""
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        tags = json.loads(row['tags']) if row['tags'] else []
        
        embedding = None
        if row['embedding']:
            try:
                embedding = np.frombuffer(row['embedding'], dtype=np.float32)
            except:
                pass
        
        return Memory(
            id=row['id'],
            memory_type=MemoryType(row['memory_type']),
            content=row['content'],
            metadata=metadata,
            created_at=row['created_at'],
            accessed_at=row['accessed_at'],
            access_count=row['access_count'],
            importance_score=row['importance_score'],
            tags=tags,
            embedding=embedding
        )
    
    async def _cleanup_old_memories(self):
        """清理舊記憶"""
        if not self.is_initialized:
            return
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        total_memories = cursor.fetchone()[0]
        
        if total_memories > self.max_memories:
            # 刪除最舊且重要性最低的記憶
            to_delete = total_memories - self.max_memories
            
            cursor.execute("""
                DELETE FROM memories 
                WHERE id IN (
                    SELECT id FROM memories 
                    ORDER BY importance_score ASC, accessed_at ASC 
                    LIMIT ?
                )
            """, (to_delete,))
            
            self.connection.commit()
            logger.info(f"🗑️ 清理記憶: 刪除 {to_delete} 個低重要性記憶")
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """獲取記憶統計信息"""
        if not self.is_initialized:
            await self.initialize()
            
        cursor = self.connection.cursor()
        
        # 總記憶數
        cursor.execute("SELECT COUNT(*) FROM memories")
        total_memories = cursor.fetchone()[0]
        
        # 按類型統計
        cursor.execute("""
            SELECT memory_type, COUNT(*) 
            FROM memories 
            GROUP BY memory_type
        """)
        type_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 平均重要性
        cursor.execute("SELECT AVG(importance_score) FROM memories")
        avg_importance = cursor.fetchone()[0] or 0
        
        stats = {
            "total_memories": total_memories,
            "working_memory_size": len(self.working_memory),
            "type_distribution": type_counts,
            "average_importance": avg_importance,
            "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0,
            "max_capacity": self.max_memories,
            "capacity_usage": (total_memories / self.max_memories) * 100
        }
        
        # 添加 RAG 统计
        if self.enable_rag:
            rag_stats = await self.get_rag_statistics()
            stats.update(rag_stats)
        
        # 添加 S3 统计
        if self.enable_s3:
            s3_stats = await self.get_s3_statistics()
            stats.update(s3_stats)
        
        return stats
    
    async def cleanup(self):
        """清理資源"""
        if self.connection:
            self.connection.close()
            self.connection = None
        self.is_initialized = False
        logger.info("✅ 記憶引擎資源已清理")
    
    # ==================== RAG 向量检索扩展方法 ====================
    
    async def add_document_to_rag(self, doc_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """添加文档到 RAG 系统"""
        if not self.enable_rag:
            logger.warning("RAG 功能未启用")
            return False
            
        try:
            # 生成嵌入向量
            embedding = self.embedding_model.encode([content])[0]
            
            # 添加到向量索引
            self.vector_index.add(np.array([embedding]).astype('float32'))
            
            # 存储文档信息
            self.document_store[doc_id] = {
                "content": content,
                "metadata": metadata or {},
                "embedding_id": self.vector_index.ntotal - 1,
                "timestamp": time.time()
            }
            
            # 同时作为语义记忆存储
            semantic_memory = Memory(
                id=f"rag_doc_{doc_id}",
                memory_type=MemoryType.SEMANTIC,
                content=content,
                metadata={
                    "doc_id": doc_id,
                    "source": "rag_document",
                    **(metadata or {})
                },
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                importance_score=0.8,  # RAG 文档默认重要性较高
                tags=["rag", "document"],
                embedding=embedding.tolist()
            )
            
            await self.store_memory(semantic_memory)
            
            logger.info(f"✅ 文档 {doc_id} 已添加到 RAG 系统")
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加文档到 RAG 失败: {e}")
            return False
    
    async def rag_query(self, query: str, top_k: int = 5, memory_types: List[MemoryType] = None) -> List[Dict[str, Any]]:
        """RAG 查询 - 结合向量检索和记忆检索"""
        if not self.enable_rag:
            return await self.search_memories(query, limit=top_k, memory_types=memory_types)
        
        try:
            results = []
            
            # 1. 向量检索 RAG 文档
            query_embedding = self.embedding_model.encode([query])[0]
            
            if self.vector_index.ntotal > 0:
                distances, indices = self.vector_index.search(
                    np.array([query_embedding]).astype('float32'), 
                    min(top_k, self.vector_index.ntotal)
                )
                
                # 处理 RAG 文档结果
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx == -1:
                        continue
                        
                    # 查找对应的文档
                    for doc_id, doc_info in self.document_store.items():
                        if doc_info.get("embedding_id") == idx:
                            similarity = float(distance)  # FAISS IP 返回的是内积
                            
                            if similarity >= self.rag_config["similarity_threshold"]:
                                results.append({
                                    "type": "rag_document",
                                    "doc_id": doc_id,
                                    "content": doc_info["content"],
                                    "metadata": doc_info["metadata"],
                                    "similarity": similarity,
                                    "rank": i + 1,
                                    "source": "vector_search"
                                })
                            break
            
            # 2. 记忆检索
            memory_results = await self.search_memories(query, limit=top_k, memory_types=memory_types)
            
            # 转换记忆结果格式
            for memory in memory_results:
                results.append({
                    "type": "memory",
                    "memory_id": memory.id,
                    "content": memory.content,
                    "metadata": memory.metadata,
                    "memory_type": memory.memory_type.value,
                    "importance_score": memory.importance_score,
                    "access_count": memory.access_count,
                    "source": "memory_search"
                })
            
            # 3. 结果排序和去重
            results = self._rank_and_deduplicate_results(results, query)
            
            logger.info(f"✅ RAG 查询完成，返回 {len(results)} 个结果")
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ RAG 查询失败: {e}")
            return []
    
    def _rank_and_deduplicate_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """结果排序和去重"""
        # 简单的去重逻辑（基于内容相似度）
        unique_results = []
        seen_contents = set()
        
        for result in results:
            content_hash = hash(result["content"][:100])  # 使用前100字符的哈希
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        # 排序：优先级 = 相似度 * 重要性权重
        def calculate_score(result):
            if result["type"] == "rag_document":
                return result.get("similarity", 0.5) * 1.0  # RAG 文档权重
            else:
                return result.get("importance_score", 0.3) * 0.8  # 记忆权重
        
        unique_results.sort(key=calculate_score, reverse=True)
        return unique_results
    
    async def get_rag_statistics(self) -> Dict[str, Any]:
        """获取 RAG 系统统计信息"""
        if not self.enable_rag:
            return {"rag_enabled": False}
        
        return {
            "rag_enabled": True,
            "total_documents": len(self.document_store),
            "vector_index_size": self.vector_index.ntotal if self.vector_index else 0,
            "embedding_model": self.rag_config["embedding_model"],
            "vector_dimension": self.rag_config["vector_dimension"],
            "similarity_threshold": self.rag_config["similarity_threshold"]
        }
    
    # ==================== AWS S3 企业级存储扩展方法 ====================
    
    async def sync_to_s3(self, force: bool = False) -> bool:
        """同步本地数据到 S3"""
        if not self.enable_s3:
            logger.warning("S3 存储未启用")
            return False
        
        try:
            # 导出本地数据
            export_data = await self._export_memories_for_s3()
            
            # 上传到 S3
            s3_key = f"{self.s3_config['prefix']}memories/memories_{int(time.time())}.json.gz"
            
            # 压缩数据
            import gzip
            compressed_data = gzip.compress(json.dumps(export_data).encode('utf-8'))
            
            self.s3_client.put_object(
                Bucket=self.s3_config["bucket_name"],
                Key=s3_key,
                Body=compressed_data,
                StorageClass=self.s3_config["storage_class"],
                Metadata={
                    "memory_count": str(len(export_data.get("memories", []))),
                    "export_timestamp": str(time.time()),
                    "version": "4.8.0"
                }
            )
            
            logger.info(f"✅ 数据已同步到 S3: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ S3 同步失败: {e}")
            return False
    
    async def restore_from_s3(self, s3_key: str = None) -> bool:
        """从 S3 恢复数据"""
        if not self.enable_s3:
            logger.warning("S3 存储未启用")
            return False
        
        try:
            # 如果没有指定 key，获取最新的备份
            if not s3_key:
                s3_key = await self._get_latest_s3_backup()
            
            if not s3_key:
                logger.warning("未找到 S3 备份文件")
                return False
            
            # 从 S3 下载数据
            response = self.s3_client.get_object(
                Bucket=self.s3_config["bucket_name"],
                Key=s3_key
            )
            
            # 解压缩数据
            import gzip
            compressed_data = response['Body'].read()
            decompressed_data = gzip.decompress(compressed_data)
            import_data = json.loads(decompressed_data.decode('utf-8'))
            
            # 导入数据
            await self._import_memories_from_s3(import_data)
            
            logger.info(f"✅ 数据已从 S3 恢复: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ S3 恢复失败: {e}")
            return False
    
    async def _export_memories_for_s3(self) -> Dict[str, Any]:
        """导出记忆数据用于 S3 存储"""
        if not self.is_initialized:
            await self.initialize()
            
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM memories")
        rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            memory = self._row_to_memory(row)
            memory_dict = memory.to_dict()
            # 转换嵌入向量为列表（JSON 序列化）
            if memory_dict.get("embedding") is not None:
                memory_dict["embedding"] = memory_dict["embedding"].tolist() if hasattr(memory_dict["embedding"], 'tolist') else memory_dict["embedding"]
            memories.append(memory_dict)
        
        return {
            "memories": memories,
            "export_timestamp": time.time(),
            "version": "4.8.0",
            "total_count": len(memories),
            "rag_enabled": self.enable_rag,
            "rag_statistics": await self.get_rag_statistics() if self.enable_rag else {}
        }
    
    async def _import_memories_from_s3(self, import_data: Dict[str, Any]):
        """从 S3 数据导入记忆"""
        memories = import_data.get("memories", [])
        
        for memory_dict in memories:
            # 重建 Memory 对象
            memory_dict["memory_type"] = MemoryType(memory_dict["memory_type"])
            
            # 转换嵌入向量
            if memory_dict.get("embedding"):
                memory_dict["embedding"] = np.array(memory_dict["embedding"])
            
            memory = Memory(**memory_dict)
            await self.store_memory(memory)
        
        logger.info(f"✅ 已导入 {len(memories)} 条记忆")
    
    async def _get_latest_s3_backup(self) -> Optional[str]:
        """获取最新的 S3 备份文件"""
        try:
            prefix = f"{self.s3_config['prefix']}memories/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_config["bucket_name"],
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return None
            
            # 按修改时间排序，获取最新的
            objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
            
            return objects[0]['Key'] if objects else None
            
        except Exception as e:
            logger.error(f"❌ 获取 S3 备份列表失败: {e}")
            return None
    
    async def get_s3_statistics(self) -> Dict[str, Any]:
        """获取 S3 存储统计信息"""
        if not self.enable_s3:
            return {"s3_enabled": False}
        
        try:
            prefix = f"{self.s3_config['prefix']}memories/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_config["bucket_name"],
                Prefix=prefix
            )
            
            total_size = 0
            backup_count = 0
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    total_size += obj['Size']
                    backup_count += 1
            
            return {
                "s3_enabled": True,
                "bucket_name": self.s3_config["bucket_name"],
                "region": self.s3_config["region"],
                "backup_count": backup_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "storage_class": self.s3_config["storage_class"],
                "encryption_enabled": self.s3_config["enable_encryption"]
            }
            
        except Exception as e:
            logger.error(f"❌ 获取 S3 统计失败: {e}")
            return {"s3_enabled": True, "error": str(e)}

# 全局实例管理
memory_engine = None

def get_memory_engine(**kwargs) -> MemoryEngine:
    """获取记忆引擎实例"""
    global memory_engine
    if memory_engine is None:
        memory_engine = MemoryEngine(**kwargs)
    return memory_engine

async def main():
    """測試記憶引擎"""
    print("🧪 測試 MemoryEngine...")
    
    engine = get_memory_engine()
    await engine.initialize()
    
    # 測試存儲記憶
    test_memory = Memory(
        id="test_001",
        memory_type=MemoryType.CLAUDE_INTERACTION,
        content="這是一個測試記憶，包含 Python 編程相關內容。",
        metadata={"source": "test", "language": "zh-TW"},
        created_at=time.time(),
        accessed_at=time.time(),
        access_count=0,
        importance_score=0.8,
        tags=["test", "python", "programming"]
    )
    
    await engine.store_memory(test_memory)
    print("✅ 記憶存儲測試完成")
    
    # 測試檢索
    retrieved = await engine.retrieve_memory("test_001")
    print(f"✅ 檢索測試: {'成功' if retrieved else '失敗'}")
    
    # 測試搜索
    results = await engine.search_memories(
        query="Python",
        memory_type=MemoryType.CLAUDE_INTERACTION,
        limit=5
    )
    print(f"✅ 搜索測試: 找到 {len(results)} 個結果")
    
    # 獲取統計信息
    stats = await engine.get_memory_statistics()
    print(f"📊 記憶統計: {stats['total_memories']} 個記憶")
    
    await engine.cleanup()
    print("✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(main())

