#!/usr/bin/env python3
"""
修復 MCP 架構，保持統一標準
基於現有 core/mcp_components 架構，最小化變更
"""

import asyncio
import sys
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent / "core"))

async def test_mcp_architecture():
    """測試 MCP 架構的完整性"""
    print("🔧 測試 MCP 架構完整性")
    
    # 測試核心 MCP 組件
    mcp_components = [
        ("ClaudeRouterMCP", "claude_router_mcp"),
        ("CommandMCP", "command_mcp"), 
        ("MemoryRAGMCP", "memory_rag_mcp"),
        ("K2ChatMCP", "k2_chat_mcp"),
        ("MemberSystemMCP", "member_system_mcp"),
        ("DataCollectionMCP", "data_collection_mcp")
    ]
    
    working_components = []
    failed_components = []
    
    for component_name, module_name in mcp_components:
        try:
            print(f"\n📋 測試 {component_name}...")
            
            # 動態導入
            module = __import__(f"mcp_components.{module_name}", fromlist=[component_name])
            component_class = getattr(module, component_name)
            
            # 創建實例
            instance = component_class()
            
            # 測試基本方法
            if hasattr(instance, 'initialize'):
                init_result = await instance.initialize()
                print(f"  ✅ 初始化: {init_result.get('status', 'unknown')}")
            
            if hasattr(instance, 'get_capabilities'):
                capabilities = instance.get_capabilities()
                print(f"  ✅ 能力: {len(capabilities)} 個")
                
            if hasattr(instance, 'call_mcp'):
                # 測試 ping 方法
                ping_result = await instance.call_mcp("ping", {})
                print(f"  ✅ 通信: {ping_result.get('status', 'unknown')}")
            
            working_components.append(component_name)
            print(f"  ✅ {component_name} 工作正常")
            
        except Exception as e:
            failed_components.append((component_name, str(e)))
            print(f"  ❌ {component_name} 失敗: {str(e)[:80]}...")
    
    return working_components, failed_components

async def test_mcp_integration():
    """測試 MCP 組件間集成"""
    print("\n🔗 測試 MCP 組件間集成")
    
    try:
        # 導入可用組件
        from mcp_components.claude_router_mcp import ClaudeRouterMCP
        from mcp_components.command_mcp import CommandMCP
        from mcp_components.k2_chat_mcp import K2ChatMCP
        
        # 創建組件實例
        claude_router = ClaudeRouterMCP()
        command_mcp = CommandMCP()
        k2_chat = K2ChatMCP()
        
        # 初始化所有組件
        await claude_router.initialize()
        await command_mcp.initialize()
        await k2_chat.initialize()
        
        print("  ✅ 所有組件初始化成功")
        
        # 測試組件間通信
        print("\n📡 測試組件間通信...")
        
        # 1. Command MCP 接收 Claude Code Tool 命令
        command_result = await command_mcp.call_mcp("process_claude_code_command", {
            "command": "/read",
            "args": ["test.py"]
        })
        print(f"  ✅ 命令處理: {command_result.get('status', 'unknown')}")
        
        # 2. Claude Router 路由到 K2
        route_result = await claude_router.call_mcp("route_request", {
            "message": "請讀取 test.py 文件",
            "model": "claude-3-sonnet"
        })
        print(f"  ✅ 請求路由: {route_result.get('status', 'unknown')}")
        
        # 3. K2 Chat 處理請求
        k2_result = await k2_chat.call_mcp("chat", {
            "message": "請讀取 test.py 文件"
        })
        print(f"  ✅ K2 處理: {k2_result.get('success', False)}")
        
        # 測試統計功能
        stats_result = await k2_chat.call_mcp("get_stats", {})
        print(f"  ✅ 統計功能: {stats_result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 集成測試失敗: {e}")
        return False

