import React, { useState, useEffect, useCallback } from 'react';
import localFileSystemService from '../services/LocalFileSystemService';
import './LocalFileManager.css';

/**
 * LocalFileManager - 本地文件管理组件
 * 集成 PowerAutomation local_adapter_mcp 的文件系统适配器
 */
const LocalFileManager = ({ onFileSelect, onFileEdit, onReleaseDeploy, className = '' }) => {
  // 文件管理状态
  const [connectedFolders, setConnectedFolders] = useState([]);
  const [currentFolder, setCurrentFolder] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name');
  
  // 连接状态
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  // Claude Code 输出
  const [claudeOutputs, setClaudeOutputs] = useState([]);
  const [showClaudeOutputs, setShowClaudeOutputs] = useState(true);
  
  // 文件夹连接对话框
  const [showConnectDialog, setShowConnectDialog] = useState(false);
  const [folderPath, setFolderPath] = useState('');

  // 初始化服务
  useEffect(() => {
    initializeService();
    
    // 注册 Claude Code 输出回调
    const handleClaudeOutput = async (claudeEvent) => {
      console.log('🎯 收到 Claude Code 输出:', claudeEvent);
      
      setClaudeOutputs(prev => [claudeEvent, ...prev.slice(0, 9)]); // 保留最新10个
      
      // 刷新当前文件夹
      if (currentFolder) {
        await refreshCurrentFolder();
      }
    };
    
    localFileSystemService.registerClaudeOutputCallback(handleClaudeOutput);
    
    // 监听文件列表变化
    const handleFileListChanged = (event) => {
      const { folderId, files } = event.detail;
      if (currentFolder && currentFolder.id === folderId) {
        setFiles(files);
      }
    };
    
    window.addEventListener('fileListChanged', handleFileListChanged);
    
    return () => {
      localFileSystemService.unregisterClaudeOutputCallback(handleClaudeOutput);
      window.removeEventListener('fileListChanged', handleFileListChanged);
    };
  }, [currentFolder]);

  const initializeService = async () => {
    try {
      setConnectionStatus('connecting');
      const result = await localFileSystemService.initialize();
      
      if (result.success) {
        setIsConnected(true);
        setConnectionStatus('connected');
        
        // 加载已连接的文件夹
        const folders = localFileSystemService.getConnectedFolders();
        setConnectedFolders(folders);
        
        if (folders.length > 0) {
          setCurrentFolder(folders[0]);
          await loadFolderFiles(folders[0].id);
        }
      } else {
        setConnectionStatus('error');
        console.error('文件系统服务初始化失败:', result.error);
      }
    } catch (error) {
      setConnectionStatus('error');
      console.error('初始化文件系统服务失败:', error);
    }
  };

  const connectLocalFolder = async () => {
    if (!folderPath.trim()) {
      alert('请输入文件夹路径');
      return;
    }
    
    try {
      setIsLoading(true);
      const result = await localFileSystemService.connectLocalFolder(folderPath, true);
      
      if (result.success) {
        const newFolder = {
          id: result.folder_id,
          path: result.path,
          fileCount: result.file_count,
          watchEnabled: result.watch_enabled
        };
        
        setConnectedFolders(prev => [...prev, newFolder]);
        setCurrentFolder(newFolder);
        setFiles(result.files || []);
        setShowConnectDialog(false);
        setFolderPath('');
        
        console.log(`✅ 文件夹连接成功: ${result.path}`);
      } else {
        alert(`连接失败: ${result.error}`);
      }
    } catch (error) {
      console.error('连接文件夹失败:', error);
      alert(`连接失败: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFolderFiles = async (folderId) => {
    try {
      setIsLoading(true);
      const result = await localFileSystemService.getFolderFiles(folderId);
      
      if (result.success) {
        setFiles(result.files);
      } else {
        console.error('加载文件失败:', result.error);
      }
    } catch (error) {
      console.error('加载文件失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshCurrentFolder = async () => {
    if (!currentFolder) return;
    
    try {
      const result = await localFileSystemService.refreshFolder(currentFolder.id);
      if (result.success) {
        setFiles(result.files);
        
        // 更新文件夹信息
        setConnectedFolders(prev => 
          prev.map(folder => 
            folder.id === currentFolder.id 
              ? { ...folder, fileCount: result.file_count }
              : folder
          )
        );
      }
    } catch (error) {
      console.error('刷新文件夹失败:', error);
    }
  };

  const handleFileClick = async (file) => {
    setSelectedFile(file);
    
    if (file.type === 'file') {
      // 通知父组件文件被选中
      onFileSelect?.(file);
      
      // 如果是可编辑文件，读取内容
      if (isEditableFile(file)) {
        await handleFileEdit(file);
      }
    } else if (file.type === 'directory') {
      // 处理目录点击（可以扩展为进入子目录）
      console.log(`📁 点击目录: ${file.name}`);
    }
  };

  const handleFileEdit = async (file) => {
    try {
      setIsLoading(true);
      const result = await localFileSystemService.getFileContent(file.path);
      
      if (result.success) {
        const fileWithContent = {
          ...file,
          content: result.content,
          lines: result.lines,
          language: result.language
        };
        
        // 通知父组件编辑文件
        onFileEdit?.(fileWithContent);
        
        console.log(`📝 编辑文件: ${file.name}`);
      } else {
        alert(`读取文件失败: ${result.error}`);
      }
    } catch (error) {
      console.error('读取文件内容失败:', error);
      alert(`读取文件失败: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReleaseDeploy = async (file) => {
    try {
      console.log(`🚀 部署 Release: ${file.name}`);
      
      // 通知父组件部署 release
      onReleaseDeploy?.({
        ...file,
        deployType: 'release',
        deployPath: file.path
      });
      
    } catch (error) {
      console.error('部署 Release 失败:', error);
      alert(`部署失败: ${error.message}`);
    }
  };

  const handleClaudeOutputClick = async (claudeEvent) => {
    const { fileInfo } = claudeEvent;
    
    if (fileInfo.isRelease) {
      await handleReleaseDeploy(fileInfo);
    } else if (fileInfo.canEdit) {
      await handleFileEdit(fileInfo);
    } else {
      await handleFileClick(fileInfo);
    }
  };

  const isEditableFile = (file) => {
    const editableExtensions = [
      '.md', '.txt', '.py', '.js', '.jsx', '.ts', '.tsx',
      '.html', '.css', '.scss', '.sass', '.json', '.yaml', '.yml'
    ];
    
    return editableExtensions.some(ext => file.name.endsWith(ext));
  };

  const isReleaseFile = (file) => {
    const releasePaths = ['dist/', 'build/', 'release/', 'deploy/'];
    const releaseExtensions = ['.zip', '.tar.gz', '.tgz'];
    
    return releasePaths.some(path => file.path.includes(path)) ||
           releaseExtensions.some(ext => file.name.endsWith(ext));
  };

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
        return a.type === 'directory' ? -1 : b.type === 'directory' ? 1 : b.size - a.size;
      case 'type':
        return a.type.localeCompare(b.type);
      default:
        return 0;
    }
  });

  const renderFileItem = (file) => {
    const isSelected = selectedFile?.path === file.path;
    const isEditable = isEditableFile(file);
    const isRelease = isReleaseFile(file);
    
    return (
      <div
        key={file.path}
        className={`file-item ${isSelected ? 'selected' : ''} ${file.type}`}
        onClick={() => handleFileClick(file)}
      >
        <div className="file-icon">
          {file.icon}
        </div>
        <div className="file-info">
          <div className="file-name" title={file.name}>
            {file.name}
          </div>
          <div className="file-meta">
            <span className="file-size">{file.size}</span>
            <span className="file-modified">{new Date(file.modified).toLocaleString()}</span>
          </div>
        </div>
        <div className="file-actions">
          {isEditable && (
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
          )}
          {isRelease && (
            <button
              className="action-btn deploy"
              onClick={(e) => {
                e.stopPropagation();
                handleReleaseDeploy(file);
              }}
              title="部署 Release"
            >
              🚀
            </button>
          )}
        </div>
      </div>
    );
  };

  const renderClaudeOutput = (claudeEvent, index) => {
    const { fileInfo, eventType, timestamp } = claudeEvent;
    
    return (
      <div
        key={`${fileInfo.path}-${timestamp}`}
        className={`claude-output-item ${fileInfo.isRelease ? 'release' : 'file'}`}
        onClick={() => handleClaudeOutputClick(claudeEvent)}
      >
        <div className="output-icon">
          {fileInfo.isRelease ? '🚀' : '📄'}
        </div>
        <div className="output-info">
          <div className="output-name">{fileInfo.name}</div>
          <div className="output-meta">
            <span className="output-type">
              {fileInfo.isRelease ? 'Release' : 'File'}
            </span>
            <span className="output-event">{eventType}</span>
            <span className="output-time">
              {new Date(timestamp).toLocaleTimeString()}
            </span>
          </div>
        </div>
        <div className="output-actions">
          {fileInfo.canEdit && (
            <span className="action-hint">点击编辑</span>
          )}
          {fileInfo.canDeploy && (
            <span className="action-hint">点击部署</span>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className={`local-file-manager ${className}`}>
      {/* 头部 */}
      <div className="file-manager-header">
        <div className="header-title">
          <span className="title-icon">🗂️</span>
          <span className="title-text">本地文件管理</span>
          <span className={`connection-status ${connectionStatus}`}>
            {connectionStatus === 'connected' && '🟢'}
            {connectionStatus === 'connecting' && '🟡'}
            {connectionStatus === 'error' && '🔴'}
          </span>
        </div>
        
        <div className="header-actions">
          <button
            className="action-btn"
            onClick={() => setShowConnectDialog(true)}
            title="连接文件夹"
            disabled={!isConnected}
          >
            📁
          </button>
          <button
            className="action-btn"
            onClick={refreshCurrentFolder}
            title="刷新"
            disabled={!currentFolder}
          >
            🔄
          </button>
        </div>
      </div>

      {/* 文件夹选择 */}
      {connectedFolders.length > 0 && (
        <div className="folder-selector">
          <select
            value={currentFolder?.id || ''}
            onChange={(e) => {
              const folder = connectedFolders.find(f => f.id === e.target.value);
              setCurrentFolder(folder);
              if (folder) {
                loadFolderFiles(folder.id);
              }
            }}
            className="folder-select"
          >
            {connectedFolders.map(folder => (
              <option key={folder.id} value={folder.id}>
                📁 {folder.path} ({folder.fileCount} 文件)
              </option>
            ))}
          </select>
        </div>
      )}

      {/* 搜索和排序 */}
      <div className="file-controls">
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
      </div>

      {/* Claude Code 输出 */}
      {claudeOutputs.length > 0 && (
        <div className="claude-outputs-section">
          <div className="section-header">
            <h4>🎯 Claude Code 输出</h4>
            <button
              className="toggle-btn"
              onClick={() => setShowClaudeOutputs(!showClaudeOutputs)}
            >
              {showClaudeOutputs ? '🔼' : '🔽'}
            </button>
          </div>
          
          {showClaudeOutputs && (
            <div className="claude-outputs-list">
              {claudeOutputs.map(renderClaudeOutput)}
            </div>
          )}
        </div>
      )}

      {/* 文件列表 */}
      <div className="files-section">
        <div className="section-header">
          <h4>📄 文件列表</h4>
          <span className="file-count">
            {sortedFiles.length} 个文件
          </span>
        </div>
        
        <div className={`file-list ${isLoading ? 'loading' : ''}`}>
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
                {searchTerm ? '未找到匹配的文件' : '请连接文件夹'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* 连接文件夹对话框 */}
      {showConnectDialog && (
        <div className="connect-dialog-overlay">
          <div className="connect-dialog">
            <div className="dialog-header">
              <h3>连接本地文件夹</h3>
              <button
                className="close-btn"
                onClick={() => setShowConnectDialog(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="dialog-content">
              <div className="input-group">
                <label>文件夹路径:</label>
                <input
                  type="text"
                  value={folderPath}
                  onChange={(e) => setFolderPath(e.target.value)}
                  placeholder="例如: /Users/username/projects/my-project"
                  className="folder-path-input"
                />
              </div>
              
              <div className="dialog-actions">
                <button
                  className="cancel-btn"
                  onClick={() => setShowConnectDialog(false)}
                >
                  取消
                </button>
                <button
                  className="connect-btn"
                  onClick={connectLocalFolder}
                  disabled={isLoading || !folderPath.trim()}
                >
                  {isLoading ? '连接中...' : '连接'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LocalFileManager;

