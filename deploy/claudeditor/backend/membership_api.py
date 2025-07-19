"""
會員積分系統API
支持用戶認證、積分管理、會員等級等功能
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
import jwt
import bcrypt
import sqlite3
from datetime import datetime, timedelta
import uuid
import json
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT配置
SECRET_KEY = "powerautomation-secret-key-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

# 創建FastAPI應用
app = FastAPI(title="PowerAutomation 會員系統API", version="1.0.0")

# 認證相關
security = HTTPBearer()

# 數據模型
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    membership_tier: str
    current_points: int
    daily_points_used: int
    monthly_points_used: int
    created_at: str

class PointsUpdate(BaseModel):
    points_to_deduct: int
    action_type: str
    provider: str = "k2"

class MembershipUpgrade(BaseModel):
    target_tier: str
    payment_method: str = "alipay"

# 數據庫初始化
def init_database():
    """初始化數據庫"""
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    
    # 用戶表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            membership_tier TEXT DEFAULT 'free',
            current_points INTEGER DEFAULT 1000,
            daily_points_used INTEGER DEFAULT 0,
            monthly_points_used INTEGER DEFAULT 0,
            total_points_purchased INTEGER DEFAULT 0,
            last_reset_date TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # 積分使用記錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS points_usage (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            points_used INTEGER NOT NULL,
            provider TEXT DEFAULT 'k2',
            cost_saved REAL DEFAULT 0,
            command_executed TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 會員升級記錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membership_upgrades (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            from_tier TEXT NOT NULL,
            to_tier TEXT NOT NULL,
            payment_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_status TEXT DEFAULT 'pending',
            upgrade_date TEXT,
            expiry_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 系統配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# 會員等級配置
MEMBERSHIP_TIERS = {
    "free": {
        "name": "體驗版",
        "price": 0,
        "daily_points": 1000,
        "monthly_points": 30000,
        "features": ["基礎AI對話", "基本UI生成", "社區支持"],
        "k2_priority": False
    },
    "pro": {
        "name": "專業版", 
        "price": 299,
        "daily_points": 10000,
        "monthly_points": 300000,
        "features": ["無限AI對話", "高級UI生成", "記憶RAG", "工作流自動化", "優先支持"],
        "k2_priority": True
    },
    "enterprise": {
        "name": "企業版",
        "price": 2999,
        "daily_points": 100000,
        "monthly_points": 3000000,
        "features": ["全部功能", "私有部署", "定制工作流", "1對1技術支持", "數據分析"],
        "k2_priority": True
    }
}

# 積分計費配置
PRICING_CONFIG = {
    "k2": {
        "cost_per_token": 0.0001,
        "points_per_token": 1
    },
    "claude": {
        "cost_per_token": 0.0008,
        "points_per_token": 8
    }
}

# 工具函數
def hash_password(password: str) -> str:
    """密碼哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """驗證密碼"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """創建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """驗證JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """根據ID獲取用戶"""
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "email": user[1],
            "password_hash": user[2],
            "username": user[3],
            "membership_tier": user[4],
            "current_points": user[5],
            "daily_points_used": user[6],
            "monthly_points_used": user[7],
            "total_points_purchased": user[8],
            "last_reset_date": user[9],
            "created_at": user[10],
            "updated_at": user[11]
        }
    return None

def reset_daily_points_if_needed(user_id: str):
    """如果需要，重置每日積分"""
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    
    today = datetime.now().date().isoformat()
    cursor.execute('SELECT last_reset_date FROM users WHERE id = ?', (user_id,))
    last_reset = cursor.fetchone()
    
    if not last_reset or last_reset[0] != today:
        cursor.execute('''
            UPDATE users 
            SET daily_points_used = 0, last_reset_date = ?, updated_at = ?
            WHERE id = ?
        ''', (today, datetime.now().isoformat(), user_id))
        conn.commit()
    
    conn.close()

# API端點
@app.on_event("startup")
async def startup_event():
    """應用啟動時初始化數據庫"""
    init_database()
    logger.info("會員系統API啟動完成")

@app.post("/api/auth/register", response_model=Dict[str, Any])
async def register(user_data: UserRegister):
    """用戶註冊"""
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    
    try:
        # 檢查用戶是否已存在
        cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', 
                      (user_data.email, user_data.username))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="用戶名或郵箱已存在"
            )
        
        # 創建新用戶
        user_id = str(uuid.uuid4())
        password_hash = hash_password(user_data.password)
        now = datetime.now().isoformat()
        today = datetime.now().date().isoformat()
        
        cursor.execute('''
            INSERT INTO users 
            (id, email, password_hash, username, created_at, updated_at, last_reset_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_data.email, password_hash, user_data.username, now, now, today))
        
        conn.commit()
        
        # 創建token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "status": "success",
            "message": "註冊成功",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user_data.email,
                "username": user_data.username,
                "membership_tier": "free",
                "current_points": 1000
            }
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"註冊失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/auth/login", response_model=Dict[str, Any])
async def login(user_data: UserLogin):
    """用戶登錄"""
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    
    try:
        # 查找用戶
        cursor.execute('SELECT * FROM users WHERE email = ?', (user_data.email,))
        user = cursor.fetchone()
        
        if not user or not verify_password(user_data.password, user[2]):
            raise HTTPException(
                status_code=401,
                detail="郵箱或密碼錯誤"
            )
        
        # 重置每日積分
        user_id = user[0]
        reset_daily_points_if_needed(user_id)
        
        # 獲取最新用戶信息
        updated_user = get_user_by_id(user_id)
        
        # 創建token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "status": "success",
            "message": "登錄成功",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": updated_user["id"],
                "email": updated_user["email"],
                "username": updated_user["username"],
                "membership_tier": updated_user["membership_tier"],
                "current_points": updated_user["current_points"],
                "daily_points_used": updated_user["daily_points_used"],
                "monthly_points_used": updated_user["monthly_points_used"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登錄失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/user/profile", response_model=Dict[str, Any])
async def get_user_profile(user_id: str = Depends(verify_token)):
    """獲取用戶資料"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    # 重置每日積分
    reset_daily_points_if_needed(user_id)
    user = get_user_by_id(user_id)  # 重新獲取更新後的用戶信息
    
    # 獲取會員等級信息
    tier_info = MEMBERSHIP_TIERS[user["membership_tier"]]
    
    return {
        "status": "success",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "membership_tier": user["membership_tier"],
            "current_points": user["current_points"],
            "daily_points_used": user["daily_points_used"],
            "monthly_points_used": user["monthly_points_used"],
            "daily_points_limit": tier_info["daily_points"],
            "monthly_points_limit": tier_info["monthly_points"],
            "features": tier_info["features"],
            "created_at": user["created_at"]
        }
    }

