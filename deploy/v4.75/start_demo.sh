#!/bin/bash

# PowerAutomation v4.75 演示启动脚本

echo "═══════════════════════════════════════════════════════════"
echo "    PowerAutomation v4.75 演示系统启动"
echo "    Claude Code Tool + ClaudeEditor 集成演示"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 设置路径
DEPLOY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname $(dirname $DEPLOY_DIR))"

# 检查依赖
echo "📋 检查系统依赖..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python3"
    exit 1
fi

echo "✅ 依赖检查通过"

# 创建演示服务器
echo ""
echo "🚀 启动演示服务器..."

# 创建简单的 HTTP 服务器来展示演示组件
cat > "$DEPLOY_DIR/demo_server.py" << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import json
from pathlib import Path

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 处理根路径
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>PowerAutomation v4.75 演示系统</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .demo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        .demo-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .demo-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }
        .demo-card h3 {
            margin-top: 0;
            color: #333;
        }
        .demo-card p {
            color: #666;
            line-height: 1.6;
        }
        .demo-link {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
        }
        .demo-link:hover {
            background: #5a5ed8;
        }
        .status {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.875rem;
            margin-left: 0.5rem;
        }
        .status.ready { background: #10b981; color: white; }
        .status.beta { background: #f59e0b; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>PowerAutomation v4.75 演示系统</h1>
        <p>Claude Code Tool + ClaudeEditor 无缝集成</p>
    </div>
    
    <div class="container">
        <h2>核心组件演示</h2>
        
        <div class="demo-grid">
            <div class="demo-card">
                <h3>StageWise 命令演示 <span class="status ready">Ready</span></h3>
                <p>展示 Claude Code Tool 原生命令在 K2 模式下的完整支持，包括 19 个命令的兼容性测试。</p>
                <a href="/stagewise-demo" class="demo-link">查看演示</a>
            </div>
            
            <div class="demo-card">
                <h3>统一部署系统 <span class="status ready">Ready</span></h3>
                <p>一键部署 Claude Code Tool 和 ClaudeEditor，实现无缝集成和实时同步。</p>
                <a href="/deployment" class="demo-link">部署管理</a>
            </div>
            
            <div class="demo-card">
                <h3>工作流自动化 <span class="status ready">Ready</span></h3>
                <p>六大工作流自动化，集成 GitHub 实时数据，展示技术和体验双指标。</p>
                <a href="/workflow" class="demo-link">查看指标</a>
            </div>
            
            <div class="demo-card">
                <h3>指标可视化 <span class="status ready">Ready</span></h3>
                <p>综合指标可视化仪表板，包括雷达图、趋势图、热力图等多维度展示。</p>
                <a href="/metrics" class="demo-link">查看仪表板</a>
            </div>
            
            <div class="demo-card">
                <h3>SmartUI 合规性 <span class="status ready">Ready</span></h3>
                <p>AG-UI/SmartUI 规范遵循度、规格覆盖率和测试覆盖率分析。</p>
                <a href="/smartui" class="demo-link">分析报告</a>
            </div>
            
            <div class="demo-card">
                <h3>测试验证系统 <span class="status ready">Ready</span></h3>
                <p>实时测试执行、数据收集和验证指标的量化展示。</p>
                <a href="/test-validation" class="demo-link">查看测试</a>
            </div>
        </div>
        
        <h2 style="margin-top: 3rem;">快速访问</h2>
        <div style="background: white; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
            <h4 style="margin-top: 0;">API 端点</h4>
            <ul>
                <li><strong>Claude Code Tool MCP:</strong> http://localhost:3001</li>
                <li><strong>K2 优化器:</strong> http://localhost:3002</li>
                <li><strong>指标收集器:</strong> http://localhost:3003/metrics</li>
            </ul>
            
            <h4>开发工具</h4>
            <ul>
                <li><strong>部署脚本:</strong> <code>bash deploy_unified.sh</code></li>
                <li><strong>查看日志:</strong> <code>tail -f deployment.log</code></li>
                <li><strong>性能监控:</strong> <code>npm run monitor</code></li>
            </ul>
            
            <h4>文档和报告</h4>
            <ul>
                <li><a href="/deployment_report.html">部署报告</a></li>
                <li><a href="/metrics_formulas.md">指标计算公式</a></li>
                <li><a href="/workflow_config.json">工作流配置</a></li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 3rem; color: #666;">
            <p>PowerAutomation v4.75 - K2 优化器集成版</p>
            <p>成本节省 80% · 响应时间 <100ms · 命令兼容性 100%</p>
        </div>
    </div>
</body>
</html>
"""
            self.wfile.write(html.encode())
            
        # 处理演示页面路由
        elif self.path == '/stagewise-demo':
            self.serve_demo_page('StageWise 命令演示', 'StageWiseCommandDemo.jsx')
        elif self.path == '/deployment':
            self.serve_demo_page('统一部署系统', 'UnifiedDeploymentUI.jsx')
        elif self.path == '/workflow':
            self.serve_demo_page('工作流自动化', 'WorkflowAutomationDashboard.jsx')
        elif self.path == '/metrics':
            self.serve_demo_page('指标可视化', 'MetricsVisualizationDashboard.jsx')
        elif self.path == '/smartui':
            self.serve_demo_page('SmartUI 合规性', 'AGUIComplianceDashboard.jsx')
        elif self.path == '/test-validation':
            self.serve_demo_page('测试验证系统', 'TestValidationDashboard.jsx')
        else:
            # 提供静态文件
            super().do_GET()
    
    def serve_demo_page(self, title, component_file):
        """提供演示页面"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title} - PowerAutomation v4.75</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/recharts@2/umd/Recharts.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .demo-notice {{
            background: #fef3c7;
            border: 1px solid #f59e0b;
            padding: 1rem;
            margin: 1rem;
            border-radius: 0.5rem;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div id="root"></div>
    <div class="demo-notice">
        <p><strong>演示模式:</strong> 这是 {component_file} 组件的静态演示。实际运行需要完整的 React 环境。</p>
        <p>查看源代码: <code>/deploy/v4.75/{component_file}</code></p>
        <a href="/" style="color: #3b82f6; text-decoration: underline;">返回主页</a>
    </div>
    
    <div style="padding: 2rem;">
        <h1 style="font-size: 2rem; font-weight: bold; margin-bottom: 2rem;">{title}</h1>
        <div style="background: white; padding: 2rem; border-radius: 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <p>组件 <strong>{component_file}</strong> 包含以下功能：</p>
            <ul style="list-style: disc; margin-left: 2rem; margin-top: 1rem;">
                <li>实时数据展示和更新</li>
                <li>交互式图表和可视化</li>
                <li>响应式设计，支持多设备</li>
                <li>K2 模型集成和优化</li>
            </ul>
            
            <div style="margin-top: 2rem; padding: 1rem; background: #f3f4f6; border-radius: 0.5rem;">
                <h3 style="font-weight: bold; margin-bottom: 0.5rem;">如何在生产环境运行：</h3>
                <pre style="background: #1f2937; color: white; padding: 1rem; border-radius: 0.25rem; overflow-x: auto;">
# 1. 安装依赖
npm install

# 2. 构建项目
npm run build

# 3. 启动服务
npm start

# 4. 访问应用
open http://localhost:3000</pre>
            </div>
        </div>
    </div>
</body>
</html>
"""
        self.wfile.write(html.encode())

# 启动服务器
PORT = 8080
with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
    print(f"✅ 演示服务器已启动: http://localhost:{PORT}")
    print("")
    print("📋 可用的演示：")
    print("   - StageWise 命令演示: http://localhost:{PORT}/stagewise-demo")
    print("   - 统一部署系统: http://localhost:{PORT}/deployment")
    print("   - 工作流自动化: http://localhost:{PORT}/workflow")
    print("   - 指标可视化: http://localhost:{PORT}/metrics")
    print("")
    print("按 Ctrl+C 停止服务器")
    httpd.serve_forever()
EOF

# 启动演示服务器
python3 "$DEPLOY_DIR/demo_server.py"