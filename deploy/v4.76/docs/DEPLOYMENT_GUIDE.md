# PowerAutomation v4.76 部署指南

## 📋 系統要求

### 最低配置
- **Node.js**: 18.0+ (推薦 18.20.8)
- **Python**: 3.9+ (推薦 3.13.3)  
- **內存**: 8GB+ (推薦 16GB)
- **存儲**: 10GB+ 可用空間
- **瀏覽器**: Chrome 90+, Firefox 88+, Safari 14+

### 推薦配置
- **CPU**: 8核心以上
- **內存**: 32GB (高並發場景)
- **存儲**: SSD 50GB+
- **網絡**: 100Mbps+

---

## 🚀 快速部署

### 一鍵安裝腳本
```bash
# 克隆最新v4.76版本
git clone https://github.com/alexchuang650730/aicore0720.git
cd aicore0720

# 執行一鍵部署
bash deploy/v4.76/deploy.sh
```

### 自動化安裝內容
- Python依賴安裝
- Node.js依賴安裝
- 環境配置生成
- MCP組件初始化
- ClaudeEditor三欄式界面設置
- 演示環境配置

---

## 📦 手動部署步驟

### 1. 環境準備
```bash
# 檢查Python版本
python --version  # 需要 3.9+

# 檢查Node.js版本  
node --version     # 需要 18.0+

# 檢查npm版本
npm --version      # 需要 8.0+
```

### 2. 依賴安裝
```bash
# Python依賴
pip install -r requirements.txt

# Node.js依賴
npm install

# 可選：yarn安裝
yarn install
```

### 3. 環境配置
```bash
# 複製環境變量模板
cp .env.example .env

# 編輯環境配置
nano .env
```

**必要配置項**:
```env
# Claude API配置
CLAUDE_API_KEY=your_claude_api_key
CLAUDE_MODEL=claude-3-sonnet-20240229

# K2模型配置  
K2_API_ENDPOINT=https://your-k2-endpoint.com
K2_API_KEY=your_k2_api_key

# 數據庫配置
DATABASE_URL=sqlite:///powerautomation.db

# Redis配置（可選）
REDIS_URL=redis://localhost:6379

# ClaudeEditor配置
CLAUDEEDITOR_PORT=3000
CLAUDEEDITOR_HOST=localhost
```

### 4. 數據庫初始化
```bash
# 創建數據庫表
python core/api/db_init.py

# 運行數據遷移（如從v4.75升級）
python deploy/v4.76/scripts/migrate_from_v475.py
```

### 5. MCP組件啟動
```bash
# 啟動MCP協調器
python core/components/mcp_coordinator_mcp/coordinator.py

# 啟動核心MCP服務
python deploy/v4.76/scripts/start_mcp_services.py
```

---

## 🎯 ClaudeEditor三欄式界面部署

### 開發模式
```bash
# 進入ClaudeEditor目錄
cd deploy/v4.76/claudeeditor

# 安裝依賴
npm install

# 啟動開發服務器
npm run dev

# 訪問界面
open http://localhost:3000
```

### 生產模式
```bash
# 構建生產版本
npm run build

# 啟動生產服務器
npm run start

# 或使用PM2管理
pm2 start ecosystem.config.js
```

### 三欄式界面配置
```json
{
  "ui_layout": "three_panel",
  "panels": {
    "left": {
      "width": "320px",
      "components": ["aiModelControl", "githubStatus", "quickActions", "sixWorkflows"]
    },
    "center": {
      "flex": "1",
      "components": ["codeEditor", "demoPreview", "conversationMode"]
    },
    "right": {
      "width": "380px", 
      "components": ["aiAssistant", "contextAnalysis", "performanceMonitor"]
    }
  }
}
```

---

## 📊 演示環境部署

### 啟動完整演示
```bash
# 進入v4.76部署目錄
cd deploy/v4.76

# 啟動演示環境
bash scripts/start_demo_environment.sh

# 驗證演示功能
python scripts/verify_demo_functionality.py
```

### 演示組件清單
- **Smart Intervention演示**: http://localhost:3000/demo/smart-intervention
- **StageWise命令演示**: http://localhost:3000/demo/stagewise-command  
- **性能指標儀表板**: http://localhost:3000/demo/metrics-tracking
- **三權限系統演示**: http://localhost:3000/demo/three-tier-auth
- **六大工作流演示**: http://localhost:3000/demo/six-workflows

---

## 🔧 服務管理

### 啟動所有服務
```bash
# 使用統一啟動腳本
bash deploy/v4.76/scripts/start_all_services.sh
```

### 分別啟動服務
```bash
# 1. 核心API服務
python core/api/main_api_server.py &

# 2. ClaudeEditor界面
cd deploy/v4.76/claudeeditor && npm run start &

# 3. MCP協調器
python core/components/mcp_coordinator_mcp/coordinator.py &

# 4. Smart Intervention服務
python core/components/smart_intervention/mcp_server.py &

# 5. Claude實時收集器
python core/components/claude_realtime_mcp/claude_realtime_manager.py &
```

### 停止服務
```bash
# 停止所有服務
bash deploy/v4.76/scripts/stop_all_services.sh

# 或手動停止
pkill -f "main_api_server.py"
pkill -f "npm run start" 
pkill -f "coordinator.py"
```

---

## 🔍 健康檢查

