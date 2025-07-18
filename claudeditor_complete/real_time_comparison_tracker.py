#!/usr/bin/env python3
"""
實時對比追蹤器 - 利用真實編程場景收集數據
基於1000小時Manus經驗 + 16小時/天Claude Code Tool使用
"""

import json
import time
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class RealTimeComparison:
    """實時對比記錄"""
    id: str
    timestamp: float
    prompt: str
    prompt_category: str
    complexity_level: str  # simple, medium, complex
    context: str  # 上下文描述
    
    # Claude Code Tool結果
    claude_response: str
    claude_time_seconds: float
    claude_satisfaction: int  # 1-10分
    claude_usable: bool
    claude_notes: str
    
    # K2結果 (如果測試了)
    k2_response: Optional[str] = None
    k2_time_seconds: Optional[float] = None
    k2_satisfaction: Optional[int] = None
    k2_usable: Optional[bool] = None
    k2_notes: Optional[str] = None
    
    # 對比結論
    preferred_model: str = "claude"  # claude, k2, tie
    quality_gap_percentage: Optional[float] = None
    cost_consideration: Optional[str] = None
    use_case_recommendation: Optional[str] = None

class RealTimeComparisonTracker:
    """實時對比追蹤器"""
    
    def __init__(self, db_path: str = "real_comparison_data.db"):
        self.db_path = db_path
        self._init_database()
        self.session_data = []
        
    def _init_database(self):
        """初始化數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comparisons (
            id TEXT PRIMARY KEY,
            timestamp REAL,
            prompt TEXT,
            prompt_category TEXT,
            complexity_level TEXT,
            context TEXT,
            claude_response TEXT,
            claude_time_seconds REAL,
            claude_satisfaction INTEGER,
            claude_usable BOOLEAN,
            claude_notes TEXT,
            k2_response TEXT,
            k2_time_seconds REAL,
            k2_satisfaction INTEGER,
            k2_usable BOOLEAN,
            k2_notes TEXT,
            preferred_model TEXT,
            quality_gap_percentage REAL,
            cost_consideration TEXT,
            use_case_recommendation TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"📊 數據庫已初始化: {self.db_path}")
    
    def log_comparison(self, comparison: RealTimeComparison) -> None:
        """記錄對比數據"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 轉換為字典
        data = asdict(comparison)
        
        # 插入數據
        columns = list(data.keys())
        placeholders = ['?' for _ in columns]
        values = list(data.values())
        
        query = f"INSERT OR REPLACE INTO comparisons ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        print(f"✅ 已記錄對比數據: {comparison.prompt[:50]}...")
    
    def quick_log_claude_only(self, 
                             prompt: str,
                             category: str,
                             complexity: str,
                             response: str,
                             satisfaction: int,
                             time_seconds: float,
                             notes: str = "") -> str:
        """快速記錄Claude使用數據"""
        
        comparison_id = hashlib.md5(f"{prompt}{time.time()}".encode()).hexdigest()[:12]
        
        comparison = RealTimeComparison(
            id=comparison_id,
            timestamp=time.time(),
            prompt=prompt,
            prompt_category=category,
            complexity_level=complexity,
            context="Real coding session",
            claude_response=response,
            claude_time_seconds=time_seconds,
            claude_satisfaction=satisfaction,
            claude_usable=satisfaction >= 7,
            claude_notes=notes
        )
        
        self.log_comparison(comparison)
        return comparison_id
    
    def add_k2_comparison(self,
                         comparison_id: str,
                         k2_response: str,
                         k2_satisfaction: int,
                         k2_time_seconds: float,
                         k2_notes: str = "") -> None:
        """為已存在的記錄添加K2對比數據"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 計算偏好和質量差距
        cursor.execute("SELECT claude_satisfaction FROM comparisons WHERE id = ?", (comparison_id,))
        result = cursor.fetchone()
        
        if result:
            claude_satisfaction = result[0]
            quality_gap = ((claude_satisfaction - k2_satisfaction) / claude_satisfaction * 100) if claude_satisfaction > 0 else 0
            
            preferred = "claude" if claude_satisfaction > k2_satisfaction else "k2" if k2_satisfaction > claude_satisfaction else "tie"
            
            # 成本考量
            cost_analysis = self._analyze_cost_benefit(claude_satisfaction, k2_satisfaction)
            
            cursor.execute('''
            UPDATE comparisons SET
                k2_response = ?,
                k2_time_seconds = ?,
                k2_satisfaction = ?,
                k2_usable = ?,
                k2_notes = ?,
                preferred_model = ?,
                quality_gap_percentage = ?,
                cost_consideration = ?
            WHERE id = ?
            ''', (k2_response, k2_time_seconds, k2_satisfaction, k2_satisfaction >= 7, 
                  k2_notes, preferred, quality_gap, cost_analysis, comparison_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 已添加K2對比數據: {comparison_id}")
    
    def _analyze_cost_benefit(self, claude_score: int, k2_score: int) -> str:
        """分析成本效益"""
        quality_gap = claude_score - k2_score
        
        if quality_gap <= 1:
            return "K2性價比極高，強烈推薦"
        elif quality_gap <= 2:
            return "K2性價比很好，推薦使用"
        elif quality_gap <= 3:
            return "K2可接受，適合成本敏感場景"
        else:
            return "Claude質量優勢明顯，建議使用"
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計數據"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 基本統計
        cursor.execute("SELECT COUNT(*) FROM comparisons")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM comparisons WHERE k2_response IS NOT NULL")
        comparison_records = cursor.fetchone()[0]
        
        # Claude統計
        cursor.execute("SELECT AVG(claude_satisfaction), AVG(claude_time_seconds) FROM comparisons")
        claude_stats = cursor.fetchone()
        
        # K2統計
        cursor.execute("SELECT AVG(k2_satisfaction), AVG(k2_time_seconds) FROM comparisons WHERE k2_response IS NOT NULL")
        k2_stats = cursor.fetchone()
        
        # 偏好統計
        cursor.execute("SELECT preferred_model, COUNT(*) FROM comparisons WHERE preferred_model IS NOT NULL GROUP BY preferred_model")
        preference_stats = dict(cursor.fetchall())
        
        # 分類統計
        cursor.execute("SELECT prompt_category, AVG(claude_satisfaction) FROM comparisons GROUP BY prompt_category")
        category_claude = dict(cursor.fetchall())
        
        cursor.execute("SELECT prompt_category, AVG(k2_satisfaction) FROM comparisons WHERE k2_response IS NOT NULL GROUP BY prompt_category")
        category_k2 = dict(cursor.fetchall())
        
        # 複雜度統計
        cursor.execute("SELECT complexity_level, AVG(claude_satisfaction) FROM comparisons GROUP BY complexity_level")
        complexity_claude = dict(cursor.fetchall())
        
        cursor.execute("SELECT complexity_level, AVG(k2_satisfaction) FROM comparisons WHERE k2_response IS NOT NULL GROUP BY complexity_level")
        complexity_k2 = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "summary": {
                "total_records": total_records,
                "comparison_records": comparison_records,
                "claude_avg_satisfaction": claude_stats[0] if claude_stats[0] else 0,
                "claude_avg_time": claude_stats[1] if claude_stats[1] else 0,
                "k2_avg_satisfaction": k2_stats[0] if k2_stats[0] else 0,
                "k2_avg_time": k2_stats[1] if k2_stats[1] else 0,
                "quality_gap": (claude_stats[0] - k2_stats[0]) if (claude_stats[0] and k2_stats[0]) else 0
            },
            "preferences": preference_stats,
            "by_category": {
                "claude": category_claude,
                "k2": category_k2
            },
            "by_complexity": {
                "claude": complexity_claude,
                "k2": complexity_k2
            }
        }
    
    def generate_insights(self) -> Dict[str, Any]:
        """生成洞察報告"""
        stats = self.get_statistics()
        
        insights = {
            "quality_assessment": "",
            "cost_recommendations": [],
            "use_case_recommendations": {},
            "improvement_suggestions": []
        }
        
        # 質量評估
        quality_gap = stats["summary"]["quality_gap"]
        if quality_gap < 1:
            insights["quality_assessment"] = "K2與Claude質量相當，可大膽使用"
        elif quality_gap < 2:
            insights["quality_assessment"] = "K2質量略遜，但性價比優秀"
        elif quality_gap < 3:
            insights["quality_assessment"] = "K2質量可接受，適合特定場景"
        else:
            insights["quality_assessment"] = "Claude質量明顯更好，K2需要改進"
        
        # 成本建議
        if quality_gap <= 2:
            insights["cost_recommendations"].append("建議優先使用K2，90%成本節省")
            insights["cost_recommendations"].append("僅在關鍵任務使用Claude")
        else:
            insights["cost_recommendations"].append("建議混合使用，平衡質量與成本")
            insights["cost_recommendations"].append("簡單任務用K2，複雜任務用Claude")
        
        # 使用場景建議
        for category, claude_score in stats["by_category"]["claude"].items():
            k2_score = stats["by_category"]["k2"].get(category, 0)
            if k2_score > 0:
                gap = claude_score - k2_score
                if gap <= 1:
                    insights["use_case_recommendations"][category] = "K2優先"
                elif gap <= 2:
                    insights["use_case_recommendations"][category] = "K2可用"
                else:
                    insights["use_case_recommendations"][category] = "Claude推薦"
        
        return insights
    
    def export_data(self, format: str = "json") -> str:
        """導出數據"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM comparisons")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        conn.close()
        
        if format == "json":
            filename = f"comparison_export_{int(time.time())}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filename
        
        return "export_complete"

