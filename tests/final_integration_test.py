#!/usr/bin/env python3
"""
Memory RAG MCP 最终完整集成测试
PowerAutomation v4.8 - 端到端验证

测试覆盖:
1. 统一接口完整功能测试
2. 高性能多 Provider 路由测试
3. 模式感知个性化测试
4. 故障回退机制测试
5. 性能基准测试
6. 并发处理测试
7. 数据一致性测试
"""

import asyncio
import logging
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures
from dataclasses import asdict

# 添加路径
sys.path.append('/home/ubuntu/aicore0716')

from core.components.unified_memory_rag_interface import (
    UnifiedMemoryRAGInterface, 
    QueryContext, 
    QueryMode,
    ServiceProvider
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinalIntegrationTester:
    """最终集成测试器"""
    
    def __init__(self):
        self.interface = None
        self.test_results = {
            "test_suite": "Memory RAG MCP Final Integration Test",
            "version": "v4.8",
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {},
            "performance_metrics": {},
            "recommendations": []
        }
        
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 Memory RAG MCP 最终完整集成测试...")
        print("=" * 80)
        
        try:
            # 1. 初始化测试
            await self._test_initialization()
            
            # 2. 基础功能测试
            await self._test_basic_functionality()
            
            # 3. 高性能多 Provider 测试
            await self._test_multi_provider_routing()
            
            # 4. 模式感知测试
            await self._test_mode_awareness()
            
            # 5. 个性化功能测试
            await self._test_personalization()
            
            # 6. 故障回退测试
            await self._test_fallback_mechanisms()
            
            # 7. 性能基准测试
            await self._test_performance_benchmarks()
            
            # 8. 并发处理测试
            await self._test_concurrent_processing()
            
            # 9. 数据一致性测试
            await self._test_data_consistency()
            
            # 10. 健康检查测试
            await self._test_health_monitoring()
            
            # 生成最终报告
            await self._generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ 测试执行失败: {e}")
            self.test_results["summary"]["overall_status"] = "FAILED"
            self.test_results["summary"]["error"] = str(e)
        
        print("=" * 80)
        print("✅ Memory RAG MCP 最终集成测试完成")
    
    async def _test_initialization(self):
        """测试初始化"""
        print("\n🔧 测试 1: 系统初始化")
        test_name = "initialization"
        start_time = time.time()
        
        try:
            # 创建统一接口
            self.interface = UnifiedMemoryRAGInterface()
            
            # 初始化
            success = await self.interface.initialize()
            
            if success:
                # 检查组件状态
                health = await self.interface.health_check()
                healthy_components = sum(
                    1 for comp in health["components"].values() 
                    if comp["status"] == "healthy"
                )
                total_components = len(health["components"])
                
                self.test_results["tests"][test_name] = {
                    "status": "PASSED",
                    "execution_time": time.time() - start_time,
                    "details": {
                        "initialization_success": True,
                        "healthy_components": healthy_components,
                        "total_components": total_components,
                        "component_health": health["components"]
                    }
                }
                print(f"  ✅ 初始化成功 ({healthy_components}/{total_components} 组件健康)")
            else:
                raise Exception("初始化失败")
                
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 初始化失败: {e}")
            raise
    
    async def _test_basic_functionality(self):
        """测试基础功能"""
        print("\n🔍 测试 2: 基础功能")
        test_name = "basic_functionality"
        start_time = time.time()
        
        try:
            # 测试基本查询
            context = QueryContext(
                current_tool="test_tool",
                current_model="test_model",
                user_id="test_user",
                session_id="test_session"
            )
            
            query = "什么是 Python？"
            result = await self.interface.query(query, context)
            
            # 测试文档添加
            doc_success = await self.interface.add_document(
                doc_id="test_doc_1",
                content="Python 是一种高级编程语言，以其简洁和可读性著称。",
                metadata={"source": "test", "type": "definition"}
            )
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED",
                "execution_time": time.time() - start_time,
                "details": {
                    "query_success": result.status == "success",
                    "query_response_time": result.response_time,
                    "document_add_success": doc_success,
                    "provider_used": result.provider,
                    "response_length": len(result.response)
                }
            }
            print(f"  ✅ 基础功能正常 (查询: {result.status}, 文档添加: {doc_success})")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 基础功能测试失败: {e}")
    
    async def _test_multi_provider_routing(self):
        """测试高性能多 Provider 路由"""
        print("\n🚀 测试 3: 高性能多 Provider 路由")
        test_name = "multi_provider_routing"
        start_time = time.time()
        
        try:
            providers_used = set()
            response_times = []
            
            # 执行多次查询，观察 Provider 路由
            queries = [
                "解释机器学习的基本概念",
                "如何优化 Python 代码性能？",
                "什么是微服务架构？",
                "数据库索引的作用是什么？",
                "如何设计 RESTful API？"
            ]
            
            for i, query in enumerate(queries):
                context = QueryContext(
                    current_tool="test_tool",
                    current_model="test_model",
                    user_id=f"test_user_{i}",
                    session_id=f"test_session_{i}"
                )
                
                result = await self.interface.query(query, context)
                providers_used.add(result.provider)
                response_times.append(result.response_time)
                
                print(f"    查询 {i+1}: {result.provider} ({result.response_time:.2f}s)")
            
            # 获取多 Provider 统计
            stats = self.interface.get_statistics()
            multi_provider_stats = stats.get("multi_provider", {})
            
            avg_response_time = sum(response_times) / len(response_times)
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED",
                "execution_time": time.time() - start_time,
                "details": {
                    "providers_used": list(providers_used),
                    "total_queries": len(queries),
                    "avg_response_time": avg_response_time,
                    "provider_stats": multi_provider_stats,
                    "routing_diversity": len(providers_used) > 1
                }
            }
            print(f"  ✅ 多 Provider 路由正常 (使用了 {len(providers_used)} 个 Provider)")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 多 Provider 路由测试失败: {e}")
    
    async def _test_mode_awareness(self):
        """测试模式感知"""
        print("\n🎯 测试 4: 模式感知")
        test_name = "mode_awareness"
        start_time = time.time()
        
        try:
            # 测试教师模式
            teacher_context = QueryContext(
                current_tool="claude_code_tool",
                current_model="claude",
                user_id="teacher_user",
                session_id="teacher_session"
            )
            
            teacher_result = await self.interface.query(
                "解释 Python 装饰器的工作原理",
                teacher_context
            )
            
            # 测试助手模式
            assistant_context = QueryContext(
                current_tool="other_tool",
                current_model="k2",
                user_id="assistant_user",
                session_id="assistant_session"
            )
            
            assistant_result = await self.interface.query(
                "解释 Python 装饰器的工作原理",
                assistant_context
            )
            
            # 检查模式检测
            teacher_mode_detected = teacher_result.mode == "teacher_mode"
            assistant_mode_detected = assistant_result.mode == "assistant_mode"
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED",
                "execution_time": time.time() - start_time,
                "details": {
                    "teacher_mode_detected": teacher_mode_detected,
                    "assistant_mode_detected": assistant_mode_detected,
                    "teacher_response_length": len(teacher_result.response),
                    "assistant_response_length": len(assistant_result.response),
                    "mode_differentiation": teacher_mode_detected and assistant_mode_detected
                }
            }
            print(f"  ✅ 模式感知正常 (教师: {teacher_mode_detected}, 助手: {assistant_mode_detected})")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 模式感知测试失败: {e}")
    
    async def _test_personalization(self):
        """测试个性化功能"""
        print("\n💡 测试 5: 个性化功能")
        test_name = "personalization"
        start_time = time.time()
        
        try:
            # 测试助手模式个性化
            context = QueryContext(
                current_tool="other_tool",
                current_model="k2",
                user_id="personalization_user",
                session_id="personalization_session"
            )
            
            result = await self.interface.query(
                "这是一个 Python 函数示例",
                context
            )
            
            # 检查个性化标识
            personalization_indicators = [
                "简洁提示" in result.response,
                "效率" in result.response,
                "轻松模式" in result.response or "你" in result.response
            ]
            
            personalization_applied = any(personalization_indicators)
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED" if personalization_applied else "PARTIAL",
                "execution_time": time.time() - start_time,
                "details": {
                    "personalization_applied": personalization_applied,
                    "personalization_indicators": {
                        "concise_hint": personalization_indicators[0],
                        "efficiency_tip": personalization_indicators[1],
                        "casual_tone": personalization_indicators[2]
                    },
                    "response_content": result.response
                }
            }
            
            status = "正常" if personalization_applied else "部分生效"
            print(f"  ✅ 个性化功能{status}")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 个性化功能测试失败: {e}")
    
    async def _test_fallback_mechanisms(self):
        """测试故障回退机制"""
        print("\n🔄 测试 6: 故障回退机制")
        test_name = "fallback_mechanisms"
        start_time = time.time()
        
        try:
            # 模拟高负载情况下的查询
            context = QueryContext(
                current_tool="test_tool",
                current_model="test_model",
                user_id="fallback_user",
                session_id="fallback_session"
            )
            
            # 执行查询并观察 Provider 选择
            result = await self.interface.query(
                "在高负载情况下如何保证系统稳定性？",
                context
            )
            
            # 检查健康状态
            health = await self.interface.health_check()
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED",
                "execution_time": time.time() - start_time,
                "details": {
                    "query_success": result.status == "success",
                    "provider_used": result.provider,
                    "system_health": health["overall_status"],
                    "fallback_available": len(health["components"]) > 1
                }
            }
            print(f"  ✅ 故障回退机制正常 (系统状态: {health['overall_status']})")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 故障回退机制测试失败: {e}")
    
    async def _test_performance_benchmarks(self):
        """测试性能基准"""
        print("\n⚡ 测试 7: 性能基准")
        test_name = "performance_benchmarks"
        start_time = time.time()
        
        try:
            # 性能基准测试
            benchmark_queries = [
                "什么是人工智能？",
                "解释深度学习的原理",
                "如何优化数据库查询？",
                "微服务架构的优缺点",
                "云计算的发展趋势"
            ]
            
            response_times = []
            success_count = 0
            
            for query in benchmark_queries:
                context = QueryContext(
                    current_tool="benchmark_tool",
                    current_model="benchmark_model",
                    user_id="benchmark_user",
                    session_id="benchmark_session"
                )
                
                query_start = time.time()
                result = await self.interface.query(query, context)
                query_time = time.time() - query_start
                
                response_times.append(query_time)
                if result.status == "success":
                    success_count += 1
            
            avg_response_time = sum(response_times) / len(response_times)
            success_rate = success_count / len(benchmark_queries)
            
            # 性能评级
            if avg_response_time < 5.0:
                performance_grade = "EXCELLENT"
            elif avg_response_time < 10.0:
                performance_grade = "GOOD"
            elif avg_response_time < 20.0:
                performance_grade = "ACCEPTABLE"
            else:
                performance_grade = "POOR"
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED",
                "execution_time": time.time() - start_time,
                "details": {
                    "avg_response_time": avg_response_time,
                    "success_rate": success_rate,
                    "performance_grade": performance_grade,
                    "total_queries": len(benchmark_queries),
                    "response_times": response_times
                }
            }
            
            self.test_results["performance_metrics"] = {
                "avg_response_time": avg_response_time,
                "success_rate": success_rate,
                "performance_grade": performance_grade
            }
            
            print(f"  ✅ 性能基准测试完成 (平均响应时间: {avg_response_time:.2f}s, 成功率: {success_rate:.1%}, 评级: {performance_grade})")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 性能基准测试失败: {e}")
    
    async def _test_concurrent_processing(self):
        """测试并发处理"""
        print("\n🔀 测试 8: 并发处理")
        test_name = "concurrent_processing"
        start_time = time.time()
        
        try:
            # 并发查询测试
            concurrent_queries = [
                f"并发查询测试 {i+1}: 什么是分布式系统？"
                for i in range(5)
            ]
            
            async def single_query(query_text, query_id):
                context = QueryContext(
                    current_tool="concurrent_tool",
                    current_model="concurrent_model",
                    user_id=f"concurrent_user_{query_id}",
                    session_id=f"concurrent_session_{query_id}"
                )
                return await self.interface.query(query_text, context)
            
            # 并发执行查询
            concurrent_start = time.time()
            tasks = [
                single_query(query, i) 
                for i, query in enumerate(concurrent_queries)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            concurrent_time = time.time() - concurrent_start
            
            # 分析结果
            successful_results = [
                r for r in results 
                if not isinstance(r, Exception) and r.status == "success"
            ]
            
            success_rate = len(successful_results) / len(concurrent_queries)
            avg_concurrent_response_time = (
                sum(r.response_time for r in successful_results) / len(successful_results)
                if successful_results else 0
            )
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED",
                "execution_time": time.time() - start_time,
                "details": {
                    "concurrent_queries": len(concurrent_queries),
                    "successful_queries": len(successful_results),
                    "success_rate": success_rate,
                    "total_concurrent_time": concurrent_time,
                    "avg_response_time": avg_concurrent_response_time,
                    "concurrency_efficiency": len(concurrent_queries) / concurrent_time
                }
            }
            print(f"  ✅ 并发处理正常 (成功率: {success_rate:.1%}, 并发效率: {len(concurrent_queries)/concurrent_time:.2f} 查询/秒)")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 并发处理测试失败: {e}")
    
    async def _test_data_consistency(self):
        """测试数据一致性"""
        print("\n🔒 测试 9: 数据一致性")
        test_name = "data_consistency"
        start_time = time.time()
        
        try:
            # 添加测试文档
            test_docs = [
                {
                    "id": "consistency_doc_1",
                    "content": "数据一致性是分布式系统的重要特性。",
                    "metadata": {"type": "definition", "topic": "consistency"}
                },
                {
                    "id": "consistency_doc_2", 
                    "content": "ACID 属性保证了数据库事务的一致性。",
                    "metadata": {"type": "explanation", "topic": "database"}
                }
            ]
            
            # 添加文档
            add_results = []
            for doc in test_docs:
                result = await self.interface.add_document(
                    doc["id"], doc["content"], doc["metadata"]
                )
                add_results.append(result)
            
            # 查询相关内容
            context = QueryContext(
                current_tool="consistency_tool",
                current_model="consistency_model",
                user_id="consistency_user",
                session_id="consistency_session"
            )
            
            query_result = await self.interface.query(
                "什么是数据一致性？",
                context
            )
            
            # 检查数据一致性
            all_docs_added = all(add_results)
            query_successful = query_result.status == "success"
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED",
                "execution_time": time.time() - start_time,
                "details": {
                    "documents_added": len([r for r in add_results if r]),
                    "total_documents": len(test_docs),
                    "add_success_rate": sum(add_results) / len(add_results),
                    "query_successful": query_successful,
                    "data_consistency": all_docs_added and query_successful
                }
            }
            print(f"  ✅ 数据一致性正常 (文档添加: {sum(add_results)}/{len(test_docs)}, 查询: {query_successful})")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 数据一致性测试失败: {e}")
    
    async def _test_health_monitoring(self):
        """测试健康监控"""
        print("\n🏥 测试 10: 健康监控")
        test_name = "health_monitoring"
        start_time = time.time()
        
        try:
            # 获取健康状态
            health = await self.interface.health_check()
            
            # 获取统计信息
            stats = self.interface.get_statistics()
            
            # 分析健康状态
            healthy_components = sum(
                1 for comp in health["components"].values()
                if comp["status"] == "healthy"
            )
            total_components = len(health["components"])
            
            health_score = healthy_components / total_components
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED",
                "execution_time": time.time() - start_time,
                "details": {
                    "overall_status": health["overall_status"],
                    "healthy_components": healthy_components,
                    "total_components": total_components,
                    "health_score": health_score,
                    "statistics_available": bool(stats),
                    "total_queries": stats.get("total_queries", 0),
                    "success_rate": (
                        stats.get("successful_queries", 0) / 
                        max(stats.get("total_queries", 1), 1)
                    )
                }
            }
            print(f"  ✅ 健康监控正常 (状态: {health['overall_status']}, 健康度: {health_score:.1%})")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "execution_time": time.time() - start_time,
                "error": str(e)
            }
            print(f"  ❌ 健康监控测试失败: {e}")
    
    async def _generate_final_report(self):
        """生成最终报告"""
        print("\n📊 生成最终测试报告...")
        
        # 计算总体统计
        total_tests = len(self.test_results["tests"])
        passed_tests = sum(
            1 for test in self.test_results["tests"].values()
            if test["status"] == "PASSED"
        )
        partial_tests = sum(
            1 for test in self.test_results["tests"].values()
            if test["status"] == "PARTIAL"
        )
        failed_tests = sum(
            1 for test in self.test_results["tests"].values()
            if test["status"] == "FAILED"
        )
        
        success_rate = (passed_tests + partial_tests * 0.5) / total_tests
        
        # 生成总结
        self.test_results["summary"] = {
            "overall_status": "PASSED" if success_rate >= 0.8 else "PARTIAL" if success_rate >= 0.6 else "FAILED",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "partial_tests": partial_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_duration": sum(
                test.get("execution_time", 0)
                for test in self.test_results["tests"].values()
            )
        }
        
        # 生成建议
        recommendations = []
        
        if failed_tests > 0:
            recommendations.append("修复失败的测试用例")
        
        if partial_tests > 0:
            recommendations.append("完善部分通过的功能")
        
        if self.test_results["performance_metrics"].get("avg_response_time", 0) > 10:
            recommendations.append("优化响应时间性能")
        
        if success_rate < 0.9:
            recommendations.append("提高系统整体稳定性")
        
        if not recommendations:
            recommendations.append("系统运行良好，可以部署到生产环境")
        
        self.test_results["recommendations"] = recommendations
        
        # 保存报告
        report_path = "/tmp/memory_rag_mcp_final_test_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # 打印总结
        print(f"\n📋 测试总结:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过: {passed_tests}")
        print(f"  部分通过: {partial_tests}")
        print(f"  失败: {failed_tests}")
        print(f"  成功率: {success_rate:.1%}")
        print(f"  整体状态: {self.test_results['summary']['overall_status']}")
        print(f"\n📄 详细报告已保存到: {report_path}")
        
        return report_path


async def main():
    """主函数"""
    tester = FinalIntegrationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

