#!/usr/bin/env python3
"""
DNS配置指南
需要用戶提供域名信息以完成PowerAutomation部署
"""

import json
from typing import Dict, List, Any
from datetime import datetime

class DNSConfigurationGuide:
    """DNS配置指南"""
    
    def __init__(self):
        self.dns_requirements = self._create_dns_requirements()
        self.ssl_configuration = self._create_ssl_configuration()
        
    def _create_dns_requirements(self) -> Dict[str, Any]:
        """創建DNS配置需求"""
        
        return {
            "primary_domain": {
                "description": "主域名配置",
                "required_info": "您的主域名 (例如: powerautomation.com)",
                "dns_records": [
                    {
                        "type": "A",
                        "name": "@",
                        "value": "YOUR_AWS_EC2_IP",
                        "ttl": 300,
                        "description": "主域名指向EC2實例"
                    },
                    {
                        "type": "CNAME", 
                        "name": "www",
                        "value": "powerautomation.com",
                        "ttl": 300,
                        "description": "www子域名重定向到主域名"
                    }
                ]
            },
            "api_subdomain": {
                "description": "API子域名配置",
                "subdomain": "api.powerautomation.com",
                "dns_records": [
                    {
                        "type": "A",
                        "name": "api",
                        "value": "YOUR_AWS_EC2_IP",
                        "ttl": 300,
                        "description": "API端點"
                    }
                ]
            },
            "admin_subdomain": {
                "description": "管理後台子域名",
                "subdomain": "admin.powerautomation.com", 
                "dns_records": [
                    {
                        "type": "A",
                        "name": "admin",
                        "value": "YOUR_AWS_EC2_IP",
                        "ttl": 300,
                        "description": "管理後台"
                    }
                ]
            },
            "developer_subdomain": {
                "description": "開發者平台子域名",
                "subdomain": "dev.powerautomation.com",
                "dns_records": [
                    {
                        "type": "A",
                        "name": "dev",
                        "value": "YOUR_AWS_EC2_IP",
                        "ttl": 300,
                        "description": "開發者平台"
                    }
                ]
            },
            "cdn_subdomain": {
                "description": "CDN子域名 (可選)",
                "subdomain": "cdn.powerautomation.com",
                "dns_records": [
                    {
                        "type": "CNAME",
                        "name": "cdn",
                        "value": "YOUR_CLOUDFRONT_DOMAIN",
                        "ttl": 300,
                        "description": "靜態資源CDN"
                    }
                ]
            },
            "email_configuration": {
                "description": "郵件服務配置",
                "mx_records": [
                    {
                        "type": "MX",
                        "name": "@",
                        "value": "10 mail.powerautomation.com",
                        "ttl": 300,
                        "description": "主郵件服務器"
                    }
                ],
                "txt_records": [
                    {
                        "type": "TXT",
                        "name": "@",
                        "value": "v=spf1 include:_spf.google.com ~all",
                        "ttl": 300,
                        "description": "SPF記錄"
                    },
                    {
                        "type": "TXT",
                        "name": "_dmarc",
                        "value": "v=DMARC1; p=quarantine; rua=mailto:dmarc@powerautomation.com",
                        "ttl": 300,
                        "description": "DMARC策略"
                    }
                ]
            }
        }
    
    def _create_ssl_configuration(self) -> Dict[str, Any]:
        """創建SSL證書配置"""
        
        return {
            "certificates_needed": [
                "powerautomation.com",
                "*.powerautomation.com",  # 通配符證書
                "api.powerautomation.com",
                "admin.powerautomation.com",
                "dev.powerautomation.com"
            ],
            "certificate_providers": {
                "lets_encrypt": {
                    "description": "免費SSL證書",
                    "renewal": "自動續期",
                    "setup_command": "sudo certbot --nginx -d powerautomation.com -d *.powerautomation.com",
                    "pros": ["免費", "自動續期", "廣泛支持"],
                    "cons": ["90天有效期", "需要定期續期"]
                },
                "cloudflare": {
                    "description": "Cloudflare SSL", 
                    "renewal": "自動管理",
                    "setup": "通過Cloudflare面板配置",
                    "pros": ["免費", "自動管理", "額外安全功能"],
                    "cons": ["需要將DNS託管到Cloudflare"]
                },
                "aws_acm": {
                    "description": "AWS Certificate Manager",
                    "renewal": "自動續期",
                    "setup": "AWS控制台申請",
                    "pros": ["與AWS集成", "自動續期", "免費"],
                    "cons": ["僅限AWS服務使用"]
                }
            },
            "recommended_approach": "cloudflare",
            "security_headers": {
                "HSTS": "max-age=31536000; includeSubDomains",
                "CSP": "default-src 'self'; script-src 'self' 'unsafe-inline'",
                "X-Frame-Options": "DENY",
                "X-Content-Type-Options": "nosniff"
            }
        }
    
    def generate_dns_records_template(self, domain: str) -> List[Dict[str, str]]:
        """生成DNS記錄模板"""
        
        records = [
            # 主域名記錄
            {
                "Type": "A",
                "Name": "@",
                "Value": "[需要填入] 您的AWS EC2公網IP",
                "TTL": "300",
                "Description": f"主域名 {domain} 指向服務器"
            },
            {
                "Type": "CNAME",
                "Name": "www",
                "Value": domain,
                "TTL": "300",
                "Description": f"www.{domain} 重定向到主域名"
            },
            # API子域名
            {
                "Type": "A",
                "Name": "api",
                "Value": "[需要填入] 您的AWS EC2公網IP",
                "TTL": "300",
                "Description": "API服務端點"
            },
            # 管理後台
            {
                "Type": "A",
                "Name": "admin",
                "Value": "[需要填入] 您的AWS EC2公網IP",
                "TTL": "300",
                "Description": "管理後台"
            },
            # 開發者平台
            {
                "Type": "A", 
                "Name": "dev",
                "Value": "[需要填入] 您的AWS EC2公網IP",
                "TTL": "300",
                "Description": "開發者平台"
            },
            # Beta測試
            {
                "Type": "A",
                "Name": "beta",
                "Value": "[需要填入] 您的AWS EC2公網IP",
                "TTL": "300",
                "Description": "Beta測試平台"
            },
            # 郵件服務 (可選)
            {
                "Type": "MX",
                "Name": "@",
                "Value": f"10 mail.{domain}",
                "TTL": "300",
                "Description": "郵件服務器"
            },
            # SPF記錄
            {
                "Type": "TXT",
                "Name": "@",
                "Value": "v=spf1 include:_spf.google.com ~all",
                "TTL": "300",
                "Description": "SPF反垃圾郵件"
            }
        ]
        
        return records
    
    def generate_nginx_config(self, domain: str) -> str:
        """生成Nginx配置"""
        
        config = f'''# PowerAutomation Nginx配置
# 域名: {domain}

# HTTP重定向到HTTPS
server {{
    listen 80;
    server_name {domain} www.{domain} api.{domain} admin.{domain} dev.{domain} beta.{domain};
    return 301 https://$server_name$request_uri;
}}

# 主域名 HTTPS
server {{
    listen 443 ssl http2;
    server_name {domain} www.{domain};
    
    # SSL證書配置
    ssl_certificate /etc/ssl/certs/{domain}.crt;
    ssl_certificate_key /etc/ssl/private/{domain}.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全頭
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 主應用
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
    
    # 靜態文件
    location /static/ {{
        alias /var/www/powerautomation/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}

# API子域名
server {{
    listen 443 ssl http2;
    server_name api.{domain};
    
    # SSL證書配置 (同上)
    ssl_certificate /etc/ssl/certs/{domain}.crt;
    ssl_certificate_key /etc/ssl/private/{domain}.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # API服務
    location / {{
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
    }}
}}

# 管理後台
server {{
    listen 443 ssl http2;
    server_name admin.{domain};
    
    # SSL證書配置
    ssl_certificate /etc/ssl/certs/{domain}.crt;
    ssl_certificate_key /etc/ssl/private/{domain}.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    
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

# 開發者平台
server {{
    listen 443 ssl http2;
    server_name dev.{domain};
    
    # SSL證書配置
    ssl_certificate /etc/ssl/certs/{domain}.crt;
    ssl_certificate_key /etc/ssl/private/{domain}.key;
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
}}

# Beta測試平台
server {{
    listen 443 ssl http2;
    server_name beta.{domain};
    
    # SSL證書配置
    ssl_certificate /etc/ssl/certs/{domain}.crt;
    ssl_certificate_key /etc/ssl/private/{domain}.key;
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
}}'''
        
        return config
    
    def generate_deployment_script(self, domain: str) -> str:
        """生成部署腳本"""
        
        script = f'''#!/bin/bash
# PowerAutomation DNS和SSL部署腳本
# 域名: {domain}

set -e

echo "🚀 開始PowerAutomation DNS和SSL配置"
echo "域名: {domain}"
echo "時間: $(date)"

# 檢查必要的環境變量
if [ -z "$DOMAIN" ]; then
    export DOMAIN="{domain}"
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
sudo crontab -l | {{ cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; }} | sudo crontab -

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
echo "4. 開始100用戶測試"'''
        
        return script
    
    def create_dns_checklist(self) -> Dict[str, Any]:
        """創建DNS配置檢查清單"""
        
        return {
            "before_deployment": {
                "title": "部署前準備",
                "tasks": [
                    "□ 購買/準備域名",
                    "□ 獲取AWS EC2公網IP地址", 
                    "□ 選擇DNS服務商 (推薦Cloudflare)",
                    "□ 準備域名註冊商的DNS控制權限"
                ]
            },
            "dns_configuration": {
                "title": "DNS配置步驟",
                "estimated_time": "30分鐘",
                "tasks": [
                    "□ 添加A記錄指向EC2 IP",
                    "□ 添加CNAME記錄用於www重定向",
                    "□ 配置api子域名",
                    "□ 配置admin子域名",
                    "□ 配置dev子域名",
                    "□ 配置beta子域名",
                    "□ 等待DNS傳播 (最多24小時)"
                ]
            },
            "ssl_setup": {
                "title": "SSL證書配置",
                "estimated_time": "20分鐘",
                "tasks": [
                    "□ 安裝Certbot",
                    "□ 申請Let's Encrypt證書",
                    "□ 配置自動續期",
                    "□ 測試HTTPS訪問",
                    "□ 配置安全頭",
                    "□ 測試SSL評級 (ssllabs.com)"
                ]
            },
            "verification": {
                "title": "部署驗證",
                "tasks": [
                    "□ 測試主域名訪問",
                    "□ 測試所有子域名",
                    "□ 驗證HTTPS重定向",
                    "□ 檢查SSL證書有效性",
                    "□ 測試負載均衡 (如果適用)",
                    "□ 驗證郵件服務 (如果配置)"
                ]
            }
        }

