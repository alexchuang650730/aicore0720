#!/usr/bin/env python3
"""
PowerAutomation 會員積分系統
支持支付寶、微信、Stripe支付
成本優化的K2平台部署
"""

import asyncio
import hashlib
import jwt
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from decimal import Decimal
import sqlite3
import json
import logging
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import requests
import stripe
from alipay import AliPay
import hashlib
import hmac
import xml.etree.ElementTree as ET

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 支付配置
PAYMENT_CONFIG = {
    "alipay": {
        "app_id": "your_alipay_app_id",
        "private_key_path": "keys/alipay_private_key.pem",
        "alipay_public_key_path": "keys/alipay_public_key.pem",
        "sign_type": "RSA2",
        "debug": False,
        "sandbox": False,
    },
    "wechat": {
        "app_id": "your_wechat_app_id",
        "mch_id": "your_wechat_mch_id",
        "api_key": "your_wechat_api_key",
        "cert_path": "keys/wechat_cert.pem",
        "key_path": "keys/wechat_key.pem",
        "sandbox": False,
    },
    "stripe": {
        "publishable_key": "pk_test_your_stripe_publishable_key",
        "secret_key": "sk_test_your_stripe_secret_key",
        "webhook_secret": "whsec_your_webhook_secret",
        "sandbox": True,
    }
}

# 會員計劃配置
MEMBERSHIP_PLANS = {
    "free": {
        "name": "免費版",
        "price": 0,
        "currency": "CNY",
        "duration": 30,  # 天
        "features": {
            "ai_calls_per_day": 10,
            "storage_gb": 1,
            "projects": 3,
            "workflows": 5,
            "team_members": 1,
            "support": "community",
            "k2_calls_per_day": 5,
            "claude_calls_per_day": 5,
        }
    },
    "pro": {
        "name": "專業版",
        "price": 599,
        "currency": "CNY",
        "duration": 30,
        "features": {
            "ai_calls_per_day": 1000,
            "storage_gb": 100,
            "projects": 50,
            "workflows": 100,
            "team_members": 1,
            "support": "email",
            "k2_calls_per_day": 500,
            "claude_calls_per_day": 500,
            "advanced_features": True,
        }
    },
    "team": {
        "name": "團隊版",
        "price": 599,  # 每人
        "currency": "CNY", 
        "duration": 30,
        "max_members": 5,
        "features": {
            "ai_calls_per_day": 5000,
            "storage_gb": 500,
            "projects": 200,
            "workflows": 500,
            "team_members": 5,
            "support": "priority",
            "k2_calls_per_day": 2500,
            "claude_calls_per_day": 2500,
            "team_collaboration": True,
            "advanced_features": True,
        }
    },
    "enterprise": {
        "name": "企業版",
        "price": 999,
        "currency": "CNY",
        "duration": 30,
        "features": {
            "ai_calls_per_day": -1,  # 無限制
            "storage_gb": -1,  # 無限制
            "projects": -1,  # 無限制
            "workflows": -1,  # 無限制
            "team_members": -1,  # 無限制
            "support": "dedicated",
            "k2_calls_per_day": -1,  # 無限制
            "claude_calls_per_day": -1,  # 無限制
            "team_collaboration": True,
            "advanced_features": True,
            "private_cloud": True,
            "custom_integration": True,
            "sla": True,
        }
    }
}

# K2成本優化配置
K2_COST_CONFIG = {
    "input_cost_per_token": 0.000002,  # 2元人民幣輸入成本
    "target_output_value": 8.0,  # 8元人民幣輸出價值
    "optimization_ratio": 4.0,  # 1:4的成本效益比
    "batch_size": 100,
    "cache_ttl": 3600,  # 1小時緩存
    "compression_enabled": True,
    "model_size": "efficient",
    "response_optimization": True,
}

# 數據模型
@dataclass
class User:
    id: str
    username: str
    email: str
    password_hash: str
    points: int = 0
    membership_tier: str = "free"
    subscription_expires: Optional[datetime] = None
    created_at: datetime = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    profile_data: Dict = None

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SubscriptionCreate(BaseModel):
    plan_name: str
    payment_method: str
    auto_renew: bool = True

class PaymentRequest(BaseModel):
    plan_name: str
    payment_method: str  # alipay, wechat, stripe
    return_url: str
    notify_url: str

