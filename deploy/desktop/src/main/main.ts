import { app, BrowserWindow, ipcMain, Menu, dialog, shell, protocol } from 'electron';
import { autoUpdater } from 'electron-updater';
import Store from 'electron-store';
import * as path from 'path';
import * as os from 'os';
import * as cluster from 'cluster';
import * as WebSocket from 'ws';

// 高性能配置
import { PerformanceManager } from './performance/PerformanceManager';
import { ConnectionPool } from './performance/ConnectionPool';
import { CacheManager } from './performance/CacheManager';
import { WorkerManager } from './performance/WorkerManager';

// 設置
const store = new Store();
const isDevelopment = process.env.NODE_ENV !== 'production';

// 性能管理器
const performanceManager = new PerformanceManager();
const connectionPool = new ConnectionPool();
const cacheManager = new CacheManager();
const workerManager = new WorkerManager();

// 主窗口
let mainWindow: BrowserWindow | null = null;
let splashWindow: BrowserWindow | null = null;

// 高併發配置
const HIGH_CONCURRENCY_CONFIG = {
  maxConnections: 10000,
  connectionTimeout: 30000,
  keepAlive: true,
  maxSockets: 100,
  maxFreeSockets: 50,
  timeout: 5000,
  freeSocketTimeout: 15000,
  workers: os.cpus().length,
  clustering: true,
  loadBalancing: true,
  compressionEnabled: true,
  cacheTTL: 300000, // 5分鐘
  batchSize: 1000,
  queueSize: 10000,
};

// 初始化高併發集群
function initializeCluster() {
  if (cluster.isMaster && HIGH_CONCURRENCY_CONFIG.clustering) {
    console.log(`主進程 ${process.pid} 正在運行`);
    
    // 創建工作進程
    for (let i = 0; i < HIGH_CONCURRENCY_CONFIG.workers; i++) {
      cluster.fork();
    }
    
    // 工作進程重啟
    cluster.on('exit', (worker, code, signal) => {
      console.log(`工作進程 ${worker.process.pid} 退出`);
      cluster.fork();
    });
    
    // 負載均衡
    cluster.on('message', (worker, message) => {
      if (message.type === 'load-balance') {
        distributeLoad(message.data);
      }
    });
  }
}

// 創建主窗口
function createMainWindow(): BrowserWindow {
  // 啟動畫面
  splashWindow = new BrowserWindow({
    width: 400,
    height: 300,
    frame: false,
    alwaysOnTop: true,
    transparent: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  splashWindow.loadFile(path.join(__dirname, '../renderer/splash.html'));

  // 主窗口配置（高性能）
  const window = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    show: false,
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, '../preload/preload.js'),
      webSecurity: !isDevelopment,
      allowRunningInsecureContent: isDevelopment,
      experimentalFeatures: true,
      // 高性能配置
      backgroundThrottling: false,
      offscreen: false,
      nodeIntegrationInWorker: true,
      nodeIntegrationInSubFrames: false,
      webgl: true,
      plugins: true,
      java: false,
      javascript: true,
      images: true,
      textAreasAreResizable: true,
      webAudio: true,
      // 內存優化
      v8CacheOptions: 'code',
      // 多進程支持
      sandbox: false,
      partition: 'persist:main',
    },
  });

  // 性能優化
  window.webContents.on('before-input-event', (event, input) => {
    performanceManager.recordInput(input);
  });

  // 加載應用
  if (isDevelopment) {
    window.loadURL('http://localhost:3000');
    window.webContents.openDevTools();
  } else {
    window.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  // 窗口事件
  window.once('ready-to-show', () => {
    if (splashWindow) {
      splashWindow.close();
      splashWindow = null;
    }
    window.show();
    
    // 性能監控
    performanceManager.startMonitoring(window);
  });

  window.on('closed', () => {
    mainWindow = null;
    performanceManager.stopMonitoring();
  });

  return window;
}

