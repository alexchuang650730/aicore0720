#!/usr/bin/env python3
"""
Model Command Handler - 處理 /model 命令來切換 K2/Claude 模式
"""

import json
import sys
import os
import subprocess
from pathlib import Path

class ModelCommandHandler:
    def __init__(self):
        self.mcp_server_path = "/Users/alexchuang/alexchuangtest/aicore0720/k2_mode_switcher_mcp.py"
        self.commands = {
            "/model": self.handle_model_command,
            "/mode": self.handle_model_command,  # 別名
        }
        
    def parse_command(self, text):
        """解析用戶輸入，檢查是否包含命令"""
        if not text.strip().startswith("/"):
            return None, None
            
        parts = text.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        return command, args
        
    def handle_model_command(self, args):
        """處理 /model 命令"""
        args = args.lower().strip()
        
        # 支持的模式
        valid_modes = {
            "k2": "k2",
            "claude": "claude", 
            "hybrid": "hybrid",
            "auto": "hybrid",
            "smart": "hybrid",
            "混合": "hybrid",
            "智能": "hybrid"
        }
        
        # 顯示幫助
        if not args or args in ["help", "?"]:
            return self.show_model_help()
            
        # 顯示當前狀態
        if args in ["status", "info", "狀態"]:
            return self.show_model_status()
            
        # 切換模式
        if args in valid_modes:
            mode = valid_modes[args]
            return self.switch_model(mode)
            
        return {
            "status": "error",
            "message": f"❌ 未知的模式: {args}\n使用 /model help 查看可用選項"
        }
        
    def switch_model(self, mode):
        """切換到指定模式"""
        try:
            # 發送切換請求
            request = json.dumps({
                "method": "k2/switch_mode",
                "params": {"mode": mode}
            })
            
            result = subprocess.run(
                ["python3", self.mcp_server_path],
                input=request,
                capture_output=True,
                text=True
            )
            
            response = json.loads(result.stdout)
            
            if response.get("status") == "success":
                mode_names = {
                    "k2": "K2 本地推理",
                    "claude": "Claude API",
                    "hybrid": "智能混合"
                }
                
                return {
                    "status": "success",
                    "message": f"✅ 已切換到 {mode_names.get(mode, mode)} 模式\n" +
                              self.get_mode_description(mode)
                }
            else:
                return {
                    "status": "error",
                    "message": f"❌ 切換失敗: {response.get('message', '未知錯誤')}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ 切換模式時出錯: {str(e)}"
            }
            
    def show_model_status(self):
        """顯示當前模型狀態"""
        try:
            request = json.dumps({"method": "k2/status", "params": {}})
            
            result = subprocess.run(
                ["python3", self.mcp_server_path],
                input=request,
                capture_output=True,
                text=True
            )
            
            status = json.loads(result.stdout)
            
            mode_emoji = {
                "k2": "🟢",
                "claude": "🔵",
                "hybrid": "🟡"
            }
            
            current_mode = status.get("mode", "unknown")
            
            message = f"""📊 當前模型狀態:

{mode_emoji.get(current_mode, '⚫')} 模式: {current_mode.upper()}
📈 K2 準確率: {status.get('accuracy', 0):.1f}%
📚 訓練樣本: {status.get('total_samples', 0):,}
🎯 置信度閾值: {status.get('confidence_threshold', 0.7):.0%}
🔄 模型版本: v{status.get('model_version', 0)}

{self.get_mode_description(current_mode)}"""
            
            return {
                "status": "success",
                "message": message
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ 獲取狀態失敗: {str(e)}"
            }
            
    def show_model_help(self):
        """顯示幫助信息"""
        help_text = """🤖 Model 命令使用說明:

**切換模式:**
• `/model k2` - 切換到 K2 本地推理模式
• `/model claude` - 切換到 Claude API 模式
• `/model hybrid` - 切換到智能混合模式（默認）

**查看狀態:**
• `/model status` - 查看當前模式和狀態
• `/model help` - 顯示此幫助信息

**快捷方式:**
• `/model auto` - 同 hybrid
• `/model smart` - 同 hybrid

**示例:**
```
/model k2        # 使用本地 K2 模型
/model claude    # 使用 Claude API
/model status    # 查看當前狀態
```

💡 提示: 也可以在對話中直接說「使用K2」或「切換到Claude模式」"""
        
        return {
            "status": "success",
            "message": help_text
        }
        
    def get_mode_description(self, mode):
        """獲取模式描述"""
        descriptions = {
            "k2": "🟢 K2 模式: 使用本地訓練的模型，響應快速，離線可用",
            "claude": "🔵 Claude 模式: 使用 Claude API，適合複雜任務",
            "hybrid": "🟡 混合模式: 根據置信度智能選擇最佳引擎"
        }
        return descriptions.get(mode, "")
        
    def process_input(self, user_input):
        """處理用戶輸入"""
        command, args = self.parse_command(user_input)
        
        if command in self.commands:
            return self.commands[command](args)
            
        return None


# 創建 MCP 集成包裝器
class ModelCommandMCP:
    """MCP 服務器集成 /model 命令"""
    
    def __init__(self):
        self.command_handler = ModelCommandHandler()
        
    def handle_request(self, request):
        """處理 MCP 請求"""
        method = request.get("method", "")
        
        if method == "command/process":
            # 處理命令
            text = request.get("params", {}).get("text", "")
            result = self.command_handler.process_input(text)
            
            if result:
                return result
            else:
                return {"status": "not_command"}
                
        return {"error": "Unknown method"}


# 測試腳本
if __name__ == "__main__":
    handler = ModelCommandHandler()
    
    # 測試命令
    test_commands = [
        "/model help",
        "/model status", 
        "/model k2",
        "/model claude",
        "/model hybrid",
        "/model unknown"
    ]
    
    print("🧪 測試 /model 命令處理器:\n")
    
    for cmd in test_commands:
        print(f"命令: {cmd}")
        result = handler.process_input(cmd)
        if result:
            print(f"結果: {result['status']}")
            print(f"消息:\n{result['message']}\n")
        else:
            print("不是命令\n")
        print("-" * 50)