#!/usr/bin/env python3
"""
PowerAuto.ai 完整支付系統
支持多種支付方式：Stripe、支付寶、微信支付
包含訂單管理、訂閱管理、發票生成等功能
"""

import os
import json
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# 模擬的 Stripe 集成
class MockStripe:
    @staticmethod
    def create_payment_intent(amount: int, currency: str = "cny", metadata: Dict = None):
        return {
            "id": f"pi_{uuid.uuid4().hex[:24]}",
            "client_secret": f"pi_{uuid.uuid4().hex[:24]}_secret",
            "amount": amount,
            "currency": currency,
            "status": "requires_payment_method",
            "metadata": metadata or {}
        }
    
    @staticmethod
    def create_subscription(customer_id: str, price_id: str, metadata: Dict = None):
        return {
            "id": f"sub_{uuid.uuid4().hex[:24]}",
            "customer": customer_id,
            "status": "active",
            "current_period_start": datetime.now().timestamp(),
            "current_period_end": (datetime.now() + timedelta(days=30)).timestamp(),
            "metadata": metadata or {}
        }

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class OrderStatus(Enum):
    CART = "cart"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PROCESSING = "processing"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PlanType(Enum):
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    TEAM = "team"
    ENTERPRISE = "enterprise"

@dataclass
class PaymentMethod:
    """支付方式"""
    method_id: str
    type: str  # "stripe", "alipay", "wechat"
    display_name: str
    is_enabled: bool
    config: Dict[str, Any]

@dataclass
class PricingPlan:
    """定價方案"""
    plan_id: str
    name: str
    plan_type: PlanType
    price_monthly: float
    price_yearly: float
    currency: str
    features: List[str]
    api_calls_limit: int
    team_members_limit: int
    support_level: str
    is_popular: bool = False

@dataclass
class Order:
    """訂單"""
    order_id: str
    customer_id: str
    customer_email: str
    customer_name: str
    plan_id: str
    billing_cycle: str  # "monthly" or "yearly"
    amount: float
    currency: str
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: str
    payment_intent_id: Optional[str]
    subscription_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]

@dataclass
class Customer:
    """客戶"""
    customer_id: str
    email: str
    name: str
    company: Optional[str]
    phone: Optional[str]
    stripe_customer_id: Optional[str]
    created_at: datetime
    metadata: Dict[str, Any]

