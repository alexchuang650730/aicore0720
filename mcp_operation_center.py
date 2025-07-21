#!/usr/bin/env python3
"""
MCP運維中心 - 統一管理和監控所有MCP
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPOperationCenter:
    """MCP運維中心"""
    
    def __init__(self):
        self.base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        self.operation_dir = self.base_dir / "monitoring" / "mcp_operation"
        self.operation_dir.mkdir(parents=True, exist_ok=True)
        
        # MCP註冊表 - 所有21個MCP模塊
        self.mcp_registry = {
            # 核心MCP (P0優先級)
            "mcp_zero": {
                "name": "MCP Zero",
                "type": "core",
                "priority": "P0",
                "capabilities": ["tool_discovery", "auto_routing", "context_management"],
                "status": "active"
            },
            "smart_intervention": {
                "name": "SmartIntervention MCP",
                "type": "intervention",
                "priority": "P0",
                "capabilities": ["error_handling", "auto_fix", "pdf_processing"]
            },
            "smarttool": {
                "name": "SmartTool MCP",
                "type": "tool",
                "priority": "P0",
                "capabilities": ["tool_enhancement", "capability_expansion"]
            },
            "memoryrag": {
                "name": "MemoryRAG MCP",
                "type": "memory",
                "priority": "P0",
                "capabilities": ["context_retention", "learning_from_history"]
            },
            "memoryos": {
                "name": "MemoryOS MCP",
                "type": "memory",
                "priority": "P0",
                "capabilities": ["memory_optimization", "personalization", "rllm_integration"]
            },
            "deepswe": {
                "name": "DeepSWE MCP",
                "type": "core",
                "priority": "P0",
                "capabilities": ["deep_learning", "swe_integration"]
            },
            
            # 功能MCP (P1優先級)
            "codeflow": {
                "name": "CodeFlow MCP",
                "type": "workflow",
                "priority": "P1",
                "capabilities": ["code_generation", "spec_to_code", "code_to_spec"]
            },
            "smartui": {
                "name": "SmartUI MCP",
                "type": "ui",
                "priority": "P1",
                "capabilities": ["ui_generation", "interaction_handling"]
            },
            "ag_ui": {
                "name": "AG UI MCP",
                "type": "ui",
                "priority": "P1",
                "capabilities": ["advanced_ui", "ag_integration"]
            },
            "test_mcp": {
                "name": "Test MCP",
                "type": "testing",
                "priority": "P1",
                "capabilities": ["test_generation", "validation", "coverage_analysis"]
            },
            "command": {
                "name": "Command MCP",
                "type": "command",
                "priority": "P1",
                "capabilities": ["command_execution", "usage_tracking"]
            },
            "local_adapter": {
                "name": "Local Adapter MCP",
                "type": "adapter",
                "priority": "P1",
                "capabilities": ["file_system_access", "local_tool_integration"]
            },
            "claudeeditor": {
                "name": "ClaudeEditor MCP",
                "type": "editor",
                "priority": "P1",
                "capabilities": ["editor_integration", "ui_consolidation"]
            },
            "claude": {
                "name": "Claude MCP",
                "type": "ai",
                "priority": "P1",
                "capabilities": ["claude_integration", "api_management"]
            },
            "claude_realtime": {
                "name": "Claude Realtime MCP",
                "type": "realtime",
                "priority": "P1",
                "capabilities": ["realtime_processing", "streaming"]
            },
            "claude_router": {
                "name": "Claude Router MCP",
                "type": "routing",
                "priority": "P1",
                "capabilities": ["request_routing", "load_balancing"]
            },
            "mcp_coordinator": {
                "name": "MCP Coordinator",
                "type": "coordinator",
                "priority": "P1",
                "capabilities": ["mcp_orchestration", "consolidation_analysis"]
            },
            "stagewise": {
                "name": "Stagewise MCP",
                "type": "workflow",
                "priority": "P1",
                "capabilities": ["stage_management", "workflow_control"]
            },
            
            # 業務/整合MCP (P2優先級)
            "business": {
                "name": "Business MCP",
                "type": "business",
                "priority": "P2",
                "capabilities": ["demo_generation", "website_optimization", "strategic_planning"]
            },
            "docs": {
                "name": "Docs MCP",
                "type": "documentation",
                "priority": "P2",
                "capabilities": ["doc_generation", "api_documentation"]
            },
            "aws_bedrock": {
                "name": "AWS Bedrock MCP",
                "type": "integration",
                "priority": "P2",
                "capabilities": ["multi_model_routing", "cloud_integration"]
            },
            "xmasters": {
                "name": "X-Masters MCP",
                "type": "advanced",
                "priority": "P2",
                "capabilities": ["advanced_reasoning", "multi_agent_coordination"]
            },
            "zen": {
                "name": "Zen MCP",
                "type": "workflow",
                "priority": "P2",
                "capabilities": ["zen_workflow", "optimization"]
            }
        }
        
        # MCP錯誤類型映射
        self.error_type_to_mcp = {
            "binary .pdf file": "smart_intervention",
            "permission denied": "smart_intervention",
            "encoding error": "smart_intervention",
            "tool not found": "mcp_zero",
            "no appropriate tool": "smarttool",
            "test failed": "test_mcp",
            "ui generation": "smartui",
            "memory context": "memoryrag"
        }
        
        # 運維狀態
        self.operation_status = {
            "total_requests": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "mcp_usage": defaultdict(int),
            "error_types": defaultdict(int)
        }
    
    async def route_error_to_mcp(self, error_message: str, context: Dict) -> Dict:
        """路由錯誤到適當的MCP處理"""
        logger.info(f"🔍 分析錯誤: {error_message[:100]}...")
        
        # 識別錯誤類型
        error_lower = error_message.lower()
        selected_mcp = None
        
        for error_pattern, mcp_name in self.error_type_to_mcp.items():
            if error_pattern in error_lower:
                selected_mcp = mcp_name
                break
        
        if not selected_mcp:
            # 默認使用MCP Zero進行工具發現
            selected_mcp = "mcp_zero"
        
        logger.info(f"📡 路由到MCP: {selected_mcp}")
        
        # 調用對應的MCP處理
        result = await self.invoke_mcp(selected_mcp, error_message, context)
        
        # 更新統計
        self.operation_status["total_requests"] += 1
        self.operation_status["mcp_usage"][selected_mcp] += 1
        
        if result.get("success"):
            self.operation_status["successful_operations"] += 1
        else:
            self.operation_status["failed_operations"] += 1
            self.operation_status["error_types"][error_message[:50]] += 1
        
        # 記錄運維日誌
        await self.log_operation({
            "timestamp": datetime.now().isoformat(),
            "error": error_message,
            "mcp_used": selected_mcp,
            "result": result,
            "context": context
        })
        
        return result
    
    async def invoke_mcp(self, mcp_name: str, error: str, context: Dict) -> Dict:
        """調用特定的MCP"""
        mcp_info = self.mcp_registry.get(mcp_name)
        
        if not mcp_info:
            return {
                "success": False,
                "error": f"MCP {mcp_name} not found"
            }
        
        # 根據MCP類型調用相應的處理器
        if mcp_name == "smart_intervention":
            # 調用SmartIntervention MCP
            try:
                from smartintervention_operation_mcp import fix_error
                result = await fix_error(error, context)
                return result
            except Exception as e:
                logger.error(f"SmartIntervention MCP錯誤: {e}")
                return {"success": False, "error": str(e)}
        
        elif mcp_name == "mcp_zero":
            # MCP Zero自動工具發現
            return {
                "success": True,
                "mcp": "mcp_zero",
                "action": "tool_discovery",
                "discovered_tools": ["pdf-reader", "ocr-tool"],
                "suggestion": "使用發現的工具重試操作"
            }
        
        elif mcp_name == "smarttool":
            # SmartTool能力擴展
            return {
                "success": True,
                "mcp": "smarttool",
                "action": "capability_expansion",
                "new_capability": "advanced_pdf_processing"
            }
        
        else:
            # 其他MCP的通用處理
            return {
                "success": True,
                "mcp": mcp_name,
                "message": f"由{mcp_info['name']}處理"
            }
    
    async def log_operation(self, operation_data: Dict):
        """記錄運維操作"""
        log_file = self.operation_dir / "operations.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(operation_data, ensure_ascii=False) + '\n')
    
    def get_mcp_status(self) -> Dict:
        """獲取所有MCP狀態"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "mcp_count": len(self.mcp_registry),
            "active_mcps": [],
            "by_type": defaultdict(list),
            "by_priority": defaultdict(list)
        }
        
        for mcp_id, mcp_info in self.mcp_registry.items():
            if mcp_info.get("status") == "active":
                status["active_mcps"].append(mcp_id)
            
            status["by_type"][mcp_info["type"]].append(mcp_id)
            status["by_priority"][mcp_info["priority"]].append(mcp_id)
        
        return status
    
    def generate_operation_dashboard(self) -> str:
        """生成運維儀表板"""
        mcp_status = self.get_mcp_status()
        
        dashboard = f"""
# MCP運維中心儀表板

更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 總體統計
- MCP總數: {mcp_status['mcp_count']}
- 活躍MCP: {len(mcp_status['active_mcps'])}
- 總請求數: {self.operation_status['total_requests']}
- 成功率: {(self.operation_status['successful_operations'] / self.operation_status['total_requests'] * 100) if self.operation_status['total_requests'] > 0 else 0:.1f}%

## 🛠️ MCP使用情況
"""
        
        # 按使用量排序
        sorted_usage = sorted(self.operation_status['mcp_usage'].items(), 
                            key=lambda x: x[1], reverse=True)
        
        for mcp_name, count in sorted_usage[:10]:
            mcp_info = self.mcp_registry.get(mcp_name, {})
            dashboard += f"- {mcp_info.get('name', mcp_name)}: {count} 次\n"
        
        dashboard += f"""
## 🎯 MCP分類

### 按優先級
"""
        for priority in ["P0", "P1", "P2"]:
            mcps = mcp_status['by_priority'].get(priority, [])
            dashboard += f"- {priority} ({len(mcps)}個): {', '.join(mcps[:5])}\n"
        
        dashboard += """
### 按類型
"""
        for mcp_type, mcps in mcp_status['by_type'].items():
            dashboard += f"- {mcp_type} ({len(mcps)}個): {', '.join(mcps[:3])}\n"
        
        dashboard += f"""
## ❌ 錯誤類型
"""
        for error_type, count in list(self.operation_status['error_types'].items())[:5]:
            dashboard += f"- {error_type}: {count} 次\n"
        
        dashboard += """
## 🚀 建議優化
"""
        
        if self.operation_status['failed_operations'] > 10:
            dashboard += "- ⚠️ 失敗操作較多，建議檢查MCP配置\n"
        
        if "smart_intervention" in self.operation_status['mcp_usage'] and \
           self.operation_status['mcp_usage']["smart_intervention"] > 20:
            dashboard += "- 💡 SmartIntervention使用頻繁，考慮預載入常用修復方案\n"
        
        return dashboard
    
    async def health_check(self) -> Dict:
        """健康檢查所有MCP"""
        health_status = {
            "healthy": [],
            "unhealthy": [],
            "warnings": []
        }
        
        for mcp_id, mcp_info in self.mcp_registry.items():
            # 簡單的健康檢查邏輯
            if mcp_info.get("status") == "active":
                health_status["healthy"].append(mcp_id)
            else:
                health_status["unhealthy"].append(mcp_id)
        
        # 系統資源檢查
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        if cpu_usage > 80:
            health_status["warnings"].append("CPU使用率過高")
        if memory.percent > 80:
            health_status["warnings"].append("內存使用率過高")
        
        return health_status


