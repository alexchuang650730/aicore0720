/**
 * Terminal Service - 终端管理服务
 * 提供终端操作、命令执行、会话管理等功能
 */

class TerminalService {
  constructor() {
    this.terminals = new Map();
    this.activeTerminalId = null;
    this.commandHistory = [];
    this.maxHistorySize = 1000;
    this.eventListeners = new Map();
  }

  /**
   * 创建新的终端会话
   * @param {string} terminalId - 终端ID
   * @param {Object} options - 终端配置选项
   * @returns {Object} 终端会话对象
   */
  createTerminal(terminalId = null, options = {}) {
    const id = terminalId || `terminal_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const terminal = {
      id,
      created: new Date(),
      lastActivity: new Date(),
      status: 'active',
      workingDirectory: options.cwd || '/home/ubuntu',
      environment: options.env || {},
      history: [],
      output: [],
      isRunning: false,
      currentCommand: null,
      ...options
    };

    this.terminals.set(id, terminal);
    this.activeTerminalId = id;

    this.emit('terminalCreated', { terminalId: id, terminal });
    return terminal;
  }

  /**
   * 执行命令
   * @param {string} command - 要执行的命令
   * @param {string} terminalId - 终端ID
   * @param {Object} options - 执行选项
   * @returns {Promise} 执行结果
   */
  async executeCommand(command, terminalId = null, options = {}) {
    const id = terminalId || this.activeTerminalId;
    const terminal = this.terminals.get(id);
    
    if (!terminal) {
      throw new Error(`Terminal ${id} not found`);
    }

    // 添加到历史记录
    this.addToHistory(command);
    
    // 更新终端状态
    terminal.isRunning = true;
    terminal.currentCommand = command;
    terminal.lastActivity = new Date();

    this.emit('commandStarted', { terminalId: id, command });

    try {
      // 模拟命令执行
      const result = await this.simulateCommandExecution(command, terminal, options);
      
      // 添加到输出
      terminal.output.push({
        type: 'command',
        content: command,
        timestamp: new Date(),
        exitCode: result.exitCode
      });

      if (result.stdout) {
        terminal.output.push({
          type: 'stdout',
          content: result.stdout,
          timestamp: new Date()
        });
      }

      if (result.stderr) {
        terminal.output.push({
          type: 'stderr',
          content: result.stderr,
          timestamp: new Date()
        });
      }

      terminal.isRunning = false;
      terminal.currentCommand = null;

      this.emit('commandCompleted', { 
        terminalId: id, 
        command, 
        result 
      });

      return result;

    } catch (error) {
      terminal.output.push({
        type: 'error',
        content: error.message,
        timestamp: new Date()
      });

      terminal.isRunning = false;
      terminal.currentCommand = null;

      this.emit('commandError', { 
        terminalId: id, 
        command, 
        error 
      });

      throw error;
    }
  }

  /**
   * 模拟命令执行
   * @param {string} command - 命令
   * @param {Object} terminal - 终端对象
   * @param {Object} options - 选项
   * @returns {Promise} 执行结果
   */
  async simulateCommandExecution(command, terminal, options = {}) {
    // 模拟执行延迟
    await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 500));

    const cmd = command.trim().toLowerCase();
    
    // 模拟常见命令
    if (cmd === 'pwd') {
      return {
        exitCode: 0,
        stdout: terminal.workingDirectory,
        stderr: ''
      };
    }

    if (cmd.startsWith('cd ')) {
      const newDir = cmd.substring(3).trim();
      terminal.workingDirectory = newDir.startsWith('/') ? newDir : `${terminal.workingDirectory}/${newDir}`;
      return {
        exitCode: 0,
        stdout: '',
        stderr: ''
      };
    }

    if (cmd === 'ls' || cmd === 'ls -la') {
      return {
        exitCode: 0,
        stdout: `total 24
drwxrwxr-x  6 ubuntu ubuntu 4096 Jul 16 04:48 .
drwxr-xr-x 10 ubuntu ubuntu 4096 Jul 16 04:21 ..
drwxrwxr-x  9 ubuntu ubuntu 4096 Jul 15 11:45 claudeditor
drwxrwxr-x  8 ubuntu ubuntu 4096 Jul 16 04:21 core
drwxrwxr-x  2 ubuntu ubuntu 4096 Jul 16 04:21 docs
drwxrwxr-x  2 ubuntu ubuntu 4096 Jul 16 04:21 tests`,
        stderr: ''
      };
    }

    if (cmd === 'whoami') {
      return {
        exitCode: 0,
        stdout: 'ubuntu',
        stderr: ''
      };
    }

    if (cmd === 'date') {
      return {
        exitCode: 0,
        stdout: new Date().toString(),
        stderr: ''
      };
    }

    if (cmd.startsWith('echo ')) {
      return {
        exitCode: 0,
        stdout: cmd.substring(5),
        stderr: ''
      };
    }

    if (cmd === 'clear') {
      terminal.output = [];
      return {
        exitCode: 0,
        stdout: '',
        stderr: ''
      };
    }

    // 默认响应
    return {
      exitCode: 0,
      stdout: `Command executed: ${command}`,
      stderr: ''
    };
  }

  /**
   * 获取终端列表
   * @returns {Array} 终端列表
   */
  getTerminals() {
    return Array.from(this.terminals.values());
  }

  /**
   * 获取指定终端
   * @param {string} terminalId - 终端ID
   * @returns {Object} 终端对象
   */
  getTerminal(terminalId) {
    return this.terminals.get(terminalId);
  }

  /**
   * 切换活动终端
   * @param {string} terminalId - 终端ID
   */
  switchTerminal(terminalId) {
    if (this.terminals.has(terminalId)) {
      this.activeTerminalId = terminalId;
      this.emit('terminalSwitched', { terminalId });
    }
  }

  /**
   * 关闭终端
   * @param {string} terminalId - 终端ID
   */
  closeTerminal(terminalId) {
    const terminal = this.terminals.get(terminalId);
    if (terminal) {
      this.terminals.delete(terminalId);
      
      if (this.activeTerminalId === terminalId) {
        const remaining = Array.from(this.terminals.keys());
        this.activeTerminalId = remaining.length > 0 ? remaining[0] : null;
      }

      this.emit('terminalClosed', { terminalId });
    }
  }

  /**
   * 获取命令历史
   * @returns {Array} 命令历史
   */
  getCommandHistory() {
    return [...this.commandHistory];
  }

  /**
   * 添加到命令历史
   * @param {string} command - 命令
   */
  addToHistory(command) {
    if (command && command.trim()) {
      this.commandHistory.push({
        command: command.trim(),
        timestamp: new Date()
      });

      // 限制历史记录大小
      if (this.commandHistory.length > this.maxHistorySize) {
        this.commandHistory = this.commandHistory.slice(-this.maxHistorySize);
      }
    }
  }

  /**
   * 清空命令历史
   */
  clearHistory() {
    this.commandHistory = [];
    this.emit('historyCleaned');
  }

  /**
   * 获取终端输出
   * @param {string} terminalId - 终端ID
   * @returns {Array} 输出内容
   */
  getTerminalOutput(terminalId) {
    const terminal = this.terminals.get(terminalId);
    return terminal ? terminal.output : [];
  }

  /**
   * 清空终端输出
   * @param {string} terminalId - 终端ID
   */
  clearTerminalOutput(terminalId) {
    const terminal = this.terminals.get(terminalId);
    if (terminal) {
      terminal.output = [];
      this.emit('terminalCleared', { terminalId });
    }
  }

  /**
   * 事件监听
   * @param {string} event - 事件名
   * @param {Function} callback - 回调函数
   */
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event).push(callback);
  }

  /**
   * 移除事件监听
   * @param {string} event - 事件名
   * @param {Function} callback - 回调函数
   */
  off(event, callback) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * 触发事件
   * @param {string} event - 事件名
   * @param {Object} data - 事件数据
   */
  emit(event, data) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in terminal service event listener:`, error);
        }
      });
    }
  }

  /**
   * 获取终端状态
   * @returns {Object} 状态信息
   */
  getStatus() {
    return {
      totalTerminals: this.terminals.size,
      activeTerminalId: this.activeTerminalId,
      commandHistorySize: this.commandHistory.length,
      runningCommands: Array.from(this.terminals.values())
        .filter(t => t.isRunning)
        .map(t => ({ id: t.id, command: t.currentCommand }))
    };
  }
}

// 创建单例实例
const terminalService = new TerminalService();

// 初始化默认终端
terminalService.createTerminal('default', {
  name: 'Default Terminal',
  cwd: '/home/ubuntu/aicore0716'
});

export default terminalService;

