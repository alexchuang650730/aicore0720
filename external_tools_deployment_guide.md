# PowerAutomation 外部工具 MCP 部署指南

## 🚀 快速開始

### 1. 環境準備

```bash
# 安裝依賴
pip install httpx asyncio python-dotenv pyyaml

# 創建配置目錄
mkdir -p config/external_tools
```

### 2. API 密鑰配置

創建 `.env` 文件：

```bash
# MCP.so
MCP_SO_API_KEY=your_mcp_so_api_key
MCP_SO_BASE_URL=https://api.mcp.so/v1

# ACI.dev
ACI_DEV_API_KEY=your_aci_dev_api_key
ACI_DEV_BASE_URL=https://api.aci.dev/v2

# Zapier
ZAPIER_API_KEY=your_zapier_api_key
ZAPIER_WEBHOOK_URL=your_zapier_webhook_url
```

### 3. 工具配置文件

創建 `config/external_tools/tools_registry.yaml`：

```yaml
# 外部工具註冊表
tools:
  # Phase 1: MCP.so 工具
  mcp_prettier:
    name: "Prettier 代碼格式化"
    platform: mcp.so
    category: code_quality
    enabled: true
    config:
      parser: babel
      printWidth: 80
      tabWidth: 2
      useTabs: false
      semi: true
      singleQuote: true
      
  mcp_eslint:
    name: "ESLint 代碼檢查"
    platform: mcp.so
    category: code_quality
    enabled: true
    config:
      extends: airbnb
      autoFix: true
      
  mcp_jest_runner:
    name: "Jest 測試運行器"
    platform: mcp.so
    category: testing
    enabled: true
    config:
      coverage: true
      coverageThreshold:
        global:
          branches: 80
          functions: 80
          lines: 80
          statements: 80
          
  # Phase 2: ACI.dev 工具
  aci_code_review:
    name: "AI 代碼審查"
    platform: aci.dev
    category: ai_analysis
    enabled: true
    config:
      model: gpt-4-turbo
      focus:
        - quality
        - security
        - performance
        
  aci_refactor:
    name: "智能重構助手"
    platform: aci.dev
    category: ai_refactor
    enabled: true
    config:
      patterns:
        - SOLID
        - DRY
        - KISS
        
  # Phase 3: Zapier 工具
  zapier_github:
    name: "GitHub 自動化"
    platform: zapier
    category: collaboration
    enabled: false  # 需要額外配置
    config:
      triggers:
        - push
        - pull_request
        - issue
        
  zapier_slack:
    name: "Slack 通知"
    platform: zapier
    category: notification
    enabled: false  # 需要額外配置
    config:
      default_channel: "#dev"
      
# 成本控制
cost_control:
  daily_limit: 50.0  # USD
  monthly_limit: 1000.0
  alert_threshold: 0.8
  free_tier_first: true
  
# 性能優化
performance:
  cache:
    enabled: true
    ttl: 3600  # 秒
    max_size: 1000
  timeout:
    default: 5000  # 毫秒
    mcp_so: 5000
    aci_dev: 10000
    zapier: 8000
  retry:
    max_attempts: 3
    backoff_factor: 2
    
# 監控配置
monitoring:
  enabled: true
  metrics:
    - latency
    - success_rate
    - cost
    - usage
  alerts:
    - type: cost_exceed
      threshold: 0.8
      notify: email
    - type: error_rate
      threshold: 0.1
      notify: slack
```

### 4. 集成到 PowerAutomation

#### 4.1 註冊 External Tools MCP

```python
# core/mcp_manager.py

from external_tools_mcp_integration import ExternalToolsMCP

class MCPManager:
    def __init__(self):
        self.components = {}
        
    async def initialize(self):
        # 註冊其他 MCP...
        
        # 註冊 External Tools MCP
        external_tools = ExternalToolsMCP()
        await external_tools.initialize()
        self.components['external_tools_mcp'] = external_tools
        
        print(f"✅ 註冊 External Tools MCP: {len(external_tools.tools_registry)} 個工具")
```

#### 4.2 更新 K2 Router

```python
# core/k2_router.py

async def route_with_external_tools(self, request):
    # 檢查是否需要外部工具
    if self._needs_external_tools(request):
        # 調用 External Tools MCP
        result = await self.mcp_manager.call(
            'external_tools_mcp',
            'get_recommendations',
            {
                'intent': request.intent,
                'context': request.context
            }
        )
        
        # 執行推薦的工具
        for tool in result['recommendations'][:3]:
            await self._execute_external_tool(tool['tool'])
```

#### 4.3 更新 ClaudeEditor UI

