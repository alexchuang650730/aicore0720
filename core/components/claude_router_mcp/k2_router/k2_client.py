#!/usr/bin/env python3
"""
K2 Service Client - K2 服务客户端
处理与 K2 服务的通信和 AI 推理任务路由
"""

import asyncio
import json
import logging
import time
import httpx
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

@dataclass
class K2Request:
    """K2 服务请求"""
    request_id: str
    request_type: str
    content: str
    context: Dict[str, Any] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = False
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if not self.request_id:
            self.request_id = str(uuid.uuid4())

@dataclass
class K2Response:
    """K2 服务响应"""
    request_id: str
    success: bool
    content: str
    usage: Dict[str, int] = None
    cost: float = 0.0
    response_time: float = 0.0
    error_message: str = ""
    
    def __post_init__(self):
        if self.usage is None:
            self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

class K2Client:
    """K2 服务客户端"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or self._get_default_config()
        
        # HTTP 客户端
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=50)
        )
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0,
            "start_time": datetime.now().isoformat()
        }
        
        # 请求历史（用于调试）
        self.request_history = []
        self.max_history_size = 100
        
        # 连接状态
        self.connected = False
        self.last_health_check = None
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "url": "https://cloud.infini-ai.com/maas/v1",
            "api_key": "sk-kqbgz7fvqdutvns7",
            "model_id": "kimi-k2-instruct",
            "enabled": True,
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 1.0
        }
    
    async def initialize(self) -> bool:
        """初始化 K2 客户端"""
        try:
            self.logger.info("🔄 初始化 K2 服务客户端...")
            
            # 健康检查
            healthy = await self.health_check()
            
            if healthy:
                self.connected = True
                self.logger.info("✅ K2 服务客户端初始化成功")
                return True
            else:
                self.logger.warning("⚠️ K2 服务连接异常，但客户端已初始化")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ K2 客户端初始化失败: {e}")
            return False
    
    async def route_ai_request(self, request: K2Request) -> K2Response:
        """路由 AI 请求到 K2 服务"""
        start_time = time.time()
        
        try:
            self.logger.info(f"🔄 路由 AI 请求到 K2: {request.request_type} - {request.request_id}")
            
            if not self.config["enabled"]:
                raise Exception("K2 服务未启用")
            
            # 构建请求
            k2_request_data = self._build_k2_request(request)
            
            # 发送请求
            response_data = await self._send_k2_request(k2_request_data)
            
            # 解析响应
            k2_response = self._parse_k2_response(request.request_id, response_data)
            
            # 计算响应时间和成本
            response_time = time.time() - start_time
            k2_response.response_time = response_time
            k2_response.cost = self._calculate_cost(k2_response.usage)
            
            # 更新统计
            self._update_stats(True, response_time, k2_response.cost)
            
            # 记录历史
            self._add_to_history(request, k2_response)
            
            self.logger.info(f"✅ K2 路由成功: {request.request_id} ({response_time:.2f}s)")
            
            return k2_response
            
        except Exception as e:
            response_time = time.time() - start_time
            error_response = K2Response(
                request_id=request.request_id,
                success=False,
                content="",
                error_message=str(e),
                response_time=response_time
            )
            
            # 更新统计
            self._update_stats(False, response_time, 0.0)
            
            # 记录历史
            self._add_to_history(request, error_response)
            
            self.logger.error(f"❌ K2 路由失败: {request.request_id} - {str(e)}")
            
            return error_response
    
    def _build_k2_request(self, request: K2Request) -> Dict[str, Any]:
        """构建 K2 请求数据"""
        return {
            "model": self.config["model_id"],
            "messages": [
                {
                    "role": "user",
                    "content": request.content
                }
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": request.stream
        }
    
    async def _send_k2_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送 K2 请求"""
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.config['url']}/chat/completions"
        
        # 重试机制
        max_retries = self.config.get("max_retries", 3)
        retry_delay = self.config.get("retry_delay", 1.0)
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.http_client.post(
                    url,
                    json=request_data,
                    headers=headers
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if attempt == max_retries:
                    raise Exception(f"HTTP 错误 {e.response.status_code}: {e.response.text}")
                
                self.logger.warning(f"请求失败，重试 {attempt + 1}/{max_retries}: {e}")
                await asyncio.sleep(retry_delay * (attempt + 1))
                
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                self.logger.warning(f"请求异常，重试 {attempt + 1}/{max_retries}: {e}")
                await asyncio.sleep(retry_delay * (attempt + 1))
    
    def _parse_k2_response(self, request_id: str, response_data: Dict[str, Any]) -> K2Response:
        """解析 K2 响应"""
        try:
            # 提取内容
            content = ""
            if "choices" in response_data and len(response_data["choices"]) > 0:
                choice = response_data["choices"][0]
                if "message" in choice:
                    content = choice["message"].get("content", "")
                elif "text" in choice:
                    content = choice.get("text", "")
            
            # 提取使用量
            usage = response_data.get("usage", {})
            
            return K2Response(
                request_id=request_id,
                success=True,
                content=content,
                usage=usage
            )
            
        except Exception as e:
            return K2Response(
                request_id=request_id,
                success=False,
                content="",
                error_message=f"解析响应失败: {str(e)}"
            )
    
    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        """计算成本"""
        # K2 服务成本：$0.0005 per 1K tokens
        cost_per_1k_tokens = 0.0005
        total_tokens = usage.get("total_tokens", 0)
        return (total_tokens / 1000) * cost_per_1k_tokens
    
    def _update_stats(self, success: bool, response_time: float, cost: float):
        """更新统计信息"""
        self.stats["total_requests"] += 1
        
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
        
        self.stats["total_cost"] += cost
        
        # 更新平均响应时间
        total_time = self.stats["average_response_time"] * (self.stats["total_requests"] - 1) + response_time
        self.stats["average_response_time"] = total_time / self.stats["total_requests"]
    
    def _add_to_history(self, request: K2Request, response: K2Response):
        """添加到请求历史"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": asdict(request),
            "response": asdict(response)
        }
        
        self.request_history.append(history_entry)
        
        # 保持历史大小限制
        if len(self.request_history) > self.max_history_size:
            self.request_history.pop(0)
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> K2Response:
        """聊天完成"""
        # 将消息转换为单个内容字符串
        content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        request = K2Request(
            request_id=str(uuid.uuid4()),
            request_type="chat_completion",
            content=content,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=kwargs.get("stream", False)
        )
        
        return await self.route_ai_request(request)
    
    async def text_generation(self, prompt: str, **kwargs) -> K2Response:
        """文本生成"""
        request = K2Request(
            request_id=str(uuid.uuid4()),
            request_type="text_generation",
            content=prompt,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=kwargs.get("stream", False)
        )
        
        return await self.route_ai_request(request)
    
    async def code_generation(self, prompt: str, language: str = "", **kwargs) -> K2Response:
        """代码生成"""
        content = f"请生成 {language} 代码：\n{prompt}" if language else prompt
        
        request = K2Request(
            request_id=str(uuid.uuid4()),
            request_type="code_generation",
            content=content,
            context={"language": language},
            temperature=kwargs.get("temperature", 0.3),  # 代码生成使用较低温度
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=kwargs.get("stream", False)
        )
        
        return await self.route_ai_request(request)
    
    async def analysis(self, data: str, analysis_type: str = "", **kwargs) -> K2Response:
        """分析请求"""
        content = f"请进行{analysis_type}分析：\n{data}" if analysis_type else f"请分析以下内容：\n{data}"
        
        request = K2Request(
            request_id=str(uuid.uuid4()),
            request_type="analysis",
            content=content,
            context={"analysis_type": analysis_type},
            temperature=kwargs.get("temperature", 0.5),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=kwargs.get("stream", False)
        )
        
        return await self.route_ai_request(request)
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            test_request = K2Request(
                request_id="health_check",
                request_type="health_check",
                content="Hello, this is a health check.",
                max_tokens=10
            )
            
            response = await self.route_ai_request(test_request)
            self.last_health_check = datetime.now()
            
            return response.success
            
        except Exception as e:
            self.logger.error(f"K2 服务健康检查失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds()
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "success_rate": (self.stats["successful_requests"] / max(self.stats["total_requests"], 1)) * 100,
            "requests_per_minute": (self.stats["total_requests"] / max(uptime / 60, 1)),
            "connected": self.connected,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "config": {
                "url": self.config["url"],
                "model_id": self.config["model_id"],
                "enabled": self.config["enabled"]
            }
        }
    
    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的请求历史"""
        return self.request_history[-limit:] if self.request_history else []
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"更新 K2 配置: {key} = {value}")
    
    async def cleanup(self):
        """清理资源"""
        try:
            await self.http_client.aclose()
            self.connected = False
            self.logger.info("K2 服务客户端清理完成")
            
        except Exception as e:
            self.logger.error(f"K2 服务客户端清理失败: {e}")


