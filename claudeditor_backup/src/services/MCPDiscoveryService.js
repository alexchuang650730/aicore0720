/**
 * MCP Discovery Service - MCP 组件发现服务
 * 提供 MCP 组件的发现、注册、状态监控等功能
 */

class MCPDiscoveryService {
  constructor() {
    this.mcpComponents = new Map();
    this.discoveryEnabled = true;
    this.lastDiscoveryTime = null;
    this.eventListeners = new Map();
    this.discoveryInterval = null;
    this.healthCheckInterval = null;
    
    // 初始化预定义的 MCP 组件
    this.initializePredefinedComponents();
    
    // 开始自动发现
    this.startAutoDiscovery();
  }

  /**
   * 初始化预定义的 MCP 组件
   */
  initializePredefinedComponents() {
    const predefinedComponents = [
      {
        id: 'codeflow_mcp',
        name: 'CodeFlow MCP',
        type: 'core',
        status: 'active',
        version: '4.6.8',
        description: '代码流程管理和规格定义',
        capabilities: ['code_generation', 'workflow_management', 'tdd_testing'],
        integrationLevel: 30,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8001/codeflow'
      },
      {
        id: 'smartui_mcp',
        name: 'SmartUI MCP',
        type: 'core',
        status: 'active',
        version: '4.6.9',
        description: '智能UI生成和设计系统',
        capabilities: ['ui_generation', 'design_system', 'responsive_design'],
        integrationLevel: 100,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8002/smartui'
      },
      {
        id: 'ag_ui_mcp',
        name: 'AG-UI MCP',
        type: 'core',
        status: 'active',
        version: '4.6.9',
        description: '自动化GUI测试和交互',
        capabilities: ['ui_testing', 'automation', 'interaction_testing'],
        integrationLevel: 100,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8003/agui'
      },
      {
        id: 'test_mcp',
        name: 'Test MCP',
        type: 'support',
        status: 'active',
        version: '4.6.9',
        description: '统一测试管理',
        capabilities: ['unit_testing', 'integration_testing', 'test_reporting'],
        integrationLevel: 100,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8004/test'
      },
      {
        id: 'config_mcp',
        name: 'Config MCP',
        type: 'support',
        status: 'active',
        version: '4.6.9',
        description: '配置管理',
        capabilities: ['config_management', 'environment_setup', 'settings_sync'],
        integrationLevel: 100,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8005/config'
      },
      {
        id: 'local_adapter_mcp',
        name: 'Local Adapter MCP',
        type: 'support',
        status: 'active',
        version: '4.6.9',
        description: '本地适配器',
        capabilities: ['local_integration', 'file_system', 'process_management'],
        integrationLevel: 100,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8006/adapter'
      },
      {
        id: 'enhanced_command_mcp',
        name: 'Enhanced Command MCP',
        type: 'core',
        status: 'active',
        version: '4.6.9',
        description: '增强命令管理',
        capabilities: ['command_execution', 'automation', 'workflow_integration'],
        integrationLevel: 100,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8007/command'
      },
      {
        id: 'claude_code_router_mcp',
        name: 'Claude Code Router MCP',
        type: 'core',
        status: 'active',
        version: '4.6.9',
        description: 'Claude Code 路由管理',
        capabilities: ['code_routing', 'ai_integration', 'request_handling'],
        integrationLevel: 100,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8008/router'
      },
      {
        id: 'memoryos_mcp',
        name: 'MemoryOS MCP',
        type: 'core',
        status: 'partial',
        version: '4.6.9',
        description: '上下文记忆系统',
        capabilities: ['memory_management', 'context_learning', 'recommendation'],
        integrationLevel: 75,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8009/memory'
      },
      {
        id: 'mcp_coordinator_mcp',
        name: 'MCP Coordinator',
        type: 'infrastructure',
        status: 'active',
        version: '4.6.9',
        description: 'MCP 组件协调器',
        capabilities: ['component_coordination', 'lifecycle_management', 'service_discovery'],
        integrationLevel: 100,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8010/coordinator'
      },
      {
        id: 'startup_trigger_mcp',
        name: 'Startup Trigger MCP',
        type: 'infrastructure',
        status: 'active',
        version: '4.6.9',
        description: '启动触发管理',
        capabilities: ['startup_automation', 'trigger_detection', 'installation_management'],
        integrationLevel: 100,
        lastSeen: new Date(),
        endpoint: 'http://localhost:8011/startup'
      }
    ];

    predefinedComponents.forEach(component => {
      this.mcpComponents.set(component.id, component);
    });

    this.lastDiscoveryTime = new Date();
  }

  /**
   * 开始自动发现
   */
  startAutoDiscovery() {
    if (this.discoveryInterval) {
      clearInterval(this.discoveryInterval);
    }

    // 每30秒进行一次发现
    this.discoveryInterval = setInterval(() => {
      if (this.discoveryEnabled) {
        this.discoverComponents();
      }
    }, 30000);

    // 开始健康检查
    this.startHealthCheck();
  }

