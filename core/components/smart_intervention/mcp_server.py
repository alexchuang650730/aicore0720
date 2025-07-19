#!/usr/bin/env python3
"""
Smart Intervention MCP Server
智能干預系統的 MCP 服務器實現
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource, Tool, TextContent, ImageContent, EmbeddedResource
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP 依賴不可用，使用模擬模式")

from .claude_keyword_listener import ClaudeKeywordListener, ClaudeHookSystem
from .claude_integration import ClaudeIntegration
from .auto_launcher import AutoLauncher
from .claudeditor_capability_switcher import ClaudeEditorCapabilitySwitcher

logger = logging.getLogger(__name__)

class SmartInterventionMCPServer:
    """Smart Intervention MCP 服務器"""
    
    def __init__(self):
        self.server = Server("smart_intervention") if MCP_AVAILABLE else None
        
        # 核心組件
        self.keyword_listener = ClaudeKeywordListener()
        self.hook_system = ClaudeHookSystem()
        self.integration = ClaudeIntegration()
        self.auto_launcher = AutoLauncher()
        self.capability_switcher = ClaudeEditorCapabilitySwitcher()
        
        # 註冊 MCP 工具和資源
        if MCP_AVAILABLE:
            self._register_tools()
            self._register_resources()
        
        # 啟動狀態
        self.is_running = False
        
    def _register_tools(self):
        """註冊 MCP 工具"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """列出可用工具"""
            return [
                Tool(
                    name="check_smart_intervention",
                    description="檢查是否需要智能干預並建議切換到 ClaudeEditor",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "用戶消息內容"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="launch_claudeditor",
                    description="啟動 ClaudeEditor 並配置相關功能",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_type": {
                                "type": "string",
                                "description": "任務類型"
                            },
                            "features": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "需要的功能列表"
                            }
                        }
                    }
                ),
                Tool(
                    name="enable_claude_integration",
                    description="啟用 Claude 深度集成",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "auto_launch": {
                                "type": "boolean",
                                "description": "是否自動啟動"
                            },
                            "collect_data": {
                                "type": "boolean", 
                                "description": "是否收集數據"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_intervention_status",
                    description="獲取智能干預系統狀態",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="setup_custom_hooks",
                    description="設置自定義觸發鉤子",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "正則表達式模式"
                            },
                            "action": {
                                "type": "string",
                                "description": "觸發動作"
                            },
                            "priority": {
                                "type": "integer",
                                "description": "優先級"
                            }
                        },
                        "required": ["pattern", "action"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """處理工具調用"""
            try:
                if name == "check_smart_intervention":
                    return await self._handle_check_intervention(arguments)
                
                elif name == "launch_claudeditor":
                    return await self._handle_launch_claudeditor(arguments)
                
                elif name == "enable_claude_integration":
                    return await self._handle_enable_integration(arguments)
                
                elif name == "get_intervention_status":
                    return await self._handle_get_status()
                
                elif name == "setup_custom_hooks":
                    return await self._handle_setup_hooks(arguments)
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"未知工具: {name}"
                    )]
                    
            except Exception as e:
                logger.error(f"工具調用失敗: {e}")
                return [TextContent(
                    type="text",
                    text=f"工具調用失敗: {str(e)}"
                )]
    
    def _register_resources(self):
        """註冊 MCP 資源"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """列出可用資源"""
            return [
                Resource(
                    uri="smart-intervention://status",
                    name="智能干預系統狀態",
                    description="獲取當前系統運行狀態",
                    mimeType="application/json"
                ),
                Resource(
                    uri="smart-intervention://history",
                    name="干預歷史記錄",
                    description="獲取干預和切換歷史",
                    mimeType="application/json"
                ),
                Resource(
                    uri="smart-intervention://config",
                    name="系統配置",
                    description="獲取當前配置信息",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """讀取資源"""
            if uri == "smart-intervention://status":
                status = self._get_comprehensive_status()
                return json.dumps(status, ensure_ascii=False, indent=2)
            
            elif uri == "smart-intervention://history":
                history = self._get_intervention_history()
                return json.dumps(history, ensure_ascii=False, indent=2)
            
            elif uri == "smart-intervention://config":
                config = self._get_system_config()
                return json.dumps(config, ensure_ascii=False, indent=2)
            
            else:
                raise ValueError(f"未知資源: {uri}")
    
    async def _handle_check_intervention(self, args: Dict[str, Any]) -> List[TextContent]:
        """處理智能干預檢查"""
        message = args.get("message", "")
        
        # 分析消息
        analysis = self.keyword_listener.analyze_message(message)
        should_switch, task_type, features = self.capability_switcher.analyze_task(message)
        
        result = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "keyword_analysis": analysis,
            "capability_analysis": {
                "should_switch": should_switch,
                "task_type": task_type,
                "recommended_features": features
            }
        }
        
        if should_switch:
            suggestion = await self.capability_switcher.suggest_switch(message, task_type)
            result["suggestion"] = suggestion
            
            response = f"""🚀 **智能干預建議**

