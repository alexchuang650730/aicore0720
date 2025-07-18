"""
增強版 Claude Router MCP
專為 K2 模式下的 Claude Code 命令增強而設計
提供智能路由、命令增強、上下文保持等功能
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """模型提供者"""
    CLAUDE = "claude"
    K2_GROQ = "k2_groq"
    K2_MOONSHOT = "k2_moonshot"
    K2_QWEN = "k2_qwen"

class CommandComplexity(Enum):
    """命令複雜度"""
    SIMPLE = "simple"        # 簡單查詢、基本操作
    MODERATE = "moderate"    # 中等邏輯、需要推理
    COMPLEX = "complex"      # 複雜任務、需要深度思考
    CRITICAL = "critical"    # 關鍵任務、需要最高準確性

class EnhancementType(Enum):
    """增強類型"""
    CONTEXT_ENRICHMENT = "context_enrichment"      # 上下文豐富化
    PROMPT_OPTIMIZATION = "prompt_optimization"    # 提示詞優化
    CHAIN_OF_THOUGHT = "chain_of_thought"         # 思維鏈
    MULTI_STEP_REASONING = "multi_step_reasoning" # 多步推理
    ERROR_CORRECTION = "error_correction"         # 錯誤糾正
    VERIFICATION = "verification"                 # 結果驗證

@dataclass
class CommandContext:
    """命令上下文"""
    command_id: str
    original_command: str
    enhanced_command: str
    complexity: CommandComplexity
    required_enhancements: List[EnhancementType]
    execution_history: List[Dict[str, Any]]
    context_data: Dict[str, Any]
    target_provider: ModelProvider
    fallback_providers: List[ModelProvider]

@dataclass
class EnhancementResult:
    """增強結果"""
    original_input: str
    enhanced_input: str
    enhancement_methods: List[str]
    confidence_score: float
    expected_quality_improvement: float
    processing_time: float

class EnhancedClaudeRouterMCP:
    """增強版 Claude Router MCP"""
    
    def __init__(self):
        self.command_analyzer = CommandAnalyzer()
        self.enhancement_engine = CommandEnhancementEngine()
        self.routing_optimizer = RoutingOptimizer()
        self.quality_evaluator = QualityEvaluator()
        self.context_manager = ContextManager()
        
        # 模型能力配置
        self.model_capabilities = {
            ModelProvider.CLAUDE: {
                "strength": ["complex_reasoning", "code_generation", "analysis"],
                "weakness": ["cost", "latency"],
                "quality_score": 0.95,
                "cost_per_token": 0.015
            },
            ModelProvider.K2_GROQ: {
                "strength": ["speed", "cost_efficiency", "simple_tasks"],
                "weakness": ["complex_reasoning", "context_handling"],
                "quality_score": 0.75,
                "cost_per_token": 0.0008
            },
            ModelProvider.K2_MOONSHOT: {
                "strength": ["chinese_tasks", "cost_efficiency", "moderate_complexity"],
                "weakness": ["complex_reasoning", "latest_knowledge"],
                "quality_score": 0.78,
                "cost_per_token": 0.001
            },
            ModelProvider.K2_QWEN: {
                "strength": ["chinese_language", "code_tasks", "cost_efficiency"],
                "weakness": ["complex_analysis", "creative_tasks"],
                "quality_score": 0.72,
                "cost_per_token": 0.0005
            }
        }
        
        logger.info("🚀 Enhanced Claude Router MCP 初始化完成")
    
    async def route_claude_code_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """路由 Claude Code 命令"""
        
        start_time = time.time()
        
        # 1. 分析命令複雜度和需求
        command_analysis = await self.command_analyzer.analyze_command(command, context)
        
        # 2. 選擇最佳模型提供者
        optimal_provider = await self.routing_optimizer.select_optimal_provider(
            command_analysis, self.model_capabilities
        )
        
        # 3. 根據選擇的提供者決定是否需要增強
        if optimal_provider != ModelProvider.CLAUDE:
            # K2 模式需要增強
            enhancement_result = await self.enhancement_engine.enhance_command_for_k2(
                command, command_analysis, optimal_provider
            )
            enhanced_command = enhancement_result.enhanced_input
        else:
            # Claude 模式，可能仍需要輕度優化
            enhancement_result = await self.enhancement_engine.optimize_for_claude(
                command, command_analysis
            )
            enhanced_command = enhancement_result.enhanced_input
        
        # 4. 執行命令
        execution_result = await self._execute_enhanced_command(
            enhanced_command, optimal_provider, command_analysis
        )
        
        # 5. 質量評估和可能的回退
        quality_assessment = await self.quality_evaluator.assess_result_quality(
            execution_result, command_analysis
        )
        
        # 6. 如果質量不達標且有回退選項，嘗試回退
        if quality_assessment["quality_score"] < 0.8 and optimal_provider != ModelProvider.CLAUDE:
            logger.warning(f"K2 結果質量不達標 ({quality_assessment['quality_score']:.2f})，嘗試 Claude 回退")
            
            fallback_enhancement = await self.enhancement_engine.prepare_fallback_command(
                command, execution_result, command_analysis
            )
            
            fallback_result = await self._execute_enhanced_command(
                fallback_enhancement.enhanced_input, ModelProvider.CLAUDE, command_analysis
            )
            
            # 更新執行結果
            execution_result = fallback_result
            execution_result["fallback_used"] = True
            execution_result["original_provider"] = optimal_provider.value
            execution_result["fallback_provider"] = ModelProvider.CLAUDE.value
        
        # 7. 更新上下文
        await self.context_manager.update_context(command, execution_result, context)
        
        processing_time = time.time() - start_time
        
        return {
            "command_id": f"cmd_{int(time.time())}",
            "original_command": command,
            "enhanced_command": enhanced_command,
            "selected_provider": optimal_provider.value,
            "enhancement_applied": optimal_provider != ModelProvider.CLAUDE,
            "enhancement_details": asdict(enhancement_result),
            "execution_result": execution_result,
            "quality_assessment": quality_assessment,
            "processing_time": processing_time,
            "cost_optimization": {
                "estimated_claude_cost": self._calculate_cost(command, ModelProvider.CLAUDE),
                "actual_cost": self._calculate_cost(enhanced_command, optimal_provider),
                "savings_percentage": self._calculate_savings_percentage(command, optimal_provider)
            }
        }
    
    async def _execute_enhanced_command(self, command: str, provider: ModelProvider, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """執行增強命令"""
        
        # 模擬不同提供者的執行
        if provider == ModelProvider.CLAUDE:
            return await self._execute_with_claude(command, analysis)
        elif provider == ModelProvider.K2_GROQ:
            return await self._execute_with_k2_groq(command, analysis)
        elif provider == ModelProvider.K2_MOONSHOT:
            return await self._execute_with_k2_moonshot(command, analysis)
        elif provider == ModelProvider.K2_QWEN:
            return await self._execute_with_k2_qwen(command, analysis)
        else:
            raise ValueError(f"不支持的提供者: {provider}")
    
    async def _execute_with_claude(self, command: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """使用 Claude 執行"""
        await asyncio.sleep(0.2)  # 模擬網絡延遲
        
        return {
            "provider": "claude",
            "response": f"Claude 執行結果: {command}",
            "quality_indicators": {
                "reasoning_depth": 0.95,
                "accuracy": 0.92,
                "completeness": 0.90,
                "creativity": 0.88
            },
            "execution_time": 2.5,
            "tokens_used": len(command.split()) * 1.5,
            "status": "success"
        }
    
    async def _execute_with_k2_groq(self, command: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """使用 K2 Groq 執行"""
        await asyncio.sleep(0.05)  # K2 更快
        
        # 根據增強程度調整質量
        enhancement_boost = 0.15 if "enhanced" in command else 0
        
        return {
            "provider": "k2_groq",
            "response": f"K2 Groq 執行結果: {command}",
            "quality_indicators": {
                "reasoning_depth": 0.70 + enhancement_boost,
                "accuracy": 0.75 + enhancement_boost,
                "completeness": 0.72 + enhancement_boost,
                "creativity": 0.65 + enhancement_boost
            },
            "execution_time": 0.8,
            "tokens_used": len(command.split()) * 1.2,
            "status": "success"
        }
    
    async def _execute_with_k2_moonshot(self, command: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """使用 K2 Moonshot 執行"""
        await asyncio.sleep(0.1)
        
        enhancement_boost = 0.12 if "enhanced" in command else 0
        
        return {
            "provider": "k2_moonshot", 
            "response": f"K2 Moonshot 執行結果: {command}",
            "quality_indicators": {
                "reasoning_depth": 0.73 + enhancement_boost,
                "accuracy": 0.78 + enhancement_boost,
                "completeness": 0.75 + enhancement_boost,
                "creativity": 0.70 + enhancement_boost
            },
            "execution_time": 1.2,
            "tokens_used": len(command.split()) * 1.3,
            "status": "success"
        }
    
    async def _execute_with_k2_qwen(self, command: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """使用 K2 Qwen 執行"""
        await asyncio.sleep(0.08)
        
        enhancement_boost = 0.18 if "enhanced" in command else 0
        
        return {
            "provider": "k2_qwen",
            "response": f"K2 Qwen 執行結果: {command}",
            "quality_indicators": {
                "reasoning_depth": 0.68 + enhancement_boost,
                "accuracy": 0.72 + enhancement_boost,
                "completeness": 0.70 + enhancement_boost,
                "creativity": 0.65 + enhancement_boost
            },
            "execution_time": 1.0,
            "tokens_used": len(command.split()) * 1.1,
            "status": "success"
        }
    
    def _calculate_cost(self, command: str, provider: ModelProvider) -> float:
        """計算執行成本"""
        token_count = len(command.split()) * 1.2
        cost_per_token = self.model_capabilities[provider]["cost_per_token"]
        return token_count * cost_per_token
    
    def _calculate_savings_percentage(self, command: str, provider: ModelProvider) -> float:
        """計算成本節省百分比"""
        claude_cost = self._calculate_cost(command, ModelProvider.CLAUDE)
        actual_cost = self._calculate_cost(command, provider)
        if claude_cost > 0:
            return ((claude_cost - actual_cost) / claude_cost) * 100
        return 0

class CommandAnalyzer:
    """命令分析器"""
    
    async def analyze_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析命令複雜度和需求"""
        
        # 分析命令複雜度
        complexity = self._assess_complexity(command)
        
        # 分析所需技能
        required_skills = self._identify_required_skills(command)
        
        # 分析語言需求
        language_requirements = self._analyze_language_requirements(command)
        
        # 分析性能需求
        performance_requirements = self._analyze_performance_requirements(command)
        
        return {
            "complexity": complexity,
            "required_skills": required_skills,
            "language_requirements": language_requirements,
            "performance_requirements": performance_requirements,
            "estimated_tokens": len(command.split()) * 1.5,
            "priority": context.get("priority", "medium") if context else "medium"
        }
    
    def _assess_complexity(self, command: str) -> CommandComplexity:
        """評估命令複雜度"""
        command_lower = command.lower()
        
        # 關鍵詞複雜度映射
        complex_indicators = [
            "analyze", "design", "architecture", "implement", "optimize",
            "debug", "refactor", "security", "performance", "algorithm"
        ]
        
        moderate_indicators = [
            "create", "modify", "update", "fix", "test", "review", "explain"
        ]
        
        simple_indicators = [
            "show", "list", "get", "find", "search", "display", "print"
        ]
        
        complex_count = sum(1 for indicator in complex_indicators if indicator in command_lower)
        moderate_count = sum(1 for indicator in moderate_indicators if indicator in command_lower)
        simple_count = sum(1 for indicator in simple_indicators if indicator in command_lower)
        
        if complex_count >= 2 or len(command.split()) > 50:
            return CommandComplexity.COMPLEX
        elif complex_count >= 1 or moderate_count >= 2:
            return CommandComplexity.MODERATE
        elif moderate_count >= 1:
            return CommandComplexity.MODERATE
        else:
            return CommandComplexity.SIMPLE
    
    def _identify_required_skills(self, command: str) -> List[str]:
        """識別所需技能"""
        skills = []
        command_lower = command.lower()
        
        skill_keywords = {
            "code_generation": ["create", "generate", "write", "implement"],
            "debugging": ["debug", "fix", "error", "issue"],
            "analysis": ["analyze", "review", "examine", "evaluate"],
            "optimization": ["optimize", "improve", "enhance", "performance"],
            "testing": ["test", "verify", "validate", "check"],
            "documentation": ["document", "explain", "describe", "comment"]
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in command_lower for keyword in keywords):
                skills.append(skill)
        
        return skills
    
    def _analyze_language_requirements(self, command: str) -> Dict[str, Any]:
        """分析語言需求"""
        # 檢測中文內容
        chinese_chars = sum(1 for char in command if '\u4e00' <= char <= '\u9fff')
        total_chars = len(command)
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
        
        return {
            "primary_language": "chinese" if chinese_ratio > 0.3 else "english",
            "chinese_ratio": chinese_ratio,
            "requires_chinese_expertise": chinese_ratio > 0.5
        }
    
    def _analyze_performance_requirements(self, command: str) -> Dict[str, Any]:
        """分析性能需求"""
        command_lower = command.lower()
        
        urgent_indicators = ["urgent", "quickly", "fast", "immediate"]
        is_urgent = any(indicator in command_lower for indicator in urgent_indicators)
        
        return {
            "urgency": "high" if is_urgent else "normal",
            "latency_sensitivity": "high" if is_urgent else "medium",
            "cost_sensitivity": "high" if not is_urgent else "medium"
        }

