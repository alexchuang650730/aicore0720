# 🚀 PowerAutomation 7/30上線版本 - 啟動指南

## ⚡ 一鍵啟動

```bash
# 在項目根目錄執行
./launch.sh
```

## 🎯 系統功能

### ✅ 已完成功能

1. **會員積分登錄系統**
   - 參考 claude-code.cn 和 aicodewith.com 的設計
   - 三種會員等級：體驗版、專業版、企業版
   - 積分管理和成本節省統計

2. **K2模型智能路由**
   - 與Claude Code Tool完全兼容
   - 自動路由到K2模型節省60-80%成本
   - 支援所有Claude Code命令

3. **ClaudeEditor可視化界面**
   - Web界面操作更便利
   - 六大工作流可視化管理
   - 項目下載和部署功能

4. **Memory RAG記憶增強**
   - 協助K2對齊Claude行為
   - 智能記憶和檢索功能

5. **Manus數據收集器**
   - 準備收集1000小時開發數據
   - 本地瀏覽器操作支持

## 🌐 訪問地址

啟動後訪問以下地址：

- **ClaudeEditor主界面**: http://localhost:8000
- **會員系統API**: http://localhost:8082
- **PowerAutomation Core**: http://localhost:8080

## 💡 使用方式

### 方式1：Claude Code Tool中使用
```bash
# 所有命令自動使用K2模型，體驗與Claude相同
/read file.py
/write new_file.py "print('Hello K2')"
/switch-k2  # 確保使用K2模型
/cost-savings  # 查看成本節省
```

### 方式2：ClaudeEditor中使用
1. 打開 http://localhost:8000
2. 註冊/登錄賬戶
3. 享受可視化開發體驗

## 🔧 配置說明

1. **API密鑰配置**
   ```bash
   # 編輯 .env 文件
   CLAUDE_API_KEY=your_claude_api_key
   KIMI_API_KEY=your_kimi_api_key
   ```

2. **會員等級對比**
   - 體驗版：1000積分/日，免費
   - 專業版：10000積分/日，¥299/月
   - 企業版：100000積分/日，¥2999/月

## 📊 核心優勢

1. **成本節省**：使用K2模型節省60-80%
2. **完全兼容**：與Claude Code Tool體驗一致
3. **雙向選擇**：命令行 + Web界面
4. **智能路由**：自動選擇最優模型
5. **數據驅動**：基於1000小時真實數據優化

## 🛠️ 故障排除

### 常見問題

1. **端口被占用**
   ```bash
   # 檢查端口占用
   lsof -i :8000
   lsof -i :8080
   ```

2. **依賴缺失**
   ```bash
   # 重新安裝依賴
   pip install -r requirements.txt
   cd claudeditor && npm install
   ```

3. **權限問題**
   ```bash
   # 給腳本執行權限
   chmod +x launch.sh
   chmod +x start_powerautomation_system.py
   ```

## 📈 7/30發布目標

- [x] 會員積分系統
- [x] K2模型路由
- [x] Claude Code兼容
- [x] ClaudeEditor界面
- [x] Memory RAG對齊
- [x] Manus數據收集準備

## 🎉 立即體驗

```bash
git clone https://github.com/alexchuang650730/aicore0718.git
cd aicore0718
./launch.sh
```

**PowerAutomation - 讓開發永不偏離目標！** 🎯