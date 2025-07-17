"""
SmartUI Manager - 智能UI管理器
基于AG-UI指导的智能响应式设计系统
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# 导入AG-UI组件进行智能指导
try:
    from ..ag_ui_mcp.ag_ui_manager import ComponentGenerator, ComponentType, ThemeType, LayoutType
except ImportError:
    logging.warning("AG-UI MCP not found, using fallback mode")
    ComponentGenerator = None

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """设备类型"""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    LARGE_DESKTOP = "large_desktop"


class BreakpointType(Enum):
    """断点类型"""
    XS = "xs"  # < 576px
    SM = "sm"  # >= 576px
    MD = "md"  # >= 768px
    LG = "lg"  # >= 992px
    XL = "xl"  # >= 1200px
    XXL = "xxl"  # >= 1400px


@dataclass
class ResponsiveConfig:
    """响应式配置"""
    device_type: DeviceType
    breakpoint: BreakpointType
    viewport_width: int
    viewport_height: int
    layout_columns: int
    sidebar_width: Optional[int]
    header_height: int
    touch_optimized: bool
    font_scale: float
    spacing_scale: float


@dataclass
class SmartUIRule:
    """智能UI规则"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int
    enabled: bool = True


class SmartUIManager:
    """SmartUI管理器 - 基于AG-UI指导的智能响应式系统"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ag_ui_generator = ComponentGenerator() if ComponentGenerator else None
        self.responsive_configs = self._init_responsive_configs()
        self.smart_rules = self._init_smart_rules()
        self.current_config = None
        
    def _init_responsive_configs(self) -> Dict[DeviceType, ResponsiveConfig]:
        """初始化响应式配置"""
        return {
            DeviceType.MOBILE: ResponsiveConfig(
                device_type=DeviceType.MOBILE,
                breakpoint=BreakpointType.XS,
                viewport_width=375,
                viewport_height=667,
                layout_columns=1,
                sidebar_width=None,  # 移动端隐藏侧边栏
                header_height=60,
                touch_optimized=True,
                font_scale=1.0,
                spacing_scale=1.2
            ),
            DeviceType.TABLET: ResponsiveConfig(
                device_type=DeviceType.TABLET,
                breakpoint=BreakpointType.MD,
                viewport_width=768,
                viewport_height=1024,
                layout_columns=2,
                sidebar_width=250,
                header_height=70,
                touch_optimized=True,
                font_scale=1.1,
                spacing_scale=1.1
            ),
            DeviceType.DESKTOP: ResponsiveConfig(
                device_type=DeviceType.DESKTOP,
                breakpoint=BreakpointType.LG,
                viewport_width=1200,
                viewport_height=800,
                layout_columns=3,
                sidebar_width=300,
                header_height=80,
                touch_optimized=False,
                font_scale=1.0,
                spacing_scale=1.0
            ),
            DeviceType.LARGE_DESKTOP: ResponsiveConfig(
                device_type=DeviceType.LARGE_DESKTOP,
                breakpoint=BreakpointType.XXL,
                viewport_width=1920,
                viewport_height=1080,
                layout_columns=3,
                sidebar_width=400,
                header_height=90,
                touch_optimized=False,
                font_scale=1.1,
                spacing_scale=0.9
            )
        }
    
    def _init_smart_rules(self) -> List[SmartUIRule]:
        """初始化智能UI规则"""
        return [
            SmartUIRule(
                rule_id="mobile_stack_layout",
                name="移动端堆叠布局",
                description="在移动设备上将三栏布局转换为堆叠布局",
                conditions={"device_type": "mobile", "layout_columns": 3},
                actions={"layout": "stack", "sidebar": "hidden", "navigation": "bottom"},
                priority=10
            ),
            SmartUIRule(
                rule_id="tablet_two_column",
                name="平板双栏布局",
                description="在平板设备上使用双栏布局",
                conditions={"device_type": "tablet"},
                actions={"layout": "two_column", "sidebar": "collapsible"},
                priority=8
            ),
            SmartUIRule(
                rule_id="desktop_three_column",
                name="桌面三栏布局",
                description="在桌面设备上使用完整三栏布局",
                conditions={"device_type": "desktop"},
                actions={"layout": "three_column", "sidebar": "fixed"},
                priority=6
            ),
            SmartUIRule(
                rule_id="touch_optimization",
                name="触控优化",
                description="为触控设备优化按钮和交互元素",
                conditions={"touch_optimized": True},
                actions={"button_size": "large", "spacing": "increased", "hover": "disabled"},
                priority=9
            ),
            SmartUIRule(
                rule_id="large_screen_optimization",
                name="大屏优化",
                description="为大屏幕优化内容密度和布局",
                conditions={"viewport_width": ">1400"},
                actions={"content_density": "high", "sidebar_width": "expanded"},
                priority=7
            )
        ]
    
    async def detect_device_and_configure(self, viewport_width: int, viewport_height: int, 
                                        user_agent: str = "") -> ResponsiveConfig:
        """检测设备并配置响应式设计"""
        device_type = self._detect_device_type(viewport_width, viewport_height, user_agent)
        config = self.responsive_configs[device_type]
        
        # 应用智能规则
        config = await self._apply_smart_rules(config, viewport_width, viewport_height)
        
        self.current_config = config
        self.logger.info(f"检测到设备类型: {device_type.value}, 配置: {config}")
        
        return config
    
    def _detect_device_type(self, width: int, height: int, user_agent: str) -> DeviceType:
        """检测设备类型"""
        # 基于视口宽度的基本检测
        if width < 576:
            return DeviceType.MOBILE
        elif width < 768:
            return DeviceType.MOBILE  # 大屏手机
        elif width < 992:
            return DeviceType.TABLET
        elif width < 1400:
            return DeviceType.DESKTOP
        else:
            return DeviceType.LARGE_DESKTOP
    
    async def _apply_smart_rules(self, config: ResponsiveConfig, width: int, height: int) -> ResponsiveConfig:
        """应用智能规则"""
        applicable_rules = []
        
        for rule in self.smart_rules:
            if not rule.enabled:
                continue
                
            if self._rule_matches(rule, config, width, height):
                applicable_rules.append(rule)
        
        # 按优先级排序并应用规则
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        for rule in applicable_rules:
            config = self._apply_rule_actions(config, rule.actions)
            self.logger.debug(f"应用规则: {rule.name}")
        
        return config
    
    def _rule_matches(self, rule: SmartUIRule, config: ResponsiveConfig, width: int, height: int) -> bool:
        """检查规则是否匹配当前条件"""
        conditions = rule.conditions
        
        for key, value in conditions.items():
            if key == "device_type":
                if config.device_type.value != value:
                    return False
            elif key == "viewport_width":
                if isinstance(value, str) and value.startswith(">"):
                    threshold = int(value[1:])
                    if width <= threshold:
                        return False
                elif isinstance(value, str) and value.startswith("<"):
                    threshold = int(value[1:])
                    if width >= threshold:
                        return False
                elif width != value:
                    return False
            elif key == "touch_optimized":
                if config.touch_optimized != value:
                    return False
            elif key == "layout_columns":
                if config.layout_columns != value:
                    return False
        
        return True
    
    def _apply_rule_actions(self, config: ResponsiveConfig, actions: Dict[str, Any]) -> ResponsiveConfig:
        """应用规则动作"""
        # 创建配置副本
        new_config = ResponsiveConfig(**asdict(config))
        
        for action, value in actions.items():
            if action == "layout":
                if value == "stack":
                    new_config.layout_columns = 1
                elif value == "two_column":
                    new_config.layout_columns = 2
                elif value == "three_column":
                    new_config.layout_columns = 3
            elif action == "sidebar":
                if value == "hidden":
                    new_config.sidebar_width = None
                elif value == "collapsible":
                    new_config.sidebar_width = 250
                elif value == "fixed":
                    new_config.sidebar_width = 300
            elif action == "button_size":
                if value == "large":
                    new_config.spacing_scale *= 1.2
            elif action == "spacing":
                if value == "increased":
                    new_config.spacing_scale *= 1.1
            elif action == "content_density":
                if value == "high":
                    new_config.spacing_scale *= 0.9
            elif action == "sidebar_width":
                if value == "expanded":
                    new_config.sidebar_width = 400
        
        return new_config
    
    async def generate_responsive_css(self, config: ResponsiveConfig) -> str:
        """生成响应式CSS"""
        css_rules = []
        
        # 基础变量
        css_rules.append(f"""
