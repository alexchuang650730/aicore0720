#!/usr/bin/env python3
"""
多MCP協作集成方案 - 增強K2工具調用體驗
PowerAutomation v4.6.9 - 集成Zen、Trae Agent、X-Masters和Smart Tool Engine

這個集成方案展示如何將四個強大的MCP組件協同工作：
1. Zen MCP - 工作流編排和執行
2. Trae Agent MCP - 智能代理協作
3. X-Masters MCP - 深度推理兜底
4. Smart Tool Engine MCP - 統一工具發現和路由

通過多MCP協作，為K2提供更強大的工具調用能力。
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

# 導入各個MCP組件
from zen_mcp.zen_workflow_engine import ZenWorkflowEngine, WorkflowDefinition, WorkflowTask, ExecutionStrategy
from trae_agent_mcp.trae_agent_manager import TraeAgentMCPManager
from xmasters_mcp.xmasters_manager import XMastersMCPManager, ProblemDomain

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """任務複雜度"""
    SIMPLE = "simple"          # 簡單任務 - 直接執行
    MEDIUM = "medium"          # 中等任務 - 需要工作流
    COMPLEX = "complex"        # 複雜任務 - 需要多代理協作
    EXTREME = "extreme"        # 極端任務 - 需要深度推理


class IntegrationMode(Enum):
    """集成模式"""
    WORKFLOW_FIRST = "workflow_first"      # 工作流優先
    AGENT_FIRST = "agent_first"           # 代理優先
    REASONING_FIRST = "reasoning_first"    # 推理優先
    ADAPTIVE = "adaptive"                 # 自適應選擇


@dataclass
class K2Request:
    """K2增強請求"""
    request_id: str
    user_query: str
    context: Dict[str, Any]
    tools_available: List[str]
    complexity: TaskComplexity = TaskComplexity.MEDIUM
    mode: IntegrationMode = IntegrationMode.ADAPTIVE
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass  
class K2Response:
    """K2增強響應"""
    request_id: str
    result: Any
    execution_path: List[str]
    tools_used: List[str]
    agents_involved: List[str]
    workflows_executed: List[str]
    reasoning_applied: bool
    confidence: float
    duration: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MultiMCPIntegrationEngine:
    """多MCP協作集成引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 初始化各個MCP組件
        self.zen_engine = ZenWorkflowEngine()
        self.trae_manager = TraeAgentMCPManager()
        self.xmasters_manager = XMastersMCPManager()
        
        # Smart Tool Engine配置（模擬）
        self.smart_tool_config = {
            "aci_dev": {"enabled": True, "priority": 1},
            "mcp_so": {"enabled": True, "priority": 2},
            "zapier": {"enabled": True, "priority": 3}
        }
        
        # 執行統計
        self.execution_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_confidence": 0.0,
            "mcp_usage": {
                "zen": 0,
                "trae": 0,
                "xmasters": 0,
                "smart_tool": 0
            }
        }
    
    async def initialize(self):
        """初始化集成引擎"""
        self.logger.info("🚀 初始化多MCP協作集成引擎")
        
        # 並行初始化所有MCP
        await asyncio.gather(
            self.zen_engine.initialize(),
            self.trae_manager.initialize(),
            self.xmasters_manager.initialize(),
            self._initialize_smart_tool_engine()
        )
        
        # 創建集成工作流
        await self._create_integration_workflows()
        
        self.logger.info("✅ 多MCP協作集成引擎初始化完成")
    
    async def _initialize_smart_tool_engine(self):
        """初始化Smart Tool Engine（模擬）"""
        self.logger.info("🔧 初始化Smart Tool Engine集成")
        # 這裡模擬Smart Tool Engine的初始化
        # 實際應該導入並初始化smart_tool_engine_mcp
        await asyncio.sleep(0.1)
    
    async def _create_integration_workflows(self):
        """創建集成工作流"""
        # 創建K2增強工作流
        k2_enhancement_workflow = WorkflowDefinition(
            workflow_id="k2_enhancement_workflow",
            name="K2工具調用增強工作流",
            description="通過多MCP協作增強K2的工具調用能力",
            tasks=[
                WorkflowTask(
                    task_id="analyze_request",
                    tool_name="request_analyzer",
                    parameters={"action": "analyze_complexity"},
                    dependencies=[]
                ),
                WorkflowTask(
                    task_id="discover_tools",
                    tool_name="smart_tool_discovery",
                    parameters={"action": "discover", "platforms": ["aci.dev", "mcp.so", "zapier"]},
                    dependencies=["analyze_request"]
                ),
                WorkflowTask(
                    task_id="route_to_mcp",
                    tool_name="mcp_router",
                    parameters={"action": "route"},
                    dependencies=["discover_tools"]
                ),
                WorkflowTask(
                    task_id="execute_task",
                    tool_name="task_executor",
                    parameters={"action": "execute"},
                    dependencies=["route_to_mcp"]
                ),
                WorkflowTask(
                    task_id="integrate_results",
                    tool_name="result_integrator",
                    parameters={"action": "integrate"},
                    dependencies=["execute_task"]
                )
            ],
            strategy=ExecutionStrategy.ADAPTIVE
        )
        
        await self.zen_engine.register_workflow(k2_enhancement_workflow)
        
        # 創建深度推理工作流
        deep_reasoning_workflow = WorkflowDefinition(
            workflow_id="deep_reasoning_workflow",
            name="深度推理協作工作流",
            description="複雜問題的多智能體深度推理",
            tasks=[
                WorkflowTask(
                    task_id="problem_decomposition",
                    tool_name="problem_analyzer",
                    parameters={"action": "decompose"},
                    dependencies=[]
                ),
                WorkflowTask(
                    task_id="agent_assignment",
                    tool_name="agent_coordinator",
                    parameters={"action": "assign_agents"},
                    dependencies=["problem_decomposition"]
                ),
                WorkflowTask(
                    task_id="parallel_reasoning",
                    tool_name="reasoning_engine",
                    parameters={"action": "parallel_reason"},
                    dependencies=["agent_assignment"]
                ),
                WorkflowTask(
                    task_id="result_synthesis",
                    tool_name="result_synthesizer",
                    parameters={"action": "synthesize"},
                    dependencies=["parallel_reasoning"]
                )
            ],
            strategy=ExecutionStrategy.PARALLEL
        )
        
        await self.zen_engine.register_workflow(deep_reasoning_workflow)
    
    async def process_k2_request(self, request: K2Request) -> K2Response:
        """處理K2增強請求"""
        start_time = datetime.now()
        
        response = K2Response(
            request_id=request.request_id,
            result=None,
            execution_path=[],
            tools_used=[],
            agents_involved=[],
            workflows_executed=[],
            reasoning_applied=False,
            confidence=0.0,
            duration=0.0
        )
        
        try:
            self.execution_stats["total_requests"] += 1
            
            # 1. 分析請求複雜度
            complexity_analysis = await self._analyze_request_complexity(request)
            response.execution_path.append("complexity_analysis")
            
            # 2. 根據複雜度和模式選擇執行路徑
            if request.mode == IntegrationMode.ADAPTIVE:
                execution_path = await self._determine_execution_path(request, complexity_analysis)
            else:
                execution_path = request.mode
            
            # 3. 執行相應的處理流程
            if execution_path == IntegrationMode.WORKFLOW_FIRST:
                result = await self._execute_workflow_path(request, response)
            elif execution_path == IntegrationMode.AGENT_FIRST:
                result = await self._execute_agent_path(request, response)
            elif execution_path == IntegrationMode.REASONING_FIRST:
                result = await self._execute_reasoning_path(request, response)
            else:
                result = await self._execute_adaptive_path(request, response)
            
            response.result = result
            response.confidence = await self._calculate_confidence(response)
            
            # 更新統計
            self.execution_stats["successful_requests"] += 1
            self._update_stats(response)
            
        except Exception as e:
            self.logger.error(f"處理K2請求失敗: {e}")
            response.result = {"error": str(e)}
            self.execution_stats["failed_requests"] += 1
        
        finally:
            end_time = datetime.now()
            response.duration = (end_time - start_time).total_seconds()
        
        return response
    
    async def _analyze_request_complexity(self, request: K2Request) -> Dict[str, Any]:
        """分析請求複雜度"""
        # 使用Smart Tool Engine進行初步分析
        response.execution_path.append("smart_tool_analysis")
        self.execution_stats["mcp_usage"]["smart_tool"] += 1
        
        # 分析關鍵指標
        query_length = len(request.user_query)
        tool_count = len(request.tools_available)
        context_complexity = len(str(request.context))
        
        # 計算複雜度分數
        complexity_score = (
            (query_length / 100) * 0.3 +
            (tool_count / 10) * 0.3 +
            (context_complexity / 1000) * 0.4
        )
        
        return {
            "score": complexity_score,
            "recommended_path": self._recommend_path(complexity_score),
            "estimated_time": complexity_score * 10,
            "tool_availability": await self._check_tool_availability(request.tools_available)
        }
    
    async def _check_tool_availability(self, tools: List[str]) -> Dict[str, bool]:
        """檢查工具可用性（通過Smart Tool Engine）"""
        # 模擬檢查各平台工具可用性
        availability = {}
        for tool in tools:
            # 實際應該調用Smart Tool Engine的API
            availability[tool] = True  # 模擬所有工具都可用
        return availability
    
    def _recommend_path(self, complexity_score: float) -> IntegrationMode:
        """根據複雜度推薦執行路徑"""
        if complexity_score < 0.3:
            return IntegrationMode.WORKFLOW_FIRST
        elif complexity_score < 0.6:
            return IntegrationMode.AGENT_FIRST
        elif complexity_score < 0.8:
            return IntegrationMode.REASONING_FIRST
        else:
            return IntegrationMode.ADAPTIVE
    
    async def _determine_execution_path(self, request: K2Request, 
                                      analysis: Dict[str, Any]) -> IntegrationMode:
        """確定執行路徑"""
        # 基於分析結果和請求特徵動態決定
        if "mathematical" in request.user_query.lower() or "prove" in request.user_query.lower():
            return IntegrationMode.REASONING_FIRST
        elif len(request.tools_available) > 5:
            return IntegrationMode.WORKFLOW_FIRST
        elif "collaborate" in request.user_query.lower() or "multiple" in request.user_query.lower():
            return IntegrationMode.AGENT_FIRST
        else:
            return analysis["recommended_path"]
    
    async def _execute_workflow_path(self, request: K2Request, response: K2Response) -> Dict[str, Any]:
        """執行工作流路徑"""
        response.execution_path.append("zen_workflow_execution")
        self.execution_stats["mcp_usage"]["zen"] += 1
        
        # 使用Zen MCP執行工作流
        execution_id = await self.zen_engine.execute_workflow(
            "k2_enhancement_workflow",
            {"request": asdict(request)}
        )
        
        response.workflows_executed.append("k2_enhancement_workflow")
        
        # 等待執行完成
        await asyncio.sleep(2.0)  # 模擬執行時間
        
        # 獲取執行結果
        execution = await self.zen_engine.get_execution_status(execution_id)
        
        if execution and execution.status.value == "completed":
            # 提取使用的工具
            for task in self.zen_engine.workflows["k2_enhancement_workflow"].tasks:
                if task.status.value == "completed":
                    response.tools_used.append(task.tool_name)
            
            return {
                "status": "success",
                "workflow_result": "工作流執行成功",
                "tasks_completed": execution.completed_tasks,
                "execution_time": execution.execution_time
            }
        else:
            return {"status": "failed", "error": "工作流執行失敗"}
    
    async def _execute_agent_path(self, request: K2Request, response: K2Response) -> Dict[str, Any]:
        """執行代理協作路徑"""
        response.execution_path.append("trae_agent_collaboration")
        self.execution_stats["mcp_usage"]["trae"] += 1
        
        # 創建協作任務
        task_id = await self.trae_manager.create_task(
            title=f"K2增強任務: {request.user_query[:50]}...",
            description=request.user_query,
            required_capabilities=self._extract_required_capabilities(request),
            priority=self._calculate_priority(request)
        )
        
        # 等待任務完成
        await asyncio.sleep(3.0)  # 模擬執行時間
        
        # 獲取任務結果
        task_status = await self.trae_manager.get_task_status(task_id)
        
        if task_status and task_status["status"] == "completed":
            # 記錄參與的代理
            if task_status["assigned_agent"]:
                agent_info = await self.trae_manager.get_agent_status(task_status["assigned_agent"])
                if agent_info:
                    response.agents_involved.append(agent_info["name"])
            
            return {
                "status": "success",
                "agent_result": task_status["result"],
                "collaboration_type": "multi_agent"
            }
        else:
            return {"status": "failed", "error": "代理協作失敗"}
    
    async def _execute_reasoning_path(self, request: K2Request, response: K2Response) -> Dict[str, Any]:
        """執行深度推理路徑"""
        response.execution_path.append("xmasters_deep_reasoning")
        response.reasoning_applied = True
        self.execution_stats["mcp_usage"]["xmasters"] += 1
        
        # 使用X-Masters進行深度推理
        reasoning_result = await self.xmasters_manager.solve_complex_problem(
            problem=request.user_query,
            domain=self._identify_domain(request),
            complexity=self._estimate_complexity_level(request)
        )
        
        if reasoning_result.status.value == "completed":
            # 記錄使用的工具和代理
            response.tools_used.extend(reasoning_result.tools_used)
            response.agents_involved.extend(reasoning_result.agents_involved)
            
            return {
                "status": "success",
                "reasoning_result": reasoning_result.solution,
                "confidence": reasoning_result.confidence,
                "reasoning_steps": len(reasoning_result.reasoning_steps),
                "duration": reasoning_result.duration
            }
        else:
            return {"status": "failed", "error": "深度推理失敗"}
    
    async def _execute_adaptive_path(self, request: K2Request, response: K2Response) -> Dict[str, Any]:
        """執行自適應路徑 - 結合多個MCP"""
        response.execution_path.append("adaptive_multi_mcp")
        
        results = {}
        
        # 1. 先使用Smart Tool Engine發現和路由工具
        tool_discovery = await self._discover_and_route_tools(request)
        response.tools_used.extend(tool_discovery.get("tools", []))
        results["tool_discovery"] = tool_discovery
        
        # 2. 創建動態工作流
        if tool_discovery.get("complexity", "medium") == "high":
            # 複雜任務：使用Trae Agent進行並行處理
            agent_result = await self._execute_agent_path(request, response)
            results["agent_collaboration"] = agent_result
        
        # 3. 如果需要深度推理，調用X-Masters
        if self._needs_deep_reasoning(request):
            reasoning_result = await self._execute_reasoning_path(request, response)
            results["deep_reasoning"] = reasoning_result
        
        # 4. 使用Zen整合所有結果
        integration_workflow = await self._create_dynamic_integration_workflow(results)
        workflow_result = await self._execute_workflow_path(request, response)
        results["workflow_integration"] = workflow_result
        
        return {
            "status": "success",
            "integrated_result": results,
            "mcp_used": len([mcp for mcp in response.execution_path if "mcp" in mcp]),
            "adaptive_strategy": "multi_mcp_collaboration"
        }
    
    async def _discover_and_route_tools(self, request: K2Request) -> Dict[str, Any]:
        """通過Smart Tool Engine發現和路由工具"""
        # 模擬Smart Tool Engine的工具發現
        discovered_tools = []
        
        # 檢查各平台
        if self.smart_tool_config["aci_dev"]["enabled"]:
            discovered_tools.extend(["aci_tool1", "aci_tool2"])
        if self.smart_tool_config["mcp_so"]["enabled"]:
            discovered_tools.extend(["mcp_tool1", "mcp_tool2"])
        if self.smart_tool_config["zapier"]["enabled"]:
            discovered_tools.extend(["zapier_automation"])
        
        return {
            "tools": discovered_tools,
            "complexity": "medium" if len(discovered_tools) < 5 else "high",
            "routing_strategy": "intelligent_routing"
        }
    
    def _extract_required_capabilities(self, request: K2Request) -> List[str]:
        """提取所需能力"""
        capabilities = []
        
        # 基於查詢內容提取能力需求
        query_lower = request.user_query.lower()
        
        if "code" in query_lower or "program" in query_lower:
            capabilities.append("code_generation")
        if "test" in query_lower:
            capabilities.append("test_automation")
        if "design" in query_lower:
            capabilities.append("ui_design")
        if "security" in query_lower:
            capabilities.append("security_audit")
        
        # 基於可用工具提取能力
        for tool in request.tools_available:
            if "api" in tool.lower():
                capabilities.append("api_integration")
            if "data" in tool.lower():
                capabilities.append("data_processing")
        
        return capabilities or ["general_processing"]
    
    def _calculate_priority(self, request: K2Request) -> int:
        """計算任務優先級"""
        # 基於複雜度計算優先級
        priority_map = {
            TaskComplexity.SIMPLE: 1,
            TaskComplexity.MEDIUM: 5,
            TaskComplexity.COMPLEX: 8,
            TaskComplexity.EXTREME: 10
        }
        return priority_map.get(request.complexity, 5)
    
    def _identify_domain(self, request: K2Request) -> str:
        """識別問題領域"""
        query_lower = request.user_query.lower()
        
        if any(keyword in query_lower for keyword in ["math", "equation", "calculate", "solve"]):
            return "mathematics"
        elif any(keyword in query_lower for keyword in ["physics", "force", "energy", "motion"]):
            return "physics"
        elif any(keyword in query_lower for keyword in ["code", "program", "algorithm", "software"]):
            return "computer_science"
        elif any(keyword in query_lower for keyword in ["biology", "cell", "gene", "organism"]):
            return "biology"
        else:
            return "interdisciplinary"
    
    def _estimate_complexity_level(self, request: K2Request) -> int:
        """估計複雜度級別（1-10）"""
        complexity_map = {
            TaskComplexity.SIMPLE: 2,
            TaskComplexity.MEDIUM: 5,
            TaskComplexity.COMPLEX: 7,
            TaskComplexity.EXTREME: 9
        }
        return complexity_map.get(request.complexity, 5)
    
    def _needs_deep_reasoning(self, request: K2Request) -> bool:
        """判斷是否需要深度推理"""
        # 基於查詢內容和複雜度判斷
        indicators = ["prove", "explain", "why", "how does", "analyze", "reason"]
        query_lower = request.user_query.lower()
        
        return (
            request.complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXTREME] or
            any(indicator in query_lower for indicator in indicators)
        )
    
    async def _create_dynamic_integration_workflow(self, results: Dict[str, Any]) -> WorkflowDefinition:
        """創建動態集成工作流"""
        tasks = []
        
        # 根據已執行的結果創建集成任務
        task_id = 0
        dependencies = []
        
        for component, result in results.items():
            if result.get("status") == "success":
                task = WorkflowTask(
                    task_id=f"integrate_{component}_{task_id}",
                    tool_name="result_processor",
                    parameters={"component": component, "data": result},
                    dependencies=dependencies.copy()
                )
                tasks.append(task)
                dependencies.append(task.task_id)
                task_id += 1
        
        # 添加最終整合任務
        tasks.append(WorkflowTask(
            task_id="final_integration",
            tool_name="final_integrator",
            parameters={"action": "synthesize_all"},
            dependencies=dependencies
        ))
        
        workflow = WorkflowDefinition(
            workflow_id=f"dynamic_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="動態集成工作流",
            description="根據執行結果動態創建的集成工作流",
            tasks=tasks,
            strategy=ExecutionStrategy.SEQUENTIAL
        )
        
        await self.zen_engine.register_workflow(workflow)
        return workflow
    
    async def _calculate_confidence(self, response: K2Response) -> float:
        """計算整體置信度"""
        confidence_factors = []
        
        # 基於執行路徑計算
        path_confidence = {
            "complexity_analysis": 0.9,
            "smart_tool_analysis": 0.85,
            "zen_workflow_execution": 0.9,
            "trae_agent_collaboration": 0.85,
            "xmasters_deep_reasoning": 0.95,
            "adaptive_multi_mcp": 0.92
        }
        
        for path in response.execution_path:
            confidence_factors.append(path_confidence.get(path, 0.8))
        
        # 基於使用的組件數量
        component_count = len(set(response.execution_path))
        if component_count > 3:
            confidence_factors.append(0.95)
        elif component_count > 1:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.85)
        
        # 如果應用了深度推理，增加置信度
        if response.reasoning_applied:
            confidence_factors.append(0.95)
        
        # 計算平均置信度
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.8
    
    def _update_stats(self, response: K2Response):
        """更新執行統計"""
        # 更新平均置信度
        total_requests = self.execution_stats["successful_requests"]
        if total_requests > 0:
            current_avg = self.execution_stats["average_confidence"]
            new_avg = (current_avg * (total_requests - 1) + response.confidence) / total_requests
            self.execution_stats["average_confidence"] = new_avg
    
    def get_status(self) -> Dict[str, Any]:
        """獲取集成引擎狀態"""
        return {
            "component": "Multi-MCP Integration Engine",
            "version": "4.6.9",
            "status": "running",
            "integrated_mcps": {
                "zen": self.zen_engine.get_status(),
                "trae": self.trae_manager.get_status(),
                "xmasters": self.xmasters_manager.get_status(),
                "smart_tool": {
                    "status": "configured",
                    "platforms": list(self.smart_tool_config.keys())
                }
            },
            "execution_stats": self.execution_stats,
            "capabilities": [
                "multi_mcp_orchestration",
                "adaptive_execution",
                "tool_discovery_routing",
                "workflow_management",
                "agent_collaboration",
                "deep_reasoning",
                "intelligent_integration"
            ]
        }


