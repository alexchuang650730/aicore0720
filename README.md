# 🚀 PowerAutomation - 业界领先的个人/企业工作流自动化解决方案

## 📋 项目概述

PowerAutomation是一个完整的工作流自动化解决方案，旨在成为Claude Code Tool的强大助手，通过六大核心工作流和目标精准化系统，确保开发过程始终与用户目标保持一致。

## 🎯 核心特性

- ✅ **Claude Code Tool集成** - 双向通信，文件下载，命令执行
- ✅ **Kimi K2智能助手** - 中文优化，记忆增强
- ✅ **SmartUI界面生成** - 智能UI生成，多框架支持
- ✅ **六大工作流系统** - 全生命周期覆盖
- ✅ **Memory RAG记忆增强** - 智能记忆和检索
- ✅ **开发目标精准化** - 防止偏离用户目标
- ✅ **PowerAutomation Core驱动** - 统一驱动ClaudeEditor

## 🏗️ 系统架构

```
PowerAutomation Core (驱动器)
├── ClaudeEditor WebUI (用户界面)
├── Claude Router MCP (统一路由)
├── Command MCP (命令管理)
├── Local Adapter MCP (本地适配)
├── Memory RAG MCP (记忆系统)
├── Six Core Workflows (六大工作流)
└── Goal Precision Engine (目标精准化)
```

## 📂 项目结构

```
aicore0718/
├── README.md                              # 项目说明
├── requirements.txt                       # Python依赖
├── setup.py                              # 安装配置
├── core/                                 # 核心系统
│   ├── powerautomation_core_driver.py   # 核心驱动器
│   ├── components/                       # MCP组件
│   │   ├── command_mcp/                 # 命令管理
│   │   ├── local_adapter_mcp/           # 本地适配
│   │   ├── claude_router_mcp/           # Claude路由
│   │   ├── memoryos_mcp/               # 记忆系统
│   │   ├── test_mcp/                   # 测试管理
│   │   ├── stagewise_mcp/              # 阶段管理
│   │   └── smartui_mcp/                # 智能UI
│   └── workflows/                       # 工作流系统
│       └── six_core_workflows.py       # 六大工作流
├── claudeditor/                         # ClaudeEditor
│   ├── index.html                      # 主界面
│   ├── src/                           # 源代码
│   └── backend/                       # 后端服务
├── claude_code_integration/             # Claude Code集成
│   ├── bidirectional_bridge.py        # 双向通信桥梁
│   └── claudeditor_enhanced.py        # 增强版ClaudeEditor
├── goal_alignment_system/               # 目标对齐系统
│   └── goal_precision_engine.py       # 目标精准化引擎
├── mcp_server/                         # MCP服务器
│   ├── main.py                        # 主服务器
│   └── tools/                         # MCP工具
└── deployment/                         # 部署相关
    └── scripts/                       # 部署脚本
```

## 🚀 六大核心工作流

### 1. **目标驱动开发工作流**
- 目标分析 → 需求分解 → 实现规划 → 开发执行 → 目标验证 → 迭代反馈
- 确保开发始终与用户目标保持一致

### 2. **智能代码生成工作流**
- 规范分析 → 架构设计 → 代码生成 → 代码审查 → 优化 → 文档生成
- AI驱动的智能代码生成和优化

### 3. **自动化测试验证工作流**
- 测试规划 → 用例生成 → 单元测试 → 集成测试 → E2E测试 → 性能测试 → 验证报告
- 全面的自动化测试和验证

### 4. **持续质量保证工作流**
- 质量基线 → 代码分析 → 安全扫描 → 性能监控 → 质量门禁 → 持续改进
- 代码质量和安全保障

### 5. **智能部署运维工作流**
- 环境准备 → 部署规划 → 自动化部署 → 健康监控 → 回滚策略 → 运维优化
- 智能化部署和运维

### 6. **自适应学习优化工作流**
- 数据收集 → 模式分析 → 学习模型 → 优化策略 → 自适应实现 → 反馈循环
- 持续学习和系统优化

## 🛠️ 快速开始

### 1. 环境要求

- Python 3.8+
- Node.js 16+
- Claude Code Tool (可选)
- Git

### 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/alexchuang650730/aicore0718.git
cd aicore0718

# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖
cd claudeditor
npm install
cd ..
```

### 3. 配置环境变量

```bash
# 创建环境变量文件
cp .env.example .env

# 编辑环境变量
export CLAUDE_API_KEY="your_claude_api_key"
export KIMI_API_KEY="your_kimi_api_key"
export OPENAI_API_KEY="your_openai_api_key"
```

### 4. 启动系统

```bash
# 启动PowerAutomation Core驱动器
python core/powerautomation_core_driver.py