@app.post("/api/points/use", response_model=Dict[str, Any])
async def use_points(points_data: PointsUpdate, user_id: str = Depends(verify_token)):
    """使用積分"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    # 重置每日積分
    reset_daily_points_if_needed(user_id)
    user = get_user_by_id(user_id)  # 重新獲取
    
    # 檢查積分是否足夠
    if user["current_points"] < points_data.points_to_deduct:
        raise HTTPException(status_code=400, detail="積分不足")
    
    # 檢查每日限制
    tier_info = MEMBERSHIP_TIERS[user["membership_tier"]]
    if user["daily_points_used"] + points_data.points_to_deduct > tier_info["daily_points"]:
        raise HTTPException(status_code=400, detail="超過每日使用限制")
    
    # 檢查每月限制
    if user["monthly_points_used"] + points_data.points_to_deduct > tier_info["monthly_points"]:
        raise HTTPException(status_code=400, detail="超過每月使用限制")
    
    # 計算成本節省
    cost_saved = 0
    if points_data.provider == "k2":
        claude_cost = points_data.points_to_deduct * PRICING_CONFIG["claude"]["cost_per_token"]
        k2_cost = points_data.points_to_deduct * PRICING_CONFIG["k2"]["cost_per_token"]
        cost_saved = claude_cost - k2_cost
    
    # 更新用戶積分
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    
    try:
        new_points = user["current_points"] - points_data.points_to_deduct
        new_daily_used = user["daily_points_used"] + points_data.points_to_deduct
        new_monthly_used = user["monthly_points_used"] + points_data.points_to_deduct
        
        cursor.execute('''
            UPDATE users 
            SET current_points = ?, daily_points_used = ?, monthly_points_used = ?, updated_at = ?
            WHERE id = ?
        ''', (new_points, new_daily_used, new_monthly_used, datetime.now().isoformat(), user_id))
        
        # 記錄使用記錄
        usage_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO points_usage 
            (id, user_id, action_type, points_used, provider, cost_saved, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (usage_id, user_id, points_data.action_type, points_data.points_to_deduct, 
              points_data.provider, cost_saved, datetime.now().isoformat()))
        
        conn.commit()
        
        return {
            "status": "success",
            "message": "積分使用成功",
            "points_used": points_data.points_to_deduct,
            "remaining_points": new_points,
            "daily_used": new_daily_used,
            "monthly_used": new_monthly_used,
            "cost_saved": cost_saved
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"使用積分失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/membership/upgrade", response_model=Dict[str, Any])
async def upgrade_membership(upgrade_data: MembershipUpgrade, user_id: str = Depends(verify_token)):
    """升級會員"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    if upgrade_data.target_tier not in MEMBERSHIP_TIERS:
        raise HTTPException(status_code=400, detail="無效的會員等級")
    
    target_tier_info = MEMBERSHIP_TIERS[upgrade_data.target_tier]
    current_tier = user["membership_tier"]
    
    if current_tier == upgrade_data.target_tier:
        raise HTTPException(status_code=400, detail="已是該會員等級")
    
    # 模擬支付過程（實際應用中需要接入支付系統）
    payment_amount = target_tier_info["price"]
    
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    
    try:
        # 更新用戶會員等級
        cursor.execute('''
            UPDATE users 
            SET membership_tier = ?, updated_at = ?
            WHERE id = ?
        ''', (upgrade_data.target_tier, datetime.now().isoformat(), user_id))
        
        # 記錄升級記錄
        upgrade_id = str(uuid.uuid4())
        upgrade_date = datetime.now().isoformat()
        expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
        
        cursor.execute('''
            INSERT INTO membership_upgrades 
            (id, user_id, from_tier, to_tier, payment_amount, payment_method, 
             payment_status, upgrade_date, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (upgrade_id, user_id, current_tier, upgrade_data.target_tier, 
              payment_amount, upgrade_data.payment_method, "completed", 
              upgrade_date, expiry_date))
        
        conn.commit()
        
        return {
            "status": "success",
            "message": "會員升級成功",
            "from_tier": current_tier,
            "to_tier": upgrade_data.target_tier,
            "payment_amount": payment_amount,
            "upgrade_date": upgrade_date,
            "expiry_date": expiry_date
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"升級會員失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/usage/stats", response_model=Dict[str, Any])
async def get_usage_stats(user_id: str = Depends(verify_token)):
    """獲取使用統計"""
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    
    try:
        # 獲取本月使用統計
        cursor.execute('''
            SELECT 
                action_type, 
                provider, 
                SUM(points_used) as total_points, 
                COUNT(*) as usage_count,
                SUM(cost_saved) as total_saved
            FROM points_usage 
            WHERE user_id = ? AND created_at >= ? 
            GROUP BY action_type, provider
        ''', (user_id, datetime.now().replace(day=1).isoformat()))
        
        usage_stats = cursor.fetchall()
        
        # 獲取總體統計
        cursor.execute('''
            SELECT 
                SUM(points_used) as total_points_used,
                SUM(cost_saved) as total_cost_saved,
                COUNT(*) as total_commands
            FROM points_usage 
            WHERE user_id = ?
        ''', (user_id,))
        
        total_stats = cursor.fetchone()
        
        # 處理統計數據
        stats_by_action = {}
        for stat in usage_stats:
            action, provider, points, count, saved = stat
            if action not in stats_by_action:
                stats_by_action[action] = {}
            stats_by_action[action][provider] = {
                "total_points": points,
                "usage_count": count,
                "cost_saved": saved
            }
        
        return {
            "status": "success",
            "usage_statistics": {
                "monthly_stats": stats_by_action,
                "total_stats": {
                    "total_points_used": total_stats[0] or 0,
                    "total_cost_saved": total_stats[1] or 0,
                    "total_commands": total_stats[2] or 0
                },
                "period": "current_month"
            }
        }
        
    except Exception as e:
        logger.error(f"獲取使用統計失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/membership/tiers", response_model=Dict[str, Any])
async def get_membership_tiers():
    """獲取會員等級信息"""
    return {
        "status": "success",
        "membership_tiers": MEMBERSHIP_TIERS
    }

@app.get("/api/system/config", response_model=Dict[str, Any])
async def get_system_config():
    """獲取系統配置"""
    return {
        "status": "success",
        "config": {
            "pricing": PRICING_CONFIG,
            "membership_tiers": MEMBERSHIP_TIERS,
            "features": {
                "k2_model_switching": True,
                "claude_code_integration": True,
                "smart_ui_generation": True,
                "workflow_automation": True,
                "memory_rag": True
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)