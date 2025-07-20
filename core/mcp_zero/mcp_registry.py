#!/usr/bin/env python3
"""
MCP-Zero 註冊中心
管理所有 MCP 的元數據和動態加載
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod
import importlib
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MCPMetadata:
    """MCP 元數據"""
    name: str
    description: str
    capabilities: List[str]
    context_size: int
    priority: str  # P0, P1, P2
    dependencies: List[str]
    tags: List[str]
    performance_score: float  # 0-1，性能評分
    success_rate: float  # 0-1，成功率


class MCPInterface(ABC):
    """MCP 統一接口"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化 MCP"""
        pass
    
    @abstractmethod
    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """執行 MCP 動作"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理資源"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """獲取能力列表"""
        pass


class MCPRegistry:
    """MCP 動態註冊和檢索中心"""
    
    def __init__(self):
        self.mcp_catalog: Dict[str, MCPMetadata] = {}
        self.loaded_mcps: Dict[str, MCPInterface] = {}
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        self._initialize_catalog()
        
    def _initialize_catalog(self):
        """初始化 MCP 目錄"""
        self.mcp_catalog = {
            # P0 核心 MCP
            "smart_intervention": MCPMetadata(
                name="smart_intervention",
                description="智能干預系統 - 自動檢測並切換到 ClaudeEditor",
                capabilities=[
                    "capability_detection", "auto_switch", "keyword_listening",
                    "hook_system", "claude_integration", "task_routing"
                ],
                context_size=1000,
                priority="P0",
                dependencies=[],
                tags=["intervention", "automation", "intelligence", "ux"],
                performance_score=0.98,
                success_rate=0.95
            ),
            
            "codeflow_mcp": MCPMetadata(
                name="codeflow_mcp",
                description="代碼生成、分析、重構和測試生成",
                capabilities=[
                    "generate_code", "analyze_code", "refactor_code",
                    "generate_tests", "code_to_spec"
                ],
                context_size=2000,
                priority="P0",
                dependencies=[],
                tags=["code", "generation", "analysis"],
                performance_score=0.95,
                success_rate=0.92
            ),
            
            "smartui_mcp": MCPMetadata(
                name="smartui_mcp",
                description="智能 UI 生成和響應式設計",
                capabilities=[
                    "generate_ui", "responsive_design", "theme_management",
                    "device_adaptation"
                ],
                context_size=1500,
                priority="P0",
                dependencies=["ag_ui_mcp"],
                tags=["ui", "design", "responsive"],
                performance_score=0.90,
                success_rate=0.88
            ),
            
            "ag_ui_mcp": MCPMetadata(
                name="ag_ui_mcp",
                description="UI 組件生成和測試界面創建",
                capabilities=[
                    "generate_components", "create_test_ui", "dashboard_builder"
                ],
                context_size=1500,
                priority="P0",
                dependencies=["smartui_mcp"],
                tags=["ui", "components", "testing"],
                performance_score=0.88,
                success_rate=0.90
            ),
            
            "test_mcp": MCPMetadata(
                name="test_mcp",
                description="自動化測試生成和執行",
                capabilities=[
                    "generate_unit_tests", "integration_testing", "coverage_analysis"
                ],
                context_size=1800,
                priority="P0",
                dependencies=["codeflow_mcp"],
                tags=["testing", "quality", "automation"],
                performance_score=0.85,
                success_rate=0.87
            ),
            
            # P1 工作流 MCP
            "stagewise_mcp": MCPMetadata(
                name="stagewise_mcp",
                description="端到端測試和用戶流程測試",
                capabilities=[
                    "e2e_testing", "user_flow_testing", "scenario_testing"
                ],
                context_size=2000,
                priority="P1",
                dependencies=["ag_ui_mcp", "test_mcp"],
                tags=["testing", "e2e", "workflow"],
                performance_score=0.82,
                success_rate=0.85
            ),
            
            "deepgraph_mcp": MCPMetadata(
                name="deepgraph_mcp",
                description="依賴分析和代碼結構可視化",
                capabilities=[
                    "dependency_analysis", "code_visualization", "architecture_mapping"
                ],
                context_size=1200,
                priority="P1",
                dependencies=["codeflow_mcp"],
                tags=["analysis", "visualization", "architecture"],
                performance_score=0.80,
                success_rate=0.88
            ),
            
            "security_mcp": MCPMetadata(
                name="security_mcp",
                description="安全掃描和漏洞檢測",
                capabilities=[
                    "security_scan", "vulnerability_detection", "compliance_check"
                ],
                context_size=1500,
                priority="P1",
                dependencies=["codeflow_mcp", "test_mcp"],
                tags=["security", "scanning", "compliance"],
                performance_score=0.78,
                success_rate=0.90
            ),
            
            # P2 支援 MCP
            "xmasters_mcp": MCPMetadata(
                name="xmasters_mcp",
                description="深度推理和複雜問題解決",
                capabilities=[
                    "deep_reasoning", "complex_problem_solving", "algorithm_optimization"
                ],
                context_size=3000,
                priority="P2",
                dependencies=["codeflow_mcp"],
                tags=["reasoning", "optimization", "complex"],
                performance_score=0.70,
                success_rate=0.75
            ),
            
            "operations_mcp": MCPMetadata(
                name="operations_mcp",
                description="智能運維和監控",
                capabilities=[
                    "monitoring", "alerting", "performance_tuning"
                ],
                context_size=1000,
                priority="P2",
                dependencies=["intelligent_monitoring_mcp"],
                tags=["operations", "monitoring", "devops"],
                performance_score=0.75,
                success_rate=0.82
            ),
            
            # 新增的 MCP
            "smarttool_mcp": MCPMetadata(
                name="smarttool_mcp",
                description="外部工具智能集成 (mcp.so, aci.dev, zapier)",
                capabilities=[
                    "external_tools", "workflow_execution", "tool_recommendation",
                    "multi_platform", "mcp_so", "aci_dev", "zapier"
                ],
                context_size=1200,
                priority="P1",
                dependencies=[],
                tags=["tools", "integration", "external", "automation"],
                performance_score=0.85,
                success_rate=0.88
            ),
            
            "memoryrag_mcp": MCPMetadata(
                name="memoryrag_mcp",
                description="智能記憶與檢索增強生成",
                capabilities=[
                    "memory_management", "rag", "k2_optimization", "learning_adapter",
                    "manus_replay", "deepswe_integration"
                ],
                context_size=2500,
                priority="P0",
                dependencies=[],
                tags=["memory", "rag", "learning", "optimization"],
                performance_score=0.92,
                success_rate=0.90
            ),
            
            # 第21個MCP組件 - Claude實時收集器
            "claude_realtime_mcp": MCPMetadata(
                name="claude_realtime_mcp",
                description="Claude實時數據收集與K2/DeepSWE訓練數據生成器",
                capabilities=[
                    "realtime_collection", "training_data_generation", "k2_training", 
                    "deepswe_training", "session_monitoring", "data_quality_assessment",
                    "process_monitoring", "conversation_tracking", "tool_usage_analysis"
                ],
                context_size=3000,
                priority="P0",
                dependencies=["memoryrag_mcp"],
                tags=["collection", "training", "k2", "deepswe", "realtime", "data"],
                performance_score=0.94,
                success_rate=0.91
            ),
            
            # 其他 MCP...
        }
        
    async def search_mcps(self, task_description: str, max_results: int = 5) -> List[str]:
        """根據任務描述搜索相關 MCP"""
        logger.info(f"搜索 MCP for: {task_description}")
        
        # 簡單的關鍵詞匹配（未來可以用語義搜索）
        keywords = task_description.lower().split()
        scores: Dict[str, float] = {}
        
        for mcp_name, metadata in self.mcp_catalog.items():
            score = 0.0
            
            # 檢查描述匹配
            desc_lower = metadata.description.lower()
            for keyword in keywords:
                if keyword in desc_lower:
                    score += 2.0
                    
            # 檢查能力匹配
            for capability in metadata.capabilities:
                for keyword in keywords:
                    if keyword in capability.lower():
                        score += 3.0
                        
            # 檢查標籤匹配
            for tag in metadata.tags:
                for keyword in keywords:
                    if keyword in tag:
                        score += 1.5
                        
            # 考慮優先級
            priority_boost = {"P0": 2.0, "P1": 1.0, "P2": 0.5}
            score *= priority_boost.get(metadata.priority, 0.5)
            
            # 考慮性能評分
            score *= metadata.performance_score
            
            if score > 0:
                scores[mcp_name] = score
                
        # 排序並返回前 N 個
        sorted_mcps = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [mcp[0] for mcp in sorted_mcps[:max_results]]
        
    async def load_mcp(self, mcp_name: str) -> Optional[MCPInterface]:
        """動態加載指定 MCP"""
        if mcp_name in self.loaded_mcps:
            logger.info(f"MCP {mcp_name} 已加載，直接返回")
            return self.loaded_mcps[mcp_name]
            
        if mcp_name not in self.mcp_catalog:
            logger.error(f"未知的 MCP: {mcp_name}")
            return None
            
        logger.info(f"動態加載 MCP: {mcp_name}")
        metadata = self.mcp_catalog[mcp_name]
        
        try:
            # 先加載依賴
            for dep in metadata.dependencies:
                if dep not in self.loaded_mcps:
                    await self.load_mcp(dep)
                    
            # 使用適配器模式加載 MCP
            from ..mcp_adapters.base_mcp_adapter import MCPAdapterFactory
            
            # 創建適配器
            mcp_instance = MCPAdapterFactory.create_adapter(mcp_name)
            
            # 初始化
            await mcp_instance.initialize()
            
            # 緩存
            self.loaded_mcps[mcp_name] = mcp_instance
            
            # 更新使用統計
            self._update_usage_stats(mcp_name, "loaded")
            
            return mcp_instance
            
        except Exception as e:
            logger.error(f"加載 MCP {mcp_name} 失敗: {str(e)}")
            return None
            
    async def unload_mcp(self, mcp_name: str) -> bool:
        """卸載指定 MCP"""
        if mcp_name not in self.loaded_mcps:
            return True
            
        logger.info(f"卸載 MCP: {mcp_name}")
        
        try:
            # 檢查是否有其他 MCP 依賴此 MCP
            dependencies = self._get_reverse_dependencies(mcp_name)
            loaded_deps = [dep for dep in dependencies if dep in self.loaded_mcps]
            
            if loaded_deps:
                logger.warning(f"無法卸載 {mcp_name}，被依賴於: {loaded_deps}")
                return False
                
            # 清理資源
            mcp_instance = self.loaded_mcps[mcp_name]
            await mcp_instance.cleanup()
            
            # 從緩存中移除
            del self.loaded_mcps[mcp_name]
            
            # 更新統計
            self._update_usage_stats(mcp_name, "unloaded")
            
            return True
            
        except Exception as e:
            logger.error(f"卸載 MCP {mcp_name} 失敗: {str(e)}")
            return False
            
    async def get_loaded_mcps(self) -> List[str]:
        """獲取當前已加載的 MCP 列表"""
        return list(self.loaded_mcps.keys())
        
    async def get_mcp_metadata(self, mcp_name: str) -> Optional[MCPMetadata]:
        """獲取 MCP 元數據"""
        return self.mcp_catalog.get(mcp_name)
        
    async def suggest_mcps_for_workflow(self, workflow: str) -> List[str]:
        """為特定工作流推薦 MCP"""
        workflow_mcp_mapping = {
            "requirement_analysis": ["codeflow_mcp", "stagewise_mcp"],
            "architecture_design": ["smartui_mcp", "ag_ui_mcp", "deepgraph_mcp"],
            "coding_implementation": ["codeflow_mcp", "smartui_mcp", "ag_ui_mcp"],
            "testing_validation": ["test_mcp", "stagewise_mcp", "security_mcp"],
            "deployment_release": ["release_trigger_mcp", "intelligent_monitoring_mcp"],
            "monitoring_operations": ["operations_mcp", "intelligent_monitoring_mcp"]
        }
        
        return workflow_mcp_mapping.get(workflow, [])
        
    def _get_reverse_dependencies(self, mcp_name: str) -> Set[str]:
        """獲取依賴於指定 MCP 的所有 MCP"""
        reverse_deps = set()
        
        for other_mcp, metadata in self.mcp_catalog.items():
            if mcp_name in metadata.dependencies:
                reverse_deps.add(other_mcp)
                
        return reverse_deps
        
    def _update_usage_stats(self, mcp_name: str, action: str):
        """更新使用統計"""
        if mcp_name not in self.usage_stats:
            self.usage_stats[mcp_name] = {
                "load_count": 0,
                "unload_count": 0,
                "total_usage_time": 0,
                "last_used": None
            }
            
        stats = self.usage_stats[mcp_name]
        
        if action == "loaded":
            stats["load_count"] += 1
            stats["last_loaded"] = asyncio.get_event_loop().time()
        elif action == "unloaded":
            stats["unload_count"] += 1
            if "last_loaded" in stats:
                usage_time = asyncio.get_event_loop().time() - stats["last_loaded"]
                stats["total_usage_time"] += usage_time
                
    async def optimize_mcp_loading(self, task_steps: List[str]) -> List[str]:
        """優化 MCP 加載順序"""
        # 收集所有需要的 MCP
        all_mcps = set()
        for step in task_steps:
            mcps = await self.search_mcps(step, max_results=3)
            all_mcps.update(mcps)
            
        # 根據依賴關係排序
        sorted_mcps = self._topological_sort(list(all_mcps))
        
        return sorted_mcps
        
    def _topological_sort(self, mcp_names: List[str]) -> List[str]:
        """拓撲排序，確保依賴順序正確"""
        # 構建依賴圖
        graph = {}
        in_degree = {}
        
        for mcp in mcp_names:
            if mcp in self.mcp_catalog:
                metadata = self.mcp_catalog[mcp]
                graph[mcp] = [dep for dep in metadata.dependencies if dep in mcp_names]
                in_degree[mcp] = 0
                
        # 計算入度
        for mcp in graph:
            for dep in graph[mcp]:
                in_degree[dep] = in_degree.get(dep, 0) + 1
                
        # 拓撲排序
        queue = [mcp for mcp in mcp_names if in_degree.get(mcp, 0) == 0]
        result = []
        
        while queue:
            mcp = queue.pop(0)
            result.append(mcp)
            
            for dep in graph.get(mcp, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
                    
        return result
        
    def get_context_usage(self) -> Dict[str, Any]:
        """獲取當前上下文使用情況"""
        total_context = 0
        mcp_contexts = {}
        
        for mcp_name in self.loaded_mcps:
            if mcp_name in self.mcp_catalog:
                context_size = self.mcp_catalog[mcp_name].context_size
                total_context += context_size
                mcp_contexts[mcp_name] = context_size
                
        return {
            "total_context_size": total_context,
            "mcp_contexts": mcp_contexts,
            "loaded_count": len(self.loaded_mcps),
            "percentage_of_max": (total_context / 100000) * 100  # 假設最大 100k tokens
        }


# 創建全局實例
mcp_registry = MCPRegistry()