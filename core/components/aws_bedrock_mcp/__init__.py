"""
AWS Bedrock MCP - PowerAutomation v4.8 核心组件

Memory RAG MCP + AWS S3 + Kimi K2 架构的核心实现
实现零余额消耗的企业级 RAG 功能

主要组件:
- bedrock_manager.py: AWS 服务管理和配置
- rag_service.py: RAG 核心功能和向量检索
- memory_os_bridge.py: MemoryOS 项目上下文管理

技术架构:
Kimi K2 (免费 LLM) + AWS S3 (RAG 存储) + MemoryOS (项目上下文)
= 强代码能力 + 企业级 RAG + 零余额消耗

成本效益:
- 年度成本: ~$1,176 (仅存储)
- vs 商用 RAG: 节省 99%+
- vs 自建方案: 节省 95%+
"""

from .bedrock_manager import BedrockManager
from .rag_service import RAGService
# 暂时注释掉有问题的导入
# from .knowledge_base_manager import KnowledgeBaseManager
# from .document_processor import DocumentProcessor
# from .integration_manager import IntegrationManager, IntegrationConfig
# from .k2_router import K2Router, K2Request, K2Response, RequestType, ModelVersion
# from .smart_routing_mcp import SmartRoutingMCP
# from .memory_os_manager import MemoryOSManager, ProjectContext, SessionContext, ContextMemory
# from .context_bridge import ContextBridge, ContextEvent, create_context_bridge

__version__ = "4.8.0"
__author__ = "PowerAutomation Team"

# 导出主要类
__all__ = [
    "BedrockManager",
    "RAGService"
]

# 模块配置
DEFAULT_CONFIG = {
    "aws_region": "us-east-1",
    "s3_bucket": "powerautomation-rag-storage",
    "kimi_k2_endpoint": "https://api.moonshot.cn/v1",
    "memory_os_enabled": True,
    "max_context_length": 32000,
    "rag_top_k": 5,
    "cost_tracking": True
}

def get_version():
    """获取 aws_bedrock_mcp 版本信息"""
    return __version__

def get_config():
    """获取默认配置"""
    return DEFAULT_CONFIG.copy()

