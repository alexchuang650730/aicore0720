#!/bin/bash

# PowerAutomation 完整系統啟動腳本
# 包含所有演示功能

set -e

echo "🚀 PowerAutomation 完整系統啟動..."
echo "====================================="

# 檢查當前目錄
if [[ ! -f "setup.py" ]]; then
    echo "❌ 請在項目根目錄運行此腳本"
    exit 1
fi

# 激活虛擬環境
echo "🔧 激活虛擬環境..."
source venv/bin/activate

# 設置環境變量
export PYTHONPATH=$PWD:$PWD/core:$PWD/mcp_server:$PWD/goal_alignment_system
export POWERAUTOMATION_ROOT=$PWD

# 啟動MCP服務器（後台運行）
echo "🔌 啟動MCP服務器..."
python3 mcp_server/main.py --port 8765 &
MCP_PID=$!
echo "✅ MCP服務器啟動完成 (PID: $MCP_PID)"

# 等待MCP服務器啟動
sleep 3

# 啟動ClaudeEditor後端服務器（後台運行）
echo "🎯 啟動ClaudeEditor後端服務器..."
python3 -c "
import asyncio
import sys
sys.path.append('claude_code_integration')
from claudeditor_enhanced import EnhancedClaudeEditor

async def start_backend():
    editor = EnhancedClaudeEditor()
    await editor.start_server()

asyncio.run(start_backend())
" &
BACKEND_PID=$!
echo "✅ ClaudeEditor後端服務器啟動完成 (PID: $BACKEND_PID)"

# 等待後端服務器啟動
sleep 3

# 啟動ClaudeEditor前端（後台運行）
echo "🌐 啟動ClaudeEditor前端..."
cd claudeditor
npm run dev &
FRONTEND_PID=$!
cd ..
echo "✅ ClaudeEditor前端啟動完成 (PID: $FRONTEND_PID)"

# 等待前端服務器啟動
sleep 5

# 創建停止腳本
cat > stop_system.sh << 'EOF'
#!/bin/bash
echo "🛑 停止PowerAutomation系統..."
pkill -f "mcp_server/main.py"
pkill -f "claudeditor_enhanced.py"
pkill -f "vite"
pkill -f "npm run dev"
echo "✅ 系統已停止"
EOF
chmod +x stop_system.sh

# 顯示系統狀態
echo ""
echo "🎉 PowerAutomation 完整系統已啟動！"
echo "====================================="
echo "🔌 MCP服務器: http://localhost:8765"
echo "🎯 ClaudeEditor後端: http://localhost:8000"
echo "🌐 ClaudeEditor前端: http://localhost:5175"
echo ""
echo "📋 功能演示："
echo "1. 訪問 http://localhost:5175 使用ClaudeEditor"
echo "2. 切換K2模式進行中文AI對話"
echo "3. 使用AI助手與Claude Code Tool溝通"
echo "4. 體驗六大工作流優化"
echo "5. 演示不偏離目標的開發工作流"
echo "6. 在Claude Code中切換到K2並調用ClaudeEditor"
echo "7. 在K2模式下使用所有commands"
echo "8. Claude Tool生成文件到ClaudeEditor編輯和部署"
echo ""
echo "🛑 停止系統: ./stop_system.sh"
echo ""
echo "🎯 PowerAutomation - 讓開發永不偏離目標！"

# 保持腳本運行
echo "按 Ctrl+C 停止所有服務..."
trap 'echo "停止所有服務..."; kill $MCP_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT

wait