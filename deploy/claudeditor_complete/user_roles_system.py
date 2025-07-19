#!/usr/bin/env python3
"""
PowerAutomation 用戶角色權限系統
支持：管理員、開發者、一般使用者三級權限
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import asyncpg
import bcrypt
import jwt
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """用戶角色類型"""
    ADMIN = "admin"           # 管理員 - 最高權限
    DEVELOPER = "developer"   # 開發者 - 開發和調試權限
    USER = "user"             # 一般使用者 - 基本使用權限

class PermissionLevel(Enum):
    """權限級別"""
    READ = "read"             # 讀取權限
    WRITE = "write"           # 寫入權限
    EXECUTE = "execute"       # 執行權限
    ADMIN = "admin"           # 管理權限
    DEBUG = "debug"           # 調試權限

@dataclass
class RolePermissions:
    """角色權限配置"""
    role: UserRole
    permissions: Dict[str, List[PermissionLevel]]
    features: List[str]
    limitations: Dict[str, Any]
    ui_access: Dict[str, bool]

class UserRoleManager:
    """用戶角色管理器"""
    
    def __init__(self):
        self.db_pool = None
        self.secret_key = "powerauto-role-secret-key"
        
        # 定義角色權限體系
        self.role_permissions = {
            UserRole.ADMIN: RolePermissions(
                role=UserRole.ADMIN,
                permissions={
                    "user_management": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN],
                    "system_config": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN],
                    "api_access": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE, PermissionLevel.ADMIN],
                    "claude_editor": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE, PermissionLevel.DEBUG],
                    "k2_providers": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN],
                    "payment_system": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN],
                    "analytics": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN],
                    "workflows": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE, PermissionLevel.DEBUG],
                    "memory_rag": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN],
                    "logs": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN]
                },
                features=[
                    "完整系統管理權限",
                    "用戶管理和權限分配", 
                    "系統配置和K2 Provider管理",
                    "支付系統管理",
                    "完整分析報告和日誌",
                    "調試模式和開發工具",
                    "數據庫直接訪問",
                    "系統備份和恢復"
                ],
                limitations={
                    "api_rate_limit": -1,        # 無限制
                    "concurrent_sessions": -1,    # 無限制
                    "daily_requests": -1,         # 無限制
                    "storage_quota_gb": -1,       # 無限制
                    "team_members": -1            # 無限制
                },
                ui_access={
                    "admin_panel": True,
                    "developer_tools": True,
                    "user_dashboard": True,
                    "system_logs": True,
                    "debug_console": True,
                    "api_explorer": True,
                    "analytics_dashboard": True
                }
            ),
            
            UserRole.DEVELOPER: RolePermissions(
                role=UserRole.DEVELOPER,
                permissions={
                    "user_management": [PermissionLevel.READ],  # 只能查看用戶信息
                    "system_config": [PermissionLevel.READ],    # 只能查看系統配置
                    "api_access": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE],
                    "claude_editor": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE, PermissionLevel.DEBUG],
                    "k2_providers": [PermissionLevel.READ, PermissionLevel.EXECUTE],
                    "payment_system": [PermissionLevel.READ],   # 只能查看支付信息
                    "analytics": [PermissionLevel.READ],        # 只能查看分析數據
                    "workflows": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE, PermissionLevel.DEBUG],
                    "memory_rag": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE],
                    "logs": [PermissionLevel.READ]              # 只能查看日誌
                },
                features=[
                    "完整的ClaudeEditor開發功能",
                    "六大工作流開發和調試",
                    "Memory RAG系統開發",
                    "API完整訪問權限",
                    "K2 Provider測試和切換",
                    "調試模式和開發工具",
                    "日誌查看和分析",
                    "代碼生成和測試"
                ],
                limitations={
                    "api_rate_limit": 10000,      # 每小時10000次
                    "concurrent_sessions": 20,     # 20個並發會話
                    "daily_requests": 50000,       # 每日50000次請求
                    "storage_quota_gb": 100,       # 100GB存儲配額
                    "team_members": 10             # 可管理10個團隊成員
                },
                ui_access={
                    "admin_panel": False,
                    "developer_tools": True,
                    "user_dashboard": True,
                    "system_logs": True,
                    "debug_console": True,
                    "api_explorer": True,
                    "analytics_dashboard": True
                }
            ),
            
            UserRole.USER: RolePermissions(
                role=UserRole.USER,
                permissions={
                    "user_management": [],                      # 無用戶管理權限
                    "system_config": [],                        # 無系統配置權限
                    "api_access": [PermissionLevel.READ, PermissionLevel.EXECUTE],  # 基本API訪問
                    "claude_editor": [PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE],
                    "k2_providers": [PermissionLevel.EXECUTE],  # 只能使用K2
                    "payment_system": [PermissionLevel.READ, PermissionLevel.WRITE],  # 管理自己的支付
                    "analytics": [PermissionLevel.READ],        # 查看自己的數據
                    "workflows": [PermissionLevel.READ, PermissionLevel.EXECUTE],     # 使用工作流
                    "memory_rag": [PermissionLevel.READ, PermissionLevel.EXECUTE],    # 使用Memory RAG
                    "logs": []                                  # 無日誌訪問權限
                },
                features=[
                    "ClaudeEditor基本功能",
                    "六大工作流使用",
                    "Memory RAG智能記憶",
                    "K2 AI對話功能",
                    "個人數據分析",
                    "支付和訂閱管理",
                    "基本API訪問"
                ],
                limitations={
                    "api_rate_limit": 1000,       # 每小時1000次
                    "concurrent_sessions": 3,      # 3個並發會話
                    "daily_requests": 5000,        # 每日5000次請求
                    "storage_quota_gb": 10,        # 10GB存儲配額
                    "team_members": 1              # 只能管理自己
                },
                ui_access={
                    "admin_panel": False,
                    "developer_tools": False,
                    "user_dashboard": True,
                    "system_logs": False,
                    "debug_console": False,
                    "api_explorer": False,
                    "analytics_dashboard": False   # 只能看個人分析
                }
            )
        }
        
        logger.info("🔐 用戶角色管理器初始化完成")
    
    async def initialize(self):
        """初始化角色管理系統"""
        try:
            self.db_pool = await asyncpg.create_pool(
                "postgresql://powerauto:powerauto123@postgres:5432/powerautomation",
                min_size=5,
                max_size=20
            )
            
            await self._create_role_tables()
            await self._create_default_roles()
            
            logger.info("✅ 用戶角色管理系統初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 角色管理系統初始化失敗: {e}")
            raise
    
    async def _create_role_tables(self):
        """創建角色相關表"""
        async with self.db_pool.acquire() as conn:
            # 用戶角色表 - 擴展原有users表
            await conn.execute('''
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user',
                ADD COLUMN IF NOT EXISTS role_assigned_at TIMESTAMP DEFAULT NOW(),
                ADD COLUMN IF NOT EXISTS role_assigned_by TEXT,
                ADD COLUMN IF NOT EXISTS permissions JSONB DEFAULT '{}',
                ADD COLUMN IF NOT EXISTS ui_preferences JSONB DEFAULT '{}',
                ADD COLUMN IF NOT EXISTS last_role_change TIMESTAMP
            ''')
            
            # 權限操作日誌表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS role_audit_logs (
                    log_id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,  -- role_change, permission_grant, permission_revoke
                    old_role TEXT,
                    new_role TEXT,
                    changed_by TEXT NOT NULL,
                    details JSONB,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # 功能訪問日誌表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS feature_access_logs (
                    log_id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    action TEXT NOT NULL,  -- access, denied, error
                    permission_required TEXT,
                    user_role TEXT,
                    success BOOLEAN DEFAULT TRUE,
                    details JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # 創建索引
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_role_audit_user ON role_audit_logs(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_feature_access_user ON feature_access_logs(user_id)')
    
    async def _create_default_roles(self):
        """創建默認角色用戶"""
        try:
            async with self.db_pool.acquire() as conn:
                # 檢查是否已有管理員
                admin_count = await conn.fetchval(
                    'SELECT COUNT(*) FROM users WHERE role = $1', 
                    UserRole.ADMIN.value
                )
                
                if admin_count == 0:
                    # 創建默認管理員
                    admin_id = str(uuid.uuid4())
                    password_hash = bcrypt.hashpw('admin123!'.encode(), bcrypt.gensalt()).decode()
                    
                    await conn.execute('''
                        INSERT INTO users 
                        (user_id, email, username, password_hash, role, plan, points, created_at, role_assigned_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        ON CONFLICT (email) DO UPDATE SET 
                        role = $5, role_assigned_at = $9
                    ''', (
                        admin_id,
                        'admin@powerauto.ai',
                        'admin',
                        password_hash,
                        UserRole.ADMIN.value,
                        'enterprise',
                        1000000,
                        time.time(),
                        time.time()
                    ))
                    
                    logger.info("👑 默認管理員創建完成: admin@powerauto.ai / admin123!")
                
                # 創建默認開發者
                dev_count = await conn.fetchval(
                    'SELECT COUNT(*) FROM users WHERE role = $1', 
                    UserRole.DEVELOPER.value
                )
                
                if dev_count == 0:
                    dev_id = str(uuid.uuid4())
                    password_hash = bcrypt.hashpw('dev123!'.encode(), bcrypt.gensalt()).decode()
                    
                    await conn.execute('''
                        INSERT INTO users 
                        (user_id, email, username, password_hash, role, plan, points, created_at, role_assigned_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        ON CONFLICT (email) DO UPDATE SET 
                        role = $5, role_assigned_at = $9
                    ''', (
                        dev_id,
                        'developer@powerauto.ai',
                        'developer',
                        password_hash,
                        UserRole.DEVELOPER.value,
                        'professional',
                        100000,
                        time.time(),
                        time.time()
                    ))
                    
                    logger.info("🛠️ 默認開發者創建完成: developer@powerauto.ai / dev123!")
                    
        except Exception as e:
            logger.error(f"❌ 創建默認角色失敗: {e}")
    
    async def assign_role(self, user_id: str, new_role: UserRole, assigned_by: str) -> bool:
        """分配用戶角色"""
        try:
            async with self.db_pool.acquire() as conn:
                # 獲取當前角色
                current_role = await conn.fetchval(
                    'SELECT role FROM users WHERE user_id = $1', user_id
                )
                
                if not current_role:
                    raise ValueError("用戶不存在")
                
                # 更新角色
                await conn.execute('''
                    UPDATE users 
                    SET role = $1, role_assigned_at = $2, role_assigned_by = $3, last_role_change = $4
                    WHERE user_id = $5
                ''', (
                    new_role.value,
                    time.time(),
                    assigned_by,
                    time.time(),
                    user_id
                ))
                
                # 記錄審計日誌
                await self._log_role_change(
                    user_id, "role_change", current_role, new_role.value, assigned_by
                )
                
                logger.info(f"✅ 用戶角色更新: {user_id} {current_role} → {new_role.value}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 分配用戶角色失敗: {e}")
            return False
    
    async def check_permission(self, user_id: str, feature: str, action: PermissionLevel) -> bool:
        """檢查用戶權限"""
        try:
            async with self.db_pool.acquire() as conn:
                user_role = await conn.fetchval(
                    'SELECT role FROM users WHERE user_id = $1', user_id
                )
                
                if not user_role:
                    return False
                
                role_enum = UserRole(user_role)
                permissions = self.role_permissions[role_enum].permissions
                
                feature_permissions = permissions.get(feature, [])
                has_permission = action in feature_permissions
                
                # 記錄訪問日誌
                await self._log_feature_access(
                    user_id, feature, action.value, user_role, has_permission
                )
                
                return has_permission
                
        except Exception as e:
            logger.error(f"❌ 檢查權限失敗: {e}")
            return False
    
    async def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """獲取用戶完整權限信息"""
        try:
            async with self.db_pool.acquire() as conn:
                user_data = await conn.fetchrow('''
                    SELECT role, email, username, plan, points, created_at, last_role_change
                    FROM users WHERE user_id = $1
                ''', user_id)
                
                if not user_data:
                    raise ValueError("用戶不存在")
                
                role_enum = UserRole(user_data['role'])
                role_config = self.role_permissions[role_enum]
                
                return {
                    "user_id": user_id,
                    "role": user_data['role'],
                    "email": user_data['email'],
                    "username": user_data['username'],
                    "plan": user_data['plan'],
                    "points": user_data['points'],
                    "permissions": {k: [p.value for p in v] for k, v in role_config.permissions.items()},
                    "features": role_config.features,
                    "limitations": role_config.limitations,
                    "ui_access": role_config.ui_access,
                    "last_role_change": user_data['last_role_change']
                }
                
        except Exception as e:
            logger.error(f"❌ 獲取用戶權限失敗: {e}")
            return {}
    
    async def get_role_statistics(self) -> Dict[str, Any]:
        """獲取角色統計信息"""
        try:
            async with self.db_pool.acquire() as conn:
                # 角色分布統計
                role_stats = await conn.fetch('''
                    SELECT role, COUNT(*) as count, 
                           COUNT(*) FILTER (WHERE last_login > NOW() - INTERVAL '24 hours') as active_24h,
                           COUNT(*) FILTER (WHERE last_login > NOW() - INTERVAL '7 days') as active_7d
                    FROM users 
                    GROUP BY role
                ''')
                
                # 權限操作統計
                permission_stats = await conn.fetch('''
                    SELECT action_type, COUNT(*) as count
                    FROM role_audit_logs 
                    WHERE created_at > NOW() - INTERVAL '30 days'
                    GROUP BY action_type
                ''')
                
                # 功能訪問統計
                feature_stats = await conn.fetch('''
                    SELECT feature_name, COUNT(*) as total_access,
                           COUNT(*) FILTER (WHERE success = false) as denied_access
                    FROM feature_access_logs 
                    WHERE created_at > NOW() - INTERVAL '7 days'
                    GROUP BY feature_name
                    ORDER BY total_access DESC
                    LIMIT 10
                ''')
                
                return {
                    "role_distribution": [dict(row) for row in role_stats],
                    "permission_operations": [dict(row) for row in permission_stats],
                    "feature_usage": [dict(row) for row in feature_stats],
                    "total_users": sum(row['count'] for row in role_stats)
                }
                
        except Exception as e:
            logger.error(f"❌ 獲取角色統計失敗: {e}")
            return {}
    
    async def _log_role_change(self, user_id: str, action: str, old_role: str, new_role: str, changed_by: str):
        """記錄角色變更日誌"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO role_audit_logs 
                    (user_id, action_type, old_role, new_role, changed_by, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                ''', (user_id, action, old_role, new_role, changed_by, time.time()))
                
        except Exception as e:
            logger.error(f"❌ 記錄角色變更日誌失敗: {e}")
    
    async def _log_feature_access(self, user_id: str, feature: str, action: str, role: str, success: bool):
        """記錄功能訪問日誌"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO feature_access_logs 
                    (user_id, feature_name, action, user_role, success, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                ''', (user_id, feature, action, role, success, time.time()))
                
        except Exception as e:
            logger.error(f"❌ 記錄功能訪問日誌失敗: {e}")
    
    async def close(self):
        """關閉角色管理器"""
        if self.db_pool:
            await self.db_pool.close()
        logger.info("✅ 用戶角色管理器已關閉")

