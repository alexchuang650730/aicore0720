#!/bin/bash

echo "🔄 更新 Claude Code 代理到增强版..."

# 创建代理目录
mkdir -p ~/.powerautomation/proxy

# 复制增强版代理
cp /home/ubuntu/aicore0716/claude_code_enhanced_proxy.py ~/.powerautomation/proxy/claude_api_proxy.py

# 更新启动脚本
cat > ~/.powerautomation/proxy/start_claude_proxy.sh << 'EOF'
#!/bin/bash
echo "🚀 启动增强版 Claude API 代理服务器..."

# 安装依赖
pip3 install aiohttp --quiet 2>/dev/null || echo "⚠️ aiohttp 安装失败，但继续运行..."

# 启动增强版代理服务器
python3 ~/.powerautomation/proxy/claude_api_proxy.py
EOF

# 设置执行权限
chmod +x ~/.powerautomation/proxy/start_claude_proxy.sh

echo "✅ 增强版代理已更新！"
echo ""
echo "🚀 使用方法:"
echo "1. 停止当前代理 (Ctrl+C)"
echo "2. 启动增强版代理:"
echo "   bash ~/.powerautomation/proxy/start_claude_proxy.sh"
echo ""
echo "🔧 增强功能:"
echo "- ✅ 智能命令检测 (git, npm, pip, python 等)"
echo "- ✅ 正确端口路由 (Claude API: 443, K2: 443)"
echo "- ✅ 详细调试日志"
echo "- ✅ 自动故障回退"

