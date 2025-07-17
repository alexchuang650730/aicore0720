"""
Kimi K2 Router - PowerAutomation v4.8

智能路由器，负责优化 Kimi K2 API 调用，包括:
- 智能路由决策算法
- 请求类型识别和分类
- 上下文增强策略
- 响应质量评估
- 负载均衡和故障转移
- 成本优化策略

设计原则:
- 最大化 Kimi K2 的免费额度利用
- 智能识别最适合的模型版本
- 动态调整请求参数
- 实时性能监控和优化
"""

import json
import logging
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import re

class RequestType(Enum):
    """请求类型枚举"""
    CODE_GENERATION = "code_generation"
    CODE_EXPLANATION = "code_explanation"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    GENERAL_CHAT = "general_chat"
    TECHNICAL_QA = "technical_qa"
    PROJECT_ANALYSIS = "project_analysis"

class ModelVersion(Enum):
    """Kimi K2 模型版本"""
    MOONSHOT_V1_8K = "moonshot-v1-8k"
    MOONSHOT_V1_32K = "moonshot-v1-32k"
    MOONSHOT_V1_128K = "moonshot-v1-128k"

@dataclass
class RoutingDecision:
    """路由决策数据结构"""
    model_version: ModelVersion
    request_type: RequestType
    confidence: float
    reasoning: str
    estimated_tokens: int
    priority: int
    use_rag: bool
    context_strategy: str

@dataclass
class K2Request:
    """K2 请求数据结构"""
    query: str
    context: str = ""
    max_tokens: int = 4000
    temperature: float = 0.3
    top_p: float = 0.8
    model_version: ModelVersion = ModelVersion.MOONSHOT_V1_32K
    request_type: RequestType = RequestType.GENERAL_CHAT
    metadata: Dict[str, Any] = None

@dataclass
class K2Response:
    """K2 响应数据结构"""
    status: str
    content: str
    model_used: str
    usage: Dict[str, Any]
    response_time_ms: float
    quality_score: float
    cost_info: Dict[str, Any]
    metadata: Dict[str, Any]

