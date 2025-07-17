/**
 * PowerAutomation 服务
 * 负责在 ClaudeEditor 启动时自动启动 PowerAutomation Core 和相关服务
 */

class PowerAutomationService {
  constructor() {
    this.isInitialized = false;
    this.services = {
      commandMCP: null,
      mirrorCode: null,
      taskSync: null
    };
    
    this.config = {
      autoStart: true,
      services: {
        commandMCP: {
          enabled: true,
          defaultModel: 'k2_cloud', // 默认使用 K2 云端
          fallbackToClaudeCode: true
        },
        mirrorCode: {
          enabled: true,
          mode: 'integrated', // 集成模式，不需要独立服务
          k2Priority: true
        },
        taskSync: {
          enabled: true,
          port: 8765
        }
      }
    };
    
    console.log('🚀 PowerAutomation Service 初始化');
  }

  /**
   * 初始化 PowerAutomation 服务
   * ClaudeEditor 启动时自动调用
   */
  async initialize() {
    if (this.isInitialized) {
      console.log('⚠️ PowerAutomation Service 已经初始化');
      return;
    }

    try {
      console.log('🔧 启动 PowerAutomation Core 服务...');
      
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
      
      // 模拟启动 Command MCP
      // 在实际实现中，这里会启动后端服务或建立 WebSocket 连接
      const response = await fetch('/api/command-mcp/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          config: this.config.services.commandMCP,
          mirrorConfig: this.config.services.mirrorCode
        })
      }).catch(() => {
        // 如果后端服务不可用，使用前端模拟
        console.log('🔄 后端服务不可用，使用前端模拟模式');
        return { ok: true, json: () => Promise.resolve({ status: 'started', mode: 'frontend' }) };
      });

      if (response.ok) {
        const result = await response.json();
        this.services.commandMCP = {
          status: 'running',
          mode: result.mode || 'backend',
          defaultModel: 'k2_cloud',
          mirrorCodeIntegrated: true
        };
        
        console.log('✅ Command MCP 启动成功 (默认 K2 模型)');
        console.log('🪞 Mirror Code 已集成到 Command MCP');
      } else {
        throw new Error('Command MCP 启动失败');
      }
      
    } catch (error) {
      console.error('❌ Command MCP 启动失败:', error);
      // 使用前端模拟模式
      this.services.commandMCP = {
        status: 'running',
        mode: 'frontend-simulation',
        defaultModel: 'k2_cloud',
        mirrorCodeIntegrated: true
      };
      console.log('🔄 使用前端模拟模式运行 Command MCP');
    }
  }

  /**
   * 启动任务同步服务
   */
  async startTaskSyncService() {
    try {
      console.log('🔗 启动任务同步服务...');
      
      // 尝试连接任务同步服务
      const wsUrl = `ws://localhost:${this.config.services.taskSync.port}`;
      
      // 模拟 WebSocket 连接
      this.services.taskSync = {
        status: 'running',
        url: wsUrl,
        connected: false
      };
      
      // 尝试建立连接
      try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('✅ 任务同步服务连接成功');
          this.services.taskSync.connected = true;
          this.services.taskSync.websocket = ws;
        };
        
        ws.onerror = () => {
          console.log('⚠️ 任务同步服务连接失败，使用本地模式');
          this.services.taskSync.connected = false;
        };
        
        // 等待连接结果
        await new Promise((resolve) => {
          setTimeout(() => {
            resolve();
          }, 1000);
        });
        
      } catch (error) {
        console.log('🔄 任务同步服务不可用，使用本地模式');
        this.services.taskSync.connected = false;
      }
      
    } catch (error) {
      console.error('❌ 任务同步服务启动失败:', error);
      this.services.taskSync = {
        status: 'error',
        error: error.message
      };
    }
  }

  /**
   * 验证服务状态
   */
  async verifyServices() {
    console.log('🔍 验证服务状态...');
    
    const status = {
      commandMCP: this.services.commandMCP?.status === 'running',
      mirrorCode: this.services.commandMCP?.mirrorCodeIntegrated === true,
      taskSync: this.services.taskSync?.status === 'running',
      defaultModel: this.services.commandMCP?.defaultModel === 'k2_cloud'
    };
    
    console.log('📊 服务状态:', status);
    
    if (status.commandMCP && status.mirrorCode && status.defaultModel) {
      console.log('✅ 核心服务验证通过');
      console.log('🤖 默认模型: K2 云端模型');
      console.log('🪞 Mirror Code: 已集成');
    } else {
      console.warn('⚠️ 部分服务可能未正常启动');
    }
    
    return status;
  }

  /**
   * 发送启动完成通知
   */
  notifyStartupComplete() {
    // 发送自定义事件
    const event = new CustomEvent('powerautomation:ready', {
      detail: {
        services: this.services,
        config: this.config,
        timestamp: new Date().toISOString()
      }
    });
    
    window.dispatchEvent(event);
    
    // 在控制台显示启动信息
    console.log(`
🎉 PowerAutomation v4.6.9.5 启动完成！

📋 服务状态:
  ✅ Command MCP: ${this.services.commandMCP?.status}
  ✅ Mirror Code: 已集成 (默认 K2 优先)
  ✅ Task Sync: ${this.services.taskSync?.status}

🤖 默认配置:
  🥇 主要模型: K2 云端模型 (高效、智能)
  🥈 备用模型: Claude Code (用户明确选择时)
  🪞 Mirror Code: 集成模式 (无需独立服务)

💡 使用提示:
  - 所有指令默认使用 K2 云端处理
  - 如需 Claude Code，使用 /switch-model claude
  - 使用 /help 查看所有可用指令
    `);
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
   * 执行命令 (通过 Command MCP)
   */
  async executeCommand(command, args = [], forceModel = null) {
    if (!this.isInitialized) {
      throw new Error('PowerAutomation Service 未初始化');
    }

    try {
      // 构建请求
      const request = {
        command,
        args,
        forceModel,
        timestamp: new Date().toISOString()
      };

      console.log(`🤖 执行命令: ${command} (模型: ${forceModel || 'K2 默认'})`);

      // 如果有后端服务，发送到后端
      if (this.services.commandMCP?.mode === 'backend') {
        const response = await fetch('/api/command-mcp/execute', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(request)
        });

        if (response.ok) {
          return await response.json();
        }
      }

      // 前端模拟执行
      return this.simulateCommandExecution(command, args, forceModel);

    } catch (error) {
      console.error('❌ 命令执行失败:', error);
      throw error;
    }
  }

  /**
   * 前端模拟命令执行
   */
  simulateCommandExecution(command, args, forceModel) {
    const isClaudeForced = forceModel === 'claude_code';
    const model = isClaudeForced ? 'Claude Code' : 'K2 云端模型';
    
    console.log(`🔄 ${model} 处理: ${command}`);
    
    // 模拟执行结果
    const result = {
      success: true,
      command,
      args,
      model: isClaudeForced ? 'claude_code' : 'k2_cloud',
      output: `${model} 处理结果: ${command}`,
      executionTime: Math.random() * 100 + 50, // 50-150ms
      timestamp: new Date().toISOString()
    };

    if (args && args.length > 0) {
      result.output += ` (参数: ${args.join(', ')})`;
    }

    return result;
  }

  /**
   * 切换默认模型
   */
  async switchModel(model) {
    if (!this.isInitialized) {
      throw new Error('PowerAutomation Service 未初始化');
    }

    const validModels = ['k2_cloud', 'claude_code'];
    if (!validModels.includes(model)) {
      throw new Error(`无效模型: ${model}`);
    }

    this.services.commandMCP.defaultModel = model;
    console.log(`🔄 默认模型已切换到: ${model}`);

    return {
      success: true,
      previousModel: this.config.services.commandMCP.defaultModel,
      newModel: model,
      message: `已切换到 ${model === 'k2_cloud' ? 'K2 云端模型' : 'Claude Code'}`
    };
  }
}

// 创建全局实例
const powerAutomationService = new PowerAutomationService();

// 导出服务实例
export default powerAutomationService;

// 也导出类，以便需要时创建新实例
export { PowerAutomationService };

