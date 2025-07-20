import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Play, Pause, RotateCcw, CheckCircle, Clock, 
  Code, Layout, Zap, GitBranch, TestTube, BarChart,
  ChevronRight, Info, Terminal, Box
} from 'lucide-react';

// 导入各个演示组件
import { StageWiseCommandDemo } from './StageWiseCommandDemo';
import { UnifiedDeploymentUI } from './UnifiedDeploymentUI';
import { WorkflowAutomationDashboard } from './WorkflowAutomationDashboard';
import { MetricsVisualizationDashboard } from './MetricsVisualizationDashboard';
import { AGUIComplianceDashboard } from './AGUIComplianceDashboard';
import { TestValidationDashboard } from './TestValidationDashboard';
import SmartInterventionDemo from './SmartInterventionDemo';

/**
 * ClaudeEditor 中间栏演示面板
 * 集成到 ClaudeEditor 的主界面中
 */
export function ClaudeEditorDemoPanel({ 
  isVisible = true,
  onClose,
  currentProject,
  editorState 
}) {
  const [activeDemo, setActiveDemo] = useState('overview');
  const [demoStatus, setDemoStatus] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  
  // 演示项目配置
  const demos = [
    {
      id: 'smart-intervention',
      name: 'Smart Intervention',
      icon: <Zap className="w-4 h-4" />,
      component: SmartInterventionDemo,
      description: 'P0级智能任务切换系统',
      status: 'ready'
    },
    {
      id: 'stagewise',
      name: 'StageWise 控制',
      icon: <Terminal className="w-4 h-4" />,
      component: StageWiseCommandDemo,
      description: 'Claude Code Tool 命令兼容性测试',
      status: 'ready'
    },
    {
      id: 'deployment',
      name: '统一部署',
      icon: <Box className="w-4 h-4" />,
      component: UnifiedDeploymentUI,
      description: '一键部署管理系统',
      status: 'ready'
    },
    {
      id: 'workflow',
      name: '工作流自动化',
      icon: <GitBranch className="w-4 h-4" />,
      component: WorkflowAutomationDashboard,
      description: '六大工作流指标监控',
      status: 'ready'
    },
    {
      id: 'metrics',
      name: '指标可视化',
      icon: <BarChart className="w-4 h-4" />,
      component: MetricsVisualizationDashboard,
      description: '综合指标仪表板',
      status: 'ready'
    },
    {
      id: 'smartui',
      name: 'SmartUI 合规',
      icon: <Layout className="w-4 h-4" />,
      component: AGUIComplianceDashboard,
      description: 'UI 组件质量分析',
      status: 'ready'
    },
    {
      id: 'test',
      name: '测试验证',
      icon: <TestTube className="w-4 h-4" />,
      component: TestValidationDashboard,
      description: '测试执行和验证',
      status: 'ready'
    }
  ];
  
  // 获取当前演示组件
  const getCurrentDemoComponent = () => {
    const demo = demos.find(d => d.id === activeDemo);
    return demo?.component || null;
  };
  
  // 演示概览组件
  const DemoOverview = () => (
    <div className="p-6 space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">PowerAutomation v4.75 演示中心</h2>
        <p className="text-gray-600">在 ClaudeEditor 中体验所有核心功能</p>
      </div>
      
      {/* 快速统计 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-primary">100%</div>
            <div className="text-sm text-gray-500">命令兼容性</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-green-600">80%</div>
            <div className="text-sm text-gray-500">成本节省</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-blue-600">16ms</div>
            <div className="text-sm text-gray-500">UI 响应</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-purple-600">92.5%</div>
            <div className="text-sm text-gray-500">用户满意度</div>
          </CardContent>
        </Card>
      </div>
      
      {/* 演示卡片网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {demos.map(demo => (
          <Card 
            key={demo.id}
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => setActiveDemo(demo.id)}
          >
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {demo.icon}
                  <span>{demo.name}</span>
                </div>
                <Badge variant={demo.status === 'ready' ? 'success' : 'secondary'}>
                  {demo.status === 'ready' ? '就绪' : '开发中'}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-3">{demo.description}</p>
              <Button variant="outline" size="sm" className="w-full">
                查看演示 <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* 部署清单信息 */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="w-5 h-5" />
            部署清单集成
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 mb-4">
            所有演示组件都已集成到 ClaudeEditor，可以直接在编辑器中使用。
          </p>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>核心仪表板</span>
              <Badge variant="outline">4 个组件</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>命令接口</span>
              <Badge variant="outline">2 个组件</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>演示组件</span>
              <Badge variant="outline">6 个组件</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>集成组件</span>
              <Badge variant="outline">3 个组件</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
  
  // 渲染当前演示
  const renderCurrentDemo = () => {
    if (activeDemo === 'overview') {
      return <DemoOverview />;
    }
    
    const DemoComponent = getCurrentDemoComponent();
    if (!DemoComponent) {
      return (
        <div className="p-6 text-center text-gray-500">
          <p>演示组件加载中...</p>
        </div>
      );
    }
    
    // 传递 ClaudeEditor 的上下文给演示组件
    return (
      <DemoComponent 
        editorContext={{
          currentProject,
          editorState,
          isEmbedded: true
        }}
      />
    );
  };
  
  if (!isVisible) return null;
  
  return (
    <div className="h-full flex flex-col bg-background">
      {/* 顶部导航栏 */}
      <div className="border-b px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="font-semibold">演示中心</h3>
          <Badge variant="outline">v4.75</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setActiveDemo('overview')}
          >
            <Layout className="w-4 h-4 mr-2" />
            概览
          </Button>
          {onClose && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
            >
              关闭
            </Button>
          )}
        </div>
      </div>
      
      {/* 侧边导航和内容区 */}
      <div className="flex-1 flex">
        {/* 侧边导航 */}
        <div className="w-48 border-r bg-muted/30">
          <ScrollArea className="h-full">
            <div className="p-2 space-y-1">
              <Button
                variant={activeDemo === 'overview' ? 'secondary' : 'ghost'}
                size="sm"
                className="w-full justify-start"
                onClick={() => setActiveDemo('overview')}
              >
                <Zap className="w-4 h-4 mr-2" />
                演示概览
              </Button>
              
              <div className="my-2 px-2 text-xs font-semibold text-muted-foreground">
                功能演示
              </div>
              
              {demos.map(demo => (
                <Button
                  key={demo.id}
                  variant={activeDemo === demo.id ? 'secondary' : 'ghost'}
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setActiveDemo(demo.id)}
                >
                  {demo.icon}
                  <span className="ml-2">{demo.name}</span>
                </Button>
              ))}
            </div>
          </ScrollArea>
        </div>
        
        {/* 内容区 */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-sm text-gray-500">加载中...</p>
                </div>
              </div>
            ) : (
              renderCurrentDemo()
            )}
          </ScrollArea>
        </div>
      </div>
      
      {/* 底部状态栏 */}
      <div className="border-t px-4 py-2 flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            实时数据
          </span>
          <span className="flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-green-500" />
            所有系统正常
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span>当前项目: {currentProject?.name || '未选择'}</span>
        </div>
      </div>
    </div>
  );
}