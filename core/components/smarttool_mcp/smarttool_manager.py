"""
SmartTool MCP Manager - PowerAutomation v4.8
智能外部工具集成管理器，與 MCP-Zero 深度整合
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

class SmartToolManager:
    """
    SmartTool 管理器
    統一管理 mcp.so, aci.dev, zapier 等外部工具平台
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adapters = {}
        self.tool_registry = {}
        self.execution_history = []
        self.cache = {}
        
        # 統計信息
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "cached_responses": 0,
            "total_cost": 0.0
        }
    
    async def initialize(self):
        """初始化管理器"""
        try:
            self.logger.info("初始化 SmartTool MCP 管理器...")
            
            # 初始化各平台適配器
            from .mcp_so_adapter import MCPSOAdapter
            from .aci_dev_adapter import ACIDevAdapter
            from .zapier_adapter import ZapierAdapter
            
            self.adapters['mcp.so'] = MCPSOAdapter()
            self.adapters['aci.dev'] = ACIDevAdapter()
            self.adapters['zapier'] = ZapierAdapter()
            
            # 初始化所有適配器
            for platform, adapter in self.adapters.items():
                result = await adapter.initialize()
                if result['status'] == 'success':
                    self.logger.info(f"✅ {platform} 適配器初始化成功")
                else:
                    self.logger.warning(f"⚠️ {platform} 適配器初始化失敗: {result.get('error')}")
            
            # 加載工具註冊表
            await self._load_tool_registry()
            
            return {
                "status": "success",
                "message": "SmartTool MCP 管理器初始化完成",
                "platforms": list(self.adapters.keys()),
                "total_tools": len(self.tool_registry)
            }
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def list_tools(self, platform: str = None, category: str = None) -> Dict[str, Any]:
        """列出可用工具"""
        try:
            tools = []
            
            if platform and platform in self.adapters:
                # 從特定平台獲取工具
                adapter_tools = await self.adapters[platform].list_tools()
                tools.extend(adapter_tools)
            else:
                # 從所有平台獲取工具
                for adapter in self.adapters.values():
                    adapter_tools = await adapter.list_tools()
                    tools.extend(adapter_tools)
            
            # 按類別過濾
            if category:
                tools = [t for t in tools if t.get('category') == category]
            
            return {
                "status": "success",
                "tools": tools,
                "total": len(tools),
                "platforms": list(self.adapters.keys())
            }
            
        except Exception as e:
            self.logger.error(f"列出工具失敗: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行工具"""
        try:
            # 查找工具所屬平台
            tool_info = self.tool_registry.get(tool_id)
            if not tool_info:
                return {"status": "error", "error": f"工具未找到: {tool_id}"}
            
            platform = tool_info['platform']
            adapter = self.adapters.get(platform)
            
            if not adapter:
                return {"status": "error", "error": f"平台適配器未找到: {platform}"}
            
            # 檢查緩存
            cache_key = f"{tool_id}:{json.dumps(parameters, sort_keys=True)}"
            if cache_key in self.cache:
                self.stats['cached_responses'] += 1
                cached_result = self.cache[cache_key]
                cached_result['cached'] = True
                return cached_result
            
            # 執行工具
            start_time = datetime.now()
            result = await adapter.execute_tool(tool_id, parameters)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 更新統計
            self.stats['total_executions'] += 1
            if result.get('status') == 'success':
                self.stats['successful_executions'] += 1
            else:
                self.stats['failed_executions'] += 1
            
            # 計算成本
            cost = tool_info.get('cost_per_call', 0.0)
            self.stats['total_cost'] += cost
            
            # 記錄執行歷史
            self.execution_history.append({
                "tool_id": tool_id,
                "parameters": parameters,
                "result": result,
                "execution_time": execution_time,
                "cost": cost,
                "timestamp": datetime.now().isoformat()
            })
            
            # 緩存成功結果
            if result.get('status') == 'success':
                self.cache[cache_key] = result
            
            # 添加執行信息
            result['execution_time'] = execution_time
            result['cost'] = cost
            result['tool'] = tool_info
            
            return result
            
        except Exception as e:
            self.logger.error(f"執行工具失敗: {str(e)}")
            self.stats['failed_executions'] += 1
            return {"status": "error", "error": str(e)}
    
    async def execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """執行工作流"""
        try:
            steps = workflow.get('steps', [])
            parallel = workflow.get('parallel', False)
            
            if parallel:
                # 並行執行
                tasks = []
                for step in steps:
                    task = self.execute_tool(
                        step['tool_id'],
                        step.get('parameters', {})
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 處理結果
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
                    result = await self.execute_tool(
                        step['tool_id'],
                        step.get('parameters', {})
                    )
                    workflow_results.append({
                        "step": i + 1,
                        **result
                    })
                    
                    # 如果步驟失敗，停止執行
                    if result.get('status') != 'success' and workflow.get('stop_on_error', True):
                        break
            
            # 計算總體狀態
            success = all(r.get('status') == 'success' for r in workflow_results)
            
            return {
                "status": "success" if success else "partial",
                "success": success,
                "total_steps": len(steps),
                "executed_steps": len(workflow_results),
                "workflow_results": workflow_results
            }
            
        except Exception as e:
            self.logger.error(f"執行工作流失敗: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def get_recommendations(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """獲取工具推薦"""
        try:
            # 分析意圖
            keywords = intent.lower().split()
            
            # 獲取所有工具
            all_tools = []
            for adapter in self.adapters.values():
                tools = await adapter.list_tools()
                all_tools.extend(tools)
            
            # 評分和排序
            recommendations = []
            for tool in all_tools:
                score = self._calculate_tool_score(tool, keywords, context)
                if score > 0.3:  # 閾值
                    recommendations.append({
                        "tool": tool,
                        "score": score,
                        "reasoning": self._generate_reasoning(tool, keywords, context)
                    })
            
            # 按分數排序
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                "status": "success",
                "intent": intent,
                "context": context,
                "recommendations": recommendations[:10],  # 返回前10個
                "reasoning": f"基於意圖 '{intent}' 和上下文，推薦以上工具"
            }
            
        except Exception as e:
            self.logger.error(f"獲取推薦失敗: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _load_tool_registry(self):
        """加載工具註冊表"""
        # 從各適配器收集工具信息
        for platform, adapter in self.adapters.items():
            tools = await adapter.list_tools()
            for tool in tools:
                tool['platform'] = platform
                self.tool_registry[tool['id']] = tool
    
    def _calculate_tool_score(self, tool: Dict[str, Any], keywords: List[str], context: Dict[str, Any]) -> float:
        """計算工具相關性分數"""
        score = 0.0
        
        # 關鍵詞匹配
        tool_text = f"{tool.get('name', '')} {tool.get('description', '')}".lower()
        for keyword in keywords:
            if keyword in tool_text:
                score += 0.2
        
        # 類別匹配
        if context.get('category') == tool.get('category'):
            score += 0.3
        
        # 語言匹配
        if context.get('language') and context['language'] in tool.get('supported_languages', []):
            score += 0.2
        
        # 項目類型匹配
        if context.get('project_type') and context['project_type'] in tool.get('project_types', []):
            score += 0.2
        
        return min(score, 1.0)
    
    def _generate_reasoning(self, tool: Dict[str, Any], keywords: List[str], context: Dict[str, Any]) -> str:
        """生成推薦理由"""
        reasons = []
        
        # 關鍵詞匹配
        matched_keywords = [k for k in keywords if k in f"{tool.get('name', '')} {tool.get('description', '')}".lower()]
        if matched_keywords:
            reasons.append(f"匹配關鍵詞: {', '.join(matched_keywords)}")
        
        # 功能匹配
        if tool.get('capabilities'):
            reasons.append(f"提供功能: {', '.join(tool['capabilities'][:3])}")
        
        # 性能特點
        if tool.get('performance_rating', 0) >= 4:
            reasons.append("高性能評分")
        
        return "; ".join(reasons) if reasons else "通用工具"
    
    async def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            "status": "success",
            "stats": self.stats,
            "platforms": {
                platform: await adapter.get_stats()
                for platform, adapter in self.adapters.items()
            },
            "cache_size": len(self.cache),
            "history_size": len(self.execution_history)
        }
    
    async def register_with_mcp_zero(self, mcp_zero_engine):
        """註冊到 MCP-Zero"""
        return await mcp_zero_engine.register_mcp(
            mcp_id='smarttool_mcp',
            mcp_instance=self,
            capabilities={
                'external_tools': True,
                'workflow_execution': True,
                'tool_recommendation': True,
                'multi_platform': True,
                'platforms': list(self.adapters.keys())
            }
        )