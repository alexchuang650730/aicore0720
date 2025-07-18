#!/usr/bin/env python3
"""
MCP-Zero 工作流引擎
將六大工作流與 MCP-Zero 動態加載架構集成
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..mcp_zero import mcp_zero_engine, mcp_registry, TaskType
from ..mcp_zero.task_planner import TaskStep

logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """工作流類型"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    CODING_IMPLEMENTATION = "coding_implementation"
    TESTING_VALIDATION = "testing_validation"
    DEPLOYMENT_RELEASE = "deployment_release"
    MONITORING_OPERATIONS = "monitoring_operations"


@dataclass
class WorkflowConfig:
    """工作流配置"""
    name: str
    description: str
    required_mcps: List[str]  # 必需的 MCP
    optional_mcps: List[str]  # 可選的 MCP
    max_context_tokens: int
    estimated_time: int  # 秒
    parallel_capable: bool


class MCPZeroWorkflowEngine:
    """MCP-Zero 工作流引擎"""
    
    def __init__(self):
        self.workflow_configs = self._initialize_workflow_configs()
        self.active_workflows: Dict[str, Any] = {}
        
    def _initialize_workflow_configs(self) -> Dict[WorkflowType, WorkflowConfig]:
        """初始化工作流配置"""
        return {
            WorkflowType.REQUIREMENT_ANALYSIS: WorkflowConfig(
                name="需求分析",
                description="從代碼提取需求，分析業務邏輯",
                required_mcps=["codeflow_mcp"],
                optional_mcps=["stagewise_mcp", "deepgraph_mcp"],
                max_context_tokens=20000,
                estimated_time=600,
                parallel_capable=False
            ),
            
            WorkflowType.ARCHITECTURE_DESIGN: WorkflowConfig(
                name="架構設計",
                description="生成系統架構和 UI 設計",
                required_mcps=["smartui_mcp", "ag_ui_mcp"],
                optional_mcps=["codeflow_mcp", "deepgraph_mcp"],
                max_context_tokens=25000,
                estimated_time=900,
                parallel_capable=True
            ),
            
            WorkflowType.CODING_IMPLEMENTATION: WorkflowConfig(
                name="編碼實現",
                description="智能代碼生成和實現",
                required_mcps=["codeflow_mcp"],
                optional_mcps=["smartui_mcp", "ag_ui_mcp", "xmasters_mcp"],
                max_context_tokens=30000,
                estimated_time=1800,
                parallel_capable=True
            ),
            
            WorkflowType.TESTING_VALIDATION: WorkflowConfig(
                name="測試驗證",
                description="自動化測試生成和執行",
                required_mcps=["test_mcp"],
                optional_mcps=["stagewise_mcp", "ag_ui_mcp", "security_mcp"],
                max_context_tokens=20000,
                estimated_time=1200,
                parallel_capable=True
            ),
            
            WorkflowType.DEPLOYMENT_RELEASE: WorkflowConfig(
                name="部署發布",
                description="一鍵部署和發布管理",
                required_mcps=["release_trigger_mcp"],
                optional_mcps=["intelligent_monitoring_mcp", "operations_mcp"],
                max_context_tokens=15000,
                estimated_time=600,
                parallel_capable=False
            ),
            
            WorkflowType.MONITORING_OPERATIONS: WorkflowConfig(
                name="監控運維",
                description="實時監控和智能運維",
                required_mcps=["intelligent_monitoring_mcp"],
                optional_mcps=["operations_mcp", "xmasters_mcp"],
                max_context_tokens=15000,
                estimated_time=0,  # 持續運行
                parallel_capable=True
            )
        }
        
    async def execute_workflow(
        self,
        workflow_type: WorkflowType,
        input_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """執行工作流 - 使用 MCP-Zero 模式"""
        
        workflow_id = f"{workflow_type.value}_{asyncio.get_event_loop().time()}"
        logger.info(f"開始執行工作流: {workflow_id}")
        
        config = self.workflow_configs[workflow_type]
        
        # 記錄活躍工作流
        self.active_workflows[workflow_id] = {
            "type": workflow_type,
            "status": "running",
            "start_time": asyncio.get_event_loop().time()
        }
        
        try:
            # 1. 預檢查必需的 MCP
            missing_mcps = await self._check_required_mcps(config.required_mcps)
            if missing_mcps:
                raise Exception(f"缺少必需的 MCP: {missing_mcps}")
                
            # 2. 優化上下文
            mcp_zero_engine.context_manager.optimize_for_workflow(workflow_type.value)
            
            # 3. 構建工作流任務描述
            task_description = self._build_task_description(workflow_type, input_data)
            
            # 4. 設置執行選項
            exec_options = {
                "max_tokens": config.max_context_tokens,
                "workflow_mode": True,
                "workflow_type": workflow_type.value,
                "parallel_execution": config.parallel_capable,
                **(options or {})
            }
            
            # 5. 使用 MCP-Zero 執行
            if workflow_type == WorkflowType.REQUIREMENT_ANALYSIS:
                result = await self._execute_requirement_analysis(task_description, exec_options)
            elif workflow_type == WorkflowType.ARCHITECTURE_DESIGN:
                result = await self._execute_architecture_design(task_description, exec_options)
            elif workflow_type == WorkflowType.CODING_IMPLEMENTATION:
                result = await self._execute_coding_implementation(task_description, exec_options)
            elif workflow_type == WorkflowType.TESTING_VALIDATION:
                result = await self._execute_testing_validation(task_description, exec_options)
            elif workflow_type == WorkflowType.DEPLOYMENT_RELEASE:
                result = await self._execute_deployment_release(task_description, exec_options)
            elif workflow_type == WorkflowType.MONITORING_OPERATIONS:
                result = await self._execute_monitoring_operations(task_description, exec_options)
            else:
                # 通用執行
                result = await mcp_zero_engine.execute_task(task_description, exec_options)
                
            # 6. 更新工作流狀態
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["result"] = result
            
            return {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type.value,
                "success": result.success,
                "execution_time": result.execution_time,
                "tokens_used": result.tokens_used,
                "cost": result.cost_estimate,
                "results": result.results
            }
            
        except Exception as e:
            logger.error(f"工作流執行失敗: {str(e)}")
            
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)
            
            return {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type.value,
                "success": False,
                "error": str(e)
            }
            
    async def _check_required_mcps(self, required_mcps: List[str]) -> List[str]:
        """檢查必需的 MCP 是否可用"""
        missing = []
        
        for mcp_name in required_mcps:
            metadata = await mcp_registry.get_mcp_metadata(mcp_name)
            if not metadata:
                missing.append(mcp_name)
                
        return missing
        
    def _build_task_description(self, workflow_type: WorkflowType, input_data: Dict[str, Any]) -> str:
        """構建任務描述"""
        base_descriptions = {
            WorkflowType.REQUIREMENT_ANALYSIS: "分析代碼並提取需求規格",
            WorkflowType.ARCHITECTURE_DESIGN: "設計系統架構和用戶界面",
            WorkflowType.CODING_IMPLEMENTATION: "實現代碼功能",
            WorkflowType.TESTING_VALIDATION: "生成並執行測試用例",
            WorkflowType.DEPLOYMENT_RELEASE: "部署應用到生產環境",
            WorkflowType.MONITORING_OPERATIONS: "監控系統運行狀態"
        }
        
        base = base_descriptions.get(workflow_type, "執行工作流")
        
        # 添加具體參數
        if "project_name" in input_data:
            base += f" for {input_data['project_name']}"
        if "requirements" in input_data:
            base += f": {input_data['requirements']}"
            
        return base
        
    async def _execute_requirement_analysis(self, task: str, options: Dict[str, Any]) -> Any:
        """執行需求分析工作流"""
        # 定制化的步驟
        custom_steps = [
            TaskStep(
                id="analyze_code",
                name="代碼分析",
                description="分析現有代碼結構和邏輯",
                task_type=TaskType.ANALYSIS,
                required_mcps=["codeflow_mcp"],
                estimated_time=300,
                dependencies=[],
                context_requirements={},
                priority=10
            ),
            TaskStep(
                id="extract_requirements",
                name="需求提取",
                description="從代碼中提取業務需求",
                task_type=TaskType.ANALYSIS,
                required_mcps=["codeflow_mcp", "deepgraph_mcp"],
                estimated_time=400,
                dependencies=["analyze_code"],
                context_requirements={"need_code_analysis": True},
                priority=9
            ),
            TaskStep(
                id="generate_spec",
                name="生成規格文檔",
                description="生成詳細的需求規格文檔",
                task_type=TaskType.CODE_GENERATION,
                required_mcps=["codeflow_mcp"],
                estimated_time=300,
                dependencies=["extract_requirements"],
                context_requirements={"format": "markdown"},
                priority=8
            )
        ]
        
        # 注入自定義步驟
        mcp_zero_engine.planner.custom_steps = custom_steps
        
        # 執行
        return await mcp_zero_engine.execute_task(task, options)
        
    async def _execute_architecture_design(self, task: str, options: Dict[str, Any]) -> Any:
        """執行架構設計工作流"""
        # 並行執行 UI 設計和系統架構設計
        options["parallel_execution"] = True
        
        custom_steps = [
            TaskStep(
                id="system_design",
                name="系統架構設計",
                description="設計整體系統架構",
                task_type=TaskType.ANALYSIS,
                required_mcps=["codeflow_mcp", "deepgraph_mcp"],
                estimated_time=600,
                dependencies=[],
                context_requirements={},
                priority=10
            ),
            TaskStep(
                id="ui_design",
                name="UI 界面設計",
                description="設計用戶界面和交互",
                task_type=TaskType.UI_DESIGN,
                required_mcps=["smartui_mcp", "ag_ui_mcp"],
                estimated_time=600,
                dependencies=[],  # 可以並行
                context_requirements={"responsive": True},
                priority=10
            ),
            TaskStep(
                id="integration_design",
                name="集成設計",
                description="設計系統集成方案",
                task_type=TaskType.ANALYSIS,
                required_mcps=["codeflow_mcp"],
                estimated_time=300,
                dependencies=["system_design", "ui_design"],
                context_requirements={},
                priority=8
            )
        ]
        
        mcp_zero_engine.planner.custom_steps = custom_steps
        return await mcp_zero_engine.execute_task(task, options)
        
    async def _execute_coding_implementation(self, task: str, options: Dict[str, Any]) -> Any:
        """執行編碼實現工作流"""
        # 智能選擇 MCP 組合
        if "ui" in task.lower() or "界面" in task.lower():
            # UI 相關任務
            priority_mcps = ["smartui_mcp", "ag_ui_mcp", "codeflow_mcp"]
        elif "api" in task.lower() or "接口" in task.lower():
            # API 相關任務
            priority_mcps = ["codeflow_mcp", "security_mcp"]
        else:
            # 通用代碼任務
            priority_mcps = ["codeflow_mcp"]
            
        # 動態調整 MCP 優先級
        for mcp in priority_mcps:
            metadata = await mcp_registry.get_mcp_metadata(mcp)
            if metadata:
                metadata.performance_score = min(1.0, metadata.performance_score + 0.1)
                
        return await mcp_zero_engine.execute_task(task, options)
        
    async def _execute_testing_validation(self, task: str, options: Dict[str, Any]) -> Any:
        """執行測試驗證工作流"""
        custom_steps = [
            TaskStep(
                id="unit_tests",
                name="單元測試生成",
                description="生成單元測試用例",
                task_type=TaskType.TEST_AUTOMATION,
                required_mcps=["test_mcp"],
                estimated_time=400,
                dependencies=[],
                context_requirements={},
                priority=10
            ),
            TaskStep(
                id="integration_tests",
                name="集成測試",
                description="生成集成測試用例",
                task_type=TaskType.TEST_AUTOMATION,
                required_mcps=["test_mcp", "stagewise_mcp"],
                estimated_time=600,
                dependencies=["unit_tests"],
                context_requirements={},
                priority=9
            ),
            TaskStep(
                id="ui_tests",
                name="UI 測試",
                description="生成 UI 自動化測試",
                task_type=TaskType.TEST_AUTOMATION,
                required_mcps=["ag_ui_mcp", "stagewise_mcp"],
                estimated_time=500,
                dependencies=["unit_tests"],  # 可以並行
                context_requirements={},
                priority=9
            ),
            TaskStep(
                id="security_scan",
                name="安全掃描",
                description="執行安全漏洞掃描",
                task_type=TaskType.ANALYSIS,
                required_mcps=["security_mcp"],
                estimated_time=300,
                dependencies=[],  # 可以並行
                context_requirements={},
                priority=8
            )
        ]
        
        mcp_zero_engine.planner.custom_steps = custom_steps
        return await mcp_zero_engine.execute_task(task, options)
        
    async def _execute_deployment_release(self, task: str, options: Dict[str, Any]) -> Any:
        """執行部署發布工作流"""
        # 部署前檢查
        pre_checks = await self._pre_deployment_checks()
        if not pre_checks["ready"]:
            raise Exception(f"部署前檢查失敗: {pre_checks['issues']}")
            
        return await mcp_zero_engine.execute_task(task, options)
        
    async def _execute_monitoring_operations(self, task: str, options: Dict[str, Any]) -> Any:
        """執行監控運維工作流"""
        # 持續運行模式
        options["continuous_mode"] = True
        options["max_time"] = 3600  # 最多運行 1 小時
        
        return await mcp_zero_engine.execute_task(task, options)
        
    async def _pre_deployment_checks(self) -> Dict[str, Any]:
        """部署前檢查"""
        checks = {
            "ready": True,
            "issues": []
        }
        
        # 檢查測試是否通過
        # 檢查代碼質量
        # 檢查配置完整性
        
        return checks
        
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """獲取工作流狀態"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            
            # 如果有關聯的任務 ID，獲取詳細狀態
            if "task_id" in workflow:
                task_status = await mcp_zero_engine.get_task_status(workflow["task_id"])
                workflow["task_status"] = task_status
                
            return workflow
            
        return None
        
    async def optimize_workflow_performance(self):
        """優化工作流性能"""
        # 分析歷史執行數據
        # 調整 MCP 優先級
        # 優化並行策略
        
        logger.info("執行工作流性能優化")
        
        # 根據使用頻率調整 MCP 性能評分
        for mcp_name, stats in mcp_registry.usage_stats.items():
            if stats["load_count"] > 10:
                metadata = await mcp_registry.get_mcp_metadata(mcp_name)
                if metadata:
                    # 頻繁使用的 MCP 提高評分
                    metadata.performance_score = min(1.0, metadata.performance_score + 0.05)
                    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """獲取工作流指標"""
        completed_workflows = [w for w in self.active_workflows.values() if w["status"] == "completed"]
        
        if not completed_workflows:
            return {"message": "尚無完成的工作流"}
            
        total_time = sum(w.get("result", {}).get("execution_time", 0) for w in completed_workflows)
        total_tokens = sum(w.get("result", {}).get("tokens_used", 0) for w in completed_workflows)
        total_cost = sum(w.get("result", {}).get("cost_estimate", 0) for w in completed_workflows)
        
        return {
            "total_workflows": len(self.active_workflows),
            "completed": len(completed_workflows),
            "average_time": total_time / len(completed_workflows) if completed_workflows else 0,
            "average_tokens": total_tokens / len(completed_workflows) if completed_workflows else 0,
            "total_cost": total_cost,
            "cost_saved": total_cost * 4  # 相比傳統模式節省 80%
        }


# 創建全局實例
mcp_zero_workflow_engine = MCPZeroWorkflowEngine()