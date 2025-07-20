import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Info } from 'lucide-react';

/**
 * 性能指標追蹤儀表板
 * 從 demo_ui/MetricsTrackingDashboard.jsx 遷移到 ClaudeEditor MCP
 * 
 * 功能：
 * - 數據訓練指標監控
 * - K2模型性能追蹤
 * - Smart Intervention延遲監控
 * - MemoryRAG壓縮率統計
 */
export function MetricsTrackingDashboard({ metrics = {} }) {
    const [selectedMetric, setSelectedMetric] = useState(null);
    
    // 默認指標數據（v4.76）
    const defaultMetrics = {
        dataQuality: 94.1,
        labelingAccuracy: 91.3,
        smartInterventionLatency: 85,
        memoryragCompression: 2.4,
        smartuiAccessibility: 100,
        k2Accuracy: 95,
        claudeResponseTime: 245,
        k2ResponseTime: 89,
        costSavings: 60,
        valueRatio: 4,
        ...metrics
    };
    
    const showFormula = (metricKey) => {
        const formulas = {
            'data_quality_score': {
                name: '數據質量分數',
                formula: 'DQS = Σ(Wi × Scorei) / ΣWi',
                variables: {
                    'Wi': '權重因子',
                    'Scorei': '各項質量指標得分',
                    'DQS': '數據質量分數'
                },
                example: 'DQS = (0.3×95 + 0.2×90 + 0.5×92) / 1.0 = 92.5'
            },
            'smart_intervention_latency': {
                name: 'Smart Intervention延遲',
                formula: 'SIL = Detection_Time + Processing_Time + Response_Time',
                variables: {
                    'Detection_Time': '檢測時間',
                    'Processing_Time': '處理時間',
                    'Response_Time': '響應時間'
                },
                example: 'SIL = 25ms + 35ms + 25ms = 85ms (目標 <100ms)'
            },
            'memoryrag_compression': {
                name: 'MemoryRAG壓縮率',
                formula: 'MCR = (Original_Size - Compressed_Size) / Original_Size × 100',
                variables: {
                    'Original_Size': '原始大小',
                    'Compressed_Size': '壓縮後大小',
                    'MCR': '壓縮率百分比'
                },
                example: 'MCR = (100KB - 2.4KB) / 100KB × 100 = 97.6% 壓縮'
            },
            'k2_accuracy': {
                name: 'K2模型準確率',
                formula: 'K2A = Correct_Predictions / Total_Predictions × 100',
                variables: {
                    'Correct_Predictions': '正確預測數',
                    'Total_Predictions': '總預測數',
                    'K2A': 'K2準確率百分比'
                },
                example: 'K2A = 950 / 1000 × 100 = 95%'
            }
        };
        
        setSelectedMetric(formulas[metricKey]);
    };
    
    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6">PowerAutomation v4.76 指標追蹤儀表板</h1>
            
            {/* v4.76 核心性能指標 */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>🎯 v4.76 核心突破指標</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                        <div className="p-4 border rounded bg-blue-50">
                            <div className="flex justify-between items-center">
                                <span>Smart Intervention延遲</span>
                                <Info 
                                    className="w-4 h-4 cursor-pointer"
                                    onClick={() => showFormula('smart_intervention_latency')}
                                />
                            </div>
                            <div className="text-2xl font-bold text-green-600">
                                {defaultMetrics.smartInterventionLatency}ms
                            </div>
                            <div className="text-sm text-gray-500">
                                目標: &lt;100ms ✅
                            </div>
                        </div>
                        
                        <div className="p-4 border rounded bg-green-50">
                            <div className="flex justify-between items-center">
                                <span>MemoryRAG壓縮率</span>
                                <Info 
                                    className="w-4 h-4 cursor-pointer"
                                    onClick={() => showFormula('memoryrag_compression')}
                                />
                            </div>
                            <div className="text-2xl font-bold text-blue-600">
                                {defaultMetrics.memoryragCompression}%
                            </div>
                            <div className="text-sm text-gray-500">
                                從47.2% → 2.4% ✅
                            </div>
                        </div>
                        
                        <div className="p-4 border rounded bg-purple-50">
                            <div className="flex justify-between items-center">
                                <span>SmartUI無障礙覆蓋</span>
                                <Info 
                                    className="w-4 h-4 cursor-pointer"
                                    onClick={() => showFormula('smartui_accessibility')}
                                />
                            </div>
                            <div className="text-2xl font-bold text-purple-600">
                                {defaultMetrics.smartuiAccessibility}%
                            </div>
                            <div className="text-sm text-gray-500">
                                WCAG 2.1 完整合規 ✅
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* AI模型性能對比 */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>🤖 Claude + K2 雙AI架構性能</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 border rounded">
                            <div className="flex justify-between items-center">
                                <span>K2模型準確率</span>
                                <Info 
                                    className="w-4 h-4 cursor-pointer"
                                    onClick={() => showFormula('k2_accuracy')}
                                />
                            </div>
                            <div className="text-2xl font-bold text-orange-600">
                                {defaultMetrics.k2Accuracy}%
                            </div>
                            <div className="text-sm text-gray-500">
                                對比Claude基準 ⚡
                            </div>
                        </div>
                        
                        <div className="p-4 border rounded">
                            <div className="flex justify-between items-center">
                                <span>響應時間對比</span>
                                <Info className="w-4 h-4 cursor-pointer" />
                            </div>
                            <div className="flex justify-between">
                                <div>
                                    <div className="text-lg font-bold text-blue-600">
                                        Claude: {defaultMetrics.claudeResponseTime}ms
                                    </div>
                                    <div className="text-lg font-bold text-green-600">
                                        K2: {defaultMetrics.k2ResponseTime}ms
                                    </div>
                                </div>
                                <div className="text-2xl font-bold text-green-600">
                                    快63%
                                </div>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
            
            {/* 成本效益分析 */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>💰 成本效益分析</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                        <div className="p-4 border rounded bg-green-50">
                            <span>K2成本節省</span>
                            <div className="text-2xl font-bold text-green-600">
                                {defaultMetrics.costSavings}%
                            </div>
                        </div>
                        
                        <div className="p-4 border rounded bg-blue-50">
                            <span>價值產出比</span>
                            <div className="text-2xl font-bold text-blue-600">
                                {defaultMetrics.valueRatio}x
                            </div>
                        </div>
                        
                        <div className="p-4 border rounded bg-yellow-50">
                            <span>投資回報</span>
                            <div className="text-2xl font-bold text-yellow-600">
                                2元→8元價值
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* 數據訓練指標 */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>📊 數據訓練指標</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 border rounded">
                            <div className="flex justify-between items-center">
                                <span>數據質量分數</span>
                                <Info 
                                    className="w-4 h-4 cursor-pointer"
                                    onClick={() => showFormula('data_quality_score')}
                                />
                            </div>
                            <div className="text-2xl font-bold">{defaultMetrics.dataQuality}%</div>
                            <div className="text-sm text-gray-500">
                                公式：DQS = Σ(Wi × Scorei) / ΣWi
                            </div>
                        </div>
                        
                        <div className="p-4 border rounded">
                            <div className="flex justify-between items-center">
                                <span>關鍵詞檢測準確率</span>
                                <Info className="w-4 h-4 cursor-pointer" />
                            </div>
                            <div className="text-2xl font-bold">{defaultMetrics.labelingAccuracy}%</div>
                            <div className="text-sm text-gray-500">
                                從82.3% → 91.3% ✅
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
            
            {/* 公式詳情彈窗 */}
            {selectedMetric && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <Card className="w-2/3 max-h-[80vh] overflow-y-auto">
                        <CardHeader>
                            <CardTitle>{selectedMetric.name} - 計算公式</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div>
                                    <h3 className="font-bold">公式：</h3>
                                    <code className="block p-2 bg-gray-100 rounded">
                                        {selectedMetric.formula}
                                    </code>
                                </div>
                                
                                <div>
                                    <h3 className="font-bold">變量說明：</h3>
                                    <ul className="list-disc ml-6">
                                        {Object.entries(selectedMetric.variables).map(([k, v]) => (
                                            <li key={k}><strong>{k}</strong>: {v}</li>
                                        ))}
                                    </ul>
                                </div>
                                
                                <div>
                                    <h3 className="font-bold">計算示例：</h3>
                                    <code className="block p-2 bg-gray-100 rounded">
                                        {selectedMetric.example}
                                    </code>
                                </div>
                                
                                <button 
                                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                                    onClick={() => setSelectedMetric(null)}
                                >
                                    關閉
                                </button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}