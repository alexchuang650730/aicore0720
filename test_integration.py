#!/usr/bin/env python3
"""
PowerAutomation Core 和 ClaudeEditor 集成測試
驗證 Core 能否正確驅動 ClaudeEditor
"""

import asyncio
import json
import time
import subprocess
import sys
from pathlib import Path

# 設置項目根目錄
project_root = Path(__file__).parent

class IntegrationTester:
    def __init__(self):
        self.test_results = []
        self.processes = {}
        
    def log(self, message, test_name=None):
        """記錄測試結果"""
        timestamp = time.strftime("%H:%M:%S")
        if test_name:
            print(f"[{timestamp}] {test_name}: {message}")
        else:
            print(f"[{timestamp}] {message}")
    
    def add_result(self, test_name, success, message):
        """添加測試結果"""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': time.time()
        })
    
    async def test_core_startup(self):
        """測試 PowerAutomation Core 啟動"""
        test_name = "Core 啟動測試"
        self.log("測試 PowerAutomation Core 啟動", test_name)
        
        try:
            # 檢查 Core 文件是否存在
            core_file = project_root / "core" / "powerautomation_core.py"
            if not core_file.exists():
                self.add_result(test_name, False, "Core 文件不存在")
                return False
                
            # 啟動 Core（非阻塞）
            core_process = subprocess.Popen([
                sys.executable, str(core_file)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['core'] = core_process
            
            # 等待啟動
            await asyncio.sleep(3)
            
            # 檢查進程是否仍在運行
            if core_process.poll() is None:
                self.add_result(test_name, True, "Core 啟動成功")
                return True
            else:
                stdout, stderr = core_process.communicate()
                self.add_result(test_name, False, f"Core 啟動失敗: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.add_result(test_name, False, f"Core 啟動異常: {str(e)}")
            return False
    
    async def test_claudeditor_startup(self):
        """測試 ClaudeEditor 啟動"""
        test_name = "ClaudeEditor 啟動測試"
        self.log("測試 ClaudeEditor 啟動", test_name)
        
        try:
            # 檢查 ClaudeEditor 目錄
            claudeditor_dir = project_root / "claudeditor"
            if not claudeditor_dir.exists():
                self.add_result(test_name, False, "ClaudeEditor 目錄不存在")
                return False
            
            # 檢查 package.json
            package_json = claudeditor_dir / "package.json"
            if not package_json.exists():
                self.add_result(test_name, False, "package.json 不存在")
                return False
            
            # 啟動 ClaudeEditor 開發服務器
            claudeditor_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=claudeditor_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['claudeditor'] = claudeditor_process
            
            # 等待啟動
            await asyncio.sleep(5)
            
            # 檢查進程是否仍在運行
            if claudeditor_process.poll() is None:
                self.add_result(test_name, True, "ClaudeEditor 啟動成功")
                return True
            else:
                stdout, stderr = claudeditor_process.communicate()
                self.add_result(test_name, False, f"ClaudeEditor 啟動失敗: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.add_result(test_name, False, f"ClaudeEditor 啟動異常: {str(e)}")
            return False
    
    async def test_websocket_connection(self):
        """測試 WebSocket 連接"""
        test_name = "WebSocket 連接測試"
        self.log("測試 WebSocket 連接", test_name)
        
        try:
            import websockets
            
            # 嘗試連接 Core WebSocket
            uri = "ws://localhost:8081"
            async with websockets.connect(uri) as websocket:
                # 發送註冊消息
                register_message = {
                    "action": "register_claudeditor",
                    "params": {
                        "name": "TestClaudeEditor",
                        "version": "test",
                        "host": "localhost",
                        "port": 3000
                    }
                }
                
                await websocket.send(json.dumps(register_message))
                
                # 等待響應
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("status") == "success":
                    self.add_result(test_name, True, "WebSocket 連接和註冊成功")
                    return True
                else:
                    self.add_result(test_name, False, f"註冊失敗: {response_data}")
                    return False
                    
        except ImportError:
            self.add_result(test_name, False, "缺少 websockets 庫")
            return False
        except Exception as e:
            self.add_result(test_name, False, f"WebSocket 連接失敗: {str(e)}")
            return False
    
    async def test_core_command_execution(self):
        """測試 Core 命令執行"""
        test_name = "Core 命令執行測試"
        self.log("測試 Core 命令執行", test_name)
        
        try:
            import websockets
            
            uri = "ws://localhost:8081"
            async with websockets.connect(uri) as websocket:
                # 首先註冊
                register_message = {
                    "action": "register_claudeditor",
                    "params": {
                        "name": "TestClaudeEditor",
                        "version": "test"
                    }
                }
                await websocket.send(json.dumps(register_message))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if response_data.get("status") != "success":
                    self.add_result(test_name, False, "註冊失敗")
                    return False
                
                claudeditor_id = response_data.get("claudeditor_id")
                
                # 發送驅動命令
                drive_command = {
                    "action": "drive_claudeditor",
                    "params": {
                        "claudeditor_id": claudeditor_id,
                        "command": "open_file",
                        "command_params": {
                            "filePath": "/test/file.py"
                        }
                    }
                }
                
                await websocket.send(json.dumps(drive_command))
                
                # 等待命令響應
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("status") == "success":
                    self.add_result(test_name, True, "Core 命令執行成功")
                    return True
                else:
                    self.add_result(test_name, False, f"命令執行失敗: {response_data}")
                    return False
                    
        except Exception as e:
            self.add_result(test_name, False, f"命令執行測試失敗: {str(e)}")
            return False
    
    async def test_file_operations(self):
        """測試文件操作"""
        test_name = "文件操作測試"
        self.log("測試文件操作", test_name)
        
        try:
            # 檢查關鍵文件是否存在
            required_files = [
                "core/powerautomation_core.py",
                "claudeditor/src/App_CoreDriven.jsx", 
                "claudeditor/src/services/CoreConnector.js",
                "claudeditor/package.json"
            ]
            
            missing_files = []
            for file_path in required_files:
                if not (project_root / file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                self.add_result(test_name, False, f"缺少文件: {', '.join(missing_files)}")
                return False
            else:
                self.add_result(test_name, True, "所有必需文件存在")
                return True
                
        except Exception as e:
            self.add_result(test_name, False, f"文件操作測試失敗: {str(e)}")
            return False
    
    def cleanup(self):
        """清理測試進程"""
        self.log("清理測試進程")
        
        for name, process in self.processes.items():
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    self.log(f"已終止 {name} 進程")
                except:
                    process.kill()
                    self.log(f"已強制終止 {name} 進程")
    
    def print_results(self):
        """打印測試結果"""
        print("\n" + "="*60)
        print("🧪 PowerAutomation 集成測試結果")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['message']}")
            
            if result['success']:
                passed += 1
            else:
                failed += 1
        
        print(f"\n📊 總計: {passed} 通過, {failed} 失敗")
        
        if failed == 0:
            print("🎉 所有測試通過！PowerAutomation Core 和 ClaudeEditor 集成正常")
        else:
            print("⚠️  部分測試失敗，請檢查配置和依賴")
        
        return failed == 0

async def main():
    """主測試函數"""
    tester = IntegrationTester()
    
    try:
        print("🚀 開始 PowerAutomation 集成測試")
        print("="*60)
        
        # 運行測試
        await tester.test_file_operations()
        await tester.test_core_startup()
        await tester.test_claudeditor_startup()
        
        # 等待服務完全啟動
        await asyncio.sleep(3)
        
        await tester.test_websocket_connection()
        await tester.test_core_command_execution()
        
        # 打印結果
        success = tester.print_results()
        
        if success:
            print("\n💡 下一步:")
            print("1. 運行 ./launch.sh 啟動完整系統")
            print("2. 訪問 http://localhost:8000 測試 ClaudeEditor")
            print("3. 使用 Claude Code Tool 測試 K2 路由")
        
    except KeyboardInterrupt:
        print("\n❌ 測試被中斷")
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())