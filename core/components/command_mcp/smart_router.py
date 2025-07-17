#!/usr/bin/env python3
"""
智能路由器 - 实现真正的 Claude Code 去除
通过 Claude Code Router 将所有请求智能路由到 K2 模型
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass

# 导入追踪器
from ..mirror_code_tracker.usage_tracker import (
    track_k2_usage, track_claude_mirror_usage, track_claude_direct_usage,
    ModelProvider, TokenUsage
)

logger = logging.getLogger(__name__)

class RoutingStrategy(Enum):
    """路由策略"""
    K2_FIRST = "k2_first"           # K2 优先策略
    K2_ONLY = "k2_only"             # 仅使用 K2
    INTELLIGENT = "intelligent"     # 智能路由
    FALLBACK = "fallback"           # 回退策略

@dataclass
class RoutingDecision:
    """路由决策结果"""
    target_model: ModelProvider
    confidence: float
    reason: str
    estimated_tokens: int
    estimated_cost: float
    fallback_available: bool = False

class SmartRouter:
    """智能路由器 - 实现 Claude Code 去除的核心组件"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.routing_strategy = RoutingStrategy(
            self.config.get("routing_strategy", "k2_first")
        )
        
        # K2 模型能力映射
        self.k2_capabilities = {
            # 基础指令 - K2 完全支持
            "basic_commands": [
                "/help", "/status", "/config", "/version", "/clear", 
                "/history", "/models", "/model", "/tools", "/api",
                "/debug", "/export", "/import", "/memory", "/usage",
                "/cost", "/doctor", "/compact", "/theme", "/lang",
                "/reset", "/exit", "/quit"
            ],
            
            # 代码相关 - K2 强项
            "code_commands": [
                "/review", "/analyze", "/refactor", "/optimize",
                "/test", "/debug", "/format", "/lint", "/docs"
            ],
            
            # 文件操作 - K2 支持
            "file_commands": [
                "/read", "/write", "/edit", "/create", "/delete",
                "/list", "/find", "/grep", "/diff", "/merge"
            ],
            
            # 项目管理 - K2 支持
            "project_commands": [
                "/init", "/build", "/run", "/deploy", "/package",
                "/install", "/update", "/clean", "/backup"
            ],
            
            # Git 操作 - K2 支持
            "git_commands": [
                "/commit", "/push", "/pull", "/branch", "/merge",
                "/rebase", "/tag", "/log", "/diff", "/status"
            ],
            
            # 高级功能 - 需要评估
            "advanced_commands": [
                "/ai", "/generate", "/translate", "/summarize",
                "/explain", "/suggest", "/improve", "/convert"
            ]
        }
        
        # Claude Code 依赖的指令（需要逐步迁移到 K2）
        self.claude_dependent_commands = [
            "/add-dir", "/remove-dir", "/list-dirs", "/chat",
            "/ask", "/context", "/session", "/workspace"
        ]
        
        # 路由统计
        self.routing_stats = {
            "total_requests": 0,
            "k2_routed": 0,
            "claude_routed": 0,
            "routing_errors": 0,
            "k2_success_rate": 0.0,
            "average_decision_time": 0.0
        }
        
        logger.info(f"🧠 智能路由器初始化完成 - 策略: {self.routing_strategy.value}")
    
    async def route_command(self, command: str, context: Dict[str, Any] = None) -> RoutingDecision:
        """
        智能路由指令到最适合的模型
        
        Args:
            command: 用户输入的指令
            context: 上下文信息（可选）
            
        Returns:
            RoutingDecision: 路由决策结果
        """
        start_time = time.time()
        self.routing_stats["total_requests"] += 1
        
        try:
            # 解析指令
            cmd_parts = command.strip().split()
            if not cmd_parts or not cmd_parts[0].startswith('/'):
                # 非斜杠指令，默认路由到 K2
                return self._create_k2_decision(
                    command, "非斜杠指令，K2 处理自然语言对话", 0.9
                )
            
            cmd_name = cmd_parts[0]
            
            # 根据路由策略进行决策
            if self.routing_strategy == RoutingStrategy.K2_ONLY:
                return await self._k2_only_routing(command, cmd_name)
            elif self.routing_strategy == RoutingStrategy.K2_FIRST:
                return await self._k2_first_routing(command, cmd_name)
            elif self.routing_strategy == RoutingStrategy.INTELLIGENT:
                return await self._intelligent_routing(command, cmd_name, context)
            else:  # FALLBACK
                return await self._fallback_routing(command, cmd_name)
                
        except Exception as e:
            logger.error(f"路由决策失败: {e}")
            self.routing_stats["routing_errors"] += 1
            return self._create_fallback_decision(command, f"路由错误: {str(e)}")
        
        finally:
            # 更新决策时间统计
            decision_time = (time.time() - start_time) * 1000
            total_time = (self.routing_stats["average_decision_time"] * 
                         (self.routing_stats["total_requests"] - 1) + decision_time)
            self.routing_stats["average_decision_time"] = total_time / self.routing_stats["total_requests"]
    
    async def _k2_only_routing(self, command: str, cmd_name: str) -> RoutingDecision:
        """K2 专用路由策略 - 强制所有请求都使用 K2"""
        logger.info(f"🎯 K2专用路由: {cmd_name}")
        
        if cmd_name in self.claude_dependent_commands:
            # 即使是 Claude 依赖的指令，也尝试用 K2 处理
            return self._create_k2_decision(
                command, 
                f"K2专用模式 - 尝试用K2处理原Claude指令: {cmd_name}",
                0.7,
                fallback_available=False  # K2专用模式不允许回退
            )
        
        return self._create_k2_decision(
            command, f"K2专用模式 - 所有指令由K2处理", 0.95
        )
    
    async def _k2_first_routing(self, command: str, cmd_name: str) -> RoutingDecision:
        """K2 优先路由策略 - 优先使用 K2，必要时回退到 Claude"""
        logger.info(f"🥇 K2优先路由: {cmd_name}")
        
        # 检查 K2 能力
        k2_capability_score = self._assess_k2_capability(cmd_name)
        
        if k2_capability_score >= 0.8:
            # K2 高度支持
            return self._create_k2_decision(
                command, f"K2高度支持指令: {cmd_name}", k2_capability_score
            )
        elif k2_capability_score >= 0.5:
            # K2 中等支持，但优先尝试
            return self._create_k2_decision(
                command, 
                f"K2中等支持，优先尝试: {cmd_name}",
                k2_capability_score,
                fallback_available=True
            )
        else:
            # K2 支持度低，但仍然优先尝试（K2 First 策略）
            return self._create_k2_decision(
                command,
                f"K2优先策略 - 即使支持度低也优先尝试: {cmd_name}",
                max(k2_capability_score, 0.3),
                fallback_available=True
            )
    
    async def _intelligent_routing(self, command: str, cmd_name: str, context: Dict[str, Any] = None) -> RoutingDecision:
        """智能路由策略 - 基于多因素分析选择最佳模型"""
        logger.info(f"🧠 智能路由分析: {cmd_name}")
        
        # 多因素评估
        k2_score = self._assess_k2_capability(cmd_name)
        complexity_score = self._assess_command_complexity(command)
        context_score = self._assess_context_requirements(context)
        cost_score = self._assess_cost_efficiency(command)
        
        # 综合评分
        k2_total_score = (
            k2_score * 0.4 +           # K2能力权重40%
            (1 - complexity_score) * 0.3 +  # 复杂度权重30%（越简单K2越适合）
            context_score * 0.2 +      # 上下文权重20%
            cost_score * 0.1           # 成本权重10%
        )
        
        logger.info(f"📊 智能评分 - K2能力:{k2_score:.2f}, 复杂度:{complexity_score:.2f}, "
                   f"上下文:{context_score:.2f}, 成本:{cost_score:.2f}, 总分:{k2_total_score:.2f}")
        
        if k2_total_score >= 0.7:
            return self._create_k2_decision(
                command, f"智能路由推荐K2 (评分:{k2_total_score:.2f})", k2_total_score
            )
        elif k2_total_score >= 0.4:
            return self._create_k2_decision(
                command, 
                f"智能路由倾向K2 (评分:{k2_total_score:.2f})",
                k2_total_score,
                fallback_available=True
            )
        else:
            # 评分过低，但仍然尝试 K2（避免 Claude 依赖）
            return self._create_k2_decision(
                command,
                f"智能路由 - 尝试K2以减少Claude依赖 (评分:{k2_total_score:.2f})",
                max(k2_total_score, 0.2),
                fallback_available=True
            )
    
    async def _fallback_routing(self, command: str, cmd_name: str) -> RoutingDecision:
        """回退路由策略 - 保守策略，确保成功执行"""
        logger.info(f"🛡️ 回退路由: {cmd_name}")
        
        k2_capability = self._assess_k2_capability(cmd_name)
        
        if k2_capability >= 0.9:
            # 高置信度使用 K2
            return self._create_k2_decision(
                command, f"回退策略 - K2高置信度: {cmd_name}", k2_capability
            )
        else:
            # 中低置信度，提供回退选项
            return self._create_k2_decision(
                command,
                f"回退策略 - K2尝试，保留回退: {cmd_name}",
                k2_capability,
                fallback_available=True
            )
    
    def _assess_k2_capability(self, cmd_name: str) -> float:
        """评估 K2 对特定指令的支持能力"""
        
        # 检查各个能力类别
        for category, commands in self.k2_capabilities.items():
            if cmd_name in commands:
                if category == "basic_commands":
                    return 0.95  # 基础指令，K2 完全支持
                elif category == "code_commands":
                    return 0.90  # 代码相关，K2 强项
                elif category in ["file_commands", "project_commands", "git_commands"]:
                    return 0.85  # 文件和项目操作，K2 良好支持
                elif category == "advanced_commands":
                    return 0.70  # 高级功能，K2 中等支持
        
        # 检查 Claude 依赖指令
        if cmd_name in self.claude_dependent_commands:
            return 0.30  # Claude 依赖指令，K2 支持度低但可尝试
        
        # 未知指令，给予中等评分
        return 0.50
    
    def _assess_command_complexity(self, command: str) -> float:
        """评估指令复杂度"""
        parts = command.split()
        
        # 基于参数数量
        param_complexity = min(len(parts) / 10, 1.0)
        
        # 基于指令长度
        length_complexity = min(len(command) / 200, 1.0)
        
        # 检查复杂关键词
        complex_keywords = ["analyze", "generate", "translate", "summarize", "explain"]
        keyword_complexity = 0.0
        for keyword in complex_keywords:
            if keyword in command.lower():
                keyword_complexity += 0.2
        
        return min(param_complexity + length_complexity + keyword_complexity, 1.0)
    
    def _assess_context_requirements(self, context: Dict[str, Any] = None) -> float:
        """评估上下文需求"""
        if not context:
            return 0.8  # 无上下文，K2 适合
        
        # 检查上下文复杂度
        context_size = len(str(context))
        if context_size > 1000:
            return 0.4  # 大量上下文，可能需要 Claude
        elif context_size > 500:
            return 0.6  # 中等上下文
        else:
            return 0.9  # 少量上下文，K2 适合
    
    def _assess_cost_efficiency(self, command: str) -> float:
        """评估成本效率（K2 云端部署成本更低）"""
        # K2 云端部署，成本效率始终更高
        return 0.95
    
    def _create_k2_decision(self, command: str, reason: str, confidence: float, 
                           fallback_available: bool = False) -> RoutingDecision:
        """创建 K2 路由决策"""
        estimated_tokens = len(command.split()) * 3  # 估算 token 数量
        estimated_cost = estimated_tokens * 0.0001   # K2 云端成本很低
        
        self.routing_stats["k2_routed"] += 1
        
        return RoutingDecision(
            target_model=ModelProvider.K2_LOCAL,
            confidence=confidence,
            reason=reason,
            estimated_tokens=estimated_tokens,
            estimated_cost=estimated_cost,
            fallback_available=fallback_available
        )
    
    def _create_claude_decision(self, command: str, reason: str, confidence: float) -> RoutingDecision:
        """创建 Claude 路由决策（应该避免使用）"""
        estimated_tokens = len(command.split()) * 4  # Claude 通常需要更多 token
        estimated_cost = estimated_tokens * 0.003    # Claude 成本较高
        
        self.routing_stats["claude_routed"] += 1
        
        logger.warning(f"⚠️ 路由到Claude: {reason}")
        
        return RoutingDecision(
            target_model=ModelProvider.CLAUDE_MIRROR,
            confidence=confidence,
            reason=f"⚠️ {reason}",
            estimated_tokens=estimated_tokens,
            estimated_cost=estimated_cost,
            fallback_available=False
        )
    
    def _create_fallback_decision(self, command: str, reason: str) -> RoutingDecision:
        """创建回退决策"""
        return self._create_k2_decision(
            command, f"回退到K2: {reason}", 0.5, fallback_available=False
        )
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        total = self.routing_stats["total_requests"]
        if total > 0:
            self.routing_stats["k2_success_rate"] = (
                self.routing_stats["k2_routed"] / total * 100
            )
        
        return {
            **self.routing_stats,
            "claude_avoidance_rate": f"{self.routing_stats['k2_success_rate']:.1f}%",
            "routing_strategy": self.routing_strategy.value,
            "k2_capabilities_count": sum(len(cmds) for cmds in self.k2_capabilities.values()),
            "claude_dependent_count": len(self.claude_dependent_commands)
        }
    
    def update_k2_capabilities(self, new_capabilities: Dict[str, List[str]]):
        """更新 K2 能力映射（用于动态学习）"""
        for category, commands in new_capabilities.items():
            if category in self.k2_capabilities:
                self.k2_capabilities[category].extend(commands)
            else:
                self.k2_capabilities[category] = commands
        
        logger.info(f"🔄 更新K2能力映射: {len(new_capabilities)} 个类别")
    
    def set_routing_strategy(self, strategy: RoutingStrategy):
        """设置路由策略"""
        self.routing_strategy = strategy
        logger.info(f"🔄 路由策略更新为: {strategy.value}")