class PointsTransaction(BaseModel):
    points: int
    transaction_type: str  # earn, spend, bonus, refund
    description: str

# 會員系統服務
class MemberService:
    def __init__(self, db_path: str = "members.db"):
        self.db_path = db_path
        self.init_database()
        self.init_payment_gateways()
        
    def init_database(self):
        """初始化數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用戶表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                membership_tier TEXT DEFAULT 'free',
                subscription_expires REAL,
                created_at REAL,
                last_login REAL,
                is_active BOOLEAN DEFAULT 1,
                profile_data TEXT DEFAULT '{}'
            )
        ''')
        
        # 積分交易表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS point_transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                points INTEGER,
                transaction_type TEXT,
                description TEXT,
                created_at REAL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 訂閱表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                plan_name TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'CNY',
                status TEXT DEFAULT 'active',
                starts_at REAL,
                expires_at REAL,
                auto_renew BOOLEAN DEFAULT 1,
                payment_method TEXT,
                payment_id TEXT,
                created_at REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 支付記錄表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                subscription_id TEXT,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'CNY',
                payment_method TEXT,
                payment_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at REAL,
                completed_at REAL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
            )
        ''')
        
        # K2使用記錄表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS k2_usage (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                input_cost REAL,
                output_value REAL,
                efficiency_ratio REAL,
                created_at REAL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def init_payment_gateways(self):
        """初始化支付網關"""
        # 支付寶
        self.alipay = AliPay(
            appid=PAYMENT_CONFIG["alipay"]["app_id"],
            app_notify_url=None,
            app_private_key_path=PAYMENT_CONFIG["alipay"]["private_key_path"],
            alipay_public_key_path=PAYMENT_CONFIG["alipay"]["alipay_public_key_path"],
            sign_type=PAYMENT_CONFIG["alipay"]["sign_type"],
            debug=PAYMENT_CONFIG["alipay"]["debug"],
        )
        
        # Stripe
        stripe.api_key = PAYMENT_CONFIG["stripe"]["secret_key"]
        
    # 用戶管理
    async def register_user(self, user_data: UserRegister) -> Dict:
        """註冊用戶"""
        try:
            # 檢查用戶是否存在
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="用戶已存在")
            
            # 創建用戶
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(user_data.password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, user_data.username, user_data.email, password_hash, time.time()))
            
            conn.commit()
            conn.close()
            
            # 贈送新用戶積分
            await self.add_points(user_id, 100, "register", "新用戶註冊贈送")
            
            return {"user_id": user_id, "message": "註冊成功"}
            
        except Exception as e:
            logger.error(f"註冊用戶失敗: {e}")
            raise HTTPException(status_code=500, detail="註冊失敗")
    
    async def login_user(self, login_data: UserLogin) -> Dict:
        """用戶登錄"""
        try:
            user = await self.get_user_by_email(login_data.email)
            if not user or not self.verify_password(login_data.password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="用戶名或密碼錯誤")
            
            if not user["is_active"]:
                raise HTTPException(status_code=401, detail="帳戶已被禁用")
            
            # 更新最後登錄時間
            await self.update_last_login(user["id"])
            
            # 生成JWT令牌
            token = self.generate_jwt_token(user["id"])
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "points": user["points"],
                    "membership_tier": user["membership_tier"],
                    "subscription_expires": user["subscription_expires"],
                }
            }
            
        except Exception as e:
            logger.error(f"用戶登錄失敗: {e}")
            raise HTTPException(status_code=500, detail="登錄失敗")
    
    # 積分管理
    async def add_points(self, user_id: str, points: int, transaction_type: str, description: str) -> Dict:
        """增加積分"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 更新用戶積分
            cursor.execute('''
                UPDATE users SET points = points + ? WHERE id = ?
            ''', (points, user_id))
            
            # 記錄交易
            transaction_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO point_transactions (id, user_id, points, transaction_type, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction_id, user_id, points, transaction_type, description, time.time()))
            
            conn.commit()
            conn.close()
            
            return {"transaction_id": transaction_id, "message": "積分添加成功"}
            
        except Exception as e:
            logger.error(f"添加積分失敗: {e}")
            raise HTTPException(status_code=500, detail="積分添加失敗")
    
    async def spend_points(self, user_id: str, points: int, description: str) -> Dict:
        """消費積分"""
        try:
            # 檢查用戶積分
            user = await self.get_user_by_id(user_id)
            if user["points"] < points:
                raise HTTPException(status_code=400, detail="積分不足")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 扣除積分
            cursor.execute('''
                UPDATE users SET points = points - ? WHERE id = ?
            ''', (points, user_id))
            
            # 記錄交易
            transaction_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO point_transactions (id, user_id, points, transaction_type, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction_id, user_id, -points, "spend", description, time.time()))
            
            conn.commit()
            conn.close()
            
            return {"transaction_id": transaction_id, "message": "積分消費成功"}
            
        except Exception as e:
            logger.error(f"消費積分失敗: {e}")
            raise HTTPException(status_code=500, detail="積分消費失敗")
    
    # 支付處理
    async def create_payment(self, user_id: str, payment_request: PaymentRequest) -> Dict:
        """創建支付"""
        try:
            plan = MEMBERSHIP_PLANS.get(payment_request.plan_name)
            if not plan:
                raise HTTPException(status_code=400, detail="無效的會員計劃")
            
            payment_id = str(uuid.uuid4())
            
            if payment_request.payment_method == "alipay":
                return await self.create_alipay_payment(user_id, payment_id, plan, payment_request)
            elif payment_request.payment_method == "wechat":
                return await self.create_wechat_payment(user_id, payment_id, plan, payment_request)
            elif payment_request.payment_method == "stripe":
                return await self.create_stripe_payment(user_id, payment_id, plan, payment_request)
            else:
                raise HTTPException(status_code=400, detail="不支持的支付方式")
                
        except Exception as e:
            logger.error(f"創建支付失敗: {e}")
            raise HTTPException(status_code=500, detail="創建支付失敗")
    
    async def create_alipay_payment(self, user_id: str, payment_id: str, plan: Dict, request: PaymentRequest) -> Dict:
        """創建支付寶支付"""
        try:
            order_string = self.alipay.api_alipay_trade_page_pay(
                out_trade_no=payment_id,
                total_amount=str(plan["price"]),
                subject=f"PowerAutomation {plan['name']}",
                return_url=request.return_url,
                notify_url=request.notify_url,
            )
            
            payment_url = f"https://openapi.alipay.com/gateway.do?{order_string}"
            
            # 保存支付記錄
            await self.save_payment_record(user_id, payment_id, plan["price"], "alipay", payment_id)
            
            return {
                "payment_id": payment_id,
                "payment_url": payment_url,
                "method": "alipay"
            }
            
        except Exception as e:
            logger.error(f"創建支付寶支付失敗: {e}")
            raise HTTPException(status_code=500, detail="創建支付寶支付失敗")
    
    async def create_wechat_payment(self, user_id: str, payment_id: str, plan: Dict, request: PaymentRequest) -> Dict:
        """創建微信支付"""
        try:
            # 微信支付統一下單
            nonce_str = str(uuid.uuid4()).replace("-", "")
            params = {
                "appid": PAYMENT_CONFIG["wechat"]["app_id"],
                "mch_id": PAYMENT_CONFIG["wechat"]["mch_id"],
                "nonce_str": nonce_str,
                "body": f"PowerAutomation {plan['name']}",
                "out_trade_no": payment_id,
                "total_fee": str(int(plan["price"] * 100)),  # 分為單位
                "spbill_create_ip": "127.0.0.1",
                "notify_url": request.notify_url,
                "trade_type": "NATIVE",
            }
            
            # 生成簽名
            sign = self.generate_wechat_sign(params)
            params["sign"] = sign
            
            # 構建XML
            xml_data = self.dict_to_xml(params)
            
            # 發送請求
            response = requests.post(
                "https://api.mch.weixin.qq.com/pay/unifiedorder",
                data=xml_data,
                headers={"Content-Type": "application/xml"}
            )
            
            result = self.xml_to_dict(response.text)
            
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                # 保存支付記錄
                await self.save_payment_record(user_id, payment_id, plan["price"], "wechat", result["prepay_id"])
                
                return {
                    "payment_id": payment_id,
                    "code_url": result["code_url"],
                    "method": "wechat"
                }
            else:
                raise Exception(f"微信支付失敗: {result.get('return_msg', '未知錯誤')}")
                
        except Exception as e:
            logger.error(f"創建微信支付失敗: {e}")
            raise HTTPException(status_code=500, detail="創建微信支付失敗")
    
    async def create_stripe_payment(self, user_id: str, payment_id: str, plan: Dict, request: PaymentRequest) -> Dict:
        """創建Stripe支付"""
        try:
            # 創建支付意圖
            intent = stripe.PaymentIntent.create(
                amount=int(plan["price"] * 100),  # 分為單位
                currency=plan["currency"].lower(),
                metadata={
                    "user_id": user_id,
                    "payment_id": payment_id,
                    "plan_name": plan["name"],
                }
            )
            
            # 保存支付記錄
            await self.save_payment_record(user_id, payment_id, plan["price"], "stripe", intent.id)
            
            return {
                "payment_id": payment_id,
                "client_secret": intent.client_secret,
                "method": "stripe"
            }
            
        except Exception as e:
            logger.error(f"創建Stripe支付失敗: {e}")
            raise HTTPException(status_code=500, detail="創建Stripe支付失敗")
    
    # K2優化處理
    async def process_k2_request(self, user_id: str, input_text: str, options: Dict = None) -> Dict:
        """處理K2請求（成本優化）"""
        try:
            # 檢查用戶權限
            user = await self.get_user_by_id(user_id)
            if not await self.check_k2_quota(user_id):
                raise HTTPException(status_code=429, detail="K2調用次數已達限制")
            
            # 成本優化配置
            input_tokens = len(input_text.split())
            input_cost = input_tokens * K2_COST_CONFIG["input_cost_per_token"]
            
            # 檢查成本控制
            if input_cost > 2.0:  # 2元人民幣成本限制
                raise HTTPException(status_code=400, detail="請求成本超過限制")
            
            # 優化處理
            optimized_options = {
                "model": K2_COST_CONFIG["model_size"],
                "max_tokens": min(options.get("max_tokens", 4000), 4000),
                "temperature": options.get("temperature", 0.7),
                "batch_processing": True,
                "compression": K2_COST_CONFIG["compression_enabled"],
                "cache_enabled": True,
            }
            
            # 模擬K2處理（實際應調用K2 API）
            output_text = await self.mock_k2_process(input_text, optimized_options)
            output_tokens = len(output_text.split())
            
            # 計算效益
            output_value = K2_COST_CONFIG["target_output_value"]
            efficiency_ratio = output_value / input_cost if input_cost > 0 else 0
            
            # 記錄使用情況
            await self.record_k2_usage(user_id, input_tokens, output_tokens, input_cost, output_value, efficiency_ratio)
            
            return {
                "response": output_text,
                "input_cost": input_cost,
                "output_value": output_value,
                "efficiency_ratio": efficiency_ratio,
                "tokens_used": output_tokens,
            }
            
        except Exception as e:
            logger.error(f"K2處理失敗: {e}")
            raise HTTPException(status_code=500, detail="K2處理失敗")
    
    # 工具方法
    def hash_password(self, password: str) -> str:
        """哈希密碼"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """驗證密碼"""
        return hashlib.sha256(password.encode()).hexdigest() == password_hash
    
    def generate_jwt_token(self, user_id: str) -> str:
        """生成JWT令牌"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, "your_secret_key", algorithm="HS256")
    
    async def get_user_by_id(self, user_id: str) -> Dict:
        """根據ID獲取用戶"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    async def get_user_by_email(self, email: str) -> Dict:
        """根據郵箱獲取用戶"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    async def update_last_login(self, user_id: str):
        """更新最後登錄時間"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE id = ?
        ''', (time.time(), user_id))
        
        conn.commit()
        conn.close()
    
    async def save_payment_record(self, user_id: str, payment_id: str, amount: float, method: str, external_id: str):
        """保存支付記錄"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO payments (id, user_id, amount, currency, payment_method, payment_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), user_id, amount, "CNY", method, external_id, time.time()))
        
        conn.commit()
        conn.close()
    
    async def record_k2_usage(self, user_id: str, input_tokens: int, output_tokens: int, input_cost: float, output_value: float, efficiency_ratio: float):
        """記錄K2使用情況"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO k2_usage (id, user_id, input_tokens, output_tokens, input_cost, output_value, efficiency_ratio, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), user_id, input_tokens, output_tokens, input_cost, output_value, efficiency_ratio, time.time()))
        
        conn.commit()
        conn.close()
    
    async def check_k2_quota(self, user_id: str) -> bool:
        """檢查K2調用配額"""
        user = await self.get_user_by_id(user_id)
        plan = MEMBERSHIP_PLANS.get(user["membership_tier"], MEMBERSHIP_PLANS["free"])
        
        k2_limit = plan["features"]["k2_calls_per_day"]
        if k2_limit == -1:  # 無限制
            return True
        
        # 檢查今日使用量
        today_start = time.time() - 86400  # 24小時前
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM k2_usage 
            WHERE user_id = ? AND created_at > ?
        ''', (user_id, today_start))
        
        usage_count = cursor.fetchone()[0]
        conn.close()
        
        return usage_count < k2_limit
    
    async def mock_k2_process(self, input_text: str, options: Dict) -> str:
        """模擬K2處理（實際應調用K2 API）"""
        # 這裡應該調用實際的K2 API
        # 為了演示，返回模擬響應
        return f"K2響應: 基於您的輸入 '{input_text[:50]}...'，我為您提供了優化的解決方案。"
    
    def generate_wechat_sign(self, params: Dict) -> str:
        """生成微信支付簽名"""
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        query_string += f"&key={PAYMENT_CONFIG['wechat']['api_key']}"
        
        return hashlib.md5(query_string.encode()).hexdigest().upper()
    
    def dict_to_xml(self, params: Dict) -> str:
        """字典轉XML"""
        xml = ["<xml>"]
        for key, value in params.items():
            xml.append(f"<{key}>{value}</{key}>")
        xml.append("</xml>")
        return "".join(xml)
    
    def xml_to_dict(self, xml_str: str) -> Dict:
        """XML轉字典"""
        root = ET.fromstring(xml_str)
        return {child.tag: child.text for child in root}

# 創建全局服務實例
member_service = MemberService()

# FastAPI應用
app = FastAPI(title="PowerAutomation Member System", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 認證依賴
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """獲取當前用戶"""
    try:
        payload = jwt.decode(credentials.credentials, "your_secret_key", algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="無效的令牌")
        
        user = await member_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="用戶不存在")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已過期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的令牌")

# API路由
@app.post("/api/register")
async def register(user_data: UserRegister):
    """用戶註冊"""
    return await member_service.register_user(user_data)

@app.post("/api/login")
async def login(login_data: UserLogin):
    """用戶登錄"""
    return await member_service.login_user(login_data)

@app.get("/api/membership/plans")
async def get_membership_plans():
    """獲取會員計劃"""
    return {"plans": MEMBERSHIP_PLANS}

@app.post("/api/payment/create")
async def create_payment(payment_request: PaymentRequest, user: Dict = Depends(get_current_user)):
    """創建支付"""
    return await member_service.create_payment(user["id"], payment_request)

@app.post("/api/points/add")
async def add_points(transaction: PointsTransaction, user: Dict = Depends(get_current_user)):
    """添加積分"""
    return await member_service.add_points(user["id"], transaction.points, transaction.transaction_type, transaction.description)

@app.post("/api/k2/process")
async def process_k2(request: Dict, user: Dict = Depends(get_current_user)):
    """處理K2請求"""
    return await member_service.process_k2_request(user["id"], request["input"], request.get("options", {}))

@app.get("/api/user/profile")
async def get_user_profile(user: Dict = Depends(get_current_user)):
    """獲取用戶資料"""
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "points": user["points"],
        "membership_tier": user["membership_tier"],
        "subscription_expires": user["subscription_expires"],
        "created_at": user["created_at"],
        "last_login": user["last_login"],
    }

@app.get("/api/user/stats")
async def get_user_stats(user: Dict = Depends(get_current_user)):
    """獲取用戶統計"""
    # 實現用戶統計邏輯
    return {
        "total_k2_calls": 0,
        "total_claude_calls": 0,
        "total_points_earned": 0,
        "total_points_spent": 0,
        "efficiency_ratio": 0.0,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)