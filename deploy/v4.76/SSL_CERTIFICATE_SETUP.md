# PowerAuto.ai SSL Certificate Setup

## 🔒 Let's Encrypt SSL Certificate Configuration

This document describes the SSL certificate setup for PowerAuto.ai using Let's Encrypt.

## Certificate Details

- **Domain**: powerauto.ai
- **Certificate Authority**: Let's Encrypt
- **Certificate Type**: ECDSA
- **Expiry Date**: 2025-10-19
- **Valid For**: 89 days (auto-renewal enabled)

## Installation Process

### 1. Install Certbot
```bash
sudo yum install -y python3-certbot-nginx
```

### 2. Configure Basic Nginx
```bash
# Basic HTTP configuration first
server {
    listen 80;
    server_name powerauto.ai;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Obtain SSL Certificate
```bash
sudo certbot --nginx -d powerauto.ai --non-interactive --agree-tos --email chuang.hsiaoyen@gmail.com
```

### 4. Enable Auto-Renewal
```bash
sudo systemctl enable certbot-renew.timer
sudo systemctl start certbot-renew.timer
```

## Certificate Files

- **Certificate**: `/etc/letsencrypt/live/powerauto.ai/fullchain.pem`
- **Private Key**: `/etc/letsencrypt/live/powerauto.ai/privkey.pem`

## Verification

### Test HTTPS Connection
```bash
curl -I https://powerauto.ai/
```

### Check Certificate Status
```bash
sudo certbot certificates
```

### Verify Auto-Renewal
```bash
sudo certbot renew --dry-run
```

## Benefits

✅ **Trusted Certificate**: No browser warnings
✅ **Auto-Renewal**: Certificates update automatically before expiry
✅ **Payment Ready**: Secure HTTPS for payment processing
✅ **Enterprise Grade**: Meets enterprise security requirements
✅ **SEO Friendly**: HTTPS boosts search rankings

## Monitoring

- Auto-renewal timer: `systemctl status certbot-renew.timer`
- Certificate expiry: Check every 60 days
- Renewal logs: `/var/log/letsencrypt/letsencrypt.log`

## Troubleshooting

### Certificate Renewal Issues
```bash
# Manual renewal
sudo certbot renew --force-renewal

# Check nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

### Domain Verification Issues
- Ensure domain points to correct IP: 13.222.125.83
- Check DNS propagation: `nslookup powerauto.ai`
- Verify port 80 is accessible for Let's Encrypt validation

---

**PowerAuto.ai SSL Certificate Setup Complete** 🔒✅
*Updated: 2025-07-21*