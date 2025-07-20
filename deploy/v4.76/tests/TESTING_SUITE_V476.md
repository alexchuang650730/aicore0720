# PowerAutomation v4.76 測試套件

## 🧪 測試概覽

PowerAutomation v4.76測試套件涵蓋性能回歸測試、UI組件集成測試、演示功能驗證、以及關鍵指標基準測試，確保v4.76版本的穩定性和性能突破。

---

## 📊 v4.76核心測試指標

### 性能基準測試目標
| 測試項目 | v4.75基線 | v4.76目標 | 測試方法 |
|---------|-----------|-----------|----------|
| Smart Intervention延遲 | 147ms | <100ms | 自動化延遲測試 |
| MemoryRAG壓縮率 | 47.2% | <5% | 壓縮算法測試 |
| SmartUI無障礙覆蓋 | 87% | 100% | WCAG 2.1合規測試 |
| K2準確率 | 85% | >95% | 對比基準測試 |
| 關鍵測試失敗 | 8個 | <5個 | 回歸測試套件 |
| 內存使用量 | 73MB | <50MB | 負載壓力測試 |

---

## 🔧 測試環境配置

### 環境要求
```bash
# 測試環境最低配置
CPU: 4核心
內存: 8GB
磁盤: 10GB可用空間
網絡: 穩定連接

# 推薦測試配置  
CPU: 8核心
內存: 16GB
磁盤: SSD 20GB
網絡: 100Mbps+
```

### 測試環境初始化
```bash
# 進入測試目錄
cd deploy/v4.76/tests

# 安裝測試依賴
pip install -r test_requirements.txt

# 初始化測試數據庫
python setup_test_environment.py

# 啟動測試服務
bash start_test_services.sh
```

---

## 🧪 自動化測試套件

### 1. 核心功能測試

#### Smart Intervention測試
```python
# smart_intervention_test.py
import pytest
import time
from core.components.smart_intervention.demo_deployment_trigger import SmartInterventionDemo

class TestSmartIntervention:
    def test_detection_latency(self):
        """測試Smart Intervention檢測延遲"""
        demo = SmartInterventionDemo()
        
        test_cases = [
            "我想要看三權限系統的演示",
            "K2模型的性能怎麼樣？", 
            "打開ClaudeEditor三欄式界面",
            "請幫我部署到生產環境"
        ]
        
        for case in test_cases:
            start_time = time.time()
            result = demo.detect_intent(case)
            end_time = time.time()
            
            latency = (end_time - start_time) * 1000  # 轉換為毫秒
            
            assert latency < 100, f"延遲超標: {latency}ms"
            assert result.confidence > 0.85, f"置信度過低: {result.confidence}"
            assert len(result.actions) > 0, "未檢測到動作"
    
    def test_accuracy_rate(self):
        """測試檢測準確率"""
        demo = SmartInterventionDemo()
        test_dataset = load_test_dataset("smart_intervention_test_cases.json")
        
        correct_predictions = 0
        total_cases = len(test_dataset)
        
        for case in test_dataset:
            result = demo.detect_intent(case['input'])
            if result.predicted_action == case['expected_action']:
                correct_predictions += 1
        
        accuracy = correct_predictions / total_cases
        assert accuracy >= 0.913, f"準確率不達標: {accuracy:.3f}"
```

#### ClaudeEditor UI測試
```python
# claudeeditor_ui_test.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestClaudeEditorUI:
    def setup_method(self):
        """設置測試瀏覽器"""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:3000/claudeditor")
        
    def test_three_panel_layout(self):
        """測試三欄式界面佈局"""
        wait = WebDriverWait(self.driver, 10)
        
        # 檢查左側面板
        left_panel = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "left-panel")))
        assert left_panel.is_displayed()
        
        # 檢查中間編輯器
        center_editor = self.driver.find_element(By.CLASS_NAME, "center-editor")
        assert center_editor.is_displayed()
        
        # 檢查右側助手
        right_assistant = self.driver.find_element(By.CLASS_NAME, "right-assistant") 
        assert right_assistant.is_displayed()
        
        # 檢查導航區
        navigation = self.driver.find_element(By.CLASS_NAME, "navigation-tabs")
        assert navigation.is_displayed()
    
    def test_ai_model_switching(self):
        """測試AI模型切換功能"""
        # 點擊AI模型控制
        model_control = self.driver.find_element(By.ID, "ai-model-control")
        model_control.click()
        
        # 切換到K2模型
        k2_option = self.driver.find_element(By.VALUE, "k2-optimized")
        k2_option.click()
        
        # 驗證切換成功
        current_model = self.driver.find_element(By.ID, "current-model-display").text
        assert "K2" in current_model
        
        # 測試響應時間
        start_time = time.time()
        input_field = self.driver.find_element(By.ID, "code-input")
        input_field.send_keys("function test() { return 'hello'; }")
        
        # 等待AI響應
        ai_response = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-suggestion"))
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        assert response_time < 200, f"K2響應時間過長: {response_time}ms"
```

