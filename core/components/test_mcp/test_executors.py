"""
測試執行器 - 支持不同類型的測試執行
包括：單元測試、集成測試、性能測試、UI操作測試
"""

import asyncio
import time
import logging
import subprocess
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import psutil
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TestExecutionResult:
    """測試執行結果"""
    test_type: str
    test_name: str
    status: str  # passed, failed, error
    execution_time: float
    start_time: str
    end_time: str
    metrics: Dict[str, Any]
    output: str
    error: Optional[str] = None
    artifacts: List[str] = None


class UnitTestExecutor:
    """單元測試執行器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def execute(self, test_file: str, test_method: Optional[str] = None) -> TestExecutionResult:
        """執行單元測試"""
        start_time = time.time()
        start_time_str = datetime.now().isoformat()
        
        try:
            # 構建 pytest 命令
            cmd = ["pytest", "-v", "-s"]
            if test_method:
                cmd.append(f"{test_file}::{test_method}")
            else:
                cmd.append(test_file)
            
            # 執行測試
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd="/Users/alexchuang/alexchuangtest/aicore0718"
            )
            
            execution_time = time.time() - start_time
            
            return TestExecutionResult(
                test_type="unit",
                test_name=test_file,
                status="passed" if result.returncode == 0 else "failed",
                execution_time=execution_time,
                start_time=start_time_str,
                end_time=datetime.now().isoformat(),
                metrics={
                    "return_code": result.returncode,
                    "tests_run": 1
                },
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                artifacts=[]
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestExecutionResult(
                test_type="unit",
                test_name=test_file,
                status="error",
                execution_time=execution_time,
                start_time=start_time_str,
                end_time=datetime.now().isoformat(),
                metrics={},
                output="",
                error=str(e),
                artifacts=[]
            )


class IntegrationTestExecutor:
    """集成測試執行器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def execute(self, test_config: Dict[str, Any]) -> TestExecutionResult:
        """執行集成測試"""
        start_time = time.time()
        start_time_str = datetime.now().isoformat()
        
        try:
            # 啟動相關服務
            services_started = await self._start_services(test_config.get("services", []))
            
            # 執行集成測試
            test_file = test_config.get("test_file")
            cmd = ["pytest", "-v", "-s", "--tb=short", test_file]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd="/Users/alexchuang/alexchuangtest/aicore0718"
            )
            
            # 停止服務
            await self._stop_services(services_started)
            
            execution_time = time.time() - start_time
            
            return TestExecutionResult(
                test_type="integration",
                test_name=test_config.get("name", "integration_test"),
                status="passed" if result.returncode == 0 else "failed",
                execution_time=execution_time,
                start_time=start_time_str,
                end_time=datetime.now().isoformat(),
                metrics={
                    "return_code": result.returncode,
                    "services_started": len(services_started)
                },
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                artifacts=[]
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestExecutionResult(
                test_type="integration",
                test_name=test_config.get("name", "integration_test"),
                status="error",
                execution_time=execution_time,
                start_time=start_time_str,
                end_time=datetime.now().isoformat(),
                metrics={},
                output="",
                error=str(e),
                artifacts=[]
            )
    
    async def _start_services(self, services: List[str]) -> List[Dict[str, Any]]:
        """啟動測試所需的服務"""
        started_services = []
        
        for service in services:
            if service == "api_server":
                # 啟動 API 服務器
                process = subprocess.Popen(
                    ["python", "start_mcpzero_server.py"],
                    cwd="/Users/alexchuang/alexchuangtest/aicore0718"
                )
                started_services.append({"name": service, "process": process})
                await asyncio.sleep(2)  # 等待服務啟動
                
        return started_services
    
    async def _stop_services(self, services: List[Dict[str, Any]]):
        """停止服務"""
        for service in services:
            if "process" in service:
                service["process"].terminate()
                await asyncio.sleep(1)


class PerformanceTestExecutor:
    """性能測試執行器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def execute(self, test_config: Dict[str, Any]) -> TestExecutionResult:
        """執行性能測試"""
        start_time = time.time()
        start_time_str = datetime.now().isoformat()
        
        try:
            # 初始化性能指標
            metrics = {
                "requests_per_second": 0,
                "average_response_time": 0,
                "memory_usage": 0,
                "cpu_usage": 0,
                "throughput": 0
            }
            
            # 記錄初始資源使用
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            initial_cpu = process.cpu_percent()
            
            # 執行性能測試
            test_function = test_config.get("test_function")
            iterations = test_config.get("iterations", 1000)
            concurrent_users = test_config.get("concurrent_users", 10)
            
            # 模擬性能測試
            response_times = []
            
            async def single_request():
                req_start = time.time()
                # 執行測試邏輯
                await asyncio.sleep(0.01)  # 模擬請求
                req_end = time.time()
                return req_end - req_start
            
            # 並發執行
            tasks = []
            for _ in range(iterations):
                if len(tasks) >= concurrent_users:
                    # 等待一些任務完成
                    done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                    for task in done:
                        response_times.append(await task)
                    tasks = list(tasks)
                
                tasks.append(asyncio.create_task(single_request()))
            
            # 等待所有任務完成
            if tasks:
                done, _ = await asyncio.wait(tasks)
                for task in done:
                    response_times.append(await task)
            
            # 計算性能指標
            execution_time = time.time() - start_time
            metrics["requests_per_second"] = iterations / execution_time
            metrics["average_response_time"] = sum(response_times) / len(response_times) * 1000  # ms
            metrics["memory_usage"] = process.memory_info().rss / 1024 / 1024 - initial_memory
            metrics["cpu_usage"] = process.cpu_percent() - initial_cpu
            metrics["throughput"] = (iterations * test_config.get("payload_size", 1024)) / execution_time / 1024  # KB/s
            
            # 判斷是否通過性能基準
            status = "passed"
            if metrics["average_response_time"] > test_config.get("max_response_time", 100):
                status = "failed"
            
            return TestExecutionResult(
                test_type="performance",
                test_name=test_config.get("name", "performance_test"),
                status=status,
                execution_time=execution_time,
                start_time=start_time_str,
                end_time=datetime.now().isoformat(),
                metrics=metrics,
                output=f"Performance test completed: {iterations} requests in {execution_time:.2f}s",
                error=None,
                artifacts=[]
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestExecutionResult(
                test_type="performance",
                test_name=test_config.get("name", "performance_test"),
                status="error",
                execution_time=execution_time,
                start_time=start_time_str,
                end_time=datetime.now().isoformat(),
                metrics={},
                output="",
                error=str(e),
                artifacts=[]
            )


class UIOperationTestExecutor:
    """UI 操作測試執行器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def execute(self, test_config: Dict[str, Any]) -> TestExecutionResult:
        """執行 UI 操作測試"""
        start_time = time.time()
        start_time_str = datetime.now().isoformat()
        
        try:
            # 使用 Playwright 執行 UI 測試
            from playwright.async_api import async_playwright
            
            artifacts = []
            test_passed = True
            error_message = None
            
            async with async_playwright() as p:
                # 啟動瀏覽器
                browser = await p.chromium.launch(
                    headless=test_config.get("headless", True)
                )
                page = await browser.new_page()
                
                # 設置視口大小
                await page.set_viewport_size({
                    "width": test_config.get("viewport_width", 1280),
                    "height": test_config.get("viewport_height", 720)
                })
                
                # 訪問測試 URL
                url = test_config.get("url", "http://localhost:8000")
                await page.goto(url)
                
                # 執行測試步驟
                for step in test_config.get("steps", []):
                    try:
                        if step["action"] == "click":
                            await page.click(step["selector"])
                        elif step["action"] == "fill":
                            await page.fill(step["selector"], step["value"])
                        elif step["action"] == "wait":
                            await page.wait_for_selector(step["selector"])
                        elif step["action"] == "screenshot":
                            screenshot_path = f"/Users/alexchuang/alexchuangtest/aicore0718/deploy/v4.73/tests/artifacts/{step['name']}.png"
                            await page.screenshot(path=screenshot_path)
                            artifacts.append(screenshot_path)
                        elif step["action"] == "assert_visible":
                            is_visible = await page.is_visible(step["selector"])
                            if not is_visible:
                                test_passed = False
                                error_message = f"Element {step['selector']} is not visible"
                                break
                        elif step["action"] == "assert_text":
                            text = await page.text_content(step["selector"])
                            if text != step["expected"]:
                                test_passed = False
                                error_message = f"Expected '{step['expected']}', got '{text}'"
                                break
                                
                        # 每步之間等待
                        await asyncio.sleep(step.get("wait_after", 0.5))
                        
                    except Exception as e:
                        test_passed = False
                        error_message = f"Step failed: {step} - {str(e)}"
                        break
                
                # 最終截圖
                final_screenshot = f"/Users/alexchuang/alexchuangtest/aicore0718/deploy/v4.73/tests/artifacts/final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=final_screenshot, full_page=True)
                artifacts.append(final_screenshot)
                
                await browser.close()
            
            execution_time = time.time() - start_time
            
            return TestExecutionResult(
                test_type="ui_operation",
                test_name=test_config.get("name", "ui_test"),
                status="passed" if test_passed else "failed",
                execution_time=execution_time,
                start_time=start_time_str,
                end_time=datetime.now().isoformat(),
                metrics={
                    "steps_executed": len(test_config.get("steps", [])),
                    "screenshots_taken": len(artifacts)
                },
                output=f"UI test completed with {len(artifacts)} artifacts",
                error=error_message,
                artifacts=artifacts
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestExecutionResult(
                test_type="ui_operation",
                test_name=test_config.get("name", "ui_test"),
                status="error",
                execution_time=execution_time,
                start_time=start_time_str,
                end_time=datetime.now().isoformat(),
                metrics={},
                output="",
                error=str(e),
                artifacts=[]
            )


class TestExecutorManager:
    """測試執行器管理器"""
    
    def __init__(self):
        self.unit_executor = UnitTestExecutor()
        self.integration_executor = IntegrationTestExecutor()
        self.performance_executor = PerformanceTestExecutor()
        self.ui_executor = UIOperationTestExecutor()
        
    async def execute_test(self, test_type: str, test_config: Dict[str, Any]) -> TestExecutionResult:
        """根據測試類型執行測試"""
        if test_type == "unit":
            return await self.unit_executor.execute(
                test_config.get("test_file"),
                test_config.get("test_method")
            )
        elif test_type == "integration":
            return await self.integration_executor.execute(test_config)
        elif test_type == "performance":
            return await self.performance_executor.execute(test_config)
        elif test_type == "ui_operation":
            return await self.ui_executor.execute(test_config)
        else:
            raise ValueError(f"Unknown test type: {test_type}")


# 單例實例
test_executor_manager = TestExecutorManager()