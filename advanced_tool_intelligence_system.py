#!/usr/bin/env python3
"""
進階工具智能系統
包含：智能推薦、效果學習、自定義工具開發
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
import uuid

# ============= 1. 工具智能推薦系統 =============

@dataclass
class UserProfile:
    """用戶檔案"""
    user_id: str
    preferences: Dict[str, float] = field(default_factory=dict)  # 工具偏好分數
    project_history: List[str] = field(default_factory=list)  # 項目類型歷史
    team_id: Optional[str] = None
    skill_level: str = "intermediate"  # beginner, intermediate, expert
    usage_patterns: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProjectContext:
    """項目上下文"""
    project_type: str  # frontend, backend, fullstack, mobile, etc.
    framework: Optional[str] = None  # react, vue, express, etc.
    language: str = "javascript"
    team_size: int = 1
    complexity: str = "medium"  # low, medium, high
    deadline_pressure: bool = False

@dataclass
class TeamCollaborationPattern:
    """團隊協作模式"""
    team_id: str
    communication_tools: List[str]  # slack, teams, discord
    workflow_style: str  # agile, waterfall, hybrid
    code_review_process: str  # pr-based, pair-programming, post-commit
    preferred_tools: Dict[str, float]  # 團隊工具偏好

class IntelligentRecommendationSystem:
    """工具智能推薦系統"""
    
    def __init__(self, external_tools_mcp):
        self.tools_mcp = external_tools_mcp
        self.user_profiles = {}
        self.team_patterns = {}
        self.recommendation_cache = {}
        self.learning_engine = ToolEffectLearningEngine()
        
    async def get_personalized_recommendations(self, 
                                             user_id: str,
                                             task: str,
                                             context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """獲取個性化工具推薦"""
        print(f"\n🎯 為用戶 {user_id} 生成個性化推薦")
        
        # 1. 獲取或創建用戶檔案
        user_profile = self._get_or_create_profile(user_id)
        
        # 2. 分析項目上下文
        project_context = self._analyze_project_context(context)
        
        # 3. 考慮團隊協作模式
        team_pattern = None
        if user_profile.team_id:
            team_pattern = self.team_patterns.get(user_profile.team_id)
        
        # 4. 生成多維度推薦
        recommendations = await self._generate_recommendations(
            user_profile,
            project_context,
            team_pattern,
            task
        )
        
        # 5. 應用個性化排序
        personalized_recommendations = self._personalize_ranking(
            recommendations,
            user_profile,
            project_context
        )
        
        return personalized_recommendations
    
    def _get_or_create_profile(self, user_id: str) -> UserProfile:
        """獲取或創建用戶檔案"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        return self.user_profiles[user_id]
    
    def _analyze_project_context(self, context: Dict[str, Any]) -> ProjectContext:
        """分析項目上下文"""
        return ProjectContext(
            project_type=context.get("project_type", "fullstack"),
            framework=context.get("framework"),
            language=context.get("language", "javascript"),
            team_size=context.get("team_size", 1),
            complexity=context.get("complexity", "medium"),
            deadline_pressure=context.get("deadline_pressure", False)
        )
    
    async def _generate_recommendations(self,
                                      user_profile: UserProfile,
                                      project_context: ProjectContext,
                                      team_pattern: Optional[TeamCollaborationPattern],
                                      task: str) -> List[Dict[str, Any]]:
        """生成多維度推薦"""
        # 獲取所有可用工具
        all_tools = await self.tools_mcp.handle_request("list_tools", {})
        
        recommendations = []
        
        for tool in all_tools["tools"]:
            score = 0.0
            factors = {}
            
            # 1. 用戶歷史偏好（40%權重）
            user_preference_score = user_profile.preferences.get(tool["id"], 0.5)
            score += user_preference_score * 0.4
            factors["user_preference"] = user_preference_score
            
            # 2. 項目類型匹配（30%權重）
            project_match_score = self._calculate_project_match(tool, project_context)
            score += project_match_score * 0.3
            factors["project_match"] = project_match_score
            
            # 3. 團隊協作適配（20%權重）
            team_score = 0.5  # 默認
            if team_pattern:
                team_score = team_pattern.preferred_tools.get(tool["id"], 0.5)
            score += team_score * 0.2
            factors["team_collaboration"] = team_score
            
            # 4. 任務相關性（10%權重）
            task_relevance = self._calculate_task_relevance(tool, task)
            score += task_relevance * 0.1
            factors["task_relevance"] = task_relevance
            
            # 5. 考慮工具效果歷史（從學習引擎獲取）
            historical_performance = await self.learning_engine.get_tool_performance(tool["id"])
            if historical_performance:
                score *= historical_performance["success_rate"]
            
            recommendations.append({
                "tool": tool,
                "score": score,
                "factors": factors,
                "reasoning": self._generate_recommendation_reasoning(factors)
            })
        
        # 排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:10]  # 返回前10個
    
    def _calculate_project_match(self, tool: Dict[str, Any], 
                               project: ProjectContext) -> float:
        """計算項目匹配度"""
        score = 0.5  # 基礎分
        
        # 語言匹配
        if project.language in str(tool.get("metadata", {})):
            score += 0.2
            
        # 框架匹配
        if project.framework and project.framework in str(tool.get("metadata", {})):
            score += 0.2
            
        # 複雜度匹配
        if project.complexity == "high" and tool["category"] in ["ai_analysis", "ai_refactor"]:
            score += 0.1
            
        return min(score, 1.0)
    
    def _calculate_task_relevance(self, tool: Dict[str, Any], task: str) -> float:
        """計算任務相關性"""
        task_lower = task.lower()
        tool_name_lower = tool["name"].lower()
        tool_desc_lower = tool.get("description", "").lower()
        
        relevance = 0.0
        
        # 名稱匹配
        if any(word in tool_name_lower for word in task_lower.split()):
            relevance += 0.5
            
        # 描述匹配
        if any(word in tool_desc_lower for word in task_lower.split()):
            relevance += 0.3
            
        # 能力匹配
        for capability in tool.get("capabilities", []):
            if capability.lower() in task_lower:
                relevance += 0.2
                
        return min(relevance, 1.0)
    
    def _personalize_ranking(self, recommendations: List[Dict[str, Any]],
                           user_profile: UserProfile,
                           project_context: ProjectContext) -> List[Dict[str, Any]]:
        """個性化排序"""
        # 根據用戶技能水平調整
        if user_profile.skill_level == "beginner":
            # 初學者偏好簡單易用的工具
            for rec in recommendations:
                if "simple" in rec["tool"]["name"].lower() or rec["tool"]["avg_latency_ms"] < 500:
                    rec["score"] *= 1.2
                    
        elif user_profile.skill_level == "expert":
            # 專家偏好功能強大的工具
            for rec in recommendations:
                if rec["tool"]["category"] in ["ai_analysis", "ai_refactor"]:
                    rec["score"] *= 1.1
        
        # 如果有截止日期壓力，優先快速工具
        if project_context.deadline_pressure:
            for rec in recommendations:
                if rec["tool"]["avg_latency_ms"] < 1000:
                    rec["score"] *= 1.15
        
        # 重新排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    
    def _generate_recommendation_reasoning(self, factors: Dict[str, float]) -> str:
        """生成推薦理由"""
        reasons = []
        
        if factors["user_preference"] > 0.7:
            reasons.append("您經常使用此工具")
        if factors["project_match"] > 0.7:
            reasons.append("非常適合當前項目類型")
        if factors["team_collaboration"] > 0.7:
            reasons.append("團隊推薦使用")
        if factors["task_relevance"] > 0.7:
            reasons.append("與任務高度相關")
            
        return "、".join(reasons) if reasons else "綜合評分較高"
    
    async def update_user_preference(self, user_id: str, tool_id: str, 
                                   feedback: float):
        """更新用戶偏好"""
        profile = self._get_or_create_profile(user_id)
        
        # 使用指數移動平均更新偏好
        alpha = 0.3  # 學習率
        current = profile.preferences.get(tool_id, 0.5)
        profile.preferences[tool_id] = alpha * feedback + (1 - alpha) * current
        
        print(f"✅ 更新用戶 {user_id} 對工具 {tool_id} 的偏好: {profile.preferences[tool_id]:.2f}")

