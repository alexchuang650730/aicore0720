"""
Smart Routing MCP Server - PowerAutomation v4.8

智能路由 MCP 服务器，作为 PowerAutomation 架构中的核心路由组件，包括:
- 与 claude_router_mcp 的无缝集成
- 统一的 MCP 协议接口
- 智能请求分发和负载均衡
- 多模型协调（Kimi K2 + 本地模型）
- 边缘-云端协作架构

设计原则:
- 遵循 PowerAutomation MCP 架构规范
- 与现有 MCP 组件无缝集成
- 支持热插拔和动态配置
- 提供统一的 CLI 接口
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import sys
import os

# MCP 协议相关
from mcp.server import Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
    ListToolsRequest, ListToolsResult, ReadResourceRequest, ReadResourceResult
)

# 导入本地组件
from .integration_manager import IntegrationManager, IntegrationConfig
from .k2_router import K2Router, K2Request, K2Response, RequestType, ModelVersion

@dataclass
class RoutingConfig:
    """路由配置"""
    enable_local_model: bool = False
    local_model_endpoint: str = "http://localhost:11434"
    enable_edge_cloud_collaboration: bool = True
    fallback_strategy: str = "cloud_first"  # cloud_first, local_first, hybrid
    load_balancing: str = "round_robin"  # round_robin, least_latency, quality_based
    enable_caching: bool = True
    cache_ttl_seconds: int = 300

class SmartRoutingMCP:
    """智能路由 MCP 服务器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化智能路由 MCP
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 初始化 MCP 服务器
        self.server = Server("smart-routing-mcp")
        
        # 初始化组件
        self.integration_manager = None
        self.k2_router = None
        
        # 路由配置
        self.routing_config = RoutingConfig(**self.config.get("routing", {}))
        
        # 状态管理
        self.is_initialized = False
        self.active_sessions = {}
        
        # 日志
        self.logger = logging.getLogger(__name__)
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "model_distribution": {},
            "last_request_time": None
        }
        
        # 注册 MCP 处理器
        self._register_handlers()
    
    def _register_handlers(self):
        """注册 MCP 处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """列出可用工具"""
            return [
                Tool(
                    name="smart_query",
                    description="智能查询，自动选择最佳模型和策略",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "用户查询内容"
                            },
                            "context": {
                                "type": "string",
                                "description": "上下文信息（可选）"
                            },
                            "kb_id": {
                                "type": "string",
                                "description": "知识库 ID（可选）"
                            },
                            "model_preference": {
                                "type": "string",
                                "enum": ["auto", "kimi_k2", "local", "hybrid"],
                                "description": "模型偏好（可选）"
                            },
                            "priority": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 10,
                                "description": "请求优先级（可选）"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="add_knowledge",
                    description="添加知识到知识库",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "文档目录路径"
                            },
                            "kb_name": {
                                "type": "string",
                                "description": "知识库名称（可选）"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "是否递归处理子目录"
                            }
                        },
                        "required": ["directory_path"]
                    }
                ),
                Tool(
                    name="get_system_status",
                    description="获取系统状态和统计信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_details": {
                                "type": "boolean",
                                "description": "是否包含详细信息"
                            }
                        }
                    }
                ),
                Tool(
                    name="configure_routing",
                    description="配置路由策略",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "enable_local_model": {
                                "type": "boolean",
                                "description": "是否启用本地模型"
                            },
                            "fallback_strategy": {
                                "type": "string",
                                "enum": ["cloud_first", "local_first", "hybrid"],
                                "description": "回退策略"
                            },
                            "load_balancing": {
                                "type": "string",
                                "enum": ["round_robin", "least_latency", "quality_based"],
                                "description": "负载均衡策略"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """调用工具"""
            try:
                if not self.is_initialized:
                    await self.initialize()
                
                if name == "smart_query":
                    return await self._handle_smart_query(arguments)
                elif name == "add_knowledge":
                    return await self._handle_add_knowledge(arguments)
                elif name == "get_system_status":
                    return await self._handle_get_system_status(arguments)
                elif name == "configure_routing":
                    return await self._handle_configure_routing(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"未知工具: {name}"
                        )],
                        isError=True
                    )
                    
            except Exception as e:
                self.logger.error(f"工具调用失败 {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"工具调用失败: {str(e)}"
                    )],
                    isError=True
                )
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """列出可用资源"""
            return [
                Resource(
                    uri="smart-routing://stats",
                    name="系统统计",
                    description="智能路由系统的统计信息",
                    mimeType="application/json"
                ),
                Resource(
                    uri="smart-routing://config",
                    name="路由配置",
                    description="当前的路由配置信息",
                    mimeType="application/json"
                ),
                Resource(
                    uri="smart-routing://health",
                    name="健康状态",
                    description="系统健康状态检查",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            """读取资源"""
            try:
                if not self.is_initialized:
                    await self.initialize()
                
                if uri == "smart-routing://stats":
                    stats = await self._get_comprehensive_stats()
                    return ReadResourceResult(
                        contents=[TextContent(
                            type="text",
                            text=json.dumps(stats, ensure_ascii=False, indent=2)
                        )]
                    )
                elif uri == "smart-routing://config":
                    config_data = asdict(self.routing_config)
                    return ReadResourceResult(
                        contents=[TextContent(
                            type="text",
                            text=json.dumps(config_data, ensure_ascii=False, indent=2)
                        )]
                    )
                elif uri == "smart-routing://health":
                    health = await self.integration_manager.get_health_status()
                    return ReadResourceResult(
                        contents=[TextContent(
                            type="text",
                            text=json.dumps(health, ensure_ascii=False, indent=2)
                        )]
                    )
                else:
                    return ReadResourceResult(
                        contents=[TextContent(
                            type="text",
                            text=f"未知资源: {uri}"
                        )],
                        isError=True
                    )
                    
            except Exception as e:
                return ReadResourceResult(
                    contents=[TextContent(
                        type="text",
                        text=f"资源读取失败: {str(e)}"
                    )],
                    isError=True
                )
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化智能路由 MCP"""
        try:
            if self.is_initialized:
                return {"status": "already_initialized"}
            
            self.logger.info("初始化智能路由 MCP...")
            
            # 1. 初始化集成管理器
            integration_config = IntegrationConfig(**self.config.get("integration", {}))
            self.integration_manager = IntegrationManager(integration_config)
            integration_result = await self.integration_manager.initialize()
            
            if integration_result["status"] != "success":
                raise Exception(f"集成管理器初始化失败: {integration_result.get('error')}")
            
            # 2. 初始化 K2 路由器
            k2_config = self.config.get("k2_router", {})
            self.k2_router = K2Router(k2_config)
            k2_result = await self.k2_router.initialize()
            
            if k2_result["status"] != "success":
                raise Exception(f"K2 路由器初始化失败: {k2_result.get('error')}")
            
            # 3. 如果启用本地模型，初始化本地模型连接
            if self.routing_config.enable_local_model:
                await self._initialize_local_model()
            
            self.is_initialized = True
            
            result = {
                "status": "success",
                "message": "智能路由 MCP 初始化完成",
                "components": {
                    "integration_manager": integration_result,
                    "k2_router": k2_result,
                    "local_model": self.routing_config.enable_local_model
                },
                "routing_config": asdict(self.routing_config),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("智能路由 MCP 初始化完成")
            return result
            
        except Exception as e:
            self.logger.error(f"智能路由 MCP 初始化失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_smart_query(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理智能查询"""
        try:
            query = arguments["query"]
            context = arguments.get("context", "")
            kb_id = arguments.get("kb_id")
            model_preference = arguments.get("model_preference", "auto")
            priority = arguments.get("priority", 5)
            
            # 执行智能路由查询
            if model_preference == "auto":
                # 自动选择最佳策略
                result = await self._auto_route_query(query, context, kb_id, priority)
            elif model_preference == "kimi_k2":
                # 强制使用 Kimi K2
                result = await self._route_to_k2(query, context, kb_id)
            elif model_preference == "local":
                # 强制使用本地模型
                result = await self._route_to_local(query, context, kb_id)
            elif model_preference == "hybrid":
                # 混合策略
                result = await self._hybrid_route(query, context, kb_id)
            else:
                raise ValueError(f"未知的模型偏好: {model_preference}")
            
            # 更新统计
            self.stats["total_requests"] += 1
            if result["status"] == "success":
                self.stats["successful_requests"] += 1
            else:
                self.stats["failed_requests"] += 1
            
            self.stats["last_request_time"] = datetime.now()
            
            # 返回结果
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )]
            )
            
        except Exception as e:
            self.logger.error(f"智能查询处理失败: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"查询处理失败: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_add_knowledge(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理添加知识"""
        try:
            directory_path = arguments["directory_path"]
            kb_name = arguments.get("kb_name")
            recursive = arguments.get("recursive", True)
            
            # 调用集成管理器添加文档
            result = await self.integration_manager.add_documents_from_directory(
                directory_path=directory_path,
                kb_name=kb_name
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )]
            )
            
        except Exception as e:
            self.logger.error(f"添加知识处理失败: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"添加知识失败: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_get_system_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理获取系统状态"""
        try:
            include_details = arguments.get("include_details", False)
            
            status = {
                "smart_routing_mcp": {
                    "initialized": self.is_initialized,
                    "stats": self.stats.copy(),
                    "routing_config": asdict(self.routing_config)
                }
            }
            
            if include_details and self.is_initialized:
                # 获取详细状态
                health = await self.integration_manager.get_health_status()
                k2_stats = await self.k2_router.get_stats()
                
                status["integration_manager"] = health
                status["k2_router"] = k2_stats
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(status, ensure_ascii=False, indent=2)
                )]
            )
            
        except Exception as e:
            self.logger.error(f"获取系统状态失败: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"获取状态失败: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_configure_routing(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理配置路由"""
        try:
            # 更新路由配置
            if "enable_local_model" in arguments:
                self.routing_config.enable_local_model = arguments["enable_local_model"]
            
            if "fallback_strategy" in arguments:
                self.routing_config.fallback_strategy = arguments["fallback_strategy"]
            
            if "load_balancing" in arguments:
                self.routing_config.load_balancing = arguments["load_balancing"]
            
            result = {
                "status": "success",
                "message": "路由配置已更新",
                "new_config": asdict(self.routing_config),
                "timestamp": datetime.now().isoformat()
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )]
            )
            
        except Exception as e:
            self.logger.error(f"配置路由失败: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"配置失败: {str(e)}"
                )],
                isError=True
            )
    
    async def _auto_route_query(self, query: str, context: str, kb_id: str, priority: int) -> Dict[str, Any]:
        """自动路由查询"""
        try:
            # 分析查询特征
            query_analysis = await self._analyze_query(query)
            
            # 根据分析结果选择路由策略
            if query_analysis["complexity"] == "high" and self.routing_config.enable_local_model:
                # 高复杂度查询，优先使用本地模型
                return await self._route_to_local(query, context, kb_id)
            elif query_analysis["type"] in ["code_generation", "debugging"]:
                # 代码相关查询，使用 Kimi K2
                return await self._route_to_k2(query, context, kb_id)
            else:
                # 默认使用集成管理器的智能查询
                return await self._route_to_integration_manager(query, context, kb_id)
                
        except Exception as e:
            self.logger.error(f"自动路由失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "fallback": "integration_manager"
            }
    
    async def _route_to_k2(self, query: str, context: str, kb_id: str) -> Dict[str, Any]:
        """路由到 Kimi K2"""
        try:
            # 构建 K2 请求
            k2_request = K2Request(
                query=query,
                context=context,
                model_version=ModelVersion.MOONSHOT_V1_32K,
                request_type=RequestType.GENERAL_CHAT
            )
            
            # 执行 K2 路由
            response = await self.k2_router.route_request(k2_request)
            
            # 更新模型分布统计
            self.stats["model_distribution"]["kimi_k2"] = \
                self.stats["model_distribution"].get("kimi_k2", 0) + 1
            
            return {
                "status": response.status,
                "answer": response.content,
                "model_used": "kimi_k2",
                "response_time_ms": response.response_time_ms,
                "quality_score": response.quality_score,
                "metadata": response.metadata
            }
            
        except Exception as e:
            self.logger.error(f"K2 路由失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "model_used": "kimi_k2"
            }
    
    async def _route_to_local(self, query: str, context: str, kb_id: str) -> Dict[str, Any]:
        """路由到本地模型"""
        try:
            if not self.routing_config.enable_local_model:
                raise Exception("本地模型未启用")
            
            # 这里可以集成本地模型调用
            # 例如 Qwen 3 8B 或其他本地模型
            
            # 更新模型分布统计
            self.stats["model_distribution"]["local"] = \
                self.stats["model_distribution"].get("local", 0) + 1
            
            return {
                "status": "success",
                "answer": "本地模型响应（待实现）",
                "model_used": "local",
                "response_time_ms": 0.0,
                "quality_score": 0.8,
                "metadata": {"note": "本地模型集成待完成"}
            }
            
        except Exception as e:
            self.logger.error(f"本地模型路由失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "model_used": "local"
            }
    
    async def _route_to_integration_manager(self, query: str, context: str, kb_id: str) -> Dict[str, Any]:
        """路由到集成管理器"""
        try:
            # 使用集成管理器的智能查询
            result = await self.integration_manager.query(
                query=query,
                kb_id=kb_id
            )
            
            # 更新模型分布统计
            self.stats["model_distribution"]["integration_manager"] = \
                self.stats["model_distribution"].get("integration_manager", 0) + 1
            
            return {
                "status": result.status,
                "answer": result.answer,
                "model_used": "integration_manager",
                "response_time_ms": result.processing_time_ms,
                "quality_score": 0.9,  # 集成管理器通常质量较高
                "sources": result.sources,
                "metadata": result.metadata
            }
            
        except Exception as e:
            self.logger.error(f"集成管理器路由失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "model_used": "integration_manager"
            }
    
    async def _hybrid_route(self, query: str, context: str, kb_id: str) -> Dict[str, Any]:
        """混合路由策略"""
        try:
            # 并行调用多个模型
            tasks = []
            
            # Kimi K2
            tasks.append(self._route_to_k2(query, context, kb_id))
            
            # 集成管理器
            tasks.append(self._route_to_integration_manager(query, context, kb_id))
            
            # 如果启用本地模型
            if self.routing_config.enable_local_model:
                tasks.append(self._route_to_local(query, context, kb_id))
            
            # 等待所有结果
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 选择最佳结果
            best_result = None
            best_score = 0.0
            
            for result in results:
                if isinstance(result, dict) and result.get("status") == "success":
                    score = result.get("quality_score", 0.0)
                    if score > best_score:
                        best_score = score
                        best_result = result
            
            if best_result:
                best_result["routing_strategy"] = "hybrid"
                return best_result
            else:
                return {
                    "status": "error",
                    "error": "所有模型都失败了",
                    "routing_strategy": "hybrid"
                }
                
        except Exception as e:
            self.logger.error(f"混合路由失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "routing_strategy": "hybrid"
            }
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """分析查询特征"""
        analysis = {
            "length": len(query),
            "complexity": "low",
            "type": "general",
            "keywords": []
        }
        
        # 长度分析
        if len(query) > 500:
            analysis["complexity"] = "high"
        elif len(query) > 100:
            analysis["complexity"] = "medium"
        
        # 类型分析
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in ["代码", "函数", "class", "def", "function"]):
            analysis["type"] = "code_generation"
        elif any(keyword in query_lower for keyword in ["错误", "bug", "调试", "debug"]):
            analysis["type"] = "debugging"
        elif any(keyword in query_lower for keyword in ["解释", "说明", "explain"]):
            analysis["type"] = "explanation"
        
        return analysis
    
    async def _initialize_local_model(self):
        """初始化本地模型连接"""
        try:
            # 这里可以添加本地模型初始化逻辑
            # 例如连接到 Ollama、Qwen 等本地模型服务
            self.logger.info(f"尝试连接本地模型: {self.routing_config.local_model_endpoint}")
            
            # 测试连接（示例）
            # async with aiohttp.ClientSession() as session:
            #     async with session.get(f"{self.routing_config.local_model_endpoint}/api/tags") as response:
            #         if response.status == 200:
            #             self.logger.info("本地模型连接成功")
            #         else:
            #             self.logger.warning("本地模型连接失败")
            
        except Exception as e:
            self.logger.error(f"本地模型初始化失败: {str(e)}")
    
    async def _get_comprehensive_stats(self) -> Dict[str, Any]:
        """获取综合统计信息"""
        stats = {
            "smart_routing_mcp": self.stats.copy(),
            "timestamp": datetime.now().isoformat()
        }
        
        if self.is_initialized:
            try:
                # 获取各组件统计
                if self.integration_manager:
                    integration_stats = await self.integration_manager.get_health_status()
                    stats["integration_manager"] = integration_stats
                
                if self.k2_router:
                    k2_stats = await self.k2_router.get_stats()
                    stats["k2_router"] = k2_stats
                    
            except Exception as e:
                stats["stats_error"] = str(e)
        
        return stats
    
    async def run_server(self, transport_type: str = "stdio"):
        """运行 MCP 服务器"""
        try:
            self.logger.info(f"启动智能路由 MCP 服务器 (transport: {transport_type})")
            
            if transport_type == "stdio":
                from mcp.server.stdio import stdio_server
                async with stdio_server() as (read_stream, write_stream):
                    await self.server.run(
                        read_stream,
                        write_stream,
                        self.server.create_initialization_options()
                    )
            else:
                raise ValueError(f"不支持的传输类型: {transport_type}")
                
        except Exception as e:
            self.logger.error(f"MCP 服务器运行失败: {str(e)}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.k2_router:
                await self.k2_router.cleanup()
            
            self.logger.info("智能路由 MCP 资源已清理")
            
        except Exception as e:
            self.logger.error(f"资源清理失败: {str(e)}")

# CLI 入口点
async def main():
    """CLI 主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerAutomation 智能路由 MCP 服务器")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--transport", type=str, default="stdio", choices=["stdio"], help="传输类型")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别")
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 加载配置
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 创建并运行服务器
    smart_routing = SmartRoutingMCP(config)
    
    try:
        await smart_routing.run_server(args.transport)
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
    finally:
        await smart_routing.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