async def test_mcp_performance():
    """測試 MCP 組件性能"""
    print("\n⚡ 測試 MCP 組件性能")
    
    try:
        from mcp_components.k2_chat_mcp import K2ChatMCP
        
        k2_chat = K2ChatMCP()
        await k2_chat.initialize()
        
        # 測試並發請求
        print("  📊 測試並發性能...")
        
        import time
        start_time = time.time()
        
        # 並發 5 個請求
        tasks = []
        for i in range(5):
            task = k2_chat.call_mcp("chat", {
                "message": f"測試並發請求 {i+1}"
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        successful = sum(1 for r in results if r.get('success', False))
        total_time = end_time - start_time
        
        print(f"  ✅ 並發測試: {successful}/5 成功")
        print(f"  ⏱️  總耗時: {total_time:.2f}s")
        print(f"  📈 平均響應: {total_time/5:.2f}s/請求")
        
        return total_time < 3.0  # 期望 3 秒內完成
        
    except Exception as e:
        print(f"  ❌ 性能測試失敗: {e}")
        return False

async def generate_mcp_report():
    """生成 MCP 架構報告"""
    print("\n📊 生成 MCP 架構報告")
    
    # 執行所有測試
    working_components, failed_components = await test_mcp_architecture()
    integration_success = await test_mcp_integration()
    performance_good = await test_mcp_performance()
    
    print("\n" + "="*60)
    print("📋 PowerAutomation MCP 架構報告")
    print("="*60)
    
    # 組件狀態
    print(f"\n🔧 組件狀態:")
    print(f"  ✅ 正常工作: {len(working_components)} 個")
    for comp in working_components:
        print(f"     - {comp}")
    
    if failed_components:
        print(f"  ❌ 需要修復: {len(failed_components)} 個")
        for comp, error in failed_components:
            print(f"     - {comp}: {error[:50]}...")
    
    # 集成狀態
    print(f"\n🔗 集成狀態:")
    print(f"  {'✅ 通過' if integration_success else '❌ 失敗'}")
    
    # 性能狀態
    print(f"\n⚡ 性能狀態:")
    print(f"  {'✅ 良好' if performance_good else '❌ 需要優化'}")
    
    # 總體評估
    total_score = len(working_components) * 2 + (1 if integration_success else 0) + (1 if performance_good else 0)
    max_score = 12 + 1 + 1  # 6個組件*2 + 集成 + 性能
    
    print(f"\n🎯 總體評估:")
    print(f"  得分: {total_score}/{max_score}")
    print(f"  評級: {'優秀' if total_score >= 10 else '良好' if total_score >= 7 else '需要改進'}")
    
    # 建議
    print(f"\n💡 建議:")
    if len(working_components) >= 4:
        print("  ✅ 核心功能已就緒，可以進行下一步開發")
    else:
        print("  ⚠️  需要修復更多組件才能正常使用")
    
    if integration_success:
        print("  ✅ 組件間通信正常，架構設計正確")
    else:
        print("  ⚠️  需要修復組件間通信問題")
    
    if performance_good:
        print("  ✅ 性能符合預期，可以處理並發請求")
    else:
        print("  ⚠️  需要優化性能或調整並發策略")
    
    return {
        "working_components": working_components,
        "failed_components": failed_components,
        "integration_success": integration_success,
        "performance_good": performance_good,
        "total_score": total_score,
        "max_score": max_score
    }

async def main():
    """主函數"""
    print("🚀 PowerAutomation MCP 架構修復與測試")
    print("沿用 core/mcp_components 架構，最小化變更")
    print("="*60)
    
    # 生成完整報告
    report = await generate_mcp_report()
    
    # 根據報告決定下一步
    if report["total_score"] >= 10:
        print("\n🎉 MCP 架構狀態良好！")
        print("✅ 可以繼續進行功能驗證和部署")
        print("✅ 建議：開始驗證 Claude Code Tool 透明切換")
    elif report["total_score"] >= 7:
        print("\n⚠️  MCP 架構基本可用，但需要一些修復")
        print("🔧 建議：修復失敗的組件，然後進行功能驗證")
    else:
        print("\n❌ MCP 架構需要重要修復")
        print("🔧 建議：優先修復核心組件，然後重新測試")
    
    print(f"\n📊 最終得分: {report['total_score']}/{report['max_score']}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())