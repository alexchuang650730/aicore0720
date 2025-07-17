# PowerAutomation 智能启动触发机制使用指南

## 🎯 概述

PowerAutomation v4.6.9.6 引入了基于钩子和 Mirror Code 的智能启动触发机制，解决了 Claude Code 执行时 ClaudeEditor 未安装的问题。

## 🚀 核心功能

### 1. 智能触发词检测
系统能够自动检测以下触发词并执行相应动作：

#### ClaudeEditor 安装触发词
- `需要 ClaudeEditor`
- `启动编辑器`
- `安装 ClaudeEditor`
- `打开编辑界面`
- `PowerAutomation setup`
- `初始化编辑环境`

#### Mirror Code 同步触发词
- `同步代码`
- `Mirror Code`
- `双向通信`
- `代码镜像`
- `实时同步`

#### 系统状态检查触发词
- `系统就绪`
- `检查状态`
- `系统状态`
- `服务状态`

### 2. 自动化动作执行
- **自动安装**: 检测到需求时自动下载并安装 ClaudeEditor
- **环境准备**: 自动配置开发环境和依赖
- **服务启动**: 自动启动 ClaudeEditor 开发服务器
- **通信建立**: 建立 Claude Code 与 ClaudeEditor 的双向通信

### 3. 钩子系统集成
- **用户输入钩子**: 监听用户输入并检测触发词
- **命令执行钩子**: 在命令执行前检测环境需求
- **工作流钩子**: 在工作流开始时准备环境
- **状态变更钩子**: 监控系统状态变更

## 📋 使用方法

### 方法一：直接触发（推荐）
在 Claude Code 中直接说出触发词：

```
需要 ClaudeEditor
```

系统将自动：
1. 检测触发词
2. 下载并安装 ClaudeEditor
3. 启动开发服务器
4. 建立双向通信
5. 返回访问地址

### 方法二：命令行接口
```bash
# 初始化触发管理器
python3 -m core.components.startup_trigger_mcp.startup_trigger_manager --action init

# 手动触发检测
python3 -m core.components.startup_trigger_mcp.startup_trigger_manager --action trigger --text "需要 ClaudeEditor"

# 检查系统状态
python3 -m core.components.startup_trigger_mcp.startup_trigger_manager --action status

# 运行测试
python3 -m core.components.startup_trigger_mcp.startup_trigger_manager --action test
```

### 方法三：自动安装脚本
```bash
# 直接运行自动安装脚本
bash claudeditor/scripts/auto_setup_claudeeditor.sh
```

## 🔧 配置选项

### 触发配置
```python
from core.components.startup_trigger_mcp import StartupTriggerConfig

config = StartupTriggerConfig(
    auto_trigger_enabled=True,      # 启用自动触发
    auto_install_enabled=True,      # 启用自动安装
    mirror_code_enabled=True,       # 启用 Mirror Code
    hook_integration_enabled=True,  # 启用钩子集成
    heartbeat_interval=30,          # 心跳间隔（秒）
    log_level="INFO"               # 日志级别
)
```

## 📊 系统状态监控

### 状态检查
```python
from core.components.startup_trigger_mcp import startup_trigger_manager

# 获取系统状态
status = await startup_trigger_manager.check_system_status()
print(status)
```

### 状态指标
- **ClaudeEditor 安装状态**: 是否已安装
- **ClaudeEditor 运行状态**: 是否正在运行
- **Mirror Code 状态**: 双向通信是否活跃
- **触发统计**: 触发次数和成功率
- **通信通道**: HTTP、WebSocket、文件通道状态

## 🧪 测试验证

### 运行测试套件
```bash
cd /home/ubuntu/aicore0716
python3 tests/test_startup_trigger.py
```

### 测试覆盖
- **触发检测测试**: 验证各种触发词的检测
- **动作执行测试**: 验证自动化动作的执行
- **钩子集成测试**: 验证钩子系统的集成
- **通信测试**: 验证 Mirror Code 双向通信
- **集成场景测试**: 验证完整的触发流程

## 🔍 故障排除

### 常见问题

#### 1. ClaudeEditor 安装失败
**症状**: 触发后 ClaudeEditor 未成功安装
**解决方案**:
```bash
# 检查网络连接
curl -I https://github.com/alexchuang650730/aicore0716.git

# 手动运行安装脚本
bash claudeditor/scripts/auto_setup_claudeeditor.sh

# 检查日志
tail -f /tmp/claudeeditor.log
```

#### 2. 触发词未被检测
**症状**: 说出触发词但系统无响应
**解决方案**:
```bash
# 检查触发系统状态
python3 -m core.components.startup_trigger_mcp.startup_trigger_manager --action status

# 手动测试触发
python3 -m core.components.startup_trigger_mcp.startup_trigger_manager --action trigger --text "需要 ClaudeEditor"
```

#### 3. 双向通信失败
**症状**: ClaudeEditor 启动但无法通信
**解决方案**:
```bash
# 检查端口占用
lsof -Pi :5176 -sTCP:LISTEN

# 检查通信状态文件
cat /tmp/claude_code_ready

# 重启 ClaudeEditor
pkill -f "vite.*5176"
bash claudeditor/scripts/auto_setup_claudeeditor.sh
```

### 日志文件位置
- **启动触发日志**: `/tmp/startup_trigger.log`
- **ClaudeEditor 日志**: `/tmp/claudeeditor.log`
- **MCP 协调器日志**: `/tmp/mcp_coordinator.log`
- **测试报告**: `/tmp/startup_trigger_test_report.json`

## 🎯 最佳实践

### 1. 使用建议
- 优先使用自然语言触发词
- 定期检查系统状态
- 保持网络连接稳定
- 及时查看日志文件

### 2. 性能优化
- 避免频繁触发安装
- 使用心跳机制维持连接
- 定期清理临时文件
- 监控资源使用情况

### 3. 安全考虑
- 仅在可信环境中使用
- 定期更新依赖包
- 监控异常行为
- 备份重要配置

## 📈 版本历史

### v4.6.9.6-startup-trigger
- ✨ 新增智能启动触发机制
- 🎯 支持多种触发词检测
- 🚀 自动化 ClaudeEditor 安装
- 🔄 Mirror Code 双向通信
- 🧪 完整测试套件验证

## 🤝 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. Fork 项目仓库
2. 创建功能分支
3. 提交代码更改
4. 运行测试套件
5. 提交 Pull Request

## 📞 支持与反馈

如有问题或建议，请：
- 提交 GitHub Issue
- 查看项目文档
- 运行诊断命令
- 检查日志文件

---

**PowerAutomation Team**  
版本: v4.6.9.6-startup-trigger  
更新时间: 2025-07-15

