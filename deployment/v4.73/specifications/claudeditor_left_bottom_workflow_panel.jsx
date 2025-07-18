import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Steps, 
  Button, 
  Badge, 
  Tooltip, 
  Progress,
  Space,
  Collapse,
  Typography,
  Tag,
  Divider,
  Spin,
  List
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  DollarOutlined,
  RocketOutlined,
  CodeOutlined,
  FileSearchOutlined,
  BugOutlined,
  CloudUploadOutlined,
  DashboardOutlined,
  ApiOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;
const { Panel } = Collapse;

// 工作流圖標映射
const workflowIcons = {
  goal_driven_development: <FileSearchOutlined />,
  intelligent_code_generation: <CodeOutlined />,
  automated_testing_validation: <BugOutlined />,
  continuous_quality_assurance: <DashboardOutlined />,
  smart_deployment_ops: <CloudUploadOutlined />,
  adaptive_learning_optimization: <SyncOutlined />
};

// MCP 狀態顏色映射
const mcpStatusColors = {
  active: '#52c41a',
  idle: '#d9d9d9',
  error: '#ff4d4f',
  loading: '#1890ff'
};

/**
 * ClaudeEditor 左下角工作流面板
 * 位置：三欄式佈局的左側底部
 * 功能：顯示和控制六大工作流
 */
