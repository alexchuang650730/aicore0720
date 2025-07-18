# PowerAutomation 支付集成代碼模板
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
