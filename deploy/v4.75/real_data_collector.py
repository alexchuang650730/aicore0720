#!/usr/bin/env python3
"""
PowerAutomation v4.75 - 真實數據收集器
接入真實的 MCP 性能數據和 ClaudeEditor UI 指標
"""

import asyncio
import json
import logging
import psutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import websocket
import threading
import queue
import requests
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RealTimeMetric:
    """實時指標"""
    name: str
    value: float
    timestamp: float
    source: str
    unit: str

class RealDataCollector:
    """真實數據收集器"""
    
    def __init__(self):
        self.root_path = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        self.metrics_queue = queue.Queue()
        self.websocket_clients = {}
        self.collection_threads = []
        self.is_running = False
        
        # MCP 服務端點
        self.mcp_endpoints = {
            "smart_intervention": "http://localhost:8761",
            "codeflow_mcp": "http://localhost:8762", 
            "smartui_mcp": "http://localhost:8763",
            "memoryrag_mcp": "http://localhost:8764",
            "smarttool_mcp": "http://localhost:8765",
            "test_mcp": "http://localhost:8766",
            "claude_router_mcp": "http://localhost:8767",
            "command_mcp": "http://localhost:8768",
            "local_adapter_mcp": "http://localhost:8769",
            "mcp_coordinator_mcp": "http://localhost:8770",
            "docs_mcp": "http://localhost:8771"
        }
        
        # ClaudeEditor 指標端點
        self.claudeditor_endpoints = {
            "performance": "http://localhost:8000/api/metrics/performance",
            "ui_interaction": "http://localhost:8000/api/metrics/ui",
            "user_behavior": "http://localhost:8000/api/metrics/behavior",
            "system_resources": "http://localhost:8000/api/metrics/system"
        }
        
        # 實時指標緩存
        self.real_metrics = {
            "mcp_technical": {},
            "ui_experience": {},
            "system_performance": {},
            "user_interaction": {}
        }
    
    async def start_collection(self):
        """啟動數據收集"""
        self.is_running = True
        logger.info("🚀 啟動真實數據收集...")
        
        # 1. 啟動 MCP 性能數據收集
        await self._start_mcp_collection()
        
        # 2. 啟動 ClaudeEditor UI 指標收集
        await self._start_ui_metrics_collection()
        
        # 3. 啟動系統性能監控
        await self._start_system_monitoring()
        
        # 4. 啟動 WebSocket 監聽
        await self._start_websocket_listeners()
        
        logger.info("✅ 真實數據收集已啟動")
    
    async def _start_mcp_collection(self):
        """啟動 MCP 性能數據收集"""
        logger.info("📊 啟動 MCP 性能數據收集...")
        
        async def collect_mcp_metrics():
            while self.is_running:
                try:
                    for mcp_name, endpoint in self.mcp_endpoints.items():
                        try:
                            # 嘗試連接 MCP 健康檢查端點
                            health_url = f"{endpoint}/health"
                            start_time = time.time()
                            
                            response = requests.get(health_url, timeout=2)
                            response_time = (time.time() - start_time) * 1000  # ms
                            
                            if response.status_code == 200:
                                health_data = response.json()
                                
                                # 收集真實指標
                                metrics = {
                                    "response_time_ms": response_time,
                                    "success_rate": health_data.get("success_rate", 99.0),
                                    "memory_usage_mb": health_data.get("memory_usage", 0),
                                    "cpu_usage_percent": health_data.get("cpu_usage", 0),
                                    "requests_per_minute": health_data.get("requests_per_minute", 0),
                                    "error_rate": health_data.get("error_rate", 0),
                                    "availability": 100.0,
                                    "health_score": health_data.get("health_score", 95.0),
                                    "active_connections": health_data.get("active_connections", 0),
                                    "queue_size": health_data.get("queue_size", 0)
                                }
                                
                                self.real_metrics["mcp_technical"][mcp_name] = {
                                    **metrics,
                                    "timestamp": time.time(),
                                    "status": "healthy"
                                }
                                
                                # 添加到實時指標隊列
                                metric = RealTimeMetric(
                                    name=f"{mcp_name}_response_time",
                                    value=response_time,
                                    timestamp=time.time(),
                                    source=mcp_name,
                                    unit="ms"
                                )
                                self.metrics_queue.put(metric)
                                
                            else:
                                # MCP 服務不健康
                                self.real_metrics["mcp_technical"][mcp_name] = {
                                    "response_time_ms": 999999,
                                    "success_rate": 0,
                                    "availability": 0,
                                    "health_score": 0,
                                    "timestamp": time.time(),
                                    "status": "unhealthy",
                                    "error": f"HTTP {response.status_code}"
                                }
                                
                        except requests.exceptions.RequestException as e:
                            # MCP 服務離線
                            self.real_metrics["mcp_technical"][mcp_name] = {
                                "response_time_ms": 999999,
                                "success_rate": 0,
                                "availability": 0,
                                "health_score": 0,
                                "timestamp": time.time(),
                                "status": "offline",
                                "error": str(e)
                            }
                        
                        # 避免過於頻繁的請求
                        await asyncio.sleep(0.1)
                    
                    # 每5秒收集一次
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.error(f"MCP 指標收集錯誤: {e}")
                    await asyncio.sleep(5)
        
        # 啟動收集任務
        asyncio.create_task(collect_mcp_metrics())
    
    async def _start_ui_metrics_collection(self):
        """啟動 ClaudeEditor UI 指標收集"""
        logger.info("🎨 啟動 ClaudeEditor UI 指標收集...")
        
        async def collect_ui_metrics():
            while self.is_running:
                try:
                    for metric_type, endpoint in self.claudeditor_endpoints.items():
                        try:
                            response = requests.get(endpoint, timeout=3)
                            if response.status_code == 200:
                                ui_data = response.json()
                                
                                if metric_type == "performance":
                                    self.real_metrics["ui_experience"]["performance"] = {
                                        "render_time_ms": ui_data.get("render_time", 50),
                                        "frame_rate": ui_data.get("frame_rate", 60),
                                        "memory_usage": ui_data.get("memory_usage", 100),
                                        "dom_nodes": ui_data.get("dom_nodes", 1000),
                                        "timestamp": time.time()
                                    }
                                
                                elif metric_type == "ui_interaction":
                                    self.real_metrics["ui_experience"]["interaction"] = {
                                        "click_response_time": ui_data.get("click_response_time", 16),
                                        "scroll_smoothness": ui_data.get("scroll_smoothness", 95),
                                        "input_lag": ui_data.get("input_lag", 10),
                                        "animation_fps": ui_data.get("animation_fps", 60),
                                        "timestamp": time.time()
                                    }
                                
                                elif metric_type == "user_behavior":
                                    self.real_metrics["ui_experience"]["behavior"] = {
                                        "session_duration": ui_data.get("session_duration", 1800),
                                        "feature_usage": ui_data.get("feature_usage", {}),
                                        "error_encounters": ui_data.get("error_encounters", 0),
                                        "satisfaction_score": ui_data.get("satisfaction_score", 85),
                                        "timestamp": time.time()
                                    }
                        
                        except requests.exceptions.RequestException:
                            # ClaudeEditor 離線，使用系統監控數據
                            await self._fallback_ui_metrics()
                    
                    await asyncio.sleep(2)  # 每2秒收集一次
                    
                except Exception as e:
                    logger.error(f"UI 指標收集錯誤: {e}")
                    await asyncio.sleep(5)
        
        asyncio.create_task(collect_ui_metrics())
    
    async def _fallback_ui_metrics(self):
        """回退UI指標收集（當ClaudeEditor離線時）"""
        try:
            # 使用系統進程監控推斷UI性能
            claude_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    if any(name in proc.info['name'].lower() for name in ['claude', 'electron', 'chrome']):
                        claude_processes.append(proc.info)
                except:
                    continue
            
            if claude_processes:
                # 基於進程數據推斷UI性能
                total_memory = sum(p['memory_info'].rss for p in claude_processes) / 1024 / 1024  # MB
                avg_cpu = sum(p['cpu_percent'] or 0 for p in claude_processes) / len(claude_processes)
                
                self.real_metrics["ui_experience"]["performance"] = {
                    "render_time_ms": min(100, avg_cpu * 2),  # CPU使用率映射到渲染時間
                    "memory_usage": total_memory,
                    "estimated": True,
                    "timestamp": time.time()
                }
        
        except Exception as e:
            logger.warning(f"回退UI指標收集失敗: {e}")
    
    async def _start_system_monitoring(self):
        """啟動系統性能監控"""
        logger.info("💻 啟動系統性能監控...")
        
        async def monitor_system():
            while self.is_running:
                try:
                    # CPU 和內存
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    # 網絡 I/O
                    net_io = psutil.net_io_counters()
                    
                    # GPU (如果有 nvidia-smi)
                    gpu_usage = await self._get_gpu_usage()
                    
                    self.real_metrics["system_performance"] = {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used_gb": memory.used / 1024**3,
                        "disk_percent": disk.percent,
                        "disk_used_gb": disk.used / 1024**3,
                        "network_bytes_sent": net_io.bytes_sent,
                        "network_bytes_recv": net_io.bytes_recv,
                        "gpu_usage": gpu_usage,
                        "timestamp": time.time()
                    }
                    
                    # 添加關鍵指標到隊列
                    for metric_name, value in [
                        ("cpu_usage", cpu_percent),
                        ("memory_usage", memory.percent),
                        ("disk_usage", disk.percent)
                    ]:
                        metric = RealTimeMetric(
                            name=metric_name,
                            value=value,
                            timestamp=time.time(),
                            source="system",
                            unit="%"
                        )
                        self.metrics_queue.put(metric)
                    
                    await asyncio.sleep(3)  # 每3秒監控一次
                    
                except Exception as e:
                    logger.error(f"系統監控錯誤: {e}")
                    await asyncio.sleep(5)
        
        asyncio.create_task(monitor_system())
    
    async def _get_gpu_usage(self) -> float:
        """獲取GPU使用率"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return 0.0
    
    async def _start_websocket_listeners(self):
        """啟動 WebSocket 監聽器"""
        logger.info("🔌 啟動 WebSocket 監聽器...")
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if data.get('type') == 'metrics':
                    # 處理實時指標推送
                    self._process_websocket_metrics(data)
            except Exception as e:
                logger.error(f"WebSocket 消息處理錯誤: {e}")
        
        def on_error(ws, error):
            logger.warning(f"WebSocket 錯誤: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logger.info("WebSocket 連接關閉")
        
        # 嘗試連接 ClaudeEditor WebSocket
        try:
            ws = websocket.WebSocketApp(
                "ws://localhost:8000/ws/metrics",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            def run_websocket():
                ws.run_forever()
            
            thread = threading.Thread(target=run_websocket, daemon=True)
            thread.start()
            self.collection_threads.append(thread)
            
        except Exception as e:
            logger.warning(f"WebSocket 連接失敗: {e}")
    
    def _process_websocket_metrics(self, data):
        """處理 WebSocket 指標數據"""
        try:
            metrics = data.get('metrics', {})
            source = data.get('source', 'websocket')
            
            for metric_name, value in metrics.items():
                metric = RealTimeMetric(
                    name=metric_name,
                    value=float(value),
                    timestamp=time.time(),
                    source=source,
                    unit=data.get('units', {}).get(metric_name, '')
                )
                self.metrics_queue.put(metric)
                
        except Exception as e:
            logger.error(f"WebSocket 指標處理錯誤: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """獲取當前所有指標"""
        return {
            "timestamp": datetime.now().isoformat(),
            "mcp_technical": self.real_metrics["mcp_technical"],
            "ui_experience": self.real_metrics["ui_experience"], 
            "system_performance": self.real_metrics["system_performance"],
            "collection_status": {
                "is_running": self.is_running,
                "queue_size": self.metrics_queue.qsize(),
                "active_threads": len([t for t in self.collection_threads if t.is_alive()])
            }
        }
    
    def get_metrics_stream(self) -> List[RealTimeMetric]:
        """獲取實時指標流"""
        metrics = []
        while not self.metrics_queue.empty():
            try:
                metrics.append(self.metrics_queue.get_nowait())
            except queue.Empty:
                break
        return metrics
    
    async def stop_collection(self):
        """停止數據收集"""
        logger.info("🛑 停止真實數據收集...")
        self.is_running = False
        
        # 等待線程結束
        for thread in self.collection_threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        logger.info("✅ 真實數據收集已停止")


# 全局數據收集器實例
real_data_collector = RealDataCollector()

async def start_real_data_collection():
    """啟動真實數據收集"""
    await real_data_collector.start_collection()

def get_real_metrics() -> Dict[str, Any]:
    """獲取真實指標數據"""
    return real_data_collector.get_current_metrics()

def get_real_time_stream() -> List[RealTimeMetric]:
    """獲取實時指標流"""
    return real_data_collector.get_metrics_stream()


# 測試函數
async def test_real_data_collection():
    """測試真實數據收集"""
    print("🧪 測試真實數據收集器")
    print("=" * 50)
    
    collector = RealDataCollector()
    
    print("📡 啟動數據收集...")
    await collector.start_collection()
    
    # 等待幾秒收集數據
    await asyncio.sleep(10)
    
    print("\n📊 當前指標:")
    metrics = collector.get_current_metrics()
    
    print(f"MCP 服務狀態:")
    for mcp, data in metrics["mcp_technical"].items():
        status = data.get("status", "unknown")
        response_time = data.get("response_time_ms", 0)
        print(f"  - {mcp}: {status} ({response_time:.1f}ms)")
    
    print(f"\n系統性能:")
    sys_perf = metrics["system_performance"]
    print(f"  - CPU: {sys_perf.get('cpu_percent', 0):.1f}%")
    print(f"  - 內存: {sys_perf.get('memory_percent', 0):.1f}%")
    print(f"  - 磁盤: {sys_perf.get('disk_percent', 0):.1f}%")
    
    print(f"\n實時指標流:")
    stream = collector.get_metrics_stream()
    for metric in stream[-5:]:  # 顯示最近5個
        print(f"  - {metric.name}: {metric.value:.2f} {metric.unit} ({metric.source})")
    
    await collector.stop_collection()
    print("\n✅ 測試完成")


if __name__ == "__main__":
    asyncio.run(test_real_data_collection())