#!/bin/bash
# 安裝 ChromeDriver

echo "🚀 安裝 ChromeDriver..."

# 方法1: 使用 Homebrew（推薦）
if command -v brew &> /dev/null; then
    echo "使用 Homebrew 安裝..."
    brew install --cask chromedriver
    
    # macOS 可能需要允許運行
    echo "允許 ChromeDriver 運行..."
    xattr -d com.apple.quarantine $(which chromedriver) 2>/dev/null || true
else
    echo "Homebrew 未安裝"
    echo "請先安裝 Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "或者手動下載 ChromeDriver:"
    echo "1. 訪問 https://chromedriver.chromium.org/"
    echo "2. 下載對應您 Chrome 版本的 ChromeDriver"
    echo "3. 解壓並移動到 /usr/local/bin/"
    echo "4. 運行: chmod +x /usr/local/bin/chromedriver"
fi

echo ""
echo "✅ 完成後，再次運行："
echo "python3 auto_manus_collector.py"