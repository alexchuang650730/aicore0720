#!/bin/bash

# PowerAutomation GitHub 部署脚本

set -e

echo "🚀 开始部署 PowerAutomation 到 GitHub..."

# 配置
GITHUB_USER="alexchuang650730"
GITHUB_REPO="aicore0718"
GITHUB_TOKEN="$1"
REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git"

# 检查参数
if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "❌ 使用方法: $0 <github_token>"
    echo "💡 示例: $0 github_pat_11AA3YQQA0jO6mQLbs0xJ5_..."
    exit 1
fi

# 检查Git状态
check_git_status() {
    echo "📋 检查Git状态..."
    
    if [[ ! -d .git ]]; then
        echo "🔧 初始化Git仓库..."
        git init
        git branch -M main
    fi
    
    # 配置Git用户信息
    git config user.name "Alex Chuang"
    git config user.email "alex.chuang@powerauto.ai"
    
    echo "✅ Git状态检查完成"
}

# 创建.gitignore文件
create_gitignore() {
    echo "📝 创建.gitignore文件..."
    
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
.idea/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
jspm_packages/

# Snowpack dependency directory
web_modules/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Optional stylelint cache
.stylelintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variable files
.env.development.local
.env.test.local
.env.production.local
.env.local

# parcel-bundler cache
.cache
.parcel-cache

# Next.js build output
.next
out

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# vue-cli / webpack
.vuepress/dist

# Docusaurus cache and generated files
.docusaurus

# Serverless directories
.serverless/

# FuseBox cache
.fusebox/

# DynamoDB Local files
.dynamodb/

# TernJS port file
.tern-port

# Stores VSCode versions used for testing VSCode extensions
.vscode-test

# yarn v2
.yarn/cache
.yarn/unplugged
.yarn/build-state.yml
.yarn/install-state.gz
.pnp.*

# PowerAutomation specific
*.db
*.sqlite
*.sqlite3
logs/
data/
uploads/
downloads/
temp/
.DS_Store
*.pid

# API Keys (never commit these)
.env
.env.local
.env.production
.env.development

# Claude Code Tool workspace
claude-code-workspace/

# Temporary files
*.tmp
*.temp
*.bak
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF

    echo "✅ .gitignore文件创建完成"
}

