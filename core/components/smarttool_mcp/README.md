# SmartTool MCP - 外部工具智能集成

## 概述

SmartTool MCP 是 PowerAutomation 的外部工具集成組件，提供與 mcp.so、aci.dev、zapier 等第三方工具平台的統一接入能力。

## 功能特性

- **多平台支持**：集成 mcp.so、aci.dev、zapier 三大工具平台
- **統一接口**：提供一致的工具調用和管理接口
- **智能推薦**：基於任務需求智能推薦合適的工具
- **工作流執行**：支持順序和並行工作流執行
- **緩存優化**：智能緩存機制提升執行效率
- **與 MCP-Zero 深度集成**：作為動態加載的 MCP 組件

## 支持的平台

### 1. MCP.so
- Prettier 代碼格式化
- ESLint 代碼檢查
- Jest 測試運行器
- 更多開發工具...

### 2. ACI.dev
- AI 代碼分析器
- 安全掃描器
- 性能分析器
- AI 驅動的開發工具...

### 3. Zapier
- Slack 通知
- GitHub 集成
- Google Sheets 操作
- Email 自動化
- 數千種應用集成...

## 使用方式

### 通過 MCP-Zero 調用

```python
# MCP-Zero 會自動發現並加載 SmartTool MCP
mcp_zero = MCPZeroEngine()
result = await mcp_zero.execute_task(
    "使用 prettier 格式化代碼並發送 Slack 通知",
    context={"code": "const x=1;", "channel": "#dev"}
)
```

### 直接使用

```python
from core.components.smarttool_mcp import SmartToolManager

# 初始化
manager = SmartToolManager()
await manager.initialize()

# 列出工具
tools = await manager.list_tools(platform="mcp.so")

# 執行工具
result = await manager.execute_tool(
    tool_id="mcp_prettier",
    parameters={"code": "const x=1;", "language": "javascript"}
)

# 執行工作流
workflow_result = await manager.execute_workflow({
    "steps": [
        {
            "tool_id": "mcp_prettier",
            "parameters": {"code": "const x=1;", "language": "javascript"}
        },
        {
            "tool_id": "zapier_slack",
            "parameters": {"channel": "#dev", "message": "代碼已格式化"}
        }
    ],
    "parallel": False
})
```

## 架構設計

```
smarttool_mcp/
├── __init__.py              # 模組入口
├── smarttool_manager.py     # 主管理器
├── external_tools_integration.py  # MCP 接口實現
├── mcp_so_adapter.py        # MCP.so 適配器
├── aci_dev_adapter.py       # ACI.dev 適配器
├── zapier_adapter.py        # Zapier 適配器
└── README.md               # 本文件
```

## 配置

環境變量：
```bash
MCP_SO_API_KEY=your_mcp_so_key
ACI_DEV_API_KEY=your_aci_dev_key
ZAPIER_API_KEY=your_zapier_key
```

## 與其他 MCP 協作

- **CodeFlow MCP**：提供代碼格式化和質量檢查工具
- **Test MCP**：提供測試執行和覆蓋率分析工具
- **MemoryRAG MCP**：記錄工具使用歷史和效果學習

## 性能指標

- 平均響應時間：< 500ms（使用緩存）
- 成功率：88%
- 支持並發：10 個請求/秒
- 緩存命中率：> 60%

## 未來計劃

1. 支持更多工具平台（GitHub Actions、Jenkins 等）
2. 智能工具組合推薦
3. 工具效果學習和優化
4. 自定義工具開發 SDK
5. 工具市場和社區分享