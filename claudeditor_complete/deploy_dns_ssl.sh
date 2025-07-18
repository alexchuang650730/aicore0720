#!/bin/bash
# PowerAutomation DNS和SSL部署腳本
# 域名: powerautomation.com

set -e

echo "🚀 開始PowerAutomation DNS和SSL配置"
echo "域名: powerautomation.com"
echo "時間: $(date)"

# 檢查必要的環境變量
if [ -z "$DOMAIN" ]; then
    export DOMAIN="powerautomation.com"
fi

if [ -z "$EC2_IP" ]; then
    echo "❌ 請設置EC2_IP環境變量"
    echo "export EC2_IP=your_ec2_public_ip"
    exit 1
fi

echo "✅ 域名: $DOMAIN"
echo "✅ EC2 IP: $EC2_IP"

# 1. 安裝必要軟件
echo "📦 安裝必要軟件..."
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 2. 配置Nginx
echo "🔧 配置Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/powerautomation
sudo ln -sf /etc/nginx/sites-available/powerautomation /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 3. 測試Nginx配置
echo "🧪 測試Nginx配置..."
sudo nginx -t

# 4. 啟動Nginx
echo "🚀 啟動Nginx..."
sudo systemctl enable nginx
sudo systemctl restart nginx

# 5. 申請SSL證書
echo "🔒 申請SSL證書..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN -d api.$DOMAIN -d admin.$DOMAIN -d dev.$DOMAIN -d beta.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# 6. 設置SSL自動續期
echo "⏰ 設置SSL自動續期..."
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

# 7. 配置防火牆
echo "🛡️ 配置防火牆..."
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

# 8. 測試部署
echo "🧪 測試部署..."
curl -I https://$DOMAIN
curl -I https://api.$DOMAIN
curl -I https://admin.$DOMAIN
curl -I https://dev.$DOMAIN
curl -I https://beta.$DOMAIN

echo "✅ DNS和SSL配置完成!"
echo "🌐 主網站: https://$DOMAIN"
echo "🔌 API端點: https://api.$DOMAIN"
echo "⚙️ 管理後台: https://admin.$DOMAIN"
echo "👨‍💻 開發者平台: https://dev.$DOMAIN"
echo "🧪 Beta測試: https://beta.$DOMAIN"

echo "📋 下一步:"
echo "1. 確認所有域名可以正常訪問"
echo "2. 部署PowerAutomation應用"
echo "3. 配置數據庫和環境變量"
echo "4. 開始100用戶測試"