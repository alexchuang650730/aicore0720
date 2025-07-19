# PowerAutomation v4.6.8 項目結構

```
aicore0720/
├── core/                    # 核心功能模塊
│   ├── components/         # MCP 組件（保留所有現有的）
│   ├── data_collection/    # 數據收集工具
│   ├── training/          # K2 訓練相關
│   ├── testing/           # 測試框架
│   ├── api/              # API 服務
│   ├── business/         # 業務邏輯
│   ├── mcp_zero/        # MCP-Zero 引擎
│   └── memoryrag/       # Memory RAG 系統
│
├── deploy/                 # 部署相關
│   ├── claudeditor/       # ClaudeEditor 部署
│   ├── mobile/           # 移動端部署
│   ├── web/             # Web 部署
│   ├── docker/          # Docker 配置
│   ├── scripts/         # 部署腳本
│   ├── v4.71/          # 版本部署
│   └── v4.73/          # 版本部署（含 mcp_server）
│
├── docs/                  # 文檔
│   ├── *.md             # 各種文檔
│   └── manus_tasks_manual.txt  # Manus 任務列表
│
├── tools/                # 工具腳本
│   ├── enhanced_codeflow_mcp.py    # 增強版 CodeFlow
│   ├── k2_optimizer_trainer.py     # K2 訓練器
│   ├── k2_pricing_system.py        # K2 定價
│   ├── cleanup_redundant_code.py   # 代碼清理
│   └── mcp_consolidation_analyzer.py # MCP 分析
│
├── data/                 # 數據文件
│   ├── *.db            # 數據庫文件
│   ├── claude_conversations/  # Claude 對話數據
│   ├── manus_*/        # Manus 數據
│   └── k2_training_data/     # K2 訓練數據
│
└── README.md            # 項目說明
```

## 核心 MCP 組件
- codeflow_mcp - 代碼生成
- smartui_mcp - UI 生成
- test_mcp - 測試管理
- ag_ui_mcp - UI 自動化
- stagewise_mcp - 端到端測試
- zen_mcp - 工作流編排
- xmasters_mcp - 深度推理
- memoryos_mcp - 記憶系統
- claude_router_mcp - 路由管理
- command_mcp - 命令執行

## 新增工具
- enhanced_codeflow_mcp - 整合所有功能的增強版
- k2_optimizer_trainer - K2 模型訓練
- k2_pricing_system - K2 定價系統
- cleanup_redundant_code - 代碼清理工具
- mcp_consolidation_analyzer - MCP 重複分析
