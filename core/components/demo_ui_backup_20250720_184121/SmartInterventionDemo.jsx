import React, { useState, useEffect } from 'react';
import { 
  BrainIcon, 
  ArrowRightIcon, 
  CheckCircleIcon, 
  AlertCircleIcon,
  ZapIcon,
  ChartBarIcon,
  CodeIcon,
  ImageIcon,
  DatabaseIcon,
  UsersIcon,
  TestTubeIcon,
  RocketIcon
} from '@heroicons/react/24/outline';

const SmartInterventionDemo = () => {
  const [activeScenario, setActiveScenario] = useState(null);
  const [detectionStatus, setDetectionStatus] = useState('idle');
  const [switchProgress, setSwitchProgress] = useState(0);
  const [demoMessages, setDemoMessages] = useState([]);

  // Smart Intervention 場景定義
  const scenarios = [
    {
      id: 'visualization',
      name: '數據可視化',
      icon: ChartBarIcon,
      trigger: '我需要創建一個圖表來展示銷售數據',
      claudeTask: '文字描述圖表需求',
      claudeEditorTask: '生成交互式圖表',
      advantage: '實時預覽、交互式編輯、多種圖表類型',
      demo: {
        input: 'sales_data.json',
        output: 'Interactive Chart Component',
        features: ['D3.js 圖表', 'Recharts 組件', '實時數據更新']
      }
    },
    {
      id: 'ui_design',
      name: 'UI 設計',
      icon: ImageIcon,
      trigger: '設計一個響應式的儀表板界面',
      claudeTask: '提供設計建議',
      claudeEditorTask: '拖放式 UI 生成',
      advantage: '視覺化設計、即時預覽、響應式調整',
      demo: {
        input: 'design_requirements.md',
        output: 'Responsive Dashboard',
        features: ['SmartUI 生成', '組件庫', '主題定制']
      }
    },
    {
      id: 'database',
      name: '數據庫設計',
      icon: DatabaseIcon,
      trigger: '創建一個電商系統的數據庫架構',
      claudeTask: 'SQL schema 建議',
      claudeEditorTask: 'ER 圖視覺化設計',
      advantage: '可視化關係圖、自動生成 DDL、版本管理',
      demo: {
        input: 'requirements.txt',
        output: 'Database Schema + Migrations',
        features: ['ER 圖生成', 'Migration 腳本', '索引優化']
      }
    },
    {
      id: 'deployment',
      name: '部署配置',
      icon: RocketIcon,
      trigger: '部署應用到 Kubernetes',
      claudeTask: 'YAML 配置建議',
      claudeEditorTask: '可視化部署流程',
      advantage: '部署流程圖、配置驗證、一鍵部署',
      demo: {
        input: 'app.yaml',
        output: 'K8s Deployment Pipeline',
        features: ['Helm Charts', 'CI/CD 集成', '監控配置']
      }
    },
    {
      id: 'testing',
      name: 'API 測試',
      icon: TestTubeIcon,
      trigger: '測試 REST API 端點',
      claudeTask: '測試案例建議',
      claudeEditorTask: 'API 測試客戶端',
      advantage: '交互式測試、自動文檔生成、性能分析',
      demo: {
        input: 'api_spec.yaml',
        output: 'Test Suite + Docs',
        features: ['Postman 集成', '自動測試', '文檔生成']
      }
    },
    {
      id: 'collaboration',
      name: '團隊協作',
      icon: UsersIcon,
      trigger: '進行代碼審查和重構',
      claudeTask: '重構建議',
      claudeEditorTask: '實時協作編輯',
      advantage: '多人實時編輯、版本對比、評論系統',
      demo: {
        input: 'pull_request.diff',
        output: 'Code Review Session',
        features: ['實時協作', '代碼標註', '改進建議']
      }
    }
  ];

  // 模擬智能檢測流程
  const simulateDetection = (scenario) => {
    setActiveScenario(scenario);
    setDetectionStatus('detecting');
    setSwitchProgress(0);
    setDemoMessages([]);

    // 模擬檢測步驟
    const steps = [
      { progress: 20, status: 'detecting', message: `檢測到關鍵詞: "${scenario.trigger}"` },
      { progress: 40, status: 'analyzing', message: `分析任務類型: ${scenario.name}` },
      { progress: 60, status: 'comparing', message: `比較 Claude vs ClaudeEditor 能力` },
      { progress: 80, status: 'switching', message: `準備切換到 ClaudeEditor...` },
      { progress: 100, status: 'completed', message: `已成功切換到 ClaudeEditor！` }
    ];

    steps.forEach((step, index) => {
      setTimeout(() => {
        setSwitchProgress(step.progress);
        setDetectionStatus(step.status);
        setDemoMessages(prev => [...prev, {
          type: step.status === 'completed' ? 'success' : 'info',
          text: step.message,
          timestamp: new Date().toLocaleTimeString()
        }]);
      }, index * 800);
    });
  };

  // 渲染場景卡片
  const renderScenarioCard = (scenario) => {
    const Icon = scenario.icon;
    const isActive = activeScenario?.id === scenario.id;

    return (
      <div
        key={scenario.id}
        className={`
          border rounded-lg p-4 cursor-pointer transition-all
          ${isActive ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}
        `}
        onClick={() => simulateDetection(scenario)}
      >
        <div className="flex items-center gap-3 mb-3">
          <Icon className={`w-6 h-6 ${isActive ? 'text-blue-500' : 'text-gray-500'}`} />
          <h3 className="font-semibold">{scenario.name}</h3>
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="flex items-start gap-2">
            <span className="text-gray-500">觸發:</span>
            <span className="text-gray-700 italic">"{scenario.trigger}"</span>
          </div>
          
          <div className="grid grid-cols-2 gap-2 mt-3">
            <div className="bg-gray-100 rounded p-2">
              <div className="text-xs text-gray-500">Claude</div>
              <div className="text-xs mt-1">{scenario.claudeTask}</div>
            </div>
            <div className="bg-green-100 rounded p-2">
              <div className="text-xs text-green-600">ClaudeEditor</div>
              <div className="text-xs mt-1">{scenario.claudeEditorTask}</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // 渲染進度條
  const renderProgressBar = () => {
    if (!activeScenario) return null;

    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">智能切換進度</h3>
        
        <div className="relative">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-500 transition-all duration-500"
              style={{ width: `${switchProgress}%` }}
            />
          </div>
          
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>檢測</span>
            <span>分析</span>
            <span>比較</span>
            <span>切換</span>
            <span>完成</span>
          </div>
        </div>

        <div className="mt-6 space-y-2">
          {demoMessages.map((msg, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-xs text-gray-400">{msg.timestamp}</span>
              <span className={`text-sm ${
                msg.type === 'success' ? 'text-green-600' : 'text-gray-700'
              }`}>
                {msg.text}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // 渲染詳細信息
  const renderDetails = () => {
    if (!activeScenario || detectionStatus !== 'completed') return null;

    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">切換結果</h3>
        
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">ClaudeEditor 優勢</h4>
            <p className="text-sm text-gray-600">{activeScenario.advantage}</p>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">演示數據</h4>
            <div className="bg-gray-50 rounded p-3 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">輸入:</span>
                <code className="text-blue-600">{activeScenario.demo.input}</code>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">輸出:</span>
                <code className="text-green-600">{activeScenario.demo.output}</code>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">生成功能</h4>
            <div className="flex flex-wrap gap-2">
              {activeScenario.demo.features.map((feature, idx) => (
                <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                  {feature}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* 標題區 */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg p-8">
        <div className="flex items-center gap-4 mb-4">
          <BrainIcon className="w-10 h-10" />
          <h1 className="text-3xl font-bold">Smart Intervention MCP</h1>
        </div>
        <p className="text-lg opacity-90">
          智能檢測任務類型，自動切換到最適合的工具
        </p>
        <div className="mt-4 flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <ZapIcon className="w-4 h-4" />
            <span>P0 級核心功能</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircleIcon className="w-4 h-4" />
            <span>自動識別 + 無縫切換</span>
          </div>
        </div>
      </div>

      {/* 場景選擇區 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">選擇測試場景</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {scenarios.map(renderScenarioCard)}
        </div>
      </div>

      {/* 進度和結果區 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderProgressBar()}
        {renderDetails()}
      </div>

      {/* 集成說明 */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">如何集成到你的項目</h3>
        <pre className="bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
          <code>{`// 1. 啟用 Smart Intervention
import { enableSmartIntervention } from '@powerautomation/smart-intervention';

// 2. 配置觸發規則
const config = {
  triggers: [
    { pattern: /創建.*圖表/, action: 'switch_to_visualization' },
    { pattern: /設計.*界面/, action: 'switch_to_ui_design' },
    { pattern: /部署.*應用/, action: 'switch_to_deployment' }
  ],
  autoSwitch: true,
  confirmBeforeSwitch: false
};

// 3. 初始化
enableSmartIntervention(config);

// 4. 在 Claude 對話中自動工作
// 當用戶說 "我需要創建一個銷售圖表" 時
// Smart Intervention 會自動檢測並切換到 ClaudeEditor`}</code>
        </pre>
      </div>
    </div>
  );
};

export default SmartInterventionDemo;