# 全局智能路由器实例
smart_router = SmartRouter()

# 便捷函数
async def route_command_intelligently(command: str, context: Dict[str, Any] = None) -> RoutingDecision:
    """智能路由指令"""
    return await smart_router.route_command(command, context)

def get_router_stats() -> Dict[str, Any]:
    """获取路由器统计"""
    return smart_router.get_routing_stats()

def configure_router(strategy: str = "k2_first", config: Dict[str, Any] = None):
    """配置路由器"""
    if strategy in [s.value for s in RoutingStrategy]:
        smart_router.set_routing_strategy(RoutingStrategy(strategy))
    
    if config:
        smart_router.config.update(config)

if __name__ == "__main__":
    # 测试智能路由器
    async def test_router():
        print("🧠 测试智能路由器")
        
        test_commands = [
            "/help",
            "/review code.py", 
            "/add-dir /path/to/project",
            "/analyze complex_algorithm.py",
            "/chat 请解释量子计算原理"
        ]
        
        for cmd in test_commands:
            decision = await route_command_intelligently(cmd)
            print(f"\n指令: {cmd}")
            print(f"路由到: {decision.target_model.value}")
            print(f"置信度: {decision.confidence:.2f}")
            print(f"原因: {decision.reason}")
            print(f"预估成本: ${decision.estimated_cost:.4f}")
        
        print(f"\n📊 路由统计:")
        stats = get_router_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    asyncio.run(test_router())

