#!/bin/bash
# ClaudeEditor 快速啟動腳本
# 可以在 Claude 對話中直接啟動並切換使用

echo "🚀 啟動 ClaudeEditor & PowerAutomation..."
echo "================================================"

# 設置環境變量
export POWERAUTOMATION_ROOT=$(pwd)
export CLAUDE_TRAINING_MODE=true
export DATA_COLLECTION_ENABLED=true

# 創建必要的目錄
mkdir -p logs
mkdir -p training_data/claude_sessions
mkdir -p training_data/manus_data

# 啟動日誌收集
echo "📊 啟動數據收集模式..."
python3 core/components/memoryrag_mcp/claude_live_collector.py &
COLLECTOR_PID=$!
echo "數據收集器 PID: $COLLECTOR_PID"

# 啟動 MCP-Zero
echo "🔧 啟動 MCP-Zero Engine..."
python3 core/mcp_zero/mcp_zero_engine.py > logs/mcp_zero.log 2>&1 &
MCZERO_PID=$!
echo "MCP-Zero PID: $MCZERO_PID"

# 等待 MCP-Zero 啟動
sleep 2

# 啟動 API 服務器
echo "🌐 啟動 API 服務器..."
python3 core/api/main_api_server.py > logs/api_server.log 2>&1 &
API_PID=$!
echo "API Server PID: $API_PID"

# 檢查前端是否已安裝
if [ ! -d "deploy/claudeditor/node_modules" ]; then
    echo "📦 安裝前端依賴..."
    cd deploy/claudeditor
    npm install
    cd ../..
fi

# 啟動前端
echo "🎨 啟動 ClaudeEditor 前端..."
cd deploy/claudeditor
npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..
echo "Frontend PID: $FRONTEND_PID"

# 等待服務啟動
sleep 3

# 打開瀏覽器
echo "🌐 打開 ClaudeEditor..."
open http://localhost:3000 || echo "請手動打開: http://localhost:3000"

echo ""
echo "✅ ClaudeEditor 已啟動！"
echo "================================================"
echo "🌐 ClaudeEditor: http://localhost:3000"
echo "🚀 API Server: http://localhost:8000"
echo "📊 數據收集: 已啟用"
echo ""
echo "💡 使用提示："
echo "1. 在 Claude 中下達指令"
echo "2. 切換到 ClaudeEditor 查看執行結果"
echo "3. 所有操作都會被記錄為訓練數據"
echo ""
echo "按 Ctrl+C 停止所有服務並保存數據"

# 保存 PID 以便清理
echo "$COLLECTOR_PID $MCZERO_PID $API_PID $FRONTEND_PID" > .running_pids

# 捕獲退出信號
trap 'echo ""; echo "🛑 停止服務並保存數據..."; kill $COLLECTOR_PID $MCZERO_PID $API_PID $FRONTEND_PID 2>/dev/null; rm .running_pids; echo "✅ 已停止並保存數據"; exit' INT TERM

# 保持運行
while true; do
    sleep 1
done