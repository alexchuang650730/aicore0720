#!/usr/bin/env python3
"""
簡單的 Manus 數據收集腳本
使用 Chrome DevTools Protocol 連接到現有瀏覽器
"""

import json
import time
import requests
from pathlib import Path

def check_chrome_debugging():
    """檢查 Chrome 是否在調試模式"""
    try:
        response = requests.get('http://localhost:9222/json')
        if response.status_code == 200:
            print("✅ Chrome 調試模式已啟動")
            return True
    except:
        pass
    
    print("\n" + "="*60)
    print("❌ 未檢測到 Chrome 調試模式")
    print("\n請按以下步驟操作：")
    print("\n1. 完全關閉所有 Chrome 窗口")
    print("\n2. 在終端運行以下命令啟動 Chrome：")
    print('   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222')
    print("\n3. Chrome 啟動後，登錄到 Manus")
    print("\n4. 保持 Chrome 開啟，重新運行此腳本")
    print("="*60)
    return False

def get_chrome_tabs():
    """獲取所有 Chrome 標籤頁"""
    response = requests.get('http://localhost:9222/json')
    return response.json()

def collect_manus_replay(replay_url):
    """收集單個 Manus replay"""
    print(f"\n📥 收集: {replay_url}")
    
    # 獲取所有標籤頁
    tabs = get_chrome_tabs()
    
    # 查找或創建 Manus 標籤頁
    manus_tab = None
    for tab in tabs:
        if 'manus.im' in tab.get('url', ''):
            manus_tab = tab
            break
    
    if not manus_tab:
        print("未找到 Manus 標籤頁，請在 Chrome 中打開 Manus")
        return None
    
    # 導航到 replay URL
    ws_url = manus_tab['webSocketDebuggerUrl']
    
    # 這裡可以使用 websocket 與 Chrome 通信
    # 為簡化，我們提供手動操作指導
    
    print(f"\n請在 Chrome 中：")
    print(f"1. 訪問: {replay_url}")
    print(f"2. 等待頁面完全加載")
    print(f"3. 按 Enter 繼續...")
    input()
    
    # 保存提取指導
    output_dir = Path("./manus_data")
    output_dir.mkdir(exist_ok=True)
    
    guide_file = output_dir / "extraction_guide.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(f"""# Manus 數據提取指南

## 手動提取步驟

1. 在 Chrome 開發者工具中（F12）
2. Console 標籤頁
3. 運行以下代碼提取數據：

```javascript
// 提取所有消息
const messages = [];
document.querySelectorAll('[class*="message"]').forEach(el => {{
    const role = el.querySelector('[class*="role"]')?.innerText || 'unknown';
    const content = el.querySelector('[class*="content"]')?.innerText || el.innerText;
    messages.push({{role, content}});
}});

// 複製到剪貼板
copy(JSON.stringify({{
    url: '{replay_url}',
    messages: messages,
    extracted_at: new Date().toISOString()
}}, null, 2));

console.log('✅ 數據已複製到剪貼板！');
```

4. 將剪貼板內容保存到 `manus_data/` 目錄下
""")
    
    print(f"\n✅ 提取指南已保存到: {guide_file}")
    return True

def main():
    # 檢查 Chrome
    if not check_chrome_debugging():
        return
    
    # 讀取 URLs
    urls_file = Path("replay_urls.txt")
    if not urls_file.exists():
        with open(urls_file, 'w') as f:
            f.write("# 添加 Manus replay URLs，每行一個\n")
            f.write("https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1\n")
        print(f"\n請在 {urls_file} 中添加要收集的 URLs")
        return
    
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("沒有找到 URLs")
        return
    
    print(f"\n準備收集 {len(urls)} 個 replays")
    
    # 收集數據
    for i, url in enumerate(urls):
        print(f"\n進度: {i+1}/{len(urls)}")
        collect_manus_replay(url)
        
        if i < len(urls) - 1:
            print("\n準備下一個...")
            time.sleep(2)
    
    print("\n✅ 完成！")
    print("請查看 manus_data/extraction_guide.md 獲取手動提取指導")

if __name__ == "__main__":
    main()