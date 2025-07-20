#!/usr/bin/env python3
"""
Smart Intervention 優化切換處理器
目標: 將切換延遲從 147ms 降低到 100ms 以下
"""

import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import logging

logger = logging.getLogger(__name__)

class SwitchMode(Enum):
    CLAUDE_TO_EDITOR = "claude_to_editor"
    EDITOR_TO_CLAUDE = "editor_to_claude"
    STAY_CURRENT = "stay_current"

@dataclass
class SwitchMetrics:
    """切換性能指標"""
    detection_time: float  # 檢測時間
    decision_time: float   # 決策時間
    execution_time: float  # 執行時間
    total_time: float      # 總時間
    cache_hit: bool        # 緩存命中
    
class OptimizedSwitchHandler:
    """優化的切換處理器"""
    
    def __init__(self):
        # 性能優化配置
        self.target_latency = 100.0  # 目標延遲 100ms
        self.cache_size = 1000
        self.pre_compute_enabled = True
        self.batch_processing = True
        
        # 緩存系統
        self.keyword_cache = {}
        self.decision_cache = {}
        self.precomputed_decisions = {}
        
        # 異步處理
        self.switch_queue = queue.Queue(maxsize=10)
        self.worker_thread = None
        self.is_running = False
        
        # 性能指標
        self.metrics_history = []
        self.last_switch_time = 0
        
        # 預編譯的正則表達式和關鍵詞
        self._precompile_patterns()
        
    def _precompile_patterns(self):
        """預編譯常用模式以提高性能"""
        import re
        
        # 高優先級切換觸發詞 (直接切換，不需複雜分析)
        self.instant_switch_patterns = [
            re.compile(r'(啟動|打開|launch|start)\s*(claudeditor|editor)', re.IGNORECASE),
            re.compile(r'(切換到|switch\s*to)\s*(claudeditor|editor)', re.IGNORECASE),
            re.compile(r'(創建|create)\s*(react|vue|angular)\s*(組件|component)', re.IGNORECASE),
            re.compile(r'(生成|generate)\s*(ui|interface|界面)', re.IGNORECASE),
        ]
        
        # 快速關鍵詞映射 (O(1) 查找)
        self.fast_keywords = {
            # 直接觸發關鍵詞
            'claudeditor': SwitchMode.CLAUDE_TO_EDITOR,
            'editor': SwitchMode.CLAUDE_TO_EDITOR,
            'ce': SwitchMode.CLAUDE_TO_EDITOR,
            '编辑器': SwitchMode.CLAUDE_TO_EDITOR,
            
            # UI/代碼相關
            'react': SwitchMode.CLAUDE_TO_EDITOR,
            'vue': SwitchMode.CLAUDE_TO_EDITOR,
            'component': SwitchMode.CLAUDE_TO_EDITOR,
            '组件': SwitchMode.CLAUDE_TO_EDITOR,
            'ui': SwitchMode.CLAUDE_TO_EDITOR,
            'interface': SwitchMode.CLAUDE_TO_EDITOR,
            '界面': SwitchMode.CLAUDE_TO_EDITOR,
            
            # 開發相關
            'code': SwitchMode.CLAUDE_TO_EDITOR,
            'develop': SwitchMode.CLAUDE_TO_EDITOR,
            'build': SwitchMode.CLAUDE_TO_EDITOR,
            '开发': SwitchMode.CLAUDE_TO_EDITOR,
            '编程': SwitchMode.CLAUDE_TO_EDITOR,
        }
        
    async def analyze_and_switch(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析消息並執行切換 - 主要性能優化入口"""
        start_time = time.perf_counter()
        
        # 階段1: 快速檢測 (目標: <20ms)
        detection_start = time.perf_counter()
        quick_decision = self._quick_detection(message)
        detection_time = (time.perf_counter() - detection_start) * 1000
        
        if quick_decision:
            # 快速路徑: 直接執行切換
            execution_start = time.perf_counter()
            result = await self._execute_switch(quick_decision, context)
            execution_time = (time.perf_counter() - execution_start) * 1000
            
            total_time = (time.perf_counter() - start_time) * 1000
            
            # 記錄指標
            metrics = SwitchMetrics(
                detection_time=detection_time,
                decision_time=0,  # 快速路徑跳過決策階段
                execution_time=execution_time,
                total_time=total_time,
                cache_hit=True
            )
            
            self._record_metrics(metrics)
            
            return {
                'switched': True,
                'mode': quick_decision,
                'latency_ms': total_time,
                'path': 'fast',
                'metrics': metrics
            }
        
        # 階段2: 深度分析 (目標: <30ms)
        decision_start = time.perf_counter()
        decision = await self._deep_analysis(message, context)
        decision_time = (time.perf_counter() - decision_start) * 1000
        
        if decision != SwitchMode.STAY_CURRENT:
            # 執行切換
            execution_start = time.perf_counter()
            result = await self._execute_switch(decision, context)
            execution_time = (time.perf_counter() - execution_start) * 1000
            
            total_time = (time.perf_counter() - start_time) * 1000
            
            metrics = SwitchMetrics(
                detection_time=detection_time,
                decision_time=decision_time,
                execution_time=execution_time,
                total_time=total_time,
                cache_hit=False
            )
            
            self._record_metrics(metrics)
            
            return {
                'switched': True,
                'mode': decision,
                'latency_ms': total_time,
                'path': 'deep',
                'metrics': metrics
            }
        
        # 不需要切換
        total_time = (time.perf_counter() - start_time) * 1000
        return {
            'switched': False,
            'latency_ms': total_time,
            'path': 'no_switch'
        }
    
    def _quick_detection(self, message: str) -> Optional[SwitchMode]:
        """快速檢測 - 使用預編譯模式和緩存"""
        
        # 緩存查找 (O(1))
        if message in self.keyword_cache:
            return self.keyword_cache[message]
        
        message_lower = message.lower()
        
        # 快速關鍵詞查找 (O(1))
        words = message_lower.split()
        for word in words:
            if word in self.fast_keywords:
                decision = self.fast_keywords[word]
                # 緩存結果
                if len(self.keyword_cache) < self.cache_size:
                    self.keyword_cache[message] = decision
                return decision
        
        # 預編譯正則表達式檢查
        for pattern in self.instant_switch_patterns:
            if pattern.search(message):
                decision = SwitchMode.CLAUDE_TO_EDITOR
                # 緩存結果
                if len(self.keyword_cache) < self.cache_size:
                    self.keyword_cache[message] = decision
                return decision
        
        return None
    
    async def _deep_analysis(self, message: str, context: Dict[str, Any]) -> SwitchMode:
        """深度分析 - 異步並發處理"""
        
        # 檢查決策緩存
        cache_key = self._generate_cache_key(message, context)
        if cache_key in self.decision_cache:
            return self.decision_cache[cache_key]
        
        # 並發分析多個維度
        tasks = [
            self._analyze_intent(message),
            self._analyze_complexity(message),
            self._analyze_context_switch_need(context),
        ]
        
        results = await asyncio.gather(*tasks)
        intent_score, complexity_score, context_score = results
        
        # 快速決策算法
        total_score = intent_score + complexity_score + context_score
        
        if total_score > 0.7:
            decision = SwitchMode.CLAUDE_TO_EDITOR
        elif total_score < -0.3:
            decision = SwitchMode.EDITOR_TO_CLAUDE
        else:
            decision = SwitchMode.STAY_CURRENT
        
        # 緩存決策
        if len(self.decision_cache) < self.cache_size:
            self.decision_cache[cache_key] = decision
        
        return decision
    
    async def _analyze_intent(self, message: str) -> float:
        """意圖分析 - 優化版本"""
        
        # 使用預計算的權重
        intent_keywords = {
            # 高權重 - 明確需要編輯器
            '創建': 0.8, 'create': 0.8, '生成': 0.8, 'generate': 0.8,
            '編寫': 0.7, 'write': 0.7, '開發': 0.7, 'develop': 0.7,
            '設計': 0.6, 'design': 0.6, '修改': 0.6, 'modify': 0.6,
            
            # 中權重 - 可能需要編輯器
            '測試': 0.4, 'test': 0.4, '調試': 0.4, 'debug': 0.4,
            '部署': 0.3, 'deploy': 0.3, '運行': 0.3, 'run': 0.3,
            
            # 負權重 - 更適合對話
            '解釋': -0.3, 'explain': -0.3, '什麼': -0.3, 'what': -0.3,
            '為什麼': -0.4, 'why': -0.4, '如何': -0.2, 'how': -0.2,
        }
        
        score = 0.0
        message_lower = message.lower()
        
        for keyword, weight in intent_keywords.items():
            if keyword in message_lower:
                score += weight
        
        return min(max(score, -1.0), 1.0)  # 限制在 [-1, 1] 範圍
    
    async def _analyze_complexity(self, message: str) -> float:
        """複雜度分析 - 簡化版本"""
        
        # 複雜度指標
        complexity_indicators = {
            'react': 0.8, 'vue': 0.8, 'angular': 0.8,
            'javascript': 0.6, 'python': 0.6, 'typescript': 0.6,
            'api': 0.5, 'database': 0.5, 'server': 0.5,
            'component': 0.7, '組件': 0.7,
            'function': 0.4, '函數': 0.4,
        }
        
        score = 0.0
        message_lower = message.lower()
        
        for indicator, weight in complexity_indicators.items():
            if indicator in message_lower:
                score += weight
        
        return min(score, 1.0)
    
    async def _analyze_context_switch_need(self, context: Dict[str, Any]) -> float:
        """上下文切換需求分析"""
        
        current_mode = context.get('current_mode', 'claude')
        last_action = context.get('last_action', '')
        user_preference = context.get('user_preference', 0.5)
        
        # 基於當前模式的切換傾向
        if current_mode == 'claude':
            return 0.2  # 輕微傾向切換到編輯器
        else:
            return -0.2  # 輕微傾向留在編輯器
    
    async def _execute_switch(self, mode: SwitchMode, context: Dict[str, Any]) -> bool:
        """執行切換 - 優化版本"""
        
        try:
            if mode == SwitchMode.CLAUDE_TO_EDITOR:
                # 異步啟動編輯器
                await self._launch_editor_optimized(context)
                return True
            elif mode == SwitchMode.EDITOR_TO_CLAUDE:
                # 異步切換到對話模式
                await self._switch_to_chat_optimized(context)
                return True
            
        except Exception as e:
            logger.error(f"切換執行失敗: {e}")
            return False
        
        return False
    
    async def _launch_editor_optimized(self, context: Dict[str, Any]):
        """優化的編輯器啟動"""
        
        # 並發執行多個啟動任務
        tasks = [
            self._preload_editor_assets(),
            self._setup_editor_context(context),
            self._notify_switch_event('claude_to_editor')
        ]
        
        await asyncio.gather(*tasks)
    
    async def _switch_to_chat_optimized(self, context: Dict[str, Any]):
        """優化的聊天模式切換"""
        
        tasks = [
            self._prepare_chat_context(context),
            self._notify_switch_event('editor_to_claude')
        ]
        
        await asyncio.gather(*tasks)
    
    async def _preload_editor_assets(self):
        """預載入編輯器資源"""
        # 模擬預載入 - 在實際實現中會載入真實資源
        await asyncio.sleep(0.01)  # 10ms 模擬載入時間
    
    async def _setup_editor_context(self, context: Dict[str, Any]):
        """設置編輯器上下文"""
        await asyncio.sleep(0.005)  # 5ms 模擬設置時間
    
    async def _prepare_chat_context(self, context: Dict[str, Any]):
        """準備聊天上下文"""
        await asyncio.sleep(0.005)  # 5ms 模擬準備時間
    
    async def _notify_switch_event(self, event_type: str):
        """通知切換事件"""
        # 異步事件通知
        await asyncio.sleep(0.001)  # 1ms 模擬通知時間
    
    def _generate_cache_key(self, message: str, context: Dict[str, Any]) -> str:
        """生成緩存鍵"""
        return f"{hash(message)}_{context.get('current_mode', 'claude')}"
    
    def _record_metrics(self, metrics: SwitchMetrics):
        """記錄性能指標"""
        self.metrics_history.append(metrics)
        
        # 保持最近 100 次記錄
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        # 記錄日誌
        if metrics.total_time > self.target_latency:
            logger.warning(
                f"切換延遲超標: {metrics.total_time:.1f}ms > {self.target_latency}ms"
            )
        else:
            logger.info(
                f"切換成功: {metrics.total_time:.1f}ms (目標: {self.target_latency}ms)"
            )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """獲取性能報告"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        recent_metrics = self.metrics_history[-20:]  # 最近20次
        
        avg_total = sum(m.total_time for m in recent_metrics) / len(recent_metrics)
        avg_detection = sum(m.detection_time for m in recent_metrics) / len(recent_metrics)
        avg_decision = sum(m.decision_time for m in recent_metrics) / len(recent_metrics)
        avg_execution = sum(m.execution_time for m in recent_metrics) / len(recent_metrics)
        
        cache_hit_rate = sum(1 for m in recent_metrics if m.cache_hit) / len(recent_metrics)
        
        under_target_rate = sum(1 for m in recent_metrics if m.total_time <= self.target_latency) / len(recent_metrics)
        
        return {
            "average_latency_ms": round(avg_total, 1),
            "target_latency_ms": self.target_latency,
            "under_target_rate": round(under_target_rate * 100, 1),
            "cache_hit_rate": round(cache_hit_rate * 100, 1),
            "breakdown": {
                "detection_ms": round(avg_detection, 1),
                "decision_ms": round(avg_decision, 1),
                "execution_ms": round(avg_execution, 1)
            },
            "status": "excellent" if avg_total <= self.target_latency else "needs_optimization",
            "sample_size": len(recent_metrics)
        }
    
    def clear_cache(self):
        """清理緩存"""
        self.keyword_cache.clear()
        self.decision_cache.clear()
        logger.info("緩存已清理")

# 創建全局優化處理器實例
optimized_handler = OptimizedSwitchHandler()

# 性能測試函數
async def performance_test():
    """性能測試"""
    
    test_messages = [
        "創建一個React組件",
        "生成用戶界面",
        "啟動ClaudeEditor",
        "寫一個Python函數",
        "設計登錄頁面",
        "什麼是React?",  # 不應該切換
        "解釋這段代碼",   # 不應該切換
        "ce",  # 快捷指令
        "開發Web應用",
        "測試API接口"
    ]
    
    context = {
        'current_mode': 'claude',
        'user_preference': 0.5
    }
    
    print("🚀 Smart Intervention 性能測試")
    print("=" * 50)
    
    results = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n測試 {i}: {message}")
        
        result = await optimized_handler.analyze_and_switch(message, context)
        results.append(result)
        
        print(f"  切換: {'是' if result['switched'] else '否'}")
        print(f"  延遲: {result['latency_ms']:.1f}ms")
        print(f"  路徑: {result.get('path', 'unknown')}")
        
        if result['latency_ms'] <= 100:
            print(f"  ✅ 達標 (≤100ms)")
        else:
            print(f"  ❌ 超標 (>100ms)")
    
    # 總體報告
    print(f"\n📊 測試總結")
    print("=" * 30)
    
    avg_latency = sum(r['latency_ms'] for r in results) / len(results)
    under_target = sum(1 for r in results if r['latency_ms'] <= 100)
    
    print(f"平均延遲: {avg_latency:.1f}ms")
    print(f"達標率: {under_target}/{len(results)} ({under_target/len(results)*100:.1f}%)")
    
    # 詳細性能報告
    report = optimized_handler.get_performance_report()
    print(f"\n詳細報告: {report}")

if __name__ == "__main__":
    asyncio.run(performance_test())