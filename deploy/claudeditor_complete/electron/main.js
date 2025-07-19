const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// 保持對window對象的全局引用
let mainWindow;
let serverProcess;

function createWindow() {
    // 創建瀏覽器窗口
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        },
        icon: path.join(__dirname, '../assets/icon.png'),
        titleBarStyle: 'hiddenInset',
        show: false
    });

    // 加載應用的HTML文件
    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:5173');
        // 打開開發者工具
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }

    // 窗口準備好後顯示
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        
        // 檢查更新
        checkForUpdates();
    });

    // 當窗口關閉時觸發
    mainWindow.on('closed', () => {
        mainWindow = null;
        
        // 關閉後端服務
        if (serverProcess) {
            serverProcess.kill();
        }
    });

    // 處理外部鏈接
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    // 設置菜單
    createMenu();
}

function createMenu() {
    const template = [
        {
            label: 'ClaudeEditor',
            submenu: [
                {
                    label: '關於ClaudeEditor',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: '關於ClaudeEditor',
                            message: 'ClaudeEditor v1.0.0',
                            detail: '讓開發永不偏離目標的智能開發助手\n\n特色功能：\n• 六大工作流管理\n• Claude + K2雙AI模式\n• 成本優化 2元→8元\n• 跨平台支持\n• 實時目標對齊檢測'
                        });
                    }
                },
                { type: 'separator' },
                {
                    label: '偏好設置',
                    accelerator: 'CmdOrCtrl+,',
                    click: () => {
                        // 發送消息到渲染進程打開設置
                        mainWindow.webContents.send('open-settings');
                    }
                },
                { type: 'separator' },
                {
                    label: '退出',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
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
                { label: '全選', accelerator: 'CmdOrCtrl+A', role: 'selectall' }
            ]
        },
        {
            label: '視圖',
            submenu: [
                { label: '重新載入', accelerator: 'CmdOrCtrl+R', role: 'reload' },
                { label: '強制重新載入', accelerator: 'CmdOrCtrl+Shift+R', role: 'forceReload' },
                { label: '開發者工具', accelerator: 'F12', role: 'toggleDevTools' },
                { type: 'separator' },
                { label: '實際大小', accelerator: 'CmdOrCtrl+0', role: 'resetZoom' },
                { label: '放大', accelerator: 'CmdOrCtrl+Plus', role: 'zoomIn' },
                { label: '縮小', accelerator: 'CmdOrCtrl+-', role: 'zoomOut' },
                { type: 'separator' },
                { label: '全屏', accelerator: 'F11', role: 'togglefullscreen' }
            ]
        },
        {
            label: '工作流',
            submenu: [
                {
                    label: '目標驅動開發',
                    accelerator: 'CmdOrCtrl+1',
                    click: () => {
                        mainWindow.webContents.send('switch-workflow', 'goal-driven');
                    }
                },
                {
                    label: '智能代碼生成',
                    accelerator: 'CmdOrCtrl+2',
                    click: () => {
                        mainWindow.webContents.send('switch-workflow', 'code-generation');
                    }
                },
                {
                    label: '自動化測試',
                    accelerator: 'CmdOrCtrl+3',
                    click: () => {
                        mainWindow.webContents.send('switch-workflow', 'testing');
                    }
                },
                {
                    label: '質量保證',
                    accelerator: 'CmdOrCtrl+4',
                    click: () => {
                        mainWindow.webContents.send('switch-workflow', 'quality');
                    }
                },
                {
                    label: '智能部署',
                    accelerator: 'CmdOrCtrl+5',
                    click: () => {
                        mainWindow.webContents.send('switch-workflow', 'deployment');
                    }
                },
                {
                    label: '自適應學習',
                    accelerator: 'CmdOrCtrl+6',
                    click: () => {
                        mainWindow.webContents.send('switch-workflow', 'learning');
                    }
                }
            ]
        },
        {
            label: 'AI助手',
            submenu: [
                {
                    label: '切換到Claude模式',
                    accelerator: 'CmdOrCtrl+Shift+C',
                    click: () => {
                        mainWindow.webContents.send('switch-ai-mode', 'claude');
                    }
                },
                {
                    label: '切換到K2模式',
                    accelerator: 'CmdOrCtrl+Shift+K',
                    click: () => {
                        mainWindow.webContents.send('switch-ai-mode', 'k2');
                    }
                },
                { type: 'separator' },
                {
                    label: '成本統計',
                    click: () => {
                        mainWindow.webContents.send('show-cost-stats');
                    }
                },
                {
                    label: '對齊度報告',
                    click: () => {
                        mainWindow.webContents.send('show-alignment-report');
                    }
                }
            ]
        },
        {
            label: '工具',
            submenu: [
                {
                    label: '打開終端',
                    accelerator: 'CmdOrCtrl+`',
                    click: () => {
                        // 在系統中打開終端
                        const terminal = process.platform === 'darwin' ? 'Terminal' : 'cmd';
                        spawn(terminal, [], { detached: true });
                    }
                },
                {
                    label: '項目管理',
                    click: () => {
                        mainWindow.webContents.send('open-project-manager');
                    }
                },
                { type: 'separator' },
                {
                    label: '導入項目',
                    click: async () => {
                        const result = await dialog.showOpenDialog(mainWindow, {
                            title: '選擇項目目錄',
                            properties: ['openDirectory']
                        });
                        
                        if (!result.canceled) {
                            mainWindow.webContents.send('import-project', result.filePaths[0]);
                        }
                    }
                },
                {
                    label: '導出項目',
                    click: async () => {
                        const result = await dialog.showSaveDialog(mainWindow, {
                            title: '保存項目',
                            defaultPath: 'claudeditor-project.zip',
                            filters: [
                                { name: 'Zip files', extensions: ['zip'] }
                            ]
                        });
                        
                        if (!result.canceled) {
                            mainWindow.webContents.send('export-project', result.filePath);
                        }
                    }
                }
            ]
        },
        {
            label: '幫助',
            submenu: [
                {
                    label: '用戶手冊',
                    click: () => {
                        shell.openExternal('https://github.com/alexchuang650730/aicore0718/blob/main/README.md');
                    }
                },
                {
                    label: '快捷鍵',
                    click: () => {
                        mainWindow.webContents.send('show-shortcuts');
                    }
                },
                { type: 'separator' },
                {
                    label: '報告問題',
                    click: () => {
                        shell.openExternal('https://github.com/alexchuang650730/aicore0718/issues');
                    }
                },
                {
                    label: '檢查更新',
                    click: () => {
                        checkForUpdates();
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

function checkForUpdates() {
    // 簡化的更新檢查
    console.log('檢查更新...');
    // 這裡可以集成electron-updater
}

// 啟動後端服務
function startBackendServer() {
    const serverPath = path.join(__dirname, '../server/index.js');
    
    if (fs.existsSync(serverPath)) {
        serverProcess = spawn('node', [serverPath], {
            stdio: 'inherit'
        });
        
        serverProcess.on('error', (error) => {
            console.error('後端服務啟動失敗:', error);
        });
        
        serverProcess.on('exit', (code) => {
            console.log(`後端服務退出，代碼: ${code}`);
        });
    }
}

// 處理IPC消息
ipcMain.handle('get-app-version', () => {
    return app.getVersion();
});

ipcMain.handle('show-message-box', async (event, options) => {
    const result = await dialog.showMessageBox(mainWindow, options);
    return result;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
    const result = await dialog.showOpenDialog(mainWindow, options);
    return result;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, options);
    return result;
});

// 當所有窗口關閉時退出應用
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

// 當Electron完成初始化時創建窗口
app.whenReady().then(() => {
    createWindow();
    startBackendServer();
});

// 處理證書錯誤
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
    // 在開發環境中忽略證書錯誤
    if (process.env.NODE_ENV === 'development') {
        event.preventDefault();
        callback(true);
    } else {
        callback(false);
    }
});

// 安全設置
app.on('web-contents-created', (event, contents) => {
    contents.on('new-window', (event, navigationUrl) => {
        event.preventDefault();
        shell.openExternal(navigationUrl);
    });
});

// 處理協議
app.setAsDefaultProtocolClient('claudeditor');