import React, { useState, useEffect } from 'react';
import terminalService from '../services/TerminalService';
import claudeCodeSync from '../services/ClaudeCodeSync';
import SystemStatusPanel from './SystemStatusPanel';
import './DualModeContainer.css';

// 模式枚举
const ViewMode = {
  WELCOME: 'welcome',
  EDIT: 'edit',
  SHOWCASE: 'showcase'
};

// 欢迎界面组件
const WelcomeMode = ({ onModeSwitch, systemStats }) => (
  <div className="welcome-mode smartui-container">
    <div className="hero-section">
      <div className="hero-content">
        <h1 className="hero-title">
          🚀 PowerAutomation ClaudeEditor v4.6.9.6
        </h1>
        <p className="hero-subtitle">
          Claude Code 的强大 UI 辅助 | 三模智能开发版
        </p>
        <div className="hero-actions">
          <button 
            className="btn btn-primary"
            onClick={() => onModeSwitch(ViewMode.EDIT)}
          >
            📝 开始编辑
          </button>
          <button 
            className="btn btn-secondary"
            onClick={() => onModeSwitch(ViewMode.SHOWCASE)}
          >
            🎭 演示模式
          </button>
        </div>
      </div>
    </div>
    
    <div className="feature-grid">
      <div className="feature-card">
        <div className="feature-icon">🚀</div>
        <h3>Claude Code 深度集成</h3>
        <p>支持所有 Claude Code 指令，双向无缝沟通</p>
        <div className="feature-status">
          状态: {systemStats.claudeCodeConnected ? '🟢 已连接' : '🔴 未连接'}
        </div>
      </div>
      <div className="feature-card">
        <div className="feature-icon">💻</div>
        <h3>跨平台终端支持</h3>
        <p>Mac/Windows WSL/Linux 终端命令执行</p>
        <div className="feature-status">
          执行: {systemStats.terminalCommands} 个命令
        </div>
      </div>
      <div className="feature-card">
        <div className="feature-icon">🌙</div>
        <h3>K2 高性价比模型</h3>
        <p>月之暗面 1T 参数，节省 60% 成本</p>
        <div className="feature-status">
          今日节省: ¥128.50
        </div>
      </div>
      <div className="feature-card">
        <div className="feature-icon">🎨</div>
        <h3>SmartUI 智能适配</h3>
        <p>基于 AI 的响应式设计，支持所有设备</p>
        <div className="feature-status">
          适配: 5 种设备断点
        </div>
      </div>
      <div className="feature-card">
        <div className="feature-icon">🔄</div>
        <h3>六大工作流支持</h3>
        <p>代码分析、自动修复、测试、构建、优化、检查</p>
        <div className="feature-status">
          节点: 6+ 个可扩展
        </div>
      </div>
      <div className="feature-card">
        <div className="feature-icon">🤝</div>
        <h3>HITL 人机交互</h3>
        <p>人工确认模式，智能决策辅助</p>
        <div className="feature-status">
          模式: 智能 + 人工
        </div>
      </div>
    </div>
    
    {/* 系统状态面板 */}
    <SystemStatusPanel />
    
    <div className="quick-start-section">
      <h2>🚀 快速开始</h2>
      <div className="quick-start-grid">
        <div className="quick-start-item" onClick={() => onModeSwitch(ViewMode.EDIT)}>
          <div className="quick-icon">📝</div>
          <div className="quick-title">新建项目</div>
          <div className="quick-desc">创建新的代码项目</div>
        </div>
        <div className="quick-start-item" onClick={() => claudeCodeSync.executeClaudeCodeCommand('/git', ['status'])}>
          <div className="quick-icon">📊</div>
          <div className="quick-title">检查仓库</div>
          <div className="quick-desc">查看 Git 仓库状态</div>
        </div>
        <div className="quick-start-item" onClick={() => terminalService.executeCommand('pwd && ls -la')}>
          <div className="quick-icon">💻</div>
          <div className="quick-title">终端操作</div>
          <div className="quick-desc">执行终端命令</div>
        </div>
        <div className="quick-start-item" onClick={() => onModeSwitch(ViewMode.SHOWCASE)}>
          <div className="quick-icon">🎭</div>
          <div className="quick-title">预览演示</div>
          <div className="quick-desc">查看项目演示</div>
        </div>
      </div>
    </div>
  </div>
);

