#!/usr/bin/env python3
"""
三權限系統實現：使用者/開發者/管理者
支持PowerAuto.ai網站和ClaudeEditor的統一認證
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """用戶角色枚舉"""
    USER = "user"           # 使用者：基本功能訪問
    DEVELOPER = "developer" # 開發者：開發工具和API訪問  
    ADMIN = "admin"         # 管理者：系統管理和配置

class PermissionLevel(Enum):
    """權限級別"""
    READ = "read"           # 讀取權限
    WRITE = "write"         # 寫入權限
    EXECUTE = "execute"     # 執行權限
    ADMIN = "admin"         # 管理權限

@dataclass
class User:
    """用戶模型"""
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: Set[str]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    session_token: Optional[str] = None
    profile: Dict[str, Any] = None

@dataclass
class Permission:
    """權限模型"""
    permission_id: str
    name: str
    description: str
    level: PermissionLevel
    resource: str
    actions: List[str]

@dataclass
class AuthSession:
    """認證會話"""
    session_id: str
    user_id: str
    role: UserRole
    permissions: Set[str]
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str

class ThreeTierAuthSystem:
    """三權限系統核心"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, AuthSession] = {}
        self.permissions: Dict[str, Permission] = {}
        
        # 初始化權限體系
        self._initialize_permissions()
        
        # 創建默認管理員
        self._create_default_admin()
        
        # 會話設置
        self.session_timeout = timedelta(hours=24)  # 24小時會話超時
        
    def _initialize_permissions(self):
        """初始化權限體系"""
        
        # 基本權限
        basic_permissions = [
            Permission("view_dashboard", "查看儀表板", "訪問基本儀表板", PermissionLevel.READ, "dashboard", ["view"]),
            Permission("view_projects", "查看項目", "查看個人項目列表", PermissionLevel.READ, "projects", ["view", "list"]),
            Permission("edit_profile", "編輯個人資料", "修改個人信息", PermissionLevel.WRITE, "profile", ["view", "edit"]),
        ]
        
        # 開發者權限
        developer_permissions = [
            Permission("create_projects", "創建項目", "創建新的開發項目", PermissionLevel.WRITE, "projects", ["create", "edit", "delete"]),
            Permission("access_api", "API訪問", "使用開發者API", PermissionLevel.EXECUTE, "api", ["read", "write", "execute"]),
            Permission("use_claudeeditor", "ClaudeEditor訪問", "使用ClaudeEditor開發工具", PermissionLevel.EXECUTE, "claudeeditor", ["access", "edit", "debug"]),
            Permission("manage_mcp", "MCP組件管理", "管理MCP組件和配置", PermissionLevel.WRITE, "mcp", ["view", "configure", "deploy"]),
            Permission("access_k2", "K2模型訪問", "使用K2模型進行開發", PermissionLevel.EXECUTE, "k2", ["query", "train", "optimize"]),
            Permission("view_metrics", "性能指標", "查看系統性能指標", PermissionLevel.READ, "metrics", ["view", "export"]),
        ]
        
        # 管理者權限
        admin_permissions = [
            Permission("manage_users", "用戶管理", "管理系統用戶", PermissionLevel.ADMIN, "users", ["create", "edit", "delete", "suspend"]),
            Permission("manage_system", "系統管理", "系統配置和維護", PermissionLevel.ADMIN, "system", ["configure", "backup", "restore", "monitor"]),
            Permission("manage_billing", "計費管理", "管理用戶計費和訂閱", PermissionLevel.ADMIN, "billing", ["view", "edit", "export"]),
            Permission("view_logs", "日誌訪問", "查看系統日誌", PermissionLevel.ADMIN, "logs", ["view", "export", "analyze"]),
            Permission("manage_permissions", "權限管理", "管理用戶角色和權限", PermissionLevel.ADMIN, "permissions", ["assign", "revoke", "audit"]),
        ]
        
        # 存儲所有權限
        all_permissions = basic_permissions + developer_permissions + admin_permissions
        for perm in all_permissions:
            self.permissions[perm.permission_id] = perm
        
        logger.info(f"初始化 {len(all_permissions)} 個權限")
        
    def _create_default_admin(self):
        """創建默認管理員賬戶"""
        admin_permissions = {
            # 基本權限
            "view_dashboard", "view_projects", "edit_profile",
            # 開發者權限  
            "create_projects", "access_api", "use_claudeeditor", "manage_mcp", 
            "access_k2", "view_metrics",
            # 管理者權限
            "manage_users", "manage_system", "manage_billing", "view_logs", 
            "manage_permissions"
        }
        
        admin_user = User(
            user_id="admin_001",
            username="admin",
            email="admin@powerauto.ai",
            role=UserRole.ADMIN,
            permissions=admin_permissions,
            created_at=datetime.now(),
            profile={
                "display_name": "系統管理員",
                "department": "技術部",
                "access_level": "full"
            }
        )
        
        self.users[admin_user.user_id] = admin_user
        logger.info("創建默認管理員賬戶")
        
    async def register_user(self, username: str, email: str, role: UserRole = UserRole.USER) -> User:
        """用戶註冊"""
        user_id = f"{role.value}_{int(time.time())}"
        
        # 根據角色分配權限
        permissions = self._get_role_permissions(role)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=permissions,
            created_at=datetime.now(),
            profile={
                "display_name": username,
                "department": "",
                "access_level": role.value
            }
        )
        
        self.users[user_id] = user
        logger.info(f"註冊新用戶: {username} ({role.value})")
        
        return user
        
    def _get_role_permissions(self, role: UserRole) -> Set[str]:
        """根據角色獲取權限"""
        if role == UserRole.USER:
            return {"view_dashboard", "view_projects", "edit_profile"}
        elif role == UserRole.DEVELOPER:
            return {
                # 基本權限
                "view_dashboard", "view_projects", "edit_profile",
                # 開發者權限
                "create_projects", "access_api", "use_claudeeditor", 
                "manage_mcp", "access_k2", "view_metrics"
            }
        elif role == UserRole.ADMIN:
            # 管理員擁有所有權限
            return set(self.permissions.keys())
        else:
            return set()
            
    async def authenticate(self, username: str, password: str, ip_address: str = "", 
                          user_agent: str = "") -> Optional[AuthSession]:
        """用戶認證"""
        # 查找用戶 (簡化版，實際應該驗證密碼哈希)
        user = None
        for u in self.users.values():
            if u.username == username and u.is_active:
                user = u
                break
                
        if not user:
            logger.warning(f"認證失敗: 用戶 {username} 不存在或已停用")
            return None
            
        # 創建會話
        session = await self._create_session(user, ip_address, user_agent)
        
        # 更新最後登錄時間
        user.last_login = datetime.now()
        user.session_token = session.session_id
        
        logger.info(f"用戶 {username} 認證成功，角色: {user.role.value}")
        return session
        
    async def _create_session(self, user: User, ip_address: str, user_agent: str) -> AuthSession:
        """創建認證會話"""
        session_id = secrets.token_urlsafe(32)
        now = datetime.now()
        
        session = AuthSession(
            session_id=session_id,
            user_id=user.user_id,
            role=user.role,
            permissions=user.permissions.copy(),
            created_at=now,
            expires_at=now + self.session_timeout,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session_id] = session
        return session
        
    async def verify_session(self, session_id: str) -> Optional[AuthSession]:
        """驗證會話"""
        session = self.sessions.get(session_id)
        if not session:
            return None
            
        # 檢查會話是否過期
        if datetime.now() > session.expires_at:
            await self.invalidate_session(session_id)
            return None
            
        # 更新最後活動時間
        session.last_activity = datetime.now()
        return session
        
    async def has_permission(self, session_id: str, permission: str) -> bool:
        """檢查權限"""
        session = await self.verify_session(session_id)
        if not session:
            return False
            
        return permission in session.permissions
        
    async def check_resource_access(self, session_id: str, resource: str, action: str) -> bool:
        """檢查資源訪問權限"""
        session = await self.verify_session(session_id)
        if not session:
            return False
            
        # 檢查是否有對應資源的權限
        for perm_id in session.permissions:
            perm = self.permissions.get(perm_id)
            if perm and perm.resource == resource and action in perm.actions:
                return True
                
        return False
        
    async def invalidate_session(self, session_id: str):
        """廢棄會話"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"會話 {session_id} 已廢棄")
            
    async def promote_user(self, admin_session_id: str, user_id: str, new_role: UserRole) -> bool:
        """提升用戶角色 (需要管理員權限)"""
        if not await self.has_permission(admin_session_id, "manage_users"):
            logger.warning("權限不足：無法提升用戶角色")
            return False
            
        user = self.users.get(user_id)
        if not user:
            return False
            
        old_role = user.role
        user.role = new_role
        user.permissions = self._get_role_permissions(new_role)
        
        # 更新活躍會話的權限
        for session in self.sessions.values():
            if session.user_id == user_id:
                session.role = new_role
                session.permissions = user.permissions.copy()
                
        logger.info(f"用戶 {user.username} 角色從 {old_role.value} 提升到 {new_role.value}")
        return True
        
    def get_user_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """獲取用戶信息"""
        session = self.sessions.get(session_id)
        if not session:
            return None
            
        user = self.users.get(session.user_id)
        if not user:
            return None
            
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "permissions": list(user.permissions),
            "profile": user.profile,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "session_expires": session.expires_at.isoformat()
        }
        
    def list_users(self, admin_session_id: str) -> Optional[List[Dict[str, Any]]]:
        """列出所有用戶 (管理員權限)"""
        session = self.sessions.get(admin_session_id)
        if not session or not self.has_permission_sync(admin_session_id, "manage_users"):
            return None
            
        users_info = []
        for user in self.users.values():
            users_info.append({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            })
            
        return users_info
        
    def has_permission_sync(self, session_id: str, permission: str) -> bool:
        """同步權限檢查"""
        session = self.sessions.get(session_id)
        if not session:
            return False
            
        # 檢查會話是否過期
        if datetime.now() > session.expires_at:
            return False
            
        return permission in session.permissions
        
    def get_system_stats(self, admin_session_id: str) -> Optional[Dict[str, Any]]:
        """獲取系統統計 (管理員權限)"""
        if not self.has_permission_sync(admin_session_id, "manage_system"):
            return None
            
        role_counts = {"user": 0, "developer": 0, "admin": 0}
        active_sessions = 0
        
        for user in self.users.values():
            if user.is_active:
                role_counts[user.role.value] += 1
                
        for session in self.sessions.values():
            if datetime.now() <= session.expires_at:
                active_sessions += 1
                
        return {
            "total_users": len(self.users),
            "role_distribution": role_counts,
            "active_sessions": active_sessions,
            "total_permissions": len(self.permissions),
            "system_uptime": datetime.now().isoformat()
        }

# 全局認證系統實例
auth_system = ThreeTierAuthSystem()

class AuthMiddleware:
    """認證中間件"""
    
    def __init__(self, auth_system: ThreeTierAuthSystem):
        self.auth = auth_system
        
    async def authenticate_request(self, session_id: str, required_permission: str = None) -> Dict[str, Any]:
        """請求認證"""
        result = {
            "authenticated": False,
            "user_info": None,
            "error": None
        }
        
        if not session_id:
            result["error"] = "缺少會話ID"
            return result
            
        session = await self.auth.verify_session(session_id)
        if not session:
            result["error"] = "會話無效或已過期"
            return result
            
        if required_permission and not await self.auth.has_permission(session_id, required_permission):
            result["error"] = f"權限不足：需要 {required_permission}"
            return result
            
        result["authenticated"] = True
        result["user_info"] = self.auth.get_user_info(session_id)
        
        return result

# 認證中間件實例
auth_middleware = AuthMiddleware(auth_system)

# 演示功能
async def demo_three_tier_auth():
    """三權限系統演示"""
    print("🔐 三權限系統演示")
    print("=" * 60)
    
    # 1. 註冊不同角色用戶
    print("\n1. 用戶註冊演示")
    user1 = await auth_system.register_user("alice", "alice@example.com", UserRole.USER)
    user2 = await auth_system.register_user("bob", "bob@developer.com", UserRole.DEVELOPER)
    print(f"註冊用戶: {user1.username} ({user1.role.value})")
    print(f"註冊開發者: {user2.username} ({user2.role.value})")
    
    # 2. 用戶認證
    print("\n2. 用戶認證演示")
    session1 = await auth_system.authenticate("alice", "password", "192.168.1.100", "Mozilla/5.0")
    session2 = await auth_system.authenticate("bob", "password", "192.168.1.101", "Chrome/91.0")
    session_admin = await auth_system.authenticate("admin", "admin_pass", "192.168.1.1", "Admin Client")
    
    print(f"Alice會話: {session1.session_id[:8]}... (角色: {session1.role.value})")
    print(f"Bob會話: {session2.session_id[:8]}... (角色: {session2.role.value})")
    print(f"Admin會話: {session_admin.session_id[:8]}... (角色: {session_admin.role.value})")
    
    # 3. 權限檢查演示
    print("\n3. 權限檢查演示")
    
    # Alice (用戶) 權限檢查
    can_view_dashboard = await auth_system.has_permission(session1.session_id, "view_dashboard")
    can_use_claudeeditor = await auth_system.has_permission(session1.session_id, "use_claudeeditor")
    can_manage_users = await auth_system.has_permission(session1.session_id, "manage_users")
    
    print(f"Alice 查看儀表板: {'✅' if can_view_dashboard else '❌'}")
    print(f"Alice 使用ClaudeEditor: {'✅' if can_use_claudeeditor else '❌'}")
    print(f"Alice 管理用戶: {'✅' if can_manage_users else '❌'}")
    
    # Bob (開發者) 權限檢查
    can_use_claudeeditor = await auth_system.has_permission(session2.session_id, "use_claudeeditor")
    can_access_k2 = await auth_system.has_permission(session2.session_id, "access_k2")
    can_manage_users = await auth_system.has_permission(session2.session_id, "manage_users")
    
    print(f"Bob 使用ClaudeEditor: {'✅' if can_use_claudeeditor else '❌'}")
    print(f"Bob 訪問K2: {'✅' if can_access_k2 else '❌'}")
    print(f"Bob 管理用戶: {'✅' if can_manage_users else '❌'}")
    
    # 4. 資源訪問控制演示
    print("\n4. 資源訪問控制演示")
    
    # 檢查不同用戶對ClaudeEditor的訪問權限
    alice_claudeeditor = await auth_system.check_resource_access(session1.session_id, "claudeeditor", "access")
    bob_claudeeditor = await auth_system.check_resource_access(session2.session_id, "claudeeditor", "access")
    admin_claudeeditor = await auth_system.check_resource_access(session_admin.session_id, "claudeeditor", "access")
    
    print(f"Alice 訪問ClaudeEditor: {'✅' if alice_claudeeditor else '❌'}")
    print(f"Bob 訪問ClaudeEditor: {'✅' if bob_claudeeditor else '❌'}")
    print(f"Admin 訪問ClaudeEditor: {'✅' if admin_claudeeditor else '❌'}")
    
    # 5. 角色提升演示
    print("\n5. 角色提升演示")
    success = await auth_system.promote_user(session_admin.session_id, user1.user_id, UserRole.DEVELOPER)
    print(f"Alice提升為開發者: {'✅' if success else '❌'}")
    
    # 重新檢查Alice的權限
    alice_new_claudeeditor = await auth_system.check_resource_access(session1.session_id, "claudeeditor", "access")
    print(f"Alice (開發者) 訪問ClaudeEditor: {'✅' if alice_new_claudeeditor else '❌'}")
    
    # 6. 用戶信息查看
    print("\n6. 用戶信息演示")
    alice_info = auth_system.get_user_info(session1.session_id)
    print(f"Alice信息: {alice_info['username']} - {alice_info['role']}")
    print(f"Alice權限數: {len(alice_info['permissions'])}")
    
    # 7. 系統統計 (管理員權限)
    print("\n7. 系統統計演示")
    stats = auth_system.get_system_stats(session_admin.session_id)
    print(f"總用戶數: {stats['total_users']}")
    print(f"角色分布: {stats['role_distribution']}")
    print(f"活躍會話: {stats['active_sessions']}")
    
    return {
        "users_created": 3,
        "sessions_active": 3,
        "permissions_tested": 10,
        "demo_success": True
    }

if __name__ == "__main__":
    result = asyncio.run(demo_three_tier_auth())
    print(f"\n✅ 三權限系統演示完成！")