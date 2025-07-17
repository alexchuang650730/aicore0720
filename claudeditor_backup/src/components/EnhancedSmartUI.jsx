import React, { useState, useEffect, useRef, useCallback } from 'react';
import './EnhancedSmartUI.css';

// 基于 ag-ui 模式和三大系统指导书的增强版 SmartUI
const EnhancedSmartUI = () => {
  // MemoryOS 上下文集成系统 - 智能记忆和学习
  const [memoryContext, setMemoryContext] = useState({
    userPreferences: {
      theme: 'light',
      workflowPatterns: [],
      frequentTasks: []
    },
    workHistory: [],
    recommendations: []
  });

  // 钩子系统集成 - 生命周期管理
  const [hookSystem, setHookSystem] = useState({
    activeHooks: [],
    eventQueue: [],
    lifecycleState: 'initialized'
  });

  // ClaudeEditor 状态显示集成 - 实时监控
  const [editorState, setEditorState] = useState({
    activeComponents: 24,
    integrationLevel: 70.8,
    systemHealth: 'healthy',
    realTimeMetrics: {
      cpu: 45,
      memory: 62,
      network: 28
    }
  });

  // 1. 智能任务管理 - 动态任务创建和状态更新
  const [taskManager, setTaskManager] = useState({
    tasks: [
      {
        id: 'task_001',
        title: '查看GitHub最新状态',
        status: 'pending',
        priority: 'high',
        workflow: 'code_generation',
        progress: 0,
        createdAt: new Date(),
        estimatedTime: 300000, // 5分钟
        dependencies: []
      },
      {
        id: 'task_002',
        title: '测试飞书通知功能',
        status: 'in_progress',
        priority: 'medium',
        workflow: 'test_automation',
        progress: 45,
        createdAt: new Date(Date.now() - 600000),
        estimatedTime: 600000, // 10分钟
        dependencies: ['task_001']
      },
      {
        id: 'task_003',
        title: '检查MCP协调器状态',
        status: 'completed',
        priority: 'high',
        workflow: 'deployment_pipeline',
        progress: 100,
        createdAt: new Date(Date.now() - 1200000),
        estimatedTime: 180000, // 3分钟
        dependencies: []
      }
    ],
    activeWorkflows: ['code_generation', 'ui_design', 'test_automation']
  });

  // 2. AI对话增强 - 更智能的回复和上下文理解
  const [aiChat, setAiChat] = useState({
    messages: [
      {
        id: 'msg_001',
        type: 'ai',
        content: '✅ 系统已完全初始化！我正在监控六大工作流的状态，并准备为您提供智能协助。当前系统集成度为70.8%，所有核心组件运行正常。',
        timestamp: new Date(Date.now() - 300000),
        context: {
          systemState: 'healthy',
          activeWorkflows: 6,
          recommendations: ['优化代码生成工作流', '增强UI设计组件']
        }
      },
      {
        id: 'msg_002',
        type: 'user',
        content: '我需要实时看到所有工作流的状态，特别是六大工作流节点的进度和质量指标。',
        timestamp: new Date(Date.now() - 180000)
      },
      {
        id: 'msg_003',
        type: 'ai',
        content: '我理解您的需求。右侧Dashboard已经显示了六大工作流的实时状态。我可以为您创建自定义监控面板，或者设置特定的告警规则。您希望重点关注哪个工作流？',
        timestamp: new Date(Date.now() - 60000),
        context: {
          suggestedActions: ['创建监控面板', '设置告警规则', '优化工作流'],
          relatedWorkflows: ['code_generation', 'ui_design', 'api_development']
        }
      }
    ],
    isTyping: false,
    contextAwareness: {
      currentTopic: 'workflow_monitoring',
      userIntent: 'monitoring_setup',
      confidence: 0.92
    }
  });

  // 3. 实时数据同步 - 与后端MCP组件的数据同步
  const [realTimeSync, setRealTimeSync] = useState({
    connectionStatus: 'connected',
    lastSyncTime: new Date(),
    syncInterval: 5000, // 5秒
    mcpComponents: {
      codeflow_mcp: { status: 'active', lastUpdate: new Date(), data: { progress: 85, quality: 92 } },
      smartui_mcp: { status: 'active', lastUpdate: new Date(), data: { progress: 78, quality: 95 } },
      test_mcp: { status: 'active', lastUpdate: new Date(), data: { progress: 92, quality: 88 } },
      memoryos_mcp: { status: 'active', lastUpdate: new Date(), data: { usage: 45, efficiency: 94 } }
    }
  });

  // 4. 工作流触发 - 从对话中直接触发工作流
  const [workflowTrigger, setWorkflowTrigger] = useState({
    availableWorkflows: [
      { id: 'code_generation', name: '代码生成工作流', trigger: 'generate_code' },
      { id: 'ui_design', name: 'UI设计工作流', trigger: 'design_ui' },
      { id: 'api_development', name: 'API开发工作流', trigger: 'develop_api' },
      { id: 'database_design', name: '数据库设计工作流', trigger: 'design_database' },
      { id: 'test_automation', name: '测试自动化工作流', trigger: 'run_tests' },
      { id: 'deployment_pipeline', name: '部署流水线工作流', trigger: 'deploy_app' }
    ],
    triggerHistory: [],
    pendingTriggers: []
  });

  // 5. Monaco Editor集成 - 代码编辑和预览功能
  const [monacoEditor, setMonacoEditor] = useState({
    isVisible: false,
    currentFile: null,
    language: 'javascript',
    theme: 'vs-light',
    content: '',
    suggestions: [],
    diagnostics: []
  });

  const editorRef = useRef(null);
  const wsRef = useRef(null);

  // 实时数据同步功能
  useEffect(() => {
    // 模拟WebSocket连接
    const simulateRealTimeSync = () => {
      setRealTimeSync(prev => ({
        ...prev,
        lastSyncTime: new Date(),
        mcpComponents: {
          ...prev.mcpComponents,
          codeflow_mcp: {
            ...prev.mcpComponents.codeflow_mcp,
            data: {
              progress: Math.min(100, prev.mcpComponents.codeflow_mcp.data.progress + Math.random() * 2),
              quality: Math.max(85, Math.min(100, prev.mcpComponents.codeflow_mcp.data.quality + (Math.random() - 0.5) * 2))
            }
          }
        }
      }));
    };

    const interval = setInterval(simulateRealTimeSync, realTimeSync.syncInterval);
    return () => clearInterval(interval);
  }, [realTimeSync.syncInterval]);

  // 智能任务管理功能
  const createTask = useCallback((taskData) => {
    const newTask = {
      id: `task_${Date.now()}`,
      ...taskData,
      status: 'pending',
      progress: 0,
      createdAt: new Date()
    };

    setTaskManager(prev => ({
      ...prev,
      tasks: [...prev.tasks, newTask]
    }));

    // 触发钩子系统
    setHookSystem(prev => ({
      ...prev,
      eventQueue: [...prev.eventQueue, { type: 'task_created', data: newTask }]
    }));
  }, []);

  const updateTaskStatus = useCallback((taskId, status, progress = null) => {
    setTaskManager(prev => ({
      ...prev,
      tasks: prev.tasks.map(task => 
        task.id === taskId 
          ? { ...task, status, progress: progress !== null ? progress : task.progress }
          : task
      )
    }));
  }, []);

  // AI对话增强功能
  const sendMessage = useCallback((content) => {
    const userMessage = {
      id: `msg_${Date.now()}`,
      type: 'user',
      content,
      timestamp: new Date()
    };

    setAiChat(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isTyping: true
    }));

    // 智能回复生成
    setTimeout(() => {
      const aiResponse = generateIntelligentResponse(content, memoryContext, taskManager);
      
      setAiChat(prev => ({
        ...prev,
        messages: [...prev.messages, aiResponse],
        isTyping: false,
        contextAwareness: {
          ...prev.contextAwareness,
          currentTopic: extractTopic(content),
          userIntent: extractIntent(content),
          confidence: 0.88
        }
      }));
    }, 1500);
  }, [memoryContext, taskManager]);

  // 添加编辑器显示状态管理
  const [editorDisplayState, setEditorDisplayState] = useState({
    showEditor: true,
    showDemo: false,
    editorMode: 'code' // 'code', 'demo', 'hidden'
  });

  // 切换编辑器显示模式
  const toggleEditorMode = (mode) => {
    setEditorDisplayState(prev => ({
      ...prev,
      editorMode: mode,
      showEditor: mode === 'code',
      showDemo: mode === 'demo'
    }));
  };

  // 添加Dashboard展开状态管理
  const [dashboardState, setDashboardState] = useState({
    workflowsExpanded: false,
    monitoringExpanded: false,
    selectedWorkflow: null
  });

  // 切换Dashboard展开状态
  const toggleDashboard = (section) => {
    setDashboardState(prev => ({
      ...prev,
      [`${section}Expanded`]: !prev[`${section}Expanded`]
    }));
  };

  // 选择工作流
  const selectWorkflow = (workflowId) => {
    setDashboardState(prev => ({
      ...prev,
      selectedWorkflow: prev.selectedWorkflow === workflowId ? null : workflowId
    }));
  };
  const triggerWorkflow = useCallback((workflowId, parameters = {}) => {
    const workflow = workflowTrigger.availableWorkflows.find(w => w.id === workflowId);
    if (!workflow) return;

    const trigger = {
      id: `trigger_${Date.now()}`,
      workflowId,
      workflowName: workflow.name,
      parameters,
      status: 'pending',
      triggeredAt: new Date()
    };

    setWorkflowTrigger(prev => ({
      ...prev,
      pendingTriggers: [...prev.pendingTriggers, trigger],
      triggerHistory: [...prev.triggerHistory, trigger]
    }));

    // 创建对应的任务
    createTask({
      title: `执行${workflow.name}`,
      workflow: workflowId,
      priority: 'high',
      estimatedTime: 600000 // 10分钟
    });
  }, [workflowTrigger.availableWorkflows, createTask]);

  // Monaco Editor 功能
  const openEditor = useCallback((file = null) => {
    setMonacoEditor(prev => ({
      ...prev,
      isVisible: true,
      currentFile: file,
      content: file ? file.content : '// 开始编写代码...\n\nfunction example() {\n  console.log("Hello, PowerAutomation!");\n}\n\nexample();'
    }));
  }, []);

  const closeEditor = useCallback(() => {
    setMonacoEditor(prev => ({
      ...prev,
      isVisible: false,
      currentFile: null
    }));
  }, []);

  // 辅助函数
  const generateIntelligentResponse = (userInput, context, tasks) => {
    // 基于上下文的智能回复生成
    let response = '';
    
    if (userInput.includes('工作流') || userInput.includes('workflow')) {
      response = '我正在分析您的工作流需求。基于当前系统状态，我建议优先处理代码生成和UI设计工作流。';
    } else if (userInput.includes('任务') || userInput.includes('task')) {
      const pendingTasks = tasks.tasks.filter(t => t.status === 'pending').length;
      response = `当前有${pendingTasks}个待处理任务。我可以帮您优化任务执行顺序或创建新任务。`;
    } else if (userInput.includes('代码') || userInput.includes('code')) {
      response = '我可以为您打开Monaco编辑器进行代码编写，或者触发代码生成工作流。您希望进行哪种操作？';
    } else {
      response = '我理解您的需求。基于当前上下文，我建议我们专注于提高系统集成度和优化工作流效率。';
    }

    return {
      id: `msg_${Date.now()}`,
      type: 'ai',
      content: response,
      timestamp: new Date(),
      context: {
        systemState: editorState.systemHealth,
        suggestions: ['优化工作流', '创建新任务', '打开编辑器']
      }
    };
  };

  const extractTopic = (content) => {
    if (content.includes('工作流')) return 'workflow_management';
    if (content.includes('任务')) return 'task_management';
    if (content.includes('代码')) return 'code_development';
    return 'general';
  };

  const extractIntent = (content) => {
    if (content.includes('创建') || content.includes('新建')) return 'create';
    if (content.includes('查看') || content.includes('显示')) return 'view';
    if (content.includes('优化') || content.includes('改进')) return 'optimize';
    return 'general_inquiry';
  };

  return (
    <div className="enhanced-smartui">
      {/* 顶部导航栏 - 基于三大系统主题色 */}
      <header className="smartui-header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">🌐</span>
            <span className="logo-text">PowerAutomation AI</span>
            <span className="version-badge">v4.6.9.6</span>
          </div>
          <div className="system-indicators">
            <div className="indicator memory-system" title="MemoryOS 上下文集成系统">
              <span className="indicator-dot"></span>
              <span>记忆系统</span>
            </div>
            <div className="indicator hook-system" title="钩子系统集成">
              <span className="indicator-dot"></span>
              <span>钩子系统</span>
            </div>
            <div className="indicator display-system" title="ClaudeEditor 状态显示集成">
              <span className="indicator-dot"></span>
              <span>状态显示</span>
            </div>
          </div>
        </div>
        <div className="header-right">
          {/* 编辑器模式切换 */}
          <div className="editor-mode-toggle">
            <button 
              className={`mode-btn ${editorDisplayState.editorMode === 'code' ? 'active' : ''}`}
              onClick={() => toggleEditorMode('code')}
            >
              📝 编辑
            </button>
            <button 
              className={`mode-btn ${editorDisplayState.editorMode === 'demo' ? 'active' : ''}`}
              onClick={() => toggleEditorMode('demo')}
            >
              🎯 演示
            </button>
            <button 
              className={`mode-btn ${editorDisplayState.editorMode === 'hidden' ? 'active' : ''}`}
              onClick={() => toggleEditorMode('hidden')}
            >
              💬 对话
            </button>
          </div>
          
          <div className="sync-status">
            <span className="sync-indicator active"></span>
            <span>实时同步</span>
          </div>
          <button className="header-btn" onClick={() => openEditor()}>
            <span>📝</span> 编辑器
          </button>
          <button className="header-btn">
            <span>🚀</span> 部署
          </button>
        </div>
      </header>

      {/* 主要内容区域 - 动态布局 */}
      <main className={`smartui-main ${editorDisplayState.editorMode === 'hidden' ? 'chat-expanded' : ''}`}>
        {/* 左侧面板 - 分为上下两部分 */}
        <aside className="left-panel">
          {/* 左上：运维监控区 (第三核心系统) */}
          <div className="left-top-section">
            {/* 代码模型选择器 */}
            <div className="model-selector-section">
              <div className="model-header">
                <h4>🤖 代码模型</h4>
                <div className="model-status">
                  <span className="current-model">claude/k2</span>
                  <span className="model-indicator active"></span>
                </div>
              </div>
              
              <div className="model-controls">
                <select className="model-dropdown" defaultValue="claude/k2">
                  <option value="claude/k2">Claude Sonnet 3.5 (K2)</option>
                  <option value="claude/haiku">Claude Haiku 3.5</option>
                  <option value="gpt-4">GPT-4 Turbo</option>
                </select>
                
                <div className="token-stats">
                  <div className="token-item">
                    <span className="token-label">已使用:</span>
                    <span className="token-value">12.5K</span>
                  </div>
                  <div className="token-item">
                    <span className="token-label">节省:</span>
                    <span className="token-value saved">8.2K</span>
                  </div>
                  <div className="token-item">
                    <span className="token-label">效率:</span>
                    <span className="token-value efficiency">+39%</span>
                  </div>
                </div>
                
                <div className="model-features">
                  <div className="feature-tag">智能补全</div>
                  <div className="feature-tag">代码生成</div>
                  <div className="feature-tag">错误检测</div>
                </div>
              </div>
            </div>

            <div className="panel-header">
              <h3>🔧 运维监控区</h3>
              <div className="integration-badge">{editorState.integrationLevel}%</div>
            </div>

            {/* 系统健康状态 */}
            <div className="status-section">
              <h4>系统健康状态</h4>
              <div className="health-metrics">
                <div className="metric-item">
                  <span className="metric-label">CPU</span>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: `${editorState.realTimeMetrics.cpu}%` }}></div>
                  </div>
                  <span className="metric-value">{editorState.realTimeMetrics.cpu}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">内存</span>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: `${editorState.realTimeMetrics.memory}%` }}></div>
                  </div>
                  <span className="metric-value">{editorState.realTimeMetrics.memory}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">网络</span>
                  <div className="metric-bar">
                    <div className="metric-fill" style={{ width: `${editorState.realTimeMetrics.network}%` }}></div>
                  </div>
                  <span className="metric-value">{editorState.realTimeMetrics.network}%</span>
                </div>
              </div>
            </div>

            {/* MCP 组件状态 */}
            <div className="mcp-section">
              <h4>MCP 组件状态</h4>
              <div className="mcp-grid">
                {Object.entries(realTimeSync.mcpComponents).map(([key, component]) => (
                  <div key={key} className="mcp-card">
                    <div className="mcp-header">
                      <span className="mcp-name">{key.replace('_mcp', '')}</span>
                      <span className={`mcp-status ${component.status}`}></span>
                    </div>
                    <div className="mcp-metrics">
                      <div className="mcp-metric">
                        <span>进度: {component.data.progress || component.data.usage || 0}%</span>
                      </div>
                      <div className="mcp-metric">
                        <span>质量: {component.data.quality || component.data.efficiency || 0}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 实时同步状态 */}
            <div className="sync-section">
              <h4>实时同步状态</h4>
              <div className="sync-info">
                <div className="sync-item">
                  <span>连接状态:</span>
                  <span className={`sync-status ${realTimeSync.connectionStatus}`}>
                    {realTimeSync.connectionStatus === 'connected' ? '已连接' : '断开'}
                  </span>
                </div>
                <div className="sync-item">
                  <span>最后同步:</span>
                  <span>{realTimeSync.lastSyncTime.toLocaleTimeString()}</span>
                </div>
                <div className="sync-item">
                  <span>同步间隔:</span>
                  <span>{realTimeSync.syncInterval / 1000}秒</span>
                </div>
              </div>
            </div>
          </div>

          {/* 左下：快速操作区 + 六大工作流Dashboard */}
          <div className="left-bottom-section">
            {/* 快速操作区 */}
            <div className="quick-actions-section">
              <div className="panel-header">
                <h3>⚡ 快速操作</h3>
              </div>
              
              <div className="quick-actions-grid">
                {/* 文件操作 */}
                <button className="quick-action-btn file-action">
                  <span className="action-icon">📁</span>
                  <span className="action-text">打开文件夹</span>
                </button>
                
                {/* Git 操作 */}
                <button className="quick-action-btn git-action">
                  <span className="action-icon">🌿</span>
                  <span className="action-text">克隆 Git 仓库</span>
                </button>
                
                {/* 远程连接 */}
                <button className="quick-action-btn remote-action">
                  <span className="action-icon">🔗</span>
                  <span className="action-text">连接远程主机</span>
                </button>
                
                {/* 终端 + Command MCP 整合 */}
                <button className="quick-action-btn terminal-command-action">
                  <span className="action-icon">⚡</span>
                  <span className="action-text">终端 & Command MCP</span>
                </button>
                
                {/* 附件操作 */}
                <button className="quick-action-btn attachment-action">
                  <span className="action-icon">📎</span>
                  <span className="action-text">管理附件</span>
                </button>
              </div>
              
              {/* 最近项目 */}
              <div className="recent-projects">
                <h4>最近</h4>
                <div className="recent-list">
                  <div className="recent-item">
                    <div className="project-avatar">C</div>
                    <div className="project-info">
                      <div className="project-name">communitypowerauto</div>
                      <div className="project-path">~/communitypowerauto</div>
                    </div>
                    <div className="project-status">✓</div>
                  </div>
                  <div className="recent-item">
                    <div className="project-avatar">VD</div>
                    <div className="project-info">
                      <div className="project-name">vsix_deploy</div>
                      <div className="project-path">~/vsix_deploy</div>
                    </div>
                    <div className="project-status"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* 六大工作流Dashboard */}
            <div className="workflows-dashboard">
              <div className="panel-header">
                <h3>🚀 六大工作流Dashboard</h3>
                <div className="workflow-summary">
                  <span>{taskManager.activeWorkflows.length}/6 活跃</span>
                </div>
              </div>

              <div className="workflows-grid">
                {workflowTrigger.availableWorkflows.map(workflow => {
                  const mcpData = realTimeSync.mcpComponents[`${workflow.id.split('_')[0]}_mcp`] || 
                                 { data: { progress: Math.floor(Math.random() * 100), quality: Math.floor(Math.random() * 100) } };
                  
                  return (
                    <div key={workflow.id} className="workflow-card">
                      <div className="workflow-header">
                        <span className="workflow-icon">
                          {workflow.id === 'code_generation' && '💻'}
                          {workflow.id === 'ui_design' && '🎨'}
                          {workflow.id === 'api_development' && '🔗'}
                          {workflow.id === 'database_design' && '🗄️'}
                          {workflow.id === 'test_automation' && '🧪'}
                          {workflow.id === 'deployment_pipeline' && '🚀'}
                        </span>
                        <span className="workflow-name">{workflow.name}</span>
                      </div>
                      <div className="workflow-metrics">
                        <div className="metric-row">
                          <span>进度:</span>
                          <span className="metric-value">{mcpData.data.progress}%</span>
                        </div>
                        <div className="metric-row">
                          <span>质量:</span>
                          <span className="metric-value">{mcpData.data.quality}</span>
                        </div>
                      </div>
                      <button 
                        className="workflow-trigger-btn"
                        onClick={() => triggerWorkflow(workflow.id)}
                      >
                        触发工作流
                      </button>
                    </div>
                  );
                })}
              </div>

              {/* 工作流触发历史 */}
              <div className="trigger-history">
                <h4>触发历史</h4>
                <div className="history-list">
                  {workflowTrigger.triggerHistory.slice(-5).map(trigger => (
                    <div key={trigger.id} className="history-item">
                      <span className="history-workflow">{trigger.workflowName}</span>
                      <span className="history-time">
                        {trigger.triggeredAt.toLocaleTimeString()}
                      </span>
                      <span className={`history-status ${trigger.status}`}>
                        {trigger.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* 中间面板 - Monaco Editor 代码编辑器和 LSP (第一核心系统) - 条件显示 */}
        {editorDisplayState.showEditor && (
          <section className="center-panel">
          {/* Monaco Editor 主要区域 */}
          <div className="monaco-main-section">
            <div className="section-header">
              <h3>📝 Monaco Editor with LSP</h3>
              <div className="editor-controls">
                <select 
                  value={monacoEditor.language}
                  onChange={(e) => setMonacoEditor(prev => ({ ...prev, language: e.target.value }))}
                  className="language-selector"
                >
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="python">Python</option>
                  <option value="html">HTML</option>
                  <option value="css">CSS</option>
                  <option value="json">JSON</option>
                </select>
                <button 
                  className="theme-toggle-btn"
                  onClick={() => {
                    const newTheme = monacoEditor.theme === 'vs-light' ? 'vs-dark' : 'vs-light';
                    setMonacoEditor(prev => ({ ...prev, theme: newTheme }));
                  }}
                >
                  {monacoEditor.theme === 'vs-light' ? '🌙' : '☀️'}
                </button>
                
                {/* 编辑器操作按钮 - 移到右上角 */}
                <div className="editor-action-buttons">
                  <button className="editor-action-btn save-btn">💾 保存</button>
                  <button className="editor-action-btn run-btn">▶️ 运行</button>
                  <button className="editor-action-btn format-btn">🔧 格式化</button>
                </div>
              </div>
            </div>
            
            {/* 文件标签栏 */}
            <div className="file-tabs">
              <div className="file-tab active">
                <span className="file-icon">📄</span>
                <span className="file-name">example.jsx</span>
                <span className="modified-indicator">●</span>
              </div>
              <div className="file-tab">
                <span className="file-icon">🎨</span>
                <span className="file-name">styles.css</span>
              </div>
              <div className="file-tab">
                <span className="file-icon">⚙️</span>
                <span className="file-name">config.json</span>
              </div>
            </div>

            {/* Monaco Editor 区域 */}
            <div className="monaco-editor-area">
              <div className="editor-container">
                <div className="line-numbers">
                  {Array.from({ length: 30 }, (_, i) => (
                    <div key={i + 1} className="line-number">{i + 1}</div>
                  ))}
                </div>
                <div className="editor-content">
                  <pre><code>{`// PowerAutomation ClaudeEditor - Monaco Editor with LSP
// 智能代码编辑器，支持语法高亮、智能补全、错误检测

import React from 'react';

/**
 * 示例组件 - 展示 Monaco Editor 的强大功能
 * @param {Object} props - 组件属性
 * @returns {JSX.Element} React 组件
 */
const ExampleComponent = ({ title, data }) => {
  const [state, setState] = React.useState({
    loading: false,
    items: data || []
  });

  // 异步数据处理函数
  const handleDataFetch = async () => {
    setState(prev => ({ ...prev, loading: true }));
    
    try {
      const response = await fetch('/api/data');
      const result = await response.json();
      
      setState({
        loading: false,
        items: result.items
      });
    } catch (error) {
      console.error('数据获取失败:', error);
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  return (
    <div className="example-component">
      <h2>{title}</h2>
      {state.loading ? (
        <div>加载中...</div>
      ) : (
        <ul>
          {state.items.map((item, index) => (
            <li key={index}>{item.name}</li>
          ))}
        </ul>
      )}
      <button onClick={handleDataFetch}>
        刷新数据
      </button>
    </div>
  );
};

export default ExampleComponent;`}</code></pre>
                </div>
              </div>
              
              {/* LSP 侧边面板 */}
              <div className="lsp-side-panel">
                {/* 诊断信息 */}
                <div className="lsp-section">
                  <h4>🔍 诊断信息</h4>
                  <div className="diagnostics-list">
                    <div className="diagnostic-item warning">
                      <span className="diagnostic-line">行 15</span>
                      <span className="diagnostic-message">未使用的变量</span>
                    </div>
                    <div className="diagnostic-item info">
                      <span className="diagnostic-line">行 23</span>
                      <span className="diagnostic-message">建议添加类型注解</span>
                    </div>
                  </div>
                </div>

                {/* 大纲视图 */}
                <div className="lsp-section">
                  <h4>📋 大纲</h4>
                  <div className="outline-list">
                    <div className="outline-item">
                      <span className="outline-icon">🔧</span>
                      <span>ExampleComponent</span>
                    </div>
                    <div className="outline-item">
                      <span className="outline-icon">⚡</span>
                      <span>handleDataFetch</span>
                    </div>
                    <div className="outline-item">
                      <span className="outline-icon">📦</span>
                      <span>useState</span>
                    </div>
                  </div>
                </div>

                {/* LSP 状态 */}
                <div className="lsp-section">
                  <h4>🔗 LSP 状态</h4>
                  <div className="lsp-status-info">
                    <div className="status-item">
                      <span className="status-indicator connected"></span>
                      <span>已连接</span>
                    </div>
                    <div className="status-item">
                      <span>语言服务器: TypeScript</span>
                    </div>
                    <div className="status-item">
                      <span>智能补全: 启用</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 编辑器底部状态栏 */}
            <div className="monaco-status-bar">
              <div className="status-left">
                <span>行: 15</span>
                <span>列: 23</span>
                <span>选择: 0</span>
                <span>语言: {monacoEditor.language}</span>
              </div>
              <div className="status-right">
                <span>UTF-8</span>
                <span>LF</span>
                <span>空格: 2</span>
              </div>
            </div>
          </div>
        </section>
        )}

        {/* 右侧面板 - AI助手对话区 (第二核心系统) */}
        <aside className="right-panel">
          <div className="chat-header">
            <h3>🤖 AI助手对话区</h3>
            <div className="chat-status">
              <span className="status-indicator active"></span>
              <span>智能协作中</span>
              {aiChat.isTyping && <span className="typing-indicator">AI正在输入...</span>}
            </div>
          </div>
          
          <div className="chat-messages">
            {aiChat.messages.map(message => (
              <div key={message.id} className={`message ${message.type}-message`}>
                <div className="message-avatar">
                  {message.type === 'ai' ? '🤖' : '👤'}
                </div>
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  <div className="message-meta">
                    <span className="message-time">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                    {message.context && (
                      <div className="message-context">
                        {message.context.suggestions && (
                          <div className="suggestions">
                            {message.context.suggestions.map((suggestion, index) => (
                              <button 
                                key={index} 
                                className="suggestion-btn"
                                onClick={() => sendMessage(suggestion)}
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="chat-input-area">
            <div className="workflow-triggers">
              <span>快速触发:</span>
              {workflowTrigger.availableWorkflows.slice(0, 3).map(workflow => (
                <button 
                  key={workflow.id}
                  className="trigger-btn"
                  onClick={() => triggerWorkflow(workflow.id)}
                >
                  {workflow.name}
                </button>
              ))}
            </div>
            <div className="input-container">
              <input 
                type="text" 
                placeholder="描述您的需求，AI将智能协助并可直接触发工作流..."
                className="chat-input"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.target.value.trim()) {
                    sendMessage(e.target.value);
                    e.target.value = '';
                  }
                }}
              />
              <button className="send-btn">📤</button>
            </div>
          </div>
        </aside>
      </main>

      {/* Monaco Editor 模态框 */}
      {monacoEditor.isVisible && (
        <div className="monaco-modal">
          <div className="monaco-container">
            <div className="monaco-header">
              <h3>📝 Monaco Editor</h3>
              <div className="monaco-controls">
                <select 
                  value={monacoEditor.language}
                  onChange={(e) => setMonacoEditor(prev => ({ ...prev, language: e.target.value }))}
                >
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="python">Python</option>
                  <option value="html">HTML</option>
                  <option value="css">CSS</option>
                </select>
                <button className="monaco-btn" onClick={closeEditor}>✖️ 关闭</button>
              </div>
            </div>
            <div className="monaco-editor-area">
              <textarea 
                ref={editorRef}
                value={monacoEditor.content}
                onChange={(e) => setMonacoEditor(prev => ({ ...prev, content: e.target.value }))}
                className="monaco-textarea"
                placeholder="在此编写代码..."
              />
            </div>
            <div className="monaco-footer">
              <div className="editor-status">
                <span>语言: {monacoEditor.language}</span>
                <span>行数: {monacoEditor.content.split('\n').length}</span>
                <span>字符: {monacoEditor.content.length}</span>
              </div>
            </div>
          </div>
        )}
    </div>
  );
};

export default EnhancedSmartUI;

