#!/usr/bin/env python3
"""
增強Real Collector效率系統
智能過濾、質量評分和效率優化
"""

import os
import json
import psutil
import time
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Tuple
import re
import hashlib
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRealCollector:
    """增強版Real Collector"""
    
    def __init__(self):
        self.data_dir = Path("data/real_collector_enhanced")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化質量評分數據庫
        self.db_path = self.data_dir / "quality_scores.db"
        self._init_database()
        
        # 智能過濾配置
        self.filter_config = {
            "min_message_length": 20,        # 最小消息長度
            "max_duplicate_ratio": 0.8,      # 最大重複率
            "min_conversation_depth": 5,     # 最小對話深度
            "quality_threshold": 0.6,        # 質量閾值
            "technical_keywords": [
                "python", "javascript", "api", "database", "algorithm",
                "optimization", "debug", "error", "function", "class",
                "模型", "訓練", "數據", "算法", "優化", "錯誤", "調試"
            ],
            "noise_patterns": [
                r"^ok$", r"^thanks?$", r"^好的$", r"^謝謝$",
                r"^\w{1,3}$",  # 過短回應
                r"^[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$"  # 只有符號
            ]
        }
        
        # 效率監控
        self.performance_metrics = {
            "processed_conversations": 0,
            "filtered_out": 0,
            "high_quality_count": 0,
            "processing_time": 0,
            "start_time": time.time()
        }
    
    def _init_database(self):
        """初始化質量評分數據庫"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_quality (
                    id TEXT PRIMARY KEY,
                    hash TEXT UNIQUE,
                    quality_score REAL,
                    technical_score REAL,
                    depth_score REAL,
                    uniqueness_score REAL,
                    timestamp TEXT,
                    source TEXT,
                    message_count INTEGER,
                    avg_message_length REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_stats (
                    timestamp TEXT,
                    processed_count INTEGER,
                    filtered_count INTEGER,
                    avg_quality REAL,
                    processing_time REAL
                )
            """)
    
    def calculate_quality_score(self, conversation: List[Dict]) -> Tuple[float, Dict]:
        """計算對話質量評分"""
        if not conversation:
            return 0.0, {}
        
        # 1. 技術內容評分 (0-1)
        technical_score = self._calculate_technical_score(conversation)
        
        # 2. 對話深度評分 (0-1)
        depth_score = self._calculate_depth_score(conversation)
        
        # 3. 獨特性評分 (0-1)
        uniqueness_score = self._calculate_uniqueness_score(conversation)
        
        # 4. 結構質量評分 (0-1)
        structure_score = self._calculate_structure_score(conversation)
        
        # 綜合評分
        weights = {
            "technical": 0.3,
            "depth": 0.25,
            "uniqueness": 0.25,
            "structure": 0.2
        }
        
        final_score = (
            technical_score * weights["technical"] +
            depth_score * weights["depth"] +
            uniqueness_score * weights["uniqueness"] +
            structure_score * weights["structure"]
        )
        
        scores_breakdown = {
            "technical_score": technical_score,
            "depth_score": depth_score,
            "uniqueness_score": uniqueness_score,
            "structure_score": structure_score,
            "final_score": final_score
        }
        
        return final_score, scores_breakdown
    
    def _calculate_technical_score(self, conversation: List[Dict]) -> float:
        """計算技術內容評分"""
        technical_count = 0
        total_words = 0
        
        for message in conversation:
            content = message.get("content", "").lower()
            words = content.split()
            total_words += len(words)
            
            # 統計技術關鍵詞
            for keyword in self.filter_config["technical_keywords"]:
                if keyword in content:
                    technical_count += 1
        
        if total_words == 0:
            return 0.0
        
        # 技術密度評分
        technical_density = min(technical_count / (total_words / 10), 1.0)
        
        # 代碼塊加分
        code_bonus = 0.0
        for message in conversation:
            content = message.get("content", "")
            if "```" in content or "def " in content or "function" in content:
                code_bonus += 0.1
        
        return min(technical_density + code_bonus, 1.0)
    
    def _calculate_depth_score(self, conversation: List[Dict]) -> float:
        """計算對話深度評分"""
        message_count = len(conversation)
        avg_length = sum(len(msg.get("content", "")) for msg in conversation) / message_count
        
        # 基於消息數量的深度評分
        depth_by_count = min(message_count / 20, 1.0)  # 20消息為滿分
        
        # 基於平均長度的深度評分
        depth_by_length = min(avg_length / 200, 1.0)   # 200字符為滿分
        
        # 多輪對話評分
        user_assistant_alternation = self._check_alternation(conversation)
        
        return (depth_by_count * 0.4 + depth_by_length * 0.4 + user_assistant_alternation * 0.2)
    
    def _check_alternation(self, conversation: List[Dict]) -> float:
        """檢查用戶和助手的交替對話質量"""
        if len(conversation) < 2:
            return 0.0
        
        alternation_count = 0
        for i in range(1, len(conversation)):
            prev_role = conversation[i-1].get("role", "")
            curr_role = conversation[i].get("role", "")
            if prev_role != curr_role:
                alternation_count += 1
        
        return min(alternation_count / (len(conversation) - 1), 1.0)
    
    def _calculate_uniqueness_score(self, conversation: List[Dict]) -> float:
        """計算獨特性評分"""
        content_hash = self._generate_conversation_hash(conversation)
        
        # 檢查數據庫中是否存在相似對話
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM conversation_quality WHERE hash = ?",
                (content_hash,)
            )
            duplicate_count = cursor.fetchone()[0]
        
        if duplicate_count > 0:
            return 0.2  # 重複內容低分
        
        # 檢查內容重複度
        all_content = " ".join([msg.get("content", "") for msg in conversation])
        words = all_content.split()
        unique_words = set(words)
        
        if len(words) == 0:
            return 0.0
        
        uniqueness_ratio = len(unique_words) / len(words)
        return min(uniqueness_ratio * 1.5, 1.0)  # 1.5倍放大
    
    def _calculate_structure_score(self, conversation: List[Dict]) -> float:
        """計算結構質量評分"""
        if not conversation:
            return 0.0
        
        score = 0.0
        
        # 1. 角色完整性 (有用戶和助手)
        roles = set(msg.get("role", "") for msg in conversation)
        if "user" in roles and "assistant" in roles:
            score += 0.4
        
        # 2. 消息格式完整性
        valid_messages = 0
        for msg in conversation:
            if msg.get("role") and msg.get("content"):
                valid_messages += 1
        
        if len(conversation) > 0:
            format_score = valid_messages / len(conversation)
            score += format_score * 0.3
        
        # 3. 噪音過濾
        noise_count = 0
        for msg in conversation:
            content = msg.get("content", "").strip()
            for pattern in self.filter_config["noise_patterns"]:
                if re.match(pattern, content, re.IGNORECASE):
                    noise_count += 1
                    break
        
        if len(conversation) > 0:
            noise_ratio = noise_count / len(conversation)
            score += (1 - noise_ratio) * 0.3
        
        return min(score, 1.0)
    
    def _generate_conversation_hash(self, conversation: List[Dict]) -> str:
        """生成對話內容的哈希值"""
        content_str = ""
        for msg in conversation:
            content_str += f"{msg.get('role', '')}:{msg.get('content', '')}"
        
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def intelligent_filter(self, conversations: List[Dict]) -> List[Dict]:
        """智能過濾對話數據"""
        start_time = time.time()
        filtered_conversations = []
        
        for conv in conversations:
            conversation_messages = conv.get("conversation", [])
            
            # 1. 基本過濾
            if len(conversation_messages) < self.filter_config["min_conversation_depth"]:
                self.performance_metrics["filtered_out"] += 1
                continue
            
            # 2. 計算質量評分
            quality_score, score_breakdown = self.calculate_quality_score(conversation_messages)
            
            # 3. 質量閾值過濾
            if quality_score < self.filter_config["quality_threshold"]:
                self.performance_metrics["filtered_out"] += 1
                continue
            
            # 4. 添加質量元數據
            conv["quality_metrics"] = score_breakdown
            conv["quality_score"] = quality_score
            
            # 5. 保存到數據庫
            self._save_quality_score(conv, score_breakdown)
            
            filtered_conversations.append(conv)
            
            if quality_score > 0.8:
                self.performance_metrics["high_quality_count"] += 1
        
        # 更新性能指標
        processing_time = time.time() - start_time
        self.performance_metrics["processed_conversations"] += len(conversations)
        self.performance_metrics["processing_time"] += processing_time
        
        logger.info(f"🔍 智能過濾完成: {len(filtered_conversations)}/{len(conversations)} 通過 "
                   f"({len(filtered_conversations)/len(conversations)*100:.1f}%)")
        
        return filtered_conversations
    
    def _save_quality_score(self, conversation: Dict, score_breakdown: Dict):
        """保存質量評分到數據庫"""
        conv_id = conversation.get("id", "")
        conversation_messages = conversation.get("conversation", [])
        content_hash = self._generate_conversation_hash(conversation_messages)
        
        avg_length = sum(len(msg.get("content", "")) for msg in conversation_messages)
        avg_length = avg_length / len(conversation_messages) if conversation_messages else 0
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO conversation_quality 
                (id, hash, quality_score, technical_score, depth_score, 
                 uniqueness_score, timestamp, source, message_count, avg_message_length)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conv_id,
                content_hash,
                score_breakdown["final_score"],
                score_breakdown["technical_score"],
                score_breakdown["depth_score"],
                score_breakdown["uniqueness_score"],
                datetime.now().isoformat(),
                conversation.get("source", "unknown"),
                len(conversation_messages),
                avg_length
            ))
    
    def optimize_collection_efficiency(self):
        """優化收集效率"""
        logger.info("⚡ 開始效率優化...")
        
        # 1. 分析歷史數據，找出高質量來源
        high_quality_sources = self._analyze_quality_sources()
        
        # 2. 動態調整過濾參數
        self._adjust_filter_parameters()
        
        # 3. 內存和CPU優化
        self._optimize_resources()
        
        # 4. 更新收集策略
        recommendations = self._generate_optimization_recommendations()
        
        return recommendations
    
    def _analyze_quality_sources(self) -> Dict:
        """分析高質量數據來源"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT source, AVG(quality_score) as avg_quality, COUNT(*) as count
                FROM conversation_quality 
                GROUP BY source
                HAVING count >= 10
                ORDER BY avg_quality DESC
            """)
            
            results = cursor.fetchall()
        
        return {
            source: {"avg_quality": avg_quality, "count": count}
            for source, avg_quality, count in results
        }
    
    def _adjust_filter_parameters(self):
        """動態調整過濾參數"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT AVG(quality_score), STDDEV(quality_score) 
                FROM conversation_quality 
                WHERE timestamp > datetime('now', '-7 days')
            """)
            
            avg_quality, std_quality = cursor.fetchone()
        
        if avg_quality:
            # 根據最近數據調整閾值
            new_threshold = max(avg_quality - std_quality, 0.3)
            self.filter_config["quality_threshold"] = new_threshold
            logger.info(f"🎯 調整質量閾值: {new_threshold:.3f}")
    
    def _optimize_resources(self):
        """優化資源使用"""
        # 檢查系統資源
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if memory_percent > 80:
            logger.warning(f"⚠️ 內存使用過高: {memory_percent}%")
            # 減少批次大小或清理緩存
        
        if cpu_percent > 80:
            logger.warning(f"⚠️ CPU使用過高: {cpu_percent}%")
            # 增加處理間隔
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """生成優化建議"""
        recommendations = []
        
        # 基於性能指標生成建議
        metrics = self.performance_metrics
        filter_rate = metrics["filtered_out"] / max(metrics["processed_conversations"], 1)
        quality_rate = metrics["high_quality_count"] / max(metrics["processed_conversations"], 1)
        
        if filter_rate > 0.7:
            recommendations.append("過濾率過高，建議降低質量閾值或優化過濾條件")
        
        if quality_rate < 0.2:
            recommendations.append("高質量對話比例較低，建議優化數據來源")
        
        processing_speed = metrics["processed_conversations"] / max(metrics["processing_time"], 1)
        if processing_speed < 10:
            recommendations.append("處理速度較慢，建議優化算法或增加並行處理")
        
        return recommendations
    
    def get_performance_report(self) -> Dict:
        """獲取性能報告"""
        runtime = time.time() - self.performance_metrics["start_time"]
        
        # 從數據庫獲取統計
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_conversations,
                    AVG(quality_score) as avg_quality,
                    COUNT(CASE WHEN quality_score > 0.8 THEN 1 END) as high_quality_count,
                    AVG(message_count) as avg_message_count,
                    AVG(avg_message_length) as avg_message_length
                FROM conversation_quality
            """)
            
            db_stats = cursor.fetchone()
        
        return {
            "performance_metrics": self.performance_metrics,
            "runtime_hours": runtime / 3600,
            "processing_rate": self.performance_metrics["processed_conversations"] / max(runtime, 1),
            "quality_stats": {
                "total_in_db": db_stats[0] if db_stats[0] else 0,
                "average_quality": db_stats[1] if db_stats[1] else 0,
                "high_quality_count": db_stats[2] if db_stats[2] else 0,
                "avg_message_count": db_stats[3] if db_stats[3] else 0,
                "avg_message_length": db_stats[4] if db_stats[4] else 0
            },
            "efficiency_recommendations": self._generate_optimization_recommendations()
        }

def main():
    """主函數"""
    collector = EnhancedRealCollector()
    
    # 顯示性能報告
    report = collector.get_performance_report()
    print(f"📊 Enhanced Real Collector 性能報告:")
    print(f"  運行時間: {report['runtime_hours']:.2f} 小時")
    print(f"  處理速度: {report['processing_rate']:.2f} 對話/秒")
    print(f"  數據庫總對話: {report['quality_stats']['total_in_db']}")
    print(f"  平均質量分數: {report['quality_stats']['average_quality']:.3f}")
    print(f"  高質量對話: {report['quality_stats']['high_quality_count']}")
    
    print(f"\n💡 優化建議:")
    for rec in report["efficiency_recommendations"]:
        print(f"  - {rec}")
    
    # 執行效率優化
    print(f"\n⚡ 執行效率優化...")
    recommendations = collector.optimize_collection_efficiency()
    
    print(f"✅ Enhanced Real Collector 已優化完成")

if __name__ == "__main__":
    main()