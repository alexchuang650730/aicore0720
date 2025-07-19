/**
 * Core-Driven Service
 * ClaudeEditor 作為被驅動的客戶端，接收 PowerAutomation Core 的指令
 */

class CoreDrivenService {
  constructor() {
    this.isConnected = false;
    this.coreConnection = null;
    this.claudeEditorId = null;
    this.messageHandlers = new Map();
    
    // 核心配置
    this.config = {
      coreHost: 'localhost',
      corePort: 8081, // WebSocket 端口
      reconnectAttempts: 5,
      reconnectDelay: 3000,
      heartbeatInterval: 30000
    };
    
    // 註冊消息處理器
    this.registerMessageHandlers();
    
    console.log('🎯 Core-Driven Service 初始化完成');
  }

  /**
   * 連接到 PowerAutomation Core
   */
  async connectToCore() {
    try {
      const wsUrl = `ws://${this.config.coreHost}:${this.config.corePort}`;
      console.log(`📡 連接到 PowerAutomation Core: ${wsUrl}`);
      
      this.coreConnection = new WebSocket(wsUrl);
      
      // 設置連接事件監聽器
      this.setupConnectionHandlers();
      
      // 等待連接建立
      await this.waitForConnection();
      
      console.log('✅ 已成功連接到 PowerAutomation Core');
      return true;
      
    } catch (error) {
      console.error('❌ 連接 PowerAutomation Core 失敗:', error);
      return false;
    }
  }

