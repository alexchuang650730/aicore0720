#!/usr/bin/env python3
"""
完整的 Memory RAG MCP 集成测试
测试所有组件的协同工作
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_complete_integration():
    """完整集成测试"""
    print("🚀 开始完整的 Memory RAG MCP 集成测试...")
    
    test_results = {
        "memoryos_mcp": {"status": "pending", "details": {}},
        "aws_bedrock_mcp": {"status": "pending", "details": {}},
        "unified_interface": {"status": "pending", "details": {}},
        "learning_adapter": {"status": "pending", "details": {}},
        "end_to_end": {"status": "pending", "details": {}}
    }
    
    try:
        # 1. 测试 MemoryOS MCP
        print("\n📝 测试 MemoryOS MCP...")
        memoryos_result = await test_memoryos_mcp()
        test_results["memoryos_mcp"] = memoryos_result
        
        # 2. 测试 AWS Bedrock MCP
        print("\n☁️ 测试 AWS Bedrock MCP...")
        bedrock_result = await test_aws_bedrock_mcp()
        test_results["aws_bedrock_mcp"] = bedrock_result
        
        # 3. 测试统一接口
        print("\n🔗 测试统一接口...")
        unified_result = await test_unified_interface()
        test_results["unified_interface"] = unified_result
        
        # 4. 测试学习适配器
        print("\n🧠 测试学习适配器...")
        learning_result = await test_learning_adapter()
        test_results["learning_adapter"] = learning_result
        
        # 5. 端到端测试
        print("\n🎯 端到端集成测试...")
        e2e_result = await test_end_to_end()
        test_results["end_to_end"] = e2e_result
        
        # 生成测试报告
        await generate_test_report(test_results)
        
        return test_results
        
    except Exception as e:
        logger.error(f"❌ 集成测试失败: {e}")
        return test_results

async def test_memoryos_mcp():
    """测试 MemoryOS MCP"""
    try:
        from core.components.memoryos_mcp.memory_engine import MemoryEngine, Memory, MemoryType
        
        # 创建内存引擎
        engine = MemoryEngine(
            db_path="test_integration.db",
            max_memories=1000,
            enable_rag=True,
            enable_s3=False
        )
        
        await engine.initialize()
        
        # 测试基本功能
        test_memory = Memory(
            id="integration_test_001",
            memory_type=MemoryType.CLAUDE_INTERACTION,
            content="这是一个集成测试记忆，包含 Python 和 JavaScript 相关内容。",
            metadata={"test": True, "languages": ["python", "javascript"]},
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            importance_score=0.8,
            tags=["integration", "test", "programming"]
        )
        
        await engine.store_memory(test_memory)
        
        # 测试检索
        retrieved = await engine.retrieve_memory("integration_test_001")
        assert retrieved is not None, "记忆检索失败"
        
        # 测试搜索
        search_results = await engine.search_memories("Python", limit=5)
        assert len(search_results) > 0, "记忆搜索失败"
        
        # 测试 RAG 功能
        rag_success = await engine.add_document_to_rag(
            "integration_doc_001",
            "这是一个测试文档，用于验证 RAG 功能。包含机器学习和深度学习的内容。",
            {"type": "test_document", "topic": "AI"}
        )
        assert rag_success, "RAG 文档添加失败"
        
        # 测试 RAG 查询
        rag_results = await engine.rag_query("机器学习", top_k=3)
        assert len(rag_results) > 0, "RAG 查询失败"
        
        # 获取统计信息
        stats = await engine.get_memory_statistics()
        
        await engine.cleanup()
        
        return {
            "status": "success",
            "details": {
                "memory_stored": True,
                "memory_retrieved": True,
                "search_results": len(search_results),
                "rag_document_added": rag_success,
                "rag_query_results": len(rag_results),
                "total_memories": stats["total_memories"],
                "rag_enabled": stats.get("rag_enabled", False)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ MemoryOS MCP 测试失败: {e}")
        return {
            "status": "error",
            "details": {"error": str(e)}
        }

async def test_aws_bedrock_mcp():
    """测试 AWS Bedrock MCP"""
    try:
        from core.components.aws_bedrock_mcp.rag_service import RAGService
        
        # 创建 RAG 服务
        service = RAGService()
        
        # 初始化服务
        init_result = await service.initialize()
        assert init_result["status"] == "success", f"RAG 服务初始化失败: {init_result}"
        
        # 测试健康检查
        health = await service.health_check()
        assert health["status"] in ["healthy", "degraded"], f"健康检查失败: {health}"
        
        # 测试添加文档
        test_docs = [
            {
                "content": "FastAPI 是一个现代、快速的 Python Web 框架，用于构建 API。",
                "metadata": {"framework": "fastapi", "language": "python"}
            },
            {
                "content": "React 是一个用于构建用户界面的 JavaScript 库。",
                "metadata": {"framework": "react", "language": "javascript"}
            }
        ]
        
        add_result = await service.add_documents(test_docs)
        assert add_result["status"] == "success", f"文档添加失败: {add_result}"
        
        # 测试文档检索
        retrieve_result = await service.retrieve_documents("Python Web 框架")
        assert retrieve_result["status"] == "success", f"文档检索失败: {retrieve_result}"
        assert len(retrieve_result["documents"]) > 0, "未找到相关文档"
        
        # 获取统计信息
        stats = await service.get_statistics()
        
        return {
            "status": "success",
            "details": {
                "service_initialized": True,
                "health_status": health["status"],
                "documents_added": add_result["added_count"],
                "documents_retrieved": len(retrieve_result["documents"]),
                "total_documents": stats["total_documents"],
                "vector_index_size": stats["vector_index_size"]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ AWS Bedrock MCP 测试失败: {e}")
        return {
            "status": "error",
            "details": {"error": str(e)}
        }

async def test_unified_interface():
    """测试统一接口"""
    try:
        from core.components.unified_memory_rag_interface import UnifiedMemoryRAGInterface, QueryMode
        
        # 创建统一接口
        interface = UnifiedMemoryRAGInterface()
        
        # 初始化
        await interface.initialize()
        
        # 测试健康检查
        health = await interface.health_check()
        assert "memoryos_mcp" in health, "MemoryOS MCP 健康检查缺失"
        assert "aws_bedrock_mcp" in health, "AWS Bedrock MCP 健康检查缺失"
        
        # 测试添加文档
        success = await interface.add_document(
            "unified_test_doc",
            "这是一个统一接口测试文档，包含 Vue.js 和 Node.js 的内容。",
            {"test": "unified", "frameworks": ["vue", "node"]}
        )
        assert success, "统一接口文档添加失败"
        
        # 测试查询 - 混合模式
        results = await interface.query(
            "Vue.js 开发",
            mode=QueryMode.HYBRID,
            top_k=3
        )
        assert len(results) > 0, "统一接口查询失败"
        
        # 测试查询 - 仅 MemoryOS
        memory_results = await interface.query(
            "Node.js",
            mode=QueryMode.MEMORY_OS,
            top_k=3
        )
        
        # 测试查询 - 仅 AWS Bedrock
        bedrock_results = await interface.query(
            "JavaScript",
            mode=QueryMode.AWS_BEDROCK,
            top_k=3
        )
        
        # 获取统计信息
        stats = await interface.get_statistics()
        
        return {
            "status": "success",
            "details": {
                "interface_initialized": True,
                "health_check_passed": True,
                "document_added": success,
                "hybrid_query_results": len(results),
                "memory_query_results": len(memory_results),
                "bedrock_query_results": len(bedrock_results),
                "total_queries": stats.get("total_queries", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 统一接口测试失败: {e}")
        return {
            "status": "error",
            "details": {"error": str(e)}
        }

async def test_learning_adapter():
    """测试学习适配器"""
    try:
        from core.components.memoryos_mcp.learning_adapter import LearningAdapter, QueryContext, InteractionMode
        
        # 模拟依赖
        class MockMemoryEngine:
            async def search_memories(self, query, limit=3):
                return []
            async def store_memory(self, memory):
                pass
        
        class MockContextManager:
            async def get_context(self, context_id):
                return None
        
        # 创建学习适配器
        adapter = LearningAdapter(MockMemoryEngine(), MockContextManager())
        await adapter.initialize()
        
        # 测试模式检测
        teacher_context = QueryContext(
            current_tool="claude_code_tool",
            current_model="claude",
            user_id="test_user_001"
        )
        
        assistant_context = QueryContext(
            current_tool="other_tool",
            current_model="k2",
            user_id="test_user_002"
        )
        
        teacher_mode = adapter.detect_interaction_mode(teacher_context)
        assistant_mode = adapter.detect_interaction_mode(assistant_context)
        
        assert teacher_mode == InteractionMode.TEACHER_MODE, "教师模式检测失败"
        assert assistant_mode == InteractionMode.ASSISTANT_MODE, "助手模式检测失败"
        
        # 测试个性化处理
        test_response = "这是一个 Python 函数示例：\n```python\ndef hello():\n    print('Hello, World!')\n```"
        
        teacher_personalized = await adapter.personalize_response(test_response, teacher_context)
        assistant_personalized = await adapter.personalize_response(test_response, assistant_context)
        
        # 测试统计信息
        stats = await adapter.get_learning_statistics()
        
        return {
            "status": "success",
            "details": {
                "adapter_initialized": True,
                "teacher_mode_detected": teacher_mode == InteractionMode.TEACHER_MODE,
                "assistant_mode_detected": assistant_mode == InteractionMode.ASSISTANT_MODE,
                "teacher_personalization": len(teacher_personalized) > len(test_response),
                "assistant_personalization": len(assistant_personalized) != len(test_response),
                "total_users": stats["user_count"],
                "total_interactions": stats["total_interactions"]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 学习适配器测试失败: {e}")
        return {
            "status": "error",
            "details": {"error": str(e)}
        }

async def test_end_to_end():
    """端到端集成测试"""
    try:
        from core.components.unified_memory_rag_interface import UnifiedMemoryRAGInterface, QueryMode
        from core.components.memoryos_mcp.learning_adapter import QueryContext, InteractionMode
        
        # 创建完整的集成环境
        interface = UnifiedMemoryRAGInterface()
        await interface.initialize()
        
        # 模拟完整的用户交互流程
        user_context = QueryContext(
            current_tool="claude_code_tool",
            current_model="claude",
            user_id="e2e_test_user",
            session_id="e2e_session_001"
        )
        
        # 1. 添加多个相关文档
        documents = [
            {
                "id": "e2e_doc_001",
                "content": "Django 是一个高级的 Python Web 框架，鼓励快速开发和干净、实用的设计。",
                "metadata": {"framework": "django", "language": "python", "type": "web"}
            },
            {
                "id": "e2e_doc_002", 
                "content": "Express.js 是一个快速、极简的 Node.js Web 应用框架。",
                "metadata": {"framework": "express", "language": "javascript", "type": "web"}
            },
            {
                "id": "e2e_doc_003",
                "content": "Spring Boot 是一个基于 Java 的框架，用于创建微服务。",
                "metadata": {"framework": "spring", "language": "java", "type": "web"}
            }
        ]
        
        for doc in documents:
            success = await interface.add_document(doc["id"], doc["content"], doc["metadata"])
            assert success, f"文档 {doc['id']} 添加失败"
        
        # 2. 执行多种查询模式
        queries = [
            ("Python Web 开发", QueryMode.HYBRID),
            ("JavaScript 框架", QueryMode.MEMORY_OS),
            ("微服务架构", QueryMode.AWS_BEDROCK)
        ]
        
        query_results = {}
        for query, mode in queries:
            results = await interface.query(query, mode=mode, top_k=5)
            query_results[f"{query}_{mode.value}"] = len(results)
        
        # 3. 测试个性化响应
        if hasattr(interface, 'learning_adapter') and interface.learning_adapter:
            test_response = "推荐使用 Django 进行 Python Web 开发"
            personalized = await interface.learning_adapter.personalize_response(
                test_response, user_context
            )
            personalization_worked = len(personalized) != len(test_response)
        else:
            personalization_worked = False
        
        # 4. 获取综合统计
        interface_stats = await interface.get_statistics()
        
        # 5. 性能测试
        start_time = time.time()
        for _ in range(5):
            await interface.query("性能测试查询", mode=QueryMode.HYBRID, top_k=3)
        avg_response_time = (time.time() - start_time) / 5
        
        return {
            "status": "success",
            "details": {
                "documents_added": len(documents),
                "query_results": query_results,
                "personalization_worked": personalization_worked,
                "avg_response_time_ms": avg_response_time * 1000,
                "total_queries": interface_stats.get("total_queries", 0),
                "system_health": "healthy" if all(
                    result["status"] == "success" 
                    for result in [
                        await test_memoryos_mcp(),
                        await test_aws_bedrock_mcp()
                    ]
                ) else "degraded"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 端到端测试失败: {e}")
        return {
            "status": "error",
            "details": {"error": str(e)}
        }

async def generate_test_report(test_results: Dict[str, Any]):
    """生成测试报告"""
    report = {
        "test_summary": {
            "timestamp": time.time(),
            "total_tests": len(test_results),
            "passed_tests": sum(1 for r in test_results.values() if r["status"] == "success"),
            "failed_tests": sum(1 for r in test_results.values() if r["status"] == "error"),
            "overall_status": "PASS" if all(r["status"] == "success" for r in test_results.values()) else "FAIL"
        },
        "detailed_results": test_results
    }
    
    # 保存报告
    with open("/tmp/memory_rag_mcp_integration_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 打印摘要
    print(f"\n📊 **测试报告摘要**")
    print(f"总测试数: {report['test_summary']['total_tests']}")
    print(f"通过测试: {report['test_summary']['passed_tests']}")
    print(f"失败测试: {report['test_summary']['failed_tests']}")
    print(f"整体状态: {report['test_summary']['overall_status']}")
    
    # 详细结果
    for test_name, result in test_results.items():
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {test_name}: {result['status']}")
        
        if result["status"] == "success" and "details" in result:
            for key, value in result["details"].items():
                if isinstance(value, bool):
                    print(f"   - {key}: {'✅' if value else '❌'}")
                elif isinstance(value, (int, float)):
                    print(f"   - {key}: {value}")
    
    print(f"\n📄 详细报告已保存到: /tmp/memory_rag_mcp_integration_test_report.json")
    
    return report

async def main():
    """主测试函数"""
    print("🎯 Memory RAG MCP 完整集成测试")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        results = await test_complete_integration()
        
        total_time = time.time() - start_time
        print(f"\n⏱️ 总测试时间: {total_time:.2f} 秒")
        
        # 判断测试是否全部通过
        all_passed = all(r["status"] == "success" for r in results.values())
        
        if all_passed:
            print("🎉 所有集成测试通过！Memory RAG MCP 系统完全可用！")
            return 0
        else:
            print("⚠️ 部分测试失败，请检查详细报告")
            return 1
            
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())

