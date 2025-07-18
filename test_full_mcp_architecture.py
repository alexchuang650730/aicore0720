#!/usr/bin/env python3
"""
測試完整的MCP架構
"""

import asyncio
import time
import sys
sys.path.append('.')

from core.mcp_manager import MCPManager

async def test_full_mcp_flow():
    """測試完整的MCP流程"""
    
    print("🚀 測試完整MCP架構")
    print("="*60)
    
    # 初始化MCP管理器
    manager = MCPManager()
    await manager.initialize()
    
    # 測試查詢
    test_query = "如何優化Python代碼性能？"
    
    print(f"\n📝 測試查詢: {test_query}")
    print("-"*50)
    
    # 1. Router決策
    print("\n1️⃣ Router MCP - 路由決策")
    route_result = await manager.call_mcp(
        "router_mcp",
        "route",
        {
            "user_input": test_query,
            "priority": "balanced"
        }
    )
    
    if route_result.get('status') == 'success':
        decision = route_result['routing_decision']
        print(f"   選擇: {decision['provider']}")
        print(f"   理由: {decision['reasoning']}")
        print(f"   預估延遲: {decision['estimated_latency_ms']}ms")
    
    # 2. Cache檢查
    print("\n2️⃣ Cache MCP - 緩存檢查")
    cache_result = await manager.call_mcp(
        "cache_mcp",
        "get",
        {"key": test_query}
    )
    
    if cache_result.get('hit'):
        print("   ✅ 緩存命中！")
        return cache_result['value']
    else:
        print("   ❌ 緩存未命中")
    
    # 3. K2 Chat
    print("\n3️⃣ K2 Chat MCP - 生成響應")
    
    # 根據路由決策選擇
    use_groq = decision['provider'] == 'groq' if 'decision' in locals() else False
    
    chat_result = await manager.call_mcp(
        "k2_chat_mcp",
        "chat",
        {
            "messages": [{"role": "user", "content": test_query}],
            "use_groq": use_groq
        }
    )
    
    if chat_result.get('status') == 'success':
        print(f"   ✅ 響應成功")
        print(f"   Provider: {chat_result.get('provider')}")
        print(f"   延遲: {chat_result.get('latency_ms', 0):.0f}ms")
        k2_response = chat_result['response']
    else:
        print("   ❌ 響應失敗")
        return
    
    # 4. RAG增強
    print("\n4️⃣ Memory RAG MCP - 增強優化")
    
    # 獲取對齊上下文
    rag_context = await manager.call_mcp(
        "memory_rag_mcp",
        "get_alignment_context",
        {"user_input": test_query}
    )
    
    # 優化提示詞
    optimized = await manager.call_mcp(
        "memory_rag_mcp",
        "optimize_k2_prompt",
        {
            "user_input": test_query,
            "original_prompt": k2_response[:100]
        }
    )
    
    if optimized.get('status') == 'success':
        print("   ✅ RAG增強成功")
    
    # 5. 緩存結果
    print("\n5️⃣ Cache MCP - 緩存結果")
    cache_set = await manager.call_mcp(
        "cache_mcp",
        "set",
        {
            "key": test_query,
            "value": k2_response,
            "ttl": 3600
        }
    )
    
    if cache_set.get('status') == 'success':
        print("   ✅ 已緩存響應")
    
    # 顯示最終結果
    print("\n📊 最終結果:")
    print("-"*50)
    print(f"響應預覽: {k2_response[:200]}...")
    
    # 獲取統計
    print("\n📈 系統統計:")
    
    # Router統計
    router_stats = await manager.call_mcp("router_mcp", "get_routing_stats", {})
    if router_stats.get('status') == 'success':
        stats = router_stats['stats']
        print(f"   路由分佈: K2={stats['distribution']['k2']}, Groq={stats['distribution']['groq']}")
    
    # Cache統計
    cache_stats = await manager.call_mcp("cache_mcp", "get_stats", {})
    if cache_stats.get('status') == 'success':
        stats = cache_stats['stats']
        print(f"   緩存命中率: {stats['hit_rate']}")
    
    # K2統計
    k2_stats = await manager.call_mcp("k2_chat_mcp", "get_stats", {})
    if k2_stats.get('status') == 'success':
        stats = k2_stats['stats']
        print(f"   平均延遲: {stats['avg_latency_ms']:.0f}ms")
    
    print("\n✅ 完整MCP流程測試完成！")

if __name__ == "__main__":
    asyncio.run(test_full_mcp_flow())
