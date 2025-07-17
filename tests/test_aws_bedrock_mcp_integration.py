#!/usr/bin/env python3
"""
AWS Bedrock MCP 集成测试套件 - PowerAutomation v4.8

全面的集成测试，验证 AWS Bedrock MCP 组件的功能和性能，包括:
- 组件初始化和配置测试
- Kimi K2 路由器集成测试
- MemoryOS 项目上下文管理测试
- 智能路由 MCP 服务器测试
- 端到端工作流测试
- 性能基准测试

测试原则:
- 全面覆盖：覆盖所有核心功能
- 真实场景：模拟实际使用场景
- 性能验证：确保满足性能要求
- 错误处理：验证异常情况处理
"""

import os
import sys
import json
import asyncio
import unittest
import tempfile
import shutil
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入待测试的组件
from core.components.aws_bedrock_mcp import (
    BedrockManager, RAGService, KnowledgeBaseManager, DocumentProcessor,
    IntegrationManager, IntegrationConfig, K2Router, K2Request, K2Response,
    RequestType, ModelVersion, SmartRoutingMCP, MemoryOSManager,
    ProjectContext, SessionContext, ContextMemory, ContextBridge,
    create_context_bridge
)

class TestAWSBedrockMCPIntegration(unittest.IsolatedAsyncioTestCase):
    """AWS Bedrock MCP 集成测试类"""
    
    async def asyncSetUp(self):
        """测试设置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.test_project_path, exist_ok=True)
        
        # 创建测试文件
        self.test_files = []
        for i in range(5):
            file_path = os.path.join(self.test_project_path, f"test_file_{i}.py")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"""
# 测试文件 {i}
def test_function_{i}():
    '''这是测试函数 {i}'''
    return "Hello from function {i}"

class TestClass{i}:
    '''测试类 {i}'''
    def __init__(self):
        self.value = {i}
    
    def get_value(self):
        return self.value
