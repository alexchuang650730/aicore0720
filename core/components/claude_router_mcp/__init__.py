"""
PowerAutomation Unified MCP - 统一的 PowerAutomation MCP 组件
PowerAutomation v4.6.9.7 - 完整解决方案

🚀 PowerAutomation Unified MCP 功能:
├── claude_sync/                # Claude Code 同步服务
│   ├── sync_manager.py         # 同步管理器
│   ├── code_tracker.py         # 代码追踪
│   └── communication.py        # 通信管理
├── k2_router/                  # K2 服务路由
│   ├── k2_client.py           # K2 客户端
│   ├── request_router.py      # 请求路由器
│   └── response_handler.py    # 响应处理器
├── tool_mode/                  # Claude 工具模式
│   ├── tool_manager.py        # 工具管理器
│   ├── request_interceptor.py # 请求拦截器
│   └── config_manager.py      # 配置管理器
├── startup_trigger/            # 启动触发管理
│   ├── trigger_detector.py    # 触发检测器
│   ├── action_executor.py     # 动作执行器
│   └── hook_integration.py    # 钩子集成
├── mirror_tracker/             # Mirror Code 追踪
│   ├── usage_tracker.py       # 使用追踪器
│   ├── cost_analyzer.py       # 成本分析器
│   └── performance_monitor.py # 性能监控器
├── utils/                      # 工具模块
│   ├── logger.py              # 日志工具
│   ├── config.py              # 配置工具
│   └── helpers.py             # 辅助函数
└── unified_mcp_server.py       # 统一 MCP 服务器

🎯 核心功能:
- ✅ Claude Code 同步服务 - 与 ClaudeEditor 无缝同步
- ✅ Claude 工具模式 - 完全避免模型推理余额消耗
- ✅ K2 服务路由 - 自动路由 AI 推理任务到 K2
- ✅ 启动触发管理 - 智能检测和自动安装
- ✅ Mirror Code 追踪 - 实时监控使用情况和成本
- ✅ 统一配置管理 - 一键配置所有功能

🚀 安装使用:
```bash
# npm 安装
npm install -g powerautomation-unified

# curl 安装
curl -fsSL https://install.powerautomation.ai | bash

# 启动服务
powerautomation start

# 配置 K2 路由
powerautomation config k2 --enable
```

📋 主要特性:
1. **零余额消耗**: 完全避免 Claude 模型推理费用
2. **无缝同步**: ClaudeEditor 和本地环境实时同步
3. **智能路由**: AI 推理任务自动路由到 K2 服务
4. **一键安装**: npm/curl 一键安装，开箱即用
5. **统一管理**: 所有功能统一配置和监控
"""

from .claude_sync.sync_manager import ClaudeSyncManager
from .k2_router.k2_client import K2Client
from .tool_mode.tool_manager import ToolModeManager
from .startup_trigger.trigger_detector import TriggerDetector
from .mirror_tracker.usage_tracker import UsageTracker
from .unified_mcp_server import PowerAutomationUnifiedMCPServer

__version__ = "4.6.9.7"
__all__ = [
    "ClaudeSyncManager",
    "K2Client", 
    "ToolModeManager",
    "TriggerDetector",
    "UsageTracker",
    "PowerAutomationUnifiedMCPServer"
]

