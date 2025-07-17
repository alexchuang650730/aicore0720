#!/usr/bin/env python3
"""
统一的 Memory RAG 接口 v2.0 - PowerAutomation v4.8
集成高性能多 Provider 支持

核心功能:
1. 统一的查询接口
2. 高性能多 Provider 路由（Groq > Together > Novita > Infini-AI）
3. 模式感知的个性化（教师模式 vs 助手模式）
4. 智能故障回退和负载均衡
5. 实时性能监控和优化
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json

# 导入核心组件
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.components.memoryos_mcp.memory_engine import MemoryEngine, MemoryType
from core.components.memoryos_mcp.learning_adapter import LearningAdapter, QueryContext, InteractionMode
from core.components.aws_bedrock_mcp.rag_service import RAGService
from core.components.aws_bedrock_mcp.multi_provider_integration import HighPerformanceMultiProviderRAG

logger = logging.getLogger(__name__)

class QueryMode(Enum):
    """查询模式枚举"""
    TEACHER_MODE = "teacher_mode"      # Claude Code Tool 模式
    ASSISTANT_MODE = "assistant_mode"  # 其他工具模式
    AUTO_MODE = "auto_mode"           # 自动检测模式

class ServiceProvider(Enum):
    """服务提供者枚举"""
    MEMORY_OS = "memoryos_mcp"
    HIGH_PERF_MULTI = "high_perf_multi_provider"
    HYBRID = "hybrid"

@dataclass
class QueryResult:
    """查询结果数据类"""
    status: str
    response: str
    provider: str
    model: Optional[str] = None
    response_time: float = 0.0
    context_used: int = 0
    mode: str = "auto"
    personalized: bool = False
    performance_score: float = 0.0
    metadata: Dict[str, Any] = None

class UnifiedMemoryRAGInterface:
    """统一的 Memory RAG 接口 v2.0"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.is_initialized = False
        
        # 核心组件
        self.memory_engine: Optional[MemoryEngine] = None
        self.learning_adapter: Optional[LearningAdapter] = None
        self.rag_service: Optional[RAGService] = None
        self.multi_provider_rag: Optional[HighPerformanceMultiProviderRAG] = None
        
        # 服务状态
        self.service_status = {
            "memoryos_mcp": False,
            "learning_adapter": False,
            "rag_service": False,
            "multi_provider_rag": False
        }
        
        # 统计信息
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "provider_usage": {
                "memoryos_mcp": 0,
                "high_perf_multi_provider": 0,
                "hybrid": 0
            },
            "mode_usage": {
                "teacher_mode": 0,
                "assistant_mode": 0,
                "auto_mode": 0
            }
        }
        
        logger.info("🔧 UnifiedMemoryRAGInterface v2.0 初始化完成")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "memory_engine": {
                "db_path": "unified_memory.db",
                "enable_rag": True,
                "enable_s3": True,
                "max_memories": 10000
            },
            "learning_adapter": {
                "enable_mode_awareness": True,
                "teacher_mode_depth": "detailed",
                "assistant_mode_style": "concise"
            },
            "routing": {
                "default_provider": "hybrid",
                "fallback_enabled": True,
                "load_balancing": True,
                "prefer_high_performance": True
            },
            "performance": {
                "query_timeout": 30.0,
                "max_concurrent_queries": 50,
                "cache_enabled": True,
                "cache_ttl": 300
            }
        }
    
    async def initialize(self) -> bool:
        """初始化所有组件"""
        try:
            logger.info("🚀 开始初始化统一 Memory RAG 接口 v2.0...")
            
            # 初始化 MemoryEngine
            await self._initialize_memory_engine()
            
            # 初始化 LearningAdapter
            await self._initialize_learning_adapter()
            
            # 初始化 RAGService
            await self._initialize_rag_service()
            
            # 初始化高性能多 Provider 集成
            await self._initialize_multi_provider_rag()
            
            # 验证组件状态
            await self._verify_components()
            
            self.is_initialized = True
            logger.info("✅ 统一 Memory RAG 接口 v2.0 初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 统一接口初始化失败: {e}")
            return False
    
    async def _initialize_memory_engine(self):
        """初始化 MemoryEngine"""
        try:
            logger.info("🔧 初始化 MemoryEngine...")
            
            config = self.config["memory_engine"]
            self.memory_engine = MemoryEngine(
                db_path=config["db_path"],
                max_memories=config["max_memories"],
                enable_rag=config["enable_rag"],
                enable_s3=config["enable_s3"]
            )
            
            await self.memory_engine.initialize()
            
            logger.info("✅ MemoryEngine 初始化成功")
            self.service_status["memoryos_mcp"] = True
            
        except Exception as e:
            logger.error(f"❌ MemoryEngine 初始化失败: {e}")
            self.service_status["memoryos_mcp"] = False
    
    async def _initialize_learning_adapter(self):
        """初始化 LearningAdapter"""
        try:
            logger.info("🔧 初始化 LearningAdapter...")
            
            self.learning_adapter = LearningAdapter(
                memory_engine=self.memory_engine,
                context_manager=None  # 使用正确的参数
            )
            
            await self.learning_adapter.initialize()
            
            logger.info("✅ LearningAdapter 初始化成功")
            self.service_status["learning_adapter"] = True
            
        except Exception as e:
            logger.error(f"❌ LearningAdapter 初始化失败: {e}")
            self.service_status["learning_adapter"] = False
    
    async def _initialize_rag_service(self):
        """初始化 RAGService"""
        try:
            logger.info("🔧 初始化 RAGService...")
            
            self.rag_service = RAGService()
            await self.rag_service.initialize()
            
            logger.info("✅ RAGService 初始化成功")
            self.service_status["rag_service"] = True
            
        except Exception as e:
            logger.error(f"❌ RAGService 初始化失败: {e}")
            self.service_status["rag_service"] = False
    
    async def _initialize_multi_provider_rag(self):
        """初始化高性能多 Provider RAG"""
        try:
            logger.info("🚀 初始化高性能多 Provider RAG...")
            
            self.multi_provider_rag = HighPerformanceMultiProviderRAG()
            
            logger.info("✅ 高性能多 Provider RAG 初始化成功")
            self.service_status["multi_provider_rag"] = True
            
        except Exception as e:
            logger.error(f"❌ 高性能多 Provider RAG 初始化失败: {e}")
            self.service_status["multi_provider_rag"] = False
    
    async def _verify_components(self):
        """验证组件状态"""
        healthy_services = sum(self.service_status.values())
        total_services = len(self.service_status)
        
        if healthy_services == 0:
            raise Exception("所有服务都不可用")
        elif healthy_services < total_services:
            logger.warning(f"⚠️ 部分服务不可用 ({healthy_services}/{total_services})")
        else:
            logger.info(f"✅ 所有服务正常 ({healthy_services}/{total_services})")
    
    async def query(self, 
                   query: str, 
                   context: QueryContext = None,
                   top_k: int = 5) -> QueryResult:
        """统一查询接口"""
        if not self.is_initialized:
            raise Exception("接口未初始化")
        
        start_time = time.time()
        self.stats["total_queries"] += 1
        
        # 创建默认上下文
        if context is None:
            context = QueryContext(
                user_id="default",
                session_id="default",
                current_tool="unknown",
                current_model="unknown",
                query_type="general"
            )
        
        try:
            # 1. 模式检测
            detected_mode = self._detect_query_mode(context)
            self.stats["mode_usage"][detected_mode.value] += 1
            
            # 2. 路由决策
            provider = await self._route_query(query, context, detected_mode)
            
            # 3. 执行查询
            raw_result = await self._execute_query(query, context, provider, top_k)
            
            # 4. 个性化处理
            personalized_result = await self._personalize_result(
                raw_result, context, detected_mode
            )
            
            # 5. 构建最终结果
            response_time = time.time() - start_time
            self.stats["successful_queries"] += 1
            self._update_avg_response_time(response_time)
            
            return QueryResult(
                status="success",
                response=personalized_result["response"],
                provider=personalized_result["provider"],
                model=personalized_result.get("model"),
                response_time=response_time,
                context_used=personalized_result.get("context_used", 0),
                mode=detected_mode.value,
                personalized=personalized_result.get("personalized", False),
                performance_score=personalized_result.get("performance_score", 0.0),
                metadata={
                    "routing_decision": provider.value,
                    "personalization_applied": personalized_result.get("personalized", False),
                    "provider_stats": personalized_result.get("provider_stats", {})
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self.stats["failed_queries"] += 1
            self._update_avg_response_time(response_time)
            
            logger.error(f"❌ 查询失败: {e}")
            return QueryResult(
                status="error",
                response=f"查询失败: {str(e)}",
                provider="none",
                response_time=response_time,
                metadata={"error": str(e)}
            )
    
    def _detect_query_mode(self, context: QueryContext) -> QueryMode:
        """检测查询模式"""
        # 检测教师模式（Claude Code Tool + Claude 模型）
        if (context.current_tool == "claude_code_tool" and 
            context.current_model == "claude"):
            return QueryMode.TEACHER_MODE
        
        # 其他情况为助手模式
        return QueryMode.ASSISTANT_MODE
    
    async def _route_query(self, 
                          query: str, 
                          context: QueryContext, 
                          mode: QueryMode) -> ServiceProvider:
        """智能路由决策"""
        
        # 优先使用高性能多 Provider（如果可用）
        if (self.service_status["multi_provider_rag"] and 
            self.config["routing"]["prefer_high_performance"]):
            return ServiceProvider.HIGH_PERF_MULTI
        
        # 混合模式：同时使用多个服务
        if (self.service_status["memoryos_mcp"] and 
            self.service_status["rag_service"]):
            return ServiceProvider.HYBRID
        
        # 降级到单一服务
        if self.service_status["memoryos_mcp"]:
            return ServiceProvider.MEMORY_OS
        
        if self.service_status["multi_provider_rag"]:
            return ServiceProvider.HIGH_PERF_MULTI
        
        raise Exception("没有可用的服务提供者")
    
    async def _execute_query(self, 
                           query: str, 
                           context: QueryContext, 
                           provider: ServiceProvider, 
                           top_k: int) -> Dict[str, Any]:
        """执行查询"""
        
        if provider == ServiceProvider.HIGH_PERF_MULTI:
            return await self._query_high_perf_multi_provider(query, context, top_k)
        
        elif provider == ServiceProvider.MEMORY_OS:
            return await self._query_memory_os(query, context, top_k)
        
        elif provider == ServiceProvider.HYBRID:
            return await self._query_hybrid(query, context, top_k)
        
        else:
            raise Exception(f"不支持的服务提供者: {provider}")
    
    async def _query_high_perf_multi_provider(self, 
                                            query: str, 
                                            context: QueryContext, 
                                            top_k: int) -> Dict[str, Any]:
        """查询高性能多 Provider"""
        
        # 从 MemoryEngine 获取相关文档作为上下文
        context_docs = []
        if self.memory_engine:
            try:
                # 使用 RAG 查询获取相关文档
                rag_results = await self.memory_engine.rag_query(query, top_k=top_k)
                context_docs = [
                    {
                        "content": result["content"],
                        "metadata": {"source": "memory_engine", "score": result.get("score", 0.0)}
                    }
                    for result in rag_results
                ]
            except Exception as e:
                logger.warning(f"⚠️ 从 MemoryEngine 获取上下文失败: {e}")
        
        # 调用高性能多 Provider
        result = await self.multi_provider_rag.generate_rag_response(
            query=query,
            context_documents=context_docs,
            max_tokens=500
        )
        
        self.stats["provider_usage"]["high_perf_multi_provider"] += 1
        
        return {
            "response": result.get("response", ""),
            "provider": f"high_perf_multi_provider:{result.get('provider', 'unknown')}",
            "model": result.get("model"),
            "context_used": result.get("context_used", len(context_docs)),
            "performance_score": result.get("performance_score", 0.0),
            "provider_stats": {
                "response_time": result.get("response_time", 0.0),
                "priority": result.get("priority", 0)
            }
        }
    
    async def _query_memory_os(self, 
                             query: str, 
                             context: QueryContext, 
                             top_k: int) -> Dict[str, Any]:
        """查询 MemoryOS MCP"""
        
        # 使用 MemoryEngine 的 RAG 功能
        rag_results = await self.memory_engine.rag_query(query, top_k=top_k)
        
        # 构建响应
        if rag_results:
            response = f"基于记忆库的回答：\n\n"
            for i, result in enumerate(rag_results[:3]):  # 限制最多3个结果
                response += f"{i+1}. {result['content']}\n\n"
        else:
            response = "在记忆库中没有找到相关信息。"
        
        self.stats["provider_usage"]["memoryos_mcp"] += 1
        
        return {
            "response": response,
            "provider": "memoryos_mcp",
            "model": "memory_engine_rag",
            "context_used": len(rag_results),
            "performance_score": 70.0  # 固定分数
        }
    
    async def _query_hybrid(self, 
                          query: str, 
                          context: QueryContext, 
                          top_k: int) -> Dict[str, Any]:
        """混合查询（并行查询多个服务）"""
        
        tasks = []
        
        # 添加高性能多 Provider 查询
        if self.service_status["multi_provider_rag"]:
            tasks.append(self._query_high_perf_multi_provider(query, context, top_k))
        
        # 添加 MemoryOS 查询
        if self.service_status["memoryos_mcp"]:
            tasks.append(self._query_memory_os(query, context, top_k))
        
        # 并行执行查询
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 选择最佳结果
        best_result = None
        best_score = 0.0
        
        for result in results:
            if isinstance(result, dict) and not isinstance(result, Exception):
                score = result.get("performance_score", 0.0)
                if score > best_score:
                    best_score = score
                    best_result = result
        
        if best_result:
            self.stats["provider_usage"]["hybrid"] += 1
            best_result["provider"] = f"hybrid:{best_result['provider']}"
            return best_result
        else:
            raise Exception("混合查询失败：所有服务都不可用")
    
    async def _personalize_result(self, 
                                raw_result: Dict[str, Any], 
                                context: QueryContext, 
                                mode: QueryMode) -> Dict[str, Any]:
        """个性化处理结果"""
        
        if not self.learning_adapter:
            raw_result["personalized"] = False
            return raw_result
        
        try:
            # 转换模式
            interaction_mode = (InteractionMode.TEACHER_MODE 
                              if mode == QueryMode.TEACHER_MODE 
                              else InteractionMode.ASSISTANT_MODE)
            
            # 应用个性化
            personalized_response = await self.learning_adapter.personalize_response(
                response=raw_result["response"],
                context=context,
                mode=interaction_mode
            )
            
            raw_result["response"] = personalized_response
            raw_result["personalized"] = True
            
        except Exception as e:
            logger.warning(f"⚠️ 个性化处理失败: {e}")
            raw_result["personalized"] = False
        
        return raw_result
    
    def _update_avg_response_time(self, response_time: float):
        """更新平均响应时间"""
        total_queries = self.stats["successful_queries"] + self.stats["failed_queries"]
        if total_queries > 0:
            current_avg = self.stats["avg_response_time"]
            self.stats["avg_response_time"] = (
                (current_avg * (total_queries - 1) + response_time) / total_queries
            )
    
    async def add_document(self, 
                          doc_id: str, 
                          content: str, 
                          metadata: Dict[str, Any] = None) -> bool:
        """添加文档到系统"""
        success_count = 0
        total_attempts = 0
        
        # 添加到 MemoryEngine
        if self.memory_engine:
            try:
                await self.memory_engine.add_document_to_rag(doc_id, content, metadata or {})
                success_count += 1
            except Exception as e:
                logger.error(f"❌ 添加文档到 MemoryEngine 失败: {e}")
            total_attempts += 1
        
        # 添加到 RAGService
        if self.rag_service:
            try:
                await self.rag_service.add_document(doc_id, content, metadata or {})
                success_count += 1
            except Exception as e:
                logger.error(f"❌ 添加文档到 RAGService 失败: {e}")
            total_attempts += 1
        
        return success_count > 0
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "overall_status": "healthy",
            "components": {},
            "statistics": self.stats,
            "performance": {}
        }
        
        # 检查各组件状态
        for service_name, is_healthy in self.service_status.items():
            health_status["components"][service_name] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "initialized": is_healthy
            }
        
        # 检查高性能多 Provider 状态
        if self.multi_provider_rag:
            try:
                multi_provider_health = await self.multi_provider_rag.health_check()
                health_status["performance"]["multi_provider"] = multi_provider_health
            except Exception as e:
                logger.error(f"❌ 多 Provider 健康检查失败: {e}")
        
        # 计算整体状态
        healthy_count = sum(self.service_status.values())
        total_count = len(self.service_status)
        
        if healthy_count == 0:
            health_status["overall_status"] = "unhealthy"
        elif healthy_count < total_count:
            health_status["overall_status"] = "degraded"
        
        return health_status
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        # 添加高性能多 Provider 统计
        if self.multi_provider_rag:
            try:
                multi_provider_stats = self.multi_provider_rag.get_statistics()
                stats["multi_provider"] = multi_provider_stats
            except Exception as e:
                logger.error(f"❌ 获取多 Provider 统计失败: {e}")
        
        return stats