// 性能優化的IPC處理
function setupIPC() {
  // 高併發API調用
  ipcMain.handle('api-call', async (event, { method, url, data, options = {} }) => {
    try {
      const pooledConnection = await connectionPool.acquire();
      const cacheKey = `${method}:${url}:${JSON.stringify(data)}`;
      
      // 檢查緩存
      const cachedResult = await cacheManager.get(cacheKey);
      if (cachedResult && options.useCache !== false) {
        connectionPool.release(pooledConnection);
        return cachedResult;
      }
      
      // 執行請求
      const result = await pooledConnection.request({
        method,
        url,
        data,
        timeout: HIGH_CONCURRENCY_CONFIG.timeout,
        ...options,
      });
      
      // 緩存結果
      if (options.cacheable !== false) {
        await cacheManager.set(cacheKey, result, HIGH_CONCURRENCY_CONFIG.cacheTTL);
      }
      
      connectionPool.release(pooledConnection);
      return result;
    } catch (error) {
      console.error('API調用失敗:', error);
      throw error;
    }
  });

  // 批量處理
  ipcMain.handle('batch-process', async (event, { operations, options = {} }) => {
    try {
      const batchSize = options.batchSize || HIGH_CONCURRENCY_CONFIG.batchSize;
      const results = [];
      
      for (let i = 0; i < operations.length; i += batchSize) {
        const batch = operations.slice(i, i + batchSize);
        const batchResults = await Promise.all(
          batch.map(op => workerManager.execute(op))
        );
        results.push(...batchResults);
      }
      
      return results;
    } catch (error) {
      console.error('批量處理失敗:', error);
      throw error;
    }
  });

  // WebSocket連接池
  ipcMain.handle('websocket-connect', async (event, { url, options = {} }) => {
    try {
      const ws = new WebSocket(url, {
        ...options,
        perMessageDeflate: HIGH_CONCURRENCY_CONFIG.compressionEnabled,
      });
      
      const connectionId = connectionPool.addWebSocket(ws);
      
      ws.on('message', (data) => {
        event.sender.send('websocket-message', { connectionId, data });
      });
      
      ws.on('error', (error) => {
        event.sender.send('websocket-error', { connectionId, error });
      });
      
      ws.on('close', () => {
        connectionPool.removeWebSocket(connectionId);
        event.sender.send('websocket-close', { connectionId });
      });
      
      return { connectionId };
    } catch (error) {
      console.error('WebSocket連接失敗:', error);
      throw error;
    }
  });

  // AI模式切換（優化版）
  ipcMain.handle('switch-ai-mode', async (event, { mode, options = {} }) => {
    try {
      const worker = await workerManager.getWorker('ai-processing');
      const result = await worker.switchMode(mode, options);
      
      // 預加載模型
      if (options.preload) {
        await worker.preloadModel(mode);
      }
      
      return result;
    } catch (error) {
      console.error('AI模式切換失敗:', error);
      throw error;
    }
  });

  // K2專用處理（低成本高效率）
  ipcMain.handle('k2-process', async (event, { input, options = {} }) => {
    try {
      const k2Worker = await workerManager.getWorker('k2-processing');
      
      // 成本優化配置
      const costOptimizedOptions = {
        ...options,
        compression: true,
        batchProcessing: true,
        cacheEnabled: true,
        modelSize: 'efficient', // 使用效率優化的模型
        maxTokens: options.maxTokens || 4000,
        temperature: options.temperature || 0.7,
        costThreshold: 2, // 2元人民幣成本控制
        targetOutput: 8, // 8元人民幣價值輸出
      };
      
      const result = await k2Worker.process(input, costOptimizedOptions);
      
      // 成本追蹤
      await cacheManager.set(
        `k2-cost-${Date.now()}`,
        {
          input: input.length,
          output: result.length,
          cost: result.cost,
          timestamp: Date.now(),
        },
        86400000 // 24小時
      );
      
      return result;
    } catch (error) {
      console.error('K2處理失敗:', error);
      throw error;
    }
  });

  // 文件處理（高性能）
  ipcMain.handle('file-process', async (event, { operation, files, options = {} }) => {
    try {
      const fileWorker = await workerManager.getWorker('file-processing');
      
      const results = await Promise.all(
        files.map(file => fileWorker.processFile(file, operation, options))
      );
      
      return results;
    } catch (error) {
      console.error('文件處理失敗:', error);
      throw error;
    }
  });

  // 性能監控
  ipcMain.handle('get-performance-stats', async () => {
    return performanceManager.getStats();
  });

  // 系統資源監控
  ipcMain.handle('get-system-stats', async () => {
    return {
      memory: process.memoryUsage(),
      cpu: process.cpuUsage(),
      uptime: process.uptime(),
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version,
      connections: connectionPool.getStats(),
      cache: cacheManager.getStats(),
      workers: workerManager.getStats(),
    };
  });
}

