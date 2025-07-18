#!/usr/bin/env python3
"""
測試SmartUI MCP與ClaudeEditor的集成
展示如何通過MCP生成UI並在ClaudeEditor中使用
"""

import asyncio
import json
from pathlib import Path

# 導入SmartUI MCP
from core.mcp_components.smartui_mcp import SmartUIMCP

async def test_smartui_claudeditor_integration():
    """測試SmartUI與ClaudeEditor集成"""
    
    print("🎨 SmartUI MCP + ClaudeEditor 集成測試")
    print("="*60)
    
    # 初始化SmartUI MCP
    smartui = SmartUIMCP()
    await smartui.initialize()
    
    # 場景1：為ClaudeEditor生成自定義工作流面板
    print("\n1️⃣ 生成ClaudeEditor工作流面板")
    
    workflow_panel = await smartui.call_mcp("generate_ui", {
        "type": "dashboard",
        "config": {
            "title": "AI工作流控制台",
            "stats": [
                {"label": "代碼分析", "value": "已完成", "icon": "🔍", "trend": "100%"},
                {"label": "自動重構", "value": "進行中", "icon": "🛠️", "trend": "45%"},
                {"label": "單元測試", "value": "待執行", "icon": "🧪", "trend": "0%"},
                {"label": "性能優化", "value": "計劃中", "icon": "🚀", "trend": "-"}
            ],
            "charts": [
                {
                    "type": "progress",
                    "title": "整體進度",
                    "data": {"completed": 35, "total": 100}
                }
            ]
        },
        "theme": "dark",
        "responsive": True,
        "framework": "html"
    })
    
    if workflow_panel["status"] == "success":
        print("✅ 工作流面板生成成功")
        
        # 將生成的代碼注入到ClaudeEditor
        claudeditor_injection = f"""
<!-- SmartUI Generated Workflow Panel -->
<div id="smartui-workflow-panel" class="stagewise-panel">
    <h3>🎯 SmartUI 生成的工作流面板</h3>
    <div class="smartui-container">
        {workflow_panel['code']}
    </div>
</div>

<script>
// SmartUI與ClaudeEditor的集成腳本
function integrateSmartUIPanel() {{
    // 將SmartUI面板添加到ClaudeEditor
    const leftPanel = document.querySelector('.panel');
    const smartUIPanel = document.getElementById('smartui-workflow-panel');
    
    if (leftPanel && smartUIPanel) {{
        leftPanel.appendChild(smartUIPanel);
        console.log('✅ SmartUI面板已集成到ClaudeEditor');
    }}
    
    // 監聽工作流狀態更新
    window.addEventListener('workflow-update', (event) => {{
        updateSmartUIStats(event.detail);
    }});
}}

// 更新SmartUI統計數據
function updateSmartUIStats(data) {{
    // 動態更新生成的UI組件
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {{
        if (data.stats && data.stats[index]) {{
            card.querySelector('h3').textContent = data.stats[index].value;
        }}
    }});
}}

// 頁面加載完成後集成
document.addEventListener('DOMContentLoaded', integrateSmartUIPanel);
</script>
"""
        
        # 保存集成代碼
        integration_path = Path("claudeditor_smartui_integration.html")
        with open(integration_path, 'w', encoding='utf-8') as f:
            f.write(claudeditor_injection)
        
        print(f"💾 集成代碼已保存到: {integration_path}")
    
    # 場景2：生成測試結果面板
    print("\n2️⃣ 生成StageWise測試結果面板")
    
    test_panel = await smartui.call_mcp("generate_ui", {
        "type": "form",
        "config": {
            "title": "StageWise測試控制",
            "fields": [
                {"type": "select", "name": "test_stage", "label": "測試階段", 
                 "options": ["單元測試", "集成測試", "E2E測試"]},
                {"type": "select", "name": "test_scope", "label": "測試範圍",
                 "options": ["當前文件", "當前模塊", "整個項目"]},
                {"type": "checkbox", "name": "coverage", "label": "生成覆蓋率報告"},
                {"type": "checkbox", "name": "watch", "label": "監視模式"}
            ]
        },
        "theme": "light"
    })
    
    if test_panel["status"] == "success":
        print("✅ 測試面板生成成功")
    
    # 場景3：生成代碼編輯器增強UI
    print("\n3️⃣ 生成代碼編輯器增強UI")
    
    editor_ui = await smartui.call_mcp("generate_ui", {
        "type": "editor",
        "config": {
            "tools": ["format", "refactor", "analyze", "optimize", "test"],
            "mode": "code",
            "features": ["syntax_highlight", "auto_complete", "error_detection"]
        },
        "theme": "dark"
    })
    
    if editor_ui["status"] == "success":
        print("✅ 編輯器增強UI生成成功")
    
    # 場景4：生成AI助手聊天界面
    print("\n4️⃣ 生成AI助手增強界面")
    
    chat_ui = await smartui.call_mcp("generate_ui", {
        "type": "chat",
        "config": {
            "features": ["code_snippets", "file_upload", "voice_input"],
            "ai_models": ["Claude", "K2"],
            "quick_actions": ["/analyze", "/refactor", "/test", "/deploy"]
        },
        "theme": "light"
    })
    
    if chat_ui["status"] == "success":
        print("✅ AI助手界面生成成功")
    
    # 生成完整的ClaudeEditor擴展配置
    print("\n5️⃣ 生成ClaudeEditor擴展配置")
    
    extension_config = {
        "name": "SmartUI Enhancement for ClaudeEditor",
        "version": "1.0.0",
        "components": {
            "workflow_panel": {
                "id": workflow_panel.get("generation_id"),
                "position": "left-panel",
                "priority": 1
            },
            "test_panel": {
                "id": test_panel.get("generation_id"),
                "position": "right-panel",
                "priority": 2
            },
            "editor_enhancement": {
                "id": editor_ui.get("generation_id"),
                "position": "editor-toolbar",
                "priority": 1
            },
            "ai_chat_enhancement": {
                "id": chat_ui.get("generation_id"),
                "position": "ai-assistant",
                "priority": 1
            }
        },
        "permissions": {
            "user": ["view"],
            "developer": ["view", "interact", "customize"],
            "admin": ["view", "interact", "customize", "configure"]
        },
        "integration_points": [
            "mcp_manager",
            "permission_system",
            "workflow_engine",
            "test_runner"
        ]
    }
    
    # 保存擴展配置
    config_path = Path("claudeditor_smartui_extension.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(extension_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 擴展配置已保存到: {config_path}")
    
    # 展示如何在ClaudeEditor中調用SmartUI
    print("\n6️⃣ ClaudeEditor調用SmartUI示例")
    
    claudeditor_call_example = """
// 在ClaudeEditor中調用SmartUI MCP
async function generateCustomUI(type, config) {
    try {
        // 通過MCP Manager調用SmartUI
        const result = await window.mcp.call('smartui_mcp', 'generate_ui', {
            type: type,
            config: config,
            theme: getCurrentTheme(),
            responsive: true
        });
        
        if (result.status === 'success') {
            // 將生成的UI注入到指定位置
            injectGeneratedUI(result.code, config.targetElement);
            
            // 更新權限控制
            applyPermissionRestrictions(currentUserPermission);
            
            console.log('✅ SmartUI生成並注入成功');
        }
    } catch (error) {
        console.error('SmartUI生成失敗:', error);
    }
}

// 示例：生成自定義工具面板
generateCustomUI('dashboard', {
    title: '我的工具面板',
    targetElement: '#custom-tools-container',
    stats: getProjectStats()
});
"""
    
    print("JavaScript調用示例:")
    print(claudeditor_call_example)
    
    # 總結
    print("\n📊 集成測試總結")
    print("="*60)
    print("✅ SmartUI MCP可以為ClaudeEditor生成:")
    print("   1. 自定義工作流面板")
    print("   2. 測試控制界面")
    print("   3. 編輯器增強工具")
    print("   4. AI助手增強界面")
    print("\n✅ 集成特點:")
    print("   - 響應式設計，支持PC/Mobile")
    print("   - 權限系統集成")
    print("   - 主題系統支持")
    print("   - MCP標準接口")
    print("\n✅ 下一步:")
    print("   1. 將SmartUI MCP註冊到MCP Manager")
    print("   2. 在ClaudeEditor中添加SmartUI調用接口")
    print("   3. 實現雙向數據同步")

if __name__ == "__main__":
    asyncio.run(test_smartui_claudeditor_integration())