# ============= 2. 工具效果學習系統 =============

@dataclass
class ToolExecutionRecord:
    """工具執行記錄"""
    record_id: str
    tool_id: str
    user_id: str
    timestamp: datetime
    execution_time_ms: int
    success: bool
    error_message: Optional[str] = None
    user_satisfaction: Optional[float] = None  # 1-5
    context: Dict[str, Any] = field(default_factory=dict)

class ToolEffectLearningEngine:
    """工具效果學習引擎"""
    
    def __init__(self):
        self.execution_records = []
        self.tool_statistics = {}
        self.learning_models = {}
        self.quality_thresholds = {
            "min_success_rate": 0.7,
            "max_avg_latency": 5000,
            "min_satisfaction": 3.0
        }
        
    async def record_execution(self, tool_id: str, user_id: str,
                             execution_data: Dict[str, Any]):
        """記錄工具執行"""
        record = ToolExecutionRecord(
            record_id=str(uuid.uuid4()),
            tool_id=tool_id,
            user_id=user_id,
            timestamp=datetime.now(),
            execution_time_ms=execution_data.get("execution_time_ms", 0),
            success=execution_data.get("success", True),
            error_message=execution_data.get("error"),
            context=execution_data.get("context", {})
        )
        
        self.execution_records.append(record)
        
        # 更新統計
        await self._update_statistics(tool_id)
        
        # 觸發學習
        if len(self.execution_records) % 100 == 0:
            await self._run_learning_cycle()
    
    async def _update_statistics(self, tool_id: str):
        """更新工具統計"""
        tool_records = [r for r in self.execution_records if r.tool_id == tool_id]
        
        if not tool_records:
            return
            
        stats = {
            "total_executions": len(tool_records),
            "success_rate": sum(1 for r in tool_records if r.success) / len(tool_records),
            "avg_latency": statistics.mean([r.execution_time_ms for r in tool_records]),
            "error_rate": sum(1 for r in tool_records if r.error_message) / len(tool_records),
            "recent_trend": self._calculate_recent_trend(tool_records),
            "last_updated": datetime.now().isoformat()
        }
        
        # 計算用戶滿意度
        satisfaction_scores = [r.user_satisfaction for r in tool_records if r.user_satisfaction]
        if satisfaction_scores:
            stats["avg_satisfaction"] = statistics.mean(satisfaction_scores)
            
        self.tool_statistics[tool_id] = stats
    
    def _calculate_recent_trend(self, records: List[ToolExecutionRecord]) -> str:
        """計算最近趨勢"""
        if len(records) < 10:
            return "insufficient_data"
            
        # 比較最近10次和之前的成功率
        recent_10 = records[-10:]
        previous = records[:-10]
        
        if not previous:
            return "stable"
            
        recent_success_rate = sum(1 for r in recent_10 if r.success) / 10
        previous_success_rate = sum(1 for r in previous if r.success) / len(previous)
        
        if recent_success_rate > previous_success_rate + 0.1:
            return "improving"
        elif recent_success_rate < previous_success_rate - 0.1:
            return "declining"
        else:
            return "stable"
    
    async def _run_learning_cycle(self):
        """運行學習週期"""
        print("\n🧠 運行工具效果學習週期")
        
        # 1. 識別表現不佳的工具
        poor_performing_tools = []
        
        for tool_id, stats in self.tool_statistics.items():
            if (stats["success_rate"] < self.quality_thresholds["min_success_rate"] or
                stats["avg_latency"] > self.quality_thresholds["max_avg_latency"] or
                stats.get("avg_satisfaction", 5) < self.quality_thresholds["min_satisfaction"]):
                
                poor_performing_tools.append({
                    "tool_id": tool_id,
                    "stats": stats,
                    "issues": self._identify_issues(stats)
                })
        
        # 2. 生成優化建議
        for tool_info in poor_performing_tools:
            recommendations = await self._generate_optimization_recommendations(tool_info)
            tool_info["recommendations"] = recommendations
            
        # 3. 更新工具評分
        await self._update_tool_scores()
        
        print(f"✅ 學習週期完成，識別出 {len(poor_performing_tools)} 個需要優化的工具")
        
        return poor_performing_tools
    
    def _identify_issues(self, stats: Dict[str, Any]) -> List[str]:
        """識別問題"""
        issues = []
        
        if stats["success_rate"] < self.quality_thresholds["min_success_rate"]:
            issues.append(f"成功率過低: {stats['success_rate']:.1%}")
            
        if stats["avg_latency"] > self.quality_thresholds["max_avg_latency"]:
            issues.append(f"響應時間過長: {stats['avg_latency']}ms")
            
        if stats.get("avg_satisfaction", 5) < self.quality_thresholds["min_satisfaction"]:
            issues.append(f"用戶滿意度低: {stats['avg_satisfaction']:.1f}/5")
            
        if stats["error_rate"] > 0.2:
            issues.append(f"錯誤率過高: {stats['error_rate']:.1%}")
            
        return issues
    
    async def _generate_optimization_recommendations(self, 
                                                   tool_info: Dict[str, Any]) -> List[str]:
        """生成優化建議"""
        recommendations = []
        stats = tool_info["stats"]
        
        if stats["success_rate"] < 0.7:
            recommendations.append("考慮切換到更穩定的替代工具")
            recommendations.append("增加錯誤處理和重試機制")
            
        if stats["avg_latency"] > 5000:
            recommendations.append("啟用結果緩存以提高響應速度")
            recommendations.append("考慮使用異步執行模式")
            
        if stats["recent_trend"] == "declining":
            recommendations.append("檢查最近的 API 變更")
            recommendations.append("聯繫工具提供方報告問題")
            
        return recommendations
    
    async def _update_tool_scores(self):
        """更新工具評分"""
        for tool_id, stats in self.tool_statistics.items():
            # 綜合評分算法
            score = (
                stats["success_rate"] * 0.4 +
                (1 - min(stats["avg_latency"] / 10000, 1)) * 0.3 +
                (stats.get("avg_satisfaction", 3) / 5) * 0.3
            )
            
            stats["quality_score"] = score
            stats["recommendation"] = "recommended" if score > 0.7 else "use_with_caution"
    
    async def get_tool_performance(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """獲取工具性能數據"""
        return self.tool_statistics.get(tool_id)
    
    async def should_exclude_tool(self, tool_id: str) -> bool:
        """判斷是否應該排除工具"""
        stats = self.tool_statistics.get(tool_id)
        
        if not stats:
            return False
            
        # 自動淘汰標準
        if (stats["total_executions"] > 50 and  # 有足夠的數據
            stats["success_rate"] < 0.5 and      # 成功率太低
            stats["recent_trend"] == "declining"):  # 持續惡化
            return True
            
        return False

# ============= 3. 自定義工具開發系統 =============

@dataclass
class CustomTool:
    """自定義工具定義"""
    tool_id: str
    name: str
    description: str
    author_id: str
    category: str
    version: str
    api_endpoint: Optional[str] = None
    script_content: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    rating: float = 0.0
    downloads: int = 0
    verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)

