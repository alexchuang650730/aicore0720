#!/bin/bash

# PowerAutomation 一鍵啟動腳本
# 7/30上線版本

echo "🚀 PowerAutomation 系統啟動中..."
echo "=================================="

# 檢查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝，請先安裝 Python 3.8+"
    exit 1
fi

echo "✅ Python 環境檢查通過"

# 檢查當前目錄
if [[ ! -f "start_powerautomation_system.py" ]]; then
    echo "❌ 請在 PowerAutomation 項目根目錄運行此腳本"
    exit 1
fi

echo "✅ 項目目錄檢查通過"

# 運行主啟動程序
echo "🎯 啟動 PowerAutomation 完整系統..."
python3 start_powerautomation_system.py

echo ""
echo "👋 PowerAutomation 已退出"
echo "感謝使用！"