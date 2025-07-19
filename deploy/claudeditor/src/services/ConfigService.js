/**
 * Config Service - 配置管理服务
 * 基于 Config MCP 的前端配置管理系统
 */

class ConfigService {
  constructor() {
    this.apiBase = 'http://localhost:5001';
    this.isInitialized = false;
    this.configs = new Map();
    this.configHistory = [];
    this.observers = [];
    
    // 配置分类定义
    this.categories = {
      APPLICATION: 'application',
      MCP: 'mcp',
      UI: 'ui',
      AI: 'ai',
      SYSTEM: 'system',
      CUSTOM: 'custom'
    };
    
    // 配置类型定义
    this.configTypes = {
      STRING: 'string',
      NUMBER: 'number',
      BOOLEAN: 'boolean',
      ARRAY: 'array',
      OBJECT: 'object'
    };
    
    this.init();
  }
  
  async init() {
    try {
      // 初始化与后端的连接
      await this.initializeConnection();
      
      // 加载配置
      await this.loadConfigs();
      
      // 设置本地存储同步
      this.setupLocalStorageSync();
      
      this.isInitialized = true;
      console.log('✅ Config Service 初始化完成');
      
    } catch (error) {
      console.error('❌ Config Service 初始化失败:', error);
    }
  }
  
  async initializeConnection() {
    try {
      const response = await fetch(`${this.apiBase}/api/config/status`);
      if (!response.ok) {
        throw new Error('Config MCP 服务连接失败');
      }
      
      const status = await response.json();
      console.log('🔗 Config MCP 连接成功:', status);
      
    } catch (error) {
      console.warn('⚠️ Config MCP 服务未启动，使用本地模式');
      this.setupLocalMode();
    }
  }
  
  setupLocalMode() {
    // 本地模式的默认配置
    const defaultConfigs = [
      {
        key: 'app.name',
        value: 'PowerAutomation',
        category: this.categories.APPLICATION,
        description: '应用程序名称',
        type: this.configTypes.STRING
      },
      {
        key: 'app.version',
        value: '4.6.9.6',
        category: this.categories.APPLICATION,
        description: '应用程序版本',
        type: this.configTypes.STRING
      },
      {
        key: 'mcp.auto_start',
        value: true,
        category: this.categories.MCP,
        description: 'MCP组件自动启动',
        type: this.configTypes.BOOLEAN
      },
      {
        key: 'ui.theme',
        value: 'dark',
        category: this.categories.UI,
        description: '用户界面主题',
        type: this.configTypes.STRING,
        options: ['light', 'dark', 'auto']
      },
      {
        key: 'ui.language',
        value: 'zh-CN',
        category: this.categories.UI,
        description: '界面语言',
        type: this.configTypes.STRING,
        options: ['zh-CN', 'en-US', 'ja-JP']
      },
      {
        key: 'ai.model',
        value: 'sonnet-4',
        category: this.categories.AI,
        description: 'AI模型选择',
        type: this.configTypes.STRING,
        options: ['sonnet-4', 'gpt-4', 'claude-3']
      },
      {
        key: 'ai.temperature',
        value: 0.7,
        category: this.categories.AI,
        description: 'AI温度参数',
        type: this.configTypes.NUMBER,
        min: 0,
        max: 1,
        step: 0.1
      },
      {
        key: 'system.debug_mode',
        value: false,
        category: this.categories.SYSTEM,
        description: '调试模式',
        type: this.configTypes.BOOLEAN
      },
      {
        key: 'system.log_level',
        value: 'info',
        category: this.categories.SYSTEM,
        description: '日志级别',
        type: this.configTypes.STRING,
        options: ['debug', 'info', 'warn', 'error']
      },
      {
        key: 'system.max_concurrent_tasks',
        value: 5,
        category: this.categories.SYSTEM,
        description: '最大并发任务数',
        type: this.configTypes.NUMBER,
        min: 1,
        max: 20
      }
    ];
    
    defaultConfigs.forEach(config => {
      this.configs.set(config.key, {
        ...config,
        lastModified: new Date().toISOString()
      });
    });
  }
  