# 便捷使用函數
def quick_claude_log(prompt: str, response: str, satisfaction: int, time_seconds: float, 
                    category: str = "general", complexity: str = "medium", notes: str = "") -> str:
    """快速記錄Claude使用"""
    tracker = RealTimeComparisonTracker()
    return tracker.quick_log_claude_only(prompt, category, complexity, response, satisfaction, time_seconds, notes)

def add_k2_test(comparison_id: str, k2_response: str, k2_satisfaction: int, k2_time: float, notes: str = ""):
    """添加K2測試結果"""
    tracker = RealTimeComparisonTracker()
    tracker.add_k2_comparison(comparison_id, k2_response, k2_satisfaction, k2_time, notes)

def show_stats():
    """顯示統計數據"""
    tracker = RealTimeComparisonTracker()
    stats = tracker.get_statistics()
    insights = tracker.generate_insights()
    
    print("\n📊 實時對比統計報告")
    print("=" * 50)
    
    print(f"\n📈 基本統計:")
    print(f"   總記錄數: {stats['summary']['total_records']}")
    print(f"   對比記錄: {stats['summary']['comparison_records']}")
    print(f"   Claude平均滿意度: {stats['summary']['claude_avg_satisfaction']:.1f}/10")
    print(f"   K2平均滿意度: {stats['summary']['k2_avg_satisfaction']:.1f}/10")
    print(f"   質量差距: {stats['summary']['quality_gap']:.1f}分")
    
    print(f"\n🎯 洞察分析:")
    print(f"   質量評估: {insights['quality_assessment']}")
    print(f"   成本建議: {', '.join(insights['cost_recommendations'])}")
    
    print(f"\n📝 使用場景建議:")
    for category, recommendation in insights['use_case_recommendations'].items():
        print(f"   {category}: {recommendation}")

# 命令行工具
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print("🚀 實時對比追蹤器")
        print("\n使用方法:")
        print("  python real_time_comparison_tracker.py stats  # 查看統計")
        print("  python real_time_comparison_tracker.py export # 導出數據")
        print("\n程式化使用:")
        print("  from real_time_comparison_tracker import quick_claude_log, add_k2_test")
        
    elif sys.argv[1] == "stats":
        show_stats()
        
    elif sys.argv[1] == "export":
        tracker = RealTimeComparisonTracker()
        filename = tracker.export_data()
        print(f"✅ 數據已導出到: {filename}")
        
    else:
        print("❌ 未知命令")