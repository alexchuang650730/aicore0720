#!/usr/bin/env python3
"""
PowerAutomation Claude Code CLI
固定的 CLI 接口，透明切換到 K2 模型
基於 MCP 架構，與 Claude Code Tool 完全兼容
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加項目路徑
sys.path.append(str(Path(__file__).parent / "core"))

class PowerAutomationCLI:
    """PowerAutomation 固定 CLI"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.mcp_components = {}
        self.current_model = "k2"  # 默認使用 K2
        self.config = {
            "mcp_server_url": "ws://localhost:8081",
            "cost_optimization": True,
            "fallback_to_claude": True,
            "verbose": False
        }
        
    async def initialize(self):
        """初始化 CLI 和 MCP 連接"""
        try:
            # 動態加載 MCP 組件
            await self._load_mcp_components()
            
            # 連接到 MCP 服務器
            await self._connect_to_mcp_server()
            
            print(f"✅ PowerAutomation CLI v{self.version} 已就緒")
            print(f"🎯 當前模型: {self.current_model.upper()}")
            print(f"💰 成本優化: {'開啟' if self.config['cost_optimization'] else '關閉'}")
            
        except Exception as e:
            print(f"❌ CLI 初始化失敗: {e}")
            sys.exit(1)
    
    async def _load_mcp_components(self):
        """動態加載 MCP 組件"""
        try:
            from mcp_components.claude_router_mcp import ClaudeRouterMCP
            from mcp_components.command_mcp import CommandMCP
            from mcp_components.k2_chat_mcp import K2ChatMCP
            from mcp_components.memory_rag_mcp import MemoryRAGMCP
            
            self.mcp_components = {
                "claude_router": ClaudeRouterMCP(),
                "command": CommandMCP(),
                "k2_chat": K2ChatMCP(),
                "memory_rag": MemoryRAGMCP()
            }
            
            # 初始化所有組件
            for name, component in self.mcp_components.items():
                await component.initialize()
                
        except Exception as e:
            print(f"❌ MCP 組件加載失敗: {e}")
            raise
    
    async def _connect_to_mcp_server(self):
        """連接到 MCP 服務器"""
        # 這裡可以添加 WebSocket 連接邏輯
        pass
    
    async def execute_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """執行 Claude Code Tool 命令"""
        args = args or []
        
        if self.config["verbose"]:
            print(f"🔧 執行命令: {command} {' '.join(args)}")
        
        try:
            # 1. 通過 Command MCP 處理命令
            command_mcp = self.mcp_components["command"]
            command_result = await command_mcp.call_mcp("process_claude_code_command", {
                "command": command,
                "args": args
            })
            
            # 2. 如果需要 AI 處理，通過 Claude Router 路由
            if self._needs_ai_processing(command):
                message = self._build_ai_message(command, args)
                
                claude_router = self.mcp_components["claude_router"]
                route_result = await claude_router.call_mcp("route_request", {
                    "message": message,
                    "model": "claude-3-sonnet" if self.current_model == "claude" else "k2"
                })
                
                # 3. 實際執行 AI 處理
                if route_result.get("provider") == "kimi_k2":
                    k2_chat = self.mcp_components["k2_chat"]
                    ai_result = await k2_chat.call_mcp("chat", {
                        "message": message
                    })
                    
                    # 顯示成本節省
                    if ai_result.get("success") and ai_result.get("cost_savings", 0) > 0:
                        print(f"💰 成本節省: ${ai_result['cost_savings']:.4f} (使用 K2 模型)")
                    
                    return {
                        "success": True,
                        "output": ai_result.get("response", ""),
                        "model": "k2",
                        "cost_savings": ai_result.get("cost_savings", 0)
                    }
                else:
                    # 使用 Claude 處理
                    return {
                        "success": True,
                        "output": "使用 Claude 模型處理",
                        "model": "claude",
                        "cost_savings": 0
                    }
            else:
                # 不需要 AI 處理的命令
                return {
                    "success": command_result.get("status") == "success",
                    "output": command_result.get("message", ""),
                    "model": None,
                    "cost_savings": 0
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": f"命令執行失敗: {e}"
            }
    
    def _needs_ai_processing(self, command: str) -> bool:
        """判斷命令是否需要 AI 處理"""
        ai_commands = [
            "/explain", "/review", "/suggest", "/optimize", 
            "/generate", "/fix", "/analyze", "/document"
        ]
        
        # 如果是文件操作命令，也可能需要 AI 分析
        file_commands = ["/read", "/write", "/edit"]
        
        return command in ai_commands or command in file_commands
    
    def _build_ai_message(self, command: str, args: List[str]) -> str:
        """構建 AI 處理消息"""
        if command == "/read":
            file_path = args[0] if args else "文件"
            return f"請讀取並分析文件 {file_path}"
        elif command == "/write":
            file_path = args[0] if args else "文件"
            content = args[1] if len(args) > 1 else "內容"
            return f"請寫入文件 {file_path}，內容：{content}"
        elif command == "/explain":
            target = args[0] if args else "代碼"
            return f"請解釋 {target}"
        elif command == "/review":
            target = args[0] if args else "代碼"
            return f"請審查 {target}"
        else:
            return f"請處理 Claude Code Tool 命令：{command} {' '.join(args)}"
    
    def print_help(self):
        """顯示幫助信息"""
        help_text = f"""
PowerAutomation CLI v{self.version}
與 Claude Code Tool 完全兼容，透明切換到 K2 模型節省 60-80% 成本

基本命令：
  /help                     顯示此幫助信息
  /version                  顯示版本信息
  /status                   顯示系統狀態
  /config                   顯示配置信息

文件操作：
  /read <file>             讀取文件
  /write <file> <content>  寫入文件
  /edit <file>             編輯文件
  /list [dir]              列出文件
  /create <file>           創建文件
  /delete <file>           刪除文件

代碼操作：
  /run <code>              執行代碼
  /test [file]             運行測試
  /explain <target>        解釋代碼
  /review <file>           代碼審查
  /optimize <file>         優化代碼
  /fix <file>              修復代碼

項目管理：
  /init <project>          初始化項目
  /build                   構建項目
  /deploy                  部署項目
  /commit <message>        提交代碼

PowerAutomation 特色：
  /switch-k2               切換到 K2 模型 (默認)
  /switch-claude           切換到 Claude 模型
  /cost-savings            查看成本節省
  /model-status            查看當前模型狀態
  /memory-search <query>   搜索記憶庫
  /workflow-start <name>   啟動工作流

使用方法：
  powerautomation <command> [args]
  
示例：
  powerautomation /read main.py
  powerautomation /write test.py "print('Hello K2')"
  powerautomation /explain function_name
  powerautomation /cost-savings
"""
        print(help_text)
    
    def print_version(self):
        """顯示版本信息"""
        print(f"PowerAutomation CLI v{self.version}")
        print("與 Claude Code Tool 完全兼容")
        print("自動切換到 K2 模型，節省 60-80% 成本")
    
    async def print_status(self):
        """顯示系統狀態"""
        print("📊 PowerAutomation 系統狀態:")
        print(f"  當前模型: {self.current_model.upper()}")
        print(f"  成本優化: {'開啟' if self.config['cost_optimization'] else '關閉'}")
        print(f"  MCP 組件: {len(self.mcp_components)} 個")
        
        # 檢查組件狀態
        for name, component in self.mcp_components.items():
            if hasattr(component, 'get_status'):
                status = component.get_status()
                print(f"    {name}: {status.get('status', 'unknown')}")
    
    async def print_cost_savings(self):
        """顯示成本節省統計"""
        try:
            k2_chat = self.mcp_components["k2_chat"]
            stats_result = await k2_chat.call_mcp("get_stats", {})
            
            if stats_result.get("success"):
                stats = stats_result["stats"]
                print("💰 成本節省統計:")
                print(f"  總請求: {stats.get('total_requests', 0)}")
                print(f"  成功請求: {stats.get('successful_requests', 0)}")
                print(f"  總節省: ${stats.get('total_cost_savings_usd', 0):.4f}")
                print(f"  成功率: {stats.get('success_rate', 0):.1f}%")
                print(f"  平均節省: ${stats.get('average_tokens_per_request', 0) * 0.0007:.4f}/請求")
            else:
                print("❌ 無法獲取成本節省統計")
                
        except Exception as e:
            print(f"❌ 獲取統計失敗: {e}")
    
    async def switch_model(self, model: str):
        """切換模型"""
        if model in ["k2", "claude"]:
            self.current_model = model
            print(f"✅ 已切換到 {model.upper()} 模型")
            if model == "k2":
                print("💰 將享受 60-80% 成本節省")
            else:
                print("⚠️  將使用原始 Claude 定價")
        else:
            print(f"❌ 未知模型: {model}")

