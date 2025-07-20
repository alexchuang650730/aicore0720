# ClaudeEditor 六大工作流集成指南

## 📋 概述

本指南說明如何將六大工作流功能集成到現有的 ClaudeEditor UI 中，採用增量設計方式，不破壞現有功能。

## 🏗️ 架構設計

### 三欄式佈局保持不變
- **左側**：AI控制區 / GitHub狀態區 / 快速操作區 / 六大工作流區
- **中間**：演示區及編輯區
- **右側**：AI助手區

### 核心改動
1. 增強左側面板，添加六大工作流區域
2. 保留所有現有功能
3. 新增工作流相關的狀態管理
4. 集成 MCP 狀態顯示

## 📦 文件結構

```
core/
└── components/
    └── claudeditor_ui/
        ├── EnhancedLeftDashboard.jsx  # 增強的左側面板
        ├── LeftDashboard.css          # 樣式文件
        ├── WorkflowService.js         # 工作流服務
        └── INTEGRATION_GUIDE.md       # 本文件
```

## 🔧 集成步驟

### 1. 更新 ClaudeEditor 的 App.jsx

```jsx
// claudeditor/src/App.jsx
import React, { useState, useEffect } from 'react';
// 使用增強版的 LeftDashboard
import LeftDashboard from '../../core/components/claudeditor_ui/EnhancedLeftDashboard';
import AIAssistant from './ai-assistant/AIAssistant';
import DualModeContainer from './components/DualModeContainer';
import TaskList from './components/TaskList';
import SmartUIService from './services/SmartUIService';
import './App.css';
import './styles/SmartUI.css';

function App() {
  // ... 現有代碼保持不變 ...
  
  return (
    <div className={`app smartui-${smartUIConfig.deviceType} smartui-${smartUIConfig.breakpoint}`}>
      <header className="app-header">
        <h1>ClaudeEditor</h1>
        <div className="smartui-indicator">
          <span className="device-info">
            📱 {smartUIConfig.deviceType} | {smartUIConfig.breakpoint}
          </span>
          <span className="version-info">SmartUI v4.7.3</span>
        </div>
      </header>

      <main className="app-main">
        {/* 使用增強的左側面板 */}
        <aside className="sidebar-left">
          <LeftDashboard />
        </aside>

        {/* 中間區域保持不變 */}
        <div className="main-content">
          <DualModeContainer />
        </div>

        {/* 右側面板保持不變 */}
        <aside className="sidebar-right">
          <AIAssistant />
        </aside>
      </main>
    </div>
  );
}

export default App;
```

### 2. 創建工作流服務

```javascript
// core/components/claudeditor_ui/WorkflowService.js
export class WorkflowService {
  constructor() {
    this.currentWorkflow = null;
    this.workflowStatus = 'idle';
    this.progress = 0;
    this.listeners = [];
  }

  startWorkflow(workflowId) {
    this.currentWorkflow = workflowId;
    this.workflowStatus = 'running';
    this.progress = 0;
    
    // 通知 PowerAutomation 核心
    window.powerautomation?.startWorkflow(workflowId);
    
    // 通知所有監聽器
    this.notifyListeners({
      type: 'workflow:started',
      workflow: workflowId
    });
  }

  updateProgress(progress) {
    this.progress = progress;
    this.notifyListeners({
      type: 'workflow:progress',
      workflow: this.currentWorkflow,
      progress: progress
    });
  }

  pauseWorkflow() {
    this.workflowStatus = 'paused';
    window.powerautomation?.pauseWorkflow();
  }

  resumeWorkflow() {
    this.workflowStatus = 'running';
    window.powerautomation?.resumeWorkflow();
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notifyListeners(event) {
    this.listeners.forEach(listener => listener(event));
  }
}

// 創建全局實例
export const workflowService = new WorkflowService();
```

### 3. 集成 MCP 狀態監控

```javascript
// core/components/claudeditor_ui/MCPStatusMonitor.js
export class MCPStatusMonitor {
  constructor() {
    this.mcpStatus = {
      codeflow_mcp: 'idle',
      test_mcp: 'idle',
      zen_mcp: 'idle',
      xmasters_mcp: 'idle',
      stagewise_mcp: 'idle',
      smartui_mcp: 'idle',
      ag_ui_mcp: 'idle'
    };
  }

  updateStatus(mcp, status) {
    this.mcpStatus[mcp] = status;
    
    // 發送狀態更新事件
    window.dispatchEvent(new CustomEvent('mcp:status', {
      detail: { mcp, status }
    }));
  }

  getStatus(mcp) {
    return this.mcpStatus[mcp] || 'unknown';
  }

  getActiveCount() {
    return Object.values(this.mcpStatus)
      .filter(status => status === 'active')
      .length;
  }
}

export const mcpMonitor = new MCPStatusMonitor();
```

