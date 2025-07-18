import React, { useState } from 'react';
import { 
  Layout, 
  Tabs, 
  Card, 
  Button, 
  Space, 
  Tag, 
  Badge, 
  Progress,
  List,
  Avatar,
  Tooltip,
  Divider,
  Typography,
  Steps,
  Switch,
  Select,
  Input
} from 'antd';
import {
  RobotOutlined,
  GithubOutlined,
  ThunderboltOutlined,
  RocketOutlined,
  CodeOutlined,
  EyeOutlined,
  MessageOutlined,
  BranchesOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  SettingOutlined
} from '@ant-design/icons';

const { Sider, Content } = Layout;
const { TabPane } = Tabs;
const { Text, Title } = Typography;
const { TextArea } = Input;

/**
 * ClaudeEditor 三欄式佈局設計
 * 左側：AI控制區 / GitHub狀態區 / 快速操作區 / 六大工作流區
 * 中間：演示區及編輯區
 * 右側：AI助手區
 */
export const ClaudeEditorLayout = () => {
  const [activeWorkflow, setActiveWorkflow] = useState(null);
  const [aiModel, setAiModel] = useState('auto');
  const [viewMode, setViewMode] = useState('split'); // split, preview, code

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 左側邊欄 - 260px */}
      <Sider width={260} style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
        <LeftSidebarContent 
          activeWorkflow={activeWorkflow}
          setActiveWorkflow={setActiveWorkflow}
          aiModel={aiModel}
          setAiModel={setAiModel}
        />
      </Sider>

      {/* 中間內容區 - 自適應 */}
      <Content style={{ background: '#f5f5f5' }}>
        <CenterContent viewMode={viewMode} setViewMode={setViewMode} />
      </Content>

      {/* 右側 AI 助手區 - 360px */}
      <Sider width={360} style={{ background: '#fff', borderLeft: '1px solid #f0f0f0' }}>
        <RightAIAssistant activeWorkflow={activeWorkflow} />
      </Sider>
    </Layout>
  );
};

/**
 * 左側邊欄內容
 */
