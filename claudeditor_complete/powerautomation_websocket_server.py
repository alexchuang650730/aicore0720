#!/usr/bin/env python3
"""
PowerAutomation WebSocket服務器
實現PowerAutomation Core和ClaudeEditor之間的雙向通信
包含Claude Router MCP和Command執行功能
"""

import asyncio
import json
import logging
import websockets
import subprocess
import os
import sys
from typing import Dict, Set, Any, List
from pathlib import Path
import uuid
import time
from datetime import datetime

# 添加項目根目錄到Python路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# 導入PowerAutomation Core組件
try:
    from core.powerautomation_core_driver import PowerAutomationCoreDriver
except ImportError as e:
    print(f"⚠️ 無法導入PowerAutomation Core組件: {e}")
    PowerAutomationCoreDriver = None

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PowerAutomationWebSocketServer:
    """PowerAutomation WebSocket服務器"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.claudeditor_clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.powerautomation_core: PowerAutomationCoreDriver = None
        self.server = None
        
        # 初始化PowerAutomation Core
        if PowerAutomationCoreDriver:
            self.powerautomation_core = PowerAutomationCoreDriver()
        
        logger.info(f"🚀 PowerAutomation WebSocket服務器初始化: {host}:{port}")
    
    async def start_server(self):
        """啟動WebSocket服務器"""
        try:
            # 初始化PowerAutomation Core
            if self.powerautomation_core:
                await self.powerautomation_core.initialize()
                logger.info("✅ PowerAutomation Core初始化完成")
            
            # 啟動WebSocket服務器
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port,
                ping_interval=20,
                ping_timeout=10
            )
            
            logger.info(f"🌐 PowerAutomation WebSocket服務器啟動: ws://{self.host}:{self.port}")
            logger.info("🎯 等待ClaudeEditor連接...")
            
            # 保持服務器運行
            await self.server.wait_closed()
            
        except Exception as e:
            logger.error(f"❌ 服務器啟動失敗: {e}")
            raise
    
    async def handle_client(self, websocket, path):
        """處理客戶端連接"""
        client_id = str(uuid.uuid4())
        logger.info(f"🔗 新客戶端連接: {client_id} from {websocket.remote_address}")
        
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 客戶端斷開連接: {client_id}")
        except Exception as e:
            logger.error(f"❌ 處理客戶端消息錯誤: {e}")
        finally:
            self.clients.discard(websocket)
            
            # 如果是ClaudeEditor客戶端，從註冊列表中移除
            registration_id = None
            for reg_id, client in self.claudeditor_clients.items():
                if client == websocket:
                    registration_id = reg_id
                    break
            
            if registration_id:
                del self.claudeditor_clients[registration_id]
                logger.info(f"📋 ClaudeEditor客戶端取消註冊: {registration_id}")
    
    async def handle_message(self, websocket, client_id, message):
        """處理客戶端消息"""
        try:
            data = json.loads(message)
            action = data.get('action', '')
            
            logger.info(f"📨 收到消息: {action} from {client_id}")
            
            # 路由消息到相應的處理器
            if action == 'register_claudeditor':
                await self.handle_claudeditor_registration(websocket, client_id, data)
                
            elif action == 'workflow_selected':
                await self.handle_workflow_selected(websocket, client_id, data)
                
            elif action == 'quick_action':
                await self.handle_quick_action(websocket, client_id, data)
                
            elif action == 'ai_mode_switched':
                await self.handle_ai_mode_switched(websocket, client_id, data)
                
            elif action == 'command_result':
                await self.handle_command_result(websocket, client_id, data)
                
            elif action == 'heartbeat_response':
                await self.handle_heartbeat_response(websocket, client_id, data)
                
            elif action == 'execute_claude_code_command':
                await self.handle_claude_code_command(websocket, client_id, data)
                
            else:
                logger.warning(f"⚠️ 未知消息類型: {action}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析錯誤: {e}")
        except Exception as e:
            logger.error(f"❌ 處理消息錯誤: {e}")
    
    async def handle_claudeditor_registration(self, websocket, client_id, data):
        """處理ClaudeEditor註冊"""
        try:
            claudeditor_info = data.get('data', {})
            
            # 通過PowerAutomation Core註冊ClaudeEditor
            if self.powerautomation_core:
                registration_id = await self.powerautomation_core.register_claudeditor(claudeditor_info)
            else:
                registration_id = str(uuid.uuid4())
            
            # 保存客戶端連接
            self.claudeditor_clients[registration_id] = websocket
            
            # 發送註冊成功響應
            response = {
                'action': 'registration_response',
                'data': {
                    'success': True,
                    'registration_id': registration_id,
                    'driver_id': self.powerautomation_core.driver_id if self.powerautomation_core else 'mock_driver',
                    'message': 'ClaudeEditor已成功註冊到PowerAutomation Core'
                }
            }
            
            await websocket.send(json.dumps(response))
            
            logger.info(f"✅ ClaudeEditor註冊成功: {registration_id}")
            
            # 啟動一個示例工作流以演示驅動功能
            await asyncio.sleep(2)
            await self.demonstrate_driving_capability(websocket, registration_id)
            
        except Exception as e:
            logger.error(f"❌ ClaudeEditor註冊失敗: {e}")
            
            response = {
                'action': 'registration_response',
                'data': {
                    'success': False,
                    'error': str(e)
                }
            }
            
            await websocket.send(json.dumps(response))
    
    async def demonstrate_driving_capability(self, websocket, registration_id):
        """演示PowerAutomation驅動ClaudeEditor的能力"""
        try:
            # 演示1: 啟動目標驅動開發工作流
            demo_message = {
                'action': 'drive_workflow',
                'data': {
                    'workflow_id': str(uuid.uuid4()),
                    'goal_id': str(uuid.uuid4()),
                    'workflow_type': 'goal_driven_development',
                    'user_goal': '創建用戶管理系統',
                    'requirements': ['用戶註冊', '用戶登錄', '權限管理'],
                    'acceptance_criteria': ['功能正常', '性能良好', '安全可靠']
                }
            }
            
            await websocket.send(json.dumps(demo_message))
            logger.info(f"📋 發送工作流驅動演示: {registration_id}")
            
            # 演示2: 更新目標對齊度
            await asyncio.sleep(3)
            alignment_message = {
                'action': 'drive_goal_update',
                'data': {
                    'goal_id': demo_message['data']['goal_id'],
                    'alignment_score': 95,
                    'progress': 0.15,
                    'feedback': 'PowerAutomation Core正在驅動開發進程，目標對齊度提升至95%'
                }
            }
            
            await websocket.send(json.dumps(alignment_message))
            logger.info(f"📊 發送目標更新演示: {registration_id}")
            
            # 演示3: 執行命令
            await asyncio.sleep(3)
            command_message = {
                'action': 'drive_command',
                'data': {
                    'command': 'analyze_code',
                    'parameters': {
                        'language': 'javascript',
                        'analysis_type': 'quality',
                        'context': 'user_management_system'
                    }
                }
            }
            
            await websocket.send(json.dumps(command_message))
            logger.info(f"⚡ 發送命令執行演示: {registration_id}")
            
        except Exception as e:
            logger.error(f"❌ 演示驅動能力失敗: {e}")
    
    async def handle_workflow_selected(self, websocket, client_id, data):
        """處理工作流選擇"""
        try:
            registration_id = data.get('registration_id')
            workflow_data = data.get('data', {})
            
            if self.powerautomation_core and registration_id:
                # 通知PowerAutomation Core工作流選擇
                result = await self.powerautomation_core.drive_claudeditor(
                    registration_id=registration_id,
                    action="start_workflow",
                    parameters={
                        "workflow_type": workflow_data.get('workflow_type'),
                        "user_goal": f"用戶選擇了{workflow_data.get('workflow_type')}工作流",
                        "context_data": workflow_data
                    }
                )
                
                logger.info(f"🎯 工作流選擇處理結果: {result}")
            
        except Exception as e:
            logger.error(f"❌ 處理工作流選擇失敗: {e}")
    
    async def handle_quick_action(self, websocket, client_id, data):
        """處理快速操作"""
        try:
            registration_id = data.get('registration_id')
            action_data = data.get('data', {})
            
            if self.powerautomation_core and registration_id:
                # 將快速操作轉換為PowerAutomation命令
                command_map = {
                    'analysis': 'analyze_code',
                    'refactor': 'refactor',
                    'deploy': 'deploy',
                    'sync': 'sync_mobile'
                }
                
                command = command_map.get(action_data.get('action_type'), 'unknown')
                
                result = await self.powerautomation_core.drive_claudeditor(
                    registration_id=registration_id,
                    action="execute_command",
                    parameters={
                        "command": command,
                        "type": "quick_action",
                        "context": action_data
                    }
                )
                
                logger.info(f"⚡ 快速操作處理結果: {result}")
            
        except Exception as e:
            logger.error(f"❌ 處理快速操作失敗: {e}")
    
    async def handle_ai_mode_switched(self, websocket, client_id, data):
        """處理AI模式切換"""
        try:
            registration_id = data.get('registration_id')
            mode_data = data.get('data', {})
            
            logger.info(f"🤖 AI模式切換: {mode_data.get('new_mode')} by {registration_id}")
            
            # 記錄模式切換到PowerAutomation Core
            if self.powerautomation_core and registration_id:
                await self.powerautomation_core.drive_claudeditor(
                    registration_id=registration_id,
                    action="sync_memory",
                    parameters={
                        "sync_type": "from_claudeditor",
                        "memory_data": {
                            "memories": [{
                                "content": f"用戶切換AI模式到: {mode_data.get('new_mode')}",
                                "type": "user_interaction",
                                "tags": ["ai_mode", "user_preference"]
                            }]
                        }
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ 處理AI模式切換失敗: {e}")
    
    async def handle_command_result(self, websocket, client_id, data):
        """處理命令執行結果"""
        try:
            registration_id = data.get('registration_id')
            result_data = data.get('data', {})
            
            logger.info(f"📊 命令執行結果: {result_data.get('command')} - {'成功' if result_data.get('success') else '失敗'}")
            
            # 將結果記錄到PowerAutomation Core
            if self.powerautomation_core and registration_id:
                await self.powerautomation_core.drive_claudeditor(
                    registration_id=registration_id,
                    action="sync_memory",
                    parameters={
                        "sync_type": "from_claudeditor",
                        "memory_data": {
                            "memories": [{
                                "content": f"命令執行: {result_data.get('command')}\\n結果: {json.dumps(result_data.get('result', {}), ensure_ascii=False)}",
                                "type": "command_execution",
                                "tags": ["command_result", "automation"]
                            }]
                        }
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ 處理命令結果失敗: {e}")
    
    async def handle_heartbeat_response(self, websocket, client_id, data):
        """處理心跳響應"""
        try:
            registration_id = data.get('registration_id')
            heartbeat_data = data.get('data', {})
            
            # 更新客戶端狀態
            logger.debug(f"💓 收到心跳: {registration_id} - 對齊度: {heartbeat_data.get('alignment_score')}%")
            
        except Exception as e:
            logger.error(f"❌ 處理心跳響應失敗: {e}")
    
    async def handle_claude_code_command(self, websocket, client_id, data):
        """處理Claude Code Tool命令執行"""
        try:
            command_data = data.get('data', {})
            command = command_data.get('command', '')
            cwd = command_data.get('cwd', os.getcwd())
            
            logger.info(f"🔧 執行Claude Code命令: {command}")
            
            # 執行命令
            result = await self.execute_claude_code_command(command, cwd)
            
            # 發送結果回ClaudeEditor
            response = {
                'action': 'claude_code_command_result',
                'data': {
                    'command': command,
                    'result': result,
                    'timestamp': time.time()
                }
            }
            
            await websocket.send(json.dumps(response))
            
        except Exception as e:
            logger.error(f"❌ 執行Claude Code命令失敗: {e}")
    
    async def execute_claude_code_command(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """執行Claude Code Tool命令"""
        try:
            if cwd is None:
                cwd = os.getcwd()
            
            # 安全性檢查 - 只允許安全的命令
            safe_commands = ['ls', 'pwd', 'cat', 'grep', 'find', 'git', 'npm', 'python', 'node']
            
            command_parts = command.split()
            if not command_parts or command_parts[0] not in safe_commands:
                return {
                    'success': False,
                    'error': f'不允許的命令: {command_parts[0] if command_parts else "empty"}',
                    'stdout': '',
                    'stderr': ''
                }
            
            # 執行命令
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy()
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                'success': process.returncode == 0,
                'returncode': process.returncode,
                'stdout': stdout.decode('utf-8', errors='ignore'),
                'stderr': stderr.decode('utf-8', errors='ignore'),
                'command': command,
                'cwd': cwd
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': '',
                'command': command,
                'cwd': cwd or os.getcwd()
            }
    
    async def broadcast_to_claudeditors(self, message: Dict[str, Any]):
        """廣播消息到所有ClaudeEditor客戶端"""
        if not self.claudeditor_clients:
            return
        
        message_str = json.dumps(message)
        
        # 同時發送到所有ClaudeEditor客戶端
        tasks = []
        for registration_id, websocket in self.claudeditor_clients.items():
            try:
                tasks.append(websocket.send(message_str))
            except Exception as e:
                logger.error(f"❌ 廣播到{registration_id}失敗: {e}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_server(self):
        """停止WebSocket服務器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        if self.powerautomation_core:
            await self.powerautomation_core.shutdown()
        
        logger.info("🔄 PowerAutomation WebSocket服務器已停止")

async def main():
    """主函數"""
    server = PowerAutomationWebSocketServer(host='localhost', port=8765)
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("🔄 收到停止信號，正在關閉服務器...")
        await server.stop_server()
    except Exception as e:
        logger.error(f"❌ 服務器運行錯誤: {e}")
        await server.stop_server()
        raise

if __name__ == "__main__":
    print("🚀 啟動PowerAutomation WebSocket服務器...")
    print("🎯 這將允許PowerAutomation Core完全驅動ClaudeEditor")
    print("📡 WebSocket地址: ws://localhost:8765")
    print("⚡ 支持Claude Router MCP雙向通信")
    print("🔧 支持命令執行: ClaudeEditor WebUI → Claude Code Tool")
    print("📋 按Ctrl+C停止服務器")
    print("-" * 60)
    
    asyncio.run(main())