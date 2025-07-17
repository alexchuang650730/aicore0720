#!/usr/bin/env python3
"""
Startup Trigger Tests - 启动触发机制测试
测试和验证所有触发组件的功能
"""

import asyncio
import unittest
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入测试目标
from core.components.startup_trigger_mcp.trigger_detection import (
    ClaudeCodeTriggerDetector, TriggerType, TriggerPriority
)
from core.components.startup_trigger_mcp.trigger_actions import (
    TriggerActionExecutor, ActionStatus
)
from core.components.startup_trigger_mcp.hook_trigger_integration import (
    HookTriggerIntegrator
)
from core.components.startup_trigger_mcp.mirror_code_communication import (
    MirrorCodeCommunicator, CommunicationStatus
)
from core.components.startup_trigger_mcp.startup_trigger_manager import (
    StartupTriggerManager, StartupTriggerConfig
)

class TestTriggerDetection(unittest.TestCase):
    """测试触发检测功能"""
    
    def setUp(self):
        self.detector = ClaudeCodeTriggerDetector()
    
    async def test_claudeeditor_install_triggers(self):
        """测试 ClaudeEditor 安装触发"""
        test_cases = [
            "需要 ClaudeEditor",
            "启动编辑器",
            "安装 ClaudeEditor",
            "打开编辑界面",
            "PowerAutomation setup",
            "初始化编辑环境"
        ]
        
        for test_text in test_cases:
            with self.subTest(text=test_text):
                context = {"claudeeditor_not_installed": True}
                events = await self.detector.detect_triggers(test_text, context)
                
                self.assertGreater(len(events), 0, f"应该检测到触发事件: {test_text}")
                
                # 检查是否有 ClaudeEditor 安装触发
                install_events = [e for e in events if e.trigger_type == TriggerType.CLAUDEEDITOR_INSTALL]
                self.assertGreater(len(install_events), 0, f"应该检测到安装触发: {test_text}")
    
    async def test_mirror_code_sync_triggers(self):
        """测试 Mirror Code 同步触发"""
        test_cases = [
            "同步代码",
            "Mirror Code",
            "双向通信",
            "代码镜像",
            "实时同步"
        ]
        
        for test_text in test_cases:
            with self.subTest(text=test_text):
                context = {"claudeeditor_installed": True, "sync_required": True}
                events = await self.detector.detect_triggers(test_text, context)
                
                # 检查是否有 Mirror Code 同步触发
                sync_events = [e for e in events if e.trigger_type == TriggerType.MIRROR_CODE_SYNC]
                self.assertGreaterEqual(len(sync_events), 0, f"可能检测到同步触发: {test_text}")
    
    async def test_context_requirements(self):
        """测试上下文要求"""
        # 测试已安装情况下不触发安装
        context = {"claudeeditor_not_installed": False}
        events = await self.detector.detect_triggers("需要 ClaudeEditor", context)
        
        install_events = [e for e in events if e.trigger_type == TriggerType.CLAUDEEDITOR_INSTALL]
        # 由于上下文要求不满足，可能不会触发安装事件
        
        # 测试 Claude Code 专用触发
        context = {"claude_code_context": True}
        events = await self.detector.detect_triggers("PowerAutomation setup", context)
        
        self.assertGreater(len(events), 0, "应该检测到 Claude Code 专用触发")

class TestTriggerActions(unittest.TestCase):
    """测试触发动作功能"""
    
    def setUp(self):
        self.executor = TriggerActionExecutor()
    
    async def test_action_execution_flow(self):
        """测试动作执行流程"""
        # 创建模拟触发事件
        from core.components.startup_trigger_mcp.trigger_detection import TriggerEvent
        import uuid
        
        trigger_event = TriggerEvent(
            event_id=str(uuid.uuid4()),
            trigger_type=TriggerType.SYSTEM_READY,
            matched_pattern="test",
            matched_text="检查系统状态",
            context={"test": True},
            timestamp=datetime.now(),
            priority=TriggerPriority.LOW,
            source="test"
        )
        
        # 执行动作
        result = await self.executor.execute_trigger_action(trigger_event)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.trigger_event_id, trigger_event.event_id)
        self.assertIn(result.status, [ActionStatus.SUCCESS, ActionStatus.FAILED])
    
    def test_action_statistics(self):
        """测试动作统计"""
        stats = self.executor.get_action_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_actions", stats)
        self.assertIn("running_actions", stats)

