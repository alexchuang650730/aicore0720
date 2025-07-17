# PowerAutomation ClaudeEditor v4.6.9.5
## 跨平台 AI 代码编辑器 - 完整安装包

### 🚀 一键安装

#### 方式一：curl 安装 (推荐)
```bash
# 自动检测平台并安装
curl -fsSL https://install.powerautomation.ai | bash

# 指定安装类型
curl -fsSL https://install.powerautomation.ai | bash -s -- --desktop
curl -fsSL https://install.powerautomation.ai | bash -s -- --mobile
curl -fsSL https://install.powerautomation.ai | bash -s -- --web
```

#### 方式二：npm 安装
```bash
# 全局安装
npm install -g @powerautomation/claudeeditor

# 创建项目
npx create-powerautomation-app my-project --type=desktop
cd my-project
npm start
```

#### 方式三：Git 克隆
```bash
git clone https://github.com/alexchuang650730/aicore0711.git
cd aicore0711
npm install
node scripts/install.js
```

### 📱 支持的平台

| 平台 | 框架 | 特性 | K2 模型 |
|------|------|------|---------|
| **桌面版** | Electron | 完整 IDE + 本地 K2 | 本地运行 |
| **移动版** | Capacitor | 触控优化 + 云端 K2 | 云端 API |
| **Web 版** | React | 响应式 + API K2 | API 调用 |

### 🎯 平台特定功能

#### 🖥️ 桌面版 (Windows/macOS/Linux)
- ✅ **K2 本地模型** - 完全离线运行
- ✅ **完整 IDE 功能** - 多窗口、文件管理
- ✅ **Mirror Code** - 智能路由到 K2
- ✅ **系统集成** - 系统托盘、快捷键
- ✅ **自动更新** - 后台自动更新

**安装要求：**
- Node.js >= 16.0.0
- Python 3.x (用于 K2 本地模型)
- 4GB+ RAM

**启动命令：**
```bash
./powerautomation          # 启动应用
npm start                  # 开发模式
npm run build:desktop      # 构建桌面应用
```

#### 📱 移动版 (Android/iOS)
- ✅ **触控优化界面** - 专为移动设备设计
- ✅ **K2 云端模型** - 通过 API 访问
- ✅ **离线缓存** - 代码和配置本地缓存
- ✅ **原生集成** - 文件系统、分享功能
- ✅ **推送通知** - 任务完成通知

**安装要求：**
- Node.js >= 16.0.0
- Android SDK (Android) 或 Xcode (iOS)
- 网络连接 (用于 K2 云端模型)

**启动命令：**
```bash
npm run dev                # 开发模式
npx cap run android        # 运行到 Android
npx cap run ios            # 运行到 iOS
npm run build:mobile       # 构建移动应用
```

#### 🌐 Web 版 (浏览器)
- ✅ **响应式设计** - 适配所有屏幕尺寸
- ✅ **K2 API 模型** - 通过 API 访问
- ✅ **即时访问** - 无需安装
- ✅ **跨平台兼容** - 支持所有现代浏览器
- ✅ **PWA 支持** - 可安装为 Web 应用

**安装要求：**
- Node.js >= 16.0.0
- 现代浏览器 (Chrome, Firefox, Safari, Edge)
- 网络连接

**启动命令：**
```bash
npm start                  # 启动开发服务器
npm run build              # 构建生产版本
# 访问: http://localhost:3000
```

### 🤖 AI 模型支持

#### K2 本地模型 (桌面版)
- **完全免费** - 无 API 费用
- **完全离线** - 无需网络连接
- **隐私保护** - 代码不离开本地
- **快速响应** - 本地处理，无延迟

#### K2 云端模型 (移动版/Web版)
- **高性能** - 云端 GPU 加速
- **实时更新** - 模型持续优化
- **多设备同步** - 跨设备使用
- **按需付费** - 只为使用付费

#### Claude Code (备用)
- **高质量** - Anthropic 官方模型
- **代码专精** - 专为编程优化
- **用户选择** - 手动切换使用
- **API 计费** - 按 Token 计费

### 🔧 核心功能

#### 🪞 Mirror Code 智能路由
- **K2 优先策略** - 默认使用 K2 模型
- **智能回退** - K2 不支持时自动切换
- **成本优化** - 最大化使用免费 K2
- **使用统计** - 详细的使用和成本分析

#### 📡 Command MCP
- **统一指令接口** - 支持所有 Claude Code 指令
- **K2 原生支持** - 19个指令完全支持
- **智能补全** - 自动补全和建议
- **批量处理** - 支持批量操作

#### 🔄 任务同步
- **实时同步** - ClaudeEditor 和 Claude Code 双向通信
- **任务列表** - 左侧任务面板显示所有任务
- **多智能体** - 支持 6 个 AI 智能体协作
- **状态追踪** - 实时任务状态更新

