import React, { useState, useEffect } from 'react'

const TaskList = () => {
  const [tasks, setTasks] = useState([])
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [showNewTaskForm, setShowNewTaskForm] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState({ isConnected: false })

  // 示例任务数据
  const sampleTasks = [
    {
      id: 'task_1',
      title: '🎨 AG-UI 组件生成测试',
      description: '测试 AG-UI 智能组件生成功能',
      priority: 'high',
      status: 'in-progress',
      assignedAgent: 'AG-UI Generator',
      estimatedTime: '30分钟',
      tags: ['AG-UI', 'UI生成', '测试'],
      subtasks: [
        { id: 'sub_1', title: '生成仪表板组件', completed: true },
        { id: 'sub_2', title: '生成表单组件', completed: false },
        { id: 'sub_3', title: '生成图表组件', completed: false }
      ],
      createdAt: new Date().toISOString(),
      deadline: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
      source: 'ag-ui'
    },
    {
      id: 'task_2',
      title: '📱 SmartUI 响应式布局优化',
      description: '优化 SmartUI 响应式布局系统',
      priority: 'medium',
      status: 'pending',
      assignedAgent: 'SmartUI Engine',
      estimatedTime: '45分钟',
      tags: ['SmartUI', '响应式', '布局'],
      subtasks: [
        { id: 'sub_4', title: '移动端适配', completed: false },
        { id: 'sub_5', title: '平板端优化', completed: false },
        { id: 'sub_6', title: '桌面端增强', completed: false }
      ],
      createdAt: new Date().toISOString(),
      deadline: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
      source: 'smartui'
    },
    {
      id: 'task_3',
      title: '🚀 PowerAutomation 集成测试',
      description: '测试 PowerAutomation v4.6.9.6 所有功能',
      priority: 'high',
      status: 'completed',
      assignedAgent: 'Test Manager',
      estimatedTime: '1小时',
      tags: ['测试', '集成', 'PowerAutomation'],
      subtasks: [
        { id: 'sub_7', title: 'MCP 组件测试', completed: true },
        { id: 'sub_8', title: 'UI 功能测试', completed: true },
        { id: 'sub_9', title: '性能测试', completed: true }
      ],
      createdAt: new Date().toISOString(),
      deadline: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
      source: 'system'
    }
  ]

  // 初始化任务
  useEffect(() => {
    setTasks(sampleTasks)
  }, [])

  // 创建新任务
  const createNewTask = async () => {
    if (!newTaskTitle.trim()) return

    const newTask = {
      id: `task_${Date.now()}`,
      title: newTaskTitle,
      description: '',
      priority: 'medium',
      status: 'pending',
      assignedAgent: null,
      estimatedTime: '1小时',
      tags: [],
      subtasks: [],
      createdAt: new Date().toISOString(),
      deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      source: 'local'
    }

    setTasks(prev => [newTask, ...prev])
    setNewTaskTitle('')
    setShowNewTaskForm(false)
  }

  // 更新任务状态
  const updateTaskStatus = (taskId, newStatus) => {
    setTasks(prev => prev.map(task => 
      task.id === taskId ? { ...task, status: newStatus } : task
    ))
  }

  // 删除任务
  const deleteTask = (taskId) => {
    setTasks(prev => prev.filter(task => task.id !== taskId))
  }

  // 获取状态颜色
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#4CAF50'
      case 'in-progress': return '#2196F3'
      case 'pending': return '#FF9800'
      case 'blocked': return '#F44336'
      default: return '#9E9E9E'
    }
  }

  // 获取优先级颜色
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#F44336'
      case 'medium': return '#FF9800'
      case 'low': return '#4CAF50'
      default: return '#9E9E9E'
    }
  }

  return (
    <div className="task-list">
      {/* 头部 */}
      <div className="task-list-header">
        <h2>📋 任务管理 - AG-UI & SmartUI</h2>
        <div className="header-actions">
          <div className="connection-status">
            <span className={`status-indicator ${connectionStatus.isConnected ? 'connected' : 'disconnected'}`}>
              {connectionStatus.isConnected ? '🟢 已连接' : '🔴 未连接'}
            </span>
          </div>
          <button 
            onClick={() => setShowNewTaskForm(true)}
            className="add-task-btn"
          >
            ➕ 新建任务
          </button>
        </div>
      </div>

      {/* 新建任务表单 */}
      {showNewTaskForm && (
        <div className="new-task-form">
          <div className="form-content">
            <h3>创建新任务</h3>
            <input
              type="text"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              placeholder="输入任务标题..."
              className="task-title-input"
              onKeyPress={(e) => e.key === 'Enter' && createNewTask()}
            />
            <div className="form-actions">
              <button onClick={createNewTask} className="create-btn">
                创建
              </button>
              <button 
                onClick={() => setShowNewTaskForm(false)} 
                className="cancel-btn"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 任务统计 */}
      <div className="task-stats">
        <div className="stat-item">
          <span className="stat-number">{tasks.length}</span>
          <span className="stat-label">总任务</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{tasks.filter(t => t.status === 'completed').length}</span>
          <span className="stat-label">已完成</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{tasks.filter(t => t.status === 'in-progress').length}</span>
          <span className="stat-label">进行中</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{tasks.filter(t => t.status === 'pending').length}</span>
          <span className="stat-label">待处理</span>
        </div>
      </div>

      {/* 任务列表 */}
      <div className="tasks-container">
        {tasks.map(task => (
          <div key={task.id} className="task-card">
            <div className="task-header">
              <h3 className="task-title">{task.title}</h3>
              <div className="task-actions">
                <select 
                  value={task.status} 
                  onChange={(e) => updateTaskStatus(task.id, e.target.value)}
                  className="status-select"
                >
                  <option value="pending">待处理</option>
                  <option value="in-progress">进行中</option>
                  <option value="completed">已完成</option>
                  <option value="blocked">阻塞</option>
                </select>
                <button 
                  onClick={() => deleteTask(task.id)}
                  className="delete-btn"
                >
                  🗑️
                </button>
              </div>
            </div>

            <div className="task-meta">
              <span 
                className="priority-badge"
                style={{ backgroundColor: getPriorityColor(task.priority) }}
              >
                {task.priority === 'high' ? '高' : task.priority === 'medium' ? '中' : '低'}优先级
              </span>
              <span 
                className="status-badge"
                style={{ backgroundColor: getStatusColor(task.status) }}
              >
                {task.status === 'completed' ? '已完成' : 
                 task.status === 'in-progress' ? '进行中' : 
                 task.status === 'pending' ? '待处理' : '阻塞'}
              </span>
              <span className="time-badge">⏱️ {task.estimatedTime}</span>
            </div>

            {task.description && (
              <p className="task-description">{task.description}</p>
            )}

            {task.tags.length > 0 && (
              <div className="task-tags">
                {task.tags.map((tag, index) => (
                  <span key={index} className="tag">#{tag}</span>
                ))}
              </div>
            )}

            {task.subtasks.length > 0 && (
              <div className="subtasks">
                <h4>子任务 ({task.subtasks.filter(st => st.completed).length}/{task.subtasks.length})</h4>
                {task.subtasks.map(subtask => (
                  <div key={subtask.id} className="subtask">
                    <span className={`subtask-status ${subtask.completed ? 'completed' : 'pending'}`}>
                      {subtask.completed ? '✅' : '⏳'}
                    </span>
                    <span className="subtask-title">{subtask.title}</span>
                  </div>
                ))}
              </div>
            )}

            <div className="task-footer">
              <span className="created-time">
                创建于: {new Date(task.createdAt).toLocaleString()}
              </span>
              {task.assignedAgent && (
                <span className="assigned-agent">
                  👤 {task.assignedAgent}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        .task-list {
          padding: 1rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
          color: white;
        }

        .task-list-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding: 1rem;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 1rem;
          backdrop-filter: blur(10px);
        }

        .task-list-header h2 {
          margin: 0;
          color: white;
        }

        .header-actions {
          display: flex;
          gap: 1rem;
          align-items: center;
        }

        .connection-status .status-indicator {
          padding: 0.5rem 1rem;
          border-radius: 0.5rem;
          font-size: 0.9rem;
          font-weight: 500;
        }

        .connection-status .connected {
          background: rgba(76, 175, 80, 0.2);
          border: 1px solid rgba(76, 175, 80, 0.5);
        }

        .connection-status .disconnected {
          background: rgba(244, 67, 54, 0.2);
          border: 1px solid rgba(244, 67, 54, 0.5);
        }

        .add-task-btn {
          padding: 0.75rem 1.5rem;
          background: rgba(255, 255, 255, 0.2);
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 0.5rem;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.3s ease;
        }

        .add-task-btn:hover {
          background: rgba(255, 255, 255, 0.3);
          transform: translateY(-2px);
        }

        .new-task-form {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }

        .form-content {
          background: rgba(255, 255, 255, 0.1);
          padding: 2rem;
          border-radius: 1rem;
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          min-width: 400px;
        }

        .form-content h3 {
          margin: 0 0 1rem 0;
          color: white;
        }

        .task-title-input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 0.5rem;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          font-size: 1rem;
          margin-bottom: 1rem;
        }

        .task-title-input::placeholder {
          color: rgba(255, 255, 255, 0.7);
        }

        .form-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
        }

        .create-btn, .cancel-btn {
          padding: 0.75rem 1.5rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 0.5rem;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.3s ease;
        }

        .create-btn {
          background: rgba(76, 175, 80, 0.3);
          color: white;
        }

        .cancel-btn {
          background: rgba(244, 67, 54, 0.3);
          color: white;
        }

        .task-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .stat-item {
          background: rgba(255, 255, 255, 0.1);
          padding: 1rem;
          border-radius: 0.5rem;
          text-align: center;
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .stat-number {
          display: block;
          font-size: 2rem;
          font-weight: bold;
          color: white;
        }

        .stat-label {
          font-size: 0.9rem;
          opacity: 0.8;
        }

        .tasks-container {
          display: grid;
          gap: 1rem;
        }

        .task-card {
          background: rgba(255, 255, 255, 0.1);
          padding: 1.5rem;
          border-radius: 1rem;
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          transition: all 0.3s ease;
        }

        .task-card:hover {
          transform: translateY(-2px);
          background: rgba(255, 255, 255, 0.15);
        }

        .task-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .task-title {
          margin: 0;
          color: white;
          font-size: 1.2rem;
        }

        .task-actions {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }

        .status-select {
          padding: 0.5rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 0.25rem;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          font-size: 0.9rem;
        }

        .delete-btn {
          padding: 0.5rem;
          background: rgba(244, 67, 54, 0.3);
          border: 1px solid rgba(244, 67, 54, 0.5);
          border-radius: 0.25rem;
          cursor: pointer;
          font-size: 1rem;
        }

        .task-meta {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
          flex-wrap: wrap;
        }

        .priority-badge, .status-badge, .time-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 1rem;
          font-size: 0.8rem;
          font-weight: 500;
          color: white;
        }

        .time-badge {
          background: rgba(255, 255, 255, 0.2);
        }

        .task-description {
          margin: 1rem 0;
          opacity: 0.9;
          line-height: 1.5;
        }

        .task-tags {
          display: flex;
          gap: 0.5rem;
          margin: 1rem 0;
          flex-wrap: wrap;
        }

        .tag {
          background: rgba(255, 255, 255, 0.2);
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.8rem;
          color: white;
        }

        .subtasks {
          margin: 1rem 0;
        }

        .subtasks h4 {
          margin: 0 0 0.5rem 0;
          font-size: 1rem;
          color: white;
        }

        .subtask {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin: 0.25rem 0;
        }

        .subtask-status.completed {
          opacity: 1;
        }

        .subtask-status.pending {
          opacity: 0.6;
        }

        .subtask-title {
          font-size: 0.9rem;
        }

        .task-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid rgba(255, 255, 255, 0.2);
          font-size: 0.8rem;
          opacity: 0.8;
        }

        .assigned-agent {
          font-weight: 500;
        }
      `}</style>
    </div>
  )
}

export default TaskList

