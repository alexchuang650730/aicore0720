#!/usr/bin/env python3
"""
PowerAutomation會員積分登錄系統
支持多種支付方式和積分管理
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
import secrets
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta
import bcrypt
import jwt
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import uvicorn

logger = logging.getLogger(__name__)

# 數據模型
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    username: str
    plan: str = "basic"  # basic, pro, team, enterprise

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PointsPurchase(BaseModel):
    points: int
    payment_method: str  # alipay, wechat, stripe
    currency: str = "CNY"

class PointsUsage(BaseModel):
    points: int
    service: str  # claude_api, k2_api, memory_rag, etc.
    description: str

class MemberSystemAPI:
    """會員系統API"""
    
    def __init__(self, db_path: str = "members.db"):
        self.db_path = db_path
        self.connection = None
        self.secret_key = secrets.token_urlsafe(32)
        
        # 會員計劃配置 - 基於用戶最新需求和claude-code.cn設計
        self.plans = {
            "personal": {
                "name": "Personal",
                "name_zh": "個人版",
                "price": 99,
                "currency": "CNY",
                "billing_period": "month",
                "monthly_points": 3000,  # 支持5小時200條訊息
                "highlight": "入門首選",
                "color": "#6B7280",
                "icon": "👤",
                "features": [
                    "5小時200條訊息",
                    "基礎AI對話",
                    "基礎工作流", 
                    "每月3000積分",
                    "社區支持",
                    "99元積分包可加沖"
                ],
                "limitations": {
                    "daily_requests": 200,
                    "daily_hours": 5,
                    "concurrent_sessions": 1,
                    "team_members": 1,
                    "api_access": False,
                    "priority_support": False,
                    "custom_deployment": False
                },
                "description": "適合個人開發者和學習使用",
                "addon_price": 99  # 加沖包價格
            },
            "professional": {
                "name": "Professional", 
                "name_zh": "專業版",
                "price": 599,
                "currency": "CNY",
                "billing_period": "month",
                "monthly_points": 50000,
                "highlight": "最受歡迎",
                "color": "#3B82F6",
                "icon": "💼",
                "features": [
                    "無限制使用",
                    "全部六大工作流",
                    "Claude + K2雙AI模式",
                    "每月50000積分",
                    "Memory RAG智能記憶",
                    "優先支持",
                    "2元→8元成本優化"
                ],
                "limitations": {
                    "daily_requests": -1,  # 無限制
                    "daily_hours": -1,     # 無限制
                    "concurrent_sessions": 5,
                    "team_members": 1,
                    "api_access": True,
                    "priority_support": True,
                    "custom_deployment": False
                },
                "description": "適合專業開發者和中型項目"
            },
            "team": {
                "name": "Team",
                "name_zh": "團隊版",
                "price": 599,
                "currency": "CNY", 
                "billing_period": "month",
                "billing_note": "每5人",
                "monthly_points": 250000,  # 5人共享
                "highlight": "協作首選",
                "color": "#10B981",
                "icon": "👥",
                "features": [
                    "無限制使用",
                    "團隊協作功能",
                    "全部Professional功能",
                    "共享Memory RAG",
                    "每月250000積分(5人共享)",
                    "管理員面板",
                    "API訪問權限",
                    "團隊分析報告"
                ],
                "limitations": {
                    "daily_requests": -1,
                    "daily_hours": -1,
                    "concurrent_sessions": 25,  # 5人 x 5會話
                    "team_members": 5,
                    "api_access": True,
                    "priority_support": True,
                    "custom_deployment": False
                },
                "description": "適合小型團隊和協作項目",
                "per_user_price": 119.8  # 599/5
            },
            "enterprise": {
                "name": "Enterprise",
                "name_zh": "企業版",
                "price": 999,
                "currency": "CNY",
                "billing_period": "month",
                "billing_note": "每人每月",
                "monthly_points": 1000000,  # 每人
                "highlight": "企業專享",
                "color": "#8B5CF6",
                "icon": "🏢",
                "features": [
                    "無限制使用",
                    "私有雲部署",
                    "企業級協作",
                    "無限團隊成員",
                    "每人每月1000000積分",
                    "定制開發服務",
                    "24/7專屬技術支持",
                    "SLA服務保證",
                    "數據安全合規",
                    "本地化定制"
                ],
                "limitations": {
                    "daily_requests": -1,  # 無限制
                    "daily_hours": -1,     # 無限制
                    "concurrent_sessions": -1,
                    "team_members": -1,
                    "api_access": True,
                    "priority_support": True,
                    "custom_deployment": True
                },
                "description": "適合大型企業和政府機構"
            }
        }
        
        # 積分消費配置
        self.point_costs = {
            "claude_api_call": 10,
            "k2_api_call": 5,  # K2更便宜
            "memory_rag_query": 2,
            "workflow_execution": 20,
            "code_analysis": 15,
            "ui_generation": 25,
            "deployment": 30
        }
        
        logger.info("🎯 PowerAutomation會員系統初始化")
    
    async def initialize(self):
        """初始化會員系統"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.connection.cursor()
            
            # 用戶表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    plan TEXT NOT NULL DEFAULT 'basic',
                    points INTEGER DEFAULT 1000,
                    total_spent_points INTEGER DEFAULT 0,
                    created_at REAL NOT NULL,
                    last_login REAL,
                    is_active BOOLEAN DEFAULT 1,
                    email_verified BOOLEAN DEFAULT 0
                )
            ''')
            
            # 積分交易記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS point_transactions (
                    transaction_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    type TEXT NOT NULL,  -- purchase, usage, refund, bonus
                    points INTEGER NOT NULL,
                    balance_after INTEGER NOT NULL,
                    description TEXT,
                    service TEXT,
                    payment_method TEXT,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 會員訂閱記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    subscription_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    start_date REAL NOT NULL,
                    end_date REAL NOT NULL,
                    auto_renew BOOLEAN DEFAULT 1,
                    payment_method TEXT,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'CNY',
                    status TEXT DEFAULT 'active',  -- active, expired, cancelled
                    created_at REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 會話記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    last_activity REAL NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 使用統計表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_stats (
                    stat_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    date TEXT NOT NULL,  -- YYYY-MM-DD
                    api_calls INTEGER DEFAULT 0,
                    points_used INTEGER DEFAULT 0,
                    workflows_executed INTEGER DEFAULT 0,
                    session_duration REAL DEFAULT 0,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 創建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user ON point_transactions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_user_date ON usage_stats(user_id, date)')
            
            self.connection.commit()
            
            # 創建默認管理員用戶
            await self._create_default_admin()
            
            logger.info("✅ 會員系統數據庫初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 會員系統初始化失敗: {e}")
            raise
    
    async def _create_default_admin(self):
        """創建默認管理員用戶"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('admin@powerauto.ai',))
            
            if cursor.fetchone()[0] == 0:
                admin_id = str(uuid.uuid4())
                password_hash = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
                
                cursor.execute('''
                    INSERT INTO users 
                    (user_id, email, username, password_hash, plan, points, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    admin_id,
                    'admin@powerauto.ai',
                    'admin',
                    password_hash,
                    'enterprise',
                    1000000,
                    time.time()
                ))
                
                self.connection.commit()
                logger.info("👑 默認管理員用戶已創建: admin@powerauto.ai / admin123")
                
        except Exception as e:
            logger.error(f"❌ 創建默認管理員失敗: {e}")
    
    async def register_user(self, registration: UserRegistration) -> Dict[str, Any]:
        """用戶註冊"""
        try:
            cursor = self.connection.cursor()
            
            # 檢查用戶是否已存在
            cursor.execute('SELECT user_id FROM users WHERE email = ? OR username = ?', 
                         (registration.email, registration.username))
            
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="用戶已存在")
            
            # 驗證會員計劃
            if registration.plan not in self.plans:
                raise HTTPException(status_code=400, detail="無效的會員計劃")
            
            # 創建用戶
            user_id = str(uuid.uuid4())
            password_hash = bcrypt.hashpw(registration.password.encode(), bcrypt.gensalt()).decode()
            current_time = time.time()
            
            # 根據計劃分配初始積分
            initial_points = self.plans[registration.plan]["monthly_points"]
            
            cursor.execute('''
                INSERT INTO users 
                (user_id, email, username, password_hash, plan, points, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                registration.email,
                registration.username,
                password_hash,
                registration.plan,
                initial_points,
                current_time
            ))
            
            # 記錄初始積分
            await self._add_point_transaction(
                user_id=user_id,
                transaction_type="bonus",
                points=initial_points,
                description=f"註冊{self.plans[registration.plan]['name']}獲得初始積分",
                service="registration"
            )
            
            # 如果是付費計劃，創建訂閱記錄
            if registration.plan != "basic":
                subscription_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO subscriptions
                    (subscription_id, user_id, plan, start_date, end_date, amount, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    subscription_id,
                    user_id,
                    registration.plan,
                    current_time,
                    current_time + (30 * 24 * 3600),  # 30天後到期
                    self.plans[registration.plan]["price"],
                    current_time
                ))
            
            self.connection.commit()
            
            # 生成JWT令牌
            token = self._generate_jwt_token(user_id, registration.email)
            
            logger.info(f"✅ 用戶註冊成功: {registration.email} ({registration.plan})")
            
            return {
                "user_id": user_id,
                "email": registration.email,
                "username": registration.username,
                "plan": registration.plan,
                "points": initial_points,
                "token": token,
                "features": self.plans[registration.plan]["features"],
                "limitations": self.plans[registration.plan]["limitations"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 用戶註冊失敗: {e}")
            raise HTTPException(status_code=500, detail=f"註冊失敗: {str(e)}")
    
    async def login_user(self, login: UserLogin) -> Dict[str, Any]:
        """用戶登錄"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT user_id, email, username, password_hash, plan, points, is_active
                FROM users 
                WHERE email = ?
            ''', (login.email,))
            
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=401, detail="用戶不存在")
            
            user_id, email, username, password_hash, plan, points, is_active = user
            
            if not is_active:
                raise HTTPException(status_code=401, detail="用戶已被禁用")
            
            # 驗證密碼
            if not bcrypt.checkpw(login.password.encode(), password_hash.encode()):
                raise HTTPException(status_code=401, detail="密碼錯誤")
            
            # 更新最後登錄時間
            current_time = time.time()
            cursor.execute('UPDATE users SET last_login = ? WHERE user_id = ?', 
                         (current_time, user_id))
            
            # 創建會話
            session_id = await self._create_user_session(user_id)
            
            self.connection.commit()
            
            # 生成JWT令牌
            token = self._generate_jwt_token(user_id, email)
            
            # 獲取當前訂閱信息
            subscription_info = await self._get_user_subscription(user_id)
            
            logger.info(f"✅ 用戶登錄成功: {email}")
            
            return {
                "user_id": user_id,
                "email": email,
                "username": username,
                "plan": plan,
                "points": points,
                "token": token,
                "session_id": session_id,
                "subscription": subscription_info,
                "features": self.plans[plan]["features"],
                "limitations": self.plans[plan]["limitations"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 用戶登錄失敗: {e}")
            raise HTTPException(status_code=500, detail="登錄失敗")
    
    async def _create_user_session(self, user_id: str) -> str:
        """創建用戶會話"""
        session_id = str(uuid.uuid4())
        current_time = time.time()
        
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO user_sessions
            (session_id, user_id, created_at, last_activity)
            VALUES (?, ?, ?, ?)
        ''', (session_id, user_id, current_time, current_time))
        
        return session_id
    
    async def _get_user_subscription(self, user_id: str) -> Dict[str, Any]:
        """獲取用戶訂閱信息"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT plan, start_date, end_date, status, auto_renew
            FROM subscriptions 
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user_id,))
        
        subscription = cursor.fetchone()
        if not subscription:
            return {"plan": "basic", "status": "free"}
        
        plan, start_date, end_date, status, auto_renew = subscription
        
        return {
            "plan": plan,
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "auto_renew": bool(auto_renew),
            "days_remaining": max(0, int((end_date - time.time()) / 86400))
        }
    
    async def purchase_points(self, user_id: str, purchase: PointsPurchase) -> Dict[str, Any]:
        """購買積分"""
        try:
            # 模擬支付處理
            payment_result = await self._process_payment(purchase)
            
            if not payment_result["success"]:
                raise HTTPException(status_code=400, detail="支付失敗")
            
            # 添加積分
            cursor = self.connection.cursor()
            cursor.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
            current_points = cursor.fetchone()[0]
            
            new_points = current_points + purchase.points
            cursor.execute('UPDATE users SET points = ? WHERE user_id = ?', 
                         (new_points, user_id))
            
            # 記錄交易
            await self._add_point_transaction(
                user_id=user_id,
                transaction_type="purchase",
                points=purchase.points,
                description=f"購買{purchase.points}積分",
                payment_method=purchase.payment_method
            )
            
            self.connection.commit()
            
            logger.info(f"💰 積分購買成功: 用戶{user_id} 購買{purchase.points}積分")
            
            return {
                "success": True,
                "points_purchased": purchase.points,
                "new_balance": new_points,
                "payment_method": purchase.payment_method,
                "transaction_id": payment_result["transaction_id"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 積分購買失敗: {e}")
            raise HTTPException(status_code=500, detail="購買失敗")
    
    async def use_points(self, user_id: str, usage: PointsUsage) -> Dict[str, Any]:
        """使用積分"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="用戶不存在")
            
            current_points = result[0]
            
            if current_points < usage.points:
                raise HTTPException(status_code=400, detail="積分不足")
            
            # 扣除積分
            new_points = current_points - usage.points
            cursor.execute('UPDATE users SET points = ?, total_spent_points = total_spent_points + ? WHERE user_id = ?', 
                         (new_points, usage.points, user_id))
            
            # 記錄交易
            await self._add_point_transaction(
                user_id=user_id,
                transaction_type="usage",
                points=-usage.points,
                description=usage.description,
                service=usage.service
            )
            
            # 更新使用統計
            await self._update_usage_stats(user_id, usage.service, usage.points)
            
            self.connection.commit()
            
            return {
                "success": True,
                "points_used": usage.points,
                "remaining_points": new_points,
                "service": usage.service
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 積分使用失敗: {e}")
            raise HTTPException(status_code=500, detail="積分使用失敗")
    
    async def _add_point_transaction(self, user_id: str, transaction_type: str, 
                                   points: int, description: str, 
                                   service: str = None, payment_method: str = None):
        """添加積分交易記錄"""
        cursor = self.connection.cursor()
        
        # 獲取當前餘額
        cursor.execute('SELECT points FROM users WHERE user_id = ?', (user_id,))
        balance_after = cursor.fetchone()[0]
        
        transaction_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO point_transactions
            (transaction_id, user_id, type, points, balance_after, description, service, payment_method, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_id,
            user_id,
            transaction_type,
            points,
            balance_after,
            description,
            service,
            payment_method,
            time.time()
        ))
    
    async def _update_usage_stats(self, user_id: str, service: str, points_used: int):
        """更新使用統計"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO usage_stats
            (stat_id, user_id, date, created_at)
            VALUES (?, ?, ?, ?)
        ''', (f"{user_id}_{today}", user_id, today, time.time()))
        
        cursor.execute('''
            UPDATE usage_stats 
            SET api_calls = api_calls + 1, 
                points_used = points_used + ?,
                workflows_executed = workflows_executed + CASE WHEN ? LIKE '%workflow%' THEN 1 ELSE 0 END
            WHERE user_id = ? AND date = ?
        ''', (points_used, service, user_id, today))
    
    async def _process_payment(self, purchase: PointsPurchase) -> Dict[str, Any]:
        """處理支付（模擬）"""
        # 這裡應該集成真實的支付API
        # 支付寶、微信支付、Stripe等
        
        # 模擬支付處理
        await asyncio.sleep(0.1)  # 模擬網絡延遲
        
        # 計算價格（1積分 = 0.01元）
        amount = purchase.points * 0.01
        
        return {
            "success": True,
            "transaction_id": str(uuid.uuid4()),
            "amount": amount,
            "currency": purchase.currency,
            "payment_method": purchase.payment_method
        }
    
    def _generate_jwt_token(self, user_id: str, email: str) -> str:
        """生成JWT令牌"""
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": time.time() + (7 * 24 * 3600),  # 7天有效期
            "iat": time.time()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    async def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """驗證JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # 檢查用戶是否仍然活躍
            cursor = self.connection.cursor()
            cursor.execute('SELECT is_active FROM users WHERE user_id = ?', (payload["user_id"],))
            
            result = cursor.fetchone()
            if not result or not result[0]:
                raise HTTPException(status_code=401, detail="用戶已被禁用")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="令牌已過期")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="無效令牌")
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """獲取用戶信息"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT email, username, plan, points, total_spent_points, created_at, last_login
                FROM users 
                WHERE user_id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="用戶不存在")
            
            email, username, plan, points, total_spent, created_at, last_login = user
            
            # 獲取訂閱信息
            subscription_info = await self._get_user_subscription(user_id)
            
            # 獲取今日使用統計
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT api_calls, points_used, workflows_executed
                FROM usage_stats 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))
            
            stats = cursor.fetchone()
            daily_stats = {
                "api_calls": stats[0] if stats else 0,
                "points_used": stats[1] if stats else 0,
                "workflows_executed": stats[2] if stats else 0
            }
            
            return {
                "user_id": user_id,
                "email": email,
                "username": username,
                "plan": plan,
                "points": points,
                "total_spent_points": total_spent,
                "created_at": created_at,
                "last_login": last_login,
                "subscription": subscription_info,
                "daily_stats": daily_stats,
                "plan_info": self.plans[plan]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 獲取用戶信息失敗: {e}")
            raise HTTPException(status_code=500, detail="獲取用戶信息失敗")
    
    async def close(self):
        """關閉會員系統"""
        if self.connection:
            self.connection.close()
        logger.info("✅ 會員系統已關閉")

# FastAPI應用
def create_member_api():
    """創建會員系統API"""
    app = FastAPI(title="PowerAutomation會員系統", version="1.0.0")
    
    # 添加CORS中間件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 初始化會員系統
    member_system = MemberSystemAPI()
    
    # 安全依賴
    security = HTTPBearer()
    
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """獲取當前用戶"""
        payload = await member_system.verify_jwt_token(credentials.credentials)
        return payload["user_id"]
    
    @app.on_event("startup")
    async def startup():
        await member_system.initialize()
    
    @app.on_event("shutdown")
    async def shutdown():
        await member_system.close()
    
    @app.post("/api/register")
    async def register(registration: UserRegistration):
        """用戶註冊"""
        return await member_system.register_user(registration)
    
    @app.post("/api/login")
    async def login(login: UserLogin):
        """用戶登錄"""
        return await member_system.login_user(login)
    
    @app.get("/api/user/info")
    async def get_user_info(user_id: str = Depends(get_current_user)):
        """獲取用戶信息"""
        return await member_system.get_user_info(user_id)
    
    @app.post("/api/points/purchase")
    async def purchase_points(purchase: PointsPurchase, user_id: str = Depends(get_current_user)):
        """購買積分"""
        return await member_system.purchase_points(user_id, purchase)
    
    @app.post("/api/points/use")
    async def use_points(usage: PointsUsage, user_id: str = Depends(get_current_user)):
        """使用積分"""
        return await member_system.use_points(user_id, usage)
    
    @app.get("/api/plans")
    async def get_plans():
        """獲取會員計劃"""
        return member_system.plans
    
    @app.get("/api/health")
    async def health_check():
        """健康檢查"""
        return {"status": "healthy", "timestamp": time.time()}
    
    return app

if __name__ == "__main__":
    print("🎯 啟動PowerAutomation會員系統...")
    app = create_member_api()
    uvicorn.run(app, host="0.0.0.0", port=8081)