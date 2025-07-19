#!/bin/bash

# PowerAutomation v4.75 演示部署腳本
# ClaudeEditor 演示環境完整配置

set -e

echo "🎪 PowerAutomation v4.75 ClaudeEditor 演示環境部署"
echo "================================================="

# 基本配置
DEMO_ROOT="/Users/alexchuang/alexchuangtest/aicore0720"
DEPLOY_PATH="$DEMO_ROOT/deploy/v4.75"
CLAUDEDITOR_PATH="$DEMO_ROOT/claudeditor"
MCP_CONFIG_PATH="$DEMO_ROOT/mcp_config"
DEMO_DATA_PATH="$DEPLOY_PATH/demo_data"

# 創建必要目錄
mkdir -p "$CLAUDEDITOR_PATH"
mkdir -p "$MCP_CONFIG_PATH"
mkdir -p "$DEMO_DATA_PATH"
mkdir -p "$DEPLOY_PATH/logs"

echo "📁 創建演示目錄結構..."

# 1. ClaudeEditor 配置
echo "⚙️  配置 ClaudeEditor 演示環境..."

cat > "$CLAUDEDITOR_PATH/demo_config.json" << 'EOF'
{
  "environment": "demo",
  "version": "v4.75",
  "demo_mode": true,
  "features": {
    "smart_intervention": {
      "enabled": true,
      "demo_keywords": ["React組件", "UI設計", "代碼生成", "測試", "部署"],
      "auto_switch_delay": 2000,
      "demo_scenarios": true
    },
    "codeflow_automation": {
      "enabled": true,
      "demo_projects": ["react-user-list", "nodejs-api", "python-service"],
      "simulation_mode": true
    },
    "smartui_designer": {
      "enabled": true,
      "component_library": "demo",
      "preview_mode": true,
      "accessibility_warnings": false
    },
    "memory_rag": {
      "enabled": true,
      "demo_contexts": 50,
      "compression_demo": true,
      "k2_optimization": true
    },
    "performance_monitor": {
      "enabled": true,
      "real_time_updates": true,
      "demo_metrics": true,
      "alert_simulation": true
    }
  },
  "ui_settings": {
    "theme": "professional",
    "layout": "demo_optimized",
    "animation_speed": "normal",
    "debug_overlay": false,
    "presenter_mode": true
  },
  "demo_constraints": {
    "max_execution_time": 300,
    "memory_limit": "2GB",
    "concurrent_operations": 5,
    "error_recovery": true
  }
}
EOF

# 2. MCP 組件配置
echo "🔧 配置 MCP 組件演示模式..."

cat > "$MCP_CONFIG_PATH/demo_mcp_config.json" << 'EOF'
{
  "mcp_components": {
    "P0_core": {
      "smart_intervention": {
        "port": 3001,
        "demo_mode": true,
        "response_time": 100,
        "success_rate": 0.95,
        "demo_triggers": {
          "ui_keywords": ["界面", "組件", "設計", "前端"],
          "code_keywords": ["代碼", "函數", "類", "API"],
          "test_keywords": ["測試", "檢查", "驗證", "調試"]
        }
      },
      "codeflow_mcp": {
        "port": 3002,
        "demo_mode": true,
        "generation_speed": 1200,
        "syntax_accuracy": 0.98,
        "demo_templates": [
          "react_component",
          "nodejs_service",
          "python_script",
          "test_suite"
        ]
      },
      "smartui_mcp": {
        "port": 3003,
        "demo_mode": true,
        "component_generation_time": 1.5,
        "responsive_accuracy": 0.95,
        "demo_components": [
          "user_list",
          "data_table",
          "navigation_bar",
          "dashboard_card"
        ]
      },
      "memoryrag_mcp": {
        "port": 3004,
        "demo_mode": true,
        "retrieval_accuracy": 0.90,
        "compression_ratio": 0.38,
        "demo_contexts": [
          "conversation_history",
          "code_documentation",
          "project_knowledge"
        ]
      }
    },
    "P1_important": {
      "smarttool_mcp": {
        "port": 3005,
        "demo_mode": true,
        "available_tools": 47,
        "response_time": 180
      },
      "test_mcp": {
        "port": 3006,
        "demo_mode": true,
        "generation_accuracy": 0.90,
        "execution_speed": 95
      },
      "claude_router_mcp": {
        "port": 3007,
        "demo_mode": true,
        "routing_accuracy": 0.97,
        "k2_switch_time": 45
      }
    },
    "P2_auxiliary": {
      "command_mcp": {
        "port": 3008,
        "demo_mode": true
      },
      "local_adapter_mcp": {
        "port": 3009,
        "demo_mode": true
      },
      "mcp_coordinator_mcp": {
        "port": 3010,
        "demo_mode": true
      },
      "docs_mcp": {
        "port": 3011,
        "demo_mode": true
      }
    }
  },
  "demo_settings": {
    "simulation_enabled": true,
    "error_injection": false,
    "performance_scaling": 0.8,
    "logging_level": "info"
  }
}
EOF

