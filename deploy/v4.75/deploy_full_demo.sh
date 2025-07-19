#!/bin/bash

echo "🚀 PowerAutomation v4.75 完整演示環境部署"
echo "==========================================="

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安裝，請先安裝 Node.js"
    exit 1
fi

# 檢查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安裝，請先安裝 npm"
    exit 1
fi

# 安裝必要依賴
echo "📦 安裝演示依賴..."
npm install -g express 2>/dev/null || true

# 1. 啟動 MCP 組件
echo "🔧 啟動 MCP 組件模擬服務..."
bash "/Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.75/start_demo_components.sh" &
MCP_PID=$!

# 等待 MCP 組件啟動
sleep 8

# 2. 啟動 ClaudeEditor
echo "🎨 啟動 ClaudeEditor 演示界面..."
bash "/Users/alexchuang/alexchuangtest/aicore0720/claudeditor/start_claudeditor_demo.sh" &
CLAUDEDITOR_PID=$!

# 等待所有服務啟動
sleep 5

echo ""
echo "🎉 演示環境部署完成！"
echo "========================"
echo "📍 服務地址："
echo "  🌐 ClaudeEditor 演示: http://localhost:8080"
echo "  📡 MCP API 基地址: http://localhost:3001-3004"
echo ""
echo "🎪 演示場景："
echo "  1. 智能干預演示 (2-3分鐘)"
echo "  2. 代碼流程自動化 (5-8分鐘)"  
echo "  3. SmartUI 設計演示 (3-5分鐘)"
echo "  4. 記憶增強檢索 (4-6分鐘)"
echo "  5. 性能監控演示 (3-4分鐘)"
echo ""
echo "⏱️  總演示時間: ~22分鐘"
echo ""
echo "🎯 演示準備就緒！打開瀏覽器訪問演示界面"
echo ""
echo "🛑 停止演示: Ctrl+C 或運行 'pkill -f demo'"

# 等待用戶中斷
trap 'echo "🛑 停止演示環境..."; kill $MCP_PID $CLAUDEDITOR_PID 2>/dev/null; exit 0' INT

# 保持腳本運行
wait
