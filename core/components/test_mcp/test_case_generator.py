"""
測試案例生成器 - Test MCP 的核心組件
負責生成測試案例並保存到指定目錄
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)


@dataclass
class GeneratedTestCase:
    """生成的測試案例"""
    id: str
    name: str
    description: str
    category: str  # unit, integration, e2e, performance 等
    test_code: str
    expected_result: str
    dependencies: List[str]
    tags: List[str]
    created_at: str
    mcp_source: str  # 來源 MCP
    
    def to_file_path(self, base_dir: Path) -> Path:
        """生成文件路徑"""
        category_dir = base_dir / self.category
        category_dir.mkdir(parents=True, exist_ok=True)
        return category_dir / f"{self.id}_{self.name.replace(' ', '_')}.py"


class TestCaseGenerator:
    """測試案例生成器"""
    
    def __init__(self, output_dir: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.output_dir = Path(output_dir or "/Users/alexchuang/alexchuangtest/aicore0718/deploy/v4.73/tests/testcases")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def generate_mcp_test_cases(self, mcp_name: str, mcp_info: Dict[str, Any]) -> List[GeneratedTestCase]:
        """為特定 MCP 生成測試案例"""
        self.logger.info(f"為 {mcp_name} 生成測試案例")
        
        test_cases = []
        
        # 1. 生成單元測試
        unit_tests = await self._generate_unit_tests(mcp_name, mcp_info)
        test_cases.extend(unit_tests)
        
        # 2. 生成集成測試
        integration_tests = await self._generate_integration_tests(mcp_name, mcp_info)
        test_cases.extend(integration_tests)
        
        # 3. 生成端到端測試
        e2e_tests = await self._generate_e2e_tests(mcp_name, mcp_info)
        test_cases.extend(e2e_tests)
        
        # 4. 保存測試案例
        for test_case in test_cases:
            await self._save_test_case(test_case)
            
        # 5. 生成測試報告
        await self._generate_test_report(mcp_name, test_cases)
        
        return test_cases
    
    async def _generate_unit_tests(self, mcp_name: str, mcp_info: Dict[str, Any]) -> List[GeneratedTestCase]:
        """生成單元測試"""
        unit_tests = []
        
        # 基礎功能測試
        test_case = GeneratedTestCase(
            id=f"ut_{mcp_name}_{uuid.uuid4().hex[:8]}",
            name=f"{mcp_name}_basic_functionality",
            description=f"測試 {mcp_name} 的基礎功能",
            category="unit",
            test_code=f'''
import pytest
from core.components.{mcp_name} import {mcp_name.title()}Manager

class Test{mcp_name.title()}Basic:
    """測試 {mcp_name} 基礎功能"""
    
    @pytest.fixture
    def manager(self):
        return {mcp_name.title()}Manager()
    
    async def test_initialization(self, manager):
        """測試初始化"""
        await manager.initialize()
        assert manager.is_initialized
        
    async def test_basic_operation(self, manager):
        """測試基本操作"""
        await manager.initialize()
        result = await manager.execute_basic_operation()
        assert result is not None
        assert result.get("status") == "success"
''',
            expected_result="所有基礎功能測試通過",
            dependencies=[f"core.components.{mcp_name}"],
            tags=["unit", mcp_name, "basic"],
            created_at=datetime.now().isoformat(),
            mcp_source=mcp_name
        )
        unit_tests.append(test_case)
        
        return unit_tests
    
    async def _generate_integration_tests(self, mcp_name: str, mcp_info: Dict[str, Any]) -> List[GeneratedTestCase]:
        """生成集成測試"""
        integration_tests = []
        
        # MCP 互動測試
        test_case = GeneratedTestCase(
            id=f"it_{mcp_name}_{uuid.uuid4().hex[:8]}",
            name=f"{mcp_name}_mcp_integration",
            description=f"測試 {mcp_name} 與其他 MCP 的集成",
            category="integration",
            test_code=f'''
import pytest
from core.components.{mcp_name} import {mcp_name.title()}Manager
from core.mcp_zero import mcp_registry

class Test{mcp_name.title()}Integration:
    """測試 {mcp_name} 集成功能"""
    
    async def test_mcp_zero_integration(self):
        """測試與 MCP-Zero 的集成"""
        # 註冊到 MCP-Zero
        await mcp_registry.register_mcp("{mcp_name}")
        
        # 動態加載
        mcp = await mcp_registry.load_mcp("{mcp_name}")
        assert mcp is not None
        
        # 執行操作
        result = await mcp.execute_operation({{"test": "data"}})
        assert result.get("status") == "success"
        
        # 卸載
        await mcp_registry.unload_mcp("{mcp_name}")
''',
            expected_result="MCP 集成測試通過",
            dependencies=[f"core.components.{mcp_name}", "core.mcp_zero"],
            tags=["integration", mcp_name, "mcp-zero"],
            created_at=datetime.now().isoformat(),
            mcp_source=mcp_name
        )
        integration_tests.append(test_case)
        
        return integration_tests
    
    async def _generate_e2e_tests(self, mcp_name: str, mcp_info: Dict[str, Any]) -> List[GeneratedTestCase]:
        """生成端到端測試"""
        e2e_tests = []
        
        # 完整工作流測試
        test_case = GeneratedTestCase(
            id=f"e2e_{mcp_name}_{uuid.uuid4().hex[:8]}",
            name=f"{mcp_name}_complete_workflow",
            description=f"測試 {mcp_name} 的完整工作流",
            category="e2e",
            test_code=f'''
import pytest
from playwright.async_api import async_playwright

class Test{mcp_name.title()}E2E:
    """測試 {mcp_name} 端到端流程"""
    
    async def test_complete_workflow(self):
        """測試完整工作流"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # 訪問應用
            await page.goto("http://localhost:8000")
            
            # 執行 {mcp_name} 相關操作
            await page.click(f"text={mcp_name.title()}")
            await page.wait_for_selector(".{mcp_name}-panel")
            
            # 驗證功能
            assert await page.is_visible(f".{mcp_name}-status")
            
            await browser.close()
