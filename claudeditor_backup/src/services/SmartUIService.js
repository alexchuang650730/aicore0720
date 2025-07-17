/**
 * SmartUI Service - 智能响应式UI服务
 * 基于AG-UI指导的前端智能适配系统
 */

class SmartUIService {
  constructor() {
    this.config = null;
    this.isInitialized = false;
    this.deviceType = null;
    this.breakpoint = null;
    this.observers = [];
    
    // 断点定义
    this.breakpoints = {
      xs: 0,
      sm: 576,
      md: 768,
      lg: 992,
      xl: 1200,
      xxl: 1400
    };
    
    this.init();
  }
  
  async init() {
    try {
      // 检测当前设备和视口
      await this.detectAndConfigure();
      
      // 设置监听器
      this.setupEventListeners();
      
      // 应用初始配置
      this.applyConfiguration();
      
      this.isInitialized = true;
      console.log('✅ SmartUI Service 初始化完成');
      
    } catch (error) {
      console.error('❌ SmartUI Service 初始化失败:', error);
    }
  }
  
  async detectAndConfigure() {
    const viewport = this.getViewportInfo();
    
    try {
      // 调用后端SmartUI API进行设备检测和配置
      const response = await fetch('/api/smartui/configure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          viewport_width: viewport.width,
          viewport_height: viewport.height,
          user_agent: navigator.userAgent,
          pixel_ratio: window.devicePixelRatio || 1,
          touch_support: 'ontouchstart' in window
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        this.config = data.config;
        this.deviceType = data.config.device_type;
        this.breakpoint = data.config.breakpoint;
        
        console.log('🎯 SmartUI 配置:', this.config);
        
        // 应用动态CSS
        if (data.css) {
          this.updateDynamicCSS(data.css);
        }
        
        // 应用JavaScript配置
        if (data.js_config) {
          this.applyJSConfig(data.js_config);
        }
        
      } else {
        throw new Error(`配置请求失败: ${response.status}`);
      }
      
    } catch (error) {
      console.warn('⚠️ 后端SmartUI不可用，使用前端检测:', error);
      // 降级到前端检测
      this.config = this.detectDeviceLocally(viewport);
      this.deviceType = this.config.device_type;
      this.breakpoint = this.config.breakpoint;
    }
  }
  
  detectDeviceLocally(viewport) {
    const { width, height } = viewport;
    
    let deviceType, breakpoint, layoutColumns, sidebarWidth;
    
    if (width < this.breakpoints.sm) {
      deviceType = 'mobile';
      breakpoint = 'xs';
      layoutColumns = 1;
      sidebarWidth = null;
    } else if (width < this.breakpoints.md) {
      deviceType = 'mobile';
      breakpoint = 'sm';
      layoutColumns = 1;
      sidebarWidth = null;
    } else if (width < this.breakpoints.lg) {
      deviceType = 'tablet';
      breakpoint = 'md';
      layoutColumns = 2;
      sidebarWidth = 250;
    } else if (width < this.breakpoints.xxl) {
      deviceType = 'desktop';
      breakpoint = 'lg';
      layoutColumns = 3;
      sidebarWidth = 300;
    } else {
      deviceType = 'large_desktop';
      breakpoint = 'xxl';
      layoutColumns = 3;
      sidebarWidth = 400;
    }
    
    return {
      device_type: deviceType,
      breakpoint: breakpoint,
      viewport_width: width,
      viewport_height: height,
      layout_columns: layoutColumns,
      sidebar_width: sidebarWidth,
      header_height: deviceType === 'mobile' ? 60 : 80,
      touch_optimized: deviceType === 'mobile' || deviceType === 'tablet',
      font_scale: deviceType === 'large_desktop' ? 1.1 : 1.0,
      spacing_scale: deviceType === 'mobile' ? 1.2 : 1.0
    };
  }
  
  getViewportInfo() {
    return {
      width: window.innerWidth,
      height: window.innerHeight,
      ratio: window.devicePixelRatio || 1
    };
  }
  
