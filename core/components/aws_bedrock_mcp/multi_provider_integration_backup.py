#!/usr/bin/env python3
"""
Memory RAG MCP - 多 Provider 集成模块
将多 Provider 代理系统集成到 RAG 服务中
使用 HuggingFace Hub InferenceClient 支持多个 provider
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Any, Optional
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

class MultiProviderRAGIntegration:
    """多 Provider RAG 集成"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 配置多个 HuggingFace Hub Provider（按性能优先级排序）
        self.llm_providers = [
            {
                "name": "HF-Groq",
                "provider": "groq", 
                "api_key": os.getenv("HF_TOKEN", ""),
                "model": "moonshotai/Kimi-K2-Instruct",
                "priority": 1,
                "expected_tps": 100,  # 预期 TPS
                "expected_latency": 0.5,  # 预期延迟（秒）
                "max_concurrent": 50  # 最大并发数
            },
            {
                "name": "HF-Together",
                "provider": "together",
                "api_key": os.getenv("HF_TOKEN", ""),
                "model": "moonshotai/Kimi-K2-Instruct", 
                "priority": 2,
                "expected_tps": 80,
                "expected_latency": 0.8,
                "max_concurrent": 40
            },
            {
                "name": "HF-Novita",
                "provider": "novita",
                "api_key": os.getenv("HF_TOKEN", ""),
                "model": "moonshotai/Kimi-K2-Instruct",
                "priority": 3,
                "expected_tps": 60,
                "expected_latency": 1.0,
                "max_concurrent": 30
            },
            {
                "name": "Kimi-K2-Direct",
                "provider": "direct",
                "endpoint": "https://api.moonshot.cn/v1",
                "api_key": os.getenv("KIMI_API_KEY", ""),
                "model": "moonshot-v1-8k",
                "priority": 4,
                "expected_tps": 40,
                "expected_latency": 1.5,
                "max_concurrent": 20
            }
        ]
        
        # 过滤有效的 provider
        self.active_providers = [
            p for p in self.llm_providers 
            if p["api_key"] and p["api_key"] != ""
        ]
        
        if not self.active_providers:
            logger.warning("⚠️ 没有配置有效的 LLM Provider")
            # 添加模拟高性能 provider 用于测试
            self.active_providers = [{
                "name": "Mock-HighPerf-Provider",
                "provider": "mock",
                "api_key": "mock",
                "model": "mock-high-perf-model",
                "priority": 999,
                "is_mock": True,
                "expected_tps": 1000,
                "expected_latency": 0.1,
                "max_concurrent": 100
            }]
        
        # 按优先级排序
        self.active_providers.sort(key=lambda x: x["priority"])
        
        logger.info(f"🔧 配置了 {len(self.active_providers)} 个高性能 LLM Provider:")
        for provider in self.active_providers:
            logger.info(f"   - {provider['name']}: TPS={provider.get('expected_tps', 'N/A')}, "
                       f"延迟={provider.get('expected_latency', 'N/A')}s, "
                       f"并发={provider.get('max_concurrent', 'N/A')}")
        
        # 性能统计和监控
        self.stats = {
            "total_queries": 0,
            "provider_usage": {p["name"]: 0 for p in self.active_providers},
            "success_rate": {p["name"]: 0.0 for p in self.active_providers},
            "avg_response_time": {p["name"]: 0.0 for p in self.active_providers},
            "current_tps": {p["name"]: 0.0 for p in self.active_providers},
            "concurrent_requests": {p["name"]: 0 for p in self.active_providers},
            "error_count": {p["name"]: 0 for p in self.active_providers}
        }
        
        # 性能监控窗口（最近 60 秒）
        self.performance_window = 60
        self.request_history = {p["name"]: [] for p in self.active_providers}
    
    async def generate_rag_response(self, 
                                  query: str, 
                                  context_documents: List[Dict[str, Any]], 
                                  max_tokens: int = 500) -> Dict[str, Any]:
        """使用多 Provider 生成 RAG 响应（智能选择高性能 provider）"""
        
        # 构建增强的提示词
        enhanced_prompt = self._build_rag_prompt(query, context_documents)
        
        # 智能选择最佳 provider
        best_providers = self._select_best_providers()
        
        # 尝试最佳 provider
        for i, provider in enumerate(best_providers):
            try:
                start_time = time.time()
                
                # 检查并发限制
                if self.stats["concurrent_requests"][provider["name"]] >= provider.get("max_concurrent", 10):
                    logger.warning(f"⚠️ Provider {provider['name']} 达到并发限制，跳过")
                    continue
                
                # 增加并发计数
                self.stats["concurrent_requests"][provider["name"]] += 1
                
                logger.info(f"📡 尝试高性能 Provider {i+1}/{len(best_providers)}: {provider['name']} "
                           f"(TPS: {provider.get('expected_tps', 'N/A')}, "
                           f"延迟: {provider.get('expected_latency', 'N/A')}s)")
                
                # 调用 provider
                response = await self._call_provider(provider, enhanced_prompt, max_tokens)
                
                # 减少并发计数
                self.stats["concurrent_requests"][provider["name"]] -= 1
                
                if response["status"] == "success":
                    response_time = time.time() - start_time
                    
                    # 更新性能统计
                    self._update_performance_stats(provider["name"], True, response_time)
                    
                    return {
                        "status": "success",
                        "response": response["content"],
                        "provider": provider["name"],
                        "model": provider["model"],
                        "response_time": response_time,
                        "context_used": len(context_documents),
                        "performance_score": self._calculate_performance_score(provider["name"])
                    }
                else:
                    response_time = time.time() - start_time
                    logger.warning(f"⚠️ Provider {provider['name']} 失败: {response.get('error', 'Unknown error')}")
                    self._update_performance_stats(provider["name"], False, response_time)
                    
            except Exception as e:
                # 减少并发计数
                if provider["name"] in self.stats["concurrent_requests"]:
                    self.stats["concurrent_requests"][provider["name"]] = max(0, 
                        self.stats["concurrent_requests"][provider["name"]] - 1)
                
                logger.error(f"❌ Provider {provider['name']} 异常: {e}")
                self._update_performance_stats(provider["name"], False, 0)
        
        # 所有 provider 都失败
        return {
            "status": "error",
            "error": "所有高性能 LLM Provider 都不可用",
            "providers_tried": len(best_providers),
            "performance_report": self._get_performance_report()
        }
    
    def _select_best_providers(self) -> List[Dict[str, Any]]:
        """智能选择最佳性能的 provider"""
        
        # 计算每个 provider 的性能分数
        provider_scores = []
        
        for provider in self.active_providers:
            name = provider["name"]
            
            # 基础性能分数（基于预期性能）
            base_score = (
                provider.get("expected_tps", 50) * 0.4 +  # TPS 权重 40%
                (1.0 / max(provider.get("expected_latency", 1.0), 0.1)) * 30 +  # 延迟权重 30%
                provider.get("max_concurrent", 20) * 0.3  # 并发权重 30%
            )
            
            # 实际性能调整
            success_rate = self.stats["success_rate"][name]
            avg_response_time = self.stats["avg_response_time"][name]
            current_tps = self.stats["current_tps"][name]
            
            # 性能调整因子
            performance_factor = 1.0
            if success_rate > 0:
                performance_factor *= success_rate  # 成功率影响
            if avg_response_time > 0:
                performance_factor *= (1.0 / max(avg_response_time, 0.1))  # 响应时间影响
            if current_tps > 0:
                performance_factor *= min(current_tps / provider.get("expected_tps", 50), 2.0)  # TPS 影响
            
            # 并发负载调整
            concurrent_load = self.stats["concurrent_requests"][name] / max(provider.get("max_concurrent", 10), 1)
            load_factor = max(0.1, 1.0 - concurrent_load)  # 负载越高，分数越低
            
            final_score = base_score * performance_factor * load_factor
            
            provider_scores.append({
                "provider": provider,
                "score": final_score,
                "base_score": base_score,
                "performance_factor": performance_factor,
                "load_factor": load_factor
            })
        
        # 按分数排序（降序）
        provider_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # 返回排序后的 provider 列表
        best_providers = [item["provider"] for item in provider_scores]
        
        # 记录选择结果
        logger.info("🎯 智能 Provider 选择结果:")
        for i, item in enumerate(provider_scores[:3]):  # 显示前3个
            logger.info(f"   {i+1}. {item['provider']['name']}: 分数={item['score']:.2f} "
                       f"(基础={item['base_score']:.1f}, 性能={item['performance_factor']:.2f}, "
                       f"负载={item['load_factor']:.2f})")
        
        return best_providers
    
    def _build_rag_prompt(self, query: str, context_documents: List[Dict[str, Any]]) -> str:
        """构建 RAG 提示词"""
        if not context_documents:
            return f"请回答以下问题：\n\n{query}"
        
        # 构建上下文
        context_text = ""
        for i, doc in enumerate(context_documents[:5]):  # 最多使用5个文档
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            context_text += f"文档 {i+1}:\n{content}\n"
            if metadata:
                context_text += f"元数据: {json.dumps(metadata, ensure_ascii=False)}\n"
            context_text += "\n"
        
        prompt = f"""基于以下文档内容，请回答用户的问题。

相关文档:
{context_text}

用户问题: {query}

请基于上述文档内容提供准确、详细的回答。如果文档中没有相关信息，请明确说明。"""
        
        return prompt
    
    async def _call_provider(self, 
                           provider: Dict[str, Any], 
                           prompt: str, 
                           max_tokens: int) -> Dict[str, Any]:
        """调用特定的 LLM Provider"""
        
        # 模拟高性能 provider
        if provider.get("is_mock", False):
            await asyncio.sleep(provider.get("expected_latency", 0.1))  # 模拟延迟
            return {
                "status": "success",
                "content": f"这是来自高性能 {provider['name']} 的回答：{prompt[:100]}..."
            }
        
        # HuggingFace Hub Provider
        if provider.get("provider") in ["novita", "groq", "together"]:
            return await self._call_huggingface_hub_provider(provider, prompt, max_tokens)
        
        # 直接 API 调用（如 Kimi K2）
        elif provider.get("provider") == "direct":
            return await self._call_direct_api(provider, prompt, max_tokens)
        
        else:
            return {
                "status": "error",
                "error": f"不支持的 provider 类型: {provider.get('provider')}"
            }
    
    async def _call_huggingface_hub_provider(self, 
                                           provider: Dict[str, Any], 
                                           prompt: str, 
                                           max_tokens: int) -> Dict[str, Any]:
        """调用 HuggingFace Hub Provider"""
        try:
            # 创建 InferenceClient
            client = InferenceClient(
                provider=provider["provider"],
                api_key=provider["api_key"]
            )
            
            # 调用聊天完成 API
            completion = client.chat.completions.create(
                model=provider["model"],
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            # 提取响应内容
            if completion.choices and len(completion.choices) > 0:
                content = completion.choices[0].message.content
                return {
                    "status": "success",
                    "content": content
                }
            else:
                return {
                    "status": "error",
                    "error": "No response from model"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _call_direct_api(self, 
                             provider: Dict[str, Any], 
                             prompt: str, 
                             max_tokens: int) -> Dict[str, Any]:
        """调用直接 API（如 Kimi K2）"""
        try:
            from aiohttp import ClientSession
            
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {provider['api_key']}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": provider["model"],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{provider['endpoint']}/chat/completions",
                    json=data,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # 提取响应内容
                        choices = result.get("choices", [])
                        if choices:
                            content = choices[0].get("message", {}).get("content", "")
                            return {
                                "status": "success",
                                "content": content
                            }
                        else:
                            return {
                                "status": "error",
                                "error": "No choices in response"
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _call_huggingface_api(self, 
                                  provider: Dict[str, Any], 
                                  prompt: str, 
                                  max_tokens: int) -> Dict[str, Any]:
        """调用 HuggingFace API"""
        try:
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {provider['api_key']}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                }
                
                async with session.post(
                    provider["endpoint"],
                    json=data,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # 处理 HuggingFace 响应格式
                        if isinstance(result, list) and len(result) > 0:
                            content = result[0].get("generated_text", "")
                        else:
                            content = str(result)
                        
                        return {
                            "status": "success",
                            "content": content
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _call_openai_compatible_api(self, 
                                        provider: Dict[str, Any], 
                                        prompt: str, 
                                        max_tokens: int) -> Dict[str, Any]:
        """调用 OpenAI 兼容 API"""
        try:
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {provider['api_key']}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": provider["model"],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{provider['endpoint']}/chat/completions",
                    json=data,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # 提取响应内容
                        choices = result.get("choices", [])
                        if choices:
                            content = choices[0].get("message", {}).get("content", "")
                            return {
                                "status": "success",
                                "content": content
                            }
                        else:
                            return {
                                "status": "error",
                                "error": "No choices in response"
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _update_stats(self, provider_name: str, success: bool, response_time: float):
        """更新统计信息"""
        self.stats["total_queries"] += 1
        self.stats["provider_usage"][provider_name] += 1
        
        # 更新成功率
        current_usage = self.stats["provider_usage"][provider_name]
        current_success_rate = self.stats["success_rate"][provider_name]
        
        if success:
            self.stats["success_rate"][provider_name] = (
                (current_success_rate * (current_usage - 1) + 1.0) / current_usage
            )
        else:
            self.stats["success_rate"][provider_name] = (
                (current_success_rate * (current_usage - 1) + 0.0) / current_usage
            )
        
        # 更新平均响应时间
        current_avg_time = self.stats["avg_response_time"][provider_name]
        self.stats["avg_response_time"][provider_name] = (
            (current_avg_time * (current_usage - 1) + response_time) / current_usage
        )
    
    async def get_provider_health(self) -> Dict[str, Any]:
        """获取 Provider 健康状态"""
        health_status = {}
        
        for provider in self.active_providers:
            try:
                # 简单的健康检查
                if provider.get("is_mock", False):
                    status = "healthy"
                else:
                    # 发送简单的测试请求
                    test_response = await self._call_provider(
                        provider, 
                        "Hello", 
                        10
                    )
                    status = "healthy" if test_response["status"] == "success" else "unhealthy"
                
                health_status[provider["name"]] = {
                    "status": status,
                    "model": provider["model"],
                    "usage_count": self.stats["provider_usage"][provider["name"]],
                    "success_rate": self.stats["success_rate"][provider["name"]],
                    "avg_response_time": self.stats["avg_response_time"][provider["name"]]
                }
                
            except Exception as e:
                health_status[provider["name"]] = {
                    "status": "error",
                    "error": str(e),
                    "model": provider["model"]
                }
        
        return {
            "overall_status": "healthy" if any(
                h["status"] == "healthy" for h in health_status.values()
            ) else "unhealthy",
            "providers": health_status,
            "total_queries": self.stats["total_queries"]
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取详细统计信息"""
        return {
            "provider_count": len(self.active_providers),
            "active_providers": [p["name"] for p in self.active_providers],
            "usage_stats": self.stats,
            "health_status": await self.get_provider_health()
        }

# 全局实例
multi_provider_integration = None

def get_multi_provider_integration(config: Dict[str, Any] = None):
    """获取多 Provider 集成实例"""
    global multi_provider_integration
    if multi_provider_integration is None:
        multi_provider_integration = MultiProviderRAGIntegration(config)
    return multi_provider_integration

async def main():
    """测试多 Provider 集成"""
    print("🧪 测试多 Provider RAG 集成...")
    
    # 创建集成实例
    integration = MultiProviderRAGIntegration()
    
    # 测试文档
    test_documents = [
        {
            "content": "Python 是一种高级编程语言，广泛用于数据科学和 Web 开发。",
            "metadata": {"language": "python", "topic": "programming"}
        },
        {
            "content": "FastAPI 是一个现代、快速的 Python Web 框架。",
            "metadata": {"framework": "fastapi", "language": "python"}
        }
    ]
    
    # 测试 RAG 响应生成
    response = await integration.generate_rag_response(
        "什么是 Python？",
        test_documents
    )
    
    print(f"✅ RAG 响应: {response}")
    
    # 测试健康检查
    health = await integration.get_provider_health()
    print(f"✅ Provider 健康状态: {health}")
    
    # 测试统计信息
    stats = await integration.get_statistics()
    print(f"✅ 统计信息: {stats}")
    
    print("✅ 多 Provider RAG 集成测试完成")

if __name__ == "__main__":
    asyncio.run(main())


    
    def _update_performance_stats(self, provider_name: str, success: bool, response_time: float):
        """更新性能统计信息"""
        current_time = time.time()
        
        # 更新基础统计
        self.stats["total_queries"] += 1
        self.stats["provider_usage"][provider_name] += 1
        
        # 更新成功率
        total_requests = self.stats["provider_usage"][provider_name]
        if success:
            current_success_rate = self.stats["success_rate"][provider_name]
            self.stats["success_rate"][provider_name] = (
                (current_success_rate * (total_requests - 1) + 1.0) / total_requests
            )
        else:
            self.stats["error_count"][provider_name] += 1
            current_success_rate = self.stats["success_rate"][provider_name]
            self.stats["success_rate"][provider_name] = (
                (current_success_rate * (total_requests - 1)) / total_requests
            )
        
        # 更新平均响应时间
        if response_time > 0:
            current_avg = self.stats["avg_response_time"][provider_name]
            self.stats["avg_response_time"][provider_name] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
        
        # 更新请求历史（用于计算 TPS）
        if provider_name not in self.request_history:
            self.request_history[provider_name] = []
        
        self.request_history[provider_name].append({
            "timestamp": current_time,
            "success": success,
            "response_time": response_time
        })
        
        # 清理过期的请求历史
        cutoff_time = current_time - self.performance_window
        self.request_history[provider_name] = [
            req for req in self.request_history[provider_name]
            if req["timestamp"] > cutoff_time
        ]
        
        # 计算当前 TPS
        recent_requests = len(self.request_history[provider_name])
        self.stats["current_tps"][provider_name] = recent_requests / self.performance_window
    
    def _calculate_performance_score(self, provider_name: str) -> float:
        """计算 provider 的性能分数"""
        success_rate = self.stats["success_rate"][provider_name]
        avg_response_time = self.stats["avg_response_time"][provider_name]
        current_tps = self.stats["current_tps"][provider_name]
        
        # 性能分数计算
        score = 0.0
        if success_rate > 0:
            score += success_rate * 40  # 成功率权重 40%
        if avg_response_time > 0:
            score += min(10.0 / avg_response_time, 30) # 响应时间权重 30%
        if current_tps > 0:
            score += min(current_tps, 30)  # TPS 权重 30%
        
        return score
    
    def _get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return {
            "total_queries": self.stats["total_queries"],
            "provider_performance": {
                name: {
                    "usage_count": self.stats["provider_usage"][name],
                    "success_rate": self.stats["success_rate"][name],
                    "avg_response_time": self.stats["avg_response_time"][name],
                    "current_tps": self.stats["current_tps"][name],
                    "concurrent_requests": self.stats["concurrent_requests"][name],
                    "error_count": self.stats["error_count"][name],
                    "performance_score": self._calculate_performance_score(name)
                }
                for name in [p["name"] for p in self.active_providers]
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        healthy_providers = []
        unhealthy_providers = []
        
        for provider in self.active_providers:
            name = provider["name"]
            success_rate = self.stats["success_rate"][name]
            avg_response_time = self.stats["avg_response_time"][name]
            current_tps = self.stats["current_tps"][name]
            
            # 健康状态判断
            is_healthy = (
                success_rate >= 0.8 and  # 成功率 >= 80%
                (avg_response_time == 0 or avg_response_time <= provider.get("expected_latency", 2.0) * 2) and  # 响应时间合理
                self.stats["concurrent_requests"][name] < provider.get("max_concurrent", 10)  # 未达到并发限制
            )
            
            provider_status = {
                "name": name,
                "status": "healthy" if is_healthy else "unhealthy",
                "model": provider["model"],
                "usage_count": self.stats["provider_usage"][name],
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "current_tps": current_tps,
                "concurrent_requests": self.stats["concurrent_requests"][name],
                "max_concurrent": provider.get("max_concurrent", 10),
                "expected_tps": provider.get("expected_tps", 50),
                "expected_latency": provider.get("expected_latency", 1.0),
                "performance_score": self._calculate_performance_score(name)
            }
            
            if is_healthy:
                healthy_providers.append(provider_status)
            else:
                unhealthy_providers.append(provider_status)
        
        # 整体健康状态
        overall_status = "healthy" if len(healthy_providers) > 0 else "unhealthy"
        if len(healthy_providers) > 0 and len(unhealthy_providers) > 0:
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "healthy_providers": healthy_providers,
            "unhealthy_providers": unhealthy_providers,
            "total_providers": len(self.active_providers),
            "performance_summary": self._get_performance_report()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "provider_count": len(self.active_providers),
            "active_providers": [p["name"] for p in self.active_providers],
            "usage_stats": {
                "total_queries": self.stats["total_queries"],
                "provider_usage": self.stats["provider_usage"],
                "success_rate": self.stats["success_rate"],
                "avg_response_time": self.stats["avg_response_time"],
                "current_tps": self.stats["current_tps"],
                "concurrent_requests": self.stats["concurrent_requests"],
                "error_count": self.stats["error_count"]
            },
            "performance_report": self._get_performance_report(),
            "health_status": asyncio.create_task(self.health_check()) if hasattr(asyncio, 'create_task') else None
        }


# 测试代码
async def main():
    """测试多 Provider RAG 集成（高性能版本）"""
    print("🧪 测试高性能多 Provider RAG 集成...")
    
    # 创建集成实例
    integration = MultiProviderRAGIntegration()
    
    # 模拟文档上下文
    context_docs = [
        {
            "content": "Python 是一种高级编程语言，具有简洁的语法和强大的功能。",
            "metadata": {"source": "python_guide.md", "score": 0.95}
        },
        {
            "content": "FastAPI 是一个现代、快速的 Web 框架，用于构建 API。",
            "metadata": {"source": "fastapi_docs.md", "score": 0.88}
        }
    ]
    
    # 测试 RAG 响应生成
    print("\n📡 测试高性能 RAG 响应生成...")
    response = await integration.generate_rag_response(
        query="如何使用 Python 开发 Web API？",
        context_documents=context_docs,
        max_tokens=200
    )
    print(f"✅ RAG 响应: {response}")
    
    # 测试健康检查
    print("\n🏥 测试 Provider 健康状态...")
    health = await integration.health_check()
    print(f"✅ Provider 健康状态: {health}")
    
    # 测试统计信息
    print("\n📊 测试统计信息...")
    stats = integration.get_statistics()
    print(f"✅ 统计信息: {stats}")
    
    print("✅ 高性能多 Provider RAG 集成测试完成")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

