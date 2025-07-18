#!/usr/bin/env python3
"""
MCP-Zero 任務規劃器
使用 LLM 進行智能任務分解和規劃
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任務類型"""
    CODE_GENERATION = "code_generation"
    UI_DESIGN = "ui_design"
    API_DEVELOPMENT = "api_development"
    DATABASE_DESIGN = "database_design"
    TEST_AUTOMATION = "test_automation"
    DEPLOYMENT = "deployment"
    ANALYSIS = "analysis"
    REFACTORING = "refactoring"
    COMPLEX = "complex"


@dataclass
class TaskStep:
    """任務步驟"""
    id: str
    name: str
    description: str
    task_type: TaskType
    required_mcps: List[str]
    estimated_time: int  # 秒
    dependencies: List[str]  # 依賴的步驟 ID
    context_requirements: Dict[str, Any]
    priority: int  # 1-10


@dataclass
class TaskContext:
    """任務上下文"""
    user_request: str
    current_step: Optional[str]
    completed_steps: List[str]
    results: Dict[str, Any]
    total_tokens_used: int
    execution_time: float


class TaskPlanner:
    """基於 LLM 的任務規劃器"""
    
    def __init__(self, mcp_registry):
        self.mcp_registry = mcp_registry
        self.task_patterns = self._initialize_task_patterns()
        
    def _initialize_task_patterns(self) -> Dict[str, List[str]]:
        """初始化任務模式庫"""
        return {
            "創建完整應用": [
                "需求分析", "架構設計", "數據庫設計", 
                "API開發", "前端開發", "測試編寫", "部署配置"
            ],
            "代碼重構": [
                "代碼分析", "識別問題", "制定方案", 
                "執行重構", "測試驗證"
            ],
            "UI設計": [
                "需求理解", "設計規劃", "組件生成", 
                "響應式適配", "測試預覽"
            ],
            "API開發": [
                "接口設計", "代碼生成", "安全檢查", 
                "文檔生成", "測試編寫"
            ],
            "調試修復": [
                "問題定位", "根因分析", "修復方案", 
                "代碼修改", "驗證測試"
            ]
        }
        
    async def decompose_task(self, user_request: str) -> List[TaskStep]:
        """將複雜任務分解為多個步驟"""
        logger.info(f"分解任務: {user_request}")
        
        # 分析任務類型
        task_type = self._analyze_task_type(user_request)
        
        # 獲取相似的任務模式
        pattern = self._find_matching_pattern(user_request)
        
        # 生成任務步驟
        if pattern:
            steps = await self._generate_steps_from_pattern(user_request, pattern, task_type)
        else:
            steps = await self._generate_custom_steps(user_request, task_type)
            
        # 優化步驟順序
        steps = self._optimize_step_order(steps)
        
        return steps
        
    def _analyze_task_type(self, request: str) -> TaskType:
        """分析任務類型"""
        request_lower = request.lower()
        
        if any(keyword in request_lower for keyword in ["生成", "創建", "新建", "開發"]):
            if "ui" in request_lower or "界面" in request_lower:
                return TaskType.UI_DESIGN
            elif "api" in request_lower or "接口" in request_lower:
                return TaskType.API_DEVELOPMENT
            else:
                return TaskType.CODE_GENERATION
                
        elif any(keyword in request_lower for keyword in ["重構", "優化", "改進"]):
            return TaskType.REFACTORING
            
        elif any(keyword in request_lower for keyword in ["測試", "驗證", "檢查"]):
            return TaskType.TEST_AUTOMATION
            
        elif any(keyword in request_lower for keyword in ["分析", "審查", "評估"]):
            return TaskType.ANALYSIS
            
        elif any(keyword in request_lower for keyword in ["部署", "發布", "上線"]):
            return TaskType.DEPLOYMENT
            
        else:
            return TaskType.COMPLEX
            
    def _find_matching_pattern(self, request: str) -> Optional[List[str]]:
        """查找匹配的任務模式"""
        request_lower = request.lower()
        
        for pattern_name, steps in self.task_patterns.items():
            if any(keyword in request_lower for keyword in pattern_name.split()):
                return steps
                
        return None
        
    async def _generate_steps_from_pattern(
        self, 
        request: str, 
        pattern: List[str], 
        task_type: TaskType
    ) -> List[TaskStep]:
        """基於模式生成任務步驟"""
        steps = []
        
        for i, step_name in enumerate(pattern):
            # 為每個步驟推薦 MCP
            required_mcps = await self.mcp_registry.search_mcps(
                f"{step_name} for {request}", 
                max_results=3
            )
            
            step = TaskStep(
                id=f"step_{i+1}",
                name=step_name,
                description=f"{step_name}: {request}",
                task_type=task_type,
                required_mcps=required_mcps,
                estimated_time=self._estimate_step_time(step_name),
                dependencies=[f"step_{i}"] if i > 0 else [],
                context_requirements={
                    "input_from_previous": i > 0,
                    "user_input_needed": step_name in ["需求分析", "設計規劃"]
                },
                priority=10 - i  # 越早的步驟優先級越高
            )
            
            steps.append(step)
            
        return steps
        
    async def _generate_custom_steps(self, request: str, task_type: TaskType) -> List[TaskStep]:
        """生成自定義任務步驟"""
        # 這裡應該調用 LLM 來智能分解任務
        # 現在先用簡單的規則
        
        steps = []
        
        # 基本步驟：理解 -> 規劃 -> 執行 -> 驗證
        basic_flow = [
            ("理解需求", "分析和理解用戶需求"),
            ("制定方案", "規劃實現方案"),
            ("執行實現", "執行具體實現"),
            ("驗證結果", "驗證實現結果")
        ]
        
        for i, (name, desc) in enumerate(basic_flow):
            required_mcps = await self.mcp_registry.search_mcps(
                f"{desc} for {request}", 
                max_results=2
            )
            
            step = TaskStep(
                id=f"step_{i+1}",
                name=name,
                description=f"{desc}: {request}",
                task_type=task_type,
                required_mcps=required_mcps,
                estimated_time=300,  # 默認 5 分鐘
                dependencies=[f"step_{i}"] if i > 0 else [],
                context_requirements={},
                priority=10 - i
            )
            
            steps.append(step)
            
        return steps
        
    def _estimate_step_time(self, step_name: str) -> int:
        """估算步驟執行時間（秒）"""
        time_estimates = {
            "需求分析": 180,
            "架構設計": 300,
            "代碼生成": 600,
            "測試編寫": 400,
            "部署配置": 300,
            "代碼分析": 200,
            "問題定位": 150,
            "修復方案": 120
        }
        
        return time_estimates.get(step_name, 300)
        
    def _optimize_step_order(self, steps: List[TaskStep]) -> List[TaskStep]:
        """優化步驟執行順序"""
        # 拓撲排序確保依賴順序
        sorted_steps = []
        completed = set()
        
        while len(sorted_steps) < len(steps):
            for step in steps:
                if step.id not in completed:
                    # 檢查所有依賴是否已完成
                    if all(dep in completed for dep in step.dependencies):
                        sorted_steps.append(step)
                        completed.add(step.id)
                        
        return sorted_steps
        
    async def plan_next_step(
        self, 
        context: TaskContext,
        remaining_steps: List[TaskStep]
    ) -> Optional[TaskStep]:
        """規劃下一步行動"""
        if not remaining_steps:
            return None
            
        # 檢查上下文限制
        context_usage = self.mcp_registry.get_context_usage()
        available_context = 100000 - context_usage["total_context_size"]
        
        # 選擇可以執行的步驟
        for step in remaining_steps:
            # 檢查依賴是否滿足
            if all(dep in context.completed_steps for dep in step.dependencies):
                # 預估此步驟需要的上下文
                step_context_need = sum(
                    self.mcp_registry.mcp_catalog[mcp].context_size 
                    for mcp in step.required_mcps 
                    if mcp in self.mcp_registry.mcp_catalog
                )
                
                # 如果上下文足夠，返回此步驟
                if step_context_need <= available_context:
                    return step
                else:
                    # 嘗試卸載一些不需要的 MCP
                    await self._free_context_space(step_context_need - available_context)
                    return step
                    
        return None
        
    async def _free_context_space(self, needed_space: int):
        """釋放上下文空間"""
        loaded_mcps = await self.mcp_registry.get_loaded_mcps()
        
        # 按優先級排序，優先卸載 P2 的 MCP
        mcp_priorities = []
        for mcp in loaded_mcps:
            metadata = await self.mcp_registry.get_mcp_metadata(mcp)
            if metadata:
                priority_score = {"P0": 0, "P1": 1, "P2": 2}.get(metadata.priority, 3)
                mcp_priorities.append((mcp, priority_score, metadata.context_size))
                
        # 按優先級排序
        mcp_priorities.sort(key=lambda x: x[1], reverse=True)
        
        # 卸載 MCP 直到釋放足夠空間
        freed_space = 0
        for mcp, _, context_size in mcp_priorities:
            if freed_space >= needed_space:
                break
                
            if await self.mcp_registry.unload_mcp(mcp):
                freed_space += context_size
                logger.info(f"卸載 {mcp} 釋放 {context_size} tokens")
                
    async def estimate_task_complexity(self, steps: List[TaskStep]) -> Dict[str, Any]:
        """估算任務複雜度"""
        total_time = sum(step.estimated_time for step in steps)
        unique_mcps = set()
        
        for step in steps:
            unique_mcps.update(step.required_mcps)
            
        max_context = 0
        for step in steps:
            step_context = sum(
                self.mcp_registry.mcp_catalog[mcp].context_size 
                for mcp in step.required_mcps 
                if mcp in self.mcp_registry.mcp_catalog
            )
            max_context = max(max_context, step_context)
            
        return {
            "total_steps": len(steps),
            "estimated_time_seconds": total_time,
            "estimated_time_minutes": total_time / 60,
            "unique_mcps_needed": len(unique_mcps),
            "max_context_needed": max_context,
            "complexity_score": self._calculate_complexity_score(steps),
            "parallel_potential": self._analyze_parallel_potential(steps)
        }
        
    def _calculate_complexity_score(self, steps: List[TaskStep]) -> float:
        """計算複雜度分數 (0-10)"""
        # 基於步驟數、依賴關係、MCP 需求等計算
        base_score = min(len(steps) / 3, 3)  # 步驟數影響
        
        # 依賴複雜度
        max_deps = max(len(step.dependencies) for step in steps) if steps else 0
        dep_score = min(max_deps, 3)
        
        # MCP 多樣性
        unique_mcps = set()
        for step in steps:
            unique_mcps.update(step.required_mcps)
        mcp_score = min(len(unique_mcps) / 5, 4)
        
        return min(base_score + dep_score + mcp_score, 10)
        
    def _analyze_parallel_potential(self, steps: List[TaskStep]) -> Dict[str, Any]:
        """分析並行執行潛力"""
        # 找出可以並行執行的步驟組
        parallel_groups = []
        processed = set()
        
        for step in steps:
            if step.id not in processed:
                # 找出所有與此步驟沒有依賴關係的步驟
                group = [step]
                processed.add(step.id)
                
                for other in steps:
                    if other.id not in processed:
                        # 檢查是否有依賴關係
                        if (other.id not in step.dependencies and 
                            step.id not in other.dependencies):
                            group.append(other)
                            processed.add(other.id)
                            
                if len(group) > 1:
                    parallel_groups.append([s.id for s in group])
                    
        return {
            "can_parallelize": len(parallel_groups) > 0,
            "parallel_groups": parallel_groups,
            "max_parallel_steps": max(len(g) for g in parallel_groups) if parallel_groups else 1,
            "time_saved_percentage": self._calculate_time_saved(steps, parallel_groups)
        }
        
    def _calculate_time_saved(self, steps: List[TaskStep], parallel_groups: List[List[str]]) -> float:
        """計算並行執行節省的時間百分比"""
        if not parallel_groups:
            return 0.0
            
        sequential_time = sum(step.estimated_time for step in steps)
        
        # 計算並行執行時間
        parallel_time = 0
        processed_steps = set()
        
        for group in parallel_groups:
            # 每組中最長的步驟決定該組的執行時間
            group_time = max(
                step.estimated_time 
                for step in steps 
                if step.id in group
            )
            parallel_time += group_time
            processed_steps.update(group)
            
        # 加上不在並行組中的步驟時間
        for step in steps:
            if step.id not in processed_steps:
                parallel_time += step.estimated_time
                
        time_saved = (sequential_time - parallel_time) / sequential_time * 100
        return round(time_saved, 1)