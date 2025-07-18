import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Progress, 
  Tag, 
  List, 
  Button, 
  Space, 
  Tooltip,
  Badge,
  Statistic,
  Row,
  Col,
  Typography,
  Divider,
  Alert
} from 'antd';
import {
  ThunderboltOutlined,
  CloudOutlined,
  DatabaseOutlined,
  ApiOutlined,
  DollarOutlined,
  ClockCircleOutlined,
  MemoryOutlined,
  RocketOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;

/**
 * MCP-Zero 狀態監控面板
 * 實時顯示動態 MCP 加載狀態和上下文使用情況
 */
export const MCPZeroStatusPanel = ({ style, onMcpLoad, onMcpUnload }) => {
  const [mcpStatus, setMcpStatus] = useState({
    loaded: [],
    available: [],
    contextUsage: { used: 0, total: 100000, percentage: 0 }
  });
  const [taskStatus, setTaskStatus] = useState(null);
  const [performance, setPerformance] = useState({
    avgLoadTime: 0,
    totalSaved: 0,
    efficiency: 0
  });
  const [isConnected, setIsConnected] = useState(false);

  // WebSocket 連接
  useEffect(() => {
    let ws = null;
    
    const connectWebSocket = () => {
      const clientId = `claudeditor_${Date.now()}`;
      ws = new WebSocket(`ws://localhost:8000/api/mcpzero/ws/${clientId}`);
      
      ws.onopen = () => {
        console.log('MCP-Zero WebSocket 連接成功');
        setIsConnected(true);
        ws.send(JSON.stringify({ type: 'ping' }));
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'task_progress') {
          setTaskStatus(data.progress);
        } else if (data.type === 'mcp_status') {
          setMcpStatus(data.status);
        }
      };
      
      ws.onclose = () => {
        console.log('MCP-Zero WebSocket 斷開');
        setIsConnected(false);
        // 重連
        setTimeout(connectWebSocket, 3000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket 錯誤:', error);
      };
    };
    
    connectWebSocket();
    
    // 定期獲取狀態
    const fetchStatus = async () => {
      try {
        // 獲取已加載的 MCP
        const loadedRes = await fetch('/api/mcpzero/mcps/loaded');
        const loadedData = await loadedRes.json();
        
        // 獲取所有可用的 MCP
        const availableRes = await fetch('/api/mcpzero/mcps');
        const availableData = await availableRes.json();
        
        setMcpStatus({
          loaded: loadedData.loaded_mcps || [],
          available: availableData.mcps || [],
          contextUsage: loadedData.context_usage || { used: 0, total: 100000, percentage: 0 }
        });
        
        // 計算性能指標
        const saved = loadedData.context_usage.total_context_size 
          ? (32000 - loadedData.context_usage.total_context_size) * 0.000002 * 8
          : 0;
        
        setPerformance({
          avgLoadTime: 0.5, // 模擬值
          totalSaved: saved,
          efficiency: 100 - loadedData.context_usage.percentage_of_max
        });
        
      } catch (error) {
        console.error('獲取 MCP 狀態失敗:', error);
      }
    };
    
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    
    return () => {
      if (ws) ws.close();
      clearInterval(interval);
    };
  }, []);

  // 手動加載 MCP
  const handleLoadMcp = async (mcpName) => {
    try {
      const response = await fetch('/api/mcpzero/mcps/load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mcp_name: mcpName })
      });
      
      if (response.ok) {
        onMcpLoad?.(mcpName);
      }
    } catch (error) {
      console.error('加載 MCP 失敗:', error);
    }
  };

  // 手動卸載 MCP
  const handleUnloadMcp = async (mcpName) => {
    try {
      const response = await fetch('/api/mcpzero/mcps/unload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mcp_name: mcpName })
      });
      
      if (response.ok) {
        onMcpUnload?.(mcpName);
      }
    } catch (error) {
      console.error('卸載 MCP 失敗:', error);
    }
  };

  return (
    <Card 
      title={
        <Space>
          <ThunderboltOutlined style={{ color: '#1890ff' }} />
          <span>MCP-Zero 動態監控</span>
          <Badge status={isConnected ? 'success' : 'error'} />
        </Space>
      }
      style={style}
      extra={
        <Space>
          <Tag color={performance.efficiency > 80 ? 'green' : 'orange'}>
            效率 {performance.efficiency.toFixed(1)}%
          </Tag>
        </Space>
      }
    >
      {/* 上下文使用情況 */}
      <div style={{ marginBottom: 20 }}>
        <Text strong>上下文使用率</Text>
        <Progress 
          percent={mcpStatus.contextUsage.percentage} 
          strokeColor={{
            '0%': '#87d068',
            '50%': '#ffe58f',
            '100%': '#ff4d4f',
          }}
          format={percent => (
            <span style={{ fontSize: 12 }}>
              {mcpStatus.contextUsage.used.toLocaleString()} / {mcpStatus.contextUsage.total.toLocaleString()}
            </span>
          )}
        />
      </div>

      {/* 性能指標 */}
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={8}>
          <Statistic
            title="平均加載時間"
            value={performance.avgLoadTime}
            precision={2}
            suffix="秒"
            prefix={<ClockCircleOutlined />}
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="節省成本"
            value={performance.totalSaved}
            precision={4}
            prefix="¥"
            valueStyle={{ color: '#3f8600' }}
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="已加載 MCP"
            value={mcpStatus.loaded.length}
            suffix={`/ ${mcpStatus.available.length}`}
            prefix={<ApiOutlined />}
          />
        </Col>
      </Row>

      <Divider />

      {/* 已加載的 MCP */}
      <div style={{ marginBottom: 20 }}>
        <Title level={5}>
          <MemoryOutlined /> 已加載的 MCP
        </Title>
        <List
          size="small"
          dataSource={mcpStatus.loaded}
          renderItem={mcp => {
            const mcpInfo = mcpStatus.available.find(a => a.name === mcp);
            return (
              <List.Item
                actions={[
                  <Tooltip title="卸載">
                    <Button 
                      size="small" 
                      danger
                      onClick={() => handleUnloadMcp(mcp)}
                    >
                      卸載
                    </Button>
                  </Tooltip>
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Tag color="blue">{mcp.replace('_mcp', '').toUpperCase()}</Tag>
                      {mcpInfo && (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {mcpInfo.context_size} tokens
                        </Text>
                      )}
                    </Space>
                  }
                  description={mcpInfo?.description}
                />
              </List.Item>
            );
          }}
        />
      </div>

      {/* 可用但未加載的 MCP */}
      {mcpStatus.available.length > mcpStatus.loaded.length && (
        <>
          <Divider />
          <div>
            <Title level={5}>
              <CloudOutlined /> 可用的 MCP
            </Title>
            <Space wrap>
              {mcpStatus.available
                .filter(mcp => !mcpStatus.loaded.includes(mcp.name))
                .map(mcp => (
                  <Tag
                    key={mcp.name}
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleLoadMcp(mcp.name)}
                  >
                    + {mcp.name.replace('_mcp', '')}
                  </Tag>
                ))}
            </Space>
          </div>
        </>
      )}

      {/* 當前任務狀態 */}
      {taskStatus && (
        <>
          <Divider />
          <Alert
            message="任務執行中"
            description={
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>任務 ID: {taskStatus.task_id}</Text>
                <Progress 
                  percent={taskStatus.progress} 
                  status="active"
                  size="small"
                />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  當前步驟: {taskStatus.current_step}
                </Text>
              </Space>
            }
            type="info"
            showIcon
            icon={<RocketOutlined />}
          />
        </>
      )}

      {/* 優化建議 */}
      {mcpStatus.contextUsage.percentage > 70 && (
        <Alert
          message="上下文使用率較高"
          description="建議卸載一些不常用的 MCP 以釋放上下文空間"
          type="warning"
          showIcon
          style={{ marginTop: 16 }}
        />
      )}
    </Card>
  );
};

export default MCPZeroStatusPanel;