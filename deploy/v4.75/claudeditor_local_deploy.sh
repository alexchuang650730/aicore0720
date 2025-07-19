#!/bin/bash

# PowerAutomation v4.75 - ClaudeEditor 本地部署
# 部署到 ClaudeEditor 的三欄式界面中

echo "╔══════════════════════════════════════════════════════════╗"
echo "║    PowerAutomation v4.75 - ClaudeEditor 集成部署         ║"
echo "║    左欄：六大工作流 | 中間：演示編輯區 | 右欄：AI助手     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 設置變量
DEPLOY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname $(dirname $DEPLOY_DIR))"
CLAUDEDITOR_DIR="$ROOT_DIR/claudeditor"
LOG_FILE="$DEPLOY_DIR/claudeditor_deployment_$(date +%Y%m%d_%H%M%S).log"

# 日誌函數
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 錯誤處理
handle_error() {
    log "❌ 錯誤: $1"
    exit 1
}

# 1. 檢查 ClaudeEditor 目錄
log "📋 檢查 ClaudeEditor 環境..."

if [ ! -d "$CLAUDEDITOR_DIR" ]; then
    log "創建 ClaudeEditor 目錄結構..."
    mkdir -p "$CLAUDEDITOR_DIR"
fi

# 2. 配置 ClaudeEditor 工作流面板（左下角）
log ""
log "🔧 配置六大工作流面板..."

# 創建工作流配置
cat > "$CLAUDEDITOR_DIR/workflow_panel_config.json" << 'EOF'
{
  "workflows": [
    {
      "id": "requirement_analysis",
      "name": "需求分析",
      "icon": "📋",
      "shortcut": "cmd+1",
      "description": "從用戶需求到技術規格"
    },
    {
      "id": "ui_generation",
      "name": "UI 生成",
      "icon": "🎨",
      "shortcut": "cmd+2",
      "description": "SmartUI 組件自動生成"
    },
    {
      "id": "code_optimization",
      "name": "代碼優化",
      "icon": "⚡",
      "shortcut": "cmd+3",
      "description": "K2 模型智能優化"
    },
    {
      "id": "test_automation",
      "name": "測試自動化",
      "icon": "🧪",
      "shortcut": "cmd+4",
      "description": "全面測試覆蓋"
    },
    {
      "id": "deployment",
      "name": "部署發布",
      "icon": "🚀",
      "shortcut": "cmd+5",
      "description": "一鍵部署系統"
    },
    {
      "id": "monitoring_feedback",
      "name": "監控反饋",
      "icon": "📊",
      "shortcut": "cmd+6",
      "description": "實時監控和反饋"
    }
  ]
}
EOF

log "✅ 工作流面板配置完成"

# 3. 配置中間演示編輯區
log ""
log "🎯 配置中間演示編輯區..."

# 創建演示區配置
cat > "$CLAUDEDITOR_DIR/demo_editor_config.json" << 'EOF'
{
  "editor": {
    "defaultView": "demo",
    "views": {
      "demo": {
        "component": "ClaudeEditorDemoPanel",
        "path": "core/components/demo_ui/ClaudeEditorDemoPanel.jsx"
      },
      "code": {
        "component": "CodeEditor",
        "features": ["syntax-highlight", "auto-complete", "k2-suggestions"]
      },
      "preview": {
        "component": "LivePreview",
        "features": ["hot-reload", "responsive-view"]
      }
    }
  },
  "demos": {
    "stagewise": {
      "component": "StageWiseCommandDemo",
      "path": "core/components/demo_ui/StageWiseCommandDemo.jsx"
    },
    "deployment": {
      "component": "UnifiedDeploymentUI",
      "path": "core/components/demo_ui/UnifiedDeploymentUI.jsx"
    },
    "workflow": {
      "component": "WorkflowAutomationDashboard",
      "path": "core/components/demo_ui/WorkflowAutomationDashboard.jsx"
    },
    "metrics": {
      "component": "MetricsVisualizationDashboard",
      "path": "core/components/demo_ui/MetricsVisualizationDashboard.jsx"
    }
  }
}
EOF

