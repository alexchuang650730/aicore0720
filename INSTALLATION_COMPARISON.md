# PowerAutomation K2 安裝版本比較

## 📊 版本對比表

| 特性 | 用戶版 (User) | 開發者版 (Developer) |
|------|--------------|-------------------|
| **安裝方式** | Docker 一鍵安裝 | 源碼完整安裝 |
| **安裝命令** | `curl -fsSL https://powerauto.ai/install \| bash` | `bash <(curl -s https://dev.powerauto.ai/install)` |
| **安裝時間** | < 2 分鐘 | 5-10 分鐘 |
| **所需空間** | ~500MB | ~2GB |
| **前置要求** | Docker | Python 3.9+, Git, Node.js, SSH |
| **認證** | 無需認證 | 需要開發者密鑰 |

## 🚀 功能對比

### 用戶版功能
✅ **基礎功能**
- `/model` 命令切換 K2/Claude
- ClaudeEditor 關鍵詞啟動
- 自動對話收集
- Web 儀表板 (http://localhost:8888)

✅ **簡化配置**
- 單一 Docker 容器
- 自動 MCP 配置
- 預設最佳設置
- 無需手動配置

✅ **易用性**
- 一行命令安裝
- 自動更新
- 簡單的啟動/停止命令
- 清晰的用戶界面

### 開發者版功能
✅ **完整源碼**
- 所有 Python 源文件
- 前端源碼
- 測試套件
- 文檔和示例

✅ **EC2 數據同步**
- 自動同步訓練數據
- 共享模型庫
- 團隊協作支持
- 每 5 分鐘自動同步

✅ **開發工具**
- 熱重載
- 調試模式
- 性能分析
- 單元測試
- 部署腳本

✅ **高級配置**
- 完整環境變量控制
- 自定義端口設置
- 批量訓練配置
- API 密鑰管理

## 📁 目錄結構

### 用戶版
```
~/.powerautomation/
├── data/           # 本地數據
├── logs/           # 日誌文件
└── docker-compose.yml
```

### 開發者版
```
~/powerautomation-dev/
├── aicore0720/
│   ├── core/       # 核心組件
│   ├── data/       # 訓練數據
│   ├── models/     # K2 模型
│   ├── scripts/    # 開發腳本
│   ├── tests/      # 測試套件
│   └── venv/       # Python 環境
├── .env.development
└── dev.sh          # 開發助手
```

## 🔧 命令對比

### 用戶版命令
```bash
# 啟動
docker start powerautomation-k2

# 停止
docker stop powerautomation-k2

# 查看狀態
docker ps | grep powerautomation

# 更新
docker pull powerauto/k2:latest
```

### 開發者版命令
```bash
# 啟動開發服務器
./dev.sh start

# 同步 EC2 數據
./dev.sh sync

# 運行訓練
./dev.sh train

# 運行測試
./dev.sh test

# 部署到生產
./dev.sh deploy
```

## 🎯 選擇建議

### 選擇用戶版如果你：
- 想要快速體驗 PowerAutomation
- 不需要修改源碼
- 希望簡單易用
- 只需要基本的 K2 功能

### 選擇開發者版如果你：
- 是 PowerAutomation 團隊成員
- 需要開發新功能
- 想要訪問完整訓練數據
- 需要自定義和擴展

## 🔄 升級路徑

### 從用戶版升級到開發者版
1. 獲取開發者密鑰
2. 運行開發者安裝腳本
3. 數據會自動遷移

### 版本切換
兩個版本可以共存，使用不同的目錄和端口

## 📞 支持

- **用戶版支持**: support@powerauto.ai
- **開發者支持**: dev@powerauto.ai
- **GitHub**: https://github.com/alexchuang650730/aicore0720

## 🔐 安全性

### 用戶版
- 只讀訪問 Claude 配置
- 本地數據存儲
- 無外部連接（除更新外）

### 開發者版
- 需要 SSH 密鑰
- EC2 加密連接
- 開發者認證
- 完整數據訪問權限