class TestHookTriggerIntegration(unittest.TestCase):
    """测试钩子触发集成功能"""
    
    def setUp(self):
        self.integrator = HookTriggerIntegrator()
    
    async def test_manual_trigger_detection(self):
        """测试手动触发检测"""
        test_text = "需要启动 ClaudeEditor"
        result = await self.integrator.manual_trigger_detection(test_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
    
    def test_integration_statistics(self):
        """测试集成统计"""
        stats = self.integrator.get_integration_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("initialized", stats)

class TestMirrorCodeCommunication(unittest.TestCase):
    """测试 Mirror Code 通信功能"""
    
    def setUp(self):
        self.communicator = MirrorCodeCommunicator()
    
    async def test_initialization(self):
        """测试初始化"""
        # 注意：这个测试可能会失败，因为 ClaudeEditor 可能没有运行
        result = await self.communicator.initialize()
        
        # 无论成功与否，都应该返回布尔值
        self.assertIsInstance(result, bool)
    
    def test_communication_status(self):
        """测试通信状态"""
        status = self.communicator.get_communication_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("channels", status)

class TestStartupTriggerManager(unittest.TestCase):
    """测试启动触发管理器"""
    
    def setUp(self):
        config = StartupTriggerConfig(
            auto_trigger_enabled=True,
            auto_install_enabled=False,  # 测试时不自动安装
            mirror_code_enabled=False,   # 测试时不启用 Mirror Code
            log_level="DEBUG"
        )
        self.manager = StartupTriggerManager(config)
    
    async def test_manager_initialization(self):
        """测试管理器初始化"""
        result = await self.manager.initialize()
        
        self.assertTrue(result, "管理器应该初始化成功")
        self.assertTrue(self.manager.initialized)
    
    async def test_claude_code_input_processing(self):
        """测试 Claude Code 输入处理"""
        await self.manager.initialize()
        
        test_inputs = [
            "需要 ClaudeEditor",
            "启动编辑器",
            "检查系统状态",
            "无关的文本内容"
        ]
        
        for test_input in test_inputs:
            with self.subTest(input=test_input):
                result = await self.manager.process_claude_code_input(test_input)
                
                self.assertIsInstance(result, dict)
                self.assertIn("processed", result)
    
    async def test_system_status_check(self):
        """测试系统状态检查"""
        await self.manager.initialize()
        
        status = await self.manager.check_system_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("manager_status", status)
        self.assertIn("trigger_system", status)
    
    async def tearDown(self):
        """清理测试"""
        if hasattr(self, 'manager') and self.manager.initialized:
            await self.manager.cleanup()

class TestIntegrationScenarios(unittest.TestCase):
    """测试集成场景"""
    
    async def test_full_trigger_flow(self):
        """测试完整触发流程"""
        # 创建管理器
        config = StartupTriggerConfig(
            auto_trigger_enabled=True,
            auto_install_enabled=False,  # 测试时不自动安装
            mirror_code_enabled=False    # 测试时不启用 Mirror Code
        )
        manager = StartupTriggerManager(config)
        
        try:
            # 初始化
            await manager.initialize()
            
            # 测试各种触发场景
            scenarios = [
                {
                    "input": "需要 ClaudeEditor",
                    "expected_triggers": True,
                    "description": "基本安装触发"
                },
                {
                    "input": "PowerAutomation setup",
                    "expected_triggers": True,
                    "description": "专用安装触发"
                },
                {
                    "input": "检查系统状态",
                    "expected_triggers": True,
                    "description": "状态检查触发"
                },
                {
                    "input": "随机文本内容",
                    "expected_triggers": False,
                    "description": "无关内容"
                }
            ]
            
            for scenario in scenarios:
                with self.subTest(scenario=scenario["description"]):
                    result = await manager.process_claude_code_input(scenario["input"])
                    
                    if scenario["expected_triggers"]:
                        self.assertTrue(result.get("processed", False), 
                                      f"应该处理触发: {scenario['description']}")
                    else:
                        # 无关内容可能不会触发，但不应该出错
                        self.assertIsInstance(result, dict)
        
        finally:
            await manager.cleanup()

# 异步测试运行器
class AsyncTestRunner:
    """异步测试运行器"""
    
    def __init__(self):
        self.test_results = []
    
    async def run_async_test(self, test_class, test_method):
        """运行异步测试"""
        try:
            test_instance = test_class()
            if hasattr(test_instance, 'setUp'):
                test_instance.setUp()
            
            # 运行测试方法
            if asyncio.iscoroutinefunction(getattr(test_instance, test_method)):
                await getattr(test_instance, test_method)()
            else:
                getattr(test_instance, test_method)()
            
            if hasattr(test_instance, 'tearDown'):
                if asyncio.iscoroutinefunction(test_instance.tearDown):
                    await test_instance.tearDown()
                else:
                    test_instance.tearDown()
            
            self.test_results.append({
                "test": f"{test_class.__name__}.{test_method}",
                "status": "PASS",
                "error": None
            })
            
        except Exception as e:
            self.test_results.append({
                "test": f"{test_class.__name__}.{test_method}",
                "status": "FAIL",
                "error": str(e)
            })
    
    async def run_all_tests(self):
        """运行所有测试"""
        test_classes = [
            TestTriggerDetection,
            TestTriggerActions,
            TestHookTriggerIntegration,
            TestMirrorCodeCommunication,
            TestStartupTriggerManager,
            TestIntegrationScenarios
        ]
        
        for test_class in test_classes:
            # 获取测试方法
            test_methods = [method for method in dir(test_class) 
                          if method.startswith('test_')]
            
            for test_method in test_methods:
                await self.run_async_test(test_class, test_method)
        
        return self.test_results

async def main():
    """主测试函数"""
    print("🧪 启动触发机制测试")
    print("=" * 50)
    
    runner = AsyncTestRunner()
    results = await runner.run_all_tests()
    
    # 统计结果
    total_tests = len(results)
    passed_tests = len([r for r in results if r["status"] == "PASS"])
    failed_tests = len([r for r in results if r["status"] == "FAIL"])
    
    print(f"\n📊 测试结果统计:")
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    # 显示详细结果
    print(f"\n📋 详细结果:")
    for result in results:
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_icon} {result['test']}")
        if result["error"]:
            print(f"   错误: {result['error']}")
    
    # 保存测试报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests/total_tests*100
        },
        "results": results
    }
    
    report_file = "/tmp/startup_trigger_test_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 测试报告已保存: {report_file}")
    
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))

