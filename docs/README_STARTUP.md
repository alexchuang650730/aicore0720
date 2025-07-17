# PowerAutomation v4.6.9.5 启动指南

## 🚀 **统一启动方式**

现在当您执行 Claude Code 时，整个 PowerAutomation 生态系统会自动启动！

### ✅ **一键启动完整生态系统**

```bash
# 方式1: 使用 Claude 包装器 (推荐)
./claude "你的命令"

# 方式2: 直接启动生态系统
python start_powerautomation_ecosystem.py

# 方式3: 启动并执行 Claude 命令
python start_powerautomation_ecosystem.py --claude-command "分析这个代码"
```

## 🌟 **启动流程**

当您运行 `./claude` 时，系统会自动：

### 1. **环境检查**
- ✅ 检查 Node.js 和 Python 环境
- ✅ 验证 ClaudeEditor 目录结构
- ✅ 确认所有依赖项

### 2. **服务启动顺序**
1. **ClaudeEditor API** (后端) - `http://localhost:5000`
2. **Command MCP** (集成 Mirror Code) - 后台服务
3. **ClaudeEditor 前端** - `http://localhost:3000`

### 3. **自动配置**
- 🤖 **默认模型**: K2 本地模型 (免费、快速)
- 🪞 **Mirror Code**: 已集成到 Command MCP
- 🔄 **智能路由**: K2 优先，Claude Code 备用
- 📱 **ClaudeEditor**: 完整的 AI 代码编辑器

## 📊 **启动完成后的状态**

```
🎉 PowerAutomation v4.6.9.5 生态系统启动完成！

📋 运行中的服务:
  ✅ ClaudeEditor API (PID: xxxx)
     🌐 http://localhost:5000
  ✅ Command MCP (集成 Mirror Code) (PID: xxxx)
  ✅ ClaudeEditor 前端 (PID: xxxx)
     🌐 http://localhost:3000

🌟 核心特性:
  🤖 默认模型: K2 本地模型 (免费、快速)
  🪞 Mirror Code: 已集成到 Command MCP
  🔄 智能路由: K2 优先，Claude Code 备用
  📱 ClaudeEditor: 跨平台 AI 代码编辑器

🔗 访问地址:
  📱 ClaudeEditor: http://localhost:3000
  🔌 API 服务: http://localhost:5000

💡 使用提示:
  - 在 ClaudeEditor 中使用 /help 查看所有指令
  - 默认使用 K2 本地模型，无需 API 费用
  - 使用 /switch-model claude 切换到 Claude Code
  - 按 Ctrl+C 停止所有服务
```

## 🎯 **核心优势**

### ✨ **默认 K2 优先策略**
- 🥇 **主要模型**: K2 本地模型 (100% 免费)
- 🥈 **备用模型**: Claude Code (用户明确选择时)
- 🪞 **Mirror Code**: 集成模式，无需独立服务
- ⚡ **响应速度**: 本地处理，零延迟

### 🔄 **智能路由机制**
- 所有指令默认使用 K2 本地处理
- 只有用户明确要求时才使用 Claude Code
- 自动回退机制确保服务可用性
- 实时使用统计和成本分析

### 📱 **完整生态系统**
- **ClaudeEditor**: AI 代码编辑器
- **Command MCP**: 指令处理中心
- **Mirror Code**: 智能模型路由
- **Task Sync**: 任务同步服务

## 🛠️ **使用示例**

### 基础使用
```bash
# 启动并执行简单命令
./claude "帮我分析这个 Python 文件"

# 启动并进入交互模式
./claude
```

### 在 ClaudeEditor 中使用
1. 访问 `http://localhost:3000`
2. 在左侧任务列表中查看任务
3. 使用 AI 助手执行指令：
   - `/help` - 查看所有可用指令
   - `/status` - 查看系统状态
   - `/chat 你好` - 与 K2 对话
   - `/switch-model claude` - 切换到 Claude Code

### 模型切换
```bash
# 在 ClaudeEditor 中
/switch-model k2      # 切换到 K2 (默认)
/switch-model claude  # 切换到 Claude Code
/usage               # 查看使用统计
```

## 🔧 **故障排除**

### 常见问题

#### 1. **端口被占用**
```bash
# 检查端口使用情况
lsof -i :3000  # ClaudeEditor 前端
lsof -i :5000  # ClaudeEditor API

# 杀死占用进程
kill -9 <PID>
```

#### 2. **Node.js 依赖问题**
```bash
cd claudeditor
npm install  # 重新安装依赖
```

#### 3. **Python 模块问题**
```bash
pip install -r requirements.txt  # 如果有的话
```

### 手动启动单个服务

如果需要单独启动某个服务：

```bash
# 只启动 ClaudeEditor 前端
cd claudeditor && npm start

# 只启动 ClaudeEditor API
cd claudeditor && python api/src/main.py

# 只启动 Command MCP
python -c "from core.components.command_mcp.command_manager import ClaudeCodeSlashCommandHandler; import asyncio; handler = ClaudeCodeSlashCommandHandler(); asyncio.get_event_loop().run_forever()"
```

## 📈 **性能监控**

### 查看系统状态
- 在 ClaudeEditor 中使用 `/status`
- 查看使用统计：`/usage`
- 监控模型切换：`/switch-model`

### 日志查看
- 启动日志会显示在终端
- ClaudeEditor 日志在浏览器控制台
- 服务状态实时显示

## 🎉 **总结**

现在您只需要运行 `./claude` 就能启动完整的 PowerAutomation 生态系统：

1. ✅ **ClaudeEditor 自动启动**
2. ✅ **PowerAutomation Core 自动启动**  
3. ✅ **Command MCP 自动启动**
4. ✅ **Mirror Code 自动集成**
5. ✅ **默认 K2 优先策略**

一个命令，完整生态系统！🚀