# 测试代码
async def main():
    """测试统一 Memory RAG 接口 v2.0"""
    print("🚀 测试统一 Memory RAG 接口 v2.0（集成高性能多 Provider）...")
    
    # 创建接口实例
    interface = UnifiedMemoryRAGInterface()
    
    # 初始化
    print("\n🔧 初始化接口...")
    success = await interface.initialize()
    if not success:
        print("❌ 初始化失败")
        return
    
    # 测试查询（教师模式）
    print("\n👨‍🏫 测试教师模式查询...")
    teacher_context = QueryContext(
        current_tool="claude_code_tool",
        current_model="claude",
        user_id="test_user",
        session_id="test_session"
    )
    
    result = await interface.query(
        query="如何使用 Python 开发高性能的 Web API？",
        context=teacher_context,
        top_k=5
    )
    print(f"✅ 教师模式结果: {result}")
    
    # 测试查询（助手模式）
    print("\n🤖 测试助手模式查询...")
    assistant_context = QueryContext(
        current_tool="other_tool",
        current_model="k2",
        user_id="test_user",
        session_id="test_session"
    )
    
    result = await interface.query(
        query="Python Web API 开发的最佳实践是什么？",
        context=assistant_context,
        top_k=3
    )
    print(f"✅ 助手模式结果: {result}")
    
    # 测试健康检查
    print("\n🏥 测试健康检查...")
    health = await interface.health_check()
    print(f"✅ 健康状态: {health}")
    
    # 测试统计信息
    print("\n📊 测试统计信息...")
    stats = interface.get_statistics()
    print(f"✅ 统计信息: {stats}")
    
    print("✅ 统一 Memory RAG 接口 v2.0 测试完成")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