// 编辑模式组件
const EditMode = ({ onModeSwitch, systemStats }) => {
  const [currentFile, setCurrentFile] = useState('untitled.js');
  const [isFileModified, setIsFileModified] = useState(false);
  
  const handleSave = () => {
    claudeCodeSync.sendFileChange(currentFile, 'modified', '// 文件内容已保存');
    setIsFileModified(false);
  };
  
  const handleRun = () => {
    claudeCodeSync.executeClaudeCodeCommand('/run', [currentFile]);
  };
  
  const handleFormat = () => {
    claudeCodeSync.executeClaudeCodeCommand('/format', [currentFile]);
  };
  
  return (
    <div className="edit-mode smartui-container">
      <div className="editor-toolbar">
        <div className="toolbar-left">
          <span className="mode-indicator">📝 编辑模式</span>
          <span className="file-indicator">
            {currentFile} {isFileModified && '*'}
          </span>
          <div className="connection-status">
            {systemStats.claudeCodeConnected ? '🟢 Claude Code' : '🔴 离线模式'}
          </div>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-sm" onClick={handleSave} title="保存 (Ctrl+S)">
            💾 保存
          </button>
          <button className="btn btn-sm" onClick={handleRun} title="运行代码">
            ▶️ 运行
          </button>
          <button className="btn btn-sm" onClick={handleFormat} title="格式化代码">
            🎨 格式化
          </button>
          <button 
            className="btn btn-sm btn-primary" 
            onClick={() => onModeSwitch(ViewMode.SHOWCASE)}
            title="预览结果"
          >
            👁️ 预览
          </button>
        </div>
      </div>
      
      <div className="editor-content">
        <div className="editor-sidebar">
          <div className="sidebar-section">
            <h4>📁 文件浏览器</h4>
            <div className="file-tree">
              <div className="file-item active" onClick={() => setCurrentFile('index.js')}>
                📄 index.js
              </div>
              <div className="file-item" onClick={() => setCurrentFile('package.json')}>
                📦 package.json
              </div>
              <div className="file-item" onClick={() => setCurrentFile('README.md')}>
                📖 README.md
              </div>
            </div>
          </div>
          
          <div className="sidebar-section">
            <h4>🔧 Claude Code 工具</h4>
            <div className="tool-buttons">
              <button 
                className="tool-btn"
                onClick={() => claudeCodeSync.executeClaudeCodeCommand('/analyze', [currentFile])}
              >
                🔍 代码分析
              </button>
              <button 
                className="tool-btn"
                onClick={() => claudeCodeSync.executeClaudeCodeCommand('/fix', ['auto'])}
              >
                🔧 自动修复
              </button>
              <button 
                className="tool-btn"
                onClick={() => claudeCodeSync.executeClaudeCodeCommand('/test', [])}
              >
                🧪 运行测试
              </button>
              <button 
                className="tool-btn"
                onClick={() => claudeCodeSync.executeClaudeCodeCommand('/docs', [])}
              >
                📚 生成文档
              </button>
            </div>
          </div>
        </div>
        
        <div className="monaco-editor-container">
          <div className="monaco-placeholder">
            <div className="placeholder-content">
              <div className="placeholder-icon">📝</div>
              <h3>Monaco Editor</h3>
              <p>VS Code 同款编辑器，支持语法高亮和 LSP</p>
              <div className="placeholder-features">
                <span className="feature-tag">✨ 智能提示</span>
                <span className="feature-tag">🎨 语法高亮</span>
                <span className="feature-tag">📁 代码折叠</span>
                <span className="feature-tag">🔍 代码搜索</span>
                <span className="feature-tag">🚀 Claude Code 集成</span>
              </div>
              <div className="editor-stats">
                <div className="stat-item">
                  <span className="stat-label">当前文件:</span>
                  <span className="stat-value">{currentFile}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">连接状态:</span>
                  <span className="stat-value">
                    {systemStats.claudeCodeConnected ? '🟢 已连接' : '🔴 未连接'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// 演示模式组件
const ShowcaseMode = ({ onModeSwitch, systemStats }) => {
  const [previewMode, setPreviewMode] = useState('desktop');
  const [isLivePreview, setIsLivePreview] = useState(true);
  
  const handleRefresh = () => {
    claudeCodeSync.executeClaudeCodeCommand('/build', []);
  };
  
  const handleDeploy = () => {
    claudeCodeSync.executeClaudeCodeCommand('/deploy', []);
  };
  
  return (
    <div className="showcase-mode smartui-container">
      <div className="showcase-toolbar">
        <div className="toolbar-left">
          <span className="mode-indicator">🎭 演示模式</span>
          <div className="preview-mode-selector">
            <button 
              className={`mode-btn ${previewMode === 'mobile' ? 'active' : ''}`}
              onClick={() => setPreviewMode('mobile')}
              title="移动端预览"
            >
              📱
            </button>
            <button 
              className={`mode-btn ${previewMode === 'tablet' ? 'active' : ''}`}
              onClick={() => setPreviewMode('tablet')}
              title="平板预览"
            >
              📟
            </button>
            <button 
              className={`mode-btn ${previewMode === 'desktop' ? 'active' : ''}`}
              onClick={() => setPreviewMode('desktop')}
              title="桌面端预览"
            >
              💻
            </button>
          </div>
          <div className="live-preview-toggle">
            <label>
              <input 
                type="checkbox" 
                checked={isLivePreview}
                onChange={(e) => setIsLivePreview(e.target.checked)}
              />
              🔄 实时预览
            </label>
          </div>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-sm" onClick={handleRefresh} title="刷新预览">
            🔄 刷新
          </button>
          <button className="btn btn-sm" onClick={handleDeploy} title="部署项目">
            🚀 部署
          </button>
          <button 
            className="btn btn-sm btn-primary" 
            onClick={() => onModeSwitch(ViewMode.EDIT)}
            title="返回编辑"
          >
            📝 编辑
          </button>
        </div>
      </div>
      
      <div className="showcase-content">
        <div className="preview-container">
          <div className={`preview-frame ${previewMode}`}>
            <div className="preview-placeholder">
              <div className="placeholder-content">
                <div className="placeholder-icon">🎭</div>
                <h3>预览区域</h3>
                <p>在这里展示您的创作成果</p>
                <div className="preview-features">
                  <span className="feature-tag">📱 响应式预览</span>
                  <span className="feature-tag">🔄 实时刷新</span>
                  <span className="feature-tag">🎨 多设备适配</span>
                  <span className="feature-tag">🚀 一键部署</span>
                </div>
                <div className="preview-stats">
                  <div className="stat-item">
                    <span className="stat-label">预览模式:</span>
                    <span className="stat-value">{previewMode}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">实时预览:</span>
                    <span className="stat-value">{isLivePreview ? '🟢 开启' : '🔴 关闭'}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Claude Code:</span>
                    <span className="stat-value">
                      {systemStats.claudeCodeConnected ? '🟢 已连接' : '🔴 未连接'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="showcase-sidebar">
          <div className="sidebar-section">
            <h4>🎯 预览控制</h4>
            <div className="control-buttons">
              <button 
                className="control-btn"
                onClick={() => claudeCodeSync.executeClaudeCodeCommand('/run', [])}
              >
                ▶️ 运行项目
              </button>
              <button 
                className="control-btn"
                onClick={() => claudeCodeSync.executeClaudeCodeCommand('/test', [])}
              >
                🧪 运行测试
              </button>
              <button 
                className="control-btn"
                onClick={() => claudeCodeSync.executeClaudeCodeCommand('/build', [])}
              >
                🔨 构建项目
              </button>
              <button 
                className="control-btn"
                onClick={() => claudeCodeSync.executeClaudeCodeCommand('/analyze', [])}
              >
                📊 性能分析
              </button>
            </div>
          </div>
          
          <div className="sidebar-section">
            <h4>📱 设备适配</h4>
            <div className="device-list">
              <div className="device-item">
                <span className="device-name">iPhone 14</span>
                <span className="device-size">390×844</span>
              </div>
              <div className="device-item">
                <span className="device-name">iPad Pro</span>
                <span className="device-size">1024×1366</span>
              </div>
              <div className="device-item">
                <span className="device-name">MacBook Pro</span>
                <span className="device-size">1440×900</span>
              </div>
            </div>
          </div>
          
          <div className="sidebar-section">
            <h4>🚀 部署选项</h4>
            <div className="deploy-options">
              <button className="deploy-btn">
                🌐 Vercel 部署
              </button>
              <button className="deploy-btn">
                ☁️ Netlify 部署
              </button>
              <button className="deploy-btn">
                🐙 GitHub Pages
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// 主三模式容器组件
const TriModeContainer = () => {
  const [currentMode, setCurrentMode] = useState(ViewMode.WELCOME);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [systemStats, setSystemStats] = useState({
    claudeCodeConnected: false,
    terminalCommands: 0,
    costSaved: 128.50
  });

  // 监听系统状态变化
  useEffect(() => {
    const updateSystemStats = () => {
      const claudeCodeStatus = claudeCodeSync.getConnectionStatus();
      const terminalStats = terminalService.getStats();
      
      setSystemStats({
        claudeCodeConnected: claudeCodeStatus.status === 'connected',
        terminalCommands: terminalStats.total,
        costSaved: 128.50 // 模拟K2成本节省
      });
    };

    // 监听服务状态变化
    claudeCodeSync.on('connection_status', updateSystemStats);
    terminalService.on('command_complete', updateSystemStats);
    terminalService.on('command_error', updateSystemStats);

    // 定期更新
    const interval = setInterval(updateSystemStats, 5000);
    updateSystemStats(); // 初始更新

    return () => {
      claudeCodeSync.off('connection_status', updateSystemStats);
      terminalService.off('command_complete', updateSystemStats);
      terminalService.off('command_error', updateSystemStats);
      clearInterval(interval);
    };
  }, []);

  // 模式切换处理
  const handleModeSwitch = async (newMode) => {
    if (newMode === currentMode || isTransitioning) return;

    setIsTransitioning(true);
    
    // AG-UI 指导的平滑过渡
    await new Promise(resolve => setTimeout(resolve, 150));
    setCurrentMode(newMode);
    await new Promise(resolve => setTimeout(resolve, 150));
    
    setIsTransitioning(false);
    
    // 通知 SmartUI 系统模式变更
    if (window.smartUIService) {
      window.smartUIService.notifyModeChange(newMode);
    }
    
    // 通知 Claude Code 模式变更
    claudeCodeSync.sendMessage({
      type: 'mode_change',
      data: { mode: newMode, timestamp: new Date().toISOString() }
    });
    
    console.log(`🎯 三模系统切换: ${newMode}`);
  };

  // 键盘快捷键支持
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case '1':
            e.preventDefault();
            handleModeSwitch(ViewMode.WELCOME);
            break;
          case '2':
            e.preventDefault();
            handleModeSwitch(ViewMode.EDIT);
            break;
          case '3':
            e.preventDefault();
            handleModeSwitch(ViewMode.SHOWCASE);
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  // 渲染当前模式
  const renderCurrentMode = () => {
    const modeProps = { 
      onModeSwitch: handleModeSwitch,
      systemStats: systemStats
    };
    
    switch (currentMode) {
      case ViewMode.WELCOME:
        return <WelcomeMode {...modeProps} />;
      case ViewMode.EDIT:
        return <EditMode {...modeProps} />;
      case ViewMode.SHOWCASE:
        return <ShowcaseMode {...modeProps} />;
      default:
        return <WelcomeMode {...modeProps} />;
    }
  };

  return (
    <div className={`tri-mode-container ${currentMode}-active ${isTransitioning ? 'transitioning' : ''}`}>
      {renderCurrentMode()}
      
      {/* 模式指示器 */}
      <div className="mode-indicator-bottom">
        <div className="mode-tabs">
          <button 
            className={`mode-tab ${currentMode === ViewMode.WELCOME ? 'active' : ''}`}
            onClick={() => handleModeSwitch(ViewMode.WELCOME)}
            title="欢迎模式 (Ctrl+1)"
          >
            🏠 欢迎
          </button>
          <button 
            className={`mode-tab ${currentMode === ViewMode.EDIT ? 'active' : ''}`}
            onClick={() => handleModeSwitch(ViewMode.EDIT)}
            title="编辑模式 (Ctrl+2)"
          >
            📝 编辑
          </button>
          <button 
            className={`mode-tab ${currentMode === ViewMode.SHOWCASE ? 'active' : ''}`}
            onClick={() => handleModeSwitch(ViewMode.SHOWCASE)}
            title="演示模式 (Ctrl+3)"
          >
            🎭 演示
          </button>
        </div>
        
        {/* 系统状态指示器 */}
        <div className="system-status-indicator">
          <div className="status-item" title="Claude Code 连接状态">
            {systemStats.claudeCodeConnected ? '🟢' : '🔴'}
          </div>
          <div className="status-item" title={`终端命令: ${systemStats.terminalCommands}`}>
            💻 {systemStats.terminalCommands}
          </div>
          <div className="status-item" title={`今日节省: ¥${systemStats.costSaved}`}>
            💰 ¥{systemStats.costSaved}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TriModeContainer;

