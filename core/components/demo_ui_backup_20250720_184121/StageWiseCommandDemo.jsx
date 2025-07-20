
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Play, Pause, RotateCcw, CheckCircle, Clock } from 'lucide-react';

export function StageWiseCommandDemo() {
    const [currentStage, setCurrentStage] = useState('init');
    const [isRunning, setIsRunning] = useState(false);
    const [testResults, setTestResults] = useState([]);
    const [metrics, setMetrics] = useState({});
    const [progress, setProgress] = useState(0);
    
    const stages = [
        { id: 'init', name: '初始化', icon: '🔧' },
        { id: 'command_test', name: '指令測試', icon: '🧪' },
        { id: 'k2_mode', name: 'K2模式', icon: '🚀' },
        { id: 'mcp_integration', name: 'MCP集成', icon: '🔌' },
        { id: 'workflow', name: '工作流', icon: '🔄' },
        { id: 'metrics', name: '指標展示', icon: '📊' },
        { id: 'complete', name: '完成', icon: '✅' }
    ];
    
    const commandCategories = [
        {
            name: 'Claude原生',
            commands: [
                { cmd: '/help', support: '✅', desc: '幫助信息' },
                { cmd: '/model', support: '🚀', desc: 'K2信息' },
                { cmd: '/save', support: '🚀', desc: '保存對話' },
                { cmd: '/export', support: '🚀', desc: '導出數據' }
            ]
        },
        {
            name: 'Command MCP',
            commands: [
                { cmd: '/run', support: '✅', desc: '執行腳本' },
                { cmd: '/test', support: '✅', desc: '運行測試' },
                { cmd: '/analyze', support: '🚀', desc: '代碼分析' },
                { cmd: '/build', support: '✅', desc: '構建項目' }
            ]
        },
        {
            name: 'ClaudeEditor',
            commands: [
                { cmd: '/ui', support: '✅', desc: 'UI設計器' },
                { cmd: '/preview', support: '✅', desc: '實時預覽' },
                { cmd: '/workflow', support: '✅', desc: '工作流' },
                { cmd: '/mcp', support: '✅', desc: 'MCP管理' }
            ]
        },
        {
            name: 'K2增強',
            commands: [
                { cmd: '/train', support: '🚀', desc: 'K2訓練' },
                { cmd: '/optimize', support: '🚀', desc: '代碼優化' },
                { cmd: '/metrics', support: '🚀', desc: '查看指標' },
                { cmd: '/record', support: '🚀', desc: '記錄對話' }
            ]
        }
    ];
    
    const runDemo = async () => {
        setIsRunning(true);
        
        for (let i = 0; i < stages.length; i++) {
            setCurrentStage(stages[i].id);
            setProgress((i + 1) / stages.length * 100);
            
            // 模擬階段執行
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            if (stages[i].id === 'command_test') {
                // 模擬測試結果
                const results = commandCategories.flatMap(cat => 
                    cat.commands.map(cmd => ({
                        ...cmd,
                        responseTime: Math.random() * 100 + 50,
                        status: 'success'
                    }))
                );
                setTestResults(results);
            } else if (stages[i].id === 'metrics') {
                // 設置指標
                setMetrics({
                    technical: { response: '95ms', success: '99.2%', uptime: '99.9%' },
                    experience: { discovery: '3擊鍵', uiSpeed: '16ms', satisfaction: '92%' },
                    k2: { samples: '8,066', accuracy: '94.2%', savings: '80%' }
                });
            }
        }
        
        setIsRunning(false);
    };
    
    const reset = () => {
        setCurrentStage('init');
        setProgress(0);
        setTestResults([]);
        setMetrics({});
    };
    
    return (
        <div className="p-6 space-y-6">
            {/* 標題和控制 */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex justify-between items-center">
                        <span>StageWise 精準控制演示</span>
                        <div className="flex gap-2">
                            <Button 
                                onClick={runDemo} 
                                disabled={isRunning}
                                size="sm"
                            >
                                {isRunning ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                                {isRunning ? '運行中' : '開始演示'}
                            </Button>
                            <Button onClick={reset} variant="outline" size="sm">
                                <RotateCcw className="w-4 h-4 mr-2" />
                                重置
                            </Button>
                        </div>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <Progress value={progress} className="mb-4" />
                    
                    {/* 階段指示器 */}
                    <div className="flex justify-between mb-6">
                        {stages.map((stage, idx) => (
                            <div 
                                key={stage.id}
                                className={`flex flex-col items-center ${
                                    currentStage === stage.id ? 'text-primary' : 
                                    stages.findIndex(s => s.id === currentStage) > idx ? 'text-green-600' : 'text-gray-400'
                                }`}
                            >
                                <span className="text-2xl mb-1">{stage.icon}</span>
                                <span className="text-xs">{stage.name}</span>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
            
            {/* 指令測試結果 */}
            {currentStage === 'command_test' && testResults.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>指令測試結果</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {commandCategories.map(category => (
                                <div key={category.name}>
                                    <h4 className="font-semibold mb-2">{category.name}</h4>
                                    {category.commands.map(cmd => {
                                        const result = testResults.find(r => r.cmd === cmd.cmd);
                                        return (
                                            <div key={cmd.cmd} className="flex items-center justify-between mb-1">
                                                <span className="text-sm font-mono">{cmd.cmd}</span>
                                                <div className="flex items-center gap-1">
                                                    <span>{cmd.support}</span>
                                                    {result && (
                                                        <Badge variant="outline" className="text-xs">
                                                            {result.responseTime.toFixed(0)}ms
                                                        </Badge>
                                                    )}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}
            
            {/* K2 模式特性 */}
            {currentStage === 'k2_mode' && (
                <Card>
                    <CardHeader>
                        <CardTitle>K2 模式特性</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 bg-blue-50 rounded">
                                <h4 className="font-semibold mb-2">🚀 增強功能</h4>
                                <ul className="text-sm space-y-1">
                                    <li>• 自動對話記錄</li>
                                    <li>• 成本優化 80%</li>
                                    <li>• 本地推理支持</li>
                                    <li>• 智能路由選擇</li>
                                </ul>
                            </div>
                            <div className="p-4 bg-green-50 rounded">
                                <h4 className="font-semibold mb-2">💰 成本對比</h4>
                                <div className="text-sm space-y-1">
                                    <div className="flex justify-between">
                                        <span>Claude API:</span>
                                        <span>¥10/M tokens</span>
                                    </div>
                                    <div className="flex justify-between font-semibold text-green-600">
                                        <span>K2 模型:</span>
                                        <span>¥2/M tokens</span>
                                    </div>
                                    <div className="mt-2 pt-2 border-t">
                                        <div className="flex justify-between">
                                            <span>節省:</span>
                                            <span className="font-bold">80%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
            
            {/* 指標展示 */}
            {currentStage === 'metrics' && Object.keys(metrics).length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>關鍵指標</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <h4 className="font-semibold mb-2">技術指標</h4>
                                {Object.entries(metrics.technical || {}).map(([key, value]) => (
                                    <div key={key} className="flex justify-between text-sm mb-1">
                                        <span>{key}:</span>
                                        <span className="font-medium">{value}</span>
                                    </div>
                                ))}
                            </div>
                            <div>
                                <h4 className="font-semibold mb-2">體驗指標</h4>
                                {Object.entries(metrics.experience || {}).map(([key, value]) => (
                                    <div key={key} className="flex justify-between text-sm mb-1">
                                        <span>{key}:</span>
                                        <span className="font-medium">{value}</span>
                                    </div>
                                ))}
                            </div>
                            <div>
                                <h4 className="font-semibold mb-2">K2 指標</h4>
                                {Object.entries(metrics.k2 || {}).map(([key, value]) => (
                                    <div key={key} className="flex justify-between text-sm mb-1">
                                        <span>{key}:</span>
                                        <span className="font-medium">{value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
            
            {/* 完成狀態 */}
            {currentStage === 'complete' && (
                <Card className="bg-green-50">
                    <CardContent className="py-8 text-center">
                        <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold mb-2">演示完成！</h3>
                        <p className="text-gray-600">
                            已成功展示 StageWise 精準控制下的指令測試和 K2 集成能力
                        </p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
