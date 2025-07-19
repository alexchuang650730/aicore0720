/**
 * PowerAutomation Driver API for ClaudeEditor
 * 讓PowerAutomation Core完全驅動ClaudeEditor的API接口
 */

class PowerAutomationDriverAPI {
    constructor() {
        this.driverId = null;
        this.registrationId = null;
        this.isConnected = false;
        this.websocket = null;
        this.powerAutomationEndpoint = 'ws://localhost:8765/powerautomation/driver';
        this.heartbeatInterval = null;
        this.eventCallbacks = new Map();
        
        // 驅動狀態
        this.drivenMode = false;
        this.currentWorkflow = null;
        this.currentGoal = null;
        this.alignmentScore = 92;
        
        console.log('🚀 PowerAutomation Driver API 初始化');
    }

    /**
     * 連接到PowerAutomation Core驅動器
     */
    async connect() {
        try {
            console.log('🔗 正在連接PowerAutomation Core驅動器...');
            
            this.websocket = new WebSocket(this.powerAutomationEndpoint);
            
            this.websocket.onopen = async (event) => {
                console.log('✅ PowerAutomation Driver 連接成功');
                this.isConnected = true;
                await this.registerWithCore();
                this.startHeartbeat();
            };
            
            this.websocket.onmessage = (event) => {
                this.handleDriverMessage(JSON.parse(event.data));
            };
            
            this.websocket.onclose = (event) => {
                console.log('❌ PowerAutomation Driver 連接關閉');
                this.isConnected = false;
                this.drivenMode = false;
                this.stopHeartbeat();
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ PowerAutomation Driver 連接錯誤:', error);
            };
            
        } catch (error) {
            console.error('❌ 連接PowerAutomation Core失敗:', error);
        }
    }

    /**
     * 向PowerAutomation Core註冊ClaudeEditor
     */
    async registerWithCore() {
        try {
            const registrationData = {
                action: 'register_claudeditor',
                data: {
                    name: 'ClaudeEditor v4.8.0',
                    version: '4.8.0',
                    type: 'web_complete',
                    capabilities: [
                        'six_workflows',
                        'dual_ai_mode', 
                        'memory_rag',
                        'goal_alignment',
                        'command_execution',
                        'ui_generation',
                        'code_analysis'
                    ],
                    host: window.location.hostname,
                    port: window.location.port,
                    url: window.location.href,
                    features: {
                        claude_mode: true,
                        k2_mode: true,
                        cost_optimization: '2→8元',
                        pc_mobile_unified: true,
                        memory_rag_enabled: true
                    }
                }
            };
            
            this.sendMessage(registrationData);
            
        } catch (error) {
            console.error('❌ 註冊到PowerAutomation Core失敗:', error);
        }
    }

    /**
     * 處理來自PowerAutomation Core的驅動消息
     */
    handleDriverMessage(message) {
        try {
            console.log('📨 收到PowerAutomation驅動消息:', message);
            
            switch (message.action) {
                case 'registration_response':
                    this.handleRegistrationResponse(message.data);
                    break;
                    
                case 'drive_command':
                    this.handleDriveCommand(message.data);
                    break;
                    
                case 'drive_workflow':
                    this.handleDriveWorkflow(message.data);
                    break;
                    
                case 'drive_goal_update':
                    this.handleDriveGoalUpdate(message.data);
                    break;
                    
                case 'drive_ui_generation':
                    this.handleDriveUIGeneration(message.data);
                    break;
                    
                case 'drive_memory_sync':
                    this.handleDriveMemorySync(message.data);
                    break;
                    
                case 'drive_ai_mode_switch':
                    this.handleDriveAIModeSwitch(message.data);
                    break;
                    
                case 'heartbeat_request':
                    this.sendHeartbeatResponse();
                    break;
                    
                default:
                    console.warn('⚠️ 未知的驅動消息類型:', message.action);
            }
            
        } catch (error) {
            console.error('❌ 處理驅動消息失敗:', error);
        }
    }

    /**
     * 處理註冊響應
     */
    handleRegistrationResponse(data) {
        if (data.success) {
            this.registrationId = data.registration_id;
            this.driverId = data.driver_id;
            this.drivenMode = true;
            
            console.log(`✅ ClaudeEditor已被PowerAutomation Core接管`);
            console.log(`📋 註冊ID: ${this.registrationId}`);
            console.log(`🎯 驅動器ID: ${this.driverId}`);
            
            // 更新UI顯示驅動狀態
            this.updateDrivenModeUI(true);
            
            // 觸發註冊成功事件
            this.triggerEvent('registration_success', data);
            
        } else {
            console.error('❌ PowerAutomation Core註冊失敗:', data.error);
        }
    }