class CommandEnhancementEngine:
    """命令增強引擎"""
    
    async def enhance_command_for_k2(self, command: str, analysis: Dict[str, Any], provider: ModelProvider) -> EnhancementResult:
        """為 K2 模型增強命令"""
        
        start_time = time.time()
        
        # 根據複雜度選擇增強策略
        complexity = analysis.get("complexity", CommandComplexity.SIMPLE)
        
        enhancement_methods = []
        enhanced_command = command
        
        # 1. 上下文豐富化
        if complexity in [CommandComplexity.MODERATE, CommandComplexity.COMPLEX]:
            enhanced_command = await self._add_context_enrichment(enhanced_command, analysis)
            enhancement_methods.append("context_enrichment")
        
        # 2. 提示詞優化
        enhanced_command = await self._optimize_prompt_for_k2(enhanced_command, provider)
        enhancement_methods.append("prompt_optimization")
        
        # 3. 思維鏈增強
        if complexity == CommandComplexity.COMPLEX:
            enhanced_command = await self._add_chain_of_thought(enhanced_command)
            enhancement_methods.append("chain_of_thought")
        
        # 4. 多步推理
        if "analysis" in analysis.get("required_skills", []):
            enhanced_command = await self._add_multi_step_reasoning(enhanced_command)
            enhancement_methods.append("multi_step_reasoning")
        
        # 5. 錯誤預防
        enhanced_command = await self._add_error_prevention(enhanced_command, analysis)
        enhancement_methods.append("error_prevention")
        
        processing_time = time.time() - start_time
        
        # 計算預期質量提升
        base_quality = 0.75  # K2 基礎質量
        enhancement_boost = len(enhancement_methods) * 0.08  # 每個增強方法提升 8%
        expected_quality = min(base_quality + enhancement_boost, 0.95)
        
        return EnhancementResult(
            original_input=command,
            enhanced_input=enhanced_command,
            enhancement_methods=enhancement_methods,
            confidence_score=expected_quality,
            expected_quality_improvement=enhancement_boost,
            processing_time=processing_time
        )
    
    async def optimize_for_claude(self, command: str, analysis: Dict[str, Any]) -> EnhancementResult:
        """為 Claude 優化命令"""
        
        # Claude 已經很強，只需要輕度優化
        enhanced_command = await self._optimize_prompt_structure(command)
        
        return EnhancementResult(
            original_input=command,
            enhanced_input=enhanced_command,
            enhancement_methods=["prompt_structure_optimization"],
            confidence_score=0.95,
            expected_quality_improvement=0.05,
            processing_time=0.01
        )
    
    async def prepare_fallback_command(self, original_command: str, k2_result: Dict[str, Any], analysis: Dict[str, Any]) -> EnhancementResult:
        """準備回退命令"""
        
        # 分析 K2 結果的問題
        quality_issues = self._identify_quality_issues(k2_result)
        
        # 針對性增強
        enhanced_command = f"""
        原始任務: {original_command}
        
        K2模型已經嘗試處理，但存在以下問題: {', '.join(quality_issues)}
        
        請作為專家級AI，提供高質量的解決方案，特別注意:
        1. 深度分析和推理
        2. 完整性和準確性 
        3. 創新性思考
        4. 實用性考慮
        
        請詳細回答:
        """
        
        return EnhancementResult(
            original_input=original_command,
            enhanced_input=enhanced_command,
            enhancement_methods=["fallback_enhancement", "problem_targeted_prompt"],
            confidence_score=0.92,
            expected_quality_improvement=0.25,
            processing_time=0.02
        )
    
    async def _add_context_enrichment(self, command: str, analysis: Dict[str, Any]) -> str:
        """添加上下文豐富化"""
        context_prefix = """
        作為一個專業的AI助手，請仔細分析以下任務並提供詳細的解決方案。
        
        任務背景: 這是一個需要深度思考的專業任務
        期望輸出: 全面、準確、實用的解決方案
        
        具體任務: 
        """
        
        return context_prefix + command
    
    async def _optimize_prompt_for_k2(self, command: str, provider: ModelProvider) -> str:
        """針對 K2 模型優化提示詞"""
        
        if provider == ModelProvider.K2_GROQ:
            # Groq 偏好簡潔明確的指令
            prefix = "請逐步分析並提供解決方案: "
        elif provider == ModelProvider.K2_MOONSHOT:
            # Moonshot 對中文任務表現更好
            prefix = "請詳細分析以下任務，並給出專業建議: "
        elif provider == ModelProvider.K2_QWEN:
            # Qwen 對代碼任務表現較好
            prefix = "請作為專業開發者，分析並解決以下問題: "
        else:
            prefix = "請仔細分析並回答: "
        
        return prefix + command
    
    async def _add_chain_of_thought(self, command: str) -> str:
        """添加思維鏈"""
        cot_suffix = """
        
        請按照以下步驟思考:
        1. 理解問題的核心
        2. 分析可能的解決方案
        3. 評估每個方案的優缺點
        4. 選擇最佳方案並詳細說明
        5. 提供實施建議
        """
        
        return command + cot_suffix
    
    async def _add_multi_step_reasoning(self, command: str) -> str:
        """添加多步推理"""
        reasoning_framework = """
        
        請使用系統性推理方法:
        - 第一步: 問題分解
        - 第二步: 信息收集
        - 第三步: 方案設計
        - 第四步: 結果驗證
        
        每一步都要詳細說明推理過程。
        """
        
        return command + reasoning_framework
    
    async def _add_error_prevention(self, command: str, analysis: Dict[str, Any]) -> str:
        """添加錯誤預防"""
        error_prevention = """
        
        請特別注意:
        - 確保回答的準確性
        - 檢查邏輯一致性
        - 考慮邊界情況
        - 提供具體示例
        """
        
        return command + error_prevention
    
    async def _optimize_prompt_structure(self, command: str) -> str:
        """優化提示詞結構"""
        return f"請詳細分析並解答: {command}"
    
    def _identify_quality_issues(self, k2_result: Dict[str, Any]) -> List[str]:
        """識別質量問題"""
        issues = []
        quality_indicators = k2_result.get("quality_indicators", {})
        
        if quality_indicators.get("reasoning_depth", 0) < 0.8:
            issues.append("推理深度不足")
        if quality_indicators.get("accuracy", 0) < 0.8:
            issues.append("準確性有待提升")
        if quality_indicators.get("completeness", 0) < 0.8:
            issues.append("回答不夠完整")
        if quality_indicators.get("creativity", 0) < 0.7:
            issues.append("創新性不足")
        
        return issues if issues else ["整體質量需要提升"]

