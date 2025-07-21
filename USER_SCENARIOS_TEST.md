# 用戶場景測試報告

## 🧪 場景 1：Docker 未安裝

**用戶操作：**
```bash
curl -fsSL https://powerauto.ai/install | bash
```

**系統響應：**
```
📦 Docker is required but not installed.

Please install Docker Desktop first:
👉 https://www.docker.com/products/docker-desktop

After installing Docker, run this command again:
curl -fsSL https://powerauto.ai/install | bash
```

**問題：** 用戶可能不知道如何安裝 Docker
**解決方案：** 提供平台特定的安裝指南鏈接

---

## 🧪 場景 2：端口被占用

**問題：** 8888 端口已被其他應用占用
**錯誤信息：**
```
docker: Error response from daemon: driver failed programming external connectivity on endpoint powerautomation-k2: Bind for 0.0.0.0:8888 failed: port is already allocated.
```

**解決方案需求：**
- 自動檢測端口占用
- 提供替代端口選項
- 或自動選擇可用端口

---

## 🧪 場景 3：Claude Code 未安裝

**問題：** 用戶沒有安裝 Claude Code
**現象：** 
- `/model` 命令無法使用
- MCP 配置無效

**解決方案：**
- 檢測 Claude Code 安裝
- 提供 Web 界面作為備選
- 引導用戶安裝 Claude Code

---

## 🧪 場景 4：/model 命令無響應

**用戶操作：**
```
在 Claude Code 中輸入: /model k2
```

**可能原因：**
1. MCP 服務器未啟動
2. Claude Code 未重啟
3. 配置文件未正確載入

**診斷步驟：**
```bash
# 檢查 Docker 容器
docker ps | grep powerautomation

# 查看日誌
docker logs powerautomation-k2

# 測試 MCP 連接
echo '{"method":"status"}' | docker exec -i powerautomation-k2 python3 /app/mcp_unified.py
```

---

## 🧪 場景 5：對話收集權限問題

**問題：** macOS 權限限制訪問 Claude 數據
**錯誤：**
```
PermissionError: [Errno 13] Permission denied: '/Users/xxx/Library/Application Support/Claude'
```

**解決方案：**
- 請求必要權限
- 使用備選收集方法
- 提供手動授權指南

---

## 🧪 場景 6：網絡連接問題

**問題：** 無法下載 Docker 鏡像
**錯誤：**
```
Unable to find image 'powerauto/k2:latest' locally
docker: Error response from daemon: pull access denied
```

**備選方案：**
- 從 GitHub 構建本地鏡像
- 提供離線安裝包
- 使用鏡像源

---

## 🧪 場景 7：升級衝突

**場景：** 用戶已有舊版本
**問題：** 
- 配置文件衝突
- 數據遷移需求
- 端口衝突

**安全升級流程：**
```bash
# 備份現有數據
docker exec powerautomation-k2 tar -czf /tmp/backup.tar.gz /data
docker cp powerautomation-k2:/tmp/backup.tar.gz ./backup-$(date +%s).tar.gz

# 停止舊版本
docker stop powerautomation-k2
docker rm powerautomation-k2

# 安裝新版本
curl -fsSL https://powerauto.ai/install | bash
```

---

## 🧪 場景 8：ClaudeEditor 無法啟動

**用戶操作：**
```
說："打開編輯器"
```

**問題：** 瀏覽器未打開
**可能原因：**
- 系統限制
- 默認瀏覽器問題
- 端口未就緒

**解決方案：**
- 提供直接鏈接
- 多種打開方式
- 狀態檢查

---

## 🛠️ 建議的改進

### 1. 安裝前檢查腳本
```bash
#!/bin/bash
# Pre-flight check
check_requirements() {
    # Check Docker
    # Check ports
    # Check permissions
    # Check disk space
}
```

### 2. 交互式安裝選項
```bash
# 讓用戶選擇
echo "Choose installation type:"
echo "1) Quick install (recommended)"
echo "2) Custom install"
echo "3) Repair existing installation"
```

### 3. 診斷工具
```bash
# powerauto doctor
powerauto doctor

Checking system...
✅ Docker: Running
✅ Container: Healthy
❌ MCP: Not responding
✅ Ports: Available
⚠️  Permissions: Limited

Suggested fixes:
1. Restart Claude Code
2. Run: powerauto fix-mcp
```

### 4. 錯誤恢復
- 自動重試機制
- 回滾功能
- 詳細錯誤日誌

### 5. 離線模式
- 打包所有依賴
- 本地鏡像緩存
- 離線文檔

---

## 📋 測試清單

- [ ] 全新 macOS 安裝
- [ ] 全新 Linux 安裝
- [ ] 升級現有安裝
- [ ] Docker 未安裝情況
- [ ] 端口衝突處理
- [ ] 權限不足處理
- [ ] 網絡故障處理
- [ ] Claude Code 集成
- [ ] ClaudeEditor 啟動
- [ ] 對話收集功能