# 创建GitHub Actions工作流
create_github_actions() {
    echo "⚙️ 创建GitHub Actions工作流..."
    
    mkdir -p .github/workflows
    
    cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Install Node.js dependencies
      run: |
        cd claudeditor
        npm install
        cd ..
    
    - name: Run Python tests
      run: |
        pytest tests/ -v
    
    - name: Run linting
      run: |
        pip install black flake8
        black --check .
        flake8 .
    
    - name: Run type checking
      run: |
        pip install mypy
        mypy core/ --ignore-missing-imports

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security checks
      run: |
        pip install safety bandit
        safety check
        bandit -r core/ -f json

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Build package
      run: |
        pip install build
        python -m build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/
EOF

    cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy to Production

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run deployment tests
      run: |
        python -m pytest tests/deployment/ -v
    
    - name: Deploy to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
      run: |
        pip install twine build
        python -m build
        twine upload dist/*
EOF

    echo "✅ GitHub Actions工作流创建完成"
}

# 创建许可证文件
create_license() {
    echo "📄 创建许可证文件..."
    
    cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 Alex Chuang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

    echo "✅ 许可证文件创建完成"
}

# 创建贡献指南
create_contributing() {
    echo "📋 创建贡献指南..."
    
    cat > CONTRIBUTING.md << 'EOF'
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
EOF

    echo "✅ 贡献指南创建完成"
}

# 创建发布说明
create_release_notes() {
    echo "📰 创建发布说明..."
    
    cat > CHANGELOG.md << 'EOF'
# 更新日志

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2024-01-15

### 新增
- 🚀 PowerAutomation Core 驱动系统
- 🎯 六大核心工作流系统
- 🧠 开发目标精准化引擎
- 🔗 Claude Code Tool 双向通信
- 🤖 Kimi K2 智能助手集成
- 🎨 SmartUI 界面生成器
- 📚 Memory RAG 记忆增强系统
- 🔌 统一 MCP 服务器架构
- 🌐 增强版 ClaudeEditor WebUI
- 📊 实时监控和状态管理

### 六大工作流
1. **目标驱动开发工作流** - 确保开发不偏离目标
2. **智能代码生成工作流** - AI驱动的代码生成
3. **自动化测试验证工作流** - 全面的测试覆盖
4. **持续质量保证工作流** - 代码质量保障
5. **智能部署运维工作流** - 自动化部署运维
6. **自适应学习优化工作流** - 持续学习优化

### 核心特性
- ✅ 防止开发偏离用户目标
- ✅ Claude Code Tool 强大助手
- ✅ 双向通信和文件下载
- ✅ 统一命令执行架构
- ✅ 记忆增强和智能检索
- ✅ 多框架 UI 生成支持
- ✅ 企业级部署支持

### 技术架构
- 🏗️ 微服务化 MCP 组件架构
- 🔄 异步处理和并发支持
- 🛡️ 安全检查和权限管理
- 📊 性能监控和优化
- 🔧 易于扩展和维护

### 兼容性
- 🐍 Python 3.8+
- 🟢 Node.js 16+
- 🔧 Claude Code Tool (可选)
- 💻 macOS/Linux/Windows

## [未来计划]

### 计划新增
- 🌍 多语言支持
- 🔧 更多 AI 模型集成
- 📱 移动端适配
- 🏢 企业级功能增强
- 🔌 更多第三方工具集成

### 持续改进
- 📊 性能优化
- 🛡️ 安全增强
- 🎨 用户体验改进
- 📚 文档完善

---

**PowerAutomation - 让开发永不偏离目标！** 🎯
EOF

    echo "✅ 发布说明创建完成"
}

# 添加和提交文件
commit_files() {
    echo "📝 添加和提交文件..."
    
    # 添加所有文件
    git add .
    
    # 创建提交
    git commit -m "🚀 PowerAutomation v1.0.0 - 业界领先的工作流自动化解决方案

✨ 核心特性:
- PowerAutomation Core 驱动系统
- 六大核心工作流 (目标驱动、智能代码生成、自动化测试等)
- 开发目标精准化引擎 (防止偏离用户目标)
- Claude Code Tool 双向通信集成
- Kimi K2 智能助手 + SmartUI 界面生成
- Memory RAG 记忆增强系统
- 统一 MCP 服务器架构

🎯 解决核心问题:
- 开发过程与用户目标偏离
- 缺乏统一的工作流管理
- AI 工具集成复杂度高
- 记忆和学习能力不足

🚀 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    echo "✅ 文件提交完成"
}

# 推送到GitHub
push_to_github() {
    echo "🚀 推送到GitHub..."
    
    # 设置远程仓库
    git remote remove origin 2>/dev/null || true
    git remote add origin "$REMOTE_URL"
    
    # 推送到GitHub
    git push -u origin main --force
    
    echo "✅ 推送到GitHub完成"
}

# 创建发布标签
create_release_tag() {
    echo "🏷️ 创建发布标签..."
    
    # 创建标签
    git tag -a v1.0.0 -m "PowerAutomation v1.0.0 - 业界领先的工作流自动化解决方案

🎯 核心特性:
- 六大工作流系统
- 目标精准化引擎
- Claude Code Tool 集成
- Memory RAG 记忆增强
- PowerAutomation Core 驱动

🚀 让开发永不偏离目标！"
    
    # 推送标签
    git push origin v1.0.0
    
    echo "✅ 发布标签创建完成"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉 PowerAutomation 部署到 GitHub 完成！"
    echo ""
    echo "📋 部署信息："
    echo "🌐 GitHub 仓库: https://github.com/${GITHUB_USER}/${GITHUB_REPO}"
    echo "📦 发布版本: v1.0.0"
    echo "📚 项目文档: https://github.com/${GITHUB_USER}/${GITHUB_REPO}/blob/main/README.md"
    echo "🐛 问题反馈: https://github.com/${GITHUB_USER}/${GITHUB_REPO}/issues"
    echo ""
    echo "📥 本地部署命令："
    echo "git clone https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
    echo "cd ${GITHUB_REPO}"
    echo "chmod +x deployment/scripts/install.sh"
    echo "./deployment/scripts/install.sh"
    echo ""
    echo "🎯 PowerAutomation - 让开发永不偏离目标！"
}

# 主函数
main() {
    echo "🎯 PowerAutomation GitHub 部署程序"
    echo "==================================="
    
    check_git_status
    create_gitignore
    create_github_actions
    create_license
    create_contributing
    create_release_notes
    commit_files
    push_to_github
    create_release_tag
    show_deployment_info
}

# 运行主函数
main