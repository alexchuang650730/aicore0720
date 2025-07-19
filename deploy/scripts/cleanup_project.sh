#!/bin/bash

# PowerAutomation 項目清理腳本
# 目標結構: core/, deploy/, showcases/, README.md

echo "開始清理 PowerAutomation 項目..."

# 1. 刪除根目錄下的所有 Python 文件
echo "刪除根目錄 Python 文件..."
rm -f *.py

# 2. 刪除根目錄下的 HTML 文件
echo "刪除根目錄 HTML 文件..."
rm -f *.html

# 3. 刪除根目錄下的配置文件
echo "刪除根目錄配置文件..."
rm -f *.json *.yaml *.yml

# 4. 刪除根目錄下的數據庫文件
echo "刪除根目錄數據庫文件..."
rm -f *.db

# 5. 刪除根目錄下的腳本文件（除了本腳本）
echo "刪除根目錄腳本文件..."
rm -f demo_all_features.sh deploy.sh launch.sh quick_start.sh one-click-deploy.sh start_complete_system.sh backup_script.sh restore_script.sh

# 6. 刪除根目錄下的文檔文件（保留 README.md）
echo "刪除根目錄文檔文件..."
rm -f BIDIRECTIONAL_COMMUNICATION_ARCHITECTURE.md CHANGELOG.md CLEANUP_PLAN.md COMPLETE_FEATURES_SUMMARY.md
rm -f CONTRIBUTING.md LAUNCH_GUIDE.md LICENSE MCP_ARCHITECTURE.md PRECISION_DEVELOPMENT_WORKFLOW.md
rm -f RELEASE_NOTES_v4.7.2.md auto_generated_spec.md external_tools_deployment_guide.md external_tools_integration_spec.md
rm -f hf_k2_provider_analysis.md integration_test_checklist.md mcp_server_plan.md rag_k2_support_analysis.md rag_optimization_plan.md
rm -f claudeditor_powerautomation_integration.md

# 7. 刪除其他文件
echo "刪除其他文件..."
rm -f Dockerfile docker-compose.yml docker-compose.production.yml
rm -f requirements.txt setup.py powerautomation
rm -f *.txt *.log

# 8. 刪除不需要的目錄
echo "刪除不需要的目錄..."
rm -rf claudeditor claudeditor_complete desktop mobile web
rm -rf data downloads logs temp uploads venv
rm -rf member_system goal_alignment_system mcp_server
rm -rf backup_20250719 mcp_backup_20250718_224735
rm -rf deployment  # 舊的 deployment 目錄

# 9. 創建 showcases 目錄（如果不存在）
echo "創建 showcases 目錄..."
mkdir -p showcases

# 10. 整理 deploy 目錄 - 創建版本化結構
echo "整理 deploy 目錄..."
mkdir -p deploy/v4.7.3/docs
mkdir -p deploy/v4.7.3/tests

# 11. 移動相關文件到新位置
if [ -d "deploy/docs" ]; then
    mv deploy/docs/* deploy/v4.7.3/docs/ 2>/dev/null || true
    rmdir deploy/docs 2>/dev/null || true
fi

if [ -d "deploy/tests" ]; then
    mv deploy/tests/* deploy/v4.7.3/tests/ 2>/dev/null || true
    rmdir deploy/tests 2>/dev/null || true
fi

# 12. 移動 showcases 內容
if [ -d "deploy/showcases" ]; then
    mv deploy/showcases/* showcases/ 2>/dev/null || true
    rmdir deploy/showcases 2>/dev/null || true
fi

# 13. 替換 README.md
if [ -f "README_NEW.md" ]; then
    mv README_NEW.md README.md
fi

# 14. 清理 core/components 中的測試相關目錄
echo "清理 core 目錄..."
rm -rf core/components/test_mcp
rm -rf core/testing

echo "清理完成！"
echo ""
echo "當前目錄結構："
echo "aicore0718/"
echo "├── core/          # 核心系統"
echo "├── deploy/        # 部署文件"
echo "│   └── v4.7.3/   # 最新版本"
echo "│       ├── docs/ # 版本文檔"
echo "│       └── tests/# 版本測試"
echo "├── showcases/     # 展示案例"
echo "└── README.md      # 項目說明"