"""
External Tools MCP Integration - PowerAutomation v4.8
外部工具整合核心模組
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

class ExternalToolsMCP:
    """
    外部工具 MCP 主類
    統一接口處理所有外部工具平台的請求
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adapters = {}
        self.initialized = False
        
    async def initialize(self):
        """初始化 MCP"""
        try:
            from .mcp_so_adapter import MCPSOAdapter
            from .aci_dev_adapter import ACIDevAdapter
            from .zapier_adapter import ZapierAdapter
            
            # 初始化平台適配器
            self.adapters = {
                'mcp.so': MCPSOAdapter(),
                'aci.dev': ACIDevAdapter(),
                'zapier': ZapierAdapter()
            }
            
            # 初始化每個適配器
            init_results = {}
            for platform, adapter in self.adapters.items():
                result = await adapter.initialize()
                init_results[platform] = result
                if result['status'] == 'success':
                    self.logger.info(f"✅ {platform} 初始化成功")
                else:
                    self.logger.warning(f"⚠️ {platform} 初始化失敗: {result.get('error')}")
            
            self.initialized = True
            return {
                "status": "success",
                "message": "External Tools MCP 初始化完成",
                "adapters": init_results
            }
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理 MCP 請求"""
        if not self.initialized:
            await self.initialize()
        
        try:
            if method == "list_tools":
                return await self._handle_list_tools(params)
            elif method == "execute_tool":
                return await self._handle_execute_tool(params)
            elif method == "search_tools":
                return await self._handle_search_tools(params)
            elif method == "execute_workflow":
                return await self._handle_execute_workflow(params)
            elif method == "get_recommendations":
                return await self._handle_get_recommendations(params)
            else:
                return {"error": f"Unknown method: {method}"}
                
        except Exception as e:
            self.logger.error(f"處理請求失敗: {str(e)}")
            return {"error": str(e)}
    
    async def _handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理列出工具請求"""
        platform = params.get('platform')
        category = params.get('category')
        
        tools = []
        
        if platform and platform in self.adapters:
            # 從特定平台獲取
            tools = await self.adapters[platform].list_tools()
        else:
            # 從所有平台獲取
            for adapter in self.adapters.values():
                adapter_tools = await adapter.list_tools()
                tools.extend(adapter_tools)
        
        # 按類別過濾
        if category:
            tools = [t for t in tools if t.get('category') == category]
        
        return {
            "tools": tools,
            "total": len(tools)
        }
    
    async def _handle_execute_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理執行工具請求"""
        tool_id = params.get('tool_id')
        tool_params = params.get('parameters', {})
        
        # 查找工具所屬平台
        for platform, adapter in self.adapters.items():
            tools = await adapter.list_tools()
            if any(t['id'] == tool_id for t in tools):
                result = await adapter.execute_tool(tool_id, tool_params)
                result['platform'] = platform
                return result
        
        return {"error": f"Tool not found: {tool_id}"}
    
    async def _handle_search_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理搜索工具請求"""
        query = params.get('query', '').lower()
        capabilities = params.get('capabilities', [])
        
        all_tools = []
        for adapter in self.adapters.values():
            tools = await adapter.list_tools()
            all_tools.extend(tools)
        
        # 搜索匹配
        matched_tools = []
        for tool in all_tools:
            # 文本搜索
            if query and query in f"{tool.get('name', '')} {tool.get('description', '')}".lower():
                matched_tools.append(tool)
                continue
            
            # 能力搜索
            if capabilities:
                tool_caps = tool.get('capabilities', [])
                if any(cap in tool_caps for cap in capabilities):
                    matched_tools.append(tool)
        
        return {
            "tools": matched_tools,
            "count": len(matched_tools)
        }
    
    async def _handle_execute_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理執行工作流請求"""
        steps = params.get('steps', [])
        parallel = params.get('parallel', False)
        
        if parallel:
            # 並行執行
            tasks = []
            for step in steps:
                task = self._handle_execute_tool({
                    'tool_id': step['tool_id'],
                    'parameters': step.get('parameters', {})
                })
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            workflow_results = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    workflow_results.append({
                        "step": i + 1,
                        "status": "error",
                        "error": str(result)
                    })
                else:
                    workflow_results.append({
                        "step": i + 1,
                        **result
                    })
        else:
            # 順序執行
            workflow_results = []
            for i, step in enumerate(steps):
                result = await self._handle_execute_tool({
                    'tool_id': step['tool_id'],
                    'parameters': step.get('parameters', {})
                })
                workflow_results.append({
                    "step": i + 1,
                    **result
                })
                
                # 如果失敗則停止
                if result.get('error'):
                    break
        
        success = all(not r.get('error') for r in workflow_results)
        
        return {
            "success": success,
            "total_steps": len(steps),
            "executed_steps": len(workflow_results),
            "workflow_results": workflow_results
        }
    
    async def _handle_get_recommendations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理獲取推薦請求"""
        intent = params.get('intent', '')
        context = params.get('context', {})
        
        # 獲取所有工具
        all_tools = []
        for adapter in self.adapters.values():
            tools = await adapter.list_tools()
            all_tools.extend(tools)
        
        # 簡單的推薦邏輯
        recommendations = []
        keywords = intent.lower().split()
        
        for tool in all_tools:
            score = 0.0
            tool_text = f"{tool.get('name', '')} {tool.get('description', '')}".lower()
            
            # 關鍵詞匹配
            for keyword in keywords:
                if keyword in tool_text:
                    score += 0.3
            
            # 上下文匹配
            if context.get('language') and context['language'] in tool.get('supported_languages', []):
                score += 0.2
            
            if score > 0:
                recommendations.append({
                    "tool": tool,
                    "score": min(score, 1.0)
                })
        
        # 排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            "recommendations": recommendations[:5],
            "reasoning": f"Based on intent '{intent}' and context"
        }