#!/bin/bash

# PowerAutomation v4.75 本地部署腳本

echo "╔══════════════════════════════════════════════════════════╗"
echo "║      PowerAutomation v4.75 本地部署                      ║"
echo "║      Claude Code Tool + ClaudeEditor 集成                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 設置變量
DEPLOY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname $(dirname $DEPLOY_DIR))"
LOG_FILE="$DEPLOY_DIR/deployment_$(date +%Y%m%d_%H%M%S).log"

# 日誌函數
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 錯誤處理
handle_error() {
    log "❌ 錯誤: $1"
    exit 1
}

# 1. 環境檢查
log "📋 執行環境檢查..."

# 檢查 Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log "✅ Node.js $NODE_VERSION"
else
    handle_error "Node.js 未安裝"
fi

# 檢查 Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log "✅ $PYTHON_VERSION"
else
    handle_error "Python3 未安裝"
fi

# 檢查 npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    log "✅ npm $NPM_VERSION"
else
    handle_error "npm 未安裝"
fi

# 2. 創建必要的目錄
log ""
log "📁 創建目錄結構..."

mkdir -p "$ROOT_DIR/logs"
mkdir -p "$ROOT_DIR/data/metrics"
mkdir -p "$ROOT_DIR/data/training"
mkdir -p "$ROOT_DIR/temp"

# 3. 安裝依賴（如果需要）
log ""
log "📦 檢查依賴..."

# 創建 package.json（如果不存在）
if [ ! -f "$DEPLOY_DIR/package.json" ]; then
    cat > "$DEPLOY_DIR/package.json" << EOF
{
  "name": "powerautomation-v475",
  "version": "4.75.0",
  "description": "PowerAutomation v4.75 - Claude Code Tool + ClaudeEditor Integration",
  "scripts": {
    "start": "node server.js",
    "demo": "python3 enhanced_demo_server.py",
    "test": "python3 verify_deployment.py",
    "metrics": "python3 workflow_automation_metrics.py"
  },
  "dependencies": {
    "express": "^4.18.0",
    "ws": "^8.0.0",
    "cors": "^2.8.0"
  }
}
EOF
    log "✅ 創建 package.json"
fi

# 4. 配置本地服務
log ""
log "🔧 配置本地服務..."

# 創建簡單的服務器
cat > "$DEPLOY_DIR/server.js" << 'EOF'
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// 中間件
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// API 路由
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy',
        version: '4.75',
        timestamp: new Date().toISOString()
    });
});

app.get('/api/deployment-manifest', (req, res) => {
    const manifestPath = path.join(__dirname, 'deployment_ui_manifest.json');
    if (fs.existsSync(manifestPath)) {
        const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
        res.json(manifest);
    } else {
        res.status(404).json({ error: 'Manifest not found' });
    }
});

app.get('/api/metrics', (req, res) => {
    const metricsPath = path.join(__dirname, 'workflow_automation_metrics.json');
    if (fs.existsSync(metricsPath)) {
        const metrics = JSON.parse(fs.readFileSync(metricsPath, 'utf8'));
        res.json(metrics);
    } else {
        res.status(404).json({ error: 'Metrics not found' });
    }
});

// 演示路由
app.get('/demo/:type', (req, res) => {
    res.json({
        demo: req.params.type,
        status: 'ready',
        message: '請使用演示 UI 查看完整功能'
    });
});

// 啟動服務器
app.listen(PORT, () => {
    console.log(`
╔══════════════════════════════════════════════════════════╗
║      PowerAutomation v4.75 服務器已啟動                  ║
╚══════════════════════════════════════════════════════════╝

🌐 訪問地址:
   - API 健康檢查: http://localhost:${PORT}/api/health
   - 部署清單: http://localhost:${PORT}/api/deployment-manifest
   - 指標數據: http://localhost:${PORT}/api/metrics
   
📊 演示系統:
   - Python 演示服務器: python3 enhanced_demo_server.py
   - 驗證部署: python3 verify_deployment.py
   
按 Ctrl+C 停止服務器
`);
});
EOF

log "✅ 創建服務器配置"

# 5. 啟動服務
log ""
log "🚀 啟動本地服務..."

# 檢查端口是否被佔用
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    log "⚠️ 端口 3000 已被佔用，嘗試使用端口 3001"
    export PORT=3001
fi

# 啟動 Python 演示服務器
log "啟動演示服務器..."
cd "$DEPLOY_DIR"
python3 enhanced_demo_server.py &
DEMO_PID=$!
log "演示服務器 PID: $DEMO_PID"

# 保存 PID 以便後續關閉
echo $DEMO_PID > "$DEPLOY_DIR/.demo_server.pid"

# 6. 運行驗證
log ""
log "🧪 運行部署驗證..."
cd "$DEPLOY_DIR"
python3 verify_deployment.py

# 7. 顯示部署信息
log ""
log "✅ PowerAutomation v4.75 本地部署完成！"
log ""
log "📋 部署信息:"
log "   - 部署目錄: $DEPLOY_DIR"
log "   - 日誌文件: $LOG_FILE"
log "   - 演示服務器: http://localhost:8080"
log ""
log "🚀 快速開始:"
log "   1. 訪問演示系統: http://localhost:8080"
log "   2. 查看 API: http://localhost:3000/api/health"
log "   3. 運行測試: cd $DEPLOY_DIR && python3 verify_deployment.py"
log ""
log "📚 相關文檔:"
log "   - 部署總結: $DEPLOY_DIR/DEPLOYMENT_SUMMARY.md"
log "   - 架構說明: $ROOT_DIR/ARCHITECTURE.md"
log "   - 文檔目錄: $ROOT_DIR/docs/README.md"
log ""
log "⚠️ 停止服務:"
log "   kill $DEMO_PID  # 停止演示服務器"

# 創建停止腳本
cat > "$DEPLOY_DIR/stop_services.sh" << EOF
#!/bin/bash
# 停止 PowerAutomation v4.75 服務

if [ -f "$DEPLOY_DIR/.demo_server.pid" ]; then
    PID=\$(cat "$DEPLOY_DIR/.demo_server.pid")
    if ps -p \$PID > /dev/null; then
        kill \$PID
        echo "✅ 演示服務器已停止"
    fi
    rm "$DEPLOY_DIR/.demo_server.pid"
fi

echo "✅ 所有服務已停止"
EOF

chmod +x "$DEPLOY_DIR/stop_services.sh"
log ""
log "💡 使用 ./stop_services.sh 停止所有服務"