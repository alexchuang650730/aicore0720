import React, { useState, useEffect } from 'react';
import LeftDashboard from './components/LeftDashboard';
import AIAssistant from './ai-assistant/AIAssistant';
import DualModeContainer from './components/DualModeContainer';
import TaskList from './components/TaskList';
import SmartUIService from './services/SmartUIService';
import './App.css';
import './styles/SmartUI.css';

function App() {
  const [smartUIConfig, setSmartUIConfig] = useState({
    deviceType: 'desktop',
    breakpoint: 'lg'
  });

  useEffect(() => {
    // 初始化 SmartUI 服务
    const smartUI = new SmartUIService();
    smartUI.initialize();
    
    // 设置全局 SmartUI 服务
    window.smartUIService = smartUI;
    
    // 监听设备变化
    const handleDeviceChange = (config) => {
      setSmartUIConfig(config);
      console.log('🎯 SmartUI 设备更新:', config);
    };
    
    smartUI.onDeviceChange(handleDeviceChange);
    
    // 初始检测
    handleDeviceChange(smartUI.getCurrentConfig());
    
    return () => {
      smartUI.cleanup();
    };
  }, []);

  return (
    <div className={`app smartui-${smartUIConfig.deviceType} smartui-${smartUIConfig.breakpoint}`}>
      {/* SmartUI 标题栏 */}
      <header className="app-header">
        <h1>ClaudeEditor</h1>
        <div className="smartui-indicator">
          <span className="device-info">
            📱 {smartUIConfig.deviceType} | {smartUIConfig.breakpoint}
          </span>
          <span className="version-info">SmartUI v4.6.9.6</span>
        </div>
      </header>

      {/* 主要内容区域 */}
      <main className="app-main">
        {/* 左侧面板 - 任务管理 */}
        <aside className="sidebar-left">
          <TaskList />
        </aside>

        {/* 中间区域 - 三模式容器 */}
        <div className="main-content">
          <DualModeContainer />
        </div>

        {/* 右侧面板 - AI助手 */}
        <aside className="sidebar-right">
          <AIAssistant />
        </aside>
      </main>
    </div>
  );
}

export default App;

