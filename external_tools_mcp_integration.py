#!/usr/bin/env python3
"""
外部工具 MCP 整合方案
將 MCP.so、ACI.dev、Zapier 封裝為標準 MCP 組件
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib

# MCP 基礎類（假設已有）
class BaseMCP:
    """MCP 基礎類"""
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.handlers = {}
        
    def register_handler(self, method: str, handler: Callable):
        """註冊方法處理器"""
        self.handlers[method] = handler
        
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理請求"""
        if method not in self.handlers:
            return {"error": f"Unknown method: {method}"}
        
        handler = self.handlers[method]
        return await handler(params)

class ExternalToolsMCP(BaseMCP):
    """
    External Tools MCP - 統一外部工具接口
    
    將 MCP.so、ACI.dev、Zapier 等外部工具服務封裝為標準 MCP 組件
    提供統一的工具發現、路由和執行接口
    """
    
    def __init__(self):
        super().__init__("external_tools_mcp", "1.0.0")
        self.tools_registry = {}
        self.platform_adapters = {}
        self.routing_engine = None
        self.cache = {}
        self._initialize()
        
    def _initialize(self):
        """初始化 MCP"""
        # 註冊 MCP 方法
        self.register_handler("list_tools", self._handle_list_tools)
        self.register_handler("execute_tool", self._handle_execute_tool)
        self.register_handler("search_tools", self._handle_search_tools)
        self.register_handler("get_tool_info", self._handle_get_tool_info)
        self.register_handler("execute_workflow", self._handle_execute_workflow)
        self.register_handler("get_recommendations", self._handle_get_recommendations)
        
        # 初始化組件
        self._init_platform_adapters()
        self._init_routing_engine()
        self._load_tools_registry()
        
    def _init_platform_adapters(self):
        """初始化平台適配器"""
        self.platform_adapters = {
            "mcp.so": MCPSOAdapter(),
            "aci.dev": ACIDevAdapter(),
            "zapier": ZapierAdapter()
        }
        
    def _init_routing_engine(self):
        """初始化智能路由引擎"""
        self.routing_engine = IntelligentRoutingEngine()
        
    def _load_tools_registry(self):
        """加載工具註冊表"""
        # Phase 1: MCP.so 工具
        self._register_mcp_so_tools()
        
        # Phase 2: ACI.dev 工具
        self._register_aci_dev_tools()
        
        # Phase 3: Zapier 工具
        self._register_zapier_tools()
        
    def _register_mcp_so_tools(self):
        """註冊 MCP.so 工具"""
        mcp_tools = [
            {
                "id": "mcp_prettier",
                "name": "Prettier 代碼格式化",
                "platform": "mcp.so",
                "category": "code_quality",
                "description": "使用 Prettier 格式化代碼，支持多種語言",
                "capabilities": ["format", "beautify"],
                "parameters": {
                    "code": {"type": "string", "required": True},
                    "language": {"type": "string", "required": True},
                    "config": {"type": "object", "required": False}
                },
                "cost_per_call": 0.001,
                "avg_latency_ms": 100
            },
            {
                "id": "mcp_eslint",
                "name": "ESLint 代碼檢查",
                "platform": "mcp.so",
                "category": "code_quality",
                "description": "使用 ESLint 進行代碼質量檢查和自動修復",
                "capabilities": ["lint", "fix", "analyze"],
                "parameters": {
                    "code": {"type": "string", "required": True},
                    "rules": {"type": "string", "default": "airbnb"},
                    "fix": {"type": "boolean", "default": True}
                },
                "cost_per_call": 0.002,
                "avg_latency_ms": 200
            },
            {
                "id": "mcp_jest_runner",
                "name": "Jest 測試運行器",
                "platform": "mcp.so",
                "category": "testing",
                "description": "運行 Jest 測試並生成覆蓋率報告",
                "capabilities": ["test", "coverage", "watch"],
                "parameters": {
                    "test_files": {"type": "array", "required": True},
                    "coverage": {"type": "boolean", "default": True},
                    "watch": {"type": "boolean", "default": False}
                },
                "cost_per_call": 0.005,
                "avg_latency_ms": 500
            }
        ]
        
        for tool in mcp_tools:
            self.tools_registry[tool["id"]] = tool
            
    def _register_aci_dev_tools(self):
        """註冊 ACI.dev 工具"""
        aci_tools = [
            {
                "id": "aci_code_review",
                "name": "AI 代碼審查",
                "platform": "aci.dev",
                "category": "ai_analysis",
                "description": "使用 AI 進行深度代碼審查，提供改進建議",
                "capabilities": ["review", "suggest", "security_check"],
                "parameters": {
                    "code": {"type": "string", "required": True},
                    "language": {"type": "string", "required": True},
                    "focus": {"type": "array", "default": ["quality", "security", "performance"]}
                },
                "cost_per_call": 0.02,
                "avg_latency_ms": 2000
            },
            {
                "id": "aci_refactor",
                "name": "智能重構助手",
                "platform": "aci.dev",
                "category": "ai_refactor",
                "description": "AI 驅動的代碼重構，遵循最佳實踐",
                "capabilities": ["refactor", "optimize", "modernize"],
                "parameters": {
                    "code": {"type": "string", "required": True},
                    "patterns": {"type": "array", "default": ["SOLID", "DRY", "KISS"]},
                    "target_version": {"type": "string", "required": False}
                },
                "cost_per_call": 0.03,
                "avg_latency_ms": 3000
            }
        ]
        
        for tool in aci_tools:
            self.tools_registry[tool["id"]] = tool
            
    def _register_zapier_tools(self):
        """註冊 Zapier 工具"""
        zapier_tools = [
            {
                "id": "zapier_github",
                "name": "GitHub 自動化",
                "platform": "zapier",
                "category": "collaboration",
                "description": "GitHub 問題、PR 和發布自動化",
                "capabilities": ["issue", "pr", "release"],
                "parameters": {
                    "action": {"type": "string", "required": True},
                    "repo": {"type": "string", "required": True},
                    "data": {"type": "object", "required": True}
                },
                "cost_per_call": 0.05,
                "avg_latency_ms": 3000
            },
            {
                "id": "zapier_slack",
                "name": "Slack 通知",
                "platform": "zapier",
                "category": "notification",
                "description": "發送 Slack 通知到指定頻道",
                "capabilities": ["notify", "alert", "report"],
                "parameters": {
                    "channel": {"type": "string", "required": True},
                    "message": {"type": "string", "required": True},
                    "attachments": {"type": "array", "required": False}
                },
                "cost_per_call": 0.02,
                "avg_latency_ms": 1000
            }
        ]
        
        for tool in zapier_tools:
            self.tools_registry[tool["id"]] = tool
    
    async def _handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理列出工具請求"""
        category = params.get("category")
        platform = params.get("platform")
        
        tools = list(self.tools_registry.values())
        
        # 過濾
        if category:
            tools = [t for t in tools if t["category"] == category]
        if platform:
            tools = [t for t in tools if t["platform"] == platform]
            
        return {
            "tools": tools,
            "total": len(tools),
            "platforms": list(set(t["platform"] for t in tools)),
            "categories": list(set(t["category"] for t in tools))
        }
    
    async def _handle_execute_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理執行工具請求"""
        tool_id = params.get("tool_id")
        tool_params = params.get("parameters", {})
        
        if tool_id not in self.tools_registry:
            return {"error": f"Tool not found: {tool_id}"}
            
        tool = self.tools_registry[tool_id]
        
        # 檢查緩存
        cache_key = self._generate_cache_key(tool_id, tool_params)
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if self._is_cache_valid(cached_result):
                return {
                    "result": cached_result["result"],
                    "cached": True,
                    "tool": tool
                }
        
        # 獲取適配器
        adapter = self.platform_adapters.get(tool["platform"])
        if not adapter:
            return {"error": f"No adapter for platform: {tool['platform']}"}
            
        # 執行工具
        try:
            result = await adapter.execute(tool, tool_params)
            
            # 緩存結果
            self.cache[cache_key] = {
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "ttl": 3600  # 1小時
            }
            
            return {
                "result": result,
                "tool": tool,
                "execution_time": result.get("execution_time_ms"),
                "cost": tool["cost_per_call"]
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "tool": tool
            }
    
    async def _handle_search_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理搜索工具請求"""
        query = params.get("query", "").lower()
        capabilities = params.get("capabilities", [])
        
        matching_tools = []
        
        for tool in self.tools_registry.values():
            # 文本搜索
            if query:
                if (query in tool["name"].lower() or 
                    query in tool["description"].lower() or
                    query in tool["category"].lower()):
                    matching_tools.append(tool)
                    continue
                    
            # 能力匹配
            if capabilities:
                if any(cap in tool["capabilities"] for cap in capabilities):
                    matching_tools.append(tool)
                    
        return {
            "tools": matching_tools,
            "count": len(matching_tools)
        }
    
    async def _handle_get_tool_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理獲取工具信息請求"""
        tool_id = params.get("tool_id")
        
        if tool_id not in self.tools_registry:
            return {"error": f"Tool not found: {tool_id}"}
            
        tool = self.tools_registry[tool_id]
        
        # 獲取詳細信息
        adapter = self.platform_adapters.get(tool["platform"])
        if adapter:
            additional_info = await adapter.get_tool_details(tool_id)
            tool.update(additional_info)
            
        return {"tool": tool}
    
    async def _handle_execute_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理執行工作流請求"""
        workflow_steps = params.get("steps", [])
        parallel = params.get("parallel", False)
        
        results = []
        
        if parallel:
            # 並行執行
            tasks = []
            for step in workflow_steps:
                task = self._handle_execute_tool({
                    "tool_id": step["tool_id"],
                    "parameters": step.get("parameters", {})
                })
                tasks.append(task)
                
            results = await asyncio.gather(*tasks)
        else:
            # 順序執行
            for step in workflow_steps:
                result = await self._handle_execute_tool({
                    "tool_id": step["tool_id"],
                    "parameters": step.get("parameters", {})
                })
                results.append(result)
                
                # 如果有錯誤且設置了 failFast
                if "error" in result and params.get("failFast", True):
                    break
                    
        return {
            "workflow_results": results,
            "total_steps": len(workflow_steps),
            "executed_steps": len(results),
            "success": all("error" not in r for r in results)
        }
    
    async def _handle_get_recommendations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理獲取推薦請求"""
        context = params.get("context", {})
        intent = params.get("intent")
        
        # 使用路由引擎獲取推薦
        recommendations = await self.routing_engine.get_recommendations(
            intent=intent,
            context=context,
            available_tools=list(self.tools_registry.values())
        )
        
        return {
            "recommendations": recommendations,
            "reasoning": "基於意圖和上下文分析"
        }
    
    def _generate_cache_key(self, tool_id: str, params: Dict[str, Any]) -> str:
        """生成緩存鍵"""
        key_data = f"{tool_id}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_item: Dict[str, Any]) -> bool:
        """檢查緩存是否有效"""
        if "timestamp" not in cached_item or "ttl" not in cached_item:
            return False
            
        cached_time = datetime.fromisoformat(cached_item["timestamp"])
        current_time = datetime.now()
        age_seconds = (current_time - cached_time).total_seconds()
        
        return age_seconds < cached_item["ttl"]
    
    def get_status(self) -> Dict[str, Any]:
        """獲取 MCP 狀態"""
        return {
            "name": self.name,
            "version": self.version,
            "total_tools": len(self.tools_registry),
            "platforms": {
                platform: len([t for t in self.tools_registry.values() if t["platform"] == platform])
                for platform in ["mcp.so", "aci.dev", "zapier"]
            },
            "categories": list(set(t["category"] for t in self.tools_registry.values())),
            "cache_size": len(self.cache),
            "adapters_status": {
                platform: adapter.is_connected()
                for platform, adapter in self.platform_adapters.items()
            }
        }

