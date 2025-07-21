# 完整的 AI 模型切換指南

## 🎯 兩種切換方式

### 方式一：使用 /model 命令（在 Claude Code 中）

在對話中直接輸入命令：
```
/model k2        # 切換到 K2 模式
/model claude    # 切換到 Claude 模式
/model hybrid    # 切換到混合模式
/model status    # 查看狀態
```

### 方式二：使用 ClaudeEditor 左上角控制面板

1. **啟動 ClaudeEditor**
   - 在 Claude Code 中說「啟動編輯器」
   - 或使用其他觸發關鍵詞

2. **使用左上角的 AI Model Control 面板**
   ```
   🤖 AI Model Control
   ├── 當前模式顯示
   ├── 三個切換按鈕
   │   ├── [K2 Mode]     - 點擊切換到 K2
   │   ├── [Claude Mode] - 點擊切換到 Claude
   │   └── [Hybrid Mode] - 點擊切換到混合模式
   ├── 狀態指示器
   │   ├── K2: 🟢 Active / 🔴 Offline
   │   └── Claude: 🟢 Connected / 🔴 Offline
   └── 置信度滑塊（0-100%）
   ```

3. **使用快捷鍵（在 ClaudeEditor 中）**
   - `⌘+K` - 切換到 K2 模式
   - `⌘+C` - 切換到 Claude 模式
   - `⌘+H` - 切換到混合模式
   - `⌘+/` - 快速循環切換

## 🔄 兩種方式的同步

**重要**：無論使用哪種方式切換，模式都會在以下位置同步：
- Claude Code 對話
- ClaudeEditor 編輯器
- 所有 K2/Claude 處理流程

## 📊 完整工作流程示例

### 示例 1：從 Claude Code 開始
```
1. Claude Code 對話:
   You: /model k2
   Assistant: ✅ 已切換到 K2 本地推理模式

2. 啟動編輯器:
   You: 啟動編輯器
   [ClaudeEditor 啟動，左上角顯示 K2 Mode 已選中]

3. 在編輯器中可以隨時切換:
   - 點擊 [Claude Mode] 按鈕
   - 或按 ⌘+C
```

### 示例 2：從 ClaudeEditor 開始
```
1. Claude Code 對話:
   You: 打開ClaudeEditor
   [ClaudeEditor 啟動]

2. 在編輯器左上角:
   - 點擊 [K2 Mode] 按鈕
   - 狀態顯示切換成功

3. 回到 Claude Code:
   You: /model status
   Assistant: 📊 當前模型狀態:
   🟢 模式: K2
   [確認已同步]
```

## 🎨 界面元素說明

### Claude Code 中的反饋
```
切換成功時：
✅ 已切換到 K2 本地推理模式
✅ 已切換到 Claude API 模式
✅ 已切換到智能混合模式

查看狀態時：
📊 當前模型狀態:
🟢 模式: K2
📈 K2 準確率: 95.0%
📚 訓練樣本: 6,560
```

### ClaudeEditor 中的視覺反饋
- **按鈕高亮**：當前模式的按鈕會高亮顯示
- **狀態指示燈**：
  - 🟢 綠燈 = 服務正常
  - 🔴 紅燈 = 服務離線
  - 🟡 黃燈 = 連接中
- **模式切換動畫**：切換時會顯示 2 秒的提示

## 💡 最佳實踐

1. **快速切換**
   - 在 Claude Code 中用 `/model` 命令最快
   - 在 ClaudeEditor 中用快捷鍵最快

2. **視覺確認**
   - ClaudeEditor 左上角提供最直觀的狀態顯示
   - 適合需要持續監控模式的場景

3. **批量任務**
   - 開始前先設置好模式
   - 使用 `/model status` 確認

## 🔧 高級功能

### 置信度調整（僅混合模式）

**在 ClaudeEditor 左上角：**
- 拖動 Confidence 滑塊（0-100%）
- 實時顯示百分比
- 立即生效

**作用：**
- 設置為 70% = K2 置信度 ≥ 70% 時使用 K2
- 設置為 90% = 只有高置信度時才用 K2
- 設置為 30% = 更多情況使用 K2

## ❓ 常見場景

**場景 1：我想全程使用 K2**
- 方法 1：`/model k2`
- 方法 2：ClaudeEditor 中點擊 [K2 Mode]

**場景 2：我想根據任務自動選擇**
- 使用默認的混合模式
- 調整置信度滑塊來優化

**場景 3：我在處理創新任務**
- 切換到 Claude 模式獲得最佳創意支持

## 📝 總結

現在你有兩種便捷的方式來控制 AI 模型：
1. **命令行方式**：在 Claude Code 中使用 `/model` 命令
2. **圖形界面方式**：在 ClaudeEditor 左上角使用控制面板

兩種方式完全同步，選擇你覺得最方便的即可！