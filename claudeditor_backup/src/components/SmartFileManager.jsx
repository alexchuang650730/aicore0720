import React, { useState, useEffect, useCallback } from 'react';
import './SmartFileManager.css';

/**
 * SmartFileManager - 基于 AI-UI 的智能文件管理组件
 * 集成 PowerAutomation MCP 架构，支持 SmartUI 响应式设计
 */
const SmartFileManager = ({ onFileSelect, onFileEdit, className = '' }) => {
  // 文件管理状态
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('list'); // list, grid, tree
  const [sortBy, setSortBy] = useState('name'); // name, date, size, type
  
  // SmartUI 响应式状态
  const [smartUIConfig, setSmartUIConfig] = useState({
    deviceType: 'desktop',
    breakpoint: 'lg',
    isCompact: false
  });
  
  // MCP 集成状态
  const [mcpStatus, setMcpStatus] = useState({
    connected: false,
    commandMcp: false,
    routerMcp: false
  });

  // 模拟文件数据 (实际应从 MCP 获取)
  const mockFiles = [
    {
      id: 1,
      name: 'README.md',
      type: 'file',
      size: '2.1 KB',
      modified: '2025-01-16 10:30',
      path: '/README.md',
      icon: '📖',
      language: 'markdown'
    },
    {
      id: 2,
      name: 'package.json',
      type: 'file',
      size: '1.5 KB',
      modified: '2025-01-16 09:15',
      path: '/package.json',
      icon: '📦',
      language: 'json'
    },
    {
      id: 3,
      name: 'src',
      type: 'directory',
      size: '12 items',
      modified: '2025-01-16 11:45',
      path: '/src',
      icon: '📁',
      children: [
        {
          id: 31,
          name: 'App.jsx',
          type: 'file',
          size: '3.2 KB',
          modified: '2025-01-16 11:45',
          path: '/src/App.jsx',
          icon: '⚛️',
          language: 'javascript'
        },
        {
          id: 32,
          name: 'index.js',
          type: 'file',
          size: '0.8 KB',
          modified: '2025-01-16 10:20',
          path: '/src/index.js',
          icon: '📄',
          language: 'javascript'
        }
      ]
    },
    {
      id: 4,
      name: 'components',
      type: 'directory',
      size: '8 items',
      modified: '2025-01-16 12:00',
      path: '/components',
      icon: '📁',
      children: []
    },
    {
      id: 5,
      name: '.gitignore',
      type: 'file',
      size: '0.3 KB',
      modified: '2025-01-15 16:30',
      path: '/.gitignore',
      icon: '🙈',
      language: 'text'
    }
  ];

  // 初始化 SmartUI 配置
  useEffect(() => {
    const updateSmartUIConfig = () => {
      if (window.smartUIService) {
        const config = window.smartUIService.getCurrentConfig();
        setSmartUIConfig({
          deviceType: config.deviceType,
          breakpoint: config.breakpoint,
          isCompact: config.breakpoint === 'xs' || config.breakpoint === 'sm'
        });
      }
    };

    updateSmartUIConfig();
    
    // 监听 SmartUI 变化
    if (window.smartUIService) {
      window.smartUIService.onDeviceChange(updateSmartUIConfig);
    }

    return () => {
      if (window.smartUIService) {
        window.smartUIService.offDeviceChange(updateSmartUIConfig);
      }
    };
  }, []);

  // 初始化文件列表
  useEffect(() => {
    loadFiles();
  }, [currentPath]);

  // 加载文件列表 (集成 PowerAutomation MCP)
  const loadFiles = useCallback(async () => {
    setIsLoading(true);
    try {
      // TODO: 集成 PowerAutomation command_mcp 获取真实文件列表
      // const result = await window.powerAutomationMCP?.command_mcp?.listFiles(currentPath);
      
      // 模拟 MCP 调用延迟
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // 使用模拟数据
      setFiles(mockFiles);
      
      // 更新 MCP 状态
      setMcpStatus({
        connected: true,
        commandMcp: true,
        routerMcp: true
      });
      
    } catch (error) {
      console.error('❌ 文件加载失败:', error);
      setFiles([]);
      setMcpStatus(prev => ({ ...prev, connected: false }));
    } finally {
      setIsLoading(false);
    }
  }, [currentPath]);

  // 文件搜索过滤
  const filteredFiles = files.filter(file => 
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 文件排序
  const sortedFiles = [...filteredFiles].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'date':
        return new Date(b.modified) - new Date(a.modified);
      case 'size':
        return a.type === 'directory' ? -1 : b.type === 'directory' ? 1 : 0;
      case 'type':
        return a.type.localeCompare(b.type);
      default:
        return 0;
    }
  });

  // 处理文件选择
  const handleFileSelect = useCallback((file) => {
    setSelectedFile(file);
    
    if (file.type === 'file') {
      // 通知父组件文件被选中
      onFileSelect?.(file);
      
      // 集成 PowerAutomation MCP 读取文件内容
      handleFileEdit(file);
    } else if (file.type === 'directory') {
      // 切换目录
      setCurrentPath(file.path);
    }
  }, [onFileSelect]);

  // 处理文件编辑
  const handleFileEdit = useCallback(async (file) => {
    try {
      // TODO: 集成 PowerAutomation command_mcp 读取文件内容
      // const content = await window.powerAutomationMCP?.command_mcp?.readFile(file.path);
      
      // 模拟文件内容
      const mockContent = `// ${file.name}\n// 文件路径: ${file.path}\n// 修改时间: ${file.modified}\n\n// 这里是文件内容...`;
      
      // 通知父组件编辑文件
      onFileEdit?.({
        ...file,
        content: mockContent
      });
      
      console.log(`📝 编辑文件: ${file.name}`);
      
    } catch (error) {
      console.error('❌ 文件读取失败:', error);
    }
  }, [onFileEdit]);

  // 创建新文件
  const handleCreateFile = useCallback(async () => {
    const fileName = prompt('请输入文件名:');
    if (!fileName) return;

    try {
      // TODO: 集成 PowerAutomation command_mcp 创建文件
      // await window.powerAutomationMCP?.command_mcp?.createFile(currentPath + '/' + fileName);
      
      console.log(`📄 创建文件: ${fileName}`);
      await loadFiles(); // 重新加载文件列表
      
    } catch (error) {
      console.error('❌ 文件创建失败:', error);
    }
  }, [currentPath, loadFiles]);

  // 创建新文件夹
  const handleCreateFolder = useCallback(async () => {
    const folderName = prompt('请输入文件夹名:');
    if (!folderName) return;

    try {
      // TODO: 集成 PowerAutomation command_mcp 创建文件夹
      // await window.powerAutomationMCP?.command_mcp?.createDirectory(currentPath + '/' + folderName);
      
      console.log(`📁 创建文件夹: ${folderName}`);
      await loadFiles(); // 重新加载文件列表
      
    } catch (error) {
      console.error('❌ 文件夹创建失败:', error);
    }
  }, [currentPath, loadFiles]);

  // 刷新文件列表
  const handleRefresh = useCallback(() => {
    loadFiles();
  }, [loadFiles]);

  // 渲染文件项
  const renderFileItem = (file) => {
    const isSelected = selectedFile?.id === file.id;
    const itemClass = `
      smart-file-item 
      ${isSelected ? 'selected' : ''} 
      ${file.type}
      ${smartUIConfig.isCompact ? 'compact' : ''}
    `.trim();

    return (
      <div
        key={file.id}
        className={itemClass}
        onClick={() => handleFileSelect(file)}
        onDoubleClick={() => file.type === 'file' && handleFileEdit(file)}
      >
        <div className="file-icon">
          {file.icon}
        </div>
        <div className="file-info">
          <div className="file-name" title={file.name}>
            {file.name}
          </div>
          {!smartUIConfig.isCompact && (
            <div className="file-meta">
              <span className="file-size">{file.size}</span>
              <span className="file-modified">{file.modified}</span>
            </div>
          )}
        </div>
        {file.type === 'file' && (
          <div className="file-actions">
            <button
              className="action-btn edit"
              onClick={(e) => {
                e.stopPropagation();
                handleFileEdit(file);
              }}
              title="编辑文件"
            >
              📝
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`smart-file-manager smartui-${smartUIConfig.deviceType} smartui-${smartUIConfig.breakpoint} ${className}`}>
      {/* 文件管理器头部 */}
      <div className="file-manager-header">
        <div className="header-title">
          <span className="title-icon">📁</span>
          <span className="title-text">文件管理</span>
          {mcpStatus.connected && (
            <span className="mcp-status" title="PowerAutomation MCP 已连接">
              🟢
            </span>
          )}
        </div>
        
        {!smartUIConfig.isCompact && (
          <div className="header-actions">
            <button
              className="action-btn"
              onClick={handleCreateFile}
              title="新建文件"
            >
              📄
            </button>
            <button
              className="action-btn"
              onClick={handleCreateFolder}
              title="新建文件夹"
            >
              📁
            </button>
            <button
              className="action-btn"
              onClick={handleRefresh}
              title="刷新"
            >
              🔄
            </button>
          </div>
        )}
      </div>

      {/* 搜索和过滤 */}
      <div className="file-manager-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="搜索文件..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>
        
        {!smartUIConfig.isCompact && (
          <div className="view-controls">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              <option value="name">按名称</option>
              <option value="date">按日期</option>
              <option value="size">按大小</option>
              <option value="type">按类型</option>
            </select>
            
            <div className="view-mode-buttons">
              <button
                className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                onClick={() => setViewMode('list')}
                title="列表视图"
              >
                📋
              </button>
              <button
                className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                onClick={() => setViewMode('grid')}
                title="网格视图"
              >
                ⊞
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 当前路径 */}
      <div className="current-path">
        <span className="path-icon">📍</span>
        <span className="path-text">{currentPath}</span>
      </div>

      {/* 文件列表 */}
      <div className={`file-list ${viewMode} ${isLoading ? 'loading' : ''}`}>
        {isLoading ? (
          <div className="loading-indicator">
            <span className="loading-icon">⏳</span>
            <span className="loading-text">加载中...</span>
          </div>
        ) : sortedFiles.length > 0 ? (
          sortedFiles.map(renderFileItem)
        ) : (
          <div className="empty-state">
            <span className="empty-icon">📂</span>
            <span className="empty-text">
              {searchTerm ? '未找到匹配的文件' : '此文件夹为空'}
            </span>
          </div>
        )}
      </div>

      {/* MCP 状态指示器 */}
      {smartUIConfig.deviceType === 'desktop' && (
        <div className="mcp-status-panel">
          <div className="status-title">🚀 PowerAutomation MCP</div>
          <div className="status-items">
            <div className={`status-item ${mcpStatus.connected ? 'connected' : 'disconnected'}`}>
              <span className="status-dot"></span>
              <span className="status-label">连接状态</span>
            </div>
            <div className={`status-item ${mcpStatus.commandMcp ? 'connected' : 'disconnected'}`}>
              <span className="status-dot"></span>
              <span className="status-label">Command MCP</span>
            </div>
            <div className={`status-item ${mcpStatus.routerMcp ? 'connected' : 'disconnected'}`}>
              <span className="status-dot"></span>
              <span className="status-label">Router MCP</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartFileManager;

