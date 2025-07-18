#!/usr/bin/env python3
"""
PowerAutomation 多重支付集成系統
支持支付寶、微信支付、Stripe三種支付方式
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
import hmac
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
from urllib.parse import quote_plus, urlencode
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class PaymentConfig:
    """支付配置"""
    
    # 支付寶配置
    ALIPAY_APP_ID = "your_alipay_app_id"
    ALIPAY_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
your_alipay_private_key_here
-----END RSA PRIVATE KEY-----"""
    ALIPAY_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
alipay_public_key_here
-----END PUBLIC KEY-----"""
    ALIPAY_GATEWAY = "https://openapi.alipay.com/gateway.do"
    ALIPAY_SANDBOX_GATEWAY = "https://openapi.alipaydev.com/gateway.do"
    
    # 微信支付配置
    WECHAT_APPID = "your_wechat_appid"
    WECHAT_MCH_ID = "your_merchant_id"
    WECHAT_API_KEY = "your_wechat_api_key"
    WECHAT_CERT_PATH = "apiclient_cert.pem"
    WECHAT_KEY_PATH = "apiclient_key.pem"
    WECHAT_NOTIFY_URL = "https://powerauto.ai/api/payment/wechat/notify"
    WECHAT_GATEWAY = "https://api.mch.weixin.qq.com"
    
    # Stripe配置
    STRIPE_PUBLIC_KEY = "pk_live_your_stripe_public_key"
    STRIPE_SECRET_KEY = "sk_live_your_stripe_secret_key"
    STRIPE_WEBHOOK_SECRET = "whsec_your_webhook_secret"
    STRIPE_ENDPOINT_SECRET = "your_endpoint_secret"

class AlipayPayment:
    """支付寶支付處理"""
    
    def __init__(self, config: PaymentConfig, sandbox: bool = True):
        self.config = config
        self.gateway = config.ALIPAY_SANDBOX_GATEWAY if sandbox else config.ALIPAY_GATEWAY
        self.app_id = config.ALIPAY_APP_ID
        self.private_key = config.ALIPAY_PRIVATE_KEY
        self.public_key = config.ALIPAY_PUBLIC_KEY
        
    async def create_payment(self, order_id: str, amount: float, subject: str, 
                           user_id: str, return_url: str = None) -> Dict[str, Any]:
        """創建支付寶支付訂單"""
        try:
            # 構建支付參數
            biz_content = {
                "out_trade_no": order_id,
                "total_amount": f"{amount:.2f}",
                "subject": subject,
                "product_code": "FAST_INSTANT_TRADE_PAY",
                "passback_params": user_id  # 透傳用戶ID
            }
            
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.page.pay",
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "notify_url": "https://powerauto.ai/api/payment/alipay/notify",
                "biz_content": json.dumps(biz_content, separators=(',', ':'))
            }
            
            if return_url:
                params["return_url"] = return_url
            
            # 生成簽名
            sign = self._generate_sign(params)
            params["sign"] = sign
            
            # 構建支付URL
            payment_url = f"{self.gateway}?{urlencode(params)}"
            
            logger.info(f"💰 支付寶支付訂單創建: {order_id} - {amount}元")
            
            return {
                "payment_method": "alipay",
                "order_id": order_id,
                "payment_url": payment_url,
                "amount": amount,
                "currency": "CNY",
                "status": "pending",
                "created_at": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ 支付寶支付創建失敗: {e}")
            raise
    
    def _generate_sign(self, params: Dict[str, str]) -> str:
        """生成支付寶簽名"""
        # 排序參數
        sorted_params = sorted(params.items())
        
        # 構建簽名字符串
        sign_string = "&".join([f"{k}={v}" for k, v in sorted_params if k != "sign"])
        
        # 這裡應該使用RSA私鑰簽名，簡化示例
        # 實際使用時需要引入 cryptography 庫
        import hashlib
        return hashlib.sha256(sign_string.encode()).hexdigest()
    
    async def verify_notify(self, notify_data: Dict[str, str]) -> bool:
        """驗證支付寶回調"""
        try:
            # 驗證簽名邏輯
            # 實際使用時需要用支付寶公鑰驗證簽名
            return True
        except Exception as e:
            logger.error(f"❌ 支付寶回調驗證失敗: {e}")
            return False

class WechatPayment:
    """微信支付處理"""
    
    def __init__(self, config: PaymentConfig):
        self.config = config
        self.appid = config.WECHAT_APPID
        self.mch_id = config.WECHAT_MCH_ID
        self.api_key = config.WECHAT_API_KEY
        self.gateway = config.WECHAT_GATEWAY
        
    async def create_payment(self, order_id: str, amount: float, subject: str, 
                           user_ip: str, user_id: str) -> Dict[str, Any]:
        """創建微信支付訂單"""
        try:
            # 構建支付參數
            params = {
                "appid": self.appid,
                "mch_id": self.mch_id,
                "nonce_str": self._generate_nonce_str(),
                "body": subject,
                "out_trade_no": order_id,
                "total_fee": str(int(amount * 100)),  # 轉換為分
                "spbill_create_ip": user_ip,
                "notify_url": self.config.WECHAT_NOTIFY_URL,
                "trade_type": "NATIVE",  # 掃碼支付
                "attach": user_id  # 透傳用戶ID
            }
            
            # 生成簽名
            params["sign"] = self._generate_sign(params)
            
            # 構建XML請求
            xml_data = self._dict_to_xml(params)
            
            # 發送請求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.gateway}/pay/unifiedorder",
                    content=xml_data,
                    headers={"Content-Type": "application/xml"}
                )
                
                result = self._xml_to_dict(response.text)
                
                if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                    logger.info(f"💰 微信支付訂單創建: {order_id} - {amount}元")
                    
                    return {
                        "payment_method": "wechat",
                        "order_id": order_id,
                        "code_url": result.get("code_url"),  # 二維碼URL
                        "prepay_id": result.get("prepay_id"),
                        "amount": amount,
                        "currency": "CNY",
                        "status": "pending",
                        "created_at": time.time()
                    }
                else:
                    raise Exception(f"微信支付創建失敗: {result.get('err_code_des', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"❌ 微信支付創建失敗: {e}")
            raise
    
    def _generate_nonce_str(self) -> str:
        """生成隨機字符串"""
        return str(uuid.uuid4()).replace("-", "")
    
    def _generate_sign(self, params: Dict[str, str]) -> str:
        """生成微信支付簽名"""
        # 排序參數
        sorted_params = sorted(params.items())
        
        # 構建簽名字符串
        sign_string = "&".join([f"{k}={v}" for k, v in sorted_params if k != "sign"])
        sign_string += f"&key={self.api_key}"
        
        # MD5簽名
        return hashlib.md5(sign_string.encode()).hexdigest().upper()
    
    def _dict_to_xml(self, params: Dict[str, str]) -> str:
        """字典轉XML"""
        xml_items = ["<xml>"]
        for k, v in params.items():
            xml_items.append(f"<{k}><![CDATA[{v}]]></{k}>")
        xml_items.append("</xml>")
        return "".join(xml_items)
    
    def _xml_to_dict(self, xml_str: str) -> Dict[str, str]:
        """XML轉字典"""
        result = {}
        root = ET.fromstring(xml_str)
        for child in root:
            result[child.tag] = child.text
        return result
    
    async def verify_notify(self, notify_data: Dict[str, str]) -> bool:
        """驗證微信支付回調"""
        try:
            # 提取簽名
            sign = notify_data.pop("sign", "")
            
            # 生成簽名
            expected_sign = self._generate_sign(notify_data)
            
            return sign == expected_sign
        except Exception as e:
            logger.error(f"❌ 微信支付回調驗證失敗: {e}")
            return False

class StripePayment:
    """Stripe支付處理"""
    
    def __init__(self, config: PaymentConfig):
        self.config = config
        self.secret_key = config.STRIPE_SECRET_KEY
        self.public_key = config.STRIPE_PUBLIC_KEY
        self.webhook_secret = config.STRIPE_WEBHOOK_SECRET
        
    async def create_payment(self, order_id: str, amount: float, currency: str,
                           user_email: str, user_id: str) -> Dict[str, Any]:
        """創建Stripe支付會話"""
        try:
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # 創建支付意圖
            payment_intent_data = {
                "amount": int(amount * 100),  # 轉換為最小貨幣單位
                "currency": currency.lower(),
                "metadata[order_id]": order_id,
                "metadata[user_id]": user_id,
                "receipt_email": user_email,
                "description": f"PowerAutomation積分購買 - 訂單{order_id}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.stripe.com/v1/payment_intents",
                    headers=headers,
                    data=payment_intent_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    logger.info(f"💰 Stripe支付訂單創建: {order_id} - {amount}{currency}")
                    
                    return {
                        "payment_method": "stripe",
                        "order_id": order_id,
                        "payment_intent_id": result["id"],
                        "client_secret": result["client_secret"],
                        "amount": amount,
                        "currency": currency,
                        "status": result["status"],
                        "created_at": time.time()
                    }
                else:
                    raise Exception(f"Stripe支付創建失敗: {response.text}")
            
        except Exception as e:
            logger.error(f"❌ Stripe支付創建失敗: {e}")
            raise
    
    async def create_checkout_session(self, order_id: str, amount: float, currency: str,
                                    user_email: str, user_id: str, points: int) -> Dict[str, Any]:
        """創建Stripe Checkout會話"""
        try:
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # 計算點數
            line_items = f"price_data[currency]={currency.lower()}&" \
                        f"price_data[product_data][name]=PowerAutomation積分&" \
                        f"price_data[product_data][description]={points}積分充值&" \
                        f"price_data[unit_amount]={int(amount * 100)}&" \
                        f"quantity=1"
            
            checkout_data = {
                "payment_method_types[]": "card",
                "line_items[0][price_data][currency]": currency.lower(),
                "line_items[0][price_data][product_data][name]": "PowerAutomation積分",
                "line_items[0][price_data][product_data][description]": f"{points}積分充值",
                "line_items[0][price_data][unit_amount]": int(amount * 100),
                "line_items[0][quantity]": "1",
                "mode": "payment",
                "success_url": f"https://powerauto.ai/payment/success?order_id={order_id}",
                "cancel_url": f"https://powerauto.ai/payment/cancel?order_id={order_id}",
                "customer_email": user_email,
                "metadata[order_id]": order_id,
                "metadata[user_id]": user_id,
                "metadata[points]": str(points)
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.stripe.com/v1/checkout/sessions",
                    headers=headers,
                    data=checkout_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    logger.info(f"💰 Stripe Checkout會話創建: {order_id}")
                    
                    return {
                        "payment_method": "stripe_checkout",
                        "order_id": order_id,
                        "session_id": result["id"],
                        "checkout_url": result["url"],
                        "amount": amount,
                        "currency": currency,
                        "status": "pending",
                        "created_at": time.time()
                    }
                else:
                    raise Exception(f"Stripe Checkout創建失敗: {response.text}")
            
        except Exception as e:
            logger.error(f"❌ Stripe Checkout創建失敗: {e}")
            raise
    
    async def verify_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """驗證Stripe Webhook"""
        try:
            import hmac
            import hashlib
            
            # 計算簽名
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # 比較簽名
            if not hmac.compare_digest(signature, f"sha256={expected_signature}"):
                raise Exception("Invalid signature")
            
            # 解析事件
            event = json.loads(payload.decode())
            
            return event
            
        except Exception as e:
            logger.error(f"❌ Stripe Webhook驗證失敗: {e}")
            raise

class PaymentManager:
    """統一支付管理器"""
    
    def __init__(self, config: PaymentConfig):
        self.config = config
        self.alipay = AlipayPayment(config)
        self.wechat = WechatPayment(config)
        self.stripe = StripePayment(config)
        
        # 支付訂單緩存
        self.pending_orders = {}
        
    async def create_payment(self, payment_method: str, order_id: str, amount: float,
                           user_info: Dict[str, Any], points: int, **kwargs) -> Dict[str, Any]:
        """創建支付訂單"""
        try:
            subject = f"PowerAutomation積分充值 - {points}積分"
            
            if payment_method == "alipay":
                result = await self.alipay.create_payment(
                    order_id=order_id,
                    amount=amount,
                    subject=subject,
                    user_id=user_info["user_id"],
                    return_url=kwargs.get("return_url")
                )
                
            elif payment_method == "wechat":
                result = await self.wechat.create_payment(
                    order_id=order_id,
                    amount=amount,
                    subject=subject,
                    user_ip=kwargs.get("user_ip", "127.0.0.1"),
                    user_id=user_info["user_id"]
                )
                
            elif payment_method == "stripe":
                result = await self.stripe.create_checkout_session(
                    order_id=order_id,
                    amount=amount,
                    currency=kwargs.get("currency", "USD"),
                    user_email=user_info["email"],
                    user_id=user_info["user_id"],
                    points=points
                )
                
            else:
                raise Exception(f"不支持的支付方式: {payment_method}")
            
            # 緩存訂單信息
            self.pending_orders[order_id] = {
                "user_id": user_info["user_id"],
                "points": points,
                "amount": amount,
                "payment_method": payment_method,
                "created_at": time.time(),
                "status": "pending"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 創建支付訂單失敗: {e}")
            raise
    
    async def handle_payment_notify(self, payment_method: str, notify_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理支付回調"""
        try:
            order_id = None
            payment_success = False
            
            if payment_method == "alipay":
                if await self.alipay.verify_notify(notify_data):
                    order_id = notify_data.get("out_trade_no")
                    payment_success = notify_data.get("trade_status") == "TRADE_SUCCESS"
                    
            elif payment_method == "wechat":
                if await self.wechat.verify_notify(notify_data):
                    order_id = notify_data.get("out_trade_no")
                    payment_success = notify_data.get("result_code") == "SUCCESS"
                    
            elif payment_method == "stripe":
                # Stripe webhook處理
                event_type = notify_data.get("type")
                if event_type == "checkout.session.completed":
                    session = notify_data["data"]["object"]
                    order_id = session["metadata"]["order_id"]
                    payment_success = session["payment_status"] == "paid"
            
            if order_id and payment_success:
                # 處理支付成功
                order_info = self.pending_orders.get(order_id)
                if order_info:
                    # 更新訂單狀態
                    self.pending_orders[order_id]["status"] = "paid"
                    
                    logger.info(f"✅ 支付成功: {order_id} - {payment_method}")
                    
                    return {
                        "success": True,
                        "order_id": order_id,
                        "user_id": order_info["user_id"],
                        "points": order_info["points"],
                        "amount": order_info["amount"],
                        "payment_method": payment_method
                    }
            
            return {"success": False, "error": "支付驗證失敗"}
            
        except Exception as e:
            logger.error(f"❌ 處理支付回調失敗: {e}")
            return {"success": False, "error": str(e)}
    
    def get_payment_methods(self) -> List[Dict[str, Any]]:
        """獲取可用支付方式"""
        return [
            {
                "method": "alipay",
                "name": "支付寶",
                "icon": "🎯",
                "description": "支持支付寶掃碼支付",
                "currencies": ["CNY"],
                "enabled": True
            },
            {
                "method": "wechat",
                "name": "微信支付",
                "icon": "💬",
                "description": "支持微信掃碼支付",
                "currencies": ["CNY"],
                "enabled": True
            },
            {
                "method": "stripe",
                "name": "信用卡",
                "icon": "💳",
                "description": "支持國際信用卡支付",
                "currencies": ["USD", "EUR", "CNY"],
                "enabled": True
            }
        ]

# 使用示例
async def main():
    """支付系統測試"""
    config = PaymentConfig()
    payment_manager = PaymentManager(config)
    
    # 創建支付寶支付
    user_info = {
        "user_id": "user_123",
        "email": "test@example.com"
    }
    
    order_id = f"order_{int(time.time())}"
    
    try:
        # 測試支付寶支付
        alipay_result = await payment_manager.create_payment(
            payment_method="alipay",
            order_id=order_id + "_alipay",
            amount=59.90,
            user_info=user_info,
            points=1000,
            return_url="https://powerauto.ai/payment/return"
        )
        
        print("支付寶支付創建成功:", alipay_result)
        
        # 測試Stripe支付
        stripe_result = await payment_manager.create_payment(
            payment_method="stripe",
            order_id=order_id + "_stripe",
            amount=9.99,
            user_info=user_info,
            points=1000,
            currency="USD"
        )
        
        print("Stripe支付創建成功:", stripe_result)
        
        # 獲取支付方式
        methods = payment_manager.get_payment_methods()
        print("可用支付方式:", methods)
        
    except Exception as e:
        print(f"支付測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())