# 使用示例
async def demo_multi_mcp_integration():
    """演示多MCP協作集成"""
    logger.info("=" * 80)
    logger.info("🚀 K2工具調用增強 - 多MCP協作演示")
    logger.info("=" * 80)
    
    # 初始化集成引擎
    engine = MultiMCPIntegrationEngine()
    await engine.initialize()
    
    # 示例1：簡單任務 - 工作流處理
    logger.info("\n📋 示例1：簡單任務處理")
    simple_request = K2Request(
        request_id="k2_req_001",
        user_query="幫我生成一個Python函數來計算斐波那契數列",
        context={"language": "python", "level": "beginner"},
        tools_available=["code_generator", "formatter", "validator"],
        complexity=TaskComplexity.SIMPLE
    )
    
    simple_response = await engine.process_k2_request(simple_request)
    logger.info(f"執行路徑: {' -> '.join(simple_response.execution_path)}")
    logger.info(f"使用工具: {simple_response.tools_used}")
    logger.info(f"置信度: {simple_response.confidence:.2%}")
    
    # 示例2：中等複雜任務 - 代理協作
    logger.info("\n🤝 示例2：多代理協作任務")
    medium_request = K2Request(
        request_id="k2_req_002",
        user_query="創建一個完整的Web應用，包括前端UI、後端API和數據庫設計",
        context={"framework": "react", "backend": "fastapi", "database": "postgresql"},
        tools_available=["ui_designer", "api_generator", "db_designer", "test_generator"],
        complexity=TaskComplexity.MEDIUM
    )
    
    medium_response = await engine.process_k2_request(medium_request)
    logger.info(f"參與代理: {medium_response.agents_involved}")
    logger.info(f"執行工作流: {medium_response.workflows_executed}")
    
    # 示例3：複雜任務 - 深度推理
    logger.info("\n🧠 示例3：深度推理任務")
    complex_request = K2Request(
        request_id="k2_req_003",
        user_query="證明對於任意正整數n，1³ + 2³ + ... + n³ = (1 + 2 + ... + n)²",
        context={"type": "mathematical_proof", "field": "number_theory"},
        tools_available=["wolfram_alpha", "proof_assistant", "latex_generator"],
        complexity=TaskComplexity.COMPLEX
    )
    
    complex_response = await engine.process_k2_request(complex_request)
    logger.info(f"應用推理: {complex_response.reasoning_applied}")
    logger.info(f"執行時間: {complex_response.duration:.2f}秒")
    
    # 示例4：極端複雜任務 - 自適應多MCP協作
    logger.info("\n🎯 示例4：自適應多MCP協作")
    extreme_request = K2Request(
        request_id="k2_req_004",
        user_query="設計並實現一個AI驅動的自動化測試系統，能夠理解需求文檔，生成測試用例，執行測試並分析結果",
        context={
            "requirements": "複雜的企業級應用",
            "technologies": ["ai", "nlp", "automation", "testing"],
            "scale": "large"
        },
        tools_available=[
            "nlp_analyzer", "test_case_generator", "code_generator",
            "test_executor", "report_generator", "ai_model", "workflow_engine"
        ],
        complexity=TaskComplexity.EXTREME,
        mode=IntegrationMode.ADAPTIVE
    )
    
    extreme_response = await engine.process_k2_request(extreme_request)
    logger.info(f"執行路徑: {' -> '.join(extreme_response.execution_path)}")
    logger.info(f"使用MCPs: {len(set([p for p in extreme_response.execution_path if 'mcp' in p]))}")
    logger.info(f"總體置信度: {extreme_response.confidence:.2%}")
    
    # 顯示集成統計
    logger.info("\n📊 集成引擎統計")
    status = engine.get_status()
    logger.info(f"總請求數: {status['execution_stats']['total_requests']}")
    logger.info(f"成功率: {status['execution_stats']['successful_requests'] / status['execution_stats']['total_requests']:.2%}")
    logger.info(f"MCP使用統計: {status['execution_stats']['mcp_usage']}")
    logger.info(f"平均置信度: {status['execution_stats']['average_confidence']:.2%}")
    
    logger.info("\n✅ 多MCP協作演示完成！")
    logger.info("=" * 80)


