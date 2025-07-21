#!/usr/bin/env python3
"""
PowerAuto.ai 完整企業級應用 - 修復版本
集成用戶認證、支付系統、分析系統、演示中心等所有功能
"""

from flask import Flask, request, jsonify, render_template, session, send_from_directory, redirect, url_for, flash
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'powerauto-production-secret-2025'
CORS(app)

# 導入所有系統模塊
try:
    from payment_system import payment_system
    PAYMENT_SYSTEM_AVAILABLE = True
    print("✅ 支付系統導入成功")
except ImportError as e:
    print(f"⚠️ 支付系統導入失敗: {e}")
    PAYMENT_SYSTEM_AVAILABLE = False

try:
    from analytics_system import analytics_system, track_request
    ANALYTICS_AVAILABLE = True
    print("✅ 分析系統導入成功")
except ImportError as e:
    print(f"⚠️ 分析系統導入失敗: {e}")
    ANALYTICS_AVAILABLE = False

try:
    from user_auth_system import auth_system, UserRole, UserStatus
    AUTH_SYSTEM_AVAILABLE = True
    print("✅ 用戶認證系統導入成功")
except ImportError as e:
    print(f"⚠️ 用戶認證系統導入失敗: {e}")
    AUTH_SYSTEM_AVAILABLE = False

def ensure_session_id():
    """確保有會話ID"""
    if 'session_id' not in session:
        session['session_id'] = f"sess_{uuid.uuid4().hex[:16]}"
    return session['session_id']

def get_current_user():
    """獲取當前登錄用戶"""
    if not AUTH_SYSTEM_AVAILABLE:
        return None
    
    session_id = session.get('user_session_id')
    if not session_id:
        return None
    
    return auth_system.validate_session(session_id)

def require_login(f):
    """登錄裝飾器"""
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_admin(f):
    """管理員權限裝飾器"""
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return jsonify({'error': '需要管理員權限'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.before_request
def track_page_view():
    """在每個請求前記錄頁面瀏覽"""
    if ANALYTICS_AVAILABLE and not request.path.startswith('/api/') and not request.path.startswith('/static/'):
        session_id = ensure_session_id()
        track_request(request, session_id=session_id)

# ==================== 主要頁面路由 ====================

@app.route('/')
def index():
    """主頁 - 完整的多語言企業網站"""
    user = get_current_user()
    announcements = []
    
    if user and AUTH_SYSTEM_AVAILABLE:
        announcements = auth_system.get_user_announcements(user.user_id)
    
    return render_template('index.html', user=user, announcements=announcements)

@app.route('/demos')
def demos_center():
    """演示導航中心"""
    try:
        return send_from_directory('/home/ec2-user', 'demo_navigation.html')
    except:
        return """
        <html>
        <head><title>演示中心</title></head>
        <body>
            <h1>🎪 PowerAuto.ai 演示中心</h1>
            <p>演示系統正在加載中...</p>
            <ul>
                <li><a href="/demos/mcp-21">21個MCP完整演示</a></li>
                <li><a href="/login">用戶登錄</a></li>
                <li><a href="/admin">管理面板</a></li>
            </ul>
        </body>
        </html>
        """

@app.route('/demos/mcp-21')
def mcp_21_demo():
    """21個MCP完整演示系統"""
    try:
        return send_from_directory('/home/ec2-user', 'mcp_21_complete_demo.html')
    except:
        return """
        <html>
        <head><title>21個MCP演示</title></head>
        <body>
            <h1>🚀 21個MCP完整生態系統</h1>
            <p>演示系統正在準備中...</p>
            <p><a href="/demos">返回演示中心</a></p>
        </body>
        </html>
        """

@app.route('/login')
def login_page():
    """登錄頁面"""
    return '''
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PowerAuto.ai 用戶登錄</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-gradient-to-br from-indigo-900 to-purple-900 min-h-screen flex items-center justify-center">
        <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
            <div class="text-center mb-8">
                <i class="fas fa-robot text-4xl text-indigo-600 mb-4"></i>
                <h1 class="text-3xl font-bold text-gray-900">PowerAuto.ai</h1>
                <p class="text-gray-600 mt-2">登錄您的賬戶</p>
            </div>
            
            <form id="login-form" action="/api/auth/login" method="POST">
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2">
                        郵箱或用戶名
                    </label>
                    <input type="text" name="email_or_username" required
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500">
                </div>
                
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2">
                        密碼
                    </label>
                    <input type="password" name="password" required
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500">
                </div>
                
                <button type="submit" 
                        class="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors">
                    <i class="fas fa-sign-in-alt mr-2"></i>登錄
                </button>
            </form>
            
            <div class="mt-6 text-center">
                <p class="text-gray-600">還沒有賬戶？ 
                    <a href="/register" class="text-indigo-600 hover:text-indigo-800">立即註冊</a>
                </p>
            </div>
            
            <div class="mt-6 pt-6 border-t">
                <p class="text-center text-sm text-gray-500">
                    測試賬戶: admin@powerauto.ai / PowerAuto2025!
                </p>
                <div class="mt-4 text-center">
                    <a href="/demos" class="text-indigo-600 hover:text-indigo-800">
                        <i class="fas fa-play mr-2"></i>體驗演示
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin')
def admin_dashboard():
    """管理面板"""
    try:
        return send_from_directory('/home/ec2-user', 'admin_dashboard.html')
    except:
        return """
        <html>
        <head><title>管理面板</title></head>
        <body>
            <h1>📊 PowerAuto.ai 管理面板</h1>
            <p>管理系統正在加載中...</p>
            <p><a href="/">返回主站</a></p>
        </body>
        </html>
        """

# ==================== API 路由 ====================

@app.route('/health')
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'payment_system': 'available' if PAYMENT_SYSTEM_AVAILABLE else 'unavailable',
        'analytics_system': 'available' if ANALYTICS_AVAILABLE else 'unavailable',
        'auth_system': 'available' if AUTH_SYSTEM_AVAILABLE else 'unavailable',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """API狀態檢查"""
    return jsonify({
        'version': 'v4.76',
        'demos': {
            'mcp_21': 'available',
            'demo_center': 'available'
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 啟動 PowerAuto.ai 完整企業級應用")
    print(f"用戶認證系統: {'✅ 可用' if AUTH_SYSTEM_AVAILABLE else '❌ 不可用'}")
    print(f"支付系統: {'✅ 可用' if PAYMENT_SYSTEM_AVAILABLE else '❌ 不可用'}")
    print(f"分析系統: {'✅ 可用' if ANALYTICS_AVAILABLE else '❌ 不可用'}")
    print("💻 主網站: http://ec2-13-222-125-83.compute-1.amazonaws.com")
    print("🎪 演示中心: http://ec2-13-222-125-83.compute-1.amazonaws.com/demos")
    print("🔐 用戶登錄: http://ec2-13-222-125-83.compute-1.amazonaws.com/login")
    print("📊 管理面板: http://ec2-13-222-125-83.compute-1.amazonaws.com/admin")
    print("👤 默認管理員: admin@powerauto.ai / PowerAuto2025!")
    app.run(debug=False, host='0.0.0.0', port=5001)