:root {{
  --viewport-width: {config.viewport_width}px;
  --viewport-height: {config.viewport_height}px;
  --header-height: {config.header_height}px;
  --sidebar-width: {config.sidebar_width or 0}px;
  --font-scale: {config.font_scale};
  --spacing-scale: {config.spacing_scale};
  --layout-columns: {config.layout_columns};
}}
""")
        
        # 布局规则
        if config.layout_columns == 1:
            css_rules.append("""
.app-content {
  flex-direction: column;
}
.file-explorer-section,
.editor-section,
.sidebar {
  width: 100%;
  border-right: none;
  border-bottom: 1px solid #e9ecef;
}
""")
        elif config.layout_columns == 2:
            css_rules.append("""
.app-content {
  flex-direction: row;
}
.file-explorer-section {
  display: none;
}
.editor-section {
  flex: 1;
}
.sidebar {
  width: var(--sidebar-width);
}
""")
        else:  # 3 columns
            css_rules.append("""
.app-content {
  flex-direction: row;
}
.file-explorer-section {
  width: 300px;
}
.editor-section {
  flex: 1;
}
.sidebar {
  width: var(--sidebar-width);
}
""")
        
        # 触控优化
        if config.touch_optimized:
            css_rules.append("""
button, .clickable {
  min-height: 44px;
  min-width: 44px;
  padding: calc(8px * var(--spacing-scale));
}
.task-item {
  padding: calc(16px * var(--spacing-scale));
  margin-bottom: calc(8px * var(--spacing-scale));
}
""")
        
        # 字体缩放
        css_rules.append(f"""
