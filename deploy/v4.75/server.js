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