class RoutingOptimizer:
    """路由優化器"""
    
    async def select_optimal_provider(self, analysis: Dict[str, Any], capabilities: Dict[ModelProvider, Dict[str, Any]]) -> ModelProvider:
        """選擇最佳提供者"""
        
        complexity = analysis.get("complexity", CommandComplexity.SIMPLE)
        required_skills = analysis.get("required_skills", [])
        language_req = analysis.get("language_requirements", {})
        performance_req = analysis.get("performance_requirements", {})
        
        # 計算每個提供者的適配分數
        scores = {}
        
        for provider, capability in capabilities.items():
            score = 0
            
            # 基礎質量分數
            score += capability["quality_score"] * 40
            
            # 複雜度適配
            if complexity == CommandComplexity.SIMPLE:
                if provider != ModelProvider.CLAUDE:
                    score += 20  # K2 適合簡單任務
            elif complexity == CommandComplexity.COMPLEX:
                if provider == ModelProvider.CLAUDE:
                    score += 30  # Claude 適合複雜任務
                else:
                    score -= 10  # K2 不太適合複雜任務
            
            # 技能匹配
            provider_strengths = capability["strength"]
            skill_match = sum(1 for skill in required_skills if any(s in skill for s in provider_strengths))
            score += skill_match * 5
            
            # 語言需求
            if language_req.get("requires_chinese_expertise", False):
                if provider in [ModelProvider.K2_MOONSHOT, ModelProvider.K2_QWEN]:
                    score += 15
            
            # 性能需求
            if performance_req.get("urgency") == "high":
                if provider in [ModelProvider.K2_GROQ, ModelProvider.K2_QWEN]:
                    score += 10  # K2 更快
            
            # 成本考慮
            if performance_req.get("cost_sensitivity") == "high":
                if provider != ModelProvider.CLAUDE:
                    score += 25  # K2 更便宜
            
            scores[provider] = score
        
        # 選擇分數最高的提供者
        optimal_provider = max(scores, key=scores.get)
        
        logger.info(f"Provider selection scores: {scores}")
        logger.info(f"Selected optimal provider: {optimal_provider}")
        
        return optimal_provider