body {{
  font-size: calc(14px * {config.font_scale});
}}
h1 {{ font-size: calc(2rem * {config.font_scale}); }}
h2 {{ font-size: calc(1.5rem * {config.font_scale}); }}
h3 {{ font-size: calc(1.25rem * {config.font_scale}); }}
""")
        
        return "\n".join(css_rules)
    
    async def generate_responsive_js(self, config: ResponsiveConfig) -> str:
        """生成响应式JavaScript"""
        js_code = f"""
// SmartUI 响应式配置
window.SmartUIConfig = {{
  deviceType: '{config.device_type.value}',
  breakpoint: '{config.breakpoint.value}',
  layoutColumns: {config.layout_columns},
  touchOptimized: {str(config.touch_optimized).lower()},
  sidebarWidth: {config.sidebar_width or 0},
  headerHeight: {config.header_height}
}};

// 设备检测和适配
class SmartUIAdapter {{
  constructor() {{
    this.config = window.SmartUIConfig;
    this.init();
  }}
  
  init() {{
    this.applyResponsiveClasses();
    this.setupEventListeners();
    this.optimizeForDevice();
  }}
  
  applyResponsiveClasses() {{
    const body = document.body;
    body.classList.add(`device-${{this.config.deviceType}}`);
    body.classList.add(`breakpoint-${{this.config.breakpoint}}`);
    body.classList.add(`columns-${{this.config.layoutColumns}}`);
    
    if (this.config.touchOptimized) {{
      body.classList.add('touch-optimized');
    }}
  }}
  
  setupEventListeners() {{
    window.addEventListener('resize', this.handleResize.bind(this));
    window.addEventListener('orientationchange', this.handleOrientationChange.bind(this));
  }}
  
  handleResize() {{
    // 重新检测设备类型
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    // 发送到后端重新配置
    this.requestReconfiguration(width, height);
  }}
  
  handleOrientationChange() {{
    setTimeout(() => {{
      this.handleResize();
    }}, 100);
  }}
  
  optimizeForDevice() {{
    if (this.config.touchOptimized) {{
      this.enableTouchOptimizations();
    }}
    
    if (this.config.deviceType === 'mobile') {{
      this.enableMobileOptimizations();
    }}
  }}
  
  enableTouchOptimizations() {{
    // 禁用hover效果
    const style = document.createElement('style');
    style.textContent = `
      @media (hover: none) {{
        .hover\\:bg-gray-100:hover {{
          background-color: inherit;
        }}
      }}
    `;
    document.head.appendChild(style);
  }}
  
  enableMobileOptimizations() {{
    // 移动端特定优化
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {{
      viewport.setAttribute('content', 
        'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
      );
    }}
  }}
  
  requestReconfiguration(width, height) {{
    // 向后端请求重新配置
    fetch('/api/smartui/reconfigure', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json'
      }},
      body: JSON.stringify({{
        viewport_width: width,
        viewport_height: height,
        user_agent: navigator.userAgent
      }})
    }})
    .then(response => response.json())
    .then(data => {{
      if (data.css) {{
        this.updateCSS(data.css);
      }}
    }})
    .catch(error => {{
      console.error('SmartUI reconfiguration failed:', error);
    }});
  }}
  
  updateCSS(newCSS) {{
    let styleElement = document.getElementById('smartui-dynamic-styles');
    if (!styleElement) {{
      styleElement = document.createElement('style');
      styleElement.id = 'smartui-dynamic-styles';
      document.head.appendChild(styleElement);
    }}
    styleElement.textContent = newCSS;
  }}
}}

// 初始化SmartUI适配器
document.addEventListener('DOMContentLoaded', () => {{
  window.smartUIAdapter = new SmartUIAdapter();
}});
"""
        return js_code
    
    async def get_ag_ui_guidance(self, component_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取AG-UI的智能指导"""
        if not self.ag_ui_generator:
            return {"guidance": "AG-UI not available", "recommendations": []}
        
        try:
            # 基于AG-UI的智能建议
            guidance = {
                "layout_recommendations": [],
                "component_suggestions": [],
                "styling_guidance": {},
                "interaction_patterns": []
            }
            
            # 根据当前配置获取AG-UI建议
            if self.current_config:
                if self.current_config.device_type == DeviceType.MOBILE:
                    guidance["layout_recommendations"].extend([
                        "使用单栏布局",
                        "增大触控目标",
                        "简化导航结构"
                    ])
                elif self.current_config.device_type == DeviceType.DESKTOP:
                    guidance["layout_recommendations"].extend([
                        "使用三栏布局",
                        "优化鼠标交互",
                        "增加快捷键支持"
                    ])
            
            return guidance
            
        except Exception as e:
            self.logger.error(f"获取AG-UI指导失败: {e}")
            return {"guidance": "Error getting AG-UI guidance", "error": str(e)}
    
    def get_current_config(self) -> Optional[ResponsiveConfig]:
        """获取当前配置"""
        return self.current_config
    
    def get_device_configs(self) -> Dict[DeviceType, ResponsiveConfig]:
        """获取所有设备配置"""
        return self.responsive_configs

