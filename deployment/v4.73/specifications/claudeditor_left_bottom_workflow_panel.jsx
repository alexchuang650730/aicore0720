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
  Divider
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
  DashboardOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;
const { Panel } = Collapse;

// 工作流圖標映射
const workflowIcons = {
  requirement_analysis: <FileSearchOutlined />,
  architecture_design: <CodeOutlined />,
  coding_implementation: <CodeOutlined />,
  testing_validation: <BugOutlined />,
  deployment_release: <CloudUploadOutlined />,
  monitoring_operations: <DashboardOutlined />
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

  // 六大工作流定義
  const workflows = [
    {
      key: 'requirement_analysis',
      title: '需求分析',
      description: '分析代碼提取需求',
      mcps: ['codeflow_mcp', 'stagewise_mcp'],
      estimatedTime: '10-15分鐘'
    },
    {
      key: 'architecture_design',
      title: '架構設計',
      description: '生成架構和UI設計',
      mcps: ['zen_mcp', 'smartui_mcp', 'stagewise_mcp'],
      estimatedTime: '15-20分鐘'
    },
    {
      key: 'coding_implementation',
      title: '編碼實現',
      description: '智能代碼生成',
      mcps: ['codeflow_mcp', 'zen_mcp', 'xmasters_mcp', 'smartui_mcp', 'ag_ui_mcp'],
      estimatedTime: '30-45分鐘'
    },
    {
      key: 'testing_validation',
      title: '測試驗證',
      description: '自動化測試執行',
      mcps: ['test_mcp', 'ag_ui_mcp', 'stagewise_mcp'],
      estimatedTime: '20-30分鐘'
    },
    {
      key: 'deployment_release',
      title: '部署發布',
      description: '一鍵部署上線',
      mcps: ['smartui_mcp', 'stagewise_mcp'],
      estimatedTime: '10-15分鐘'
    },
    {
      key: 'monitoring_operations',
      title: '監控運維',
      description: '實時監控優化',
      mcps: ['codeflow_mcp', 'xmasters_mcp', 'stagewise_mcp'],
      estimatedTime: '持續運行'
    }
  ];

  // 處理工作流啟動
  const handleStartWorkflow = (workflowKey) => {
    setActiveWorkflow(workflowKey);
    setWorkflowStatus('running');
    setCurrentStep(workflows.findIndex(w => w.key === workflowKey));
    setProgress(0);
    
    // 通知後端啟動工作流
    window.powerautomation?.startWorkflow(workflowKey);
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

  // 監聽工作流進度
  useEffect(() => {
    const handleWorkflowProgress = (event) => {
      const { workflow, progress, mcpStatus, cost } = event.detail;
      setProgress(progress);
      setMcpStatus(mcpStatus);
      setCostInfo(cost);
      
      if (progress === 100) {
        setWorkflowStatus('completed');
      }
    };

    window.addEventListener('workflow:progress', handleWorkflowProgress);
    return () => window.removeEventListener('workflow:progress', handleWorkflowProgress);
  }, []);

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
            onClick={() => handleStartWorkflow('requirement_analysis')}
            disabled={!!activeWorkflow}
          >
            快速開始
          </Button>
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