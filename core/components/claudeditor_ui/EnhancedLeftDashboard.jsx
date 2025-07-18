import React, { useState, useEffect } from 'react';
import './LeftDashboard.css';

const EnhancedLeftDashboard = () => {
  const [systemStats, setSystemStats] = useState({
    mcpCoordinator: 'running',
    feishuIntegration: 'connected',
    githubSync: 'syncing',
    costSavings: {
      today: 128.50,
      month: 2456.80,
      percentage: 60
    },
    terminalStats: {
      success: 15,
      failed: 2,
      total: 17,
      avgTime: 1.2
    }
  });

  // 六大工作流狀態
  const [activeWorkflow, setActiveWorkflow] = useState('architecture');
  const [workflowProgress, setWorkflowProgress] = useState(35);
  const [workflowStatus, setWorkflowStatus] = useState('running'); // idle, running, paused, completed

  // 六大工作流配置
  const sixWorkflows = [
    {
      id: 'requirement',
      name: '需求分析',
      icon: '📋',
      description: '分析代碼提取需求',
      mcps: ['CodeFlow', 'Stagewise'],
      status: 'completed',
      progress: 100
    },
    {
      id: 'architecture',
      name: '架構設計',
      icon: '🏗️',
      description: '生成架構和UI設計',
      mcps: ['Zen', 'SmartUI', 'Stagewise'],
      status: 'running',
      progress: 35
    },
    {
      id: 'coding',
      name: '編碼實現',
      icon: '💻',
      description: '智能代碼生成',
      mcps: ['CodeFlow', 'Zen', 'XMasters', 'SmartUI', 'AG-UI'],
      status: 'pending',
      progress: 0
    },
    {
      id: 'testing',
      name: '測試驗證',
      icon: '🧪',
      description: '自動化測試執行',
      mcps: ['Test', 'AG-UI', 'Stagewise'],
      status: 'pending',
      progress: 0
    },
    {
      id: 'deployment',
      name: '部署發布',
      icon: '🚀',
      description: '一鍵部署上線',
      mcps: ['SmartUI', 'Stagewise'],
      status: 'pending',
      progress: 0
    },
    {
      id: 'monitoring',
      name: '監控運維',
      icon: '📊',
      description: '實時監控優化',
      mcps: ['CodeFlow', 'XMasters', 'Stagewise'],
      status: 'pending',
      progress: 0
    }
  ];

  const [currentSystem, setCurrentSystem] = useState('mac'); // mac, windows, linux

  // AI 控制狀態
  const [aiModel, setAiModel] = useState('auto'); // auto, k2, claude
  const [aiControlExpanded, setAiControlExpanded] = useState(true);

  // GitHub 狀態
  const [gitStats, setGitStats] = useState({
    branch: 'main',
    changes: { added: 125, removed: 45, modified: 5 },
    lastSync: '2分鐘前'
  });

  const quickCommands = {
    claude: [
      { cmd: '/edit', desc: '編輯文件', icon: '📝' },
      { cmd: '/search', desc: '搜索代碼', icon: '🔍' },
      { cmd: '/run', desc: '執行代碼', icon: '⚡' },
      { cmd: '/create', desc: '創建項目', icon: '📦' }
    ],
    workflow: [
      { cmd: '/analyze', desc: '分析需求', icon: '📊' },
      { cmd: '/design', desc: '設計架構', icon: '🎨' },
      { cmd: '/test', desc: '運行測試', icon: '🧪' },
      { cmd: '/deploy', desc: '部署應用', icon: '🚀' }
    ]
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
      case 'connected':
      case 'completed':
        return '🟢';
      case 'syncing':
      case 'in-progress':
        return '🟡';
      case 'pending':
      case 'failed':
        return '🔴';
      default:
        return '⚪';
    }
  };

  const getSystemIcon = () => {
    switch (currentSystem) {
      case 'mac': return '🍎';
      case 'windows': return '🪟';
      case 'linux': return '🐧';
      default: return '💻';
    }
  };

  const executeWorkflow = (workflowId) => {
    setActiveWorkflow(workflowId);
    setWorkflowStatus('running');
    // 通知後端啟動工作流
    window.powerautomation?.startWorkflow(workflowId);
  };

  const pauseResumeWorkflow = () => {
    if (workflowStatus === 'running') {
      setWorkflowStatus('paused');
    } else if (workflowStatus === 'paused') {
      setWorkflowStatus('running');
    }
  };

  return (
    <div className="left-dashboard enhanced">
      {/* 1. AI 控制區 */}
      <div className="dashboard-section ai-control">
        <div 
          className="section-header clickable"
          onClick={() => setAiControlExpanded(!aiControlExpanded)}
        >
          <h3>🤖 AI 控制中心</h3>
          <span className="expand-icon">{aiControlExpanded ? '▼' : '▶'}</span>
        </div>
        
        {aiControlExpanded && (
          <div className="section-content">
            {/* 模型選擇 */}
            <div className="ai-model-selector">
              <label>模型路由:</label>
              <div className="model-options">
                <button 
                  className={`model-btn ${aiModel === 'auto' ? 'active' : ''}`}
                  onClick={() => setAiModel('auto')}
                >
                  <span className="model-icon">🎯</span>
                  <span className="model-name">智能路由</span>
                  <span className="model-desc">自動選擇最佳</span>
                </button>
                <button 
                  className={`model-btn ${aiModel === 'k2' ? 'active' : ''}`}
                  onClick={() => setAiModel('k2')}
                >
                  <span className="model-icon">💰</span>
                  <span className="model-name">K2 模型</span>
                  <span className="model-desc">節省 60-80%</span>
                </button>
                <button 
                  className={`model-btn ${aiModel === 'claude' ? 'active' : ''}`}
                  onClick={() => setAiModel('claude')}
                >
                  <span className="model-icon">⚡</span>
                  <span className="model-name">Claude</span>
                  <span className="model-desc">高精度模式</span>
                </button>
              </div>
            </div>

            {/* 成本監控 */}
            <div className="cost-monitor">
              <div className="cost-stats">
                <div className="cost-item">
                  <span className="cost-label">當前成本:</span>
                  <span className="cost-value">¥{systemStats.costSavings.today}</span>
                </div>
                <div className="cost-item">
                  <span className="cost-label">已節省:</span>
                  <span className="cost-value success">¥{systemStats.costSavings.month}</span>
                </div>
              </div>
              <div className="cost-progress">
                <div 
                  className="progress-bar"
                  style={{ width: `${systemStats.costSavings.percentage}%` }}
                />
                <span className="progress-text">{systemStats.costSavings.percentage}% 節省</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 2. GitHub 狀態區 */}
      <div className="dashboard-section github-status">
        <h3>🐙 GitHub 狀態</h3>
        <div className="github-content">
          <div className="git-info">
            <div className="git-branch">
              <span className="branch-icon">🌿</span>
              <span className="branch-name">{gitStats.branch}</span>
              <span className="sync-status">已同步</span>
            </div>
            <div className="git-changes">
              <span className="change-stat add">+{gitStats.changes.added}</span>
              <span className="change-stat remove">-{gitStats.changes.removed}</span>
              <span className="change-stat modify">~{gitStats.changes.modified}</span>
            </div>
          </div>
          <div className="git-actions">
            <button className="git-btn">🔄 拉取</button>
            <button className="git-btn primary">📤 推送</button>
            <button className="git-btn">💾 提交</button>
          </div>
        </div>
      </div>

      {/* 3. 快速操作區 */}
      <div className="dashboard-section quick-actions">
        <h3>⚡ 快速操作</h3>
        <div className="command-tabs">
          <div className="tab-content">
            <div className="command-grid">
              {quickCommands.claude.map((cmd, index) => (
                <button
                  key={index}
                  className="command-btn"
                  title={cmd.desc}
                >
                  <span className="cmd-icon">{cmd.icon}</span>
                  <span className="cmd-text">{cmd.cmd}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
        
        {/* 終端命令 */}
        <div className="terminal-quick">
          <input
            type="text"
            placeholder={`${getSystemIcon()} 輸入命令...`}
            className="terminal-input"
          />
          <div className="terminal-suggestions">
            <span className="suggestion">npm run dev</span>
            <span className="suggestion">git status</span>
            <span className="suggestion">python test.py</span>
          </div>
        </div>
      </div>

      {/* 4. 六大工作流區 - 重點部分 */}
      <div className="dashboard-section six-workflows">
        <h3>🚀 六大工作流</h3>
        
        {/* 當前工作流狀態 */}
        {activeWorkflow && (
          <div className="active-workflow-status">
            <div className="workflow-header">
              <span className="workflow-name">
                {sixWorkflows.find(w => w.id === activeWorkflow)?.icon}
                {sixWorkflows.find(w => w.id === activeWorkflow)?.name}
              </span>
              <button 
                className="workflow-control"
                onClick={pauseResumeWorkflow}
              >
                {workflowStatus === 'running' ? '⏸️' : '▶️'}
              </button>
            </div>
            <div className="workflow-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${workflowProgress}%` }}
                />
              </div>
              <span className="progress-text">{workflowProgress}%</span>
            </div>
            <div className="mcp-indicators">
              {sixWorkflows.find(w => w.id === activeWorkflow)?.mcps.map(mcp => (
                <span key={mcp} className="mcp-badge active">{mcp}</span>
              ))}
            </div>
          </div>
        )}

        {/* 工作流列表 */}
        <div className="workflow-list">
          {sixWorkflows.map((workflow) => (
            <div 
              key={workflow.id}
              className={`workflow-item ${workflow.status} ${activeWorkflow === workflow.id ? 'active' : ''}`}
              onClick={() => executeWorkflow(workflow.id)}
            >
              <div className="workflow-main">
                <span className="workflow-icon">{workflow.icon}</span>
                <div className="workflow-info">
                  <span className="workflow-title">{workflow.name}</span>
                  <span className="workflow-desc">{workflow.description}</span>
                </div>
                <span className="workflow-status-icon">
                  {workflow.status === 'completed' && '✅'}
                  {workflow.status === 'running' && '🔄'}
                  {workflow.status === 'pending' && '⏳'}
                </span>
              </div>
              {workflow.status === 'running' && (
                <div className="workflow-mcps">
                  {workflow.mcps.map(mcp => (
                    <span key={mcp} className="mcp-mini">{mcp}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* 工作流快速啟動 */}
        <div className="workflow-quick-start">
          <button className="start-btn primary">
            🚀 快速開始完整流程
          </button>
          <button className="start-btn">
            📊 查看工作流報告
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnhancedLeftDashboard;