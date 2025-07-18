#!/usr/bin/env python3
"""
支付集成配置模板
需要用戶提供真實的支付商戶信息和API認證
"""

import json
from typing import Dict, Any
from datetime import datetime

class PaymentIntegrationSetup:
    """支付集成配置設置"""
    
    def __init__(self):
        self.payment_config_template = self._create_payment_config_template()
        
    def _create_payment_config_template(self) -> Dict[str, Any]:
        """創建支付配置模板"""
        
        return {
            "alipay": {
                "provider": "支付寶",
                "required_credentials": {
                    "app_id": {
                        "description": "支付寶開放平台應用ID",
                        "example": "2021001234567890",
                        "required": True,
                        "where_to_get": "支付寶開放平台 -> 我的應用 -> 應用詳情"
                    },
                    "private_key": {
                        "description": "應用私鑰 (RSA2048)",
                        "example": "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...",
                        "required": True,
                        "where_to_get": "支付寶開放平台 -> 開發設置 -> 接口加密方式"
                    },
                    "alipay_public_key": {
                        "description": "支付寶公鑰",
                        "example": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
                        "required": True,
                        "where_to_get": "支付寶開放平台 -> 開發設置 -> 支付寶公鑰"
                    },
                    "sign_type": {
                        "description": "簽名算法",
                        "example": "RSA2",
                        "required": True,
                        "default": "RSA2"
                    }
                },
                "configuration_steps": [
                    "1. 登錄支付寶開放平台 (open.alipay.com)",
                    "2. 創建應用並獲得app_id",
                    "3. 上傳應用公鑰，獲取支付寶公鑰",
                    "4. 申請手機網站支付能力",
                    "5. 配置應用網關和授權回調地址",
                    "6. 提交審核並上線"
                ],
                "callback_urls": {
                    "notify_url": "https://your-domain.com/api/payment/alipay/notify",
                    "return_url": "https://your-domain.com/payment/success"
                },
                "supported_features": [
                    "即時到賬",
                    "手機網站支付",
                    "掃碼支付",
                    "APP支付"
                ]
            },
            "wechat_pay": {
                "provider": "微信支付",
                "required_credentials": {
                    "mch_id": {
                        "description": "微信支付商戶號",
                        "example": "1234567890",
                        "required": True,
                        "where_to_get": "微信支付商戶平台 -> 賬戶中心 -> 商戶信息"
                    },
                    "app_id": {
                        "description": "微信公眾號/小程序AppID",
                        "example": "wx1234567890abcdef",
                        "required": True,
                        "where_to_get": "微信公眾平台 -> 開發 -> 基本配置"
                    },
                    "mch_key": {
                        "description": "商戶API密鑰",
                        "example": "32位字符串密鑰",
                        "required": True,
                        "where_to_get": "微信支付商戶平台 -> 賬戶中心 -> API安全"
                    },
                    "cert_path": {
                        "description": "商戶證書路徑",
                        "example": "/path/to/apiclient_cert.pem",
                        "required": True,
                        "where_to_get": "微信支付商戶平台 -> 賬戶中心 -> API證書"
                    },
                    "key_path": {
                        "description": "商戶私鑰路徑",
                        "example": "/path/to/apiclient_key.pem",
                        "required": True,
                        "where_to_get": "下載的證書包中的私鑰文件"
                    }
                },
                "configuration_steps": [
                    "1. 註冊微信支付商戶賬號",
                    "2. 完成商戶資質認證",
                    "3. 獲取商戶號和API密鑰",
                    "4. 下載API證書",
                    "5. 配置支付授權目錄",
                    "6. 設置接收通知URL"
                ],
                "callback_urls": {
                    "notify_url": "https://your-domain.com/api/payment/wechat/notify",
                    "redirect_url": "https://your-domain.com/payment/success"
                },
                "supported_features": [
                    "JSAPI支付",
                    "Native支付",
                    "H5支付",
                    "小程序支付"
                ]
            },
            "stripe": {
                "provider": "Stripe",
                "required_credentials": {
                    "publishable_key": {
                        "description": "Stripe可發布密鑰",
                        "example": "pk_live_51234567890abcdef...",
                        "required": True,
                        "where_to_get": "Stripe Dashboard -> API Keys -> Publishable key"
                    },
                    "secret_key": {
                        "description": "Stripe秘密密鑰",
                        "example": "sk_live_51234567890abcdef...",
                        "required": True,
                        "where_to_get": "Stripe Dashboard -> API Keys -> Secret key"
                    },
                    "webhook_secret": {
                        "description": "Webhook端點秘密",
                        "example": "whsec_1234567890abcdef...",
                        "required": True,
                        "where_to_get": "Stripe Dashboard -> Webhooks -> 端點詳情"
                    }
                },
                "configuration_steps": [
                    "1. 註冊Stripe賬戶並完成KYC驗證",
                    "2. 在Dashboard中激活Live模式",
                    "3. 獲取API密鑰",
                    "4. 配置Webhook端點",
                    "5. 設置產品和價格",
                    "6. 配置稅務設置"
                ],
                "webhook_events": [
                    "payment_intent.succeeded",
                    "payment_intent.payment_failed",
                    "customer.subscription.created",
                    "customer.subscription.updated",
                    "customer.subscription.deleted",
                    "invoice.payment_succeeded",
                    "invoice.payment_failed"
                ],
                "callback_urls": {
                    "webhook_url": "https://your-domain.com/api/payment/stripe/webhook",
                    "success_url": "https://your-domain.com/payment/success",
                    "cancel_url": "https://your-domain.com/payment/cancel"
                },
                "supported_features": [
                    "一次性付款",
                    "訂閱付款",
                    "多種支付方式",
                    "自動發票",
                    "稅務處理"
                ]
            }
        }
    
    def generate_env_template(self) -> str:
        """生成環境變量模板"""
        
        template = """# PowerAutomation 支付配置環境變量
# 請填入您的真實支付商戶信息

# ============== 支付寶配置 ==============
# 從支付寶開放平台獲取
ALIPAY_APP_ID=your_alipay_app_id_here
ALIPAY_PRIVATE_KEY=your_alipay_private_key_here
ALIPAY_PUBLIC_KEY=your_alipay_public_key_here
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_SANDBOX=false  # 生產環境設置為false

# ============== 微信支付配置 ==============
# 從微信支付商戶平台獲取
WECHAT_MCH_ID=your_wechat_mch_id_here
WECHAT_APP_ID=your_wechat_app_id_here
WECHAT_MCH_KEY=your_wechat_mch_key_here
WECHAT_CERT_PATH=/path/to/apiclient_cert.pem
WECHAT_KEY_PATH=/path/to/apiclient_key.pem
WECHAT_SANDBOX=false  # 生產環境設置為false

# ============== Stripe配置 ==============
# 從Stripe Dashboard獲取
STRIPE_PUBLISHABLE_KEY=pk_live_your_key_here
STRIPE_SECRET_KEY=sk_live_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_MODE=live  # 或 test

# ============== 通用配置 ==============
PAYMENT_CURRENCY=CNY  # 或 USD
PAYMENT_SUCCESS_URL=https://your-domain.com/payment/success
PAYMENT_CANCEL_URL=https://your-domain.com/payment/cancel
PAYMENT_NOTIFY_EMAIL=your-email@domain.com

# ============== PowerAutomation特定配置 ==============
# 會員價格 (分為單位)
PRICE_PERSONAL_MONTHLY=9900  # ¥99.00
PRICE_PROFESSIONAL_MONTHLY=59900  # ¥599.00
PRICE_TEAM_MONTHLY=59900  # ¥599.00 (5人)
PRICE_ENTERPRISE_MONTHLY=99900  # ¥999.00 per user

# 免費試用配置
FREE_TRIAL_DAYS=7
BETA_DEVELOPER_DAYS=60

# 支付安全配置
PAYMENT_ENCRYPTION_KEY=your_32_char_encryption_key_here
PAYMENT_SESSION_TIMEOUT=1800  # 30分鐘
"""
        
        return template
    
    def generate_configuration_checklist(self) -> Dict[str, Any]:
        """生成配置檢查清單"""
        
        return {
            "pre_setup": {
                "title": "配置前準備",
                "tasks": [
                    "✅ 準備企業營業執照和相關資質文件",
                    "✅ 準備銀行賬戶信息 (對公賬戶)",
                    "✅ 準備網站域名和SSL證書",
                    "✅ 確定產品定價策略",
                    "✅ 準備客服聯繫方式"
                ]
            },
            "alipay_setup": {
                "title": "支付寶配置步驟",
                "estimated_time": "2-3個工作日",
                "tasks": [
                    "□ 註冊支付寶開放平台賬號",
                    "□ 創建應用並提交資質審核",
                    "□ 生成RSA密鑰對",
                    "□ 配置應用公鑰",
                    "□ 申請手機網站支付產品",
                    "□ 配置授權回調地址",
                    "□ 測試支付流程"
                ]
            },
            "wechat_setup": {
                "title": "微信支付配置步驟", 
                "estimated_time": "3-5個工作日",
                "tasks": [
                    "□ 註冊微信支付商戶賬號",
                    "□ 提交商戶資質認證",
                    "□ 等待審核通過",
                    "□ 獲取商戶號和API密鑰",
                    "□ 下載API證書",
                    "□ 配置支付授權目錄",
                    "□ 設置接收通知URL",
                    "□ 測試支付流程"
                ]
            },
            "stripe_setup": {
                "title": "Stripe配置步驟",
                "estimated_time": "1-2個工作日",
                "tasks": [
                    "□ 註冊Stripe賬戶",
                    "□ 完成身份驗證 (KYC)",
                    "□ 激活Live模式",
                    "□ 配置產品和價格",
                    "□ 設置Webhook端點",
                    "□ 配置稅務設置",
                    "□ 測試支付流程"
                ]
            },
            "integration_testing": {
                "title": "集成測試",
                "tasks": [
                    "□ 測試支付寶支付流程",
                    "□ 測試微信支付流程", 
                    "□ 測試Stripe支付流程",
                    "□ 測試訂閱創建和取消",
                    "□ 測試退款流程",
                    "□ 測試Webhook通知",
                    "□ 測試異常情況處理"
                ]
            },
            "security_compliance": {
                "title": "安全合規檢查",
                "tasks": [
                    "□ 確保所有支付數據加密傳輸",
                    "□ 實施PCI DSS合規要求",
                    "□ 設置支付日誌和監控",
                    "□ 配置防欺詐檢測",
                    "□ 設置支付限額和風控",
                    "□ 準備隱私政策和服務條款"
                ]
            }
        }
    
    def generate_integration_code_template(self) -> str:
        """生成支付集成代碼模板"""
        
        return '''# PowerAutomation 支付集成代碼模板
# 需要安裝依賴: pip install alipay-sdk-python wechatpay-python stripe

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import hashlib
import json

# 支付寶集成
from alipay import AliPay

class AlipayIntegration:
    def __init__(self):
        self.alipay = AliPay(
            appid=os.getenv('ALIPAY_APP_ID'),
            app_notify_url=f"{os.getenv('BASE_URL')}/api/payment/alipay/notify",
            app_private_key_string=os.getenv('ALIPAY_PRIVATE_KEY'),
            alipay_public_key_string=os.getenv('ALIPAY_PUBLIC_KEY'),
            sign_type="RSA2",
            debug=os.getenv('ALIPAY_SANDBOX', 'false').lower() == 'true'
        )
    
    def create_payment(self, order_id: str, amount: float, subject: str) -> str:
        """創建支付寶支付"""
        order_string = self.alipay.api_alipay_trade_wap_pay(
            out_trade_no=order_id,
            total_amount=str(amount),
            subject=subject,
            return_url=f"{os.getenv('BASE_URL')}/payment/success",
            notify_url=f"{os.getenv('BASE_URL')}/api/payment/alipay/notify"
        )
        return f"https://openapi.alipay.com/gateway.do?{order_string}"

# 微信支付集成
from wechatpay import WeChatPay

class WechatPayIntegration:
    def __init__(self):
        self.wxpay = WeChatPay(
            wechatpay_type=WeChatPay.NATIVE,
            mchid=os.getenv('WECHAT_MCH_ID'),
            private_key=open(os.getenv('WECHAT_KEY_PATH')).read(),
            cert_serial_no='your_cert_serial_no',
            app_id=os.getenv('WECHAT_APP_ID'),
            mch_key=os.getenv('WECHAT_MCH_KEY')
        )
    
    def create_payment(self, order_id: str, amount: int, description: str) -> Dict:
        """創建微信支付"""
        # 微信支付金額以分為單位
        return self.wxpay.pay(
            description=description,
            out_trade_no=order_id,
            amount={'total': amount},
            notify_url=f"{os.getenv('BASE_URL')}/api/payment/wechat/notify"
        )

# Stripe集成
import stripe

class StripeIntegration:
    def __init__(self):
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    def create_payment_intent(self, amount: int, currency: str = 'cny') -> Dict:
        """創建Stripe支付意圖"""
        return stripe.PaymentIntent.create(
            amount=amount,  # 以分為單位
            currency=currency,
            metadata={'platform': 'powerautomation'}
        )
    
    def create_subscription(self, customer_id: str, price_id: str) -> Dict:
        """創建訂閱"""
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': price_id}],
            trial_period_days=7  # 7天免費試用
        )

# 統一支付管理器
class PaymentManager:
    def __init__(self):
        self.alipay = AlipayIntegration()
        self.wechat = WechatPayIntegration()
        self.stripe = StripeIntegration()
    
    def create_payment(self, payment_method: str, order_info: Dict) -> Dict:
        """統一支付創建接口"""
        if payment_method == 'alipay':
            return {
                'type': 'redirect',
                'url': self.alipay.create_payment(
                    order_info['order_id'],
                    order_info['amount'],
                    order_info['subject']
                )
            }
        elif payment_method == 'wechat':
            return {
                'type': 'qrcode',
                'data': self.wechat.create_payment(
                    order_info['order_id'],
                    int(order_info['amount'] * 100),  # 轉換為分
                    order_info['subject']
                )
            }
        elif payment_method == 'stripe':
            return {
                'type': 'elements',
                'client_secret': self.stripe.create_payment_intent(
                    int(order_info['amount'] * 100),  # 轉換為分
                    order_info.get('currency', 'cny')
                )['client_secret']
            }
        else:
            raise ValueError(f"Unsupported payment method: {payment_method}")

# 使用示例
if __name__ == "__main__":
    # 確保環境變量已設置
    required_vars = [
        'ALIPAY_APP_ID', 'ALIPAY_PRIVATE_KEY', 'ALIPAY_PUBLIC_KEY',
        'WECHAT_MCH_ID', 'WECHAT_APP_ID', 'WECHAT_MCH_KEY',
        'STRIPE_SECRET_KEY', 'BASE_URL'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ 缺少環境變量: {', '.join(missing_vars)}")
        print("請參考 .env.template 文件配置")
        exit(1)
    
    print("✅ 支付集成配置完成!")
'''

