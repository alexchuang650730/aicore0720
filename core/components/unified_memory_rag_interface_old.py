#!/usr/bin/env python3
"""
统一的 Memory RAG 接口 - PowerAutomation v4.8

这个模块提供了一个统一的接口来协调 memoryos_mcp 和 aws_bedrock_mcp 的功能，
实现无缝的 Memory RAG 体验。

核心功能:
1. 统一的查询接口
2. 智能路由决策
3. 模式感知的个性化
4. 性能监控和优化
5. 错误处理和降级

设计原则:
- 单一入口点，简化使用
- 智能路由，自动选择最佳服务
- 模式感知，提供个性化体验
- 高可用性，支持降级和恢复
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
from .memoryos_mcp.memory_engine import MemoryEngine, MemoryType
from .memoryos_mcp.learning_adapter import LearningAdapter, QueryContext
from .aws_bedrock_mcp.rag_service import RAGService
from .aws_bedrock_mcp.multi_provider_integration import HighPerformanceMultiProviderRAG

logger = logging.getLogger(__name__)

class QueryMode(Enum):
    """查询模式枚举"""
    TEACHER_MODE = "teacher_mode"      # Claude Code Tool 模式
    ASSISTANT_MODE = "assistant_mode"  # 其他工具模式
    AUTO_MODE = "auto_mode"           # 自动检测模式

class ServiceProvider(Enum):
    """服务提供者枚举"""
    MEMORY_OS = "memoryos_mcp"
    AWS_BEDROCK = "aws_bedrock_mcp"
    HYBRID = "hybrid"

@dataclass
class QueryContext:
    """查询上下文数据结构"""
    user_id: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    current_tool: Optional[str] = None
    current_model: Optional[str] = None
    mode: QueryMode = QueryMode.AUTO_MODE
    preferences: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

@dataclass
class QueryResult:
    """查询结果数据结构"""
    content: str
    sources: List[Dict[str, Any]]
    confidence: float
    processing_time: float
    provider: ServiceProvider
    mode: QueryMode
    personalized: bool
    metadata: Dict[str, Any]

class UnifiedMemoryRAGInterface:
    """统一的 Memory RAG 接口"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化统一接口"""
        self.config = config or self._get_default_config()
        
        # 核心组件
        self.memory_engine = None
        self.learning_adapter = None
        self.integration_manager = None
        self.k2_router = None
        self.rag_service = None
        
        # 状态管理
        self.is_initialized = False
        self.service_status = {
            "memoryos_mcp": False,
            "aws_bedrock_mcp": False
        }
        
        # 性能统计
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "provider_usage": {
                "memoryos_mcp": 0,
                "aws_bedrock_mcp": 0,
                "hybrid": 0
            }
        }
        
        logger.info("🔧 UnifiedMemoryRAGInterface 初始化完成")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "memory_engine": {
                "db_path": "unified_memory.db",
                "enable_rag": True,
                "enable_s3": True
            },
            "learning_adapter": {
                "enable_mode_awareness": True,
                "teacher_mode_depth": "detailed",
                "assistant_mode_style": "concise"
            },
            "routing": {
                "default_provider": "hybrid",
                "fallback_enabled": True,
                "load_balancing": True
            },
            "performance": {
                "query_timeout": 30.0,
                "max_concurrent_queries": 20,
                "cache_enabled": True,
                "cache_ttl": 300
            }
        }
    
    async def initialize(self) -> bool:
        """初始化所有组件"""
        try:
            logger.info("🚀 开始初始化统一 Memory RAG 接口...")
            
            # 初始化 MemoryEngine
            await self._initialize_memory_engine()
            
            # 初始化 LearningAdapter
            await self._initialize_learning_adapter()
            
            # 初始化 AWS Bedrock MCP 组件
            await self._initialize_aws_bedrock_components()
            
            # 验证组件状态
            await self._verify_components()
            
            self.is_initialized = True
            logger.info("✅ 统一 Memory RAG 接口初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 统一接口初始化失败: {e}")
            return False
    
    async def _initialize_memory_engine(self):
        """初始化 MemoryEngine"""
        try:
            config = self.config["memory_engine"]
            self.memory_engine = MemoryEngine(
                db_path=config["db_path"],
                enable_rag=config["enable_rag"],
                enable_s3=config["enable_s3"]
            )
            await self.memory_engine.initialize()
            self.service_status["memoryos_mcp"] = True
            logger.info("✅ MemoryEngine 初始化成功")
            
        except Exception as e:
            logger.error(f"❌ MemoryEngine 初始化失败: {e}")
            self.service_status["memoryos_mcp"] = False
    
    async def _initialize_learning_adapter(self):
        """初始化 LearningAdapter"""
        try:
            # 创建模拟的 context_manager
            class MockContextManager:
                async def get_context(self, context_id):
                    return None
            
            self.learning_adapter = LearningAdapter(
                memory_engine=self.memory_engine,
                context_manager=MockContextManager()
            )
            await self.learning_adapter.initialize()
            logger.info("✅ LearningAdapter 初始化成功")
            
        except Exception as e:
            logger.error(f"❌ LearningAdapter 初始化失败: {e}")
            self.learning_ada    async def _initialize_aws_bedrock_components(self):
        """初始化 AWS Bedrock MCP 组件"""
        try:
            logger.info("🔧 初始化 AWS Bedrock MCP 组件...")
            
            # 初始化 RAGService
            self.rag_service = RAGService()
            await self.rag_service.initialize()
            
            # 初始化高性能多 Provider 集成
            self.multi_provider_rag = HighPerformanceMultiProviderRAG()
            logger.info("🚀 高性能多 Provider RAG 集成初始化完成")
            
            logger.info("✅ AWS Bedrock MCP 组件初始化成功")
            self.service_status["aws_bedrock_mcp"] = True
            
        except Exception as e:
            logger.error(f"❌ AWS Bedrock MCP 组件初始化失败: {e}")
            self.service_status["aws_bedrock_mcp"] = False   """验证组件状态"""
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
                   context: QueryContext,
                   top_k: int = 5) -> QueryResult:
        """统一查询接口"""
        if not self.is_initialized:
            raise Exception("接口未初始化")
        
        start_time = time.time()
        self.stats["total_queries"] += 1
        
        try:
            # 1. 模式检测
            detected_mode = self._detect_query_mode(context)
            
            # 2. 路由决策
            provider = await self._route_query(query, context, detected_mode)
            
            # 3. 执行查询
            raw_result = await self._execute_query(query, context, provider, top_k)
            
            # 4. 个性化处理
            personalized_result = await self._personalize_result(
                raw_result, context, detected_mode
            )
            
            # 5. 构建最终结果
            processing_time = time.time() - start_time
            result = QueryResult(
                content=personalized_result["content"],
                sources=personalized_result["sources"],
                confidence=personalized_result["confidence"],
                processing_time=processing_time,
                provider=provider,
                mode=detected_mode,
                personalized=True,
                metadata=personalized_result.get("metadata", {})
            )
            
            # 6. 更新统计
            self._update_stats(provider, processing_time, True)
            
            # 7. 学习和适配
            await self._learn_from_interaction(query, result, context)
            
            logger.info(f"✅ 查询完成: {processing_time:.3f}s, 模式: {detected_mode.value}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(ServiceProvider.HYBRID, processing_time, False)
            logger.error(f"❌ 查询失败: {e}")
            
            # 返回错误结果
            return QueryResult(
                content=f"查询处理失败: {str(e)}",
                sources=[],
                confidence=0.0,
                processing_time=processing_time,
                provider=ServiceProvider.HYBRID,
                mode=context.mode,
                personalized=False,
                metadata={"error": str(e)}
            )
    
    def _detect_query_mode(self, context: QueryContext) -> QueryMode:
        """检测查询模式"""
        if context.mode != QueryMode.AUTO_MODE:
            return context.mode
        
        # 自动模式检测
        if (context.current_tool == "claude_code_tool" and 
            context.current_model == "claude"):
            return QueryMode.TEACHER_MODE
        else:
            return QueryMode.ASSISTANT_MODE
    
    async def _route_query(self, 
                          query: str, 
                          context: QueryContext, 
                          mode: QueryMode) -> ServiceProvider:
        """路由决策"""
        try:
            # 检查服务可用性
            memoryos_available = self.service_status["memoryos_mcp"]
            bedrock_available = self.service_status["aws_bedrock_mcp"]
            
            # 根据配置和可用性决策
            if self.config["routing"]["default_provider"] == "hybrid":
                if memoryos_available and bedrock_available:
                    return ServiceProvider.HYBRID
                elif memoryos_available:
                    return ServiceProvider.MEMORY_OS
                elif bedrock_available:
                    return ServiceProvider.AWS_BEDROCK
                else:
                    raise Exception("没有可用的服务提供者")
            
            # 单一提供者模式
            elif self.config["routing"]["default_provider"] == "memoryos_mcp":
                if memoryos_available:
                    return ServiceProvider.MEMORY_OS
                elif bedrock_available and self.config["routing"]["fallback_enabled"]:
                    return ServiceProvider.AWS_BEDROCK
                else:
                    raise Exception("MemoryOS MCP 不可用且未启用降级")
            
            else:  # aws_bedrock_mcp
                if bedrock_available:
                    return ServiceProvider.AWS_BEDROCK
                elif memoryos_available and self.config["routing"]["fallback_enabled"]:
                    return ServiceProvider.MEMORY_OS
                else:
                    raise Exception("AWS Bedrock MCP 不可用且未启用降级")
                    
        except Exception as e:
            logger.error(f"路由决策失败: {e}")
            return ServiceProvider.HYBRID
    
    async def _execute_query(self, 
                           query: str, 
                           context: QueryContext, 
                           provider: ServiceProvider,
                           top_k: int) -> Dict[str, Any]:
        """执行查询"""
        if provider == ServiceProvider.MEMORY_OS:
            return await self._query_memory_os(query, context, top_k)
        elif provider == ServiceProvider.AWS_BEDROCK:
            return await self._query_aws_bedrock(query, context, top_k)
        else:  # HYBRID
            return await self._query_hybrid(query, context, top_k)
    
    async def _query_memory_os(self, 
                              query: str, 
                              context: QueryContext, 
                              top_k: int) -> Dict[str, Any]:
        """查询 MemoryOS MCP"""
        try:
            # 使用 MemoryEngine 的 RAG 查询
            results = await self.memory_engine.rag_query(query, top_k)
            
            return {
                "content": self._format_memory_results(results),
                "sources": results,
                "confidence": self._calculate_confidence(results),
                "provider": "memoryos_mcp"
            }
            
        except Exception as e:
            logger.error(f"MemoryOS 查询失败: {e}")
            raise
    
    async def _query_aws_bedrock(self, 
                                query: str, 
                                context: QueryContext, 
                                top_k: int) -> Dict[str, Any]:
        """查询 AWS Bedrock MCP"""
        try:
            # 直接使用 RAGService 进行查询
            result = await self.rag_service.retrieve_documents(query, top_k=top_k)
            
            if result["status"] == "success":
                return {
                    "content": f"基于 {len(result['documents'])} 个文档的回答",
                    "sources": result["documents"],
                    "confidence": 0.8,
                    "provider": "aws_bedrock_mcp"
                }
            else:
                return {
                    "content": "查询失败",
                    "sources": [],
                    "confidence": 0.0,
                    "provider": "aws_bedrock_mcp"
                }
            
        except Exception as e:
            logger.error(f"AWS Bedrock 查询失败: {e}")
            raise
    
    async def _query_hybrid(self, 
                           query: str, 
                           context: QueryContext, 
                           top_k: int) -> Dict[str, Any]:
        """混合查询"""
        try:
            # 并行查询两个服务
            tasks = []
            
            if self.service_status["memoryos_mcp"]:
                tasks.append(self._query_memory_os(query, context, top_k))
            
            if self.service_status["aws_bedrock_mcp"]:
                tasks.append(self._query_aws_bedrock(query, context, top_k))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 合并结果
            return self._merge_results(results)
            
        except Exception as e:
            logger.error(f"混合查询失败: {e}")
            raise
    
    def _merge_results(self, results: List[Any]) -> Dict[str, Any]:
        """合并查询结果"""
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        if not valid_results:
            raise Exception("所有查询都失败了")
        
        # 简单合并策略：选择置信度最高的结果
        best_result = max(valid_results, key=lambda x: x.get("confidence", 0))
        
        # 合并所有来源
        all_sources = []
        for result in valid_results:
            all_sources.extend(result.get("sources", []))
        
        return {
            "content": best_result["content"],
            "sources": all_sources,
            "confidence": best_result["confidence"],
            "provider": "hybrid"
        }
    
    async def _personalize_result(self, 
                                 raw_result: Dict[str, Any], 
                                 context: QueryContext, 
                                 mode: QueryMode) -> Dict[str, Any]:
        """个性化处理结果"""
        if not self.learning_adapter:
            return raw_result
        
        try:
            # 根据模式应用个性化
            if mode == QueryMode.TEACHER_MODE:
                personalized_content = await self.learning_adapter.apply_teacher_personalization(
                    raw_result["content"], context
                )
            else:
                personalized_content = await self.learning_adapter.apply_assistant_personalization(
                    raw_result["content"], context
                )
            
            return {
                **raw_result,
                "content": personalized_content,
                "personalized": True
            }
            
        except Exception as e:
            logger.error(f"个性化处理失败: {e}")
            return raw_result
    
    async def _learn_from_interaction(self, 
                                    query: str, 
                                    result: QueryResult, 
                                    context: QueryContext):
        """从交互中学习"""
        if not self.learning_adapter:
            return
        
        try:
            interaction_data = {
                "query": query,
                "result": result,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.learning_adapter.learn_from_interaction(interaction_data)
            
        except Exception as e:
            logger.error(f"学习处理失败: {e}")
    
    def _format_memory_results(self, results: List[Dict[str, Any]]) -> str:
        """格式化记忆查询结果"""
        if not results:
            return "没有找到相关信息。"
        
        formatted_parts = []
        for i, result in enumerate(results[:3], 1):  # 只显示前3个结果
            content = result.get("content", "")[:200]  # 限制长度
            formatted_parts.append(f"{i}. {content}...")
        
        return "\n\n".join(formatted_parts)
    
    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """计算置信度"""
        if not results:
            return 0.0
        
        # 简单的置信度计算：基于结果数量和相似度
        base_confidence = min(len(results) * 0.2, 1.0)
        
        # 如果有相似度分数，使用平均值
        similarities = [r.get("similarity", 0.5) for r in results]
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.5
        
        return min(base_confidence * avg_similarity, 1.0)
    
    def _update_stats(self, provider: ServiceProvider, processing_time: float, success: bool):
        """更新统计信息"""
        if success:
            self.stats["successful_queries"] += 1
        else:
            self.stats["failed_queries"] += 1
        
        # 更新平均响应时间
        total_queries = self.stats["successful_queries"] + self.stats["failed_queries"]
        self.stats["avg_response_time"] = (
            (self.stats["avg_response_time"] * (total_queries - 1) + processing_time) / total_queries
        )
        
        # 更新提供者使用统计
        provider_key = provider.value
        self.stats["provider_usage"][provider_key] = self.stats["provider_usage"].get(provider_key, 0) + 1
    
    async def add_document(self, 
                          doc_id: str, 
                          content: str, 
                          metadata: Dict[str, Any] = None,
                          provider: ServiceProvider = ServiceProvider.HYBRID) -> bool:
        """添加文档到系统"""
        try:
            success_count = 0
            
            if provider in [ServiceProvider.MEMORY_OS, ServiceProvider.HYBRID]:
                if self.memory_engine:
                    success = await self.memory_engine.add_document_to_rag(doc_id, content, metadata)
                    if success:
                        success_count += 1
            
            if provider in [ServiceProvider.AWS_BEDROCK, ServiceProvider.HYBRID]:
                if self.rag_service:
                    await self.rag_service.add_document(doc_id, content, metadata or {})
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "initialized": self.is_initialized,
            "service_status": self.service_status,
            "statistics": self.stats,
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            checks = {}
            
            # 检查 MemoryEngine
            if self.memory_engine:
                checks["memory_engine"] = await self.memory_engine.get_rag_statistics()
            
            # 检查 AWS Bedrock 组件
            if self.integration_manager:
                checks["integration_manager"] = await self.integration_manager.get_system_status()
            
            # 检查 LearningAdapter
            if self.learning_adapter:
                checks["learning_adapter"] = {"status": "healthy"}
            
            overall_health = all(
                check.get("status") != "unhealthy" 
                for check in checks.values() 
                if isinstance(check, dict)
            )
            
            return {
                "status": "healthy" if overall_health else "degraded",
                "checks": checks,
                "service_status": self.service_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 全局实例
_unified_interface = None

async def get_unified_interface(config: Dict[str, Any] = None) -> UnifiedMemoryRAGInterface:
    """获取统一接口的单例实例"""
    global _unified_interface
    
    if _unified_interface is None:
        _unified_interface = UnifiedMemoryRAGInterface(config)
        await _unified_interface.initialize()
    
    return _unified_interface

# 便捷函数
async def unified_query(query: str, context: QueryContext, top_k: int = 5) -> QueryResult:
    """便捷的统一查询函数"""
    interface = await get_unified_interface()
    return await interface.query(query, context, top_k)

async def unified_add_document(doc_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
    """便捷的文档添加函数"""
    interface = await get_unified_interface()
    return await interface.add_document(doc_id, content, metadata)

async def unified_health_check() -> Dict[str, Any]:
    """便捷的健康检查函数"""
    interface = await get_unified_interface()
    return await interface.health_check()

