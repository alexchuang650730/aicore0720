#!/usr/bin/env python3
"""
Claude 集成模塊
實現與 Claude 對話的深度集成，支持實時啟動和數據收集
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import subprocess
import threading
import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeIntegration:
    """Claude 深度集成"""
    
    def __init__(self):
        self.is_active = False
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.collectors = []
        self.current_session = None
        self.claudeditor_process = None
        
        # 集成配置
        self.config = {
            "auto_launch": True,
            "collect_data": True,
            "sync_state": True,
            "hot_reload": True,
            "smart_suggestions": True
        }
        
        # 狀態同步
        self.state = {
            "current_file": None,
            "current_task": None,
            "open_panels": [],
            "recent_actions": []
        }
        
    def enable_integration(self):
        """啟用 Claude 集成"""
        logger.info("🔗 啟用 Claude 集成...")
        
        # 設置環境變量
        os.environ["CLAUDE_INTEGRATION_ENABLED"] = "true"
        os.environ["CLAUDE_DATA_COLLECTION"] = "true"
        
        # 啟動監聽線程
        listener_thread = threading.Thread(
            target=self._message_listener,
            daemon=True
        )
        listener_thread.start()
        
        # 啟動數據收集器
        if self.config["collect_data"]:
            self._start_data_collectors()
        
        self.is_active = True
        logger.info("✅ Claude 集成已啟用")
    
    def _message_listener(self):
        """消息監聽器"""
        while self.is_active:
            try:
                # 從隊列獲取消息
                if not self.message_queue.empty():
                    message = self.message_queue.get()
                    self._process_claude_message(message)
            except Exception as e:
                logger.error(f"消息處理錯誤: {str(e)}")
            
            # 短暫休眠避免CPU占用過高
            threading.Event().wait(0.1)
    
    def _process_claude_message(self, message: Dict[str, Any]):
        """處理 Claude 消息"""
        msg_type = message.get("type")
        content = message.get("content", "")
        
        # 記錄到當前會話
        if self.current_session:
            self.current_session["messages"].append({
                "timestamp": datetime.now().isoformat(),
                "type": msg_type,
                "content": content
            })
        
        # 檢查是否需要啟動 ClaudeEditor
        if self.config["auto_launch"] and self._should_launch(content):
            self._launch_claudeditor_async()
        
        # 同步狀態
        if self.config["sync_state"] and self.claudeditor_process:
            self._sync_with_claudeditor(message)
    
    def _should_launch(self, content: str) -> bool:
        """判斷是否需要啟動 ClaudeEditor"""
        launch_indicators = [
            "寫代碼", "創建", "編輯", "修改",
            "設計", "界面", "組件", "測試",
            "部署", "運行", "調試", "檢查"
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in launch_indicators)
    
    def _launch_claudeditor_async(self):
        """異步啟動 ClaudeEditor"""
        if self.claudeditor_process and self.claudeditor_process.poll() is None:
            logger.info("ClaudeEditor 已在運行")
            return
        
        logger.info("🚀 自動啟動 ClaudeEditor...")
        
        try:
            # 創建啟動配置
            launch_config = {
                "mode": "integrated",
                "claude_session": self.current_session["id"] if self.current_session else None,
                "auto_sync": True,
                "features": self._detect_required_features()
            }
            
            # 保存配置
            config_file = Path("claude_integration_config.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(launch_config, f, ensure_ascii=False, indent=2)
            
            # 啟動 ClaudeEditor
            self.claudeditor_process = subprocess.Popen([
                "bash", "start_claudeditor.sh"
            ], env={
                **os.environ,
                "CLAUDE_INTEGRATION": "true",
                "INTEGRATION_CONFIG": str(config_file)
            })
            
            logger.info("✅ ClaudeEditor 已啟動並集成")
            
        except Exception as e:
            logger.error(f"啟動失敗: {str(e)}")
    
    def _detect_required_features(self) -> List[str]:
        """檢測需要的功能"""
        features = []
        
        # 根據最近的動作檢測
        recent_keywords = " ".join(self.state["recent_actions"][-5:])
        
        if any(kw in recent_keywords for kw in ["代碼", "function", "class", "api"]):
            features.append("code_editor")
        
        if any(kw in recent_keywords for kw in ["界面", "ui", "組件", "design"]):
            features.append("ui_designer")
        
        if any(kw in recent_keywords for kw in ["測試", "test", "檢查"]):
            features.append("test_runner")
        
        if any(kw in recent_keywords for kw in ["部署", "deploy", "發布"]):
            features.append("deployment")
        
        return features
    
    def _sync_with_claudeditor(self, message: Dict[str, Any]):
        """與 ClaudeEditor 同步狀態"""
        sync_data = {
            "timestamp": datetime.now().isoformat(),
            "claude_message": message,
            "current_state": self.state,
            "action": "sync"
        }
        
        # 通過 IPC 或 API 發送同步數據
        try:
            # 這裡應該使用實際的 IPC 機制
            sync_file = Path("/tmp/claude_editor_sync.json")
            with open(sync_file, 'w', encoding='utf-8') as f:
                json.dump(sync_data, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"同步失敗: {str(e)}")
    
    def _start_data_collectors(self):
        """啟動數據收集器"""
        # Claude 對話收集器
        claude_collector = threading.Thread(
            target=self._collect_claude_data,
            daemon=True
        )
        claude_collector.start()
        self.collectors.append(claude_collector)
        
        # ClaudeEditor 操作收集器
        editor_collector = threading.Thread(
            target=self._collect_editor_data,
            daemon=True
        )
        editor_collector.start()
        self.collectors.append(editor_collector)
        
        logger.info("📊 數據收集器已啟動")
    
    def _collect_claude_data(self):
        """收集 Claude 對話數據"""
        data_dir = Path("training_data/claude_integration")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        while self.is_active:
            if self.current_session and len(self.current_session["messages"]) > 0:
                # 保存當前會話
                session_file = data_dir / f"session_{self.current_session['id']}.json"
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_session, f, ensure_ascii=False, indent=2)
            
            # 每分鐘保存一次
            threading.Event().wait(60)
    
    def _collect_editor_data(self):
        """收集 ClaudeEditor 操作數據"""
        data_dir = Path("training_data/editor_actions")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        action_log = []
        
        while self.is_active:
            # 監控 ClaudeEditor 日志
            log_file = Path("logs/claudeditor_actions.log")
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        # 讀取新的操作
                        new_actions = f.readlines()
                        for action in new_actions:
                            if action.strip():
                                action_data = {
                                    "timestamp": datetime.now().isoformat(),
                                    "action": action.strip(),
                                    "session": self.current_session["id"] if self.current_session else None
                                }
                                action_log.append(action_data)
                        
                        # 定期保存
                        if len(action_log) >= 100:
                            log_file = data_dir / f"actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
                            with open(log_file, 'a', encoding='utf-8') as f:
                                for item in action_log:
                                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                            action_log.clear()
                
                except Exception as e:
                    logger.error(f"收集操作數據失敗: {str(e)}")
            
            threading.Event().wait(5)
    
    def start_session(self, session_id: Optional[str] = None):
        """開始新的集成會話"""
        self.current_session = {
            "id": session_id or f"claude_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "messages": [],
            "state_history": [],
            "features_used": set()
        }
        
        logger.info(f"開始集成會話: {self.current_session['id']}")
    
    def end_session(self):
        """結束當前會話"""
        if not self.current_session:
            return
        
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["features_used"] = list(self.current_session["features_used"])
        
        # 保存完整會話
        session_file = Path(f"training_data/sessions/{self.current_session['id']}_complete.json")
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_session, f, ensure_ascii=False, indent=2)
        
        logger.info(f"會話結束: {self.current_session['id']}")
        self.current_session = None
    
    def send_to_claudeditor(self, command: str, params: Dict[str, Any] = None):
        """發送命令到 ClaudeEditor"""
        if not self.claudeditor_process or self.claudeditor_process.poll() is not None:
            logger.warning("ClaudeEditor 未運行")
            return
        
        command_data = {
            "command": command,
            "params": params or {},
            "timestamp": datetime.now().isoformat(),
            "from": "claude_integration"
        }
        
        # 通過 API 或 IPC 發送
        try:
            # 這裡應該使用實際的通信機制
            cmd_file = Path("/tmp/claudeditor_command.json")
            with open(cmd_file, 'w', encoding='utf-8') as f:
                json.dump(command_data, f, ensure_ascii=False)
            
            logger.info(f"發送命令到 ClaudeEditor: {command}")
            
        except Exception as e:
            logger.error(f"發送命令失敗: {str(e)}")
    
    def get_claudeditor_state(self) -> Optional[Dict[str, Any]]:
        """獲取 ClaudeEditor 當前狀態"""
        try:
            state_file = Path("/tmp/claudeditor_state.json")
            if state_file.exists():
                with open(state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"獲取狀態失敗: {str(e)}")
        
        return None
    
    def shutdown(self):
        """關閉集成"""
        logger.info("關閉 Claude 集成...")
        
        self.is_active = False
        
        # 結束當前會話
        if self.current_session:
            self.end_session()
        
        # 關閉 ClaudeEditor
        if self.claudeditor_process and self.claudeditor_process.poll() is None:
            self.claudeditor_process.terminate()
            self.claudeditor_process.wait()
        
        logger.info("✅ Claude 集成已關閉")


# 全局集成實例
claude_integration = ClaudeIntegration()

# 便捷函數
def enable_claude_integration():
    """啟用 Claude 集成"""
    claude_integration.enable_integration()

def send_to_editor(command: str, params: Dict[str, Any] = None):
    """發送命令到編輯器"""
    claude_integration.send_to_claudeditor(command, params)

def get_editor_state() -> Optional[Dict[str, Any]]:
    """獲取編輯器狀態"""
    return claude_integration.get_claudeditor_state()