export const WorkflowBottomPanel = () => {
  const [activeWorkflow, setActiveWorkflow] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [workflowStatus, setWorkflowStatus] = useState('idle'); // idle, running, paused, completed
  const [progress, setProgress] = useState(0);
  const [costInfo, setCostInfo] = useState({ current: 0, saved: 0 });
  const [mcpStatus, setMcpStatus] = useState({});
  const [collapsed, setCollapsed] = useState(false);
  const [loadedMcps, setLoadedMcps] = useState([]);
  const [contextUsage, setContextUsage] = useState({ used: 0, total: 100000, percentage: 0 });
  const [mcpZeroMode, setMcpZeroMode] = useState(true); // 默認使用 MCP-Zero 模式
  const [integrationStatus, setIntegrationStatus] = useState(null);
  const [mcpIntegrationLevel, setMcpIntegrationLevel] = useState({});

  // 六大工作流定義 - 更新為新的工作流系統
  const workflows = [
    {
      key: 'goal_driven_development',
      title: '目標驅動開發',
      description: '確保開發與用戶目標對齊',
      mcps: ['business_mcp', 'memoryos_mcp', 'claude_router_mcp'],
      estimatedTime: '全程跟蹤',
      integrationLevel: 100
    },
    {
      key: 'intelligent_code_generation',
      title: '智能代碼生成',
      description: '基於規格智能生成代碼',
      mcps: ['codeflow_mcp', 'smartui_mcp', 'claude_router_mcp', 'docs_mcp'],
      estimatedTime: '15-30分鐘',
      integrationLevel: 100
    },
    {
      key: 'automated_testing_validation',
      title: '自動化測試驗證',
      description: '全面的自動化測試',
      mcps: ['test_mcp', 'command_mcp', 'claude_router_mcp'],
      estimatedTime: '20-40分鐘',
      integrationLevel: 100
    },
    {
      key: 'continuous_quality_assurance',
      title: '持續質量保證',
      description: '持續監控和改進代碼質量',
      mcps: ['test_mcp', 'memoryos_mcp', 'claude_router_mcp'],
      estimatedTime: '持續運行',
      integrationLevel: 100
    },
    {
      key: 'smart_deployment_ops',
      title: '智能部署運維',
      description: '自動化部署和運維',
      mcps: ['command_mcp', 'business_mcp', 'claude_router_mcp'],
      estimatedTime: '10-20分鐘',
      integrationLevel: 100
    },
    {
      key: 'adaptive_learning_optimization',
      title: '自適應學習優化',
      description: '持續學習和優化系統',
      mcps: ['memoryos_mcp', 'business_mcp', 'docs_mcp', 'claude_router_mcp'],
      estimatedTime: '持續學習',
      integrationLevel: 100
    }
  ];

  // 處理工作流啟動 - MCP-Zero 模式
  const handleStartWorkflow = async (workflowKey) => {
    setActiveWorkflow(workflowKey);
    setWorkflowStatus('running');
    setCurrentStep(workflows.findIndex(w => w.key === workflowKey));
    setProgress(0);
    
    if (mcpZeroMode) {
      // 使用 MCP-Zero 動態加載
      try {
        const response = await fetch('/api/mcpzero/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            task: `執行${workflows.find(w => w.key === workflowKey).title}工作流`,
            options: {
              workflow_type: workflowKey,
              max_tokens: 30000
            }
          })
        });
        const result = await response.json();
        window.powerautomation?.startWorkflow(workflowKey, { task_id: result.task_id });
      } catch (error) {
        console.error('MCP-Zero 執行失敗:', error);
      }
    } else {
      // 傳統模式
      window.powerautomation?.startWorkflow(workflowKey);
    }
  };

  // 處理工作流控制
  const handlePauseResume = () => {
    if (workflowStatus === 'running') {
      setWorkflowStatus('paused');
      window.powerautomation?.pauseWorkflow();
    } else if (workflowStatus === 'paused') {
      setWorkflowStatus('running');
      window.powerautomation?.resumeWorkflow();
    }
  };

  // 監聽工作流進度和 MCP 狀態
  useEffect(() => {
    const handleWorkflowProgress = (event) => {
      const { workflow, progress, mcpStatus, cost, loaded_mcps, context_usage } = event.detail;
      setProgress(progress);
      setMcpStatus(mcpStatus);
      setCostInfo(cost);
      
      // MCP-Zero 模式下更新加載的 MCP 和上下文使用
      if (loaded_mcps) {
        setLoadedMcps(loaded_mcps);
      }
      if (context_usage) {
        setContextUsage(context_usage);
      }
      
      if (progress === 100) {
        setWorkflowStatus('completed');
      }
    };

    // 定期獲取 MCP-Zero 狀態和集成狀態
    const fetchMcpStatus = async () => {
      if (mcpZeroMode && activeWorkflow) {
        try {
          // 獲取 MCP-Zero 狀態
          const response = await fetch('/api/mcpzero/mcps/loaded');
          const data = await response.json();
          setLoadedMcps(data.loaded_mcps);
          setContextUsage({
            used: data.context_usage.total_context_size,
            total: 100000,
            percentage: data.context_usage.percentage_of_max
          });
          
          // 獲取集成狀態
          const integrationResponse = await fetch('/api/workflows/integration-status');
          const integrationData = await integrationResponse.json();
          setIntegrationStatus(integrationData);
          setMcpIntegrationLevel(integrationData.mcp_status || {});
        } catch (error) {
          console.error('獲取 MCP 狀態失敗:', error);
        }
      }
    };

    window.addEventListener('workflow:progress', handleWorkflowProgress);
    const interval = setInterval(fetchMcpStatus, 2000); // 每 2 秒更新一次
    
    return () => {
      window.removeEventListener('workflow:progress', handleWorkflowProgress);
      clearInterval(interval);
    };
  }, [mcpZeroMode, activeWorkflow]);

  // 渲染 MCP 狀態指示器
  const MCPStatusIndicator = ({ mcp, status = 'idle' }) => (
    <Tooltip title={`${mcp}: ${status}`}>
      <Badge 
        dot 
        status={status === 'active' ? 'success' : status === 'error' ? 'error' : 'default'}
        style={{ marginRight: 8 }}
      >
        <Tag 
          color={status === 'active' ? 'green' : status === 'error' ? 'red' : 'default'}
          style={{ fontSize: 11 }}
        >
          {mcp.replace('_mcp', '').toUpperCase()}
        </Tag>
      </Badge>
    </Tooltip>
  );

  // 渲染緊湊模式（摺疊時）
  if (collapsed) {
    return (
      <div className="workflow-panel-collapsed" style={{ 
        position: 'fixed',
        bottom: 0,
        left: 0,
        width: 260,
        background: '#fff',
        borderTop: '1px solid #f0f0f0',
        borderRight: '1px solid #f0f0f0',
        padding: '8px 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        cursor: 'pointer'
      }} onClick={() => setCollapsed(false)}>
        <Space>
          <RocketOutlined style={{ fontSize: 16, color: '#1890ff' }} />
          <Text strong>工作流</Text>
          {activeWorkflow && (
            <Badge status={workflowStatus === 'running' ? 'processing' : 'default'} />
          )}
        </Space>
        <Text type="secondary" style={{ fontSize: 12 }}>
          {activeWorkflow ? `${progress}%` : '點擊展開'}
        </Text>
      </div>
    );
  }

  // 渲染完整面板
  return (
    <div className="workflow-bottom-panel" style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      width: 260,
      maxHeight: '50vh',
      background: '#fff',
      borderTop: '1px solid #f0f0f0',
      borderRight: '1px solid #f0f0f0',
      display: 'flex',
      flexDirection: 'column',
      boxShadow: '0 -2px 8px rgba(0,0,0,0.08)'
    }}>
      {/* 面板頭部 */}
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Space>
          <RocketOutlined style={{ fontSize: 18, color: '#1890ff' }} />
          <Title level={5} style={{ margin: 0 }}>六大工作流</Title>
          {mcpZeroMode && (
            <Tag icon={<ThunderboltOutlined />} color="blue">
              MCP-Zero
            </Tag>
          )}
          {integrationStatus && (
            <Tooltip title={`P1 MCP 集成度: ${integrationStatus.overall_integration_percentage || '0%'}`}>
              <Tag color={integrationStatus.integration_complete ? 'green' : 'orange'}>
                {integrationStatus.overall_integration_percentage || '0%'}
              </Tag>
            </Tooltip>
          )}
        </Space>
        <Space>
          {/* 成本顯示 */}
          <Tooltip title={`已節省 ¥${costInfo.saved.toFixed(2)}`}>
            <Tag icon={<DollarOutlined />} color="green">
              ¥{costInfo.current.toFixed(2)}
            </Tag>
          </Tooltip>
          <Button 
            type="text" 
            size="small" 
            onClick={() => setCollapsed(true)}
            style={{ fontSize: 12 }}
          >
            收起
          </Button>
        </Space>
      </div>

      {/* 當前工作流狀態 */}
      {activeWorkflow && (
        <div style={{ padding: '12px 16px', background: '#fafafa' }}>
          <Space direction="vertical" style={{ width: '100%' }} size={8}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Text strong>{workflows[currentStep].title}</Text>
              <Space>
                <Button
                  size="small"
                  icon={workflowStatus === 'running' ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                  onClick={handlePauseResume}
                  disabled={workflowStatus === 'completed'}
                >
                  {workflowStatus === 'running' ? '暫停' : '繼續'}
                </Button>
              </Space>
            </div>
            <Progress 
              percent={progress} 
              size="small" 
              status={workflowStatus === 'completed' ? 'success' : 'active'}
            />
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {workflows[currentStep].mcps.map(mcp => (
                <MCPStatusIndicator 
                  key={mcp} 
                  mcp={mcp} 
                  status={mcpStatus[mcp] || 'idle'} 
                />
              ))}
            </div>
          </Space>
        </div>
      )}

      {/* MCP-Zero 狀態顯示 */}
      {mcpZeroMode && activeWorkflow && (
        <div style={{ 
          padding: '8px 16px', 
          background: '#e6f7ff',
          borderBottom: '1px solid #91d5ff'
        }}>
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text style={{ fontSize: 12 }}>上下文使用</Text>
              <Text type="secondary" style={{ fontSize: 11 }}>
                {contextUsage.used.toLocaleString()} / {contextUsage.total.toLocaleString()} tokens
              </Text>
            </div>
            <Progress 
              percent={contextUsage.percentage} 
              size="small" 
              strokeColor={contextUsage.percentage > 80 ? '#ff4d4f' : '#1890ff'}
              showInfo={false}
            />
            <div style={{ marginTop: 4 }}>
              <Text style={{ fontSize: 11, fontWeight: 'bold' }}>動態加載的 MCP:</Text>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                {loadedMcps.map(mcp => (
                  <Tag key={mcp} size="small" color="processing">
                    {mcp.replace('_mcp', '')}
                  </Tag>
                ))}
              </div>
            </div>
          </Space>
        </div>
      )}
      
      {/* 工作流列表 */}
      <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
        <Steps
          direction="vertical"
          size="small"
          current={currentStep}
          style={{ marginTop: 8 }}
        >
          {workflows.map((workflow, index) => (
            <Steps.Step
              key={workflow.key}
              title={
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Space size={4}>
                    {workflowIcons[workflow.key]}
                    <Text style={{ fontSize: 13 }}>{workflow.title}</Text>
                    {workflow.integrationLevel && (
                      <Tag color="green" style={{ fontSize: 10 }}>
                        {workflow.integrationLevel}%
                      </Tag>
                    )}
                  </Space>
                  {!activeWorkflow && (
                    <Button
                      size="small"
                      type="link"
                      onClick={() => handleStartWorkflow(workflow.key)}
                      style={{ fontSize: 12, padding: '0 4px' }}
                    >
                      啟動
                    </Button>
                  )}
                </div>
              }
              description={
                <div style={{ marginTop: 4 }}>
                  <Text type="secondary" style={{ fontSize: 11 }}>
                    {workflow.description}
                  </Text>
                  <div style={{ marginTop: 4 }}>
                    <Text type="secondary" style={{ fontSize: 10 }}>
                      預計: {workflow.estimatedTime}
                    </Text>
                  </div>
                  <div style={{ marginTop: 4, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                    {workflow.mcps.map(mcp => (
                      <Tag 
                        key={mcp} 
                        style={{ fontSize: 9, padding: '0 4px', margin: 0 }}
                        color={mcpIntegrationLevel[mcp]?.status === 'active' ? 'success' : 'default'}
                      >
                        {mcp.replace('_mcp', '').substring(0, 3).toUpperCase()}
                      </Tag>
                    ))}
                  </div>
                </div>
              }
              status={
                index < currentStep ? 'finish' : 
                index === currentStep && workflowStatus === 'running' ? 'process' :
                index === currentStep && workflowStatus === 'completed' ? 'finish' :
                'wait'
              }
            />
          ))}
        </Steps>
      </div>

      {/* 快捷操作 */}
      <div style={{ 
        padding: '8px 16px', 
        borderTop: '1px solid #f0f0f0',
        background: '#fafafa' 
      }}>
        <Space size={8}>
          <Button
            size="small"
            type={activeWorkflow ? 'default' : 'primary'}
            icon={<RocketOutlined />}
            onClick={() => handleStartWorkflow('goal_driven_development')}
            disabled={!!activeWorkflow}
          >
            快速開始
          </Button>
          <Tooltip title={mcpZeroMode ? '切換到傳統模式' : '切換到 MCP-Zero 模式'}>
            <Button
              size="small"
              icon={<ApiOutlined />}
              onClick={() => setMcpZeroMode(!mcpZeroMode)}
              type={mcpZeroMode ? 'primary' : 'default'}
            >
              {mcpZeroMode ? 'Zero' : '傳統'}
            </Button>
          </Tooltip>
          <Button
            size="small"
            icon={<SyncOutlined />}
            onClick={() => window.location.reload()}
          >
            重置
          </Button>
        </Space>
      </div>
    </div>
  );
};

// 導出樣式
export const workflowPanelStyles = `
.workflow-bottom-panel {
  transition: all 0.3s ease;
}

.workflow-panel-collapsed {
  transition: all 0.3s ease;
}

.workflow-bottom-panel:hover {
  box-shadow: 0 -4px 12px rgba(0,0,0,0.12);
}

/* 響應式適配 */
@media (max-height: 768px) {
  .workflow-bottom-panel {
    max-height: 40vh;
  }
}

/* 暗色主題支持 */
@media (prefers-color-scheme: dark) {
  .workflow-bottom-panel,
  .workflow-panel-collapsed {
    background: #141414;
    border-color: #303030;
  }
}
`;