#!/usr/bin/env python3
"""
Dialogue Collector - 自動收集 Claude Code 對話用於 K2 訓練
"""

import os
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import queue

class DialogueCollector(FileSystemEventHandler):
    def __init__(self, watch_path="/Users/alexchuang/Library/Application Support/Claude"):
        self.watch_path = Path(watch_path)
        self.data_dir = Path("/app/data") if os.path.exists("/app/data") else Path("./data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 創建數據庫
        self.db_path = self.data_dir / "dialogues.db"
        self.init_database()
        
        # 處理隊列
        self.process_queue = queue.Queue()
        self.start_processor()
        
        # 已處理文件記錄
        self.processed_files = set()
        self.load_processed_files()
        
    def init_database(self):
        """初始化對話數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dialogues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            conversation_id TEXT,
            turn_number INTEGER,
            role TEXT,
            content TEXT,
            intent TEXT,
            tools_used TEXT,
            model_mode TEXT,
            processed BOOLEAN DEFAULT FALSE
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_files (
            file_path TEXT PRIMARY KEY,
            processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
        
    def load_processed_files(self):
        """加載已處理的文件列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM processed_files")
        self.processed_files = {row[0] for row in cursor.fetchall()}
        conn.close()
        
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
            
        # 檢查是否為對話相關文件
        if self.is_dialogue_file(event.src_path):
            self.process_queue.put(event.src_path)
            
    def on_created(self, event):
        """文件創建事件"""
        if event.is_directory:
            return
            
        if self.is_dialogue_file(event.src_path):
            # 等待文件寫入完成
            time.sleep(0.5)
            self.process_queue.put(event.src_path)
            
    def is_dialogue_file(self, file_path):
        """檢查是否為對話文件"""
        path = Path(file_path)
        
        # Claude 對話文件特徵
        dialogue_patterns = [
            "conversation*.json",
            "chat*.json",
            "*messages*.json",
            "claude*.json"
        ]
        
        return any(path.match(pattern) for pattern in dialogue_patterns)
        
    def start_processor(self):
        """啟動處理線程"""
        def process_loop():
            while True:
                try:
                    file_path = self.process_queue.get(timeout=1)
                    if file_path and file_path not in self.processed_files:
                        self.process_dialogue_file(file_path)
                        self.processed_files.add(file_path)
                        self.mark_file_processed(file_path)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"處理錯誤: {e}")
                    
        thread = threading.Thread(target=process_loop, daemon=True)
        thread.start()
        
    def process_dialogue_file(self, file_path):
        """處理對話文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 提取對話信息
            conversation_id = data.get('conversation_id', str(file_path))
            messages = data.get('messages', [])
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for i, msg in enumerate(messages):
                # 解析消息
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                # 檢測 /model 命令
                model_mode = self.detect_model_command(content)
                
                # 檢測工具使用
                tools_used = self.detect_tools(content)
                
                # 預測意圖（簡化版）
                intent = self.predict_intent(content)
                
                # 插入數據庫
                cursor.execute("""
                INSERT INTO dialogues 
                (conversation_id, turn_number, role, content, intent, tools_used, model_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (conversation_id, i, role, content, intent, tools_used, model_mode))
                
            conn.commit()
            conn.close()
            
            print(f"✅ 收集了 {len(messages)} 條對話: {Path(file_path).name}")
            
        except Exception as e:
            print(f"處理文件失敗 {file_path}: {e}")
            
    def detect_model_command(self, content):
        """檢測模型切換命令"""
        if "/model k2" in content.lower():
            return "k2"
        elif "/model claude" in content.lower():
            return "claude"
        elif "/model hybrid" in content.lower():
            return "hybrid"
        return None
        
    def detect_tools(self, content):
        """檢測工具使用"""
        tools = []
        tool_keywords = {
            "read": ["讀取", "查看", "打開文件"],
            "write": ["寫入", "創建", "保存"],
            "edit": ["修改", "編輯", "更新"],
            "bash": ["執行", "運行", "command"],
            "search": ["搜索", "查找", "grep"]
        }
        
        content_lower = content.lower()
        for tool, keywords in tool_keywords.items():
            if any(kw in content_lower for kw in keywords):
                tools.append(tool)
                
        return ",".join(tools) if tools else None
        
    def predict_intent(self, content):
        """簡單的意圖預測"""
        intents = {
            "code_generation": ["寫", "創建", "實現", "生成"],
            "bug_fixing": ["修復", "錯誤", "bug", "問題"],
            "explanation": ["解釋", "說明", "什麼是", "為什麼"],
            "refactoring": ["重構", "優化", "改進"],
            "testing": ["測試", "驗證", "檢查"]
        }
        
        content_lower = content.lower()
        for intent, keywords in intents.items():
            if any(kw in content_lower for kw in keywords):
                return intent
                
        return "general"
        
    def mark_file_processed(self, file_path):
        """標記文件已處理"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO processed_files (file_path) VALUES (?)",
            (str(file_path),)
        )
        conn.commit()
        conn.close()
        
    def get_training_data(self, limit=100):
        """獲取用於訓練的數據"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT content, intent, tools_used, model_mode
        FROM dialogues
        WHERE role = 'user' AND processed = FALSE
        ORDER BY timestamp DESC
        LIMIT ?
        """, (limit,))
        
        data = cursor.fetchall()
        
        # 標記為已處理
        cursor.execute("""
        UPDATE dialogues
        SET processed = TRUE
        WHERE role = 'user' AND processed = FALSE
        ORDER BY timestamp DESC
        LIMIT ?
        """, (limit,))
        
        conn.commit()
        conn.close()
        
        return data
        
    def get_statistics(self):
        """獲取統計信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 總對話數
        cursor.execute("SELECT COUNT(DISTINCT conversation_id) FROM dialogues")
        stats['total_conversations'] = cursor.fetchone()[0]
        
        # 總消息數
        cursor.execute("SELECT COUNT(*) FROM dialogues")
        stats['total_messages'] = cursor.fetchone()[0]
        
        # 各意圖分布
        cursor.execute("""
        SELECT intent, COUNT(*) 
        FROM dialogues 
        WHERE role = 'user' 
        GROUP BY intent
        """)
        stats['intent_distribution'] = dict(cursor.fetchall())
        
        # 模型使用統計
        cursor.execute("""
        SELECT model_mode, COUNT(*) 
        FROM dialogues 
        WHERE model_mode IS NOT NULL 
        GROUP BY model_mode
        """)
        stats['model_usage'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
        
    def start_watching(self):
        """開始監控"""
        observer = Observer()
        observer.schedule(self, str(self.watch_path), recursive=True)
        observer.start()
        
        print(f"🔍 開始監控 Claude 對話: {self.watch_path}")
        print(f"💾 數據保存到: {self.db_path}")
        
        try:
            while True:
                time.sleep(1)
                # 定期顯示統計
                if int(time.time()) % 60 == 0:
                    stats = self.get_statistics()
                    print(f"📊 統計: {stats['total_conversations']} 對話, "
                          f"{stats['total_messages']} 消息")
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    # 支持 Docker 環境變量
    watch_path = os.environ.get('WATCH_PATH', 
                               '/Users/alexchuang/Library/Application Support/Claude')
    
    collector = DialogueCollector(watch_path)
    collector.start_watching()