log "✅ 演示編輯區配置完成"

# 4. 配置 AI 助手（右欄）
log ""
log "🤖 配置 AI 助手面板..."

cat > "$CLAUDEDITOR_DIR/ai_assistant_config.json" << 'EOF'
{
  "assistant": {
    "models": {
      "default": "claude-3-opus",
      "k2": {
        "enabled": true,
        "auto_switch": true,
        "threshold": 1000
      }
    },
    "features": {
      "code_suggestions": true,
      "error_fixes": true,
      "refactoring": true,
      "documentation": true,
      "test_generation": true
    },
    "integration": {
      "mcp_server": "http://localhost:3001",
      "demo_mcp": "core/components/demo_mcp.py"
    }
  }
}
EOF

log "✅ AI 助手配置完成"

# 5. 創建 ClaudeEditor 啟動腳本
log ""
log "🚀 創建 ClaudeEditor 啟動配置..."

cat > "$CLAUDEDITOR_DIR/start_claudeditor.js" << 'EOF'
// ClaudeEditor v4.75 啟動腳本

const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

// 配置
const config = {
  title: 'ClaudeEditor - PowerAutomation v4.75',
  width: 1600,
  height: 1000,
  minWidth: 1200,
  minHeight: 800,
  webPreferences: {
    nodeIntegration: true,
    contextIsolation: false
  }
};