def main():
    """生成DNS配置指南"""
    guide = DNSConfigurationGuide()
    
    print("🌐 PowerAutomation DNS配置指南")
    print("=" * 50)
    
    # 請求用戶輸入域名
    print("\n❗ 重要：需要您的域名信息")
    print("請提供以下信息以完成DNS配置:")
    print("1. 主域名 (例如: powerautomation.com)")
    print("2. AWS EC2實例的公網IP地址")
    print("3. 郵箱地址 (用於SSL證書註冊)")
    
    # 使用示例域名生成模板
    example_domain = "powerautomation.com"
    
    # 生成DNS記錄模板
    dns_records = guide.generate_dns_records_template(example_domain)
    with open('dns_records_template.json', 'w', encoding='utf-8') as f:
        json.dump(dns_records, f, indent=2, ensure_ascii=False)
    
    # 生成Nginx配置
    nginx_config = guide.generate_nginx_config(example_domain)
    with open('nginx.conf', 'w', encoding='utf-8') as f:
        f.write(nginx_config)
    
    # 生成部署腳本
    deploy_script = guide.generate_deployment_script(example_domain)
    with open('deploy_dns_ssl.sh', 'w', encoding='utf-8') as f:
        f.write(deploy_script)
    
    # 生成檢查清單
    checklist = guide.create_dns_checklist()
    with open('dns_setup_checklist.json', 'w', encoding='utf-8') as f:
        json.dump(checklist, f, indent=2, ensure_ascii=False)
    
    # 保存完整配置
    full_config = {
        "dns_requirements": guide.dns_requirements,
        "ssl_configuration": guide.ssl_configuration,
        "dns_records_template": dns_records,
        "generated_at": datetime.now().isoformat()
    }
    
    with open('dns_configuration_complete.json', 'w', encoding='utf-8') as f:
        json.dump(full_config, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 已生成DNS配置文件:")
    print(f"   dns_records_template.json - DNS記錄模板")
    print(f"   nginx.conf - Nginx配置文件")
    print(f"   deploy_dns_ssl.sh - 自動部署腳本")
    print(f"   dns_setup_checklist.json - 配置檢查清單")
    print(f"   dns_configuration_complete.json - 完整配置")
    
    print(f"\n🚨 緊急需要的信息:")
    print(f"   ✅ 您的域名 (例如: yourcompany.com)")
    print(f"   ✅ AWS EC2公網IP地址")
    print(f"   ✅ 管理員郵箱地址")
    print(f"   ✅ DNS管理權限 (Cloudflare/Aliyun/etc)")
    
    print(f"\n⏰ 配置時間估算:")
    print(f"   DNS配置: 30分鐘 + 24小時傳播")
    print(f"   SSL設置: 20分鐘")
    print(f"   總計: 約1小時 (不含DNS傳播)")
    
    print(f"\n📋 下一步行動:")
    print(f"   1. 提供域名和IP信息")
    print(f"   2. 修改模板文件中的實際值")
    print(f"   3. 執行: chmod +x deploy_dns_ssl.sh")
    print(f"   4. 運行: ./deploy_dns_ssl.sh")
    print(f"   5. 驗證所有域名正常訪問")

if __name__ == "__main__":
    main()