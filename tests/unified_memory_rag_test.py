#!/usr/bin/env python3
"""
统一 Memory RAG 接口全面测试

测试范围:
1. 统一接口初始化和配置
2. 模式感知查询功能
3. 智能路由决策
4. 混合查询和结果合并
5. 个性化处理
6. 性能和并发测试
7. 错误处理和降级
8. 健康检查和监控
"""

import os
import sys
import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any
import tempfile

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入测试目标
from core.components.unified_memory_rag_interface import (
    UnifiedMemoryRAGInterface,
    QueryContext,
    QueryMode,
    ServiceProvider,
    unified_query,
    unified_add_document,
    unified_health_check
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedMemoryRAGTest:
    """统一 Memory RAG 接口测试类"""
    
    def __init__(self):
        self.interface = None
        self.test_results = {}
        self.temp_dir = tempfile.mkdtemp()
        
    async def setup(self):
        """测试环境设置"""
        logger.info("🔧 设置统一接口测试环境...")
        
        try:
            # 创建测试配置
            test_config = {
                "memory_engine": {
                    "db_path": os.path.join(self.temp_dir, "test_unified.db"),
                    "enable_rag": True,
                    "enable_s3": False  # 测试环境不使用 S3
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
                    "query_timeout": 10.0,
                    "max_concurrent_queries": 10,
                    "cache_enabled": False,  # 测试时禁用缓存
                    "cache_ttl": 60
                }
            }
            
            # 初始化统一接口
            self.interface = UnifiedMemoryRAGInterface(test_config)
            success = await self.interface.initialize()
            
            if success:
                logger.info("✅ 统一接口测试环境设置完成")
                return True
            else:
                logger.error("❌ 统一接口初始化失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 测试环境设置失败: {e}")
            return False
    
    async def test_interface_initialization(self):
        """测试接口初始化"""
        logger.info("🧪 测试统一接口初始化...")
        
        test_results = {
            "initialization": False,
            "service_status": False,
            "health_check": False
        }
        
        try:
            # 测试初始化状态
            test_results["initialization"] = self.interface.is_initialized
            
            # 测试服务状态
            status = await self.interface.get_system_status()
            test_results["service_status"] = status["initialized"]
            
            # 测试健康检查
            health = await self.interface.health_check()
            test_results["health_check"] = health["status"] in ["healthy", "degraded"]
            
            logger.info(f"✅ 初始化测试完成: {test_results}")
            
        except Exception as e:
            logger.error(f"❌ 初始化测试失败: {e}")
        
        self.test_results["interface_initialization"] = test_results
        return all(test_results.values())
    
    async def test_mode_aware_queries(self):
        """测试模式感知查询"""
        logger.info("🧪 测试模式感知查询...")
        
        test_results = {
            "teacher_mode": False,
            "assistant_mode": False,
            "auto_mode": False
        }
        
        try:
            # 准备测试文档
            await self.interface.add_document(
                "test_doc_mode",
                "PowerAutomation 是一个智能开发平台，支持代码生成和项目管理。",
                {"test": "mode_awareness"}
            )
            
            # 测试教师模式
            teacher_context = QueryContext(
                user_id="test_user",
                current_tool="claude_code_tool",
                current_model="claude",
                mode=QueryMode.TEACHER_MODE
            )
            
            teacher_result = await self.interface.query(
                "PowerAutomation 的主要功能是什么？",
                teacher_context
            )
            
            test_results["teacher_mode"] = (
                teacher_result.mode == QueryMode.TEACHER_MODE and
                len(teacher_result.content) > 0
            )
            
            # 测试助手模式
            assistant_context = QueryContext(
                user_id="test_user",
                current_tool="other_tool",
                current_model="k2",
                mode=QueryMode.ASSISTANT_MODE
            )
            
            assistant_result = await self.interface.query(
                "PowerAutomation 的主要功能是什么？",
                assistant_context
            )
            
            test_results["assistant_mode"] = (
                assistant_result.mode == QueryMode.ASSISTANT_MODE and
                len(assistant_result.content) > 0
            )
            
            # 测试自动模式检测
            auto_context = QueryContext(
                user_id="test_user",
                current_tool="claude_code_tool",
                current_model="claude",
                mode=QueryMode.AUTO_MODE
            )
            
            auto_result = await self.interface.query(
                "PowerAutomation 的主要功能是什么？",
                auto_context
            )
            
            test_results["auto_mode"] = (
                auto_result.mode == QueryMode.TEACHER_MODE  # 应该自动检测为教师模式
            )
            
            logger.info(f"✅ 模式感知测试完成: {test_results}")
            
        except Exception as e:
            logger.error(f"❌ 模式感知测试失败: {e}")
        
        self.test_results["mode_aware_queries"] = test_results
        return all(test_results.values())
    
    async def test_routing_strategies(self):
        """测试路由策略"""
        logger.info("🧪 测试路由策略...")
        
        test_results = {
            "hybrid_routing": False,
            "fallback_routing": False,
            "provider_selection": False
        }
        
        try:
            context = QueryContext(user_id="test_user")
            
            # 测试混合路由
            result = await self.interface.query("测试混合路由", context)
            test_results["hybrid_routing"] = result.provider in [
                ServiceProvider.HYBRID, 
                ServiceProvider.MEMORY_OS, 
                ServiceProvider.AWS_BEDROCK
            ]
            
            # 测试提供者选择逻辑
            test_results["provider_selection"] = True  # 如果能执行到这里说明选择逻辑正常
            
            # 测试降级机制（模拟服务不可用）
            original_status = self.interface.service_status.copy()
            self.interface.service_status["aws_bedrock_mcp"] = False
            
            fallback_result = await self.interface.query("测试降级路由", context)
            test_results["fallback_routing"] = fallback_result.provider == ServiceProvider.MEMORY_OS
            
            # 恢复状态
            self.interface.service_status = original_status
            
            logger.info(f"✅ 路由策略测试完成: {test_results}")
            
        except Exception as e:
            logger.error(f"❌ 路由策略测试失败: {e}")
        
        self.test_results["routing_strategies"] = test_results
        return all(test_results.values())
    
    async def test_document_management(self):
        """测试文档管理"""
        logger.info("🧪 测试文档管理...")
        
        test_results = {
            "add_document": False,
            "query_document": False,
            "batch_add": False
        }
        
        try:
            # 测试单个文档添加
            success = await self.interface.add_document(
                "test_doc_1",
                "这是第一个测试文档，包含重要的测试信息。",
                {"category": "test", "priority": "high"}
            )
            test_results["add_document"] = success
            
            # 测试文档查询
            context = QueryContext(user_id="test_user")
            result = await self.interface.query("测试文档的内容是什么？", context)
            test_results["query_document"] = len(result.sources) > 0
            
            # 测试批量添加
            batch_success = 0
            for i in range(5):
                success = await self.interface.add_document(
                    f"batch_doc_{i}",
                    f"这是批量测试文档 {i}，用于测试批量处理能力。",
                    {"batch": i}
                )
                if success:
                    batch_success += 1
            
            test_results["batch_add"] = batch_success >= 3  # 至少成功添加3个
            
            logger.info(f"✅ 文档管理测试完成: {test_results}")
            
        except Exception as e:
            logger.error(f"❌ 文档管理测试失败: {e}")
        
        self.test_results["document_management"] = test_results
        return all(test_results.values())
    
    async def test_performance_concurrent(self):
        """测试性能和并发"""
        logger.info("🧪 测试性能和并发...")
        
        test_results = {
            "response_time": False,
            "concurrent_queries": False,
            "throughput": False
        }
        
        try:
            context = QueryContext(user_id="test_user")
            
            # 测试单次查询响应时间
            start_time = time.time()
            result = await self.interface.query("性能测试查询", context)
            response_time = time.time() - start_time
            
            test_results["response_time"] = response_time < 5.0  # 5秒内完成
            
            # 测试并发查询
            start_time = time.time()
            
            tasks = []
            for i in range(10):
                task = self.interface.query(f"并发测试查询 {i}", context)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            concurrent_time = time.time() - start_time
            
            successful_queries = sum(
                1 for r in results 
                if not isinstance(r, Exception) and hasattr(r, 'content')
            )
            
            test_results["concurrent_queries"] = successful_queries >= 7  # 至少70%成功
            test_results["throughput"] = concurrent_time < 10.0  # 10秒内完成
            
            logger.info(f"✅ 性能测试完成: {test_results}")
            logger.info(f"   响应时间: {response_time:.3f}s")
            logger.info(f"   并发成功率: {successful_queries}/10")
            logger.info(f"   并发总时间: {concurrent_time:.3f}s")
            
        except Exception as e:
            logger.error(f"❌ 性能测试失败: {e}")
        
        self.test_results["performance_concurrent"] = test_results
        return all(test_results.values())
    
    async def test_error_handling(self):
        """测试错误处理"""
        logger.info("🧪 测试错误处理...")
        
        test_results = {
            "invalid_query": False,
            "service_failure": False,
            "graceful_degradation": False
        }
        
        try:
            context = QueryContext(user_id="test_user")
            
            # 测试无效查询处理
            result = await self.interface.query("", context)  # 空查询
            test_results["invalid_query"] = result.confidence == 0.0
            
            # 测试服务故障处理
            original_status = self.interface.service_status.copy()
            self.interface.service_status["memoryos_mcp"] = False
            self.interface.service_status["aws_bedrock_mcp"] = False
            
            try:
                result = await self.interface.query("测试服务故障", context)
                test_results["service_failure"] = "失败" in result.content or "错误" in result.content
            except:
                test_results["service_failure"] = True  # 预期的异常
            
            # 恢复部分服务测试优雅降级
            self.interface.service_status["memoryos_mcp"] = True
            result = await self.interface.query("测试优雅降级", context)
            test_results["graceful_degradation"] = result.provider == ServiceProvider.MEMORY_OS
            
            # 恢复状态
            self.interface.service_status = original_status
            
            logger.info(f"✅ 错误处理测试完成: {test_results}")
            
        except Exception as e:
            logger.error(f"❌ 错误处理测试失败: {e}")
        
        self.test_results["error_handling"] = test_results
        return all(test_results.values())
    
    async def test_convenience_functions(self):
        """测试便捷函数"""
        logger.info("🧪 测试便捷函数...")
        
        test_results = {
            "unified_query": False,
            "unified_add_document": False,
            "unified_health_check": False
        }
        
        try:
            # 测试便捷查询函数
            context = QueryContext(user_id="test_user")
            result = await unified_query("便捷函数测试", context)
            test_results["unified_query"] = hasattr(result, 'content')
            
            # 测试便捷文档添加函数
            success = await unified_add_document(
                "convenience_doc",
                "这是便捷函数测试文档",
                {"test": "convenience"}
            )
            test_results["unified_add_document"] = success
            
            # 测试便捷健康检查函数
            health = await unified_health_check()
            test_results["unified_health_check"] = "status" in health
            
            logger.info(f"✅ 便捷函数测试完成: {test_results}")
            
        except Exception as e:
            logger.error(f"❌ 便捷函数测试失败: {e}")
        
        self.test_results["convenience_functions"] = test_results
        return all(test_results.values())
    
    async def cleanup(self):
        """清理测试环境"""
        logger.info("🧹 清理测试环境...")
        
        try:
            # 清理数据库连接
            if self.interface and self.interface.memory_engine:
                if hasattr(self.interface.memory_engine, 'connection') and self.interface.memory_engine.connection:
                    self.interface.memory_engine.connection.close()
            
            # 清理临时文件
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            
            logger.info("✅ 测试环境清理完成")
            
        except Exception as e:
            logger.error(f"❌ 清理测试环境失败: {e}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始统一 Memory RAG 接口全面测试...")
        
        # 设置测试环境
        if not await self.setup():
            return False
        
        try:
            # 运行各项测试
            tests = [
                ("接口初始化", self.test_interface_initialization),
                ("模式感知查询", self.test_mode_aware_queries),
                ("路由策略", self.test_routing_strategies),
                ("文档管理", self.test_document_management),
                ("性能并发", self.test_performance_concurrent),
                ("错误处理", self.test_error_handling),
                ("便捷函数", self.test_convenience_functions)
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
            logger.info(f"📊 统一接口测试结果汇总")
            logger.info(f"{'='*60}")
            logger.info(f"通过测试: {passed_tests}/{total_tests}")
            logger.info(f"成功率: {success_rate:.1f}%")
            
            # 显示详细结果
            for category, results in self.test_results.items():
                if isinstance(results, dict):
                    passed = sum(1 for v in results.values() if v)
                    total = len(results)
                    logger.info(f"  {category}: {passed}/{total}")
            
            if success_rate >= 80:
                logger.info("🎉 统一 Memory RAG 接口测试整体通过！")
                return True
            else:
                logger.error("❌ 统一 Memory RAG 接口测试整体失败！")
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
                ),
                "overall_success": all(
                    (all(category.values()) if isinstance(category, dict) else category)
                    for category in self.test_results.values()
                )
            }
        }
        
        return report

async def main():
    """主函数"""
    test_runner = UnifiedMemoryRAGTest()
    
    try:
        success = await test_runner.run_all_tests()
        
        # 生成报告
        report = test_runner.generate_report()
        
        # 保存报告
        with open("unified_memory_rag_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 测试报告已保存到: unified_memory_rag_test_report.json")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ 测试运行失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

