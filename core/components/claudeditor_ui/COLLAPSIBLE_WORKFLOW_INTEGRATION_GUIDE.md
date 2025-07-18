# 六大工作流折疊式UI集成指南

## 概述

為了避免左側工作區過長，六大工作流區域採用了折疊式設計。用戶可以通過點擊標題來展開或折疊工作流列表。

## 實現要點

### 1. 狀態管理

```jsx
// 添加折疊狀態
const [workflowsExpanded, setWorkflowsExpanded] = useState(false);
```

### 2. 標題交互

```jsx
<h3 
  className="collapsible-header"
  onClick={() => setWorkflowsExpanded(!workflowsExpanded)}
  style={{ cursor: 'pointer', userSelect: 'none' }}
>
  <span>🚀 六大工作流</span>
  <span style={{ float: 'right', fontSize: '0.8em' }}>
    {workflowsExpanded ? '▼' : '▶'}
  </span>
</h3>
```

### 3. 條件渲染

- **折疊時**：顯示當前活躍工作流的摘要
- **展開時**：顯示完整的工作流列表

```jsx
{/* 折疊時的摘要 */}
{!workflowsExpanded && activeWorkflow && (
  <div className="workflow-summary">
    <span className="summary-icon">{icon}</span>
    <span className="summary-text">{name} - 執行中</span>
    <span className="summary-progress">{progress}%</span>
  </div>
)}

{/* 展開時的完整內容 */}
{workflowsExpanded && (
  <div className="workflows-expanded">
    {/* 工作流列表 */}
  </div>
)}
```

### 4. 樣式優化

```css
/* 折疊動畫 */
.workflows-expanded {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}
```

## 使用場景

### 默認狀態
- 初始加載時，工作流區域默認為**折疊狀態**
- 顯示當前活躍工作流的簡要信息

### 用戶交互
1. 點擊標題可切換折疊/展開狀態
2. 鼠標懸停在標題上有視覺反饋
3. 箭頭圖標指示當前狀態（▶ 折疊，▼ 展開）

### 自動展開場景
- 當用戶首次啟動工作流時
- 當工作流出現錯誤需要用戶關注時
- 當用戶通過快捷鍵（如 Ctrl+W）觸發時

## 集成步驟

1. **更新組件文件**
   - `/core/components/claudeditor_ui/EnhancedLeftDashboard.jsx`
   - 添加折疊狀態和相關邏輯

2. **更新樣式文件**
   - `/core/components/claudeditor_ui/LeftDashboard.css`
   - 添加折疊動畫和相關樣式

3. **測試功能**
   - 確保折疊/展開動畫流暢
   - 驗證狀態持久化（可選）
   - 測試不同屏幕尺寸下的表現

## 優化建議

1. **狀態持久化**：將折疊狀態保存到 localStorage
   ```jsx
   useEffect(() => {
     const saved = localStorage.getItem('workflowsExpanded');
     if (saved !== null) {
       setWorkflowsExpanded(JSON.parse(saved));
     }
   }, []);
   
   useEffect(() => {
     localStorage.setItem('workflowsExpanded', JSON.stringify(workflowsExpanded));
   }, [workflowsExpanded]);
   ```

2. **鍵盤快捷鍵**：添加快捷鍵支持（如 Ctrl+W）
   ```jsx
   useEffect(() => {
     const handleKeyPress = (e) => {
       if (e.ctrlKey && e.key === 'w') {
         setWorkflowsExpanded(prev => !prev);
       }
     };
     window.addEventListener('keydown', handleKeyPress);
     return () => window.removeEventListener('keydown', handleKeyPress);
   }, []);
   ```

3. **智能展開**：根據工作流狀態自動展開
   ```jsx
   useEffect(() => {
     // 當有工作流失敗時自動展開
     if (sixWorkflows.some(w => w.status === 'failed')) {
       setWorkflowsExpanded(true);
     }
   }, [sixWorkflows]);
   ```

## 演示

查看 `claudeditor_collapsible_workflow_demo.html` 文件以查看實際效果。

## 注意事項

1. 確保折疊狀態不影響工作流的實際執行
2. 保持摘要信息的實時更新
3. 在移動設備上可能需要不同的交互方式
4. 考慮添加過渡動畫以提升用戶體驗