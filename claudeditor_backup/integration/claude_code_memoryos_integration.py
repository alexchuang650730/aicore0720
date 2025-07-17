#!/usr/bin/env python3
"""
Claude Code 与 MemoryOS MCP 集成配置
确保 Claude Code 可以使用 MemoryOS 存储和检索数据
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.components.memoryos_mcp.memory_engine import MemoryEngine, Memory, MemoryType
from core.components.memoryos_mcp.api_server import MemoryOSAPIServer
from core.components.memoryos_mcp.context_manager import ContextManager

logger = logging.getLogger(__name__)

class ClaudeCodeMemoryOSIntegration:
    """Claude Code 与 MemoryOS 集成管理器"""
    
    def __init__(self, memory_db_path: str = "~/.powerautomation/memory/claude_code.db"):
        """初始化集成管理器"""
        self.memory_db_path = Path(memory_db_path).expanduser()
        self.memory_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化 MemoryOS 组件
        self.memory_engine = MemoryEngine(str(self.memory_db_path))
        self.context_manager = ContextManager(self.memory_engine)
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        
    async def initialize(self):
        """初始化内存系统"""
        try:
            await self.memory_engine.initialize()
            await self.context_manager.initialize()
            logger.info("✅ MemoryOS 集成初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ MemoryOS 集成初始化失败: {e}")
            return False
    
    async def store_claude_interaction(self, user_input: str, claude_response: str, 
                                     metadata: Dict[str, Any] = None) -> str:
        """存储 Claude Code 交互记录"""
        if metadata is None:
            metadata = {}
            
        # 添加交互元数据
        metadata.update({
            "source": "claude_code",
            "interaction_type": "command_execution",
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # 创建记忆项目
        memory_content = {
            "user_input": user_input,
            "claude_response": claude_response,
            "metadata": metadata
        }
        
        memory_id = await self.memory_engine.store_memory(
            memory_type=MemoryType.CLAUDE_INTERACTION,
            content=json.dumps(memory_content),
            metadata=metadata,
            tags=["claude_code", "interaction"]
        )
        
        logger.info(f"✅ 存储 Claude Code 交互: {memory_id}")
        return memory_id
    
    async def retrieve_relevant_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """检索相关上下文"""
        try:
            memories = await self.memory_engine.search_memories(
                query=query,
                memory_types=[MemoryType.CLAUDE_INTERACTION, MemoryType.SEMANTIC],
                limit=limit
            )
            
            context_data = []
            for memory in memories:
                try:
                    content = json.loads(memory.content)
                    context_data.append({
                        "id": memory.id,
                        "content": content,
                        "metadata": memory.metadata,
                        "created_at": memory.created_at,
                        "importance_score": memory.importance_score
                    })
                except json.JSONDecodeError:
                    # 处理非 JSON 内容
                    context_data.append({
                        "id": memory.id,
                        "content": {"text": memory.content},
                        "metadata": memory.metadata,
                        "created_at": memory.created_at,
                        "importance_score": memory.importance_score
                    })
            
            logger.info(f"✅ 检索到 {len(context_data)} 条相关上下文")
            return context_data
            
        except Exception as e:
            logger.error(f"❌ 检索上下文失败: {e}")
            return []
    
    async def store_user_preference(self, preference_key: str, preference_value: Any) -> str:
        """存储用户偏好"""
        metadata = {
            "preference_key": preference_key,
            "source": "claude_code",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        memory_id = await self.memory_engine.store_memory(
            memory_type=MemoryType.USER_PREFERENCE,
            content=json.dumps({"key": preference_key, "value": preference_value}),
            metadata=metadata,
            tags=["user_preference", "claude_code"]
        )
        
        logger.info(f"✅ 存储用户偏好: {preference_key}")
        return memory_id
    
    async def get_user_preference(self, preference_key: str) -> Optional[Any]:
        """获取用户偏好"""
        try:
            memories = await self.memory_engine.search_memories(
                query=preference_key,
                memory_types=[MemoryType.USER_PREFERENCE],
                limit=1
            )
            
            if memories:
                content = json.loads(memories[0].content)
                return content.get("value")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取用户偏好失败: {e}")
            return None
    
    async def store_project_context(self, project_path: str, context_data: Dict[str, Any]) -> str:
        """存储项目上下文"""
        metadata = {
            "project_path": project_path,
            "source": "claude_code",
            "context_type": "project",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        memory_id = await self.memory_engine.store_memory(
            memory_type=MemoryType.SEMANTIC,
            content=json.dumps(context_data),
            metadata=metadata,
            tags=["project_context", "claude_code", os.path.basename(project_path)]
        )
        
        logger.info(f"✅ 存储项目上下文: {project_path}")
        return memory_id
    
    async def get_project_context(self, project_path: str) -> Optional[Dict[str, Any]]:
        """获取项目上下文"""
        try:
            memories = await self.memory_engine.search_memories(
                query=f"project_path:{project_path}",
                memory_types=[MemoryType.SEMANTIC],
                limit=1
            )
            
            if memories:
                return json.loads(memories[0].content)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取项目上下文失败: {e}")
            return None
    
    async def cleanup_old_memories(self, days_old: int = 30):
        """清理旧记忆"""
        try:
            cleaned_count = await self.memory_engine.cleanup_old_memories(days_old)
            logger.info(f"✅ 清理了 {cleaned_count} 条旧记忆")
            return cleaned_count
        except Exception as e:
            logger.error(f"❌ 清理旧记忆失败: {e}")
            return 0

# 全局集成实例
_integration_instance = None

async def get_memoryos_integration() -> ClaudeCodeMemoryOSIntegration:
    """获取 MemoryOS 集成实例"""
    global _integration_instance
    
    if _integration_instance is None:
        _integration_instance = ClaudeCodeMemoryOSIntegration()
        await _integration_instance.initialize()
    
    return _integration_instance

# 便捷函数
async def store_interaction(user_input: str, claude_response: str, metadata: Dict[str, Any] = None) -> str:
    """存储交互记录的便捷函数"""
    integration = await get_memoryos_integration()
    return await integration.store_claude_interaction(user_input, claude_response, metadata)

async def get_context(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """获取上下文的便捷函数"""
    integration = await get_memoryos_integration()
    return await integration.retrieve_relevant_context(query, limit)

async def store_preference(key: str, value: Any) -> str:
    """存储偏好的便捷函数"""
    integration = await get_memoryos_integration()
    return await integration.store_user_preference(key, value)

async def get_preference(key: str) -> Optional[Any]:
    """获取偏好的便捷函数"""
    integration = await get_memoryos_integration()
    return await integration.get_user_preference(key)

if __name__ == "__main__":
    async def test_integration():
        """测试集成功能"""
        print("🧪 测试 Claude Code MemoryOS 集成...")
        
        integration = await get_memoryos_integration()
        
        # 测试存储交互
        memory_id = await store_interaction(
            "git status",
            "On branch main\nnothing to commit, working tree clean",
            {"command_type": "git", "success": True}
        )
        print(f"✅ 存储交互记录: {memory_id}")
        
        # 测试检索上下文
        context = await get_context("git status")
        print(f"✅ 检索到上下文: {len(context)} 条")
        
        # 测试用户偏好
        await store_preference("default_editor", "vscode")
        editor = await get_preference("default_editor")
        print(f"✅ 用户偏好: {editor}")
        
        print("🎉 集成测试完成！")
    
    asyncio.run(test_integration())

