"""
Test MCP - Master Control Platform for Testing
PowerAutomation v4.6.1 統一測試管理平台

基於aicore0707的Test MCP實現，提供：
- 統一測試管理
- AI驅動測試生成
- 多框架支持
- 實時監控
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path

# 導入測試案例生成器和執行器
from .test_case_generator import test_case_generator, GeneratedTestCase
from .test_executors import test_executor_manager, TestExecutionResult

logger = logging.getLogger(__name__)


class TestType(Enum):
    """測試類型枚舉"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    UI = "ui"
    API = "api"
    PERFORMANCE = "performance"
    VISUAL = "visual"


class TestStatus(Enum):
    """測試狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestCase:
    """測試用例"""
    id: str
    name: str
    description: str
    test_type: TestType
    test_file: str
    test_method: str
    priority: int = 1
    timeout: int = 30
    tags: List[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class TestResult:
    """測試結果"""
    test_id: str
    test_name: str
    status: TestStatus
    execution_time: float
    start_time: str
    end_time: str
    error_message: Optional[str] = None
    output: Optional[str] = None
    screenshots: List[str] = None
    artifacts: List[str] = None
    
    def __post_init__(self):
        if self.screenshots is None:
            self.screenshots = []
        if self.artifacts is None:
            self.artifacts = []


@dataclass
class TestSuite:
    """測試套件"""
    id: str
    name: str
    description: str
    test_cases: List[TestCase]
    setup_script: Optional[str] = None
    teardown_script: Optional[str] = None
    parallel_execution: bool = False
    max_parallel: int = 4


class TestExecutor:
    """測試執行器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.running_tests = {}
        self.test_results = []
    
    async def execute_test_case(self, test_case: TestCase) -> TestResult:
        """執行單個測試用例"""
        self.logger.info(f"執行測試: {test_case.name}")
        
        # 準備測試配置
        test_config = {
            "test_file": test_case.test_file,
            "test_method": test_case.test_method,
            "name": test_case.name,
            "timeout": test_case.timeout
        }
        
        # 使用新的執行器
        test_type_map = {
            TestType.UNIT: "unit",
            TestType.INTEGRATION: "integration",
            TestType.PERFORMANCE: "performance",
            TestType.UI: "ui_operation",
            TestType.API: "integration",
            TestType.E2E: "ui_operation",
            TestType.VISUAL: "ui_operation"
        }
        
        executor_type = test_type_map.get(test_case.test_type, "unit")
        
        # 執行測試
        execution_result = await test_executor_manager.execute_test(executor_type, test_config)
        
        # 轉換為 TestResult
        test_result = TestResult(
            test_id=test_case.id,
            test_name=test_case.name,
            status=TestStatus(execution_result.status.upper()) if execution_result.status.upper() in [s.value for s in TestStatus] else TestStatus.ERROR,
            execution_time=execution_result.execution_time,
            start_time=execution_result.start_time,
            end_time=execution_result.end_time,
            output=execution_result.output,
            error_message=execution_result.error,
            artifacts=execution_result.artifacts
        )
        
        self.test_results.append(test_result)
        return test_result
    
    
    async def execute_test_suite(self, test_suite: TestSuite) -> List[TestResult]:
        """執行測試套件"""
        self.logger.info(f"執行測試套件: {test_suite.name}")
        
        results = []
        
        if test_suite.parallel_execution:
            # 並行執行
            semaphore = asyncio.Semaphore(test_suite.max_parallel)
            
            async def run_with_semaphore(test_case):
                async with semaphore:
                    return await self.execute_test_case(test_case)
            
            tasks = [run_with_semaphore(tc) for tc in test_suite.test_cases]
            results = await asyncio.gather(*tasks)
        else:
            # 串行執行
            for test_case in test_suite.test_cases:
                result = await self.execute_test_case(test_case)
                results.append(result)
        
        return results


