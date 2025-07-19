#!/usr/bin/env python3
"""
簡單的 Manus 數據提取指南
從一個 replay URL 獲取所有任務
"""

print("""
🚀 Manus 數據提取步驟

1. 在 Chrome 中打開您的 replay URL:
   https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1

2. 打開開發者工具 (F12) -> Console

3. 運行以下代碼提取所有任務:

=== 複製下面的代碼 ===

// 提取左側任務列表
const tasks = [];
document.querySelectorAll('.task-list-item, [class*="conversation"], [class*="task"]').forEach((item, index) => {
    const title = item.innerText.split('\\n')[0];
    const link = item.querySelector('a');
    
    // 構建分享 URL
    let shareUrl = '';
    if (link && link.href.includes('/app/')) {
        const taskId = link.href.split('/app/')[1];
        shareUrl = `https://manus.im/share/${taskId}?replay=1`;
    }
    
    tasks.push({
        index: index,
        title: title,
        shareUrl: shareUrl
    });
});

// 生成 replay_urls.txt 內容
const urlsContent = tasks
    .filter(t => t.shareUrl)
    .map(t => `# ${t.title}\\n${t.shareUrl}`)
    .join('\\n\\n');

// 複製到剪貼板
copy(urlsContent);

console.log(`✅ 已複製 ${tasks.length} 個任務的 replay URLs 到剪貼板！`);
console.log('請將內容貼到 replay_urls.txt 文件中');

=== 代碼結束 ===

4. 將剪貼板內容貼到 replay_urls.txt

5. 運行收集腳本:
   python3 collect_manus_data.py
""")

# 創建更簡單的提取腳本
with open('extract_manus_js.txt', 'w') as f:
    f.write("""// Manus 任務提取腳本
// 在 Manus replay 頁面的 Console 中運行

(() => {
    // 方法1: 從側邊欄提取
    const tasks = [];
    
    // 嘗試各種選擇器
    const selectors = [
        '.conversation-list-item',
        '.task-item',
        '.sidebar-item',
        '[data-testid="conversation-item"]',
        '.chat-history-item'
    ];
    
    let items = [];
    for (const selector of selectors) {
        items = document.querySelectorAll(selector);
        if (items.length > 0) break;
    }
    
    if (items.length === 0) {
        // 方法2: 從任何可能包含任務的元素提取
        items = document.querySelectorAll('[class*="item"]:has(a[href*="/app/"])');
    }
    
    items.forEach((item, index) => {
        const text = item.innerText.trim();
        const title = text.split('\\n')[0];
        
        // 提取任務 ID
        const link = item.querySelector('a[href*="/app/"]');
        if (link) {
            const href = link.href;
            const match = href.match(/\\/app\\/([^\\/?]+)/);
            if (match) {
                const taskId = match[1];
                const shareUrl = `https://manus.im/share/${taskId}?replay=1`;
                
                tasks.push({
                    index: index + 1,
                    title: title || `任務 ${index + 1}`,
                    taskId: taskId,
                    shareUrl: shareUrl
                });
            }
        }
    });
    
    if (tasks.length === 0) {
        console.error('未找到任務，請確保您在 Manus replay 頁面');
        return;
    }
    
    // 生成 URLs
    const urls = tasks.map(t => t.shareUrl).join('\\n');
    
    // 複製到剪貼板
    copy(urls);
    
    console.log(`✅ 成功提取 ${tasks.length} 個任務！`);
    console.log('URLs 已複製到剪貼板');
    console.table(tasks);
})();
""")

print("\n💡 JavaScript 代碼已保存到 extract_manus_js.txt")