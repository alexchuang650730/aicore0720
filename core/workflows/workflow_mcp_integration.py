"""
工作流與 MCP 深度集成
將所有 P1 MCP 完全整合到六大工作流系統中
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 導入所有 P1 MCP
from ..components.test_mcp import test_mcp
from ..components.docs_mcp import docs_manager
from ..components.business_mcp import business_manager
from ..components.codeflow_mcp.codeflow_manager import codeflow_mcp
from ..components.smartui_mcp import smartui_manager
from ..components.claude_router_mcp import claude_router
from ..components.command_mcp import command_manager
from ..components.memoryos_mcp import memory_engine
from ..mcp_zero import mcp_registry, mcp_zero_engine

logger = logging.getLogger(__name__)


class MCPIntegrationLevel(Enum):
    """MCP 集成級別"""
    BASIC = "basic"          # 基礎集成 (60%)
    ADVANCED = "advanced"    # 高級集成 (80%)
    FULL = "full"           # 完全集成 (100%)


@dataclass
class MCPWorkflowMapping:
    """MCP 與工作流的映射關係"""
    mcp_name: str
    workflow_stages: List[str]
    integration_level: MCPIntegrationLevel
    capabilities: List[str]


class WorkflowMCPIntegrator:
    """工作流 MCP 集成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # P1 MCP 映射到工作流
        self.mcp_mappings = {
            # 1. Test MCP - 深度集成到測試驗證工作流
            "test_mcp": MCPWorkflowMapping(
                mcp_name="test_mcp",
                workflow_stages=[
                    "automated_testing_validation.*",  # 所有測試階段
                    "continuous_quality_assurance.code_analysis",
                    "goal_driven_development.goal_validation"
                ],
                integration_level=MCPIntegrationLevel.FULL,
                capabilities=[
                    "自動生成測試案例",
                    "執行多類型測試",
                    "生成測試報告",
                    "測試覆蓋率分析"
                ]
            ),
            
            # 2. Docs MCP - 深度集成到所有工作流的文檔階段
            "docs_mcp": MCPWorkflowMapping(
                mcp_name="docs_mcp",
                workflow_stages=[
                    "*.documentation",  # 所有工作流的文檔階段
                    "intelligent_code_generation.documentation",
                    "adaptive_learning_optimization.feedback_loop"
                ],
                integration_level=MCPIntegrationLevel.FULL,
                capabilities=[
                    "自動生成 API 文檔",
                    "更新架構文檔",
                    "版本化文檔管理",
                    "生成用戶指南"
                ]
            ),
            
            # 3. Business MCP - 集成到目標驅動和優化工作流
            "business_mcp": MCPWorkflowMapping(
                mcp_name="business_mcp",
                workflow_stages=[
                    "goal_driven_development.goal_analysis",
                    "goal_driven_development.requirement_decomposition",
                    "adaptive_learning_optimization.optimization_strategy",
                    "smart_deployment_ops.ops_optimization"
                ],
                integration_level=MCPIntegrationLevel.FULL,
                capabilities=[
                    "ROI 分析",
                    "定價策略生成",
                    "市場分析",
                    "財務預測"
                ]
            ),
            
            # 4. CodeFlow MCP - 核心代碼生成工作流
            "codeflow_mcp": MCPWorkflowMapping(
                mcp_name="codeflow_mcp",
                workflow_stages=[
                    "intelligent_code_generation.*",  # 所有代碼生成階段
                    "goal_driven_development.development_execution",
                    "continuous_quality_assurance.code_analysis"
                ],
                integration_level=MCPIntegrationLevel.FULL,
                capabilities=[
                    "代碼到規格轉換",
                    "智能代碼生成",
                    "代碼優化建議",
                    "多語言支持"
                ]
            ),
            
            # 5. SmartUI MCP - UI 生成和測試
            "smartui_mcp": MCPWorkflowMapping(
                mcp_name="smartui_mcp",
                workflow_stages=[
                    "intelligent_code_generation.code_generation",
                    "automated_testing_validation.e2e_testing",
                    "goal_driven_development.development_execution"
                ],
                integration_level=MCPIntegrationLevel.FULL,
                capabilities=[
                    "動態 UI 生成",
                    "響應式設計",
                    "UI 測試自動化",
                    "多平台適配"
                ]
            ),
            
            # 6. Claude Router MCP - 智能路由和 K2 集成
            "claude_router_mcp": MCPWorkflowMapping(
                mcp_name="claude_router_mcp",
                workflow_stages=[
                    "*.*",  # 所有工作流的所有階段
                ],
                integration_level=MCPIntegrationLevel.FULL,
                capabilities=[
                    "K2 模型路由",
                    "成本優化",
                    "智能模型選擇",
                    "使用統計追蹤"
                ]
            ),
            
            # 7. Command MCP - 命令執行和自動化
            "command_mcp": MCPWorkflowMapping(
                mcp_name="command_mcp",
                workflow_stages=[
                    "smart_deployment_ops.*",  # 所有部署階段
                    "automated_testing_validation.*",
                    "goal_driven_development.development_execution"
                ],
                integration_level=MCPIntegrationLevel.FULL,
                capabilities=[
                    "命令執行",
                    "腳本自動化",
                    "環境管理",
                    "部署自動化"
                ]
            ),
            
            # 8. MemoryOS MCP - 記憶和學習
            "memoryos_mcp": MCPWorkflowMapping(
                mcp_name="memoryos_mcp",
                workflow_stages=[
                    "adaptive_learning_optimization.*",  # 所有學習階段
                    "goal_driven_development.goal_analysis",
                    "continuous_quality_assurance.continuous_improvement"
                ],
                integration_level=MCPIntegrationLevel.FULL,
                capabilities=[
                    "上下文記憶",
                    "學習模式識別",
                    "知識持久化",
                    "個性化優化"
                ]
            )
        }
        
        self.logger.info("🔌 工作流 MCP 集成器初始化完成")
    
    async def integrate_mcp_to_workflow(self, workflow_type: str, stage: str) -> Dict[str, Any]:
        """將 MCP 集成到特定工作流階段"""
        self.logger.info(f"集成 MCP 到工作流: {workflow_type}.{stage}")
        
        # 查找適用的 MCP
        applicable_mcps = []
        
        for mcp_name, mapping in self.mcp_mappings.items():
            for pattern in mapping.workflow_stages:
                if self._matches_pattern(f"{workflow_type}.{stage}", pattern):
                    applicable_mcps.append(mcp_name)
                    break
        
        # 動態加載需要的 MCP
        loaded_mcps = {}
        for mcp_name in applicable_mcps:
            mcp_instance = await mcp_registry.load_mcp(mcp_name)
            if mcp_instance:
                loaded_mcps[mcp_name] = mcp_instance
        
        return {
            "workflow": workflow_type,
            "stage": stage,
            "integrated_mcps": list(loaded_mcps.keys()),
            "mcp_instances": loaded_mcps
        }
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """檢查文本是否匹配模式"""
        if pattern == "*.*":
            return True
        
        parts = pattern.split(".")
        text_parts = text.split(".")
        
        if len(parts) != len(text_parts):
            return False
        
        for i, part in enumerate(parts):
            if part == "*":
                continue
            if part != text_parts[i]:
                return False
        
        return True
    
    async def execute_mcp_in_workflow(self, workflow_context: Dict[str, Any], 
                                    mcp_name: str, operation: str, 
                                    params: Dict[str, Any]) -> Dict[str, Any]:
        """在工作流中執行 MCP 操作"""
        self.logger.info(f"執行 MCP 操作: {mcp_name}.{operation}")
        
        # 獲取 MCP 實例
        mcp_instance = workflow_context.get("mcp_instances", {}).get(mcp_name)
        
        if not mcp_instance:
            # 動態加載
            mcp_instance = await mcp_registry.load_mcp(mcp_name)
        
        if not mcp_instance:
            return {"error": f"MCP {mcp_name} 不可用"}
        
        # 執行操作
        try:
            if mcp_name == "test_mcp":
                return await self._execute_test_mcp(mcp_instance, operation, params)
            elif mcp_name == "docs_mcp":
                return await self._execute_docs_mcp(mcp_instance, operation, params)
            elif mcp_name == "business_mcp":
                return await self._execute_business_mcp(mcp_instance, operation, params)
            elif mcp_name == "codeflow_mcp":
                return await self._execute_codeflow_mcp(mcp_instance, operation, params)
            elif mcp_name == "smartui_mcp":
                return await self._execute_smartui_mcp(mcp_instance, operation, params)
            elif mcp_name == "claude_router_mcp":
                return await self._execute_claude_router_mcp(mcp_instance, operation, params)
            elif mcp_name == "command_mcp":
                return await self._execute_command_mcp(mcp_instance, operation, params)
            elif mcp_name == "memoryos_mcp":
                return await self._execute_memoryos_mcp(mcp_instance, operation, params)
            else:
                return {"error": f"未知的 MCP: {mcp_name}"}
                
        except Exception as e:
            self.logger.error(f"執行 MCP 操作失敗: {e}")
            return {"error": str(e)}
    
    async def _execute_test_mcp(self, mcp_instance, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 Test MCP 操作"""
        if operation == "generate_test_cases":
            return await test_mcp.generate_ai_test_cases(
                params.get("component_name"),
                params.get("test_type")
            )
        elif operation == "run_tests":
            if params.get("test_type") == "unit":
                return await test_mcp.execute_unit_tests(params.get("mcp_name"))
            elif params.get("test_type") == "integration":
                return await test_mcp.execute_integration_tests(params.get("scenarios", []))
            elif params.get("test_type") == "performance":
                return await test_mcp.execute_performance_tests(params.get("configs", []))
            elif params.get("test_type") == "ui":
                return await test_mcp.execute_ui_operation_tests(params.get("ui_configs", []))
        elif operation == "generate_test_suite":
            return await test_mcp.generate_mcp_zero_test_suite()
        
        return {"error": f"未知的 Test MCP 操作: {operation}"}
    
    async def _execute_docs_mcp(self, mcp_instance, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 Docs MCP 操作"""
        if operation == "generate_api_docs":
            return await docs_manager.generate_api_documentation(params.get("mcp_name"))
        elif operation == "generate_user_guide":
            return await docs_manager.generate_user_guide(
                params.get("topic"),
                params.get("content_outline")
            )
        elif operation == "generate_architecture_docs":
            return await docs_manager.generate_architecture_docs()
        elif operation == "generate_changelog":
            return await docs_manager.generate_changelog(
                params.get("version"),
                params.get("changes", [])
            )
        elif operation == "update_readme":
            return await docs_manager.update_root_readme(
                params.get("update_type"),
                params.get("content")
            )
        
        return {"error": f"未知的 Docs MCP 操作: {operation}"}
    
    async def _execute_business_mcp(self, mcp_instance, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 Business MCP 操作"""
        if operation == "generate_pricing_strategy":
            return await business_manager.generate_pricing_strategy()
        elif operation == "generate_roi_analysis":
            return await business_manager.generate_roi_analysis(params.get("scenario"))
        elif operation == "generate_market_analysis":
            return await business_manager.generate_market_analysis()
        elif operation == "generate_financial_projection":
            return await business_manager.generate_financial_projection(params.get("years", 3))
        elif operation == "generate_customer_acquisition":
            return await business_manager.generate_customer_acquisition_strategy()
        
        return {"error": f"未知的 Business MCP 操作: {operation}"}
    
    async def _execute_codeflow_mcp(self, mcp_instance, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 CodeFlow MCP 操作"""
        if operation == "generate_code":
            return await codeflow_mcp.generate_code(params.get("specification"))
        elif operation == "code_to_spec":
            return await codeflow_mcp.code_to_specification(
                params.get("code"),
                params.get("language")
            )
        elif operation == "optimize_code":
            return await codeflow_mcp.optimize_code(params.get("code"))
        elif operation == "analyze_code":
            return await codeflow_mcp.analyze_code_quality(params.get("code"))
        
        return {"error": f"未知的 CodeFlow MCP 操作: {operation}"}
    
    async def _execute_smartui_mcp(self, mcp_instance, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 SmartUI MCP 操作"""
        if operation == "generate_ui":
            return await smartui_manager.generate_ui(params.get("specification"))
        elif operation == "generate_responsive_ui":
            return await smartui_manager.generate_responsive_ui(params.get("design"))
        elif operation == "generate_ui_tests":
            return await smartui_manager.generate_ui_tests(params.get("ui_components"))
        elif operation == "optimize_ui_performance":
            return await smartui_manager.optimize_ui_performance(params.get("metrics"))
        
        return {"error": f"未知的 SmartUI MCP 操作: {operation}"}
    
    async def _execute_claude_router_mcp(self, mcp_instance, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 Claude Router MCP 操作"""
        if operation == "route_request":
            return await claude_router.route_to_optimal_model(params.get("request"))
        elif operation == "get_usage_stats":
            return await claude_router.get_usage_statistics()
        elif operation == "optimize_costs":
            return await claude_router.optimize_model_costs(params.get("constraints"))
        elif operation == "switch_to_k2":
            return await claude_router.switch_to_k2_model()
        
        return {"error": f"未知的 Claude Router MCP 操作: {operation}"}
    
    async def _execute_command_mcp(self, mcp_instance, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 Command MCP 操作"""
        if operation == "execute_command":
            return await command_manager.execute_command(params.get("command"))
        elif operation == "run_script":
            return await command_manager.run_script(params.get("script_path"))
        elif operation == "manage_environment":
            return await command_manager.manage_environment(params.get("action"), params.get("env_config"))
        elif operation == "deploy_application":
            return await command_manager.deploy_application(params.get("deploy_config"))
        
        return {"error": f"未知的 Command MCP 操作: {operation}"}
    
    async def _execute_memoryos_mcp(self, mcp_instance, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行 MemoryOS MCP 操作"""
        if operation == "store_context":
            return await memory_engine.store_context(params.get("context"))
        elif operation == "retrieve_context":
            return await memory_engine.retrieve_context(params.get("query"))
        elif operation == "learn_pattern":
            return await memory_engine.learn_from_pattern(params.get("pattern_data"))
        elif operation == "get_recommendations":
            return await memory_engine.get_personalized_recommendations(params.get("user_context"))
        
        return {"error": f"未知的 MemoryOS MCP 操作: {operation}"}
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """獲取集成狀態"""
        integration_status = {}
        
        for mcp_name, mapping in self.mcp_mappings.items():
            integration_status[mcp_name] = {
                "integration_level": mapping.integration_level.value,
                "integrated_workflows": len(mapping.workflow_stages),
                "capabilities": len(mapping.capabilities),
                "status": "active"
            }
        
        # 計算整體集成度
        total_mcps = len(self.mcp_mappings)
        full_integrated = sum(1 for m in self.mcp_mappings.values() 
                            if m.integration_level == MCPIntegrationLevel.FULL)
        
        overall_integration = (full_integrated / total_mcps) * 100 if total_mcps > 0 else 0
        
        return {
            "total_mcps": total_mcps,
            "full_integrated": full_integrated,
            "overall_integration_percentage": f"{overall_integration:.1f}%",
            "mcp_status": integration_status,
            "integration_complete": overall_integration >= 100
        }
    
    async def validate_integration(self) -> Dict[str, Any]:
        """驗證集成完整性"""
        validation_results = []
        
        # 測試每個 MCP 的基本功能
        for mcp_name in self.mcp_mappings.keys():
            try:
                # 嘗試加載 MCP
                mcp_instance = await mcp_registry.load_mcp(mcp_name)
                
                if mcp_instance:
                    # 獲取 MCP 狀態
                    if hasattr(mcp_instance, 'get_status'):
                        status = mcp_instance.get_status()
                        validation_results.append({
                            "mcp": mcp_name,
                            "status": "passed",
                            "details": status
                        })
                    else:
                        validation_results.append({
                            "mcp": mcp_name,
                            "status": "warning",
                            "details": "無狀態方法"
                        })
                else:
                    validation_results.append({
                        "mcp": mcp_name,
                        "status": "failed",
                        "details": "無法加載 MCP"
                    })
                    
            except Exception as e:
                validation_results.append({
                    "mcp": mcp_name,
                    "status": "error",
                    "details": str(e)
                })
        
        # 計算驗證結果
        passed = sum(1 for r in validation_results if r["status"] == "passed")
        total = len(validation_results)
        
        return {
            "validation_passed": passed == total,
            "passed_count": passed,
            "total_count": total,
            "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "results": validation_results
        }


# 單例實例
workflow_mcp_integrator = WorkflowMCPIntegrator()