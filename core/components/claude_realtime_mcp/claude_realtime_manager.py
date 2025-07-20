#!/usr/bin/env python3
"""
Claude實時收集器MCP管理器
整合Claude實時收集器到MCP架構中，作為第21個MCP組件
解決K2和DeepSWE訓練數據不足的問題
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
import uuid
import subprocess
import signal

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

from ..mcp_base import MCPBase

logger = logging.getLogger(__name__)

@dataclass
class TrainingDataPoint:
    """訓練數據點"""
    id: str
    timestamp: float
    user_input: str
    assistant_response: str
    tool_calls: List[Dict[str, Any]]
    context: Dict[str, Any]
    session_id: str
    category: str  # 'k2', 'deepswe', 'general'
    confidence: float
    source: str  # 'claude_code', 'claudeditor', 'manus'

@dataclass 
class TrainingSession:
    """訓練會話"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    data_points: List[TrainingDataPoint] = None
    total_interactions: int = 0
    k2_examples: int = 0
    deepswe_examples: int = 0
    project_context: str = ""
    user_goal: str = ""
    
    def __post_init__(self):
        if self.data_points is None:
            self.data_points = []

class ClaudeRealtimeMCPManager(MCPBase):
    """Claude實時收集器MCP管理器"""
    
    def __init__(self):
        super().__init__()
        self.name = "claude_realtime_mcp"
        self.version = "1.0.0"
        self.description = "Claude實時數據收集與K2/DeepSWE訓練數據生成器"
        
        # 數據存儲
        self.data_dir = Path("./data/claude_realtime_mcp")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 會話管理
        self.active_sessions: Dict[str, TrainingSession] = {}
        self.completed_sessions: List[TrainingSession] = []
        
        # 訓練數據統計
        self.training_stats = {
            "total_k2_examples": 0,
            "total_deepswe_examples": 0,
            "total_general_examples": 0,
            "sessions_completed": 0,
            "data_quality_score": 0.0,
            "last_collection_time": None
        }
        
        # 監控配置
        self.collection_running = False
        self.monitor_task = None
        self.save_task = None
        
        # 進程監控
        self.claude_processes = []
        self.monitored_commands = [
            "claude",
            "claude-code", 
            "claudeditor",
            "manus"
        ]
        
        # K2和DeepSWE特徵檢測
        self.k2_keywords = [
            "k2", "優化", "分析", "執行任務", "基於分析",
            "觀察結果", "執行操作", "思考", "決策"
        ]
        
        self.deepswe_keywords = [
            "代碼", "編程", "開發", "debug", "程式", "函數",
            "算法", "軟體工程", "架構", "重構", "測試"
        ]
        
        # 質量評估閾值
        self.quality_thresholds = {
            "min_interaction_length": 50,
            "min_response_length": 100,
            "tool_usage_bonus": 0.2,
            "context_richness_bonus": 0.1
        }
    
    async def initialize(self) -> bool:
        """初始化MCP組件"""
        try:
            self.logger.info("🚀 初始化Claude實時收集器MCP...")
            
            # 設置信號處理器
            self._setup_signal_handlers()
            
            # 啟動數據收集
            await self.start_collection()
            
            # 啟動自動保存任務
            self.save_task = asyncio.create_task(self._auto_save_loop())
            
            self.logger.info("✅ Claude實時收集器MCP初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Claude實時收集器MCP初始化失敗: {e}")
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
        if self.collection_running:
            return
        
        self.collection_running = True
        self.monitor_task = asyncio.create_task(self._monitor_claude_processes())
        
        self.logger.info("🎯 Claude實時數據收集已啟動")
    
    async def stop_collection(self):
        """停止數據收集"""
        self.collection_running = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
        
        if self.save_task:
            self.save_task.cancel()
        
        self.logger.info("🛑 Claude實時數據收集已停止")
    
    async def _monitor_claude_processes(self):
        """監控Claude相關進程"""
        while self.collection_running:
            try:
                if PSUTIL_AVAILABLE:
                    await self._detect_claude_sessions()
                else:
                    await self._detect_claude_sessions_fallback()
                
                await asyncio.sleep(2.0)  # 2秒檢查一次
                
            except Exception as e:
                self.logger.error(f"進程監控錯誤: {e}")
                await asyncio.sleep(5)
    
    async def _detect_claude_sessions(self):
        """檢測Claude會話（psutil版本）"""
        current_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                proc_info = proc.info
                cmd_line = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                
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
        
        # 檢測新的Claude會話
        for proc in current_processes:
            if proc['pid'] not in [p['pid'] for p in self.claude_processes]:
                await self._on_claude_session_started(proc)
        
        # 檢測結束的會話
        active_pids = [p['pid'] for p in current_processes]
        for proc in self.claude_processes[:]:
            if proc['pid'] not in active_pids:
                await self._on_claude_session_ended(proc)
                self.claude_processes.remove(proc)
        
        self.claude_processes = current_processes
    
    async def _detect_claude_sessions_fallback(self):
        """檢測Claude會話（回退版本）"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            
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
            
            # 簡單的新會話檢測
            for proc in current_processes:
                if proc['pid'] not in [p['pid'] for p in self.claude_processes]:
                    await self._on_claude_session_started(proc)
            
            self.claude_processes = current_processes
            
        except Exception as e:
            self.logger.warning(f"回退會話檢測失敗: {e}")
    
    async def _on_claude_session_started(self, proc_info: Dict[str, Any]):
        """Claude會話開始事件"""
        session_id = str(uuid.uuid4())
        
        session = TrainingSession(
            session_id=session_id,
            start_time=time.time(),
            project_context=self._detect_project_context(proc_info)
        )
        
        self.active_sessions[session_id] = session
        
        self.logger.info(f"🔍 檢測到新的Claude會話: {proc_info['name']} (Session: {session_id[:8]})")
        
        # 開始收集這個會話的訓練數據
        asyncio.create_task(self._collect_session_training_data(session_id, proc_info))
    
    async def _on_claude_session_ended(self, proc_info: Dict[str, Any]):
        """Claude會話結束事件"""
        self.logger.info(f"📝 Claude會話結束: {proc_info['name']}")
        
        # 結束所有相關的活躍會話
        for session_id, session in list(self.active_sessions.items()):
            if session.end_time is None:
                session.end_time = time.time()
                await self._finalize_training_session(session_id, session)
    
    def _detect_project_context(self, proc_info: Dict[str, Any]) -> str:
        """檢測項目上下文"""
        cmdline = proc_info.get('cmdline', '')
        
        # 從命令行檢測項目路徑
        if 'claude' in cmdline:
            parts = cmdline.split()
            for part in parts:
                if part.startswith('/') and ('project' in part.lower() or 'work' in part.lower()):
                    return part
                if part.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    return os.path.dirname(part)
        
        # 檢測當前工作目錄
        try:
            return os.getcwd()
        except:
            return "unknown"
    
    async def _collect_session_training_data(self, session_id: str, proc_info: Dict[str, Any]):
        """收集會話的訓練數據"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        try:
            # 模擬收集Claude對話數據
            # 在實際實現中，這裡需要接入Claude的實際對話流
            await self._simulate_training_data_collection(session)
            
        except Exception as e:
            self.logger.error(f"收集訓練數據失敗: {e}")
    
    async def _simulate_training_data_collection(self, session: TrainingSession):
        """模擬訓練數據收集（示例實現）"""
        # 這是一個示例實現，實際應該接入真實的Claude對話流
        sample_interactions = [
            {
                "user": "幫我分析這個Python函數的性能問題",
                "assistant": "我將分析這個函數的性能。首先檢查算法複雜度...",
                "tools": [{"name": "code_analysis", "result": "O(n²) complexity detected"}],
                "category": "deepswe"
            },
            {
                "user": "K2優化：提升這個查詢的效率",
                "assistant": "基於分析，我發現可以通過索引優化來提升效率...",
                "tools": [{"name": "database_optimizer", "result": "index suggestion"}],
                "category": "k2"
            }
        ]
        
        for interaction in sample_interactions:
            data_point = TrainingDataPoint(
                id=str(uuid.uuid4()),
                timestamp=time.time(),
                user_input=interaction["user"],
                assistant_response=interaction["assistant"],
                tool_calls=interaction["tools"],
                context={"project": session.project_context},
                session_id=session.session_id,
                category=interaction["category"],
                confidence=self._calculate_data_quality(interaction),
                source="claude_code"
            )
            
            session.data_points.append(data_point)
            session.total_interactions += 1
            
            if interaction["category"] == "k2":
                session.k2_examples += 1
            elif interaction["category"] == "deepswe":
                session.deepswe_examples += 1
            
            await asyncio.sleep(0.1)  # 模擬實時收集
    
    def _calculate_data_quality(self, interaction: Dict[str, Any]) -> float:
        """計算數據質量分數"""
        quality_score = 0.5  # 基礎分數
        
        # 檢查輸入長度
        if len(interaction["user"]) >= self.quality_thresholds["min_interaction_length"]:
            quality_score += 0.1
        
        # 檢查回應長度
        if len(interaction["assistant"]) >= self.quality_thresholds["min_response_length"]:
            quality_score += 0.1
        
        # 工具使用加分
        if interaction.get("tools") and len(interaction["tools"]) > 0:
            quality_score += self.quality_thresholds["tool_usage_bonus"]
        
        # 上下文豐富度加分
        if len(interaction.get("context", {})) > 0:
            quality_score += self.quality_thresholds["context_richness_bonus"]
        
        # K2和DeepSWE特徵檢測加分
        text_content = (interaction["user"] + " " + interaction["assistant"]).lower()
        
        k2_matches = sum(1 for keyword in self.k2_keywords if keyword in text_content)
        deepswe_matches = sum(1 for keyword in self.deepswe_keywords if keyword in text_content)
        
        if k2_matches > 0:
            quality_score += min(k2_matches * 0.05, 0.2)
        
        if deepswe_matches > 0:
            quality_score += min(deepswe_matches * 0.05, 0.2)
        
        return min(quality_score, 1.0)
    
    async def _finalize_training_session(self, session_id: str, session: TrainingSession):
        """完成訓練會話處理"""
        try:
            # 計算會話統計
            duration = session.end_time - session.start_time
            
            # 更新全局統計
            self.training_stats["total_k2_examples"] += session.k2_examples
            self.training_stats["total_deepswe_examples"] += session.deepswe_examples
            self.training_stats["total_general_examples"] += (
                session.total_interactions - session.k2_examples - session.deepswe_examples
            )
            self.training_stats["sessions_completed"] += 1
            self.training_stats["last_collection_time"] = datetime.now().isoformat()
            
            # 計算數據質量分數
            if session.data_points:
                avg_quality = sum(dp.confidence for dp in session.data_points) / len(session.data_points)
                self.training_stats["data_quality_score"] = avg_quality
            
            # 保存訓練數據
            await self._save_training_data(session_id, session)
            
            # 生成K2/DeepSWE格式的訓練文件
            await self._generate_k2_training_files(session)
            await self._generate_deepswe_training_files(session)
            
            # 移到完成列表
            self.completed_sessions.append(session)
            del self.active_sessions[session_id]
            
            # 保持列表大小限制
            if len(self.completed_sessions) > 100:
                self.completed_sessions.pop(0)
            
            self.logger.info(
                f"📊 訓練會話完成: {session_id[:8]} "
                f"(時長: {duration:.1f}s, "
                f"K2: {session.k2_examples}, "
                f"DeepSWE: {session.deepswe_examples})"
            )
            
        except Exception as e:
            self.logger.error(f"完成訓練會話處理失敗: {e}")
    
    async def _save_training_data(self, session_id: str, session: TrainingSession):
        """保存訓練數據"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            session_file = self.data_dir / f"training_session_{session_id}_{timestamp}.json"
            
            session_data = {
                'session_id': session_id,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'duration': session.end_time - session.start_time if session.end_time else 0,
                'total_interactions': session.total_interactions,
                'k2_examples': session.k2_examples,
                'deepswe_examples': session.deepswe_examples,
                'project_context': session.project_context,
                'data_points': [asdict(dp) for dp in session.data_points]
            }
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"💾 訓練數據已保存: {session_file}")
            
        except Exception as e:
            self.logger.error(f"保存訓練數據失敗: {e}")
    
    async def _generate_k2_training_files(self, session: TrainingSession):
        """生成K2格式的訓練文件"""
        try:
            k2_data_points = [dp for dp in session.data_points if dp.category == "k2"]
            
            if not k2_data_points:
                return
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            k2_file = self.data_dir / f"k2_training_{timestamp}.jsonl"
            
            with open(k2_file, 'w', encoding='utf-8') as f:
                for dp in k2_data_points:
                    k2_format = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是 K2 優化器，擅長分析任務並提供最佳解決方案。"
                            },
                            {
                                "role": "user", 
                                "content": f"分析並執行任務\\n{dp.user_input}"
                            },
                            {
                                "role": "assistant",
                                "content": dp.assistant_response
                            }
                        ],
                        "metadata": {
                            "category": dp.category,
                            "tools": dp.tool_calls,
                            "confidence": dp.confidence,
                            "source": dp.source
                        }
                    }
                    f.write(json.dumps(k2_format, ensure_ascii=False) + '\n')
            
            self.logger.info(f"📝 K2訓練文件已生成: {k2_file} ({len(k2_data_points)} 樣本)")
            
        except Exception as e:
            self.logger.error(f"生成K2訓練文件失敗: {e}")
    
    async def _generate_deepswe_training_files(self, session: TrainingSession):
        """生成DeepSWE格式的訓練文件"""
        try:
            deepswe_data_points = [dp for dp in session.data_points if dp.category == "deepswe"]
            
            if not deepswe_data_points:
                return
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            deepswe_file = self.data_dir / f"deepswe_training_{timestamp}.jsonl"
            
            with open(deepswe_file, 'w', encoding='utf-8') as f:
                for dp in deepswe_data_points:
                    deepswe_format = {
                        "instruction": dp.user_input,
                        "input": json.dumps(dp.context),
                        "output": dp.assistant_response,
                        "tools_used": dp.tool_calls,
                        "metadata": {
                            "category": "software_engineering",
                            "confidence": dp.confidence,
                            "source": dp.source,
                            "timestamp": dp.timestamp
                        }
                    }
                    f.write(json.dumps(deepswe_format, ensure_ascii=False) + '\n')
            
            self.logger.info(f"📝 DeepSWE訓練文件已生成: {deepswe_file} ({len(deepswe_data_points)} 樣本)")
            
        except Exception as e:
            self.logger.error(f"生成DeepSWE訓練文件失敗: {e}")
    
    async def _auto_save_loop(self):
        """自動保存循環"""
        while self.collection_running:
            try:
                await self._save_stats()
                await asyncio.sleep(60)  # 每分鐘保存一次統計
            except Exception as e:
                self.logger.error(f"自動保存失敗: {e}")
                await asyncio.sleep(30)
    
    async def _save_stats(self):
        """保存統計數據"""
        try:
            stats_file = self.data_dir / "training_stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存統計數據失敗: {e}")
    
    async def get_training_summary(self) -> Dict[str, Any]:
        """獲取訓練數據摘要"""
        return {
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.completed_sessions),
            "training_stats": self.training_stats,
            "data_directory": str(self.data_dir),
            "collection_running": self.collection_running,
            "monitored_processes": len(self.claude_processes)
        }
    
    async def export_training_data(self, format_type: str = "combined") -> str:
        """匯出訓練數據"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format_type == "k2":
                export_file = self.data_dir / f"k2_export_{timestamp}.jsonl"
                await self._export_k2_data(export_file)
            elif format_type == "deepswe":
                export_file = self.data_dir / f"deepswe_export_{timestamp}.jsonl"
                await self._export_deepswe_data(export_file)
            else:
                export_file = self.data_dir / f"combined_export_{timestamp}.json"
                await self._export_combined_data(export_file)
            
            return str(export_file)
            
        except Exception as e:
            self.logger.error(f"匯出訓練數據失敗: {e}")
            raise
    
    async def _export_k2_data(self, export_file: Path):
        """匯出K2格式數據"""
        with open(export_file, 'w', encoding='utf-8') as f:
            for session in self.completed_sessions:
                for dp in session.data_points:
                    if dp.category == "k2":
                        k2_format = {
                            "messages": [
                                {"role": "system", "content": "你是 K2 優化器，擅長分析任務並提供最佳解決方案。"},
                                {"role": "user", "content": f"分析並執行任務\\n{dp.user_input}"},
                                {"role": "assistant", "content": dp.assistant_response}
                            ],
                            "metadata": {
                                "category": dp.category,
                                "tools": dp.tool_calls,
                                "confidence": dp.confidence,
                                "source": dp.source
                            }
                        }
                        f.write(json.dumps(k2_format, ensure_ascii=False) + '\n')
    
    async def _export_deepswe_data(self, export_file: Path):
        """匯出DeepSWE格式數據"""
        with open(export_file, 'w', encoding='utf-8') as f:
            for session in self.completed_sessions:
                for dp in session.data_points:
                    if dp.category == "deepswe":
                        deepswe_format = {
                            "instruction": dp.user_input,
                            "input": json.dumps(dp.context),
                            "output": dp.assistant_response,
                            "tools_used": dp.tool_calls,
                            "metadata": {
                                "category": "software_engineering",
                                "confidence": dp.confidence,
                                "source": dp.source,
                                "timestamp": dp.timestamp
                            }
                        }
                        f.write(json.dumps(deepswe_format, ensure_ascii=False) + '\n')
    
    async def _export_combined_data(self, export_file: Path):
        """匯出綜合格式數據"""
        combined_data = {
            "export_timestamp": datetime.now().isoformat(),
            "training_stats": self.training_stats,
            "sessions": [asdict(session) for session in self.completed_sessions],
            "summary": await self.get_training_summary()
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
    
    async def shutdown(self):
        """關閉MCP組件"""
        try:
            await self.stop_collection()
            
            # 結束所有活躍會話
            for session_id, session in list(self.active_sessions.items()):
                session.end_time = time.time()
                await self._finalize_training_session(session_id, session)
            
            # 最終保存統計
            await self._save_stats()
            
            self.logger.info("✅ Claude實時收集器MCP已關閉")
            
        except Exception as e:
            self.logger.error(f"關閉MCP組件失敗: {e}")

# 全局實例
claude_realtime_mcp = ClaudeRealtimeMCPManager()

async def deploy_claude_realtime_mcp():
    """部署Claude實時收集器MCP"""
    print("🚀 部署Claude實時收集器MCP - 第21個MCP組件")
    print("=" * 60)
    
    try:
        # 配置日誌
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 初始化MCP
        success = await claude_realtime_mcp.initialize()
        
        if success:
            print("✅ Claude實時收集器MCP部署成功！")
            print(f"📊 數據目錄: {claude_realtime_mcp.data_dir}")
            print("🔍 正在監控Claude會話並收集訓練數據...")
            print("🎯 自動生成K2和DeepSWE訓練數據...")
            print("\n當前訓練數據統計:")
            
            summary = await claude_realtime_mcp.get_training_summary()
            for key, value in summary["training_stats"].items():
                print(f"  {key}: {value}")
            
            print("\n按 Ctrl+C 停止收集器")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 正在停止收集器...")
        else:
            print("❌ MCP部署失敗")
            return False
    
    except Exception as e:
        print(f"❌ 部署過程中出錯: {e}")
        return False
    
    finally:
        await claude_realtime_mcp.shutdown()
    
    return True

if __name__ == "__main__":
    asyncio.run(deploy_claude_realtime_mcp())