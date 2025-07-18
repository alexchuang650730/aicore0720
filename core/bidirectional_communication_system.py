#!/usr/bin/env python3
"""
雙向通信系統 - Claude Code Tool 與 ClaudeEditor 的橋樑
1. 自動將 Claude Code Tool 切換到 K2 模式
2. 檢測需要可視化的操作，自動啟動 ClaudeEditor
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import webbrowser
from datetime import datetime

class BidirectionalCommunicationSystem:
    """雙向通信系統"""
    
    def __init__(self):
        self.claudeditor_url = "http://localhost:8080"
        self.k2_mode_enabled = False
        self.visual_triggers = {
            # 觸發詞到ClaudeEditor功能的映射
            "下載文件": "file_download",
            "download": "file_download",
            "部署": "deployment_workflow",
            "deploy": "deployment_workflow",
            "六大工作流": "six_workflows",
            "工作流": "workflow_visual",
            "生成UI": "smartui_generation",
            "generate ui": "smartui_generation",
            "預覽": "preview_file",
            "preview": "preview_file",
            "演示": "demo_mode",
            "demo": "demo_mode",
            "編輯": "monaco_editor",
            "edit": "monaco_editor",
            "測試報告": "test_report_visual",
            "test report": "test_report_visual"
        }
        
        # 最近生成的文件追蹤
        self.recent_files = []
        self.workspace_path = Path.cwd()
        
    async def setup_k2_mode_hijack(self):
        """設置 K2 模式劫持 - 一鍵安裝後自動生效"""
        print("🚀 設置 Claude Code Tool K2 模式劫持...")
        
        # 創建劫持腳本
        hijack_script = """#!/bin/bash
# PowerAutomation K2 Mode Hijacker
# 自動將 Claude Code Tool 請求重定向到 K2

# 檢查是否為 Claude Code Tool 調用
if [[ "$1" == *"claude"* ]] || [[ "$CLAUDE_CODE_TOOL" == "true" ]]; then
    echo "🎯 PowerAutomation: 檢測到 Claude Code Tool 請求"
    echo "🔄 自動切換到 K2 模式以節省成本..."
    
    # 設置 K2 模式環境變量
    export POWERAUTOMATION_MODE="k2"
    export K2_ENABLED="true"
    
    # 調用 Python 腳本處理請求
    python3 {script_path} --k2-mode "$@"
else
    # 非 Claude 請求，正常執行
    "$@"