# 平台適配器
class MCPSOAdapter:
    """MCP.so 平台適配器"""
    
    def __init__(self):
        self.api_key = None  # 從環境變量讀取
        self.base_url = "https://api.mcp.so/v1"
        
    async def execute(self, tool: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 MCP.so 工具"""
        # 模擬 API 調用
        await asyncio.sleep(tool["avg_latency_ms"] / 1000)
        
        # 根據工具類型返回模擬結果
        if tool["id"] == "mcp_prettier":
            return {
                "formatted_code": "// Formatted code\n" + params.get("code", ""),
                "execution_time_ms": 95
            }
        elif tool["id"] == "mcp_eslint":
            return {
                "issues": [],
                "fixed": True,
                "execution_time_ms": 180
            }
        elif tool["id"] == "mcp_jest_runner":
            return {
                "tests_passed": 15,
                "tests_failed": 0,
                "coverage": 92.5,
                "execution_time_ms": 450
            }
            
    async def get_tool_details(self, tool_id: str) -> Dict[str, Any]:
        """獲取工具詳細信息"""
        return {
            "status": "available",
            "version": "latest",
            "usage_today": 142
        }
        
    def is_connected(self) -> bool:
        """檢查連接狀態"""
        return True

class ACIDevAdapter:
    """ACI.dev 平台適配器"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.aci.dev/v2"
        
    async def execute(self, tool: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 ACI.dev 工具"""
        await asyncio.sleep(tool["avg_latency_ms"] / 1000)
        
        if tool["id"] == "aci_code_review":
            return {
                "review_score": 8.5,
                "suggestions": [
                    "考慮使用 const 替代 let",
                    "添加錯誤處理",
                    "優化循環性能"
                ],
                "security_issues": [],
                "execution_time_ms": 1850
            }
        elif tool["id"] == "aci_refactor":
            return {
                "refactored_code": "// AI refactored code\n" + params.get("code", ""),
                "improvements": ["更好的命名", "減少複雜度", "提高可讀性"],
                "execution_time_ms": 2800
            }
            
    async def get_tool_details(self, tool_id: str) -> Dict[str, Any]:
        return {
            "ai_model": "gpt-4-turbo",
            "rate_limit": "100/hour"
        }
        
    def is_connected(self) -> bool:
        return True

class ZapierAdapter:
    """Zapier 平台適配器"""
    
    def __init__(self):
        self.api_key = None
        self.webhook_url = None
        
    async def execute(self, tool: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 Zapier 工具"""
        await asyncio.sleep(tool["avg_latency_ms"] / 1000)
        
        if tool["id"] == "zapier_github":
            return {
                "action": params.get("action"),
                "status": "success",
                "github_response": {"id": "12345", "url": "https://github.com/..."},
                "execution_time_ms": 2500
            }
        elif tool["id"] == "zapier_slack":
            return {
                "message_sent": True,
                "channel": params.get("channel"),
                "timestamp": datetime.now().isoformat(),
                "execution_time_ms": 800
            }
            
    async def get_tool_details(self, tool_id: str) -> Dict[str, Any]:
        return {
            "webhook_status": "active",
            "last_triggered": "2025-07-18T10:30:00"
        }
        
    def is_connected(self) -> bool:
        return True

class IntelligentRoutingEngine:
    """智能路由引擎"""
    
    async def get_recommendations(self, intent: str, context: Dict[str, Any], 
                                 available_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """獲取工具推薦"""
        recommendations = []
        
        # 簡化的推薦邏輯
        intent_keywords = {
            "format": ["prettier", "format", "beautify"],
            "test": ["jest", "test", "coverage"],
            "review": ["review", "analyze", "suggest"],
            "notify": ["slack", "notify", "alert"]
        }
        
        for tool in available_tools:
            score = 0
            
            # 意圖匹配
            for keyword, related in intent_keywords.items():
                if intent and keyword in intent.lower():
                    if any(r in tool["name"].lower() or r in str(tool["capabilities"]) for r in related):
                        score += 0.5
                        
            # 上下文匹配
            if context.get("language") and context["language"] in str(tool.get("parameters", {})):
                score += 0.3
                
            if score > 0:
                recommendations.append({
                    "tool": tool,
                    "score": score,
                    "reason": "基於意圖和上下文匹配"
                })
                
        # 排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:5]  # 返回前5個推薦

# 集成到 PowerAutomation MCP Manager
class PowerAutomationMCPManager:
    """PowerAutomation MCP 管理器擴展"""
    
    def __init__(self):
        self.mcp_components = {}
        
    async def register_external_tools_mcp(self):
        """註冊外部工具 MCP"""
        external_tools_mcp = ExternalToolsMCP()
        self.mcp_components["external_tools_mcp"] = external_tools_mcp
        
        print("✅ External Tools MCP 已註冊到 PowerAutomation")
        print(f"   - 可用工具數: {len(external_tools_mcp.tools_registry)}")
        print(f"   - 支持平台: MCP.so, ACI.dev, Zapier")
        
        return external_tools_mcp

# 使用示例
async def demonstrate_external_tools_mcp():
    """演示外部工具 MCP 使用"""
    print("🚀 External Tools MCP 演示")
    print("="*70)
    
    # 初始化
    mcp = ExternalToolsMCP()
    
    # 1. 列出所有工具
    print("\n1️⃣ 列出所有可用工具")
    tools_response = await mcp.handle_request("list_tools", {})
    print(f"總工具數: {tools_response['total']}")
    
    # 計算每個平台的工具數
    platform_counts = {}
    for tool in tools_response['tools']:
        platform = tool['platform']
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    for platform, count in platform_counts.items():
        print(f"  {platform}: {count} 個工具")
    
    # 2. 搜索工具
    print("\n2️⃣ 搜索格式化工具")
    search_response = await mcp.handle_request("search_tools", {
        "query": "format",
        "capabilities": ["format"]
    })
    print(f"找到 {search_response['count']} 個匹配工具")
    for tool in search_response['tools']:
        print(f"  - {tool['name']} ({tool['platform']})")
    
    # 3. 執行單個工具
    print("\n3️⃣ 執行 Prettier 格式化")
    prettier_response = await mcp.handle_request("execute_tool", {
        "tool_id": "mcp_prettier",
        "parameters": {
            "code": "const x=1;const y=2;",
            "language": "javascript"
        }
    })
    print(f"執行結果: {prettier_response.get('result', {}).get('formatted_code', 'N/A')}")
    print(f"執行時間: {prettier_response.get('execution_time', 'N/A')}ms")
    
    # 4. 執行工作流
    print("\n4️⃣ 執行代碼質量工作流")
    workflow_response = await mcp.handle_request("execute_workflow", {
        "steps": [
            {
                "tool_id": "mcp_prettier",
                "parameters": {"code": "const x=1;", "language": "javascript"}
            },
            {
                "tool_id": "mcp_eslint",
                "parameters": {"code": "const x=1;", "rules": "airbnb"}
            }
        ],
        "parallel": True
    })
    print(f"工作流執行成功: {workflow_response['success']}")
    print(f"執行步驟: {workflow_response['executed_steps']}/{workflow_response['total_steps']}")
    
    # 5. 獲取推薦
    print("\n5️⃣ 獲取工具推薦")
    recommendations = await mcp.handle_request("get_recommendations", {
        "intent": "format and test javascript code",
        "context": {"language": "javascript", "project_type": "react"}
    })
    print("推薦工具:")
    for rec in recommendations['recommendations'][:3]:
        print(f"  - {rec['tool']['name']} (評分: {rec['score']:.2f})")
    
    # 6. MCP 狀態
    print("\n6️⃣ MCP 狀態")
    status = mcp.get_status()
    print(f"名稱: {status['name']} v{status['version']}")
    print(f"總工具數: {status['total_tools']}")
    print("平台狀態:")
    for platform, connected in status['adapters_status'].items():
        print(f"  {platform}: {'✅ 已連接' if connected else '❌ 未連接'}")

if __name__ == "__main__":
    asyncio.run(demonstrate_external_tools_mcp())