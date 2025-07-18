#!/usr/bin/env python3
"""
MCP-Zero 上下文管理器
優化上下文使用，智能管理 token 分配
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import json
import time

logger = logging.getLogger(__name__)


@dataclass
class ContextWindow:
    """上下文窗口"""
    content: str
    tokens: int
    priority: int  # 0-10，越高越重要
    timestamp: float
    source: str  # 來源（step_id, mcp_name 等）
    expiry: Optional[float] = None  # 過期時間


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, max_tokens: int = 100000):
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.context_windows: List[ContextWindow] = []
        self.context_history: deque = deque(maxlen=1000)
        self.compression_strategies = self._init_compression_strategies()
        
    def _init_compression_strategies(self) -> Dict[str, Any]:
        """初始化壓縮策略"""
        return {
            "summarization": {
                "threshold": 0.8,  # 當上下文使用超過 80% 時啟動
                "ratio": 0.3,      # 壓縮到原來的 30%
                "min_priority": 5  # 只壓縮優先級低於 5 的內容
            },
            "truncation": {
                "threshold": 0.9,
                "keep_recent": 20,  # 保留最近的 20 個窗口
                "min_priority": 3
            },
            "removal": {
                "threshold": 0.95,
                "min_priority": 2
            }
        }
        
    def add_context(
        self, 
        content: str, 
        tokens: int, 
        priority: int,
        source: str,
        expiry: Optional[float] = None
    ) -> bool:
        """添加上下文"""
        # 檢查是否需要壓縮
        if self.current_tokens + tokens > self.max_tokens:
            logger.info(f"上下文即將溢出，需要 {tokens} tokens，當前 {self.current_tokens}/{self.max_tokens}")
            
            # 嘗試壓縮
            freed_tokens = self._compress_context(tokens)
            
            if self.current_tokens + tokens > self.max_tokens:
                logger.error("無法騰出足夠的上下文空間")
                return False
                
        # 創建上下文窗口
        window = ContextWindow(
            content=content,
            tokens=tokens,
            priority=priority,
            timestamp=time.time(),
            source=source,
            expiry=expiry
        )
        
        # 插入到適當位置（按優先級排序）
        insert_pos = 0
        for i, w in enumerate(self.context_windows):
            if w.priority < priority:
                insert_pos = i
                break
        else:
            insert_pos = len(self.context_windows)
            
        self.context_windows.insert(insert_pos, window)
        self.current_tokens += tokens
        
        # 記錄歷史
        self.context_history.append({
            "action": "add",
            "source": source,
            "tokens": tokens,
            "timestamp": time.time()
        })
        
        logger.info(f"添加上下文: {source}, {tokens} tokens, 優先級 {priority}")
        return True
        
    def get_context_for_step(self, step_id: str, required_sources: List[str]) -> str:
        """獲取步驟所需的上下文"""
        relevant_windows = []
        
        # 收集相關的上下文窗口
        for window in self.context_windows:
            # 檢查是否過期
            if window.expiry and time.time() > window.expiry:
                continue
                
            # 檢查是否是需要的來源
            if window.source in required_sources or window.priority >= 8:
                relevant_windows.append(window)
                
        # 按優先級和時間排序
        relevant_windows.sort(key=lambda w: (w.priority, w.timestamp), reverse=True)
        
        # 組合上下文
        context_parts = []
        total_tokens = 0
        max_step_tokens = self.max_tokens * 0.5  # 單步最多使用 50% 的上下文
        
        for window in relevant_windows:
            if total_tokens + window.tokens <= max_step_tokens:
                context_parts.append(f"[{window.source}]\n{window.content}\n")
                total_tokens += window.tokens
                
        return "\n".join(context_parts)
        
    def _compress_context(self, needed_tokens: int) -> int:
        """壓縮上下文以騰出空間"""
        freed_tokens = 0
        
        # 1. 移除過期的窗口
        freed_tokens += self._remove_expired_windows()
        
        if freed_tokens >= needed_tokens:
            return freed_tokens
            
        # 2. 應用壓縮策略
        usage_ratio = self.current_tokens / self.max_tokens
        
        for strategy_name, config in self.compression_strategies.items():
            if usage_ratio >= config["threshold"]:
                if strategy_name == "summarization":
                    freed_tokens += self._apply_summarization(config)
                elif strategy_name == "truncation":
                    freed_tokens += self._apply_truncation(config)
                elif strategy_name == "removal":
                    freed_tokens += self._apply_removal(config)
                    
                if freed_tokens >= needed_tokens:
                    break
                    
        return freed_tokens
        
    def _remove_expired_windows(self) -> int:
        """移除過期的上下文窗口"""
        current_time = time.time()
        freed_tokens = 0
        
        # 從後向前遍歷，安全刪除
        for i in range(len(self.context_windows) - 1, -1, -1):
            window = self.context_windows[i]
            if window.expiry and current_time > window.expiry:
                freed_tokens += window.tokens
                self.context_windows.pop(i)
                logger.info(f"移除過期上下文: {window.source}, 釋放 {window.tokens} tokens")
                
        self.current_tokens -= freed_tokens
        return freed_tokens
        
    def _apply_summarization(self, config: Dict[str, Any]) -> int:
        """應用摘要壓縮"""
        freed_tokens = 0
        
        for i, window in enumerate(self.context_windows):
            if window.priority < config["min_priority"]:
                # 模擬摘要（實際應調用 LLM）
                original_tokens = window.tokens
                compressed_tokens = int(original_tokens * config["ratio"])
                
                # 簡單的摘要模擬：截斷內容
                compressed_content = window.content[:int(len(window.content) * config["ratio"])] + "..."
                
                # 更新窗口
                self.context_windows[i] = ContextWindow(
                    content=compressed_content,
                    tokens=compressed_tokens,
                    priority=window.priority,
                    timestamp=window.timestamp,
                    source=f"{window.source}_compressed",
                    expiry=window.expiry
                )
                
                freed_tokens += original_tokens - compressed_tokens
                logger.info(f"壓縮上下文: {window.source}, 從 {original_tokens} 到 {compressed_tokens} tokens")
                
        self.current_tokens -= freed_tokens
        return freed_tokens
        
    def _apply_truncation(self, config: Dict[str, Any]) -> int:
        """應用截斷策略"""
        # 保留最近的 N 個高優先級窗口
        keep_count = config["keep_recent"]
        min_priority = config["min_priority"]
        
        # 分離高優先級和低優先級窗口
        high_priority = [w for w in self.context_windows if w.priority >= min_priority]
        low_priority = [w for w in self.context_windows if w.priority < min_priority]
        
        # 截斷低優先級窗口
        if len(low_priority) > keep_count:
            to_remove = low_priority[keep_count:]
            freed_tokens = sum(w.tokens for w in to_remove)
            
            # 重建窗口列表
            self.context_windows = high_priority + low_priority[:keep_count]
            self.current_tokens -= freed_tokens
            
            logger.info(f"截斷 {len(to_remove)} 個低優先級窗口，釋放 {freed_tokens} tokens")
            return freed_tokens
            
        return 0
        
    def _apply_removal(self, config: Dict[str, Any]) -> int:
        """應用移除策略"""
        min_priority = config["min_priority"]
        freed_tokens = 0
        
        # 移除所有低於最小優先級的窗口
        new_windows = []
        for window in self.context_windows:
            if window.priority < min_priority:
                freed_tokens += window.tokens
                logger.info(f"移除低優先級上下文: {window.source}, 釋放 {window.tokens} tokens")
            else:
                new_windows.append(window)
                
        self.context_windows = new_windows
        self.current_tokens -= freed_tokens
        
        return freed_tokens
        
    def update_priority(self, source: str, new_priority: int):
        """更新特定來源的優先級"""
        for window in self.context_windows:
            if window.source == source:
                window.priority = new_priority
                logger.info(f"更新 {source} 的優先級為 {new_priority}")
                
        # 重新排序
        self.context_windows.sort(key=lambda w: w.priority, reverse=True)
        
    def get_usage_stats(self) -> Dict[str, Any]:
        """獲取使用統計"""
        stats = {
            "current_tokens": self.current_tokens,
            "max_tokens": self.max_tokens,
            "usage_percentage": (self.current_tokens / self.max_tokens) * 100,
            "window_count": len(self.context_windows),
            "priority_distribution": {}
        }
        
        # 統計優先級分佈
        for window in self.context_windows:
            priority_bucket = f"priority_{window.priority}"
            if priority_bucket not in stats["priority_distribution"]:
                stats["priority_distribution"][priority_bucket] = {
                    "count": 0,
                    "tokens": 0
                }
            stats["priority_distribution"][priority_bucket]["count"] += 1
            stats["priority_distribution"][priority_bucket]["tokens"] += window.tokens
            
        return stats
        
    def export_context(self) -> Dict[str, Any]:
        """導出當前上下文（用於調試或持久化）"""
        return {
            "timestamp": time.time(),
            "current_tokens": self.current_tokens,
            "windows": [
                {
                    "source": w.source,
                    "tokens": w.tokens,
                    "priority": w.priority,
                    "timestamp": w.timestamp,
                    "content_preview": w.content[:100] + "..." if len(w.content) > 100 else w.content
                }
                for w in self.context_windows
            ]
        }
        
    def clear_context(self, keep_high_priority: bool = True):
        """清空上下文"""
        if keep_high_priority:
            # 只保留高優先級（>= 8）的窗口
            high_priority_windows = [w for w in self.context_windows if w.priority >= 8]
            self.context_windows = high_priority_windows
            self.current_tokens = sum(w.tokens for w in high_priority_windows)
            logger.info(f"清空上下文，保留 {len(high_priority_windows)} 個高優先級窗口")
        else:
            self.context_windows = []
            self.current_tokens = 0
            logger.info("完全清空上下文")
            
        # 記錄歷史
        self.context_history.append({
            "action": "clear",
            "timestamp": time.time(),
            "keep_high_priority": keep_high_priority
        })
        
    def optimize_for_workflow(self, workflow_type: str):
        """針對特定工作流優化上下文"""
        optimization_rules = {
            "code_generation": {
                "keep_sources": ["requirements", "architecture", "previous_code"],
                "priority_boost": {"requirements": 2, "architecture": 1}
            },
            "ui_design": {
                "keep_sources": ["design_spec", "components", "theme"],
                "priority_boost": {"design_spec": 3, "theme": 2}
            },
            "testing": {
                "keep_sources": ["code", "test_spec", "coverage"],
                "priority_boost": {"code": 2, "test_spec": 2}
            }
        }
        
        if workflow_type in optimization_rules:
            rules = optimization_rules[workflow_type]
            
            # 提升特定來源的優先級
            for source, boost in rules.get("priority_boost", {}).items():
                for window in self.context_windows:
                    if source in window.source:
                        window.priority = min(10, window.priority + boost)
                        
            # 降低其他來源的優先級
            for window in self.context_windows:
                if not any(keep in window.source for keep in rules["keep_sources"]):
                    window.priority = max(0, window.priority - 1)
                    
            # 重新排序
            self.context_windows.sort(key=lambda w: w.priority, reverse=True)
            
            logger.info(f"優化上下文 for {workflow_type} 工作流")