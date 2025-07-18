#!/usr/bin/env python3
"""
ClaudeEditor 和 Claude Code Tool 雙向溝通測試
驗證功能完整性和無縫集成
"""

import asyncio
import json
import time
import subprocess
import threading
import websockets
import requests
from pathlib import Path
import sys

class BidirectionalCommunicationTester:
    def __init__(self):
        self.test_results = []
        self.core_process = None
        self.claudeditor_process = None
        self.ws_connection = None
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def add_result(self, test_name, success, message, details=None):
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': time.time()
        })
    
    async def setup_environment(self):
        """設置測試環境"""
        self.log("設置測試環境")
        
        # 1. 啟動 PowerAutomation Core
        try:
            self.log("啟動 PowerAutomation Core")
            self.core_process = subprocess.Popen([
                sys.executable, "core/powerautomation_core.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待 Core 啟動
            await asyncio.sleep(5)
            
            if self.core_process.poll() is None:
                self.log("PowerAutomation Core 啟動成功")
            else:
                self.log("PowerAutomation Core 啟動失敗", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"啟動 Core 失敗: {e}", "ERROR")
            return False
        
        # 2. 啟動 ClaudeEditor
        try:
            self.log("啟動 ClaudeEditor")
            self.claudeditor_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd="claudeditor", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待 ClaudeEditor 啟動
            await asyncio.sleep(8)
            
            if self.claudeditor_process.poll() is None:
                self.log("ClaudeEditor 啟動成功")
            else:
                self.log("ClaudeEditor 啟動失敗", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"啟動 ClaudeEditor 失敗: {e}", "ERROR")
            return False
        
        return True
    
    async def test_websocket_connection(self):
        """測試 WebSocket 連接"""
        test_name = "WebSocket 連接測試"
        
        try:
            # 連接到 PowerAutomation Core
            self.ws_connection = await websockets.connect("ws://localhost:8081")
            
            # 發送註冊消息
            register_msg = {
                "action": "register_claudeditor",
                "params": {
                    "name": "TestClaudeEditor",
                    "version": "4.6.9.1",
                    "host": "localhost",
                    "port": 8000
                }
            }
            
            await self.ws_connection.send(json.dumps(register_msg))
            
            # 等待響應
            response = await asyncio.wait_for(self.ws_connection.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get("status") == "success":
                self.claudeditor_id = response_data.get("claudeditor_id")
                self.add_result(test_name, True, f"WebSocket 連接成功，ID: {self.claudeditor_id}")
                return True
            else:
                self.add_result(test_name, False, f"註冊失敗: {response_data}")
                return False
                
        except Exception as e:
            self.add_result(test_name, False, f"WebSocket 連接失敗: {e}")
            return False
    
    async def test_claude_code_tool_commands(self):
        """測試 Claude Code Tool 命令完整性"""
        test_name = "Claude Code Tool 命令完整性測試"
        
        if not self.ws_connection:
            self.add_result(test_name, False, "WebSocket 未連接")
            return False
        
        # 測試常見的 Claude Code Tool 命令
        test_commands = [
            {
                "command": "read_file",
                "description": "讀取文件",
                "params": {"file_path": "test.py"}
            },
            {
                "command": "write_file", 
                "description": "寫入文件",
                "params": {"file_path": "output.py", "content": "print('Hello World')"}
            },
            {
                "command": "list_files",
                "description": "列出文件",
                "params": {"directory": "."}
            },
            {
                "command": "create_project",
                "description": "創建項目",
                "params": {"project_name": "test_project", "template": "python"}
            },
            {
                "command": "run_command",
                "description": "執行命令",
                "params": {"command": "ls -la"}
            }
        ]
        
        successful_commands = 0
        command_results = []
        
        for cmd in test_commands:
            try:
                # 發送命令到 ClaudeEditor
                drive_msg = {
                    "action": "drive_claudeditor",
                    "params": {
                        "claudeditor_id": self.claudeditor_id,
                        "command": cmd["command"],
                        "command_params": cmd["params"]
                    }
                }
                
                await self.ws_connection.send(json.dumps(drive_msg))
                
                # 等待響應
                response = await asyncio.wait_for(self.ws_connection.recv(), timeout=3.0)
                response_data = json.loads(response)
                
                if response_data.get("status") == "success":
                    successful_commands += 1
                    command_results.append({
                        "command": cmd["command"],
                        "description": cmd["description"],
                        "success": True,
                        "response": response_data
                    })
                else:
                    command_results.append({
                        "command": cmd["command"],
                        "description": cmd["description"],
                        "success": False,
                        "error": response_data.get("message", "Unknown error")
                    })
                    
            except Exception as e:
                command_results.append({
                    "command": cmd["command"],
                    "description": cmd["description"],
                    "success": False,
                    "error": str(e)
                })
        
        success_rate = successful_commands / len(test_commands)
        
        if success_rate >= 0.8:
            self.add_result(test_name, True, f"命令完整性: {success_rate:.1%} ({successful_commands}/{len(test_commands)})", command_results)
            return True
        else:
            self.add_result(test_name, False, f"命令完整性不足: {success_rate:.1%}", command_results)
            return False
    
    async def test_claudeditor_to_claude_code_sync(self):
        """測試 ClaudeEditor 到 Claude Code Tool 的同步"""
        test_name = "ClaudeEditor -> Claude Code Tool 同步測試"
        
        if not self.ws_connection:
            self.add_result(test_name, False, "WebSocket 未連接")
            return False
        
        try:
            # 模擬在 ClaudeEditor 中進行的操作
            operations = [
                {
                    "type": "file_edit",
                    "action": "在 ClaudeEditor 中編輯文件",
                    "data": {
                        "file_path": "sync_test.py",
                        "content": "# 這是通過 ClaudeEditor 編輯的文件\nprint('Hello from ClaudeEditor')"
                    }
                },
                {
                    "type": "project_change",
                    "action": "在 ClaudeEditor 中切換項目",
                    "data": {
                        "project_name": "sync_test_project"
                    }
                }
            ]
            
            sync_results = []
            
            for op in operations:
                # 發送操作到 Core
                sync_msg = {
                    "action": "sync_to_claude_code",
                    "params": {
                        "claudeditor_id": self.claudeditor_id,
                        "operation": op["type"],
                        "data": op["data"]
                    }
                }
                
                await self.ws_connection.send(json.dumps(sync_msg))
                
                # 等待同步結果
                response = await asyncio.wait_for(self.ws_connection.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                sync_results.append({
                    "operation": op["action"],
                    "success": response_data.get("status") == "success",
                    "response": response_data
                })
            
            successful_syncs = sum(1 for r in sync_results if r["success"])
            sync_rate = successful_syncs / len(operations)
            
            if sync_rate >= 0.8:
                self.add_result(test_name, True, f"同步成功率: {sync_rate:.1%} ({successful_syncs}/{len(operations)})", sync_results)
                return True
            else:
                self.add_result(test_name, False, f"同步成功率不足: {sync_rate:.1%}", sync_results)
                return False
                
        except Exception as e:
            self.add_result(test_name, False, f"同步測試失敗: {e}")
            return False
    
    async def test_claude_code_to_claudeditor_sync(self):
        """測試 Claude Code Tool 到 ClaudeEditor 的同步"""
        test_name = "Claude Code Tool -> ClaudeEditor 同步測試"
        
        if not self.ws_connection:
            self.add_result(test_name, False, "WebSocket 未連接")
            return False
        
        try:
            # 模擬 Claude Code Tool 的操作
            claude_code_operations = [
                {
                    "command": "create_file",
                    "description": "Claude Code Tool 創建文件",
                    "params": {
                        "file_path": "claude_code_test.py",
                        "content": "# 這是通過 Claude Code Tool 創建的文件\nprint('Hello from Claude Code Tool')"
                    }
                },
                {
                    "command": "open_file",
                    "description": "Claude Code Tool 打開文件",
                    "params": {
                        "file_path": "claude_code_test.py"
                    }
                }
            ]
            
            sync_results = []
            
            for op in claude_code_operations:
                # 通過 Core 路由到 ClaudeEditor
                route_msg = {
                    "action": "integrate_with_claude_code",
                    "params": {
                        "claudeditor_id": self.claudeditor_id,
                        "claude_command": op["command"],
                        "params": op["params"]
                    }
                }
                
                await self.ws_connection.send(json.dumps(route_msg))
                
                # 等待 ClaudeEditor 響應
                response = await asyncio.wait_for(self.ws_connection.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                sync_results.append({
                    "operation": op["description"],
                    "success": response_data.get("status") == "success",
                    "response": response_data
                })
            
            successful_syncs = sum(1 for r in sync_results if r["success"])
            sync_rate = successful_syncs / len(claude_code_operations)
            
            if sync_rate >= 0.8:
                self.add_result(test_name, True, f"反向同步成功率: {sync_rate:.1%} ({successful_syncs}/{len(claude_code_operations)})", sync_results)
                return True
            else:
                self.add_result(test_name, False, f"反向同步成功率不足: {sync_rate:.1%}", sync_results)
                return False
                
        except Exception as e:
            self.add_result(test_name, False, f"反向同步測試失敗: {e}")
            return False
    
    async def test_real_time_collaboration(self):
        """測試實時協作功能"""
        test_name = "實時協作功能測試"
        
        if not self.ws_connection:
            self.add_result(test_name, False, "WebSocket 未連接")
            return False
        
        try:
            # 模擬多個編輯器同時編輯
            collaboration_scenarios = [
                {
                    "action": "simultaneous_edit",
                    "description": "同時編輯同一文件",
                    "data": {
                        "file_path": "collaboration_test.py",
                        "edits": [
                            {"line": 1, "content": "# 編輯者 1 的修改"},
                            {"line": 2, "content": "# 編輯者 2 的修改"}
                        ]
                    }
                },
                {
                    "action": "conflict_resolution",
                    "description": "解決編輯衝突",
                    "data": {
                        "file_path": "collaboration_test.py",
                        "conflicts": [
                            {"line": 1, "version_a": "print('Version A')", "version_b": "print('Version B')"}
                        ]
                    }
                }
            ]
            
            collaboration_results = []
            
            for scenario in collaboration_scenarios:
                # 發送協作場景測試
                collab_msg = {
                    "action": "test_collaboration",
                    "params": {
                        "claudeditor_id": self.claudeditor_id,
                        "scenario": scenario["action"],
                        "data": scenario["data"]
                    }
                }
                
                await self.ws_connection.send(json.dumps(collab_msg))
                
                # 等待協作結果
                response = await asyncio.wait_for(self.ws_connection.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                collaboration_results.append({
                    "scenario": scenario["description"],
                    "success": response_data.get("status") == "success",
                    "response": response_data
                })
            
            successful_collaborations = sum(1 for r in collaboration_results if r["success"])
            collaboration_rate = successful_collaborations / len(collaboration_scenarios)
            
            if collaboration_rate >= 0.7:
                self.add_result(test_name, True, f"協作功能: {collaboration_rate:.1%} ({successful_collaborations}/{len(collaboration_scenarios)})", collaboration_results)
                return True
            else:
                self.add_result(test_name, False, f"協作功能不足: {collaboration_rate:.1%}", collaboration_results)
                return False
                
        except Exception as e:
            self.add_result(test_name, False, f"協作測試失敗: {e}")
            return False
    
    async def test_performance_metrics(self):
        """測試性能指標"""
        test_name = "性能指標測試"
        
        if not self.ws_connection:
            self.add_result(test_name, False, "WebSocket 未連接")
            return False
        
        try:
            # 性能測試場景
            performance_tests = [
                {
                    "name": "命令響應時間",
                    "command": "read_file",
                    "params": {"file_path": "test.py"},
                    "expected_time": 1.0  # 1秒內響應
                },
                {
                    "name": "文件操作延遲",
                    "command": "write_file",
                    "params": {"file_path": "perf_test.py", "content": "print('Performance test')"},
                    "expected_time": 2.0  # 2秒內完成
                },
                {
                    "name": "同步延遲",
                    "command": "sync_state",
                    "params": {"force": True},
                    "expected_time": 0.5  # 0.5秒內同步
                }
            ]
            
            performance_results = []
            
            for test in performance_tests:
                start_time = time.time()
                
                # 發送性能測試命令
                perf_msg = {
                    "action": "drive_claudeditor",
                    "params": {
                        "claudeditor_id": self.claudeditor_id,
                        "command": test["command"],
                        "command_params": test["params"]
                    }
                }
                
                await self.ws_connection.send(json.dumps(perf_msg))
                
                # 等待響應並測量時間
                response = await asyncio.wait_for(self.ws_connection.recv(), timeout=5.0)
                response_time = time.time() - start_time
                
                performance_results.append({
                    "test": test["name"],
                    "response_time": response_time,
                    "expected_time": test["expected_time"],
                    "success": response_time <= test["expected_time"]
                })
            
            passed_tests = sum(1 for r in performance_results if r["success"])
            performance_rate = passed_tests / len(performance_tests)
            
            if performance_rate >= 0.8:
                self.add_result(test_name, True, f"性能指標: {performance_rate:.1%} ({passed_tests}/{len(performance_tests)})", performance_results)
                return True
            else:
                self.add_result(test_name, False, f"性能指標不符合要求: {performance_rate:.1%}", performance_results)
                return False
                
        except Exception as e:
            self.add_result(test_name, False, f"性能測試失敗: {e}")
            return False
    
    async def test_error_handling(self):
        """測試錯誤處理"""
        test_name = "錯誤處理測試"
        
        if not self.ws_connection:
            self.add_result(test_name, False, "WebSocket 未連接")
            return False
        
        try:
            # 錯誤場景測試
            error_scenarios = [
                {
                    "name": "無效命令",
                    "command": "invalid_command",
                    "params": {},
                    "expected_error": True
                },
                {
                    "name": "文件不存在",
                    "command": "read_file",
                    "params": {"file_path": "non_existent_file.py"},
                    "expected_error": True
                },
                {
                    "name": "權限錯誤",
                    "command": "write_file",
                    "params": {"file_path": "/root/restricted_file.py", "content": "test"},
                    "expected_error": True
                }
            ]
            
            error_handling_results = []
            
            for scenario in error_scenarios:
                # 發送錯誤場景
                error_msg = {
                    "action": "drive_claudeditor",
                    "params": {
                        "claudeditor_id": self.claudeditor_id,
                        "command": scenario["command"],
                        "command_params": scenario["params"]
                    }
                }
                
                await self.ws_connection.send(json.dumps(error_msg))
                
                # 等待錯誤響應
                response = await asyncio.wait_for(self.ws_connection.recv(), timeout=3.0)
                response_data = json.loads(response)
                
                # 檢查是否正確處理錯誤
                has_error = response_data.get("status") == "error" or "error" in response_data
                correct_handling = has_error == scenario["expected_error"]
                
                error_handling_results.append({
                    "scenario": scenario["name"],
                    "expected_error": scenario["expected_error"],
                    "got_error": has_error,
                    "correct_handling": correct_handling
                })
            
            correct_handlings = sum(1 for r in error_handling_results if r["correct_handling"])
            error_handling_rate = correct_handlings / len(error_scenarios)
            
            if error_handling_rate >= 0.8:
                self.add_result(test_name, True, f"錯誤處理: {error_handling_rate:.1%} ({correct_handlings}/{len(error_scenarios)})", error_handling_results)
                return True
            else:
                self.add_result(test_name, False, f"錯誤處理不足: {error_handling_rate:.1%}", error_handling_results)
                return False
                
        except Exception as e:
            self.add_result(test_name, False, f"錯誤處理測試失敗: {e}")
            return False
    
    async def cleanup(self):
        """清理測試環境"""
        self.log("清理測試環境")
        
        if self.ws_connection:
            await self.ws_connection.close()
        
        if self.claudeditor_process and self.claudeditor_process.poll() is None:
            self.claudeditor_process.terminate()
            self.claudeditor_process.wait()
            self.log("ClaudeEditor 進程已終止")
        
        if self.core_process and self.core_process.poll() is None:
            self.core_process.terminate()
            self.core_process.wait()
            self.log("PowerAutomation Core 進程已終止")
    
    def print_comprehensive_results(self):
        """打印詳細測試結果"""
        print("\n" + "="*70)
        print("🔄 ClaudeEditor ↔ Claude Code Tool 雙向溝通測試結果")
        print("="*70)
        
        passed = 0
        failed = 0
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {result['test']}")
            print(f"     └─ {result['message']}")
            
            if result['success']:
                passed += 1
            else:
                failed += 1
        
        print(f"\n📊 測試總結: {passed} 通過, {failed} 失敗")
        
        # 功能完整性評估
        print("\n🎯 功能完整性評估:")
        
        # 雙向溝通測試
        sync_tests = [r for r in self.test_results if "同步" in r['test']]
        if sync_tests:
            sync_passed = sum(1 for r in sync_tests if r['success'])
            print(f"   雙向同步: {sync_passed}/{len(sync_tests)} 通過")
        
        # 命令完整性測試
        command_tests = [r for r in self.test_results if "命令" in r['test']]
        if command_tests:
            command_passed = sum(1 for r in command_tests if r['success'])
            print(f"   命令完整性: {command_passed}/{len(command_tests)} 通過")
        
        # 性能測試
        perf_tests = [r for r in self.test_results if "性能" in r['test']]
        if perf_tests:
            perf_passed = sum(1 for r in perf_tests if r['success'])
            print(f"   性能指標: {perf_passed}/{len(perf_tests)} 通過")
        
        # 最終結論
        print("\n🎯 最終結論:")
        if failed == 0:
            print("   ✅ 所有功能測試通過！")
            print("   ✅ ClaudeEditor 和 Claude Code Tool 可以完美協作")
            print("   ✅ 雙向溝通功能完整，性能符合要求")
            print("   ✅ 系統已就緒，可以投入使用")
        else:
            print("   ❌ 部分功能存在問題：")
            failed_tests = [r for r in self.test_results if not r['success']]
            for test in failed_tests:
                print(f"      - {test['test']}")
            print("   ⚠️  建議修復後再進行部署")
        
        return failed == 0

async def main():
    """主測試函數"""
    tester = BidirectionalCommunicationTester()
    
    try:
        print("🚀 開始 ClaudeEditor ↔ Claude Code Tool 雙向溝通測試")
        print("="*70)
        
        # 設置測試環境
        if not await tester.setup_environment():
            print("❌ 測試環境設置失敗")
            return
        
        # 執行測試
        await tester.test_websocket_connection()
        await tester.test_claude_code_tool_commands()
        await tester.test_claudeditor_to_claude_code_sync()
        await tester.test_claude_code_to_claudeditor_sync()
        await tester.test_real_time_collaboration()
        await tester.test_performance_metrics()
        await tester.test_error_handling()
        
        # 打印結果
        success = tester.print_comprehensive_results()
        
        if success:
            print("\n🎉 雙向溝通測試全部通過！")
            print("💡 PowerAutomation 系統已準備就緒")
        else:
            print("\n⚠️  部分測試失敗，需要修復")
        
    except KeyboardInterrupt:
        print("\n❌ 測試被用戶中斷")
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())