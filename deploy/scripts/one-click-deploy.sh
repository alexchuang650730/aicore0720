#!/bin/bash

# PowerAutomation 一鍵部署腳本
# curl -sSL https://powerauto.ai/deploy.sh | bash

set -e

echo "🚀 PowerAutomation 一鍵部署開始..."
echo "=========================================="
echo "🎯 目標: 部署 PowerAutomation 到 powerauto.ai"
echo "📅 版本: 7/30 正式版"
echo ""

# 檢查系統
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ 檢測到 macOS 系統"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ 檢測到 Linux 系統"
else
    echo "❌ 不支持的操作系統: $OSTYPE"
    exit 1
fi

# 檢查必要工具
REQUIRED_TOOLS=("git" "docker" "curl")
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v $tool &> /dev/null; then
        echo "❌ 缺少必要工具: $tool"
        echo "請安裝後重試"
        exit 1
    fi
done

echo "✅ 系統檢查通過"

# 設置變數
REPO_URL="https://github.com/alexchuang650730/aicore0718.git"
DEPLOY_DIR="powerautomation-deploy"
EC2_HOST="ec2-13-222-125-83.compute-1.amazonaws.com"
DOMAIN="powerauto.ai"

# 清理舊部署
if [[ -d "$DEPLOY_DIR" ]]; then
    echo "🧹 清理舊部署..."
    rm -rf "$DEPLOY_DIR"
fi

# 克隆代碼
echo "📥 下載 PowerAutomation 代碼..."
git clone "$REPO_URL" "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

# 檢查部署密鑰（用戶需要提供）
if [[ ! -f "alexchuang.pem" ]]; then
    echo "❌ 缺少部署密鑰文件: alexchuang.pem"
    echo "請聯繫 Alex Chuang 獲取部署密鑰"
    echo "📧 Email: alex@powerauto.ai"
    exit 1
fi

# 檢查生產環境配置
if [[ ! -f ".env.production" ]]; then
    echo "❌ 缺少生產環境配置: .env.production"
    echo "正在創建模板配置文件..."
    
    cat > .env.production << 'ENV_EOF'
# PowerAutomation 生產環境配置
NODE_ENV=production
JWT_SECRET_KEY=powerautomation-secret-key-2025

# API 密鑰（請填入實際密鑰）
CLAUDE_API_KEY=your_claude_api_key_here
KIMI_API_KEY=your_kimi_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# 服務端口
CORE_PORT=8080
CLAUDEDITOR_PORT=3000
WEBSOCKET_PORT=8081
MEMBERSHIP_API_PORT=8082

# 數據庫配置
DATABASE_URL=sqlite:///data/powerautomation.db

# 系統配置
DEBUG=false
LOG_LEVEL=INFO
ENV_EOF
    
    echo "⚠️  請編輯 .env.production 文件，填入正確的 API 密鑰"
    echo "完成後重新運行部署腳本"
    exit 1
fi

# 給部署腳本執行權限
chmod +x deploy.sh

# 確認部署
echo ""
echo "🎯 部署信息確認："
echo "===================="
echo "域名: $DOMAIN"
echo "服務器: $EC2_HOST"
echo "部署目錄: $(pwd)"
echo ""

read -p "確認開始部署？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

# 執行部署
echo "🚀 開始執行部署..."
./deploy.sh

# 部署完成
echo ""
echo "🎉 一鍵部署完成！"
echo "===================="
echo "🌐 網站地址: https://$DOMAIN"
echo "🔧 管理面板: https://$DOMAIN/admin"
echo "📊 API 文檔: https://$DOMAIN/api/docs"
echo ""

# 進行基本健康檢查
echo "🔍 執行最終健康檢查..."

# 檢查網站是否可訪問
for i in {1..5}; do
    echo "📡 嘗試連接 $DOMAIN (第 $i 次)..."
    if curl -f -s "https://$DOMAIN" > /dev/null; then
        echo "✅ 網站訪問正常"
        break
    elif [[ $i -eq 5 ]]; then
        echo "⚠️  網站可能需要更多時間啟動，請稍後檢查"
    else
        sleep 10
    fi
done

# 清理部署文件
cd ..
rm -rf "$DEPLOY_DIR"

echo ""
echo "🎯 PowerAutomation 7/30 正式版部署完成！"
echo "🚀 開始您的 AI 開發之旅！"
echo ""
echo "📞 技術支持："
echo "  GitHub: https://github.com/alexchuang650730/aicore0718"
echo "  Email: alex@powerauto.ai"
echo ""
echo "💡 使用提示："
echo "  1. 訪問 https://$DOMAIN 註冊帳戶"
echo "  2. 安裝 Claude Code Tool 並使用 K2 模型"
echo "  3. 享受 60-80% 成本節省的開發體驗！"