const LeftSidebarContent = ({ activeWorkflow, setActiveWorkflow, aiModel, setAiModel }) => {
  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 1. AI 控制區 */}
      <Card 
        size="small" 
        title={
          <Space>
            <RobotOutlined style={{ color: '#1890ff' }} />
            <Text strong>AI 控制中心</Text>
          </Space>
        }
        style={{ margin: 8, marginBottom: 0 }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size={12}>
          {/* 模型選擇 */}
          <div>
            <Text type="secondary" style={{ fontSize: 12 }}>模型路由</Text>
            <Select
              value={aiModel}
              onChange={setAiModel}
              style={{ width: '100%', marginTop: 4 }}
              size="small"
            >
              <Select.Option value="auto">
                <Space>
                  <Badge status="processing" />
                  智能路由（推薦）
                </Space>
              </Select.Option>
              <Select.Option value="k2">
                <Space>
                  <Badge status="success" />
                  K2 模型（節省60-80%）
                </Space>
              </Select.Option>
              <Select.Option value="claude">
                <Space>
                  <Badge status="warning" />
                  Claude（高精度）
                </Space>
              </Select.Option>
            </Select>
          </div>

          {/* 成本監控 */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>當前成本</Text>
              <Text strong style={{ color: '#52c41a' }}>¥12.35</Text>
            </div>
            <Progress percent={35} size="small" showInfo={false} />
            <Text type="secondary" style={{ fontSize: 11 }}>
              相比 Claude 已節省 ¥23.65
            </Text>
          </div>

          {/* AI 設置 */}
          <Space>
            <Switch size="small" defaultChecked /> 
            <Text style={{ fontSize: 12 }}>自動優化提示詞</Text>
          </Space>
        </Space>
      </Card>

      {/* 2. GitHub 狀態區 */}
      <Card 
        size="small" 
        title={
          <Space>
            <GithubOutlined />
            <Text strong>GitHub 狀態</Text>
          </Space>
        }
        style={{ margin: 8, marginBottom: 0 }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size={8}>
          {/* 當前分支 */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Space size={4}>
              <BranchesOutlined style={{ fontSize: 12 }} />
              <Text style={{ fontSize: 12 }}>main</Text>
            </Space>
            <Tag color="green" style={{ fontSize: 11 }}>已同步</Tag>
          </div>

          {/* 更改統計 */}
          <div style={{ background: '#f5f5f5', padding: 8, borderRadius: 4 }}>
            <Space size={16}>
              <Text type="secondary" style={{ fontSize: 11 }}>
                <span style={{ color: '#52c41a' }}>+125</span> / 
                <span style={{ color: '#ff4d4f' }}> -45</span>
              </Text>
              <Text type="secondary" style={{ fontSize: 11 }}>
                5 files changed
              </Text>
            </Space>
          </div>

          {/* 快速操作 */}
          <Space size={8}>
            <Button size="small" icon={<SyncOutlined />}>拉取</Button>
            <Button size="small" type="primary" icon={<CheckCircleOutlined />}>提交</Button>
          </Space>
        </Space>
      </Card>

      {/* 3. 快速操作區 */}
      <Card 
        size="small" 
        title={
          <Space>
            <ThunderboltOutlined style={{ color: '#faad14' }} />
            <Text strong>快速操作</Text>
          </Space>
        }
        style={{ margin: 8, marginBottom: 0 }}
      >
        <Space wrap size={8}>
          <Button size="small" icon={<CodeOutlined />}>新建文件</Button>
          <Button size="small" icon={<SearchOutlined />}>全局搜索</Button>
          <Button size="small" icon={<TerminalOutlined />}>終端</Button>
          <Button size="small" icon={<SnippetsOutlined />}>代碼片段</Button>
          <Button size="small" icon={<FormatPainterOutlined />}>格式化</Button>
          <Button size="small" icon={<BugOutlined />}>調試</Button>
        </Space>
      </Card>

      {/* 4. 六大工作流區 */}
      <Card 
        size="small" 
        title={
          <Space>
            <RocketOutlined style={{ color: '#722ed1' }} />
            <Text strong>六大工作流</Text>
          </Space>
        }
        style={{ margin: 8, flex: 1, overflow: 'hidden' }}
        bodyStyle={{ padding: 8, height: 'calc(100% - 40px)', overflow: 'auto' }}
      >
        <SixWorkflowPanel 
          activeWorkflow={activeWorkflow}
          setActiveWorkflow={setActiveWorkflow}
        />
      </Card>
    </div>
  );
};

/**
 * 六大工作流面板組件
 */
const SixWorkflowPanel = ({ activeWorkflow, setActiveWorkflow }) => {
  const workflows = [
    {
      key: 'requirement',
      title: '需求分析',
      icon: <FileSearchOutlined />,
      color: '#1890ff',
      mcps: ['CodeFlow', 'Stagewise'],
      status: 'completed'
    },
    {
      key: 'architecture',
      title: '架構設計',
      icon: <ApartmentOutlined />,
      color: '#52c41a',
      mcps: ['Zen', 'SmartUI', 'Stagewise'],
      status: 'active'
    },
    {
      key: 'coding',
      title: '編碼實現',
      icon: <CodeOutlined />,
      color: '#722ed1',
      mcps: ['CodeFlow', 'Zen', 'XMasters'],
      status: 'pending'
    },
    {
      key: 'testing',
      title: '測試驗證',
      icon: <BugOutlined />,
      color: '#fa8c16',
      mcps: ['Test', 'AG-UI', 'Stagewise'],
      status: 'pending'
    },
    {
      key: 'deployment',
      title: '部署發布',
      icon: <CloudUploadOutlined />,
      color: '#13c2c2',
      mcps: ['SmartUI', 'Stagewise'],
      status: 'pending'
    },
    {
      key: 'monitoring',
      title: '監控運維',
      icon: <DashboardOutlined />,
      color: '#eb2f96',
      mcps: ['CodeFlow', 'XMasters'],
      status: 'pending'
    }
  ];

  const currentStep = workflows.findIndex(w => w.status === 'active');

  return (
    <Steps
      direction="vertical"
      size="small"
      current={currentStep}
      onChange={(index) => setActiveWorkflow(workflows[index].key)}
    >
      {workflows.map((workflow, index) => (
        <Steps.Step
          key={workflow.key}
          title={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Space size={8}>
                <span style={{ color: workflow.color }}>{workflow.icon}</span>
                <Text style={{ fontSize: 13 }}>{workflow.title}</Text>
              </Space>
              {workflow.status === 'active' && (
                <Badge status="processing" />
              )}
            </div>
          }
          description={
            <div style={{ marginTop: 4 }}>
              <Space size={4} wrap>
                {workflow.mcps.map(mcp => (
                  <Tag 
                    key={mcp} 
                    style={{ fontSize: 10, padding: '0 4px', margin: 0 }}
                    color={workflow.status === 'active' ? 'blue' : 'default'}
                  >
                    {mcp}
                  </Tag>
                ))}
              </Space>
              {workflow.status === 'active' && (
                <Progress 
                  percent={65} 
                  size="small" 
                  style={{ marginTop: 4 }}
                  strokeColor={workflow.color}
                />
              )}
            </div>
          }
          status={
            workflow.status === 'completed' ? 'finish' :
            workflow.status === 'active' ? 'process' :
            'wait'
          }
        />
      ))}
    </Steps>
  );
};

/**
 * 中間內容區
 */
const CenterContent = ({ viewMode, setViewMode }) => {
  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 頂部工具欄 */}
      <div style={{ 
        background: '#fff', 
        padding: '8px 16px', 
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Space>
          <Text strong>main.py</Text>
          <Tag color="green" style={{ fontSize: 11 }}>已保存</Tag>
        </Space>
        
        {/* 視圖切換 */}
        <Space>
          <Button.Group size="small">
            <Button 
              type={viewMode === 'code' ? 'primary' : 'default'}
              icon={<CodeOutlined />}
              onClick={() => setViewMode('code')}
            >
              代碼
            </Button>
            <Button 
              type={viewMode === 'split' ? 'primary' : 'default'}
              icon={<ColumnWidthOutlined />}
              onClick={() => setViewMode('split')}
            >
              分屏
            </Button>
            <Button 
              type={viewMode === 'preview' ? 'primary' : 'default'}
              icon={<EyeOutlined />}
              onClick={() => setViewMode('preview')}
            >
              預覽
            </Button>
          </Button.Group>
        </Space>
      </div>

      {/* 主內容區 */}
      <div style={{ flex: 1, display: 'flex', background: '#fff' }}>
        {viewMode !== 'preview' && (
          <div style={{ 
            flex: viewMode === 'split' ? 1 : undefined,
            width: viewMode === 'code' ? '100%' : undefined,
            borderRight: viewMode === 'split' ? '1px solid #f0f0f0' : 'none'
          }}>
            {/* Monaco Editor 區域 */}
            <div style={{ 
              height: '100%', 
              background: '#1e1e1e',
              color: '#d4d4d4',
              padding: 16,
              fontFamily: 'Consolas, Monaco, monospace',
              fontSize: 14,
              overflow: 'auto'
            }}>
              <pre>{`import asyncio
from typing import Dict, Any

class PowerAutomation:
    """PowerAutomation 主類"""
    
    def __init__(self):
        self.workflows = {}
        self.active_mcps = []
        
    async def execute_workflow(self, workflow_name: str):
        """執行指定的工作流"""
        print(f"執行工作流: {workflow_name}")
        # 實現代碼...`}</pre>
            </div>
          </div>
        )}
        
        {viewMode !== 'code' && (
          <div style={{ 
            flex: viewMode === 'split' ? 1 : undefined,
            width: viewMode === 'preview' ? '100%' : undefined,
            padding: 24,
            overflow: 'auto'
          }}>
            {/* 預覽/演示區 */}
            <Card title="工作流執行演示" size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Alert
                  message="工作流正在執行"
                  description="架構設計階段進行中，SmartUI MCP 正在生成 UI 組件..."
                  type="info"
                  showIcon
                />
                
                <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 8 }}>
                  <Text type="secondary">生成的 UI 組件預覽：</Text>
                  <div style={{ marginTop: 12 }}>
                    <Button type="primary" style={{ marginRight: 8 }}>主按鈕</Button>
                    <Button>次要按鈕</Button>
                  </div>
                </div>
              </Space>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * 右側 AI 助手
 */
const RightAIAssistant = ({ activeWorkflow }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '你好！我是 PowerAutomation AI 助手。我可以幫你完成六大工作流的任何任務。',
      time: '10:23'
    },
    {
      role: 'user',
      content: '幫我分析這個項目的架構',
      time: '10:24'
    },
    {
      role: 'assistant',
      content: '正在為您分析項目架構...\n\n發現以下關鍵組件：\n1. MCP 協調系統\n2. 工作流引擎\n3. AI 路由器\n\n建議使用微服務架構來優化系統性能。',
      time: '10:24',
      workflow: 'architecture'
    }
  ]);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* AI 助手頭部 */}
      <div style={{ 
        padding: '12px 16px', 
        borderBottom: '1px solid #f0f0f0',
        background: '#fafafa'
      }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <MessageOutlined style={{ fontSize: 18, color: '#1890ff' }} />
            <Title level={5} style={{ margin: 0 }}>AI 助手</Title>
          </Space>
          <Space>
            <Tag color="blue" style={{ margin: 0 }}>
              {activeWorkflow ? '工作流模式' : '對話模式'}
            </Tag>
            <Button 
              size="small" 
              type="text" 
              icon={<SettingOutlined />}
            />
          </Space>
        </Space>
      </div>

      {/* 消息列表 */}
      <div style={{ 
        flex: 1, 
        overflow: 'auto',
        padding: 16,
        background: '#f5f5f5'
      }}>
        <List
          dataSource={messages}
          renderItem={(message) => (
            <div style={{ 
              marginBottom: 16,
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <div style={{
                maxWidth: '80%',
                background: message.role === 'user' ? '#1890ff' : '#fff',
                color: message.role === 'user' ? '#fff' : '#000',
                padding: '8px 12px',
                borderRadius: 8,
                boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
              }}>
                {message.workflow && (
                  <Tag 
                    color="purple" 
                    style={{ fontSize: 10, marginBottom: 4 }}
                  >
                    {message.workflow}
                  </Tag>
                )}
                <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
                <Text 
                  type="secondary" 
                  style={{ 
                    fontSize: 11, 
                    marginTop: 4,
                    color: message.role === 'user' ? 'rgba(255,255,255,0.8)' : undefined
                  }}
                >
                  {message.time}
                </Text>
              </div>
            </div>
          )}
        />
      </div>

      {/* 輸入區 */}
      <div style={{ 
        padding: 16, 
        borderTop: '1px solid #f0f0f0',
        background: '#fff'
      }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            placeholder="輸入消息或命令..."
            autoSize={{ minRows: 1, maxRows: 4 }}
            style={{ resize: 'none' }}
          />
          <Button type="primary" icon={<SendOutlined />}>
            發送
          </Button>
        </Space.Compact>
        
        {/* 快捷命令 */}
        <Space wrap size={4} style={{ marginTop: 8 }}>
          <Tag 
            color="blue" 
            style={{ cursor: 'pointer', fontSize: 11 }}
            onClick={() => {}}
          >
            /analyze
          </Tag>
          <Tag 
            color="blue" 
            style={{ cursor: 'pointer', fontSize: 11 }}
            onClick={() => {}}
          >
            /refactor
          </Tag>
          <Tag 
            color="blue" 
            style={{ cursor: 'pointer', fontSize: 11 }}
            onClick={() => {}}
          >
            /test
          </Tag>
          <Tag 
            color="blue" 
            style={{ cursor: 'pointer', fontSize: 11 }}
            onClick={() => {}}
          >
            /deploy
          </Tag>
        </Space>
      </div>
    </div>
  );
};

// 導入必要的圖標（補充）
import {
  SearchOutlined,
  TerminalOutlined,
  SnippetsOutlined,
  FormatPainterOutlined,
  BugOutlined,
  FileSearchOutlined,
  ApartmentOutlined,
  CloudUploadOutlined,
  DashboardOutlined,
  ColumnWidthOutlined,
  SendOutlined,
  Alert
} from '@ant-design/icons';

export default ClaudeEditorLayout;