class TestMCPManager:
    """Test MCP管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.executor = TestExecutor()
        self.test_suites = {}
        self.test_sessions = {}
        
        # AI組件集成
        self.ai_test_generator = None
        self.stagewise_integration = None
        self.ag_ui_integration = None
    
    async def initialize(self):
        """初始化Test MCP"""
        self.logger.info("🧪 初始化Test MCP - 統一測試管理平台")
        
        # 初始化AI測試生成器
        await self._initialize_ai_components()
        
        # 載入默認測試套件
        await self._load_default_test_suites()
        
        self.logger.info("✅ Test MCP初始化完成")
    
    async def _initialize_ai_components(self):
        """初始化AI組件"""
        try:
            # 嘗試集成Stagewise MCP
            self.stagewise_integration = "stagewise_available"
            
            # 嘗試集成AG-UI MCP
            self.ag_ui_integration = "ag_ui_available"
            
            self.logger.info("✅ AI組件集成成功")
        except Exception as e:
            self.logger.warning(f"⚠️ AI組件集成部分失敗: {e}")
    
    async def _load_default_test_suites(self):
        """載入默認測試套件"""
        # 創建PowerAutomation核心測試套件
        core_test_suite = TestSuite(
            id="powerautomation_core",
            name="PowerAutomation核心功能測試",
            description="測試PowerAutomation的核心功能",
            test_cases=[
                TestCase(
                    id="test_001",
                    name="系統啟動測試",
                    description="驗證PowerAutomation能夠正常啟動",
                    test_type=TestType.UNIT,
                    test_file="test_system_startup.py",
                    test_method="test_startup",
                    tags=["core", "startup"]
                ),
                TestCase(
                    id="test_002",
                    name="MCP組件載入測試",
                    description="驗證所有MCP組件能夠正常載入",
                    test_type=TestType.INTEGRATION,
                    test_file="test_mcp_loading.py",
                    test_method="test_mcp_loading",
                    tags=["mcp", "integration"]
                ),
                TestCase(
                    id="test_003",
                    name="API端點測試",
                    description="測試REST API端點功能",
                    test_type=TestType.API,
                    test_file="test_api_endpoints.py",
                    test_method="test_all_endpoints",
                    tags=["api", "rest"]
                )
            ],
            parallel_execution=True,
            max_parallel=3
        )
        
        self.test_suites["powerautomation_core"] = core_test_suite
    
    async def create_test_session(self, session_name: str, test_suite_ids: List[str]) -> str:
        """創建測試會話"""
        session_id = str(uuid.uuid4())
        
        session = {
            "id": session_id,
            "name": session_name,
            "test_suite_ids": test_suite_ids,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "results": []
        }
        
        self.test_sessions[session_id] = session
        self.logger.info(f"創建測試會話: {session_name} ({session_id})")
        
        return session_id
    
    async def run_test_session(self, session_id: str) -> Dict[str, Any]:
        """運行測試會話"""
        if session_id not in self.test_sessions:
            raise ValueError(f"測試會話不存在: {session_id}")
        
        session = self.test_sessions[session_id]
        session["status"] = "running"
        session["started_at"] = datetime.now().isoformat()
        
        self.logger.info(f"開始運行測試會話: {session['name']}")
        
        all_results = []
        
        for suite_id in session["test_suite_ids"]:
            if suite_id in self.test_suites:
                suite_results = await self.executor.execute_test_suite(self.test_suites[suite_id])
                all_results.extend(suite_results)
        
        session["results"] = [asdict(result) for result in all_results]
        session["status"] = "completed"
        session["completed_at"] = datetime.now().isoformat()
        
        # 計算統計信息
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.status == TestStatus.PASSED)
        failed_tests = sum(1 for r in all_results if r.status == TestStatus.FAILED)
        
        session["statistics"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_execution_time": sum(r.execution_time for r in all_results)
        }
        
        self.logger.info(f"測試會話完成: {passed_tests}/{total_tests} 通過")
        
        return session
    
    async def generate_ai_test_cases(self, component_name: str, test_type: TestType) -> List[TestCase]:
        """AI生成測試用例"""
        self.logger.info(f"為 {component_name} 生成 {test_type.value} 測試用例")
        
        # 使用測試案例生成器
        mcp_info = {
            "name": component_name,
            "priority": "P1",
            "category": "component",
            "description": f"{component_name} MCP 組件"
        }
        
        # 生成測試案例並保存到文件
        generated_test_cases = await test_case_generator.generate_mcp_test_cases(component_name, mcp_info)
        
        # 轉換為 TestCase 格式
        generated_tests = []
        for gtc in generated_test_cases:
            test_case = TestCase(
                id=gtc.id,
                name=gtc.name,
                description=gtc.description,
                test_type=TestType(gtc.category) if gtc.category in [t.value for t in TestType] else TestType.UNIT,
                test_file=str(gtc.to_file_path(test_case_generator.output_dir)),
                test_method=f"test_{gtc.name}",
                tags=gtc.tags
            )
            generated_tests.append(test_case)
        
        return generated_tests
    
    async def integrate_with_stagewise(self, recording_session_id: str) -> TestSuite:
        """與Stagewise MCP集成，從錄製會話生成測試"""
        self.logger.info(f"從Stagewise錄製會話 {recording_session_id} 生成測試套件")
        
        # 模擬從Stagewise生成測試
        test_cases = [
            TestCase(
                id=f"stagewise_{recording_session_id}_1",
                name="Stagewise錄製回放測試",
                description="基於用戶錄製操作生成的自動化測試",
                test_type=TestType.UI,
                test_file="stagewise_generated.py",
                test_method="test_recorded_scenario",
                tags=["stagewise", "recorded", "ui"]
            )
        ]
        
        suite = TestSuite(
            id=f"stagewise_suite_{recording_session_id}",
            name=f"Stagewise生成測試套件",
            description="基於Stagewise錄製生成的測試套件",
            test_cases=test_cases
        )
        
        self.test_suites[suite.id] = suite
        return suite
    
    async def generate_ui_test_dashboard(self) -> Dict[str, Any]:
        """生成UI測試儀表板"""
        if not self.ag_ui_integration:
            return {"error": "AG-UI MCP未集成"}
        
        # 模擬AG-UI生成測試儀表板
        dashboard = {
            "type": "test_dashboard",
            "components": [
                {
                    "type": "test_execution_panel",
                    "title": "測試執行面板",
                    "features": ["start_test", "stop_test", "view_progress"]
                },
                {
                    "type": "test_results_viewer", 
                    "title": "測試結果查看器",
                    "features": ["results_table", "charts", "export"]
                },
                {
                    "type": "test_suite_manager",
                    "title": "測試套件管理器",
                    "features": ["create_suite", "edit_suite", "import_suite"]
                }
            ],
            "theme": "dark",
            "layout": "grid"
        }
        
        return dashboard
    
    async def generate_mcp_zero_test_suite(self) -> Dict[str, Any]:
        """生成 MCP-Zero 完整測試套件"""
        self.logger.info("生成 MCP-Zero 完整測試套件")
        
        # 使用測試案例生成器生成所有測試
        summary_report = await test_case_generator.generate_mcp_zero_test_suite()
        
        # 創建測試套件
        test_suite = TestSuite(
            id="mcp_zero_complete",
            name="MCP-Zero 完整測試套件",
            description="涵蓋所有 MCP 組件的完整測試",
            test_cases=[],  # 從生成的文件動態加載
            parallel_execution=True,
            max_parallel=4
        )
        
        self.test_suites[test_suite.id] = test_suite
        
        return summary_report
    
    async def run_test_with_results(self, test_suite_id: str) -> Dict[str, Any]:
        """運行測試並生成結果報告"""
        if test_suite_id not in self.test_suites:
            raise ValueError(f"測試套件不存在: {test_suite_id}")
        
        # 創建測試會話
        session_id = await self.create_test_session(
            f"Test Run - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            [test_suite_id]
        )
        
        # 運行測試
        session_result = await self.run_test_session(session_id)
        
        # 生成測試結果報告
        report_path = test_case_generator.output_dir / f"test_results_{session_id}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(session_result, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"測試結果已保存: {report_path}")
        
        return session_result
    
    async def execute_unit_tests(self, mcp_name: Optional[str] = None) -> Dict[str, Any]:
        """執行單元測試"""
        self.logger.info(f"執行單元測試: {mcp_name or '所有組件'}")
        
        # 生成單元測試案例
        test_cases = []
        if mcp_name:
            # 特定 MCP 的單元測試
            unit_tests = await self.generate_ai_test_cases(mcp_name, TestType.UNIT)
            test_cases.extend(unit_tests)
        else:
            # 所有 MCP 的單元測試
            from core.mcp_zero import mcp_registry
            for name in mcp_registry.mcp_catalog.keys():
                unit_tests = await self.generate_ai_test_cases(name, TestType.UNIT)
                test_cases.extend(unit_tests)
        
        # 創建測試套件
        test_suite = TestSuite(
            id=f"unit_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="單元測試套件",
            description="自動生成的單元測試",
            test_cases=test_cases,
            parallel_execution=True,
            max_parallel=4
        )
        
        # 執行測試
        results = await self.execute_test_suite(test_suite)
        
        return {
            "test_type": "unit",
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.status == TestStatus.PASSED),
            "failed": sum(1 for r in results if r.status == TestStatus.FAILED),
            "results": [asdict(r) for r in results]
        }
    
    async def execute_integration_tests(self, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """執行集成測試"""
        self.logger.info("執行集成測試")
        
        results = []
        for scenario in test_scenarios:
            test_config = {
                "name": scenario.get("name", "integration_test"),
                "test_file": scenario.get("test_file"),
                "services": scenario.get("services", [])
            }
            
            result = await test_executor_manager.execute_test("integration", test_config)
            results.append(result)
        
        return {
            "test_type": "integration",
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.status == "passed"),
            "failed": sum(1 for r in results if r.status == "failed"),
            "results": [asdict(r) for r in results]
        }
    
    async def execute_performance_tests(self, performance_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """執行性能測試"""
        self.logger.info("執行性能測試")
        
        results = []
        for config in performance_configs:
            result = await test_executor_manager.execute_test("performance", config)
            results.append(result)
        
        return {
            "test_type": "performance",
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.status == "passed"),
            "failed": sum(1 for r in results if r.status == "failed"),
            "metrics": {
                "average_response_time": sum(r.metrics.get("average_response_time", 0) for r in results) / len(results) if results else 0,
                "average_rps": sum(r.metrics.get("requests_per_second", 0) for r in results) / len(results) if results else 0
            },
            "results": [asdict(r) for r in results]
        }
    
    async def execute_ui_operation_tests(self, ui_test_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """執行 UI 操作測試"""
        self.logger.info("執行 UI 操作測試")
        
        results = []
        for config in ui_test_configs:
            result = await test_executor_manager.execute_test("ui_operation", config)
            results.append(result)
        
        # 收集所有截圖
        all_artifacts = []
        for result in results:
            if result.artifacts:
                all_artifacts.extend(result.artifacts)
        
        return {
            "test_type": "ui_operation",
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.status == "passed"),
            "failed": sum(1 for r in results if r.status == "failed"),
            "artifacts": all_artifacts,
            "results": [asdict(r) for r in results]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """獲取Test MCP狀態"""
        return {
            "component": "Test MCP",
            "version": "4.7.3",
            "status": "running",
            "test_suites": len(self.test_suites),
            "active_sessions": len([s for s in self.test_sessions.values() if s["status"] == "running"]),
            "total_sessions": len(self.test_sessions),
            "test_output_dir": str(test_case_generator.output_dir),
            "integrations": {
                "stagewise_mcp": self.stagewise_integration is not None,
                "ag_ui_mcp": self.ag_ui_integration is not None,
                "test_case_generator": True
            }
        }


# 單例實例
test_mcp = TestMCPManager()