# 集成架構優勢總結
def print_integration_benefits():
    """打印集成架構的優勢"""
    benefits = """
    🎯 多MCP協作集成架構優勢：
    
    1. 智能任務路由
       - 根據任務複雜度自動選擇最優執行路徑
       - Smart Tool Engine提供統一的工具發現和路由
    
    2. 協同增效
       - Zen MCP：工作流編排，確保任務有序執行
       - Trae Agent MCP：多代理協作，並行處理複雜任務
       - X-Masters MCP：深度推理，解決高難度問題
       - Smart Tool Engine：跨平台工具集成
    
    3. 自適應執行
       - 動態調整執行策略
       - 根據中間結果優化後續步驟
    
    4. 全面的工具支持
       - 集成ACI.dev、MCP.so、Zapier等多個平台
       - 統一的工具調用接口
    
    5. 高置信度結果
       - 多維度驗證
       - 深度推理支持
       - 結果可解釋性
    
    6. 可擴展架構
       - 易於添加新的MCP組件
       - 支持自定義工作流和策略
    
    通過這種多MCP協作，K2能夠處理從簡單到極其複雜的各種任務，
    提供更智能、更可靠的工具調用體驗。
    """
    print(benefits)


if __name__ == "__main__":
    # 配置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 運行演示
    asyncio.run(demo_multi_mcp_integration())
    
    # 顯示集成優勢
    print_integration_benefits()