    /**
     * 處理命令驅動
     */
    async handleDriveCommand(data) {
        try {
            console.log('⚡ PowerAutomation驅動命令執行:', data.command);
            
            const result = await this.executeCommand(data.command, data.parameters);
            
            // 回報執行結果
            this.sendMessage({
                action: 'command_result',
                registration_id: this.registrationId,
                data: {
                    command: data.command,
                    result: result,
                    success: true,
                    timestamp: Date.now()
                }
            });
            
            // 更新UI
            this.addMessage(`⚡ PowerAutomation驅動執行: ${data.command}`, 'system');
            
        } catch (error) {
            console.error('❌ 命令執行失敗:', error);
            
            this.sendMessage({
                action: 'command_result',
                registration_id: this.registrationId,
                data: {
                    command: data.command,
                    result: null,
                    success: false,
                    error: error.message,
                    timestamp: Date.now()
                }
            });
        }
    }

    /**
     * 處理工作流驅動
     */
    async handleDriveWorkflow(data) {
        try {
            console.log('🎯 PowerAutomation驅動工作流啟動:', data.workflow_type);
            
            this.currentWorkflow = data.workflow_id;
            this.currentGoal = data.goal_id;
            
            // 在UI中啟動對應的工作流
            const workflowElement = this.findWorkflowElement(data.workflow_type);
            if (workflowElement) {
                // 移除其他工作流的active狀態
                document.querySelectorAll('.workflow-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // 啟動目標工作流
                workflowElement.classList.add('active');
                this.updateCurrentWorkflow(data.workflow_type);
            }
            
            // 更新目標對齊度
            this.alignmentScore = 85; // 新工作流開始時的對齊度
            this.updateAlignmentScore();
            
            // 在聊天中顯示
            this.addMessage(
                `🎯 PowerAutomation啟動工作流: ${data.workflow_type}<br>` +
                `📋 工作流ID: ${data.workflow_id}<br>` +
                `🎯 目標ID: ${data.goal_id}<br>` +
                `📝 用戶目標: ${data.user_goal}`,
                'system'
            );
            
            // 回報工作流啟動成功
            this.sendMessage({
                action: 'workflow_started',
                registration_id: this.registrationId,
                data: {
                    workflow_id: data.workflow_id,
                    goal_id: data.goal_id,
                    workflow_type: data.workflow_type,
                    success: true,
                    timestamp: Date.now()
                }
            });
            
        } catch (error) {
            console.error('❌ 工作流啟動失敗:', error);
        }
    }

    /**
     * 處理目標更新驅動
     */
    async handleDriveGoalUpdate(data) {
        try {
            console.log('📊 PowerAutomation驅動目標更新:', data);
            
            // 更新對齊度
            if (data.alignment_score !== undefined) {
                this.alignmentScore = data.alignment_score;
                this.updateAlignmentScore();
            }
            
            // 更新進度
            if (data.progress !== undefined) {
                // 更新UI中的進度顯示
                this.updateProgress(data.progress);
            }
            
            // 顯示反饋
            if (data.feedback) {
                this.addMessage(`📊 目標更新: ${data.feedback}`, 'system');
            }
            
        } catch (error) {
            console.error('❌ 目標更新失敗:', error);
        }
    }

    /**
     * 處理AI模式切換驅動
     */
    async handleDriveAIModeSwitch(data) {
        try {
            console.log('🤖 PowerAutomation驅動AI模式切換:', data.mode);
            
            // 切換AI模式
            if (typeof switchMode === 'function') {
                switchMode(data.mode);
            }
            
            this.addMessage(
                `🔄 PowerAutomation切換AI模式: ${data.mode === 'claude' ? 'Claude' : 'K2中文'}`,
                'system'
            );
            
        } catch (error) {
            console.error('❌ AI模式切換失敗:', error);
        }
    }

    /**
     * 處理記憶同步驅動
     */
    async handleDriveMemorySync(data) {
        try {
            console.log('🧠 PowerAutomation驅動記憶同步:', data.sync_type);
            
            if (data.sync_type === 'to_claudeditor' && data.memories) {
                // 從PowerAutomation Core接收記憶數據
                for (const memory of data.memories) {
                    // 將記憶內容顯示在UI中
                    this.addMessage(
                        `🧠 記憶同步: ${memory.content}`,
                        'memory'
                    );
                }
            }
            
        } catch (error) {
            console.error('❌ 記憶同步失敗:', error);
        }
    }

    /**
     * 執行命令
     */
    async executeCommand(command, parameters = {}) {
        try {
            // 模擬命令執行
            const commandMap = {
                'analyze_code': () => this.analyzeCode(parameters),
                'generate_ui': () => this.generateUI(parameters),
                'run_tests': () => this.runTests(parameters),
                'deploy': () => this.deploy(parameters),
                'refactor': () => this.refactor(parameters)
            };
            
            if (commandMap[command]) {
                return await commandMap[command]();
            } else {
                throw new Error(`不支持的命令: ${command}`);
            }
            
        } catch (error) {
            throw error;
        }
    }

    /**
     * 發送消息到PowerAutomation Core
     */
    sendMessage(message) {
        if (this.websocket && this.isConnected) {
            this.websocket.send(JSON.stringify(message));
        }
    }

    /**
     * 發送心跳響應
     */
    sendHeartbeatResponse() {
        this.sendMessage({
            action: 'heartbeat_response',
            registration_id: this.registrationId,
            data: {
                status: 'active',
                alignment_score: this.alignmentScore,
                current_workflow: this.currentWorkflow,
                current_goal: this.currentGoal,
                timestamp: Date.now()
            }
        });
    }

    /**
     * 啟動心跳
     */
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            this.sendHeartbeatResponse();
        }, 30000); // 30秒心跳
    }

    /**
     * 停止心跳
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    /**
     * 更新驅動模式UI
     */
    updateDrivenModeUI(isDriven) {
        // 在header添加驅動狀態指示
        const header = document.querySelector('.header');
        if (header && isDriven) {
            const drivenIndicator = document.createElement('div');
            drivenIndicator.innerHTML = `
                <div style="background: #28a745; color: white; padding: 8px 16px; border-radius: 20px; 
                           margin: 10px auto; width: fit-content; font-weight: 600;">
                    🎯 PowerAutomation Core 驅動模式
                </div>
            `;
            header.appendChild(drivenIndicator);
        }
    }

    /**
     * 查找工作流元素
     */
    findWorkflowElement(workflowType) {
        const workflowMap = {
            'goal_driven_development': document.querySelector('[onclick*="goal-driven"]'),
            'intelligent_code_generation': document.querySelector('[onclick*="code-generation"]'),
            'automated_testing': document.querySelector('[onclick*="testing"]'),
            'continuous_quality_assurance': document.querySelector('[onclick*="quality"]'),
            'intelligent_deployment': document.querySelector('[onclick*="deployment"]'),
            'adaptive_learning': document.querySelector('[onclick*="learning"]')
        };
        
        return workflowMap[workflowType];
    }

    /**
     * 更新當前工作流顯示
     */
    updateCurrentWorkflow(workflowType) {
        const workflowNames = {
            'goal_driven_development': '目標驅動開發',
            'intelligent_code_generation': '智能代碼生成',
            'automated_testing': '自動化測試',
            'continuous_quality_assurance': '質量保證',
            'intelligent_deployment': '智能部署',
            'adaptive_learning': '自適應學習'
        };
        
        const currentWorkflowElement = document.getElementById('current-workflow');
        if (currentWorkflowElement) {
            currentWorkflowElement.textContent = workflowNames[workflowType] || workflowType;
        }
    }

    /**
     * 更新對齊度顯示
     */
    updateAlignmentScore() {
        const alignmentElements = document.querySelectorAll('#alignment-score, #status-alignment');
        alignmentElements.forEach(element => {
            if (element) {
                element.textContent = Math.round(this.alignmentScore) + '%';
            }
        });
    }

    /**
     * 添加消息到聊天區域
     */
    addMessage(content, type = 'system') {
        const messages = document.getElementById('messages');
        if (messages) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = content;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
    }

    /**
     * 註冊事件回調
     */
    on(event, callback) {
        if (!this.eventCallbacks.has(event)) {
            this.eventCallbacks.set(event, []);
        }
        this.eventCallbacks.get(event).push(callback);
    }

    /**
     * 觸發事件
     */
    triggerEvent(event, data) {
        if (this.eventCallbacks.has(event)) {
            this.eventCallbacks.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`事件回調錯誤 ${event}:`, error);
                }
            });
        }
    }

    /**
     * 斷開連接
     */
    disconnect() {
        this.isConnected = false;
        this.drivenMode = false;
        this.stopHeartbeat();
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        console.log('🔌 PowerAutomation Driver API 已斷開');
    }

    // 模擬命令執行方法
    async analyzeCode(parameters) {
        return {
            analysis: '代碼質量: A+',
            suggestions: ['優化性能', '增加註釋', '重構函數'],
            metrics: { quality: 95, performance: 88, maintainability: 92 }
        };
    }

    async generateUI(parameters) {
        return {
            generated: true,
            component: 'React組件已生成',
            files: ['Component.jsx', 'Component.css']
        };
    }

    async runTests(parameters) {
        return {
            passed: 24,
            failed: 1,
            coverage: '87%',
            duration: '2.3s'
        };
    }

    async deploy(parameters) {
        return {
            deployed: true,
            environment: 'production',
            url: 'https://app.example.com'
        };
    }

    async refactor(parameters) {
        return {
            refactored: true,
            improvements: ['性能提升15%', '代碼行數減少20%'],
            files_modified: 5
        };
    }
}

// 全局實例
window.powerAutomationDriver = new PowerAutomationDriverAPI();

// 自動連接到PowerAutomation Core
document.addEventListener('DOMContentLoaded', () => {
    // 等待頁面加載完成後連接
    setTimeout(() => {
        window.powerAutomationDriver.connect();
    }, 1000);
});

console.log('🚀 PowerAutomation Driver API 已載入');