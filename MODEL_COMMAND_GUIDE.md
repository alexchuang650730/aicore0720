# /model 命令使用指南

## 🎯 快速開始

在 Claude Code 對話中使用 `/model` 命令來切換 AI 模型：

```
/model k2        # 切換到 K2 模式
/model claude    # 切換到 Claude 模式  
/model hybrid    # 切換到混合模式
/model status    # 查看當前狀態
/model help      # 顯示幫助
```

## 📋 完整命令列表

### 切換模式命令

| 命令 | 說明 | 示例 |
|------|------|------|
| `/model k2` | 切換到 K2 本地推理模式 | `/model k2` |
| `/model claude` | 切換到 Claude API 模式 | `/model claude` |
| `/model hybrid` | 切換到智能混合模式 | `/model hybrid` |
| `/model auto` | 同 hybrid（別名） | `/model auto` |
| `/model smart` | 同 hybrid（別名） | `/model smart` |

### 查詢命令

| 命令 | 說明 | 示例 |
|------|------|------|
| `/model status` | 查看當前模式和狀態 | `/model status` |
| `/model info` | 同 status（別名） | `/model info` |
| `/model help` | 顯示幫助信息 | `/model help` |
| `/model ?` | 同 help（別名） | `/model ?` |

## 🔄 模式說明

### 🟢 K2 模式
- **特點**：使用本地訓練的 K2 模型
- **優勢**：響應速度快，離線可用，已學習你的編碼風格
- **適用**：重複性任務、已訓練的場景
- **切換**：`/model k2`

### 🔵 Claude 模式
- **特點**：使用 Claude API
- **優勢**：強大的理解能力，適合複雜任務
- **適用**：創新性任務、探索性開發
- **切換**：`/model claude`

### 🟡 混合模式（默認）
- **特點**：根據置信度智能選擇
- **優勢**：平衡速度和準確性
- **適用**：日常開發，自動優化
- **切換**：`/model hybrid`

## 💡 使用示例

### 場景 1：快速代碼補全
```
You: /model k2
Assistant: ✅ 已切換到 K2 本地推理模式

You: 幫我完成這個函數
Assistant: [使用 K2 快速生成代碼]
```

### 場景 2：複雜算法設計
```
You: /model claude
Assistant: ✅ 已切換到 Claude API 模式

You: 設計一個分布式系統架構
Assistant: [使用 Claude 進行深度分析]
```

### 場景 3：查看狀態
```
You: /model status
Assistant: 📊 當前模型狀態:
🟡 模式: HYBRID
📈 K2 準確率: 95.0%
📚 訓練樣本: 6,560
🎯 置信度閾值: 70%
🔄 模型版本: v3
```

## 🎨 與 ClaudeEditor 配合

`/model` 命令與 ClaudeEditor 完美配合：

1. **先切換模式**
   ```
   /model k2
   ```

2. **啟動編輯器**
   ```
   啟動編輯器
   ```

3. **編輯器會使用你選擇的模式**

## ⚡ 快捷技巧

1. **命令可以在任何對話中使用**
   - 不需要單獨一行
   - 可以在問題前加上命令

2. **支持中文輸入**
   ```
   /model 狀態    # 等同於 /model status
   ```

3. **命令不區分大小寫**
   ```
   /MODEL K2     # 有效
   /Model Claude # 有效
   ```

## 🔧 高級設置

### 調整置信度閾值（混合模式）

在混合模式下，當 K2 置信度高於閾值時使用 K2，否則使用 Claude。

默認閾值：70%

可通過配置文件調整：
```json
{
  "k2_confidence_threshold": 0.7
}
```

## ❓ 常見問題

**Q: 命令沒有響應？**
A: 確保已重啟 Claude Code 載入新的 MCP 配置

**Q: 如何知道當前使用哪個模式？**
A: 使用 `/model status` 查看

**Q: 切換後立即生效嗎？**
A: 是的，下一個請求就會使用新模式

**Q: 可以設置默認模式嗎？**
A: 可以在配置文件中設置默認模式

## 📝 備註

- `/model` 和 `/mode` 是等價的，都可以使用
- 模式設置在整個會話中保持，直到下次切換
- 每次切換都會顯示確認消息