#!/bin/bash
# ClaudeEditor 六大工作流集成部署腳本

echo "🚀 開始部署 ClaudeEditor 六大工作流集成..."

# 設置變量
PROJECT_ROOT=$(pwd)
CORE_UI_DIR="$PROJECT_ROOT/core/components/claudeditor_ui"
CLAUDEDITOR_DIR="$PROJECT_ROOT/claudeditor"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment/v4.73"

# 創建必要的目錄
echo "📁 創建目錄結構..."
mkdir -p "$CORE_UI_DIR"
mkdir -p "$DEPLOYMENT_DIR/logs"
mkdir -p "$DEPLOYMENT_DIR/backup"

# 備份現有文件
echo "💾 備份現有文件..."
if [ -f "$CLAUDEDITOR_DIR/src/components/LeftDashboard.jsx" ]; then
    cp "$CLAUDEDITOR_DIR/src/components/LeftDashboard.jsx" \
       "$DEPLOYMENT_DIR/backup/LeftDashboard.jsx.$(date +%Y%m%d_%H%M%S)"
fi

# 創建符號鏈接（保持原有結構，但使用新的增強版本）
echo "🔗 創建符號鏈接..."
ln -sf "$CORE_UI_DIR/EnhancedLeftDashboard.jsx" \
       "$CLAUDEDITOR_DIR/src/components/LeftDashboard.jsx"

# 複製樣式文件
echo "🎨 複製樣式文件..."
cp "$CORE_UI_DIR/LeftDashboard.css" \
   "$CLAUDEDITOR_DIR/src/components/"

# 安裝依賴
echo "📦 安裝依賴..."
cd "$CLAUDEDITOR_DIR"
npm install zustand clsx

# 創建工作流服務
echo "⚙️ 創建工作流服務..."
cat > "$CLAUDEDITOR_DIR/src/services/WorkflowService.js" << 'EOF'
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

export const workflowService = new WorkflowService();
EOF

# 創建部署配置
echo "📋 創建部署配置..."
cat > "$DEPLOYMENT_DIR/claudeditor_config.json" << EOF
{
  "version": "4.7.3",
  "features": {
    "sixWorkflows": true,
    "aiControl": true,
    "githubIntegration": true,
    "quickActions": true
  },
  "mcpIntegration": {
    "codeflow": true,
    "test": true,
    "zen": true,
    "xmasters": true,
    "stagewise": true,
    "smartui": true,
    "agui": true
  },
  "deployment": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "environment": "production"
  }
}
EOF

# 構建項目
echo "🔨 構建項目..."
cd "$CLAUDEDITOR_DIR"
npm run build

# 生成部署報告
echo "📊 生成部署報告..."
cat > "$DEPLOYMENT_DIR/deployment_report.md" << EOF
# ClaudeEditor v4.7.3 部署報告

## 部署信息
- **時間**: $(date)
- **版本**: v4.7.3
- **功能**: 六大工作流集成

## 已部署組件
- ✅ EnhancedLeftDashboard.jsx
- ✅ LeftDashboard.css
- ✅ WorkflowService.js
- ✅ 工作流狀態管理
- ✅ MCP 集成

## 文件結構
\`\`\`
core/
└── components/
    └── claudeditor_ui/
        ├── EnhancedLeftDashboard.jsx
        ├── LeftDashboard.css
        ├── WorkflowService.js
        └── INTEGRATION_GUIDE.md

deployment/
└── v4.73/
    ├── claudeditor_config.json
    ├── deployment_report.md
    └── backup/
        └── LeftDashboard.jsx.[timestamp]
\`\`\`

## 測試檢查
- [ ] 左側面板正確顯示
- [ ] 六大工作流可以啟動
- [ ] MCP 狀態正確顯示
- [ ] 成本監控正常工作
- [ ] GitHub 集成正常

## 下一步
1. 運行集成測試
2. 驗證所有功能
3. 監控系統性能
4. 收集用戶反饋
EOF

echo "✅ 部署完成！"
echo ""
echo "📝 後續步驟："
echo "1. 運行 ClaudeEditor: cd claudeditor && npm run dev"
echo "2. 檢查左側面板是否正確顯示六大工作流"
echo "3. 測試工作流啟動和執行"
echo "4. 查看部署報告: $DEPLOYMENT_DIR/deployment_report.md"