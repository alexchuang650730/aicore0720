#!/usr/bin/env python3
"""
MCP-Zero 執行引擎
核心執行邏輯，實現迭代式任務執行
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import time

from .mcp_registry import MCPRegistry, mcp_registry
from .task_planner import TaskPlanner, TaskStep, TaskContext, TaskType
from .context_manager import ContextManager

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """執行結果"""
    task_id: str
    success: bool
    steps_completed: int
    total_steps: int
    results: Dict[str, Any]
    errors: List[str]
    execution_time: float
    tokens_used: int
    cost_estimate: float


@dataclass
class StepResult:
    """步驟執行結果"""
    step_id: str
    success: bool
    output: Any
    error: Optional[str]
    mcps_used: List[str]
    execution_time: float
    tokens_used: int


class MCPZeroEngine:
    """MCP-Zero 執行引擎"""
    
    def __init__(self):
        self.registry = mcp_registry
        self.planner = TaskPlanner(self.registry)
        self.context_manager = ContextManager()
        self.active_tasks: Dict[str, TaskContext] = {}
        self.execution_history: List[ExecutionResult] = []
        
    async def execute_task(self, user_request: str, options: Dict[str, Any] = None) -> ExecutionResult:
        """執行用戶任務"""
        task_id = self._generate_task_id()
        start_time = time.time()
        
        logger.info(f"開始執行任務 {task_id}: {user_request}")
        
        # 初始化任務上下文
        context = TaskContext(
            user_request=user_request,
            current_step=None,
            completed_steps=[],
            results={},
            total_tokens_used=0,
            execution_time=0
        )
        
        self.active_tasks[task_id] = context
        
        try:
            # 1. 任務分解
            steps = await self.planner.decompose_task(user_request)
            logger.info(f"任務分解為 {len(steps)} 個步驟")
            
            # 2. 評估複雜度
            complexity = await self.planner.estimate_task_complexity(steps)
            logger.info(f"任務複雜度: {complexity}")
            
            # 3. 迭代執行
            results = []
            errors = []
            
            for i, step in enumerate(steps):
                logger.info(f"執行步驟 {i+1}/{len(steps)}: {step.name}")
                
                # 3.1 規劃下一步
                next_step = await self.planner.plan_next_step(context, steps[i:])
                if not next_step:
                    logger.warning("無法規劃下一步")
                    break
                    
                # 3.2 執行步驟
                step_result = await self._execute_step(next_step, context, options)
                results.append(step_result)
                
                # 3.3 更新上下文
                context.current_step = step_result.step_id
                context.completed_steps.append(step_result.step_id)
                context.results[step_result.step_id] = step_result.output
                context.total_tokens_used += step_result.tokens_used
                
                # 3.4 處理錯誤
                if not step_result.success:
                    errors.append(step_result.error or "未知錯誤")
                    if options and options.get("stop_on_error", True):
                        logger.error(f"步驟失敗，停止執行: {step_result.error}")
                        break
                        
                # 3.5 檢查是否需要暫停
                if await self._should_pause(context, options):
                    logger.info("任務暫停")
                    break
                    
            # 4. 編譯結果
            execution_time = time.time() - start_time
            
            result = ExecutionResult(
                task_id=task_id,
                success=len(errors) == 0,
                steps_completed=len(context.completed_steps),
                total_steps=len(steps),
                results=self._compile_results(results),
                errors=errors,
                execution_time=execution_time,
                tokens_used=context.total_tokens_used,
                cost_estimate=self._calculate_cost(context.total_tokens_used)
            )
            
            # 5. 清理
            await self._cleanup_task(task_id)
            
            # 6. 記錄歷史
            self.execution_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"任務執行失敗: {str(e)}")
            
            # 緊急清理
            await self._emergency_cleanup()
            
            return ExecutionResult(
                task_id=task_id,
                success=False,
                steps_completed=len(context.completed_steps),
                total_steps=0,
                results={},
                errors=[str(e)],
                execution_time=time.time() - start_time,
                tokens_used=context.total_tokens_used,
                cost_estimate=self._calculate_cost(context.total_tokens_used)
            )
            
    async def _execute_step(
        self, 
        step: TaskStep, 
        context: TaskContext,
        options: Optional[Dict[str, Any]]
    ) -> StepResult:
        """執行單個步驟"""
        start_time = time.time()
        mcps_loaded = []
        
        try:
            # 1. 加載需要的 MCP
            for mcp_name in step.required_mcps:
                mcp = await self.registry.load_mcp(mcp_name)
                if mcp:
                    mcps_loaded.append(mcp_name)
                else:
                    logger.warning(f"無法加載 MCP: {mcp_name}")
                    
            if not mcps_loaded:
                return StepResult(
                    step_id=step.id,
                    success=False,
                    output=None,
                    error="沒有可用的 MCP",
                    mcps_used=[],
                    execution_time=time.time() - start_time,
                    tokens_used=0
                )
                
            # 2. 準備執行參數
            params = self._prepare_step_params(step, context)
            
            # 3. 選擇主要 MCP 執行
            primary_mcp_name = mcps_loaded[0]
            primary_mcp = self.registry.loaded_mcps[primary_mcp_name]
            
            # 4. 執行操作
            output = await self._execute_with_mcp(
                primary_mcp, 
                step, 
                params,
                secondary_mcps=mcps_loaded[1:]
            )
            
            # 5. 估算 token 使用
            tokens_used = self._estimate_tokens(step, output)
            
            return StepResult(
                step_id=step.id,
                success=True,
                output=output,
                error=None,
                mcps_used=mcps_loaded,
                execution_time=time.time() - start_time,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            logger.error(f"步驟執行失敗: {str(e)}")
            
            return StepResult(
                step_id=step.id,
                success=False,
                output=None,
                error=str(e),
                mcps_used=mcps_loaded,
                execution_time=time.time() - start_time,
                tokens_used=0
            )
            
    async def _execute_with_mcp(
        self, 
        mcp: Any, 
        step: TaskStep,
        params: Dict[str, Any],
        secondary_mcps: List[str]
    ) -> Any:
        """使用 MCP 執行具體操作"""
        # 根據步驟類型選擇操作
        action_mapping = {
            TaskType.CODE_GENERATION: "generate_code",
            TaskType.UI_DESIGN: "generate_ui",
            TaskType.API_DEVELOPMENT: "generate_api",
            TaskType.TEST_AUTOMATION: "generate_tests",
            TaskType.ANALYSIS: "analyze",
            TaskType.REFACTORING: "refactor"
        }
        
        action = action_mapping.get(step.task_type, "execute")
        
        # 檢查 MCP 是否支持該操作
        if hasattr(mcp, action):
            method = getattr(mcp, action)
            return await method(params)
        else:
            # 使用通用執行方法
            return await mcp.execute(action, params)
            
    def _prepare_step_params(self, step: TaskStep, context: TaskContext) -> Dict[str, Any]:
        """準備步驟執行參數"""
        params = {
            "request": context.user_request,
            "step_description": step.description,
            "context": {}
        }
        
        # 添加前置步驟的結果
        for dep in step.dependencies:
            if dep in context.results:
                params["context"][dep] = context.results[dep]
                
        # 添加特定需求
        if step.context_requirements:
            params.update(step.context_requirements)
            
        return params
        
    def _estimate_tokens(self, step: TaskStep, output: Any) -> int:
        """估算 token 使用量"""
        # 簡單估算：輸入 + 輸出
        input_tokens = len(step.description) * 0.3  # 粗略估算
        
        output_tokens = 0
        if isinstance(output, str):
            output_tokens = len(output) * 0.3
        elif isinstance(output, dict):
            output_tokens = len(json.dumps(output)) * 0.3
            
        # 加上 MCP 的基礎消耗
        mcp_tokens = len(step.required_mcps) * 500
        
        return int(input_tokens + output_tokens + mcp_tokens)
        
    def _calculate_cost(self, tokens: int) -> float:
        """計算成本（基於 K2 定價）"""
        # K2 定價：input 2元/M tokens, output 8元/M tokens
        # 假設 input:output = 1:3
        input_tokens = tokens * 0.25
        output_tokens = tokens * 0.75
        
        input_cost = (input_tokens / 1_000_000) * 2
        output_cost = (output_tokens / 1_000_000) * 8
        
        return round(input_cost + output_cost, 4)
        
    def _compile_results(self, step_results: List[StepResult]) -> Dict[str, Any]:
        """編譯所有步驟的結果"""
        compiled = {
            "summary": {},
            "details": {},
            "artifacts": []
        }
        
        for result in step_results:
            if result.success and result.output:
                # 提取關鍵信息
                if isinstance(result.output, dict):
                    if "code" in result.output:
                        compiled["artifacts"].append({
                            "type": "code",
                            "step_id": result.step_id,
                            "content": result.output["code"]
                        })
                    if "ui" in result.output:
                        compiled["artifacts"].append({
                            "type": "ui",
                            "step_id": result.step_id,
                            "content": result.output["ui"]
                        })
                        
                compiled["details"][result.step_id] = result.output
                
        # 生成摘要
        compiled["summary"] = {
            "total_artifacts": len(compiled["artifacts"]),
            "artifact_types": list(set(a["type"] for a in compiled["artifacts"]))
        }
        
        return compiled
        
    async def _should_pause(self, context: TaskContext, options: Optional[Dict[str, Any]]) -> bool:
        """檢查是否需要暫停"""
        if not options:
            return False
            
        # 檢查 token 限制
        if "max_tokens" in options:
            if context.total_tokens_used >= options["max_tokens"]:
                logger.warning("達到 token 限制，暫停執行")
                return True
                
        # 檢查時間限制
        if "max_time" in options:
            if context.execution_time >= options["max_time"]:
                logger.warning("達到時間限制，暫停執行")
                return True
                
        # 檢查步驟限制
        if "max_steps" in options:
            if len(context.completed_steps) >= options["max_steps"]:
                logger.warning("達到步驟限制，暫停執行")
                return True
                
        return False
        
    async def _cleanup_task(self, task_id: str):
        """清理任務資源"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
            
        # 智能卸載 MCP
        await self._smart_unload_mcps()
        
    async def _smart_unload_mcps(self):
        """智能卸載不需要的 MCP"""
        # 獲取所有活躍任務需要的 MCP
        active_mcps = set()
        for context in self.active_tasks.values():
            for step_id, result in context.results.items():
                if isinstance(result, dict) and "mcps_used" in result:
                    active_mcps.update(result["mcps_used"])
                    
        # 卸載不在活躍列表中的 MCP
        loaded_mcps = await self.registry.get_loaded_mcps()
        for mcp in loaded_mcps:
            if mcp not in active_mcps:
                metadata = await self.registry.get_mcp_metadata(mcp)
                # 保留 P0 級別的 MCP
                if metadata and metadata.priority != "P0":
                    await self.registry.unload_mcp(mcp)
                    
    async def _emergency_cleanup(self):
        """緊急清理（發生錯誤時）"""
        logger.warning("執行緊急清理")
        
        # 卸載所有非 P0 的 MCP
        loaded_mcps = await self.registry.get_loaded_mcps()
        for mcp in loaded_mcps:
            metadata = await self.registry.get_mcp_metadata(mcp)
            if metadata and metadata.priority != "P0":
                try:
                    await self.registry.unload_mcp(mcp)
                except Exception as e:
                    logger.error(f"緊急卸載 {mcp} 失敗: {e}")
                    
    def _generate_task_id(self) -> str:
        """生成任務 ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"task_{timestamp}_{len(self.execution_history)}"
        
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """獲取任務狀態"""
        if task_id in self.active_tasks:
            context = self.active_tasks[task_id]
            return {
                "status": "active",
                "current_step": context.current_step,
                "completed_steps": len(context.completed_steps),
                "tokens_used": context.total_tokens_used,
                "cost_so_far": self._calculate_cost(context.total_tokens_used)
            }
            
        # 在歷史中查找
        for result in self.execution_history:
            if result.task_id == task_id:
                return {
                    "status": "completed" if result.success else "failed",
                    "steps_completed": result.steps_completed,
                    "total_steps": result.total_steps,
                    "execution_time": result.execution_time,
                    "cost": result.cost_estimate
                }
                
        return None
        
    async def pause_task(self, task_id: str) -> bool:
        """暫停任務"""
        if task_id in self.active_tasks:
            # 這裡可以設置一個標誌，在下次步驟執行前檢查
            logger.info(f"任務 {task_id} 已標記為暫停")
            return True
        return False
        
    async def resume_task(self, task_id: str) -> bool:
        """恢復任務"""
        # 實現任務恢復邏輯
        logger.info(f"任務 {task_id} 恢復執行")
        return True
        

# 創建全局實例
mcp_zero_engine = MCPZeroEngine()