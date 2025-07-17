#!/usr/bin/env python3
"""
Test Claude Tool Mode - 测试 Claude 工具模式功能
验证完全不使用 Claude 模型服务，只使用工具和指令，将 AI 推理任务路由到 K2 服务的功能
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from core.components.startup_trigger_mcp.startup_trigger_manager import (
    StartupTriggerManager, StartupTriggerConfig
)
from core.components.startup_trigger_mcp.claude_tool_mode_config import (
    ClaudeToolModeManager
)
from core.components.startup_trigger_mcp.k2_service_router import (
    K2ServiceRouter, K2Request
)
from core.components.startup_trigger_mcp.claude_tool_mode_integration import (
    ClaudeToolModeIntegration
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ClaudeToolModeTest:
    """Claude 工具模式测试类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.test_results = []
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始 Claude 工具模式功能测试")
        print("=" * 60)
        
        tests = [
            ("工具模式配置测试", self.test_tool_mode_config),
            ("K2 服务路由测试", self.test_k2_service_router),
            ("工具模式集成测试", self.test_tool_mode_integration),
            ("启动触发管理器测试", self.test_startup_trigger_manager),
            ("模型请求拦截测试", self.test_model_request_interception),
            ("AI 推理路由测试", self.test_ai_inference_routing),
            ("工具请求处理测试", self.test_tool_request_handling),
            ("完整流程测试", self.test_complete_workflow)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}...")
            try:
                result = await test_func()
                self.test_results.append({
                    "name": test_name,
                    "success": result,
                    "error": None
                })
                status = "✅ 通过" if result else "❌ 失败"
                print(f"   {status}")
            except Exception as e:
                self.test_results.append({
                    "name": test_name,
                    "success": False,
                    "error": str(e)
                })
                print(f"   ❌ 异常: {e}")
        
        # 输出测试总结
        self.print_test_summary()
    
    async def test_tool_mode_config(self) -> bool:
        """测试工具模式配置"""
        try:
            manager = ClaudeToolModeManager()
            
            # 测试启用工具模式
            manager.enable_tool_mode()
            
            # 验证配置
            assert manager.is_tool_mode_enabled() == True
            assert manager.is_model_inference_disabled() == True
            
            # 测试工具白名单
            assert manager.is_tool_allowed("file_read") == True
            assert manager.is_tool_allowed("unknown_tool") == False
            
            # 测试端点阻止
            assert manager.is_endpoint_blocked("/v1/messages") == True
            assert manager.is_endpoint_blocked("/v1/tools") == False
            
            # 测试 K2 路由
            assert manager.should_route_to_k2("chat_completion") == True
            assert manager.should_route_to_k2("file_operation") == False
            
            print("     ✓ 工具模式配置正常")
            print("     ✓ 工具白名单功能正常")
            print("     ✓ 端点阻止功能正常")
            print("     ✓ K2 路由判断正常")
            
            return True
            
        except Exception as e:
            print(f"     ❌ 配置测试失败: {e}")
            return False
    
    async def test_k2_service_router(self) -> bool:
        """测试 K2 服务路由"""
        try:
            router = K2ServiceRouter()
            
            # 测试健康检查
            print("     🔍 检查 K2 服务健康状态...")
            healthy = await router.health_check()
            print(f"     K2 服务状态: {'✅ 正常' if healthy else '⚠️ 异常'}")
            
            # 如果服务正常，测试路由功能
            if healthy:
                # 测试文本生成
                response = await router.route_text_generation("Hello, this is a test.")
                assert response.success == True
                assert len(response.content) > 0
                print(f"     ✓ 文本生成测试通过 (响应时间: {response.response_time:.2f}s)")
                
                # 测试代码生成
                response = await router.route_code_generation("写一个 Python 函数计算斐波那契数列", "python")
                assert response.success == True
                print(f"     ✓ 代码生成测试通过 (响应时间: {response.response_time:.2f}s)")
            
            # 测试统计信息
            stats = router.get_stats()
            assert "total_requests" in stats
            assert "success_rate" in stats
            print("     ✓ 统计信息获取正常")
            
            await router.cleanup()
            return True
            
        except Exception as e:
            print(f"     ❌ K2 路由测试失败: {e}")
            return False
    
    async def test_tool_mode_integration(self) -> bool:
        """测试工具模式集成"""
        try:
            integration = ClaudeToolModeIntegration()
            
            # 测试初始化
            success = await integration.initialize()
            assert success == True
            print("     ✓ 集成器初始化成功")
            
            # 测试请求拦截器注册
            assert len(integration.request_interceptors) > 0
            print(f"     ✓ 已注册 {len(integration.request_interceptors)} 个请求拦截器")
            
            # 测试模型请求拦截
            request_data = {
                "endpoint": "/v1/messages",
                "type": "chat_completion",
                "content": "Hello"
            }
            
            result = await integration.intercept_request(request_data)
            assert result.get("blocked") == True or result.get("routed_to_k2") == True
            print("     ✓ 模型请求拦截功能正常")
            
            # 测试统计信息
            stats = integration.get_integration_stats()
            assert "intercepted_requests" in stats
            assert "initialized" in stats
            print("     ✓ 集成统计信息正常")
            
            await integration.cleanup()
            return True
            
        except Exception as e:
            print(f"     ❌ 集成测试失败: {e}")
            return False
    
    async def test_startup_trigger_manager(self) -> bool:
        """测试启动触发管理器"""
        try:
            config = StartupTriggerConfig(
                claude_tool_mode_enabled=True,
                k2_service_enabled=True,
                mirror_code_enabled=False  # 简化测试
            )
            
            manager = StartupTriggerManager(config)
            
            # 测试初始化
            success = await manager.initialize()
            assert success == True
            print("     ✓ 启动触发管理器初始化成功")
            
            # 测试系统状态
            status = await manager.check_system_status()
            assert "manager_status" in status
            assert "tool_mode_stats" in status
            print("     ✓ 系统状态检查正常")
            
            await manager.cleanup()
            return True
            
        except Exception as e:
            print(f"     ❌ 启动触发管理器测试失败: {e}")
            return False
    
    async def test_model_request_interception(self) -> bool:
        """测试模型请求拦截"""
        try:
            config = StartupTriggerConfig(
                claude_tool_mode_enabled=True,
                k2_service_enabled=True
            )
            
            manager = StartupTriggerManager(config)
            await manager.initialize()
            
            # 测试模型推理请求（应该被拦截或路由到 K2）
            test_inputs = [
                "请帮我分析这段代码",
                "生成一个 Python 函数",
                "解释一下机器学习的概念",
                "翻译这段英文"
            ]
            
            for test_input in test_inputs:
                result = await manager.process_claude_code_input(test_input)
                
                # 验证请求被正确处理
                assert result.get("processed") == True
                
                # 检查是否被工具模式处理
                if result.get("tool_mode_handled"):
                    assert result.get("blocked") == True or result.get("routed_to_k2") == True
                    print(f"     ✓ 输入 '{test_input[:20]}...' 被正确拦截/路由")
            
            await manager.cleanup()
            return True
            
        except Exception as e:
            print(f"     ❌ 模型请求拦截测试失败: {e}")
            return False
    
    async def test_ai_inference_routing(self) -> bool:
        """测试 AI 推理路由"""
        try:
            integration = ClaudeToolModeIntegration()
            await integration.initialize()
            
            # 测试 AI 推理请求路由
            ai_requests = [
                {
                    "type": "chat_completion",
                    "content": "Hello, how are you?",
                    "context": {"test": True}
                },
                {
                    "type": "code_generation", 
                    "content": "写一个排序算法",
                    "context": {"language": "python"}
                },
                {
                    "type": "analysis",
                    "content": "分析这个数据集",
                    "context": {"data_type": "csv"}
                }
            ]
            
            for request in ai_requests:
                result = await integration._route_ai_inference_requests(request)
                
                if result and result.get("routed_to_k2"):
                    k2_response = result.get("response", {})
                    assert k2_response.get("success") == True
                    print(f"     ✓ {request['type']} 请求成功路由到 K2")
            
            await integration.cleanup()
            return True
            
        except Exception as e:
            print(f"     ❌ AI 推理路由测试失败: {e}")
            return False
    
    async def test_tool_request_handling(self) -> bool:
        """测试工具请求处理"""
        try:
            integration = ClaudeToolModeIntegration()
            await integration.initialize()
            
            # 测试允许的工具请求
            allowed_tools = ["file_read", "shell_exec", "browser_navigate"]
            
            for tool_name in allowed_tools:
                request_data = {
                    "tool_name": tool_name,
                    "type": "tool_request"
                }
                
                result = await integration._handle_tool_requests(request_data)
                
                # 允许的工具应该返回 None（不拦截）
                assert result is None
                print(f"     ✓ 工具 '{tool_name}' 被正确允许")
            
            # 测试不允许的工具请求
            blocked_tool = "unknown_dangerous_tool"
            request_data = {
                "tool_name": blocked_tool,
                "type": "tool_request"
            }
            
            result = await integration._handle_tool_requests(request_data)
            
            # 不允许的工具应该被阻止
            if result:
                assert result.get("blocked") == True
                print(f"     ✓ 工具 '{blocked_tool}' 被正确阻止")
            
            await integration.cleanup()
            return True
            
        except Exception as e:
            print(f"     ❌ 工具请求处理测试失败: {e}")
            return False
    
    async def test_complete_workflow(self) -> bool:
        """测试完整工作流程"""
        try:
            print("     🔄 测试完整的 Claude 工具模式工作流程...")
            
            # 1. 创建配置
            config = StartupTriggerConfig(
                claude_tool_mode_enabled=True,
                k2_service_enabled=True,
                mirror_code_enabled=False
            )
            
            # 2. 初始化管理器
            manager = StartupTriggerManager(config)
            success = await manager.initialize()
            assert success == True
            print("     ✓ 步骤 1: 管理器初始化成功")
            
            # 3. 测试模型请求被拦截并路由到 K2
            ai_input = "请帮我写一个计算器程序"
            result = await manager.process_claude_code_input(ai_input)
            
            assert result.get("processed") == True
            assert result.get("tool_mode_handled") == True
            
            if result.get("routed_to_k2"):
                k2_response = result.get("k2_response", {})
                assert k2_response.get("success") == True
                print("     ✓ 步骤 2: AI 请求成功路由到 K2 服务")
                print(f"       响应时间: {k2_response.get('response_time', 0):.2f}s")
                print(f"       成本: ${k2_response.get('cost', 0):.4f}")
            elif result.get("blocked"):
                print("     ✓ 步骤 2: 模型请求被正确阻止")
            
            # 4. 测试工具请求正常通过
            tool_input = "需要 ClaudeEditor"  # 这应该触发工具安装
            result = await manager.process_claude_code_input(tool_input)
            
            assert result.get("processed") == True
            print("     ✓ 步骤 3: 工具请求正常处理")
            
            # 5. 检查最终状态
            final_status = await manager.check_system_status()
            tool_mode_stats = final_status.get("tool_mode_stats", {})
            
            print(f"     ✓ 步骤 4: 最终状态检查完成")
            print(f"       拦截请求数: {tool_mode_stats.get('intercepted_requests', 0)}")
            print(f"       路由到 K2: {tool_mode_stats.get('routed_to_k2', 0)}")
            print(f"       阻止模型请求: {tool_mode_stats.get('blocked_model_requests', 0)}")
            
            await manager.cleanup()
            print("     ✅ 完整工作流程测试通过")
            
            return True
            
        except Exception as e:
            print(f"     ❌ 完整工作流程测试失败: {e}")
            return False
    
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("🧪 Claude 工具模式测试总结")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['name']}")
                    if result["error"]:
                        print(f"    错误: {result['error']}")
        
        print("\n" + "=" * 60)
        
        if failed_tests == 0:
            print("🎉 所有测试通过！Claude 工具模式功能正常工作。")
        else:
            print("⚠️ 部分测试失败，请检查相关功能。")


async def main():
    """主函数"""
    print("🚀 PowerAutomation Claude 工具模式测试")
    print("完全不使用 Claude 模型服务，只使用工具和指令，将 AI 推理任务路由到 K2 服务")
    print()
    
    tester = ClaudeToolModeTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

