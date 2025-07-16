import React, { useState, useEffect } from 'react';
import './LeftDashboard.css';

const LeftDashboard = () => {
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

  const [workflowNodes, setWorkflowNodes] = useState([
    { id: 1, name: '📝 代码分析', status: 'completed' },
    { id: 2, name: '🔧 自动修复', status: 'in-progress' },
    { id: 3, name: '🧪 单元测试', status: 'pending' },
    { id: 4, name: '📦 构建部署', status: 'pending' },
    { id: 5, name: '🚀 性能优化', status: 'pending' },
    { id: 6, name: '📊 质量检查', status: 'pending' }
  ]);

  const [currentSystem, setCurrentSystem] = useState('mac'); // mac, windows, linux

  const quickCommands = {
    claude: [
      { cmd: '/edit', desc: '编辑文件', icon: '📝' },
      { cmd: '/search', desc: '搜索代码', icon: '🔍' },
      { cmd: '/run', desc: '执行代码', icon: '⚡' },
      { cmd: '/create', desc: '创建项目', icon: '📦' },
      { cmd: '/fix', desc: '修复问题', icon: '🔧' },
      { cmd: '/analyze', desc: '代码分析', icon: '📊' },
      { cmd: '/test', desc: '运行测试', icon: '🧪' },
      { cmd: '/docs', desc: '生成文档', icon: '📚' }
    ],
    mcp: [
      { cmd: '智能路由', desc: 'K2/Claude', icon: '🎯' },
      { cmd: 'MCP工具管理', desc: '工具管理', icon: '🔧' },
      { cmd: '快速命令执行', desc: '命令执行', icon: '⚡' },
      { cmd: '同步MCP状态', desc: '状态同步', icon: '🔄' }
    ]
  };

  const projectActions = [
    { label: '🔗 Git Clone 仓库', action: 'git-clone' },
    { label: '📂 打开本地目录', action: 'open-local' },
    { label: '🌐 连接远程主机', action: 'connect-remote' },
    { label: '📊 获取仓库信息', action: 'repo-info' }
  ];

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

  const executeQuickCommand = (cmd) => {
    console.log(`执行快速命令: ${cmd}`);
    // 这里会与 Claude Code 同步
  };

  const executeProjectAction = (action) => {
    console.log(`执行项目操作: ${action}`);
  };

  return (
    <div className="left-dashboard">
      {/* 快速操作区 */}
      <div className="dashboard-section quick-actions">
        <h3>🚀 快速操作区</h3>
        
        {/* 项目管理 */}
        <div className="subsection">
          <h4>📁 项目管理</h4>
          <div className="action-buttons">
            {projectActions.map((action, index) => (
              <button
                key={index}
                className="action-btn"
                onClick={() => executeProjectAction(action.action)}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>

        {/* 终端命令支持 */}
        <div className="subsection">
          <h4>💻 终端命令支持</h4>
          <div className="terminal-support">
            <div className="system-indicator">
              <span className="system-icon">{getSystemIcon()}</span>
              <span className="system-name">
                {currentSystem === 'mac' && 'Mac 终端执行'}
                {currentSystem === 'windows' && 'Windows WSL 支持'}
                {currentSystem === 'linux' && 'Linux 终端'}
              </span>
            </div>
          </div>
        </div>

        {/* 智能快速指令集 */}
        <div className="subsection">
          <h4>🚀 智能快速指令集</h4>
          <div className="command-tabs">
            <div className="tab-header">
              <button className="tab-btn active">📝 Claude Code</button>
              <button className="tab-btn">🎯 Command MCP</button>
            </div>
            <div className="command-grid">
              {quickCommands.claude.map((cmd, index) => (
                <button
                  key={index}
                  className="command-btn"
                  onClick={() => executeQuickCommand(cmd.cmd)}
                  title={cmd.desc}
                >
                  <span className="cmd-icon">{cmd.icon}</span>
                  <span className="cmd-text">{cmd.cmd}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 系统终端 */}
        <div className="subsection">
          <h4>💻 系统终端</h4>
          <div className="terminal-input">
            <input
              type="text"
              placeholder="输入命令..."
              className="terminal-field"
            />
            <button className="execute-btn">执行</button>
          </div>
          <div className="terminal-suggestions">
            <span className="suggestion">git status</span>
            <span className="suggestion">npm install</span>
            <span className="suggestion">docker ps</span>
          </div>
        </div>

        {/* HITL 人机交互 */}
        <div className="subsection">
          <h4>🤝 HITL 人机交互</h4>
          <div className="hitl-controls">
            <button className="hitl-btn">✋ 人工确认模式</button>
            <button className="hitl-btn">🎛️ 交互控制面板</button>
            <button className="hitl-btn">📋 待确认任务列表</button>
            <button className="hitl-btn">⚙️ HITL 设置</button>
          </div>
        </div>
      </div>

      {/* 系统状态监控 */}
      <div className="dashboard-section system-status">
        <h3>📈 系统状态</h3>
        <div className="status-items">
          <div className="status-item">
            <span className="status-icon">{getStatusIcon(systemStats.mcpCoordinator)}</span>
            <span className="status-label">MCP协调器</span>
            <span className="status-value">运行中</span>
          </div>
          <div className="status-item">
            <span className="status-icon">{getStatusIcon(systemStats.feishuIntegration)}</span>
            <span className="status-label">飞书集成</span>
            <span className="status-value">已连接</span>
          </div>
          <div className="status-item">
            <span className="status-icon">{getStatusIcon(systemStats.githubSync)}</span>
            <span className="status-label">GitHub同步</span>
            <span className="status-value">同步中</span>
          </div>
        </div>

        {/* 成本节省统计 */}
        <div className="cost-savings">
          <h4>💰 成本节省统计</h4>
          <div className="savings-stats">
            <div className="savings-item">
              <span className="savings-label">K2 模型:</span>
              <span className="savings-value">节省 {systemStats.costSavings.percentage}%</span>
            </div>
            <div className="savings-item">
              <span className="savings-label">今日节省:</span>
              <span className="savings-value">¥{systemStats.costSavings.today}</span>
            </div>
            <div className="savings-item">
              <span className="savings-label">本月节省:</span>
              <span className="savings-value">¥{systemStats.costSavings.month}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 工作流仪表盘 */}
      <div className="dashboard-section workflow-dashboard">
        <h3>🔄 工作流状态 (6+ 节点)</h3>
        <div className="workflow-nodes">
          {workflowNodes.map((node) => (
            <div key={node.id} className={`workflow-node ${node.status}`}>
              <span className="node-number">{node.id}.</span>
              <span className="node-name">{node.name}</span>
              <span className="node-status">
                {node.status === 'completed' && '✅ 完成'}
                {node.status === 'in-progress' && '🔄 进行中'}
                {node.status === 'pending' && '⏳ 等待'}
              </span>
            </div>
          ))}
          <div className="workflow-node expandable">
            <span className="node-expand">+ 更多节点...</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeftDashboard;