  async loadConfigs() {
    try {
      const response = await fetch(`${this.apiBase}/api/config/all`);
      if (response.ok) {
        const configs = await response.json();
        configs.forEach(config => {
          this.configs.set(config.key, config);
        });
      }
    } catch (error) {
      console.warn('使用本地配置数据');
    }
  }
  
  setupLocalStorageSync() {
    // 从 localStorage 加载用户自定义配置
    const savedConfigs = localStorage.getItem('powerautomation_configs');
    if (savedConfigs) {
      try {
        const parsed = JSON.parse(savedConfigs);
        Object.entries(parsed).forEach(([key, value]) => {
          if (this.configs.has(key)) {
            const config = this.configs.get(key);
            config.value = value;
            this.configs.set(key, config);
          }
        });
      } catch (error) {
        console.warn('加载本地配置失败:', error);
      }
    }
  }
  
  saveToLocalStorage() {
    const configsToSave = {};
    this.configs.forEach((config, key) => {
      configsToSave[key] = config.value;
    });
    localStorage.setItem('powerautomation_configs', JSON.stringify(configsToSave));
  }
  
  // 公共 API 方法
  
  /**
   * 获取配置值
   */
  async getConfig(key) {
    if (this.configs.has(key)) {
      return this.configs.get(key).value;
    }
    
    try {
      const response = await fetch(`${this.apiBase}/api/config/${key}`);
      if (response.ok) {
        const config = await response.json();
        this.configs.set(key, config);
        return config.value;
      }
    } catch (error) {
      console.warn(`获取配置 ${key} 失败:`, error);
    }
    
    return null;
  }
  
  /**
   * 设置配置值
   */
  async setConfig(key, value, category = this.categories.CUSTOM, description = '') {
    try {
      const response = await fetch(`${this.apiBase}/api/config/${key}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          value,
          category,
          description
        })
      });
      
      if (response.ok) {
        const config = await response.json();
        this.configs.set(key, config);
        this.saveToLocalStorage();
        this.notifyObservers({ type: 'config_updated', key, value, config });
        return true;
      }
    } catch (error) {
      console.warn('设置配置失败，使用本地模式:', error);
    }
    
    // 本地模式设置
    const config = {
      key,
      value,
      category,
      description,
      lastModified: new Date().toISOString(),
      type: this.inferType(value)
    };
    
    this.configs.set(key, config);
    this.configHistory.push({ ...config, action: 'set' });
    this.saveToLocalStorage();
    this.notifyObservers({ type: 'config_updated', key, value, config });
    
    return true;
  }
  
  /**
   * 删除配置
   */
  async deleteConfig(key) {
    try {
      const response = await fetch(`${this.apiBase}/api/config/${key}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        this.configs.delete(key);
        this.saveToLocalStorage();
        this.notifyObservers({ type: 'config_deleted', key });
        return true;
      }
    } catch (error) {
      console.warn('删除配置失败:', error);
    }
    
    // 本地模式删除
    if (this.configs.has(key)) {
      const config = this.configs.get(key);
      this.configs.delete(key);
      this.configHistory.push({ ...config, action: 'delete' });
      this.saveToLocalStorage();
      this.notifyObservers({ type: 'config_deleted', key });
      return true;
    }
    
    return false;
  }
  
  /**
   * 重置配置到默认值
   */
  async resetConfig(key) {
    const config = this.configs.get(key);
    if (config && config.defaultValue !== undefined) {
      return await this.setConfig(key, config.defaultValue, config.category, config.description);
    }
    return false;
  }
  
  /**
   * 批量设置配置
   */
  async setBatchConfigs(configMap) {
    const results = [];
    for (const [key, value] of Object.entries(configMap)) {
      const result = await this.setConfig(key, value);
      results.push({ key, success: result });
    }
    return results;
  }
  
