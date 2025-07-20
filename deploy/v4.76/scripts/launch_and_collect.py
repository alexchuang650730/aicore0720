#!/usr/bin/env python3
"""
PowerAutomation & ClaudeEditor 全量級啟動和數據收集器
同時測試功能並收集訓練數據
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import queue
import signal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PowerAutomationLauncher:
    """PowerAutomation 全量級啟動器"""
    
    def __init__(self):
        self.processes = {}
        self.data_queue = queue.Queue()
        self.collectors = []
        self.running = False
        self.data_dir = Path("training_data/live_collection")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    async def launch_all_services(self):
        """啟動所有服務"""
        logger.info("🚀 啟動 PowerAutomation 全量級服務...")
        
        services = [
            {
                "name": "MCP-Zero Engine",
                "command": ["python3", "core/mcp_zero/mcp_zero_engine.py"],
                "port": None
            },
            {
                "name": "Main API Server",
                "command": ["python3", "core/api/main_api_server.py"],
                "port": 8000
            },
            {
                "name": "ClaudeEditor Backend",
                "command": ["python3", "core/components/claudeditor_ui/backend_server.py"],
                "port": 8080
            },
            {
                "name": "MCP Servers",
                "command": ["python3", "deploy/v4.74/start_all_mcps.py"],
                "port": None
            }
        ]
        
        # 啟動服務
        for service in services:
            try:
                logger.info(f"啟動 {service['name']}...")
                
                # 檢查端口是否被占用
                if service['port'] and self._is_port_in_use(service['port']):
                    logger.warning(f"端口 {service['port']} 已被占用，跳過 {service['name']}")
                    continue
                
                process = subprocess.Popen(
                    service['command'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.processes[service['name']] = process
                
                # 等待服務啟動
                await asyncio.sleep(2)
                
                if process.poll() is None:
                    logger.info(f"✅ {service['name']} 啟動成功 (PID: {process.pid})")
                else:
                    logger.error(f"❌ {service['name']} 啟動失敗")
                    
            except Exception as e:
                logger.error(f"啟動 {service['name']} 失敗: {str(e)}")
        
        # 啟動前端
        await self.launch_frontend()
        
        # 啟動數據收集器
        self.start_data_collectors()
        
        self.running = True
        logger.info("✅ 所有服務啟動完成！")
    
    async def launch_frontend(self):
        """啟動前端界面"""
        logger.info("啟動 ClaudeEditor 前端...")
        
        # 檢查是否需要安裝依賴
        claudeditor_path = Path("deploy/claudeditor")
        if not (claudeditor_path / "node_modules").exists():
            logger.info("安裝前端依賴...")
            subprocess.run(["npm", "install"], cwd=claudeditor_path, check=True)
        
        # 啟動開發服務器
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=claudeditor_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.processes["ClaudeEditor Frontend"] = frontend_process
        
        # 等待前端啟動
        await asyncio.sleep(5)
        
        logger.info("✅ ClaudeEditor 前端已啟動: http://localhost:3000")
        
        # 自動打開瀏覽器
        try:
            subprocess.run(["open", "http://localhost:3000"])
        except:
            logger.info("請手動打開瀏覽器訪問: http://localhost:3000")
    
    def start_data_collectors(self):
        """啟動數據收集器"""
        logger.info("啟動數據收集器...")
        
        # API 請求收集器
        api_collector = threading.Thread(
            target=self.collect_api_requests,
            daemon=True
        )
        api_collector.start()
        self.collectors.append(api_collector)
        
        # 用戶交互收集器
        ui_collector = threading.Thread(
            target=self.collect_ui_interactions,
            daemon=True
        )
        ui_collector.start()
        self.collectors.append(ui_collector)
        
        # MCP 調用收集器
        mcp_collector = threading.Thread(
            target=self.collect_mcp_calls,
            daemon=True
        )
        mcp_collector.start()
        self.collectors.append(mcp_collector)
        
        logger.info("✅ 數據收集器已啟動")
    
    def collect_api_requests(self):
        """收集 API 請求數據"""
        log_file = Path("logs/api_requests.log")
        if not log_file.exists():
            return
        
        with open(log_file, 'r') as f:
            # 移動到文件末尾
            f.seek(0, 2)
            
            while self.running:
                line = f.readline()
                if line:
                    try:
                        # 解析 API 請求
                        if "REQUEST" in line or "RESPONSE" in line:
                            data = {
                                "type": "api_request",
                                "timestamp": datetime.now().isoformat(),
                                "content": line.strip()
                            }
                            self.data_queue.put(data)
                    except:
                        pass
                else:
                    time.sleep(0.1)
    
    def collect_ui_interactions(self):
        """收集 UI 交互數據"""
        # 監控前端日志
        log_file = Path("logs/frontend.log")
        if not log_file.exists():
            return
        
        with open(log_file, 'r') as f:
            f.seek(0, 2)
            
            while self.running:
                line = f.readline()
                if line:
                    try:
                        if "USER_ACTION" in line:
                            data = {
                                "type": "ui_interaction",
                                "timestamp": datetime.now().isoformat(),
                                "content": line.strip()
                            }
                            self.data_queue.put(data)
                    except:
                        pass
                else:
                    time.sleep(0.1)
    
    def collect_mcp_calls(self):
        """收集 MCP 調用數據"""
        # 監控 MCP 日志
        log_file = Path("logs/mcp_calls.log")
        if not log_file.exists():
            return
        
        with open(log_file, 'r') as f:
            f.seek(0, 2)
            
            while self.running:
                line = f.readline()
                if line:
                    try:
                        if "MCP_CALL" in line:
                            data = {
                                "type": "mcp_call",
                                "timestamp": datetime.now().isoformat(),
                                "content": line.strip()
                            }
                            self.data_queue.put(data)
                    except:
                        pass
                else:
                    time.sleep(0.1)
    
    async def run_test_scenarios(self):
        """運行測試場景以生成數據"""
        logger.info("開始運行測試場景...")
        
        scenarios = [
            {
                "name": "代碼生成測試",
                "actions": [
                    {"type": "create_file", "params": {"filename": "test.py"}},
                    {"type": "generate_code", "params": {"prompt": "創建一個 FastAPI 應用"}},
                    {"type": "run_tests", "params": {}}
                ]
            },
            {
                "name": "UI 生成測試",
                "actions": [
                    {"type": "create_component", "params": {"name": "Dashboard"}},
                    {"type": "add_responsive_design", "params": {}},
                    {"type": "preview", "params": {}}
                ]
            },
            {
                "name": "工作流測試",
                "actions": [
                    {"type": "create_workflow", "params": {"name": "CI/CD Pipeline"}},
                    {"type": "add_steps", "params": {"steps": ["test", "build", "deploy"]}},
                    {"type": "execute", "params": {}}
                ]
            }
        ]
        
        for scenario in scenarios:
            logger.info(f"執行場景: {scenario['name']}")
            
            for action in scenario['actions']:
                # 記錄測試動作
                test_data = {
                    "type": "test_scenario",
                    "scenario": scenario['name'],
                    "action": action,
                    "timestamp": datetime.now().isoformat()
                }
                self.data_queue.put(test_data)
                
                # 模擬執行時間
                await asyncio.sleep(2)
            
            logger.info(f"✅ 場景 {scenario['name']} 完成")
    
    def save_collected_data(self):
        """保存收集的數據"""
        collected_data = []
        
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get_nowait()
                collected_data.append(data)
            except:
                break
        
        if collected_data:
            filename = self.data_dir / f"collected_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            with open(filename, 'a', encoding='utf-8') as f:
                for item in collected_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            logger.info(f"保存了 {len(collected_data)} 條數據到 {filename}")
    
    def _is_port_in_use(self, port: int) -> bool:
        """檢查端口是否被占用"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    async def monitor_and_collect(self):
        """監控並收集數據"""
        logger.info("開始監控和數據收集...")
        
        while self.running:
            # 定期保存數據
            self.save_collected_data()
            
            # 檢查服務狀態
            for name, process in self.processes.items():
                if process.poll() is not None:
                    logger.warning(f"服務 {name} 已停止")
            
            await asyncio.sleep(10)
    
    async def shutdown(self):
        """關閉所有服務"""
        logger.info("關閉所有服務...")
        self.running = False
        
        # 保存最後的數據
        self.save_collected_data()
        
        # 終止所有進程
        for name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"終止 {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        logger.info("✅ 所有服務已關閉")


async def main():
    """主函數"""
    launcher = PowerAutomationLauncher()
    
    # 設置信號處理
    def signal_handler(signum, frame):
        logger.info("收到終止信號...")
        asyncio.create_task(launcher.shutdown())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 啟動所有服務
        await launcher.launch_all_services()
        
        # 等待服務穩定
        await asyncio.sleep(5)
        
        # 運行測試場景
        test_task = asyncio.create_task(launcher.run_test_scenarios())
        
        # 開始監控和收集
        monitor_task = asyncio.create_task(launcher.monitor_and_collect())
        
        logger.info("🎯 系統已完全啟動！")
        logger.info("📊 正在收集數據...")
        logger.info("🌐 ClaudeEditor: http://localhost:3000")
        logger.info("🚀 API Server: http://localhost:8000")
        logger.info("\n按 Ctrl+C 停止並保存數據")
        
        # 等待任務
        await asyncio.gather(test_task, monitor_task)
        
    except KeyboardInterrupt:
        logger.info("用戶中斷...")
    finally:
        await launcher.shutdown()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════╗
║  PowerAutomation & ClaudeEditor 啟動器      ║
║  全量級功能測試 + 數據收集                    ║
╚══════════════════════════════════════════════╝
""")
    
    asyncio.run(main())