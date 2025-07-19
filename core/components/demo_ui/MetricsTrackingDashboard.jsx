
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Info } from 'lucide-react';

export function MetricsTrackingDashboard({ metrics }) {
    const [selectedMetric, setSelectedMetric] = useState(null);
    
    const showFormula = (metric) => {
        setSelectedMetric(metric);
    };
    
    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6">指標追蹤儀表板</h1>
            
            {/* 數據訓練指標 */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>數據訓練指標</CardTitle>
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
                            <div className="text-2xl font-bold">{metrics.dataQuality}%</div>
                            <div className="text-sm text-gray-500">
                                公式：DQS = Σ(Wi × Scorei) / ΣWi
                            </div>
                        </div>
                        
                        <div className="p-4 border rounded">
                            <div className="flex justify-between items-center">
                                <span>標註準確率</span>
                                <Info 
                                    className="w-4 h-4 cursor-pointer"
                                    onClick={() => showFormula('labeling_accuracy')}
                                />
                            </div>
                            <div className="text-2xl font-bold">{metrics.labelingAccuracy}%</div>
                            <div className="text-sm text-gray-500">
                                公式：LA = 正確標註 / 總標註 × 100
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
            
            {/* 公式詳情彈窗 */}
            {selectedMetric && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
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
                                            <li key={k}>{k}: {v}</li>
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
                                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
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