### 4. 更新 package.json 依賴

```json
{
  "dependencies": {
    // ... 現有依賴 ...
    "zustand": "^4.4.1",  // 狀態管理
    "clsx": "^2.0.0"      // 樣式工具
  }
}
```

### 5. 添加工作流狀態管理

```javascript
// core/components/claudeditor_ui/useWorkflowStore.js
import { create } from 'zustand';

export const useWorkflowStore = create((set) => ({
  // 六大工作流定義
  workflows: [
    {
      id: 'requirement',
      name: '需求分析',
      icon: '📋',
      description: '分析代碼提取需求',
      mcps: ['CodeFlow', 'Stagewise'],
      status: 'idle',
      progress: 0
    },
    // ... 其他工作流 ...
  ],
  
  // 當前活動的工作流
  activeWorkflow: null,
  
  // 工作流狀態
  workflowStatus: 'idle', // idle, running, paused, completed
  
  // 操作方法
  startWorkflow: (workflowId) => set((state) => ({
    activeWorkflow: workflowId,
    workflowStatus: 'running',
    workflows: state.workflows.map(w => 
      w.id === workflowId 
        ? { ...w, status: 'running', progress: 0 }
        : w
    )
  })),
  
  updateProgress: (workflowId, progress) => set((state) => ({
    workflows: state.workflows.map(w => 
      w.id === workflowId 
        ? { ...w, progress }
        : w
    )
  })),
  
  pauseWorkflow: () => set({ workflowStatus: 'paused' }),
  
  resumeWorkflow: () => set({ workflowStatus: 'running' }),
  
  completeWorkflow: (workflowId) => set((state) => ({
    workflows: state.workflows.map(w => 
      w.id === workflowId 
        ? { ...w, status: 'completed', progress: 100 }
        : w
    )
  }))
}));
```

## 🎨 樣式集成

### 更新主題以支持新功能

```css
/* claudeditor/src/App.css - 添加以下樣式 */

/* 左側面板寬度調整 */
.sidebar-left {
  width: 260px;
  min-width: 260px;
  max-width: 260px;
}

/* 響應式適配 */
@media (max-width: 1024px) {
  .sidebar-left {
    width: 220px;
    min-width: 220px;
  }
}

/* 暗色主題支持 */
@media (prefers-color-scheme: dark) {
  .left-dashboard.enhanced {
    background: #1e1e1e;
    color: #d4d4d4;
  }
  
  .dashboard-section {
    background: #2d2d2d;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  }
}
```

## 🔌 後端集成

### PowerAutomation 核心通信

```javascript
// 在 window 對象上掛載 PowerAutomation API
window.powerautomation = {
  startWorkflow: async (workflowId) => {
    const response = await fetch('/api/workflow/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workflowId })
    });
    return response.json();
  },
  
  pauseWorkflow: async () => {
    // 實現暫停邏輯
  },
  
  resumeWorkflow: async () => {
    // 實現恢復邏輯
  },
  
  getWorkflowStatus: async (workflowId) => {
    // 獲取工作流狀態
  }
};
```

## ✅ 測試檢查清單

- [ ] 左側面板正確顯示四個區域
- [ ] AI 控制區可以切換模型
- [ ] GitHub 狀態實時更新
- [ ] 快速操作命令正常工作
- [ ] 六大工作流可以啟動和暫停
- [ ] MCP 狀態指示器正確顯示
- [ ] 工作流進度條正確更新
- [ ] 成本監控數據準確
- [ ] 響應式設計在不同螢幕正常
- [ ] 暗色主題正確顯示

## 🚀 部署注意事項

1. **向後兼容**：確保所有現有功能正常工作
2. **性能優化**：工作流狀態更新使用防抖處理
3. **錯誤處理**：添加工作流執行失敗的處理
4. **日誌記錄**：記錄所有工作流操作
5. **配置管理**：支持工作流配置的動態更新

## 📝 後續優化

1. 添加工作流模板功能
2. 支持自定義工作流
3. 添加工作流執行歷史
4. 集成更多 MCP 功能
5. 優化移動端體驗