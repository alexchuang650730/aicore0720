# ClaudeEditor + K2 整合使用指南

## 🎨 ClaudeEditor 啟動方式

### 1. **關鍵詞啟動（推薦）**
在 Claude Code 對話中說出以下任一關鍵詞：

- 🇹🇼 **中文關鍵詞**：
  - "啟動編輯器"
  - "打開ClaudeEditor"
  - "編輯器模式"
  - "開啟編輯器"
  - "進入編輯器"

- 🇺🇸 **英文關鍵詞**：
  - "start editor"
  - "open claudeeditor"
  - "launch editor"
  - "editor mode"
  - "claudeeditor"

### 2. **命令行啟動**
```bash
# 從終端直接啟動
open /Users/alexchuang/Desktop/ClaudeEditor.app

# 或使用快捷命令（如果已配置）
claudeeditor
```

### 3. **從 Dock 或 Launchpad 啟動**
如果已將 ClaudeEditor 添加到 Dock，直接點擊圖標即可

## 🔄 ClaudeEditor 中的模式切換

### 在 ClaudeEditor 內切換 K2 模式

ClaudeEditor 支持三種工作模式，可通過設置面板或快捷鍵切換：

1. **K2 優先模式** `⌘+K`
   - 優先使用 K2 進行代碼理解和生成
   - 適合重複性任務和已訓練場景
   - 響應速度快，離線可用

2. **Claude 優先模式** `⌘+C`
   - 優先使用 Claude API
   - 適合複雜創新任務
   - 需要網絡連接

3. **智能混合模式** `⌘+H`（默認）
   - 根據任務自動選擇最佳引擎
   - K2 置信度高時使用 K2
   - 複雜任務自動切換到 Claude

### 模式切換指示器

ClaudeEditor 狀態欄會顯示當前模式：
- 🟢 K2 - 使用本地 K2 引擎
- 🔵 Claude - 使用 Claude API
- 🟡 Hybrid - 智能混合模式

## 🎯 K2 + ClaudeEditor 最佳實踐

### 1. **代碼補全場景**
```
模式：K2 優先
原因：K2 已學習你的編碼風格，補全更準確
設置：Editor → Preferences → Completion → K2 Mode
```

### 2. **代碼重構場景**
```
模式：智能混合
原因：簡單重構用 K2，複雜重構自動切換到 Claude
設置：默認模式即可
```

### 3. **新功能開發**
```
模式：Claude 優先
原因：需要創新性思考和設計
設置：Editor → Preferences → Generation → Claude Mode
```

## 📊 查看 K2 訓練狀態

在 ClaudeEditor 中查看 K2 狀態：

1. **狀態面板** `⌘+I`
   - 顯示 K2 模型版本
   - 當前準確率
   - 訓練樣本數

2. **訓練監控** `⌘+T`
   - 實時訓練進度
   - 性能指標圖表
   - 錯誤分析

## 🚀 快速工作流程

### 典型使用流程：

```
1. 在 Claude Code 中對話
   You: "啟動編輯器"
   → ClaudeEditor 自動啟動

2. 在 ClaudeEditor 中編碼
   - 自動使用混合模式
   - K2 提供快速補全
   - Claude 處理複雜邏輯

3. 切換模式（如需要）
   - 按 ⌘+K 切換到 K2 模式
   - 按 ⌘+C 切換到 Claude 模式
   - 按 ⌘+H 返回混合模式

4. 查看訓練狀態
   - 按 ⌘+I 查看當前狀態
   - K2 持續從你的編碼中學習
```

## 🎨 高級功能

### 1. **上下文同步**
ClaudeEditor 會自動同步 Claude Code 的對話上下文，確保連貫性

### 2. **訓練反饋**
你的每次編輯都會作為訓練數據改進 K2 模型

### 3. **快捷命令**
- `⌘+/` - 快速切換模式
- `⌘+R` - 刷新 K2 模型
- `⌘+S` - 保存並訓練

## 💡 技巧提示

1. **首次使用**：建議使用混合模式，讓系統學習你的偏好
2. **重複任務**：完成幾次後切換到 K2 模式以提高效率
3. **創新任務**：直接使用 Claude 模式獲得最佳創意支持

## 🔧 故障排除

### ClaudeEditor 未啟動？
1. 檢查路徑：`/Users/alexchuang/Desktop/ClaudeEditor.app`
2. 確認 MCP 配置已載入（重啟 Claude Code）
3. 查看日誌：`~/Library/Logs/claudeeditor.log`

### K2 模式不工作？
1. 確認訓練服務運行中：`./start_k2_training.sh`
2. 檢查模型文件存在：`enhanced_intent_model_final.json`
3. 查看 K2 日誌：`tail -f unified_k2_training.log`

## 📈 性能優化建議

1. **定期訓練**：每天讓 K2 訓練系統運行至少 1 小時
2. **模式選擇**：根據任務類型主動切換模式
3. **反饋學習**：使用 ClaudeEditor 的反饋功能幫助 K2 改進

---

💬 **需要幫助？**
- 在 Claude Code 中說："幫助我使用 ClaudeEditor"
- 查看日誌：`~/alexchuangtest/aicore0720/logs/`
- 聯繫支持：在 ClaudeEditor 中按 `⌘+?`