class CustomToolDevelopmentSDK:
    """自定義工具開發 SDK"""
    
    def __init__(self):
        self.custom_tools = {}
        self.tool_templates = self._load_templates()
        self.verification_engine = ToolVerificationEngine()
        self.rating_system = ToolRatingSystem()
        
    def _load_templates(self) -> Dict[str, str]:
        """加載工具模板"""
        return {
            "basic_script": """
# Custom Tool Template
import asyncio

async def execute(params):
    '''
    Tool execution function
    :param params: Dictionary containing tool parameters
    :return: Tool execution result
    '''
    # Your tool logic here
    result = {
        'status': 'success',
        'output': 'Tool executed successfully'
    }
    return result

# Tool metadata
METADATA = {
    'name': 'My Custom Tool',
    'description': 'Description of what this tool does',
    'category': 'custom',
    'parameters': {
        'input': {'type': 'string', 'required': True},
        'options': {'type': 'object', 'required': False}
    }
}
""",
            "api_wrapper": """
# API Wrapper Template
import httpx
import asyncio

class CustomAPITool:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = 'https://api.example.com'
        
    async def execute(self, params):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/endpoint',
                json=params,
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            return response.json()
"""
        }
    
    async def create_custom_tool(self, author_id: str, 
                               tool_definition: Dict[str, Any]) -> CustomTool:
        """創建自定義工具"""
        print(f"\n🔨 創建自定義工具: {tool_definition['name']}")
        
        # 生成工具 ID
        tool_id = f"custom_{author_id}_{uuid.uuid4().hex[:8]}"
        
        # 創建工具實例
        custom_tool = CustomTool(
            tool_id=tool_id,
            name=tool_definition["name"],
            description=tool_definition["description"],
            author_id=author_id,
            category=tool_definition.get("category", "custom"),
            version="1.0.0",
            api_endpoint=tool_definition.get("api_endpoint"),
            script_content=tool_definition.get("script_content"),
            parameters=tool_definition.get("parameters", {}),
            requirements=tool_definition.get("requirements", [])
        )
        
        # 驗證工具
        validation_result = await self.verification_engine.verify_tool(custom_tool)
        
        if validation_result["valid"]:
            self.custom_tools[tool_id] = custom_tool
            print(f"✅ 工具創建成功: {tool_id}")
            return custom_tool
        else:
            raise ValueError(f"工具驗證失敗: {validation_result['errors']}")
    
    def get_tool_template(self, template_type: str) -> str:
        """獲取工具模板"""
        return self.tool_templates.get(template_type, self.tool_templates["basic_script"])
    
    async def test_custom_tool(self, tool_id: str, 
                             test_params: Dict[str, Any]) -> Dict[str, Any]:
        """測試自定義工具"""
        if tool_id not in self.custom_tools:
            return {"error": "Tool not found"}
            
        tool = self.custom_tools[tool_id]
        
        try:
            # 執行工具（這裡是模擬）
            result = {
                "status": "success",
                "output": f"Test execution of {tool.name}",
                "execution_time": 100,
                "test_params": test_params
            }
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def publish_tool(self, tool_id: str) -> Dict[str, Any]:
        """發布工具到市場"""
        if tool_id not in self.custom_tools:
            return {"error": "Tool not found"}
            
        tool = self.custom_tools[tool_id]
        
        # 最終驗證
        final_check = await self.verification_engine.final_verification(tool)
        
        if final_check["approved"]:
            tool.verified = True
            
            # 添加到公開市場（模擬）
            return {
                "status": "published",
                "tool_id": tool_id,
                "marketplace_url": f"https://tools.powerautomation.ai/{tool_id}"
            }
        else:
            return {
                "status": "rejected",
                "reasons": final_check["reasons"]
            }

