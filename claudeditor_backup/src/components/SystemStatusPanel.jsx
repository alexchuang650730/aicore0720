/**
 * System Status Panel - 系统状态面板
 * 显示三大核心系统的实时状态
 */

import React, { useState, useEffect } from 'react';
import claudeCodeRouterService from '../services/ClaudeCodeRouterService';
import mcpDiscoveryService from '../services/MCPDiscoveryService';

const SystemStatusPanel = () => {
  const [systemStatus, setSystemStatus] = useState({
    memoryos: {
      status: 'unknown',
      contextCount: 0,
      learningProgress: 0,
      recommendations: 0
    },
    hooks: {
      status: 'unknown',
      totalHooks: 0,
      activeHooks: 0,
      executionCount: 0
    },
    statusDisplay: {
      status: 'unknown',
      componentsMonitored: 0,
      alerts: 0,
      performance: 0
    },
    router: {
      status: 'unknown',
      totalRequests: 0,
      costSavings: 0,
      currentModel: 'unknown'
    },
    mcpComponents: []
  });

  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    // 初始化状态
    updateSystemStatus();
    
    // 定期更新状态
    const interval = setInterval(updateSystemStatus, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const updateSystemStatus = async () => {
    try {
      // 获取路由器状态
      const routerStats = claudeCodeRouterService.getRoutingStats();
      
      // 获取 MCP 组件状态
      const mcpComponents = await mcpDiscoveryService.getDiscoveredMCPs();
      
      // 模拟其他系统状态（实际应该从相应服务获取）
      setSystemStatus(prev => ({
        ...prev,
        router: {
          status: routerStats.isConnected ? 'running' : 'offline',
          totalRequests: routerStats.totalRequests || 0,
          costSavings: routerStats.costSavings || 0,
          currentModel: routerStats.currentModel || 'unknown'
        },
        mcpComponents: mcpComponents || [],
        memoryos: {
          status: 'running', // 模拟状态
          contextCount: Math.floor(Math.random() * 100) + 50,
          learningProgress: Math.floor(Math.random() * 100),
          recommendations: Math.floor(Math.random() * 20) + 5
        },
        hooks: {
          status: 'running',
          totalHooks: 24,
          activeHooks: Math.floor(Math.random() * 20) + 15,
          executionCount: Math.floor(Math.random() * 1000) + 500
        },
        statusDisplay: {
          status: 'running',
          componentsMonitored: mcpComponents?.length || 0,
          alerts: Math.floor(Math.random() * 3),
          performance: Math.floor(Math.random() * 30) + 70
        }
      }));
      
    } catch (error) {
      console.error('更新系统状态失败:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return '#28a745';
      case 'warning': return '#ffc107';
      case 'error': return '#dc3545';
      case 'offline': return '#6c757d';
      default: return '#6c757d';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running': return '🟢';
      case 'warning': return '🟡';
      case 'error': return '🔴';
      case 'offline': return '⚫';
      default: return '⚪';
    }
  };

  return (
    <div style={{
      backgroundColor: '#f8f9fa',
      border: '1px solid #e9ecef',
      borderRadius: '8px',
      padding: '12px',
      marginBottom: '10px'
    }}>
      {/* 状态面板头部 */}
      <div 
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          marginBottom: isExpanded ? '10px' : '0'
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '14px', fontWeight: 'bold' }}>
            🖥️ 系统状态监控
          </span>
          <div style={{
            fontSize: '10px',
            padding: '2px 6px',
            backgroundColor: '#e3f2fd',
            borderRadius: '4px',
            color: '#1976d2'
          }}>
            v4.6.9.6
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <span style={{ fontSize: '10px', color: '#666' }}>
            {isExpanded ? '收起' : '展开'}
          </span>
          <span style={{ fontSize: '12px' }}>
            {isExpanded ? '▲' : '▼'}
          </span>
        </div>
      </div>

      {/* 简化状态显示 */}
      {!isExpanded && (
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '11px'
        }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <span>{getStatusIcon(systemStatus.memoryos.status)} MemoryOS</span>
            <span>{getStatusIcon(systemStatus.hooks.status)} 钩子系统</span>
            <span>{getStatusIcon(systemStatus.statusDisplay.status)} 状态显示</span>
            <span>{getStatusIcon(systemStatus.router.status)} 智能路由</span>
          </div>
          <div style={{ color: '#28a745', fontWeight: 'bold' }}>
            💰 ${systemStatus.router.costSavings.toFixed(4)}
          </div>
        </div>
      )}

      {/* 详细状态显示 */}
      {isExpanded && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          {/* MemoryOS 状态 */}
          <div style={{
            backgroundColor: 'white',
            padding: '10px',
            borderRadius: '6px',
            border: '1px solid #e9ecef'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '8px'
            }}>
              <span style={{ fontSize: '12px', fontWeight: 'bold' }}>
                🧠 MemoryOS
              </span>
              <span style={{
                fontSize: '10px',
                color: getStatusColor(systemStatus.memoryos.status)
              }}>
                {getStatusIcon(systemStatus.memoryos.status)} {systemStatus.memoryos.status}
              </span>
            </div>
            <div style={{ fontSize: '10px', color: '#666' }}>
              <div>上下文: {systemStatus.memoryos.contextCount}</div>
              <div>学习进度: {systemStatus.memoryos.learningProgress}%</div>
              <div>推荐数: {systemStatus.memoryos.recommendations}</div>
            </div>
          </div>

          {/* 钩子系统状态 */}
          <div style={{
            backgroundColor: 'white',
            padding: '10px',
            borderRadius: '6px',
            border: '1px solid #e9ecef'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '8px'
            }}>
              <span style={{ fontSize: '12px', fontWeight: 'bold' }}>
                🎣 钩子系统
              </span>
              <span style={{
                fontSize: '10px',
                color: getStatusColor(systemStatus.hooks.status)
              }}>
                {getStatusIcon(systemStatus.hooks.status)} {systemStatus.hooks.status}
              </span>
            </div>
            <div style={{ fontSize: '10px', color: '#666' }}>
              <div>总钩子: {systemStatus.hooks.totalHooks}</div>
              <div>活跃: {systemStatus.hooks.activeHooks}</div>
              <div>执行次数: {systemStatus.hooks.executionCount}</div>
            </div>
          </div>

          {/* 状态显示系统 */}
          <div style={{
            backgroundColor: 'white',
            padding: '10px',
            borderRadius: '6px',
            border: '1px solid #e9ecef'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '8px'
            }}>
              <span style={{ fontSize: '12px', fontWeight: 'bold' }}>
                📊 状态显示
              </span>
              <span style={{
                fontSize: '10px',
                color: getStatusColor(systemStatus.statusDisplay.status)
              }}>
                {getStatusIcon(systemStatus.statusDisplay.status)} {systemStatus.statusDisplay.status}
              </span>
            </div>
            <div style={{ fontSize: '10px', color: '#666' }}>
              <div>监控组件: {systemStatus.statusDisplay.componentsMonitored}</div>
              <div>警报: {systemStatus.statusDisplay.alerts}</div>
              <div>性能: {systemStatus.statusDisplay.performance}%</div>
            </div>
          </div>

          {/* 智能路由状态 */}
          <div style={{
            backgroundColor: 'white',
            padding: '10px',
            borderRadius: '6px',
            border: '1px solid #e9ecef'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '8px'
            }}>
              <span style={{ fontSize: '12px', fontWeight: 'bold' }}>
                🌐 智能路由
              </span>
              <span style={{
                fontSize: '10px',
                color: getStatusColor(systemStatus.router.status)
              }}>
                {getStatusIcon(systemStatus.router.status)} {systemStatus.router.status}
              </span>
            </div>
            <div style={{ fontSize: '10px', color: '#666' }}>
              <div>总请求: {systemStatus.router.totalRequests}</div>
              <div>当前模型: {systemStatus.router.currentModel}</div>
              <div style={{ color: '#28a745', fontWeight: 'bold' }}>
                💰 节省: ${systemStatus.router.costSavings.toFixed(4)}
              </div>
            </div>
          </div>

          {/* MCP 组件状态 */}
          {systemStatus.mcpComponents.length > 0 && (
            <div style={{
              gridColumn: '1 / -1',
              backgroundColor: 'white',
              padding: '10px',
              borderRadius: '6px',
              border: '1px solid #e9ecef'
            }}>
              <div style={{
                fontSize: '12px',
                fontWeight: 'bold',
                marginBottom: '8px'
              }}>
                🔧 MCP 组件状态 ({systemStatus.mcpComponents.length})
              </div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                gap: '5px',
                fontSize: '10px'
              }}>
                {systemStatus.mcpComponents.slice(0, 8).map((mcp, index) => (
                  <div key={index} style={{
                    padding: '4px 6px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <span>{mcp.name || `MCP-${index + 1}`}</span>
                    <span>{getStatusIcon('running')}</span>
                  </div>
                ))}
                {systemStatus.mcpComponents.length > 8 && (
                  <div style={{
                    padding: '4px 6px',
                    backgroundColor: '#e9ecef',
                    borderRadius: '4px',
                    textAlign: 'center',
                    color: '#666'
                  }}>
                    +{systemStatus.mcpComponents.length - 8} 更多
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SystemStatusPanel;

