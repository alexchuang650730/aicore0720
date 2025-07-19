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
