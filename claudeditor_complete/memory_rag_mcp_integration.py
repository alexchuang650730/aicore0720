#!/usr/bin/env python3
"""
Memory RAG MCP 集成組件
將Memory RAG系統集成為PowerAutomation的記憶中心
支持ClaudeEditor和PowerAutomation Core之間的智能記憶同步
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sqlite3
import pickle
import hashlib
from datetime import datetime, timedelta
import numpy as np

# 嘗試導入向量搜索庫
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS未安裝，將使用簡單的文本匹配搜索")

logger = logging.getLogger(__name__)

class MemoryRAGMCPIntegration:
    """Memory RAG MCP集成組件"""
    
    def __init__(self, db_path: str = "memory_rag.db"):
        """
        初始化Memory RAG MCP集成
        
        Args:
            db_path: 數據庫文件路徑
        """
        self.db_path = db_path
        self.connection = None
        self.vector_index = None
        self.embedding_dim = 384  # 使用較小的嵌入維度
        self.memory_cache = {}
        self.last_sync_time = time.time()
        
        # MCP連接狀態
        self.mcp_connected = False
        self.claudeditor_sessions = {}
        self.powerautomation_sessions = {}
        
        logger.info("🧠 Memory RAG MCP集成組件初始化")
    
    async def initialize(self):
        """初始化Memory RAG系統"""
        try:
            # 初始化數據庫
            await self._initialize_database()
            
            # 初始化向量索引
            if FAISS_AVAILABLE:
                await self._initialize_vector_index()
            
            # 加載緩存
            await self._load_memory_cache()
            
            self.mcp_connected = True
            logger.info("✅ Memory RAG MCP集成初始化完成")
            
        except Exception as e:
            logger.error(f"❌ Memory RAG MCP集成初始化失敗: {e}")
            raise
    
    async def _initialize_database(self):
        """初始化SQLite數據庫"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.connection.cursor()
            
            # 創建記憶表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    tags TEXT,
                    metadata TEXT,
                    embedding_hash TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    importance_score REAL DEFAULT 0.5
                )
            ''')
            
            # 創建會話表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    client_type TEXT NOT NULL,
                    client_info TEXT,
                    created_at REAL NOT NULL,
                    last_activity REAL NOT NULL,
                    memory_count INTEGER DEFAULT 0
                )
            ''')
            
            # 創建同步記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_records (
                    sync_id TEXT PRIMARY KEY,
                    source_session TEXT NOT NULL,
                    target_session TEXT NOT NULL,
                    memory_ids TEXT NOT NULL,
                    sync_type TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            # 創建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_source ON memories(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_type ON sessions(client_type)')
            
            self.connection.commit()
            logger.info("✅ Memory RAG數據庫初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 數據庫初始化失敗: {e}")
            raise
    
    async def _initialize_vector_index(self):
        """初始化FAISS向量索引"""
        if not FAISS_AVAILABLE:
            return
        
        try:
            # 創建FAISS索引
            self.vector_index = faiss.IndexFlatIP(self.embedding_dim)  # 內積相似度
            
            # 嘗試加載已存在的索引
            index_path = Path(self.db_path).with_suffix('.faiss')
            if index_path.exists():
                self.vector_index = faiss.read_index(str(index_path))
                logger.info(f"✅ 加載已存在的FAISS索引: {self.vector_index.ntotal} 個向量")
            else:
                logger.info("🆕 創建新的FAISS向量索引")
            
        except Exception as e:
            logger.error(f"❌ FAISS向量索引初始化失敗: {e}")
            self.vector_index = None
    
    async def _load_memory_cache(self):
        """加載記憶緩存"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT id, content, memory_type, tags, importance_score 
                FROM memories 
                WHERE importance_score > 0.7 
                ORDER BY access_count DESC, created_at DESC 
                LIMIT 1000
            ''')
            
            rows = cursor.fetchall()
            for row in rows:
                memory_id, content, memory_type, tags, importance = row
                self.memory_cache[memory_id] = {
                    'content': content,
                    'type': memory_type,
                    'tags': tags.split(',') if tags else [],
                    'importance': importance
                }
            
            logger.info(f"✅ 加載記憶緩存: {len(self.memory_cache)} 條高重要性記憶")
            
        except Exception as e:
            logger.error(f"❌ 記憶緩存加載失敗: {e}")
    
    async def register_session(self, session_id: str, client_type: str, client_info: Dict[str, Any] = None):
        """
        註冊新會話
        
        Args:
            session_id: 會話ID
            client_type: 客戶端類型 (claudeditor/powerautomation)
            client_info: 客戶端信息
        """
        try:
            cursor = self.connection.cursor()
            
            # 插入會話記錄
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_id, client_type, client_info, created_at, last_activity, memory_count)
                VALUES (?, ?, ?, ?, ?, 0)
            ''', (
                session_id,
                client_type,
                json.dumps(client_info or {}),
                time.time(),
                time.time()
            ))
            
            self.connection.commit()
            
            # 添加到對應的會話列表
            if client_type == 'claudeditor':
                self.claudeditor_sessions[session_id] = {
                    'info': client_info,
                    'registered_at': time.time(),
                    'last_activity': time.time()
                }
            elif client_type == 'powerautomation':
                self.powerautomation_sessions[session_id] = {
                    'info': client_info,
                    'registered_at': time.time(),
                    'last_activity': time.time()
                }
            
            logger.info(f"📝 會話註冊成功: {session_id} ({client_type})")
            
        except Exception as e:
            logger.error(f"❌ 會話註冊失敗: {e}")
            raise
    
    async def add_memory(self, content: str, memory_type: str, source: str, 
                        tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """
        添加新記憶
        
        Args:
            content: 記憶內容
            memory_type: 記憶類型
            source: 來源會話ID
            tags: 標籤列表
            metadata: 元數據
            
        Returns:
            記憶ID
        """
        try:
            memory_id = str(uuid.uuid4())
            current_time = time.time()
            
            # 計算重要性分數
            importance_score = await self._calculate_importance(content, memory_type, tags)
            
            # 計算嵌入哈希
            embedding_hash = hashlib.md5(content.encode()).hexdigest()
            
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO memories 
                (id, content, memory_type, source, tags, metadata, embedding_hash, 
                 created_at, updated_at, importance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory_id,
                content,
                memory_type,
                source,
                ','.join(tags or []),
                json.dumps(metadata or {}),
                embedding_hash,
                current_time,
                current_time,
                importance_score
            ))
            
            self.connection.commit()
            
            # 添加到緩存（如果重要性足夠高）
            if importance_score > 0.7:
                self.memory_cache[memory_id] = {
                    'content': content,
                    'type': memory_type,
                    'tags': tags or [],
                    'importance': importance_score
                }
            
            # 更新會話記憶計數
            await self._update_session_memory_count(source)
            
            logger.info(f"🧠 添加記憶: {memory_id} (重要性: {importance_score:.2f})")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ 添加記憶失敗: {e}")
            raise
    
    async def search_memories(self, query: str, session_id: str = None, 
                            memory_types: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索記憶
        
        Args:
            query: 搜索查詢
            session_id: 會話ID（可選）
            memory_types: 記憶類型過濾
            limit: 結果限制
            
        Returns:
            搜索結果列表
        """
        try:
            # 首先在緩存中搜索
            cache_results = await self._search_in_cache(query, limit // 2)
            
            # 在數據庫中搜索
            db_results = await self._search_in_database(query, session_id, memory_types, limit)
            
            # 合併和去重結果
            all_results = cache_results + db_results
            seen_ids = set()
            unique_results = []
            
            for result in all_results:
                if result['id'] not in seen_ids:
                    seen_ids.add(result['id'])
                    unique_results.append(result)
                    
                    # 更新訪問計數
                    await self._update_access_count(result['id'])
            
            return unique_results[:limit]
            
        except Exception as e:
            logger.error(f"❌ 記憶搜索失敗: {e}")
            return []
    
    async def _search_in_cache(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """在緩存中搜索"""
        results = []
        query_lower = query.lower()
        
        for memory_id, memory_data in self.memory_cache.items():
            content_lower = memory_data['content'].lower()
            
            # 簡單的文本匹配評分
            score = 0.0
            
            # 完全匹配
            if query_lower in content_lower:
                score += 1.0
            
            # 關鍵詞匹配
            query_words = query_lower.split()
            content_words = content_lower.split()
            matched_words = len(set(query_words) & set(content_words))
            if len(query_words) > 0:
                score += matched_words / len(query_words) * 0.5
            
            # 標籤匹配
            for tag in memory_data['tags']:
                if tag.lower() in query_lower:
                    score += 0.3
            
            # 重要性權重
            score *= memory_data['importance']
            
            if score > 0.1:  # 最低相關性閾值
                results.append({
                    'id': memory_id,
                    'content': memory_data['content'],
                    'type': memory_data['type'],
                    'tags': memory_data['tags'],
                    'score': score,
                    'source': 'cache'
                })
        
        # 按分數排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    async def _search_in_database(self, query: str, session_id: str = None, 
                                memory_types: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """在數據庫中搜索"""
        try:
            cursor = self.connection.cursor()
            
            # 構建SQL查詢
            sql = '''
                SELECT id, content, memory_type, source, tags, importance_score, access_count
                FROM memories 
                WHERE content LIKE ?
            '''
            params = [f'%{query}%']
            
            # 添加會話過濾
            if session_id:
                sql += ' AND source = ?'
                params.append(session_id)
            
            # 添加類型過濾
            if memory_types:
                placeholders = ','.join(['?' for _ in memory_types])
                sql += f' AND memory_type IN ({placeholders})'
                params.extend(memory_types)
            
            # 排序和限制
            sql += ' ORDER BY importance_score DESC, access_count DESC, created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                memory_id, content, memory_type, source, tags, importance, access_count = row
                
                # 計算相關性分數
                score = importance * 0.6 + min(access_count / 10, 1.0) * 0.4
                
                results.append({
                    'id': memory_id,
                    'content': content,
                    'type': memory_type,
                    'source': source,
                    'tags': tags.split(',') if tags else [],
                    'score': score,
                    'importance': importance,
                    'access_count': access_count,
                    'source': 'database'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 數據庫搜索失敗: {e}")
            return []
    
    async def sync_memories(self, source_session: str, target_sessions: List[str], 
                          memory_types: List[str] = None, 
                          sync_type: str = "bidirectional") -> Dict[str, Any]:
        """
        在會話間同步記憶
        
        Args:
            source_session: 源會話ID
            target_sessions: 目標會話ID列表
            memory_types: 要同步的記憶類型
            sync_type: 同步類型 (bidirectional/one_way)
            
        Returns:
            同步結果
        """
        try:
            sync_id = str(uuid.uuid4())
            synced_memories = []
            
            # 獲取源會話的記憶
            cursor = self.connection.cursor()
            
            sql = 'SELECT id, content, memory_type, tags, importance_score FROM memories WHERE source = ?'
            params = [source_session]
            
            if memory_types:
                placeholders = ','.join(['?' for _ in memory_types])
                sql += f' AND memory_type IN ({placeholders})'
                params.extend(memory_types)
            
            sql += ' ORDER BY importance_score DESC, created_at DESC'
            
            cursor.execute(sql, params)
            source_memories = cursor.fetchall()
            
            # 記錄同步
            for target_session in target_sessions:
                cursor.execute('''
                    INSERT INTO sync_records 
                    (sync_id, source_session, target_session, memory_ids, sync_type, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'in_progress')
                ''', (
                    sync_id + f'_{target_session}',
                    source_session,
                    target_session,
                    json.dumps([m[0] for m in source_memories]),
                    sync_type,
                    time.time()
                ))
            
            self.connection.commit()
            
            # 準備同步數據
            sync_data = []
            for memory in source_memories:
                memory_id, content, memory_type, tags, importance = memory
                sync_data.append({
                    'id': memory_id,
                    'content': content,
                    'type': memory_type,
                    'tags': tags.split(',') if tags else [],
                    'importance': importance,
                    'synced_from': source_session
                })
                synced_memories.append(memory_id)
            
            # 更新同步狀態
            for target_session in target_sessions:
                cursor.execute('''
                    UPDATE sync_records 
                    SET status = 'completed' 
                    WHERE sync_id = ?
                ''', (sync_id + f'_{target_session}',))
            
            self.connection.commit()
            
            logger.info(f"🔄 記憶同步完成: {source_session} → {target_sessions} ({len(synced_memories)} 條記憶)")
            
            return {
                'sync_id': sync_id,
                'source_session': source_session,
                'target_sessions': target_sessions,
                'synced_memories': synced_memories,
                'sync_data': sync_data,
                'sync_type': sync_type,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ 記憶同步失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _calculate_importance(self, content: str, memory_type: str, tags: List[str] = None) -> float:
        """計算記憶重要性分數"""
        score = 0.5  # 基礎分數
        
        # 基於類型的重要性
        type_weights = {
            'goal': 0.9,
            'workflow': 0.8,
            'command_execution': 0.7,
            'user_interaction': 0.6,
            'claude_interaction': 0.6,
            'code_analysis': 0.7,
            'error_handling': 0.8,
            'system_status': 0.4,
            'debug_info': 0.3
        }
        
        score = type_weights.get(memory_type, 0.5)
        
        # 基於內容長度
        if len(content) > 200:
            score += 0.1
        if len(content) > 500:
            score += 0.1
        
        # 基於標籤
        if tags:
            important_tags = ['goal', 'error', 'success', 'critical', 'workflow', 'ai_mode']
            for tag in tags:
                if tag.lower() in important_tags:
                    score += 0.1
        
        # 基於關鍵詞
        important_keywords = ['error', 'success', 'fail', 'complete', 'goal', 'workflow', 'ai', 'powerautomation']
        content_lower = content.lower()
        for keyword in important_keywords:
            if keyword in content_lower:
                score += 0.05
        
        return min(score, 1.0)  # 限制在1.0以內
    
    async def _update_access_count(self, memory_id: str):
        """更新記憶訪問計數"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE memories 
                SET access_count = access_count + 1, updated_at = ?
                WHERE id = ?
            ''', (time.time(), memory_id))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"❌ 更新訪問計數失敗: {e}")
    
    async def _update_session_memory_count(self, session_id: str):
        """更新會話記憶計數"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE sessions 
                SET memory_count = memory_count + 1, last_activity = ?
                WHERE session_id = ?
            ''', (time.time(), session_id))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"❌ 更新會話記憶計數失敗: {e}")
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """獲取記憶統計信息"""
        try:
            cursor = self.connection.cursor()
            
            # 總記憶數
            cursor.execute('SELECT COUNT(*) FROM memories')
            total_memories = cursor.fetchone()[0]
            
            # 按類型分組
            cursor.execute('''
                SELECT memory_type, COUNT(*) 
                FROM memories 
                GROUP BY memory_type 
                ORDER BY COUNT(*) DESC
            ''')
            type_stats = dict(cursor.fetchall())
            
            # 按來源分組
            cursor.execute('''
                SELECT source, COUNT(*) 
                FROM memories 
                GROUP BY source 
                ORDER BY COUNT(*) DESC
            ''')
            source_stats = dict(cursor.fetchall())
            
            # 重要性分佈
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN importance_score >= 0.8 THEN 'high'
                        WHEN importance_score >= 0.6 THEN 'medium'
                        ELSE 'low'
                    END as importance_level,
                    COUNT(*)
                FROM memories
                GROUP BY importance_level
            ''')
            importance_stats = dict(cursor.fetchall())
            
            # 活躍會話
            active_sessions = len(self.claudeditor_sessions) + len(self.powerautomation_sessions)
            
            return {
                'total_memories': total_memories,
                'type_distribution': type_stats,
                'source_distribution': source_stats,
                'importance_distribution': importance_stats,
                'active_sessions': active_sessions,
                'claudeditor_sessions': len(self.claudeditor_sessions),
                'powerautomation_sessions': len(self.powerautomation_sessions),
                'cache_size': len(self.memory_cache),
                'mcp_connected': self.mcp_connected,
                'last_sync_time': self.last_sync_time
            }
            
        except Exception as e:
            logger.error(f"❌ 獲取記憶統計失敗: {e}")
            return {}
    
    async def cleanup_old_memories(self, days_threshold: int = 30, 
                                 importance_threshold: float = 0.3):
        """清理舊的低重要性記憶"""
        try:
            threshold_time = time.time() - (days_threshold * 24 * 3600)
            
            cursor = self.connection.cursor()
            cursor.execute('''
                DELETE FROM memories 
                WHERE created_at < ? AND importance_score < ? AND access_count < 2
            ''', (threshold_time, importance_threshold))
            
            deleted_count = cursor.rowcount
            self.connection.commit()
            
            logger.info(f"🧹 清理舊記憶: 刪除了 {deleted_count} 條低重要性記憶")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 清理記憶失敗: {e}")
            return 0
    
    async def close(self):
        """關閉Memory RAG MCP集成"""
        try:
            # 保存向量索引
            if FAISS_AVAILABLE and self.vector_index:
                index_path = Path(self.db_path).with_suffix('.faiss')
                faiss.write_index(self.vector_index, str(index_path))
            
            # 關閉數據庫連接
            if self.connection:
                self.connection.close()
            
            # 清理會話
            self.claudeditor_sessions.clear()
            self.powerautomation_sessions.clear()
            self.memory_cache.clear()
            
            self.mcp_connected = False
            
            logger.info("✅ Memory RAG MCP集成已關閉")
            
        except Exception as e:
            logger.error(f"❌ 關閉Memory RAG MCP集成失敗: {e}")

# 使用示例
async def main():
    """示例使用"""
    memory_rag = MemoryRAGMCPIntegration()
    
    try:
        # 初始化
        await memory_rag.initialize()
        
        # 註冊會話
        await memory_rag.register_session('claudeditor_1', 'claudeditor', {
            'name': 'ClaudeEditor v4.8.0',
            'version': '4.8.0'
        })
        
        await memory_rag.register_session('powerautomation_1', 'powerautomation', {
            'name': 'PowerAutomation Core',
            'version': '1.0.0'
        })
        
        # 添加記憶
        memory_id = await memory_rag.add_memory(
            content="用戶啟動了目標驅動開發工作流，目標是創建用戶管理系統",
            memory_type="workflow",
            source="claudeditor_1",
            tags=["goal", "workflow", "user_management"]
        )
        
        print(f"添加記憶: {memory_id}")
        
        # 搜索記憶
        results = await memory_rag.search_memories("用戶管理", limit=5)
        print(f"搜索結果: {len(results)} 條")
        
        # 同步記憶
        sync_result = await memory_rag.sync_memories(
            source_session="claudeditor_1",
            target_sessions=["powerautomation_1"],
            sync_type="bidirectional"
        )
        
        print(f"同步結果: {sync_result['success']}")
        
        # 獲取統計
        stats = await memory_rag.get_memory_statistics()
        print(f"記憶統計: {stats}")
        
    finally:
        await memory_rag.close()

if __name__ == "__main__":
    asyncio.run(main())