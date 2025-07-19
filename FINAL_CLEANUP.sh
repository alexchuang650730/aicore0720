#!/bin/bash

echo "🧹 開始徹底清理 aicore0720 項目..."

# 1. 清理根目錄的垃圾文件
echo "📁 清理根目錄..."
rm -f auto_scroll_extract.js
rm -f auto_generated_spec.md

# 將 Manus 測試輸出移到 data 目錄
mv manus_test_output data/ 2>/dev/null

# 2. 清理 deployment 目錄（應該已經合併到 deploy）
if [ -d "deployment" ]; then
    echo "🔄 合併 deployment 到 deploy..."
    cp -r deployment/* deploy/ 2>/dev/null
    rm -rf deployment
fi

# 3. 清理核心目錄中的冗餘文件
echo "🗑️ 清理 core 目錄冗餘..."

# 移除冗餘的整合文件
rm -f core/components/evaluate_external_tools_integration.py
rm -f core/components/external_tools_mcp_integration.py
rm -f core/components/implement_external_tools_integration.py
rm -f core/components/powerautomation_external_tools_integration.py
rm -f core/components/powerautomation_integration_demo.py
rm -f core/components/unified_tool_integration_example.py
rm -f core/components/k2_final_integration.py

# 移除高級工具智能系統（已經有更好的實現）
rm -f core/components/advanced_tool_intelligence_system.py

# 4. 整理數據收集文件
echo "📊 整理數據收集文件..."
# 所有 simple_manus_*.py 應該在 data_collection 目錄
rm -f simple_manus_*.py 2>/dev/null

# 5. 整理部署腳本
echo "📜 整理部署腳本..."
# 移除根目錄的部署腳本
rm -f deploy.sh
rm -f one-click-deploy.sh

# 6. 清理測試相關文件
echo "🧪 整理測試文件..."
rm -f test_analyzer.py
rm -f test_manus_collection.py
rm -f external_tools_integration_test_cases.py

# 7. 清理集成規格文件
echo "📋 清理重複的規格文件..."
rm -f external_tools_integration_spec.md
rm -f external_tools_deployment_guide.md
rm -f integration_test_checklist.md
rm -f hf_k2_provider_analysis.md
rm -f rag_k2_support_analysis.md
rm -f rag_optimization_plan.md

# 8. 整理工具目錄
echo "🔧 整理工具目錄..."
# 移除已經整合的工具
rm -f tools/integrate_optimizations_to_mcp.py
rm -f tools/integrate_xmasters_k2_enhancement.py
rm -f tools/strengthen_mcp_architecture.py
rm -f tools/fix_mcp_architecture.py
rm -f tools/codeflow_spec_generator.py  # 保留 enhanced 版本

# 9. 清理 __pycache__
echo "🗑️ 清理緩存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name ".DS_Store" -delete

# 10. 創建清晰的項目結構
echo "📂 創建清晰的項目結構..."

# 確保主要目錄存在
mkdir -p core/components
mkdir -p core/data_collection
mkdir -p core/training  
mkdir -p core/testing
mkdir -p deploy/scripts
mkdir -p deploy/docker
mkdir -p docs
mkdir -p tools
mkdir -p data

# 11. 生成新的項目結構文檔
cat > PROJECT_STRUCTURE.md << 'EOF'
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
EOF

echo "✅ 清理完成！"
echo ""
echo "📊 清理統計："
echo "- 移除冗餘整合文件"
echo "- 合併 deployment 到 deploy"
echo "- 整理數據收集文件"
echo "- 清理測試文件"
echo "- 移除重複規格文檔"
echo "- 清理緩存文件"
echo ""
echo "📁 當前項目結構已保存到 PROJECT_STRUCTURE.md"