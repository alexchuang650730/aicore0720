# 贡献指南

感谢您对 PowerAutomation 项目的关注！

## 🚀 快速开始

1. **Fork 项目**
2. **克隆到本地**
   ```bash
   git clone https://github.com/your-username/aicore0718.git
   cd aicore0718
   ```

3. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   cd claudeditor && npm install && cd ..
   ```

5. **运行测试**
   ```bash
   pytest tests/ -v
   ```

## 📝 代码规范

### Python 代码
- 使用 Black 进行代码格式化
- 使用 flake8 进行代码检查
- 使用 mypy 进行类型检查
- 遵循 PEP 8 代码风格

### JavaScript 代码
- 使用 ESLint 进行代码检查
- 使用 Prettier 进行代码格式化
- 遵循 ES6+ 标准

### 提交消息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型:**
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式化
- refactor: 重构
- test: 测试相关
- chore: 构建工具或辅助工具的变动

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_workflows.py -v

# 运行覆盖率测试
pytest tests/ --cov=core --cov-report=html
```

### 编写测试
- 为新功能编写单元测试
- 为复杂逻辑编写集成测试
- 确保测试覆盖率 > 80%

## 🔧 开发流程

1. **创建Issue** - 描述问题或功能需求
2. **讨论设计** - 在Issue中讨论实现方案
3. **编写代码** - 遵循代码规范
4. **编写测试** - 确保功能正确
5. **提交PR** - 详细描述变更内容
6. **代码审查** - 等待维护者审查
7. **合并代码** - 审查通过后合并

## 📊 项目结构

```
aicore0718/
├── core/                    # 核心系统
├── claudeditor/            # ClaudeEditor
├── mcp_server/             # MCP服务器
├── tests/                  # 测试文件
├── deployment/             # 部署脚本
└── docs/                   # 文档
```

## 🤝 提交 Pull Request

1. **确保代码质量**
   - 所有测试通过
   - 代码格式正确
   - 无明显性能问题

2. **详细描述变更**
   - 解释为什么需要这个变更
   - 描述具体的变更内容
   - 如果修复了bug，请提供复现步骤

3. **更新文档**
   - 如果添加了新功能，请更新README.md
   - 如果修改了API，请更新API文档

## 🐛 报告问题

请使用 GitHub Issues 报告问题：

1. **搜索现有Issue** - 确保问题未被报告
2. **使用模板** - 使用提供的Issue模板
3. **提供详细信息** - 包括错误消息、复现步骤等
4. **添加标签** - 选择合适的标签

## 📧 联系我们

- **邮箱**: alex.chuang@powerauto.ai
- **GitHub**: [@alexchuang650730](https://github.com/alexchuang650730)
- **Issues**: [GitHub Issues](https://github.com/alexchuang650730/aicore0718/issues)

---

**感谢您的贡献！** 🙏
