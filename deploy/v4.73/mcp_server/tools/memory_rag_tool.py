"""
Memory RAG工具
基于现有的Memory RAG MCP组件，提供标准的MCP工具接口
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

# 添加项目根目录到path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.components.memoryos_mcp.memory_engine import MemoryEngine
from core.components.memoryos_mcp.context_manager import ContextManager
from core.components.memoryos_mcp.learning_adapter import LearningAdapter

logger = logging.getLogger(__name__)

class MemoryRAGTool:
    """Memory RAG工具类"""
    
    def __init__(self):
        """初始化Memory RAG工具"""
        self.memory_engine = None
        self.context_manager = None
        self.learning_adapter = None
        self._initialize()
    
    def _initialize(self):
        """初始化组件"""
        try:
            # 初始化内存引擎
            self.memory_engine = MemoryEngine()
            
            # 初始化上下文管理器
            self.context_manager = ContextManager()
            
            # 初始化学习适配器
            self.learning_adapter = LearningAdapter()
            
            logger.info("✅ Memory RAG工具初始化完成")
        except Exception as e:
            logger.error(f"❌ Memory RAG工具初始化失败: {e}")
            # 创建模拟实现作为备选
            self._create_fallback_implementation()
    
    def _create_fallback_implementation(self):
        """创建备选实现"""
        logger.warning("⚠️ 使用Memory RAG备选实现")
        
        class FallbackMemoryEngine:
            def __init__(self):
                self.memories = []
            
            async def add_memory(self, content: str, memory_type: str, tags: List[str] = None, importance: float = 0.5):
                memory_id = f"mem_{len(self.memories)}"
                memory = {
                    "id": memory_id,
                    "content": content,
                    "memory_type": memory_type,
                    "tags": tags or [],
                    "importance": importance
                }
                self.memories.append(memory)
                return memory_id
            
            async def rag_query(self, query: str, top_k: int = 5, memory_types: List[str] = None):
                # 简单的文本匹配
                results = []
                for memory in self.memories:
                    if memory_types and memory["memory_type"] not in memory_types:
                        continue
                    
                    # 简单的关键词匹配
                    if any(word.lower() in memory["content"].lower() for word in query.split()):
                        results.append({
                            "memory": memory,
                            "score": 0.8,
                            "content": memory["content"]
                        })
                
                return results[:top_k]
        
        self.memory_engine = FallbackMemoryEngine()
        self.context_manager = type('MockContextManager', (), {})()
        self.learning_adapter = type('MockLearningAdapter', (), {})()
    
    async def query(self, query: str, top_k: int = 5, memory_types: List[str] = None) -> Dict[str, Any]:
        """
        查询记忆库
        
        Args:
            query: 查询内容
            top_k: 返回结果数量
            memory_types: 记忆类型筛选
            
        Returns:
            查询结果
        """
        try:
            logger.info(f"📋 Memory RAG查询: {query}")
            
            # 执行RAG查询
            results = await self.memory_engine.rag_query(
                query=query,
                top_k=top_k,
                memory_types=memory_types
            )
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.get("content", ""),
                    "memory_type": result.get("memory", {}).get("memory_type", "unknown"),
                    "score": result.get("score", 0.0),
                    "tags": result.get("memory", {}).get("tags", []),
                    "importance": result.get("memory", {}).get("importance", 0.0)
                })
            
            return {
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Memory RAG查询失败: {e}")
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def store(self, content: str, memory_type: str, tags: List[str] = None, importance: float = 0.5) -> str:
        """
        存储记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            tags: 标签
            importance: 重要性评分
            
        Returns:
            记忆ID
        """
        try:
            logger.info(f"💾 存储记忆: {memory_type}")
            
            # 存储记忆
            memory_id = await self.memory_engine.add_memory(
                content=content,
                memory_type=memory_type,
                tags=tags or [],
                importance=importance
            )
            
            logger.info(f"✅ 记忆存储成功: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ 记忆存储失败: {e}")
            raise
    
    async def get_context_enhancement(self, query: str, context: List[str] = None) -> Dict[str, Any]:
        """
        获取上下文增强
        
        Args:
            query: 查询内容
            context: 当前上下文
            
        Returns:
            增强的上下文信息
        """
        try:
            # 获取相关记忆
            memory_results = await self.query(query, top_k=3)
            
            # 获取上下文建议
            context_suggestions = []
            if hasattr(self.context_manager, 'get_context_recommendations'):
                context_suggestions = await self.context_manager.get_context_recommendations(query)
            
            # 获取学习建议
            learning_insights = []
            if hasattr(self.learning_adapter, 'get_learning_insights'):
                learning_insights = await self.learning_adapter.get_learning_insights(query)
            
            return {
                "query": query,
                "memory_results": memory_results["results"],
                "context_suggestions": context_suggestions,
                "learning_insights": learning_insights,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ 上下文增强失败: {e}")
            return {
                "query": query,
                "memory_results": [],
                "context_suggestions": [],
                "learning_insights": [],
                "status": "error",
                "error": str(e)
            }