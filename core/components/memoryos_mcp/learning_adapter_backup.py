#!/usr/bin/env python3
"""
MemoryOS MCP - 學習適配器
處理不同來源的學習數據並進行適配
支持模式感知的个性化处理
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class LearningType(Enum):
    """學習類型"""
    CLAUDE_INTERACTION = "claude_interaction"
    USER_BEHAVIOR = "user_behavior"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ERROR_CORRECTION = "error_correction"
    CONTEXT_ENHANCEMENT = "context_enhancement"

class InteractionMode(Enum):
    """交互模式"""
    TEACHER_MODE = "teacher_mode"      # Claude Code Tool + Claude 模型
    ASSISTANT_MODE = "assistant_mode"  # 其他工具和模型

@dataclass
class QueryContext:
    """查询上下文"""
    current_tool: str
    current_model: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    interaction_history: List[Dict[str, Any]] = None
    user_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.interaction_history is None:
            self.interaction_history = []
        if self.user_preferences is None:
            self.user_preferences = {}

@dataclass
class LearningData:
    """學習數據"""
    id: str
    source: str
    learning_type: LearningType
    interaction_mode: InteractionMode
    data: Dict[str, Any]
    performance_metrics: Dict[str, float]
    timestamp: float
    success: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        result = asdict(self)
        result['learning_type'] = self.learning_type.value
        result['interaction_mode'] = self.interaction_mode.value
        return result

class LearningAdapter:
    """學習適配器 - 支持模式感知的个性化处理"""
    
    def __init__(self, memory_engine, context_manager):
        self.memory_engine = memory_engine
        self.context_manager = context_manager
        self.learning_history = deque(maxlen=1000)
        self.performance_tracker = defaultdict(list)
        self.learning_patterns = defaultdict(dict)
        self.adaptation_rules = {}
        self.user_profiles = defaultdict(dict)  # 用户个性化配置
        self.mode_preferences = defaultdict(dict)  # 模式偏好设置
        self.is_initialized = False
        
    async def initialize(self):
        """初始化學習適配器"""
        logger.info("🧠 初始化 Learning Adapter...")
        
        # 載入適配規則
        await self._load_adaptation_rules()
        
        # 初始化性能追蹤器
        await self._initialize_performance_tracker()
        
        # 初始化模式感知配置
        await self._initialize_mode_awareness()
        
        self.is_initialized = True
        logger.info("✅ Learning Adapter 初始化完成")
    
    async def _initialize_mode_awareness(self):
        """初始化模式感知配置"""
        # 教师模式配置
        self.mode_preferences[InteractionMode.TEACHER_MODE] = {
            "response_style": "detailed_technical",
            "explanation_depth": "comprehensive",
            "code_review_level": "strict",
            "best_practices_emphasis": True,
            "academic_tone": True,
            "example_complexity": "advanced",
            "error_handling_focus": True
        }
        
        # 助手模式配置
        self.mode_preferences[InteractionMode.ASSISTANT_MODE] = {
            "response_style": "concise_practical",
            "explanation_depth": "essential",
            "code_review_level": "moderate",
            "best_practices_emphasis": False,
            "academic_tone": False,
            "example_complexity": "simple",
            "error_handling_focus": False
        }
        
        logger.info("✅ 模式感知配置初始化完成")
    
    def detect_interaction_mode(self, context: QueryContext) -> InteractionMode:
        """检测交互模式"""
        if (context.current_tool == "claude_code_tool" and 
            context.current_model == "claude"):
            return InteractionMode.TEACHER_MODE
        else:
            return InteractionMode.ASSISTANT_MODE
    
    async def personalize_response(self, response: str, context: QueryContext) -> str:
        """个性化响应处理"""
        try:
            # 检测当前模式
            current_mode = self.detect_interaction_mode(context)
            
            # 根据模式调整个性化策略
            if current_mode == InteractionMode.TEACHER_MODE:
                return await self._teacher_mode_personalization(response, context)
            else:
                return await self._assistant_mode_personalization(response, context)
                
        except Exception as e:
            logger.error(f"❌ 个性化处理失败: {e}")
            return response
    
    async def _teacher_mode_personalization(self, response: str, context: QueryContext) -> str:
        """教师模式个性化处理"""
        try:
            # 获取用户技术栈偏好
            user_preferences = await self._get_user_preferences(context.user_id)
            tech_stack = user_preferences.get("tech_stack", [])
            
            # 调整技术深度
            if user_preferences.get("experience_level") == "beginner":
                response = await self._add_detailed_explanations(response)
            elif user_preferences.get("experience_level") == "expert":
                response = await self._add_advanced_insights(response)
            
            # 匹配用户偏好的代码风格
            preferred_style = user_preferences.get("code_style", "standard")
            if preferred_style != "standard":
                response = await self._adjust_code_style(response, preferred_style)
            
            # 推荐相关的项目资源
            if tech_stack:
                response = await self._add_resource_recommendations(response, tech_stack)
            
            # 优化解释方式
            learning_style = user_preferences.get("learning_style", "visual")
            response = await self._optimize_explanation_style(response, learning_style)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ 教师模式个性化失败: {e}")
            return response
    
    async def _assistant_mode_personalization(self, response: str, context: QueryContext) -> str:
        """助手模式个性化处理"""
        try:
            # 获取用户偏好
            user_preferences = await self._get_user_preferences(context.user_id)
            
            # 快速实用的回答风格
            if user_preferences.get("prefer_concise", True):
                response = await self._make_response_concise(response)
            
            # 简洁的代码示例
            response = await self._simplify_code_examples(response)
            
            # 效率优先的建议
            response = await self._add_efficiency_tips(response)
            
            # 轻松的交流风格
            response = await self._adjust_tone_casual(response)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ 助手模式个性化失败: {e}")
            return response
    
    async def _get_user_preferences(self, user_id: Optional[str]) -> Dict[str, Any]:
        """获取用户偏好设置"""
        if not user_id:
            return {}
        
        if user_id not in self.user_profiles:
            # 从记忆中加载用户偏好
            user_memories = await self.memory_engine.search_memories(
                query=f"user_preferences_{user_id}",
                memory_type=self.memory_engine.MemoryType.SYSTEM_STATE,
                limit=1
            )
            
            if user_memories:
                self.user_profiles[user_id] = user_memories[0].metadata.get("preferences", {})
            else:
                # 默认偏好设置
                self.user_profiles[user_id] = {
                    "experience_level": "intermediate",
                    "tech_stack": ["python", "javascript"],
                    "code_style": "standard",
                    "learning_style": "visual",
                    "prefer_concise": True
                }
        
        return self.user_profiles[user_id]
    
    async def learn_user_preferences(self, context: QueryContext, feedback: Dict[str, Any]):
        """学习用户偏好"""
        try:
            if not context.user_id:
                return
            
            current_mode = self.detect_interaction_mode(context)
            user_preferences = await self._get_user_preferences(context.user_id)
            
            # 根据反馈调整偏好
            if feedback.get("too_detailed"):
                if current_mode == InteractionMode.TEACHER_MODE:
                    user_preferences["experience_level"] = "expert"
                else:
                    user_preferences["prefer_concise"] = True
            
            if feedback.get("too_simple"):
                if current_mode == InteractionMode.TEACHER_MODE:
                    user_preferences["experience_level"] = "beginner"
                else:
                    user_preferences["prefer_concise"] = False
            
            # 学习技术栈偏好
            mentioned_tech = feedback.get("mentioned_technologies", [])
            if mentioned_tech:
                current_tech = set(user_preferences.get("tech_stack", []))
                current_tech.update(mentioned_tech)
                user_preferences["tech_stack"] = list(current_tech)
            
            # 学习交流风格偏好
            if feedback.get("preferred_tone"):
                user_preferences["preferred_tone"] = feedback["preferred_tone"]
            
            # 更新用户配置
            self.user_profiles[context.user_id] = user_preferences
            
            # 存储到记忆系统
            await self._save_user_preferences(context.user_id, user_preferences)
            
            logger.info(f"✅ 学习用户偏好: {context.user_id}")
            
        except Exception as e:
            logger.error(f"❌ 学习用户偏好失败: {e}")
    
    async def _save_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """保存用户偏好到记忆系统"""
        from .memory_engine import Memory, MemoryType
        
        memory = Memory(
            id=f"user_preferences_{user_id}",
            memory_type=MemoryType.SYSTEM_STATE,
            content=f"用户 {user_id} 的偏好设置",
            metadata={
                "preferences": preferences,
                "last_updated": time.time()
            },
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            importance_score=0.9,
            tags=["user_preferences", "personalization"]
        )
        
        await self.memory_engine.store_memory(memory)
    
    # 个性化处理的具体实现方法
    async def _add_detailed_explanations(self, response: str) -> str:
        """为初学者添加详细解释"""
        # 简单的实现，实际应用中可以使用更复杂的NLP处理
        if "def " in response or "function" in response:
            response += "\n\n💡 **详细解释**: 这个函数的作用是..."
        return response
    
    async def _add_advanced_insights(self, response: str) -> str:
        """为专家添加高级见解"""
        if "import " in response:
            response += "\n\n🔬 **高级提示**: 考虑使用更高效的实现方式..."
        return response
    
    async def _adjust_code_style(self, response: str, style: str) -> str:
        """调整代码风格"""
        # 根据用户偏好调整代码风格
        return response
    
    async def _add_resource_recommendations(self, response: str, tech_stack: List[str]) -> str:
        """添加资源推荐"""
        if tech_stack:
            response += f"\n\n📚 **相关资源**: 基于您的技术栈 {', '.join(tech_stack)}..."
        return response
    
    async def _optimize_explanation_style(self, response: str, learning_style: str) -> str:
        """优化解释方式"""
        if learning_style == "visual" and "```" in response:
            response += "\n\n📊 **可视化提示**: 建议绘制流程图来理解..."
        return response
    
    async def _make_response_concise(self, response: str) -> str:
        """使回答更简洁"""
        # 简化实现
        lines = response.split('\n')
        if len(lines) > 10:
            response = '\n'.join(lines[:8]) + "\n\n... (简化显示)"
        return response
    
    async def _simplify_code_examples(self, response: str) -> str:
        """简化代码示例"""
        return response
    
    async def _add_efficiency_tips(self, response: str) -> str:
        """添加效率提示"""
        if "for " in response or "while " in response:
            response += "\n\n⚡ **效率提示**: 考虑使用列表推导式..."
        return response
    
    async def _adjust_tone_casual(self, response: str) -> str:
        """调整为轻松语调"""
        return response.replace("您", "你").replace("请注意", "注意")
    
    async def get_personalization_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """获取个性化统计信息"""
        stats = {
            "total_users": len(self.user_profiles),
            "mode_distribution": defaultdict(int),
            "preference_trends": defaultdict(int)
        }
        
        # 统计模式分布
        for learning_data in self.learning_history:
            stats["mode_distribution"][learning_data.interaction_mode.value] += 1
        
        # 统计偏好趋势
        for user_prefs in self.user_profiles.values():
            for key, value in user_prefs.items():
                if isinstance(value, (str, bool)):
                    stats["preference_trends"][f"{key}_{value}"] += 1
        
        if user_id and user_id in self.user_profiles:
            stats["user_preferences"] = self.user_profiles[user_id]
        
        return dict(stats)
    async def _load_adaptation_rules(self):
        """載入適配規則"""
        self.adaptation_rules = {
            LearningType.CLAUDE_INTERACTION: {
                "weight": 1.0,
                "adaptation_rate": 0.1,
                "success_threshold": 0.7,
                "features": ["user_satisfaction", "response_time", "context_relevance"]
            },
            LearningType.USER_BEHAVIOR: {
                "weight": 0.8,
                "adaptation_rate": 0.15,
                "success_threshold": 0.6,
                "features": ["interaction_frequency", "preference_consistency", "workflow_efficiency"]
            },
            LearningType.PERFORMANCE_OPTIMIZATION: {
                "weight": 0.9,
                "adaptation_rate": 0.05,
                "success_threshold": 0.8,
                "features": ["response_time", "accuracy", "resource_usage"]
            },
            LearningType.ERROR_CORRECTION: {
                "weight": 1.2,
                "adaptation_rate": 0.2,
                "success_threshold": 0.9,
                "features": ["error_rate", "correction_accuracy", "learning_speed"]
            },
            LearningType.CONTEXT_ENHANCEMENT: {
                "weight": 0.7,
                "adaptation_rate": 0.12,
                "success_threshold": 0.65,
                "features": ["context_relevance", "enhancement_quality", "user_acceptance"]
            }
        }
    
    async def _initialize_performance_tracker(self):
        """初始化性能追蹤器"""
        for learning_type in LearningType:
            self.performance_tracker[learning_type] = []
    
    async def process_interaction(self, interaction_data: Dict[str, Any]):
        """處理交互數據"""
        try:
            # 提取學習特徵
            features = await self._extract_learning_features(interaction_data)
            
            # 評估交互質量
            quality_score = await self._evaluate_interaction_quality(interaction_data, features)
            
            # 更新學習模式
            await self._update_learning_patterns(interaction_data, features, quality_score)
            
            # 存儲學習數據
            learning_data = LearningData(
                id=f"learning_{int(time.time())}_{hash(str(interaction_data)) % 10000}",
                source="claude_interaction",
                learning_type=LearningType.CLAUDE_INTERACTION,
                data={
                    "interaction": interaction_data,
                    "features": features,
                    "quality_score": quality_score
                },
                performance_metrics={
                    "response_time": interaction_data.get("response_time", 0),
                    "user_satisfaction": interaction_data.get("user_satisfaction", 0),
                    "context_relevance": features.get("context_relevance", 0)
                },
                timestamp=time.time(),
                success=quality_score > 0.5
            )
            
            await self._store_learning_data(learning_data)
            
            logger.debug(f"✅ 處理交互學習: {learning_data.id} (質量: {quality_score:.3f})")
            
        except Exception as e:
            logger.error(f"❌ 處理交互學習失敗: {e}")
    
    async def _extract_learning_features(self, interaction_data: Dict[str, Any]) -> Dict[str, float]:
        """提取學習特徵"""
        features = {}
        
        # 基本特徵
        features["response_time"] = min(1.0, 5000.0 / max(1.0, interaction_data.get("response_time", 5000)))
        features["user_satisfaction"] = interaction_data.get("user_satisfaction", 0.5)
        features["input_length"] = min(1.0, len(interaction_data.get("user_input", "")) / 1000.0)
        features["output_length"] = min(1.0, len(interaction_data.get("claude_response", "")) / 2000.0)
        
        # 上下文特徵
        context_id = interaction_data.get("context_id")
        if context_id:
            context = await self.context_manager.get_context(context_id)
            if context:
                features["context_relevance"] = context.relevance_score
                features["context_age"] = min(1.0, (time.time() - context.created_at) / 3600.0)
        
        # 歷史特徵
        user_input = interaction_data.get("user_input", "")
        similar_interactions = await self.memory_engine.get_similar_memories(
            content=user_input,
            memory_type=self.memory_engine.MemoryType.CLAUDE_INTERACTION,
            limit=3
        )
        
        if similar_interactions:
            features["similarity_score"] = np.mean([mem.importance_score for mem in similar_interactions])
            features["repetition_factor"] = len(similar_interactions) / 10.0
        else:
            features["similarity_score"] = 0.0
            features["repetition_factor"] = 0.0
        
        return features
    
    async def _evaluate_interaction_quality(self, 
                                          interaction_data: Dict[str, Any], 
                                          features: Dict[str, float]) -> float:
        """評估交互質量"""
        quality_components = []
        
        # 用戶滿意度 (40%)
        user_satisfaction = interaction_data.get("user_satisfaction", 0.5)
        quality_components.append(user_satisfaction * 0.4)
        
        # 響應效率 (25%)
        response_efficiency = features.get("response_time", 0.5)
        quality_components.append(response_efficiency * 0.25)
        
        # 內容相關性 (20%)
        content_relevance = features.get("context_relevance", 0.5)
        quality_components.append(content_relevance * 0.2)
        
        # 輸出質量 (15%)
        output_quality = min(1.0, features.get("output_length", 0.5) * 2.0)
        quality_components.append(output_quality * 0.15)
        
        return sum(quality_components)
    
    async def _update_learning_patterns(self, 
                                      interaction_data: Dict[str, Any], 
                                      features: Dict[str, float], 
                                      quality_score: float):
        """更新學習模式"""
        user_input = interaction_data.get("user_input", "")
        
        # 提取關鍵詞
        keywords = self._extract_keywords(user_input)
        
        # 更新模式
        for keyword in keywords:
            if keyword not in self.learning_patterns[LearningType.CLAUDE_INTERACTION]:
                self.learning_patterns[LearningType.CLAUDE_INTERACTION][keyword] = {
                    "count": 0,
                    "total_quality": 0.0,
                    "avg_quality": 0.0,
                    "features": defaultdict(list)
                }
            
            pattern = self.learning_patterns[LearningType.CLAUDE_INTERACTION][keyword]
            pattern["count"] += 1
            pattern["total_quality"] += quality_score
            pattern["avg_quality"] = pattern["total_quality"] / pattern["count"]
            
            # 更新特徵
            for feature, value in features.items():
                pattern["features"][feature].append(value)
                # 保持最近的特徵值
                if len(pattern["features"][feature]) > 20:
                    pattern["features"][feature] = pattern["features"][feature][-20:]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取關鍵詞"""
        # 簡化的關鍵詞提取
        words = text.lower().split()
        keywords = []
        
        # 編程相關關鍵詞
        programming_keywords = {
            "python", "javascript", "java", "c++", "html", "css", "sql",
            "react", "vue", "angular", "nodejs", "django", "flask",
            "function", "class", "variable", "loop", "condition",
            "debug", "error", "exception", "test", "api", "database"
        }
        
        for word in words:
            if word in programming_keywords or len(word) > 3:
                keywords.append(word)
        
        return keywords[:10]  # 限制關鍵詞數量
    
    async def record_learning_data(self, 
                                 source: str, 
                                 data: Dict[str, Any], 
                                 learning_type: str, 
                                 timestamp: float):
        """記錄學習數據"""
        try:
            # 轉換學習類型
            learning_type_enum = LearningType(learning_type)
            
            # 提取性能指標
            performance_metrics = data.get("performance_metrics", {})
            
            # 創建學習數據
            learning_data = LearningData(
                id=f"learning_{int(timestamp)}_{hash(str(data)) % 10000}",
                source=source,
                learning_type=learning_type_enum,
                data=data,
                performance_metrics=performance_metrics,
                timestamp=timestamp,
                success=data.get("success", True)
            )
            
            await self._store_learning_data(learning_data)
            
            # 更新性能追蹤
            await self._update_performance_tracker(learning_data)
            
            logger.debug(f"✅ 記錄學習數據: {learning_data.id} ({source})")
            
        except Exception as e:
            logger.error(f"❌ 記錄學習數據失敗: {e}")
    
    async def _store_learning_data(self, learning_data: LearningData):
        """存儲學習數據"""
        # 添加到歷史記錄
        self.learning_history.append(learning_data)
        
        # 存儲到記憶引擎
        memory_id = f"learning_{learning_data.id}"
        
        memory = self.memory_engine.Memory(
            id=memory_id,
            memory_type=self.memory_engine.MemoryType.PROCEDURAL,
            content=json.dumps(learning_data.to_dict()),
            metadata={
                "source": learning_data.source,
                "learning_type": learning_data.learning_type.value,
                "success": learning_data.success,
                "performance_metrics": learning_data.performance_metrics
            },
            created_at=learning_data.timestamp,
            accessed_at=learning_data.timestamp,
            access_count=1,
            importance_score=self._calculate_learning_importance(learning_data),
            tags=["learning", learning_data.learning_type.value, learning_data.source]
        )
        
        await self.memory_engine.store_memory(memory)
    
    def _calculate_learning_importance(self, learning_data: LearningData) -> float:
        """計算學習重要性"""
        base_importance = 0.5
        
        # 成功率影響
        if learning_data.success:
            base_importance *= 1.2
        else:
            base_importance *= 0.8
        
        # 學習類型權重
        type_weight = self.adaptation_rules.get(learning_data.learning_type, {}).get("weight", 1.0)
        base_importance *= type_weight
        
        # 性能指標影響
        performance_avg = np.mean(list(learning_data.performance_metrics.values())) if learning_data.performance_metrics else 0.5
        base_importance *= (0.5 + performance_avg * 0.5)
        
        return min(2.0, max(0.1, base_importance))
    
    async def _update_performance_tracker(self, learning_data: LearningData):
        """更新性能追蹤器"""
        tracker = self.performance_tracker[learning_data.learning_type]
        
        # 添加性能數據
        tracker.append({
            "timestamp": learning_data.timestamp,
            "success": learning_data.success,
            "metrics": learning_data.performance_metrics,
            "importance": self._calculate_learning_importance(learning_data)
        })
        
        # 保持最近的性能數據
        if len(tracker) > 100:
            self.performance_tracker[learning_data.learning_type] = tracker[-100:]
    
    async def get_best_practices(self, query: str, domain: str = "general") -> List[Dict[str, Any]]:
        """獲取最佳實踐"""
        try:
            # 搜索相關的學習記憶
            learning_memories = await self.memory_engine.search_memories(
                query=query,
                memory_type=self.memory_engine.MemoryType.PROCEDURAL,
                tags=["learning"],
                limit=10
            )
            
            best_practices = []
            
            for memory in learning_memories:
                try:
                    learning_data = json.loads(memory.content)
                    
                    # 過濾成功的學習數據
                    if learning_data.get("success", False):
                        performance_metrics = learning_data.get("performance_metrics", {})
                        
                        # 計算實践質量
                        quality_score = np.mean(list(performance_metrics.values())) if performance_metrics else 0.5
                        
                        if quality_score > 0.6:
                            best_practices.append({
                                "id": memory.id,
                                "content": learning_data.get("data", {}).get("interaction", {}).get("claude_response", "")[:200],
                                "quality_score": quality_score,
                                "domain": domain,
                                "tags": memory.tags,
                                "timestamp": memory.created_at
                            })
                            
                except Exception as e:
                    logger.warning(f"解析學習數據失敗: {e}")
                    continue
            
            # 按質量排序
            best_practices.sort(key=lambda x: x["quality_score"], reverse=True)
            
            return best_practices[:5]
            
        except Exception as e:
            logger.error(f"❌ 獲取最佳實踐失敗: {e}")
            return []
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """獲取學習統計"""
        try:
            stats = {
                "total_learning_records": len(self.learning_history),
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "context_enhancement_rate": 0.0,
                "avg_user_satisfaction": 0.0,
                "learning_type_distribution": {},
                "performance_trends": {}
            }
            
            if self.learning_history:
                # 成功率
                successful_records = [ld for ld in self.learning_history if ld.success]
                stats["success_rate"] = len(successful_records) / len(self.learning_history)
                
                # 平均響應時間
                response_times = [ld.performance_metrics.get("response_time", 0) for ld in self.learning_history]
                stats["avg_response_time"] = np.mean(response_times) if response_times else 0.0
                
                # 平均用戶滿意度
                satisfactions = [ld.performance_metrics.get("user_satisfaction", 0) for ld in self.learning_history]
                stats["avg_user_satisfaction"] = np.mean(satisfactions) if satisfactions else 0.0
                
                # 學習類型分佈
                for learning_data in self.learning_history:
                    type_name = learning_data.learning_type.value
                    stats["learning_type_distribution"][type_name] = stats["learning_type_distribution"].get(type_name, 0) + 1
                
                # 上下文增強率
                enhanced_count = sum(1 for ld in self.learning_history 
                                   if ld.data.get("interaction", {}).get("context_enhanced", False))
                stats["context_enhancement_rate"] = enhanced_count / len(self.learning_history)
            
            # 性能趨勢
            for learning_type, tracker in self.performance_tracker.items():
                if tracker:
                    recent_performance = tracker[-10:]  # 最近10個記錄
                    stats["performance_trends"][learning_type.value] = {
                        "recent_success_rate": np.mean([p["success"] for p in recent_performance]),
                        "trend_direction": "up" if len(recent_performance) > 5 else "stable"
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 獲取學習統計失敗: {e}")
            return {}
    
    async def optimize_learning_parameters(self):
        """優化學習參數"""
        try:
            logger.info("🔧 優化學習參數...")
            
            # 分析學習模式
            for learning_type, patterns in self.learning_patterns.items():
                if not patterns:
                    continue
                
                # 獲取適配規則
                rules = self.adaptation_rules.get(learning_type, {})
                
                # 計算平均性能
                avg_quality = np.mean([pattern["avg_quality"] for pattern in patterns.values()])
                
                # 調整適配率
                if avg_quality > rules.get("success_threshold", 0.7):
                    # 性能良好，降低適配率
                    rules["adaptation_rate"] = max(0.01, rules["adaptation_rate"] * 0.95)
                else:
                    # 性能不佳，提高適配率
                    rules["adaptation_rate"] = min(0.5, rules["adaptation_rate"] * 1.05)
                
                logger.debug(f"📊 調整 {learning_type.value} 適配率: {rules['adaptation_rate']:.4f}")
            
            logger.info("✅ 學習參數優化完成")
            
        except Exception as e:
            logger.error(f"❌ 優化學習參數失敗: {e}")
    
    async def cleanup(self):
        """清理資源"""
        self.learning_history.clear()
        self.performance_tracker.clear()
        self.learning_patterns.clear()
        logger.info("🧹 Learning Adapter 清理完成")

# 測試函數
async def main():
    """測試學習適配器"""
    print("🧪 測試 Learning Adapter...")
    
    # 模擬依賴
    class MockMemoryEngine:
        class MemoryType:
            CLAUDE_INTERACTION = "claude_interaction"
            PROCEDURAL = "procedural"
        
        class Memory:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        
        async def get_similar_memories(self, content, memory_type, limit):
            return []
        
        async def store_memory(self, memory):
            return True
        
        async def search_memories(self, query, memory_type, tags, limit):
            return []
    
    class MockContextManager:
        async def get_context(self, context_id):
            return None
    
    # 創建測試實例
    memory_engine = MockMemoryEngine()
    context_manager = MockContextManager()
    
    adapter = LearningAdapter(memory_engine, context_manager)
    await adapter.initialize()
    
    # 測試交互處理
    test_interaction = {
        "user_input": "如何使用 Python 進行數據分析？",
        "claude_response": "Python 數據分析可以使用 pandas、numpy 等庫...",
        "response_time": 2500,
        "user_satisfaction": 0.85,
        "context_id": "test_context"
    }
    
    await adapter.process_interaction(test_interaction)
    
    # 測試統計
    stats = await adapter.get_learning_statistics()
    print(f"📊 學習統計: {stats}")
    
    await adapter.cleanup()
    print("✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
        self.adaptation_rules = {
            LearningType.CLAUDE_INTERACTION: {
                "weight": 1.0,
                "adaptation_rate": 0.1,
                "success_threshold": 0.7,
                "features": ["user_satisfaction", "response_time", "context_relevance"]
            },
            LearningType.USER_BEHAVIOR: {
                "weight": 0.8,
                "adaptation_rate": 0.15,
                "success_threshold": 0.6,
                "features": ["interaction_frequency", "preference_consistency", "workflow_efficiency"]
            },
            LearningType.PERFORMANCE_OPTIMIZATION: {
                "weight": 0.9,
                "adaptation_rate": 0.05,
                "success_threshold": 0.8,
                "features": ["response_time", "accuracy", "resource_usage"]
            },
            LearningType.ERROR_CORRECTION: {
                "weight": 1.2,
                "adaptation_rate": 0.2,
                "success_threshold": 0.9,
                "features": ["error_rate", "correction_accuracy", "learning_speed"]
            },
            LearningType.CONTEXT_ENHANCEMENT: {
                "weight": 0.7,
                "adaptation_rate": 0.12,
                "success_threshold": 0.65,
                "features": ["context_relevance", "enhancement_quality", "user_acceptance"]
            }
        }
    
    async def _initialize_performance_tracker(self):
        """初始化性能追蹤器"""
        for learning_type in LearningType:
            self.performance_tracker[learning_type] = []
    
    async def process_interaction(self, interaction_data: Dict[str, Any], context: QueryContext):
        """處理交互數據 - 支持模式感知"""
        try:
            # 检测交互模式
            interaction_mode = self.detect_interaction_mode(context)
            
            # 提取學習特徵
            features = await self._extract_learning_features(interaction_data)
            
            # 評估交互質量
            quality_score = await self._evaluate_interaction_quality(interaction_data, features)
            
            # 更新學習模式
            await self._update_learning_patterns(interaction_data, features, quality_score, interaction_mode)
            
            # 存儲學習數據
            learning_data = LearningData(
                id=f"learning_{int(time.time())}_{hash(str(interaction_data)) % 10000}",
                source="claude_interaction",
                learning_type=LearningType.CLAUDE_INTERACTION,
                interaction_mode=interaction_mode,
                data={
                    "interaction": interaction_data,
                    "features": features,
                    "quality_score": quality_score,
                    "context": context.to_dict() if hasattr(context, 'to_dict') else {}
                },
                performance_metrics={
                    "response_time": interaction_data.get("response_time", 0),
                    "user_satisfaction": interaction_data.get("user_satisfaction", 0),
                    "context_relevance": features.get("context_relevance", 0)
                },
                timestamp=time.time(),
                success=quality_score > 0.5
            )
            
            await self._store_learning_data(learning_data)
            
            logger.debug(f"✅ 處理交互學習: {learning_data.id} (質量: {quality_score:.3f}, 模式: {interaction_mode.value})")
            
        except Exception as e:
            logger.error(f"❌ 處理交互學習失敗: {e}")
    
    async def _extract_learning_features(self, interaction_data: Dict[str, Any]) -> Dict[str, float]:
        """提取學習特徵"""
        features = {}
        
        # 基本特徵
        features["response_time"] = min(1.0, 5000.0 / max(1.0, interaction_data.get("response_time", 5000)))
        features["user_satisfaction"] = interaction_data.get("user_satisfaction", 0.5)
        features["input_length"] = min(1.0, len(interaction_data.get("user_input", "")) / 1000.0)
        features["output_length"] = min(1.0, len(interaction_data.get("claude_response", "")) / 2000.0)
        
        # 上下文特徵
        context_id = interaction_data.get("context_id")
        if context_id and hasattr(self.context_manager, 'get_context'):
            try:
                context = await self.context_manager.get_context(context_id)
                if context:
                    features["context_relevance"] = getattr(context, 'relevance_score', 0.5)
                    features["context_age"] = min(1.0, (time.time() - getattr(context, 'created_at', time.time())) / 3600.0)
            except:
                features["context_relevance"] = 0.5
                features["context_age"] = 0.5
        else:
            features["context_relevance"] = 0.5
            features["context_age"] = 0.5
        
        # 歷史特徵
        user_input = interaction_data.get("user_input", "")
        if user_input and hasattr(self.memory_engine, 'search_memories'):
            try:
                similar_interactions = await self.memory_engine.search_memories(
                    query=user_input[:100],
                    limit=3
                )
                
                if similar_interactions:
                    features["similarity_score"] = np.mean([getattr(mem, 'importance_score', 0.5) for mem in similar_interactions])
                    features["repetition_factor"] = len(similar_interactions) / 10.0
                else:
                    features["similarity_score"] = 0.0
                    features["repetition_factor"] = 0.0
            except:
                features["similarity_score"] = 0.0
                features["repetition_factor"] = 0.0
        else:
            features["similarity_score"] = 0.0
            features["repetition_factor"] = 0.0
        
        return features
    
    async def _evaluate_interaction_quality(self, 
                                          interaction_data: Dict[str, Any], 
                                          features: Dict[str, float]) -> float:
        """評估交互質量"""
        quality_components = []
        
        # 用戶滿意度 (40%)
        user_satisfaction = interaction_data.get("user_satisfaction", 0.5)
        quality_components.append(user_satisfaction * 0.4)
        
        # 響應效率 (25%)
        response_efficiency = features.get("response_time", 0.5)
        quality_components.append(response_efficiency * 0.25)
        
        # 內容相關性 (20%)
        content_relevance = features.get("context_relevance", 0.5)
        quality_components.append(content_relevance * 0.2)
        
        # 輸出質量 (15%)
        output_quality = min(1.0, features.get("output_length", 0.5) * 2.0)
        quality_components.append(output_quality * 0.15)
        
        return sum(quality_components)
    
    async def _update_learning_patterns(self, interaction_data: Dict[str, Any], 
                                      features: Dict[str, float], 
                                      quality_score: float,
                                      interaction_mode: InteractionMode):
        """更新學習模式 - 支持模式感知"""
        try:
            # 按模式分别更新学习模式
            mode_key = interaction_mode.value
            
            if mode_key not in self.learning_patterns:
                self.learning_patterns[mode_key] = {
                    "feature_weights": defaultdict(float),
                    "quality_history": deque(maxlen=100),
                    "adaptation_count": 0,
                    "success_rate": 0.0
                }
            
            pattern = self.learning_patterns[mode_key]
            
            # 更新特徵權重
            for feature, value in features.items():
                current_weight = pattern["feature_weights"][feature]
                adaptation_rate = self.adaptation_rules[LearningType.CLAUDE_INTERACTION]["adaptation_rate"]
                
                # 根據質量分數調整權重
                if quality_score > 0.7:
                    pattern["feature_weights"][feature] = current_weight + adaptation_rate * value
                elif quality_score < 0.3:
                    pattern["feature_weights"][feature] = current_weight - adaptation_rate * value * 0.5
            
            # 更新質量歷史
            pattern["quality_history"].append(quality_score)
            pattern["adaptation_count"] += 1
            
            # 計算成功率
            if len(pattern["quality_history"]) > 0:
                pattern["success_rate"] = sum(1 for q in pattern["quality_history"] if q > 0.5) / len(pattern["quality_history"])
            
            logger.debug(f"✅ 更新學習模式: {mode_key} (成功率: {pattern['success_rate']:.3f})")
            
        except Exception as e:
            logger.error(f"❌ 更新學習模式失敗: {e}")
    
    async def _store_learning_data(self, learning_data: LearningData):
        """存儲學習數據"""
        try:
            # 添加到歷史記錄
            self.learning_history.append(learning_data)
            
            # 更新性能追蹤器
            self.performance_tracker[learning_data.learning_type].append({
                "timestamp": learning_data.timestamp,
                "quality_score": learning_data.performance_metrics.get("user_satisfaction", 0),
                "success": learning_data.success,
                "interaction_mode": learning_data.interaction_mode.value
            })
            
            # 存儲到記憶引擎
            if hasattr(self.memory_engine, 'store_memory'):
                from .memory_engine import Memory, MemoryType
                
                memory = Memory(
                    id=learning_data.id,
                    memory_type=MemoryType.SYSTEM_STATE,
                    content=f"學習數據: {learning_data.learning_type.value}",
                    metadata=learning_data.to_dict(),
                    created_at=learning_data.timestamp,
                    accessed_at=learning_data.timestamp,
                    access_count=0,
                    importance_score=0.6,
                    tags=["learning", "adaptation", learning_data.interaction_mode.value]
                )
                
                await self.memory_engine.store_memory(memory)
            
        except Exception as e:
            logger.error(f"❌ 存儲學習數據失敗: {e}")
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """獲取學習統計信息"""
        stats = {
            "total_interactions": len(self.learning_history),
            "learning_patterns": {},
            "performance_trends": {},
            "mode_statistics": defaultdict(int),
            "success_rates": {}
        }
        
        # 統計模式分布
        for learning_data in self.learning_history:
            stats["mode_statistics"][learning_data.interaction_mode.value] += 1
        
        # 統計學習模式
        for mode, pattern in self.learning_patterns.items():
            stats["learning_patterns"][mode] = {
                "adaptation_count": pattern["adaptation_count"],
                "success_rate": pattern["success_rate"],
                "top_features": dict(sorted(
                    pattern["feature_weights"].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5])
            }
        
        # 統計性能趨勢
        for learning_type, records in self.performance_tracker.items():
            if records:
                recent_records = records[-20:]  # 最近20條記錄
                stats["performance_trends"][learning_type.value] = {
                    "avg_quality": np.mean([r["quality_score"] for r in recent_records]),
                    "success_rate": sum(1 for r in recent_records if r["success"]) / len(recent_records),
                    "total_records": len(records)
                }
        
        # 個性化統計
        personalization_stats = await self.get_personalization_statistics()
        stats.update(personalization_stats)
        
        return stats

# 全局实例管理
learning_adapter = None

def get_learning_adapter(memory_engine=None, context_manager=None):
    """获取学习适配器实例"""
    global learning_adapter
    if learning_adapter is None and memory_engine and context_manager:
        learning_adapter = LearningAdapter(memory_engine, context_manager)
    return learning_adapter

async def main():
    """测试学习适配器"""
    print("🧪 测试 LearningAdapter...")
    
    # 模拟依赖
    class MockMemoryEngine:
        async def search_memories(self, query, limit=3):
            return []
        
        async def store_memory(self, memory):
            pass
    
    class MockContextManager:
        async def get_context(self, context_id):
            return None
    
    # 创建适配器
    adapter = LearningAdapter(MockMemoryEngine(), MockContextManager())
    await adapter.initialize()
    
    # 测试模式检测
    context = QueryContext(
        current_tool="claude_code_tool",
        current_model="claude",
        user_id="test_user"
    )
    
    mode = adapter.detect_interaction_mode(context)
    print(f"✅ 模式检测: {mode.value}")
    
    # 测试个性化处理
    response = "这是一个Python函数示例"
    personalized = await adapter.personalize_response(response, context)
    print(f"✅ 个性化处理完成")
    
    # 测试统计信息
    stats = await adapter.get_learning_statistics()
    print(f"✅ 统计信息: {len(stats)} 个指标")
    
    print("✅ LearningAdapter 测试完成")

if __name__ == "__main__":
    asyncio.run(main())

