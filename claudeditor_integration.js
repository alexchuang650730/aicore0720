
// ClaudeEditor與PowerAutomation集成代碼
class ClaudeEditorPowerAutomationBridge {
    constructor() {
        this.mcp = window.mcp || {};
        this.smartUI = window.smartUI || {};
        this.permissions = window.currentUserPermission || 'user';
    }
    
    // 初始化集成
    async initialize() {
        console.log('🚀 初始化ClaudeEditor-PowerAutomation橋接');
        
        // 1. 註冊MCP調用接口
        this.registerMCPHandlers();
        
        // 2. 設置SmartUI生成規則
        this.setupSmartUIRules();
        
        // 3. 綁定UI事件到MCP
        this.bindUIEvents();
        
        console.log('✅ 橋接初始化完成');
    }
    
    // 註冊MCP處理器
    registerMCPHandlers() {
        // AI模型控制 -> Router MCP
        this.mcp.handlers['model_switch'] = async (model) => {
            return await this.callMCP('router_mcp', 'route', {
                target_model: model,
                user_permission: this.permissions
            });
        };
        
        // 工作流執行 -> Workflow MCP
        this.mcp.handlers['execute_workflow'] = async (workflow) => {
            return await this.callMCP('workflow_mcp', 'execute', {
                workflow_type: workflow,
                context: this.getContext()
            });
        };
        
        // AI對話 -> K2 Chat MCP
        this.mcp.handlers['chat'] = async (message) => {
            return await this.callMCP('k2_chat_mcp', 'chat', {
                messages: [{role: 'user', content: message}],
                use_k2: this.shouldUseK2()
            });
        };
    }
    
    // 設置SmartUI規則
    setupSmartUIRules() {
        this.smartUI.rules = {
            // 權限感知生成
            permission_aware: (component, permission) => {
                if (permission === 'user' && component.requires === 'developer') {
                    return { ...component, disabled: true, tooltip: '需要開發者權限' };
                }
                return component;
            },
            
            // 響應式適配
            responsive_adapt: (component, screenSize) => {
                if (screenSize < 768) {
                    return { ...component, layout: 'mobile', simplified: true };
                }
                return component;
            },
            
            // 增強但不破壞
            enhance_preserve: (component, enhancement) => {
                return {
                    ...component,
                    enhanced_features: enhancement,
                    original_preserved: true
                };
            }
        };
    }
    
    // 綁定UI事件
    bindUIEvents() {
        // 模型切換
        document.querySelectorAll('.model-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const model = e.target.dataset.model;
                const result = await this.mcp.handlers['model_switch'](model);
                this.updateUIWithSmartUI(result);
            });
        });
        
        // 工作流執行
        document.querySelectorAll('.workflow-item').forEach(item => {
            item.addEventListener('click', async (e) => {
                const workflow = e.target.dataset.workflow;
                const result = await this.mcp.handlers['execute_workflow'](workflow);
                this.updateWorkflowStatus(result);
            });
        });
    }
    
    // 調用MCP
    async callMCP(component, method, params) {
        try {
            // 實際調用PowerAutomation MCP
            const result = await fetch('/api/mcp/call', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ component, method, params })
            });
            return await result.json();
        } catch (error) {
            console.error('MCP調用失敗:', error);
            return { status: 'error', message: error.message };
        }
    }
    
    // 使用SmartUI更新界面
    updateUIWithSmartUI(data) {
        // 調用SmartUI生成增強UI
        const enhancement = this.smartUI.generateEnhancement(data);
        
        // 應用增強但保持原有結構
        this.smartUI.applyEnhancement(enhancement, {
            preserve_layout: true,
            animate: true
        });
    }
    
    // 判斷是否使用K2
    shouldUseK2() {
        // 基於路由策略判斷
        return this.currentModel === 'k2' || this.costOptimizationEnabled;
    }
    
    // 獲取當前上下文
    getContext() {
        return {
            user_permission: this.permissions,
            current_file: window.currentFile,
            editor_content: window.monacoEditor?.getValue(),
            screen_size: window.innerWidth
        };
    }
}

// 初始化橋接
document.addEventListener('DOMContentLoaded', () => {
    const bridge = new ClaudeEditorPowerAutomationBridge();
    bridge.initialize();
    window.powerAutomationBridge = bridge;
});
