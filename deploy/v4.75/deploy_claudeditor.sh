#!/bin/bash
# ClaudeEditor 部署脚本

echo "🎨 部署 ClaudeEditor..."

EDITOR_ROOT="/Users/alexchuang/alexchuangtest/aicore0720/claudeditor"
DEPLOY_MODE="${1:-web}"  # web 或 desktop

# 构建前端资源
echo "🏗️ 构建前端资源..."
cd "$EDITOR_ROOT"
npm install
npm run build:$DEPLOY_MODE

if [ "$DEPLOY_MODE" = "web" ]; then
    # Web 版本部署
    echo "🌐 部署 Web 版本..."
    
    # 复制构建文件
    cp -r dist/* /var/www/claudeditor/
    
    # 配置 nginx
    cat > /etc/nginx/sites-available/claudeditor << EOF
server {
    listen 80;
    server_name claudeditor.local;
    root /var/www/claudeditor;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
    
    location /ws {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}
EOF
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/claudeditor /etc/nginx/sites-enabled/
    nginx -s reload
    
    echo "✅ Web 版本部署完成"
    echo "📊 访问地址: http://claudeditor.local"
    
elif [ "$DEPLOY_MODE" = "desktop" ]; then
    # Desktop 版本部署
    echo "🖥️ 部署 Desktop 版本..."
    
    # 打包 Electron 应用
    npm run package:mac
    
    # 复制到应用目录
    cp -r dist/mac/ClaudeEditor.app /Applications/
    
    echo "✅ Desktop 版本部署完成"
    echo "📊 应用位置: /Applications/ClaudeEditor.app"
fi

# 配置 K2 集成
echo "🔌 配置 K2 集成..."
cat > "$EDITOR_ROOT/config/k2.json" << EOF
{
    "enabled": true,
    "auto_switch": true,
    "threshold": {
        "token_count": 1000,
        "cost_limit": 0.1
    },
    "endpoints": {
        "k2": "http://localhost:3002/v1/complete",
        "claude": "https://api.anthropic.com/v1/complete"
    }
}
EOF

echo "✅ ClaudeEditor 部署完成"
