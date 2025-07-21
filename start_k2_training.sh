#!/bin/bash
# 啟動 K2 訓練服務

AICORE_DIR="$HOME/alexchuangtest/aicore0720"
cd "$AICORE_DIR"

echo "🚀 啟動 K2 訓練服務..."

# 啟動實時訓練系統
if ! pgrep -f "unified_realtime_k2_fixed.py" > /dev/null; then
    echo "📊 啟動實時 K2 訓練..."
    nohup python3 unified_realtime_k2_fixed.py > k2_training.log 2>&1 &
    echo "✅ K2 訓練已啟動 (PID: $!)"
else
    echo "ℹ️  K2 訓練已在運行"
fi

# 啟動持續學習系統
if ! pgrep -f "integrated_continuous_learning.py" > /dev/null; then
    echo "🧠 啟動持續學習系統..."
    nohup python3 integrated_continuous_learning.py > continuous_learning.log 2>&1 &
    echo "✅ 持續學習已啟動 (PID: $!)"
else
    echo "ℹ️  持續學習已在運行"
fi

echo "📈 K2 訓練服務已就緒！"
