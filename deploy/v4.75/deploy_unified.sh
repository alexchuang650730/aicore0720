#!/bin/bash
# 统一部署脚本

echo "🚀 PowerAutomation v4.75 统一部署"
echo "=================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$SCRIPT_DIR/deployment.log"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 错误处理
handle_error() {
    log "❌ 错误: $1"
    exit 1
}

# 前置检查
log "📋 执行前置检查..."
python3 "$SCRIPT_DIR/pre_deployment_check.py" || handle_error "前置检查失败"

# 1. 部署 Claude Code Tool
log "1️⃣ 部署 Claude Code Tool..."
bash "$SCRIPT_DIR/deploy_claude_code_tool.sh" || handle_error "Claude Code Tool 部署失败"

# 2. 部署 ClaudeEditor
log "2️⃣ 部署 ClaudeEditor (Web 版本)..."
bash "$SCRIPT_DIR/deploy_claudeditor.sh" web || handle_error "ClaudeEditor Web 部署失败"

# 3. 部署演示系统
log "3️⃣ 部署演示系统..."
cd "$SCRIPT_DIR"
npm install
npm run build
npm run serve:demo &
DEMO_PID=$!
log "演示系统 PID: $DEMO_PID"

# 4. 配置集成
log "4️⃣ 配置系统集成..."
python3 "$SCRIPT_DIR/configure_integration.py" || handle_error "集成配置失败"

# 5. 运行测试
log "5️⃣ 运行集成测试..."
npm test || handle_error "集成测试失败"

# 6. 生成部署报告
log "6️⃣ 生成部署报告..."
python3 "$SCRIPT_DIR/generate_deployment_report.py"

log "✅ 部署完成！"
log ""
log "访问地址:"
log "- Claude Code Tool: http://localhost:3001"
log "- ClaudeEditor: http://claudeditor.local"
log "- 演示系统: http://localhost:3000/demo"
log "- 监控面板: http://localhost:3000/metrics"
log ""
log "查看部署报告: $SCRIPT_DIR/deployment_report.html"
