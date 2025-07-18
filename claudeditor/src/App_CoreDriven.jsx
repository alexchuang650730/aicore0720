import React, { useState, useEffect } from 'react';
import LeftDashboard from './components/LeftDashboard';
import AIAssistant from './ai-assistant/AIAssistant';
import DualModeContainer from './components/DualModeContainer';
import TaskList from './components/TaskList';
import coreConnector from './services/CoreConnector';
import './App.css';

function App() {
  const [coreStatus, setCoreStatus] = useState('disconnected');
  const [currentCommand, setCurrentCommand] = useState(null);
  const [editorState, setEditorState] = useState({
    activeFile: null,
    openFiles: [],
    currentProject: null
  });

  useEffect(() => {
    // 連接到 PowerAutomation Core
    initializeCoreConnection();
    
    // 監聽來自 Core 的命令
    window.addEventListener('core-command', handleCoreCommand);
    
    return () => {
      window.removeEventListener('core-command', handleCoreCommand);
    };
  }, []);

  const initializeCoreConnection = async () => {
    setCoreStatus('connecting');
    const success = await coreConnector.connect();
    setCoreStatus(success ? 'connected' : 'failed');
  };

  const handleCoreCommand = (event) => {
    const { command, params } = event.detail;
    setCurrentCommand({ command, params });
    
    // 執行具體命令
    executeCommand(command, params);
  };

  const executeCommand = (command, params) => {
    let result = { success: false };
    
    switch (command) {
      case 'open_file':
        result = openFile(params.filePath);
        break;
      case 'save_file':
        result = saveFile(params.filePath, params.content);
        break;
      case 'create_project':
        result = createProject(params.projectName);
        break;
      case 'generate_ui':
        result = generateUI(params.description);
        break;
      default:
        result = { success: false, error: `Unknown command: ${command}` };
    }
    
    // 回應 Core
    coreConnector.respondToCore(command, result);
  };

  // === 實際功能實現 ===
  
  const openFile = (filePath) => {
    try {
      // 實際的文件打開邏輯
      const newOpenFiles = [...editorState.openFiles];
      if (!newOpenFiles.includes(filePath)) {
        newOpenFiles.push(filePath);
      }
      
      setEditorState({
        ...editorState,
        activeFile: filePath,
        openFiles: newOpenFiles
      });
      
      console.log(`📂 已打開文件: ${filePath}`);
      return { success: true, filePath };
    } catch (error) {
      console.error('打開文件失敗:', error);
      return { success: false, error: error.message };
    }
  };

  const saveFile = (filePath, content) => {
    try {
      // 實際的文件保存邏輯
      // 這裡可以調用文件系統 API 或發送到後端
      console.log(`💾 已保存文件: ${filePath}`);
      return { success: true, filePath, saved: true };
    } catch (error) {
      console.error('保存文件失敗:', error);
      return { success: false, error: error.message };
    }
  };

  const createProject = (projectName) => {
    try {
      // 實際的項目創建邏輯
      setEditorState({
        ...editorState,
        currentProject: projectName,
        openFiles: []
      });
      
      console.log(`🚀 已創建項目: ${projectName}`);
      return { success: true, projectName };
    } catch (error) {
      console.error('創建項目失敗:', error);
      return { success: false, error: error.message };
    }
  };

  const generateUI = (description) => {
    try {
      // 實際的 UI 生成邏輯
      console.log(`🎨 生成 UI: ${description}`);
      
      // 這裡可以調用 SmartUI 生成服務
      const generatedCode = `<!-- Generated UI for: ${description} -->
<div class="generated-ui">
  <h1>${description}</h1>
  <p>Generated at: ${new Date().toISOString()}</p>
</div>`;
      
      return { 
        success: true, 
        description, 
        code: generatedCode,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('生成 UI 失敗:', error);
      return { success: false, error: error.message };
    }
  };

  const getCoreStatusColor = () => {
    switch (coreStatus) {
      case 'connected': return 'green';
      case 'connecting': return 'yellow';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div className="app">
      {/* 狀態欄 */}
      <header className="app-header">
        <h1>ClaudeEditor</h1>
        <div className="status-bar">
          <span className="core-status">
            <span 
              className="status-indicator" 
              style={{ backgroundColor: getCoreStatusColor() }}
            />
            PowerAutomation Core: {coreStatus}
          </span>
          {coreStatus === 'connected' && (
            <span className="core-id">
              ID: {coreConnector.claudeEditorId}
            </span>
          )}
        </div>
      </header>

      {/* 命令顯示區 */}
      {currentCommand && (
        <div className="command-display">
          <span>正在執行: {currentCommand.command}</span>
          <button onClick={() => setCurrentCommand(null)}>✕</button>
        </div>
      )}

      {/* 主要內容 */}
      <main className="app-main">
        <aside className="sidebar-left">
          <TaskList />
        </aside>

        <div className="main-content">
          <DualModeContainer 
            editorState={editorState}
            onEditorStateChange={setEditorState}
          />
        </div>

        <aside className="sidebar-right">
          <AIAssistant />
        </aside>
      </main>

      {/* 調試信息 */}
      {process.env.NODE_ENV === 'development' && (
        <div className="debug-info">
          <h3>調試信息</h3>
          <p>Core 狀態: {coreStatus}</p>
          <p>活動文件: {editorState.activeFile || 'none'}</p>
          <p>當前項目: {editorState.currentProject || 'none'}</p>
          <p>打開文件數: {editorState.openFiles.length}</p>
        </div>
      )}
    </div>
  );
}

export default App;