檢測到您的任務更適合 ClaudeEditor 處理：

**任務類型**: {task_type}
**推薦功能**: {', '.join(features)}

**建議理由**: {self.capability_switcher.claudeditor_superior_tasks[task_type]['message']}

您可以使用 `launch_claudeditor` 工具立即啟動 ClaudeEditor。"""
        
        else:
            response = "當前任務適合在 Claude 中繼續處理，無需切換到 ClaudeEditor。"
        
        return [TextContent(
            type="text",
            text=response
        )]
    
    async def _handle_launch_claudeditor(self, args: Dict[str, Any]) -> List[TextContent]:
        """處理 ClaudeEditor 啟動"""
        task_type = args.get("task_type", "general")
        features = args.get("features", [])
        
        try:
            # 通過能力切換器啟動
            success = await self.capability_switcher.auto_switch_to_claudeditor(task_type, features)
            
            if success:
                response = f"""✅ **ClaudeEditor 啟動成功**

**任務類型**: {task_type}
**啟用功能**: {', '.join(features)}

ClaudeEditor 已啟動並配置完成，您現在可以使用專業工具來完成您的任務。

**提示**: 相關功能面板將自動打開，您可以立即開始工作。"""
            else:
                response = "❌ ClaudeEditor 啟動失敗，請檢查系統配置。"
        
        except Exception as e:
            response = f"❌ 啟動過程中出錯: {str(e)}"
        
        return [TextContent(
            type="text",
            text=response
        )]
    
    async def _handle_enable_integration(self, args: Dict[str, Any]) -> List[TextContent]:
        """處理 Claude 集成啟用"""
        auto_launch = args.get("auto_launch", True)
        collect_data = args.get("collect_data", True)
        
        # 更新配置
        self.integration.config.update({
            "auto_launch": auto_launch,
            "collect_data": collect_data
        })
        
        # 啟用集成
        self.integration.enable_integration()
        
        # 啟動新會話
        self.integration.start_session()
        
        response = f"""✅ **Claude 深度集成已啟用**

**配置**:
- 自動啟動: {'是' if auto_launch else '否'}
- 數據收集: {'是' if collect_data else '否'}

**功能**:
- 實時監聽 Claude 對話
- 智能檢測啟動時機
- 雙向狀態同步
- 自動數據收集

**會話ID**: {self.integration.current_session['id'] if self.integration.current_session else 'None'}

集成已激活，系統將智能地檢測何時需要啟動 ClaudeEditor。"""
        
        return [TextContent(
            type="text",
            text=response
        )]
    
    async def _handle_get_status(self) -> List[TextContent]:
        """處理狀態查詢"""
        status = self._get_comprehensive_status()
        
        response = f"""📊 **智能干預系統狀態**

**運行狀態**: {'🟢 運行中' if self.is_running else '🔴 已停止'}

**組件狀態**:
- 關鍵詞監聽器: {'🟢 活躍' if self.keyword_listener.is_running else '🔴 停止'}
- Claude 集成: {'🟢 已啟用' if self.integration.is_active else '🔴 未啟用'}
- 自動啟動器: {'🟢 工作中' if hasattr(self.auto_launcher, 'running') else '🔴 未運行'}

