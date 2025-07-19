# MCP-Zero 與 SmartTool MCP 整合協同指南

## 整合架構

```
用戶請求
    ↓
MCP-Zero Engine (智能調度)
    ↓
任務分析 → 發現需要外部工具
    ↓
動態加載 SmartTool MCP
    ↓
SmartTool MCP 執行外部工具
    ↓
返回結果給 MCP-Zero
    ↓
整合結果返回用戶
```

## 協同工作方式

### 1. 自動發現與加載

當 MCP-Zero 分析任務時，會自動識別需要外部工具的場景：

```python
# MCP-Zero 任務分析
async def analyze_task(self, task: str):
    # 檢測外部工具需求關鍵詞
    tool_keywords = ['format', 'lint', 'prettier', 'eslint', 'slack', 'github', 'zapier']
    
    if any(keyword in task.lower() for keyword in tool_keywords):
        # 自動加載 SmartTool MCP
        smarttool = await self.registry.load_mcp('smarttool_mcp')
        return smarttool
```

### 2. 智能工具選擇

MCP-Zero 會根據任務上下文智能選擇合適的工具：

```python
# 示例：複合任務處理
task = "修復這段代碼的格式問題，運行測試，然後發送結果到 Slack"

# MCP-Zero 分解任務
steps = [
    {
        "mcp": "smarttool_mcp",
        "action": "execute_tool",
        "tool_id": "mcp_prettier",
        "params": {"code": code}
    },
    {
        "mcp": "smarttool_mcp", 
        "action": "execute_tool",
        "tool_id": "mcp_jest_runner",
        "params": {"test_files": ["test.js"]}
    },
    {
        "mcp": "smarttool_mcp",
        "action": "execute_tool", 
        "tool_id": "zapier_slack",
        "params": {"channel": "#dev", "message": "測試完成"}
    }
]
```

### 3. 跨 MCP 協作

SmartTool MCP 可以與其他 MCP 協同工作：

```python
# 完整工作流示例
async def code_review_workflow(code_file):
    # 1. CodeFlow MCP 分析代碼
    codeflow = await mcp_zero.load_mcp('codeflow_mcp')
    analysis = await codeflow.analyze_code(code_file)
    
    # 2. SmartTool MCP 格式化
    smarttool = await mcp_zero.load_mcp('smarttool_mcp')
    formatted = await smarttool.execute_tool(
        'mcp_prettier',
        {'code': analysis['code']}
    )
    
    # 3. Test MCP 生成測試
    test_mcp = await mcp_zero.load_mcp('test_mcp')
    tests = await test_mcp.generate_tests(formatted['result'])
    
    # 4. SmartTool MCP 運行測試
    test_results = await smarttool.execute_tool(
        'mcp_jest_runner',
        {'tests': tests}
    )
    
    # 5. SmartTool MCP 發送通知
    await smarttool.execute_tool(
        'zapier_slack',
        {
            'channel': '#code-review',
            'message': f'代碼審查完成: {test_results}'
        }
    )
```

## 實際使用場景

### 場景 1：代碼質量檢查
```python
# 用戶：「檢查並修復我的代碼質量問題」
result = await mcp_zero.execute_task(
    "檢查並修復我的代碼質量問題",
    context={'file': 'app.js'}
)

# MCP-Zero 自動：
# 1. 加載 SmartTool MCP
# 2. 執行 ESLint 檢查
# 3. 執行 Prettier 格式化
# 4. 返回修復後的代碼
```

### 場景 2：CI/CD 集成
```python
# 用戶：「部署代碼並通知團隊」
result = await mcp_zero.execute_task(
    "運行測試，如果通過就部署到生產環境並通知團隊",
    context={'branch': 'main'}
)

# MCP-Zero 自動協調：
# 1. SmartTool MCP - 運行測試（Jest）
# 2. 如果測試通過：
#    - SmartTool MCP - GitHub 創建發布
#    - SmartTool MCP - Slack 通知成功
# 3. 如果測試失敗：
#    - SmartTool MCP - Slack 通知失敗
```

