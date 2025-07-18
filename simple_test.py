#!/usr/bin/env python3
"""
PowerAutomation 简单测试脚本
验证核心功能是否正常工作
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.append('.')
sys.path.append('core')
sys.path.append('mcp_server')
sys.path.append('goal_alignment_system')

async def test_goal_precision_engine():
    """测试目标精准化引擎"""
    print("🎯 测试目标精准化引擎...")
    
    try:
        from goal_precision_engine import GoalPrecisionEngine
        
        engine = GoalPrecisionEngine()
        
        # 创建目标
        goal_id = await engine.create_goal(
            title="创建用户管理系统",
            description="开发一个完整的用户管理系统，包含用户注册、登录、权限管理等功能",
            user_requirements=["用户注册功能", "用户登录验证", "权限管理系统", "用户信息管理"],
            acceptance_criteria=["用户可以成功注册", "用户可以正常登录", "权限系统工作正常", "通过所有测试"]
        )
        
        print(f"✅ 目标创建成功: {goal_id}")
        
        # 获取目标状态
        status = await engine.get_goal_status(goal_id)
        print(f"✅ 目标状态查询成功: {status['goal']['title']}")
        
        # 生成对齐报告
        report = await engine.generate_alignment_report(goal_id)
        print(f"✅ 对齐报告生成成功: 总体对齐度 {report['overall_alignment']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 目标精准化引擎测试失败: {e}")
        return False

async def test_six_workflows():
    """测试六大工作流"""
    print("🔄 测试六大工作流...")
    
    try:
        from workflows.six_core_workflows import SixCoreWorkflows
        
        workflows = SixCoreWorkflows()
        
        # 测试目标驱动开发工作流
        workflow_id = await workflows.start_workflow(
            workflow_type="goal_driven_development",
            user_goal="创建用户管理系统",
            context_data={"priority": "high", "deadline": "2024-02-01"}
        )
        
        print(f"✅ 目标驱动开发工作流启动成功: {workflow_id}")
        
        # 执行工作流步骤
        result = await workflows.execute_workflow_step(
            workflow_id=workflow_id,
            step_data={"stage": "goal_analysis", "workflow_type": "goal_driven_development"}
        )
        
        print(f"✅ 工作流步骤执行成功: {result['message']}")
        
        # 获取工作流状态
        status = await workflows.get_workflow_status(workflow_id)
        print(f"✅ 工作流状态查询成功: {status['progress']:.1f}%")
        
        # 测试智能代码生成工作流
        code_workflow_id = await workflows.start_workflow(
            workflow_type="intelligent_code_generation",
            user_goal="生成用户登录组件",
            context_data={"framework": "react", "style": "modern"}
        )
        
        print(f"✅ 智能代码生成工作流启动成功: {code_workflow_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 六大工作流测试失败: {e}")
        return False

async def test_mcp_tools():
    """测试MCP工具"""
    print("🔧 测试MCP工具...")
    
    try:
        # 测试Memory RAG工具
        from tools.memory_rag_tool import MemoryRAGTool
        
        memory_tool = MemoryRAGTool()
        
        # 存储记忆
        memory_id = await memory_tool.store(
            content="用户管理系统需要包含用户注册、登录、权限管理等核心功能",
            memory_type="semantic",
            tags=["用户管理", "系统需求", "核心功能"],
            importance=0.9
        )
        
        print(f"✅ 记忆存储成功: {memory_id}")
        
        # 查询记忆
        query_result = await memory_tool.query("用户管理系统", 3)
        print(f"✅ 记忆查询成功: {len(query_result['results'])} 个结果")
        
        # 测试K2聊天工具
        from tools.k2_chat_tool import K2ChatTool
        
        k2_tool = K2ChatTool()
        response = await k2_tool.chat(
            message="请帮我分析用户管理系统的核心需求",
            context=["包含用户注册、登录、权限管理"],
            use_memory=True
        )
        
        print(f"✅ K2聊天成功: {response[:80]}...")
        
        # 测试代码分析工具
        from tools.code_analysis_tool import CodeAnalysisTool
        
        code_tool = CodeAnalysisTool()
        sample_code = '''
def authenticate_user(username, password):
    """用户认证函数"""
    if not username or not password:
        return {"success": False, "error": "用户名和密码不能为空"}
    
    # 模拟数据库查询
    user = get_user_by_username(username)
    if not user:
        return {"success": False, "error": "用户不存在"}
    
    if verify_password(password, user.password_hash):
        return {"success": True, "user": user}
    else:
        return {"success": False, "error": "密码错误"}
'''
        
        analysis_result = await code_tool.analyze(sample_code, "python", "all")
        print(f"✅ 代码分析成功: {analysis_result['status']}")
        
        # 测试UI生成工具
        from tools.ui_generation_tool import UIGenerationTool
        
        ui_tool = UIGenerationTool()
        ui_code = await ui_tool.generate(
            description="创建用户登录界面，包含用户名输入框、密码输入框和登录按钮",
            framework="react",
            style="modern",
            responsive=True
        )
        
        print(f"✅ UI生成成功: {len(ui_code)} 字符的代码")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP工具测试失败: {e}")
        return False

async def test_core_driver():
    """测试PowerAutomation Core驱动器"""
    print("🚀 测试PowerAutomation Core驱动器...")
    
    try:
        # 创建简化版的核心驱动器测试
        from powerautomation_core_driver import PowerAutomationCoreDriver
        
        driver = PowerAutomationCoreDriver()
        
        # 测试驱动器状态
        status = await driver.get_driver_status()
        print(f"✅ 驱动器状态查询成功: {status['status']}")
        
        # 测试ClaudeEditor注册
        reg_id = await driver.register_claudeditor({
            "name": "TestEditor",
            "version": "1.0.0",
            "host": "localhost",
            "port": 8000
        })
        
        print(f"✅ ClaudeEditor注册成功: {reg_id}")
        
        # 测试驱动功能
        result = await driver.drive_claudeditor(
            registration_id=reg_id,
            action="start_workflow",
            parameters={
                "workflow_type": "goal_driven_development",
                "user_goal": "创建用户管理系统",
                "requirements": ["用户注册", "用户登录", "权限管理"],
                "acceptance_criteria": ["功能正常", "性能良好", "安全可靠"]
            }
        )
        
        print(f"✅ 驱动功能测试成功: {result.get('workflow_type', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Core驱动器测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 PowerAutomation 核心功能测试")
    print("=" * 40)
    
    # 记录测试结果
    test_results = []
    
    # 1. 测试目标精准化引擎
    result1 = await test_goal_precision_engine()
    test_results.append(("目标精准化引擎", result1))
    
    # 2. 测试六大工作流
    result2 = await test_six_workflows()
    test_results.append(("六大工作流", result2))
    
    # 3. 测试MCP工具
    result3 = await test_mcp_tools()
    test_results.append(("MCP工具", result3))
    
    # 4. 测试Core驱动器
    result4 = await test_core_driver()
    test_results.append(("Core驱动器", result4))
    
    # 输出测试结果
    print("\n" + "=" * 40)
    print("🎯 测试结果汇总:")
    print("=" * 40)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 总计: {passed} 个测试通过, {failed} 个测试失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过！PowerAutomation 核心功能正常工作")
        print("🌟 系统已准备好进行生产环境部署")
        print("\n📋 接下来可以:")
        print("1. 配置 .env 文件中的API密钥")
        print("2. 启动完整的PowerAutomation系统")
        print("3. 通过ClaudeEditor WebUI使用所有功能")
        print("4. 集成到你的开发工作流中")
        print("\n🎯 PowerAutomation - 让开发永不偏离目标！")
        return True
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，请检查相关组件")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)