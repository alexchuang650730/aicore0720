# PowerAutomation + ClaudeEditor AWS EC2 部署指南

> 🎯 讓開發永不偏離目標的智能系統 - powerauto.ai

## 🌟 系統概述

PowerAutomation驅動的ClaudeEditor是一個完整的AI開發助手系統，集成了：

- 🎯 **六大工作流**：目標驅動開發、智能代碼生成、自動化測試、質量保證、智能部署、自適應學習
- 🤖 **雙AI模式**：Claude + K2中文優化（2元→8元成本效益）
- 🧠 **Memory RAG**：智能記憶和學習系統
- 💰 **會員積分系統**：支持支付寶、微信、Stripe多種支付方式
- ⚡ **實時監控**：目標對齊度監控，防止開發偏離
- 📱 **全平台支持**：Web、PC桌面、移動端統一

## 🚀 快速部署

### 前置條件

1. **AWS EC2實例**
   - 操作系統：Ubuntu 20.04 LTS 或更新版本
   - 實例類型：建議 t3.medium 或以上
   - 存儲：至少 20GB
   - 安全組：開放端口 22 (SSH), 80 (HTTP), 443 (HTTPS)

2. **SSH密鑰**
   - 將 `alexchuang.pem` 放在部署腳本同目錄下
   - 確保密鑰權限正確 (600)

3. **域名設置** (可選)
   - 將 `powerauto.ai` 和 `www.powerauto.ai` 解析到EC2公網IP

### 一鍵部署

```bash
# 1. 下載部署腳本
chmod +x deploy_to_aws.sh

# 2. 執行部署
./deploy_to_aws.sh
```

部署腳本將自動完成：
- ✅ 系統依賴安裝
- ✅ 應用代碼部署
- ✅ Python環境配置
- ✅ 系統服務配置
- ✅ Nginx反向代理設置
- ✅ 防火牆配置
- ✅ 服務啟動和驗證

## 📁 系統架構

```
/opt/powerautomation/              # 主部署目錄
├── index.html                     # ClaudeEditor Web界面
├── powerautomation_driver_api.js  # 驅動API
├── powerautomation_websocket_server.py  # WebSocket服務器
├── member_system.py               # 會員系統API
├── memory_rag_mcp_integration.py  # Memory RAG集成
├── start_powerautomation_driven.py # 啟動腳本
├── requirements.txt               # Python依賴
├── venv/                          # Python虛擬環境
├── logs/                          # 日誌目錄
├── data/                          # 數據目錄
└── backups/                       # 備份目錄
```

## 🌐 服務端口

| 服務 | 端口 | 協議 | 用途 |
|------|------|------|------|
| Nginx | 80/443 | HTTP/HTTPS | 反向代理和靜態文件 |
| ClaudeEditor | 8080 | HTTP | Web應用界面 |
| PowerAutomation WebSocket | 8765 | WebSocket | 驅動通信 |
| 會員系統API | 8081 | HTTP | 用戶管理和積分 |

## 🔧 服務管理

### SystemD 服務控制

```bash
# 啟動服務
sudo systemctl start powerautomation

# 停止服務
sudo systemctl stop powerautomation

# 重啟服務
sudo systemctl restart powerautomation

# 查看狀態
sudo systemctl status powerautomation

# 開機自啟
sudo systemctl enable powerautomation

# 禁用自啟
sudo systemctl disable powerautomation
```

### 日誌管理

```bash
# 查看實時日誌
sudo journalctl -u powerautomation -f

# 查看最近日誌
sudo journalctl -u powerautomation -n 100

# 查看特定時間段日誌
sudo journalctl -u powerautomation --since "2024-01-01" --until "2024-01-02"
```

### Nginx 管理

```bash
# 測試配置
sudo nginx -t

# 重新加載配置
sudo nginx -s reload

# 重啟Nginx
sudo systemctl restart nginx

# 查看Nginx狀態
sudo systemctl status nginx
```

## 🎯 功能配置

### 會員計劃設置

系統預設4種會員計劃：

1. **基礎版** (免費)
   - 1000積分/月
   - 基礎AI對話
   - 基礎工作流
   - 100次/日請求限制

2. **專業版** (599元/月)
   - 10000積分/月
   - 全部六大工作流
   - K2模式訪問
   - 1000次/日請求限制

3. **團隊版** (2995元/月，5人)
   - 50000積分/月
   - 團隊協作功能
   - API訪問
   - 5000次/日請求限制

4. **企業版** (9999元/月)
   - 200000積分/月
   - 私有部署
   - 無限制使用
   - 24/7技術支持

### 積分消費配置

| 服務 | 消費積分 | 說明 |
|------|----------|------|
| Claude API調用 | 10積分 | 英文優化模式 |
| K2 API調用 | 5積分 | 中文優化，更便宜 |
| Memory RAG查詢 | 2積分 | 智能記憶搜索 |
| 工作流執行 | 20積分 | 六大工作流 |
| 代碼分析 | 15積分 | AI代碼質量分析 |
| UI生成 | 25積分 | 智能界面生成 |
| 部署操作 | 30積分 | 自動化部署 |

## 🔐 安全配置

