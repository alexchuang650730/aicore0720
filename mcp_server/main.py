#!/usr/bin/env python3
"""
PowerAutomation MCP服务器
提供标准MCP协议支持，集成Memory RAG、K2模型、代码分析等功能
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# 导入我们的核心组件
from tools.memory_rag_tool import MemoryRAGTool
from tools.k2_chat_tool import K2ChatTool
from tools.code_analysis_tool import CodeAnalysisTool
from tools.ui_generation_tool import UIGenerationTool
from tools.workflow_automation_tool import WorkflowAutomationTool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PowerAutomationMCPServer:
    """PowerAutomation MCP服务器主类"""
    
    def __init__(self):
        self.server = Server("powerautomation-mcp")
        self.tools = {}
        self._initialize_tools()
        self._register_handlers()
    
    def _initialize_tools(self):
        """初始化所有工具"""
        try:
            # 初始化核心工具
            self.tools['memory_rag'] = MemoryRAGTool()
            self.tools['k2_chat'] = K2ChatTool()
            self.tools['code_analysis'] = CodeAnalysisTool()
            self.tools['ui_generation'] = UIGenerationTool()
            self.tools['workflow_automation'] = WorkflowAutomationTool()
            
            logger.info("✅ 所有MCP工具初始化完成")
        except Exception as e:
            logger.error(f"❌ 工具初始化失败: {e}")
            raise
    
    def _register_handlers(self):
        """注册MCP协议处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """列出所有可用工具"""
            tools = []
            
            # Memory RAG工具
            tools.append(Tool(
                name="memory_rag_query",
                description="从记忆库中检索相关信息，支持RAG检索",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "查询内容"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "返回结果数量",
                            "default": 5
                        },
                        "memory_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "记忆类型筛选"
                        }
                    },
                    "required": ["query"]
                }
            ))
            
            tools.append(Tool(
                name="memory_rag_store",
                description="存储信息到记忆库",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "要存储的内容"
                        },
                        "memory_type": {
                            "type": "string",
                            "description": "记忆类型",
                            "enum": ["episodic", "semantic", "procedural", "working", "claude_interaction"]
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签"
                        },
                        "importance": {
                            "type": "number",
                            "description": "重要性评分",
                            "minimum": 0,
                            "maximum": 1
                        }
                    },
                    "required": ["content", "memory_type"]
                }
            ))
            
            # K2聊天工具
            tools.append(Tool(
                name="k2_chat",
                description="使用Kimi K2模型进行对话",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "对话消息"
                        },
                        "context": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "上下文信息"
                        },
                        "use_memory": {
                            "type": "boolean",
                            "description": "是否使用记忆增强",
                            "default": True
                        }
                    },
                    "required": ["message"]
                }
            ))
            
            # 代码分析工具
            tools.append(Tool(
                name="code_analysis",
                description="分析代码结构、质量和潜在问题",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "要分析的代码"
                        },
                        "language": {
                            "type": "string",
                            "description": "编程语言",
                            "enum": ["python", "javascript", "typescript", "java", "cpp", "go", "rust"]
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "分析类型",
                            "enum": ["quality", "security", "performance", "structure", "all"],
                            "default": "all"
                        }
                    },
                    "required": ["code", "language"]
                }
            ))
            
            # UI生成工具
            tools.append(Tool(
                name="ui_generation",
                description="智能生成UI组件和界面",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "UI需求描述"
                        },
                        "framework": {
                            "type": "string",
                            "description": "UI框架",
                            "enum": ["react", "vue", "angular", "svelte", "html"],
                            "default": "react"
                        },
                        "style": {
                            "type": "string",
                            "description": "样式风格",
                            "enum": ["modern", "classic", "minimal", "material", "tailwind"],
                            "default": "modern"
                        },
                        "responsive": {
                            "type": "boolean",
                            "description": "是否响应式设计",
                            "default": True
                        }
                    },
                    "required": ["description"]
                }
            ))
            
            # 工作流自动化工具
            tools.append(Tool(
                name="workflow_automation",
                description="执行工作流自动化任务",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_type": {
                            "type": "string",
                            "description": "工作流类型",
                            "enum": ["code_generation", "testing", "deployment", "documentation", "analysis"]
                        },
                        "parameters": {
                            "type": "object",
                            "description": "工作流参数"
                        },
                        "async_execution": {
                            "type": "boolean",
                            "description": "是否异步执行",
                            "default": False
                        }
                    },
                    "required": ["workflow_type"]
                }
            ))
            
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """调用工具"""
            try:
                logger.info(f"📞 调用工具: {name}")
                
                if name == "memory_rag_query":
                    result = await self.tools['memory_rag'].query(
                        query=arguments["query"],
                        top_k=arguments.get("top_k", 5),
                        memory_types=arguments.get("memory_types")
                    )
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
                
                elif name == "memory_rag_store":
                    result = await self.tools['memory_rag'].store(
                        content=arguments["content"],
                        memory_type=arguments["memory_type"],
                        tags=arguments.get("tags", []),
                        importance=arguments.get("importance", 0.5)
                    )
                    return [TextContent(type="text", text=f"✅ 记忆存储成功，ID: {result}")]
                
                elif name == "k2_chat":
                    result = await self.tools['k2_chat'].chat(
                        message=arguments["message"],
                        context=arguments.get("context", []),
                        use_memory=arguments.get("use_memory", True)
                    )
                    return [TextContent(type="text", text=result)]
                
                elif name == "code_analysis":
                    result = await self.tools['code_analysis'].analyze(
                        code=arguments["code"],
                        language=arguments["language"],
                        analysis_type=arguments.get("analysis_type", "all")
                    )
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
                
                elif name == "ui_generation":
                    result = await self.tools['ui_generation'].generate(
                        description=arguments["description"],
                        framework=arguments.get("framework", "react"),
                        style=arguments.get("style", "modern"),
                        responsive=arguments.get("responsive", True)
                    )
                    return [TextContent(type="text", text=result)]
                
                elif name == "workflow_automation":
                    result = await self.tools['workflow_automation'].execute(
                        workflow_type=arguments["workflow_type"],
                        parameters=arguments.get("parameters", {}),
                        async_execution=arguments.get("async_execution", False)
                    )
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
                
                else:
                    raise ValueError(f"未知工具: {name}")
                    
            except Exception as e:
                logger.error(f"❌ 工具调用失败: {e}")
                return [TextContent(type="text", text=f"❌ 工具调用失败: {str(e)}")]
    
    async def run(self):
        """运行MCP服务器"""
        logger.info("🚀 PowerAutomation MCP服务器启动中...")
        
        # 使用标准输入输出运行MCP服务器
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="powerautomation-mcp",
                    server_version="1.0.0",
                    capabilities={
                        "tools": {},
                        "logging": {}
                    }
                )
            )

async def main():
    """主函数"""
    server = PowerAutomationMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())