# FastAPI中間件和裝飾器
class RoleBasedAuth:
    """基於角色的認證中間件"""
    
    def __init__(self, role_manager: UserRoleManager):
        self.role_manager = role_manager
        self.security = HTTPBearer()
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """獲取當前用戶"""
        try:
            # 解析JWT token
            payload = jwt.decode(credentials.credentials, self.role_manager.secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            if not user_id:
                raise HTTPException(status_code=401, detail="無效的token")
            
            return user_id
            
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="token已過期或無效")
    
    def require_permission(self, feature: str, action: PermissionLevel):
        """權限檢查裝飾器"""
        async def permission_check(user_id: str = Depends(self.get_current_user)):
            has_permission = await self.role_manager.check_permission(user_id, feature, action)
            
            if not has_permission:
                raise HTTPException(
                    status_code=403, 
                    detail=f"權限不足: 需要 {feature}.{action.value} 權限"
                )
            
            return user_id
        
        return permission_check
    
    def require_role(self, required_role: UserRole):
        """角色檢查裝飾器"""
        async def role_check(user_id: str = Depends(self.get_current_user)):
            async with self.role_manager.db_pool.acquire() as conn:
                user_role = await conn.fetchval(
                    'SELECT role FROM users WHERE user_id = $1', user_id
                )
                
                if not user_role or UserRole(user_role) != required_role:
                    raise HTTPException(
                        status_code=403,
                        detail=f"權限不足: 需要 {required_role.value} 角色"
                    )
                
                return user_id
        
        return role_check

if __name__ == "__main__":
    # 測試角色管理系統
    async def test_role_system():
        role_manager = UserRoleManager()
        
        try:
            await role_manager.initialize()
            
            # 測試權限檢查
            test_user_id = "test_user_123"
            
            # 檢查不同權限
            permissions_to_test = [
                ("claude_editor", PermissionLevel.READ),
                ("claude_editor", PermissionLevel.WRITE),
                ("system_config", PermissionLevel.ADMIN),
                ("api_access", PermissionLevel.EXECUTE)
            ]
            
            for feature, action in permissions_to_test:
                has_permission = await role_manager.check_permission(test_user_id, feature, action)
                print(f"權限檢查 {feature}.{action.value}: {has_permission}")
            
            # 獲取角色統計
            stats = await role_manager.get_role_statistics()
            print("角色統計:", json.dumps(stats, indent=2, ensure_ascii=False))
            
        finally:
            await role_manager.close()
    
    # 運行測試
    asyncio.run(test_role_system())