#### MemoryRAG壓縮測試
```python
# memoryrag_compression_test.py
import pytest
from core.components.memoryrag_mcp.advanced_compression_optimizer import MemoryRAGCompressor

class TestMemoryRAGCompression:
    def test_compression_ratio(self):
        """測試MemoryRAG壓縮率"""
        compressor = MemoryRAGCompressor(version="4.76")
        
        # 測試數據準備
        test_contexts = load_test_contexts("memoryrag_test_data.json")
        
        total_original_size = 0
        total_compressed_size = 0
        
        for context in test_contexts:
            original_size = len(context['content'].encode('utf-8'))
            compressed = compressor.compress(context['content'])
            compressed_size = len(compressed.encode('utf-8'))
            
            total_original_size += original_size
            total_compressed_size += compressed_size
        
        compression_ratio = (total_compressed_size / total_original_size) * 100
        
        assert compression_ratio <= 5.0, f"壓縮率未達標: {compression_ratio:.2f}%"
        assert compression_ratio >= 1.0, f"壓縮率異常: {compression_ratio:.2f}%"
    
    def test_compression_quality(self):
        """測試壓縮質量（信息保留度）"""
        compressor = MemoryRAGCompressor(version="4.76")
        
        test_case = {
            'content': "PowerAutomation v4.76 實現了Smart Intervention延遲優化到85ms，MemoryRAG壓縮率提升到2.4%，SmartUI無障礙覆蓋達到100%。",
            'key_info': ["v4.76", "85ms", "2.4%", "100%"]
        }
        
        compressed = compressor.compress(test_case['content'])
        
        # 檢查關鍵信息是否保留
        for key_info in test_case['key_info']:
            assert key_info in compressed or compressor.contains_semantic_equivalent(compressed, key_info)
```

### 2. 性能基準測試

#### 響應時間基準測試
```python
# performance_benchmark_test.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class TestPerformanceBenchmark:
    def test_claude_vs_k2_response_time(self):
        """測試Claude vs K2響應時間對比"""
        from core.components.claude_mcp.claude_manager import ClaudeManager
        from core.components.memoryrag_mcp.k2_provider_final import K2Provider
        
        claude_manager = ClaudeManager()
        k2_provider = K2Provider()
        
        test_prompts = [
            "生成一個React組件",
            "解釋這段Python代碼的功能",
            "優化這個SQL查詢",
            "設計一個API接口"
        ]
        
        claude_times = []
        k2_times = []
        
        for prompt in test_prompts:
            # 測試Claude響應時間
            start = time.time()
            claude_response = claude_manager.generate(prompt)
            claude_time = (time.time() - start) * 1000
            claude_times.append(claude_time)
            
            # 測試K2響應時間
            start = time.time()
            k2_response = k2_provider.generate(prompt)
            k2_time = (time.time() - start) * 1000
            k2_times.append(k2_time)
        
        avg_claude_time = sum(claude_times) / len(claude_times)
        avg_k2_time = sum(k2_times) / len(k2_times)
        
        # K2應該比Claude快至少50%
        improvement = (avg_claude_time - avg_k2_time) / avg_claude_time
        assert improvement >= 0.5, f"K2性能提升不足: {improvement:.2f}"
        
        # K2平均響應時間應該<100ms
        assert avg_k2_time < 100, f"K2響應時間過長: {avg_k2_time:.2f}ms"
    
    def test_concurrent_load(self):
        """測試並發負載性能"""
        from core.components.claudeeditor_mcp.main import ClaudeEditorApp
        
        app = ClaudeEditorApp()
        
        def simulate_user_request():
            start = time.time()
            response = app.process_request({
                'type': 'code_generation',
                'prompt': 'Create a simple function',
                'model': 'k2-optimized'
            })
            return (time.time() - start) * 1000
        
        # 模擬50個並發用戶
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(simulate_user_request) for _ in range(50)]
            response_times = [future.result() for future in futures]
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 500, f"平均響應時間過長: {avg_response_time:.2f}ms"
        assert max_response_time < 1000, f"最大響應時間過長: {max_response_time:.2f}ms"
```

