#!/bin/bash
# 停止 PowerAutomation v4.75 服務

if [ -f "/Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.75/.demo_server.pid" ]; then
    PID=$(cat "/Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.75/.demo_server.pid")
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "✅ 演示服務器已停止"
    fi
    rm "/Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.75/.demo_server.pid"
fi

echo "✅ 所有服務已停止"