### 場景 3：數據處理自動化
```python
# 用戶：「從 API 獲取數據，處理後存入 Google Sheets」
result = await mcp_zero.execute_task(
    "從我們的 API 獲取銷售數據，計算月度總結，存入 Google Sheets",
    context={'api_endpoint': '/sales', 'sheet_id': 'abc123'}
)

# MCP-Zero 協調：
# 1. CodeFlow MCP - 生成數據獲取代碼
# 2. 執行代碼獲取數據
# 3. SmartTool MCP - 使用 zapier_google_sheets 存儲結果
```

## 配置整合

### 1. MCP-Zero 配置
```python
# mcp_zero_config.py
MCP_REGISTRY = {
    'smarttool_mcp': {
        'priority': 'P1',
        'auto_load_keywords': ['format', 'lint', 'slack', 'github', 'zapier'],
        'dependencies': [],
        'capabilities': ['external_tools', 'workflow_execution']
    }
}
```

### 2. SmartTool 配置
```python
# smarttool_config.py
EXTERNAL_TOOLS_CONFIG = {
    'mcp.so': {
        'api_key': os.getenv('MCP_SO_API_KEY'),
        'enabled_tools': ['prettier', 'eslint', 'jest']
    },
    'aci.dev': {
        'api_key': os.getenv('ACI_DEV_API_KEY'),
        'enabled_tools': ['code_analyzer', 'security_scanner']
    },
    'zapier': {
        'api_key': os.getenv('ZAPIER_API_KEY'),
        'enabled_tools': ['slack', 'github', 'google_sheets']
    }
}
```

## 性能優化

### 1. 智能緩存
- MCP-Zero 緩存已加載的 SmartTool MCP 實例
- SmartTool MCP 緩存工具執行結果
- 相同請求直接返回緩存結果

### 2. 並行執行
```python
# MCP-Zero 支持並行調用 SmartTool
results = await mcp_zero.parallel_execute([
    ('smarttool_mcp', 'execute_tool', {'tool_id': 'mcp_prettier'}),
    ('smarttool_mcp', 'execute_tool', {'tool_id': 'mcp_eslint'}),
    ('smarttool_mcp', 'execute_tool', {'tool_id': 'aci_security_scanner'})
])
```

### 3. 按需加載
- SmartTool MCP 只在需要時加載
- 不使用時自動卸載釋放資源
- 根據使用頻率調整加載優先級

## 監控與調試

### 1. 執行追踪
```python
# MCP-Zero 提供完整的執行追踪
trace = await mcp_zero.get_execution_trace()
# 顯示：
# - 哪些 MCP 被加載
# - SmartTool 執行了哪些工具
# - 每個步驟的耗時
# - 成功/失敗狀態
```

### 2. 錯誤處理
```python
# SmartTool MCP 錯誤會被 MCP-Zero 捕獲並處理
try:
    result = await smarttool.execute_tool('unknown_tool')
except ToolNotFoundError:
    # MCP-Zero 自動降級處理
    fallback_result = await mcp_zero.use_fallback_strategy()
```

## 最佳實踐

1. **任務描述要清晰** - 幫助 MCP-Zero 準確識別需要的工具
2. **配置 API 密鑰** - 確保外部工具可以正常使用
3. **使用工作流** - 對於複雜任務，定義清晰的工作流
4. **監控使用情況** - 追踪哪些工具使用頻繁，優化配置
5. **錯誤降級** - 當外部工具失敗時，有備選方案

## 未來規劃

1. **更智能的工具推薦** - 基於歷史使用和效果
2. **自定義工具市場** - 用戶可以貢獻自己的工具
3. **工具組合優化** - 自動發現最佳工具組合
4. **跨平台工具鏈** - 不同平台工具的無縫銜接