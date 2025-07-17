const { chromium } = require('playwright');

async function runFinalTest() {
    console.log('🧪 开始 ClaudeEditor v4.7.2 最终测试...\n');
    
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    try {
        // 1. 页面加载测试
        console.log('1️⃣ 测试页面加载...');
        await page.goto('https://ghwzxdop.manus.space/');
        await page.waitForLoadState('networkidle');
        console.log('✅ 页面加载成功');
        
        // 2. 对话功能测试
        console.log('\n2️⃣ 测试对话功能...');
        const userInput = page.locator('input[placeholder*="編程需求"]');
        const sendButton = page.locator('button:has-text("發送")');
        
        await userInput.fill('测试对话功能');
        await sendButton.click();
        await page.waitForTimeout(2000);
        
        const messages = await page.locator('.message').count();
        if (messages > 0) {
            console.log('✅ 对话功能正常');
        } else {
            console.log('❌ 对话功能异常');
        }
        
        // 3. 文件点击编辑测试
        console.log('\n3️⃣ 测试文件点击编辑功能...');
        const firstFile = page.locator('.file-item').first();
        await firstFile.click();
        await page.waitForTimeout(1000);
        
        const editButton = page.locator('button:has-text("編輯")');
        const isEditActive = await editButton.evaluate(el => el.classList.contains('active'));
        if (isEditActive) {
            console.log('✅ 文件点击编辑功能正常');
        } else {
            console.log('❌ 文件点击编辑功能异常');
        }
        
        // 4. Memory RAG监控测试
        console.log('\n4️⃣ 测试Memory RAG监控功能...');
        const memoryRAGButton = page.locator('button:has-text("Memory RAG 監控")');
        await memoryRAGButton.click();
        await page.waitForTimeout(1000);
        
        const modal = page.locator('#memoryRAGModal');
        const isModalVisible = await modal.isVisible();
        if (isModalVisible) {
            console.log('✅ Memory RAG监控功能正常');
            
            // 测试关闭功能
            const closeButton = page.locator('.close-button');
            await closeButton.click();
            await page.waitForTimeout(500);
            
            const isModalHidden = await modal.isHidden();
            if (isModalHidden) {
                console.log('✅ Memory RAG关闭功能正常');
            } else {
                console.log('❌ Memory RAG关闭功能异常');
            }
        } else {
            console.log('❌ Memory RAG监控功能异常');
        }
        
        // 5. 六大工作流折叠测试
        console.log('\n5️⃣ 测试六大工作流折叠功能...');
        const workflowGrid = page.locator('.workflow-grid');
        const isWorkflowHidden = await workflowGrid.isHidden();
        if (isWorkflowHidden) {
            console.log('✅ 六大工作流默认折叠正常');
        } else {
            console.log('❌ 六大工作流默认折叠异常');
        }
        
        // 6. 布局切换测试
        console.log('\n6️⃣ 测试布局切换功能...');
        const dialogButton = page.locator('button:has-text("對話")');
        await dialogButton.click();
        await page.waitForTimeout(500);
        
        const isDialogActive = await dialogButton.evaluate(el => el.classList.contains('active'));
        if (isDialogActive) {
            console.log('✅ 布局切换功能正常');
        } else {
            console.log('❌ 布局切换功能异常');
        }
        
        console.log('\n🎉 ClaudeEditor v4.7.2 最终测试完成！');
        
    } catch (error) {
        console.error('❌ 测试过程中出现错误:', error);
    } finally {
        await browser.close();
    }
}

runFinalTest();

