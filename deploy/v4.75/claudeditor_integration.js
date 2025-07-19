/**
 * ClaudeEditor 集成配置
 * 将演示系统集成到 ClaudeEditor 的中间栏
 */

// 演示面板集成配置
export const DemoPanelIntegration = {
  // 面板 ID
  id: 'powerautomation-demo-v475',
  
  // 面板名称
  name: 'PowerAutomation v4.75 演示',
  
  // 面板位置：中间栏
  position: 'center',
  
  // 面板图标
  icon: 'rocket',
  
  // 面板组件路径
  component: './deploy/v4.75/ClaudeEditorDemoPanel.jsx',
  
  // 是否默认显示
  defaultVisible: false,
  
  // 快捷键
  shortcut: 'cmd+shift+d',
  
  // 面板配置
  config: {
    // 最小宽度
    minWidth: 600,
    
    // 默认宽度
    defaultWidth: 800,
    
    // 是否可调整大小
    resizable: true,
    
    // 是否可关闭
    closable: true,
    
    // 是否持久化状态
    persistent: true
  },
  
  // 依赖的组件
  dependencies: [
    'StageWiseCommandDemo',
    'UnifiedDeploymentUI',
    'WorkflowAutomationDashboard',
    'MetricsVisualizationDashboard',
    'AGUIComplianceDashboard',
    'TestValidationDashboard'
  ],
  
  // 初始化函数
  initialize: async (editor) => {
    console.log('初始化 PowerAutomation 演示面板...');
    
    // 注册命令
    editor.registerCommand('demo:open', {
      name: '打开演示面板',
      handler: () => {
        editor.showPanel('powerautomation-demo-v475');
      }
    });
    
    // 注册菜单项
    editor.addMenuItem('view', {
      id: 'demo-panel',
      label: 'PowerAutomation 演示',
      command: 'demo:open',
      icon: 'rocket'
    });
    
    // 注册工具栏按钮
    editor.addToolbarButton({
      id: 'demo-button',
      tooltip: 'PowerAutomation v4.75 演示',
      icon: 'rocket',
      position: 'right',
      handler: () => {
        editor.togglePanel('powerautomation-demo-v475');
      }
    });
    
    return true;
  },
  
  // 面板激活时的回调
  onActivate: (panel, editor) => {
    console.log('演示面板已激活');
    
    // 发送激活事件
    editor.emit('demo:panel:activated', {
      panelId: panel.id,
      timestamp: new Date().toISOString()
    });
  },
  
  // 面板关闭时的回调
  onDeactivate: (panel, editor) => {
    console.log('演示面板已关闭');
    
    // 保存状态
    editor.saveState('demo-panel-state', {
      lastActiveDemo: panel.getState('activeDemo'),
      timestamp: new Date().toISOString()
    });
  },
  
  // 与其他面板的交互
  interactions: {
    // 与命令面板的交互
    commandPalette: {
      commands: [
        {
          id: 'demo:stagewise',
          name: '运行 StageWise 演示',
          category: '演示',
          handler: () => {
            editor.showPanel('powerautomation-demo-v475');
            editor.sendMessage('demo-panel', {
              action: 'setActiveDemo',
              demo: 'stagewise'
            });
          }
        },
        {
          id: 'demo:deployment',
          name: '查看部署系统',
          category: '演示',
          handler: () => {
            editor.showPanel('powerautomation-demo-v475');
            editor.sendMessage('demo-panel', {
              action: 'setActiveDemo',
              demo: 'deployment'
            });
          }
        }
      ]
    },
    
    // 与文件浏览器的交互
    fileExplorer: {
      contextMenu: [
        {
          id: 'demo:analyze-component',
          label: '在 SmartUI 合规性中分析',
          when: 'resourceExtname == .jsx || resourceExtname == .tsx',
          handler: (file) => {
            editor.showPanel('powerautomation-demo-v475');
            editor.sendMessage('demo-panel', {
              action: 'analyzeComponent',
              file: file.path
            });
          }
        }
      ]
    },
    
    // 与终端的交互
    terminal: {
      commands: {
        'demo': {
          description: '打开 PowerAutomation 演示面板',
          handler: () => {
            editor.showPanel('powerautomation-demo-v475');
          }
        },
        'demo:run': {
          description: '运行指定的演示',
          usage: 'demo:run <demo-id>',
          handler: (args) => {
            const demoId = args[0];
            editor.showPanel('powerautomation-demo-v475');
            editor.sendMessage('demo-panel', {
              action: 'setActiveDemo',
              demo: demoId
            });
          }
        }
      }
    }
  },
  
  // API 端点
  api: {
    // 获取演示状态
    getDemoStatus: async () => {
      return {
        version: '4.75',
        demos: [
          { id: 'stagewise', status: 'ready' },
          { id: 'deployment', status: 'ready' },
          { id: 'workflow', status: 'ready' },
          { id: 'metrics', status: 'ready' },
          { id: 'smartui', status: 'ready' },
          { id: 'test', status: 'ready' }
        ],
        metrics: {
          commandCompatibility: 100,
          costSaving: 80,
          uiResponse: 16,
          userSatisfaction: 92.5
        }
      };
    },
    
    // 运行演示
    runDemo: async (demoId) => {
      console.log(`运行演示: ${demoId}`);
      return { success: true, demoId };
    }
  }
};

// 注册到 ClaudeEditor
if (window.ClaudeEditor) {
  window.ClaudeEditor.registerPanel(DemoPanelIntegration);
} else {
  console.warn('ClaudeEditor 未找到，演示面板注册延迟');
  
  // 等待 ClaudeEditor 加载完成
  const checkInterval = setInterval(() => {
    if (window.ClaudeEditor) {
      window.ClaudeEditor.registerPanel(DemoPanelIntegration);
      clearInterval(checkInterval);
      console.log('演示面板已成功注册到 ClaudeEditor');
    }
  }, 100);
}