def main():
    """生成支付配置文件"""
    setup = PaymentIntegrationSetup()
    
    print("💳 PowerAutomation 支付集成配置")
    print("=" * 50)
    
    # 生成環境變量模板
    env_template = setup.generate_env_template()
    with open('.env.payment.template', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    # 生成配置檢查清單
    checklist = setup.generate_configuration_checklist()
    with open('payment_setup_checklist.json', 'w', encoding='utf-8') as f:
        json.dump(checklist, f, indent=2, ensure_ascii=False)
    
    # 生成集成代碼模板
    code_template = setup.generate_integration_code_template()
    with open('payment_integration_template.py', 'w', encoding='utf-8') as f:
        f.write(code_template)
    
    # 生成完整配置
    config = setup.payment_config_template
    with open('payment_providers_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("📁 已生成支付配置文件:")
    print("   .env.payment.template - 環境變量模板")
    print("   payment_setup_checklist.json - 配置檢查清單")
    print("   payment_integration_template.py - 代碼集成模板")
    print("   payment_providers_config.json - 完整配置信息")
    
    print("\n🚨 緊急需要的信息:")
    print("   ✅ 支付寶開放平台賬號和應用信息")
    print("   ✅ 微信支付商戶號和API證書")
    print("   ✅ Stripe賬戶和API密鑰")
    print("   ✅ 企業資質和銀行賬戶信息")
    
    print("\n⏰ 預計配置時間:")
    print("   支付寶: 2-3個工作日")
    print("   微信支付: 3-5個工作日")
    print("   Stripe: 1-2個工作日")
    
    print("\n📋 下一步行動:")
    print("   1. 填寫 .env.payment.template 中的真實信息")
    print("   2. 按照 payment_setup_checklist.json 完成配置")
    print("   3. 使用 payment_integration_template.py 進行集成")
    print("   4. 完成測試後部署到生產環境")

if __name__ == "__main__":
    main()