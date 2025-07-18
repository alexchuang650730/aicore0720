#!/usr/bin/env python3
"""
綜合數據收集器 - 多源真實對比數據
整合Manus + Claude Code Tool + Safari開發場景
"""

import json
import time
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from real_time_comparison_tracker import RealTimeComparisonTracker

@dataclass
class MultiSourceSession:
    """多源會話記錄"""
    session_id: str
    source: str  # manus, claude_code_tool, safari_dev
    timestamp: float
    prompt: str
    response: str
    category: str
    complexity: str
    satisfaction_score: int
    time_taken: float
    cost_estimate: float
    task_completed: bool
    context: str  # 使用環境背景
    notes: str

class ComprehensiveDataCollector:
    """綜合數據收集器"""
    
    def __init__(self):
        self.tracker = RealTimeComparisonTracker()
        self.sessions = []
        
        # 擴展的場景分類
        self.advanced_categories = {
            "frontend": {
                "keywords": ["react", "vue", "typescript", "javascript", "css", "html", "ui", "component"],
                "subcategories": ["hooks", "state_management", "performance", "styling", "routing"]
            },
            "backend": {
                "keywords": ["python", "fastapi", "django", "node", "api", "server", "microservice"],
                "subcategories": ["auth", "database", "caching", "scaling", "security"]
            },
            "algorithm": {
                "keywords": ["sort", "search", "dp", "graph", "tree", "leetcode", "optimization"],
                "subcategories": ["sorting", "searching", "dynamic_programming", "graph_theory"]
            },
            "database": {
                "keywords": ["sql", "mongodb", "redis", "query", "optimization", "indexing"],
                "subcategories": ["query_optimization", "schema_design", "performance_tuning"]
            },
            "devops": {
                "keywords": ["docker", "kubernetes", "deployment", "ci/cd", "aws", "infrastructure"],
                "subcategories": ["containerization", "orchestration", "monitoring", "security"]
            },
            "browser_dev": {
                "keywords": ["safari", "webkit", "browser", "extension", "automation", "testing"],
                "subcategories": ["extension_dev", "automation", "performance", "compatibility"]
            },
            "debugging": {
                "keywords": ["debug", "error", "bug", "fix", "troubleshoot", "exception"],
                "subcategories": ["memory_leaks", "performance_issues", "logic_errors"]
            },
            "architecture": {
                "keywords": ["design", "system", "scalability", "microservice", "patterns"],
                "subcategories": ["system_design", "scalability", "patterns", "best_practices"]
            }
        }
    
    def add_manus_session(self, prompt: str, response: str, satisfaction: int, 
                         time_taken: float = 30.0, context: str = "", notes: str = "") -> str:
        """添加Manus會話記錄"""
        session = MultiSourceSession(
            session_id=f"manus_{int(time.time())}_{len(self.sessions)}",
            source="manus",
            timestamp=time.time(),
            prompt=prompt,
            response=response,
            category=self._categorize_prompt(prompt),
            complexity=self._assess_complexity(prompt, response),
            satisfaction_score=satisfaction,
            time_taken=time_taken,
            cost_estimate=self._estimate_manus_cost(len(response)),
            task_completed=satisfaction >= 7,
            context=f"Manus Environment: {context}",
            notes=notes
        )
        
        self.sessions.append(session)
        return session.session_id
    
    def add_claude_code_tool_session(self, prompt: str, response: str, satisfaction: int,
                                   time_taken: float = 25.0, context: str = "", notes: str = "") -> str:
        """添加Claude Code Tool會話記錄"""
        session = MultiSourceSession(
            session_id=f"claude_tool_{int(time.time())}_{len(self.sessions)}",
            source="claude_code_tool",
            timestamp=time.time(),
            prompt=prompt,
            response=response,
            category=self._categorize_prompt(prompt),
            complexity=self._assess_complexity(prompt, response),
            satisfaction_score=satisfaction,
            time_taken=time_taken,
            cost_estimate=self._estimate_claude_cost(len(response)),
            task_completed=satisfaction >= 7,
            context=f"Claude Code Tool: {context}",
            notes=notes
        )
        
        self.sessions.append(session)
        return session.session_id
    
    def add_safari_dev_session(self, prompt: str, response: str, satisfaction: int,
                              time_taken: float = 35.0, context: str = "", notes: str = "") -> str:
        """添加Safari開發會話記錄"""
        session = MultiSourceSession(
            session_id=f"safari_{int(time.time())}_{len(self.sessions)}",
            source="safari_dev",
            timestamp=time.time(),
            prompt=prompt,
            response=response,
            category=self._categorize_prompt(prompt),
            complexity=self._assess_complexity(prompt, response),
            satisfaction_score=satisfaction,
            time_taken=time_taken,
            cost_estimate=0.0,  # Safari開發通常是免費工具
            task_completed=satisfaction >= 6,  # Safari開發標準可能稍低
            context=f"Safari Development: {context}",
            notes=notes
        )
        
        self.sessions.append(session)
        return session.session_id
    
    def _categorize_prompt(self, prompt: str) -> str:
        """智能分類prompt"""
        prompt_lower = prompt.lower()
        
        # 計算每個類別的匹配分數
        category_scores = {}
        for category, config in self.advanced_categories.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in prompt_lower:
                    score += 1
            category_scores[category] = score
        
        # 返回得分最高的類別
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:
                return best_category[0]
        
        return "general"
    
    def _assess_complexity(self, prompt: str, response: str) -> str:
        """評估複雜度"""
        complexity_indicators = {
            "complex": ["architecture", "design", "system", "scalability", "distributed", "microservice", "performance"],
            "medium": ["implement", "create", "build", "develop", "integrate", "optimize"],
            "simple": ["fix", "debug", "simple", "basic", "quick"]
        }
        
        prompt_lower = prompt.lower()
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in prompt_lower for indicator in indicators):
                # 根據response長度調整
                if len(response) > 2000:
                    return "complex" if complexity == "medium" else complexity
                elif len(response) < 500:
                    return "simple" if complexity == "medium" else complexity
                return complexity
        
        # 基於長度的後備評估
        if len(response) > 1500:
            return "complex"
        elif len(response) > 500:
            return "medium"
        else:
            return "simple"
    
    def _estimate_manus_cost(self, response_length: int) -> float:
        """估算Manus成本 (基於token使用)"""
        tokens = response_length // 4
        return tokens * 0.02 / 1000  # 估算每1000 tokens $0.02
    
    def _estimate_claude_cost(self, response_length: int) -> float:
        """估算Claude成本"""
        tokens = response_length // 4
        return tokens * 0.015 / 1000  # Claude Sonnet pricing
    
    def convert_to_comparison_data(self) -> List[str]:
        """轉換所有會話為對比數據"""
        comparison_ids = []
        
        for session in self.sessions:
            comparison_id = self.tracker.quick_log_claude_only(
                prompt=session.prompt,
                category=session.category,
                complexity=session.complexity,
                response=session.response,
                satisfaction=session.satisfaction_score,
                time_seconds=session.time_taken,
                notes=f"{session.source}: {session.notes}"
            )
            comparison_ids.append(comparison_id)
        
        return comparison_ids
    
    def generate_quality_analysis(self) -> Dict[str, Any]:
        """生成質量分析報告"""
        if not self.sessions:
            return {"error": "沒有數據"}
        
        # 按來源分組
        by_source = {}
        for session in self.sessions:
            if session.source not in by_source:
                by_source[session.source] = []
            by_source[session.source].append(session)
        
        # 計算各來源統計
        source_stats = {}
        for source, sessions in by_source.items():
            avg_satisfaction = sum(s.satisfaction_score for s in sessions) / len(sessions)
            avg_time = sum(s.time_taken for s in sessions) / len(sessions)
            avg_cost = sum(s.cost_estimate for s in sessions) / len(sessions)
            completion_rate = sum(1 for s in sessions if s.task_completed) / len(sessions)
            
            source_stats[source] = {
                "session_count": len(sessions),
                "avg_satisfaction": avg_satisfaction,
                "avg_time": avg_time,
                "avg_cost": avg_cost,
                "completion_rate": completion_rate
            }
        
        # 按類別分析
        by_category = {}
        for session in self.sessions:
            if session.category not in by_category:
                by_category[session.category] = []
            by_category[session.category].append(session)
        
        category_stats = {}
        for category, sessions in by_category.items():
            avg_satisfaction = sum(s.satisfaction_score for s in sessions) / len(sessions)
            category_stats[category] = {
                "count": len(sessions),
                "avg_satisfaction": avg_satisfaction,
                "sources": list(set(s.source for s in sessions))
            }
        
        return {
            "total_sessions": len(self.sessions),
            "by_source": source_stats,
            "by_category": category_stats,
            "overall_avg_satisfaction": sum(s.satisfaction_score for s in self.sessions) / len(self.sessions),
            "overall_completion_rate": sum(1 for s in self.sessions if s.task_completed) / len(self.sessions)
        }
    
    def export_for_k2_testing(self) -> List[Dict]:
        """導出高質量場景用於K2測試"""
        high_quality_sessions = [
            s for s in self.sessions 
            if s.satisfaction_score >= 8 and s.task_completed
        ]
        
        k2_test_scenarios = []
        for session in high_quality_sessions:
            scenario = {
                "original_session_id": session.session_id,
                "source": session.source,
                "prompt": session.prompt,
                "expected_quality": session.satisfaction_score,
                "category": session.category,
                "complexity": session.complexity,
                "benchmark_time": session.time_taken,
                "benchmark_cost": session.cost_estimate,
                "context": session.context,
                "notes": f"原始來源: {session.source}, 期望質量: {session.satisfaction_score}/10"
            }
            k2_test_scenarios.append(scenario)
        
        return k2_test_scenarios
    
    def save_comprehensive_report(self, filename: str = None):
        """保存綜合報告"""
        if filename is None:
            filename = f"comprehensive_analysis_{int(time.time())}.json"
        
        report = {
            "metadata": {
                "generated_at": time.time(),
                "total_sessions": len(self.sessions),
                "sources": list(set(s.source for s in self.sessions)),
                "date_range": {
                    "start": min(s.timestamp for s in self.sessions) if self.sessions else 0,
                    "end": max(s.timestamp for s in self.sessions) if self.sessions else 0
                }
            },
            "sessions": [asdict(s) for s in self.sessions],
            "analysis": self.generate_quality_analysis(),
            "k2_test_scenarios": self.export_for_k2_testing()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 綜合報告已保存到: {filename}")
        return filename

# 真實數據示例 - 基於你的多源使用經驗
def load_sample_data(collector: ComprehensiveDataCollector):
    """載入示例數據"""
    
    # Manus數據示例 (基於1000小時經驗)
    collector.add_manus_session(
        prompt="創建React Hook管理複雜表單狀態，包含嵌套對象和數組驗證",
        response="""// 複雜的React Hook實現
const useFormManager = (schema) => {
  const [values, setValues] = useState({});
  const [errors, setErrors] = useState({});
  // ... 複雜的狀態管理邏輯
};""",
        satisfaction=8,
        time_taken=45.0,
        context="複雜Web應用開發",
        notes="Manus提供了完整的Hook實現，包含深度嵌套驗證"
    )
    
    # Claude Code Tool數據示例 (基於每日16小時使用)
    collector.add_claude_code_tool_session(
        prompt="優化Python算法性能，處理百萬級數據排序",
        response="""import heapq
from typing import List

def optimized_sort(data: List[int]) -> List[int]:
    # 使用堆排序優化大數據集
    heapq.heapify(data)
    return [heapq.heappop(data) for _ in range(len(data))]""",
        satisfaction=9,
        time_taken=20.0,
        context="高性能計算項目",
        notes="Claude Code Tool提供了高效的算法實現"
    )
    
    # Safari開發數據示例
    collector.add_safari_dev_session(
        prompt="創建Safari擴展進行頁面自動化測試",
        response="""// Safari Extension Background Script
browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'automate') {
    // 頁面自動化邏輯
    browser.tabs.executeScript({
      code: `document.querySelector('${request.selector}').click();`
    });
  }
});""",
        satisfaction=7,
        time_taken=60.0,
        context="瀏覽器自動化測試",
        notes="Safari開發工具提供了基本的擴展模板"
    )

def main():
    """演示綜合數據收集"""
    print("🎯 綜合數據收集器")
    print("整合Manus + Claude Code Tool + Safari開發")
    print("=" * 60)
    
    collector = ComprehensiveDataCollector()
    
    # 載入示例數據
    load_sample_data(collector)
    
    # 生成分析報告
    analysis = collector.generate_quality_analysis()
    print(f"\n📊 分析結果:")
    print(f"   總會話數: {analysis['total_sessions']}")
    print(f"   平均滿意度: {analysis['overall_avg_satisfaction']:.1f}/10")
    print(f"   完成率: {analysis['overall_completion_rate']:.1%}")
    
    print(f"\n📈 按來源統計:")
    for source, stats in analysis['by_source'].items():
        print(f"   {source:15} | 滿意度: {stats['avg_satisfaction']:.1f} | 時間: {stats['avg_time']:.1f}s | 成本: ${stats['avg_cost']:.4f}")
    
    # 生成K2測試場景
    k2_scenarios = collector.export_for_k2_testing()
    print(f"\n🧪 已生成 {len(k2_scenarios)} 個K2測試場景")
    
    # 保存報告
    filename = collector.save_comprehensive_report()
    
    print(f"\n📝 接下來可以:")
    print(f"1. 手動添加更多真實使用數據")
    print(f"2. 執行K2 API測試對比")
    print(f"3. 分析不同來源的質量差異")
    print(f"4. 制定基於真實數據的產品策略")

if __name__ == "__main__":
    main()