#### 內存使用測試
```python
# memory_usage_test.py
import pytest
import psutil
import time
from core.components.claudeeditor_mcp.main import ClaudeEditorApp

class TestMemoryUsage:
    def test_memory_consumption(self):
        """測試內存使用量"""
        process = psutil.Process()
        
        # 記錄啟動前內存
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 啟動ClaudeEditor應用
        app = ClaudeEditorApp()
        app.start()
        
        time.sleep(5)  # 等待完全啟動
        
        # 記錄啟動後內存
        startup_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 執行高負載測試
        for i in range(100):
            app.process_request({
                'type': 'complex_generation',
                'data': f'large_dataset_{i}' * 1000
            })
        
        # 記錄高負載時內存
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        app.stop()
        
        # 驗證內存使用
        startup_overhead = startup_memory - initial_memory
        peak_overhead = peak_memory - initial_memory
        
        assert startup_overhead < 30, f"啟動內存過高: {startup_overhead:.2f}MB"
        assert peak_overhead < 50, f"峰值內存過高: {peak_overhead:.2f}MB"
```

### 3. 集成測試

#### MCP組件協調測試
```python
# mcp_integration_test.py
import pytest
from core.components.mcp_coordinator_mcp.coordinator import MCPCoordinator

class TestMCPIntegration:
    def test_21_mcp_components_status(self):
        """測試21個MCP組件狀態"""
        coordinator = MCPCoordinator()
        
        expected_mcps = [
            'CodeFlow', 'SmartUI', 'Test', 'AG-UI', 'Stagewise', 'Zen', 'X-Masters',
            'MemoryOS', 'MemoryRAG', 'SmartTool', 'Claude', 'Claude Router', 
            'AWS Bedrock', 'DeepSWE', 'Business', 'Docs', 'Command', 
            'Local Adapter', 'MCP Coordinator', 'Claude Collector', 'Smart Intervention'
        ]
        
        status = coordinator.get_all_components_status()
        
        for mcp_name in expected_mcps:
            assert mcp_name in status, f"MCP組件缺失: {mcp_name}"
            assert status[mcp_name]['status'] == 'online', f"MCP組件離線: {mcp_name}"
            assert status[mcp_name]['health'] == 'healthy', f"MCP組件不健康: {mcp_name}"
    
    def test_component_communication(self):
        """測試組件間通信"""
        coordinator = MCPCoordinator()
        
        # 測試CodeFlow -> SmartUI工作流
        result = coordinator.execute_workflow({
            'type': 'code_to_ui',
            'source': 'CodeFlow',
            'target': 'SmartUI',
            'data': 'function createButton() { return <button>Click</button>; }'
        })
        
        assert result.status == 'success'
        assert 'button' in result.ui_component.lower()
        
        # 測試Smart Intervention -> ClaudeEditor切換
        result = coordinator.execute_workflow({
            'type': 'smart_switch',
            'trigger': 'demo_request',
            'source': 'Smart Intervention',
            'target': 'ClaudeEditor'
        })
        
        assert result.status == 'success'
        assert result.switch_time < 100  # ms
```

#### 端到端工作流測試
```python
# e2e_workflow_test.py
import pytest
from core.components.zen_mcp.zen_workflow_engine import ZenWorkflowEngine

class TestE2EWorkflow:
    def test_complete_development_workflow(self):
        """測試完整開發工作流"""
        zen = ZenWorkflowEngine()
        
        # 1. 需求分析階段
        requirements = zen.execute_stage('requirement_analysis', {
            'description': '建立一個電商產品展示頁面'
        })
        
        assert requirements.status == 'completed'
        assert len(requirements.requirements) > 0
        
        # 2. 架構設計階段
        architecture = zen.execute_stage('architecture_design', {
            'requirements': requirements.requirements
        })
        
        assert architecture.status == 'completed'
        assert 'react' in architecture.tech_stack.lower()
        
        # 3. 編碼實現階段
        implementation = zen.execute_stage('code_implementation', {
            'architecture': architecture.design
        })
        
        assert implementation.status == 'completed'
        assert len(implementation.code_files) > 0
        
        # 4. 測試驗證階段
        testing = zen.execute_stage('testing_verification', {
            'code': implementation.code_files
        })
        
        assert testing.status == 'completed'
        assert testing.test_coverage > 0.8
        
        # 5. 部署發布階段
        deployment = zen.execute_stage('deployment_release', {
            'code': implementation.code_files,
            'tests': testing.test_results
        })
        
        assert deployment.status == 'completed'
        assert deployment.deployment_url is not None
        
        # 6. 監控運維階段
        monitoring = zen.execute_stage('monitoring_maintenance', {
            'deployment': deployment.config
        })
        
        assert monitoring.status == 'completed'
        assert monitoring.monitoring_dashboard is not None
```