# 3. 演示數據準備
echo "📊 準備演示數據..."

# 創建示例項目
mkdir -p "$DEMO_DATA_PATH/projects/react-user-list"
cat > "$DEMO_DATA_PATH/projects/react-user-list/requirements.md" << 'EOF'
# 用戶列表組件需求

## 功能要求
1. 顯示用戶列表
2. 支持搜索過濾
3. 分頁功能
4. 響應式設計
5. 無障礙訪問支持

## 技術規範
- React 18+
- TypeScript
- Tailwind CSS
- Jest 測試

## UI設計
- 卡片式布局
- 搜索欄置頂
- 分頁控件底部
- 加載狀態顯示
EOF

# 創建性能測試數據
cat > "$DEMO_DATA_PATH/performance_metrics.json" << 'EOF'
{
  "system_metrics": {
    "cpu_usage": 25.3,
    "memory_usage": 187.2,
    "active_components": 11,
    "response_time": 124,
    "throughput": 847,
    "error_rate": 0.23
  },
  "component_metrics": {
    "smart_intervention": {
      "detection_accuracy": 94.2,
      "switch_latency": 89,
      "memory_usage": 38.1
    },
    "codeflow_mcp": {
      "generation_speed": 1247,
      "syntax_accuracy": 96.8,
      "deployment_success": 94.1
    },
    "smartui_mcp": {
      "generation_time": 1.8,
      "responsive_accuracy": 94.7,
      "accessibility_score": 87.4
    },
    "memoryrag_mcp": {
      "retrieval_accuracy": 89.7,
      "compression_ratio": 0.38,
      "k2_optimization": 27.3
    }
  }
}
EOF

# 4. 啟動腳本
echo "🚀 創建組件啟動腳本..."

cat > "$DEPLOY_PATH/start_demo_components.sh" << 'EOF'
#!/bin/bash

echo "🎬 啟動 PowerAutomation v4.75 演示組件..."

# 設置環境變量
export DEMO_MODE=true
export LOG_LEVEL=info
export MCP_CONFIG_PATH="/Users/alexchuang/alexchuangtest/aicore0720/mcp_config/demo_mcp_config.json"

# 啟動 MCP 組件 (模擬模式)
echo "📡 啟動 MCP 組件模擬服務..."

# P0 核心組件
node -e "
const express = require('express');
const app = express();
app.use(express.json());

// Smart Intervention 模擬
app.post('/smart-intervention/analyze', (req, res) => {
  setTimeout(() => {
    res.json({
      detected: true,
      confidence: 0.95,
      suggested_mode: 'claudeditor',
      switch_time: 89
    });
  }, 89);
});

app.listen(3001, () => console.log('✅ Smart Intervention MCP - Port 3001'));
" &

# CodeFlow MCP 模擬
node -e "
const express = require('express');
const app = express();
app.use(express.json());

app.post('/codeflow/generate', (req, res) => {
  setTimeout(() => {
    res.json({
      code: 'const UserList = () => { /* Generated code */ };',
      tests: '// Generated tests',
      deployment: { status: 'ready', time: '2.3s' },
      metrics: { speed: 1247, accuracy: 0.968 }
    });
  }, 1200);
});

app.listen(3002, () => console.log('✅ CodeFlow MCP - Port 3002'));
" &

# SmartUI MCP 模擬
node -e "
const express = require('express');
const app = express();
app.use(express.json());

app.post('/smartui/generate', (req, res) => {
  setTimeout(() => {
    res.json({
      component: '<div className=\"user-card\">...</div>',
      styles: '.user-card { /* Generated styles */ }',
      responsive: true,
      accessibility: { score: 87.4, issues: 2 }
    });
  }, 1800);
});

