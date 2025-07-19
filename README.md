# PowerAutomation v4.6.8 - AI 驅動的全棧開發平台

<div align="center">
  <img src="docs/images/logo.png" alt="PowerAutomation Logo" width="200"/>
  
  [![Version](https://img.shields.io/badge/version-4.6.8-blue.svg)](https://github.com/alexchuang650730/aicore0720)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
  [![Status](https://img.shields.io/badge/status-active-success.svg)]()
</div>

## 🚀 概述

PowerAutomation 是一個革命性的 AI 驅動全棧開發平台，通過六大核心工作流和智能 MCP 組件，實現 99% 的開發任務自動化。

## 📁 項目結構

```
aicore0720/
├── core/                    # 核心功能模塊
│   ├── components/         # MCP 組件
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
│   └── v4.73/          # 版本部署（含 mcp_server）
│
├── docs/                  # 文檔
├── data/                 # 數據文件
└── README.md            # 本文件
```

## 🎯 核心特性

### 六大工作流
1. **代碼生成工作流** - 智能代碼生成和優化
2. **UI 設計工作流** - 智能 UI 生成和響應式設計
3. **API 開發工作流** - RESTful API 自動生成
4. **測試自動化工作流** - 全面的測試覆蓋
5. **數據庫設計工作流** - 智能數據模型設計
6. **部署流水線工作流** - 一鍵部署和監控

### 核心 MCP 組件
- **CodeFlow MCP** - 代碼生成引擎
- **SmartUI MCP** - UI 智能生成
- **Test MCP** - 測試管理
- **AG-UI MCP** - UI 自動化
- **Stagewise MCP** - 端到端測試
- **Zen MCP** - 工作流編排
- **X-Masters MCP** - 深度推理
- **MemoryOS MCP** - 智能記憶系統

### 新增功能
- **Enhanced CodeFlow MCP** - 整合所有功能的增強版（在 codeflow_mcp 中）
- **K2 優化器訓練系統** - 支持 K2 模型訓練（在 core/training 中）
- **代碼清理工具** - 智能識別和清理冗餘代碼（在 codeflow_mcp 中）
- **MCP 合併分析器** - 分析和優化 MCP 組件（在 mcp_coordinator_mcp 中）

## 🛠️ 快速開始

### 環境要求
- Python 3.8+
- Node.js 16+
- Git

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/alexchuang650730/aicore0720.git
cd aicore0720

# 安裝依賴
pip install -r requirements.txt
npm install

# 配置環境
cp .env.example .env
# 編輯 .env 文件，添加必要的配置
```

### 運行

```bash
# 啟動核心服務
python core/api/main_api_server.py

# 啟動 ClaudeEditor
cd deploy/claudeditor
npm run dev

# 運行測試
python -m pytest core/testing/
```

## 📊 數據和訓練

項目包含豐富的訓練數據：
- Claude 對話數據
- 103 個 Manus 任務示例
- K2 模型訓練數據集

使用 K2 優化器：
```python
from core.training.k2_optimizer_trainer import K2OptimizerTrainer

trainer = K2OptimizerTrainer()
trainer.train_with_existing_data()
```

## 🔧 功能使用

### 代碼清理
```bash
python core/components/codeflow_mcp/cleanup_redundant_code.py
```

### MCP 分析
```bash
python core/components/mcp_coordinator_mcp/mcp_consolidation_analyzer.py
```

## 📖 文檔

詳細文檔請查看 `docs/` 目錄：
- [項目架構](docs/architecture/MCP_ARCHITECTURE.md)
- [部署指南](docs/guides/LAUNCH_GUIDE.md)
- [API 文檔](docs/api/)

## 🤝 貢獻

歡迎貢獻！請查看 [貢獻指南](CONTRIBUTING.md)。

## 📄 許可證

本項目採用 MIT 許可證 - 詳見 [LICENSE](LICENSE) 文件。

## 📞 聯繫

- 作者：Alex Chuang
- Email：chuang.hsiaoyen@gmail.com
- GitHub：[@alexchuang650730](https://github.com/alexchuang650730)

---

⭐ 如果這個項目對你有幫助，請給個星標！