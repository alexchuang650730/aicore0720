#!/bin/bash
# PowerAutomation v4.76 部署腳本

echo "🚀 部署 PowerAutomation v4.76..."

# 檢查系統要求
echo "檢查系統要求..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安裝"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安裝"
    exit 1
fi

echo "✅ 系統要求檢查通過"

# 安裝依賴
echo "安裝依賴..."
npm install
python3 -m pip install -r requirements.txt

# 構建應用
echo "構建應用..."
npm run build

# 運行健康檢查
echo "運行健康檢查..."
npm run health-check

echo "✅ PowerAutomation v4.76 部署完成！"
