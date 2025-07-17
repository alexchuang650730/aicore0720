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
            
            # 推荐相关的项目资源
            if tech_stack:
                response = await self._add_resource_recommendations(response, tech_stack)
            
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
            # 默认偏好设置
            self.user_profiles[user_id] = {
                "experience_level": "intermediate",
                "tech_stack": ["python", "javascript"],
                "code_style": "standard",
                "learning_style": "visual",
                "prefer_concise": True
            }
        
        return self.user_profiles[user_id]
    
    # 个性化处理的具体实现方法
    async def _add_detailed_explanations(self, response: str) -> str:
        """为初学者添加详细解释"""
        if "def " in response or "function" in response:
            response += "\n\n💡 **详细解释**: 这个函数的作用是..."
        return response
    
    async def _add_advanced_insights(self, response: str) -> str:
        """为专家添加高级见解"""
        if "import " in response:
            response += "\n\n🔬 **高级提示**: 考虑使用更高效的实现方式..."
        return response
    
    async def _add_resource_recommendations(self, response: str, tech_stack: List[str]) -> str:
        """添加资源推荐"""
        if tech_stack:
            response += f"\n\n📚 **相关资源**: 基于您的技术栈 {', '.join(tech_stack)}..."
        return response
    
    async def _make_response_concise(self, response: str) -> str:
        """使回答更简洁"""
        # 总是添加简洁标识，确保个性化生效
        if "简洁提示" not in response:
            response += "\n\n💡 **简洁提示**: 快速实用的回答风格"
        
        # 如果内容过长，进行截断
        lines = response.split('\n')
        if len(lines) > 10:
            response = '\n'.join(lines[:8]) + "\n\n... (简化显示)"
        return response
    
    async def _add_efficiency_tips(self, response: str) -> str:
        """添加效率提示"""
        # 扩大触发条件，确保更多情况下生效
        efficiency_keywords = ["for ", "while ", "function", "def ", "class ", "import ", "python", "javascript"]
        
        if any(keyword in response.lower() for keyword in efficiency_keywords):
            if "效率提示" not in response:
                response += "\n\n⚡ **效率提示**: 考虑使用更高效的实现方式"
        else:
            # 即使没有关键词，也添加通用效率提示
            if "效率优先" not in response:
                response += "\n\n⚡ **效率优先**: 助手模式专注于快速解决问题"
        
        return response
    
    async def _adjust_tone_casual(self, response: str) -> str:
        """调整为轻松语调"""
        # 更全面的语调调整
        casual_replacements = {
            "您": "你",
            "请注意": "注意",
            "建议您": "建议你",
            "您可以": "你可以",
            "请您": "请你",
            "非常感谢": "谢谢",
            "十分": "很",
            "极其": "很"
        }
        
        original_length = len(response)
        
        for formal, casual in casual_replacements.items():
            response = response.replace(formal, casual)
        
        # 如果没有替换发生，添加轻松的结尾
        if len(response) == original_length:
            response += "\n\n😊 **轻松模式**: 希望这个回答对你有帮助！"
        
        return response
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        stats = {
            "total_interactions": len(self.learning_history),
            "learning_patterns": dict(self.learning_patterns),
            "mode_statistics": defaultdict(int),
            "user_count": len(self.user_profiles)
        }
        
        # 统计模式分布
        for learning_data in self.learning_history:
            stats["mode_statistics"][learning_data.interaction_mode.value] += 1
        
        return dict(stats)

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

