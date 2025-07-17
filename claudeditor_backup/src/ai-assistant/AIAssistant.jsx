import React, { useState, useEffect, useRef } from 'react'

const AIAssistant = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: '🚀 PowerAutomation AI 助手 v4.6.9.6 - AG-UI & SmartUI Edition\n\n我是您的智能 AI 助手！现在支持：\n\n🎨 **AG-UI 智能生成**\n• 自动生成UI组件\n• 智能布局设计\n• 多主题支持\n\n📱 **SmartUI 响应式系统**\n• 智能设备适配\n• 自动布局调整\n• 跨设备兼容\n\n💻 **开发辅助功能**\n• 代码生成和优化\n• 项目架构分析\n• 自动化测试\n\n选择功能开始使用吧！',
      timestamp: new Date().toLocaleTimeString(),
      model: 'claude',
      source: 'system'
    }
  ])
  
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentModel, setCurrentModel] = useState('claude')
  const messagesEndRef = useRef(null)

  // 可用模型配置
  const availableModels = [
    { id: 'claude', name: 'Claude 3.5 Sonnet', icon: '🔵', cost: '$0.015', quality: '最高' },
    { id: 'kimi', name: 'Kimi K2 (推荐)', icon: '🌙', cost: '$0.006', quality: '高' },
    { id: 'gpt4', name: 'GPT-4', icon: '🟢', cost: '$0.030', quality: '高' },
    { id: 'gpt3.5', name: 'GPT-3.5 Turbo', icon: '🟡', cost: '$0.002', quality: '中' }
  ]

  // 快速操作按钮
  const quickActions = [
    { label: '🎨 生成AG-UI组件', action: '使用AG-UI系统生成智能UI组件' },
    { label: '📱 创建SmartUI布局', action: '创建响应式SmartUI布局设计' },
    { label: '🚀 创建React应用', action: '创建一个完整的React应用，包含路由和状态管理' },
    { label: '🐛 自动调试', action: '扫描并修复当前项目中的所有错误' },
    { label: '⚡ 性能优化', action: '分析并优化项目性能，提供详细报告' },
    { label: '🧪 生成测试', action: '为整个项目生成完整的测试套件' }
  ]

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 生成 AI 响应
  const generateAIResponse = (userInput) => {
    const input = userInput.toLowerCase()
    
    if (input.includes('ag-ui') || input.includes('agui')) {
      return '🎨 **AG-UI 智能组件生成**\n\n我可以帮您：\n• 生成智能UI组件\n• 创建自适应布局\n• 设计主题系统\n• 优化用户体验\n\n请告诉我您需要什么类型的组件？'
    }
    
    if (input.includes('smartui') || input.includes('响应式')) {
      return '📱 **SmartUI 响应式系统**\n\n我可以帮您：\n• 创建响应式布局\n• 适配多种设备\n• 优化移动端体验\n• 实现智能断点\n\n请描述您的布局需求！'
    }
    
    if (input.includes('hello') || input.includes('你好') || input.includes('hi')) {
      return '👋 你好！我是 PowerAutomation AI 助手，专门支持 AG-UI 和 SmartUI 功能。我可以帮助您进行智能UI设计、响应式布局和代码开发。'
    }
    
    if (input.includes('帮助') || input.includes('help') || input.includes('功能')) {
      return '🚀 **我的核心能力**:\n\n🎨 **AG-UI 智能生成**:\n• 自动生成UI组件\n• 智能布局设计\n• 多主题支持\n\n📱 **SmartUI 响应式**:\n• 智能设备适配\n• 自动布局调整\n• 跨设备兼容\n\n💻 **开发辅助**:\n• 代码生成和优化\n• 项目架构分析\n• 自动化测试\n\n请告诉我您需要什么帮助！'
    }
    
    return `🤖 我理解您的需求: "${userInput}"\n\n💡 **建议**: 我可以帮您使用 AG-UI 和 SmartUI 功能。例如：\n• "生成一个响应式导航栏"\n• "创建AG-UI仪表板组件"\n• "优化移动端布局"`
  }

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString(),
      model: currentModel
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // 模拟 AI 响应
      setTimeout(() => {
        const aiResponse = {
          id: Date.now() + 1,
          type: 'assistant',
          content: generateAIResponse(inputMessage),
          timestamp: new Date().toLocaleTimeString(),
          model: currentModel
        }
        setMessages(prev => [...prev, aiResponse])
        setIsLoading(false)
      }, 1000)
    } catch (error) {
      console.error('发送消息失败:', error)
      setIsLoading(false)
    }
  }

  // 按键处理
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // 快速操作处理
  const handleQuickAction = (action) => {
    setInputMessage(action)
    setTimeout(() => handleSendMessage(), 100)
  }

  return (
    <div className="ai-assistant">
      {/* 头部 */}
      <div className="ai-assistant-header">
        <h2>🤖 AI 助手 - AG-UI & SmartUI</h2>
        <div className="model-selector">
          <select 
            value={currentModel} 
            onChange={(e) => setCurrentModel(e.target.value)}
            className="model-select"
          >
            {availableModels.map(model => (
              <option key={model.id} value={model.id}>
                {model.icon} {model.name} ({model.cost})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 快速操作按钮 */}
      <div className="quick-actions">
        {quickActions.map((action, index) => (
          <button
            key={index}
            onClick={() => handleQuickAction(action.action)}
            className="quick-action-btn"
          >
            {action.label}
          </button>
        ))}
      </div>

      {/* 消息区域 */}
      <div className="messages-container">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              <div className="message-meta">
                <span className="timestamp">{message.timestamp}</span>
                <span className="model">{message.model}</span>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="loading">🤖 正在思考中...</div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题或需求... (支持 AG-UI 和 SmartUI 功能)"
            className="message-input"
            rows="3"
          />
          <button 
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="send-button"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </div>

      <style jsx>{`
        .ai-assistant {
          display: flex;
          flex-direction: column;
          height: 100%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .ai-assistant-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }

        .ai-assistant-header h2 {
          margin: 0;
          color: white;
          font-weight: 600;
        }

        .model-select {
          padding: 0.5rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 0.5rem;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          backdrop-filter: blur(10px);
        }

        .quick-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          padding: 1rem;
          background: rgba(255, 255, 255, 0.05);
        }

        .quick-action-btn {
          padding: 0.5rem 1rem;
          background: rgba(255, 255, 255, 0.2);
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 1rem;
          cursor: pointer;
          font-size: 0.9rem;
          transition: all 0.3s ease;
        }

        .quick-action-btn:hover {
          background: rgba(255, 255, 255, 0.3);
          transform: translateY(-2px);
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .message {
          display: flex;
          max-width: 80%;
        }

        .message.user {
          align-self: flex-end;
        }

        .message.assistant {
          align-self: flex-start;
        }

        .message-content {
          background: rgba(255, 255, 255, 0.1);
          padding: 1rem;
          border-radius: 1rem;
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .message.user .message-content {
          background: rgba(255, 255, 255, 0.2);
        }

        .message-text {
          white-space: pre-wrap;
          line-height: 1.5;
        }

        .message-meta {
          display: flex;
          justify-content: space-between;
          margin-top: 0.5rem;
          font-size: 0.75rem;
          opacity: 0.7;
        }

        .input-container {
          padding: 1rem;
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-top: 1px solid rgba(255, 255, 255, 0.2);
        }

        .input-wrapper {
          display: flex;
          gap: 0.5rem;
          align-items: flex-end;
        }

        .message-input {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 0.5rem;
          resize: none;
          font-family: inherit;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          backdrop-filter: blur(10px);
        }

        .message-input::placeholder {
          color: rgba(255, 255, 255, 0.7);
        }

        .send-button {
          padding: 0.75rem 1rem;
          background: rgba(255, 255, 255, 0.2);
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 0.5rem;
          cursor: pointer;
          font-size: 1.2rem;
          backdrop-filter: blur(10px);
          transition: all 0.3s ease;
        }

        .send-button:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .send-button:disabled {
          background: rgba(255, 255, 255, 0.1);
          cursor: not-allowed;
        }

        .loading {
          font-style: italic;
          opacity: 0.8;
        }
      `}</style>
    </div>
  )
}

export default AIAssistant

