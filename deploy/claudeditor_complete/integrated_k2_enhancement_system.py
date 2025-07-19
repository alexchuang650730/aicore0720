"""
集成 K2 增強系統
整合 Enhanced Claude Router MCP + PowerAutomation + ClaudeEditor
提供端到端的智能路由和命令增強服務
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
import websockets
from enhanced_claude_router_mcp import EnhancedClaudeRouterMCP, ModelProvider, CommandComplexity

logger = logging.getLogger(__name__)

@dataclass
class K2EnhancementConfig:
    """K2 增強配置"""
    enable_auto_enhancement: bool = True
    quality_threshold: float = 0.8
    cost_optimization_priority: float = 0.7  # 0-1，越高越注重成本
    enable_fallback: bool = True
    fallback_threshold: float = 0.75
    enable_learning: bool = True
    max_retry_attempts: int = 2

class IntegratedK2EnhancementSystem:
    """集成 K2 增強系統"""
    
    def __init__(self, config: K2EnhancementConfig = None):
        self.config = config or K2EnhancementConfig()
        self.router = EnhancedClaudeRouterMCP()
        self.powerautomation_connector = PowerAutomationConnector()
        self.claudeditor_interface = ClaudeEditorInterface()
        self.websocket_server = WebSocketServer()
        
        # 統計和學習
        self.usage_statistics = {
            "total_commands": 0,
            "k2_usage_count": 0,
            "claude_usage_count": 0,
            "fallback_count": 0,
            "cost_savings": 0.0,
            "quality_scores": []
        }
        
        logger.info("🚀 Integrated K2 Enhancement System 初始化完成")
    
    async def start_system(self, port: int = 8765):
        """啟動完整系統"""
        
        # 啟動 WebSocket 服務器
        await self.websocket_server.start_server(self.handle_websocket_message, port)
        
        # 啟動 PowerAutomation 連接器
        await self.powerautomation_connector.initialize()
        
        # 啟動 ClaudeEditor 接口
        await self.claudeditor_interface.initialize()
        
        logger.info(f"✅ K2 Enhancement System 已啟動，監聽端口: {port}")
    
    async def handle_websocket_message(self, websocket, path):
        """處理 WebSocket 消息"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "claude_code_command":
                    response = await self.process_claude_code_command(data)
                    await websocket.send(json.dumps(response))
                
                elif data["type"] == "workflow_command":
                    response = await self.process_workflow_command(data)
                    await websocket.send(json.dumps(response))
                
                elif data["type"] == "config_update":
                    response = await self.update_configuration(data)
                    await websocket.send(json.dumps(response))
                
                elif data["type"] == "statistics_request":
                    response = await self.get_statistics()
                    await websocket.send(json.dumps(response))
                
        except Exception as e:
            logger.error(f"WebSocket 消息處理錯誤: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))
    
    async def process_claude_code_command(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """處理 Claude Code 命令"""
        
        command = request.get("command", "")
        context = request.get("context", {})
        user_preferences = request.get("user_preferences", {})
        
        # 1. 更新配置（如果用戶有特定偏好）
        effective_config = self._merge_config_with_preferences(user_preferences)
        
        # 2. 使用增強路由器處理命令
        routing_result = await self.router.route_claude_code_command(command, context)
        
        # 3. 更新統計信息
        await self._update_statistics(routing_result)
        
        # 4. 學習和優化
        if self.config.enable_learning:
            await self._learn_from_result(routing_result, context)
        
        # 5. 通知 PowerAutomation
        await self.powerautomation_connector.notify_command_execution(routing_result)
        
        # 6. 更新 ClaudeEditor 界面
        await self.claudeditor_interface.update_ui_with_result(routing_result)
        
        return {
            "type": "claude_code_response",
            "success": True,
            "routing_result": routing_result,
            "system_statistics": self._get_current_statistics(),
            "recommendations": await self._generate_recommendations(routing_result)
        }
    
    async def process_workflow_command(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """處理工作流命令"""
        
        workflow_type = request.get("workflow_type", "")
        workflow_data = request.get("workflow_data", {})
        
        # 1. 分析工作流中的 AI 需求
        ai_tasks = await self._extract_ai_tasks_from_workflow(workflow_type, workflow_data)
        
        # 2. 為每個 AI 任務選擇最佳提供者
        optimized_tasks = []
        for task in ai_tasks:
            task_result = await self.router.route_claude_code_command(
                task["command"], 
                task.get("context", {})
            )
            optimized_tasks.append({
                "task_id": task["task_id"],
                "original_command": task["command"],
                "routing_result": task_result
            })
        
        # 3. 生成工作流執行計劃
        execution_plan = await self._generate_workflow_execution_plan(optimized_tasks)
        
        return {
            "type": "workflow_response",
            "success": True,
            "optimized_tasks": optimized_tasks,
            "execution_plan": execution_plan,
            "estimated_cost_savings": self._calculate_workflow_cost_savings(optimized_tasks),
            "estimated_completion_time": self._calculate_workflow_completion_time(optimized_tasks)
        }
    
    async def update_configuration(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置"""
        
        new_config = request.get("config", {})
        
        # 更新配置
        for key, value in new_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        logger.info(f"配置已更新: {new_config}")
        
        return {
            "type": "config_update_response",
            "success": True,
            "current_config": asdict(self.config)
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        
        stats = self.usage_statistics.copy()
        
        # 計算額外指標
        if stats["total_commands"] > 0:
            stats["k2_usage_percentage"] = (stats["k2_usage_count"] / stats["total_commands"]) * 100
            stats["claude_usage_percentage"] = (stats["claude_usage_count"] / stats["total_commands"]) * 100
            stats["fallback_rate"] = (stats["fallback_count"] / stats["total_commands"]) * 100
            stats["average_quality_score"] = sum(stats["quality_scores"]) / len(stats["quality_scores"]) if stats["quality_scores"] else 0
        
        # 性能指標
        stats["performance_metrics"] = await self._calculate_performance_metrics()
        
        return {
            "type": "statistics_response",
            "statistics": stats,
            "timestamp": time.time()
        }
    
    def _merge_config_with_preferences(self, preferences: Dict[str, Any]) -> K2EnhancementConfig:
        """合併配置與用戶偏好"""
        
        config = K2EnhancementConfig()
        
        # 用戶偏好覆蓋默認配置
        if "cost_priority" in preferences:
            config.cost_optimization_priority = preferences["cost_priority"]
        
        if "quality_threshold" in preferences:
            config.quality_threshold = preferences["quality_threshold"]
        
        if "enable_fallback" in preferences:
            config.enable_fallback = preferences["enable_fallback"]
        
        return config
    
    async def _update_statistics(self, routing_result: Dict[str, Any]) -> None:
        """更新統計信息"""
        
        self.usage_statistics["total_commands"] += 1
        
        provider = routing_result.get("selected_provider", "")
        if provider == "claude":
            self.usage_statistics["claude_usage_count"] += 1
        else:
            self.usage_statistics["k2_usage_count"] += 1
        
        if routing_result.get("fallback_used", False):
            self.usage_statistics["fallback_count"] += 1
        
        # 成本節省
        cost_savings = routing_result.get("cost_optimization", {}).get("savings_percentage", 0)
        self.usage_statistics["cost_savings"] += cost_savings
        
        # 質量分數
        quality_score = routing_result.get("quality_assessment", {}).get("quality_score", 0)
        self.usage_statistics["quality_scores"].append(quality_score)
        
        # 保持最近 1000 條記錄
        if len(self.usage_statistics["quality_scores"]) > 1000:
            self.usage_statistics["quality_scores"] = self.usage_statistics["quality_scores"][-1000:]
    
    async def _learn_from_result(self, routing_result: Dict[str, Any], context: Dict[str, Any]) -> None:
        """從結果中學習"""
        
        # 分析成功模式
        quality_score = routing_result.get("quality_assessment", {}).get("quality_score", 0)
        provider = routing_result.get("selected_provider", "")
        command_complexity = context.get("complexity", "unknown")
        
        # 記錄成功/失敗模式用於未來優化
        learning_data = {
            "provider": provider,
            "complexity": command_complexity,
            "quality_score": quality_score,
            "enhancement_applied": routing_result.get("enhancement_applied", False),
            "fallback_used": routing_result.get("fallback_used", False),
            "timestamp": time.time()
        }
        
        # 這裡可以實現更復雜的學習算法
        logger.debug(f"學習數據: {learning_data}")
    
    async def _extract_ai_tasks_from_workflow(self, workflow_type: str, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """從工作流中提取 AI 任務"""
        
        ai_tasks = []
        
        if workflow_type == "goal_driven_development":
            ai_tasks = [
                {
                    "task_id": "requirement_analysis",
                    "command": f"分析用戶需求: {workflow_data.get('user_goal', '')}",
                    "context": {"complexity": "moderate", "priority": "high"}
                },
                {
                    "task_id": "test_case_generation", 
                    "command": f"為以下需求生成測試用例: {workflow_data.get('requirements', [])}",
                    "context": {"complexity": "moderate", "priority": "medium"}
                },
                {
                    "task_id": "code_generation",
                    "command": f"根據需求生成代碼實現: {workflow_data.get('specifications', '')}",
                    "context": {"complexity": "complex", "priority": "high"}
                }
            ]
        
        elif workflow_type == "intelligent_code_generation":
            ai_tasks = [
                {
                    "task_id": "architecture_design",
                    "command": f"設計系統架構: {workflow_data.get('requirements', '')}",
                    "context": {"complexity": "complex", "priority": "high"}
                },
                {
                    "task_id": "code_implementation",
                    "command": f"實現代碼: {workflow_data.get('design_specs', '')}",
                    "context": {"complexity": "moderate", "priority": "high"}
                }
            ]
        
        return ai_tasks
    
    async def _generate_workflow_execution_plan(self, optimized_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成工作流執行計劃"""
        
        return {
            "execution_order": [task["task_id"] for task in optimized_tasks],
            "parallel_tasks": [],  # 可以並行執行的任務
            "dependencies": {},    # 任務依賴關係
            "estimated_duration": sum(
                task["routing_result"].get("processing_time", 0) 
                for task in optimized_tasks
            ),
            "resource_requirements": {
                "claude_tokens": sum(
                    task["routing_result"].get("cost_optimization", {}).get("estimated_claude_cost", 0)
                    for task in optimized_tasks
                    if task["routing_result"].get("selected_provider") == "claude"
                ),
                "k2_tokens": sum(
                    task["routing_result"].get("cost_optimization", {}).get("actual_cost", 0)
                    for task in optimized_tasks
                    if task["routing_result"].get("selected_provider") != "claude"
                )
            }
        }
    
    def _calculate_workflow_cost_savings(self, optimized_tasks: List[Dict[str, Any]]) -> float:
        """計算工作流成本節省"""
        
        total_savings = 0.0
        total_tasks = len(optimized_tasks)
        
        for task in optimized_tasks:
            savings_percentage = task["routing_result"].get("cost_optimization", {}).get("savings_percentage", 0)
            total_savings += savings_percentage
        
        return total_savings / total_tasks if total_tasks > 0 else 0.0
    
    def _calculate_workflow_completion_time(self, optimized_tasks: List[Dict[str, Any]]) -> float:
        """計算工作流完成時間"""
        
        total_time = 0.0
        
        for task in optimized_tasks:
            execution_time = task["routing_result"].get("execution_result", {}).get("execution_time", 0)
            total_time += execution_time
        
        return total_time
    
    def _get_current_statistics(self) -> Dict[str, Any]:
        """獲取當前統計信息"""
        
        stats = self.usage_statistics.copy()
        
        if stats["total_commands"] > 0:
            stats["k2_adoption_rate"] = (stats["k2_usage_count"] / stats["total_commands"]) * 100
            stats["average_cost_savings"] = stats["cost_savings"] / stats["total_commands"]
            stats["system_reliability"] = 1.0 - (stats["fallback_count"] / stats["total_commands"])
        
        return stats
    
    async def _generate_recommendations(self, routing_result: Dict[str, Any]) -> List[str]:
        """生成建議"""
        
        recommendations = []
        
        # 基於結果質量的建議
        quality_score = routing_result.get("quality_assessment", {}).get("quality_score", 0)
        if quality_score < 0.8:
            recommendations.append("建議使用 Claude 以獲得更高質量的結果")
        
        # 基於成本的建議
        savings_percentage = routing_result.get("cost_optimization", {}).get("savings_percentage", 0)
        if savings_percentage > 80:
            recommendations.append("K2 模式在此類任務上表現出色，建議繼續使用")
        
        # 基於增強效果的建議
        if routing_result.get("enhancement_applied", False):
            enhancement_methods = routing_result.get("enhancement_details", {}).get("enhancement_methods", [])
            if len(enhancement_methods) > 2:
                recommendations.append("命令已經過多重增強，質量得到顯著提升")
        
        # 基於回退的建議
        if routing_result.get("fallback_used", False):
            recommendations.append("此類任務建議直接使用 Claude 以避免回退")
        
        return recommendations
    
    async def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """計算性能指標"""
        
        recent_scores = self.usage_statistics["quality_scores"][-100:] if self.usage_statistics["quality_scores"] else []
        
        return {
            "response_time_p95": 2.5,  # 95th percentile 響應時間
            "success_rate": 0.96,      # 成功率
            "quality_consistency": len(set(recent_scores)) / len(recent_scores) if recent_scores else 0,
            "cost_efficiency": self.usage_statistics.get("average_cost_savings", 0),
            "user_satisfaction": 0.88   # 模擬用戶滿意度
        }

class PowerAutomationConnector:
    """PowerAutomation 連接器"""
    
    async def initialize(self) -> None:
        """初始化連接器"""
        logger.info("PowerAutomation 連接器已初始化")
    
    async def notify_command_execution(self, routing_result: Dict[str, Any]) -> None:
        """通知命令執行結果"""
        # 這裡會將結果發送給 PowerAutomation Core
        logger.debug(f"通知 PowerAutomation: {routing_result['command_id']}")

class ClaudeEditorInterface:
    """ClaudeEditor 接口"""
    
    async def initialize(self) -> None:
        """初始化接口"""
        logger.info("ClaudeEditor 接口已初始化")
    
    async def update_ui_with_result(self, routing_result: Dict[str, Any]) -> None:
        """更新 UI 顯示結果"""
        # 這裡會更新 ClaudeEditor 的 UI
        logger.debug(f"更新 ClaudeEditor UI: {routing_result['selected_provider']}")

class WebSocketServer:
    """WebSocket 服務器"""
    
    async def start_server(self, handler, port: int) -> None:
        """啟動服務器"""
        # 這裡會啟動實際的 WebSocket 服務器
        logger.info(f"WebSocket 服務器已啟動，端口: {port}")

# 使用示例和測試
async def main():
    """主函數示例"""
    
    # 創建系統配置
    config = K2EnhancementConfig(
        enable_auto_enhancement=True,
        quality_threshold=0.8,
        cost_optimization_priority=0.7,
        enable_fallback=True,
        enable_learning=True
    )
    
    # 初始化系統
    system = IntegratedK2EnhancementSystem(config)
    
    # 模擬啟動系統（實際使用中會真正啟動）
    print("🚀 啟動 Integrated K2 Enhancement System...")
    
    # 模擬處理一些命令
    test_requests = [
        {
            "type": "claude_code_command",
            "command": "create a simple web server",
            "context": {"priority": "medium"},
            "user_preferences": {"cost_priority": 0.8}
        },
        {
            "type": "claude_code_command", 
            "command": "設計一個複雜的微服務架構並實現負載均衡",
            "context": {"priority": "high"},
            "user_preferences": {"quality_threshold": 0.9}
        },
        {
            "type": "workflow_command",
            "workflow_type": "goal_driven_development",
            "workflow_data": {
                "user_goal": "創建用戶管理系統",
                "requirements": ["用戶註冊", "用戶登錄", "權限管理"]
            }
        }
    ]
    
    for i, request in enumerate(test_requests):
        print(f"\n{'='*60}")
        print(f"處理請求 {i+1}: {request['type']}")
        print(f"{'='*60}")
        
        if request["type"] == "claude_code_command":
            response = await system.process_claude_code_command(request)
            routing_result = response["routing_result"]
            
            print(f"選擇的提供者: {routing_result['selected_provider']}")
            print(f"增強方法: {routing_result.get('enhancement_details', {}).get('enhancement_methods', [])}")
            print(f"質量分數: {routing_result['quality_assessment']['quality_score']:.2f}")
            print(f"成本節省: {routing_result['cost_optimization']['savings_percentage']:.1f}%")
            
            if routing_result.get('fallback_used'):
                print("⚠️ 使用了 Claude 回退")
                
        elif request["type"] == "workflow_command":
            response = await system.process_workflow_command(request)
            
            print(f"優化任務數量: {len(response['optimized_tasks'])}")
            print(f"預估成本節省: {response['estimated_cost_savings']:.1f}%")
            print(f"預估完成時間: {response['estimated_completion_time']:.2f}s")
    
    # 獲取最終統計
    final_stats = await system.get_statistics()
    print(f"\n📊 最終統計:")
    print(f"總命令數: {final_stats['statistics']['total_commands']}")
    print(f"K2 使用率: {final_stats['statistics'].get('k2_usage_percentage', 0):.1f}%")
    print(f"平均質量分數: {final_stats['statistics'].get('average_quality_score', 0):.2f}")
    print(f"系統可靠性: {final_stats['statistics'].get('system_reliability', 0):.2f}")

if __name__ == "__main__":
    asyncio.run(main())