# 全局 K2 客户端实例
k2_client = K2Client()


def get_k2_client() -> K2Client:
    """获取 K2 客户端实例"""
    return k2_client


# CLI 接口
if __name__ == "__main__":
    import argparse
    import sys
    
    async def main():
        parser = argparse.ArgumentParser(description="K2 服务客户端测试")
        parser.add_argument("--action", choices=["test", "health", "stats", "chat"], 
                           default="test", help="执行的动作")
        parser.add_argument("--prompt", type=str, default="Hello, how are you?", 
                           help="测试提示")
        parser.add_argument("--api-key", type=str, help="K2 API Key")
        
        args = parser.parse_args()
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        
        client = K2Client()
        
        if args.api_key:
            client.update_config(api_key=args.api_key)
        
        try:
            await client.initialize()
            
            if args.action == "test":
                print(f"🧪 测试 K2 文本生成: {args.prompt}")
                response = await client.text_generation(args.prompt)
                print(f"响应: {response.content}")
                print(f"成功: {response.success}")
                print(f"成本: ${response.cost:.4f}")
                print(f"响应时间: {response.response_time:.2f}s")
            
            elif args.action == "health":
                print("🔍 K2 服务健康检查...")
                healthy = await client.health_check()
                print(f"健康状态: {'✅ 正常' if healthy else '❌ 异常'}")
            
            elif args.action == "stats":
                print("📊 K2 客户端统计信息:")
                stats = client.get_stats()
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            
            elif args.action == "chat":
                print(f"💬 测试 K2 聊天: {args.prompt}")
                messages = [{"role": "user", "content": args.prompt}]
                response = await client.chat_completion(messages)
                print(f"响应: {response.content}")
                print(f"成功: {response.success}")
        
        finally:
            await client.cleanup()
    
    asyncio.run(main())

