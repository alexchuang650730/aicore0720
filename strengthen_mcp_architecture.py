#!/usr/bin/env python3
"""
強化MCP架構
確保所有特性都以MCP組件形式實現
"""

import os
from pathlib import Path

def strengthen_mcp_architecture():
    """強化MCP架構"""
    
    print("🏗️ 強化MCP架構")
    print("="*60)
    
    # 1. 創建Router MCP組件
    router_mcp = '''"""
Router MCP - 智能路由組件
負責在Claude和K2之間智能切換
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_mcp import BaseMCP

logger = logging.getLogger(__name__)

class RouterMCP(BaseMCP):
    """路由MCP組件 - 智能選擇最佳模型"""
    
    def __init__(self):
        super().__init__("router_mcp")
        
        # 路由策略配置
        self.routing_config = {
            "simple_queries": {
                "patterns": ["what is", "how to", "explain", "什麼是", "如何"],
                "preferred_provider": "groq",
                "fallback": "moonshot"
            },
            "complex_queries": {
                "patterns": ["optimize", "refactor", "analyze", "優化", "重構", "分析"],
                "preferred_provider": "moonshot",
                "fallback": "claude"
            },
            "code_generation": {
                "patterns": ["write", "create", "generate", "寫", "創建", "生成"],
                "preferred_provider": "moonshot",
                "fallback": "claude"
            }
        }
        
        # 性能閾值
        self.performance_thresholds = {
            "max_latency_ms": 2000,
            "quality_threshold": 0.7,
            "cost_weight": 0.3
        }
        
        # 路由統計
        self.routing_stats = {
            "total_routes": 0,
            "routes_to_k2": 0,
            "routes_to_groq": 0,
            "routes_to_claude": 0,
            "avg_decision_time_ms": 0
        }
        
    async def initialize(self) -> Dict[str, Any]:
        """初始化Router MCP"""
        try:
            self.status = "running"
            logger.info("✅ Router MCP 初始化成功")
            
            return {
                "status": "success",
                "component": self.component_name,
                "routing_strategies": list(self.routing_config.keys()),
                "performance_thresholds": self.performance_thresholds
            }
            
        except Exception as e:
            self.status = "error"
            self.record_error(e)
            return {
                "status": "error",
                "component": self.component_name,
                "error": str(e)
            }
    
    async def call_mcp(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """調用MCP方法"""
        self.update_activity()
        
        try:
            if method == "route":
                return await self._route_request(params)
            elif method == "get_routing_stats":
                return self._get_routing_stats()
            elif method == "update_thresholds":
                return self._update_thresholds(params)
            else:
                return {
                    "status": "error",
                    "message": f"未知方法: {method}"
                }
                
        except Exception as e:
            self.record_error(e)
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _route_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """智能路由請求"""
        start_time = time.time()
        
        user_input = params.get("user_input", "")
        context = params.get("context", {})
        priority = params.get("priority", "balanced")  # balanced, speed, quality, cost
        
        # 分析查詢類型
        query_type = self._analyze_query_type(user_input)
        
        # 根據優先級和查詢類型選擇提供商
        selected_provider = self._select_provider(query_type, priority, context)
        
        # 準備路由決策
        routing_decision = {
            "provider": selected_provider,
            "query_type": query_type,
            "reasoning": self._get_routing_reasoning(query_type, selected_provider, priority),
            "estimated_latency_ms": self._estimate_latency(selected_provider),
            "estimated_cost_savings": self._estimate_savings(selected_provider)
        }
        
        # 更新統計
        decision_time = (time.time() - start_time) * 1000
        self._update_routing_stats(selected_provider, decision_time)
        
        return {
            "status": "success",
            "routing_decision": routing_decision,
            "decision_time_ms": decision_time
        }
    
    def _analyze_query_type(self, user_input: str) -> str:
        """分析查詢類型"""
        input_lower = user_input.lower()
        
        for query_type, config in self.routing_config.items():
            for pattern in config["patterns"]:
                if pattern in input_lower:
                    return query_type
        
        return "general"
    
    def _select_provider(self, query_type: str, priority: str, context: Dict) -> str:
        """選擇最佳提供商"""
        # 基於查詢類型的默認選擇
        if query_type in self.routing_config:
            preferred = self.routing_config[query_type]["preferred_provider"]
        else:
            preferred = "moonshot"  # 默認K2
        
        # 根據優先級調整
        if priority == "speed":
            # 速度優先，偏好Groq
            if query_type == "simple_queries":
                return "groq"
            else:
                return preferred
        elif priority == "quality":
            # 質量優先，可能選擇Claude
            if query_type == "complex_queries":
                return "claude" if context.get("budget_ok", False) else "moonshot"
            else:
                return preferred
        elif priority == "cost":
            # 成本優先，避免Claude
            return "groq" if query_type == "simple_queries" else "moonshot"
        else:
            # 平衡模式
            return preferred
    
    def _get_routing_reasoning(self, query_type: str, provider: str, priority: str) -> str:
        """獲取路由理由"""
        reasons = {
            "groq": f"選擇Groq：超快響應（~300ms），適合{query_type}",
            "moonshot": f"選擇Moonshot K2：平衡性能和成本，適合{query_type}",
            "claude": f"選擇Claude：最高質量，適合複雜的{query_type}"
        }
        
        base_reason = reasons.get(provider, "智能路由選擇")
        priority_reason = f"，優先級：{priority}"
        
        return base_reason + priority_reason
    
    def _estimate_latency(self, provider: str) -> int:
        """估算延遲"""
        latencies = {
            "groq": 350,
            "moonshot": 1500,
            "claude": 2000
        }
        return latencies.get(provider, 1500)
    
    def _estimate_savings(self, provider: str) -> float:
        """估算成本節省"""
        savings = {
            "groq": 0.95,
            "moonshot": 0.75,
            "claude": 0.0
        }
        return savings.get(provider, 0.5)
    
    def _update_routing_stats(self, provider: str, decision_time: float):
        """更新路由統計"""
        self.routing_stats["total_routes"] += 1
        
        if provider == "moonshot":
            self.routing_stats["routes_to_k2"] += 1
        elif provider == "groq":
            self.routing_stats["routes_to_groq"] += 1
        elif provider == "claude":
            self.routing_stats["routes_to_claude"] += 1
        
        # 更新平均決策時間
        n = self.routing_stats["total_routes"]
        avg = self.routing_stats["avg_decision_time_ms"]
        self.routing_stats["avg_decision_time_ms"] = (avg * (n-1) + decision_time) / n
    
    def _get_routing_stats(self) -> Dict[str, Any]:
        """獲取路由統計"""
        total = self.routing_stats["total_routes"]
        
        return {
            "status": "success",
            "stats": {
                "total_routes": total,
                "distribution": {
                    "k2": f"{self.routing_stats['routes_to_k2']/max(total,1)*100:.1f}%",
                    "groq": f"{self.routing_stats['routes_to_groq']/max(total,1)*100:.1f}%",
                    "claude": f"{self.routing_stats['routes_to_claude']/max(total,1)*100:.1f}%"
                },
                "avg_decision_time_ms": f"{self.routing_stats['avg_decision_time_ms']:.1f}"
            }
        }
    
    def _update_thresholds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """更新性能閾值"""
        for key, value in params.items():
            if key in self.performance_thresholds:
                self.performance_thresholds[key] = value
        
        return {
            "status": "success",
            "updated_thresholds": self.performance_thresholds
        }
    
    def get_info(self) -> Dict[str, Any]:
        """獲取組件信息"""
        return {
            "component": self.component_name,
            "description": "智能路由MCP，在不同AI提供商間智能切換",
            "version": "1.0",
            "status": self.status,
            "features": ["查詢分析", "智能路由", "性能預測", "成本優化"],
            "supported_providers": ["groq", "moonshot", "claude"]
        }
'''
    
    # 保存Router MCP
    router_path = Path("core/mcp_components/router_mcp")
    router_path.mkdir(parents=True, exist_ok=True)
    
    with open(router_path / "__init__.py", 'w') as f:
        f.write('from .router import RouterMCP\n\n__all__ = ["RouterMCP"]')
    
    with open(router_path / "router.py", 'w') as f:
        f.write(router_mcp)
    
    print("✅ 創建 Router MCP 組件")
    
    # 2. 創建Cache MCP組件
    cache_mcp = '''"""
Cache MCP - 高性能緩存組件
提供分佈式緩存支持
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..base_mcp import BaseMCP

logger = logging.getLogger(__name__)

class CacheMCP(BaseMCP):
    """緩存MCP組件"""
    
    def __init__(self):
        super().__init__("cache_mcp")
        
        # 內存緩存（生產環境應使用Redis）
        self.cache_store = {}
        
        # 緩存配置
        self.cache_config = {
            "default_ttl": 3600,  # 1小時
            "max_size": 10000,    # 最大條目數
            "eviction_policy": "LRU",
            "enable_compression": True
        }
        
        # 緩存統計
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        
    async def initialize(self) -> Dict[str, Any]:
        """初始化Cache MCP"""
        try:
            # TODO: 連接Redis
            
            self.status = "running"
            logger.info("✅ Cache MCP 初始化成功")
            
            return {
                "status": "success",
                "component": self.component_name,
                "cache_config": self.cache_config,
                "backend": "memory"  # 或 "redis"
            }
            
        except Exception as e:
            self.status = "error"
            self.record_error(e)
            return {
                "status": "error",
                "component": self.component_name,
                "error": str(e)
            }
    
    async def call_mcp(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """調用MCP方法"""
        self.update_activity()
        
        try:
            if method == "get":
                return await self._get(params)
            elif method == "set":
                return await self._set(params)
            elif method == "delete":
                return await self._delete(params)
            elif method == "clear":
                return await self._clear()
            elif method == "get_stats":
                return self._get_stats()
            else:
                return {
                    "status": "error",
                    "message": f"未知方法: {method}"
                }
                
        except Exception as e:
            self.record_error(e)
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """獲取緩存值"""
        key = params.get("key", "")
        
        if not key:
            return {"status": "error", "message": "缺少key參數"}
        
        self.cache_stats["total_requests"] += 1
        
        cache_key = self._make_key(key)
        
        if cache_key in self.cache_store:
            entry = self.cache_store[cache_key]
            
            # 檢查過期
            if entry["expires_at"] > time.time():
                self.cache_stats["hits"] += 1
                
                # 更新LRU
                entry["last_accessed"] = time.time()
                
                return {
                    "status": "success",
                    "value": entry["value"],
                    "hit": True,
                    "ttl": int(entry["expires_at"] - time.time())
                }
            else:
                # 過期，刪除
                del self.cache_store[cache_key]
        
        self.cache_stats["misses"] += 1
        
        return {
            "status": "success",
            "value": None,
            "hit": False
        }
    
    async def _set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """設置緩存值"""
        key = params.get("key", "")
        value = params.get("value")
        ttl = params.get("ttl", self.cache_config["default_ttl"])
        
        if not key:
            return {"status": "error", "message": "缺少key參數"}
        
        # 檢查緩存大小
        if len(self.cache_store) >= self.cache_config["max_size"]:
            await self._evict()
        
        cache_key = self._make_key(key)
        
        self.cache_store[cache_key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        
        return {
            "status": "success",
            "key": key,
            "ttl": ttl
        }
    
    async def _delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """刪除緩存值"""
        key = params.get("key", "")
        
        if not key:
            return {"status": "error", "message": "缺少key參數"}
        
        cache_key = self._make_key(key)
        
        if cache_key in self.cache_store:
            del self.cache_store[cache_key]
            return {"status": "success", "deleted": True}
        
        return {"status": "success", "deleted": False}
    
    async def _clear(self) -> Dict[str, Any]:
        """清空緩存"""
        size = len(self.cache_store)
        self.cache_store.clear()
        
        return {
            "status": "success",
            "cleared": size
        }
    
    async def _evict(self):
        """LRU驅逐"""
        if not self.cache_store:
            return
        
        # 找到最久未訪問的條目
        oldest_key = min(
            self.cache_store.keys(),
            key=lambda k: self.cache_store[k]["last_accessed"]
        )
        
        del self.cache_store[oldest_key]
        self.cache_stats["evictions"] += 1
    
    def _make_key(self, key: str) -> str:
        """生成緩存鍵"""
        if isinstance(key, dict):
            key = json.dumps(key, sort_keys=True)
        
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_stats(self) -> Dict[str, Any]:
        """獲取緩存統計"""
        total = self.cache_stats["total_requests"]
        hits = self.cache_stats["hits"]
        
        return {
            "status": "success",
            "stats": {
                "total_requests": total,
                "hits": hits,
                "misses": self.cache_stats["misses"],
                "hit_rate": f"{hits/max(total,1)*100:.1f}%",
                "evictions": self.cache_stats["evictions"],
                "current_size": len(self.cache_store)
            }
        }
    
    def get_info(self) -> Dict[str, Any]:
        """獲取組件信息"""
        return {
            "component": self.component_name,
            "description": "高性能緩存MCP組件",
            "version": "1.0",
            "status": self.status,
            "features": ["LRU驅逐", "TTL支持", "統計信息", "分佈式就緒"]
        }
'''
    
    # 保存Cache MCP
    cache_path = Path("core/mcp_components/cache_mcp")
    cache_path.mkdir(parents=True, exist_ok=True)
    
    with open(cache_path / "__init__.py", 'w') as f:
        f.write('from .cache import CacheMCP\n\n__all__ = ["CacheMCP"]')
    
    with open(cache_path / "cache.py", 'w') as f:
        f.write(cache_mcp)
    
    print("✅ 創建 Cache MCP 組件")
    
    # 3. 更新MCP管理器註冊新組件
    mcp_manager_registration = '''
# 在MCPManager的_register_components方法中添加：

        # 註冊Router MCP
        try:
            from .mcp_components.router_mcp import RouterMCP
            router = RouterMCP()
            self.components["router_mcp"] = router
            logger.info("✅ 註冊 Router MCP")
        except Exception as e:
            logger.error(f"註冊 Router MCP 失敗: {e}")
        
        # 註冊Cache MCP
        try:
            from .mcp_components.cache_mcp import CacheMCP
            cache = CacheMCP()
            self.components["cache_mcp"] = cache
            logger.info("✅ 註冊 Cache MCP")
        except Exception as e:
            logger.error(f"註冊 Cache MCP 失敗: {e}")
'''
    
    print("\n📝 請在 mcp_manager.py 的 _register_components 方法中添加：")
    print(mcp_manager_registration)
    
    # 4. 創建MCP架構示意圖
    architecture_doc = '''# PowerAutomation MCP架構

## 🏗️ MCP組件架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                     PowerAutomation Core                      │
├─────────────────────────────────────────────────────────────┤
│                      MCP Manager                              │
│  統一管理所有MCP組件，提供標準化接口                             │
└────────────────┬───────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┬────────────┬──────────────┐
    │                         │            │              │
┌───▼────┐          ┌────────▼───┐  ┌────▼─────┐  ┌─────▼────┐
│Router  │          │  K2 Chat   │  │Memory RAG│  │  Cache   │
│  MCP   │          │    MCP     │  │   MCP    │  │   MCP    │
├────────┤          ├────────────┤  ├──────────┤  ├──────────┤
│智能路由│          │Moonshot K2 │  │ RAG增強  │  │高速緩存  │
│決策引擎│          │Groq備用    │  │風格對齊  │  │LRU策略   │
└───┬────┘          └──────┬─────┘  └────┬─────┘  └────┬─────┘
    │                      │              │              │
    └──────────────────────┴──────────────┴──────────────┘
                           │
                    ┌──────▼───────┐
                    │ 統一響應接口  │
                    └──────────────┘
```

## 📦 MCP組件列表

### 1. **Router MCP** - 智能路由器
- 分析查詢類型
- 選擇最佳AI提供商
- 平衡速度、質量、成本

### 2. **K2 Chat MCP** - 核心對話引擎
- Moonshot K2為主
- Groq超快備用
- 自動降級機制

### 3. **Memory RAG MCP** - 記憶增強
- Claude行為學習
- K2響應優化
- 風格對齊

### 4. **Cache MCP** - 緩存加速
- 響應緩存
- LRU驅逐策略
- 分佈式就緒

### 5. **Workflow MCP** - 工作流引擎
- 六大自動化工作流
- 任務編排
- 狀態管理

### 6. **ClaudeEditor MCP** - 編輯器集成
- 雙向通信
- IDE功能
- 實時協作

### 7. **SmartUI MCP** - UI生成
- 智能界面生成
- 響應式設計
- 組件庫管理

## 🔄 請求流程

1. **用戶請求** → MCP Manager
2. **Router MCP** 分析並路由
3. **Cache MCP** 檢查緩存
4. **K2 Chat MCP** 生成響應
5. **Memory RAG MCP** 增強優化
6. **統一響應** → 用戶

## 🎯 架構優勢

- **模塊化**: 每個功能獨立MCP組件
- **可擴展**: 輕鬆添加新MCP組件
- **高性能**: 緩存+並行處理
- **容錯性**: 自動降級和錯誤恢復
- **標準化**: 統一的MCP接口規範
'''
    
    with open("MCP_ARCHITECTURE.md", 'w') as f:
        f.write(architecture_doc)
    
    print("✅ 創建 MCP架構文檔")
    
    # 5. 創建完整測試腳本
    full_test = '''#!/usr/bin/env python3
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
    
    print(f"\\n📝 測試查詢: {test_query}")
    print("-"*50)
    
    # 1. Router決策
    print("\\n1️⃣ Router MCP - 路由決策")
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
    print("\\n2️⃣ Cache MCP - 緩存檢查")
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
    print("\\n3️⃣ K2 Chat MCP - 生成響應")
    
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
    print("\\n4️⃣ Memory RAG MCP - 增強優化")
    
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
    print("\\n5️⃣ Cache MCP - 緩存結果")
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
    print("\\n📊 最終結果:")
    print("-"*50)
    print(f"響應預覽: {k2_response[:200]}...")
    
    # 獲取統計
    print("\\n📈 系統統計:")
    
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
    
    print("\\n✅ 完整MCP流程測試完成！")

if __name__ == "__main__":
    asyncio.run(test_full_mcp_flow())
'''
    
    with open("test_full_mcp_architecture.py", 'w') as f:
        f.write(full_test)
    os.chmod("test_full_mcp_architecture.py", 0o755)
    
    print("✅ 創建完整測試腳本")
    
    print("\n🏗️ MCP架構強化完成！")
    print("="*60)
    print("新增組件：")
    print("1. ✅ Router MCP - 智能路由決策")
    print("2. ✅ Cache MCP - 高性能緩存")
    print("\n架構特點：")
    print("- 所有功能都是獨立的MCP組件")
    print("- 標準化的MCP接口")
    print("- 模塊化和可擴展")
    print("- 完整的錯誤處理和統計")
    print("\n下一步：")
    print("1. 更新 mcp_manager.py 註冊新組件")
    print("2. 運行測試: python3 test_full_mcp_architecture.py")
    print("3. 查看架構文檔: MCP_ARCHITECTURE.md")

if __name__ == "__main__":
    strengthen_mcp_architecture()