#!/bin/bash
# SSH密鑰設置腳本

echo "🔐 AWS EC2 SSH密鑰設置"
echo "=" * 50

# 檢查常見的密鑰位置
COMMON_LOCATIONS=(
    "$HOME/.ssh/alexchuang.pem"
    "$HOME/Downloads/alexchuang.pem"
    "$HOME/Desktop/alexchuang.pem"
    "./alexchuang.pem"
    "../alexchuang.pem"
)

echo "🔍 搜索SSH密鑰文件..."

KEY_FOUND=false
for location in "${COMMON_LOCATIONS[@]}"; do
    if [ -f "$location" ]; then
        echo "✅ 找到密鑰文件: $location"
        
        # 複製到當前目錄
        cp "$location" ./alexchuang.pem
        chmod 600 ./alexchuang.pem
        
        echo "✅ 密鑰已複製到部署目錄並設置正確權限"
        KEY_FOUND=true
        break
    fi
done

if [ "$KEY_FOUND" = false ]; then
    echo "❌ 未找到SSH密鑰文件 alexchuang.pem"
    echo ""
    echo "📝 請執行以下操作之一："
    echo ""
    echo "方案1: 如果你有密鑰文件，請複製到當前目錄"
    echo "  cp /path/to/alexchuang.pem ./alexchuang.pem"
    echo "  chmod 600 ./alexchuang.pem"
    echo ""
    echo "方案2: 從AWS Console下載密鑰"
    echo "  1. 登錄AWS Console"
    echo "  2. 進入EC2 > Key Pairs"
    echo "  3. 找到alexchuang密鑰並下載"
    echo ""
    echo "方案3: 創建新的密鑰對"
    echo "  1. 在AWS Console創建新密鑰對"
    echo "  2. 更新EC2實例的密鑰對"
    echo "  3. 更新部署腳本中的SSH_KEY變量"
    echo ""
    echo "方案4: 使用密碼認證 (不推薦)"
    echo "  修改部署腳本，使用ssh密碼認證"
    echo ""
    exit 1
fi

# 測試SSH連接
echo "🔗 測試SSH連接..."
EC2_HOST="ec2-44-206-225-192.compute-1.amazonaws.com"
EC2_USER="ubuntu"

if ssh -i alexchuang.pem -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "echo 'SSH connection successful'"; then
    echo "✅ SSH連接測試成功！"
    echo "🚀 現在可以運行部署腳本了:"
    echo "   ./deploy_to_aws.sh"
else
    echo "❌ SSH連接測試失敗"
    echo "📝 請檢查:"
    echo "  1. EC2實例是否運行中"
    echo "  2. 安全組是否允許SSH(22)端口"
    echo "  3. 密鑰文件是否正確"
    echo "  4. EC2實例IP是否正確"
fi