**統計信息**:
- 檢測會話: {len(self.keyword_listener.launch_history)}
- 切換次數: {len(self.capability_switcher.switch_history)}
- 集成會話: {len(self.integration.completed_sessions) if hasattr(self.integration, 'completed_sessions') else 0}

**當前會話**: {self.integration.current_session['id'] if self.integration.current_session else '無'}"""
        
        return [TextContent(
            type="text",
            text=response
        )]
    
    async def _handle_setup_hooks(self, args: Dict[str, Any]) -> List[TextContent]:
        """處理自定義鉤子設置"""
        pattern = args.get("pattern")
        action = args.get("action")
        priority = args.get("priority", 5)
        
        # 註冊鉤子
        self.hook_system.register_hook(pattern, action, priority)
        
        response = f"""✅ **自定義鉤子已設置**

**模式**: `{pattern}`
**動作**: {action}
**優先級**: {priority}

鉤子已註冊到系統中，當檢測到匹配的消息時將自動觸發指定動作。

**當前鉤子總數**: {len(self.hook_system.hooks)}"""
        
        return [TextContent(
            type="text",
            text=response
        )]
    
    def _get_comprehensive_status(self) -> Dict[str, Any]:
        """獲取全面的系統狀態"""
        return {
            "timestamp": datetime.now().isoformat(),
            "running": self.is_running,
            "components": {
                "keyword_listener": self.keyword_listener.get_status(),
                "integration": {
                    "active": self.integration.is_active,
                    "current_session": self.integration.current_session
                },
                "capability_switcher": self.capability_switcher.get_switch_statistics(),
                "hook_system": {
                    "registered_hooks": len(self.hook_system.hooks)
                }
            },
            "mcp_server": {
                "available": MCP_AVAILABLE,
                "tools_count": 5,
                "resources_count": 3
            }
        }
    
    def _get_intervention_history(self) -> Dict[str, Any]:
        """獲取干預歷史"""
        return {
            "keyword_launches": self.keyword_listener.launch_history,
            "capability_switches": self.capability_switcher.switch_history,
            "integration_sessions": getattr(self.integration, 'completed_sessions', [])
        }
    
    def _get_system_config(self) -> Dict[str, Any]:
        """獲取系統配置"""
        return {
            "auto_launcher": getattr(self.auto_launcher, 'config', {}),
            "integration": self.integration.config,
            "capability_switcher": self.capability_switcher.auto_switch_config,
            "mcp_available": MCP_AVAILABLE
        }
    
    async def start(self):
        """啟動 MCP 服務器"""
        logger.info("🚀 啟動 Smart Intervention MCP 服務器...")
        
        self.is_running = True
        
        # 設置默認鉤子
        self.hook_system.setup_default_hooks()
        
        if MCP_AVAILABLE and self.server:
            logger.info("✅ MCP 服務器啟動成功")
        else:
            logger.warning("⚠️ MCP 不可用，使用獨立模式")
        
        logger.info("✅ Smart Intervention MCP 服務器已啟動")
    
    async def stop(self):
        """停止 MCP 服務器"""
        logger.info("🛑 停止 Smart Intervention MCP 服務器...")
        
        self.is_running = False
        
        # 停止各組件
        if self.keyword_listener.is_running:
            self.keyword_listener.stop_system()
        
        if self.integration.is_active:
            self.integration.shutdown()
        
        logger.info("✅ Smart Intervention MCP 服務器已停止")


# 全局 MCP 服務器實例
smart_intervention_server = SmartInterventionMCPServer()

async def main():
    """主函數 - 用於獨立運行"""
    if MCP_AVAILABLE:
        # 作為 MCP 服務器運行
        await smart_intervention_server.start()
        async with stdio_server() as (read_stream, write_stream):
            await smart_intervention_server.server.run(
                read_stream, write_stream,
                InitializationOptions(
                    server_name="smart_intervention",
                    server_version="1.0.0",
                    capabilities={}
                )
            )
    else:
        # 獨立模式運行
        await smart_intervention_server.start()
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await smart_intervention_server.stop()

if __name__ == "__main__":
    asyncio.run(main())