  /**
   * 設置連接事件處理器
   */
  setupConnectionHandlers() {
    this.coreConnection.onopen = () => {
      console.log('🔗 WebSocket 連接已建立');
      this.isConnected = true;
      this.registerWithCore();
      this.startHeartbeat();
    };

    this.coreConnection.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleCoreMessage(message);
      } catch (error) {
        console.error('❌ 解析 Core 消息失敗:', error);
      }
    };

    this.coreConnection.onclose = () => {
      console.log('📴 與 Core 的連接已斷開');
      this.isConnected = false;
      this.claudeEditorId = null;
      this.attemptReconnect();
    };

    this.coreConnection.onerror = (error) => {
      console.error('❌ WebSocket 連接錯誤:', error);
    };
  }

  /**
   * 向 Core 註冊 ClaudeEditor 實例
   */
  async registerWithCore() {
    try {
      const registrationData = {
        action: 'register_claudeditor',
        params: {
          name: 'ClaudeEditor',
          version: '4.6.9.1',
          host: window.location.hostname,
          port: window.location.port,
          capabilities: [
            'code_editing',
            'file_management',
            'ui_generation',
            'project_management',
            'claude_code_integration'
          ],
          metadata: {
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
          }
        }
      };

      this.sendToCore(registrationData);
      console.log('📋 向 Core 註冊 ClaudeEditor 實例');
      
    } catch (error) {
      console.error('❌ 註冊失敗:', error);
    }
  }

  /**
   * 註冊消息處理器
   */
  registerMessageHandlers() {
    // 註冊成功響應
    this.messageHandlers.set('register_response', (data) => {
      if (data.status === 'success') {
        this.claudeEditorId = data.claudeditor_id;
        console.log(`✅ 註冊成功，ClaudeEditor ID: ${this.claudeEditorId}`);
        this.notifyRegistrationComplete();
      } else {
        console.error('❌ 註冊失敗:', data.message);
      }
    });

    // Core 驅動命令
    this.messageHandlers.set('core_command', (data) => {
      this.handleCoreCommand(data);
    });

    // 工作流執行命令
    this.messageHandlers.set('execute_workflow', (data) => {
      this.handleWorkflowExecution(data);
    });

    // Claude Code 響應處理
    this.messageHandlers.set('handle_claude_code_response', (data) => {
      this.handleClaudeCodeResponse(data);
    });

    // 系統狀態查詢
    this.messageHandlers.set('get_status', (data) => {
      this.handleStatusQuery(data);
    });
  }

  /**
   * 處理來自 Core 的消息
   */
  handleCoreMessage(message) {
    const { type, ...data } = message;
    
    console.log(`📨 收到 Core 消息: ${type}`, data);
    
    const handler = this.messageHandlers.get(type);
    if (handler) {
      handler(data);
    } else {
      console.warn(`⚠️ 未知的消息類型: ${type}`);
    }
  }

  /**
   * 處理 Core 驅動命令
   */
  async handleCoreCommand(data) {
    try {
      const { command, params } = data;
      
      console.log(`🎛️ 執行 Core 命令: ${command}`);
      
      let result;
      
      switch (command) {
        case 'open_file':
          result = await this.openFile(params.filePath);
          break;
          
        case 'save_file':
          result = await this.saveFile(params.filePath, params.content);
          break;
          
        case 'create_project':
          result = await this.createProject(params.projectName, params.template);
          break;
          
        case 'generate_ui':
          result = await this.generateUI(params.description, params.framework);
          break;
          
        case 'switch_model':
          result = await this.switchModel(params.model);
          break;
          
        case 'execute_claude_code':
          result = await this.executeClaudeCode(params.command, params.args);
          break;
          
        default:
          result = {
            success: false,
            error: `未知命令: ${command}`
          };
      }
      
      // 回應 Core
      this.sendToCore({
        action: 'command_response',
        params: {
          command,
          result,
          timestamp: new Date().toISOString()
        }
      });
      
    } catch (error) {
      console.error('❌ 執行 Core 命令失敗:', error);
      this.sendToCore({
        action: 'command_response',
        params: {
          command: data.command,
          result: {
            success: false,
            error: error.message
          },
          timestamp: new Date().toISOString()
        }
      });
    }
  }

  /**
   * 處理工作流執行
   */
  async handleWorkflowExecution(data) {
    try {
      const { workflow_type, params } = data;
      
      console.log(`⚙️ 執行工作流: ${workflow_type}`);
      
      // 根據工作流類型執行相應操作
      let result;
      
      switch (workflow_type) {
        case 'goal_driven_development':
          result = await this.executeGoalDrivenDevelopment(params);
          break;
          
        case 'intelligent_code_generation':
          result = await this.executeIntelligentCodeGeneration(params);
          break;
          
        case 'automated_testing':
          result = await this.executeAutomatedTesting(params);
          break;
          
        case 'quality_assurance':
          result = await this.executeQualityAssurance(params);
          break;
          
        case 'deployment_ops':
          result = await this.executeDeploymentOps(params);
          break;
          
        case 'adaptive_learning':
          result = await this.executeAdaptiveLearning(params);
          break;
          
        default:
          result = {
            success: false,
            error: `未知工作流: ${workflow_type}`
          };
      }
      
      // 回應工作流執行結果
      this.sendToCore({
        action: 'workflow_response',
        params: {
          workflow_type,
          result,
          timestamp: new Date().toISOString()
        }
      });
      
    } catch (error) {
      console.error('❌ 工作流執行失敗:', error);
    }
  }

  /**
   * 處理 Claude Code 響應
   */
  handleClaudeCodeResponse(data) {
    const { original_command, route_result } = data;
    
    console.log(`🤖 處理 Claude Code 響應: ${original_command}`);
    
    // 在 UI 中顯示響應
    this.displayClaudeCodeResponse(original_command, route_result);
    
    // 觸發相應的 UI 更新
    this.triggerUIUpdate('claude_code_response', {
      command: original_command,
      result: route_result
    });
  }

  /**
   * 處理狀態查詢
   */
  handleStatusQuery() {
    const status = {
      claudeditor_id: this.claudeEditorId,
      connected: this.isConnected,
      version: '4.6.9.1',
      capabilities: [
        'code_editing',
        'file_management', 
        'ui_generation',
        'project_management',
        'claude_code_integration'
      ],
      current_state: this.getCurrentState(),
      timestamp: new Date().toISOString()
    };
    
    this.sendToCore({
      action: 'status_response',
      params: { status }
    });
  }

  /**
   * 發送消息到 Core
   */
  sendToCore(message) {
    if (this.isConnected && this.coreConnection) {
      this.coreConnection.send(JSON.stringify(message));
    } else {
      console.warn('⚠️ 未連接到 Core，無法發送消息');
    }
  }

  /**
   * 等待連接建立
   */
  waitForConnection() {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('連接超時'));
      }, 10000);
      
      const checkConnection = () => {
        if (this.isConnected) {
          clearTimeout(timeout);
          resolve();
        } else {
          setTimeout(checkConnection, 100);
        }
      };
      
      checkConnection();
    });
  }

  /**
   * 開始心跳檢測
   */
  startHeartbeat() {
    setInterval(() => {
      if (this.isConnected) {
        this.sendToCore({
          action: 'heartbeat',
          params: {
            claudeditor_id: this.claudeEditorId,
            timestamp: new Date().toISOString()
          }
        });
      }
    }, this.config.heartbeatInterval);
  }

  /**
   * 嘗試重新連接
   */
  async attemptReconnect() {
    let attempts = 0;
    
    while (attempts < this.config.reconnectAttempts) {
      console.log(`🔄 嘗試重新連接 (${attempts + 1}/${this.config.reconnectAttempts})`);
      
      await new Promise(resolve => setTimeout(resolve, this.config.reconnectDelay));
      
      const success = await this.connectToCore();
      if (success) {
        console.log('✅ 重新連接成功');
        return;
      }
      
      attempts++;
    }
    
    console.error('❌ 重新連接失敗，請檢查 PowerAutomation Core 是否運行');
  }

  /**
   * 通知註冊完成
   */
  notifyRegistrationComplete() {
    const event = new CustomEvent('claudeditor:core_registered', {
      detail: {
        claudeditor_id: this.claudeEditorId,
        timestamp: new Date().toISOString()
      }
    });
    
    window.dispatchEvent(event);
  }

  /**
   * 觸發 UI 更新
   */
  triggerUIUpdate(type, data) {
    const event = new CustomEvent('claudeditor:ui_update', {
      detail: { type, data }
    });
    
    window.dispatchEvent(event);
  }

  /**
   * 獲取當前狀態
   */
  getCurrentState() {
    return {
      activeEditor: window.activeEditor || null,
      openFiles: window.openFiles || [],
      currentProject: window.currentProject || null,
      lastActivity: new Date().toISOString()
    };
  }

  // === 具體功能實現方法 ===

  async openFile(filePath) {
    // 實現文件打開邏輯
    console.log(`📂 打開文件: ${filePath}`);
    return { success: true, filePath };
  }

  async saveFile(filePath, content) {
    // 實現文件保存邏輯
    console.log(`💾 保存文件: ${filePath}`);
    return { success: true, filePath, saved: true };
  }

  async createProject(projectName, template) {
    // 實現項目創建邏輯
    console.log(`🚀 創建項目: ${projectName}`);
    return { success: true, projectName, template };
  }

  async generateUI(description, framework) {
    // 實現 UI 生成邏輯
    console.log(`🎨 生成 UI: ${description}`);
    return { success: true, description, framework, generated: true };
  }

  async switchModel(model) {
    // 實現模型切換邏輯
    console.log(`🔄 切換模型: ${model}`);
    return { success: true, model, switched: true };
  }

  async executeClaudeCode(command, args) {
    // 實現 Claude Code 執行邏輯
    console.log(`🤖 執行 Claude Code: ${command}`);
    return { success: true, command, args, executed: true };
  }

  // === 工作流實現方法 ===

  async executeGoalDrivenDevelopment(params) {
    console.log('🎯 執行目標驅動開發');
    return { success: true, workflow: 'goal_driven_development' };
  }

  async executeIntelligentCodeGeneration(params) {
    console.log('🧠 執行智能代碼生成');
    return { success: true, workflow: 'intelligent_code_generation' };
  }

  async executeAutomatedTesting(params) {
    console.log('🧪 執行自動化測試');
    return { success: true, workflow: 'automated_testing' };
  }

  async executeQualityAssurance(params) {
    console.log('✅ 執行質量保證');
    return { success: true, workflow: 'quality_assurance' };
  }

  async executeDeploymentOps(params) {
    console.log('🚀 執行部署運維');
    return { success: true, workflow: 'deployment_ops' };
  }

  async executeAdaptiveLearning(params) {
    console.log('🎓 執行自適應學習');
    return { success: true, workflow: 'adaptive_learning' };
  }

  displayClaudeCodeResponse(command, result) {
    console.log(`📺 顯示 Claude Code 響應: ${command}`, result);
  }
}

// 創建全局實例
const coreDrivenService = new CoreDrivenService();

// 導出服務
export default coreDrivenService;
export { CoreDrivenService };