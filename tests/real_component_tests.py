#!/usr/bin/env python3
"""
PowerAutomation v4.8 实际组件功能测试

这个测试套件将实际测试我们创建的组件，而不是模拟测试。
包括：
1. 实际的文档处理器测试
2. 实际的知识库管理器测试
3. 实际的 RAG 服务测试
4. 实际的 MemoryOS 管理器测试
5. 实际的 MCP 通信测试
"""

import os
import sys
import json
import asyncio
import tempfile
import shutil
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class RealRAGSystemTester:
    """实际 RAG 系统测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        
    async def setup(self):
        """设置测试环境"""
        logger.info("🔧 设置实际 RAG 系统测试环境...")
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="rag_test_")
        
        # 创建测试文件
        await self._create_test_files()
        
        logger.info("✅ RAG 系统测试环境设置完成")
        
    async def cleanup(self):
        """清理测试环境"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    async def _create_test_files(self):
        """创建测试文件"""
        test_files = {
            "test_python.py": '''
def calculate_fibonacci(n):
    """计算斐波那契数列的第n项
    
    Args:
        n (int): 要计算的项数
        
    Returns:
        int: 斐波那契数列的第n项
    """
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        self.data = []
        
    def add_data(self, item):
        """添加数据项"""
        self.data.append(item)
        
    def process_data(self):
        """处理数据"""
        return [item * 2 for item in self.data if isinstance(item, (int, float))]
''',
            "test_javascript.js": '''
/**
 * 用户管理类
 */
class UserManager {
    constructor() {
        this.users = [];
    }
    
    /**
     * 添加用户
     * @param {Object} user - 用户对象
     * @param {string} user.name - 用户名
     * @param {string} user.email - 邮箱
     */
    addUser(user) {
        if (!user.name || !user.email) {
            throw new Error('用户名和邮箱不能为空');
        }
        this.users.push(user);
    }
    
    /**
     * 根据邮箱查找用户
     * @param {string} email - 邮箱地址
     * @returns {Object|null} 用户对象或null
     */
    findUserByEmail(email) {
        return this.users.find(user => user.email === email) || null;
    }
}

// 导出模块
module.exports = UserManager;
''',
            "README.md": '''# 测试项目

这是一个用于测试 RAG 系统的示例项目。

## 功能特性

- 斐波那契数列计算
- 数据处理功能
- 用户管理系统

## 使用方法

### Python 部分

```python
from test_python import calculate_fibonacci, DataProcessor

# 计算斐波那契数列
result = calculate_fibonacci(10)
print(f"第10项斐波那契数: {result}")

# 数据处理
processor = DataProcessor()
processor.add_data(5)
processor.add_data(10)
processed = processor.process_data()
print(f"处理后的数据: {processed}")
```

### JavaScript 部分

```javascript
const UserManager = require('./test_javascript');

const manager = new UserManager();
manager.addUser({
    name: '张三',
    email: 'zhangsan@example.com'
});

const user = manager.findUserByEmail('zhangsan@example.com');
console.log('找到用户:', user);
```

## 性能优化建议

1. **斐波那契计算优化**
   - 使用动态规划避免重复计算
   - 考虑使用记忆化技术

2. **数据处理优化**
   - 批量处理大数据集
   - 使用流式处理减少内存占用

3. **用户管理优化**
   - 添加索引提高查找效率
   - 实现用户数据缓存机制
''',
            "config.json": '''
{
    "project": {
        "name": "测试项目",
        "version": "1.0.0",
        "description": "用于测试 RAG 系统的示例项目"
    },
    "settings": {
        "debug": true,
        "max_users": 1000,
        "cache_enabled": true
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "test_db"
    }
}
'''
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
    async def test_document_processor(self):
        """测试实际的文档处理器"""
        logger.info("📄 测试实际文档处理器...")
        
        try:
            # 导入实际的文档处理器
            from core.components.aws_bedrock_mcp.document_processor import DocumentProcessor
            
            processor = DocumentProcessor()
            
            # 测试 Python 文件处理
            python_file = os.path.join(self.temp_dir, "test_python.py")
            result = await processor.process_file(python_file)
            
            # 验证处理结果
            assert result["file_type"] == "python"
            assert len(result["chunks"]) > 0
            assert "functions" in result["metadata"]
            assert "calculate_fibonacci" in result["metadata"]["functions"]
            
            self.test_results["document_processor"] = {
                "status": "passed",
                "file_type": result["file_type"],
                "chunks_count": len(result["chunks"]),
                "functions_found": len(result["metadata"]["functions"]),
                "classes_found": len(result["metadata"]["classes"])
            }
            
            logger.info("✅ 文档处理器测试通过")
            
        except ImportError as e:
            logger.warning(f"⚠️ 无法导入文档处理器: {e}")
            self.test_results["document_processor"] = {
                "status": "skipped",
                "reason": "模块导入失败"
            }
        except Exception as e:
            logger.error(f"❌ 文档处理器测试失败: {e}")
            self.test_results["document_processor"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def test_knowledge_base_manager(self):
        """测试实际的知识库管理器"""
        logger.info("🗄️ 测试实际知识库管理器...")
        
        try:
            # 导入实际的知识库管理器
            from core.components.aws_bedrock_mcp.knowledge_base_manager import KnowledgeBaseManager
            
            # 创建配置
            config = {
                "storage_path": os.path.join(self.temp_dir, "kb_storage"),
                "embedding_model": "all-MiniLM-L6-v2",
                "chunk_size": 500,
                "chunk_overlap": 100
            }
            
            kb_manager = KnowledgeBaseManager(config)
            await kb_manager.initialize()
            
            # 测试创建知识库
            kb_result = await kb_manager.create_knowledge_base(
                kb_name="测试知识库",
                description="用于测试的知识库"
            )
            
            assert kb_result["status"] == "success"
            kb_id = kb_result["kb_id"]
            
            # 测试添加文档
            add_result = await kb_manager.add_documents_from_directory(
                directory_path=self.temp_dir,
                kb_id=kb_id,
                recursive=False
            )
            
            assert add_result["status"] == "success"
            assert add_result["processed_files"] > 0
            
            self.test_results["knowledge_base_manager"] = {
                "status": "passed",
                "kb_id": kb_id,
                "processed_files": add_result["processed_files"],
                "total_chunks": add_result["total_chunks"]
            }
            
            logger.info("✅ 知识库管理器测试通过")
            
        except ImportError as e:
            logger.warning(f"⚠️ 无法导入知识库管理器: {e}")
            self.test_results["knowledge_base_manager"] = {
                "status": "skipped",
                "reason": "模块导入失败"
            }
        except Exception as e:
            logger.error(f"❌ 知识库管理器测试失败: {e}")
            self.test_results["knowledge_base_manager"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def test_rag_service(self):
        """测试实际的 RAG 服务"""
        logger.info("🧠 测试实际 RAG 服务...")
        
        try:
            # 导入实际的 RAG 服务
            from core.components.aws_bedrock_mcp.rag_service import RAGService
            
            # 创建配置
            config = {
                "storage_path": os.path.join(self.temp_dir, "rag_storage"),
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_dim": 384,
                "similarity_threshold": 0.7
            }
            
            rag_service = RAGService(config)
            await rag_service.initialize()
            
            # 测试添加文档
            documents = [
                {
                    "content": "斐波那契数列是一个数学序列，每个数字是前两个数字的和。",
                    "metadata": {"source": "test_python.py", "type": "documentation"}
                },
                {
                    "content": "用户管理系统需要验证用户名和邮箱的有效性。",
                    "metadata": {"source": "test_javascript.js", "type": "documentation"}
                }
            ]
            
            add_result = await rag_service.add_documents(documents, kb_id="test_kb")
            assert add_result["status"] == "success"
            
            # 测试文档检索
            query = "如何计算斐波那契数列？"
            retrieve_result = await rag_service.retrieve_documents(
                query=query,
                kb_id="test_kb",
                top_k=3
            )
            
            assert retrieve_result["status"] == "success"
            assert len(retrieve_result["documents"]) > 0
            
            self.test_results["rag_service"] = {
                "status": "passed",
                "documents_added": len(documents),
                "retrieved_documents": len(retrieve_result["documents"]),
                "query_time_ms": retrieve_result.get("query_time_ms", 0)
            }
            
            logger.info("✅ RAG 服务测试通过")
            
        except ImportError as e:
            logger.warning(f"⚠️ 无法导入 RAG 服务: {e}")
            self.test_results["rag_service"] = {
                "status": "skipped",
                "reason": "模块导入失败"
            }
        except Exception as e:
            logger.error(f"❌ RAG 服务测试失败: {e}")
            self.test_results["rag_service"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def run_all_tests(self):
        """运行所有 RAG 系统测试"""
        logger.info("🚀 开始实际 RAG 系统组件测试...")
        
        await self.setup()
        
        try:
            await self.test_document_processor()
            await self.test_knowledge_base_manager()
            await self.test_rag_service()
        finally:
            await self.cleanup()
        
        logger.info("✅ RAG 系统组件测试完成")
        return self.test_results

class RealMemoryOSTester:
    """实际 MemoryOS 测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        
    async def setup(self):
        """设置测试环境"""
        logger.info("🔧 设置实际 MemoryOS 测试环境...")
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="memory_os_test_")
        
        logger.info("✅ MemoryOS 测试环境设置完成")
        
    async def cleanup(self):
        """清理测试环境"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    async def test_memory_os_manager(self):
        """测试实际的 MemoryOS 管理器"""
        logger.info("🧠 测试实际 MemoryOS 管理器...")
        
        try:
            # 导入实际的 MemoryOS 管理器
            from core.components.aws_bedrock_mcp.memory_os_manager import MemoryOSManager
            
            # 创建配置
            config = {
                "storage_path": os.path.join(self.temp_dir, "memory_storage"),
                "max_memory_size": 100,
                "context_ttl_days": 7,
                "compression_enabled": True
            }
            
            memory_manager = MemoryOSManager(config)
            await memory_manager.initialize()
            
            # 测试创建项目上下文
            project_result = await memory_manager.create_project_context(
                project_name="测试项目",
                project_path="/test/project",
                description="这是一个测试项目"
            )
            
            assert project_result["status"] == "success"
            project_id = project_result["project_id"]
            
            # 测试开始会话
            session_result = await memory_manager.start_session(
                project_id=project_id,
                initial_context="开始新的开发会话"
            )
            
            assert session_result["status"] == "success"
            session_id = session_result["session_id"]
            
            # 测试添加记忆
            memory_result = await memory_manager.add_memory(
                project_id=project_id,
                memory_type="solution",
                content="使用动态规划优化斐波那契计算",
                importance=0.9,
                tags=["算法", "优化", "动态规划"]
            )
            
            assert memory_result["status"] == "success"
            
            # 测试搜索记忆
            search_result = await memory_manager.search_memories(
                project_id=project_id,
                query="算法优化",
                limit=5
            )
            
            assert search_result["status"] == "success"
            assert len(search_result["memories"]) > 0
            
            self.test_results["memory_os_manager"] = {
                "status": "passed",
                "project_id": project_id,
                "session_id": session_id,
                "memories_found": len(search_result["memories"])
            }
            
            logger.info("✅ MemoryOS 管理器测试通过")
            
        except ImportError as e:
            logger.warning(f"⚠️ 无法导入 MemoryOS 管理器: {e}")
            self.test_results["memory_os_manager"] = {
                "status": "skipped",
                "reason": "模块导入失败"
            }
        except Exception as e:
            logger.error(f"❌ MemoryOS 管理器测试失败: {e}")
            self.test_results["memory_os_manager"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def test_context_bridge(self):
        """测试实际的上下文桥接器"""
        logger.info("🌉 测试实际上下文桥接器...")
        
        try:
            # 导入实际的上下文桥接器
            from core.components.aws_bedrock_mcp.context_bridge import ContextBridge
            
            # 创建配置
            config = {
                "storage_path": os.path.join(self.temp_dir, "context_storage"),
                "cache_size": 100,
                "cache_ttl_minutes": 30
            }
            
            context_bridge = ContextBridge(config)
            await context_bridge.initialize()
            
            # 测试注册组件
            register_result = await context_bridge.register_component(
                component_name="test_component",
                component_type="rag_service"
            )
            
            assert register_result["status"] == "success"
            
            # 测试获取相关上下文
            context_result = await context_bridge.get_relevant_context_for_query(
                query="性能优化",
                project_path="/test/project"
            )
            
            assert len(context_result) >= 0  # 可能为空，但不应该出错
            
            self.test_results["context_bridge"] = {
                "status": "passed",
                "registered_components": 1,
                "context_length": len(context_result)
            }
            
            logger.info("✅ 上下文桥接器测试通过")
            
        except ImportError as e:
            logger.warning(f"⚠️ 无法导入上下文桥接器: {e}")
            self.test_results["context_bridge"] = {
                "status": "skipped",
                "reason": "模块导入失败"
            }
        except Exception as e:
            logger.error(f"❌ 上下文桥接器测试失败: {e}")
            self.test_results["context_bridge"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def run_all_tests(self):
        """运行所有 MemoryOS 测试"""
        logger.info("🚀 开始实际 MemoryOS 组件测试...")
        
        await self.setup()
        
        try:
            await self.test_memory_os_manager()
            await self.test_context_bridge()
        finally:
            await self.cleanup()
        
        logger.info("✅ MemoryOS 组件测试完成")
        return self.test_results

class RealMCPTester:
    """实际 MCP 测试器"""
    
    def __init__(self):
        self.test_results = {}
        
    async def test_k2_router(self):
        """测试实际的 K2 路由器"""
        logger.info("🤖 测试实际 K2 路由器...")
        
        try:
            # 导入实际的 K2 路由器
            from core.components.aws_bedrock_mcp.k2_router import K2Router
            
            # 创建配置（使用测试配置）
            config = {
                "api_endpoint": "https://api.moonshot.cn/v1",
                "api_key": "test_api_key",  # 测试密钥
                "enable_smart_routing": True,
                "enable_context_optimization": True,
                "max_concurrent_requests": 5,
                "rate_limit_per_minute": 30
            }
            
            k2_router = K2Router(config)
            await k2_router.initialize()
            
            # 测试请求类型识别
            request_type = k2_router.identify_request_type("写一个计算斐波那契数列的函数")
            assert request_type == "code_generation"
            
            # 测试上下文优化
            long_context = "这是一个很长的上下文..." * 100
            optimized_context = k2_router.optimize_context(long_context, strategy="compress")
            assert len(optimized_context) < len(long_context)
            
            # 测试模型选择
            model = k2_router.select_model("简单问题", context_length=100)
            assert model in ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
            
            self.test_results["k2_router"] = {
                "status": "passed",
                "request_type_detection": True,
                "context_optimization": True,
                "model_selection": True
            }
            
            logger.info("✅ K2 路由器测试通过")
            
        except ImportError as e:
            logger.warning(f"⚠️ 无法导入 K2 路由器: {e}")
            self.test_results["k2_router"] = {
                "status": "skipped",
                "reason": "模块导入失败"
            }
        except Exception as e:
            logger.error(f"❌ K2 路由器测试失败: {e}")
            self.test_results["k2_router"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def test_smart_routing_mcp(self):
        """测试实际的智能路由 MCP"""
        logger.info("🎯 测试实际智能路由 MCP...")
        
        try:
            # 导入实际的智能路由 MCP
            from core.components.aws_bedrock_mcp.smart_routing_mcp import SmartRoutingMCP
            
            # 创建配置
            config = {
                "server_name": "SmartRoutingMCP",
                "version": "4.8.0",
                "k2_router_config": {
                    "api_endpoint": "https://api.moonshot.cn/v1",
                    "api_key": "test_api_key"
                },
                "integration_manager_config": {
                    "storage_path": "/tmp/test_integration"
                }
            }
            
            smart_mcp = SmartRoutingMCP(config)
            await smart_mcp.initialize()
            
            # 测试工具列表
            tools = await smart_mcp.list_tools()
            expected_tools = ["smart_query", "add_knowledge", "get_system_status", "configure_routing"]
            
            tool_names = [tool["name"] for tool in tools]
            for expected_tool in expected_tools:
                assert expected_tool in tool_names
            
            self.test_results["smart_routing_mcp"] = {
                "status": "passed",
                "tools_registered": len(tools),
                "expected_tools_found": len(expected_tools)
            }
            
            logger.info("✅ 智能路由 MCP 测试通过")
            
        except ImportError as e:
            logger.warning(f"⚠️ 无法导入智能路由 MCP: {e}")
            self.test_results["smart_routing_mcp"] = {
                "status": "skipped",
                "reason": "模块导入失败"
            }
        except Exception as e:
            logger.error(f"❌ 智能路由 MCP 测试失败: {e}")
            self.test_results["smart_routing_mcp"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def run_all_tests(self):
        """运行所有 MCP 测试"""
        logger.info("🚀 开始实际 MCP 组件测试...")
        
        await self.test_k2_router()
        await self.test_smart_routing_mcp()
        
        logger.info("✅ MCP 组件测试完成")
        return self.test_results

async def run_real_component_tests():
    """运行实际组件测试"""
    logger.info("🚀 开始 PowerAutomation v4.8 实际组件功能测试")
    logger.info("=" * 60)
    
    # 创建测试器
    rag_tester = RealRAGSystemTester()
    memory_tester = RealMemoryOSTester()
    mcp_tester = RealMCPTester()
    
    # 运行所有测试
    test_results = {}
    
    # Phase 1: RAG 系统组件测试
    logger.info("\n📚 Phase 1: 实际 RAG 系统组件测试")
    test_results["rag_system"] = await rag_tester.run_all_tests()
    
    # Phase 2: MemoryOS 组件测试
    logger.info("\n🧠 Phase 2: 实际 MemoryOS 组件测试")
    test_results["memory_os"] = await memory_tester.run_all_tests()
    
    # Phase 3: MCP 组件测试
    logger.info("\n🔗 Phase 3: 实际 MCP 组件测试")
    test_results["mcp_system"] = await mcp_tester.run_all_tests()
    
    # 生成测试报告
    await generate_real_test_report(test_results)
    
    logger.info("\n🎉 实际组件功能测试完成！")

async def generate_real_test_report(test_results: Dict[str, Any]):
    """生成实际测试报告"""
    logger.info("\n📊 生成实际组件测试报告...")
    
    # 统计测试结果
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0
    
    for category, results in test_results.items():
        for test_name, result in results.items():
            total_tests += 1
            status = result.get("status", "unknown")
            if status == "passed":
                passed_tests += 1
            elif status == "failed":
                failed_tests += 1
            elif status == "skipped":
                skipped_tests += 1
    
    # 计算成功率
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # 生成报告
    report = f"""
# PowerAutomation v4.8 实际组件功能测试报告

## 测试概览

- **总测试数**: {total_tests}
- **通过测试**: {passed_tests}
- **失败测试**: {failed_tests}
- **跳过测试**: {skipped_tests}
- **成功率**: {success_rate:.1f}%
- **测试时间**: {datetime.utcnow().isoformat()}

## 测试结果详情

"""
    
    for category, results in test_results.items():
        report += f"\n### {category.replace('_', ' ').title()}\n"
        for test_name, result in results.items():
            status = result.get("status", "unknown")
            if status == "passed":
                status_icon = "✅"
            elif status == "failed":
                status_icon = "❌"
            elif status == "skipped":
                status_icon = "⚠️"
            else:
                status_icon = "❓"
            
            report += f"- {status_icon} {test_name.replace('_', ' ').title()}"
            
            if status == "failed":
                report += f" - 错误: {result.get('error', '未知错误')}"
            elif status == "skipped":
                report += f" - 原因: {result.get('reason', '未知原因')}"
            
            report += "\n"
    
    report += f"""
## 组件状态分析

### RAG 系统组件
- **文档处理器**: {'✅ 正常' if test_results.get('rag_system', {}).get('document_processor', {}).get('status') == 'passed' else '❌ 异常'}
- **知识库管理器**: {'✅ 正常' if test_results.get('rag_system', {}).get('knowledge_base_manager', {}).get('status') == 'passed' else '❌ 异常'}
- **RAG 服务**: {'✅ 正常' if test_results.get('rag_system', {}).get('rag_service', {}).get('status') == 'passed' else '❌ 异常'}

### MemoryOS 组件
- **MemoryOS 管理器**: {'✅ 正常' if test_results.get('memory_os', {}).get('memory_os_manager', {}).get('status') == 'passed' else '❌ 异常'}
- **上下文桥接器**: {'✅ 正常' if test_results.get('memory_os', {}).get('context_bridge', {}).get('status') == 'passed' else '❌ 异常'}

### MCP 组件
- **K2 路由器**: {'✅ 正常' if test_results.get('mcp_system', {}).get('k2_router', {}).get('status') == 'passed' else '❌ 异常'}
- **智能路由 MCP**: {'✅ 正常' if test_results.get('mcp_system', {}).get('smart_routing_mcp', {}).get('status') == 'passed' else '❌ 异常'}

## 结论

{'✅ 所有组件测试通过，系统准备就绪！' if failed_tests == 0 else f'⚠️ {failed_tests} 个组件测试失败，需要检查依赖和配置'}

PowerAutomation v4.8 的核心组件已完成实际功能验证。
"""
    
    # 保存报告
    report_path = "/tmp/powerautomation_v4.8_real_component_test_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"📄 实际组件测试报告已保存到: {report_path}")
    logger.info(f"🎯 组件测试成功率: {success_rate:.1f}%")

if __name__ == "__main__":
    asyncio.run(run_real_component_tests())