### 默認管理員賬號

**重要：部署後請立即更改密碼！**

- 郵箱：`admin@powerauto.ai`
- 密碼：`admin123`
- 計劃：企業版
- 積分：1,000,000

### SSL證書配置 (推薦)

使用Let's Encrypt免費證書：

```bash
# 安裝certbot
sudo apt install certbot python3-certbot-nginx

# 獲取證書
sudo certbot --nginx -d powerauto.ai -d www.powerauto.ai

# 自動續期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

### 防火牆設置

```bash
# 查看防火牆狀態
sudo ufw status

# 允許特定IP訪問SSH
sudo ufw allow from YOUR_IP to any port 22

# 限制SSH訪問
sudo ufw delete allow ssh
sudo ufw allow from YOUR_IP to any port 22
```

## 📊 監控和維護

### 系統監控

```bash
# 查看系統資源
htop

# 查看磁盤使用
df -h

# 查看內存使用
free -h

# 查看網絡連接
netstat -tlnp

# 查看進程
ps aux | grep powerautomation
```

### 數據庫維護

```bash
# 進入部署目錄
cd /opt/powerautomation

# 備份數據庫
cp members.db backups/members_$(date +%Y%m%d_%H%M%S).db
cp memory_rag.db backups/memory_rag_$(date +%Y%m%d_%H%M%S).db

# 清理舊備份（保留30天）
find backups/ -name "*.db" -mtime +30 -delete
```

### 日誌輪轉

創建日誌輪轉配置：

```bash
sudo tee /etc/logrotate.d/powerautomation << EOF
/opt/powerautomation/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload powerautomation
    endscript
}
EOF
```

## 🚨 故障排除

### 常見問題

1. **服務無法啟動**
   ```bash
   # 檢查Python虛擬環境
   cd /opt/powerautomation
   source venv/bin/activate
   python -c "import fastapi, websockets"
   
   # 檢查端口占用
   sudo netstat -tlnp | grep -E ':(8080|8765|8081)'
   ```

2. **WebSocket連接失敗**
   ```bash
   # 檢查防火牆
   sudo ufw status
   
   # 檢查Nginx配置
   sudo nginx -t
   sudo cat /etc/nginx/sites-enabled/powerautomation
   ```

3. **數據庫錯誤**
   ```bash
   # 檢查數據庫文件權限
   ls -la /opt/powerautomation/*.db
   
   # 修復權限
   sudo chown ubuntu:ubuntu /opt/powerautomation/*.db
   ```

4. **內存不足**
   ```bash
   # 添加交換空間
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

### 性能優化

1. **數據庫優化**
   ```python
   # 在Python中執行
   import sqlite3
   conn = sqlite3.connect('/opt/powerautomation/members.db')
   conn.execute('VACUUM')
   conn.close()
   ```

2. **緩存配置**
   ```bash
   # 在Nginx配置中添加
   location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

## 🔄 升級和維護

### 代碼升級

```bash
# 備份當前版本
sudo cp -r /opt/powerautomation /opt/powerautomation_backup_$(date +%Y%m%d)

# 下載新版本
# 重新運行部署腳本

# 恢復數據（如需要）
sudo cp /opt/powerautomation_backup_*/members.db /opt/powerautomation/
sudo cp /opt/powerautomation_backup_*/memory_rag.db /opt/powerautomation/
```

### 定期維護任務

創建維護腳本：

```bash
sudo tee /opt/powerautomation/maintenance.sh << 'EOF'
#!/bin/bash
# PowerAutomation 定期維護腳本

cd /opt/powerautomation

# 清理舊日誌
find logs/ -name "*.log" -mtime +7 -delete

# 備份數據庫
cp members.db backups/members_$(date +%Y%m%d).db
cp memory_rag.db backups/memory_rag_$(date +%Y%m%d).db

# 清理舊備份
find backups/ -name "*.db" -mtime +30 -delete

# 重啟服務
sudo systemctl restart powerautomation

echo "$(date): 維護任務完成" >> logs/maintenance.log
EOF

sudo chmod +x /opt/powerautomation/maintenance.sh

# 添加到cron (每週日執行)
echo "0 2 * * 0 /opt/powerautomation/maintenance.sh" | sudo crontab -
```

## 🎉 成功部署後的操作

1. **訪問系統**
   - 🌐 主界面：http://powerauto.ai 或 http://EC2_IP
   - 🔧 API文檔：http://powerauto.ai/api/docs

2. **管理員登錄**
   - 使用默認賬號登錄
   - 立即更改密碼
   - 配置系統設置

3. **創建用戶**
   - 註冊測試用戶
   - 測試各種會員計劃
   - 驗證積分系統

4. **功能測試**
   - 測試六大工作流
   - 驗證AI模式切換
   - 檢查WebSocket連接
   - 測試Memory RAG功能

## 📞 技術支持

- 📧 郵箱：alex.chuang@powerauto.ai
- 🐛 問題反饋：GitHub Issues
- 📚 文檔：完整的API文檔和使用指南

---

**🎯 PowerAutomation - 讓開發永不偏離目標！**

*部署完成後，請及時配置SSL證書和更新管理員密碼以確保系統安全。*