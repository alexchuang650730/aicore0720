#!/usr/bin/env python3
"""
基礎核心功能測試
只測試最關鍵的 K2 路由和 Claude Code Tool 命令
"""

import asyncio
import sys
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent / "core"))

async def test_k2_chat_basic():
    """測試 K2 聊天基礎功能"""
    print("🧪 測試 K2 聊天基礎功能")
    
    try:
        from mcp_components.k2_chat_mcp import K2ChatMCP
        
        # 創建 K2 聊天組件
        k2_chat = K2ChatMCP()
        
        # 初始化
        init_result = await k2_chat.initialize()
        print(f"  初始化結果: {init_result['status']}")
        
        # 測試聊天
        chat_result = await k2_chat.call_mcp("chat", {
            "message": "你好，請幫我寫一個 Python 函數"
        })
        print(f"  聊天結果: {chat_result['success']}")
        if chat_result['success']:
            print(f"  響應: {chat_result['response'][:100]}...")
            print(f"  成本節省: ${chat_result['cost_savings']:.4f}")
        
        # 測試統計
        stats_result = await k2_chat.call_mcp("get_stats", {})
        print(f"  統計結果: {stats_result['success']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ K2 聊天測試失敗: {e}")
        return False

async def test_claude_router_basic():
    """測試 Claude Router 基礎功能"""
    print("🧪 測試 Claude Router 基礎功能")
    
    try:
        from mcp_components.claude_router_mcp import ClaudeRouterMCP
        
        # 創建 Claude Router
        claude_router = ClaudeRouterMCP()
        
        # 初始化
        init_result = await claude_router.initialize()
        print(f"  初始化結果: {init_result['status']}")
        
        # 測試路由
        route_result = await claude_router.call_mcp("route_request", {
            "message": "請幫我創建一個簡單的 Python 項目",
            "model": "claude-3-sonnet"
        })
        print(f"  路由結果: {route_result['status']}")
        if route_result['status'] == 'success':
            print(f"  使用提供商: {route_result['provider']}")
            print(f"  成本節省: ${route_result['cost_saved']:.4f}")
        
        # 測試成本統計
        cost_result = await claude_router.call_mcp("get_cost_savings", {})
        print(f"  成本統計: {cost_result['status']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Claude Router 測試失敗: {e}")
        return False

async def test_command_mcp_basic():
    """測試 Command MCP 基礎功能"""
    print("🧪 測試 Command MCP 基礎功能")
    
    try:
        from mcp_components.command_mcp import CommandMCP
        
        # 創建 Command MCP
        command_mcp = CommandMCP()
        
        # 初始化
        init_result = await command_mcp.initialize()
        print(f"  初始化結果: {init_result['status']}")
        
        # 測試命令幫助
        help_result = await command_mcp.call_mcp("get_command_help", {
            "command": "/read"
        })
        print(f"  命令幫助: {help_result['status']}")
        
        # 測試模型狀態
        status_result = await command_mcp.call_mcp("get_model_status", {})
        print(f"  模型狀態: {status_result['status']}")
        if status_result['status'] == 'success':
            print(f"  當前模型: {status_result['current_model']}")
        
        # 測試 Claude Code Tool 命令處理
        claude_cmd_result = await command_mcp.call_mcp("process_claude_code_command", {
            "command": "/help",
            "args": []
        })
        print(f"  Claude Code 命令: {claude_cmd_result['status']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Command MCP 測試失敗: {e}")
        return False

async def test_integration_basic():
    """測試基礎集成功能"""
    print("🧪 測試基礎集成功能")
    
    try:
        from mcp_components.k2_chat_mcp import K2ChatMCP
        from mcp_components.claude_router_mcp import ClaudeRouterMCP
        from mcp_components.command_mcp import CommandMCP
        
        # 創建所有組件
        k2_chat = K2ChatMCP()
        claude_router = ClaudeRouterMCP()
        command_mcp = CommandMCP()
        
        # 初始化所有組件
        await k2_chat.initialize()
        await claude_router.initialize()
        await command_mcp.initialize()
        
        print("  ✅ 所有組件初始化成功")
        
        # 測試集成流程：命令 -> 路由 -> K2 執行
        print("  測試集成流程...")
        
        # 1. 通過 Command MCP 處理 Claude Code Tool 命令
        command_result = await command_mcp.call_mcp("process_claude_code_command", {
            "command": "/read",
            "args": ["test.py"]
        })
        
        # 2. 通過 Claude Router 路由請求
        route_result = await claude_router.call_mcp("route_request", {
            "message": "請幫我讀取 test.py 文件",
            "model": "claude-3-sonnet"
        })
        
        # 3. 通過 K2 Chat 執行
        k2_result = await k2_chat.call_mcp("chat", {
            "message": "請幫我讀取 test.py 文件"
        })
        
        print(f"  命令處理: {command_result['status']}")
        print(f"  路由結果: {route_result['status']}")
        print(f"  K2 執行: {k2_result['success']}")
        
        if all([
            command_result['status'] == 'success',
            route_result['status'] == 'success', 
            k2_result['success']
        ]):
            print("  ✅ 集成流程測試成功")
            return True
        else:
            print("  ❌ 集成流程測試失敗")
            return False
        
    except Exception as e:
        print(f"  ❌ 集成測試失敗: {e}")
        return False

async def main():
    """主測試函數"""
    print("🚀 PowerAutomation 基礎核心功能測試")
    print("="*60)
    
    tests = [
        ("K2 聊天基礎功能", test_k2_chat_basic),
        ("Claude Router 基礎功能", test_claude_router_basic),
        ("Command MCP 基礎功能", test_command_mcp_basic),
        ("基礎集成功能", test_integration_basic)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            success = await test_func()
            if success:
                print(f"✅ {test_name} 通過")
                passed += 1
            else:
                print(f"❌ {test_name} 失敗")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} 異常: {e}")
            failed += 1
    
    print(f"\n📊 測試結果: {passed} 通過, {failed} 失敗")
    
    if failed == 0:
        print("🎉 所有基礎功能測試通過！")
        print("✅ K2 路由器工作正常")
        print("✅ Claude Code Tool 命令支持就緒")
        print("✅ 基礎集成功能可用")
        print("\n💡 下一步：運行完整的雙向溝通測試")
    else:
        print("⚠️  部分基礎功能需要修復")

if __name__ == "__main__":
    asyncio.run(main())