#!/usr/bin/env python3
"""
共享對話記憶系統 - ClaudeEditor 與 Claude Code Tool 的統一記憶
通過 Memory RAG 實現對話內容和學習經驗的持久化與共享
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib
from dataclasses import dataclass, asdict
import numpy as np
from collections import deque

@dataclass
class ConversationTurn:
    """對話回合"""
    id: str
    source: str  # "claude_code_tool" 或 "claudeditor"
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: str
    context: Dict[str, Any]  # 上下文信息
    embeddings: Optional[List[float]] = None

@dataclass
class MemoryEntry:
    """記憶條目"""
    id: str
    conversation_id: str
    summary: str
    keywords: List[str]
    learned_patterns: List[str]
    file_references: List[str]
    timestamp: str
    importance_score: float

class SharedConversationMemorySystem:
    """共享對話記憶系統"""
    
    def __init__(self):
        self.memory_path = Path.home() / ".powerautomation" / "shared_memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # 記憶存儲
        self.conversations_db = self.memory_path / "conversations.json"
        self.memory_db = self.memory_path / "memory_entries.json"
        self.embeddings_db = self.memory_path / "embeddings.npy"
        
        # 實時共享緩存
        self.active_conversation = None
        self.conversation_buffer = deque(maxlen=100)  # 最近100條對話
        self.learning_buffer = []  # 待學習的模式
        
        # 載入現有記憶
        self._load_memory()
        
    def _load_memory(self):
        """載入現有記憶"""
        self.conversations = {}
        self.memory_entries = {}
        self.embeddings = {}
        
        if self.conversations_db.exists():
            with open(self.conversations_db, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.conversations = {k: [ConversationTurn(**turn) for turn in v] 
                                    for k, v in data.items()}
                
        if self.memory_db.exists():
            with open(self.memory_db, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.memory_entries = {k: MemoryEntry(**v) for k, v in data.items()}
                
        if self.embeddings_db.exists():
            self.embeddings = np.load(self.embeddings_db, allow_pickle=True).item()
            
    def _save_memory(self):
        """保存記憶到磁盤"""
        # 保存對話
        conversations_data = {
            k: [asdict(turn) for turn in v] 
            for k, v in self.conversations.items()
        }
        with open(self.conversations_db, 'w', encoding='utf-8') as f:
            json.dump(conversations_data, f, ensure_ascii=False, indent=2)
            
        # 保存記憶條目
        memory_data = {k: asdict(v) for k, v in self.memory_entries.items()}
        with open(self.memory_db, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
        # 保存嵌入向量
        np.save(self.embeddings_db, self.embeddings)
        
    async def add_conversation_turn(self, 
                                  source: str,
                                  role: str,
                                  content: str,
                                  context: Optional[Dict[str, Any]] = None) -> str:
        """添加對話回合 - 支持實時同步"""
        turn_id = self._generate_id(f"{source}_{role}_{content}")
        
        turn = ConversationTurn(
            id=turn_id,
            source=source,
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            context=context or {}
        )
        
        # 添加到當前對話
        if not self.active_conversation:
            self.active_conversation = self._generate_id(f"conversation_{datetime.now()}")
            self.conversations[self.active_conversation] = []
            
        self.conversations[self.active_conversation].append(turn)
        self.conversation_buffer.append(turn)
        
        # 實時廣播到其他組件
        await self._broadcast_conversation_update(turn)
        
        # 觸發學習流程
        if len(self.conversation_buffer) % 10 == 0:  # 每10條對話觸發一次
            await self._trigger_learning()
            
        # 保存到磁盤
        self._save_memory()
        
        return turn_id
        
    async def _broadcast_conversation_update(self, turn: ConversationTurn):
        """廣播對話更新到 ClaudeEditor 和 Claude Code Tool"""
        update_message = {
            "type": "conversation_update",
            "turn": asdict(turn),
            "conversation_id": self.active_conversation,
            "timestamp": datetime.now().isoformat()
        }
        
        # 發送到 ClaudeEditor WebSocket
        await self._send_to_claudeditor(update_message)
        
        # 更新 Claude Code Tool 共享內存
        await self._update_claude_tool_memory(update_message)
        
    async def _send_to_claudeditor(self, message: Dict[str, Any]):
        """發送消息到 ClaudeEditor"""
        try:
            import websockets
            async with websockets.connect("ws://localhost:8081/ws") as websocket:
                await websocket.send(json.dumps(message))
        except Exception as e:
            print(f"⚠️ 無法發送到 ClaudeEditor: {e}")
            
    async def _update_claude_tool_memory(self, message: Dict[str, Any]):
        """更新 Claude Code Tool 的共享內存"""
        shared_memory_file = Path.home() / ".claude-code" / "shared_memory.json"
        shared_memory_file.parent.mkdir(exist_ok=True)
        
        try:
            existing = {}
            if shared_memory_file.exists():
                with open(shared_memory_file, 'r') as f:
                    existing = json.load(f)
                    
            existing["last_update"] = message
            existing["conversation_buffer"] = [asdict(t) for t in self.conversation_buffer]
            
            with open(shared_memory_file, 'w') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 無法更新 Claude Tool 記憶: {e}")
            
    async def search_memory(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相關記憶"""
        # 生成查詢嵌入
        query_embedding = await self._generate_embedding(query)
        
        # 計算相似度
        similarities = []
        for mem_id, memory_entry in self.memory_entries.items():
            if mem_id in self.embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, 
                    self.embeddings[mem_id]
                )
                similarities.append((similarity, memory_entry))
                
        # 排序並返回 top_k
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, memory in similarities[:top_k]:
            # 獲取相關對話上下文
            conversation = self.conversations.get(memory.conversation_id, [])
            context_turns = [asdict(turn) for turn in conversation[-5:]]  # 最近5條
            
            results.append({
                "memory": asdict(memory),
                "relevance_score": score,
                "context": context_turns,
                "source_files": memory.file_references
            })
            
        return results
        
    async def _trigger_learning(self):
        """觸發學習流程 - 從對話中提取模式和知識"""
        print("🧠 觸發 Memory RAG 學習流程...")
        
        # 分析最近的對話
        recent_turns = list(self.conversation_buffer)[-20:]  # 最近20條
        
        # 提取模式
        patterns = await self._extract_patterns(recent_turns)
        
        # 提取關鍵詞
        keywords = await self._extract_keywords(recent_turns)
        
        # 生成摘要
        summary = await self._generate_summary(recent_turns)
        
        # 識別相關文件
        file_refs = self._extract_file_references(recent_turns)
        
        # 計算重要性分數
        importance = self._calculate_importance(patterns, keywords, file_refs)
        
        # 創建記憶條目
        memory_id = self._generate_id(f"memory_{datetime.now()}")
        memory = MemoryEntry(
            id=memory_id,
            conversation_id=self.active_conversation,
            summary=summary,
            keywords=keywords,
            learned_patterns=patterns,
            file_references=file_refs,
            timestamp=datetime.now().isoformat(),
            importance_score=importance
        )
        
        # 生成並存儲嵌入
        embedding = await self._generate_embedding(summary)
        self.embeddings[memory_id] = embedding
        
        # 保存記憶
        self.memory_entries[memory_id] = memory
        self._save_memory()
        
        print(f"✅ 學習完成，新增記憶: {memory_id}")
        
    async def _extract_patterns(self, turns: List[ConversationTurn]) -> List[str]:
        """提取對話模式"""
        patterns = []
        
        # 提取常見的命令模式
        commands = [t.content for t in turns if t.role == "user"]
        for cmd in commands:
            if cmd.startswith("/"):
                patterns.append(f"command_pattern:{cmd.split()[0]}")
                
        # 提取問答模式
        for i in range(len(turns) - 1):
            if turns[i].role == "user" and turns[i+1].role == "assistant":
                if "如何" in turns[i].content or "how to" in turns[i].content.lower():
                    patterns.append("qa_pattern:how_to")
                elif "為什麼" in turns[i].content or "why" in turns[i].content.lower():
                    patterns.append("qa_pattern:why")
                    
        return list(set(patterns))  # 去重
        
    async def _extract_keywords(self, turns: List[ConversationTurn]) -> List[str]:
        """提取關鍵詞"""
        # 簡單實現，實際可以使用 NLP 模型
        keywords = []
        
        # 技術關鍵詞
        tech_keywords = [
            "react", "python", "javascript", "api", "database",
            "deployment", "docker", "kubernetes", "測試", "部署"
        ]
        
        all_content = " ".join([t.content for t in turns])
        all_content_lower = all_content.lower()
        
        for keyword in tech_keywords:
            if keyword in all_content_lower:
                keywords.append(keyword)
                
        return keywords
        
    async def _generate_summary(self, turns: List[ConversationTurn]) -> str:
        """生成對話摘要"""
        # 簡單實現，實際可以使用 LLM
        user_intents = []
        assistant_actions = []
        
        for turn in turns:
            if turn.role == "user":
                # 提取用戶意圖
                if len(turn.content) < 100:
                    user_intents.append(turn.content)
            else:
                # 提取助手動作
                if "created" in turn.content or "生成" in turn.content:
                    assistant_actions.append("file_creation")
                elif "fixed" in turn.content or "修復" in turn.content:
                    assistant_actions.append("bug_fix")
                elif "deployed" in turn.content or "部署" in turn.content:
                    assistant_actions.append("deployment")
                    
        summary = f"用戶意圖: {', '.join(user_intents[:3])}; "
        summary += f"執行動作: {', '.join(set(assistant_actions))}"
        
        return summary
        
    def _extract_file_references(self, turns: List[ConversationTurn]) -> List[str]:
        """提取文件引用"""
        file_refs = []
        
        for turn in turns:
            # 從上下文中提取
            if "files" in turn.context:
                file_refs.extend(turn.context["files"])
                
            # 從內容中提取文件路徑
            import re
            # 匹配常見文件路徑模式
            paths = re.findall(r'[./\w-]+\.\w+', turn.content)
            file_refs.extend(paths)
            
        return list(set(file_refs))  # 去重
        
    def _calculate_importance(self, patterns: List[str], 
                            keywords: List[str], 
                            file_refs: List[str]) -> float:
        """計算重要性分數"""
        # 基於多個因素計算
        pattern_score = len(patterns) * 0.3
        keyword_score = len(keywords) * 0.3
        file_score = len(file_refs) * 0.4
        
        total_score = pattern_score + keyword_score + file_score
        
        # 標準化到 0-1
        return min(total_score / 10, 1.0)
        
    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        # 簡單實現，實際應使用嵌入模型
        # 這裡用哈希模擬
        hash_val = hashlib.sha256(text.encode()).hexdigest()
        # 轉換為固定長度的向量
        embedding = [int(hash_val[i:i+2], 16) / 255.0 for i in range(0, 64, 2)]
        return embedding[:32]  # 返回32維向量
        
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """計算餘弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
        
    def _generate_id(self, content: str) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{content}_{datetime.now()}".encode()).hexdigest()[:16]
        
    async def get_context_for_tool(self, tool_name: str) -> Dict[str, Any]:
        """為特定工具獲取上下文"""
        # 搜索相關記憶
        relevant_memories = await self.search_memory(tool_name, top_k=3)
        
        # 獲取最近的對話
        recent_conversation = [asdict(t) for t in list(self.conversation_buffer)[-10:]]
        
        return {
            "tool": tool_name,
            "relevant_memories": relevant_memories,
            "recent_conversation": recent_conversation,
            "active_files": self._get_active_files(),
            "learned_preferences": self._get_user_preferences()
        }
        
    def _get_active_files(self) -> List[str]:
        """獲取當前活躍的文件"""
        files = []
        for turn in self.conversation_buffer:
            if "files" in turn.context:
                files.extend(turn.context["files"])
        return list(set(files))[-10:]  # 最近10個不重複文件
        
    def _get_user_preferences(self) -> Dict[str, Any]:
        """獲取學習到的用戶偏好"""
        preferences = {
            "language": "zh_TW",  # 從對話中檢測
            "framework_preferences": [],
            "coding_style": [],
            "common_commands": []
        }
        
        # 分析對話提取偏好
        for memory in self.memory_entries.values():
            for keyword in memory.keywords:
                if keyword in ["react", "vue", "angular"]:
                    preferences["framework_preferences"].append(keyword)
                    
        return preferences


# 單例實例
shared_memory = SharedConversationMemorySystem()


async def sync_conversation(source: str, role: str, content: str, context: Dict = None):
    """同步對話的便捷函數"""
    return await shared_memory.add_conversation_turn(source, role, content, context)


async def search_relevant_memory(query: str) -> List[Dict[str, Any]]:
    """搜索相關記憶的便捷函數"""
    return await shared_memory.search_memory(query)