# ClaudeEditor 目录结构

## 📁 **标准目录结构**

```
claudeditor/
├── src/                      # 主要源代码
│   ├── claudeditor_ui_main.py
│   ├── claudeditor_agui_interface.py
│   ├── claudeditor_simple_ui_server.py
│   └── claudeditor_testing_management_ui.py
├── api/                      # API 相关文件
│   ├── ai_assistant_backend.py
│   ├── session_sharing_backend.py
│   └── url_processor.py
├── components/               # 组件和生成器
│   └── claudeditor_test_generator.py
├── scripts/                  # 安装和配置脚本
│   └── auto_setup_claudeeditor.sh
├── integration/              # 集成测试和组件
│   ├── claude_claudeditor_integration_simple_test.py
│   └── claude_claudeditor_integration_test.py
├── tests/                    # 单元测试和功能测试
│   ├── claudeditor_ai_assistant_integration.py
│   ├── claudeditor_claude_code_integration.py
│   ├── claudeditor_cli.sh
│   ├── claudeditor_completion_report.py
│   ├── claudeditor_desktop_tester.py
│   ├── claudeditor_enhanced_left_panel.py
│   ├── claudeditor_final_demo.py
│   ├── claudeditor_workflow_interface.py
│   ├── deploy_claudeditor_local.py
│   ├── kimi_k2_claudeditor_integration.py
│   ├── start_claudeditor.sh
│   └── test_claudeditor_integration.py
├── utils/                    # 工具函数
├── static/                   # 静态资源
├── templates/                # 模板文件
├── src-tauri/                # Tauri 桌面应用
├── ui/                       # 用户界面组件
├── node_modules/             # Node.js 依赖
├── claudeditor_demo.html     # 演示页面
├── package.json              # Node.js 包配置
├── package-lock.json         # 依赖锁定文件
├── tsconfig.json             # TypeScript 配置
├── vite.config.js            # Vite 构建配置
└── README.md                 # 项目说明
```

## 🎯 **目录功能说明**

### **src/** - 主要源代码
- `claudeditor_ui_main.py` - ClaudeEditor 主界面入口
- `claudeditor_agui_interface.py` - AG-UI 智能界面组件
- `claudeditor_simple_ui_server.py` - 轻量级 Web 界面服务
- `claudeditor_testing_management_ui.py` - 测试管理界面

### **api/** - API 相关文件
- `ai_assistant_backend.py` - AI 助手后端服务
- `session_sharing_backend.py` - 会话共享后端
- `url_processor.py` - URL 处理器

### **components/** - 组件和生成器
- `claudeditor_test_generator.py` - 测试生成器组件

### **scripts/** - 安装和配置脚本
- `auto_setup_claudeeditor.sh` - 自动安装配置脚本

### **integration/** - 集成测试和组件
- `claude_claudeditor_integration_simple_test.py` - 简单集成测试
- `claude_claudeditor_integration_test.py` - 完整集成测试

### **tests/** - 单元测试和功能测试
- `claudeditor_ai_assistant_integration.py` - AI 助手集成测试
- `claudeditor_claude_code_integration.py` - Claude Code 集成测试
- `claudeditor_cli.sh` - 命令行界面测试
- `claudeditor_completion_report.py` - 完成报告生成
- `claudeditor_desktop_tester.py` - 桌面应用测试
- `claudeditor_enhanced_left_panel.py` - 增强左侧面板测试
- `claudeditor_final_demo.py` - 最终演示
- `claudeditor_workflow_interface.py` - 工作流界面测试
- `deploy_claudeditor_local.py` - 本地部署测试
- `kimi_k2_claudeditor_integration.py` - Kimi K2 集成测试
- `start_claudeditor.sh` - 启动脚本
- `test_claudeditor_integration.py` - E2E 集成测试

## 🚀 **使用指南**

### **启动主界面**
```bash
python claudeditor/src/claudeditor_ui_main.py
```

### **启动 AG-UI 界面**
```bash
python claudeditor/src/claudeditor_agui_interface.py
```

### **启动简化服务器**
```bash
python claudeditor/src/claudeditor_simple_ui_server.py
```

### **运行集成测试**
```bash
python claudeditor/integration/claude_claudeditor_integration_simple_test.py
```

### **运行完整测试套件**
```bash
bash claudeditor/tests/claudeditor_cli.sh
```

## 📊 **文件统计**

- **Python 文件**: 21 个
- **JavaScript/TypeScript 文件**: 7,176 个
- **HTML 文件**: 8 个
- **配置文件**: 5 个
- **脚本文件**: 3 个
- **总文件数**: 14,183 个

## 🔧 **开发指南**

### **添加新组件**
1. 在 `src/` 目录下创建新的 Python 文件
2. 遵循 `claudeditor_` 前缀命名规范
3. 在 `tests/` 目录下添加对应的测试文件
4. 更新此文档

### **集成新功能**
1. 在 `integration/` 目录下创建集成测试
2. 确保与 Claude Code 和 MemoryOS MCP 的兼容性
3. 更新相关的 API 文件

## 📝 **文件移动历史**

### **v4.6.9.8 重构 (2025-07-16)**
- 将 `tests/claudeditor_*` 文件移动到 `claudeditor/tests/`
- 将 `tests/desktop/claudeditor_*` 文件移动到 `claudeditor/tests/`
- 将 `tests/e2e/test_claudeditor_integration.py` 移动到 `claudeditor/tests/`
- 统一了所有 claudeditor 相关文件的组织结构

### **v4.6.9.7 初始整理 (2025-07-15)**
- 创建了基本的目录结构
- 移动了主要的源代码文件到 `src/` 目录
- 移动了 API 文件到 `api/` 目录

## 🎯 **与 PowerAutomation 的集成**

ClaudeEditor 作为 PowerAutomation 的重要组成部分，与以下组件深度集成：

- **claude_router_mcp** - 统一的 MCP 路由服务
- **memoryos_mcp** - 内存和数据存储
- **task_management** - 任务管理系统
- **Claude Code** - 代码生成和执行

## 📈 **版本信息**

- **当前版本**: v4.6.9.8
- **最后更新**: 2025-07-16
- **维护团队**: PowerAutomation Team
- **许可证**: MIT License