---

## 🚨 回歸測試

### 關鍵測試失敗監控
```python
# regression_test.py
import pytest
from core.components.test_mcp.critical_test_failure_resolver import CriticalTestResolver

class TestRegression:
    def test_critical_failures_count(self):
        """測試關鍵失敗數量"""
        resolver = CriticalTestResolver()
        
        # 運行完整測試套件
        test_results = resolver.run_all_critical_tests()
        
        failed_tests = [test for test in test_results if test.status == 'failed']
        critical_failures = [test for test in failed_tests if test.priority == 'critical']
        
        assert len(critical_failures) <= 3, f"關鍵測試失敗過多: {len(critical_failures)}"
        
        # 檢查具體失敗原因
        for failure in critical_failures:
            print(f"關鍵失敗: {failure.name} - {failure.error}")
    
    def test_v475_compatibility(self):
        """測試v4.75兼容性"""
        from deploy.v4.75.scripts.compatibility_checker import check_v475_compatibility
        
        compatibility_result = check_v475_compatibility()
        
        assert compatibility_result.data_migration == 'success'
        assert compatibility_result.api_compatibility >= 0.95
        assert len(compatibility_result.breaking_changes) == 0
```

### 無障礙性測試
```python
# accessibility_test.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import axe_selenium_python

class TestAccessibility:
    def setup_method(self):
        """設置無障礙測試環境"""
        chrome_options = Options()
        chrome_options.add_argument("--enable-automation")
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def test_wcag_compliance(self):
        """測試WCAG 2.1合規性"""
        self.driver.get("http://localhost:3000/claudeditor")
        
        # 使用axe-core進行無障礙測試
        axe = axe_selenium_python.Axe(self.driver)
        results = axe.run()
        
        # 檢查無障礙違規
        violations = results.get('violations', [])
        
        # v4.76應該100%無障礙合規
        critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]
        assert len(critical_violations) == 0, f"發現嚴重無障礙問題: {critical_violations}"
        
        # 計算合規率
        total_elements = len(results.get('passes', [])) + len(violations)
        compliant_elements = len(results.get('passes', []))
        compliance_rate = compliant_elements / total_elements if total_elements > 0 else 1
        
        assert compliance_rate >= 1.0, f"無障礙合規率不達標: {compliance_rate:.2%}"
```

---

## 📈 性能監控測試

### 實時性能監控
```python
# performance_monitoring_test.py
import pytest
import time
import threading
from core.components.claudeeditor_mcp.ui.demo.MetricsTrackingDashboard import MetricsTracker

class TestPerformanceMonitoring:
    def test_real_time_metrics_collection(self):
        """測試實時指標收集"""
        tracker = MetricsTracker()
        tracker.start_monitoring()
        
        # 模擬系統負載
        def simulate_load():
            for i in range(100):
                tracker.record_event('api_call', {'duration': 50 + i})
                time.sleep(0.1)
        
        load_thread = threading.Thread(target=simulate_load)
        load_thread.start()
        
        # 監控5秒
        time.sleep(5)
        
        load_thread.join()
        tracker.stop_monitoring()
        
        # 驗證指標收集
        metrics = tracker.get_current_metrics()
        
        assert metrics['total_requests'] >= 50
        assert metrics['avg_response_time'] < 200
        assert metrics['error_rate'] < 0.01
    
    def test_performance_alerting(self):
        """測試性能告警"""
        tracker = MetricsTracker()
        
        # 模擬性能異常
        tracker.record_event('slow_request', {'duration': 5000})  # 5秒慢請求
        tracker.record_event('error', {'type': 'timeout'})
        
        alerts = tracker.check_performance_alerts()
        
        assert len(alerts) > 0
        assert any(alert['type'] == 'high_latency' for alert in alerts)
        assert any(alert['type'] == 'error_spike' for alert in alerts)
```

---

## 🏃‍♂️ 快速測試執行