''',
            expected_result="端到端測試通過",
            dependencies=[f"core.components.{mcp_name}", "playwright"],
            tags=["e2e", mcp_name, "ui"],
            created_at=datetime.now().isoformat(),
            mcp_source=mcp_name
        )
        e2e_tests.append(test_case)
        
        return e2e_tests
    
    async def _save_test_case(self, test_case: GeneratedTestCase):
        """保存測試案例到文件"""
        file_path = test_case.to_file_path(self.output_dir)
        
        # 保存 Python 測試文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_case.test_code)
            
        # 保存測試元數據
        metadata_path = file_path.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(test_case), f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"測試案例已保存: {file_path}")
    
    async def _generate_test_report(self, mcp_name: str, test_cases: List[GeneratedTestCase]):
        """生成測試報告"""
        report = {
            "mcp_name": mcp_name,
            "generated_at": datetime.now().isoformat(),
            "total_test_cases": len(test_cases),
            "categories": {
                "unit": len([tc for tc in test_cases if tc.category == "unit"]),
                "integration": len([tc for tc in test_cases if tc.category == "integration"]),
                "e2e": len([tc for tc in test_cases if tc.category == "e2e"])
            },
            "test_cases": [asdict(tc) for tc in test_cases]
        }
        
        report_path = self.output_dir / f"{mcp_name}_test_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"測試報告已生成: {report_path}")
    
    async def generate_mcp_zero_test_suite(self):
        """生成 MCP-Zero 完整測試套件"""
        self.logger.info("生成 MCP-Zero 測試套件")
        
        # 從 MCP 註冊表獲取所有 MCP
        from core.mcp_zero import mcp_registry
        
        all_test_cases = []
        
        # 為每個註冊的 MCP 生成測試
        for mcp_name, mcp_meta in mcp_registry.mcp_catalog.items():
            mcp_info = {
                "name": mcp_name,
                "priority": mcp_meta.priority,
                "category": mcp_meta.category,
                "description": mcp_meta.description
            }
            
            test_cases = await self.generate_mcp_test_cases(mcp_name, mcp_info)
            all_test_cases.extend(test_cases)
        
        # 生成總體測試報告
        summary_report = {
            "project": "PowerAutomation v4.73",
            "feature": "MCP-Zero Dynamic Loading",
            "generated_at": datetime.now().isoformat(),
            "total_mcps": len(mcp_registry.mcp_catalog),
            "total_test_cases": len(all_test_cases),
            "test_coverage": {
                "unit": len([tc for tc in all_test_cases if tc.category == "unit"]),
                "integration": len([tc for tc in all_test_cases if tc.category == "integration"]),
                "e2e": len([tc for tc in all_test_cases if tc.category == "e2e"])
            }
        }
        
        summary_path = self.output_dir / "mcp_zero_test_suite_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"MCP-Zero 測試套件生成完成: {len(all_test_cases)} 個測試案例")
        
        return summary_report


# 單例實例
test_case_generator = TestCaseGenerator()