#!/bin/bash

# PowerAutomation 快速启动脚本
# 适用于本地开发和测试

set -e

echo "🚀 PowerAutomation 快速启动..."

# 检查当前目录
if [[ ! -f "setup.py" ]]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 创建虚拟环境
create_venv() {
    echo "🔧 创建虚拟环境..."
    
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        echo "✅ 虚拟环境创建完成"
    else
        echo "✅ 虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
}

# 安装依赖
install_dependencies() {
    echo "📦 安装依赖..."
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装基础依赖
    pip install fastapi uvicorn pydantic websockets httpx aiofiles numpy
    
    # 尝试安装可选依赖
    pip install sentence-transformers 2>/dev/null || echo "⚠️ sentence-transformers 跳过"
    pip install faiss-cpu 2>/dev/null || echo "⚠️ faiss-cpu 跳过"
    
    echo "✅ 依赖安装完成"
}

# 配置环境变量
setup_env() {
    echo "⚙️ 配置环境变量..."
    
    if [[ ! -f ".env" ]]; then
        cat > .env << 'EOF'
# PowerAutomation 环境变量
HOST=localhost
PORT=8000
WEBSOCKET_PORT=8001
MCP_SERVER_PORT=8765
LOG_LEVEL=INFO
DEBUG=true
CLAUDE_API_KEY=your_claude_api_key
KIMI_API_KEY=your_kimi_api_key
OPENAI_API_KEY=your_openai_api_key
EOF
        echo "✅ .env 文件已创建"
    else
        echo "✅ .env 文件已存在"
    fi
}

# 创建必要目录
create_directories() {
    echo "📁 创建必要目录..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p uploads
    mkdir -p downloads
    mkdir -p temp
    
    echo "✅ 目录创建完成"
}

# 初始化数据库
init_database() {
    echo "🗄️ 初始化数据库..."
    
    python3 -c "
import sqlite3
import time

try:
    # 创建主数据库
    conn = sqlite3.connect('powerautomation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT,
            created_at REAL,
            updated_at REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            status TEXT,
            started_at REAL,
            completed_at REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id TEXT PRIMARY KEY,
            command TEXT NOT NULL,
            result TEXT,
            executed_at REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # 创建内存数据库
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            memory_type TEXT,
            created_at REAL,
            importance REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print('✅ 数据库初始化完成')
    
except Exception as e:
    print(f'⚠️ 数据库初始化失败: {e}')
"
}

# 测试核心模块
test_core_modules() {
    echo "🧪 测试核心模块..."
    
    # 测试导入
    python3 -c "
import sys
import os
sys.path.append('.')

try:
    # 测试基础模块
    from pathlib import Path
    from typing import Dict, List, Any
    import asyncio
    import json
    import logging
    import time
    import uuid
    
    print('✅ 基础模块导入成功')
    
    # 测试MCP工具
    sys.path.append('mcp_server')
    from tools.memory_rag_tool import MemoryRAGTool
    from tools.k2_chat_tool import K2ChatTool
    from tools.code_analysis_tool import CodeAnalysisTool
    from tools.ui_generation_tool import UIGenerationTool
    from tools.workflow_automation_tool import WorkflowAutomationTool
    
    print('✅ MCP工具导入成功')
    
    # 测试核心组件
    sys.path.append('core')
    from workflows.six_core_workflows import SixCoreWorkflows
    from powerautomation_core_driver import PowerAutomationCoreDriver
    
    print('✅ 核心组件导入成功')
    
    # 测试目标精准化
    sys.path.append('goal_alignment_system')
    from goal_precision_engine import GoalPrecisionEngine
    
    print('✅ 目标精准化引擎导入成功')
    
    print('🎉 所有核心模块测试通过！')
    
except ImportError as e:
    print(f'❌ 模块导入失败: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ 测试失败: {e}')
    sys.exit(1)
"
}

# 创建启动脚本
create_startup_script() {
    echo "📝 创建启动脚本..."
    
    cat > start_demo.py << 'EOF'
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
EOF

    chmod +x start_demo.py
    echo "✅ 启动脚本创建完成"
}

# 运行演示
run_demo() {
    echo "🎬 运行PowerAutomation演示..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 运行演示
    python3 start_demo.py
}

# 主函数
main() {
    echo "🎯 PowerAutomation 快速启动程序"
    echo "================================"
    
    create_venv
    install_dependencies
    setup_env
    create_directories
    init_database
    test_core_modules
    create_startup_script
    run_demo
    
    echo ""
    echo "🎉 PowerAutomation 快速启动完成！"
    echo ""
    echo "📋 接下来可以："
    echo "1. 编辑 .env 文件，配置你的API密钥"
    echo "2. 运行 python3 start_demo.py 重新测试"
    echo "3. 查看 README.md 了解完整使用方法"
    echo "4. 访问 GitHub 仓库获取最新版本"
    echo ""
    echo "🎯 PowerAutomation - 让开发永不偏离目标！"
}

# 运行主函数
main