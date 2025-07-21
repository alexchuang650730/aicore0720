#!/usr/bin/env python3
"""
Enhanced ClaudeEditor Launcher - 支持 /model 命令和關鍵詞啟動
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from model_command_handler import ModelCommandHandler

class EnhancedClaudeEditorLauncher:
    def __init__(self):
        self.editor_path = os.environ.get('CLAUDEEDITOR_PATH', '/Applications/ClaudeEditor.app')
        self.trigger_file = Path(os.environ.get('TRIGGER_FILE', '~/.claudeeditor_trigger')).expanduser()
        
        # ClaudeEditor 啟動關鍵詞
        self.editor_keywords = [
            "啟動編輯器", "打開ClaudeEditor", "start editor", 
            "open claudeeditor", "編輯器模式", "claudeeditor"
        ]
        
        # 初始化命令處理器
        self.command_handler = ModelCommandHandler()
        
    def check_triggers(self, text):
        """檢查所有觸發條件"""
        text_lower = text.lower()
        
        # 檢查 ClaudeEditor 觸發詞
        if any(keyword.lower() in text_lower for keyword in self.editor_keywords):
            return "launch_editor"
            
        # 檢查 /model 命令
        if text.strip().startswith("/model") or text.strip().startswith("/mode"):
            return "model_command"
            
        return None
        
    def launch_editor(self):
        """啟動 ClaudeEditor"""
        try:
            if os.path.exists(self.editor_path):
                subprocess.Popen(['open', self.editor_path])
                return {
                    "status": "launched", 
                    "path": self.editor_path,
                    "message": "✅ ClaudeEditor 已啟動"
                }
            else:
                return {
                    "status": "error", 
                    "message": f"❌ ClaudeEditor 未找到: {self.editor_path}"
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def handle_request(self, request):
        """處理 MCP 請求"""
        method = request.get("method", "")
        
        if method == "enhanced/process":
            # 處理增強請求（同時支持關鍵詞和命令）
            text = request.get("params", {}).get("text", "")
            trigger_type = self.check_triggers(text)
            
            if trigger_type == "launch_editor":
                return self.launch_editor()
            elif trigger_type == "model_command":
                result = self.command_handler.process_input(text)
                return result if result else {"status": "no_action"}
            else:
                return {"status": "no_trigger"}
                
        elif method == "claudeeditor/launch":
            # 直接啟動編輯器
            return self.launch_editor()
            
        elif method == "model/command":
            # 處理 /model 命令
            text = request.get("params", {}).get("text", "")
            result = self.command_handler.process_input(text)
            return result if result else {"status": "invalid_command"}
            
        elif method == "status":
            # 返回完整狀態
            return {
                "editor_available": os.path.exists(self.editor_path),
                "editor_keywords": self.editor_keywords,
                "commands": ["/model", "/mode"],
                "model_status": self.command_handler.show_model_status()
            }
            
        return {"error": "Unknown method"}

if __name__ == "__main__":
    launcher = EnhancedClaudeEditorLauncher()
    
    # MCP 服務器主循環
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            response = launcher.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()