/**
 * 簡潔的 Core 連接器 - 只處理核心通信
 */
class CoreConnector {
  constructor() {
    this.ws = null;
    this.connected = false;
    this.claudeEditorId = null;
    this.callbacks = new Map();
  }

  async connect() {
    try {
      this.ws = new WebSocket('ws://localhost:8081');
      
      this.ws.onopen = () => {
        this.connected = true;
        this.register();
        console.log('✅ 已連接到 PowerAutomation Core');
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      };

      this.ws.onclose = () => {
        this.connected = false;
        console.log('❌ 與 Core 連接斷開');
      };

      return true;
    } catch (error) {
      console.error('連接失敗:', error);
      return false;
    }
  }

  register() {
    this.send({
      action: 'register_claudeditor',
      params: {
        name: 'ClaudeEditor',
        version: '4.6.9.1',
        capabilities: ['code_editing', 'file_management', 'ui_generation']
      }
    });
  }

  handleMessage(data) {
    const { type, ...payload } = data;
    
    if (type === 'core_command') {
      this.executeCommand(payload);
    } else if (type === 'register_response' && payload.status === 'success') {
      this.claudeEditorId = payload.claudeditor_id;
      console.log(`✅ 註冊成功: ${this.claudeEditorId}`);
    }
  }

  executeCommand({ command, params }) {
    // 觸發事件給 React 組件處理
    const event = new CustomEvent('core-command', {
      detail: { command, params }
    });
    window.dispatchEvent(event);
  }

  send(message) {
    if (this.connected && this.ws) {
      this.ws.send(JSON.stringify(message));
    }
  }

  // 回應 Core 命令
  respondToCore(command, result) {
    this.send({
      action: 'command_response',
      params: { command, result }
    });
  }
}

const coreConnector = new CoreConnector();
export default coreConnector;