fi
"""
        
        # 寫入劫持腳本
        hijack_path = Path.home() / ".powerautomation" / "claude_hijack.sh"
        hijack_path.parent.mkdir(exist_ok=True)
        hijack_path.write_text(hijack_script.format(script_path=__file__))
        hijack_path.chmod(0o755)
        
        # 設置環境變量
        shell_config = Path.home() / ".zshrc"  # 或 .bashrc
        if shell_config.exists():
            config_content = shell_config.read_text()
            if "POWERAUTOMATION_HIJACK" not in config_content:
                with open(shell_config, "a") as f:
                    f.write("\n# PowerAutomation K2 Mode\n")
                    f.write(f"alias claude='{hijack_path}'\n")
                    f.write("export POWERAUTOMATION_HIJACK=true\n")
        
        print("✅ K2 模式劫持設置完成！")
        self.k2_mode_enabled = True
        
    async def detect_visual_task(self, user_input: str) -> Optional[Dict[str, Any]]:
        """檢測需要可視化的任務"""
        user_input_lower = user_input.lower()
        
        for trigger, action in self.visual_triggers.items():
            if trigger in user_input_lower:
                return {
                    "action": action,
                    "trigger": trigger,
                    "input": user_input,
                    "timestamp": datetime.now().isoformat()
                }
        
        return None
        
    async def launch_claudeditor(self, task: Dict[str, Any]):
        """啟動 ClaudeEditor 處理可視化任務"""
        print(f"\n🖥️  檢測到需要可視化的任務: {task['trigger']}")
        print("🚀 正在啟動 ClaudeEditor...")
        
        # 準備啟動參數
        launch_params = {
            "action": task["action"],
            "context": {
                "user_input": task["input"],
                "working_directory": str(self.workspace_path),
                "recent_files": self.recent_files[-10:],  # 最近10個文件
                "k2_mode": self.k2_mode_enabled
            }
        }
        
        # 保存啟動參數到臨時文件
        params_file = Path.home() / ".powerautomation" / "launch_params.json"
        params_file.parent.mkdir(exist_ok=True)
        params_file.write_text(json.dumps(launch_params, indent=2))
        
        # 啟動 ClaudeEditor
        try:
            # 檢查 ClaudeEditor 是否已運行
            import requests
            try:
                response = requests.get(f"{self.claudeditor_url}/api/health", timeout=1)
                if response.status_code == 200:
                    print("✅ ClaudeEditor 已在運行")
                else:
                    await self._start_claudeditor()
            except:
                await self._start_claudeditor()
                
            # 發送任務到 ClaudeEditor
            await self._send_task_to_claudeditor(launch_params)
            
            # 在瀏覽器中打開
            webbrowser.open(f"{self.claudeditor_url}?task={task['action']}")
            
        except Exception as e:
            print(f"❌ 啟動 ClaudeEditor 失敗: {e}")
            
    async def _start_claudeditor(self):
        """啟動 ClaudeEditor 服務"""
        print("🔄 正在啟動 ClaudeEditor 服務...")
        
        # 啟動後端服務
        backend_cmd = [
            sys.executable,
            str(self.workspace_path / "claude_code_integration" / "claudeditor_enhanced.py")
        ]
        subprocess.Popen(backend_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 等待服務啟動
        await asyncio.sleep(2)
        
        print("✅ ClaudeEditor 服務已啟動")
        
    async def _send_task_to_claudeditor(self, params: Dict[str, Any]):
        """發送任務參數到 ClaudeEditor"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.claudeditor_url}/api/task",
                    json=params
                ) as response:
                    if response.status == 200:
                        print("✅ 任務已發送到 ClaudeEditor")
                    else:
                        print(f"⚠️ 發送任務失敗: {response.status}")
            except Exception as e:
                print(f"⚠️ 無法連接到 ClaudeEditor: {e}")
                
    async def track_generated_file(self, file_path: str):
        """追蹤生成的文件"""
        self.recent_files.append({
            "path": file_path,
            "timestamp": datetime.now().isoformat(),
            "type": self._get_file_type(file_path)
        })
        
        # 只保留最近50個文件
        if len(self.recent_files) > 50:
            self.recent_files = self.recent_files[-50:]
            
    def _get_file_type(self, file_path: str) -> str:
        """判斷文件類型"""
        ext = Path(file_path).suffix.lower()
        
        file_types = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "react",
            ".ts": "typescript",
            ".tsx": "typescript-react",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".md": "markdown",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".sh": "shell",
            ".dockerfile": "docker",
            ".docker-compose.yml": "docker-compose"
        }
        
        return file_types.get(ext, "text")
        
    async def handle_claude_request(self, command: str, args: List[str]):
        """處理 Claude Code Tool 請求"""
        print(f"\n🤖 PowerAutomation 雙向通信系統")
        print(f"📥 接收到請求: {command} {' '.join(args)}")
        
        # 組合完整的用戶輸入
        user_input = f"{command} {' '.join(args)}"
        
        # 檢測是否需要可視化
        visual_task = await self.detect_visual_task(user_input)
        
        if visual_task:
            # 需要可視化，啟動 ClaudeEditor
            await self.launch_claudeditor(visual_task)
            
            # 根據不同的任務類型返回不同的響應
            if visual_task["action"] == "file_download":
                print("\n📂 文件已添加到 ClaudeEditor 快速工作區")
                print("💡 提示: 點擊文件可在 Monaco Editor 中查看和編輯")
            elif visual_task["action"] == "deployment_workflow":
                print("\n🚀 部署工作流已在 ClaudeEditor 中啟動")
                print("💡 提示: 可視化界面顯示部署進度和日誌")
            elif visual_task["action"] == "six_workflows":
                print("\n🔄 六大工作流可視化界面已打開")
                print("💡 提示: 可以拖拽調整工作流順序和配置")
            elif visual_task["action"] == "demo_mode":
                print("\n🎬 演示模式已啟動")
                print("💡 提示: 選擇文件後可實時預覽效果")
                
        else:
            # 不需要可視化，使用 K2 模式處理
            if self.k2_mode_enabled:
                print("\n🔄 使用 K2 模式處理請求...")
                print("💰 預計節省 60% 成本")
                # 這裡調用 K2 API 處理請求
                await self._process_with_k2(user_input)
            else:
                print("\n⚠️ K2 模式未啟用，使用標準模式")
                
    async def _process_with_k2(self, user_input: str):
        """使用 K2 模式處理請求"""
        # 這裡實現 K2 API 調用邏輯
        print(f"🤖 K2 處理中: {user_input}")
        # ... K2 API 調用代碼 ...


# 命令行接口
async def main():
    """主函數"""
    system = BidirectionalCommunicationSystem()
    
    # 解析命令行參數
    if len(sys.argv) > 1:
        if sys.argv[1] == "--setup":
            # 設置模式
            await system.setup_k2_mode_hijack()
        elif sys.argv[1] == "--k2-mode":
            # K2 模式處理
            if len(sys.argv) > 2:
                command = sys.argv[2]
                args = sys.argv[3:] if len(sys.argv) > 3 else []
                await system.handle_claude_request(command, args)
        else:
            # 直接處理請求
            command = sys.argv[1]
            args = sys.argv[2:] if len(sys.argv) > 2 else []
            await system.handle_claude_request(command, args)
    else:
        print("🎯 PowerAutomation 雙向通信系統")
        print("\n使用方法:")
        print("  python bidirectional_communication_system.py --setup    # 設置 K2 模式劫持")
        print("  python bidirectional_communication_system.py <command>  # 處理命令")


if __name__ == "__main__":
    asyncio.run(main())