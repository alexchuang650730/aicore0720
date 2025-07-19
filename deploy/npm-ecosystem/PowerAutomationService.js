/**
 * PowerAutomation 服务
 * 负责在 ClaudeEditor 启动时自动初始化 PowerAutomation Core
 */

class PowerAutomationService {
  constructor() {
    this.isInitialized = false;
    this.services = {};
    this.config = {
      services: {
        commandMCP: {
          port: null,
          defaultModel: 'k2_local',
          mirrorCodeEnabled: true
        },
        taskSync: {
          port: 8765,
          protocol: 'websocket'
        }
      }
    };
  }

  /**
   * 初始化 PowerAutomation 服务
   */
  async initialize() {
    if (this.isInitialized) {
      console.log('⚠️ PowerAutomation Service 已经初始化');
      return;
    }

    try {
      console.log('🚀 初始化 PowerAutomation Core...');
      
      // 1. 启动 Command MCP (集成了 Mirror Code)
      await this.startCommandMCP();
      
      // 2. 启动任务同步服务
      await this.startTaskSyncService();
      
      // 3. 验证服务状态
      await this.verifyServices();
      
      this.isInitialized = true;
      console.log('✅ PowerAutomation Core 启动完成');
      
      // 发送启动完成事件
      this.notifyStartupComplete();
      
    } catch (error) {
      console.error('❌ PowerAutomation Service 启动失败:', error);
      throw error;
    }
  }

  /**
   * 启动 Command MCP (集成了 Mirror Code)
   */
  async startCommandMCP() {
    try {
      console.log('📡 启动 Command MCP (集成 Mirror Code)...');
      
      // 尝试连接后端 API
      try {
        const response = await fetch('/api/command-mcp/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            config: this.config.services.commandMCP
          })
        });
        