// 創建主窗口
function createWindow() {
  const mainWindow = new BrowserWindow(config);
  
  // 加載主頁面
  mainWindow.loadFile('index.html');
  
  // 開發模式下打開開發者工具
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

// 應用就緒
app.whenReady().then(createWindow);

// 所有窗口關閉時退出
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
EOF

# 6. 創建主頁面
cat > "$CLAUDEDITOR_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ClaudeEditor - PowerAutomation v4.75</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            height: 100vh;
            overflow: hidden;
        }
        
        .container {
            display: flex;
            height: 100vh;
        }
        
        /* 左欄 - 工作流 */
        .left-panel {
            width: 250px;
            background: #1e1e1e;
            color: white;
            display: flex;
            flex-direction: column;
        }
        
        .workflow-section {
            flex: 1;
            display: flex;
            flex-direction: column;
            margin-top: auto;
            padding: 20px;
        }
        
        .workflow-title {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 15px;
            opacity: 0.8;
        }
        
        .workflow-item {
            padding: 10px 15px;
            margin: 5px 0;
            background: rgba(255,255,255,0.1);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .workflow-item:hover {
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
        }
        
        .workflow-item.active {
            background: #007acc;
        }
        
        /* 中間欄 - 演示編輯區 */
        .center-panel {
            flex: 1;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
        }
        
        .editor-tabs {
            background: white;
            border-bottom: 1px solid #ddd;
            display: flex;
            padding: 0 20px;
        }
        
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        
        .tab:hover {
            background: #f0f0f0;
        }
        
        .tab.active {
            border-bottom-color: #007acc;
            color: #007acc;
        }
        
        .editor-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        
        /* 右欄 - AI 助手 */
        .right-panel {
            width: 350px;
            background: white;
            border-left: 1px solid #ddd;
            display: flex;
            flex-direction: column;
        }
        
        .ai-header {
            padding: 20px;
            border-bottom: 1px solid #ddd;
        }
        
        .ai-chat {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        
        .ai-input {
            padding: 20px;
            border-top: 1px solid #ddd;
        }
        
        .ai-input textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            resize: none;
            font-family: inherit;
        }
        
        /* 演示內容 */
        .demo-content {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .demo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .demo-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s;
            cursor: pointer;
        }
        
        .demo-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 左欄：六大工作流 -->
        <div class="left-panel">
            <div class="workflow-section">
                <div class="workflow-title">六大工作流</div>
                <div class="workflow-item active" data-workflow="requirement">
                    <span>📋</span> 需求分析
                </div>
                <div class="workflow-item" data-workflow="ui">
                    <span>🎨</span> UI 生成
                </div>
                <div class="workflow-item" data-workflow="optimization">
                    <span>⚡</span> 代碼優化
                </div>
                <div class="workflow-item" data-workflow="test">
                    <span>🧪</span> 測試自動化
                </div>
                <div class="workflow-item" data-workflow="deployment">
                    <span>🚀</span> 部署發布
                </div>
                <div class="workflow-item" data-workflow="monitoring">
                    <span>📊</span> 監控反饋
                </div>
            </div>
        </div>
        
        <!-- 中間欄：演示編輯區 -->
        <div class="center-panel">
            <div class="editor-tabs">
                <div class="tab active">演示中心</div>
                <div class="tab">代碼編輯</div>
                <div class="tab">實時預覽</div>
            </div>
            <div class="editor-content">
                <div class="demo-content">
                    <h2>PowerAutomation v4.75 演示中心</h2>
                    <p>在 ClaudeEditor 中體驗所有核心功能</p>
                    
                    <div class="demo-grid">
                        <div class="demo-card">
                            <h3>🎮 StageWise 控制</h3>
                            <p>Claude Code Tool 命令兼容性測試</p>
                        </div>
                        <div class="demo-card">
                            <h3>🚀 統一部署</h3>
                            <p>一鍵部署管理系統</p>
                        </div>
                        <div class="demo-card">
                            <h3>📊 工作流自動化</h3>
                            <p>六大工作流指標監控</p>
                        </div>
                        <div class="demo-card">
                            <h3>📈 指標可視化</h3>
                            <p>綜合指標仪表板</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 右欄：AI 助手 -->
        <div class="right-panel">
            <div class="ai-header">
                <h3>AI 助手</h3>
                <p style="font-size: 12px; color: #666; margin-top: 5px;">
                    Claude 3 Opus | K2 優化器已啟用
                </p>
            </div>
            <div class="ai-chat">
                <div style="text-align: center; color: #999; padding: 40px;">
                    <p>👋 我是你的 AI 編程助手</p>
                    <p style="font-size: 14px; margin-top: 10px;">
                        可以幫助你進行代碼生成、優化、測試等任務
                    </p>
                </div>
            </div>
            <div class="ai-input">
                <textarea rows="3" placeholder="輸入你的問題..."></textarea>
            </div>
        </div>
    </div>
    
    <script>
        // 工作流切換
        document.querySelectorAll('.workflow-item').forEach(item => {
            item.addEventListener('click', function() {
                document.querySelectorAll('.workflow-item').forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                console.log('切換到工作流:', this.dataset.workflow);
            });
        });
        
        // 標籤切換
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
        
        // 演示卡片點擊
        document.querySelectorAll('.demo-card').forEach(card => {
            card.addEventListener('click', function() {
                console.log('打開演示:', card.querySelector('h3').textContent);
            });
        });
    </script>
</body>
</html>
EOF

log "✅ ClaudeEditor 主頁面創建完成"

# 7. 創建開發服務器（用於本地測試）
log ""
log "🌐 創建開發服務器..."

cat > "$CLAUDEDITOR_DIR/dev_server.js" << 'EOF'
const express = require('express');
const path = require('path');
const app = express();
const PORT = 3456;

// 靜態文件服務
app.use(express.static(__dirname));
app.use('/core', express.static(path.join(__dirname, '../core')));
app.use('/deploy', express.static(path.join(__dirname, '../deploy')));

// API 路由
app.get('/api/workflow/status', (req, res) => {
    res.json({
        workflows: ['requirement', 'ui', 'optimization', 'test', 'deployment', 'monitoring'],
        status: 'all_ready'
    });
});

app.get('/api/demo/list', (req, res) => {
    res.json({
        demos: [
            { id: 'stagewise', name: 'StageWise 控制', status: 'ready' },
            { id: 'deployment', name: '統一部署', status: 'ready' },
            { id: 'workflow', name: '工作流自動化', status: 'ready' },
            { id: 'metrics', name: '指標可視化', status: 'ready' }
        ]
    });
});

app.listen(PORT, () => {
    console.log(`
╔══════════════════════════════════════════════════════════╗
║     ClaudeEditor 開發服務器已啟動                        ║
╚══════════════════════════════════════════════════════════╝

🌐 訪問地址: http://localhost:${PORT}
📁 項目目錄: ${__dirname}

✨ 功能說明:
   - 左欄：六大工作流控制面板
   - 中間：演示和編輯區域
   - 右欄：AI 助手（Claude/K2）

按 Ctrl+C 停止服務器
`);
});
EOF

# 8. 創建 package.json
cat > "$CLAUDEDITOR_DIR/package.json" << EOF
{
  "name": "claudeditor-v475",
  "version": "4.75.0",
  "description": "ClaudeEditor with PowerAutomation v4.75",
  "main": "start_claudeditor.js",
  "scripts": {
    "start": "node dev_server.js",
    "electron": "electron .",
    "dev": "NODE_ENV=development electron ."
  },
  "dependencies": {
    "express": "^4.18.0",
    "electron": "^22.0.0"
  }
}
EOF

# 9. 啟動開發服務器
log ""
log "🚀 啟動 ClaudeEditor 開發服務器..."

cd "$CLAUDEDITOR_DIR"

# 檢查 node_modules
if [ ! -d "node_modules" ]; then
    log "安裝依賴..."
    npm install express
fi

# 啟動服務器
node dev_server.js &
SERVER_PID=$!

# 保存 PID
echo $SERVER_PID > "$CLAUDEDITOR_DIR/.server.pid"

# 10. 生成部署報告
log ""
log "📊 生成部署報告..."

cat > "$DEPLOY_DIR/CLAUDEDITOR_DEPLOYMENT_REPORT.md" << EOF
# ClaudeEditor v4.75 本地部署報告

## 部署成功 ✅

**時間**: $(date '+%Y-%m-%d %H:%M:%S')
**服務器 PID**: $SERVER_PID
**訪問地址**: http://localhost:3456

## 三欄式界面結構

### 左欄：六大工作流（左下角）
- 📋 需求分析
- 🎨 UI 生成
- ⚡ 代碼優化
- 🧪 測試自動化
- 🚀 部署發布
- 📊 監控反饋

### 中間欄：演示編輯區
- 演示中心（默認視圖）
- 代碼編輯器
- 實時預覽

### 右欄：AI 助手
- Claude 3 Opus（默認）
- K2 優化器（自動切換）
- 實時代碼建議

## 配置文件

- 工作流配置: $CLAUDEDITOR_DIR/workflow_panel_config.json
- 演示區配置: $CLAUDEDITOR_DIR/demo_editor_config.json
- AI 助手配置: $CLAUDEDITOR_DIR/ai_assistant_config.json

## 停止服務

\`\`\`bash
kill $SERVER_PID
\`\`\`

或使用：

\`\`\`bash
cd $DEPLOY_DIR
./stop_claudeditor.sh
\`\`\`
EOF

# 創建停止腳本
cat > "$DEPLOY_DIR/stop_claudeditor.sh" << EOF
#!/bin/bash
if [ -f "$CLAUDEDITOR_DIR/.server.pid" ]; then
    PID=\$(cat "$CLAUDEDITOR_DIR/.server.pid")
    if ps -p \$PID > /dev/null; then
        kill \$PID
        echo "✅ ClaudeEditor 服務器已停止"
    fi
    rm "$CLAUDEDITOR_DIR/.server.pid"
fi
EOF

chmod +x "$DEPLOY_DIR/stop_claudeditor.sh"

log ""
log "✅ ClaudeEditor v4.75 部署完成！"
log ""
log "🌐 訪問 http://localhost:3456 查看 ClaudeEditor"
log "📁 項目目錄: $CLAUDEDITOR_DIR"
log "📊 部署報告: $DEPLOY_DIR/CLAUDEDITOR_DEPLOYMENT_REPORT.md"