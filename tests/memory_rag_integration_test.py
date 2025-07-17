#!/usr/bin/env python3
"""
Memory RAG MCP 集成测试
测试 memoryos_mcp 和 aws_bedrock_mcp 的集成功能

测试范围:
1. MemoryEngine RAG 功能测试
2. AWS Bedrock MCP 组件测试
3. 两个 MCP 之间的协调测试
4. 性能和稳定性测试
"""

import os
import sys
import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.components.memoryos_mcp.memory_engine import MemoryEngine, MemoryType, Memory
from core.components.aws_bedrock_mcp.integration_manager import IntegrationManager
from core.components.aws_bedrock_mcp.rag_service import RAGService
from core.components.aws_bedrock_mcp.k2_router import K2Router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemoryRAGIntegrationTest:
    """Memory RAG 集成测试类"""
    
    def __init__(self):
        self.memory_engine = None
        self.integration_manager = None
        self.rag_service = None
        self.k2_router = None
        self.test_results = {}
        
    async def setup(self):
        """测试环境设置"""
        logger.info("🔧 设置测试环境...")
        
        try:
            # 初始化 MemoryEngine (带 RAG 功能)
            self.memory_engine = MemoryEngine(
                db_path="test_memory.db",
                enable_rag=True,
                enable_s3=False  # 测试环境不使用 S3
            )
            await self.memory_engine.initialize()
            
            # 初始化 AWS Bedrock MCP 组件
            self.integration_manager = IntegrationManager()
            await self.integration_manager.initialize()
            
            self.rag_service = RAGService()
            await self.rag_service.initialize()
            
            self.k2_router = K2Router()
            
            logger.info("✅ 测试环境设置完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 测试环境设置失败: {e}")
            return False
    
    async def test_memory_engine_rag(self):
        """测试 MemoryEngine 的 RAG 功能"""
        logger.info("🧪 测试 MemoryEngine RAG 功能...")
        
        test_results = {
            "add_document": False,
            "rag_query": False,
            "statistics": False
        }
        
        try:
            # 测试添加文档到 RAG
            test_doc = """
            PowerAutomation v4.8 是一个先进的自动化开发平台。
            它集成了 Memory RAG 系统，支持智能代码生成和项目管理。
            主要特性包括：
            1. 智能路由 MCP - 自动选择最佳模型
            2. Memory OS - 项目上下文管理
            3. RAG 检索 - 基于向量的文档检索
            4. AWS S3 集成 - 企业级存储
            """
            
            success = await self.memory_engine.add_document_to_rag(
                doc_id="test_doc_1",
                content=test_doc,
                metadata={"source": "test", "version": "4.8"}
            )
            test_results["add_document"] = success
            
            if success:
                logger.info("✅ 文档添加到 RAG 成功")
            else:
                logger.error("❌ 文档添加到 RAG 失败")
            
            # 测试 RAG 查询
            query_results = await self.memory_engine.rag_query(
                query="PowerAutomation 的主要特性是什么？",
                top_k=3
            )
            
            test_results["rag_query"] = len(query_results) > 0
            
            if query_results:
                logger.info(f"✅ RAG 查询成功，返回 {len(query_results)} 个结果")
                for i, result in enumerate(query_results):
                    logger.info(f"  结果 {i+1}: {result.get('content', '')[:100]}...")
            else:
                logger.error("❌ RAG 查询失败")
            
            # 测试统计信息
            stats = await self.memory_engine.get_rag_statistics()
            test_results["statistics"] = stats.get("rag_enabled", False)
            
            if stats.get("rag_enabled"):
                logger.info(f"✅ RAG 统计信息: {stats}")
            else:
                logger.error("❌ RAG 统计信息获取失败")
                
        except Exception as e:
            logger.error(f"❌ MemoryEngine RAG 测试失败: {e}")
        
        self.test_results["memory_engine_rag"] = test_results
        return all(test_results.values())
    
    async def test_aws_bedrock_mcp(self):
        """测试 AWS Bedrock MCP 组件"""
        logger.info("🧪 测试 AWS Bedrock MCP 组件...")
        
        test_results = {
            "integration_manager": False,
            "rag_service": False,
            "k2_router": False
        }
        
        try:
            # 测试 IntegrationManager
            if self.integration_manager:
                status = await self.integration_manager.get_system_status()
                test_results["integration_manager"] = status.get("status") == "healthy"
                logger.info(f"✅ IntegrationManager 状态: {status}")
            
            # 测试 RAGService
            if self.rag_service:
                # 添加测试文档
                await self.rag_service.add_document(
                    "test_doc_2",
                    "这是 AWS Bedrock MCP 的测试文档。它包含了 RAG 服务的功能测试。",
                    {"source": "aws_bedrock_test"}
                )
                
                # 查询测试
                results = await self.rag_service.query(
                    "AWS Bedrock MCP 的功能是什么？",
                    top_k=2
                )
                test_results["rag_service"] = len(results) > 0
                logger.info(f"✅ RAGService 查询返回 {len(results)} 个结果")
            
            # 测试 K2Router
            if self.k2_router:
                # 测试路由决策
                route_decision = await self.k2_router.route_request(
                    "生成一个 Python 函数",
                    context_length=1000
                )
                test_results["k2_router"] = route_decision is not None
                logger.info(f"✅ K2Router 路由决策: {route_decision}")
                
        except Exception as e:
            logger.error(f"❌ AWS Bedrock MCP 测试失败: {e}")
        
        self.test_results["aws_bedrock_mcp"] = test_results
        return all(test_results.values())
    
    async def test_integration_coordination(self):
        """测试两个 MCP 之间的协调"""
        logger.info("🧪 测试 MCP 协调功能...")
        
        test_results = {
            "data_sharing": False,
            "unified_query": False,
            "performance": False
        }
        
        try:
            # 测试数据共享
            # 在 MemoryEngine 中添加文档
            await self.memory_engine.add_document_to_rag(
                "shared_doc",
                "这是一个共享文档，用于测试 MCP 之间的数据协调。",
                {"shared": True}
            )
            
            # 通过 IntegrationManager 查询
            if self.integration_manager:
                query_result = await self.integration_manager.unified_query(
                    "共享文档的内容是什么？"
                )
                test_results["data_sharing"] = query_result.get("status") == "success"
                logger.info(f"✅ 数据共享测试: {query_result}")
            
            # 测试统一查询接口
            start_time = time.time()
            
            # 并发查询测试
            tasks = []
            for i in range(5):
                task = self.memory_engine.rag_query(f"测试查询 {i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful_queries = sum(1 for r in results if not isinstance(r, Exception))
            test_results["unified_query"] = successful_queries >= 3
            
            # 性能测试
            query_time = end_time - start_time
            test_results["performance"] = query_time < 5.0  # 5秒内完成
            
            logger.info(f"✅ 并发查询测试: {successful_queries}/5 成功，耗时 {query_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ MCP 协调测试失败: {e}")
        
        self.test_results["integration_coordination"] = test_results
        return all(test_results.values())
    
    async def test_performance_stress(self):
        """性能压力测试"""
        logger.info("🧪 进行性能压力测试...")
        
        test_results = {
            "bulk_insert": False,
            "concurrent_query": False,
            "memory_usage": False
        }
        
        try:
            # 批量插入测试
            start_time = time.time()
            
            for i in range(50):
                await self.memory_engine.add_document_to_rag(
                    f"bulk_doc_{i}",
                    f"这是批量测试文档 {i}。内容包含了各种测试数据和信息。",
                    {"batch": i}
                )
            
            bulk_time = time.time() - start_time
            test_results["bulk_insert"] = bulk_time < 30.0  # 30秒内完成
            logger.info(f"✅ 批量插入测试: 50个文档，耗时 {bulk_time:.2f}s")
            
            # 并发查询压力测试
            start_time = time.time()
            
            tasks = []
            for i in range(20):
                task = self.memory_engine.rag_query(f"批量测试文档 {i % 10}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            concurrent_time = time.time() - start_time
            
            successful_queries = sum(1 for r in results if not isinstance(r, Exception))
            test_results["concurrent_query"] = (
                successful_queries >= 15 and concurrent_time < 10.0
            )
            
            logger.info(f"✅ 并发查询压力测试: {successful_queries}/20 成功，耗时 {concurrent_time:.2f}s")
            
            # 内存使用测试 (简化版)
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            test_results["memory_usage"] = memory_mb < 500  # 小于 500MB
            
            logger.info(f"✅ 内存使用测试: {memory_mb:.2f}MB")
            
        except Exception as e:
            logger.error(f"❌ 性能压力测试失败: {e}")
        
        self.test_results["performance_stress"] = test_results
        return all(test_results.values())
    
    async def cleanup(self):
        """清理测试环境"""
        logger.info("🧹 清理测试环境...")
        
        try:
            # 清理测试数据库
            if self.memory_engine and self.memory_engine.connection:
                self.memory_engine.connection.close()
            
            # 删除测试文件
            test_files = ["test_memory.db", "test_memory.db-wal", "test_memory.db-shm"]
            for file in test_files:
                if os.path.exists(file):
                    os.remove(file)
            
            logger.info("✅ 测试环境清理完成")
            
        except Exception as e:
            logger.error(f"❌ 清理测试环境失败: {e}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始 Memory RAG MCP 集成测试...")
        
        # 设置测试环境
        if not await self.setup():
            return False
        
        try:
            # 运行各项测试
            tests = [
                ("MemoryEngine RAG 功能", self.test_memory_engine_rag),
                ("AWS Bedrock MCP 组件", self.test_aws_bedrock_mcp),
                ("MCP 协调功能", self.test_integration_coordination),
                ("性能压力测试", self.test_performance_stress)
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                logger.info(f"\n{'='*50}")
                logger.info(f"🧪 运行测试: {test_name}")
                logger.info(f"{'='*50}")
                
                try:
                    result = await test_func()
                    if result:
                        logger.info(f"✅ {test_name} - 通过")
                        passed_tests += 1
                    else:
                        logger.error(f"❌ {test_name} - 失败")
                except Exception as e:
                    logger.error(f"❌ {test_name} - 异常: {e}")
            
            # 生成测试报告
            success_rate = (passed_tests / total_tests) * 100
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 测试结果汇总")
            logger.info(f"{'='*60}")
            logger.info(f"通过测试: {passed_tests}/{total_tests}")
            logger.info(f"成功率: {success_rate:.1f}%")
            
            if success_rate >= 80:
                logger.info("🎉 Memory RAG MCP 集成测试整体通过！")
                return True
            else:
                logger.error("❌ Memory RAG MCP 集成测试整体失败！")
                return False
                
        finally:
            await self.cleanup()
    
    def generate_report(self):
        """生成详细测试报告"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": self.test_results,
            "summary": {
                "total_test_categories": len(self.test_results),
                "passed_categories": sum(
                    1 for category in self.test_results.values() 
                    if (all(category.values()) if isinstance(category, dict) else category)
                )
            }
        }
        
        return report

async def main():
    """主函数"""
    test_runner = MemoryRAGIntegrationTest()
    
    try:
        success = await test_runner.run_all_tests()
        
        # 生成报告
        report = test_runner.generate_report()
        
        # 保存报告
        with open("memory_rag_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 测试报告已保存到: memory_rag_test_report.json")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ 测试运行失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

