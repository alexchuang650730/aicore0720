#!/usr/bin/env python3
"""
PowerAutomation 演示启动脚本
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

async def demo_powerautomation():
    """演示PowerAutomation核心功能"""
    print("🚀 PowerAutomation 演示开始...")
    
    try:
        # 1. 测试目标精准化引擎
        print("🎯 测试目标精准化引擎...")
        from goal_precision_engine import GoalPrecisionEngine
        
        goal_engine = GoalPrecisionEngine()
        goal_id = await goal_engine.create_goal(
            title="创建用户管理系统",
            description="开发一个完整的用户管理系统",
            user_requirements=["用户注册", "用户登录", "权限管理"],
            acceptance_criteria=["功能正常", "性能良好", "安全可靠"]
        )
        
        print(f"✅ 目标创建成功: {goal_id}")
        
        # 2. 测试六大工作流
        print("🔄 测试六大工作流...")
        from workflows.six_core_workflows import SixCoreWorkflows
        
        workflows = SixCoreWorkflows()
        workflow_id = await workflows.start_workflow(
            workflow_type="goal_driven_development",
            user_goal="创建用户管理系统",
            context_data={"priority": "high"}
        )
        
        print(f"✅ 工作流启动成功: {workflow_id}")
        
        # 执行工作流步骤
        result = await workflows.execute_workflow_step(
            workflow_id=workflow_id,
            step_data={"stage": "goal_analysis", "workflow_type": "goal_driven_development"}
        )
        
        print(f"✅ 工作流执行成功: {result['message']}")
        
        # 3. 测试Memory RAG工具
        print("🧠 测试Memory RAG工具...")
        from tools.memory_rag_tool import MemoryRAGTool
        
        memory_tool = MemoryRAGTool()
        memory_id = await memory_tool.store(
            content="用户管理系统需要包含注册、登录、权限管理功能",
            memory_type="semantic",
            tags=["用户管理", "需求分析"],
            importance=0.8
        )
        
        print(f"✅ 记忆存储成功: {memory_id}")
        
        # 查询记忆
        query_result = await memory_tool.query("用户管理系统", 3)
        print(f"✅ 记忆查询成功: {len(query_result['results'])} 个结果")
        
        # 4. 测试K2聊天工具
        print("🤖 测试K2聊天工具...")
        from tools.k2_chat_tool import K2ChatTool
        
        k2_tool = K2ChatTool()
        response = await k2_tool.chat(
            message="请帮我设计用户管理系统的架构",
            context=["需要包含用户注册、登录、权限管理"],
            use_memory=True
        )
        
        print(f"✅ K2聊天成功: {response[:100]}...")
        
        # 5. 测试代码分析工具
        print("🔍 测试代码分析工具...")
        from tools.code_analysis_tool import CodeAnalysisTool
        
        code_tool = CodeAnalysisTool()
        sample_code = '''
def user_login(username, password):
    if not username or not password:
        return False
    # 简单的登录逻辑
    return username == "admin" and password == "password"
'''
        
        analysis_result = await code_tool.analyze(sample_code, "python", "all")
        print(f"✅ 代码分析成功: {analysis_result['status']}")
        
        # 6. 测试UI生成工具
        print("🎨 测试UI生成工具...")
        from tools.ui_generation_tool import UIGenerationTool
        
        ui_tool = UIGenerationTool()
        ui_code = await ui_tool.generate(
            description="创建用户登录界面",
            framework="react",
            style="modern",
            responsive=True
        )
        
        print(f"✅ UI生成成功: {len(ui_code)} 字符的代码")
        
        # 7. 测试PowerAutomation Core驱动器
        print("🚀 测试PowerAutomation Core驱动器...")
        from powerautomation_core_driver import PowerAutomationCoreDriver
        
        core_driver = PowerAutomationCoreDriver()
        init_result = await core_driver.initialize()
        print(f"✅ Core驱动器初始化成功: {init_result['status']}")
        
        # 注册ClaudeEditor
        reg_id = await core_driver.register_claudeditor({
            "name": "DemoEditor",
            "version": "1.0.0",
            "host": "localhost",
            "port": 8000
        })
        
        print(f"✅ ClaudeEditor注册成功: {reg_id}")
        
        # 驱动工作流
        workflow_result = await core_driver.drive_claudeditor(
            registration_id=reg_id,
            action="start_workflow",
            parameters={
                "workflow_type": "goal_driven_development",
                "user_goal": "创建用户管理系统",
                "requirements": ["用户注册", "用户登录", "权限管理"],
                "acceptance_criteria": ["功能正常", "性能良好", "安全可靠"]
            }
        )
        
        print(f"✅ 工作流驱动成功: {workflow_result['workflow_type']}")
        
        # 关闭驱动器
        await core_driver.shutdown()
        
        print("🎉 PowerAutomation 演示完成！")
        print("✅ 所有核心功能测试通过")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(demo_powerautomation())
    if success:
        print("\n🎯 PowerAutomation 准备就绪！")
        print("📚 查看 README.md 了解更多使用方法")
        print("🌐 访问 https://github.com/alexchuang650730/aicore0718 获取最新版本")
        print("💡 配置 .env 文件中的API密钥以启用完整功能")
    else:
        print("\n❌ 演示失败，请检查错误信息")
        sys.exit(1)
