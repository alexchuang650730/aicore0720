# ClaudeEditor MCP UI組件整合清單

## 🎯 指導原則
> UI組件最好都在ClaudeEditor MCP裡，其他的MCP是驅動UI的

## 📦 當前UI組件分佈（需要整合）

### ✅ 已在正確位置的組件
- `core/components/claudeeditor_ui/EnhancedLeftDashboard.jsx`
- `core/components/claudeeditor_ui/MCPZeroStatusPanel.jsx`
- `core/components/claudeeditor_ui/ClaudeEditorMainView.jsx`
- `core/components/claudeeditor_ui/SixWorkflowSidebar.jsx`

### 🔄 需要遷移的組件

#### 從 demo_ui/ 遷移到 claudeeditor_mcp/
1. `demo_ui/MetricsTrackingDashboard.jsx` → `claudeeditor_mcp/ui/MetricsTrackingDashboard.jsx`
2. `demo_ui/StageWiseCommandDemo.jsx` → `claudeeditor_mcp/ui/StageWiseCommandDemo.jsx`
3. `demo_ui/UnifiedDeploymentUI.jsx` → `claudeeditor_mcp/ui/UnifiedDeploymentUI.jsx`
4. `demo_ui/WorkflowAutomationDashboard.jsx` → `claudeeditor_mcp/ui/WorkflowAutomationDashboard.jsx`
5. `demo_ui/SmartInterventionDemo.jsx` → `claudeeditor_mcp/ui/SmartInterventionDemo.jsx`
6. `demo_ui/ClaudeEditorDemoPanel.jsx` → `claudeeditor_mcp/ui/ClaudeEditorDemoPanel.jsx`

#### 從 codeflow_mcp/ 遷移到 claudeeditor_mcp/
1. `codeflow_mcp/frontend_integration_enhancement.jsx` → `claudeeditor_mcp/ui/CodeFlowPanel.jsx`

### 🔧 需要保留在其他MCP的驅動邏輯

#### CodeFlow MCP (驅動邏輯)
- 代碼生成邏輯
- 工作流協調
- API接口

#### SmartUI MCP (驅動邏輯)
- UI生成算法
- 無障礙性處理
- 響應式邏輯

#### Stagewise MCP (驅動邏輯)
- 端到端測試邏輯
- 命令執行
- 狀態管理

## 🏗️ 新的ClaudeEditor MCP結構

```
core/components/claudeeditor_mcp/
├── ui/                          # 所有UI組件
│   ├── panels/                  # 面板組件
│   │   ├── LeftDashboard.jsx
│   │   ├── CenterEditor.jsx
│   │   └── RightAssistant.jsx
│   ├── demo/                    # 演示相關UI
│   │   ├── MetricsTrackingDashboard.jsx
│   │   ├── StageWiseCommandDemo.jsx
│   │   ├── UnifiedDeploymentUI.jsx
│   │   ├── WorkflowAutomationDashboard.jsx
│   │   ├── SmartInterventionDemo.jsx
│   │   └── ClaudeEditorDemoPanel.jsx
│   ├── workflows/               # 工作流UI
│   │   ├── SixWorkflowSidebar.jsx
│   │   └── WorkflowControls.jsx
│   ├── codeflow/               # CodeFlow相關UI
│   │   └── CodeFlowPanel.jsx
│   └── shared/                 # 共享UI組件
│       ├── StatusPanel.jsx
│       └── PerformanceMetrics.jsx
├── api/                        # ClaudeEditor API接口
├── drivers/                    # 各MCP驅動接口
│   ├── codeflow_driver.py
│   ├── smartui_driver.py
│   ├── stagewise_driver.py
│   └── smart_intervention_driver.py
├── main.py                     # ClaudeEditor MCP主入口
└── config.json                 # 配置文件
```

## 🔄 遷移步驟

1. **創建統一的ClaudeEditor MCP結構**
2. **遷移UI組件到新位置**
3. **建立驅動接口連接其他MCP**
4. **移除其他MCP中的UI組件**
5. **更新導入路徑和依賴**
6. **測試集成功能**

## 🎯 驅動邏輯保留原則

### CodeFlow MCP 保留：
- 代碼生成引擎
- AST解析邏輯
- 模板系統
- API端點

### SmartUI MCP 保留：
- UI生成算法
- 無障礙性分析
- 響應式計算
- 主題系統

### Stagewise MCP 保留：
- 測試執行引擎
- 命令協調器
- 狀態機管理
- 結果聚合

### Smart Intervention 保留：
- 需求檢測算法
- 觸發邏輯
- 路由規則
- 性能監控

## 📋 驗證清單

- [ ] 所有UI組件集中在ClaudeEditor MCP
- [ ] 其他MCP只保留驅動邏輯
- [ ] API接口正常工作
- [ ] 三欄式界面功能完整
- [ ] 演示系統正常運行
- [ ] 性能指標正常