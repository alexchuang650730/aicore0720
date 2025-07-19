#!/usr/bin/env python3
"""
Claude 實時對話數據收集器
在當前對話中即時收集訓練數據
"""

import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """對話回合"""
    role: str  # user or assistant
    content: str
    timestamp: str
    metadata: Dict[str, Any] = None
    tools_used: List[str] = None
    thinking_process: str = None

@dataclass
class ConversationSession:
    """對話會話"""
    session_id: str
    start_time: str
    end_time: str = None
    turns: List[ConversationTurn] = None
    context: Dict[str, Any] = None
    summary: str = None
    quality_score: float = None

class ClaudeLiveCollector:
    """Claude 實時數據收集器"""
    
    def __init__(self):
        # 使用絕對路徑
        base_dir = Path(__file__).parent.parent.parent.parent
        self.data_dir = base_dir / "data/claude_conversations"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None
        self.sessions = []
        
        # 載入已有數據
        self.load_existing_data()
        
        # 啟動當前會話
        self.start_new_session()
        
    def load_existing_data(self):
        """載入已有的訓練數據"""
        try:
            data_file = self.data_dir / "claude_conversations.json"
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = [
                        ConversationSession(**session) for session in data.get("sessions", [])
                    ]
                logger.info(f"載入了 {len(self.sessions)} 個歷史會話")
        except Exception as e:
            logger.error(f"載入數據失敗: {str(e)}")
    
    def start_session(self, context: Dict[str, Any] = None) -> str:
        """開始新的收集會話"""
        session_id = f"claude_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = ConversationSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            turns=[],
            context=context or {
                "platform": "ClaudeEditor",
                "version": "4.74",
                "purpose": "training_data_collection"
            }
        )
        
        logger.info(f"開始新會話: {session_id}")
        return session_id
    
    def add_turn(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """添加對話回合"""
        if not self.current_session:
            self.start_session()
        
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {},
            tools_used=self._extract_tools_from_content(content),
            thinking_process=self._extract_thinking_from_content(content)
        )
        
        self.current_session.turns.append(turn)
        logger.info(f"添加 {role} 回合，長度: {len(content)} 字符")
        
        # 自動保存
        self.save_current_session()
    
    def _extract_tools_from_content(self, content: str) -> List[str]:
        """從內容中提取使用的工具"""
        tools = []
        tool_keywords = {
            "Read": ["讀取", "查看", "檢查文件"],
            "Write": ["創建", "寫入", "生成文件"],
            "Edit": ["修改", "編輯", "更新"],
            "Bash": ["執行", "運行命令", "bash"],
            "WebFetch": ["獲取網頁", "抓取"],
            "Task": ["任務", "搜索"],
            "TodoWrite": ["待辦", "任務列表"]
        }
        
        for tool, keywords in tool_keywords.items():
            if any(keyword in content for keyword in keywords):
                tools.append(tool)
        
        return tools
    
    def _extract_thinking_from_content(self, content: str) -> Optional[str]:
        """提取思考過程"""
        thinking_patterns = [
            "我需要", "我會", "首先", "然後", "接下來",
            "讓我", "我來", "分析", "理解", "考慮"
        ]
        
        for pattern in thinking_patterns:
            if pattern in content:
                # 提取包含思考模式的句子
                sentences = content.split('。')
                for sentence in sentences:
                    if pattern in sentence:
                        return sentence.strip()
        
        return None
    
    def end_session(self, summary: str = None, quality_score: float = None):
        """結束當前會話"""
        if not self.current_session:
            logger.warning("沒有活動的會話")
            return
        
        self.current_session.end_time = datetime.now().isoformat()
        self.current_session.summary = summary
        self.current_session.quality_score = quality_score
        
        # 添加到會話列表
        self.sessions.append(self.current_session)
        
        # 保存所有數據
        self.save_all_data()
        
        logger.info(f"結束會話: {self.current_session.session_id}")
        self.current_session = None
    
    def save_current_session(self):
        """保存當前會話（增量保存）"""
        if not self.current_session:
            return
        
        session_file = self.data_dir / f"{self.current_session.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.current_session), f, ensure_ascii=False, indent=2)
    
    def save_all_data(self):
        """保存所有數據"""
        data_file = self.data_dir / "claude_conversations.json"
        
        data = {
            "metadata": {
                "total_sessions": len(self.sessions),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            },
            "sessions": [asdict(session) for session in self.sessions]
        }
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存了 {len(self.sessions)} 個會話數據")
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        total_turns = sum(len(session.turns) for session in self.sessions)
        total_user_turns = sum(
            len([t for t in session.turns if t.role == "user"]) 
            for session in self.sessions
        )
        total_assistant_turns = sum(
            len([t for t in session.turns if t.role == "assistant"]) 
            for session in self.sessions
        )
        
        # 工具使用統計
        tool_usage = {}
        for session in self.sessions:
            for turn in session.turns:
                if turn.tools_used:
                    for tool in turn.tools_used:
                        tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        return {
            "total_sessions": len(self.sessions),
            "total_turns": total_turns,
            "user_turns": total_user_turns,
            "assistant_turns": total_assistant_turns,
            "avg_turns_per_session": total_turns / len(self.sessions) if self.sessions else 0,
            "tool_usage": tool_usage,
            "last_session": self.sessions[-1].session_id if self.sessions else None
        }
    
    def export_for_training(self, output_format: str = "jsonl") -> Path:
        """導出訓練數據"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format == "jsonl":
            # 導出為 JSONL 格式（用於微調）
            output_file = self.data_dir / f"claude_training_{timestamp}.jsonl"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for session in self.sessions:
                    for i in range(0, len(session.turns) - 1, 2):
                        if (i + 1 < len(session.turns) and 
                            session.turns[i].role == "user" and 
                            session.turns[i + 1].role == "assistant"):
                            
                            conversation = {
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": session.turns[i].content
                                    },
                                    {
                                        "role": "assistant",
                                        "content": session.turns[i + 1].content
                                    }
                                ],
                                "metadata": {
                                    "session_id": session.session_id,
                                    "timestamp": session.turns[i].timestamp,
                                    "tools_used": session.turns[i + 1].tools_used
                                }
                            }
                            f.write(json.dumps(conversation, ensure_ascii=False) + '\n')
        
        elif output_format == "json":
            # 導出為結構化 JSON
            output_file = self.data_dir / f"claude_training_{timestamp}.json"
            
            training_data = {
                "metadata": self.get_statistics(),
                "conversations": []
            }
            
            for session in self.sessions:
                for i in range(0, len(session.turns) - 1, 2):
                    if (i + 1 < len(session.turns) and 
                        session.turns[i].role == "user" and 
                        session.turns[i + 1].role == "assistant"):
                        
                        training_data["conversations"].append({
                            "input": session.turns[i].content,
                            "output": session.turns[i + 1].content,
                            "context": session.context,
                            "tools": session.turns[i + 1].tools_used,
                            "thinking": session.turns[i + 1].thinking_process
                        })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"導出訓練數據: {output_file}")
        return output_file


# 全局收集器實例
collector = ClaudeLiveCollector()

def start_collection(context: Dict[str, Any] = None):
    """開始收集"""
    return collector.start_session(context)

def collect_user_input(content: str, metadata: Dict[str, Any] = None):
    """收集用戶輸入"""
    collector.add_turn("user", content, metadata)

def collect_assistant_response(content: str, metadata: Dict[str, Any] = None):
    """收集助手回應"""
    collector.add_turn("assistant", content, metadata)

def end_collection(summary: str = None, quality_score: float = None):
    """結束收集"""
    collector.end_session(summary, quality_score)

def get_collection_stats():
    """獲取收集統計"""
    return collector.get_statistics()

def export_training_data(format: str = "jsonl"):
    """導出訓練數據"""
    return collector.export_for_training(format)


# 命令行接口
if __name__ == "__main__":
    print("🚀 Claude 實時對話數據收集器")
    print("="*50)
    
    # 顯示統計
    stats = get_collection_stats()
    print(f"已收集會話: {stats['total_sessions']}")
    print(f"總對話回合: {stats['total_turns']}")
    print(f"工具使用統計: {stats['tool_usage']}")
    
    # 選項
    print("\n選項:")
    print("1. 開始新的收集會話")
    print("2. 導出訓練數據 (JSONL)")
    print("3. 導出訓練數據 (JSON)")
    print("4. 查看詳細統計")
    
    choice = input("\n請選擇 (1-4): ")
    
    if choice == "1":
        session_id = start_collection()
        print(f"✅ 已開始新會話: {session_id}")
        print("現在可以開始收集對話數據了！")
    
    elif choice == "2":
        file_path = export_training_data("jsonl")
        print(f"✅ 已導出 JSONL 訓練數據: {file_path}")
    
    elif choice == "3":
        file_path = export_training_data("json")
        print(f"✅ 已導出 JSON 訓練數據: {file_path}")
    
    elif choice == "4":
        print("\n詳細統計:")
        print(json.dumps(stats, ensure_ascii=False, indent=2))