```javascript
// claudeditor/js/external_tools.js

class ExternalToolsPanel {
    constructor() {
        this.mcp = window.powerAutomation.mcp;
    }
    
    async initialize() {
        // 獲取工具列表
        const tools = await this.mcp.call('external_tools_mcp', 'list_tools', {});
        
        // 渲染到 UI
        this.render(tools);
        
        // 綁定事件
        this.bindEvents();
    }
    
    async executeToolWorkflow(workflow) {
        // 顯示進度
        this.showProgress();
        
        try {
            // 執行工作流
            const result = await this.mcp.call(
                'external_tools_mcp',
                'execute_workflow',
                {
                    steps: workflow.steps,
                    parallel: workflow.parallel
                }
            );
            
            // 顯示結果
            this.showResult(result);
            
        } catch (error) {
            this.showError(error);
        }
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    const toolsPanel = new ExternalToolsPanel();
    toolsPanel.initialize();
});
```

### 5. 測試驗證

#### 5.1 單元測試

```python
# tests/test_external_tools_mcp.py

import pytest
import asyncio

async def test_list_tools():
    mcp = ExternalToolsMCP()
    result = await mcp.handle_request('list_tools', {})
    assert result['total'] > 0
    assert 'mcp.so' in result['platforms']

async def test_execute_prettier():
    mcp = ExternalToolsMCP()
    result = await mcp.handle_request('execute_tool', {
        'tool_id': 'mcp_prettier',
        'parameters': {
            'code': 'const x=1;',
            'language': 'javascript'
        }
    })
    assert 'error' not in result
    assert 'formatted_code' in result['result']

async def test_workflow_execution():
    mcp = ExternalToolsMCP()
    result = await mcp.handle_request('execute_workflow', {
        'steps': [
            {'tool_id': 'mcp_prettier', 'parameters': {...}},
            {'tool_id': 'mcp_eslint', 'parameters': {...}}
        ],
        'parallel': True
    })
    assert result['success'] == True
```

#### 5.2 集成測試

```bash
# 啟動測試環境
python3 -m pytest tests/integration/test_external_tools_integration.py -v

# 性能測試
python3 performance_test.py --tools=10 --concurrent=5
```

### 6. 監控和優化

#### 6.1 監控儀表板

```python
# monitoring/external_tools_dashboard.py

class ExternalToolsDashboard:
    def __init__(self):
        self.metrics = {
            'total_calls': 0,
            'success_rate': 0.0,
            'avg_latency': 0.0,
            'total_cost': 0.0,
            'tool_usage': {}
        }
    
    async def update_metrics(self):
        # 從 MCP 獲取指標
        status = await mcp.get_status()
        
        # 更新儀表板
        self.display_metrics(status)
```

#### 6.2 成本優化策略

1. **使用免費層優先**
   ```python
   if tool['cost_per_call'] == 0 or self.within_free_tier(tool):
       # 優先使用
       priority = 1.0
   ```

2. **緩存高頻結果**
   ```python
   # 對於相同的輸入，使用緩存結果
   cache_key = generate_cache_key(tool_id, params)
   if cache_key in cache:
       return cache[cache_key]
   ```

3. **批量處理**
   ```python
   # 合併多個請求
   batch_request = combine_requests(requests)
   result = await execute_batch(batch_request)
   ```

### 7. 故障排除

#### 常見問題

1. **API 連接失敗**
   - 檢查 API 密鑰
   - 驗證網絡連接
   - 查看防火牆設置

2. **工具執行超時**
   - 增加超時設置
   - 檢查工具狀態
   - 使用異步執行

3. **成本超限**
   - 檢查成本控制配置
   - 查看使用報告
   - 優化調用頻率

### 8. 擴展指南

#### 添加新工具

1. 在 `tools_registry.yaml` 添加配置
2. 實現對應的適配器方法
3. 添加測試用例
4. 更新文檔

#### 添加新平台

1. 創建新的適配器類
2. 實現標準接口
3. 註冊到 MCP
4. 配置認證信息

### 9. 最佳實踐

1. **安全性**
   - 所有 API 密鑰使用環境變量
   - 敏感數據加密存儲
   - 定期輪換密鑰

2. **性能**
   - 使用連接池
   - 實現智能緩存
   - 異步並發執行

3. **可靠性**
   - 實現重試機制
   - 降級策略
   - 錯誤恢復

### 10. 發布檢查清單

- [ ] 所有測試通過
- [ ] API 密鑰已配置
- [ ] 成本控制已設置
- [ ] 監控已啟用
- [ ] 文檔已更新
- [ ] 備份計劃已制定

## 🎯 結論

通過遵循這個部署指南，您可以在 **1-2 週內** 成功將外部工具 MCP 集成到 PowerAutomation 中，立即獲得：

- 500+ 個外部工具
- 3倍的自動化能力提升
- 更好的用戶體驗
- 行業領先的競爭優勢

開始部署，讓 PowerAutomation 進入下一個階段！