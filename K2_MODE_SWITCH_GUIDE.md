# K2 模式切換使用指南

## 🎯 三種運行模式

### 1. **K2 模式** 
- 完全使用 K2 進行意圖理解和工具推薦
- 適合已訓練充分的場景
- 響應速度快，本地推理

### 2. **Claude 模式**
- 使用 Claude Code 原生能力
- 適合複雜或新穎的任務
- 利用 Claude 的通用理解能力

### 3. **混合模式（默認）**
- 智能選擇 K2 或 Claude
- 根據 K2 置信度自動切換
- 兼顧準確性和效率

## 🔄 切換方式

### 方法一：關鍵詞切換
在對話中說出以下關鍵詞即可切換：

**切換到 K2 模式：**
- "使用K2"
- "切換到K2"
- "K2模式"
- "use k2"
- "k2 mode"

**切換到 Claude 模式：**
- "使用Claude"
- "切換到Claude"
- "Claude模式"
- "use claude"
- "claude mode"

**切換到混合模式：**
- "混合模式"
- "智能模式"
- "自動選擇"
- "hybrid mode"
- "auto mode"

### 方法二：命令切換
```bash
# 查看當前模式
echo '{"method": "k2/get_mode"}' | python3 k2_mode_switcher_mcp.py

# 切換到 K2 模式
echo '{"method": "k2/switch_mode", "params": {"mode": "k2"}}' | python3 k2_mode_switcher_mcp.py
```

## 📊 置信度閾值設置

在混合模式下，系統根據 K2 的置信度決定是否使用 K2：

- 默認閾值：0.7（70%）
- 高於閾值：使用 K2
- 低於閾值：使用 Claude

調整閾值：
```bash
# 設置為 80% 置信度
echo '{"method": "k2/set_threshold", "params": {"threshold": 0.8}}' | python3 k2_mode_switcher_mcp.py
```

## 💡 使用建議

1. **日常開發任務**：使用混合模式（默認）
2. **重複性任務**：切換到 K2 模式以獲得更快響應
3. **探索性任務**：切換到 Claude 模式以獲得更好的理解

## 📈 查看狀態

```bash
# 查看完整狀態
echo '{"method": "k2/status"}' | python3 k2_mode_switcher_mcp.py
```

返回信息包括：
- 當前模式
- 模型版本
- 準確率
- 訓練樣本數
- 置信度閾值

## 🎨 與 ClaudeEditor 配合

ClaudeEditor 啟動不受模式影響，在任何模式下都可以通過關鍵詞啟動：
- "啟動編輯器"
- "打開ClaudeEditor"
- "start editor"

## 🚀 快速開始示例

```
You: 使用K2模式
Assistant: 已切換到 K2 模式

You: 幫我分析這個代碼
Assistant: [使用 K2 進行快速本地推理]

You: 切換到混合模式
Assistant: 已切換到 hybrid 模式

You: 實現一個複雜的算法
Assistant: [根據任務複雜度自動選擇 K2 或 Claude]
```