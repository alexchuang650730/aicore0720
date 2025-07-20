#!/usr/bin/env python3
"""
集成會員積分登錄支付系統到三權限系統
統一認證體系：使用者/開發者/管理者 + 會員積分 + 支付系統
"""

import asyncio
import json
import time
import hashlib
import secrets
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import sqlite3

# 導入基礎認證系統
from .three_tier_auth import (
    auth_system, UserRole, User, AuthSession, 
    ThreeTierAuthSystem, AuthMiddleware
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MembershipPlan(Enum):
    """會員計劃"""
    FREE = "free"               # 免費版
    PERSONAL = "personal"       # 個人版 99元/月
    PROFESSIONAL = "professional"  # 專業版 599元/月
    TEAM = "team"              # 團隊版 599元/月 (5人)
    ENTERPRISE = "enterprise"   # 企業版 999元/月

class PaymentMethod(Enum):
    """支付方式"""
    ALIPAY = "alipay"          # 支付寶
    WECHAT = "wechat"          # 微信支付
    STRIPE = "stripe"          # Stripe信用卡

class PointTransactionType(Enum):
    """積分交易類型"""
    EARN = "earn"              # 獲得積分
    SPEND = "spend"            # 消費積分
    BONUS = "bonus"            # 獎勵積分
    PENALTY = "penalty"        # 懲罰扣分

@dataclass
class MembershipInfo:
    """會員信息"""
    user_id: str
    plan: MembershipPlan
    start_date: datetime
    end_date: datetime
    is_active: bool
    auto_renewal: bool
    points_balance: int
    k2_usage_quota: int        # K2使用配額
    k2_used_this_month: int    # 本月已使用K2次數

@dataclass
class PointTransaction:
    """積分交易記錄"""
    transaction_id: str
    user_id: str
    transaction_type: PointTransactionType
    points: int
    description: str
    created_at: datetime
    reference_id: Optional[str] = None

@dataclass
class PaymentRecord:
    """支付記錄"""
    payment_id: str
    user_id: str
    amount: float
    currency: str
    payment_method: PaymentMethod
    status: str                # pending/completed/failed/refunded
    plan: MembershipPlan
    created_at: datetime
    completed_at: Optional[datetime] = None
    stripe_session_id: Optional[str] = None
    alipay_trade_no: Optional[str] = None
    wechat_prepay_id: Optional[str] = None

class IntegratedMemberAuthSystem(ThreeTierAuthSystem):
    """集成會員認證系統"""
    
    def __init__(self):
        super().__init__()
        
        # 會員數據
        self.memberships: Dict[str, MembershipInfo] = {}
        self.point_transactions: List[PointTransaction] = []
        self.payment_records: List[PaymentRecord] = []
        
        # 會員計劃配置
        self.plan_configs = {
            MembershipPlan.FREE: {
                "price": 0,
                "k2_quota": 100,           # 每月100次K2調用
                "features": ["basic_tools", "limited_support"]
            },
            MembershipPlan.PERSONAL: {
                "price": 99,
                "k2_quota": 1000,          # 每月1000次K2調用
                "features": ["all_tools", "email_support", "basic_analytics"]
            },
            MembershipPlan.PROFESSIONAL: {
                "price": 599,
                "k2_quota": 10000,         # 每月10000次K2調用
                "features": ["all_tools", "priority_support", "advanced_analytics", "api_access"]
            },
            MembershipPlan.TEAM: {
                "price": 599,
                "k2_quota": 15000,         # 每月15000次K2調用 (5人共享)
                "features": ["all_tools", "team_collaboration", "priority_support", "admin_dashboard"]
            },
            MembershipPlan.ENTERPRISE: {
                "price": 999,
                "k2_quota": 50000,         # 每月50000次K2調用
                "features": ["all_tools", "dedicated_support", "custom_integration", "sla_guarantee"]
            }
        }
        
        # 初始化數據庫
        self._init_database()
        
        # 創建演示數據
        self._create_demo_members()
        
    def _init_database(self):
        """初始化會員數據庫"""
        db_path = Path("data/member_auth_system.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 會員信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memberships (
                user_id TEXT PRIMARY KEY,
                plan TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                is_active BOOLEAN NOT NULL,
                auto_renewal BOOLEAN NOT NULL,
                points_balance INTEGER NOT NULL DEFAULT 0,
                k2_usage_quota INTEGER NOT NULL,
                k2_used_this_month INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 積分交易表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS point_transactions (
                transaction_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                points INTEGER NOT NULL,
                description TEXT NOT NULL,
                reference_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES memberships (user_id)
            )
        ''')
        
        # 支付記錄表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_records (
                payment_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                status TEXT NOT NULL,
                plan TEXT NOT NULL,
                stripe_session_id TEXT,
                alipay_trade_no TEXT,
                wechat_prepay_id TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES memberships (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("會員數據庫初始化完成")
        
    def _create_demo_members(self):
        """創建演示會員數據"""
        # 為現有用戶創建會員信息
        demo_memberships = [
            ("admin_001", MembershipPlan.ENTERPRISE, 5000),
            ("user_001", MembershipPlan.PERSONAL, 1200),
            ("dev_001", MembershipPlan.PROFESSIONAL, 2500)
        ]
        
        for user_id, plan, points in demo_memberships:
            if user_id in self.users:
                self._create_membership(user_id, plan, points)
                
    def _create_membership(self, user_id: str, plan: MembershipPlan, initial_points: int = 0):
        """創建會員資格"""
        now = datetime.now()
        
        membership = MembershipInfo(
            user_id=user_id,
            plan=plan,
            start_date=now,
            end_date=now + timedelta(days=30),  # 30天有效期
            is_active=True,
            auto_renewal=True,
            points_balance=initial_points,
            k2_usage_quota=self.plan_configs[plan]["k2_quota"],
            k2_used_this_month=0
        )
        
        self.memberships[user_id] = membership
        
        # 添加初始積分記錄
        if initial_points > 0:
            self._add_point_transaction(
                user_id, PointTransactionType.BONUS, 
                initial_points, "新用戶註冊獎勵"
            )
            
        logger.info(f"創建會員資格: {user_id} - {plan.value}")
        
    def _add_point_transaction(self, user_id: str, transaction_type: PointTransactionType,
                             points: int, description: str, reference_id: str = None):
        """添加積分交易記錄"""
        transaction = PointTransaction(
            transaction_id=f"pt_{int(time.time() * 1000)}",
            user_id=user_id,
            transaction_type=transaction_type,
            points=points,
            description=description,
            created_at=datetime.now(),
            reference_id=reference_id
        )
        
        self.point_transactions.append(transaction)
        
        # 更新用戶積分餘額
        if user_id in self.memberships:
            if transaction_type in [PointTransactionType.EARN, PointTransactionType.BONUS]:
                self.memberships[user_id].points_balance += points
            else:  # SPEND, PENALTY
                self.memberships[user_id].points_balance -= points
                
        logger.info(f"積分交易: {user_id} {transaction_type.value} {points}分")
        
    async def register_member(self, username: str, email: str, plan: MembershipPlan = MembershipPlan.FREE) -> Dict[str, Any]:
        """會員註冊"""
        # 先創建基礎用戶
        role = UserRole.USER if plan == MembershipPlan.FREE else UserRole.DEVELOPER
        user = await self.register_user(username, email, role)
        
        # 創建會員資格
        initial_points = 500 if plan != MembershipPlan.FREE else 100
        self._create_membership(user.user_id, plan, initial_points)
        
        return {
            "user_id": user.user_id,
            "username": username,
            "plan": plan.value,
            "initial_points": initial_points,
            "success": True
        }
        
    async def authenticate_member(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """會員認證登錄"""
        # 基礎認證
        session = await self.authenticate(username, password)
        if not session:
            return None
            
        # 獲取會員信息
        membership = self.memberships.get(session.user_id)
        if not membership:
            # 為沒有會員資格的用戶創建免費會員
            self._create_membership(session.user_id, MembershipPlan.FREE)
            membership = self.memberships[session.user_id]
            
        user_info = self.get_user_info(session.session_id)
        
        return {
            "session_id": session.session_id,
            "user_info": user_info,
            "membership": {
                "plan": membership.plan.value,
                "points_balance": membership.points_balance,
                "k2_quota": membership.k2_usage_quota,
                "k2_used": membership.k2_used_this_month,
                "k2_remaining": membership.k2_usage_quota - membership.k2_used_this_month,
                "expires_at": membership.end_date.isoformat(),
                "is_active": membership.is_active
            }
        }
        
    async def create_payment(self, session_id: str, plan: MembershipPlan, 
                           payment_method: PaymentMethod) -> Dict[str, Any]:
        """創建支付訂單"""
        session = await self.verify_session(session_id)
        if not session:
            return {"success": False, "error": "會話無效"}
            
        plan_config = self.plan_configs[plan]
        payment_id = f"pay_{int(time.time() * 1000)}"
        
        payment = PaymentRecord(
            payment_id=payment_id,
            user_id=session.user_id,
            amount=plan_config["price"],
            currency="CNY",
            payment_method=payment_method,
            status="pending",
            plan=plan,
            created_at=datetime.now()
        )
        
        self.payment_records.append(payment)
        
        # 模擬支付URL生成
        payment_urls = {
            PaymentMethod.ALIPAY: f"https://openapi.alipay.com/gateway.do?trade_no={payment_id}",
            PaymentMethod.WECHAT: f"weixin://wxpay/bizpayurl?trade_no={payment_id}",
            PaymentMethod.STRIPE: f"https://checkout.stripe.com/pay/{payment_id}"
        }
        
        return {
            "success": True,
            "payment_id": payment_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "payment_url": payment_urls[payment_method],
            "expires_in": 1800  # 30分鐘過期
        }
        
    async def complete_payment(self, payment_id: str) -> Dict[str, Any]:
        """完成支付 (模擬支付成功)"""
        payment = None
        for p in self.payment_records:
            if p.payment_id == payment_id:
                payment = p
                break
                
        if not payment:
            return {"success": False, "error": "支付記錄不存在"}
            
        if payment.status != "pending":
            return {"success": False, "error": "支付狀態異常"}
            
        # 更新支付狀態
        payment.status = "completed"
        payment.completed_at = datetime.now()
        
        # 升級會員資格
        if payment.user_id in self.memberships:
            membership = self.memberships[payment.user_id]
            membership.plan = payment.plan
            membership.k2_usage_quota = self.plan_configs[payment.plan]["k2_quota"]
            membership.end_date = datetime.now() + timedelta(days=30)
            membership.is_active = True
            
            # 獎勵積分
            bonus_points = int(payment.amount * 10)  # 1元=10積分
            self._add_point_transaction(
                payment.user_id, PointTransactionType.BONUS,
                bonus_points, f"購買{payment.plan.value}計劃獎勵", payment_id
            )
            
        logger.info(f"支付完成: {payment_id} - {payment.plan.value}")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "plan": payment.plan.value,
            "new_quota": self.plan_configs[payment.plan]["k2_quota"]
        }
        
    async def use_k2_service(self, session_id: str, cost_estimate: float = 0.02) -> Dict[str, Any]:
        """使用K2服務 (扣費/配額)"""
        session = await self.verify_session(session_id)
        if not session:
            return {"success": False, "error": "會話無效"}
            
        membership = self.memberships.get(session.user_id)
        if not membership or not membership.is_active:
            return {"success": False, "error": "會員資格無效"}
            
        # 檢查K2配額
        if membership.k2_used_this_month >= membership.k2_usage_quota:
            return {"success": False, "error": "K2配額已用完，請升級計劃"}
            
        # 扣除配額
        membership.k2_used_this_month += 1
        
        # 計算積分消耗 (成本轉換為積分)
        points_cost = max(1, int(cost_estimate * 100))  # 0.02元 = 2積分
        
        if membership.points_balance >= points_cost:
            self._add_point_transaction(
                session.user_id, PointTransactionType.SPEND,
                points_cost, f"K2服務使用 (預估成本: {cost_estimate}元)"
            )
        
        return {
            "success": True,
            "k2_remaining": membership.k2_usage_quota - membership.k2_used_this_month,
            "points_cost": points_cost,
            "points_remaining": membership.points_balance,
            "estimated_value": cost_estimate * 4  # 2元成本產生8元價值
        }
        
    def get_member_dashboard(self, session_id: str) -> Optional[Dict[str, Any]]:
        """獲取會員儀表板數據"""
        session = self.sessions.get(session_id)
        if not session:
            return None
            
        membership = self.memberships.get(session.user_id)
        if not membership:
            return None
            
        # 計算本月積分收支
        user_transactions = [t for t in self.point_transactions if t.user_id == session.user_id]
        monthly_earn = sum(t.points for t in user_transactions 
                          if t.transaction_type in [PointTransactionType.EARN, PointTransactionType.BONUS]
                          and t.created_at.month == datetime.now().month)
        monthly_spend = sum(t.points for t in user_transactions
                           if t.transaction_type in [PointTransactionType.SPEND, PointTransactionType.PENALTY]
                           and t.created_at.month == datetime.now().month)
        
        return {
            "membership": {
                "plan": membership.plan.value,
                "expires_at": membership.end_date.isoformat(),
                "is_active": membership.is_active,
                "auto_renewal": membership.auto_renewal
            },
            "points": {
                "balance": membership.points_balance,
                "monthly_earned": monthly_earn,
                "monthly_spent": monthly_spend
            },
            "k2_usage": {
                "quota": membership.k2_usage_quota,
                "used": membership.k2_used_this_month,
                "remaining": membership.k2_usage_quota - membership.k2_used_this_month,
                "usage_rate": (membership.k2_used_this_month / membership.k2_usage_quota) * 100
            },
            "recent_transactions": [
                {
                    "type": t.transaction_type.value,
                    "points": t.points,
                    "description": t.description,
                    "date": t.created_at.isoformat()
                }
                for t in sorted(user_transactions, key=lambda x: x.created_at, reverse=True)[:5]
            ]
        }

# 全局集成認證系統實例
integrated_auth = IntegratedMemberAuthSystem()

# 演示功能
async def demo_integrated_member_auth():
    """集成會員認證系統演示"""
    print("💳 PowerAutomation 集成會員認證系統演示")
    print("=" * 70)
    
    # 1. 會員註冊演示
    print("\n1. 會員註冊演示")
    member1 = await integrated_auth.register_member("alice_vip", "alice@vip.com", MembershipPlan.PROFESSIONAL)
    member2 = await integrated_auth.register_member("bob_team", "bob@team.com", MembershipPlan.TEAM)
    print(f"註冊專業版會員: {member1['username']} (初始積分: {member1['initial_points']})")
    print(f"註冊團隊版會員: {member2['username']} (初始積分: {member2['initial_points']})")
    
    # 2. 會員登錄演示
    print("\n2. 會員登錄演示")
    auth_result1 = await integrated_auth.authenticate_member("alice_vip", "password")
    auth_result2 = await integrated_auth.authenticate_member("bob_team", "password")
    
    session1 = auth_result1["session_id"]
    session2 = auth_result2["session_id"]
    
    print(f"Alice (專業版): 積分 {auth_result1['membership']['points_balance']}, K2配額 {auth_result1['membership']['k2_quota']}")
    print(f"Bob (團隊版): 積分 {auth_result2['membership']['points_balance']}, K2配額 {auth_result2['membership']['k2_quota']}")
    
    # 3. 支付系統演示
    print("\n3. 支付系統演示")
    
    # Alice升級到企業版
    payment_order = await integrated_auth.create_payment(session1, MembershipPlan.ENTERPRISE, PaymentMethod.ALIPAY)
    print(f"創建支付訂單: {payment_order['payment_id']} - {payment_order['amount']}元")
    
    # 模擬支付完成
    payment_result = await integrated_auth.complete_payment(payment_order['payment_id'])
    print(f"支付完成: 升級到 {payment_result['plan']}, 新配額 {payment_result['new_quota']}")
    
    # 4. K2服務使用演示
    print("\n4. K2服務使用演示")
    
    # Alice使用K2服務
    for i in range(3):
        k2_result = await integrated_auth.use_k2_service(session1, 0.02)
        print(f"K2調用 #{i+1}: 剩餘配額 {k2_result['k2_remaining']}, 積分扣除 {k2_result['points_cost']}")
    
    # Bob使用K2服務
    k2_result = await integrated_auth.use_k2_service(session2, 0.05)
    print(f"Bob K2調用: 剩餘配額 {k2_result['k2_remaining']}, 預估價值 {k2_result['estimated_value']}元")
    
    # 5. 會員儀表板演示
    print("\n5. 會員儀表板演示")
    
    alice_dashboard = integrated_auth.get_member_dashboard(session1)
    bob_dashboard = integrated_auth.get_member_dashboard(session2)
    
    print(f"\nAlice 儀表板:")
    print(f"- 會員計劃: {alice_dashboard['membership']['plan']}")
    print(f"- 積分餘額: {alice_dashboard['points']['balance']}")
    print(f"- K2使用率: {alice_dashboard['k2_usage']['usage_rate']:.1f}%")
    print(f"- 最近交易: {len(alice_dashboard['recent_transactions'])}筆")
    
    print(f"\nBob 儀表板:")
    print(f"- 會員計劃: {bob_dashboard['membership']['plan']}")
    print(f"- 積分餘額: {bob_dashboard['points']['balance']}")
    print(f"- K2使用率: {bob_dashboard['k2_usage']['usage_rate']:.1f}%")
    
    # 6. 權限集成演示
    print("\n6. 權限集成演示")
    
    # 檢查不同會員的功能權限
    features = [
        ("基礎ClaudeEditor", "use_claudeeditor"),
        ("K2模型訪問", "access_k2"),
        ("API調用", "access_api"),
        ("高級分析", "view_metrics"),
        ("用戶管理", "manage_users")
    ]
    
    print(f"{'功能':<15} {'Alice(企業版)':<12} {'Bob(團隊版)':<12}")
    print("-" * 45)
    
    for feature_name, permission in features:
        alice_has = await integrated_auth.has_permission(session1, permission)
        bob_has = await integrated_auth.has_permission(session2, permission)
        
        alice_status = "✅" if alice_has else "❌"
        bob_status = "✅" if bob_has else "❌"
        
        print(f"{feature_name:<15} {alice_status:<12} {bob_status:<12}")
    
    return {
        "members_created": 2,
        "payments_processed": 1,
        "k2_calls_made": 4,
        "integration_success": True
    }

if __name__ == "__main__":
    result = asyncio.run(demo_integrated_member_auth())
    print(f"\n🎉 集成會員認證系統演示完成！")