class ToolVerificationEngine:
    """工具驗證引擎"""
    
    async def verify_tool(self, tool: CustomTool) -> Dict[str, Any]:
        """驗證工具"""
        errors = []
        warnings = []
        
        # 1. 基本信息檢查
        if len(tool.name) < 3:
            errors.append("工具名稱太短")
        if len(tool.description) < 10:
            errors.append("描述信息不足")
            
        # 2. 安全檢查（簡化版）
        if tool.script_content:
            dangerous_patterns = ["eval", "exec", "__import__", "os.system"]
            for pattern in dangerous_patterns:
                if pattern in tool.script_content:
                    errors.append(f"檢測到潛在危險代碼: {pattern}")
                    
        # 3. 參數檢查
        if not tool.parameters:
            warnings.append("未定義輸入參數")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def final_verification(self, tool: CustomTool) -> Dict[str, Any]:
        """最終發布前驗證"""
        # 更嚴格的檢查
        reasons = []
        
        # 必須通過基本驗證
        basic_check = await self.verify_tool(tool)
        if not basic_check["valid"]:
            reasons.extend(basic_check["errors"])
            
        # 必須有完整文檔
        if not tool.parameters or not tool.description:
            reasons.append("文檔不完整")
            
        return {
            "approved": len(reasons) == 0,
            "reasons": reasons
        }

