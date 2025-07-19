# Manus 數據收集指南

## 🚀 快速開始

### 方法一：使用現有 Chrome 會話（推薦）

這個方法會連接到您已經登錄的 Chrome，避免重新認證。

#### 步驟：

1. **準備 Chrome 遠程調試**
   ```bash
   # 1. 完全關閉所有 Chrome 窗口
   
   # 2. 在新終端窗口運行：
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
   
   # 3. Chrome 會啟動，這時登錄到 Manus
   ```

2. **準備 replay URLs**
   創建 `replay_urls.txt` 文件，添加您的 Manus replay 連結：
   ```
   https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1
   https://manus.im/share/另一個ID?replay=1
   # 每行一個 URL
   ```

3. **運行收集腳本**
   ```bash
   # 在另一個終端窗口
   python3 collect_manus_data.py
   ```

### 方法二：使用 Safari（如果 Chrome 有問題）

1. **啟用 Safari 遠程自動化**
   - Safari → 偏好設置 → 高級 → 勾選「在菜單欄中顯示開發菜單」
   - 開發菜單 → 勾選「允許遠程自動化」

2. **運行腳本並選擇 Safari**
   ```bash
   python3 collect_manus_data.py
   # 選擇 safari
   ```

## 📝 注意事項

1. **保持瀏覽器開啟**：收集過程中不要關閉瀏覽器
2. **網絡穩定**：確保網絡連接穩定
3. **避免操作**：收集過程中不要在瀏覽器中進行其他操作

## 🔧 故障排除

### Chrome 連接失敗
- 確保完全關閉了所有 Chrome 窗口再啟動遠程調試
- 檢查是否有其他程序佔用 9222 端口

### 無法提取數據
- 檢查 Manus 是否已登錄
- 確保 replay URL 是有效的
- 查看 `data/manus_chrome/debug/` 目錄下的截圖

## 📊 輸出結果

收集的數據會保存在：
- `data/manus_chrome/` - Chrome 收集的數據
- `data/manus_safari/` - Safari 收集的數據

每個 replay 會生成：
- JSON 文件包含所有對話
- 提取的訓練對
- 質量評分