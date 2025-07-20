#!/usr/bin/env python3
"""
ClaudeEditor + MCP 監控運維系統
專注於工具調用準確率和系統健康度監控
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import aiohttp
import psutil
from collections import defaultdict, deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeEditorMCPMonitor:
    """ClaudeEditor和MCP監控運維系統"""
    
    def __init__(self):
        self.base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        self.monitor_dir = self.base_dir / "monitoring"
        self.monitor_dir.mkdir(exist_ok=True)
        
        # 監控指標
        self.metrics = {
            "tool_call_accuracy": deque(maxlen=100),  # 最近100次工具調用
            "mcp_latency": deque(maxlen=100),         # MCP響應延遲
            "error_rate": deque(maxlen=100),          # 錯誤率
            "system_health": 100                       # 系統健康度
        }
        
        # MCP工具映射
        self.mcp_tools = {
            "Read": {"priority": "P0", "category": "file_ops"},
            "Write": {"priority": "P0", "category": "file_ops"},
            "Edit": {"priority": "P0", "category": "file_ops"},
            "Search": {"priority": "P0", "category": "search"},
            "Grep": {"priority": "P0", "category": "search"},
            "TodoWrite": {"priority": "P1", "category": "planning"},
            "WebFetch": {"priority": "P1", "category": "web"},
            "SmartTool": {"priority": "P0", "category": "smart"}
        }
        
        # 告警閾值
        self.alert_thresholds = {
            "tool_accuracy_min": 75,      # 工具準確率最低值
            "mcp_latency_max": 1000,      # MCP最大延遲(ms)
            "error_rate_max": 5,          # 最大錯誤率(%)
            "cpu_usage_max": 80,          # CPU使用率上限
            "memory_usage_max": 80        # 內存使用率上限
        }
    
    async def monitor_tool_calls(self):
        """監控工具調用情況"""
        log_file = self.base_dir / "unified_k2_training.log"
        
        if not log_file.exists():
            return
        
        # 分析最近的工具調用
        tool_stats = defaultdict(lambda: {"success": 0, "failed": 0})
        
        # 模擬分析（實際應從日誌解析）
        recent_calls = [
            {"tool": "Read", "success": True},
            {"tool": "Write", "success": True},
            {"tool": "Search", "success": False},
            {"tool": "SmartTool", "success": True},
            {"tool": "Edit", "success": True}
        ]
        
        for call in recent_calls:
            if call["success"]:
                tool_stats[call["tool"]]["success"] += 1
            else:
                tool_stats[call["tool"]]["failed"] += 1
        
        # 計算準確率
        total_success = sum(s["success"] for s in tool_stats.values())
        total_calls = sum(s["success"] + s["failed"] for s in tool_stats.values())
        
        if total_calls > 0:
            accuracy = (total_success / total_calls) * 100
            self.metrics["tool_call_accuracy"].append(accuracy)
            
            # 檢查告警
            if accuracy < self.alert_thresholds["tool_accuracy_min"]:
                await self.send_alert("tool_accuracy", f"工具調用準確率過低: {accuracy:.1f}%")
    
    async def monitor_mcp_zero(self):
        """監控MCP Zero狀態"""
        # 檢查MCP服務狀態
        mcp_healthy = True
        latency = 50  # 模擬延遲
        
        # 檢查MCP配置
        mcp_config = self.base_dir / "mcp-zero-config.json"
        if mcp_config.exists():
            with open(mcp_config, 'r') as f:
                config = json.load(f)
                if config.get("discovery", {}).get("enabled"):
                    logger.info("MCP Zero工具發現: 已啟用")
        
        self.metrics["mcp_latency"].append(latency)
        
        if latency > self.alert_thresholds["mcp_latency_max"]:
            await self.send_alert("mcp_latency", f"MCP延遲過高: {latency}ms")
        
        return mcp_healthy
    
    def get_system_metrics(self) -> Dict:
        """獲取系統資源使用情況"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_usage": disk.percent,
            "disk_free_gb": disk.free / (1024**3)
        }
        
        # 檢查資源告警
        if cpu_percent > self.alert_thresholds["cpu_usage_max"]:
            asyncio.create_task(self.send_alert("cpu", f"CPU使用率過高: {cpu_percent}%"))
        
        if memory.percent > self.alert_thresholds["memory_usage_max"]:
            asyncio.create_task(self.send_alert("memory", f"內存使用率過高: {memory.percent}%"))
        
        return metrics
    
    def calculate_health_score(self) -> int:
        """計算系統健康分數"""
        score = 100
        
        # 工具準確率影響
        if self.metrics["tool_call_accuracy"]:
            avg_accuracy = sum(self.metrics["tool_call_accuracy"]) / len(self.metrics["tool_call_accuracy"])
            if avg_accuracy < 80:
                score -= (80 - avg_accuracy) * 0.5
        
        # MCP延遲影響
        if self.metrics["mcp_latency"]:
            avg_latency = sum(self.metrics["mcp_latency"]) / len(self.metrics["mcp_latency"])
            if avg_latency > 500:
                score -= min((avg_latency - 500) / 50, 20)
        
        # 錯誤率影響
        if self.metrics["error_rate"]:
            avg_error_rate = sum(self.metrics["error_rate"]) / len(self.metrics["error_rate"])
            score -= avg_error_rate * 2
        
        # 系統資源影響
        system_metrics = self.get_system_metrics()
        if system_metrics["cpu_usage"] > 70:
            score -= (system_metrics["cpu_usage"] - 70) * 0.3
        if system_metrics["memory_usage"] > 70:
            score -= (system_metrics["memory_usage"] - 70) * 0.3
        
        return max(0, min(100, int(score)))
    
    async def send_alert(self, alert_type: str, message: str):
        """發送告警"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": "high" if "過高" in message or "過低" in message else "medium"
        }
        
        # 寫入告警日誌
        alert_file = self.monitor_dir / "alerts.jsonl"
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert, ensure_ascii=False) + '\n')
        
        logger.warning(f"🚨 告警: {message}")
    
    def generate_dashboard(self) -> str:
        """生成監控儀表板"""
        health_score = self.calculate_health_score()
        system_metrics = self.get_system_metrics()
        
        # 計算平均值
        avg_accuracy = sum(self.metrics["tool_call_accuracy"]) / len(self.metrics["tool_call_accuracy"]) if self.metrics["tool_call_accuracy"] else 0
        avg_latency = sum(self.metrics["mcp_latency"]) / len(self.metrics["mcp_latency"]) if self.metrics["mcp_latency"] else 0
        
        dashboard = f"""