### 一鍵測試腳本
```bash
#!/bin/bash
# run_v476_tests.sh

echo "🧪 開始PowerAutomation v4.76測試套件..."

# 1. 環境檢查
python deploy/v4.76/tests/test_environment_check.py

# 2. 核心功能測試
echo "🔧 運行核心功能測試..."
pytest deploy/v4.76/tests/smart_intervention_test.py -v
pytest deploy/v4.76/tests/claudeeditor_ui_test.py -v
pytest deploy/v4.76/tests/memoryrag_compression_test.py -v

# 3. 性能基準測試
echo "📊 運行性能基準測試..."
pytest deploy/v4.76/tests/performance_benchmark_test.py -v
pytest deploy/v4.76/tests/memory_usage_test.py -v

# 4. 集成測試
echo "🔗 運行集成測試..."
pytest deploy/v4.76/tests/mcp_integration_test.py -v
pytest deploy/v4.76/tests/e2e_workflow_test.py -v

# 5. 回歸測試
echo "🚨 運行回歸測試..."
pytest deploy/v4.76/tests/regression_test.py -v
pytest deploy/v4.76/tests/accessibility_test.py -v

# 6. 生成測試報告
echo "📋 生成測試報告..."
python deploy/v4.76/tests/generate_test_report.py

echo "✅ 測試完成！查看報告: deploy/v4.76/tests/reports/test_report_$(date +%Y%m%d_%H%M%S).html"
```

### 持續集成配置
```yaml
# .github/workflows/v476_test.yml
name: PowerAutomation v4.76 Testing

on:
  push:
    branches: [ main, v4.76 ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: 18
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        npm install
        
    - name: Run v4.76 test suite
      run: |
        bash deploy/v4.76/tests/run_v476_tests.sh
        
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: test-results-v476
        path: deploy/v4.76/tests/reports/
```

---

## 📊 測試結果分析

### 預期測試結果
```json
{
  "v476_test_results": {
    "performance_benchmarks": {
      "smart_intervention_latency": {
        "target": "<100ms",
        "actual": "85ms",
        "status": "PASS"
      },
      "memoryrag_compression": {
        "target": "<5%", 
        "actual": "2.4%",
        "status": "PASS"
      },
      "k2_accuracy": {
        "target": ">95%",
        "actual": "95.2%", 
        "status": "PASS"
      }
    },
    "integration_tests": {
      "mcp_components": {
        "total": 21,
        "online": 21,
        "status": "PASS"
      },
      "ui_components": {
        "claudeeditor_panels": "PASS",
        "demo_components": "PASS",
        "accessibility": "PASS"
      }
    },
    "regression_tests": {
      "critical_failures": {
        "target": "<5",
        "actual": 3,
        "status": "PASS"
      },
      "v475_compatibility": "PASS"
    }
  }
}
```

### 測試失敗處理
```python
# test_failure_handler.py
class TestFailureHandler:
    def handle_test_failure(self, test_name, error_info):
        """處理測試失敗"""
        if test_name == "smart_intervention_latency":
            return self.fix_latency_issue(error_info)
        elif test_name == "memoryrag_compression":
            return self.fix_compression_issue(error_info)
        elif test_name == "mcp_integration":
            return self.fix_mcp_issue(error_info)
        else:
            return self.generic_failure_handler(error_info)
    
    def fix_latency_issue(self, error_info):
        """修復延遲問題"""
        # 清理緩存
        # 重啟Smart Intervention服務
        # 重新測試
        pass
    
    def generate_failure_report(self, failures):
        """生成失敗報告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_failures': len(failures),
            'critical_failures': len([f for f in failures if f.priority == 'critical']),
            'suggested_actions': self.get_suggested_actions(failures)
        }
        return report
```

---

## 🔍 測試文檔

### 測試用例文檔
- **功能測試用例**: [test_cases/functional_tests.md](test_cases/functional_tests.md)
- **性能測試用例**: [test_cases/performance_tests.md](test_cases/performance_tests.md)
- **無障礙測試用例**: [test_cases/accessibility_tests.md](test_cases/accessibility_tests.md)
- **回歸測試用例**: [test_cases/regression_tests.md](test_cases/regression_tests.md)

### 測試數據
- **測試數據集**: [test_data/](test_data/)
- **基準數據**: [benchmarks/](benchmarks/)
- **模擬數據**: [mocks/](mocks/)

---

**PowerAutomation v4.76 測試套件**  
*最後更新: 2025-07-20*  
*🧪 確保Performance Excellence版本的穩定性和性能突破*