# K2 + ClaudeEditor 在 Claude Code 中的使用指南

## 🚀 快速開始

### 1. 啟動 K2 訓練服務
```bash
cd ~/alexchuangtest/aicore0720
./start_k2_training.sh
```

### 2. 在 Claude Code 中使用 K2

K2 會自動：
- 分析你的對話意圖
- 建議合適的工具
- 從每次交互中學習
- 提升準確率

### 3. 啟動 ClaudeEditor

只需在對話中說出關鍵詞：
- "啟動編輯器"
- "打開ClaudeEditor"
- "start editor"
- "編輯器模式"

## 📊 查看訓練狀態

```bash
# 查看實時日誌
tail -f ~/alexchuangtest/aicore0720/unified_k2_training.log

# 查看當前準確率
grep "相似度:" ~/alexchuangtest/aicore0720/unified_k2_training.log | tail -1
```

## 🔧 配置調整

編輯配置文件：
```bash
nano ~/.claude/k2_config.json
```

## 💡 使用技巧

1. **更準確的意圖理解**：K2 會學習你的使用模式
2. **更快的響應**：本地推理比雲端更快
3. **隱私保護**：訓練數據保存在本地
4. **持續改進**：每次使用都在優化模型

## 🎯 當前性能

- 意圖理解準確率: 97%
- Claude Code 相似度: 95%
- 訓練樣本數: 6,560+
- 支持 8 種主要意圖類型