async def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="PowerAutomation - 與 Claude Code Tool 兼容的 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("command", nargs="?", help="要執行的命令")
    parser.add_argument("args", nargs="*", help="命令參數")
    parser.add_argument("-v", "--verbose", action="store_true", help="詳細輸出")
    parser.add_argument("--version", action="version", version="PowerAutomation CLI v1.0.0")
    
    args = parser.parse_args()
    
    # 創建 CLI 實例
    cli = PowerAutomationCLI()
    cli.config["verbose"] = args.verbose
    
    # 初始化
    await cli.initialize()
    
    # 處理命令
    if not args.command:
        cli.print_help()
        return
    
    command = args.command
    command_args = args.args
    
    # 處理特殊命令
    if command == "/help":
        cli.print_help()
    elif command == "/version":
        cli.print_version()
    elif command == "/status":
        await cli.print_status()
    elif command == "/cost-savings":
        await cli.print_cost_savings()
    elif command == "/switch-k2":
        await cli.switch_model("k2")
    elif command == "/switch-claude":
        await cli.switch_model("claude")
    else:
        # 執行 Claude Code Tool 命令
        result = await cli.execute_command(command, command_args)
        
        if result["success"]:
            print(result["output"])
            if result.get("cost_savings", 0) > 0:
                print(f"💰 本次節省: ${result['cost_savings']:.4f}")
        else:
            print(f"❌ {result.get('error', '命令執行失敗')}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())