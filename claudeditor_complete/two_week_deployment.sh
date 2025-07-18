#!/bin/bash
# PowerAutomation 兩週部署腳本
# 目標：快速部署100用戶測試環境

set -e

echo "🚀 PowerAutomation 兩週部署開始"
echo "時間: $(date)"
echo "目標: 100用戶實戰測試環境"

# 環境檢查
echo "📋 檢查環境依賴..."
command -v docker >/dev/null 2>&1 || { echo "需要安裝Docker"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "需要安裝Python3"; exit 1; }

# 配置環境變量
export POWERAUTOMATION_ENV=production
export CLAUDE_API_KEY=${CLAUDE_API_KEY}
export MOONSHOT_API_KEY=${MOONSHOT_API_KEY}
export GROQ_API_KEY=${GROQ_API_KEY}
export AWS_REGION=${AWS_REGION:-us-west-2}

# 部署核心服務
echo "🔧 部署核心服務..."
docker-compose -f docker-compose.production.yml up -d

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 30

# 初始化數據庫
echo "🗄️ 初始化數據庫..."
python3 scripts/init_database.py

# 設置K2集成
echo "🤖 配置K2集成..."
python3 scripts/setup_k2_integration.py

# 部署數據收集系統
echo "📊 部署數據收集系統..."
python3 scripts/deploy_analytics.py

# 設置監控
echo "📈 設置監控系統..."
python3 scripts/setup_monitoring.py

# 健康檢查
echo "🏥 執行健康檢查..."
python3 scripts/health_check.py

# 創建邀請系統
echo "💌 創建用戶邀請系統..."
python3 scripts/setup_invitations.py

echo "✅ 部署完成!"
echo "🌐 訪問地址: https://powerautomation.your-domain.com"
echo "📊 監控面板: https://monitoring.your-domain.com"
echo "👥 用戶管理: https://admin.your-domain.com"

echo "📋 接下來步驟:"
echo "1. 驗證所有功能正常"
echo "2. 邀請前10名核心用戶"
echo "3. 開始數據收集"
echo "4. 監控系統健康"
