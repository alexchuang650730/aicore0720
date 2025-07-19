#!/usr/bin/env python3
"""
測試 Manus 數據收集系統
"""

import requests
from bs4 import BeautifulSoup
import json

def test_manus_replay_structure(replay_url):
    """測試 Manus replay 頁面結構"""
    print(f"測試 URL: {replay_url}")
    
    try:
        # 發送請求
        response = requests.get(replay_url)
        print(f"狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找可能包含數據的結構
            print("\n=== 頁面分析 ===")
            
            # 查找 script 標籤
            scripts = soup.find_all('script')
            print(f"找到 {len(scripts)} 個 script 標籤")
            
            # 查找包含數據的 script
            for i, script in enumerate(scripts):
                if script.string:
                    if any(keyword in script.string for keyword in ['conversation', 'messages', 'replay', '__INITIAL']):
                        print(f"\nScript {i} 包含關鍵數據:")
                        print(script.string[:200] + "...")
            
            # 查找可能的數據容器
            data_containers = soup.find_all(['div', 'section'], {'class': lambda x: x and any(word in x for word in ['message', 'chat', 'conversation'])})
            print(f"\n找到 {len(data_containers)} 個可能的數據容器")
            
            # 保存頁面供分析
            with open('manus_replay_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("\n頁面已保存到 manus_replay_page.html")
            
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    # 測試您提供的 replay URL
    test_url = "https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1"
    test_manus_replay_structure(test_url)