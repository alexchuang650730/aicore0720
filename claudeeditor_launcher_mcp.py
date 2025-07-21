#!/usr/bin/env python3
"""
ClaudeEditor Launcher MCP - 通過關鍵詞啟動 ClaudeEditor
"""

import json
import sys
import os
import subprocess
from pathlib import Path

class ClaudeEditorLauncher:
    def __init__(self):
        self.editor_path = os.environ.get('CLAUDEEDITOR_PATH', '/Applications/ClaudeEditor.app')
        self.trigger_file = Path(os.environ.get('TRIGGER_FILE', '~/.claudeeditor_trigger')).expanduser()
        self.keywords = [
            "啟動編輯器", "打開ClaudeEditor", "start editor", 
            "open claudeeditor", "編輯器模式", "claudeeditor"
        ]
        
    def check_trigger(self, text):
        """檢查是否包含觸發關鍵詞"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
        
    def launch_editor(self):
        """啟動 ClaudeEditor"""
        try:
            if os.path.exists(self.editor_path):
                subprocess.Popen(['open', self.editor_path])
                return {"status": "launched", "path": self.editor_path}
            else:
                return {"status": "error", "message": f"ClaudeEditor not found at {self.editor_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def handle_request(self, request):
        """處理 MCP 請求"""
        method = request.get("method", "")
        
        if method == "claudeeditor/check":
            # 檢查文本是否包含觸發詞
            text = request.get("params", {}).get("text", "")
            if self.check_trigger(text):
                return self.launch_editor()
            return {"status": "no_trigger"}
            
        elif method == "claudeeditor/launch":
            # 直接啟動
            return self.launch_editor()
            
        elif method == "claudeeditor/status":
            # 檢查狀態
            return {
                "available": os.path.exists(self.editor_path),
                "keywords": self.keywords
            }
            
        return {"error": "Unknown method"}

if __name__ == "__main__":
    launcher = ClaudeEditorLauncher()
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