### 📦 安装包内容

```
claudeeditor_autostart_package/
├── package.json                    # npm 包配置
├── install.sh                      # curl 安装脚本
├── scripts/
│   ├── install.js                  # 智能安装器
│   ├── postinstall.js             # 安装后配置
│   ├── start.js                   # 启动脚本
│   └── build.js                   # 构建脚本
├── bin/
│   ├── powerautomation            # 主命令
│   ├── claudeeditor               # 编辑器命令
│   └── claude                     # Claude 包装器
├── templates/                      # 平台模板
├── PowerAutomationService.js       # 前端服务
├── start_powerautomation_ecosystem.py  # 生态系统启动器
├── demo_autostart_flow.py         # 演示脚本
└── README.md                      # 说明文档
```

### 🚀 快速开始

#### 1. 安装
```bash
# 选择一种方式安装
curl -fsSL https://install.powerautomation.ai | bash
# 或
npm install -g @powerautomation/claudeeditor
```

#### 2. 创建项目
```bash
# npm 方式
npx create-powerautomation-app my-project

# 或直接使用
powerautomation init my-project
```

#### 3. 启动
```bash
cd my-project
npm start
# 或
./powerautomation
```

#### 4. 访问
- **桌面版**: 自动启动应用
- **移动版**: 安装到设备
- **Web 版**: http://localhost:3000

### 💡 使用示例

#### 基本命令
```bash
# 启动完整生态系统
./claude "分析这个代码文件"

# 查看帮助
./claude --help

# 切换模型
./claude "/switch-model claude"

# 查看使用统计
./claude "/usage"
```

#### 在 ClaudeEditor 中
```
/help                    # 查看所有指令
/status                  # 查看系统状态
/chat 你好               # 与 K2 对话
/analyze main.py         # 分析代码文件
/review --fix           # 代码审查并修复
/switch-model claude    # 切换到 Claude Code
/usage                  # 查看使用统计
```

### 🔧 配置选项

#### 环境变量
```bash
export POWERAUTOMATION_HOME=/path/to/powerautomation
export POWERAUTOMATION_MODEL=k2_local
export POWERAUTOMATION_API_KEY=your_api_key
export POWERAUTOMATION_DEBUG=true
```

#### 配置文件 (powerautomation.config.json)
```json
{
  "version": "4.6.9.5",
  "models": {
    "default": "k2_local",
    "k2_local": {
      "enabled": true,
      "path": "./models/k2"
    },
    "k2_cloud": {
      "enabled": true,
      "apiKey": "your_api_key"
    },
    "claude_code": {
      "enabled": true,
      "apiKey": "your_claude_key"
    }
  },
  "features": {
    "mirrorCode": true,
    "commandMCP": true,
    "taskSync": true,
    "multiAgent": true
  }
}
```

### 🛠️ 开发者选项

#### 开发模式
```bash
npm run dev              # 开发模式
npm run dev:desktop      # 桌面开发模式
npm run dev:mobile       # 移动开发模式
```

#### 构建选项
```bash
npm run build            # 构建所有平台
npm run build:desktop    # 构建桌面版
npm run build:mobile     # 构建移动版
npm run build:web        # 构建 Web 版
```

#### 测试
```bash
npm test                 # 运行测试
npm run test:unit        # 单元测试
npm run test:e2e         # 端到端测试
```

### 📚 文档和支持

- **官方文档**: https://powerautomation.ai/docs
- **API 文档**: https://powerautomation.ai/api
- **GitHub**: https://github.com/alexchuang650730/aicore0711
- **问题反馈**: https://github.com/alexchuang650730/aicore0711/issues
- **社区讨论**: https://powerautomation.ai/community

### 🔄 更新和维护

#### 自动更新
```bash
powerautomation update   # 检查并安装更新
```

#### 手动更新
```bash
npm update -g @powerautomation/claudeeditor
# 或
curl -fsSL https://install.powerautomation.ai | bash
```

### 🎉 特色亮点

- 🤖 **默认 K2 本地模型** - 免费、快速、隐私
- 🪞 **智能 Mirror Code** - 自动路由到最优模型
- 📱 **真正跨平台** - 桌面、移动、Web 一套代码
- 🔄 **实时协作** - 多智能体任务协作
- 💰 **成本优化** - 最大化使用免费资源
- 🛡️ **隐私保护** - 本地处理，数据不外泄
- ⚡ **高性能** - 毫秒级响应时间
- 🎯 **用户友好** - 一键安装，开箱即用

---

**PowerAutomation ClaudeEditor v4.6.9.5** - 让 AI 编程更简单、更智能、更经济！

