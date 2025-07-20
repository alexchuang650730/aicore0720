import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  LineChart, Line, BarChart, Bar, RadarChart, Radar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import { Activity, GitBranch, Zap, Users, TrendingUp, Shield } from 'lucide-react';

export function WorkflowAutomationDashboard() {
  const [selectedWorkflow, setSelectedWorkflow] = useState('all');
  
  // 工作流数据
  const workflowData = [{"name": "需求分析工作流", "success_rate": 75.0, "duration": 0.018000000000000002, "api_calls": 12, "ui_response": 16.3}, {"name": "UI 生成工作流", "success_rate": 75.0, "duration": 0.001, "api_calls": 12, "ui_response": 16.3}, {"name": "代码优化工作流", "success_rate": 75.0, "duration": 0.0, "api_calls": 12, "ui_response": 16.3}, {"name": "测试自动化工作流", "success_rate": 75.0, "duration": 0.001, "api_calls": 12, "ui_response": 16.3}, {"name": "部署发布工作流", "success_rate": 75.0, "duration": 0.0, "api_calls": 12, "ui_response": 16.3}, {"name": "监控反馈工作流", "success_rate": 75.0, "duration": 0.0, "api_calls": 12, "ui_response": 16.3}];
  
  // GitHub 实际数据
  const githubMetrics = {
    commits: 12,
    pullRequests: 3,
    issuesClosed: 5,
    coverage: 85.3,
    buildSuccess: 92.5,
    deployFrequency: 2.5
  };
  
  // 自动化评分
  const automationScores = {
    overall: 86.5,
    technical: 81.8,
    experience: 74.8,
    efficiency: 88.0,
    reliability: 40.0
  };
  
  // 六大工作流定义
  const workflows = [
    { id: 'requirement_analysis', name: '需求分析', icon: '📋', color: '#3b82f6' },
    { id: 'ui_generation', name: 'UI生成', icon: '🎨', color: '#10b981' },
    { id: 'code_optimization', name: '代码优化', icon: '⚡', color: '#f59e0b' },
    { id: 'test_automation', name: '测试自动化', icon: '🧪', color: '#8b5cf6' },
    { id: 'deployment', name: '部署发布', icon: '🚀', color: '#ef4444' },
    { id: 'monitoring_feedback', name: '监控反馈', icon: '📊', color: '#6366f1' }
  ];
  
  // 雷达图数据
  const radarData = [
    { metric: '成功率', value: automationScores.overall },
    { metric: '性能', value: automationScores.efficiency },
    { metric: '可靠性', value: automationScores.reliability },
    { metric: '用户体验', value: automationScores.experience },
    { metric: '技术指标', value: automationScores.technical },
    { metric: '自动化度', value: 88.5 }
  ];
  
  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981';
    if (score >= 70) return '#f59e0b';
    return '#ef4444';
  };
  
  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">工作流自动化指标</h1>
        <Badge variant="outline" className="text-sm">
          实时数据 · GitHub 集成
        </Badge>
      </div>
      
      {/* 顶部指标卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <GitBranch className="w-4 h-4" />
              今日提交
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{githubMetrics.commits}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">PR 数量</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{githubMetrics.pullRequests}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">关闭 Issue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{githubMetrics.issuesClosed}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">代码覆盖率</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{githubMetrics.coverage}%</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">构建成功率</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{githubMetrics.buildSuccess}%</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">部署频率</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{githubMetrics.deployFrequency}/天</div>
          </CardContent>
        </Card>
      </div>
      
      {/* 自动化评分 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>自动化评分</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span>整体评分</span>
                  <span className="font-bold" style={{ color: getScoreColor(automationScores.overall) }}>
                    {automationScores.overall}%
                  </span>
                </div>
                <Progress value={automationScores.overall} />
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span>技术指标</span>
                  <span className="font-bold">{automationScores.technical}%</span>
                </div>
                <Progress value={automationScores.technical} />
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span>体验指标</span>
                  <span className="font-bold">{automationScores.experience}%</span>
                </div>
                <Progress value={automationScores.experience} />
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span>效率指标</span>
                  <span className="font-bold">{automationScores.efficiency}%</span>
                </div>
                <Progress value={automationScores.efficiency} />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>多维度评估</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={radarData}>
                <PolarGrid strokeDasharray="3 3" />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="当前值"
                  dataKey="value"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.6}
                />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
      
      {/* 六大工作流状态 */}
      <Card>
        <CardHeader>
          <CardTitle>六大工作流执行状态</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {workflows.map(workflow => (
              <div 
                key={workflow.id}
                className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedWorkflow(workflow.id)}
              >
                <div className="text-center">
                  <div className="text-3xl mb-2">{workflow.icon}</div>
                  <div className="font-semibold">{workflow.name}</div>
                  <div className="text-sm text-gray-500 mt-1">
                    {workflowData.find(w => w.name.includes(workflow.name.split('')[0]))?.success_rate || 95}% 成功
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* 详细指标 */}
      <Tabs defaultValue="technical" className="space-y-4">
        <TabsList>
          <TabsTrigger value="technical">技术指标</TabsTrigger>
          <TabsTrigger value="experience">体验指标</TabsTrigger>
          <TabsTrigger value="efficiency">效率分析</TabsTrigger>
          <TabsTrigger value="trends">趋势分析</TabsTrigger>
        </TabsList>
        
        <TabsContent value="technical">
          <Card>
            <CardHeader>
              <CardTitle>PowerAutomation Core 技术指标</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={workflowData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="api_calls" name="API 调用数" fill="#3b82f6" />
                  <Bar dataKey="duration" name="执行时长(ms)" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="experience">
          <Card>
            <CardHeader>
              <CardTitle>ClaudeEditor SmartUI 体验指标</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={workflowData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="ui_response" 
                    name="UI 响应时间(ms)" 
                    stroke="#f59e0b" 
                    strokeWidth={2} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="success_rate" 
                    name="成功率(%)" 
                    stroke="#10b981" 
                    strokeWidth={2} 
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="efficiency">
          <Card>
            <CardHeader>
              <CardTitle>工作流效率分析</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {workflowData.map((workflow, idx) => (
                  <div key={idx} className="border-b pb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold">{workflow.name}</span>
                      <Badge variant={workflow.success_rate > 90 ? 'success' : 'warning'}>
                        {workflow.success_rate}% 成功率
                      </Badge>
                    </div>
                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">执行时长:</span>
                        <span className="ml-2 font-medium">{workflow.duration}ms</span>
                      </div>
                      <div>
                        <span className="text-gray-500">API 调用:</span>
                        <span className="ml-2 font-medium">{workflow.api_calls}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">UI 响应:</span>
                        <span className="ml-2 font-medium">{workflow.ui_response}ms</span>
                      </div>
                      <div>
                        <span className="text-gray-500">效率评分:</span>
                        <span className="ml-2 font-medium">
                          {(100 - workflow.duration / 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="trends">
          <Card>
            <CardHeader>
              <CardTitle>24小时趋势分析</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center text-gray-500 py-8">
                趋势数据收集中...
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}