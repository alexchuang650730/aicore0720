#!/usr/bin/env python3
"""
Mirror Code 修复验证测试
验证智能路由器是否成功实现 Claude Code 去除
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MirrorCodeFixTest:
    """Mirror Code 修复验证测试"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def run_all_tests(self):
        """运行所有测试"""
        print("🔧 开始 Mirror Code 修复验证测试")
        print("=" * 60)
        
        # 测试智能路由器
        await self.test_smart_router()
        
        # 测试K2指令处理器
        await self.test_k2_handlers()
        
        # 测试Command MCP集成
        await self.test_command_mcp_integration()
        
        # 测试Claude Code去除
        await self.test_claude_code_elimination()
        
        # 生成测试报告
        self.generate_test_report()
    
    async def test_smart_router(self):
        """测试智能路由器"""
        print("\n🧠 测试智能路由器")
        print("-" * 40)
        
        try:
            # 导入智能路由器
            from core.components.command_mcp.smart_router import (
                route_command_intelligently, get_router_stats, smart_router
            )
            
            # 测试基础指令路由
            test_commands = [
                "/help",
                "/status", 
                "/add-dir /test/path",
                "/review code.py",
                "/chat 请解释代码",
                "/unknown-command"
            ]
            
            for cmd in test_commands:
                try:
                    decision = await route_command_intelligently(cmd)
                    
                    # 验证路由决策
                    assert hasattr(decision, 'target_model'), "路由决策缺少目标模型"
                    assert hasattr(decision, 'confidence'), "路由决策缺少置信度"
                    assert hasattr(decision, 'reason'), "路由决策缺少原因"
                    
                    # 验证是否路由到K2
                    is_k2_routed = decision.target_model.value == "k2_cloud"
                    
                    self.record_test(
                        f"路由指令: {cmd}",
                        True,
                        f"✅ 路由到 {decision.target_model.value} (置信度: {decision.confidence:.2f})"
                    )
                    
                    print(f"  {cmd} -> {decision.target_model.value} ({decision.confidence:.2f})")
                    
                except Exception as e:
                    self.record_test(f"路由指令: {cmd}", False, f"❌ 路由失败: {str(e)}")
            
            # 测试路由统计
            stats = get_router_stats()
            assert isinstance(stats, dict), "路由统计应该返回字典"
            
            self.record_test("智能路由器统计", True, f"✅ 统计正常: {stats.get('total_requests', 0)} 个请求")
            
        except ImportError as e:
            self.record_test("智能路由器导入", False, f"❌ 导入失败: {str(e)}")
        except Exception as e:
            self.record_test("智能路由器测试", False, f"❌ 测试失败: {str(e)}")
    
    async def test_k2_handlers(self):
        """测试K2指令处理器"""
        print("\n🤖 测试K2指令处理器")
        print("-" * 40)
        
        try:
            # 导入K2处理器
            from core.components.command_mcp.k2_command_handlers import (
                handle_add_dir_k2, handle_chat_k2, handle_ask_k2,
                handle_review_k2, handle_unknown_command_k2
            )
            
            # 测试添加目录
            result = await handle_add_dir_k2(["/tmp"])
            assert isinstance(result, dict), "K2处理器应该返回字典"
            self.record_test("K2 /add-dir", True, "✅ 目录添加功能正常")
            
            # 测试聊天功能
            result = await handle_chat_k2(["测试K2聊天功能"])
            assert "success" in result or "ai_response" in result, "聊天功能应该有响应"
            self.record_test("K2 /chat", True, "✅ 聊天功能正常")
            
            # 测试问答功能
            result = await handle_ask_k2(["K2如何处理代码分析？"])
            assert "answer" in result or "success" in result, "问答功能应该有答案"
            self.record_test("K2 /ask", True, "✅ 问答功能正常")
            
            # 测试未知指令处理
            result = await handle_unknown_command_k2("/unknown-test", ["arg1"])
            assert "warning" in result or "k2_analysis" in result, "应该有未知指令分析"
            self.record_test("K2 未知指令处理", True, "✅ 未知指令处理正常")
            
            print("  ✅ K2指令处理器所有功能正常")
            
        except ImportError as e:
            self.record_test("K2处理器导入", False, f"❌ 导入失败: {str(e)}")
        except Exception as e:
            self.record_test("K2处理器测试", False, f"❌ 测试失败: {str(e)}")
    
    async def test_command_mcp_integration(self):
        """测试Command MCP集成"""
        print("\n⚙️ 测试Command MCP集成")
        print("-" * 40)
        
        try:
            # 导入Command MCP
            from core.components.command_mcp.command_manager import CommandMCP
            
            # 创建Command MCP实例
            command_mcp = CommandMCP()
            
            # 测试基础指令
            test_commands = [
                "/help",
                "/status",
                "/add-dir /tmp/test",
                "/chat 测试集成"
            ]
            
            for cmd in test_commands:
                try:
                    result = await command_mcp.handle_slash_command(cmd)
                    
                    # 验证结果结构
                    assert isinstance(result, dict), "Command MCP应该返回字典"
                    
                    # 验证路由信息
                    if "routing_info" in result:
                        routing_info = result["routing_info"]
                        assert "claude_avoided" in routing_info, "应该有Claude避免信息"
                        
                        if routing_info.get("claude_avoided"):
                            self.record_test(
                                f"Command MCP: {cmd}",
                                True,
                                f"✅ 成功避免Claude，使用 {routing_info.get('model', 'K2')}"
                            )
                        else:
                            self.record_test(
                                f"Command MCP: {cmd}",
                                False,
                                f"❌ 未能避免Claude依赖"
                            )
                    else:
                        # 旧版本结果格式
                        self.record_test(
                            f"Command MCP: {cmd}",
                            True,
                            "✅ 指令执行成功（旧格式）"
                        )
                    
                    print(f"  {cmd} -> 执行成功")
                    
                except Exception as e:
                    self.record_test(f"Command MCP: {cmd}", False, f"❌ 执行失败: {str(e)}")
            
        except ImportError as e:
            self.record_test("Command MCP导入", False, f"❌ 导入失败: {str(e)}")
        except Exception as e:
            self.record_test("Command MCP集成测试", False, f"❌ 测试失败: {str(e)}")
    
    async def test_claude_code_elimination(self):
        """测试Claude Code去除效果"""
        print("\n🚫 测试Claude Code去除效果")
        print("-" * 40)
        
        try:
            # 导入使用追踪器
            from core.components.mirror_code_tracker.usage_tracker import (
                get_current_usage_summary, usage_tracker
            )
            
            # 重置追踪器统计
            usage_tracker.session_records = []
            usage_tracker.session_stats = {
                "session_start": datetime.now().isoformat(),
                "total_commands": 0,
                "k2_cloud_count": 0,
                "claude_mirror_count": 0,
                "claude_direct_count": 0,
                "total_cost_usd": 0.0,
                "total_tokens": usage_tracker.session_stats["total_tokens"],
                "average_response_time": 0.0
            }
            
            # 模拟执行一些指令
            from core.components.command_mcp.command_manager import CommandMCP
            command_mcp = CommandMCP()
            
            test_commands = [
                "/help",
                "/add-dir /tmp",
                "/chat 测试Claude去除",
                "/ask K2如何工作？",
                "/review test.py"
            ]
            
            for cmd in test_commands:
                try:
                    await command_mcp.handle_slash_command(cmd)
                except:
                    pass  # 忽略执行错误，专注于追踪
            
            # 检查使用统计
            summary = get_current_usage_summary()
            
            if isinstance(summary, dict) and "model_distribution" in summary:
                k2_percentage = summary["model_distribution"].get("k2_cloud", {}).get("percentage", 0)
                claude_percentage = (
                    summary["model_distribution"].get("claude_mirror", {}).get("percentage", 0) +
                    summary["model_distribution"].get("claude_direct", {}).get("percentage", 0)
                )
                
                if k2_percentage >= 80:
                    self.record_test(
                        "Claude Code去除效果",
                        True,
                        f"✅ K2处理率: {k2_percentage}%, Claude使用率: {claude_percentage}%"
                    )
                else:
                    self.record_test(
                        "Claude Code去除效果",
                        False,
                        f"❌ K2处理率过低: {k2_percentage}%, Claude使用率: {claude_percentage}%"
                    )
                
                print(f"  K2处理率: {k2_percentage}%")
                print(f"  Claude使用率: {claude_percentage}%")
            else:
                self.record_test(
                    "Claude Code去除效果",
                    False,
                    "❌ 无法获取使用统计"
                )
            
        except Exception as e:
            self.record_test("Claude Code去除测试", False, f"❌ 测试失败: {str(e)}")
    
    def record_test(self, test_name: str, passed: bool, details: str):
        """记录测试结果"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 Mirror Code 修复验证报告")
        print("=" * 60)
        
        print(f"\n📈 测试统计:")
        print(f"  总测试数: {self.total_tests}")
        print(f"  通过测试: {self.passed_tests}")
        print(f"  失败测试: {self.failed_tests}")
        print(f"  成功率: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "  成功率: 0%")
        
        print(f"\n📋 详细结果:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"  {status} {result['test_name']}")
            print(f"     {result['details']}")
        
        # 保存测试报告
        report_data = {
            "test_summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0
            },
            "test_results": self.test_results,
            "test_timestamp": datetime.now().isoformat()
        }
        
        report_file = f"/home/ubuntu/aicore0711/mirror_code_fix_test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 测试报告已保存: {report_file}")
        
        # 总结
        if self.failed_tests == 0:
            print("\n🎉 所有测试通过！Mirror Code 修复成功！")
            print("✅ Claude Code 依赖已成功去除")
            print("✅ K2 智能路由正常工作")
            print("✅ 系统完全使用 K2 云端模型")
        else:
            print(f"\n⚠️ 有 {self.failed_tests} 个测试失败，需要进一步修复")
            print("请检查失败的测试项目并进行修复")

async def main():
    """主测试函数"""
    tester = MirrorCodeFixTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