class QualityEvaluator:
    """質量評估器"""
    
    async def assess_result_quality(self, result: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """評估結果質量"""
        
        quality_indicators = result.get("quality_indicators", {})
        
        # 計算綜合質量分數
        weights = {
            "reasoning_depth": 0.3,
            "accuracy": 0.35,
            "completeness": 0.25,
            "creativity": 0.1
        }
        
        quality_score = sum(
            quality_indicators.get(metric, 0) * weight
            for metric, weight in weights.items()
        )
        
        # 根據任務複雜度調整期望
        complexity = analysis.get("complexity", CommandComplexity.SIMPLE)
        if complexity == CommandComplexity.COMPLEX:
            quality_threshold = 0.85
        elif complexity == CommandComplexity.MODERATE:
            quality_threshold = 0.75
        else:
            quality_threshold = 0.65
        
        meets_threshold = quality_score >= quality_threshold
        
        return {
            "quality_score": quality_score,
            "quality_threshold": quality_threshold,
            "meets_threshold": meets_threshold,
            "quality_breakdown": quality_indicators,
            "improvement_suggestions": self._generate_improvement_suggestions(quality_indicators, quality_threshold)
        }
    
    def _generate_improvement_suggestions(self, indicators: Dict[str, float], threshold: float) -> List[str]:
        """生成改進建議"""
        suggestions = []
        
        for metric, score in indicators.items():
            if score < threshold:
                if metric == "reasoning_depth":
                    suggestions.append("需要更深入的推理和分析")
                elif metric == "accuracy":
                    suggestions.append("需要提高回答的準確性")
                elif metric == "completeness":
                    suggestions.append("需要更完整的回答")
                elif metric == "creativity":
                    suggestions.append("需要更多創新性思考")
        
        return suggestions

class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.context_store = {}
    
    async def update_context(self, command: str, result: Dict[str, Any], context: Dict[str, Any] = None) -> None:
        """更新上下文"""
        
        session_id = context.get("session_id", "default") if context else "default"
        
        if session_id not in self.context_store:
            self.context_store[session_id] = {
                "command_history": [],
                "quality_history": [],
                "preferences": {}
            }
        
        self.context_store[session_id]["command_history"].append({
            "command": command,
            "result": result,
            "timestamp": time.time()
        })
        
        # 保持最近 10 條記錄
        if len(self.context_store[session_id]["command_history"]) > 10:
            self.context_store[session_id]["command_history"] = \
                self.context_store[session_id]["command_history"][-10:]

# 使用示例
async def main():
    """主函數示例"""
    router = EnhancedClaudeRouterMCP()
    
    # 測試不同類型的命令
    test_commands = [
        "list all files in current directory",  # 簡單命令
        "create a user management system with authentication",  # 中等複雜度
        "設計一個高性能的分佈式微服務架構，包含負載均衡、服務發現、容錯機制",  # 複雜命令
        "debug this performance issue and optimize the algorithm"  # 需要深度分析
    ]
    
    for i, command in enumerate(test_commands):
        print(f"\n{'='*50}")
        print(f"測試命令 {i+1}: {command}")
        print(f"{'='*50}")
        
        result = await router.route_claude_code_command(command)
        
        print(f"選擇的提供者: {result['selected_provider']}")
        print(f"是否應用增強: {result['enhancement_applied']}")
        print(f"質量評分: {result['quality_assessment']['quality_score']:.2f}")
        print(f"成本節省: {result['cost_optimization']['savings_percentage']:.1f}%")
        print(f"處理時間: {result['processing_time']:.2f}s")
        
        if result.get('fallback_used'):
            print(f"⚠️ 使用了回退機制: {result['original_provider']} → {result['fallback_provider']}")

if __name__ == "__main__":
    asyncio.run(main())