class PaymentSystem:
    """支付系統核心"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 模擬數據庫
        self.orders: Dict[str, Order] = {}
        self.customers: Dict[str, Customer] = {}
        self.pricing_plans: Dict[str, PricingPlan] = {}
        
        # 支付方式配置
        self.payment_methods = {
            "stripe": PaymentMethod(
                method_id="stripe",
                type="stripe",
                display_name="信用卡/借記卡",
                is_enabled=True,
                config={
                    "public_key": "pk_test_...",
                    "secret_key": "sk_test_...",
                    "webhook_secret": "whsec_..."
                }
            ),
            "alipay": PaymentMethod(
                method_id="alipay",
                type="alipay",
                display_name="支付寶",
                is_enabled=True,
                config={
                    "app_id": "2021000000000000",
                    "private_key": "MII...",
                    "public_key": "MII...",
                    "gateway_url": "https://openapi.alipay.com/gateway.do"
                }
            ),
            "wechat": PaymentMethod(
                method_id="wechat",
                type="wechat", 
                display_name="微信支付",
                is_enabled=True,
                config={
                    "app_id": "wx1234567890123456",
                    "mch_id": "1234567890",
                    "api_key": "1234567890123456789012345678901234567890",
                    "cert_path": "/path/to/cert.pem"
                }
            )
        }
        
        # 初始化定價方案
        self._initialize_pricing_plans()
    
    def _initialize_pricing_plans(self):
        """初始化定價方案"""
        plans = [
            PricingPlan(
                plan_id="personal",
                name="個人版",
                plan_type=PlanType.PERSONAL,
                price_monthly=0.0,
                price_yearly=0.0,
                currency="CNY",
                features=[
                    "每月100次API調用",
                    "基礎代碼生成",
                    "Smart Intervention (有限)",
                    "社區支持",
                    "基礎模板庫"
                ],
                api_calls_limit=100,
                team_members_limit=1,
                support_level="community"
            ),
            PricingPlan(
                plan_id="professional",
                name="專業版",
                plan_type=PlanType.PROFESSIONAL,
                price_monthly=299.0,
                price_yearly=2990.0,  # 1個月免費
                currency="CNY",
                features=[
                    "每月10,000次API調用",
                    "完整代碼生成功能",
                    "Smart Intervention 無限制",
                    "K2模型成本優化",
                    "六大工作流自動化",
                    "優先技術支持",
                    "高級模板庫",
                    "GitHub集成"
                ],
                api_calls_limit=10000,
                team_members_limit=1,
                support_level="priority",
                is_popular=True
            ),
            PricingPlan(
                plan_id="team",
                name="團隊版",
                plan_type=PlanType.TEAM,
                price_monthly=999.0,
                price_yearly=9990.0,  # 2個月免費
                currency="CNY",
                features=[
                    "每月50,000次API調用",
                    "包含專業版所有功能",
                    "團隊協作工具",
                    "項目管理集成",
                    "進度跟踪和報告",
                    "多人實時協作",
                    "團隊分析儀表板",
                    "24/7 技術支持"
                ],
                api_calls_limit=50000,
                team_members_limit=20,
                support_level="24x7"
            ),
            PricingPlan(
                plan_id="enterprise",
                name="企業版",
                plan_type=PlanType.ENTERPRISE,
                price_monthly=0.0,  # 定制報價
                price_yearly=0.0,   # 定制報價
                currency="CNY",
                features=[
                    "無限API調用",
                    "包含團隊版所有功能",
                    "企業級安全和合規",
                    "SSO單點登錄",
                    "私有部署選項",
                    "定制集成服務",
                    "專屬客戶經理",
                    "SLA服務保證"
                ],
                api_calls_limit=-1,  # 無限
                team_members_limit=-1,  # 無限
                support_level="dedicated"
            )
        ]
        
        for plan in plans:
            self.pricing_plans[plan.plan_id] = plan
    
    def create_customer(self, email: str, name: str, company: str = None, 
                       phone: str = None, metadata: Dict = None) -> Customer:
        """創建客戶"""
        customer_id = f"cust_{uuid.uuid4().hex[:24]}"
        
        customer = Customer(
            customer_id=customer_id,
            email=email,
            name=name,
            company=company,
            phone=phone,
            stripe_customer_id=None,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.customers[customer_id] = customer
        self.logger.info(f"客戶已創建: {customer_id}")
        
        return customer
    
    def create_order(self, customer_id: str, plan_id: str, billing_cycle: str = "monthly",
                    payment_method: str = "stripe", metadata: Dict = None) -> Order:
        """創建訂單"""
        if customer_id not in self.customers:
            raise ValueError(f"客戶不存在: {customer_id}")
        
        if plan_id not in self.pricing_plans:
            raise ValueError(f"定價方案不存在: {plan_id}")
        
        customer = self.customers[customer_id]
        plan = self.pricing_plans[plan_id]
        
        # 計算金額
        if billing_cycle == "yearly":
            amount = plan.price_yearly
        else:
            amount = plan.price_monthly
        
        order_id = f"order_{uuid.uuid4().hex[:24]}"
        
        order = Order(
            order_id=order_id,
            customer_id=customer_id,
            customer_email=customer.email,
            customer_name=customer.name,
            plan_id=plan_id,
            billing_cycle=billing_cycle,
            amount=amount,
            currency=plan.currency,
            status=OrderStatus.PENDING_PAYMENT,
            payment_status=PaymentStatus.PENDING,
            payment_method=payment_method,
            payment_intent_id=None,
            subscription_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),  # 24小時內完成支付
            metadata=metadata or {}
        )
        
        self.orders[order_id] = order
        self.logger.info(f"訂單已創建: {order_id}")
        
        return order
    
    def create_payment_intent(self, order_id: str) -> Dict[str, Any]:
        """創建支付意圖"""
        if order_id not in self.orders:
            raise ValueError(f"訂單不存在: {order_id}")
        
        order = self.orders[order_id]
        
        if order.payment_method == "stripe":
            # 創建 Stripe 支付意圖
            payment_intent = MockStripe.create_payment_intent(
                amount=int(order.amount * 100),  # 轉換為分
                currency=order.currency.lower(),
                metadata={
                    "order_id": order_id,
                    "customer_id": order.customer_id,
                    "plan_id": order.plan_id
                }
            )
            
            # 更新訂單
            order.payment_intent_id = payment_intent["id"]
            order.payment_status = PaymentStatus.PROCESSING
            order.updated_at = datetime.now()
            
            return {
                "payment_intent": payment_intent,
                "client_secret": payment_intent["client_secret"],
                "amount": order.amount,
                "currency": order.currency
            }
        
        elif order.payment_method == "alipay":
            # 創建支付寶支付
            return self._create_alipay_payment(order)
        
        elif order.payment_method == "wechat":
            # 創建微信支付
            return self._create_wechat_payment(order)
        
        else:
            raise ValueError(f"不支持的支付方式: {order.payment_method}")
    
    def _create_alipay_payment(self, order: Order) -> Dict[str, Any]:
        """創建支付寶支付"""
        # 模擬支付寶 API 調用
        alipay_order_id = f"alipay_{uuid.uuid4().hex[:24]}"
        
        return {
            "trade_no": alipay_order_id,
            "qr_code": f"https://qr.alipay.com/pay?id={alipay_order_id}",
            "app_pay_url": f"alipays://platformapi/startapp?appId=pay&orderStr={alipay_order_id}",
            "amount": order.amount,
            "currency": order.currency,
            "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
    
    def _create_wechat_payment(self, order: Order) -> Dict[str, Any]:
        """創建微信支付"""
        # 模擬微信支付 API 調用
        wechat_order_id = f"wx_{uuid.uuid4().hex[:24]}"
        
        return {
            "prepay_id": wechat_order_id,
            "qr_code": f"weixin://wxpay/bizpayurl?pr={wechat_order_id}",
            "app_pay_params": {
                "appid": self.payment_methods["wechat"].config["app_id"],
                "partnerid": self.payment_methods["wechat"].config["mch_id"],
                "prepayid": wechat_order_id,
                "package": "Sign=WXPay",
                "noncestr": uuid.uuid4().hex[:32],
                "timestamp": str(int(datetime.now().timestamp()))
            },
            "amount": order.amount,
            "currency": order.currency,
            "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
    
    def confirm_payment(self, order_id: str, payment_result: Dict[str, Any]) -> bool:
        """確認支付結果"""
        if order_id not in self.orders:
            raise ValueError(f"訂單不存在: {order_id}")
        
        order = self.orders[order_id]
        
        # 驗證支付結果
        if self._verify_payment_result(order, payment_result):
            order.payment_status = PaymentStatus.COMPLETED
            order.status = OrderStatus.PAID
            order.updated_at = datetime.now()
            
            # 如果是訂閱服務，創建訂閱
            if order.plan_id != "personal":
                subscription = self._create_subscription(order)
                order.subscription_id = subscription["id"]
                order.status = OrderStatus.ACTIVE
            
            self.logger.info(f"支付已確認: {order_id}")
            return True
        
        else:
            order.payment_status = PaymentStatus.FAILED
            order.updated_at = datetime.now()
            self.logger.warning(f"支付驗證失敗: {order_id}")
            return False
    
    def _verify_payment_result(self, order: Order, payment_result: Dict[str, Any]) -> bool:
        """驗證支付結果"""
        # 這裡應該實現具體的支付驗證邏輯
        # 對於演示，我們簡化處理
        return payment_result.get("status") == "succeeded"
    
    def _create_subscription(self, order: Order) -> Dict[str, Any]:
        """創建訂閱"""
        if order.payment_method == "stripe":
            return MockStripe.create_subscription(
                customer_id=order.customer_id,
                price_id=f"price_{order.plan_id}_{order.billing_cycle}",
                metadata={
                    "order_id": order.order_id,
                    "plan_id": order.plan_id
                }
            )
        else:
            # 對於其他支付方式，創建內部訂閱記錄
            return {
                "id": f"sub_{uuid.uuid4().hex[:24]}",
                "customer": order.customer_id,
                "status": "active",
                "current_period_start": datetime.now().timestamp(),
                "current_period_end": (datetime.now() + timedelta(days=30 if order.billing_cycle == "monthly" else 365)).timestamp()
            }
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """獲取訂單"""
        return self.orders.get(order_id)
    
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        """獲取客戶的所有訂單"""
        return [order for order in self.orders.values() if order.customer_id == customer_id]
    
    def get_pricing_plans(self) -> List[PricingPlan]:
        """獲取所有定價方案"""
        return list(self.pricing_plans.values())
    
    def get_payment_methods(self) -> List[PaymentMethod]:
        """獲取可用的支付方式"""
        return [method for method in self.payment_methods.values() if method.is_enabled]
    
    def request_enterprise_quote(self, company: str, email: str, phone: str, 
                                team_size: str, requirements: str = "") -> Dict[str, Any]:
        """企業版詢價"""
        quote_id = f"quote_{uuid.uuid4().hex[:24]}"
        
        quote_request = {
            "quote_id": quote_id,
            "company": company,
            "email": email,
            "phone": phone,
            "team_size": team_size,
            "requirements": requirements,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "estimated_response_time": "24小時內"
        }
        
        # 這裡可以發送通知給銷售團隊
        self.logger.info(f"企業詢價請求已提交: {quote_id}")
        
        return quote_request
    
    def generate_invoice(self, order_id: str) -> Dict[str, Any]:
        """生成發票"""
        if order_id not in self.orders:
            raise ValueError(f"訂單不存在: {order_id}")
        
        order = self.orders[order_id]
        customer = self.customers[order.customer_id]
        plan = self.pricing_plans[order.plan_id]
        
        invoice = {
            "invoice_id": f"inv_{uuid.uuid4().hex[:24]}",
            "order_id": order_id,
            "customer_name": customer.name,
            "customer_email": customer.email,
            "company": customer.company or "個人",
            "plan_name": plan.name,
            "billing_cycle": order.billing_cycle,
            "amount": order.amount,
            "currency": order.currency,
            "issue_date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": "paid" if order.payment_status == PaymentStatus.COMPLETED else "pending",
            "items": [
                {
                    "description": f"{plan.name} - {order.billing_cycle}訂閱",
                    "quantity": 1,
                    "unit_price": order.amount,
                    "total": order.amount
                }
            ],
            "subtotal": order.amount,
            "tax": 0.0,  # 根據地區調整
            "total": order.amount
        }
        
        return invoice

# 全局支付系統實例
payment_system = PaymentSystem()

def demo_payment_system():
    """支付系統演示"""
    print("💳 PowerAuto.ai 支付系統演示")
    print("=" * 50)
    
    # 1. 創建客戶
    print("\n1. 創建客戶")
    customer = payment_system.create_customer(
        email="demo@example.com",
        name="演示用戶",
        company="演示公司",
        phone="13800138000"
    )
    print(f"客戶已創建: {customer.customer_id}")
    
    # 2. 獲取定價方案
    print("\n2. 可用定價方案")
    plans = payment_system.get_pricing_plans()
    for plan in plans:
        print(f"  - {plan.name}: ¥{plan.price_monthly}/月, ¥{plan.price_yearly}/年")
    
    # 3. 創建訂單
    print("\n3. 創建專業版訂單")
    order = payment_system.create_order(
        customer_id=customer.customer_id,
        plan_id="professional",
        billing_cycle="monthly",
        payment_method="stripe"
    )
    print(f"訂單已創建: {order.order_id}, 金額: ¥{order.amount}")
    
    # 4. 創建支付意圖
    print("\n4. 創建支付意圖")
    payment_intent = payment_system.create_payment_intent(order.order_id)
    print(f"支付意圖已創建: {payment_intent.get('payment_intent', {}).get('id', 'N/A')}")
    
    # 5. 模擬支付成功
    print("\n5. 模擬支付確認")
    payment_result = {"status": "succeeded", "payment_method": "card"}
    success = payment_system.confirm_payment(order.order_id, payment_result)
    print(f"支付結果: {'成功' if success else '失敗'}")
    
    # 6. 生成發票
    print("\n6. 生成發票")
    invoice = payment_system.generate_invoice(order.order_id)
    print(f"發票已生成: {invoice['invoice_id']}")
    
    # 7. 企業詢價
    print("\n7. 企業版詢價")
    quote = payment_system.request_enterprise_quote(
        company="大型企業",
        email="enterprise@example.com",
        phone="400-888-0123",
        team_size="100+"
    )
    print(f"詢價請求已提交: {quote['quote_id']}")
    
    return {
        "customer_created": True,
        "order_created": True,
        "payment_processed": success,
        "invoice_generated": True,
        "enterprise_quote_requested": True
    }

if __name__ == "__main__":
    result = demo_payment_system()
    print(f"\n🎉 支付系統演示完成！")