app.listen(3003, () => console.log('✅ SmartUI MCP - Port 3003'));
" &

# MemoryRAG MCP 模擬
node -e "
const express = require('express');
const app = express();
app.use(express.json());

app.post('/memoryrag/compress', (req, res) => {
  setTimeout(() => {
    res.json({
      original_tokens: 1024,
      compressed_tokens: 389,
      compression_ratio: 0.38,
      retrieval_accuracy: 0.897,
      k2_optimization: 0.273
    });
  }, 200);
});

app.listen(3004, () => console.log('✅ MemoryRAG MCP - Port 3004'));
" &

echo "⏳ 等待所有組件啟動..."
sleep 5

echo "🎉 所有演示組件已啟動！"
echo "📍 組件端口："
echo "  - Smart Intervention: 3001"
echo "  - CodeFlow: 3002" 
echo "  - SmartUI: 3003"
echo "  - MemoryRAG: 3004"

# 健康檢查
echo "🔍 執行健康檢查..."
for port in 3001 3002 3003 3004; do
  if curl -s "http://localhost:$port" > /dev/null 2>&1; then
    echo "✅ Port $port - OK"
  else
    echo "❌ Port $port - Failed"
  fi
done

echo "🏁 演示環境就緒！"
EOF

chmod +x "$DEPLOY_PATH/start_demo_components.sh"

# 5. ClaudeEditor 啟動腳本
echo "🎨 創建 ClaudeEditor 演示啟動腳本..."

cat > "$CLAUDEDITOR_PATH/start_claudeditor_demo.sh" << 'EOF'
#!/bin/bash

echo "🎪 啟動 ClaudeEditor 演示模式..."

# 設置演示環境
export DEMO_MODE=true
export CLAUDEDITOR_CONFIG="/Users/alexchuang/alexchuangtest/aicore0720/claudeditor/demo_config.json"
export MCP_ENDPOINTS="http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:3004"

# 檢查 MCP 組件
echo "🔍 檢查 MCP 組件連接..."
for port in 3001 3002 3003 3004; do
  if ! curl -s "http://localhost:$port" > /dev/null; then
    echo "❌ MCP 組件 $port 未啟動，請先運行 start_demo_components.sh"
    exit 1
  fi
done

echo "✅ 所有 MCP 組件連接正常"

# 啟動 ClaudeEditor (模擬)
echo "🚀 啟動 ClaudeEditor 演示界面..."

# 創建簡單的演示服務器
node -e "
const express = require('express');
const path = require('path');
const app = express();

app.use(express.static('.'));
app.use(express.json());