  /**
   * 开始健康检查
   */
  startHealthCheck() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }

    // 每60秒进行一次健康检查
    this.healthCheckInterval = setInterval(() => {
      this.performHealthCheck();
    }, 60000);
  }

  /**
   * 发现 MCP 组件
   */
  async discoverComponents() {
    try {
      this.emit('discoveryStarted', { timestamp: new Date() });

      // 模拟发现过程
      await new Promise(resolve => setTimeout(resolve, 500));

      // 更新组件状态
      this.updateComponentStatuses();

      this.lastDiscoveryTime = new Date();
      
      this.emit('discoveryCompleted', {
        timestamp: this.lastDiscoveryTime,
        componentCount: this.mcpComponents.size
      });

    } catch (error) {
      this.emit('discoveryError', {
        error: error.message,
        timestamp: new Date()
      });
    }
  }

  /**
   * 更新组件状态
   */
  updateComponentStatuses() {
    this.mcpComponents.forEach((component, id) => {
      // 模拟状态变化
      const random = Math.random();
      
      if (random > 0.95) {
        component.status = 'inactive';
      } else if (random > 0.9) {
        component.status = 'partial';
      } else {
        component.status = 'active';
      }

      component.lastSeen = new Date();
      
      // 模拟性能指标
      component.performance = {
        responseTime: Math.floor(Math.random() * 200) + 50,
        memoryUsage: Math.floor(Math.random() * 100) + 20,
        cpuUsage: Math.floor(Math.random() * 50) + 5
      };
    });
  }

  /**
   * 执行健康检查
   */
  async performHealthCheck() {
    const healthResults = [];

    for (const [id, component] of this.mcpComponents) {
      try {
        // 模拟健康检查
        await new Promise(resolve => setTimeout(resolve, 100));

        const health = {
          componentId: id,
          status: component.status,
          responseTime: Math.floor(Math.random() * 200) + 50,
          lastCheck: new Date(),
          issues: []
        };

        // 模拟一些健康问题
        if (Math.random() > 0.8) {
          health.issues.push({
            type: 'warning',
            message: '响应时间较慢',
            severity: 'low'
          });
        }

        if (component.status === 'partial') {
          health.issues.push({
            type: 'error',
            message: '部分功能不可用',
            severity: 'medium'
          });
        }

        healthResults.push(health);

      } catch (error) {
        healthResults.push({
          componentId: id,
          status: 'error',
          error: error.message,
          lastCheck: new Date()
        });
      }
    }

    this.emit('healthCheckCompleted', {
      results: healthResults,
      timestamp: new Date()
    });
  }

  /**
   * 注册新的 MCP 组件
   * @param {Object} componentInfo - 组件信息
   */
  registerComponent(componentInfo) {
    const component = {
      id: componentInfo.id,
      name: componentInfo.name,
      type: componentInfo.type || 'custom',
      status: 'active',
      version: componentInfo.version || '1.0.0',
      description: componentInfo.description || '',
      capabilities: componentInfo.capabilities || [],
      integrationLevel: componentInfo.integrationLevel || 0,
      lastSeen: new Date(),
      endpoint: componentInfo.endpoint,
      ...componentInfo
    };

    this.mcpComponents.set(component.id, component);

    this.emit('componentRegistered', { component });
  }

  /**
   * 注销 MCP 组件
   * @param {string} componentId - 组件ID
   */
  unregisterComponent(componentId) {
    const component = this.mcpComponents.get(componentId);
    if (component) {
      this.mcpComponents.delete(componentId);
      this.emit('componentUnregistered', { componentId, component });
    }
  }

  /**
   * 获取所有 MCP 组件
   * @returns {Array} 组件列表
   */
  getAllComponents() {
    return Array.from(this.mcpComponents.values());
  }

  /**
   * 获取指定组件
   * @param {string} componentId - 组件ID
   * @returns {Object} 组件信息
   */
  getComponent(componentId) {
    return this.mcpComponents.get(componentId);
  }

  /**
   * 按类型获取组件
   * @param {string} type - 组件类型
   * @returns {Array} 组件列表
   */
  getComponentsByType(type) {
    return Array.from(this.mcpComponents.values())
      .filter(component => component.type === type);
  }

  /**
   * 按状态获取组件
   * @param {string} status - 组件状态
   * @returns {Array} 组件列表
   */
  getComponentsByStatus(status) {
    return Array.from(this.mcpComponents.values())
      .filter(component => component.status === status);
  }

  /**
   * 获取组件统计信息
   * @returns {Object} 统计信息
   */
  getStatistics() {
    const components = Array.from(this.mcpComponents.values());
    
    const stats = {
      total: components.length,
      byStatus: {},
      byType: {},
      averageIntegrationLevel: 0,
      lastDiscovery: this.lastDiscoveryTime
    };

    // 按状态统计
    components.forEach(component => {
      stats.byStatus[component.status] = (stats.byStatus[component.status] || 0) + 1;
      stats.byType[component.type] = (stats.byType[component.type] || 0) + 1;
    });

    // 计算平均集成度
    if (components.length > 0) {
      stats.averageIntegrationLevel = Math.round(
        components.reduce((sum, comp) => sum + comp.integrationLevel, 0) / components.length
      );
    }

    return stats;
  }

  /**
   * 启用/禁用自动发现
   * @param {boolean} enabled - 是否启用
   */
  setDiscoveryEnabled(enabled) {
    this.discoveryEnabled = enabled;
    this.emit('discoveryToggled', { enabled, timestamp: new Date() });
  }

  /**
   * 手动触发发现
   */
  triggerDiscovery() {
    return this.discoverComponents();
  }

  /**
   * 停止发现服务
   */
  stop() {
    if (this.discoveryInterval) {
      clearInterval(this.discoveryInterval);
      this.discoveryInterval = null;
    }

    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }

    this.emit('serviceStopped', { timestamp: new Date() });
  }

  /**
   * 事件监听
   * @param {string} event - 事件名
   * @param {Function} callback - 回调函数
   */
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event).push(callback);
  }

  /**
   * 移除事件监听
   * @param {string} event - 事件名
   * @param {Function} callback - 回调函数
   */
  off(event, callback) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * 触发事件
   * @param {string} event - 事件名
   * @param {Object} data - 事件数据
   */
  emit(event, data) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in MCP discovery service event listener:`, error);
        }
      });
    }
  }
}

// 创建单例实例
const mcpDiscoveryService = new MCPDiscoveryService();

export default mcpDiscoveryService;