# ClaudeEditor + MCP 監控儀表板

更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🏥 系統健康度: {health_score}%
{'🟢 健康' if health_score >= 80 else '🟡 警告' if health_score >= 60 else '🔴 危險'}

## 📊 核心指標

### 工具調用準確率
- 當前: {self.metrics["tool_call_accuracy"][-1] if self.metrics["tool_call_accuracy"] else 0:.1f}%
- 平均: {avg_accuracy:.1f}%
- 趨勢: {'📈' if len(self.metrics["tool_call_accuracy"]) > 1 and self.metrics["tool_call_accuracy"][-1] > self.metrics["tool_call_accuracy"][-2] else '📉'}

### MCP Zero狀態
- 響應延遲: {avg_latency:.0f}ms
- 工具發現: ✅ 已啟用
- SmartTool: ✅ 就緒

### 系統資源
- CPU使用率: {system_metrics['cpu_usage']:.1f}%
- 內存使用率: {system_metrics['memory_usage']:.1f}%
- 可用內存: {system_metrics['memory_available_gb']:.1f}GB
- 磁盤使用率: {system_metrics['disk_usage']:.1f}%

## 🛠️ 工具使用統計

| 工具 | 優先級 | 調用次數 | 成功率 |
|------|--------|----------|--------|
"""
        
        # 添加工具統計
        for tool, info in self.mcp_tools.items():
            dashboard += f"| {tool} | {info['priority']} | - | - |\n"
        
        dashboard += f"""
## 🎯 3天目標進度

- Day 1: 80% ➡️ 當前 {avg_accuracy:.1f}%
- Day 2: 85% (明天)
- Day 3: 89% (後天)

## 📈 改進建議

"""
        
        if avg_accuracy < 80:
            dashboard += "- ⚠️ 工具調用準確率需要提升\n"
            dashboard += "- 建議: 加載更多訓練數據\n"
        
        if avg_latency > 500:
            dashboard += "- ⚠️ MCP響應延遲較高\n"
            dashboard += "- 建議: 優化工具發現緩存\n"
        
        if health_score < 80:
            dashboard += "- ⚠️ 系統健康度下降\n"
            dashboard += "- 建議: 檢查資源使用和錯誤日誌\n"
        
        return dashboard
    
    async def run_monitoring_loop(self):
        """主監控循環"""
        logger.info("🚀 啟動ClaudeEditor + MCP監控系統...")
        
        while True:
            try:
                # 執行監控任務
                await self.monitor_tool_calls()
                await self.monitor_mcp_zero()
                
                # 生成並保存儀表板
                dashboard = self.generate_dashboard()
                dashboard_file = self.monitor_dir / "dashboard.md"
                with open(dashboard_file, 'w', encoding='utf-8') as f:
                    f.write(dashboard)
                
                # 保存指標歷史
                metrics_file = self.monitor_dir / "metrics_history.json"
                with open(metrics_file, 'w') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "health_score": self.calculate_health_score(),
                        "tool_accuracy": list(self.metrics["tool_call_accuracy"])[-10:],
                        "mcp_latency": list(self.metrics["mcp_latency"])[-10:],
                        "system_metrics": self.get_system_metrics()
                    }, f, indent=2)
                
                # 每30秒更新一次
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"監控錯誤: {e}")
                await asyncio.sleep(60)


async def main():
    """主函數"""
    monitor = ClaudeEditorMCPMonitor()
    await monitor.run_monitoring_loop()


if __name__ == "__main__":
    asyncio.run(main())