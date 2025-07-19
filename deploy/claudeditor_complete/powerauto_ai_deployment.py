#!/usr/bin/env python3
"""
PowerAuto.ai 自動化部署方案
基於真實域名 powerauto.ai 的完整部署配置
包含電腦控制自動化以避免重複認證
"""

import json
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Any

class PowerAutoAIDeployment:
    """PowerAuto.ai 自動化部署"""
    
    def __init__(self):
        self.domain = "powerauto.ai"
        self.subdomains = [
            "www.powerauto.ai",
            "api.powerauto.ai", 
            "admin.powerauto.ai",
            "dev.powerauto.ai",
            "beta.powerauto.ai",
            "app.powerauto.ai"
        ]
        
    def generate_real_dns_records(self, ec2_ip: str) -> List[Dict[str, str]]:
        """生成powerauto.ai的真實DNS記錄"""
        
        return [
            # 主域名
            {
                "Type": "A",
                "Name": "@",
                "Value": ec2_ip,
                "TTL": "300",
                "Priority": "1",
                "Description": "主域名 powerauto.ai 指向 EC2"
            },
            {
                "Type": "CNAME",
                "Name": "www",
                "Value": "powerauto.ai",
                "TTL": "300",
                "Priority": "1", 
                "Description": "www 重定向到主域名"
            },
            # API服務
            {
                "Type": "A",
                "Name": "api",
                "Value": ec2_ip,
                "TTL": "300",
                "Priority": "1",
                "Description": "API服務端點"
            },
            # 管理後台
            {
                "Type": "A",
                "Name": "admin",
                "Value": ec2_ip,
                "TTL": "300",
                "Priority": "1",
                "Description": "管理後台界面"
            },
            # 開發者平台
            {
                "Type": "A",
                "Name": "dev",
                "Value": ec2_ip,
                "TTL": "300",
                "Priority": "1",
                "Description": "開發者平台"
            },
            # Beta測試
            {
                "Type": "A",
                "Name": "beta",
                "Value": ec2_ip,
                "TTL": "300",
                "Priority": "1",
                "Description": "Beta測試平台"
            },
            # 主應用
            {
                "Type": "A",
                "Name": "app",
                "Value": ec2_ip,
                "TTL": "300",
                "Priority": "1",
                "Description": "主應用界面"
            },
            # 郵件服務
            {
                "Type": "MX",
                "Name": "@",
                "Value": "10 mail.powerauto.ai",
                "TTL": "300",
                "Priority": "10",
                "Description": "郵件服務器"
            },
            # SPF記錄
            {
                "Type": "TXT",
                "Name": "@",
                "Value": "v=spf1 include:_spf.google.com ~all",
                "TTL": "300",
                "Priority": "1",
                "Description": "SPF反垃圾郵件記錄"
            },
            # DMARC記錄
            {
                "Type": "TXT",
                "Name": "_dmarc",
                "Value": "v=DMARC1; p=quarantine; rua=mailto:dmarc@powerauto.ai",
                "TTL": "300",
                "Priority": "1",
                "Description": "DMARC郵件安全策略"
            }
        ]
    
    def generate_local_automation_script(self) -> str:
        """生成本地電腦自動化腳本，避免重複認證"""
        
        return '''#!/usr/bin/env python3
"""
PowerAuto.ai 本地自動化腳本
通過控制本地電腦瀏覽器來收集Manus/Safari數據，避免重複認證
"""

import time
import json
import pyautogui
import webbrowser
from datetime import datetime
from typing import Dict, List, Any
import subprocess
import os

class LocalBrowserAutomation:
    """本地瀏覽器自動化"""
    
    def __init__(self):
        self.data_collection_results = []
        self.session_start = datetime.now()
        
        # 配置pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1
        
        # Manus和Safari的URL
        self.manus_urls = [
            "https://manus.im/app/xHbeFo8tzQV51VeTErhskc",
            "https://manus.im/app/0aHoMEVe7vZNMlfy2I9VCU"
        ]
        
    def open_manus_sessions(self):
        """打開Manus會話並提取數據"""
        print("🚀 開始Manus數據提取...")
        
        for i, url in enumerate(self.manus_urls):
            print(f"📂 打開Manus會話 {i+1}...")
            
            # 在現有瀏覽器中打開新標籤
            webbrowser.open_new_tab(url)
            time.sleep(3)  # 等待頁面載入
            
            # 等待用戶確認頁面已加載
            input(f"✅ 請確認Manus會話 {i+1} 已完全載入，然後按Enter繼續...")
            
            # 提取左側任務列表
            self.extract_manus_task_list(i+1)
            
            # 提取對話內容
            self.extract_manus_conversations(i+1)
            
        print("✅ Manus數據提取完成")
    
    def extract_manus_task_list(self, session_num: int):
        """提取Manus左側任務列表"""
        print(f"📋 提取會話 {session_num} 的任務列表...")
        
        # 模擬點擊左側列表項
        tasks_extracted = []
        
        # 這裡可以添加具體的點擊座標邏輯
        # 暫時使用手動方式
        print("👆 請手動點擊左側任務列表中的各個項目")
        print("🔍 我們將記錄每個任務的以下信息：")
        print("   - 任務描述")
        print("   - 代碼輸出")
        print("   - 滿意度評分 (1-10)")
        print("   - 執行時間")
        
        num_tasks = int(input("❓ 這個會話中有多少個任務？"))
        
        for task_id in range(1, num_tasks + 1):
            print(f"\\n📝 任務 {task_id}:")
            task_desc = input("   任務描述: ")
            satisfaction = int(input("   滿意度 (1-10): "))
            exec_time = float(input("   執行時間 (秒): "))
            
            task_data = {
                "session": session_num,
                "task_id": task_id,
                "description": task_desc,
                "satisfaction": satisfaction,
                "execution_time": exec_time,
                "timestamp": datetime.now().isoformat(),
                "source": "manus"
            }
            
            tasks_extracted.append(task_data)
            
            # 保存到數據收集結果
            self.data_collection_results.append(task_data)
        
        print(f"✅ 會話 {session_num} 共提取 {len(tasks_extracted)} 個任務")
    
    def extract_manus_conversations(self, session_num: int):
        """提取Manus對話內容"""
        print(f"💬 提取會話 {session_num} 的對話內容...")
        
        # 使用鍵盤快捷鍵複製內容
        print("📋 使用 Cmd+A 選擇所有內容，然後 Cmd+C 複製")
        input("按Enter確認已複製對話內容...")
        
        # 獲取剪貼板內容
        try:
            import pyperclip
            conversation_content = pyperclip.paste()
            
            # 保存對話內容
            filename = f"manus_conversation_{session_num}_{int(time.time())}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(conversation_content)
            
            print(f"💾 對話內容已保存到: {filename}")
            
        except ImportError:
            print("⚠️ 需要安裝 pyperclip: pip install pyperclip")
            print("📝 請手動保存對話內容")
    
    def extract_safari_data(self):
        """提取Safari開發相關數據"""
        print("🦁 開始Safari數據提取...")
        
        # 打開Safari並導航到相關頁面
        safari_urls = [
            "https://developer.apple.com/documentation/",
            "https://webkit.org/",
            # 添加更多相關URL
        ]
        
        for url in safari_urls:
            webbrowser.open_new_tab(url)
            time.sleep(2)
        
        print("🔍 Safari數據提取（手動記錄）...")
        num_tasks = int(input("❓ Safari開發任務數量？"))
        
        for task_id in range(1, num_tasks + 1):
            print(f"\\n🦁 Safari任務 {task_id}:")
            task_desc = input("   任務描述: ")
            satisfaction = int(input("   滿意度 (1-10): "))
            exec_time = float(input("   執行時間 (秒): "))
            
            task_data = {
                "task_id": f"safari_{task_id}",
                "description": task_desc,
                "satisfaction": satisfaction,
                "execution_time": exec_time,
                "timestamp": datetime.now().isoformat(),
                "source": "safari"
            }
            
            self.data_collection_results.append(task_data)
    
    def save_collected_data(self):
        """保存收集到的數據"""
        timestamp = int(time.time())
        filename = f"powerauto_data_collection_{timestamp}.json"
        
        collection_summary = {
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "total_tasks": len(self.data_collection_results),
            "sources": list(set([task["source"] for task in self.data_collection_results])),
            "tasks": self.data_collection_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(collection_summary, f, indent=2, ensure_ascii=False)
        
        print(f"💾 數據已保存到: {filename}")
        
        # 生成統計報告
        self.generate_summary_report(collection_summary)
    
    def generate_summary_report(self, data: Dict):
        """生成數據收集總結報告"""
        print("\\n📊 數據收集總結報告")
        print("=" * 50)
        
        # 按來源統計
        sources_stats = {}
        for task in data["tasks"]:
            source = task["source"]
            if source not in sources_stats:
                sources_stats[source] = {
                    "count": 0,
                    "avg_satisfaction": 0,
                    "total_time": 0
                }
            
            sources_stats[source]["count"] += 1
            sources_stats[source]["avg_satisfaction"] += task["satisfaction"]
            sources_stats[source]["total_time"] += task["execution_time"]
        
        # 計算平均值
        for source in sources_stats:
            stats = sources_stats[source]
            stats["avg_satisfaction"] = stats["avg_satisfaction"] / stats["count"]
            stats["avg_time"] = stats["total_time"] / stats["count"]
        
        print(f"總任務數: {data['total_tasks']}")
        print("\\n按來源統計:")
        for source, stats in sources_stats.items():
            print(f"  {source:10} | 任務數: {stats['count']:2d} | 平均滿意度: {stats['avg_satisfaction']:.1f}/10 | 平均時間: {stats['avg_time']:.1f}s")
        
        print("\\n📋 接下來可以:")
        print("1. 使用收集的數據作為Claude基準")
        print("2. 對相同任務測試K2性能")
        print("3. 生成質量對比報告")
        print("4. 制定PowerAuto.ai產品策略")

def main():
    """主函數"""
    print("🚀 PowerAuto.ai 本地自動化數據收集")
    print("避免重複認證，直接使用現有瀏覽器會話")
    print("=" * 60)
    
    automation = LocalBrowserAutomation()
    
    try:
        # 提取Manus數據
        automation.open_manus_sessions()
        
        # 提取Safari數據
        collect_safari = input("\\n🦁 是否收集Safari開發數據？(y/n): ").lower() == 'y'
        if collect_safari:
            automation.extract_safari_data()
        
        # 保存數據
        automation.save_collected_data()
        
    except KeyboardInterrupt:
        print("\\n👋 用戶中斷，保存已收集的數據...")
        automation.save_collected_data()
    except Exception as e:
        print(f"\\n❌ 發生錯誤: {e}")
        automation.save_collected_data()

if __name__ == "__main__":
    main()
'''
    
    def generate_powerauto_ai_nginx(self, ec2_ip: str) -> str:
        """生成powerauto.ai的Nginx配置"""
        
        return f'''# PowerAuto.ai Nginx配置
# 域名: powerauto.ai
# EC2 IP: {ec2_ip}

# HTTP重定向到HTTPS
server {{
    listen 80;
    server_name powerauto.ai www.powerauto.ai api.powerauto.ai admin.powerauto.ai dev.powerauto.ai beta.powerauto.ai app.powerauto.ai;
    return 301 https://$server_name$request_uri;
}}

# 主域名 HTTPS - PowerAuto.ai
server {{
    listen 443 ssl http2;
    server_name powerauto.ai www.powerauto.ai;
    
    # SSL證書配置
    ssl_certificate /etc/letsencrypt/live/powerauto.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/powerauto.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全頭
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # 主應用 - PowerAutomation ClaudeEditor
    location / {{
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }}
    
    # 靜態文件
    location /static/ {{
        alias /var/www/powerauto/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    }}
    
    # WebSocket支持
    location /ws/ {{
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}

# API子域名 - api.powerauto.ai
server {{
    listen 443 ssl http2;
    server_name api.powerauto.ai;
    
    # SSL證書配置
    ssl_certificate /etc/letsencrypt/live/powerauto.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/powerauto.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # CORS配置
    add_header Access-Control-Allow-Origin "https://powerauto.ai" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
    
    # API服務
    location / {{
        if ($request_method = 'OPTIONS') {{
            add_header Access-Control-Allow-Origin "https://powerauto.ai";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With";
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 200;
        }}
        
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # API特定配置
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        
        # 限流配置
        limit_req zone=api burst=20 nodelay;
    }}
}}

# 管理後台 - admin.powerauto.ai
server {{
    listen 443 ssl http2;
    server_name admin.powerauto.ai;
    
    # SSL證書配置
    ssl_certificate /etc/letsencrypt/live/powerauto.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/powerauto.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # 額外安全設置 (管理後台)
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer" always;
    
    # IP白名單 (可選)
    # allow {ec2_ip};
    # deny all;
    
    # 管理後台應用
    location / {{
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}

# 開發者平台 - dev.powerauto.ai
server {{
    listen 443 ssl http2;
    server_name dev.powerauto.ai;
    
    # SSL證書配置
    ssl_certificate /etc/letsencrypt/live/powerauto.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/powerauto.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # 開發者平台應用
    location / {{
        proxy_pass http://127.0.0.1:3002;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # API文檔
    location /docs/ {{
        proxy_pass http://127.0.0.1:8000/docs/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}

# Beta測試平台 - beta.powerauto.ai
server {{
    listen 443 ssl http2;
    server_name beta.powerauto.ai;
    
    # SSL證書配置
    ssl_certificate /etc/letsencrypt/live/powerauto.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/powerauto.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Beta平台應用
    location / {{
        proxy_pass http://127.0.0.1:3003;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}

# 主應用 - app.powerauto.ai
server {{
    listen 443 ssl http2;
    server_name app.powerauto.ai;
    
    # SSL證書配置
    ssl_certificate /etc/letsencrypt/live/powerauto.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/powerauto.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # 主應用 (與主域名相同的應用)
    location / {{
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }}
}}

# 限流配置
http {{
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;
}}'''
    
    def generate_deployment_script(self, ec2_ip: str, admin_email: str) -> str:
        """生成powerauto.ai部署腳本"""
        
        return f'''#!/bin/bash
# PowerAuto.ai 完整部署腳本
# 域名: powerauto.ai
# EC2 IP: {ec2_ip}
# 管理員郵箱: {admin_email}

set -e

echo "🚀 PowerAuto.ai 部署開始"
echo "域名: powerauto.ai"
echo "EC2 IP: {ec2_ip}"
echo "時間: $(date)"

# 檢查必要環境變量
export DOMAIN="powerauto.ai"
export EC2_IP="{ec2_ip}"
export ADMIN_EMAIL="{admin_email}"

# 1. 系統更新和依賴安裝
echo "📦 更新系統和安裝依賴..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx certbot python3-certbot-nginx docker.io docker-compose git python3-pip nodejs npm

# 2. 配置防火牆
echo "🛡️ 配置防火牆..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 3000:3003/tcp  # 應用端口
sudo ufw allow 8000/tcp       # API端口
sudo ufw --force enable

# 3. 克隆PowerAutomation代碼
echo "📂 克隆PowerAutomation代碼..."
if [ ! -d "/var/www/powerauto" ]; then
    sudo mkdir -p /var/www/powerauto
    sudo chown $USER:$USER /var/www/powerauto
    cd /var/www/powerauto
    
    # 這裡需要你的實際Git倉庫
    # git clone https://github.com/your-repo/powerautomation.git .
    
    # 或者從當前目錄複製文件
    echo "📋 請手動上傳PowerAutomation代碼到 /var/www/powerauto/"
    echo "包含所有我們創建的文件："
    echo "  - index.html (ClaudeEditor界面)"
    echo "  - member_system.py"
    echo "  - k2_provider_integration.py"
    echo "  - real_time_comparison_tracker.py"
    echo "  - 等等..."
fi

# 4. 安裝Python依賴
echo "🐍 安裝Python依賴..."
cd /var/www/powerauto
pip3 install -r requirements.txt || echo "⚠️ requirements.txt不存在，請手動安裝依賴"

# 5. 安裝Node.js依賴
echo "📦 安裝Node.js依賴..."
if [ -f "package.json" ]; then
    npm install
fi

# 6. 配置Nginx
echo "🔧 配置Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/powerauto.ai
sudo ln -sf /etc/nginx/sites-available/powerauto.ai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 測試Nginx配置
sudo nginx -t

# 7. 啟動Nginx
echo "🚀 啟動Nginx..."
sudo systemctl enable nginx
sudo systemctl restart nginx

# 8. 申請SSL證書
echo "🔒 申請SSL證書..."
sudo certbot --nginx -d powerauto.ai -d www.powerauto.ai -d api.powerauto.ai -d admin.powerauto.ai -d dev.powerauto.ai -d beta.powerauto.ai -d app.powerauto.ai --non-interactive --agree-tos --email $ADMIN_EMAIL

# 9. 設置SSL自動續期
echo "⏰ 設置SSL自動續期..."
(sudo crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -

# 10. 創建環境變量文件
echo "⚙️ 創建環境變量配置..."
cat > /var/www/powerauto/.env << EOF
# PowerAuto.ai 環境變量
DOMAIN=powerauto.ai
EC2_IP={ec2_ip}
ADMIN_EMAIL={admin_email}

# 數據庫配置
DATABASE_URL=postgresql://powerauto:password@localhost/powerauto_db

# Redis配置 
REDIS_URL=redis://localhost:6379

# API配置
CLAUDE_API_KEY=your_claude_api_key_here
MOONSHOT_API_KEY=your_moonshot_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# 支付配置 (稍後配置)
STRIPE_SECRET_KEY=your_stripe_secret_key
ALIPAY_APP_ID=your_alipay_app_id
WECHAT_MCH_ID=your_wechat_mch_id

# 應用端口
MAIN_APP_PORT=3000
ADMIN_APP_PORT=3001
DEV_APP_PORT=3002
BETA_APP_PORT=3003
API_PORT=8000
EOF

# 11. 設置Docker服務
echo "🐳 配置Docker服務..."
if [ -f "docker-compose.yml" ]; then
    sudo docker-compose up -d
fi

# 12. 創建系統服務
echo "⚙️ 創建PowerAuto.ai系統服務..."
sudo tee /etc/systemd/system/powerauto.service > /dev/null <<EOF
[Unit]
Description=PowerAuto.ai Main Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/var/www/powerauto
Environment=NODE_ENV=production
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 啟用服務
sudo systemctl daemon-reload
sudo systemctl enable powerauto
sudo systemctl start powerauto

# 13. 健康檢查
echo "🏥 執行健康檢查..."
sleep 10

# 檢查域名
for subdomain in "" "www." "api." "admin." "dev." "beta." "app."; do
    url="https://${{subdomain}}powerauto.ai"
    echo "檢查: $url"
    if curl -f -s -I "$url" > /dev/null; then
        echo "✅ $url - OK"
    else
        echo "❌ $url - 失敗"
    fi
done

# 14. 生成部署報告
echo "📋 生成部署報告..."
cat > /var/www/powerauto/deployment_report.json << EOF
{{
    "domain": "powerauto.ai",
    "ec2_ip": "{ec2_ip}",
    "deployed_at": "$(date -Iseconds)",
    "ssl_status": "enabled",
    "services": {{
        "nginx": "$(sudo systemctl is-active nginx)",
        "powerauto": "$(sudo systemctl is-active powerauto)"
    }},
    "urls": {{
        "main": "https://powerauto.ai",
        "api": "https://api.powerauto.ai",
        "admin": "https://admin.powerauto.ai",
        "dev": "https://dev.powerauto.ai",
        "beta": "https://beta.powerauto.ai",
        "app": "https://app.powerauto.ai"
    }}
}}
EOF

echo ""
echo "🎉 PowerAuto.ai 部署完成！"
echo ""
echo "🌐 訪問地址："
echo "   主網站: https://powerauto.ai"
echo "   API端點: https://api.powerauto.ai"
echo "   管理後台: https://admin.powerauto.ai"
echo "   開發者平台: https://dev.powerauto.ai"
echo "   Beta測試: https://beta.powerauto.ai"
echo "   主應用: https://app.powerauto.ai"
echo ""
echo "📋 接下來需要完成："
echo "   1. 配置API密鑰 (.env文件)"
echo "   2. 設置支付集成"
echo "   3. 導入PowerAutomation代碼"
echo "   4. 測試所有功能"
echo "   5. 邀請Beta開發者"
echo ""
echo "📊 部署報告: /var/www/powerauto/deployment_report.json"
'''

