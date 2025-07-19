# Smart Intervention MCP (P0級核心能力)

智能干預系統 - 自動檢測並切換到 ClaudeEditor 處理更適合的任務

## 核心功能

### 1. 關鍵詞監聽系統
- 實時監聽 Claude 對話
- 智能識別任務類型
- 自動觸發啟動

### 2. 能力切換器
檢測 Claude 不擅長但 ClaudeEditor 擅長的任務：
- **可視化**：圖表、流程圖、架構圖
- **文件管理**：下載、打包、批量操作
- **部署**：CI/CD、Docker、Kubernetes
- **實時預覽**：熱重載、即時反饋
- **UI 設計**：拖放設計、響應式布局
- **數據庫**：視覺化設計、查詢構建
- **性能分析**：分析器、優化建議
- **團隊協作**：實時編輯、代碼審查
- **大型重構**：批量修改、智能分析
- **API 測試**：測試客戶端、文檔生成

### 3. Claude 深度集成
- 雙向通信
- 狀態同步
- 數據收集
- 智能建議

### 4. 自動啟動器
- 鉤子系統
- 優先級管理
- 冷卻機制
- 配置管理

## 使用方式

```python
from core.components.smart_intervention import (
    check_and_switch,
    enable_claude_integration,
    hook_system
)

# 檢查並切換
await check_and_switch("我需要創建一個流程圖")

# 啟用集成
enable_claude_integration()

# 設置鉤子
hook_system.register_hook(
    r"(創建|設計).*(圖表|流程圖)",
    "launch_claudeditor",
    priority=10
)
```

## 優先級說明

作為 P0 級核心能力，Smart Intervention 是 PowerAutomation 的關鍵差異化功能：

1. **提升效率**：自動識別並切換到最適合的工具
2. **無縫體驗**：用戶無需手動判斷和切換
3. **智能推薦**：基於任務類型自動配置功能
4. **數據驅動**：收集使用數據持續優化

## 與 MCP-Zero 集成

Smart Intervention 通過 MCP-Zero 與其他 MCP 協同工作：
- 觸發 SmartUI MCP 進行 UI 設計
- 調用 CodeFlow MCP 生成代碼
- 使用 Test MCP 運行測試
- 協調 SmartTool MCP 執行外部工具