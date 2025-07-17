import React, { useState, useEffect } from 'react';
import './SmartUILayout.css';

// 基于 CodeFlow 分析和三大系统指导书的 SmartUI 三栏布局组件
const SmartUILayout = () => {
  // 模式切换状态 - 支持编  // 模式状态管理
  const [currentMode, setCurrentMode] = useState('edit'); // 'edit', 'demo', 'chat'
  
  // 工作流展开状态管理
  const [workflowsExpanded, setWorkflowsExpanded] = useState(false);
  
  // 最近部署文件状态管理
  const [recentFilesExpanded, setRecentFilesExpanded] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  
  // 模型切换和Token统计状态管理
  const [currentModel, setCurrentModel] = useState('Claude');
  const [modelStats, setModelStats] = useState({
    currentModel: 'Claude-3.5-Sonnet',
    currentRepo: 'aicore0716',
    tokensSaved: 12847,
    totalTokens: 45623,
    savingsPercentage: 28.2,
    lastSwitchTime: '2分钟前'
  });

  // 命令输入和智能补全状态管理
  const [commandInput, setCommandInput] = useState('');
  const [commandSuggestions, setCommandSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  // 预定义的命令列表
  const predefinedCommands = [
    { command: 'npm install', icon: '⚡', description: '安装依赖包' },
    { command: 'npm run dev', icon: '🔧', description: '启动开发服务器' },
    { command: 'npm run build', icon: '📦', description: '构建项目' },
    { command: 'npm test', icon: '🧪', description: '运行测试' },
    { command: 'git status', icon: '📊', description: '查看Git状态' },
    { command: 'git add .', icon: '➕', description: '添加所有文件' },
    { command: 'git commit -m', icon: '💾', description: '提交更改' },
    { command: 'git push', icon: '🚀', description: '推送到远程' },
    { command: 'ls -la', icon: '📁', description: '列出文件详情' },
    { command: 'cd', icon: '📂', description: '切换目录' }
  ];
  
  // 系统状态数据 - 基于三大核心系统
  const [systemStatus, setSystemStatus] = useState({
    // 实时状态
    realTimeStatus: {
      points: { value: 2847, change: +127 },
      savings: { value: 8.42, currency: '$' },
      systemStatus: '运行中',
      intelligentRouting: '端侧处理'
    },
    
    // Git仓库信息
    gitRepository: {
      currentRepo: 'aicore0716',
      branch: 'main',
      checkinStats: {
        today: 12,
        thisWeek: 45,
        thisMonth: 156
      },
      prStats: {
        open: 3,
        merged: 28,
        pending: 5
      },
      modifiedUncommitted: {
        files: 8,
        lines: 234
      }
    },

    mcpCoordinator: { status: '运行中', color: 'blue', components: 24 },
    feishuIntegration: { status: '已连接', color: 'green', notifications: 24, groups: 3 },
    githubSync: { status: '同步中', color: 'yellow', branch: 'v0.6', lastSync: '2分钟前' }
  });

  // 最近部署的Release文件数据
  const [recentReleaseFiles, setRecentReleaseFiles] = useState([
    {
      id: 'powerautomation_v4.6.9.6',
      name: 'PowerAutomation_三大核心系统完整指导书_v4.6.9.6.md',
      type: 'markdown',
      size: '2.3MB',
      deployTime: '2小时前',
      status: 'deployed',
      content: '# PowerAutomation 三大核心系统完整指导书\n\n## 系统概述\n这是一个完整的PowerAutomation系统指导书...'
    },
    {
      id: 'claudeditor_v1.2.0',
      name: 'ClaudeEditor_智能代码编辑器_v1.2.0.js',
      type: 'javascript',
      size: '856KB',
      deployTime: '4小时前',
      status: 'deployed',
      content: '// ClaudeEditor 智能代码编辑器\nconst ClaudeEditor = {\n  version: "1.2.0",\n  initialize() {\n    console.log("ClaudeEditor initialized");\n  }\n};'
    },
    {
      id: 'smartui_layout_v2.1',
      name: 'SmartUILayout_响应式布局组件_v2.1.jsx',
      type: 'react',
      size: '124KB',
      deployTime: '6小时前',
      status: 'deployed',
      content: 'import React, { useState } from "react";\n\nconst SmartUILayout = () => {\n  const [currentMode, setCurrentMode] = useState("edit");\n  return <div>SmartUI Layout Component</div>;\n};'
    },
    {
      id: 'mcp_coordinator_v3.0',
      name: 'MCP_协调器核心模块_v3.0.py',
      type: 'python',
      size: '445KB',
      deployTime: '1天前',
      status: 'deployed',
      content: '# MCP 协调器核心模块\nclass MCPCoordinator:\n    def __init__(self):\n        self.components = []\n        self.status = "running"\n    \n    def coordinate(self):\n        pass'
    },
    {
      id: 'api_gateway_v1.8',
      name: 'API_Gateway_网关服务_v1.8.json',
      type: 'json',
      size: '67KB',
      deployTime: '2天前',
      status: 'deployed',
      content: '{\n  "apiVersion": "v1.8",\n  "kind": "Gateway",\n  "metadata": {\n    "name": "api-gateway",\n    "namespace": "default"\n  },\n  "spec": {\n    "routes": []\n  }\n}'
    }
  ]);

  // 处理文件选择
  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setCurrentMode('edit'); // 切换到编辑模式显示文件内容
  };

  // 处理模型切换
  const handleModelSwitch = (model) => {
    setCurrentModel(model);
    setModelStats(prev => ({
      ...prev,
      currentModel: model === 'K2' ? 'K2-Advanced' : 'Claude-3.5-Sonnet',
      lastSwitchTime: '刚刚'
    }));
  };

  // 处理命令输入变化
  const handleCommandInputChange = (e) => {
    const value = e.target.value;
    setCommandInput(value);
    
    if (value.trim()) {
      const filtered = predefinedCommands.filter(cmd => 
        cmd.command.toLowerCase().includes(value.toLowerCase()) ||
        cmd.description.includes(value)
      );
      setCommandSuggestions(filtered);
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  // 处理命令选择
  const handleCommandSelect = (command) => {
    setCommandInput(command);
    setShowSuggestions(false);
  };

  // 处理命令执行
  const handleCommandExecute = () => {
    if (commandInput.trim()) {
      console.log('执行命令:', commandInput);
      // 这里可以添加实际的命令执行逻辑
      setCommandInput('');
      setShowSuggestions(false);
    }
  };

  // 处理键盘事件
  const handleCommandKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleCommandExecute();
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  // 六大工作流状态 - 基于 CodeFlow 分析结果
  const [sixWorkflows, setSixWorkflows] = useState([
    {
      id: 'code_generation',
      name: '代码生成工作流',
      icon: '💻',
      status: '运行中',
      color: 'blue',
      progress: 100,
      quality: 92,
      components: ['codeflow', 'zen', 'mirror_code', 'test']
    },
    {
      id: 'ui_design',
      name: 'UI设计工作流',
      icon: '🎨',
      status: '运行中',
      color: 'purple',
      progress: 85,
      quality: 95,
      components: ['smartui', 'ag-ui', 'stagewise', 'codeflow']
    },
    {
      id: 'api_development',
      name: 'API开发工作流',
      icon: '🔗',
      status: '待执行',
      color: 'orange',
      progress: 15,
      quality: 0,
      components: ['codeflow', 'test', 'security', 'release_trigger']
    },
    {
      id: 'database_design',
      name: '数据库设计工作流',
      icon: '🗄️',
      status: '规划中',
      color: 'green',
      progress: 30,
      quality: 88,
      components: ['deepgraph', 'codeflow', 'test']
    },
    {
      id: 'test_automation',
      name: '测试自动化工作流',
      icon: '🧪',
      status: '运行中',
      color: 'cyan',
      progress: 78,
      quality: 94,
      components: ['test', 'ag-ui', 'stagewise', 'intelligent_monitoring']
    },
    {
      id: 'deployment_pipeline',
      name: '部署流水线工作流',
      icon: '🚀',
      status: '监控中',
      color: 'red',
      progress: 92,
      quality: 97,
      components: ['release_trigger', 'zen', 'intelligent_monitoring', 'operations']
    }
  ]);

  // AI对话历史
  const [chatHistory, setChatHistory] = useState([
    {
      type: 'ai',
      message: '✅ 完全理解！右侧面板已经集成了六大工作流Dashboard，实时显示代码生成、UI设计、API开发、数据库设计、测试自动化、部署流水线的状态。',
      timestamp: new Date()
    },
    {
      type: 'user',
      message: '很好！我需要实时看到所有工作流的状态，特别是六大工作流节点的进度和质量指标。',
      timestamp: new Date()
    }
  ]);

  const [inputMessage, setInputMessage] = useState('');

  // 发送消息
  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      setChatHistory(prev => [...prev, {
        type: 'user',
        message: inputMessage,
        timestamp: new Date()
      }]);
      setInputMessage('');
      
      // 模拟AI回复
      setTimeout(() => {
        setChatHistory(prev => [...prev, {
          type: 'ai',
          message: '我理解您的需求，正在分析工作流状态并提供智能建议...',
          timestamp: new Date()
        }]);
      }, 1000);
    }
  };

  return (
    <div className="smartui-layout">
      {/* 顶部导航栏 */}
      <header className="smartui-header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">🌐</span>
            <span className="logo-text">PowerAutomation AI</span>
          </div>
          <div className="subtitle">智慧UI助手 - 在线 | MCP协调中</div>
        </div>
        <div className="header-center">
          {/* 模式切换按钮 */}
          <div className="mode-switcher">
            <button 
              className={`mode-btn ${currentMode === 'edit' ? 'active' : ''}`}
              onClick={() => setCurrentMode('edit')}
            >
              📝 编辑
            </button>
            <button 
              className={`mode-btn ${currentMode === 'demo' ? 'active' : ''}`}
              onClick={() => setCurrentMode('demo')}
            >
              🎯 演示
            </button>
            <button 
              className={`mode-btn ${currentMode === 'chat' ? 'active' : ''}`}
              onClick={() => setCurrentMode('chat')}
            >
              💬 对话
            </button>
          </div>
        </div>
        <div className="header-right">
        </div>
      </header>

      {/* 主要内容区域 */}
      <main className={`smartui-main ${currentMode === 'chat' ? 'chat-mode' : 'normal-mode'}`}>
        {/* 左侧系统状态监控面板 - 第三核心系统：运维监控区 */}
        <aside className="left-panel">
          {/* 模型切换和Token统计区 */}
          <div className="model-switch-section">
            <div className="model-switch-header">
              <h3 className="section-title">
                <span className="model-icon">🤖</span>
                AI模型控制
              </h3>
            </div>
            
            <div className="model-switch-controls">
              <div className="model-buttons">
                <button 
                  className={`model-btn ${currentModel === 'K2' ? 'active' : ''}`}
                  onClick={() => handleModelSwitch('K2')}
                >
                  <span className="model-name">K2</span>
                  <span className="model-badge">高级</span>
                </button>
                <button 
                  className={`model-btn ${currentModel === 'Claude' ? 'active' : ''}`}
                  onClick={() => handleModelSwitch('Claude')}
                >
                  <span className="model-name">Claude</span>
                  <span className="model-badge">标准</span>
                </button>
              </div>
              
              <div className="model-info">
                <div className="current-model">
                  <span className="info-label">当前模型:</span>
                  <span className="info-value">{modelStats.currentModel}</span>
                </div>
                <div className="current-repo">
                  <span className="info-label">当前仓库:</span>
                  <span className="info-value">{modelStats.currentRepo}</span>
                </div>
              </div>
              
              <div className="token-stats">
                <div className="token-saved">
                  <span className="token-icon">💰</span>
                  <div className="token-details">
                    <span className="token-label">已节省Token</span>
                    <span className="token-value">{modelStats.tokensSaved.toLocaleString()}</span>
                  </div>
                </div>
                <div className="token-total">
                  <span className="token-icon">📊</span>
                  <div className="token-details">
                    <span className="token-label">总Token使用</span>
                    <span className="token-value">{modelStats.totalTokens.toLocaleString()}</span>
                  </div>
                </div>
                <div className="savings-percentage">
                  <span className="savings-label">节省率:</span>
                  <span className="savings-value">{modelStats.savingsPercentage}%</span>
                </div>
                <div className="last-switch">
                  <span className="switch-label">上次切换:</span>
                  <span className="switch-time">{modelStats.lastSwitchTime}</span>
                </div>
              </div>
            </div>
          </div>

          {/* 实时状态区 */}
          <div className="panel-section">
            <h3 className="panel-title">
              <span className="status-icon">📊</span>
              实时状态
            </h3>
          </div>

          {/* 实时状态项 - 两列布局 */}
          <div className="status-grid">
            {/* 第一列 */}
            <div className="status-column">
              {/* 积分状态 */}
              <div className="status-item">
                <div className="status-icon">💎</div>
                <div className="status-content">
                  <span className="status-label">积分</span>
                  <span className="status-value">
                    {systemStatus.realTimeStatus.points.value.toLocaleString()} 
                    <span className="status-change positive">
                      ({systemStatus.realTimeStatus.points.change > 0 ? '+' : ''}{systemStatus.realTimeStatus.points.change})
                    </span>
                  </span>
                </div>
              </div>

              {/* 系统状态 */}
              <div className="status-item">
                <div className="status-icon">🟢</div>
                <div className="status-content">
                  <span className="status-label">系统状态</span>
                  <span className="status-value">{systemStatus.realTimeStatus.systemStatus}</span>
                </div>
              </div>
            </div>

            {/* 第二列 */}
            <div className="status-column">
              {/* 节省状态 */}
              <div className="status-item">
                <div className="status-icon">💰</div>
                <div className="status-content">
                  <span className="status-label">节省</span>
                  <span className="status-value">
                    {systemStatus.realTimeStatus.savings.currency}{systemStatus.realTimeStatus.savings.value}
                  </span>
                </div>
              </div>

              {/* 智慧路由 */}
              <div className="status-item">
                <div className="status-icon">⚡</div>
                <div className="status-content">
                  <span className="status-label">智慧路由</span>
                  <span className="status-value">{systemStatus.realTimeStatus.intelligentRouting}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Git仓库统计 */}
          <div className="panel-section">
            <h3 className="panel-title">
              <span className="status-icon">📁</span>
              Git仓库统计
            </h3>
          </div>

          {/* 当前仓库 */}
          <div className="git-repo-info">
            <div className="repo-name">
              <span className="repo-icon">📂</span>
              <span className="repo-text">{systemStatus.gitRepository.currentRepo}</span>
              <span className="branch-tag">{systemStatus.gitRepository.branch}</span>
            </div>
          </div>

          {/* Checkin统计 */}
          <div className="git-stats-grid">
            <div className="git-stat-card">
              <div className="git-stat-value">{systemStatus.gitRepository.checkinStats.today}</div>
              <div className="git-stat-label">今日Checkin</div>
            </div>
            <div className="git-stat-card">
              <div className="git-stat-value">{systemStatus.gitRepository.checkinStats.thisWeek}</div>
              <div className="git-stat-label">本周Checkin</div>
            </div>
          </div>

          {/* PR统计 */}
          <div className="git-stats-grid">
            <div className="git-stat-card">
              <div className="git-stat-value">{systemStatus.gitRepository.prStats.open}</div>
              <div className="git-stat-label">开放PR</div>
            </div>
            <div className="git-stat-card">
              <div className="git-stat-value">{systemStatus.gitRepository.prStats.merged}</div>
              <div className="git-stat-label">已合并PR</div>
            </div>
          </div>

          {/* 已修改未checkin */}
          <div className="uncommitted-changes">
            <div className="uncommitted-header">
              <span className="uncommitted-icon">⚠️</span>
              <span className="uncommitted-title">已修改未Checkin</span>
            </div>
            <div className="uncommitted-stats">
              <span className="uncommitted-files">{systemStatus.gitRepository.modifiedUncommitted.files} 文件</span>
              <span className="uncommitted-lines">{systemStatus.gitRepository.modifiedUncommitted.lines} 行</span>
            </div>
          </div>

          {/* 快速操作区 */}
          <div className="panel-section">
            <h3 className="panel-title">
              <span className="status-icon">🚀</span>
              快速操作
            </h3>
          </div>

          {/* 文件管理 */}
          <button className="quick-action-btn primary">
            <span className="action-icon">📁</span>
            <span className="action-text">打开文件夹</span>
          </button>

          <button className="quick-action-btn secondary">
            <span className="action-icon">🔄</span>
            <span className="action-text">克隆Git仓库</span>
          </button>

          <button className="quick-action-btn secondary">
            <span className="action-icon">🖥️</span>
            <span className="action-text">连接远程主机</span>
          </button>

          {/* Command MCP 智能补全输入 */}
          <div className="command-mcp-section">
            <h4 className="command-title">Command MCP</h4>
            
            <div className="command-input-container">
              <input
                type="text"
                className="command-input"
                placeholder="输入命令... (如: npm install)"
                value={commandInput}
                onChange={handleCommandInputChange}
                onKeyPress={handleCommandKeyPress}
              />
              <button 
                className="command-execute-btn"
                onClick={handleCommandExecute}
                disabled={!commandInput.trim()}
              >
                ▶
              </button>
              
              {showSuggestions && commandSuggestions.length > 0 && (
                <div className="command-suggestions">
                  {commandSuggestions.map((suggestion, index) => (
                    <div 
                      key={index}
                      className="suggestion-item"
                      onClick={() => handleCommandSelect(suggestion.command)}
                    >
                      <span className="suggestion-icon">{suggestion.icon}</span>
                      <div className="suggestion-content">
                        <span className="suggestion-command">{suggestion.command}</span>
                        <span className="suggestion-description">{suggestion.description}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* 最近部署文件管理 */}
          <div className="recent-deploy-section">
            <div 
              className="recent-deploy-header"
              onClick={() => setRecentFilesExpanded(!recentFilesExpanded)}
            >
              <h4 className="recent-deploy-title">最近部署文件</h4>
              <span className={`expand-icon ${recentFilesExpanded ? 'expanded' : ''}`}>
                {recentFilesExpanded ? '▼' : '▶'}
              </span>
            </div>
            
            {recentFilesExpanded && (
              <div className="recent-deploy-files">
                {recentReleaseFiles.map((file) => (
                  <div 
                    key={file.id} 
                    className={`deploy-file-item ${selectedFile?.id === file.id ? 'selected' : ''}`}
                    onClick={() => handleFileSelect(file)}
                  >
                    <div className="file-icon-wrapper">
                      <span className={`file-type-icon ${file.type}`}>
                        {file.type === 'markdown' ? '📝' : 
                         file.type === 'javascript' ? '🟨' :
                         file.type === 'react' ? '⚛️' :
                         file.type === 'python' ? '🐍' :
                         file.type === 'json' ? '📋' : '📄'}
                      </span>
                    </div>
                    <div className="file-details">
                      <div className="file-name">{file.name}</div>
                      <div className="file-meta">
                        <span className="file-size">{file.size}</span>
                        <span className="file-time">{file.deployTime}</span>
                      </div>
                    </div>
                    <div className="file-status-badge">
                      <span className="status-dot deployed"></span>
                      <span className="status-text">已部署</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {!recentFilesExpanded && (
              <div className="recent-deploy-summary">
                <div className="summary-text">
                  {recentReleaseFiles.length} 个已部署文件
                </div>
                <div className="summary-hint">点击展开查看详细列表</div>
              </div>
            )}
          </div>

          {/* 六大工作流Dashboard - 在左侧面板底部 */}
          <div className="panel-section">
            <div 
              className="panel-title-clickable" 
              onClick={() => setWorkflowsExpanded(!workflowsExpanded)}
            >
              <h3 className="panel-title">六大工作流Dashboard</h3>
              <span className={`expand-icon ${workflowsExpanded ? 'expanded' : ''}`}>
                {workflowsExpanded ? '▼' : '▶'}
              </span>
            </div>
          </div>

          {/* 六大工作流卡片 - 可展开/收起 */}
          {workflowsExpanded && (
            <div className="workflows-container">
              {sixWorkflows.map((workflow, index) => (
                <div key={workflow.id} className={`workflow-card ${workflow.color}`}>
                  <div className="workflow-header">
                    <span className="workflow-icon">{workflow.icon}</span>
                    <span className="workflow-title">{workflow.name}</span>
                    <span className="workflow-status">{workflow.status}</span>
                  </div>
                  <div className="workflow-stats">
                    <div className="stat-row">
                      <span className="stat-label">进度</span>
                      <span className="stat-value">{workflow.progress}%</span>
                    </div>
                    <div className="stat-row">
                      <span className="stat-label">质量</span>
                      <span className="stat-value">{workflow.quality}</span>
                    </div>
                    <div className="workflow-components">
                      <span className="components-label">组件:</span>
                      <div className="components-list">
                        {workflow.components.map((comp, i) => (
                          <span key={i} className="component-tag">{comp}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 工作流摘要 - 收起时显示 */}
          {!workflowsExpanded && (
            <div className="workflows-summary">
              <div className="summary-stats">
                <div className="summary-item">
                  <span className="summary-label">总进度</span>
                  <span className="summary-value">
                    {Math.round(sixWorkflows.reduce((acc, w) => acc + w.progress, 0) / sixWorkflows.length)}%
                  </span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">运行中</span>
                  <span className="summary-value">
                    {sixWorkflows.filter(w => w.status === '运行中').length}/{sixWorkflows.length}
                  </span>
                </div>
              </div>
              <div className="summary-hint">点击展开查看详细信息</div>
            </div>
          )}
        </aside>

        {/* 中间主工作区域 - 根据模式显示不同内容 */}
        {currentMode !== 'chat' && (
          <section className="center-panel">
            {currentMode === 'edit' && (
              <div className="edit-mode-content">
                {selectedFile ? (
                  <div className="file-editor">
                    <div className="file-editor-header">
                      <div className="file-info">
                        <span className={`file-type-icon ${selectedFile.type}`}>
                          {selectedFile.type === 'markdown' ? '📝' : 
                           selectedFile.type === 'javascript' ? '🟨' :
                           selectedFile.type === 'react' ? '⚛️' :
                           selectedFile.type === 'python' ? '🐍' :
                           selectedFile.type === 'json' ? '📋' : '📄'}
                        </span>
                        <span className="file-name">{selectedFile.name}</span>
                        <span className="file-size">({selectedFile.size})</span>
                      </div>
                      <div className="file-actions">
                        <button className="action-btn">保存</button>
                        <button className="action-btn secondary">关闭</button>
                      </div>
                    </div>
                    <div className="file-content-editor">
                      <pre className="code-content">
                        {selectedFile.content}
                      </pre>
                    </div>
                  </div>
                ) : (
                  <div className="no-file-selected">
                    <h3>📝 编辑模式</h3>
                    <p>请从左侧"最近部署文件"中选择一个文件进行编辑</p>
                    <div className="editor-placeholder">
                      <div className="placeholder-icon">📄</div>
                      <div className="placeholder-text">选择文件后将在此处显示内容</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {currentMode === 'demo' && (
              <div className="demo-mode-content">
                <h3>🎯 演示模式</h3>
                <p>演示和预览功能将在这里显示</p>
                <div className="demo-placeholder">
                  <div className="placeholder-icon">🎯</div>
                  <div className="placeholder-text">演示内容将在此处显示</div>
                </div>
              </div>
            )}
          </section>
        )}

        {/* AI对话区域 - 根据模式调整位置和大小 */}
        <section className={`ai-chat-panel ${currentMode === 'chat' ? 'expanded' : 'normal'}`}>
          <div className="ai-chat-section">
            <div className="chat-header">
              <h4>🤖 AI助手对话区</h4>
              <span className="chat-status">智能协作中</span>
            </div>
            
            <div className="chat-messages">
              {chatHistory.map((msg, index) => (
                <div key={index} className={`message ${msg.type}-message`}>
                  <div className="message-avatar">
                    {msg.type === 'ai' ? 'AI' : 'U'}
                  </div>
                  <div className="message-bubble">
                    {msg.type === 'ai' && msg.message.startsWith('✅') && (
                      <span className="ai-check">✅ 完全理解！</span>
                    )}
                    <p>{msg.message.replace('✅ 完全理解！', '')}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* 输入区域 */}
            <div className="chat-input-area">
              <div className="input-container">
                <div className="multimodal-upload">
                  <input 
                    type="file" 
                    id="multimodal-upload" 
                    multiple 
                    accept="image/*,video/*,audio/*,text/*,.pdf,.doc,.docx"
                    className="multimodal-input" 
                  />
                  <label htmlFor="multimodal-upload" className="upload-arrow" title="上传多模态文件">
                    ↗️
                  </label>
                </div>
                <input 
                  type="text" 
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="描述您的开发需求，AI将智能介入协助..."
                  className="chat-input"
                />
                <div className="input-actions">
                  <button className="send-btn" onClick={handleSendMessage}>📤</button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default SmartUILayout;

