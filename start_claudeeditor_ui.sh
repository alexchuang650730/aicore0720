#!/bin/bash

echo "🚀 启动 ClaudeEditor 三栏式UI演示"
echo "=================================="

# 检查端口是否被占用
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "📍 ClaudeEditor 已在运行"
    echo "🌐 访问地址: http://localhost:8080/claudeeditor_three_panel_ui.html"
else
    echo "🔧 启动HTTP服务器..."
    cd /Users/alexchuang/alexchuangtest/aicore0720/demo
    nohup python3 -m http.server 8080 > server.log 2>&1 &
    sleep 2
    echo "✅ 服务器启动完成"
    echo "🌐 访问地址: http://localhost:8080/claudeeditor_three_panel_ui.html"
fi

echo ""
echo "🎯 UI特色:"
echo "  ✨ 现代玻璃拟态设计风格"
echo "  🔮 三栏式专业开发界面"
echo "  🤖 Claude + K2 双AI架构"
echo "  🔄 六大工作流自动化"
echo "  📊 实时性能监控"
echo ""
echo "🛑 停止服务: pkill -f 'python3 -m http.server 8080'"
echo ""

# 自动打开浏览器 (macOS)
if command -v open &> /dev/null; then
    echo "🖥️  自动打开浏览器..."
    open "http://localhost:8080/claudeeditor_three_panel_ui.html"
fi