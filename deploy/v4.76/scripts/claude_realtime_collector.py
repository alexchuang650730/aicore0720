#!/usr/bin/env python3
"""
Claude 實時信息收集器
參考claude router mcp的startup_trigger機制，實現一鍵部署後自動收集Claude對話
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import subprocess
import signal
import sys

# 可選依賴處理
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CollectorStatus(Enum):
    """收集器狀態"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    COLLECTING = "collecting"
    ERROR = "error"

@dataclass
class ClaudeSession:
    """Claude 會話記錄"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    messages: List[Dict[str, Any]] = None
    tool_calls: List[Dict[str, Any]] = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    project_context: str = ""
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        if self.tool_calls is None:
            self.tool_calls = []

class ClaudeRealtimeCollector:
    """Claude 實時信息收集器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or self._get_default_config()
        
        # 狀態管理
        self.status = CollectorStatus.STOPPED
        self.running = False
        self.start_time = None
        
        # 數據存儲
        self.data_dir = Path(self.config.get("data_dir", "./data/claude_realtime"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 會話管理
        self.active_sessions = {}
        self.completed_sessions = []
        self.max_sessions = 1000
        
        # 收集統計
        self.stats = {
            "total_sessions": 0,
            "total_messages": 0,
            "total_tool_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "start_time": None,
            "uptime": 0
        }
        
        # 任務管理
        self.monitor_task = None
        self.collector_task = None
        self.heartbeat_task = None
        
        # 進程監控
        self.claude_processes = []
        self.monitored_commands = [
            "claude",
            "claude-code", 
            "claudeditor",
            "manus"
        ]
        
        # 回調函數
        self.session_callbacks = []
        self.message_callbacks = []
        
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "data_dir": "./data/claude_realtime",
            "auto_start": True,
            "monitor_interval": 1.0,
            "heartbeat_interval": 30,
            "max_sessions": 1000,
            "enable_websocket": True,
            "websocket_port": 8765,
            "collect_system_info": True,
            "save_interval": 60,
            "compress_old_data": True,
            "retention_days": 30
        }
    
    async def initialize(self) -> bool:
        """初始化收集器"""
        try:
            self.logger.info("🚀 初始化 Claude 實時信息收集器...")
            
            # 設置信號處理器
            self._setup_signal_handlers()
            
            # 啟動收集服務
            await self.start_collection()
            
            # 啟動 WebSocket 服務器（如果啟用）
            if self.config.get("enable_websocket", True):
                await self.start_websocket_server()
            
            self.logger.info("✅ Claude 實時收集器初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 收集器初始化失敗: {e}")
            return False
    
    def _setup_signal_handlers(self):
        """設置信號處理器"""
        def signal_handler(signum, frame):
            self.logger.info(f"📡 收到信號 {signum}，正在優雅關閉...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start_collection(self):
        """啟動數據收集"""
        if self.running:
            return
        
        self.running = True
        self.status = CollectorStatus.STARTING
        self.start_time = time.time()
        self.stats["start_time"] = datetime.now().isoformat()
        
        # 啟動監控任務
        self.monitor_task = asyncio.create_task(self._process_monitor())
        self.collector_task = asyncio.create_task(self._data_collector())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        
        self.status = CollectorStatus.RUNNING
        self.logger.info("🎯 Claude 實時數據收集已啟動")
    
    async def _process_monitor(self):
        """進程監控器"""
        while self.running:
            try:
                if PSUTIL_AVAILABLE:
                    await self._monitor_claude_processes()
                else:
                    await self._monitor_claude_processes_fallback()
                
                await asyncio.sleep(self.config.get("monitor_interval", 1.0))
                
            except Exception as e:
                self.logger.error(f"進程監控錯誤: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_claude_processes(self):
        """監控 Claude 相關進程（psutil版本）"""
        current_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                proc_info = proc.info
                cmd_line = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                
                # 檢查是否是 Claude 相關進程
                if any(cmd in cmd_line.lower() for cmd in self.monitored_commands):
                    current_processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cmdline': cmd_line,
                        'create_time': proc_info['create_time'],
                        'detected_at': time.time()
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 檢測新進程
        for proc in current_processes:
            if proc['pid'] not in [p['pid'] for p in self.claude_processes]:
                await self._on_claude_process_started(proc)
        
        # 檢測結束的進程
        active_pids = [p['pid'] for p in current_processes]
        for proc in self.claude_processes[:]:
            if proc['pid'] not in active_pids:
                await self._on_claude_process_ended(proc)
                self.claude_processes.remove(proc)
        
        # 更新進程列表
        self.claude_processes = current_processes
    
    async def _monitor_claude_processes_fallback(self):
        """監控 Claude 相關進程（回退版本）"""
        try:
            # 使用 ps 命令檢查進程
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            current_processes = []
            for line in result.stdout.split('\n'):
                if any(cmd in line.lower() for cmd in self.monitored_commands):
                    parts = line.split()
                    if len(parts) >= 11:
                        current_processes.append({
                            'pid': int(parts[1]),
                            'name': parts[10],
                            'cmdline': ' '.join(parts[10:]),
                            'create_time': time.time(),
                            'detected_at': time.time()
                        })
            
            # 簡單的新進程檢測
            for proc in current_processes:
                if proc['pid'] not in [p['pid'] for p in self.claude_processes]:
                    await self._on_claude_process_started(proc)
            
            self.claude_processes = current_processes
            
        except Exception as e:
            self.logger.warning(f"回退進程監控失敗: {e}")
    
    async def _on_claude_process_started(self, proc_info: Dict[str, Any]):
        """Claude 進程啟動事件"""
        self.logger.info(f"🔍 檢測到 Claude 進程: {proc_info['name']} (PID: {proc_info['pid']})")
        
        # 創建新會話
        session_id = str(uuid.uuid4())
        session = ClaudeSession(
            session_id=session_id,
            start_time=time.time(),
            project_context=self._detect_project_context(proc_info)
        )
        
        self.active_sessions[session_id] = session
        self.stats["total_sessions"] += 1
        
        # 開始收集這個會話的數據
        asyncio.create_task(self._collect_session_data(session_id, proc_info))
        
        # 觸發回調
        for callback in self.session_callbacks:
            try:
                await callback('session_started', session)
            except Exception as e:
                self.logger.error(f"會話回調錯誤: {e}")
    
    async def _on_claude_process_ended(self, proc_info: Dict[str, Any]):
        """Claude 進程結束事件"""
        self.logger.info(f"📝 Claude 進程結束: {proc_info['name']} (PID: {proc_info['pid']})")
        
        # 結束相關會話
        for session_id, session in list(self.active_sessions.items()):
            if session.end_time is None:
                session.end_time = time.time()
                await self._finalize_session(session_id, session)
    
    def _detect_project_context(self, proc_info: Dict[str, Any]) -> str:
        """檢測項目上下文"""
        cmdline = proc_info.get('cmdline', '')
        
        # 嘗試從命令行參數檢測項目路徑
        if 'claude' in cmdline:
            parts = cmdline.split()
            for i, part in enumerate(parts):
                if part.startswith('/') and 'project' in part.lower():
                    return part
                if part.endswith('.py') or part.endswith('.js'):
                    return os.path.dirname(part)
        
        # 檢測當前工作目錄
        try:
            cwd = os.getcwd()
            return cwd
        except:
            pass
        
        return "unknown"
    
    async def _collect_session_data(self, session_id: str, proc_info: Dict[str, Any]):
        """收集會話數據"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        self.status = CollectorStatus.COLLECTING
        
        try:
            # 監控文件系統變化
            await self._monitor_file_changes(session)
            
            # 監控網絡活動（如果可能）
            await self._monitor_network_activity(session)
            
            # 收集系統信息
            if self.config.get("collect_system_info", True):
                await self._collect_system_info(session)
            
        except Exception as e:
            self.logger.error(f"收集會話數據失敗: {e}")
        
        self.status = CollectorStatus.RUNNING
    
    async def _monitor_file_changes(self, session: ClaudeSession):
        """監控文件變化"""
        # 這裡可以實現文件監控邏輯
        # 使用 watchdog 或其他文件監控工具
        pass
    
    async def _monitor_network_activity(self, session: ClaudeSession):
        """監控網絡活動"""
        # 這裡可以實現網絡監控邏輯
        # 監控 Claude API 調用
        pass
    
    async def _collect_system_info(self, session: ClaudeSession):
        """收集系統信息"""
        try:
            system_info = {
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent() if PSUTIL_AVAILABLE else 0,
                'memory_percent': psutil.virtual_memory().percent if PSUTIL_AVAILABLE else 0,
                'disk_usage': psutil.disk_usage('/').percent if PSUTIL_AVAILABLE else 0
            }
            
            # 添加到會話數據
            if not hasattr(session, 'system_info'):
                session.system_info = []
            session.system_info.append(system_info)
            
        except Exception as e:
            self.logger.warning(f"收集系統信息失敗: {e}")
    
    async def _finalize_session(self, session_id: str, session: ClaudeSession):
        """完成會話處理"""
        try:
            # 計算會話統計
            duration = session.end_time - session.start_time
            
            # 更新統計
            self.stats["total_messages"] += len(session.messages)
            self.stats["total_tool_calls"] += len(session.tool_calls)
            self.stats["total_tokens"] += session.tokens_used
            self.stats["total_cost"] += session.cost_usd
            
            # 保存會話數據
            await self._save_session_data(session_id, session)
            
            # 移到完成列表
            self.completed_sessions.append(session)
            del self.active_sessions[session_id]
            
            # 保持列表大小限制
            if len(self.completed_sessions) > self.max_sessions:
                self.completed_sessions.pop(0)
            
            self.logger.info(f"📊 會話完成: {session_id} (時長: {duration:.1f}s)")
            
            # 觸發回調
            for callback in self.session_callbacks:
                try:
                    await callback('session_ended', session)
                except Exception as e:
                    self.logger.error(f"會話結束回調錯誤: {e}")
            
        except Exception as e:
            self.logger.error(f"完成會話處理失敗: {e}")
    
    async def _save_session_data(self, session_id: str, session: ClaudeSession):
        """保存會話數據"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            session_file = self.data_dir / f"session_{session_id}_{timestamp}.json"
            
            session_data = {
                'session_id': session_id,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'duration': session.end_time - session.start_time if session.end_time else 0,
                'messages': session.messages,
                'tool_calls': session.tool_calls,
                'tokens_used': session.tokens_used,
                'cost_usd': session.cost_usd,
                'project_context': session.project_context,
                'system_info': getattr(session, 'system_info', [])
            }
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"💾 會話數據已保存: {session_file}")
            
        except Exception as e:
            self.logger.error(f"保存會話數據失敗: {e}")
    
    async def _data_collector(self):
        """數據收集器主循環"""
        while self.running:
            try:
                # 定期保存統計數據
                await self._save_stats()
                
                # 清理舊數據
                if self.config.get("compress_old_data", True):
                    await self._cleanup_old_data()
                
                await asyncio.sleep(self.config.get("save_interval", 60))
                
            except Exception as e:
                self.logger.error(f"數據收集器錯誤: {e}")
                await asyncio.sleep(30)
    
    async def _save_stats(self):
        """保存統計數據"""
        try:
            self.stats["uptime"] = time.time() - self.start_time if self.start_time else 0
            
            stats_file = self.data_dir / "collector_stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.logger.error(f"保存統計數據失敗: {e}")
    
    async def _cleanup_old_data(self):
        """清理舊數據"""
        try:
            retention_days = self.config.get("retention_days", 30)
            cutoff_time = time.time() - (retention_days * 24 * 3600)
            
            for file_path in self.data_dir.glob("session_*.json"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    self.logger.debug(f"🗑️ 清理舊文件: {file_path}")
            
        except Exception as e:
            self.logger.error(f"清理舊數據失敗: {e}")
    
    async def _heartbeat_monitor(self):
        """心跳監控"""
        while self.running:
            try:
                self.logger.debug(f"💓 收集器心跳: {len(self.active_sessions)} 活躍會話")
                await asyncio.sleep(self.config.get("heartbeat_interval", 30))
            except Exception as e:
                self.logger.error(f"心跳監控錯誤: {e}")
    
    async def start_websocket_server(self):
        """啟動 WebSocket 服務器"""
        if not WEBSOCKETS_AVAILABLE:
            self.logger.warning("WebSocket 依賴不可用，跳過 WebSocket 服務器")
            return
        
        port = self.config.get("websocket_port", 8765)
        
        async def handle_websocket(websocket, path):
            try:
                self.logger.info(f"📡 WebSocket 客戶端連接: {websocket.remote_address}")
                
                # 發送當前狀態
                status = self.get_status()
                await websocket.send(json.dumps(status))
                
                # 保持連接並發送實時更新
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self._handle_websocket_message(websocket, data)
                    except json.JSONDecodeError:
                        await websocket.send(json.dumps({"error": "Invalid JSON"}))
                        
            except websockets.exceptions.ConnectionClosed:
                self.logger.info("📡 WebSocket 客戶端斷開連接")
            except Exception as e:
                self.logger.error(f"WebSocket 處理錯誤: {e}")
        
        server = await websockets.serve(handle_websocket, "localhost", port)
        self.logger.info(f"🌐 WebSocket 服務器啟動: ws://localhost:{port}")
        return server
    
    async def _handle_websocket_message(self, websocket, data: Dict[str, Any]):
        """處理 WebSocket 消息"""
        message_type = data.get("type", "")
        
        if message_type == "get_status":
            status = self.get_status()
            await websocket.send(json.dumps(status))
        
        elif message_type == "get_sessions":
            sessions = self.get_sessions()
            await websocket.send(json.dumps(sessions))
        
        elif message_type == "start_collection":
            await self.start_collection()
            await websocket.send(json.dumps({"status": "started"}))
        
        elif message_type == "stop_collection":
            await self.stop_collection()
            await websocket.send(json.dumps({"status": "stopped"}))
        
        else:
            await websocket.send(json.dumps({"error": f"Unknown message type: {message_type}"}))
    
    def get_status(self) -> Dict[str, Any]:
        """獲取收集器狀態"""
        return {
            "status": self.status.value,
            "running": self.running,
            "start_time": self.start_time,
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.completed_sessions),
            "claude_processes": len(self.claude_processes),
            "stats": self.stats,
            "config": self.config
        }
    
    def get_sessions(self) -> Dict[str, Any]:
        """獲取會話信息"""
        return {
            "active_sessions": [asdict(session) for session in self.active_sessions.values()],
            "completed_sessions": [asdict(session) for session in self.completed_sessions[-10:]],
            "total_sessions": len(self.active_sessions) + len(self.completed_sessions)
        }
    
    async def stop_collection(self):
        """停止收集"""
        self.logger.info("🛑 停止 Claude 實時數據收集...")
        self.running = False
        self.status = CollectorStatus.STOPPED
    
    async def shutdown(self):
        """關閉收集器"""
        try:
            await self.stop_collection()
            
            # 結束所有活躍會話
            for session_id, session in list(self.active_sessions.items()):
                session.end_time = time.time()
                await self._finalize_session(session_id, session)
            
            # 取消任務
            for task in [self.monitor_task, self.collector_task, self.heartbeat_task]:
                if task:
                    task.cancel()
            
            # 最終保存統計
            await self._save_stats()
            
            self.logger.info("✅ Claude 實時收集器已關閉")
            
        except Exception as e:
            self.logger.error(f"關閉收集器失敗: {e}")

# 全局收集器實例
claude_collector = ClaudeRealtimeCollector()

async def one_click_deploy():
    """一鍵部署 Claude 實時收集器"""
    print("🚀 一鍵部署 Claude 實時信息收集器")
    print("=" * 50)
    
    try:
        # 配置日誌
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 初始化收集器
        success = await claude_collector.initialize()
        
        if success:
            print("✅ Claude 實時收集器部署成功！")
            print(f"📊 監控面板: http://localhost:{claude_collector.config.get('websocket_port', 8765)}")
            print(f"💾 數據目錄: {claude_collector.data_dir}")
            print("🔍 正在監控 Claude 相關進程...")
            print("\n按 Ctrl+C 停止收集器")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 正在停止收集器...")
        else:
            print("❌ 收集器部署失敗")
            return False
    
    except Exception as e:
        print(f"❌ 部署過程中出錯: {e}")
        return False
    
    finally:
        await claude_collector.shutdown()
    
    return True

if __name__ == "__main__":
    asyncio.run(one_click_deploy())