// 菜單設置
function createMenu() {
  const template = [
    {
      label: 'PowerAutomation',
      submenu: [
        {
          label: '關於 PowerAutomation',
          role: 'about',
        },
        {
          label: '設置',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            mainWindow?.webContents.send('open-settings');
          },
        },
        { type: 'separator' },
        {
          label: '隱藏 PowerAutomation',
          accelerator: 'CmdOrCtrl+H',
          role: 'hide',
        },
        {
          label: '隱藏其他',
          accelerator: 'CmdOrCtrl+Alt+H',
          role: 'hideothers',
        },
        { type: 'separator' },
        {
          label: '退出',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          },
        },
      ],
    },
    {
      label: '編輯',
      submenu: [
        { label: '撤銷', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
        { label: '重做', accelerator: 'Shift+CmdOrCtrl+Z', role: 'redo' },
        { type: 'separator' },
        { label: '剪切', accelerator: 'CmdOrCtrl+X', role: 'cut' },
        { label: '複製', accelerator: 'CmdOrCtrl+C', role: 'copy' },
        { label: '粘貼', accelerator: 'CmdOrCtrl+V', role: 'paste' },
        { label: '全選', accelerator: 'CmdOrCtrl+A', role: 'selectall' },
      ],
    },
    {
      label: '視圖',
      submenu: [
        { label: '重載', accelerator: 'CmdOrCtrl+R', role: 'reload' },
        { label: '強制重載', accelerator: 'CmdOrCtrl+Shift+R', role: 'forceReload' },
        { label: '切換開發者工具', accelerator: 'F12', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: '實際大小', accelerator: 'CmdOrCtrl+0', role: 'resetZoom' },
        { label: '放大', accelerator: 'CmdOrCtrl+Plus', role: 'zoomIn' },
        { label: '縮小', accelerator: 'CmdOrCtrl+-', role: 'zoomOut' },
        { type: 'separator' },
        { label: '全屏', accelerator: 'F11', role: 'togglefullscreen' },
      ],
    },
    {
      label: 'AI',
      submenu: [
        {
          label: '切換到 Claude 模式',
          accelerator: 'CmdOrCtrl+1',
          click: () => {
            mainWindow?.webContents.send('switch-ai-mode', 'claude');
          },
        },
        {
          label: '切換到 K2 模式',
          accelerator: 'CmdOrCtrl+2',
          click: () => {
            mainWindow?.webContents.send('switch-ai-mode', 'k2');
          },
        },
        { type: 'separator' },
        {
          label: '新建對話',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow?.webContents.send('new-chat');
          },
        },
        {
          label: '清除對話',
          accelerator: 'CmdOrCtrl+K',
          click: () => {
            mainWindow?.webContents.send('clear-chat');
          },
        },
      ],
    },
    {
      label: '工具',
      submenu: [
        {
          label: '性能監控',
          click: () => {
            mainWindow?.webContents.send('open-performance-monitor');
          },
        },
        {
          label: '系統狀態',
          click: () => {
            mainWindow?.webContents.send('open-system-status');
          },
        },
        {
          label: '連接池狀態',
          click: () => {
            mainWindow?.webContents.send('open-connection-pool-status');
          },
        },
        { type: 'separator' },
        {
          label: '清除緩存',
          click: async () => {
            await cacheManager.clear();
            mainWindow?.webContents.send('cache-cleared');
          },
        },
        {
          label: '重置連接池',
          click: async () => {
            await connectionPool.reset();
            mainWindow?.webContents.send('connection-pool-reset');
          },
        },
      ],
    },
    {
      label: '窗口',
      submenu: [
        { label: '最小化', accelerator: 'CmdOrCtrl+M', role: 'minimize' },
        { label: '關閉', accelerator: 'CmdOrCtrl+W', role: 'close' },
        { type: 'separator' },
        { label: '前置所有窗口', role: 'front' },
      ],
    },
    {
      label: '幫助',
      submenu: [
        {
          label: '了解 PowerAutomation',
          click: () => {
            shell.openExternal('https://github.com/alexchuang650730/aicore0718');
          },
        },
        {
          label: '報告問題',
          click: () => {
            shell.openExternal('https://github.com/alexchuang650730/aicore0718/issues');
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// 自動更新
function setupAutoUpdater() {
  if (isDevelopment) return;

  autoUpdater.checkForUpdatesAndNotify();

  autoUpdater.on('update-available', () => {
    dialog.showMessageBox(mainWindow!, {
      type: 'info',
      title: '更新可用',
      message: '發現新版本，正在下載...',
      buttons: ['確定'],
    });
  });

  autoUpdater.on('update-downloaded', () => {
    dialog.showMessageBox(mainWindow!, {
      type: 'info',
      title: '更新下載完成',
      message: '更新已下載完成，將在重啟後安裝',
      buttons: ['立即重啟', '稍後重啟'],
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  });
}

// 應用程序事件
app.whenReady().then(() => {
  // 初始化集群
  initializeCluster();
  
  // 設置協議
  protocol.registerFileProtocol('powerautomation', (request, callback) => {
    const url = request.url.substr(16);
    callback({ path: path.normalize(`${__dirname}/${url}`) });
  });

  // 創建主窗口
  mainWindow = createMainWindow();
  
  // 設置菜單
  createMenu();
  
  // 設置IPC
  setupIPC();
  
  // 設置自動更新
  setupAutoUpdater();
  
  // 性能優化
  app.commandLine.appendSwitch('--max-http-header-size', '81920');
  app.commandLine.appendSwitch('--max-old-space-size', '8192');
  app.commandLine.appendSwitch('--enable-features', 'VaapiVideoDecoder');
  app.commandLine.appendSwitch('--disable-features', 'VizDisplayCompositor');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    mainWindow = createMainWindow();
  }
});

// 性能優化
app.on('browser-window-created', (event, window) => {
  window.webContents.on('did-finish-load', () => {
    window.webContents.insertCSS(`
      body {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }
    `);
  });
});

// 內存清理
setInterval(() => {
  if (global.gc) {
    global.gc();
  }
}, 300000); // 每5分鐘清理一次

// 處理未捕獲的異常
process.on('uncaughtException', (error) => {
  console.error('未捕獲的異常:', error);
});

process.on('unhandledRejection', (error) => {
  console.error('未處理的Promise拒絕:', error);
});

// 負載分發
function distributeLoad(data: any) {
  const workers = Object.values(cluster.workers);
  const targetWorker = workers[Math.floor(Math.random() * workers.length)];
  targetWorker?.send({ type: 'task', data });
}

export { mainWindow, HIGH_CONCURRENCY_CONFIG };