def main():
    """主函數"""
    deployment = PowerAutoAIDeployment()
    
    print("🚀 PowerAuto.ai 完整部署方案")
    print("=" * 50)
    print(f"域名: {deployment.domain}")
    print(f"子域名: {', '.join(deployment.subdomains)}")
    
    # 獲取用戶輸入
    print("\n❗ 需要您提供以下信息:")
    ec2_ip = input("🖥️  AWS EC2公網IP地址: ").strip()
    admin_email = input("📧 管理員郵箱地址: ").strip()
    
    if not ec2_ip or not admin_email:
        print("❌ IP地址和郵箱地址不能為空")
        return
    
    # 生成DNS記錄
    dns_records = deployment.generate_real_dns_records(ec2_ip)
    with open('powerauto_ai_dns_records.json', 'w', encoding='utf-8') as f:
        json.dump(dns_records, f, indent=2, ensure_ascii=False)
    
    # 生成Nginx配置
    nginx_config = deployment.generate_powerauto_ai_nginx(ec2_ip)
    with open('powerauto_ai_nginx.conf', 'w', encoding='utf-8') as f:
        f.write(nginx_config)
    
    # 生成部署腳本
    deploy_script = deployment.generate_deployment_script(ec2_ip, admin_email)
    with open('deploy_powerauto_ai.sh', 'w', encoding='utf-8') as f:
        f.write(deploy_script)
    
    # 生成本地自動化腳本
    automation_script = deployment.generate_local_automation_script()
    with open('local_browser_automation.py', 'w', encoding='utf-8') as f:
        f.write(automation_script)
    
    print(f"\n✅ PowerAuto.ai 部署文件已生成:")
    print(f"   powerauto_ai_dns_records.json - DNS記錄")
    print(f"   powerauto_ai_nginx.conf - Nginx配置")
    print(f"   deploy_powerauto_ai.sh - 完整部署腳本")
    print(f"   local_browser_automation.py - 本地數據收集腳本")
    
    print(f"\n🎯 您的PowerAuto.ai配置:")
    print(f"   主域名: powerauto.ai -> {ec2_ip}")
    print(f"   API: api.powerauto.ai -> {ec2_ip}")
    print(f"   管理: admin.powerauto.ai -> {ec2_ip}")
    print(f"   開發: dev.powerauto.ai -> {ec2_ip}")
    print(f"   測試: beta.powerauto.ai -> {ec2_ip}")
    print(f"   應用: app.powerauto.ai -> {ec2_ip}")
    
    print(f"\n📋 立即行動:")
    print(f"   1. 在DNS提供商添加DNS記錄")
    print(f"   2. 上傳文件到EC2服務器")
    print(f"   3. 執行: chmod +x deploy_powerauto_ai.sh")
    print(f"   4. 運行: ./deploy_powerauto_ai.sh")
    print(f"   5. 使用local_browser_automation.py收集Manus數據")

if __name__ == "__main__":
    main()