class K2Router:
    """Kimi K2 智能路由器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化 K2 路由器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # API 配置
        self.api_endpoint = self.config.get("api_endpoint", "https://api.moonshot.cn/v1")
        self.api_key = self.config.get("api_key", "")
        self.timeout = self.config.get("timeout", 30)
        self.max_retries = self.config.get("max_retries", 3)
        
        # 路由配置
        self.enable_smart_routing = self.config.get("enable_smart_routing", True)
        self.enable_context_optimization = self.config.get("enable_context_optimization", True)
        self.enable_quality_assessment = self.config.get("enable_quality_assessment", True)
        self.enable_cost_optimization = self.config.get("enable_cost_optimization", True)
        
        # 性能配置
        self.max_concurrent_requests = self.config.get("max_concurrent_requests", 10)
        self.rate_limit_per_minute = self.config.get("rate_limit_per_minute", 60)
        
        # 初始化组件
        self.logger = logging.getLogger(__name__)
        self.session = None
        
        # 请求队列和限流
        self.request_queue = asyncio.Queue()
        self.rate_limiter = []
        self.concurrent_requests = 0
        
        # 统计和监控
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "avg_response_time": 0.0,
            "model_usage": {},
            "request_type_distribution": {},
            "quality_scores": [],
            "cost_savings": 0.0,
            "last_request_time": None
        }
        
        # 缓存
        self.response_cache = {}
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5分钟
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化路由器"""
        try:
            self.logger.info("初始化 Kimi K2 路由器...")
            
            # 创建 HTTP 会话
            connector = aiohttp.TCPConnector(limit=self.max_concurrent_requests)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            
            # 验证 API 连接
            if self.api_key:
                test_result = await self._test_api_connection()
                if not test_result["success"]:
                    self.logger.warning(f"API 连接测试失败: {test_result['error']}")
            else:
                self.logger.warning("API 密钥未配置")
            
            # 启动后台任务
            asyncio.create_task(self._rate_limiter_task())
            asyncio.create_task(self._cache_cleanup_task())
            
            result = {
                "status": "success",
                "api_endpoint": self.api_endpoint,
                "smart_routing_enabled": self.enable_smart_routing,
                "context_optimization_enabled": self.enable_context_optimization,
                "max_concurrent_requests": self.max_concurrent_requests,
                "rate_limit_per_minute": self.rate_limit_per_minute,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("K2 路由器初始化完成")
            return result
            
        except Exception as e:
            self.logger.error(f"K2 路由器初始化失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def route_request(self, request: K2Request) -> K2Response:
        """
        智能路由请求
        
        Args:
            request: K2 请求对象
            
        Returns:
            K2 响应对象
        """
        try:
            start_time = time.time()
            
            # 1. 检查缓存
            cache_key = self._generate_cache_key(request)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self.logger.info("返回缓存响应")
                return cached_response
            
            # 2. 智能路由决策
            routing_decision = await self._make_routing_decision(request)
            
            # 3. 上下文优化
            optimized_request = await self._optimize_context(request, routing_decision)
            
            # 4. 执行请求
            response = await self._execute_request(optimized_request, routing_decision)
            
            # 5. 质量评估
            if self.enable_quality_assessment:
                response.quality_score = await self._assess_response_quality(
                    optimized_request, response
                )
            
            # 6. 缓存响应
            if response.status == "success" and response.quality_score > 0.7:
                self._cache_response(cache_key, response)
            
            # 7. 更新统计
            await self._update_stats(optimized_request, response, routing_decision, start_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"请求路由失败: {str(e)}")
            return K2Response(
                status="error",
                content=f"请求处理失败: {str(e)}",
                model_used="unknown",
                usage={},
                response_time_ms=0.0,
                quality_score=0.0,
                cost_info={},
                metadata={"error": str(e)}
            )
    
    async def _make_routing_decision(self, request: K2Request) -> RoutingDecision:
        """智能路由决策"""
        try:
            if not self.enable_smart_routing:
                return RoutingDecision(
                    model_version=request.model_version,
                    request_type=request.request_type,
                    confidence=1.0,
                    reasoning="智能路由已禁用",
                    estimated_tokens=len(request.query) // 4,
                    priority=5,
                    use_rag=True,
                    context_strategy="default"
                )
            
            # 分析请求类型
            detected_type = await self._detect_request_type(request.query)
            
            # 估算 token 使用量
            estimated_tokens = await self._estimate_token_usage(request)
            
            # 选择最佳模型版本
            best_model = await self._select_best_model(detected_type, estimated_tokens)
            
            # 确定是否使用 RAG
            use_rag = await self._should_use_rag(detected_type, request.query)
            
            # 选择上下文策略
            context_strategy = await self._select_context_strategy(detected_type, estimated_tokens)
            
            # 计算优先级
            priority = await self._calculate_priority(detected_type, estimated_tokens)
            
            decision = RoutingDecision(
                model_version=best_model,
                request_type=detected_type,
                confidence=0.85,  # 可以基于更复杂的算法计算
                reasoning=f"基于请求类型 {detected_type.value} 和预估 {estimated_tokens} tokens",
                estimated_tokens=estimated_tokens,
                priority=priority,
                use_rag=use_rag,
                context_strategy=context_strategy
            )
            
            self.logger.info(f"路由决策: {best_model.value}, 类型: {detected_type.value}")
            return decision
            
        except Exception as e:
            self.logger.error(f"路由决策失败: {str(e)}")
            # 返回默认决策
            return RoutingDecision(
                model_version=ModelVersion.MOONSHOT_V1_32K,
                request_type=RequestType.GENERAL_CHAT,
                confidence=0.5,
                reasoning=f"决策失败，使用默认配置: {str(e)}",
                estimated_tokens=1000,
                priority=5,
                use_rag=True,
                context_strategy="default"
            )
    
    async def _detect_request_type(self, query: str) -> RequestType:
        """检测请求类型"""
        query_lower = query.lower()
        
        # 代码生成关键词
        code_gen_keywords = [
            "写一个", "生成代码", "实现", "创建函数", "写函数", "代码示例",
            "write code", "generate", "implement", "create function"
        ]
        
        # 代码解释关键词
        code_explain_keywords = [
            "解释代码", "这段代码", "代码作用", "代码功能", "explain code",
            "what does", "how does", "code analysis"
        ]
        
        # 代码审查关键词
        code_review_keywords = [
            "代码审查", "检查代码", "优化代码", "代码问题", "code review",
            "optimize", "improve code", "code issues"
        ]
        
        # 调试关键词
        debug_keywords = [
            "调试", "错误", "bug", "异常", "debug", "error", "exception",
            "not working", "问题", "fix"
        ]
        
        # 文档关键词
        doc_keywords = [
            "文档", "注释", "说明", "documentation", "comment", "readme",
            "how to", "tutorial", "guide"
        ]
        
        # 技术问答关键词
        qa_keywords = [
            "如何", "怎么", "什么是", "为什么", "how to", "what is", "why",
            "difference", "compare", "best practice"
        ]
        
        # 检测逻辑
        if any(keyword in query_lower for keyword in code_gen_keywords):
            return RequestType.CODE_GENERATION
        elif any(keyword in query_lower for keyword in code_explain_keywords):
            return RequestType.CODE_EXPLANATION
        elif any(keyword in query_lower for keyword in code_review_keywords):
            return RequestType.CODE_REVIEW
        elif any(keyword in query_lower for keyword in debug_keywords):
            return RequestType.DEBUGGING
        elif any(keyword in query_lower for keyword in doc_keywords):
            return RequestType.DOCUMENTATION
        elif any(keyword in query_lower for keyword in qa_keywords):
            return RequestType.TECHNICAL_QA
        else:
            return RequestType.GENERAL_CHAT
    
    async def _estimate_token_usage(self, request: K2Request) -> int:
        """估算 token 使用量"""
        # 简单的 token 估算（1 token ≈ 4 字符）
        query_tokens = len(request.query) // 4
        context_tokens = len(request.context) // 4
        
        # 根据请求类型调整估算
        type_multipliers = {
            RequestType.CODE_GENERATION: 3.0,  # 代码生成通常需要更多输出
            RequestType.CODE_EXPLANATION: 2.0,
            RequestType.CODE_REVIEW: 2.5,
            RequestType.DOCUMENTATION: 2.0,
            RequestType.DEBUGGING: 2.0,
            RequestType.TECHNICAL_QA: 1.5,
            RequestType.GENERAL_CHAT: 1.0,
            RequestType.PROJECT_ANALYSIS: 3.0
        }
        
        multiplier = type_multipliers.get(request.request_type, 1.0)
        estimated_output_tokens = int(query_tokens * multiplier)
        
        total_tokens = query_tokens + context_tokens + estimated_output_tokens
        return min(total_tokens, 32000)  # 限制在最大上下文长度内
    
    async def _select_best_model(self, request_type: RequestType, estimated_tokens: int) -> ModelVersion:
        """选择最佳模型版本"""
        # 根据 token 数量选择模型
        if estimated_tokens <= 8000:
            return ModelVersion.MOONSHOT_V1_8K
        elif estimated_tokens <= 32000:
            return ModelVersion.MOONSHOT_V1_32K
        else:
            return ModelVersion.MOONSHOT_V1_128K
    
    async def _should_use_rag(self, request_type: RequestType, query: str) -> bool:
        """判断是否应该使用 RAG"""
        # 代码相关的请求通常受益于 RAG
        rag_beneficial_types = {
            RequestType.CODE_GENERATION,
            RequestType.CODE_EXPLANATION,
            RequestType.CODE_REVIEW,
            RequestType.DEBUGGING,
            RequestType.TECHNICAL_QA,
            RequestType.PROJECT_ANALYSIS
        }
        
        return request_type in rag_beneficial_types
    
    async def _select_context_strategy(self, request_type: RequestType, estimated_tokens: int) -> str:
        """选择上下文策略"""
        if estimated_tokens > 16000:
            return "compress"  # 压缩上下文
        elif request_type in [RequestType.CODE_GENERATION, RequestType.DEBUGGING]:
            return "focused"  # 聚焦相关代码
        else:
            return "default"  # 默认策略
    
    async def _calculate_priority(self, request_type: RequestType, estimated_tokens: int) -> int:
        """计算请求优先级 (1-10, 1最高)"""
        # 基础优先级
        base_priorities = {
            RequestType.DEBUGGING: 2,  # 调试优先级最高
            RequestType.CODE_GENERATION: 3,
            RequestType.CODE_REVIEW: 4,
            RequestType.TECHNICAL_QA: 5,
            RequestType.CODE_EXPLANATION: 6,
            RequestType.DOCUMENTATION: 7,
            RequestType.PROJECT_ANALYSIS: 8,
            RequestType.GENERAL_CHAT: 9
        }
        
        priority = base_priorities.get(request_type, 5)
        
        # 根据 token 数量调整（小请求优先级更高）
        if estimated_tokens < 1000:
            priority -= 1
        elif estimated_tokens > 10000:
            priority += 1
        
        return max(1, min(10, priority))
    
    async def _optimize_context(self, request: K2Request, decision: RoutingDecision) -> K2Request:
        """优化上下文"""
        if not self.enable_context_optimization:
            return request
        
        try:
            optimized_context = request.context
            
            if decision.context_strategy == "compress":
                # 压缩上下文
                optimized_context = await self._compress_context(request.context)
            elif decision.context_strategy == "focused":
                # 聚焦相关内容
                optimized_context = await self._focus_context(request.context, request.query)
            
            # 创建优化后的请求
            optimized_request = K2Request(
                query=request.query,
                context=optimized_context,
                max_tokens=min(request.max_tokens, decision.estimated_tokens),
                temperature=request.temperature,
                top_p=request.top_p,
                model_version=decision.model_version,
                request_type=decision.request_type,
                metadata=request.metadata
            )
            
            return optimized_request
            
        except Exception as e:
            self.logger.error(f"上下文优化失败: {str(e)}")
            return request
    
    async def _compress_context(self, context: str) -> str:
        """压缩上下文"""
        if len(context) <= 2000:
            return context
        
        # 简单的压缩策略：保留开头和结尾，压缩中间部分
        lines = context.split('\n')
        if len(lines) <= 20:
            return context
        
        compressed_lines = (
            lines[:10] +  # 保留前10行
            [f"... (省略 {len(lines) - 20} 行) ..."] +  # 压缩标记
            lines[-10:]  # 保留后10行
        )
        
        return '\n'.join(compressed_lines)
    
    async def _focus_context(self, context: str, query: str) -> str:
        """聚焦相关上下文"""
        if len(context) <= 2000:
            return context
        
        # 提取查询中的关键词
        query_keywords = re.findall(r'\b\w+\b', query.lower())
        
        # 按行分析相关性
        lines = context.split('\n')
        scored_lines = []
        
        for i, line in enumerate(lines):
            score = 0
            line_lower = line.lower()
            
            # 计算关键词匹配分数
            for keyword in query_keywords:
                if keyword in line_lower:
                    score += 1
            
            scored_lines.append((score, i, line))
        
        # 排序并选择最相关的行
        scored_lines.sort(key=lambda x: x[0], reverse=True)
        selected_lines = scored_lines[:30]  # 选择前30行
        selected_lines.sort(key=lambda x: x[1])  # 按原始顺序排序
        
        focused_context = '\n'.join([line[2] for line in selected_lines])
        return focused_context
    
    async def _execute_request(self, request: K2Request, decision: RoutingDecision) -> K2Response:
        """执行 API 请求"""
        try:
            # 等待速率限制
            await self._wait_for_rate_limit()
            
            # 构建请求负载
            payload = {
                "model": decision.model_version.value,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的编程助手，专注于提供高质量的代码和技术解答。"
                    },
                    {
                        "role": "user",
                        "content": f"{request.context}\n\n{request.query}" if request.context else request.query
                    }
                ],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p
            }
            
            # 执行请求
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{self.api_endpoint}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    return K2Response(
                        status="success",
                        content=data["choices"][0]["message"]["content"],
                        model_used=data["model"],
                        usage=data.get("usage", {}),
                        response_time_ms=response_time,
                        quality_score=0.0,  # 将在后续评估
                        cost_info={"estimated_cost": 0.0},  # Kimi K2 免费
                        metadata={
                            "request_type": decision.request_type.value,
                            "routing_decision": decision.reasoning
                        }
                    )
                else:
                    error_text = await response.text()
                    return K2Response(
                        status="error",
                        content=f"API 错误: {response.status} - {error_text}",
                        model_used=decision.model_version.value,
                        usage={},
                        response_time_ms=response_time,
                        quality_score=0.0,
                        cost_info={},
                        metadata={"error": error_text}
                    )
                    
        except Exception as e:
            self.logger.error(f"API 请求执行失败: {str(e)}")
            return K2Response(
                status="error",
                content=f"请求执行失败: {str(e)}",
                model_used="unknown",
                usage={},
                response_time_ms=0.0,
                quality_score=0.0,
                cost_info={},
                metadata={"error": str(e)}
            )
    
    async def _assess_response_quality(self, request: K2Request, response: K2Response) -> float:
        """评估响应质量"""
        try:
            if response.status != "success":
                return 0.0
            
            score = 0.0
            
            # 1. 长度合理性 (0-0.3)
            content_length = len(response.content)
            if 50 <= content_length <= 2000:
                score += 0.3
            elif content_length > 2000:
                score += 0.2
            elif content_length > 20:
                score += 0.1
            
            # 2. 内容相关性 (0-0.4)
            query_keywords = set(re.findall(r'\b\w+\b', request.query.lower()))
            response_keywords = set(re.findall(r'\b\w+\b', response.content.lower()))
            
            if query_keywords:
                relevance = len(query_keywords & response_keywords) / len(query_keywords)
                score += relevance * 0.4
            
            # 3. 代码质量 (0-0.3，仅对代码相关请求)
            if request.request_type in [RequestType.CODE_GENERATION, RequestType.CODE_EXPLANATION]:
                if "```" in response.content:  # 包含代码块
                    score += 0.2
                if any(keyword in response.content.lower() for keyword in ["function", "class", "def", "return"]):
                    score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"质量评估失败: {str(e)}")
            return 0.5  # 默认中等质量
    
    async def _wait_for_rate_limit(self):
        """等待速率限制"""
        current_time = time.time()
        
        # 清理过期的请求记录
        self.rate_limiter = [
            req_time for req_time in self.rate_limiter 
            if current_time - req_time < 60
        ]
        
        # 检查是否超过速率限制
        if len(self.rate_limiter) >= self.rate_limit_per_minute:
            sleep_time = 60 - (current_time - self.rate_limiter[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # 记录当前请求
        self.rate_limiter.append(current_time)
    
    def _generate_cache_key(self, request: K2Request) -> str:
        """生成缓存键"""
        content = f"{request.query}_{request.context}_{request.model_version.value}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[K2Response]:
        """获取缓存响应"""
        if cache_key in self.response_cache:
            cached_data, timestamp = self.response_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.response_cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: K2Response):
        """缓存响应"""
        self.response_cache[cache_key] = (response, time.time())
    
    async def _update_stats(self, request: K2Request, response: K2Response, decision: RoutingDecision, start_time: float):
        """更新统计信息"""
        try:
            self.stats["total_requests"] += 1
            self.stats["last_request_time"] = datetime.now()
            
            if response.status == "success":
                self.stats["successful_requests"] += 1
                
                # 更新响应时间
                response_time = response.response_time_ms
                self.stats["avg_response_time"] = (
                    (self.stats["avg_response_time"] * (self.stats["successful_requests"] - 1) + response_time) 
                    / self.stats["successful_requests"]
                )
                
                # 更新模型使用统计
                model = response.model_used
                self.stats["model_usage"][model] = self.stats["model_usage"].get(model, 0) + 1
                
                # 更新请求类型分布
                req_type = decision.request_type.value
                self.stats["request_type_distribution"][req_type] = \
                    self.stats["request_type_distribution"].get(req_type, 0) + 1
                
                # 更新质量分数
                if response.quality_score > 0:
                    self.stats["quality_scores"].append(response.quality_score)
                    # 只保留最近100个分数
                    if len(self.stats["quality_scores"]) > 100:
                        self.stats["quality_scores"] = self.stats["quality_scores"][-100:]
                
                # 更新 token 使用
                if "total_tokens" in response.usage:
                    self.stats["total_tokens_used"] += response.usage["total_tokens"]
            else:
                self.stats["failed_requests"] += 1
                
        except Exception as e:
            self.logger.error(f"统计更新失败: {str(e)}")
    
    async def _test_api_connection(self) -> Dict[str, Any]:
        """测试 API 连接"""
        try:
            test_request = K2Request(
                query="test",
                max_tokens=10,
                model_version=ModelVersion.MOONSHOT_V1_8K
            )
            
            payload = {
                "model": test_request.model_version.value,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{self.api_endpoint}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return {"success": True, "message": "API 连接正常"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _rate_limiter_task(self):
        """速率限制后台任务"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟清理一次
                current_time = time.time()
                self.rate_limiter = [
                    req_time for req_time in self.rate_limiter 
                    if current_time - req_time < 60
                ]
            except Exception as e:
                self.logger.error(f"速率限制任务错误: {str(e)}")
    
    async def _cache_cleanup_task(self):
        """缓存清理后台任务"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分钟清理一次
                current_time = time.time()
                expired_keys = [
                    key for key, (_, timestamp) in self.response_cache.items()
                    if current_time - timestamp > self.cache_ttl
                ]
                for key in expired_keys:
                    del self.response_cache[key]
                    
                if expired_keys:
                    self.logger.info(f"清理了 {len(expired_keys)} 个过期缓存")
                    
            except Exception as e:
                self.logger.error(f"缓存清理任务错误: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        # 计算平均质量分数
        if stats["quality_scores"]:
            stats["avg_quality_score"] = sum(stats["quality_scores"]) / len(stats["quality_scores"])
        else:
            stats["avg_quality_score"] = 0.0
        
        # 计算成功率
        if stats["total_requests"] > 0:
            stats["success_rate"] = stats["successful_requests"] / stats["total_requests"]
        else:
            stats["success_rate"] = 0.0
        
        # 添加缓存统计
        stats["cache_size"] = len(self.response_cache)
        stats["rate_limiter_size"] = len(self.rate_limiter)
        
        return stats
    
    async def cleanup(self):
        """清理资源"""
        if self.session:
            await self.session.close()
        self.logger.info("K2 路由器资源已清理")


    def identify_request_type(self, query: str) -> str:
        """识别请求类型
        
        Args:
            query: 用户查询
            
        Returns:
            请求类型
        """
        query_lower = query.lower()
        
        # 代码生成类型
        code_keywords = ["写一个", "生成代码", "实现", "创建函数", "编写", "代码", "function", "class", "def ", "import"]
        if any(keyword in query_lower for keyword in code_keywords):
            return "code_generation"
            
        # 调试类型
        debug_keywords = ["调试", "错误", "bug", "修复", "debug", "error", "exception", "traceback"]
        if any(keyword in query_lower for keyword in debug_keywords):
            return "debugging"
            
        # 解释类型
        explain_keywords = ["解释", "说明", "什么是", "如何", "为什么", "explain", "what is", "how to"]
        if any(keyword in query_lower for keyword in explain_keywords):
            return "explanation"
            
        # 文档类型
        doc_keywords = ["文档", "注释", "说明书", "readme", "documentation", "comment"]
        if any(keyword in query_lower for keyword in doc_keywords):
            return "documentation"
            
        # 优化类型
        optimize_keywords = ["优化", "性能", "改进", "提升", "optimize", "performance", "improve"]
        if any(keyword in query_lower for keyword in optimize_keywords):
            return "optimization"
            
        # 测试类型
        test_keywords = ["测试", "单元测试", "test", "unittest", "pytest"]
        if any(keyword in query_lower for keyword in test_keywords):
            return "testing"
            
        # 重构类型
        refactor_keywords = ["重构", "重写", "改写", "refactor", "rewrite"]
        if any(keyword in query_lower for keyword in refactor_keywords):
            return "refactoring"
            
        # 默认为一般查询
        return "general_query"
    
    def optimize_context(self, context: str, strategy: str = "default") -> str:
        """优化上下文
        
        Args:
            context: 原始上下文
            strategy: 优化策略 (compress, focus, default)
            
        Returns:
            优化后的上下文
        """
        if not context or len(context) <= 1000:
            return context
            
        if strategy == "compress":
            # 压缩策略：保留关键信息，移除冗余
            lines = context.split('\n')
            important_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 保留重要的行
                if any(keyword in line.lower() for keyword in [
                    'def ', 'class ', 'import ', 'from ', 'error', 'exception',
                    'todo', 'fixme', 'bug', 'issue', '问题', '错误'
                ]):
                    important_lines.append(line)
                elif len(line) > 20 and not line.startswith('#'):
                    # 保留较长的非注释行
                    important_lines.append(line)
            
            compressed = '\n'.join(important_lines)
            return compressed[:len(context) // 2] if len(compressed) > len(context) // 2 else compressed
            
        elif strategy == "focus":
            # 聚焦策略：只保留最相关的部分
            sentences = context.split('.')
            focused_sentences = []
            
            for sentence in sentences[:10]:  # 只保留前10句
                if len(sentence.strip()) > 10:
                    focused_sentences.append(sentence.strip())
            
            return '. '.join(focused_sentences)
            
        else:
            # 默认策略：简单截断
            max_length = 2000
            if len(context) > max_length:
                return context[:max_length] + "..."
            return context
    
    def select_model(self, query: str, context_length: int = 0) -> str:
        """选择合适的模型
        
        Args:
            query: 用户查询
            context_length: 上下文长度
            
        Returns:
            模型名称
        """
        # 根据上下文长度选择模型
        if context_length > 100000:
            return "moonshot-v1-128k"
        elif context_length > 30000:
            return "moonshot-v1-32k"
        else:
            return "moonshot-v1-8k"