// 演示首頁
app.get('/', (req, res) => {
  res.send(\`
<!DOCTYPE html>
<html>
<head>
  <title>ClaudeEditor v4.75 - PowerAutomation 演示</title>
  <style>
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      margin: 0; padding: 20px; background: #f5f5f5;
    }
    .header { 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white; padding: 30px; border-radius: 10px; text-align: center;
      margin-bottom: 30px;
    }
    .demo-grid { 
      display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px; margin-bottom: 30px;
    }
    .demo-card { 
      background: white; padding: 25px; border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 4px solid #667eea;
    }
    .demo-card h3 { margin-top: 0; color: #333; }
    .demo-button { 
      background: #667eea; color: white; border: none;
      padding: 12px 24px; border-radius: 6px; cursor: pointer;
      font-size: 14px; margin-right: 10px; margin-top: 10px;
    }
    .demo-button:hover { background: #5a6fd8; }
    .status-bar { 
      background: white; padding: 15px; border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .status-item { 
      display: inline-block; margin-right: 30px; 
      padding: 8px 15px; background: #e8f2ff; border-radius: 20px;
      font-size: 14px; color: #1a73e8;
    }
    .metrics-panel {
      background: white; padding: 20px; border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .metric { 
      display: flex; justify-content: space-between; 
      padding: 10px 0; border-bottom: 1px solid #eee;
    }
    .metric:last-child { border-bottom: none; }
    .value { font-weight: bold; color: #1a73e8; }
  </style>
</head>
<body>
  <div class=\"header\">
    <h1>🎪 ClaudeEditor v4.75 演示中心</h1>
    <p>PowerAutomation 智能開發平台 - 20+1 MCP 組件架構</p>
  </div>

  <div class=\"status-bar\">
    <div class=\"status-item\">📊 系統狀態: 運行中</div>
    <div class=\"status-item\">🔧 MCP 組件: 11/11 活躍</div>
    <div class=\"status-item\">⚡ 性能: 90.1% 良好</div>
    <div class=\"status-item\">🧠 K2 模式: 已啟用</div>
  </div>

  <div class=\"demo-grid\">
    <div class=\"demo-card\">
      <h3>🧠 智能干預演示</h3>
      <p>展示關鍵詞檢測和自動模式切換功能</p>
      <button class=\"demo-button\" onclick=\"startDemo('intervention')\">開始演示</button>
      <button class=\"demo-button\" onclick=\"showCode('intervention')\">查看代碼</button>
    </div>

    <div class=\"demo-card\">
      <h3>⚡ 代碼流程自動化</h3>
      <p>完整的開發工作流程：需求→代碼→測試→部署</p>
      <button class=\"demo-button\" onclick=\"startDemo('codeflow')\">開始演示</button>
      <button class=\"demo-button\" onclick=\"showMetrics('codeflow')\">性能指標</button>
    </div>

    <div class=\"demo-card\">
      <h3>🎨 SmartUI 設計系統</h3>
      <p>智能 UI 組件生成和響應式設計</p>
      <button class=\"demo-button\" onclick=\"startDemo('smartui')\">開始演示</button>
      <button class=\"demo-button\" onclick=\"showPreview('smartui')\">預覽組件</button>
    </div>

    <div class=\"demo-card\">
      <h3>🗂️ 記憶增強檢索</h3>
      <p>上下文壓縮和智能檢索系統</p>
      <button class=\"demo-button\" onclick=\"startDemo('memoryrag')\">開始演示</button>
      <button class=\"demo-button\" onclick=\"showCompression('memoryrag')\">壓縮分析</button>
    </div>

    <div class=\"demo-card\">
      <h3>📈 性能監控系統</h3>
      <p>實時性能指標和系統健康度監控</p>
      <button class=\"demo-button\" onclick=\"startDemo('monitoring')\">開始演示</button>
      <button class=\"demo-button\" onclick=\"showDashboard('monitoring')\">儀表板</button>
    </div>

    <div class=\"demo-card\">
      <h3>🎛️ 集成演示場景</h3>
      <p>完整工作流程展示 (22分鐘)</p>
      <button class=\"demo-button\" onclick=\"startFullDemo()\">完整演示</button>
      <button class=\"demo-button\" onclick=\"downloadReport()\">下載報告</button>
    </div>
  </div>

  <div class=\"metrics-panel\">
    <h3>📊 實時性能指標</h3>
    <div class=\"metric\">
      <span>Smart Intervention 檢測準確率</span>
      <span class=\"value\">94.2%</span>
    </div>
    <div class=\"metric\">
      <span>CodeFlow 代碼生成速度</span>
      <span class=\"value\">1,247 tokens/s</span>
    </div>
    <div class=\"metric\">
      <span>SmartUI 組件生成時間</span>
      <span class=\"value\">1.8s</span>
    </div>
    <div class=\"metric\">
      <span>MemoryRAG 壓縮比</span>
      <span class=\"value\">38%</span>
    </div>
    <div class=\"metric\">
      <span>系統響應時間</span>
      <span class=\"value\">124ms</span>
    </div>
    <div class=\"metric\">
      <span>總體系統健康度</span>
      <span class=\"value\">90.1%</span>
    </div>
  </div>

  <script>
    function startDemo(type) {
      alert('🎬 啟動 ' + type + ' 演示場景...');
      // 這裡會調用實際的演示邏輯
    }

    function showCode(type) {
      window.open('/demo/' + type + '/code', '_blank');
    }

    function showMetrics(type) {
      window.open('/demo/' + type + '/metrics', '_blank');
    }

    function showPreview(type) {
      window.open('/demo/' + type + '/preview', '_blank');
    }

    function showCompression(type) {
      window.open('/demo/' + type + '/compression', '_blank');
    }

    function showDashboard(type) {
      window.open('/demo/' + type + '/dashboard', '_blank');
    }

    function startFullDemo() {
      if(confirm('確定要開始完整演示嗎？這將需要約22分鐘。')) {
        alert('🎪 開始完整演示流程...');
      }
    }

    function downloadReport() {
      alert('📄 下載演示報告...');
    }

    // 自動更新指標 (模擬)
    setInterval(() => {
      const values = document.querySelectorAll('.value');
      values.forEach(v => {
        if(v.textContent.includes('%')) {
          const current = parseFloat(v.textContent);
          const variation = (Math.random() - 0.5) * 2;
          v.textContent = Math.max(0, Math.min(100, current + variation)).toFixed(1) + '%';
        }
      });
    }, 3000);
  </script>
</body>
</html>
\`);
});

// API 端點
app.get('/api/status', (req, res) => {
  res.json({
    status: 'running',
    components: 11,
    performance: 90.1,
    k2_enabled: true
  });
});

app.listen(8080, () => {
  console.log('🎪 ClaudeEditor 演示界面啟動: http://localhost:8080');
  console.log('📊 演示控制台: http://localhost:8080/api/status');
});
" &

echo "✅ ClaudeEditor 演示模式已啟動!"
echo "🌐 演示地址: http://localhost:8080"
echo "🎯 準備開始演示..."

# 等待一下讓服務啟動
sleep 3

# 自動打開瀏覽器 (macOS)
if command -v open &> /dev/null; then
  echo "🖥️  自動打開演示界面..."
  open "http://localhost:8080"
fi

echo "🎉 ClaudeEditor 演示環境已就緒！"
EOF

chmod +x "$CLAUDEDITOR_PATH/start_claudeditor_demo.sh"

# 6. 完整部署腳本
echo "🎯 創建一鍵部署腳本..."

cat > "$DEPLOY_PATH/deploy_full_demo.sh" << 'EOF'
#!/bin/bash

echo "🚀 PowerAutomation v4.75 完整演示環境部署"
echo "==========================================="

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安裝，請先安裝 Node.js"
    exit 1
fi

# 檢查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安裝，請先安裝 npm"
    exit 1
fi

# 安裝必要依賴
echo "📦 安裝演示依賴..."
npm install -g express 2>/dev/null || true

# 1. 啟動 MCP 組件
echo "🔧 啟動 MCP 組件模擬服務..."
bash "/Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.75/start_demo_components.sh" &
MCP_PID=$!

# 等待 MCP 組件啟動
sleep 8

# 2. 啟動 ClaudeEditor
echo "🎨 啟動 ClaudeEditor 演示界面..."
bash "/Users/alexchuang/alexchuangtest/aicore0720/claudeditor/start_claudeditor_demo.sh" &
CLAUDEDITOR_PID=$!

# 等待所有服務啟動
sleep 5

echo ""
echo "🎉 演示環境部署完成！"
echo "========================"
echo "📍 服務地址："
echo "  🌐 ClaudeEditor 演示: http://localhost:8080"
echo "  📡 MCP API 基地址: http://localhost:3001-3004"
echo ""
echo "🎪 演示場景："
echo "  1. 智能干預演示 (2-3分鐘)"
echo "  2. 代碼流程自動化 (5-8分鐘)"  
echo "  3. SmartUI 設計演示 (3-5分鐘)"
echo "  4. 記憶增強檢索 (4-6分鐘)"
echo "  5. 性能監控演示 (3-4分鐘)"
echo ""
echo "⏱️  總演示時間: ~22分鐘"
echo ""
echo "🎯 演示準備就緒！打開瀏覽器訪問演示界面"
echo ""
echo "🛑 停止演示: Ctrl+C 或運行 'pkill -f demo'"

# 等待用戶中斷
trap 'echo "🛑 停止演示環境..."; kill $MCP_PID $CLAUDEDITOR_PID 2>/dev/null; exit 0' INT

# 保持腳本運行
wait
EOF

chmod +x "$DEPLOY_PATH/deploy_full_demo.sh"

echo ""
echo "✅ 演示部署腳本創建完成！"
echo "=========================="
echo ""
echo "📋 部署清單："
echo "  ✅ ClaudeEditor 配置文件"
echo "  ✅ MCP 組件配置文件" 
echo "  ✅ 演示數據準備"
echo "  ✅ 組件啟動腳本"
echo "  ✅ ClaudeEditor 演示界面"
echo "  ✅ 一鍵部署腳本"
echo ""
echo "🚀 開始演示："
echo "  bash $DEPLOY_PATH/deploy_full_demo.sh"
echo ""
echo "🎪 演示地址："
echo "  http://localhost:8080"