# 在另一个终端启动ClaudeEditor
python claude_code_integration/claudeditor_enhanced.py

# 在另一个终端启动MCP服务器
python mcp_server/main.py
```

### 5. 访问界面

- **ClaudeEditor WebUI**: http://localhost:8000
- **MCP服务器**: http://localhost:8765
- **API文档**: http://localhost:8000/docs

## 🎮 使用示例

### 1. 启动目标驱动开发工作流

```python
# 通过PowerAutomation Core驱动ClaudeEditor
result = await driver.drive_claudeditor(
    registration_id="your_registration_id",
    action="start_workflow",
    parameters={
        "workflow_type": "goal_driven_development",
        "user_goal": "创建用户管理系统",
        "requirements": ["用户注册", "用户登录", "权限管理"],
        "acceptance_criteria": ["功能正常", "性能良好", "安全可靠"]
    }
)
```

### 2. 执行Claude Code命令

```python
# 通过ClaudeEditor执行Claude Code命令
result = await driver.drive_claudeditor(
    registration_id="your_registration_id",
    action="execute_command",
    parameters={
        "command": "generate --type=component --name=UserLogin",
        "type": "claude_code",
        "parameters": {"framework": "react"}
    }
)
```

### 3. 生成SmartUI界面

```python
# 生成智能UI界面
result = await driver.drive_claudeditor(
    registration_id="your_registration_id",
    action="generate_ui",
    parameters={
        "description": "创建现代化的用户登录界面",
        "framework": "react",
        "style": "modern",
        "responsive": True
    }
)
```

## 🔧 配置说明

### 1. 核心配置

```python
# core/config.py
POWERAUTOMATION_CONFIG = {
    "driver": {
        "heartbeat_interval": 30,
        "monitoring_interval": 60,
        "max_claudeditor_instances": 10
    },
    "workflows": {
        "goal_driven_development": {"enabled": True, "timeout": 3600},
        "intelligent_code_generation": {"enabled": True, "timeout": 1800},
        "automated_testing_validation": {"enabled": True, "timeout": 2400},
        "continuous_quality_assurance": {"enabled": True, "timeout": 1200},
        "smart_deployment_ops": {"enabled": True, "timeout": 1800},
        "adaptive_learning_optimization": {"enabled": True, "timeout": 3600}
    },
    "memory_rag": {
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_index_type": "faiss",
        "max_memory_size": 10000
    }
}
```

### 2. ClaudeEditor配置

```json
{
  "claudeditor": {
    "host": "localhost",
    "port": 8000,
    "websocket_port": 8001,
    "features": {
      "claude_code_integration": true,
      "k2_chat": true,
      "smartui_generation": true,
      "memory_rag": true,
      "goal_precision": true
    }
  }
}
```

## 📊 性能指标

- **命令执行延迟**: < 200ms
- **工作流启动时间**: < 5s
- **记忆检索时间**: < 100ms
- **目标偏离检测**: 实时
- **系统可用性**: > 99.9%

## 🛡️ 安全特性

- **命令安全检查**: 防止危险命令执行
- **API访问控制**: 基于Token的认证
- **数据加密**: 敏感数据加密存储
- **审计日志**: 完整的操作日志
- **权限管理**: 分级权限控制

## 🔄 故障排除

### 常见问题

1. **Claude Code Tool连接失败**
   ```bash
   # 检查Claude Code Tool是否安装
   claude-code --version
   
   # 检查环境变量
   echo $CLAUDE_API_KEY
   ```

2. **MCP服务器启动失败**
   ```bash
   # 检查端口占用
   lsof -i :8765
   
   # 检查依赖
   pip list | grep mcp
   ```

3. **ClaudeEditor无法访问**
   ```bash
   # 检查服务状态
   curl http://localhost:8000/api/status
   
   # 查看日志
   tail -f logs/claudeditor.log
   ```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送到分支: `git push origin feature/amazing-feature`
5. 打开Pull Request

## 📄 许可证

本项目基于MIT许可证开源 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Claude Code Tool](https://docs.anthropic.com/claude-code) - 强大的AI编程助手
- [Kimi K2](https://kimi.moonshot.cn) - 中文优化的AI模型
- [MCP Protocol](https://github.com/modelcontextprotocol/python-sdk) - 模型上下文协议

## 📧 联系我们

- 作者: Alex Chuang
- 邮箱: alex.chuang@powerautomation.ai
- GitHub: [@alexchuang650730](https://github.com/alexchuang650730)
- 项目地址: https://github.com/alexchuang650730/aicore0718

---

**PowerAutomation - 让开发永不偏离目标！** 🎯