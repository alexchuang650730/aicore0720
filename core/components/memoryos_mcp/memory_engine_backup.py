#!/usr/bin/env python3
"""
MemoryOS MCP - 記憶引擎
核心記憶存儲和檢索系統
"""

import sqlite3
import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """記憶類型"""
    EPISODIC = "episodic"        # 特定事件記憶
    SEMANTIC = "semantic"        # 事實和知識記憶
    PROCEDURAL = "procedural"    # 技能和流程記憶
    WORKING = "working"          # 工作記憶
    CLAUDE_INTERACTION = "claude_interaction"  # Claude Code 互動記憶
    USER_PREFERENCE = "user_preference"       # 用戶偏好記憶

@dataclass
class Memory:
    """記憶項目"""
    id: str
    memory_type: MemoryType
    content: str
    metadata: Dict[str, Any]
    created_at: float
    accessed_at: float
    access_count: int
    importance_score: float
    tags: List[str]
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """從字典創建"""
        if 'memory_type' in data:
            data['memory_type'] = MemoryType(data['memory_type'])
        return cls(**data)

class MemoryEngine:
    """記憶引擎核心類"""
    
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
            "storage_class": "STANDARD_IA",
            "enable_encryption": True
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
        """初始化 S3 存储"""
        try:
            import boto3
            self.s3_client = boto3.client('s3', region_name=self.s3_config["region"])
            logger.info("✅ S3 存储初始化完成")
        except Exception as e:
            logger.warning(f"⚠️ S3 初始化失败，禁用 S3 功能: {e}")
            self.enable_s3 = False
        
    async def initialize(self):
        """初始化記憶引擎"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.execute('PRAGMA journal_mode=WAL')
            self.connection.execute('PRAGMA synchronous=NORMAL')
            
            # 創建表結構
            await self._create_tables()
            
            # 載入工作記憶
            await self._load_working_memory()
            
            self.is_initialized = True
            logger.info(f"✅ MemoryEngine 初始化完成 (DB: {self.db_path})")
            
        except Exception as e:
            logger.error(f"❌ MemoryEngine 初始化失敗: {e}")
            raise
    
    async def _create_tables(self):
        """創建數據庫表"""
        create_sql = """
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            created_at REAL NOT NULL,
            accessed_at REAL NOT NULL,
            access_count INTEGER DEFAULT 0,
            importance_score REAL DEFAULT 0.0,
            tags TEXT,
            embedding BLOB
        );
        
        CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type);
        CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at);
        CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance_score);
        CREATE INDEX IF NOT EXISTS idx_tags ON memories(tags);
        """
        
        self.connection.executescript(create_sql)
        self.connection.commit()
    
    async def _load_working_memory(self):
        """載入工作記憶"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM memories 
            WHERE memory_type = ? 
            ORDER BY accessed_at DESC 
            LIMIT ?
        """, (MemoryType.WORKING.value, self.max_working_memory))
        
        rows = cursor.fetchall()
        for row in rows:
            memory = self._row_to_memory(row)
            self.working_memory[memory.id] = memory
    
    def _row_to_memory(self, row) -> Memory:
        """將數據庫行轉換為記憶對象"""
        return Memory(
            id=row[0],
            memory_type=MemoryType(row[1]),
            content=row[2],
            metadata=json.loads(row[3]) if row[3] else {},
            created_at=row[4],
            accessed_at=row[5],
            access_count=row[6],
            importance_score=row[7],
            tags=json.loads(row[8]) if row[8] else [],
            embedding=np.frombuffer(row[9]) if row[9] else None
        )
    
    async def store_memory(self, memory: Memory) -> bool:
        """存儲記憶"""
        try:
            # 生成嵌入向量
            if memory.embedding is None:
                memory.embedding = self._generate_embedding(memory.content)
            
            # 插入到數據庫
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memories 
                (id, memory_type, content, metadata, created_at, accessed_at, 
                 access_count, importance_score, tags, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.memory_type.value,
                memory.content,
                json.dumps(memory.metadata),
                memory.created_at,
                memory.accessed_at,
                memory.access_count,
                memory.importance_score,
                json.dumps(memory.tags),
                memory.embedding.tobytes() if memory.embedding is not None else None
            ))
            
            self.connection.commit()
            
            # 更新工作記憶
            if memory.memory_type == MemoryType.WORKING:
                await self._update_working_memory(memory)
            
            # 檢查記憶容量
            await self._manage_memory_capacity()
            
            logger.debug(f"✅ 存儲記憶: {memory.id} ({memory.memory_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 存儲記憶失敗: {e}")
            return False
    
    async def _update_working_memory(self, memory: Memory):
        """更新工作記憶"""
        self.working_memory[memory.id] = memory
        
        # 限制工作記憶大小
        if len(self.working_memory) > self.max_working_memory:
            # 移除最舊的記憶
            oldest_id = min(self.working_memory.keys(), 
                          key=lambda x: self.working_memory[x].accessed_at)
            del self.working_memory[oldest_id]
    
    async def retrieve_memory(self, memory_id: str) -> Optional[Memory]:
        """檢索單個記憶"""
        try:
            # 先檢查工作記憶
            if memory_id in self.working_memory:
                memory = self.working_memory[memory_id]
                await self._update_memory_access(memory)
                return memory
            
            # 從數據庫檢索
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
            row = cursor.fetchone()
            
            if row:
                memory = self._row_to_memory(row)
                await self._update_memory_access(memory)
                return memory
                
            return None
            
        except Exception as e:
            logger.error(f"❌ 檢索記憶失敗: {e}")
            return None
    
    async def search_memories(self, 
                            query: str = "",
                            memory_type: Optional[MemoryType] = None,
                            tags: Optional[List[str]] = None,
                            limit: int = 10,
                            min_importance: float = 0.0) -> List[Memory]:
        """搜索記憶"""
        try:
            conditions = []
            params = []
            
            if memory_type:
                conditions.append("memory_type = ?")
                params.append(memory_type.value)
            
            if tags:
                for tag in tags:
                    conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
            
            if min_importance > 0:
                conditions.append("importance_score >= ?")
                params.append(min_importance)
            
            if query:
                conditions.append("content LIKE ?")
                params.append(f"%{query}%")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cursor = self.connection.cursor()
            cursor.execute(f"""
                SELECT * FROM memories 
                WHERE {where_clause}
                ORDER BY importance_score DESC, accessed_at DESC
                LIMIT ?
            """, params + [limit])
            
            rows = cursor.fetchall()
            memories = [self._row_to_memory(row) for row in rows]
            
            # 更新訪問統計
            for memory in memories:
                await self._update_memory_access(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"❌ 搜索記憶失敗: {e}")
            return []
    
    async def get_similar_memories(self, 
                                 content: str, 
                                 memory_type: Optional[MemoryType] = None,
                                 limit: int = 5) -> List[Memory]:
        """獲取相似記憶"""
        try:
            query_embedding = self._generate_embedding(content)
            
            # 簡化的相似度計算（在實際實現中應該使用向量數據庫）
            cursor = self.connection.cursor()
            conditions = []
            params = []
            
            if memory_type:
                conditions.append("memory_type = ?")
                params.append(memory_type.value)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cursor.execute(f"""
                SELECT * FROM memories 
                WHERE {where_clause} AND embedding IS NOT NULL
                ORDER BY importance_score DESC
                LIMIT ?
            """, params + [limit * 2])  # 獲取更多候選
            
            rows = cursor.fetchall()
            memories = [self._row_to_memory(row) for row in rows]
            
            # 計算相似度並排序
            similarities = []
            for memory in memories:
                if memory.embedding is not None:
                    similarity = self._cosine_similarity(query_embedding, memory.embedding)
                    similarities.append((memory, similarity))
            
            # 按相似度排序
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return [mem for mem, _ in similarities[:limit]]
            
        except Exception as e:
            logger.error(f"❌ 獲取相似記憶失敗: {e}")
            return []
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """生成嵌入向量（簡化版）"""
        # 這裡使用簡化的嵌入生成，實際應該使用專業的嵌入模型
        words = text.lower().split()
        embedding = np.random.random(128)  # 128維向量
        
        # 簡單的詞頻統計影響
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # 根據詞頻調整嵌入
        for i, word in enumerate(words[:128]):
            if i < len(embedding):
                embedding[i] *= word_counts.get(word, 1)
        
        return embedding / np.linalg.norm(embedding)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """計算餘弦相似度"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    async def _update_memory_access(self, memory: Memory):
        """更新記憶訪問統計"""
        memory.accessed_at = time.time()
        memory.access_count += 1
        memory.importance_score = self._calculate_importance(memory)
        
        # 更新數據庫
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE memories 
            SET accessed_at = ?, access_count = ?, importance_score = ?
            WHERE id = ?
        """, (memory.accessed_at, memory.access_count, memory.importance_score, memory.id))
        self.connection.commit()
    
    def _calculate_importance(self, memory: Memory) -> float:
        """計算記憶重要性分數"""
        current_time = time.time()
        age = current_time - memory.created_at
        
        # 基礎分數
        base_score = 1.0
        
        # 訪問頻率影響
        frequency_score = min(memory.access_count / 10.0, 2.0)
        
        # 時間衰減影響
        time_decay = max(0.1, 1.0 / (1.0 + age / 86400))  # 按天衰減
        
        # 記憶類型權重
        type_weights = {
            MemoryType.CLAUDE_INTERACTION: 1.5,
            MemoryType.USER_PREFERENCE: 1.3,
            MemoryType.PROCEDURAL: 1.2,
            MemoryType.SEMANTIC: 1.0,
            MemoryType.EPISODIC: 0.8,
            MemoryType.WORKING: 0.5
        }
        
        type_weight = type_weights.get(memory.memory_type, 1.0)
        
        return base_score * frequency_score * time_decay * type_weight
    
    async def _manage_memory_capacity(self):
        """管理記憶容量"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        
        if count > self.max_memories:
            # 刪除最不重要的記憶
            to_delete = count - self.max_memories + 100  # 多刪除一些
            
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
        avg_importance = cursor.fetchone()[0] or 0.0
        
        # 工作記憶統計
        working_memory_count = len(self.working_memory)
        
        return {
            "total_memories": total_memories,
            "working_memory_count": working_memory_count,
            "type_distribution": type_counts,
            "average_importance": avg_importance,
            "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0,
            "max_capacity": self.max_memories,
            "capacity_usage": (total_memories / self.max_memories) * 100
        }
    
    async def cleanup(self):
        """清理資源"""
        if self.connection:
            self.connection.close()
            self.connection = None
        
        self.working_memory.clear()
        logger.info("🧹 MemoryEngine 清理完成")

# 全局记忆引擎实例将在需要时创建
memory_engine = None

def get_memory_engine(**kwargs):
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
        content="用戶問了如何使用 Python 進行數據分析",
        metadata={"user_id": "user123", "topic": "data_analysis"},
        created_at=time.time(),
        accessed_at=time.time(),
        access_count=1,
        importance_score=1.0,
        tags=["python", "data_analysis", "question"]
    )
    
    success = await memory_engine.store_memory(test_memory)
    print(f"✅ 存儲測試: {'成功' if success else '失敗'}")
    
    # 測試檢索
    retrieved = await memory_engine.retrieve_memory("test_001")
    print(f"✅ 檢索測試: {'成功' if retrieved else '失敗'}")
    
    # 測試搜索
    results = await memory_engine.search_memories(
        query="Python",
        memory_type=MemoryType.CLAUDE_INTERACTION,
        limit=5
    )
    print(f"✅ 搜索測試: 找到 {len(results)} 個結果")
    
    # 獲取統計信息
    stats = await memory_engine.get_memory_statistics()
    print(f"📊 記憶統計: {stats['total_memories']} 個記憶")
    
    await memory_engine.cleanup()
    print("✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(main())


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