### 自動化驗證
```bash
# 運行完整驗證套件
python deploy/v4.76/tests/health_check.py

# 驗證特定組件
python deploy/v4.76/tests/claudeeditor_validation.py
python deploy/v4.76/tests/mcp_integration_test.py
```

### 手動檢查清單
- [ ] API服務響應正常 (http://localhost:8000/health)
- [ ] ClaudeEditor界面加載 (http://localhost:3000)  
- [ ] MCP組件全部在線 (21個組件)
- [ ] Smart Intervention <100ms響應
- [ ] K2模型路由正常
- [ ] 演示功能完整

### 性能指標監控
```bash
# 實時性能監控
python deploy/v4.76/scripts/performance_monitor.py

# 檢查關鍵指標
curl http://localhost:8000/api/v476/metrics
```

**預期指標**:
- Smart Intervention延遲: <100ms
- MemoryRAG壓縮率: ~2.4%  
- K2準確率: >95%
- 內存使用: <50MB (單服務)

---

## 🌐 生產環境部署

### Docker部署
```bash
# 構建Docker鏡像
docker build -t powerautomation:v4.76 .

# 運行容器
docker run -d \
  --name powerautomation-v476 \
  -p 3000:3000 \
  -p 8000:8000 \
  -e CLAUDE_API_KEY=$CLAUDE_API_KEY \
  powerautomation:v4.76
```

### Kubernetes部署
```yaml
# deploy/v4.76/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: powerautomation-v476
spec:
  replicas: 3
  selector:
    matchLabels:
      app: powerautomation
      version: v4.76
  template:
    metadata:
      labels:
        app: powerautomation
        version: v4.76
    spec:
      containers:
      - name: powerautomation
        image: powerautomation:v4.76
        ports:
        - containerPort: 3000
        - containerPort: 8000
        env:
        - name: CLAUDE_API_KEY
          valueFrom:
            secretKeyRef:
              name: claude-api-secret
              key: api-key
```

### 負載均衡配置
```nginx
# nginx.conf
upstream powerautomation_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

upstream claudeeditor_frontend {
    server 127.0.0.1:3000;
    server 127.0.0.1:3001; 
    server 127.0.0.1:3002;
}

server {
    listen 80;
    server_name powerauto.ai;
    
    location /api/ {
        proxy_pass http://powerautomation_backend;
    }
    
    location / {
        proxy_pass http://claudeeditor_frontend;
    }
}
```

---

## 🚨 故障排除

### 常見問題

**1. ClaudeEditor無法啟動**
```bash
# 檢查端口占用
lsof -i :3000

# 檢查Node.js版本
node --version

# 重新安裝依賴
rm -rf node_modules package-lock.json
npm install
```

**2. MCP組件連接失敗**
```bash
# 檢查MCP協調器狀態
python -c "from core.components.mcp_coordinator_mcp.coordinator import check_status; print(check_status())"

# 重啟MCP服務
bash deploy/v4.76/scripts/restart_mcp_services.sh
```

**3. Smart Intervention延遲過高**
```bash
# 檢查緩存狀態
redis-cli ping

# 重置Smart Intervention緩存
python core/components/smart_intervention/cache_reset.py
```

**4. K2模型響應異常**
```bash
# 測試K2連接
python core/components/memoryrag_mcp/k2_provider_final.py --test

# 檢查API配額
curl -H "Authorization: Bearer $K2_API_KEY" https://your-k2-endpoint.com/status
```

### 日志分析
```bash
# 查看系統日志
tail -f deploy/v4.76/logs/system.log

# 查看錯誤日志  
tail -f deploy/v4.76/logs/error.log

# 查看性能日志
tail -f deploy/v4.76/logs/performance.log
```

---

## 📈 監控和維護

### 日常監控
```bash
# 每日健康檢查
crontab -e
# 添加: 0 9 * * * cd /path/to/aicore0720 && python deploy/v4.76/tests/daily_health_check.py

# 性能報告生成
0 0 * * 0 cd /path/to/aicore0720 && python deploy/v4.76/scripts/weekly_performance_report.py
```

### 備份策略
```bash
# 數據庫備份
sqlite3 powerautomation.db ".backup backup_$(date +%Y%m%d).db"

# 配置文件備份
tar -czf config_backup_$(date +%Y%m%d).tar.gz deploy/v4.76/config/

# 日志歸檔
gzip deploy/v4.76/logs/system.log.$(date +%Y%m%d)
```

### 版本升級
```bash
# 從v4.75升級到v4.76
python deploy/v4.76/scripts/upgrade_from_v475.py

# 備份當前版本
cp -r deploy/v4.75 deploy/v4.75_backup_$(date +%Y%m%d)

# 驗證升級結果
python deploy/v4.76/tests/upgrade_verification.py
```

---

## 📞 技術支持

### 文檔資源
- **API文檔**: [deploy/v4.76/docs/API_REFERENCE.md](API_REFERENCE.md)
- **故障排除**: [deploy/v4.76/docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **性能調優**: [deploy/v4.76/docs/PERFORMANCE_TUNING.md](PERFORMANCE_TUNING.md)

### 社群支持
- **GitHub Issues**: https://github.com/alexchuang650730/aicore0720/issues
- **演示問題**: https://powerauto.ai/support
- **技術諮詢**: chuang.hsiaoyen@gmail.com

---

**PowerAutomation v4.76 部署指南**  
*最後更新: 2025-07-20*  
*版本: 1.0.0*