  setupEventListeners() {
    // 视口变化监听
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        this.handleViewportChange();
      }, 250);
    });
    
    // 方向变化监听
    window.addEventListener('orientationchange', () => {
      setTimeout(() => {
        this.handleViewportChange();
      }, 100);
    });
    
    // 可见性变化监听
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        this.handleViewportChange();
      }
    });
  }
  
  async handleViewportChange() {
    const oldDeviceType = this.deviceType;
    const oldBreakpoint = this.breakpoint;
    
    await this.detectAndConfigure();
    
    // 如果设备类型或断点发生变化，通知观察者
    if (oldDeviceType !== this.deviceType || oldBreakpoint !== this.breakpoint) {
      console.log(`📱 设备类型变化: ${oldDeviceType} → ${this.deviceType}`);
      this.notifyObservers('device_change', {
        oldDeviceType,
        newDeviceType: this.deviceType,
        oldBreakpoint,
        newBreakpoint: this.breakpoint
      });
    }
    
    this.applyConfiguration();
  }
  
  applyConfiguration() {
    if (!this.config) return;
    
    const body = document.body;
    
    // 清除旧的类名
    body.classList.remove(
      'device-mobile', 'device-tablet', 'device-desktop', 'device-large_desktop',
      'breakpoint-xs', 'breakpoint-sm', 'breakpoint-md', 'breakpoint-lg', 'breakpoint-xl', 'breakpoint-xxl',
      'columns-1', 'columns-2', 'columns-3',
      'touch-optimized'
    );
    
    // 应用新的类名
    body.classList.add(`device-${this.config.device_type}`);
    body.classList.add(`breakpoint-${this.config.breakpoint}`);
    body.classList.add(`columns-${this.config.layout_columns}`);
    
    if (this.config.touch_optimized) {
      body.classList.add('touch-optimized');
    }
    
    // 设置CSS变量
    const root = document.documentElement;
    root.style.setProperty('--smartui-viewport-width', `${this.config.viewport_width}px`);
    root.style.setProperty('--smartui-viewport-height', `${this.config.viewport_height}px`);
    root.style.setProperty('--smartui-header-height', `${this.config.header_height}px`);
    root.style.setProperty('--smartui-sidebar-width', `${this.config.sidebar_width || 0}px`);
    root.style.setProperty('--smartui-font-scale', this.config.font_scale);
    root.style.setProperty('--smartui-spacing-scale', this.config.spacing_scale);
    root.style.setProperty('--smartui-layout-columns', this.config.layout_columns);
    
    // 通知观察者配置已应用
    this.notifyObservers('config_applied', this.config);
  }
  
  updateDynamicCSS(css) {
    let styleElement = document.getElementById('smartui-dynamic-styles');
    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = 'smartui-dynamic-styles';
      document.head.appendChild(styleElement);
    }
    styleElement.textContent = css;
  }
  
  applyJSConfig(jsConfig) {
    // 应用JavaScript配置
    window.SmartUIConfig = { ...window.SmartUIConfig, ...jsConfig };
  }
  
  // 观察者模式
  subscribe(callback) {
    this.observers.push(callback);
    return () => {
      this.observers = this.observers.filter(obs => obs !== callback);
    };
  }
  
  notifyObservers(event, data) {
    this.observers.forEach(callback => {
      try {
        callback(event, data);
      } catch (error) {
        console.error('SmartUI observer error:', error);
      }
    });
  }
  
  // 公共API
  getCurrentConfig() {
    return this.config;
  }
  
  getDeviceType() {
    return this.deviceType;
  }
  
  getBreakpoint() {
    return this.breakpoint;
  }
  
  isTouch() {
    return this.config?.touch_optimized || false;
  }
  
  isMobile() {
    return this.deviceType === 'mobile';
  }
  
  isTablet() {
    return this.deviceType === 'tablet';
  }
  
  isDesktop() {
    return this.deviceType === 'desktop' || this.deviceType === 'large_desktop';
  }
  
  getLayoutColumns() {
    return this.config?.layout_columns || 3;
  }
  
  getSidebarWidth() {
    return this.config?.sidebar_width || 0;
  }
  
  // 布局助手方法
  shouldShowSidebar() {
    return this.config?.sidebar_width > 0;
  }
  
  shouldCollapseSidebar() {
    return this.isTablet() || (this.isMobile() && this.config?.sidebar_width);
  }
  
  shouldStackLayout() {
    return this.isMobile();
  }
  
  // 样式助手方法
  getButtonSize() {
    return this.isTouch() ? 'large' : 'medium';
  }
  
  getSpacing() {
    const scale = this.config?.spacing_scale || 1.0;
    return {
      xs: `${4 * scale}px`,
      sm: `${8 * scale}px`,
      md: `${16 * scale}px`,
      lg: `${24 * scale}px`,
      xl: `${32 * scale}px`
    };
  }
  
  getFontSizes() {
    const scale = this.config?.font_scale || 1.0;
    return {
      xs: `${12 * scale}px`,
      sm: `${14 * scale}px`,
      base: `${16 * scale}px`,
      lg: `${18 * scale}px`,
      xl: `${20 * scale}px`,
      '2xl': `${24 * scale}px`,
      '3xl': `${30 * scale}px`
    };
  }
  
  // AG-UI集成方法
  async getAGUIGuidance(componentType, context = {}) {
    try {
      const response = await fetch('/api/smartui/ag-ui-guidance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          component_type: componentType,
          context: {
            ...context,
            device_type: this.deviceType,
            breakpoint: this.breakpoint,
            config: this.config
          }
        })
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`AG-UI guidance request failed: ${response.status}`);
      }
      
    } catch (error) {
      console.warn('⚠️ AG-UI guidance not available:', error);
      return {
        guidance: 'AG-UI guidance not available',
        recommendations: []
      };
    }
  }
}

// 创建全局实例
window.smartUIService = new SmartUIService();

export default SmartUIService;