class ToolRatingSystem:
    """工具評分系統"""
    
    def __init__(self):
        self.ratings = {}  # tool_id -> list of ratings
        self.reviews = {}  # tool_id -> list of reviews
        
    async def rate_tool(self, tool_id: str, user_id: str, 
                       rating: float, review: Optional[str] = None):
        """為工具評分"""
        if tool_id not in self.ratings:
            self.ratings[tool_id] = []
            self.reviews[tool_id] = []
            
        # 記錄評分
        self.ratings[tool_id].append({
            "user_id": user_id,
            "rating": rating,
            "timestamp": datetime.now()
        })
        
        # 記錄評論
        if review:
            self.reviews[tool_id].append({
                "user_id": user_id,
                "review": review,
                "rating": rating,
                "timestamp": datetime.now()
            })
            
        # 更新平均評分
        avg_rating = statistics.mean([r["rating"] for r in self.ratings[tool_id]])
        
        return {
            "average_rating": avg_rating,
            "total_ratings": len(self.ratings[tool_id])
        }
    
    def get_tool_rating(self, tool_id: str) -> Dict[str, Any]:
        """獲取工具評分"""
        if tool_id not in self.ratings:
            return {"average_rating": 0, "total_ratings": 0}
            
        ratings_list = [r["rating"] for r in self.ratings[tool_id]]
        
        return {
            "average_rating": statistics.mean(ratings_list),
            "total_ratings": len(ratings_list),
            "rating_distribution": {
                "5": sum(1 for r in ratings_list if r >= 4.5),
                "4": sum(1 for r in ratings_list if 3.5 <= r < 4.5),
                "3": sum(1 for r in ratings_list if 2.5 <= r < 3.5),
                "2": sum(1 for r in ratings_list if 1.5 <= r < 2.5),
                "1": sum(1 for r in ratings_list if r < 1.5)
            }
        }