  /**
   * 导出配置
   */
  exportConfigs(category = null) {
    const configsToExport = {};
    
    this.configs.forEach((config, key) => {
      if (!category || config.category === category) {
        configsToExport[key] = {
          value: config.value,
          category: config.category,
          description: config.description,
          type: config.type
        };
      }
    });
    
    return configsToExport;
  }
  
  /**
   * 导入配置
   */
  async importConfigs(configsData) {
    const results = [];
    
    for (const [key, configData] of Object.entries(configsData)) {
      try {
        const success = await this.setConfig(
          key, 
          configData.value, 
          configData.category || this.categories.CUSTOM,
          configData.description || ''
        );
        results.push({ key, success });
      } catch (error) {
        results.push({ key, success: false, error: error.message });
      }
    }
    
    return results;
  }
  
  /**
   * 搜索配置
   */
  searchConfigs(query) {
    const results = [];
    const lowerQuery = query.toLowerCase();
    
    this.configs.forEach((config, key) => {
      if (
        key.toLowerCase().includes(lowerQuery) ||
        config.description.toLowerCase().includes(lowerQuery) ||
        config.category.toLowerCase().includes(lowerQuery)
      ) {
        results.push({ key, ...config });
      }
    });
    
    return results;
  }
  
  // 工具方法
  
  inferType(value) {
    if (typeof value === 'boolean') return this.configTypes.BOOLEAN;
    if (typeof value === 'number') return this.configTypes.NUMBER;
    if (Array.isArray(value)) return this.configTypes.ARRAY;
    if (typeof value === 'object' && value !== null) return this.configTypes.OBJECT;
    return this.configTypes.STRING;
  }
  
  validateConfigValue(config, value) {
    switch (config.type) {
      case this.configTypes.NUMBER:
        const num = Number(value);
        if (isNaN(num)) return false;
        if (config.min !== undefined && num < config.min) return false;
        if (config.max !== undefined && num > config.max) return false;
        return true;
      
      case this.configTypes.BOOLEAN:
        return typeof value === 'boolean';
      
      case this.configTypes.STRING:
        if (config.options && !config.options.includes(value)) return false;
        return typeof value === 'string';
      
      default:
        return true;
    }
  }
  
  // 状态查询方法
  
  getAllConfigs() {
    return Array.from(this.configs.entries()).map(([key, config]) => ({
      key,
      ...config
    }));
  }
  
  getConfigsByCategory(category) {
    return this.getAllConfigs().filter(config => config.category === category);
  }
  
  getCategories() {
    const categories = new Set();
    this.configs.forEach(config => categories.add(config.category));
    return Array.from(categories);
  }
  
  getConfigHistory() {
    return [...this.configHistory];
  }
  
  getConfigInfo(key) {
    return this.configs.get(key);
  }
  
  hasConfig(key) {
    return this.configs.has(key);
  }
  
  // 观察者模式
  
  addObserver(callback) {
    this.observers.push(callback);
  }
  
  removeObserver(callback) {
    const index = this.observers.indexOf(callback);
    if (index > -1) {
      this.observers.splice(index, 1);
    }
  }
  
  notifyObservers(data) {
    this.observers.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('观察者回调执行失败:', error);
      }
    });
  }
  
  // 预设配置模板
  
  getConfigTemplates() {
    return {
      development: {
        'system.debug_mode': true,
        'system.log_level': 'debug',
        'ai.temperature': 0.3
      },
      production: {
        'system.debug_mode': false,
        'system.log_level': 'warn',
        'ai.temperature': 0.7
      },
      testing: {
        'system.debug_mode': true,
        'system.log_level': 'info',
        'system.max_concurrent_tasks': 2
      }
    };
  }
  
  async applyTemplate(templateName) {
    const templates = this.getConfigTemplates();
    if (templates[templateName]) {
      return await this.setBatchConfigs(templates[templateName]);
    }
    return [];
  }
}

// 创建全局实例
const configService = new ConfigService();

export default configService;

