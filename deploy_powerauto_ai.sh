#!/bin/bash

echo "🌐 PowerAuto.ai 本地部署启动"
echo "============================"

# 创建虚拟环境
echo "📦 创建PowerAuto.ai虚拟环境..."
cd /Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.76/website/backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install flask flask-sqlalchemy flask-bcrypt flask-cors stripe pyjwt || {
    echo "❌ 依赖安装失败"
    exit 1
}

# 设置环境变量
export SECRET_KEY="powerauto-ai-local-dev-key"
export DATABASE_URL="sqlite:///powerauto_local.db"
export STRIPE_SECRET_KEY="sk_test_dummy_key"

# 启动后端服务
echo "🚀 启动PowerAuto.ai后端服务..."
# 确保在正确目录且虚拟环境已激活
source venv/bin/activate
python3 -c "
from app import app, db, User, bcrypt
import os

# 确保数据库目录存在
os.makedirs(os.path.dirname('powerauto_local.db'), exist_ok=True)

# 创建数据库表
with app.app_context():
    db.create_all()
    
    # 创建默认管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(
            username='admin',
            email='admin@powerauto.ai',
            password_hash=admin_password,
            role='admin',
            subscription='enterprise',
            api_calls_limit=100000
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ 管理员用户已创建: admin/admin123')
    
    # 创建测试用户
    testuser = User.query.filter_by(username='testuser').first()
    if not testuser:
        test_password = bcrypt.generate_password_hash('test123').decode('utf-8')
        testuser = User(
            username='testuser',
            email='test@powerauto.ai',
            password_hash=test_password,
            role='user',
            subscription='free',
            api_calls_limit=100
        )
        db.session.add(testuser)
        db.session.commit()
        print('✅ 测试用户已创建: testuser/test123')

print('🎉 PowerAuto.ai 数据库初始化完成')
" && echo "✅ 数据库初始化完成"

# 启动Flask应用
echo "🌐 启动PowerAuto.ai网站服务 (http://localhost:5001)..."
source venv/bin/activate
nohup python3 app.py > powerauto_ai.log 2>&1 &

sleep 3

# 检查服务状态
if curl -s http://localhost:5001/api/subscription/plans >/dev/null; then
    echo "✅ PowerAuto.ai 后端API启动成功"
    echo "🌐 访问地址: http://localhost:5001"
    echo "📡 API测试: http://localhost:5001/api/subscription/plans"
    echo ""
    echo "🔑 默认账户:"
    echo "  管理员: admin / admin123"
    echo "  测试用户: testuser / test123"
    echo ""
    echo "🛑 停止服务: pkill -f 'python3 app.py'"
else
    echo "❌ PowerAuto.ai 启动失败，检查日志: cat powerauto_ai.log"
fi