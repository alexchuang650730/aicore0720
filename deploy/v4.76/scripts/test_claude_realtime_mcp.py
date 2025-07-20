#!/usr/bin/env python3
"""
Claude實時收集器MCP測試和驗證腳本
驗證第21個MCP組件的功能完整性
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# 添加項目路徑
sys.path.append(str(Path(__file__).parent))

from core.components.claude_realtime_mcp.claude_realtime_manager import ClaudeRealtimeMCPManager
from core.mcp_zero.mcp_registry import mcp_registry

class ClaudeRealtimeMCPTester:
    """Claude實時收集器MCP測試器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.test_results = []
        self.mcp_manager = None
        
    async def run_all_tests(self):
        """運行所有測試"""
        print("🧪 Claude實時收集器MCP - 功能測試套件")
        print("=" * 50)
        
        # 配置日誌
        logging.basicConfig(level=logging.INFO)
        
        tests = [
            self.test_mcp_initialization,
            self.test_mcp_registry_integration,
            self.test_training_data_generation,
            self.test_k2_data_format,
            self.test_deepswe_data_format,
            self.test_quality_assessment,
            self.test_session_management,
            self.test_data_export,
            self.test_performance_metrics
        ]
        
        for test in tests:
            try:
                print(f"\n🔍 執行測試: {test.__name__}")
                await test()
                self.test_results.append({"test": test.__name__, "status": "PASS", "error": None})
                print("✅ 測試通過")
            except Exception as e:
                self.test_results.append({"test": test.__name__, "status": "FAIL", "error": str(e)})
                print(f"❌ 測試失敗: {e}")
        
        await self._generate_test_report()
    
    async def test_mcp_initialization(self):
        """測試MCP初始化"""
        self.mcp_manager = ClaudeRealtimeMCPManager()
        success = await self.mcp_manager.initialize()
        
        assert success, "MCP初始化失敗"
        assert self.mcp_manager.collection_running, "收集服務未啟動"
        assert self.mcp_manager.data_dir.exists(), "數據目錄未創建"
    
    async def test_mcp_registry_integration(self):
        """測試MCP註冊中心集成"""
        # 檢查是否已註冊
        metadata = await mcp_registry.get_mcp_metadata("claude_realtime_mcp")
        assert metadata is not None, "MCP未在註冊中心註冊"
        
        # 檢查元數據正確性
        assert metadata.name == "claude_realtime_mcp"
        assert metadata.priority == "P0"
        assert "realtime_collection" in metadata.capabilities
        assert "k2_training" in metadata.capabilities
        assert "deepswe_training" in metadata.capabilities
        
        # 測試搜索功能
        search_results = await mcp_registry.search_mcps("K2 training data collection")
        assert "claude_realtime_mcp" in search_results, "搜索功能未正確識別MCP"
    
    async def test_training_data_generation(self):
        """測試訓練數據生成"""
        # 模擬一個訓練會話
        from core.components.claude_realtime_mcp.claude_realtime_manager import TrainingSession, TrainingDataPoint
        import uuid
        import time
        
        session = TrainingSession(
            session_id=str(uuid.uuid4()),
            start_time=time.time(),
            project_context="/test/project"
        )
        
        # 添加測試數據點
        data_point = TrainingDataPoint(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            user_input="K2優化：分析這個Python函數的性能",
            assistant_response="基於分析，這個函數存在O(n²)複雜度問題，建議使用字典優化...",
            tool_calls=[{"name": "code_analyzer", "result": "performance_issue_detected"}],
            context={"language": "python", "function": "test_func"},
            session_id=session.session_id,
            category="k2",
            confidence=0.85,
            source="test"
        )
        
        session.data_points.append(data_point)
        session.k2_examples += 1
        session.total_interactions += 1
        
        # 測試質量計算
        quality = self.mcp_manager._calculate_data_quality({
            "user": data_point.user_input,
            "assistant": data_point.assistant_response,
            "tools": data_point.tool_calls,
            "context": data_point.context
        })
        
        assert quality > 0.5, f"數據質量分數過低: {quality}"
        assert session.k2_examples == 1, "K2樣本計數錯誤"
    
    async def test_k2_data_format(self):
        """測試K2數據格式"""
        # 創建測試會話
        from core.components.claude_realtime_mcp.claude_realtime_manager import TrainingSession, TrainingDataPoint
        import uuid
        import time
        
        session = TrainingSession(
            session_id=str(uuid.uuid4()),
            start_time=time.time()
        )
        
        k2_data_point = TrainingDataPoint(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            user_input="分析並執行任務：優化數據庫查詢",
            assistant_response="基於分析，我理解這個任務需要：查詢優化",
            tool_calls=[],
            context={},
            session_id=session.session_id,
            category="k2",
            confidence=0.8,
            source="test"
        )
        
        session.data_points.append(k2_data_point)
        session.k2_examples += 1
        
        # 測試K2文件生成
        await self.mcp_manager._generate_k2_training_files(session)
        
        # 檢查生成的文件
        k2_files = list(self.mcp_manager.data_dir.glob("k2_training_*.jsonl"))
        assert len(k2_files) > 0, "K2訓練文件未生成"
        
        # 驗證文件格式
        with open(k2_files[0], 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            k2_data = json.loads(line)
            
            assert "messages" in k2_data, "K2格式缺少messages字段"
            assert len(k2_data["messages"]) == 3, "K2格式消息數量錯誤"
            assert k2_data["messages"][0]["role"] == "system", "K2格式系統消息錯誤"
            assert "K2 優化器" in k2_data["messages"][0]["content"], "K2系統提示詞錯誤"
    
    async def test_deepswe_data_format(self):
        """測試DeepSWE數據格式"""
        from core.components.claude_realtime_mcp.claude_realtime_manager import TrainingSession, TrainingDataPoint
        import uuid
        import time
        
        session = TrainingSession(
            session_id=str(uuid.uuid4()),
            start_time=time.time()
        )
        
        deepswe_data_point = TrainingDataPoint(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            user_input="幫我重構這個Python函數，提高代碼可讀性",
            assistant_response="我將重構這個函數，採用單一職責原則...",
            tool_calls=[{"name": "code_refactor", "result": "refactored_code"}],
            context={"language": "python", "task": "refactoring"},
            session_id=session.session_id,
            category="deepswe",
            confidence=0.9,
            source="test"
        )
        
        session.data_points.append(deepswe_data_point)
        session.deepswe_examples += 1
        
        # 測試DeepSWE文件生成
        await self.mcp_manager._generate_deepswe_training_files(session)
        
        # 檢查生成的文件
        deepswe_files = list(self.mcp_manager.data_dir.glob("deepswe_training_*.jsonl"))
        assert len(deepswe_files) > 0, "DeepSWE訓練文件未生成"
        
        # 驗證文件格式
        with open(deepswe_files[0], 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            deepswe_data = json.loads(line)
            
            assert "instruction" in deepswe_data, "DeepSWE格式缺少instruction字段"
            assert "output" in deepswe_data, "DeepSWE格式缺少output字段"
            assert "tools_used" in deepswe_data, "DeepSWE格式缺少tools_used字段"
            assert deepswe_data["metadata"]["category"] == "software_engineering", "DeepSWE類別錯誤"
    
    async def test_quality_assessment(self):
        """測試數據質量評估"""
        # 測試高質量數據
        high_quality_interaction = {
            "user": "K2優化：分析這個複雜的算法並提供優化建議，需要考慮時間複雜度和空間複雜度",
            "assistant": "基於分析，我發現這個算法存在以下問題：1. 時間複雜度為O(n²)，可以優化到O(n log n)；2. 空間複雜度可以從O(n)優化到O(1)。具體優化方案如下...",
            "tools": [{"name": "algorithm_analyzer", "result": "complexity_analysis"}],
            "context": {"language": "python", "complexity": "high"}
        }
        
        high_quality_score = self.mcp_manager._calculate_data_quality(high_quality_interaction)
        assert high_quality_score > 0.7, f"高質量數據評分過低: {high_quality_score}"
        
        # 測試低質量數據
        low_quality_interaction = {
            "user": "幫我",
            "assistant": "好的",
            "tools": [],
            "context": {}
        }
        
        low_quality_score = self.mcp_manager._calculate_data_quality(low_quality_interaction)
        assert low_quality_score < 0.6, f"低質量數據評分過高: {low_quality_score}"
        
        assert high_quality_score > low_quality_score, "質量評估邏輯錯誤"
    
    async def test_session_management(self):
        """測試會話管理"""
        # 測試活躍會話管理
        initial_active = len(self.mcp_manager.active_sessions)
        
        # 模擬新會話開始
        proc_info = {
            "pid": 12345,
            "name": "claude-code",
            "cmdline": "claude-code /test/project",
            "create_time": 1234567890,
            "detected_at": 1234567890
        }
        
        await self.mcp_manager._on_claude_session_started(proc_info)
        
        assert len(self.mcp_manager.active_sessions) == initial_active + 1, "活躍會話計數錯誤"
        assert self.mcp_manager.training_stats["total_sessions"] > 0, "會話統計未更新"
        
        # 測試會話結束
        await self.mcp_manager._on_claude_session_ended(proc_info)
        
        # 等待會話處理完成
        await asyncio.sleep(0.1)
    
    async def test_data_export(self):
        """測試數據匯出"""
        # 確保有一些測試數據
        await self.test_training_data_generation()
        
        # 測試綜合格式匯出
        export_file = await self.mcp_manager.export_training_data("combined")
        export_path = Path(export_file)
        
        assert export_path.exists(), "匯出文件未創建"
        assert export_path.stat().st_size > 0, "匯出文件為空"
        
        # 驗證匯出內容
        with open(export_path, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
            
            assert "export_timestamp" in export_data, "匯出文件缺少時間戳"
            assert "training_stats" in export_data, "匯出文件缺少統計數據"
            assert "sessions" in export_data, "匯出文件缺少會話數據"
            assert "summary" in export_data, "匯出文件缺少摘要"
    
    async def test_performance_metrics(self):
        """測試性能指標"""
        # 獲取訓練摘要
        summary = await self.mcp_manager.get_training_summary()
        
        # 驗證摘要結構
        required_keys = [
            "active_sessions", "completed_sessions", "training_stats",
            "data_directory", "collection_running", "monitored_processes"
        ]
        
        for key in required_keys:
            assert key in summary, f"訓練摘要缺少{key}字段"
        
        # 驗證統計數據結構
        stats = summary["training_stats"]
        stats_keys = [
            "total_k2_examples", "total_deepswe_examples", "total_general_examples",
            "sessions_completed", "data_quality_score"
        ]
        
        for key in stats_keys:
            assert key in stats, f"統計數據缺少{key}字段"
            assert isinstance(stats[key], (int, float)), f"{key}字段類型錯誤"
    
    async def _generate_test_report(self):
        """生成測試報告"""
        print("\n" + "=" * 50)
        print("📊 Claude實時收集器MCP測試報告")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        print(f"總測試數: {total_tests}")
        print(f"✅ 通過: {passed_tests}")
        print(f"❌ 失敗: {failed_tests}")
        print(f"通過率: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失敗的測試:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['error']}")
        
        # 保存測試報告
        report_file = Path("claude_realtime_mcp_test_report.json")
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": (passed_tests/total_tests)*100,
            "test_results": self.test_results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 詳細報告已保存: {report_file}")
        
        # 清理
        if self.mcp_manager:
            await self.mcp_manager.shutdown()
        
        return passed_tests == total_tests

async def main():
    """主函數"""
    tester = ClaudeRealtimeMCPTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 所有測試通過！Claude實時收集器MCP準備就緒！")
        return 0
    else:
        print("\n💥 部分測試失敗，請檢查錯誤並修復")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)