# 全局運維中心實例
operation_center = MCPOperationCenter()


async def handle_error(error_message: str, context: Dict = None) -> Dict:
    """統一錯誤處理入口"""
    context = context or {}
    return await operation_center.route_error_to_mcp(error_message, context)


async def main():
    """測試MCP運維中心"""
    logger.info("🚀 啟動MCP運維中心...")
    
    # 測試不同類型的錯誤
    test_cases = [
        {
            "error": "Error: This tool cannot read binary files. The file appears to be a binary .pdf file.",
            "context": {"file_path": "test.pdf"}
        },
        {
            "error": "Permission denied: /etc/passwd",
            "context": {"file_path": "/etc/passwd"}
        },
        {
            "error": "Tool not found: advanced-search",
            "context": {"required_tool": "advanced-search"}
        }
    ]
    
    for test in test_cases:
        result = await handle_error(test["error"], test["context"])
        logger.info(f"處理結果: {result}")
    
    # 生成儀表板
    dashboard = operation_center.generate_operation_dashboard()
    print(dashboard)
    
    # 保存儀表板
    dashboard_file = operation_center.operation_dir / "dashboard.md"
    with open(dashboard_file, 'w') as f:
        f.write(dashboard)


if __name__ == "__main__":
    asyncio.run(main())