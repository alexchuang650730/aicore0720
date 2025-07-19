#!/bin/bash
# 安裝 Manus 數據收集器的依賴

echo "🚀 安裝 Manus 數據收集系統依賴..."

# 安裝基本依賴
pip3 install selenium beautifulsoup4 requests aiohttp aiofiles

# 安裝 Selenium WebDriver
echo "
📝 注意事項：
1. Chrome 用戶：
   - 確保已安裝 Chrome 瀏覽器
   - 下載 ChromeDriver: https://chromedriver.chromium.org/
   - 將 chromedriver 放到 PATH 中

2. Safari 用戶：
   - 在 Safari 偏好設置 > 高級 中啟用開發者菜單
   - 在開發菜單中啟用'允許遠程自動化'
   - 運行: safaridriver --enable

3. 使用方法：
   - 在 replay_urls.txt 中添加 Manus replay URLs
   - 運行: python3 collect_manus_data.py
   - 選擇您的瀏覽器（chrome/safari）
"

# 創建數據目錄
mkdir -p data/manus_chrome
mkdir -p data/manus_safari

echo "✅ 安裝完成！"