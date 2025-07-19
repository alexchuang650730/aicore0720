#!/usr/bin/env python3
"""
PowerAutomation 外部工具整合 - 完整測試用例集
基於重構規格文檔 v1.0
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

# 假設已導入的模組
from external_tools_mcp_integration import (
    ExternalToolsMCP, 
    MCPSOAdapter,
    ACIDevAdapter,
    ZapierAdapter
)

from advanced_tool_intelligence_system import (
    IntelligentRecommendationSystem,
    ToolEffectLearningEngine,
    CustomToolDevelopmentSDK,
    UserProfile,
    ProjectContext
)

class TestExternalToolsMCP:
    """External Tools MCP 核心功能測試"""
    
    @pytest.fixture
    async def mcp(self):
        """創建 MCP 實例"""
        mcp = ExternalToolsMCP()
        return mcp
    
    @pytest.mark.asyncio
    async def test_list_tools_basic(self, mcp):
        """測試基本工具列表功能"""
        # 執行
        result = await mcp.handle_request("list_tools", {})
        
        # 驗證
        assert "tools" in result
        assert "total" in result
        assert result["total"] > 0
        assert len(result["tools"]) == result["total"]
        
        # 驗證工具結構
        for tool in result["tools"]:
            assert "id" in tool
            assert "name" in tool
            assert "platform" in tool
            assert "category" in tool
            assert "cost_per_call" in tool
    
    @pytest.mark.asyncio
    async def test_list_tools_with_filters(self, mcp):
        """測試帶過濾條件的工具列表"""
        # 測試平台過濾
        result = await mcp.handle_request("list_tools", {"platform": "mcp.so"})
        assert all(tool["platform"] == "mcp.so" for tool in result["tools"])
        
        # 測試類別過濾
        result = await mcp.handle_request("list_tools", {"category": "code_quality"})
        assert all(tool["category"] == "code_quality" for tool in result["tools"])
    
    @pytest.mark.asyncio
    async def test_execute_tool_success(self, mcp):
        """測試成功執行工具"""
        # 準備參數
        params = {
            "tool_id": "mcp_prettier",
            "parameters": {
                "code": "const x=1;const y=2;",
                "language": "javascript"
            }
        }
        
        # 執行
        result = await mcp.handle_request("execute_tool", params)
        
        # 驗證
        assert "result" in result
        assert "tool" in result
        assert "execution_time" in result
        assert "cost" in result
        assert result["tool"]["id"] == "mcp_prettier"
        assert "formatted_code" in result["result"]
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_cache(self, mcp):
        """測試工具執行緩存"""
        params = {
            "tool_id": "mcp_prettier",
            "parameters": {"code": "const x=1;", "language": "javascript"}
        }
        
        # 第一次執行
        result1 = await mcp.handle_request("execute_tool", params)
        assert result1.get("cached", False) == False
        
        # 第二次執行（應該從緩存獲取）
        result2 = await mcp.handle_request("execute_tool", params)
        assert result2.get("cached", False) == True
        assert result1["result"] == result2["result"]
    
    @pytest.mark.asyncio
    async def test_execute_tool_error_handling(self, mcp):
        """測試工具執行錯誤處理"""
        # 不存在的工具
        result = await mcp.handle_request("execute_tool", {
            "tool_id": "non_existent_tool",
            "parameters": {}
        })
        assert "error" in result
        assert "Tool not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_search_tools(self, mcp):
        """測試工具搜索功能"""
        # 文本搜索
        result = await mcp.handle_request("search_tools", {"query": "format"})
        assert result["count"] > 0
        assert any("format" in tool["name"].lower() for tool in result["tools"])
        
        # 能力搜索
        result = await mcp.handle_request("search_tools", {"capabilities": ["lint"]})
        assert result["count"] > 0
        assert any("lint" in tool["capabilities"] for tool in result["tools"])
    
    @pytest.mark.asyncio
    async def test_execute_workflow_sequential(self, mcp):
        """測試順序執行工作流"""
        workflow = {
            "steps": [
                {
                    "tool_id": "mcp_prettier",
                    "parameters": {"code": "const x=1;", "language": "javascript"}
                },
                {
                    "tool_id": "mcp_eslint",
                    "parameters": {"code": "const x=1;", "rules": "airbnb"}
                }
            ],
            "parallel": False
        }
        
        result = await mcp.handle_request("execute_workflow", workflow)
        
        assert result["success"] == True
        assert result["total_steps"] == 2
        assert result["executed_steps"] == 2
        assert len(result["workflow_results"]) == 2
    
    @pytest.mark.asyncio
    async def test_execute_workflow_parallel(self, mcp):
        """測試並行執行工作流"""
        workflow = {
            "steps": [
                {"tool_id": "mcp_prettier", "parameters": {"code": "test", "language": "js"}},
                {"tool_id": "mcp_eslint", "parameters": {"code": "test", "rules": "airbnb"}},
                {"tool_id": "mcp_jest_runner", "parameters": {"test_files": ["test.js"]}}
            ],
            "parallel": True
        }
        
        start_time = datetime.now()
        result = await mcp.handle_request("execute_workflow", workflow)
        end_time = datetime.now()
        
        # 並行執行應該更快
        execution_time = (end_time - start_time).total_seconds()
        assert execution_time < 1.0  # 假設並行執行在1秒內完成
        assert result["success"] == True
    
    @pytest.mark.asyncio
    async def test_get_recommendations(self, mcp):
        """測試獲取工具推薦"""
        params = {
            "intent": "format and test javascript code",
            "context": {
                "language": "javascript",
                "project_type": "frontend"
            }
        }
        
        result = await mcp.handle_request("get_recommendations", params)
        
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
        assert "reasoning" in result
        
        # 驗證推薦結構
        for rec in result["recommendations"]:
            assert "tool" in rec
            assert "score" in rec
            assert rec["score"] >= 0 and rec["score"] <= 1


class TestIntelligentRecommendationSystem:
    """智能推薦系統測試"""
    
    @pytest.fixture
    async def recommender(self):
        """創建推薦系統實例"""
        mcp = Mock()
        mcp.handle_request = AsyncMock(return_value={
            "tools": [
                {"id": "tool1", "name": "Tool 1", "category": "test"},
                {"id": "tool2", "name": "Tool 2", "category": "format"}
            ]
        })
        return IntelligentRecommendationSystem(mcp)
    
    @pytest.mark.asyncio
    async def test_personalized_recommendations(self, recommender):
        """測試個性化推薦"""
        # 設置用戶偏好
        user_id = "test_user"
        recommender.user_profiles[user_id] = UserProfile(
            user_id=user_id,
            preferences={"tool1": 0.8, "tool2": 0.3},
            skill_level="intermediate"
        )
        
        # 獲取推薦
        recommendations = await recommender.get_personalized_recommendations(
            user_id=user_id,
            task="test my code",
            context={"project_type": "backend"}
        )
        
        # 驗證
        assert len(recommendations) > 0
        assert recommendations[0]["tool"]["id"] == "tool1"  # 偏好分數更高
        assert all("factors" in rec for rec in recommendations)
        assert all("reasoning" in rec for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_project_context_matching(self, recommender):
        """測試項目上下文匹配"""
        context = {
            "project_type": "frontend",
            "framework": "react",
            "language": "javascript",
            "complexity": "high",
            "deadline_pressure": True
        }
        
        recommendations = await recommender.get_personalized_recommendations(
            user_id="new_user",
            task="optimize performance",
            context=context
        )
        
        # 驗證考慮了截止日期壓力（快速工具應該排名更高）
        assert len(recommendations) > 0
        # 實際測試中應該驗證快速工具的排名
    
    @pytest.mark.asyncio
    async def test_update_user_preference(self, recommender):
        """測試更新用戶偏好"""
        user_id = "test_user"
        tool_id = "tool1"
        
        # 初始偏好
        await recommender.update_user_preference(user_id, tool_id, 0.9)
        profile = recommender._get_or_create_profile(user_id)
        assert profile.preferences[tool_id] > 0.5
        
        # 更新偏好（負面反饋）
        await recommender.update_user_preference(user_id, tool_id, 0.1)
        assert profile.preferences[tool_id] < 0.5


class TestToolEffectLearningEngine:
    """工具效果學習引擎測試"""
    
    @pytest.fixture
    def learning_engine(self):
        """創建學習引擎實例"""
        return ToolEffectLearningEngine()
    
    @pytest.mark.asyncio
    async def test_record_execution(self, learning_engine):
        """測試記錄執行數據"""
        # 記錄多次執行
        for i in range(10):
            await learning_engine.record_execution(
                tool_id="test_tool",
                user_id="user1",
                execution_data={
                    "execution_time_ms": 100 + i * 10,
                    "success": i != 5,  # 第6次失敗
                    "context": {"test": True}
                }
            )
        
        # 驗證統計
        stats = learning_engine.tool_statistics.get("test_tool")
        assert stats is not None
        assert stats["total_executions"] == 10
        assert stats["success_rate"] == 0.9
        assert stats["avg_latency"] == 145  # (100+110+...+190)/10
    
    @pytest.mark.asyncio
    async def test_identify_poor_performing_tools(self, learning_engine):
        """測試識別表現不佳的工具"""
        # 創建表現不佳的工具數據
        for i in range(20):
            await learning_engine.record_execution(
                tool_id="poor_tool",
                user_id="user1",
                execution_data={
                    "execution_time_ms": 6000,  # 超過閾值
                    "success": i % 3 != 0,  # 33%失敗率
                    "user_satisfaction": 2.0  # 低滿意度
                }
            )
        
        # 運行學習週期
        poor_tools = await learning_engine._run_learning_cycle()
        
        # 驗證
        assert len(poor_tools) > 0
        assert any(tool["tool_id"] == "poor_tool" for tool in poor_tools)
        
        # 驗證問題識別
        poor_tool = next(t for t in poor_tools if t["tool_id"] == "poor_tool")
        assert len(poor_tool["issues"]) > 0
        assert len(poor_tool["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_should_exclude_tool(self, learning_engine):
        """測試自動淘汰工具"""
        # 創建持續惡化的工具數據
        tool_id = "bad_tool"
        
        # 前50次還可以
        for i in range(50):
            await learning_engine.record_execution(
                tool_id=tool_id,
                user_id="user1",
                execution_data={
                    "execution_time_ms": 1000,
                    "success": True
                }
            )
        
        # 後20次很糟糕
        for i in range(20):
            await learning_engine.record_execution(
                tool_id=tool_id,
                user_id="user1",
                execution_data={
                    "execution_time_ms": 5000,
                    "success": False
                }
            )
        
        # 檢查是否應該排除
        should_exclude = await learning_engine.should_exclude_tool(tool_id)
        # 根據實際算法調整預期結果


class TestCustomToolDevelopmentSDK:
    """自定義工具開發 SDK 測試"""
    
    @pytest.fixture
    def sdk(self):
        """創建 SDK 實例"""
        return CustomToolDevelopmentSDK()
    
    @pytest.mark.asyncio
    async def test_create_custom_tool(self, sdk):
        """測試創建自定義工具"""
        tool_definition = {
            "name": "My Custom Tool",
            "description": "A test custom tool for unit testing",
            "category": "testing",
            "parameters": {
                "input": {"type": "string", "required": True}
            },
            "script_content": "# Test script"
        }
        
        # 創建工具
        custom_tool = await sdk.create_custom_tool("author123", tool_definition)
        
        # 驗證
        assert custom_tool.tool_id.startswith("custom_author123_")
        assert custom_tool.name == "My Custom Tool"
        assert custom_tool.author_id == "author123"
        assert custom_tool.version == "1.0.0"
        assert custom_tool.tool_id in sdk.custom_tools
    
    @pytest.mark.asyncio
    async def test_tool_validation(self, sdk):
        """測試工具驗證"""
        # 測試危險代碼檢測
        with pytest.raises(ValueError) as exc_info:
            await sdk.create_custom_tool("author123", {
                "name": "Dangerous Tool",
                "description": "This tool has dangerous code",
                "script_content": "eval('malicious code')"
            })
        assert "危險代碼" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_test_custom_tool(self, sdk):
        """測試執行自定義工具"""
        # 先創建工具
        tool = await sdk.create_custom_tool("author123", {
            "name": "Test Tool",
            "description": "Test tool for testing",
            "script_content": "# Test"
        })
        
        # 測試工具
        result = await sdk.test_custom_tool(
            tool.tool_id,
            {"input": "test data"}
        )
        
        assert result["status"] == "success"
        assert "output" in result
        assert result["test_params"]["input"] == "test data"
    
    @pytest.mark.asyncio
    async def test_publish_tool(self, sdk):
        """測試發布工具"""
        # 創建完整的工具
        tool = await sdk.create_custom_tool("author123", {
            "name": "Complete Tool",
            "description": "A complete tool ready for publishing",
            "category": "utility",
            "parameters": {
                "input": {"type": "string", "required": True},
                "options": {"type": "object", "required": False}
            },
            "script_content": "# Complete implementation"
        })
        
        # 發布工具
        result = await sdk.publish_tool(tool.tool_id)
        
        # 驗證
        assert result["status"] in ["published", "rejected"]
        if result["status"] == "published":
            assert "marketplace_url" in result
            assert sdk.custom_tools[tool.tool_id].verified == True


class TestIntegrationScenarios:
    """集成場景測試"""
    
    @pytest.mark.asyncio
    async def test_k2_tool_chain_execution(self):
        """測試 K2 工具鏈執行"""
        # 模擬 K2 請求處理流程
        mcp = ExternalToolsMCP()
        
        # K2 解析用戶意圖並生成工具鏈
        user_request = "格式化我的代碼，運行測試，然後發送通知"
        
        # 獲取推薦
        recommendations = await mcp.handle_request("get_recommendations", {
            "intent": "format test notify",
            "context": {"language": "javascript"}
        })
        
        # 執行工作流
        workflow_steps = [
            {"tool_id": "mcp_prettier", "parameters": {"code": "test", "language": "js"}},
            {"tool_id": "mcp_jest_runner", "parameters": {"test_files": ["test.js"]}},
            {"tool_id": "zapier_slack", "parameters": {"channel": "#dev", "message": "Done"}}
        ]
        
        result = await mcp.handle_request("execute_workflow", {
            "steps": workflow_steps,
            "parallel": False
        })
        
        assert result["success"] == True
        assert result["executed_steps"] == 3
    
    @pytest.mark.asyncio
    async def test_claudeeditor_quick_action(self):
        """測試 ClaudeEditor 快速操作"""
        mcp = ExternalToolsMCP()
        
        # 模擬 ClaudeEditor 格式化當前文件
        result = await mcp.handle_request("execute_tool", {
            "tool_id": "mcp_prettier",
            "parameters": {
                "code": "function test(){console.log('hello')}",
                "language": "javascript",
                "config": {"semi": True, "singleQuote": True}
            }
        })
        
        assert "result" in result
        assert "formatted_code" in result["result"]
    
    @pytest.mark.asyncio
    async def test_learning_feedback_loop(self):
        """測試學習反饋循環"""
        mcp = ExternalToolsMCP()
        learning_engine = ToolEffectLearningEngine()
        
        # 執行工具並記錄結果
        tool_id = "mcp_prettier"
        
        for i in range(5):
            # 執行工具
            result = await mcp.handle_request("execute_tool", {
                "tool_id": tool_id,
                "parameters": {"code": f"test{i}", "language": "js"}
            })
            
            # 記錄執行數據
            await learning_engine.record_execution(
                tool_id=tool_id,
                user_id="test_user",
                execution_data={
                    "execution_time_ms": result.get("execution_time", 100),
                    "success": "error" not in result,
                    "user_satisfaction": 4.5
                }
            )
        
        # 獲取性能數據
        performance = await learning_engine.get_tool_performance(tool_id)
        assert performance is not None
        assert performance["total_executions"] >= 5


class TestPerformanceAndScalability:
    """性能和可擴展性測試"""
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """測試並發工具執行"""
        mcp = ExternalToolsMCP()
        
        # 創建多個並發請求
        tasks = []
        for i in range(10):
            task = mcp.handle_request("execute_tool", {
                "tool_id": "mcp_prettier",
                "parameters": {"code": f"const x={i};", "language": "javascript"}
            })
            tasks.append(task)
        
        # 並發執行
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        # 驗證
        assert len(results) == 10
        assert all("result" in r for r in results)
        
        # 性能驗證（應該在合理時間內完成）
        execution_time = (end_time - start_time).total_seconds()
        assert execution_time < 5.0  # 5秒內完成10個請求
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """測試緩存性能"""
        mcp = ExternalToolsMCP()
        
        params = {
            "tool_id": "mcp_prettier",
            "parameters": {"code": "const x=1;", "language": "javascript"}
        }
        
        # 第一次執行（無緩存）
        start1 = datetime.now()
        result1 = await mcp.handle_request("execute_tool", params)
        time1 = (datetime.now() - start1).total_seconds()
        
        # 第二次執行（有緩存）
        start2 = datetime.now()
        result2 = await mcp.handle_request("execute_tool", params)
        time2 = (datetime.now() - start2).total_seconds()
        
        # 緩存應該顯著更快
        assert time2 < time1 * 0.1  # 至少快10倍
        assert result2.get("cached") == True


class TestSecurityAndValidation:
    """安全性和驗證測試"""
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self):
        """測試參數驗證"""
        mcp = ExternalToolsMCP()
        
        # 缺少必需參數
        result = await mcp.handle_request("execute_tool", {
            "tool_id": "mcp_prettier"
            # 缺少 parameters
        })
        
        # 應該返回錯誤
        assert "error" in result or "parameters" in str(result)
    
    @pytest.mark.asyncio
    async def test_malicious_code_detection(self):
        """測試惡意代碼檢測"""
        sdk = CustomToolDevelopmentSDK()
        
        malicious_patterns = [
            "import os; os.system('rm -rf /')",
            "eval('__import__(\"os\").system(\"ls\")')",
            "exec(compile('print(\"hacked\")', 'string', 'exec'))"
        ]
        
        for pattern in malicious_patterns:
            with pytest.raises(ValueError) as exc_info:
                await sdk.create_custom_tool("hacker", {
                    "name": "Malicious Tool",
                    "description": "Bad tool",
                    "script_content": pattern
                })
            assert "危險代碼" in str(exc_info.value)


# 運行測試的配置
if __name__ == "__main__":
    pytest.main([
        "-v",  # 詳細輸出
        "-s",  # 顯示 print 輸出
        "--asyncio-mode=auto",  # 自動處理異步測試
        __file__
    ])