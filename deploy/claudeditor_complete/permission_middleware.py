# PowerAutomation 權限中間件
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
