/**
 * LocalFileSystemService - 本地文件系统服务
 * 集成 PowerAutomation local_adapter_mcp 的文件系统适配器
 */

class LocalFileSystemService {
  constructor() {
    this.connectedFolders = new Map();
    this.fileCache = new Map();
    this.claudeOutputCallbacks = [];
    this.isInitialized = false;
    
    // PowerAutomation MCP 集成
    this.mcpEndpoint = 'http://127.0.0.1:8080/mcp';
    this.adapterEndpoint = 'http://127.0.0.1:8080/local-adapter';
  }
  
  async initialize() {
    try {
      console.log('🗂️ 初始化本地文件系统服务...');
      
      // 检查 PowerAutomation MCP 连接
      const mcpStatus = await this.checkMCPConnection();
      if (!mcpStatus.connected) {
        throw new Error('PowerAutomation MCP 未连接');
      }
      
      // 初始化文件系统适配器
      const initResult = await this.callMCPAdapter('initialize', {});
      if (!initResult.success) {
        throw new Error('文件系统适配器初始化失败');
      }
      
      this.isInitialized = true;
      console.log('✅ 本地文件系统服务初始化完成');
      
      return { success: true };
      
    } catch (error) {
      console.error('❌ 本地文件系统服务初始化失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  async checkMCPConnection() {
    try {
      const response = await fetch(`${this.mcpEndpoint}/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const status = await response.json();
        return {
          connected: true,
          status: status
        };
      }
      
      return { connected: false };
      
    } catch (error) {
      console.warn('MCP 连接检查失败:', error);
      return { connected: false, error: error.message };
    }
  }
  
  async callMCPAdapter(method, params) {
    try {
      const response = await fetch(`${this.adapterEndpoint}/file-system`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          method: method,
          params: params
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
      
    } catch (error) {
      console.error(`MCP 适配器调用失败 (${method}):`, error);
      return { success: false, error: error.message };
    }
  }
  
  async connectLocalFolder(folderPath, watchChanges = true) {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }
      
      console.log(`📁 连接本地文件夹: ${folderPath}`);
      
      const result = await this.callMCPAdapter('connect_local_folder', {
        folder_path: folderPath,
        watch_changes: watchChanges
      });
      
      if (result.success) {
        this.connectedFolders.set(result.folder_id, {
          id: result.folder_id,
          path: result.path,
          fileCount: result.file_count,
          watchEnabled: result.watch_enabled,
          files: result.files || []
        });
        
        // 缓存文件列表
        this.fileCache.set(result.folder_id, result.files || []);
        
        console.log(`✅ 文件夹连接成功: ${result.file_count} 个文件`);
        
        // 启动 Claude Code 输出监听
        if (watchChanges) {
          this.startClaudeOutputMonitoring(result.folder_id);
        }
      }
      
      return result;
      
    } catch (error) {
      console.error('连接本地文件夹失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  async getFileContent(filePath) {
    try {
      console.log(`📖 读取文件内容: ${filePath}`);
      
      const result = await this.callMCPAdapter('get_file_content', {
        file_path: filePath
      });
      
      if (result.success) {
        console.log(`✅ 文件读取成功: ${result.lines} 行`);
      }
      
      return result;
      
    } catch (error) {
      console.error('读取文件内容失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  async saveFileContent(filePath, content) {
    try {
      console.log(`💾 保存文件内容: ${filePath}`);
      
      const result = await this.callMCPAdapter('save_file_content', {
        file_path: filePath,
        content: content
      });
      
      if (result.success) {
        console.log(`✅ 文件保存成功: ${result.size} 字节`);
      }
      
      return result;
      
    } catch (error) {
      console.error('保存文件内容失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  async getFolderFiles(folderId) {
    try {
      const result = await this.callMCPAdapter('get_folder_files', {
        folder_id: folderId
      });
      
      if (result.success) {
        // 更新缓存
        this.fileCache.set(folderId, result.files);
        
        // 更新连接信息
        if (this.connectedFolders.has(folderId)) {
          const folder = this.connectedFolders.get(folderId);
          folder.fileCount = result.file_count;
          folder.files = result.files;
        }
      }
      
      return result;
      
    } catch (error) {
      console.error('获取文件夹文件失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  async refreshFolder(folderId) {
    try {
      console.log(`🔄 刷新文件夹: ${folderId}`);
      
      const result = await this.callMCPAdapter('refresh_folder', {
        folder_id: folderId
      });
      
      if (result.success) {
        // 更新缓存
        this.fileCache.set(folderId, result.files);
        
        // 更新连接信息
        if (this.connectedFolders.has(folderId)) {
          const folder = this.connectedFolders.get(folderId);
          folder.fileCount = result.file_count;
          folder.files = result.files;
        }
        
        console.log(`✅ 文件夹刷新成功: ${result.file_count} 个文件`);
        
        // 通知所有监听器
        this.notifyFileListChanged(folderId, result.files);
      }
      
      return result;
      
    } catch (error) {
      console.error('刷新文件夹失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  startClaudeOutputMonitoring(folderId) {
    console.log(`👀 开始监听 Claude Code 输出: ${folderId}`);
    
    // 模拟 Claude Code 输出监听
    // 实际实现中，这里会通过 WebSocket 或 Server-Sent Events 接收实时更新
    setInterval(async () => {
      try {
        const result = await this.getFolderFiles(folderId);
        if (result.success) {
          // 检查是否有新文件
          const cachedFiles = this.fileCache.get(folderId) || [];
          const newFiles = result.files.filter(file => 
            !cachedFiles.find(cached => cached.path === file.path)
          );
          
          if (newFiles.length > 0) {
            console.log(`🔍 检测到 ${newFiles.length} 个新文件`);
            
            // 分析新文件类型
            for (const file of newFiles) {
              await this.handleClaudeOutput(folderId, 'created', file);
            }
          }
        }
      } catch (error) {
        console.error('Claude Code 输出监听失败:', error);
      }
    }, 2000); // 每2秒检查一次
  }
  
  async handleClaudeOutput(folderId, eventType, fileInfo) {
    try {
      console.log(`🎯 处理 Claude Code 输出: ${fileInfo.name} (${eventType})`);
      
      // 判断文件类型
      const isRelease = this.isReleaseFile(fileInfo);
      
      const claudeEvent = {
        folderId: folderId,
        eventType: eventType,
        fileInfo: {
          ...fileInfo,
          isRelease: isRelease,
          canEdit: !isRelease && this.isEditableFile(fileInfo),
          canDeploy: isRelease
        },
        timestamp: new Date().toISOString()
      };
      
      // 通知所有回调函数
      for (const callback of this.claudeOutputCallbacks) {
        try {
          await callback(claudeEvent);
        } catch (error) {
          console.error('Claude 输出回调执行失败:', error);
        }
      }
      
    } catch (error) {
      console.error('处理 Claude Code 输出失败:', error);
    }
  }
  
  isReleaseFile(fileInfo) {
    const releasePaths = ['dist/', 'build/', 'release/', 'deploy/'];
    const releaseExtensions = ['.zip', '.tar.gz', '.tgz'];
    
    return releasePaths.some(path => fileInfo.path.includes(path)) ||
           releaseExtensions.some(ext => fileInfo.name.endsWith(ext));
  }
  
  isEditableFile(fileInfo) {
    const editableExtensions = [
      '.md', '.txt', '.py', '.js', '.jsx', '.ts', '.tsx',
      '.html', '.css', '.scss', '.sass', '.json', '.yaml', '.yml'
    ];
    
    return editableExtensions.some(ext => fileInfo.name.endsWith(ext));
  }
  
  registerClaudeOutputCallback(callback) {
    this.claudeOutputCallbacks.push(callback);
    console.log(`📝 注册 Claude 输出回调: ${this.claudeOutputCallbacks.length} 个回调`);
  }
  
  unregisterClaudeOutputCallback(callback) {
    const index = this.claudeOutputCallbacks.indexOf(callback);
    if (index > -1) {
      this.claudeOutputCallbacks.splice(index, 1);
      console.log(`🗑️ 取消注册 Claude 输出回调: ${this.claudeOutputCallbacks.length} 个回调`);
    }
  }
  
  notifyFileListChanged(folderId, files) {
    // 触发自定义事件
    const event = new CustomEvent('fileListChanged', {
      detail: { folderId, files }
    });
    window.dispatchEvent(event);
  }
  
  getConnectedFolders() {
    return Array.from(this.connectedFolders.values());
  }
  
  getFileCache(folderId) {
    return this.fileCache.get(folderId) || [];
  }
  
  async getStatus() {
    try {
      const result = await this.callMCPAdapter('get_status', {});
      
      return {
        service: 'LocalFileSystemService',
        initialized: this.isInitialized,
        connectedFolders: this.connectedFolders.size,
        claudeCallbacks: this.claudeOutputCallbacks.length,
        mcpAdapter: result.success ? result : null
      };
      
    } catch (error) {
      return {
        service: 'LocalFileSystemService',
        initialized: this.isInitialized,
        connectedFolders: this.connectedFolders.size,
        claudeCallbacks: this.claudeOutputCallbacks.length,
        error: error.message
      };
    }
  }
}

// 全局实例
const localFileSystemService = new LocalFileSystemService();

// 导出
export default localFileSystemService;