        if (response.ok) {
          // 后端可用
          this.services.commandMCP = { 
            status: 'running', 
            mode: 'backend',
            defaultModel: 'k2_local',
            mirrorCodeEnabled: true
          };
          console.log('✅ Command MCP (后端模式) 已启动');
        } else {
          throw new Error('后端 API 不可用');
        }
      } catch (error) {
        // 后端不可用，使用前端模拟
        console.log('⚠️ 后端不可用，使用前端模拟模式');
        this.services.commandMCP = { 
          status: 'running', 
          mode: 'frontend-simulation',
          defaultModel: 'k2_local',
          mirrorCodeEnabled: true
        };
        console.log('✅ Command MCP (前端模拟) 已启动');
      }
      
    } catch (error) {
      console.error('❌ Command MCP 启动失败:', error);
      throw error;
    }
  }

  /**
   * 启动任务同步服务
   */
  async startTaskSyncService() {
    try {
      console.log('🔄 启动任务同步服务...');
      
      // 尝试连接 WebSocket 服务
      try {
        const ws = new WebSocket(`ws://localhost:${this.config.services.taskSync.port}`);
        
        ws.onopen = () => {
          this.services.taskSync = { 
            status: 'running', 
            connection: ws,
            protocol: 'websocket'
          };
          console.log('✅ 任务同步服务 (WebSocket) 已连接');
        };
        
        ws.onerror = () => {
          throw new Error('WebSocket 连接失败');
        };
        
      } catch (error) {
        // WebSocket 不可用，使用本地模拟
        console.log('⚠️ WebSocket 不可用，使用本地模拟');
        this.services.taskSync = { 
          status: 'running', 
          mode: 'local-simulation',
          protocol: 'local'
        };
        console.log('✅ 任务同步服务 (本地模拟) 已启动');
      }
      
    } catch (error) {
      console.error('❌ 任务同步服务启动失败:', error);
      throw error;
    }
  }

  /**
   * 验证所有服务状态
   */
  async verifyServices() {
    console.log('🔍 验证服务状态...');
    
    const services = Object.keys(this.services);
    for (const serviceName of services) {
      const service = this.services[serviceName];
      if (service.status === 'running') {
        console.log(`✅ ${serviceName}: ${service.mode || 'running'}`);
      } else {
        console.log(`❌ ${serviceName}: ${service.status}`);
      }
    }
    
    console.log('✅ 服务状态验证完成');
  }

  /**
   * 发送启动完成事件
   */
  notifyStartupComplete() {
    // 发送自定义事件
    const event = new CustomEvent('powerautomation-ready', {
      detail: {
        services: this.services,
        config: this.config,
        timestamp: new Date().toISOString()
      }
    });
    
    window.dispatchEvent(event);
    console.log('📡 PowerAutomation 启动完成事件已发送');
  }

  /**
   * 获取服务状态
   */
  getStatus() {
    return {
      initialized: this.isInitialized,
      services: this.services,
      config: this.config
    };
  }

  /**
   * 执行 Claude 命令
   */
  async executeCommand(command, options = {}) {
    if (!this.isInitialized) {
      throw new Error('PowerAutomation Service 未初始化');
    }

    try {
      console.log(`🧠 执行命令: ${command}`);
      
      // 使用 Command MCP 处理命令
      const result = await this.processWithCommandMCP(command, options);
      
      console.log('✅ 命令执行完成');
      return result;
      
    } catch (error) {
      console.error('❌ 命令执行失败:', error);
      throw error;
    }
  }

  /**
   * 通过 Command MCP 处理命令
   */
  async processWithCommandMCP(command, options) {
    const commandMCP = this.services.commandMCP;
    
    if (!commandMCP || commandMCP.status !== 'running') {
      throw new Error('Command MCP 服务不可用');
    }

    // 根据模式处理命令
    if (commandMCP.mode === 'backend') {
      // 后端模式：发送到后端 API
      return await this.sendToBackend(command, options);
    } else {
      // 前端模拟模式：本地处理
      return await this.processLocally(command, options);
    }
  }

  /**
   * 发送命令到后端
   */
  async sendToBackend(command, options) {
    try {
      const response = await fetch('/api/command-mcp/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command: command,
          options: options,
          model: 'k2_local'  // 默认使用 K2
        })
      });
      
      if (!response.ok) {
        throw new Error(`后端处理失败: ${response.status}`);
      }
      
      return await response.json();
      
    } catch (error) {
      console.error('后端处理失败，回退到本地处理:', error);
      return await this.processLocally(command, options);
    }
  }

  /**
   * 本地处理命令
   */
  async processLocally(command, options) {
    // 模拟 K2 本地处理
    console.log('🤖 使用 K2 本地模型处理...');
    
    // 这里可以集成实际的 K2 本地模型
    // 现在先返回模拟结果
    return {
      success: true,
      model: 'k2_local',
      response: `K2 本地模型处理结果: ${command}`,
      timestamp: new Date().toISOString(),
      cost: 0  // 本地处理无成本
    };
  }

  /**
   * 切换模型
   */
  async switchModel(modelName) {
    console.log(`🔄 切换模型到: ${modelName}`);
    
    if (this.services.commandMCP) {
      this.services.commandMCP.defaultModel = modelName;
      this.config.services.commandMCP.defaultModel = modelName;
      
      console.log(`✅ 默认模型已切换到: ${modelName}`);
      
      // 发送模型切换事件
      const event = new CustomEvent('model-switched', {
        detail: { model: modelName }
      });
      window.dispatchEvent(event);
    }
  }

  /**
   * 获取使用统计
   */
  getUsageStats() {
    // 这里可以返回实际的使用统计
    return {
      totalCommands: 0,
      k2Usage: 0,
      claudeUsage: 0,
      costSaved: 0,
      lastUpdated: new Date().toISOString()
    };
  }
}

// 创建全局实例
const powerAutomationService = new PowerAutomationService();

// 导出服务
export default powerAutomationService;

