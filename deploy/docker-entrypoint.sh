#!/bin/bash
set -e

# PowerAutomation Docker 入口點腳本

echo "🚀 PowerAutomation Docker 容器啟動..."

# 初始化數據庫
echo "🗄️ 初始化數據庫..."
python3 -c "
import sqlite3
import os
from datetime import datetime

# 創建數據目錄
os.makedirs('/app/data', exist_ok=True)

# 初始化主數據庫
conn = sqlite3.connect('/app/data/powerautomation.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        user_id TEXT,
        status TEXT DEFAULT 'active',
        progress REAL DEFAULT 0.0,
        created_at REAL,
        updated_at REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS workflows (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        user_id TEXT,
        goal_id TEXT,
        status TEXT DEFAULT 'pending',
        progress REAL DEFAULT 0.0,
        started_at REAL,
        completed_at REAL,
        result TEXT,
        FOREIGN KEY (goal_id) REFERENCES goals (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        id TEXT PRIMARY KEY,
        command TEXT NOT NULL,
        user_id TEXT,
        workflow_id TEXT,
        result TEXT,
        status TEXT DEFAULT 'pending',
        executed_at REAL,
        FOREIGN KEY (workflow_id) REFERENCES workflows (id)
    )
''')

conn.commit()
conn.close()

# 初始化會員數據庫
conn = sqlite3.connect('/app/data/members.db')
cursor = conn.cursor()

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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        token TEXT UNIQUE,
        device_info TEXT,
        ip_address TEXT,
        expires_at REAL,
        created_at REAL,
        last_accessed REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

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
        created_at REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

conn.commit()
conn.close()

# 初始化記憶數據庫
conn = sqlite3.connect('/app/data/memory.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        content TEXT NOT NULL,
        memory_type TEXT DEFAULT 'semantic',
        importance REAL DEFAULT 0.5,
        tags TEXT DEFAULT '[]',
        embedding BLOB,
        created_at REAL,
        accessed_at REAL,
        access_count INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS memory_contexts (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        context_name TEXT NOT NULL,
        context_data TEXT,
        created_at REAL,
        updated_at REAL
    )
''')

conn.commit()
conn.close()

print('✅ 數據庫初始化完成')
"

# 等待依賴服務
echo "⏳ 等待依賴服務..."
while ! nc -z redis 6379; do
    echo "等待 Redis..."
    sleep 2
done
echo "✅ Redis 連接成功"

if [ -n "$POSTGRES_HOST" ]; then
    while ! nc -z postgres 5432; do
        echo "等待 PostgreSQL..."
        sleep 2
    done
    echo "✅ PostgreSQL 連接成功"
fi

# 設置環境變量
export PYTHONPATH=/app:/app/core:/app/mcp_server:/app/goal_alignment_system
export POWERAUTOMATION_ROOT=/app

# 啟動 Supervisor
echo "🔧 啟動 Supervisor..."
supervisord -c /app/deploy/supervisord.conf

# 保持容器運行
echo "🎉 PowerAutomation 容器啟動完成!"
echo "🌐 主服務: http://localhost:8000"
echo "🎯 ClaudeEditor: http://localhost:5173"
echo "🔌 MCP 服務: http://localhost:8765"

# 保持前台運行
tail -f /app/logs/supervisord.log