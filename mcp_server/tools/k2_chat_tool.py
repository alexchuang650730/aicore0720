"""
K2聊天工具
集成Kimi K2模型，提供智能对话功能
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import httpx
import os

logger = logging.getLogger(__name__)

class K2ChatTool:
    """K2聊天工具类"""
    
    def __init__(self):
        """初始化K2聊天工具"""
        self.api_key = os.getenv("KIMI_API_KEY")
        self.api_url = "https://api.moonshot.cn/v1/chat/completions"
        self.model = "moonshot-v1-8k"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # 如果没有API密钥，创建模拟实现
        if not self.api_key:
            logger.warning("⚠️ 未找到KIMI_API_KEY，使用模拟实现")
            self._create_mock_implementation()
    
    def _create_mock_implementation(self):
        """创建模拟实现"""
        self.is_mock = True
        
        # 模拟响应模板
        self.mock_responses = {
            "代码": "我是K2模型，专门处理代码相关问题。请提供具体的代码需求，我会帮您分析和优化。",
            "UI": "我可以帮您设计和生成UI界面。请描述您需要的界面功能和样式要求。",
            "测试": "我可以帮您编写测试用例和自动化测试。请提供要测试的代码或功能。",
            "文档": "我可以帮您生成技术文档和API文档。请提供相关的代码或项目信息。",
            "分析": "我可以帮您分析代码结构、性能问题和优化建议。请提供需要分析的代码。",
            "default": "我是K2本地模型，支持中文对话。请告诉我您需要什么帮助？"
        }
    
    async def chat(self, message: str, context: List[str] = None, use_memory: bool = True) -> str:
        """
        与K2模型对话
        
        Args:
            message: 对话消息
            context: 上下文信息
            use_memory: 是否使用记忆增强
            
        Returns:
            K2模型的响应
        """
        try:
            logger.info(f"💬 K2对话: {message[:50]}...")
            
            # 如果是模拟实现
            if hasattr(self, 'is_mock') and self.is_mock:
                return await self._mock_chat(message, context, use_memory)
            
            # 构建消息
            messages = []
            
            # 添加系统提示
            messages.append({
                "role": "system",
                "content": "你是K2助手，专门为PowerAutomation工作流自动化提供支持。你可以帮助用户进行代码分析、UI设计、测试生成、文档编写等任务。"
            })
            
            # 添加上下文
            if context:
                context_content = "\\n".join(context)
                messages.append({
                    "role": "user",
                    "content": f"上下文信息：\\n{context_content}"
                })
            
            # 添加当前消息
            messages.append({
                "role": "user",
                "content": message
            })
            
            # 调用API
            response = await self._call_kimi_api(messages)
            
            # 记忆增强（如果需要）
            if use_memory:
                # 这里可以集成Memory RAG工具
                pass
            
            return response
            
        except Exception as e:
            logger.error(f"❌ K2对话失败: {e}")
            return f"❌ 对话失败: {str(e)}"
    
    async def _call_kimi_api(self, messages: List[Dict[str, str]]) -> str:
        """
        调用Kimi API
        
        Args:
            messages: 消息列表
            
        Returns:
            API响应
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                self.api_url,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Kimi API调用失败: {e}")
            raise
    
    async def _mock_chat(self, message: str, context: List[str] = None, use_memory: bool = True) -> str:
        """
        模拟对话实现
        
        Args:
            message: 对话消息
            context: 上下文信息
            use_memory: 是否使用记忆增强
            
        Returns:
            模拟响应
        """
        # 模拟处理时间
        await asyncio.sleep(0.1)
        
        # 根据消息内容选择响应
        message_lower = message.lower()
        
        # 关键词匹配
        for keyword, response in self.mock_responses.items():
            if keyword != "default" and keyword in message_lower:
                return f"{response}\\n\\n基于您的输入: {message}"
        
        # 默认响应
        return f"{self.mock_responses['default']}\\n\\n您的消息: {message}"
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息
        """
        return {
            "model": self.model,
            "api_url": self.api_url,
            "is_mock": hasattr(self, 'is_mock') and self.is_mock,
            "has_api_key": bool(self.api_key),
            "status": "available"
        }
    
    async def close(self):
        """关闭客户端"""
        if hasattr(self, 'client'):
            await self.client.aclose()