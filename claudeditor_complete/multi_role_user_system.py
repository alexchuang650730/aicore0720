#!/usr/bin/env python3
"""
多角色用戶權限管理系統
管理員 / 開發者 / 一般用戶 的完整權限體系
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class UserRole(Enum):
    """用戶角色枚舉"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    REGULAR_USER = "regular_user"

class PermissionLevel(Enum):
    """權限級別"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

@dataclass
class Permission:
    """權限定義"""
    resource: str  # 資源名稱
    level: PermissionLevel  # 權限級別
    description: str  # 權限描述

@dataclass
class User:
    """用戶信息"""
    user_id: str
    email: str
    name: str
    role: UserRole
    permissions: List[Permission]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    metadata: Dict[str, Any]

class MultiRoleUserSystem:
    """多角色用戶權限管理系統"""
    
    def __init__(self):
        self.role_permissions = self._define_role_permissions()
        self.ui_configurations = self._define_ui_configurations()
        
    def _define_role_permissions(self) -> Dict[UserRole, List[Permission]]:
        """定義各角色的權限"""
        
        return {
            UserRole.ADMIN: [
                # 系統管理
                Permission("system", PermissionLevel.ADMIN, "系統完全控制權限"),
                Permission("users", PermissionLevel.ADMIN, "用戶管理權限"),
                Permission("billing", PermissionLevel.ADMIN, "計費和支付管理"),
                Permission("analytics", PermissionLevel.ADMIN, "系統分析和統計"),
                Permission("logs", PermissionLevel.READ, "系統日誌查看"),
                Permission("settings", PermissionLevel.ADMIN, "系統設置管理"),
                
                # 產品管理
                Permission("features", PermissionLevel.ADMIN, "功能開關管理"),
                Permission("api_keys", PermissionLevel.ADMIN, "API密鑰管理"),
                Permission("webhooks", PermissionLevel.ADMIN, "Webhook配置"),
                Permission("integrations", PermissionLevel.ADMIN, "第三方集成管理"),
                
                # 數據管理
                Permission("database", PermissionLevel.ADMIN, "數據庫管理"),
                Permission("backups", PermissionLevel.ADMIN, "備份和恢復"),
                Permission("exports", PermissionLevel.ADMIN, "數據導出"),
                
                # 開發者功能
                Permission("claude_api", PermissionLevel.ADMIN, "Claude API無限使用"),
                Permission("k2_api", PermissionLevel.ADMIN, "K2 API無限使用"),
                Permission("comparisons", PermissionLevel.ADMIN, "對比測試無限制"),
                Permission("workflows", PermissionLevel.ADMIN, "工作流管理"),
            ],
            
            UserRole.DEVELOPER: [
                # 開發功能
                Permission("claude_api", PermissionLevel.WRITE, "Claude API高配額使用"),
                Permission("k2_api", PermissionLevel.WRITE, "K2 API高配額使用"),
                Permission("comparisons", PermissionLevel.WRITE, "對比測試功能"),
                Permission("workflows", PermissionLevel.WRITE, "自定義工作流"),
                Permission("integrations", PermissionLevel.WRITE, "API集成功能"),
                
                # 數據和分析
                Permission("analytics", PermissionLevel.READ, "使用分析查看"),
                Permission("exports", PermissionLevel.WRITE, "數據導出"),
                Permission("logs", PermissionLevel.READ, "個人日誌查看"),
                
                # 協作功能
                Permission("team", PermissionLevel.WRITE, "團隊協作功能"),
                Permission("sharing", PermissionLevel.WRITE, "代碼分享"),
                Permission("feedback", PermissionLevel.WRITE, "反饋提交"),
                
                # 高級功能
                Permission("beta_features", PermissionLevel.READ, "Beta功能訪問"),
                Permission("api_access", PermissionLevel.READ, "API訪問權限"),
                Permission("webhooks", PermissionLevel.READ, "Webhook配置"),
                
                # 個人設置
                Permission("profile", PermissionLevel.WRITE, "個人資料管理"),
                Permission("preferences", PermissionLevel.WRITE, "偏好設置"),
            ],
            
            UserRole.REGULAR_USER: [
                # 基本功能
                Permission("claude_api", PermissionLevel.READ, "Claude API基礎使用"),
                Permission("k2_api", PermissionLevel.READ, "K2 API基礎使用"),
                Permission("comparisons", PermissionLevel.READ, "基礎對比功能"),
                Permission("workflows", PermissionLevel.READ, "預設工作流使用"),
                
                # 個人功能
                Permission("profile", PermissionLevel.WRITE, "個人資料管理"),
                Permission("preferences", PermissionLevel.WRITE, "基本偏好設置"),
                Permission("billing", PermissionLevel.READ, "個人賬單查看"),
                
                # 有限分析
                Permission("analytics", PermissionLevel.READ, "個人使用統計"),
                Permission("exports", PermissionLevel.READ, "有限數據導出"),
                
                # 社群功能
                Permission("community", PermissionLevel.READ, "社群內容訪問"),
                Permission("feedback", PermissionLevel.WRITE, "反饋提交"),
            ]
        }
    
    def _define_ui_configurations(self) -> Dict[UserRole, Dict[str, Any]]:
        """定義各角色的UI配置"""
        
        return {
            UserRole.ADMIN: {
                "navigation": [
                    {"name": "儀表板", "icon": "dashboard", "url": "/admin/dashboard"},
                    {"name": "用戶管理", "icon": "users", "url": "/admin/users"},
                    {"name": "系統設置", "icon": "settings", "url": "/admin/settings"},
                    {"name": "計費管理", "icon": "billing", "url": "/admin/billing"},
                    {"name": "分析報告", "icon": "analytics", "url": "/admin/analytics"},
                    {"name": "系統日誌", "icon": "logs", "url": "/admin/logs"},
                    {"name": "API管理", "icon": "api", "url": "/admin/api"},
                    {"name": "開發工具", "icon": "code", "url": "/dev/tools"},
                ],
                "dashboard_widgets": [
                    "system_health",
                    "user_statistics", 
                    "revenue_metrics",
                    "api_usage",
                    "error_monitoring",
                    "performance_metrics"
                ],
                "features": {
                    "unlimited_api_calls": True,
                    "system_administration": True,
                    "user_management": True,
                    "billing_management": True,
                    "advanced_analytics": True,
                    "beta_features": True,
                    "api_key_management": True,
                    "webhook_configuration": True
                },
                "ui_theme": {
                    "primary_color": "#DC2626",  # Red for admin
                    "badge": "管理員",
                    "badge_color": "#DC2626"
                }
            },
            
            UserRole.DEVELOPER: {
                "navigation": [
                    {"name": "開發工作台", "icon": "code", "url": "/dev/workspace"},
                    {"name": "API測試", "icon": "api", "url": "/dev/api-test"},
                    {"name": "對比分析", "icon": "compare", "url": "/dev/comparisons"},
                    {"name": "工作流", "icon": "workflow", "url": "/dev/workflows"},
                    {"name": "團隊協作", "icon": "team", "url": "/dev/team"},
                    {"name": "使用分析", "icon": "analytics", "url": "/dev/analytics"},
                    {"name": "文檔中心", "icon": "docs", "url": "/dev/docs"},
                    {"name": "反饋中心", "icon": "feedback", "url": "/dev/feedback"},
                ],
                "dashboard_widgets": [
                    "api_usage_stats",
                    "comparison_results",
                    "team_activity",
                    "performance_metrics",
                    "recent_workflows",
                    "feature_updates"
                ],
                "features": {
                    "high_api_quota": True,
                    "comparison_tools": True,
                    "custom_workflows": True,
                    "team_collaboration": True,
                    "advanced_analytics": True,
                    "beta_features": True,
                    "api_access": True,
                    "export_capabilities": True
                },
                "api_limits": {
                    "claude_daily": 1000,
                    "k2_daily": 2000,
                    "comparisons_daily": 500,
                    "exports_monthly": 100
                },
                "ui_theme": {
                    "primary_color": "#2563EB",  # Blue for developers
                    "badge": "開發者",
                    "badge_color": "#2563EB"
                }
            },
            
            UserRole.REGULAR_USER: {
                "navigation": [
                    {"name": "工作台", "icon": "home", "url": "/workspace"},
                    {"name": "代碼助手", "icon": "code", "url": "/assistant"},
                    {"name": "我的項目", "icon": "projects", "url": "/projects"},
                    {"name": "使用統計", "icon": "stats", "url": "/stats"},
                    {"name": "設置", "icon": "settings", "url": "/settings"},
                    {"name": "幫助中心", "icon": "help", "url": "/help"},
                ],
                "dashboard_widgets": [
                    "daily_usage",
                    "recent_projects",
                    "tips_and_tricks",
                    "upgrade_prompt"
                ],
                "features": {
                    "basic_api_access": True,
                    "basic_comparisons": True,
                    "preset_workflows": True,
                    "community_access": True,
                    "basic_analytics": True
                },
                "api_limits": {
                    "claude_daily": 50,
                    "k2_daily": 100,
                    "comparisons_daily": 20,
                    "exports_monthly": 5
                },
                "upgrade_prompts": {
                    "show_upgrade_banner": True,
                    "highlight_premium_features": True,
                    "trial_offers": True
                },
                "ui_theme": {
                    "primary_color": "#059669",  # Green for regular users
                    "badge": "用戶",
                    "badge_color": "#059669"
                }
            }
        }
    
    def get_user_permissions(self, role: UserRole) -> List[Permission]:
        """獲取用戶權限"""
        return self.role_permissions.get(role, [])
    
    def check_permission(self, user_role: UserRole, resource: str, level: PermissionLevel) -> bool:
        """檢查用戶權限"""
        user_permissions = self.get_user_permissions(user_role)
        
        for permission in user_permissions:
            if permission.resource == resource:
                if permission.level == PermissionLevel.ADMIN:
                    return True
                elif permission.level == level:
                    return True
                elif level == PermissionLevel.READ and permission.level in [PermissionLevel.WRITE, PermissionLevel.DELETE]:
                    return True
        
        return False
    
    def get_ui_config(self, role: UserRole) -> Dict[str, Any]:
        """獲取用戶UI配置"""
        return self.ui_configurations.get(role, {})
    
    def generate_role_based_html(self, role: UserRole) -> str:
        """生成基於角色的HTML模板"""
        
        config = self.get_ui_config(role)
        permissions = self.get_user_permissions(role)
        
        html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation - {config["ui_theme"]["badge"]}界面</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        :root {{
            --primary-color: {config["ui_theme"]["primary_color"]};
            --badge-color: {config["ui_theme"]["badge_color"]};
        }}
        .primary-bg {{ background-color: var(--primary-color); }}
        .primary-text {{ color: var(--primary-color); }}
        .primary-border {{ border-color: var(--primary-color); }}
        .role-badge {{
            background-color: var(--badge-color);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- 頭部導航 -->
    <header class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center">
                    <img src="/static/logo.png" alt="PowerAutomation" class="h-8 w-auto">
                    <span class="ml-2 text-xl font-bold">PowerAutomation</span>
                    <span class="ml-4 role-badge">{config["ui_theme"]["badge"]}</span>
                </div>
                
                <div class="flex items-center space-x-4">
                    <div class="relative">
                        <button class="flex items-center text-sm text-gray-700 hover:text-gray-900">
                            <img class="h-8 w-8 rounded-full" src="/static/default-avatar.png" alt="User">
                            <span class="ml-2">用戶名</span>
                            <i class="fas fa-chevron-down ml-1"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <div class="flex min-h-screen">
        <!-- 側邊欄導航 -->
        <nav class="w-64 bg-white shadow-sm">
            <div class="p-4">
                <h2 class="text-lg font-semibold text-gray-900 mb-4">導航菜單</h2>
                <ul class="space-y-2">'''
        
        # 添加導航項目
        for nav_item in config.get("navigation", []):
            html += f'''
                    <li>
                        <a href="{nav_item['url']}" class="flex items-center p-3 text-gray-700 rounded-lg hover:bg-gray-100 hover:primary-text">
                            <i class="fas fa-{nav_item['icon']} mr-3"></i>
                            <span>{nav_item['name']}</span>
                        </a>
                    </li>'''
        
        html += '''
                </ul>
            </div>
        </nav>

        <!-- 主內容區域 -->
        <main class="flex-1 p-6">
            <!-- 儀表板標題 -->
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-gray-900">
                    {role_name}工作台
                </h1>
                <p class="text-gray-600 mt-2">
                    歡迎使用PowerAutomation，您當前的角色是{badge_name}
                </p>
            </div>

            <!-- 功能卡片網格 -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">'''.format(
                role_name=config["ui_theme"]["badge"],
                badge_name=config["ui_theme"]["badge"]
            )
        
        # 添加儀表板小部件
        widget_configs = {
            "system_health": {"title": "系統健康", "icon": "heartbeat", "color": "green"},
            "user_statistics": {"title": "用戶統計", "icon": "users", "color": "blue"},
            "revenue_metrics": {"title": "收入指標", "icon": "dollar-sign", "color": "green"},
            "api_usage": {"title": "API使用", "icon": "code", "color": "purple"},
            "api_usage_stats": {"title": "API統計", "icon": "chart-bar", "color": "blue"},
            "comparison_results": {"title": "對比結果", "icon": "balance-scale", "color": "orange"},
            "team_activity": {"title": "團隊活動", "icon": "users-cog", "color": "blue"},
            "daily_usage": {"title": "今日使用", "icon": "clock", "color": "green"},
            "recent_projects": {"title": "最近項目", "icon": "folder", "color": "blue"},
            "upgrade_prompt": {"title": "升級提示", "icon": "arrow-up", "color": "yellow"}
        }
        
        for widget in config.get("dashboard_widgets", []):
            widget_config = widget_configs.get(widget, {"title": "未知", "icon": "question", "color": "gray"})
            html += f'''
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-{widget_config['color']}-100 text-{widget_config['color']}-600">
                            <i class="fas fa-{widget_config['icon']} text-xl"></i>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-lg font-semibold text-gray-900">{widget_config['title']}</h3>
                            <p class="text-gray-600">數據載入中...</p>
                        </div>
                    </div>
                </div>'''
        
        html += '''
            </div>

            <!-- 權限列表 -->
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-4">當前權限</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">'''
        
        # 添加權限列表
        for permission in permissions:
            level_colors = {
                PermissionLevel.READ: "blue",
                PermissionLevel.WRITE: "green", 
                PermissionLevel.DELETE: "yellow",
                PermissionLevel.ADMIN: "red"
            }
            color = level_colors.get(permission.level, "gray")
            
            html += f'''
                    <div class="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                            <span class="font-medium">{permission.description}</span>
                            <span class="text-sm text-gray-500 block">{permission.resource}</span>
                        </div>
                        <span class="px-2 py-1 text-xs font-semibold bg-{color}-100 text-{color}-800 rounded">
                            {permission.level.value}
                        </span>
                    </div>'''
        
        html += '''
                </div>
            </div>
        </main>
    </div>

    <!-- JavaScript -->
    <script>
        // 角色特定的JavaScript功能
        console.log('PowerAutomation loaded for role:', '{role}');
        
        // 根據角色顯示不同的功能
        document.addEventListener('DOMContentLoaded', function() {{
            const roleFeatures = {features};
            
            // 根據features對象啟用/禁用功能
            Object.keys(roleFeatures).forEach(feature => {{
                if (roleFeatures[feature]) {{
                    console.log('Feature enabled:', feature);
                }}
            }});
        }});
    </script>
</body>
</html>'''.format(
            role=role.value,
            features=json.dumps(config.get("features", {}))
        )
        
        return html
    
    def generate_permission_middleware(self) -> str:
        """生成權限中間件代碼"""
        
        return '''# PowerAutomation 權限中間件
from functools import wraps
from flask import request, jsonify, g
from typing import Callable, Any

def require_permission(resource: str, level: str):
    """權限裝飾器"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs) -> Any:
            # 從請求中獲取用戶信息
            user = getattr(g, 'current_user', None)
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # 檢查權限
            user_system = MultiRoleUserSystem()
            if not user_system.check_permission(user.role, resource, PermissionLevel(level)):
                return jsonify({'error': 'Permission denied'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 使用示例
@app.route('/admin/users')
@require_permission('users', 'admin')
def manage_users():
    """用戶管理接口 - 需要管理員權限"""
    return jsonify({'users': []})

@app.route('/dev/api-test')
@require_permission('api_access', 'read')
def api_test():
    """API測試接口 - 需要開發者權限"""
    return jsonify({'test': 'success'})

@app.route('/workspace')
@require_permission('claude_api', 'read')
def workspace():
    """工作台接口 - 所有用戶都可訪問"""
    return jsonify({'workspace': 'loaded'})
'''

def main():
    """生成多角色用戶系統"""
    system = MultiRoleUserSystem()
    
    print("👥 PowerAutomation 多角色用戶權限系統")
    print("=" * 60)
    
    # 顯示角色權限概覽
    print("\n🔐 角色權限概覽:")
    for role in UserRole:
        permissions = system.get_user_permissions(role)
        ui_config = system.get_ui_config(role)
        
        print(f"\n{role.value.upper()} ({ui_config['ui_theme']['badge']}):")
        print(f"   權限數量: {len(permissions)}")
        print(f"   導航項目: {len(ui_config.get('navigation', []))}")
        print(f"   儀表板組件: {len(ui_config.get('dashboard_widgets', []))}")
        
        # 顯示關鍵權限
        key_permissions = [p for p in permissions if p.level in [PermissionLevel.ADMIN, PermissionLevel.WRITE]][:3]
        if key_permissions:
            print(f"   主要權限: {', '.join([p.resource for p in key_permissions])}")
    
    # 生成各角色的HTML界面
    for role in UserRole:
        html_content = system.generate_role_based_html(role)
        filename = f"{role.value}_interface.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"   ✅ 已生成: {filename}")
    
    # 生成權限中間件
    middleware_code = system.generate_permission_middleware()
    with open('permission_middleware.py', 'w', encoding='utf-8') as f:
        f.write(middleware_code)
    
    # 保存完整配置
    full_config = {
        "role_permissions": {
            role.value: [
                {
                    "resource": p.resource,
                    "level": p.level.value,
                    "description": p.description
                }
                for p in permissions
            ]
            for role, permissions in system.role_permissions.items()
        },
        "ui_configurations": {
            role.value: config
            for role, config in system.ui_configurations.items()
        },
        "generated_at": datetime.now().isoformat()
    }
    
    with open('multi_role_system_config.json', 'w', encoding='utf-8') as f:
        json.dump(full_config, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 已生成文件:")
    print(f"   admin_interface.html - 管理員界面")
    print(f"   developer_interface.html - 開發者界面") 
    print(f"   regular_user_interface.html - 一般用戶界面")
    print(f"   permission_middleware.py - 權限中間件")
    print(f"   multi_role_system_config.json - 完整配置")
    
    print(f"\n🎯 關鍵特性:")
    print(f"   ✅ 三層權限體系 (管理員/開發者/一般用戶)")
    print(f"   ✅ 基於角色的UI差異化")
    print(f"   ✅ 細粒度權限控制")
    print(f"   ✅ API配額管理")
    print(f"   ✅ 升級引導機制")

if __name__ == "__main__":
    main()