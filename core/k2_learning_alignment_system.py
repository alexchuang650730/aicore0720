#!/usr/bin/env python3
"""
K2 學習對齊系統 - 從 Claude Code Tool 的使用記錄中學習
每天16小時的編程記錄將被分析、提取並用於訓練K2模型的對齊
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib

@dataclass
class CodingSession:
    """編程會話記錄"""
    session_id: str
    start_time: str
    end_time: str
    duration_hours: float
    user_id: str
    interactions: List[Dict[str, Any]]
    files_created: List[str]
    files_modified: List[str]
    commands_used: List[str]
    errors_encountered: List[Dict[str, Any]]
    successful_patterns: List[str]

@dataclass
class LearningPattern:
    """學習到的模式"""
    pattern_id: str
    pattern_type: str  # command, code_generation, error_fix, refactoring
    trigger: str  # 觸發條件
    claude_response: str  # Claude的響應
    k2_response: str  # K2的響應（用於對比）
    success_rate: float
    usage_count: int
    context_requirements: Dict[str, Any]

class K2LearningAlignmentSystem:
    """K2 學習對齊系統"""
    
    def __init__(self):
        self.data_path = Path.home() / ".powerautomation" / "k2_learning"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # 數據存儲
        self.sessions_db = self.data_path / "coding_sessions.json"
        self.patterns_db = self.data_path / "learned_patterns.json"
        self.alignment_db = self.data_path / "k2_alignment.json"
        
        # 學習配置
        self.learning_config = {
            "min_pattern_occurrences": 3,  # 模式最少出現次數
            "confidence_threshold": 0.8,   # 置信度閾值
            "batch_size": 100,            # 批次大小
            "learning_interval_hours": 4   # 學習間隔
        }
        
        # 載入現有數據
        self._load_data()
        
        # 啟動背景學習任務
        self.learning_task = None
        
    def _load_data(self):
        """載入現有數據"""
        self.sessions = {}
        self.patterns = {}
        self.alignment_data = {
            "total_hours_analyzed": 0,
            "patterns_learned": 0,
            "alignment_score": 0.0,
            "last_update": None
        }
        
        if self.sessions_db.exists():
            with open(self.sessions_db, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sessions = {k: CodingSession(**v) for k, v in data.items()}
                
        if self.patterns_db.exists():
            with open(self.patterns_db, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.patterns = {k: LearningPattern(**v) for k, v in data.items()}
                
        if self.alignment_db.exists():
            with open(self.alignment_db, 'r', encoding='utf-8') as f:
                self.alignment_data = json.load(f)
                
    def _save_data(self):
        """保存數據"""
        # 保存會話
        sessions_data = {k: asdict(v) for k, v in self.sessions.items()}
        with open(self.sessions_db, 'w', encoding='utf-8') as f:
            json.dump(sessions_data, f, ensure_ascii=False, indent=2)
            
        # 保存模式
        patterns_data = {k: asdict(v) for k, v in self.patterns.items()}
        with open(self.patterns_db, 'w', encoding='utf-8') as f:
            json.dump(patterns_data, f, ensure_ascii=False, indent=2)
            
        # 保存對齊數據
        with open(self.alignment_db, 'w', encoding='utf-8') as f:
            json.dump(self.alignment_data, f, ensure_ascii=False, indent=2)
            
    async def start_continuous_learning(self):
        """啟動持續學習"""
        print("🧠 啟動 K2 持續學習系統...")
        self.learning_task = asyncio.create_task(self._continuous_learning_loop())
        
    async def _continuous_learning_loop(self):
        """持續學習循環"""
        while True:
            try:
                # 收集最近的編程會話
                recent_sessions = await self._collect_recent_sessions()
                
                if recent_sessions:
                    print(f"📊 發現 {len(recent_sessions)} 個新會話待分析")
                    
                    # 分析會話提取模式
                    new_patterns = await self._analyze_sessions(recent_sessions)
                    
                    # 對齊 K2 響應
                    await self._align_k2_responses(new_patterns)
                    
                    # 更新統計
                    self._update_statistics(recent_sessions, new_patterns)
                    
                    print(f"✅ 學習完成，新增 {len(new_patterns)} 個模式")
                    
                # 等待下一個學習週期
                await asyncio.sleep(self.learning_config["learning_interval_hours"] * 3600)
                
            except Exception as e:
                print(f"❌ 學習過程出錯: {e}")
                await asyncio.sleep(300)  # 5分鐘後重試
                
    async def _collect_recent_sessions(self) -> List[CodingSession]:
        """收集最近的編程會話"""
        # 從 Claude Code Tool 日誌收集
        claude_logs_path = Path.home() / ".claude-code" / "logs"
        recent_sessions = []
        
        if claude_logs_path.exists():
            cutoff_time = datetime.now() - timedelta(
                hours=self.learning_config["learning_interval_hours"]
            )
            
            for log_file in claude_logs_path.glob("*.json"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                        
                    # 轉換為會話格式
                    session = self._parse_claude_log(log_data)
                    
                    if session and datetime.fromisoformat(session.start_time) > cutoff_time:
                        recent_sessions.append(session)
                        
                except Exception as e:
                    print(f"⚠️ 解析日誌失敗 {log_file}: {e}")
                    
        return recent_sessions
        
    def _parse_claude_log(self, log_data: Dict[str, Any]) -> Optional[CodingSession]:
        """解析 Claude 日誌"""
        try:
            interactions = []
            files_created = []
            files_modified = []
            commands_used = []
            errors = []
            patterns = []
            
            # 提取交互記錄
            for entry in log_data.get("entries", []):
                if entry["type"] == "interaction":
                    interactions.append({
                        "timestamp": entry["timestamp"],
                        "user_input": entry["user_input"],
                        "claude_response": entry["response"],
                        "execution_time": entry.get("execution_time", 0)
                    })
                    
                    # 提取命令
                    if entry["user_input"].startswith("/"):
                        commands_used.append(entry["user_input"].split()[0])
                        
                    # 提取文件操作
                    if "files" in entry:
                        for file_op in entry["files"]:
                            if file_op["action"] == "create":
                                files_created.append(file_op["path"])
                            elif file_op["action"] == "modify":
                                files_modified.append(file_op["path"])
                                
                    # 提取錯誤
                    if "error" in entry:
                        errors.append({
                            "error": entry["error"],
                            "context": entry.get("context", {})
                        })
                        
                    # 識別成功模式
                    if entry.get("success", False):
                        pattern = self._extract_pattern(entry)
                        if pattern:
                            patterns.append(pattern)
                            
            # 創建會話對象
            session_id = self._generate_id(f"session_{log_data.get('session_id', '')}")
            
            return CodingSession(
                session_id=session_id,
                start_time=log_data.get("start_time", datetime.now().isoformat()),
                end_time=log_data.get("end_time", datetime.now().isoformat()),
                duration_hours=log_data.get("duration_hours", 0),
                user_id=log_data.get("user_id", "unknown"),
                interactions=interactions,
                files_created=files_created,
                files_modified=files_modified,
                commands_used=commands_used,
                errors_encountered=errors,
                successful_patterns=patterns
            )
            
        except Exception as e:
            print(f"⚠️ 解析會話失敗: {e}")
            return None
            
    def _extract_pattern(self, interaction: Dict[str, Any]) -> Optional[str]:
        """從交互中提取模式"""
        user_input = interaction.get("user_input", "")
        response = interaction.get("response", "")
        
        # 識別常見模式
        if "generate" in user_input and "component" in user_input:
            return "component_generation"
        elif "fix" in user_input and "error" in user_input:
            return "error_fixing"
        elif "refactor" in user_input:
            return "code_refactoring"
        elif "test" in user_input:
            return "test_creation"
        elif "deploy" in user_input:
            return "deployment_task"
            
        return None
        
    async def _analyze_sessions(self, sessions: List[CodingSession]) -> List[LearningPattern]:
        """分析會話提取學習模式"""
        pattern_candidates = defaultdict(list)
        
        for session in sessions:
            # 分析每個交互
            for interaction in session.interactions:
                # 提取觸發條件和響應
                trigger = interaction["user_input"]
                response = interaction["claude_response"]
                
                # 識別模式類型
                pattern_type = self._classify_pattern_type(trigger, response)
                
                if pattern_type:
                    pattern_key = f"{pattern_type}:{self._normalize_trigger(trigger)}"
                    pattern_candidates[pattern_key].append({
                        "trigger": trigger,
                        "response": response,
                        "context": {
                            "files": session.files_created + session.files_modified,
                            "previous_commands": session.commands_used[-5:],
                            "errors": session.errors_encountered
                        }
                    })
                    
        # 篩選高頻模式
        learned_patterns = []
        
        for pattern_key, instances in pattern_candidates.items():
            if len(instances) >= self.learning_config["min_pattern_occurrences"]:
                # 創建學習模式
                pattern_type, normalized_trigger = pattern_key.split(":", 1)
                
                pattern = LearningPattern(
                    pattern_id=self._generate_id(pattern_key),
                    pattern_type=pattern_type,
                    trigger=normalized_trigger,
                    claude_response=self._merge_responses(instances),
                    k2_response="",  # 待生成
                    success_rate=self._calculate_success_rate(instances),
                    usage_count=len(instances),
                    context_requirements=self._extract_context_requirements(instances)
                )
                
                learned_patterns.append(pattern)
                
        return learned_patterns
        
    def _classify_pattern_type(self, trigger: str, response: str) -> Optional[str]:
        """分類模式類型"""
        trigger_lower = trigger.lower()
        
        if trigger_lower.startswith("/"):
            return "command"
        elif "generate" in trigger_lower or "create" in trigger_lower:
            return "code_generation"
        elif "fix" in trigger_lower or "error" in trigger_lower:
            return "error_fix"
        elif "refactor" in trigger_lower or "optimize" in trigger_lower:
            return "refactoring"
        elif "explain" in trigger_lower or "what" in trigger_lower:
            return "explanation"
            
        return "general"
        
    def _normalize_trigger(self, trigger: str) -> str:
        """標準化觸發條件"""
        # 移除特定值，保留模式
        import re
        
        # 替換文件路徑
        normalized = re.sub(r'[./\w-]+\.\w+', '<FILE>', trigger)
        
        # 替換數字
        normalized = re.sub(r'\b\d+\b', '<NUM>', normalized)
        
        # 替換字符串
        normalized = re.sub(r'"[^"]*"', '<STR>', normalized)
        normalized = re.sub(r"'[^']*'", '<STR>', normalized)
        
        return normalized.strip()
        
    def _merge_responses(self, instances: List[Dict[str, Any]]) -> str:
        """合併多個響應為模板"""
        # 簡單實現：取最常見的響應結構
        # 實際應該使用更智能的模板提取
        if instances:
            return instances[0]["response"]
        return ""
        
    def _calculate_success_rate(self, instances: List[Dict[str, Any]]) -> float:
        """計算成功率"""
        # 基於錯誤數量計算
        total = len(instances)
        errors = sum(1 for inst in instances if inst.get("context", {}).get("errors"))
        
        return (total - errors) / total if total > 0 else 0.0
        
    def _extract_context_requirements(self, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提取上下文需求"""
        requirements = {
            "required_files": [],
            "required_commands": [],
            "common_errors": []
        }
        
        # 統計共同元素
        file_counts = defaultdict(int)
        command_counts = defaultdict(int)
        error_counts = defaultdict(int)
        
        for inst in instances:
            context = inst.get("context", {})
            
            for file in context.get("files", []):
                file_counts[self._get_file_type(file)] += 1
                
            for cmd in context.get("previous_commands", []):
                command_counts[cmd] += 1
                
            for error in context.get("errors", []):
                error_counts[error.get("error", "")] += 1
                
        # 提取高頻需求
        threshold = len(instances) * 0.5
        
        requirements["required_files"] = [
            file_type for file_type, count in file_counts.items()
            if count >= threshold
        ]
        
        requirements["required_commands"] = [
            cmd for cmd, count in command_counts.items()
            if count >= threshold
        ]
        
        requirements["common_errors"] = [
            error for error, count in error_counts.items()
            if count >= 2
        ]
        
        return requirements
        
    def _get_file_type(self, file_path: str) -> str:
        """獲取文件類型"""
        return Path(file_path).suffix or "unknown"
        
    async def _align_k2_responses(self, patterns: List[LearningPattern]):
        """對齊 K2 響應"""
        print("🔄 開始 K2 響應對齊...")
        
        for pattern in patterns:
            # 生成 K2 響應模板
            k2_response = await self._generate_k2_response(pattern)
            pattern.k2_response = k2_response
            
            # 保存到模式庫
            self.patterns[pattern.pattern_id] = pattern
            
        self._save_data()
        
    async def _generate_k2_response(self, pattern: LearningPattern) -> str:
        """生成 K2 響應模板"""
        # 基於 Claude 響應生成 K2 版本
        # 實際實現應該調用 K2 API 進行微調
        
        # 簡化響應，提高效率
        claude_response = pattern.claude_response
        
        # 提取關鍵動作
        k2_response = f"[K2 Optimized]\n"
        
        if pattern.pattern_type == "code_generation":
            k2_response += "快速生成代碼...\n"
        elif pattern.pattern_type == "error_fix":
            k2_response += "診斷並修復錯誤...\n"
        elif pattern.pattern_type == "command":
            k2_response += "執行命令...\n"
            
        # 保留核心內容，移除冗餘解釋
        k2_response += self._simplify_response(claude_response)
        
        return k2_response
        
    def _simplify_response(self, response: str) -> str:
        """簡化響應內容"""
        # 移除過多的解釋
        lines = response.split('\n')
        
        # 保留代碼塊和關鍵信息
        simplified = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                simplified.append(line)
            elif in_code_block:
                simplified.append(line)
            elif any(keyword in line.lower() for keyword in ["error", "warning", "success", "created", "fixed"]):
                simplified.append(line)
                
        return '\n'.join(simplified)
        
    def _update_statistics(self, sessions: List[CodingSession], patterns: List[LearningPattern]):
        """更新統計數據"""
        # 計算總學習時間
        total_hours = sum(session.duration_hours for session in sessions)
        self.alignment_data["total_hours_analyzed"] += total_hours
        
        # 更新模式數量
        self.alignment_data["patterns_learned"] = len(self.patterns)
        
        # 計算對齊分數
        if self.patterns:
            avg_success_rate = sum(p.success_rate for p in self.patterns.values()) / len(self.patterns)
            self.alignment_data["alignment_score"] = avg_success_rate
            
        self.alignment_data["last_update"] = datetime.now().isoformat()
        
        self._save_data()
        
        # 生成報告
        self._generate_learning_report()
        
    def _generate_learning_report(self):
        """生成學習報告"""
        report = f"""
📊 K2 學習對齊報告
生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 學習統計:
- 總分析時間: {self.alignment_data['total_hours_analyzed']:.1f} 小時
- 學習模式數: {self.alignment_data['patterns_learned']}
- 對齊分數: {self.alignment_data['alignment_score']:.2%}

🎯 高頻模式 Top 5:
"""
        
        # 排序模式
        sorted_patterns = sorted(
            self.patterns.values(), 
            key=lambda p: p.usage_count, 
            reverse=True
        )[:5]
        
        for i, pattern in enumerate(sorted_patterns, 1):
            report += f"{i}. {pattern.pattern_type}: {pattern.trigger} (使用 {pattern.usage_count} 次)\n"
            
        # 保存報告
        report_path = self.data_path / "learning_report.md"
        report_path.write_text(report, encoding='utf-8')
        
        print(f"\n{report}")
        
    def _generate_id(self, content: str) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{content}_{datetime.now()}".encode()).hexdigest()[:16]
        
    async def get_k2_response_template(self, user_input: str) -> Optional[Dict[str, Any]]:
        """獲取 K2 響應模板"""
        # 標準化輸入
        normalized = self._normalize_trigger(user_input)
        
        # 查找匹配的模式
        for pattern in self.patterns.values():
            if pattern.trigger == normalized or self._is_similar(pattern.trigger, normalized):
                return {
                    "pattern_id": pattern.pattern_id,
                    "k2_response": pattern.k2_response,
                    "confidence": pattern.success_rate,
                    "context_requirements": pattern.context_requirements,
                    "usage_count": pattern.usage_count
                }
                
        return None
        
    def _is_similar(self, pattern: str, input: str) -> bool:
        """檢查相似性"""
        # 簡單的相似性檢查
        pattern_tokens = set(pattern.lower().split())
        input_tokens = set(input.lower().split())
        
        intersection = pattern_tokens.intersection(input_tokens)
        union = pattern_tokens.union(input_tokens)
        
        if not union:
            return False
            
        similarity = len(intersection) / len(union)
        return similarity > 0.7


# 創建全局實例
k2_learning_system = K2LearningAlignmentSystem()


async def start_k2_learning():
    """啟動 K2 學習"""
    await k2_learning_system.start_continuous_learning()


async def get_k2_aligned_response(user_input: str) -> Optional[Dict[str, Any]]:
    """獲取 K2 對齊的響應"""
    return await k2_learning_system.get_k2_response_template(user_input)