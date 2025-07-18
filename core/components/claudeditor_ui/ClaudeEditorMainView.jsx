import React, { useState, useEffect } from 'react';
import { Layout, Card, Tabs, Button, Space, message } from 'antd';
import { CodeOutlined, RocketOutlined, SettingOutlined } from '@ant-design/icons';
import MonacoEditor from '@monaco-editor/react';

// 導入增強的組件
import { EnhancedLeftDashboard } from './EnhancedLeftDashboard';
import { CodeFlowPanel } from '../codeflow_mcp/frontend_integration_enhancement';
import { WorkflowBottomPanel } from '../../deployment/v4.73/specifications/claudeditor_left_bottom_workflow_panel';

const { Header, Content, Sider } = Layout;
const { TabPane } = Tabs;

/**
 * ClaudeEditor 主視圖組件
 * 整合 CodeFlow MCP 和六大工作流
 */
export const ClaudeEditorMainView = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState('editor');
  const [currentFile, setCurrentFile] = useState(null);
  const [editorContent, setEditorContent] = useState('');
  const [showCodeFlow, setShowCodeFlow] = useState(false);
  
  // 處理文件打開
  const handleFileOpen = (file) => {
    setCurrentFile(file);
    // 模擬加載文件內容
    setEditorContent(`// 文件: ${file.name}\n// 這是模擬的文件內容`);
    setActiveTab('editor');
  };
  
  // 處理工作流啟動
  const handleWorkflowStart = (workflow) => {
    message.info(`啟動工作流: ${workflow}`);
    // 根據工作流類型決定是否顯示 CodeFlow 面板
    if (['code_generation', 'ui_design', 'api_development'].includes(workflow)) {
      setShowCodeFlow(true);
      setActiveTab('codeflow');
    }
  };
  
  // 處理代碼生成完成
  const handleCodeGenerated = (result) => {
    if (result.code) {
      setEditorContent(result.code);
      setActiveTab('editor');
      message.success('代碼生成完成！');
    }
  };
  
  return (
    <Layout style={{ height: '100vh' }}>
      {/* 頂部標題欄 */}
      <Header style={{ 
        background: '#001529', 
        color: '#fff', 
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <CodeOutlined style={{ fontSize: 24 }} />
          <h1 style={{ margin: 0, fontSize: 20 }}>ClaudeEditor</h1>
          <span style={{ fontSize: 12, opacity: 0.7 }}>v4.73 - Powered by CodeFlow MCP</span>
        </div>
        <Space>
          <Button icon={<RocketOutlined />} type="primary">
            快速部署
          </Button>
          <Button icon={<SettingOutlined />}>
            設置
          </Button>
        </Space>
      </Header>
      
      <Layout>
        {/* 左側邊欄 - 增強版 Dashboard */}
        <Sider 
          width={260} 
          theme="light"
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          style={{ 
            background: '#fff',
            borderRight: '1px solid #f0f0f0',
            position: 'relative',
            paddingBottom: 280 // 為底部工作流面板留空間
          }}
        >
          <EnhancedLeftDashboard 
            onFileOpen={handleFileOpen}
            onWorkflowStart={handleWorkflowStart}
            collapsed={collapsed}
          />
          
          {/* 六大工作流面板 - 固定在左下角 */}
          <WorkflowBottomPanel />
        </Sider>
        
        {/* 中間主要內容區 */}
        <Content style={{ padding: 24, background: '#f0f2f5' }}>
          <Card 
            style={{ height: '100%' }}
            bodyStyle={{ padding: 0, height: '100%' }}
          >
            <Tabs 
              activeKey={activeTab} 
              onChange={setActiveTab}
              style={{ height: '100%' }}
              tabBarStyle={{ margin: 0, paddingLeft: 16 }}
            >
              <TabPane 
                tab={
                  <span>
                    <CodeOutlined />
                    編輯器
                  </span>
                } 
                key="editor"
              >
                <div style={{ height: 'calc(100vh - 200px)' }}>
                  <MonacoEditor
                    height="100%"
                    language="javascript"
                    theme="vs-light"
                    value={editorContent}
                    onChange={setEditorContent}
                    options={{
                      minimap: { enabled: true },
                      fontSize: 14,
                      wordWrap: 'on',
                      automaticLayout: true
                    }}
                  />
                </div>
              </TabPane>
              
              {showCodeFlow && (
                <TabPane 
                  tab={
                    <span>
                      <RocketOutlined />
                      CodeFlow 助手
                    </span>
                  } 
                  key="codeflow"
                >
                  <div style={{ height: 'calc(100vh - 200px)', overflow: 'auto' }}>
                    <CodeFlowPanel 
                      onWorkflowStart={handleWorkflowStart}
                      onCodeGenerated={handleCodeGenerated}
                    />
                  </div>
                </TabPane>
              )}
              
              <TabPane 
                tab={
                  <span>
                    <SettingOutlined />
                    演示預覽
                  </span>
                } 
                key="preview"
              >
                <div style={{ 
                  height: 'calc(100vh - 200px)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center' 
                }}>
                  <Card style={{ width: '80%', maxWidth: 800 }}>
                    <h2>演示預覽區</h2>
                    <p>在這裡可以預覽生成的組件和界面效果</p>
                    {currentFile && (
                      <div>
                        <h3>當前文件: {currentFile.name}</h3>
                        <div style={{ 
                          background: '#f5f5f5', 
                          padding: 16, 
                          borderRadius: 4,
                          marginTop: 16
                        }}>
                          <pre>{editorContent}</pre>
                        </div>
                      </div>
                    )}
                  </Card>
                </div>
              </TabPane>
            </Tabs>
          </Card>
        </Content>
        
        {/* 右側 AI 助手區（可選） */}
        <Sider 
          width={320} 
          theme="light"
          style={{ 
            background: '#fff',
            borderLeft: '1px solid #f0f0f0',
            padding: 16
          }}
        >
          <Card 
            title="AI 助手" 
            size="small"
            style={{ height: '100%' }}
          >
            <div style={{ padding: 16, textAlign: 'center', color: '#999' }}>
              <RocketOutlined style={{ fontSize: 48, marginBottom: 16 }} />
              <p>AI 助手正在待命</p>
              <p style={{ fontSize: 12 }}>
                選擇一個工作流或開始編碼，AI 將為您提供實時建議
              </p>
            </div>
          </Card>
        </Sider>
      </Layout>
    </Layout>
  );
};

// 樣式定義
export const claudeEditorStyles = `
.ant-layout-sider-trigger {
  bottom: 280px !important;
}

.ant-tabs-content {
  height: 100%;
}

.ant-tabs-tabpane {
  height: 100%;
}

/* 響應式調整 */
@media (max-width: 1200px) {
  .ant-layout-sider:last-child {
    display: none;
  }
}

/* 深色主題支持 */
@media (prefers-color-scheme: dark) {
  .ant-layout-header {
    background: #141414;
  }
  
  .ant-layout-sider {
    background: #1f1f1f;
  }
  
  .ant-card {
    background: #1f1f1f;
    color: #fff;
  }
}
`;

export default ClaudeEditorMainView;