#!/bin/bash

# PowerAuto.ai 支付系統 EC2 部署腳本
# 版本: v4.76

set -e

# 配置
EC2_HOST="ec2-13-222-125-83.compute-1.amazonaws.com"
EC2_USER="ec2-user"
KEY_PATH="/Users/alexchuang/alexchuang.pem"
REMOTE_DIR="/home/ec2-user/powerauto-ai-payment"
LOCAL_DIR="/Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.76/website/backend"

echo "🚀 開始部署 PowerAuto.ai 支付系統到 EC2..."
echo "目標服務器: $EC2_HOST"
echo "本地目錄: $LOCAL_DIR"
echo "遠程目錄: $REMOTE_DIR"
echo ""

# 創建遠程目錄
echo "📁 創建遠程目錄..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "mkdir -p $REMOTE_DIR"
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "mkdir -p $REMOTE_DIR/templates"

# 傳輸核心文件
echo "📦 傳輸核心文件..."
scp -i "$KEY_PATH" "$LOCAL_DIR/app.py" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"
scp -i "$KEY_PATH" "$LOCAL_DIR/payment_system.py" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"
scp -i "$KEY_PATH" "$LOCAL_DIR/start_server.py" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

# 傳輸測試文件
echo "🧪 傳輸測試文件..."
scp -i "$KEY_PATH" "$LOCAL_DIR/simple_test.py" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"
scp -i "$KEY_PATH" "$LOCAL_DIR/test_payment_system.py" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

# 傳輸模板文件
echo "📄 傳輸模板文件..."
scp -i "$KEY_PATH" "$LOCAL_DIR/templates/product_pages.html" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/templates/"
scp -i "$KEY_PATH" "$LOCAL_DIR/templates/checkout_pages.html" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/templates/"
scp -i "$KEY_PATH" "$LOCAL_DIR/templates/success.html" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/templates/"

# 傳輸配置文件
echo "⚙️ 傳輸配置文件..."
scp -i "$KEY_PATH" "$LOCAL_DIR/requirements.txt" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/" 2>/dev/null || echo "requirements.txt 不存在，跳過"
scp -i "$KEY_PATH" "$LOCAL_DIR/README_PAYMENT_SYSTEM.md" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

# 創建 requirements.txt（如果不存在）
echo "📝 創建依賴文件..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "cat > $REMOTE_DIR/requirements.txt << 'EOF'
flask==2.3.3
flask-sqlalchemy==3.0.5
flask-bcrypt==1.0.1
flask-cors==4.0.0
stripe==5.5.0
PyJWT==2.8.0
requests==2.31.0
EOF"

# 創建啟動腳本
echo "🔧 創建 EC2 啟動腳本..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "cat > $REMOTE_DIR/start_production.sh << 'EOF'
#!/bin/bash

# PowerAuto.ai 生產環境啟動腳本

echo \"🚀 啟動 PowerAuto.ai 支付系統生產環境\"
echo \"============================================\"

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo \"❌ Python3 未安裝，正在安裝...\"
    sudo yum update -y
    sudo yum install -y python3 python3-pip
fi

# 檢查依賴
echo \"📦 安裝 Python 依賴...\"
pip3 install --user -r requirements.txt

# 設置環境變量
export FLASK_APP=app.py
export FLASK_ENV=production
export SECRET_KEY=\"powerauto-ai-production-secret-$(date +%s)\"
export DATABASE_URL=\"sqlite:///powerauto_production.db\"

# 測試核心功能
echo \"🧪 測試核心功能...\"
python3 simple_test.py

if [ \$? -eq 0 ]; then
    echo \"✅ 核心功能測試通過\"
    
    # 啟動服務器
    echo \"🌐 啟動生產服務器...\"
    echo \"訪問地址: http://$EC2_HOST:5001\"
    echo \"產品頁面: http://$EC2_HOST:5001/products\"
    echo \"\"
    python3 app.py
else
    echo \"❌ 核心功能測試失敗，請檢查日誌\"
    exit 1
fi
EOF"

# 設置執行權限
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "chmod +x $REMOTE_DIR/start_production.sh"

# 創建 systemd 服務文件
echo "🔧 創建 systemd 服務..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "sudo tee /etc/systemd/system/powerauto-payment.service > /dev/null << 'EOF'
[Unit]
Description=PowerAuto.ai Payment System
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$REMOTE_DIR
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production
Environment=SECRET_KEY=powerauto-ai-production-secret
Environment=DATABASE_URL=sqlite:///powerauto_production.db
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

# 檢查部署結果
echo "🔍 檢查部署結果..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "ls -la $REMOTE_DIR"
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "ls -la $REMOTE_DIR/templates"

echo ""
echo "✅ PowerAuto.ai 支付系統部署完成！"
echo ""
echo "📋 下一步操作："
echo "1. 連接到 EC2: ssh -i \"$KEY_PATH\" $EC2_USER@$EC2_HOST"
echo "2. 進入目錄: cd $REMOTE_DIR"
echo "3. 運行測試: python3 simple_test.py"
echo "4. 啟動服務: ./start_production.sh"
echo "5. 或使用系統服務: sudo systemctl start powerauto-payment"
echo ""
echo "🌐 訪問地址："
echo "- 產品頁面: http://$EC2_HOST:5001/products"
echo "- 結帳頁面: http://$EC2_HOST:5001/checkout"
echo "- API測試: http://$EC2_HOST:5001/api/plans"
echo ""
echo "🎉 部署成功！"