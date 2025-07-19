# PowerAutomation v4.75 架構說明

## 目錄結構規範

### 1. UI 組件位置
- **SmartUI 工作區**: `core/components/smartui_mcp/`
  - 所有 UI 組件（.jsx, .tsx）都應該在這裡創建
  - 包括儀表板、表單、圖表等可視化組件
  
- **演示 UI**: `core/components/demo_ui/`
  - 專門用於演示的 UI 組件
  - 集成到 ClaudeEditor 中間欄

### 2. MCP 系統位置
- **核心 MCP**: `core/components/`
  - 只有需要與 AI 模型交互的功能才需要 MCP
  - 例如：codeflow_mcp.py, smartui_mcp.py, demo_mcp.py

### 3. 什麼時候需要 MCP？

**需要 MCP 的情況：**
- ✅ 需要與 Claude/K2 模型交互
- ✅ 需要統一的 API 接口管理
- ✅ 需要跨組件的狀態同步
- ✅ 需要複雜的業務邏輯協調
- ✅ 需要與外部服務集成

**不需要 MCP 的情況：**
- ❌ 純 UI 展示組件
- ❌ 簡單的工具函數
- ❌ 靜態配置文件
- ❌ 獨立的腳本工具

### 4. 現有 MCP 系統

1. **CodeFlow MCP** (`codeflow_mcp.py`)
   - 管理代碼規範和流程
   - 提供代碼分析和優化建議

2. **SmartUI MCP** (`smartui_mcp.py`)
   - 管理 UI 組件生成
   - 處理規格覆蓋和測試

3. **Demo MCP** (`demo_mcp.py`)
   - 管理演示功能
   - 協調多個演示組件的執行

### 5. 工作流程

```
用戶請求 → ClaudeEditor → MCP 系統 → AI 模型/業務邏輯
                ↓
            UI 組件 ← 數據響應
```

### 6. 最佳實踐

1. **UI 開發**：
   - 在 `smartui_mcp/` 或 `demo_ui/` 中創建
   - 遵循 SmartUI 規範
   - 使用統一的組件庫

2. **MCP 開發**：
   - 只在必要時創建 MCP
   - 保持接口簡潔統一
   - 處理錯誤和異常

3. **集成方式**：
   - UI 通過 props 接收數據
   - MCP 通過 API 提供服務
   - 使用事件系統進行通信

## 總結

- **不是所有功能都需要 MCP**
- MCP 主要用於需要 AI 交互或複雜協調的場景
- UI 組件應該保持純粹，通過 props 和事件通信
- 遵循既定的目錄結構，不要另行創建新位置