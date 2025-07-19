// Manus 自動滾動並提取所有任務的腳本
// 在 Manus replay 頁面的 Console 中運行

async function extractAllTasks() {
    console.log('🚀 開始提取所有任務...');
    
    // 找到任務列表容器
    const sidebar = document.querySelector('.sidebar, [class*="task-list"], [class*="conversation-list"]');
    if (!sidebar) {
        console.error('❌ 找不到任務列表');
        return;
    }
    
    const allTasks = new Map(); // 使用 Map 避免重複
    let previousCount = 0;
    let scrollAttempts = 0;
    const maxScrollAttempts = 50; // 最多滾動50次
    
    // 滾動函數
    async function scrollAndCollect() {
        // 收集當前可見的任務
        const items = document.querySelectorAll('[class*="conversation"], [class*="task-item"], .sidebar-item');
        
        items.forEach(item => {
            const link = item.querySelector('a[href*="/app/"]');
            if (link) {
                const href = link.href;
                const match = href.match(/\/app\/([^\/\?]+)/);
                if (match) {
                    const taskId = match[1];
                    const title = item.innerText.split('\n')[0].trim();
                    const shareUrl = `https://manus.im/share/${taskId}?replay=1`;
                    
                    // 使用 taskId 作為 key 避免重複
                    allTasks.set(taskId, {
                        title: title || `任務 ${allTasks.size + 1}`,
                        taskId: taskId,
                        shareUrl: shareUrl
                    });
                }
            }
        });
        
        console.log(`當前收集: ${allTasks.size} 個任務`);
        
        // 滾動到底部
        sidebar.scrollTop = sidebar.scrollHeight;
        
        // 等待新內容加載
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 檢查是否有新任務加載
        if (allTasks.size === previousCount) {
            scrollAttempts++;
            if (scrollAttempts > 3) {
                console.log('✅ 已到達列表底部');
                return false;
            }
        } else {
            scrollAttempts = 0;
            previousCount = allTasks.size;
        }
        
        return scrollAttempts < maxScrollAttempts;
    }
    
    // 先滾動到頂部
    sidebar.scrollTop = 0;
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 開始滾動收集
    let shouldContinue = true;
    while (shouldContinue) {
        shouldContinue = await scrollAndCollect();
    }
    
    // 轉換為數組
    const tasks = Array.from(allTasks.values());
    
    console.log(`\n✅ 總共提取了 ${tasks.length} 個任務！`);
    
    // 生成 replay_urls.txt 內容
    const urlsContent = tasks
        .map((t, i) => `# ${i + 1}. ${t.title}\n${t.shareUrl}`)
        .join('\n\n');
    
    // 複製到剪貼板
    copy(urlsContent);
    
    console.log('📋 所有 replay URLs 已複製到剪貼板！');
    console.log('請將內容貼到 replay_urls.txt 文件中');
    
    // 顯示前10個作為預覽
    console.table(tasks.slice(0, 10));
    console.log(`... 還有 ${Math.max(0, tasks.length - 10)} 個任務`);
    
    return tasks;
}

// 執行提取
extractAllTasks();