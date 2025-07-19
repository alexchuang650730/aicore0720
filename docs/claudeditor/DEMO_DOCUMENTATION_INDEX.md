# ClaudeEditor v4.75 演示文檔索引

## 📋 演示功能清單

本文檔提供 ClaudeEditor v4.75 中所有演示功能的完整文檔索引。

### 1. Smart Intervention MCP (P0級核心功能)

**位置**: 演示中心首位  
**組件**: `SmartInterventionDemo.jsx`  
**文檔**: [/docs/mcp/smart_intervention_mcp.md](/docs/mcp/smart_intervention_mcp.md)

**功能說明**:
- 自動檢測任務類型
- 智能切換到最適合的工具
- 支持 6 大場景切換
- 實時監聽和響應

**演示內容**:
- 數據可視化場景
- UI/UX 設計場景
- 數據庫設計場景
- 部署配置場景
- API 測試場景
- 團隊協作場景

---

### 2. StageWise 控制系統

**位置**: 功能演示區  
**組件**: `StageWiseCommandDemo.jsx`  
**文檔**: [/docs/stagewise/command_compatibility.md](/docs/stagewise/command_compatibility.md)

**功能說明**:
- Claude Code Tool 命令 100% 兼容
- 分階段精準控制
- 命令執行追蹤
- K2 模式優化

**演示內容**:
- 命令兼容性矩陣
- 實時執行演示
- 性能對比圖表
- 錯誤處理展示

---

### 3. 統一部署系統

**位置**: 功能演示區  
**組件**: `UnifiedDeploymentUI.jsx`  
**文檔**: [/docs/deployment/unified_deployment.md](/docs/deployment/unified_deployment.md)

**功能說明**:
- Claude Code Tool 集成
- ClaudeEditor 無縫部署
- 一鍵部署流程
- 多環境支持

**演示內容**:
- 部署清單管理
- 環境配置
- 實時部署狀態
- 回滾機制

---

### 4. 工作流自動化

**位置**: 功能演示區  
**組件**: `WorkflowAutomationDashboard.jsx`  
**文檔**: [/docs/workflow/automation_guide.md](/docs/workflow/automation_guide.md)

**功能說明**:
- 六大工作流監控
- 實時 GitHub 數據
- 技術/體驗雙指標
- 自動化執行

**演示內容**:
- 工作流狀態面板
- GitHub 集成展示
- 指標實時更新
- 自動化觸發器

---

### 5. 指標可視化系統

**位置**: 功能演示區  
**組件**: `MetricsVisualizationDashboard.jsx`  
**文檔**: [/docs/metrics/visualization_guide.md](/docs/metrics/visualization_guide.md)

**功能說明**:
- 綜合指標儀表板
- 多維度數據展示
- 實時圖表更新
- 計算公式展示

**演示內容**:
- 數據質量指標
- 性能指標
- 用戶滿意度
- 成本效益分析

---

### 6. SmartUI 合規檢查

**位置**: 功能演示區  
**組件**: `AGUIComplianceDashboard.jsx`  
**文檔**: [/docs/smartui/compliance_guide.md](/docs/smartui/compliance_guide.md)

**功能說明**:
- UI 組件質量分析
- SmartUI 規範檢查
- 規格覆蓋率
- 測試覆蓋率

**演示內容**:
- 合規性報告
- 組件分析
- 改進建議
- 實時檢測

---

### 7. 測試驗證系統

**位置**: 功能演示區  
**組件**: `TestValidationDashboard.jsx`  
**文檔**: [/docs/testing/validation_guide.md](/docs/testing/validation_guide.md)

**功能說明**:
- 自動化測試執行
- 測試結果可視化
- 覆蓋率分析
- 錯誤追蹤

**演示內容**:
- 測試套件管理
- 執行進度追蹤
- 結果分析圖表
- 報告生成

---

## 🔧 如何使用演示

### 在 ClaudeEditor 中訪問

1. **打開 ClaudeEditor**
   - 啟動 ClaudeEditor 應用
   - 確保版本為 v4.75 或更高

2. **進入演示中心**
   - 點擊中間欄的"演示中心"標籤
   - 或使用快捷鍵 `Cmd+D` (Mac) / `Ctrl+D` (Windows)

3. **選擇演示功能**
   - 從左側導航選擇要查看的功能
   - 點擊後在中間區域查看演示

4. **交互式體驗**
   - 每個演示都支持實時交互
   - 可以修改參數查看效果
   - 支持導出演示數據

### 本地開發測試

```bash
# 進入項目目錄
cd /Users/alexchuang/alexchuangtest/aicore0720

# 啟動本地演示服務器
cd deploy/v4.75
python3 enhanced_demo_server.py

# 訪問演示
open http://localhost:8080
```

---

## 📚 相關資源

### API 文檔
- [Smart Intervention API](/docs/api/smart_intervention.md)
- [StageWise API](/docs/api/stagewise.md)
- [Deployment API](/docs/api/deployment.md)
- [Workflow API](/docs/api/workflow.md)
- [Metrics API](/docs/api/metrics.md)
- [SmartUI API](/docs/api/smartui.md)
- [Testing API](/docs/api/testing.md)

### 集成指南
- [ClaudeEditor 集成指南](/docs/integration/claudeditor.md)
- [MCP 集成指南](/docs/integration/mcp.md)
- [GitHub Actions 集成](/docs/integration/github_actions.md)

### 最佳實踐
- [演示開發指南](/docs/guides/demo_development.md)
- [性能優化指南](/docs/guides/performance.md)
- [安全最佳實踐](/docs/guides/security.md)

---

## 🎯 下一步

1. **體驗演示**: 立即在 ClaudeEditor 中體驗所有功能
2. **查看源碼**: 所有演示組件源碼位於 `/core/components/demo_ui/`
3. **自定義開發**: 參考文檔創建自己的演示組件
4. **反饋改進**: 通過 GitHub Issues 提供反饋

---

*PowerAutomation v4.75 - 讓 AI 編程更智能、更高效、更經濟*