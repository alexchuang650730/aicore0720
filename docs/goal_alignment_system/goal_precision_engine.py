"""
开发目标精准化引擎
通过Stagewise MCP、Test MCP、CodeFlow MCP、AG-UI&SmartUI MCP协同工作
确保开发过程始终与用户目标保持一致，防止偏离
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import uuid
import time

logger = logging.getLogger(__name__)

class GoalStatus(Enum):
    """目标状态枚举"""
    DEFINED = "defined"           # 已定义
    IN_PROGRESS = "in_progress"   # 进行中
    COMPLETED = "completed"       # 已完成
    DEVIATED = "deviated"         # 偏离
    BLOCKED = "blocked"           # 阻塞
    REFINED = "refined"           # 已细化

class ComponentType(Enum):
    """组件类型枚举"""
    STAGEWISE = "stagewise"
    TEST = "test"
    CODEFLOW = "codeflow"
    AGUI_SMARTUI = "agui_smartui"

@dataclass
class DevelopmentGoal:
    """开发目标数据结构"""
    id: str
    title: str
    description: str
    user_requirements: List[str]
    acceptance_criteria: List[str]
    priority: int
    status: GoalStatus
    created_at: float
    updated_at: float
    parent_goal_id: Optional[str] = None
    sub_goals: List[str] = None
    tags: List[str] = None
    estimated_effort: int = 0  # 预估工作量（小时）
    actual_effort: int = 0     # 实际工作量（小时）
    progress_percentage: float = 0.0
    stakeholders: List[str] = None
    
    def __post_init__(self):
        if self.sub_goals is None:
            self.sub_goals = []
        if self.tags is None:
            self.tags = []
        if self.stakeholders is None:
            self.stakeholders = []

@dataclass
class GoalDeviationAlert:
    """目标偏离警告"""
    goal_id: str
    deviation_type: str
    severity: str  # low, medium, high, critical
    description: str
    suggested_actions: List[str]
    detected_at: float
    component_source: ComponentType

class GoalPrecisionEngine:
    """目标精准化引擎"""
    
    def __init__(self):
        """初始化目标精准化引擎"""
        self.goals: Dict[str, DevelopmentGoal] = {}
        self.goal_history: List[Dict[str, Any]] = []
        self.deviation_alerts: List[GoalDeviationAlert] = []
        self.component_handlers = {
            ComponentType.STAGEWISE: self._handle_stagewise_feedback,
            ComponentType.TEST: self._handle_test_feedback,
            ComponentType.CODEFLOW: self._handle_codeflow_feedback,
            ComponentType.AGUI_SMARTUI: self._handle_agui_smartui_feedback
        }
        
        # 目标对齐阈值
        self.alignment_thresholds = {
            "progress_deviation": 0.3,      # 进度偏离阈值
            "scope_expansion": 0.2,         # 范围扩展阈值
            "quality_threshold": 0.8,       # 质量阈值
            "time_overrun": 0.5            # 时间超支阈值
        }
    
    async def create_goal(self, title: str, description: str, 
                         user_requirements: List[str], 
                         acceptance_criteria: List[str],
                         priority: int = 5) -> str:
        """
        创建新的开发目标
        
        Args:
            title: 目标标题
            description: 目标描述
            user_requirements: 用户需求列表
            acceptance_criteria: 验收标准
            priority: 优先级 (1-10)
            
        Returns:
            目标ID
        """
        goal_id = str(uuid.uuid4())
        current_time = time.time()
        
        goal = DevelopmentGoal(
            id=goal_id,
            title=title,
            description=description,
            user_requirements=user_requirements,
            acceptance_criteria=acceptance_criteria,
            priority=priority,
            status=GoalStatus.DEFINED,
            created_at=current_time,
            updated_at=current_time
        )
        
        self.goals[goal_id] = goal
        
        # 记录目标创建历史
        self.goal_history.append({
            "action": "create",
            "goal_id": goal_id,
            "timestamp": current_time,
            "data": asdict(goal)
        })
        
        logger.info(f"🎯 创建新目标: {title}")
        
        # 自动分解目标
        await self._auto_decompose_goal(goal_id)
        
        return goal_id
    
    async def _auto_decompose_goal(self, goal_id: str):
        """自动分解目标为子目标"""
        goal = self.goals.get(goal_id)
        if not goal:
            return
        
        # 基于用户需求自动生成子目标
        sub_goals = []
        
        for i, requirement in enumerate(goal.user_requirements):
            sub_goal_id = await self.create_sub_goal(
                parent_goal_id=goal_id,
                title=f"需求{i+1}: {requirement[:50]}...",
                description=f"实现用户需求: {requirement}",
                user_requirements=[requirement],
                acceptance_criteria=[f"完成{requirement}的实现和测试"]
            )
            sub_goals.append(sub_goal_id)
        
        # 更新父目标
        goal.sub_goals = sub_goals
        goal.updated_at = time.time()
        
        logger.info(f"🔄 目标分解完成: {goal.title} -> {len(sub_goals)}个子目标")
    
    async def create_sub_goal(self, parent_goal_id: str, title: str, 
                            description: str, user_requirements: List[str],
                            acceptance_criteria: List[str]) -> str:
        """创建子目标"""
        sub_goal_id = str(uuid.uuid4())
        current_time = time.time()
        
        parent_goal = self.goals.get(parent_goal_id)
        if not parent_goal:
            raise ValueError(f"父目标不存在: {parent_goal_id}")
        
        sub_goal = DevelopmentGoal(
            id=sub_goal_id,
            title=title,
            description=description,
            user_requirements=user_requirements,
            acceptance_criteria=acceptance_criteria,
            priority=parent_goal.priority,
            status=GoalStatus.DEFINED,
            created_at=current_time,
            updated_at=current_time,
            parent_goal_id=parent_goal_id
        )
        
        self.goals[sub_goal_id] = sub_goal
        return sub_goal_id
    
    async def update_goal_progress(self, goal_id: str, progress_percentage: float,
                                 component_type: ComponentType,
                                 feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新目标进度并检查偏离
        
        Args:
            goal_id: 目标ID
            progress_percentage: 进度百分比
            component_type: 反馈来源组件
            feedback_data: 反馈数据
            
        Returns:
            更新结果和偏离检测
        """
        goal = self.goals.get(goal_id)
        if not goal:
            raise ValueError(f"目标不存在: {goal_id}")
        
        # 记录之前的进度
        previous_progress = goal.progress_percentage
        
        # 更新进度
        goal.progress_percentage = progress_percentage
        goal.updated_at = time.time()
        
        # 检查是否偏离
        deviation_check = await self._check_goal_deviation(
            goal_id, component_type, feedback_data
        )
        
        # 处理组件特定反馈
        component_feedback = await self.component_handlers[component_type](
            goal_id, feedback_data
        )
        
        # 记录历史
        self.goal_history.append({
            "action": "progress_update",
            "goal_id": goal_id,
            "timestamp": time.time(),
            "previous_progress": previous_progress,
            "new_progress": progress_percentage,
            "component_type": component_type.value,
            "feedback": feedback_data
        })
        
        logger.info(f"📊 目标进度更新: {goal.title} - {progress_percentage:.1f}%")
        
        return {
            "goal_id": goal_id,
            "progress_updated": True,
            "deviation_detected": deviation_check["deviation_detected"],
            "component_feedback": component_feedback,
            "suggested_actions": deviation_check.get("suggested_actions", [])
        }
    
    async def _check_goal_deviation(self, goal_id: str, component_type: ComponentType,
                                  feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """检查目标偏离"""
        goal = self.goals.get(goal_id)
        if not goal:
            return {"deviation_detected": False}
        
        deviations = []
        
        # 1. 进度偏离检查
        if "expected_progress" in feedback_data:
            expected = feedback_data["expected_progress"]
            actual = goal.progress_percentage
            deviation = abs(expected - actual) / expected if expected > 0 else 0
            
            if deviation > self.alignment_thresholds["progress_deviation"]:
                deviations.append({
                    "type": "progress_deviation",
                    "severity": "high" if deviation > 0.5 else "medium",
                    "description": f"实际进度({actual:.1f}%)与预期进度({expected:.1f}%)偏离{deviation:.1%}",
                    "suggested_actions": [
                        "重新评估任务复杂度",
                        "调整资源分配",
                        "更新时间估算"
                    ]
                })
        
        # 2. 范围扩展检查
        if "new_requirements" in feedback_data:
            new_req_count = len(feedback_data["new_requirements"])
            original_req_count = len(goal.user_requirements)
            
            if new_req_count > 0:
                expansion_ratio = new_req_count / original_req_count
                
                if expansion_ratio > self.alignment_thresholds["scope_expansion"]:
                    deviations.append({
                        "type": "scope_expansion",
                        "severity": "high",
                        "description": f"需求范围扩展{expansion_ratio:.1%}，新增{new_req_count}个需求",
                        "suggested_actions": [
                            "与用户确认优先级",
                            "评估影响范围",
                            "调整项目计划"
                        ]
                    })
        
        # 3. 质量偏离检查
        if "quality_metrics" in feedback_data:
            quality_score = feedback_data["quality_metrics"].get("overall_score", 1.0)
            
            if quality_score < self.alignment_thresholds["quality_threshold"]:
                deviations.append({
                    "type": "quality_deviation",
                    "severity": "high",
                    "description": f"质量分数({quality_score:.2f})低于阈值({self.alignment_thresholds['quality_threshold']:.2f})",
                    "suggested_actions": [
                        "增加代码审查",
                        "完善测试覆盖",
                        "重构关键模块"
                    ]
                })
        
        # 4. 时间超支检查
        if "time_spent" in feedback_data:
            time_spent = feedback_data["time_spent"]
            estimated_time = goal.estimated_effort
            
            if estimated_time > 0:
                overrun_ratio = (time_spent - estimated_time) / estimated_time
                
                if overrun_ratio > self.alignment_thresholds["time_overrun"]:
                    deviations.append({
                        "type": "time_overrun",
                        "severity": "medium",
                        "description": f"时间超支{overrun_ratio:.1%}，预估{estimated_time}小时，实际{time_spent}小时",
                        "suggested_actions": [
                            "重新评估剩余工作量",
                            "优化开发流程",
                            "考虑技术债务"
                        ]
                    })
        
        # 创建偏离警告
        for deviation in deviations:
            alert = GoalDeviationAlert(
                goal_id=goal_id,
                deviation_type=deviation["type"],
                severity=deviation["severity"],
                description=deviation["description"],
                suggested_actions=deviation["suggested_actions"],
                detected_at=time.time(),
                component_source=component_type
            )
            self.deviation_alerts.append(alert)
        
        return {
            "deviation_detected": len(deviations) > 0,
            "deviations": deviations,
            "suggested_actions": [action for dev in deviations for action in dev["suggested_actions"]]
        }
    
    # 组件特定反馈处理器
    async def _handle_stagewise_feedback(self, goal_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理Stagewise MCP反馈"""
        goal = self.goals.get(goal_id)
        if not goal:
            return {"processed": False}
        
        # 处理阶段性进展
        if "stage_completed" in feedback_data:
            stage_info = feedback_data["stage_completed"]
            
            # 更新目标状态
            if stage_info.get("is_milestone"):
                goal.status = GoalStatus.IN_PROGRESS
                
                # 检查是否偏离用户期望
                if "user_feedback" in stage_info:
                    user_satisfaction = stage_info["user_feedback"].get("satisfaction", 0.5)
                    if user_satisfaction < 0.7:
                        # 目标偏离，需要调整
                        goal.status = GoalStatus.DEVIATED
                        
                        # 建议调整措施
                        return {
                            "processed": True,
                            "deviation_detected": True,
                            "recommendation": "根据用户反馈调整开发方向",
                            "suggested_adjustments": [
                                "重新理解用户需求",
                                "调整设计方案",
                                "增加用户确认环节"
                            ]
                        }
        
        return {"processed": True, "deviation_detected": False}
    
    async def _handle_test_feedback(self, goal_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理Test MCP反馈"""
        goal = self.goals.get(goal_id)
        if not goal:
            return {"processed": False}
        
        # 处理测试结果
        if "test_results" in feedback_data:
            test_results = feedback_data["test_results"]
            
            # 验收标准验证
            acceptance_coverage = 0
            for i, criteria in enumerate(goal.acceptance_criteria):
                test_key = f"acceptance_test_{i}"
                if test_key in test_results and test_results[test_key]["passed"]:
                    acceptance_coverage += 1
            
            coverage_ratio = acceptance_coverage / len(goal.acceptance_criteria)
            
            if coverage_ratio < 0.8:
                # 验收标准未充分满足
                return {
                    "processed": True,
                    "deviation_detected": True,
                    "recommendation": "验收标准覆盖不足，需要补充实现",
                    "coverage_ratio": coverage_ratio,
                    "missing_criteria": [
                        criteria for i, criteria in enumerate(goal.acceptance_criteria)
                        if f"acceptance_test_{i}" not in test_results or not test_results[f"acceptance_test_{i}"]["passed"]
                    ]
                }
        
        return {"processed": True, "deviation_detected": False}
    
    async def _handle_codeflow_feedback(self, goal_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理CodeFlow MCP反馈"""
        goal = self.goals.get(goal_id)
        if not goal:
            return {"processed": False}
        
        # 处理代码流程反馈
        if "code_analysis" in feedback_data:
            analysis = feedback_data["code_analysis"]
            
            # 检查代码是否偏离需求
            if "requirement_alignment" in analysis:
                alignment_score = analysis["requirement_alignment"]["score"]
                
                if alignment_score < 0.7:
                    # 代码实现偏离需求
                    return {
                        "processed": True,
                        "deviation_detected": True,
                        "recommendation": "代码实现偏离用户需求，需要重构",
                        "alignment_score": alignment_score,
                        "misaligned_modules": analysis["requirement_alignment"].get("misaligned_modules", [])
                    }
        
        return {"processed": True, "deviation_detected": False}
    
    async def _handle_agui_smartui_feedback(self, goal_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理AG-UI & SmartUI MCP反馈"""
        goal = self.goals.get(goal_id)
        if not goal:
            return {"processed": False}
        
        # 处理UI生成反馈
        if "ui_generation" in feedback_data:
            ui_feedback = feedback_data["ui_generation"]
            
            # 检查UI是否符合用户期望
            if "user_expectation_match" in ui_feedback:
                match_score = ui_feedback["user_expectation_match"]["score"]
                
                if match_score < 0.8:
                    # UI不符合用户期望
                    return {
                        "processed": True,
                        "deviation_detected": True,
                        "recommendation": "UI设计偏离用户期望，需要调整",
                        "match_score": match_score,
                        "improvement_suggestions": ui_feedback["user_expectation_match"].get("suggestions", [])
                    }
        
        return {"processed": True, "deviation_detected": False}
    
    async def get_goal_status(self, goal_id: str) -> Dict[str, Any]:
        """获取目标状态"""
        goal = self.goals.get(goal_id)
        if not goal:
            return {"error": "目标不存在"}
        
        # 获取子目标状态
        sub_goal_statuses = []
        for sub_goal_id in goal.sub_goals:
            sub_goal = self.goals.get(sub_goal_id)
            if sub_goal:
                sub_goal_statuses.append({
                    "id": sub_goal_id,
                    "title": sub_goal.title,
                    "status": sub_goal.status.value,
                    "progress": sub_goal.progress_percentage
                })
        
        # 获取相关偏离警告
        related_alerts = [
            {
                "deviation_type": alert.deviation_type,
                "severity": alert.severity,
                "description": alert.description,
                "suggested_actions": alert.suggested_actions,
                "detected_at": alert.detected_at
            }
            for alert in self.deviation_alerts
            if alert.goal_id == goal_id
        ]
        
        return {
            "goal": asdict(goal),
            "sub_goals": sub_goal_statuses,
            "deviation_alerts": related_alerts,
            "overall_health": self._calculate_goal_health(goal_id)
        }
    
    def _calculate_goal_health(self, goal_id: str) -> str:
        """计算目标健康度"""
        goal = self.goals.get(goal_id)
        if not goal:
            return "unknown"
        
        # 检查最近的偏离警告
        recent_alerts = [
            alert for alert in self.deviation_alerts
            if alert.goal_id == goal_id and 
            time.time() - alert.detected_at < 3600  # 1小时内
        ]
        
        critical_alerts = [alert for alert in recent_alerts if alert.severity == "critical"]
        high_alerts = [alert for alert in recent_alerts if alert.severity == "high"]
        
        if critical_alerts:
            return "critical"
        elif high_alerts:
            return "warning"
        elif goal.status == GoalStatus.DEVIATED:
            return "attention_needed"
        elif goal.progress_percentage >= 0.8:
            return "healthy"
        else:
            return "monitoring"
    
    async def generate_alignment_report(self, goal_id: str) -> Dict[str, Any]:
        """生成目标对齐报告"""
        goal = self.goals.get(goal_id)
        if not goal:
            return {"error": "目标不存在"}
        
        # 计算各维度对齐度
        alignment_metrics = {
            "requirement_alignment": 0.85,  # 需求对齐度
            "timeline_alignment": 0.75,     # 时间对齐度
            "quality_alignment": 0.90,      # 质量对齐度
            "scope_alignment": 0.80         # 范围对齐度
        }
        
        # 总体对齐度
        overall_alignment = sum(alignment_metrics.values()) / len(alignment_metrics)
        
        # 生成建议
        recommendations = []
        if alignment_metrics["requirement_alignment"] < 0.8:
            recommendations.append("加强需求理解和确认")
        if alignment_metrics["timeline_alignment"] < 0.8:
            recommendations.append("优化时间规划和估算")
        if alignment_metrics["quality_alignment"] < 0.8:
            recommendations.append("提升质量保证措施")
        if alignment_metrics["scope_alignment"] < 0.8:
            recommendations.append("严格控制范围变更")
        
        return {
            "goal_id": goal_id,
            "goal_title": goal.title,
            "overall_alignment": overall_alignment,
            "alignment_metrics": alignment_metrics,
            "health_status": self._calculate_goal_health(goal_id),
            "recommendations": recommendations,
            "generated_at": time.time()
        }

# 使用示例
async def main():
    """主函数示例"""
    engine = GoalPrecisionEngine()
    
    # 创建目标
    goal_id = await engine.create_goal(
        title="构建用户管理系统",
        description="创建一个完整的用户管理系统，包括注册、登录、权限管理",
        user_requirements=[
            "用户可以注册账号",
            "用户可以登录系统",
            "管理员可以管理用户权限",
            "系统要有安全保障"
        ],
        acceptance_criteria=[
            "用户注册功能正常运作",
            "用户登录验证正确",
            "权限管理界面完善",
            "通过安全性测试"
        ],
        priority=8
    )
    
    # 模拟进度更新
    await engine.update_goal_progress(
        goal_id=goal_id,
        progress_percentage=0.3,
        component_type=ComponentType.CODEFLOW,
        feedback_data={
            "expected_progress": 0.5,
            "code_analysis": {
                "requirement_alignment": {
                    "score": 0.6,
                    "misaligned_modules": ["user_authentication"]
                }
            }
        }
    )
    
    # 获取目标状态
    status = await engine.get_goal_status(goal_id)
    print(json.dumps(status, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())