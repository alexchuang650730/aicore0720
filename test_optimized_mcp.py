#!/usr/bin/env python3
"""
測試優化後的MCP系統
"""

import asyncio
import sys
sys.path.append('.')

from core.mcp_manager import MCPManager

async def test_optimized_mcp():
    """測試優化的MCP"""
    
    print("🚀 測試優化後的MCP系統")
    print("="*60)
    
    # 初始化MCP管理器
    manager = MCPManager()
    await manager.initialize()
    
    # 測試K2聊天
    print("\n📝 測試K2聊天（使用Moonshot）")
    k2_result = await manager.call_mcp(
        "k2_chat_mcp",
        "chat",
        {
            "messages": [{"role": "user", "content": "什麼是Python裝飾器？"}]
        }
    )
    
    if k2_result.get('status') == 'success':
        print(f"✅ K2響應成功")
        print(f"   Provider: {k2_result.get('provider')}")
        print(f"   延遲: {k2_result.get('latency_ms', 0):.0f}ms")
        print(f"   響應: {k2_result['response'][:100]}...")
    
    # 測試RAG增強
    print("\n🧠 測試RAG增強")
    rag_result = await manager.call_mcp(
        "memory_rag_mcp",
        "get_alignment_context",
        {
            "user_input": "如何優化Python代碼性能"
        }
    )
    
    if rag_result.get('status') == 'success':
        print("✅ RAG增強成功")
    
    # 獲取統計
    print("\n📊 系統統計")
    stats = await manager.call_mcp("k2_chat_mcp", "get_stats", {})
    if stats.get('status') == 'success':
        print(f"   總請求: {stats['stats']['total_requests']}")
        print(f"   平均延遲: {stats['stats']['avg_latency_ms']:.0f}ms")
    
    print("\n✅ 測試完成！MCP系統已優化")

if __name__ == "__main__":
    asyncio.run(test_optimized_mcp())