# ============= 整合演示 =============

async def demonstrate_advanced_systems():
    """演示進階系統功能"""
    print("🚀 進階工具智能系統演示")
    print("="*70)
    
    # 模擬 External Tools MCP
    class MockExternalToolsMCP:
        async def handle_request(self, method, params):
            if method == "list_tools":
                return {
                    "tools": [
                        {"id": "prettier", "name": "Prettier", "category": "format"},
                        {"id": "eslint", "name": "ESLint", "category": "lint"},
                        {"id": "jest", "name": "Jest", "category": "test"}
                    ]
                }
            return {}
    
    external_tools_mcp = MockExternalToolsMCP()
    
    # 1. 智能推薦系統演示
    print("\n📍 1. 工具智能推薦系統")
    print("-"*50)
    
    recommendation_system = IntelligentRecommendationSystem(external_tools_mcp)
    
    # 模擬用戶請求
    recommendations = await recommendation_system.get_personalized_recommendations(
        user_id="user123",
        task="format and test my React code",
        context={
            "project_type": "frontend",
            "framework": "react",
            "language": "javascript",
            "team_size": 5,
            "complexity": "high"
        }
    )
    
    print("\n推薦結果:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"{i}. {rec['tool']['name']}")
        print(f"   評分: {rec['score']:.2f}")
        print(f"   理由: {rec['reasoning']}")
    
    # 2. 工具效果學習演示
    print("\n\n📍 2. 工具效果學習系統")
    print("-"*50)
    
    learning_engine = ToolEffectLearningEngine()
    
    # 模擬執行記錄
    for i in range(20):
        await learning_engine.record_execution(
            tool_id="prettier",
            user_id="user123",
            execution_data={
                "execution_time_ms": 100 + i * 10,
                "success": i % 5 != 0,  # 20% 失敗率
                "context": {"file_size": 1000 + i * 100}
            }
        )
    
    # 獲取工具性能
    performance = await learning_engine.get_tool_performance("prettier")
    print(f"\nPrettier 性能統計:")
    print(f"  成功率: {performance['success_rate']:.1%}")
    print(f"  平均延遲: {performance['avg_latency']:.0f}ms")
    print(f"  趨勢: {performance['recent_trend']}")
    
    # 3. 自定義工具開發演示
    print("\n\n📍 3. 自定義工具開發系統")
    print("-"*50)
    
    sdk = CustomToolDevelopmentSDK()
    
    # 創建自定義工具
    custom_tool = await sdk.create_custom_tool(
        author_id="dev001",
        tool_definition={
            "name": "React Component Generator",
            "description": "Automatically generates React component boilerplate",
            "category": "code_generation",
            "parameters": {
                "component_name": {"type": "string", "required": True},
                "use_typescript": {"type": "boolean", "default": True}
            },
            "script_content": sdk.get_tool_template("basic_script")
        }
    )
    
    print(f"\n創建的自定義工具:")
    print(f"  ID: {custom_tool.tool_id}")
    print(f"  名稱: {custom_tool.name}")
    print(f"  作者: {custom_tool.author_id}")
    
    # 測試工具
    test_result = await sdk.test_custom_tool(
        custom_tool.tool_id,
        {"component_name": "MyComponent", "use_typescript": True}
    )
    print(f"\n測試結果: {test_result['status']}")
    
    # 發布工具
    publish_result = await sdk.publish_tool(custom_tool.tool_id)
    print(f"發布結果: {publish_result['status']}")
    
    # 總結
    print("\n" + "="*70)
    print("✨ 進階系統效果總結")
    print("="*70)
    print("\n1. 智能推薦讓工具選擇更精準")
    print("2. 效果學習持續優化工具質量")
    print("3. 自定義開發打造工具生態系統")
    print("\n🎯 這些系統將 K2 的工具調用能力提升到新的高度！")

if __name__ == "__main__":
    asyncio.run(demonstrate_advanced_systems())