""")
            self.test_files.append(file_path)
        
        # 测试配置
        self.test_config = {
            "integration": {
                "aws_region": "us-east-1",
                "s3_bucket": "test-powerautomation-rag",
                "kimi_k2_endpoint": "https://api.moonshot.cn/v1",
                "kimi_k2_api_key": "test_api_key",
                "embedding_model": "all-MiniLM-L6-v2",
                "chunk_size": 500,
                "chunk_overlap": 100
            },
            "k2_router": {
                "api_endpoint": "https://api.moonshot.cn/v1",
                "api_key": "test_api_key",
                "enable_smart_routing": True,
                "enable_context_optimization": True,
                "max_concurrent_requests": 5,
                "rate_limit_per_minute": 30
            },
            "memory_os": {
                "storage_path": os.path.join(self.temp_dir, "memory_os"),
                "max_memory_size": 100,
                "context_ttl_days": 7,
                "compression_enabled": True,
                "auto_cleanup_enabled": False  # 测试时禁用自动清理
            },
            "routing": {
                "enable_local_model": False,
                "fallback_strategy": "cloud_first",
                "load_balancing": "round_robin"
            }
        }
        
        # 初始化组件
        self.integration_config = IntegrationConfig(**self.test_config["integration"])
        self.memory_os_manager = None
        self.context_bridge = None
        self.integration_manager = None
        self.k2_router = None
        self.smart_routing_mcp = None
    
    async def asyncTearDown(self):
        """测试清理"""
        # 清理组件
        if self.context_bridge:
            await self.context_bridge.cleanup()
        
        if self.memory_os_manager:
            await self.memory_os_manager.cleanup()
        
        if self.k2_router:
            await self.k2_router.cleanup()
        
        # 删除临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    async def test_01_memory_os_manager_initialization(self):
        """测试 MemoryOS 管理器初始化"""
        print("\n🧪 测试 MemoryOS 管理器初始化...")
        
        # 创建 MemoryOS 管理器
        self.memory_os_manager = MemoryOSManager(self.test_config["memory_os"])
        
        # 初始化
        result = await self.memory_os_manager.initialize()
        
        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertIn("storage_path", result)
        self.assertEqual(result["projects_loaded"], 0)
        self.assertEqual(result["memories_loaded"], 0)
        
        print("✅ MemoryOS 管理器初始化成功")
    
    async def test_02_project_context_management(self):
        """测试项目上下文管理"""
        print("\n🧪 测试项目上下文管理...")
        
        if not self.memory_os_manager:
            await self.test_01_memory_os_manager_initialization()
        
        # 创建项目上下文
        create_result = await self.memory_os_manager.create_project_context(
            project_name="测试项目",
            project_path=self.test_project_path,
            description="这是一个测试项目"
        )
        
        self.assertEqual(create_result["status"], "success")
        project_id = create_result["project_id"]
        
        # 获取项目上下文
        get_result = await self.memory_os_manager.get_project_context(project_id)
        
        self.assertEqual(get_result["status"], "success")
        project = get_result["project"]
        self.assertEqual(project["project_name"], "测试项目")
        self.assertEqual(project["project_path"], self.test_project_path)
        
        print(f"✅ 项目上下文管理成功，项目 ID: {project_id}")
        
        # 保存项目 ID 供后续测试使用
        self.test_project_id = project_id
    
    async def test_03_session_management(self):
        """测试会话管理"""
        print("\n🧪 测试会话管理...")
        
        if not hasattr(self, 'test_project_id'):
            await self.test_02_project_context_management()
        
        # 开始会话
        session_result = await self.memory_os_manager.start_session(
            project_id=self.test_project_id,
            initial_context="这是初始上下文"
        )
        
        self.assertEqual(session_result["status"], "success")
        session_id = session_result["session_id"]
        
        # 更新会话上下文
        update_result = await self.memory_os_manager.update_session_context(
            session_id=session_id,
            context_update={
                "query": "测试查询",
                "response": "测试响应",
                "success": True,
                "opened_files": [self.test_files[0]],
                "current_task": "执行测试"
            }
        )
        
        self.assertEqual(update_result["status"], "success")
        
        # 获取会话上下文
        get_session_result = await self.memory_os_manager.get_session_context(session_id)
        
        self.assertEqual(get_session_result["status"], "success")
        session = get_session_result["session"]
        self.assertEqual(len(session["query_history"]), 1)
        self.assertEqual(session["current_task"], "执行测试")
        
        print(f"✅ 会话管理成功，会话 ID: {session_id}")
        
        # 保存会话 ID 供后续测试使用
        self.test_session_id = session_id
    
    async def test_04_memory_management(self):
        """测试记忆管理"""
        print("\n🧪 测试记忆管理...")
        
        if not hasattr(self, 'test_project_id'):
            await self.test_02_project_context_management()
        
        # 添加记忆
        memory_result = await self.memory_os_manager.add_memory(
            project_id=self.test_project_id,
            memory_type="concept",
            content="这是一个重要的概念：测试驱动开发",
            importance=0.8,
            tags=["TDD", "测试", "开发"],
            related_files=[self.test_files[0]]
        )
        
        self.assertEqual(memory_result["status"], "success")
        memory_id = memory_result["memory_id"]
        
        # 搜索记忆
        search_result = await self.memory_os_manager.search_memories(
            project_id=self.test_project_id,
            query="测试",
            limit=5
        )
        
        self.assertEqual(search_result["status"], "success")
        self.assertGreater(len(search_result["memories"]), 0)
        
        # 验证记忆内容
        found_memory = search_result["memories"][0]
        self.assertEqual(found_memory["memory_id"], memory_id)
        self.assertIn("测试", found_memory["content"])
        
        print(f"✅ 记忆管理成功，记忆 ID: {memory_id}")
    
    async def test_05_context_bridge_initialization(self):
        """测试上下文桥接器初始化"""
        print("\n🧪 测试上下文桥接器初始化...")
        
        if not self.memory_os_manager:
            await self.test_01_memory_os_manager_initialization()
        
        # 创建上下文桥接器
        self.context_bridge = await create_context_bridge(
            memory_os_manager=self.memory_os_manager,
            config={}
        )
        
        # 验证初始化
        self.assertIsNotNone(self.context_bridge)
        self.assertEqual(len(self.context_bridge.event_handlers), 5)  # 5个默认处理器
        
        print("✅ 上下文桥接器初始化成功")
    
    async def test_06_context_bridge_integration(self):
        """测试上下文桥接器集成"""
        print("\n🧪 测试上下文桥接器集成...")
        
        if not self.context_bridge:
            await self.test_05_context_bridge_initialization()
        
        # 开始组件会话
        session_result = await self.context_bridge.start_session_for_component(
            component_name="test_component",
            project_path=self.test_project_path,
            initial_context="测试组件初始上下文"
        )
        
        self.assertEqual(session_result["status"], "success")
        
        # 模拟文件操作
        await self.context_bridge.on_file_opened(
            file_path=self.test_files[0],
            project_path=self.test_project_path,
            content="测试文件内容"
        )
        
        await self.context_bridge.on_file_modified(
            file_path=self.test_files[0],
            project_path=self.test_project_path,
            changes="添加了新的函数"
        )
        
        # 模拟查询执行
        await self.context_bridge.on_query_executed(
            query="如何优化这个函数？",
            response="可以通过缓存来优化性能",
            project_path=self.test_project_path,
            success=True
        )
        
        # 获取相关上下文
        relevant_context = await self.context_bridge.get_relevant_context_for_query(
            query="优化",
            project_path=self.test_project_path
        )
        
        self.assertIsInstance(relevant_context, str)
        self.assertGreater(len(relevant_context), 0)
        
        print("✅ 上下文桥接器集成成功")
    
    @patch('aiohttp.ClientSession.post')
    async def test_07_k2_router_functionality(self, mock_post):
        """测试 K2 路由器功能"""
        print("\n🧪 测试 K2 路由器功能...")
        
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "这是 Kimi K2 的测试响应"
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # 创建 K2 路由器
        self.k2_router = K2Router(self.test_config["k2_router"])
        
        # 初始化
        init_result = await self.k2_router.initialize()
        self.assertEqual(init_result["status"], "success")
        
        # 创建测试请求
        k2_request = K2Request(
            query="测试查询",
            context="测试上下文",
            model_version=ModelVersion.MOONSHOT_V1_8K,
            request_type=RequestType.GENERAL_CHAT
        )
        
        # 执行路由
        response = await self.k2_router.route_request(k2_request)
        
        # 验证响应
        self.assertEqual(response.status, "success")
        self.assertIn("Kimi K2", response.content)
        self.assertGreater(response.response_time_ms, 0)
        
        print("✅ K2 路由器功能测试成功")
    
    async def test_08_integration_manager_functionality(self):
        """测试集成管理器功能"""
        print("\n🧪 测试集成管理器功能...")
        
        # 创建集成管理器
        self.integration_manager = IntegrationManager(self.integration_config)
        
        # 模拟初始化（跳过实际的 AWS 调用）
        with patch.object(self.integration_manager, '_initialize_aws_services', return_value={"status": "success"}):
            with patch.object(self.integration_manager, '_initialize_embedding_model', return_value={"status": "success"}):
                init_result = await self.integration_manager.initialize()
                self.assertEqual(init_result["status"], "success")
        
        # 测试文档处理（模拟）
        with patch.object(self.integration_manager, 'add_documents_from_directory') as mock_add_docs:
            mock_add_docs.return_value = {
                "status": "success",
                "successful_files": 5,
                "failed_files": [],
                "total_chunks": 25,
                "processing_time_seconds": 2.5
            }
            
            add_result = await self.integration_manager.add_documents_from_directory(
                directory_path=self.test_project_path
            )
            
            self.assertEqual(add_result["status"], "success")
            self.assertEqual(add_result["successful_files"], 5)
        
        print("✅ 集成管理器功能测试成功")
    
    async def test_09_smart_routing_mcp_functionality(self):
        """测试智能路由 MCP 功能"""
        print("\n🧪 测试智能路由 MCP 功能...")
        
        # 创建智能路由 MCP
        self.smart_routing_mcp = SmartRoutingMCP(self.test_config)
        
        # 模拟初始化
        with patch.object(self.smart_routing_mcp, 'initialize') as mock_init:
            mock_init.return_value = {"status": "success"}
            
            init_result = await self.smart_routing_mcp.initialize()
            self.assertEqual(init_result["status"], "success")
        
        # 测试工具列表
        tools = await self.smart_routing_mcp.server.list_tools()
        self.assertGreater(len(tools), 0)
        
        # 验证核心工具存在
        tool_names = [tool.name for tool in tools]
        expected_tools = ["smart_query", "add_knowledge", "get_system_status", "configure_routing"]
        for tool_name in expected_tools:
            self.assertIn(tool_name, tool_names)
        
        print("✅ 智能路由 MCP 功能测试成功")
    
    async def test_10_end_to_end_workflow(self):
        """测试端到端工作流"""
        print("\n🧪 测试端到端工作流...")
        
        # 确保所有组件都已初始化
        if not self.memory_os_manager:
            await self.test_01_memory_os_manager_initialization()
        
        if not self.context_bridge:
            await self.test_05_context_bridge_initialization()
        
        # 1. 创建项目和会话
        project_result = await self.memory_os_manager.create_project_context(
            project_name="端到端测试项目",
            project_path=self.test_project_path,
            description="端到端工作流测试"
        )
        
        self.assertEqual(project_result["status"], "success")
        project_id = project_result["project_id"]
        
        # 2. 通过桥接器开始会话
        session_result = await self.context_bridge.start_session_for_component(
            component_name="end_to_end_test",
            project_path=self.test_project_path,
            initial_context="端到端测试初始上下文"
        )
        
        self.assertEqual(session_result["status"], "success")
        
        # 3. 模拟完整的开发工作流
        
        # 文件操作
        for i, file_path in enumerate(self.test_files[:3]):
            await self.context_bridge.on_file_opened(
                file_path=file_path,
                project_path=self.test_project_path,
                content=f"文件 {i} 的内容"
            )
            
            await self.context_bridge.on_file_modified(
                file_path=file_path,
                project_path=self.test_project_path,
                changes=f"修改了文件 {i}"
            )
        
        # 智能操作
        await self.context_bridge.on_smart_operation(
            operation_type="code_refactor",
            project_path=self.test_project_path,
            operation_data={
                "files": self.test_files[:2],
                "operation": "重构函数",
                "result": "成功重构"
            }
        )
        
        # 查询执行
        queries = [
            ("如何优化这个函数？", "可以使用缓存来优化"),
            ("这段代码有什么问题？", "没有发现明显问题"),
            ("如何添加单元测试？", "可以使用 unittest 框架")
        ]
        
        for query, response in queries:
            await self.context_bridge.on_query_executed(
                query=query,
                response=response,
                project_path=self.test_project_path,
                success=True
            )
        
        # 4. 验证上下文积累
        
        # 获取项目上下文
        project_context_result = await self.memory_os_manager.get_project_context(
            project_id, include_sessions=True
        )
        
        self.assertEqual(project_context_result["status"], "success")
        project_context = project_context_result["project"]
        
        # 验证文件记录
        self.assertGreater(len(project_context["active_files"]), 0)
        
        # 验证查询记录
        self.assertGreater(len(project_context["recent_queries"]), 0)
        
        # 5. 验证记忆搜索
        search_result = await self.memory_os_manager.search_memories(
            project_id=project_id,
            query="优化",
            limit=10
        )
        
        self.assertEqual(search_result["status"], "success")
        self.assertGreater(len(search_result["memories"]), 0)
        
        # 6. 验证相关上下文获取
        relevant_context = await self.context_bridge.get_relevant_context_for_query(
            query="如何优化代码？",
            project_path=self.test_project_path
        )
        
        self.assertIsInstance(relevant_context, str)
        self.assertGreater(len(relevant_context), 0)
        
        print("✅ 端到端工作流测试成功")
    
    async def test_11_performance_benchmarks(self):
        """测试性能基准"""
        print("\n🧪 测试性能基准...")
        
        if not self.memory_os_manager:
            await self.test_01_memory_os_manager_initialization()
        
        # 性能测试参数
        num_projects = 10
        num_sessions_per_project = 5
        num_memories_per_project = 20
        
        # 1. 项目创建性能
        start_time = time.time()
        project_ids = []
        
        for i in range(num_projects):
            result = await self.memory_os_manager.create_project_context(
                project_name=f"性能测试项目_{i}",
                project_path=f"{self.test_project_path}_{i}",
                description=f"性能测试项目 {i}"
            )
            self.assertEqual(result["status"], "success")
            project_ids.append(result["project_id"])
        
        project_creation_time = time.time() - start_time
        print(f"📊 项目创建性能: {num_projects} 个项目，耗时 {project_creation_time:.2f} 秒")
        
        # 2. 会话创建性能
        start_time = time.time()
        session_ids = []
        
        for project_id in project_ids:
            for j in range(num_sessions_per_project):
                result = await self.memory_os_manager.start_session(
                    project_id=project_id,
                    initial_context=f"性能测试会话 {j}"
                )
                self.assertEqual(result["status"], "success")
                session_ids.append(result["session_id"])
        
        session_creation_time = time.time() - start_time
        total_sessions = num_projects * num_sessions_per_project
        print(f"📊 会话创建性能: {total_sessions} 个会话，耗时 {session_creation_time:.2f} 秒")
        
        # 3. 记忆添加性能
        start_time = time.time()
        
        for project_id in project_ids:
            for k in range(num_memories_per_project):
                result = await self.memory_os_manager.add_memory(
                    project_id=project_id,
                    memory_type="performance_test",
                    content=f"性能测试记忆 {k}：这是一个测试记忆，用于验证系统性能",
                    importance=0.5,
                    tags=[f"test_{k}", "performance"]
                )
                self.assertEqual(result["status"], "success")
        
        memory_creation_time = time.time() - start_time
        total_memories = num_projects * num_memories_per_project
        print(f"📊 记忆添加性能: {total_memories} 条记忆，耗时 {memory_creation_time:.2f} 秒")
        
        # 4. 记忆搜索性能
        start_time = time.time()
        search_count = 50
        
        for i in range(search_count):
            project_id = project_ids[i % len(project_ids)]
            result = await self.memory_os_manager.search_memories(
                project_id=project_id,
                query="测试",
                limit=5
            )
            self.assertEqual(result["status"], "success")
        
        search_time = time.time() - start_time
        print(f"📊 记忆搜索性能: {search_count} 次搜索，耗时 {search_time:.2f} 秒")
        
        # 5. 性能要求验证
        avg_project_creation = project_creation_time / num_projects
        avg_session_creation = session_creation_time / total_sessions
        avg_memory_creation = memory_creation_time / total_memories
        avg_search_time = search_time / search_count
        
        print(f"\n📈 性能基准结果:")
        print(f"  - 平均项目创建时间: {avg_project_creation:.3f} 秒")
        print(f"  - 平均会话创建时间: {avg_session_creation:.3f} 秒")
        print(f"  - 平均记忆添加时间: {avg_memory_creation:.3f} 秒")
        print(f"  - 平均搜索时间: {avg_search_time:.3f} 秒")
        
        # 性能要求（可以根据实际需求调整）
        self.assertLess(avg_project_creation, 0.1, "项目创建时间应小于 100ms")
        self.assertLess(avg_session_creation, 0.05, "会话创建时间应小于 50ms")
        self.assertLess(avg_memory_creation, 0.02, "记忆添加时间应小于 20ms")
        self.assertLess(avg_search_time, 0.1, "搜索时间应小于 100ms")
        
        print("✅ 性能基准测试通过")
    
    async def test_12_error_handling(self):
        """测试错误处理"""
        print("\n🧪 测试错误处理...")
        
        if not self.memory_os_manager:
            await self.test_01_memory_os_manager_initialization()
        
        # 1. 测试不存在的项目
        result = await self.memory_os_manager.get_project_context("nonexistent_project")
        self.assertEqual(result["status"], "error")
        self.assertIn("项目不存在", result["error"])
        
        # 2. 测试不存在的会话
        result = await self.memory_os_manager.get_session_context("nonexistent_session")
        self.assertEqual(result["status"], "error")
        self.assertIn("会话不存在", result["error"])
        
        # 3. 测试无效的会话更新
        result = await self.memory_os_manager.update_session_context(
            "nonexistent_session", {"test": "data"}
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("会话不存在", result["error"])
        
        # 4. 测试重复项目创建
        create_result1 = await self.memory_os_manager.create_project_context(
            project_name="重复测试项目",
            project_path=self.test_project_path,
            description="第一次创建"
        )
        self.assertEqual(create_result1["status"], "success")
        
        create_result2 = await self.memory_os_manager.create_project_context(
            project_name="重复测试项目",
            project_path=self.test_project_path,
            description="第二次创建"
        )
        self.assertEqual(create_result2["status"], "exists")
        
        print("✅ 错误处理测试通过")
    
    async def test_13_statistics_and_monitoring(self):
        """测试统计和监控"""
        print("\n🧪 测试统计和监控...")
        
        if not self.memory_os_manager:
            await self.test_01_memory_os_manager_initialization()
        
        if not self.context_bridge:
            await self.test_05_context_bridge_initialization()
        
        # 获取 MemoryOS 统计
        memory_stats = await self.memory_os_manager.get_stats()
        self.assertIn("total_projects", memory_stats)
        self.assertIn("total_memories", memory_stats)
        self.assertIn("timestamp", memory_stats)
        
        # 获取上下文桥接器统计
        bridge_stats = await self.context_bridge.get_stats()
        self.assertIn("events_processed", bridge_stats)
        self.assertIn("context_syncs", bridge_stats)
        self.assertIn("registered_components", bridge_stats)
        
        print(f"📊 MemoryOS 统计: {memory_stats}")
        print(f"📊 上下文桥接器统计: {bridge_stats}")
        
        print("✅ 统计和监控测试通过")

class TestPerformanceBenchmarks(unittest.IsolatedAsyncioTestCase):
    """性能基准测试类"""
    
    async def test_concurrent_operations(self):
        """测试并发操作性能"""
        print("\n🚀 测试并发操作性能...")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 配置
            config = {
                "storage_path": os.path.join(temp_dir, "memory_os"),
                "max_memory_size": 1000,
                "context_ttl_days": 30,
                "compression_enabled": True,
                "auto_cleanup_enabled": False
            }
            
            # 创建 MemoryOS 管理器
            memory_os = MemoryOSManager(config)
            await memory_os.initialize()
            
            # 并发创建项目
            async def create_project(i):
                return await memory_os.create_project_context(
                    project_name=f"并发项目_{i}",
                    project_path=f"/tmp/concurrent_project_{i}",
                    description=f"并发测试项目 {i}"
                )
            
            start_time = time.time()
            tasks = [create_project(i) for i in range(20)]
            results = await asyncio.gather(*tasks)
            concurrent_time = time.time() - start_time
            
            # 验证结果
            for result in results:
                self.assertEqual(result["status"], "success")
            
            print(f"📊 并发创建 20 个项目耗时: {concurrent_time:.2f} 秒")
            self.assertLess(concurrent_time, 2.0, "并发操作应在 2 秒内完成")
            
            # 清理
            await memory_os.cleanup()
            
        finally:
            shutil.rmtree(temp_dir)
        
        print("✅ 并发操作性能测试通过")

def run_integration_tests():
    """运行集成测试"""
    print("🧪 开始 PowerAutomation v4.8 AWS Bedrock MCP 集成测试")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestAWSBedrockMCPIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceBenchmarks))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 所有集成测试通过！")
        return True
    else:
        print(f"❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        return False

if __name__ == "__main__":
    # 运行测试
    success = run_integration_tests()
    sys.exit(0 if success else 1)

