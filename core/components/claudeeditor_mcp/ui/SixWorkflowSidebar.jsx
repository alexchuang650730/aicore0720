import React, { useState, useEffect } from 'react';
import { 
  ChevronDown, 
  ChevronRight,
  Search,
  Building2,
  PaintBucket,
  Code,
  TestTube,
  Rocket,
  Activity,
  Circle,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react';

/**
 * ClaudeEditor 左邊欄六大工作流折疊組件
 * 位於左側邊欄最下方，可折疊展開
 */
export function SixWorkflowSidebar({ className = "" }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [workflowStatus, setWorkflowStatus] = useState({});
  const [activeMCPs, setActiveMCPs] = useState(new Set());

  // 六大工作流配置
  const workflows = [
    {
      id: 'requirement_analysis',
      name: '需求分析',
      icon: <Search className="w-4 h-4" />,
      color: 'text-blue-500',
      mcps: [
        { name: 'Business MCP', status: 'active', priority: 'P1' },
        { name: 'Claude Router MCP', status: 'active', priority: 'P1' },
        { name: 'MemoryOS MCP', status: 'active', priority: 'P1' },
        { name: 'DeepSWE MCP', status: 'idle', priority: 'P1' }
      ]
    },
    {
      id: 'architecture_design',
      name: '架構設計',
      icon: <Building2 className="w-4 h-4" />,
      color: 'text-purple-500',
      mcps: [
        { name: 'SmartUI MCP', status: 'active', priority: 'P0' },
        { name: 'AG-UI MCP', status: 'active', priority: 'P0' },
        { name: 'CodeFlow MCP', status: 'active', priority: 'P0' },
        { name: 'MemoryRAG MCP', status: 'idle', priority: 'P0' }
      ]
    },
    {
      id: 'coding_implementation',
      name: '編碼實現',
      icon: <Code className="w-4 h-4" />,
      color: 'text-green-500',
      mcps: [
        { name: 'CodeFlow MCP', status: 'active', priority: 'P0' },
        { name: 'SmartTool MCP', status: 'active', priority: 'P1' },
        { name: 'Local Adapter MCP', status: 'active', priority: 'P2' },
        { name: 'X-Masters MCP', status: 'idle', priority: 'P2' }
      ]
    },
    {
      id: 'testing_validation',
      name: '測試驗證',
      icon: <TestTube className="w-4 h-4" />,
      color: 'text-orange-500',
      mcps: [
        { name: 'Test MCP', status: 'active', priority: 'P0' },
        { name: 'StageWise MCP', status: 'active', priority: 'P1' },
        { name: 'Command MCP', status: 'active', priority: 'P2' },
        { name: 'Smart Intervention MCP', status: 'idle', priority: 'P0' }
      ]
    },
    {
      id: 'deployment_release',
      name: '部署發布',
      icon: <Rocket className="w-4 h-4" />,
      color: 'text-red-500',
      mcps: [
        { name: 'AWS Bedrock MCP', status: 'active', priority: 'P1' },
        { name: 'Command MCP', status: 'active', priority: 'P2' },
        { name: 'MCP Coordinator MCP', status: 'active', priority: 'P2' },
        { name: 'Zen MCP', status: 'idle', priority: 'P2' }
      ]
    },
    {
      id: 'monitoring_operations',
      name: '監控運維',
      icon: <Activity className="w-4 h-4" />,
      color: 'text-indigo-500',
      mcps: [
        { name: 'Operations MCP', status: 'active', priority: 'P2' },
        { name: 'Smart Intervention MCP', status: 'active', priority: 'P0' },
        { name: 'MemoryOS MCP', status: 'active', priority: 'P1' },
        { name: 'Claude Router MCP', status: 'idle', priority: 'P1' }
      ]
    }
  ];

  // MCP 狀態圖標
  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-3 h-3 text-green-500" />;
      case 'idle':
        return <Circle className="w-3 h-3 text-gray-400" />;
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-500" />;
      default:
        return <Clock className="w-3 h-3 text-yellow-500" />;
    }
  };

  // 優先級標籤顏色
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'P0':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'P1':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'P2':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // 計算工作流狀態
  const getWorkflowStatus = (workflow) => {
    const activeMCPs = workflow.mcps.filter(mcp => mcp.status === 'active').length;
    const totalMCPs = workflow.mcps.length;
    const percentage = (activeMCPs / totalMCPs) * 100;
    
    if (percentage === 100) return 'active';
    if (percentage >= 50) return 'partial';
    return 'idle';
  };

  useEffect(() => {
    // 模擬實時更新 MCP 狀態
    const interval = setInterval(() => {
      const newActiveMCPs = new Set();
      workflows.forEach(workflow => {
        workflow.mcps.forEach(mcp => {
          if (mcp.status === 'active') {
            newActiveMCPs.add(mcp.name);
          }
        });
      });
      setActiveMCPs(newActiveMCPs);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className={`border-t bg-white ${className}`}>
      {/* 折疊標題 */}
      <div 
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          {isExpanded ? 
            <ChevronDown className="w-4 h-4 text-gray-500" /> : 
            <ChevronRight className="w-4 h-4 text-gray-500" />
          }
          <span className="text-sm font-medium text-gray-700">六大工作流</span>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-500">{activeMCPs.size}/19</span>
          </div>
        </div>
        
        {/* 快速狀態指示器 */}
        <div className="flex gap-1">
          {workflows.map((workflow, index) => {
            const status = getWorkflowStatus(workflow);
            return (
              <div
                key={workflow.id}
                className={`w-2 h-2 rounded-full ${
                  status === 'active' ? 'bg-green-500' :
                  status === 'partial' ? 'bg-yellow-500' : 'bg-gray-300'
                }`}
                title={workflow.name}
              />
            );
          })}
        </div>
      </div>

      {/* 展開內容 */}
      {isExpanded && (
        <div className="border-t bg-gray-50">
          <div className="p-2 space-y-1 max-h-96 overflow-y-auto">
            {workflows.map(workflow => {
              const workflowStatus = getWorkflowStatus(workflow);
              const activeMCPCount = workflow.mcps.filter(mcp => mcp.status === 'active').length;
              
              return (
                <div key={workflow.id} className="space-y-1">
                  {/* 工作流標題 */}
                  <div className="flex items-center justify-between py-1">
                    <div className="flex items-center gap-2">
                      <div className={workflow.color}>
                        {workflow.icon}
                      </div>
                      <span className="text-sm font-medium text-gray-800">
                        {workflow.name}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-gray-500">
                        {activeMCPCount}/{workflow.mcps.length}
                      </span>
                      {getStatusIcon(workflowStatus)}
                    </div>
                  </div>
                  
                  {/* MCP 列表 */}
                  <div className="ml-6 space-y-1">
                    {workflow.mcps.map(mcp => (
                      <div 
                        key={mcp.name}
                        className="flex items-center justify-between py-1 px-2 rounded hover:bg-white transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          {getStatusIcon(mcp.status)}
                          <span className="text-xs text-gray-600 truncate">
                            {mcp.name}
                          </span>
                        </div>
                        <span className={`text-xs px-1 py-0.5 rounded border ${getPriorityColor(mcp.priority)}`}>
                          {mcp.priority}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
          
          {/* 統計信息 */}
          <div className="border-t p-2 bg-white">
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <div className="text-xs font-medium text-gray-800">總計</div>
                <div className="text-sm text-gray-600">19 MCP</div>
              </div>
              <div>
                <div className="text-xs font-medium text-green-600">活躍</div>
                <div className="text-sm text-green-600">{activeMCPs.size}</div>
              </div>
              <div>
                <div className="text-xs font-medium text-blue-600">工作流</div>
                <div className="text-sm text-blue-600">
                  {workflows.filter(w => getWorkflowStatus(w) === 'active').length}/6
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SixWorkflowSidebar;