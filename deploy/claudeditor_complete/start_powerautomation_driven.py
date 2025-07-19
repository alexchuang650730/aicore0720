#!/usr/bin/env python3
"""
PowerAutomation驅動ClaudeEditor啟動腳本
一鍵啟動完整的PowerAutomation + ClaudeEditor集成系統
"""

import asyncio
import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path
import webbrowser
import http.server
import socketserver
from typing import List, Optional

class PowerAutomationSystem:
    """PowerAutomation系統管理器"""
    
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.processes: List[subprocess.Popen] = []
        self.web_server = None
        self.web_server_thread = None
        self.websocket_process = None
        
        # 配置
        self.web_port = 8080
        self.websocket_port = 8765
        
        print("🚀 PowerAutomation驅動ClaudeEditor系統初始化")
    
    def start_web_server(self):
        """啟動Web服務器為ClaudeEditor提供HTTP服務"""
        try:
            os.chdir(self.current_dir)
            
            class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def log_message(self, format, *args):
                    # 靜默日誌，避免過多輸出
                    pass
                
                def end_headers(self):
                    # 添加CORS頭以支持WebSocket連接
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    super().end_headers()
            
            self.web_server = socketserver.TCPServer(
                ("", self.web_port), 
                CustomHTTPRequestHandler
            )
            
            def run_server():
                print(f"🌐 Web服務器啟動: http://localhost:{self.web_port}")
                self.web_server.serve_forever()
            
            self.web_server_thread = threading.Thread(target=run_server, daemon=True)
            self.web_server_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Web服務器啟動失敗: {e}")
            return False
    
    def start_websocket_server(self):
        """啟動PowerAutomation WebSocket服務器"""
        try:
            websocket_script = self.current_dir / "powerautomation_websocket_server.py"
            
            if not websocket_script.exists():
                print(f"❌ WebSocket服務器腳本不存在: {websocket_script}")
                return False
            
            print("🔌 啟動PowerAutomation WebSocket服務器...")
            
            self.websocket_process = subprocess.Popen(
                [sys.executable, str(websocket_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 在背景線程中處理WebSocket服務器輸出
            def handle_websocket_output():
                for line in self.websocket_process.stdout:
                    print(f"[WebSocket] {line.rstrip()}")
            
            websocket_thread = threading.Thread(target=handle_websocket_output, daemon=True)
            websocket_thread.start()
            
            # 等待WebSocket服務器啟動
            time.sleep(2)
            
            if self.websocket_process.poll() is None:
                print(f"✅ PowerAutomation WebSocket服務器已啟動: ws://localhost:{self.websocket_port}")
                return True
            else:
                print("❌ PowerAutomation WebSocket服務器啟動失敗")
                return False
                
        except Exception as e:
            print(f"❌ WebSocket服務器啟動失敗: {e}")
            return False
    
    def open_claudeditor(self):
        """在瀏覽器中打開ClaudeEditor"""
        try:
            claudeditor_url = f"http://localhost:{self.web_port}/index.html"
            
            print(f"🌐 正在打開ClaudeEditor: {claudeditor_url}")
            
            # 等待Web服務器完全啟動
            time.sleep(1)
            
            # 在默認瀏覽器中打開
            webbrowser.open(claudeditor_url)
            
            return True
            
        except Exception as e:
            print(f"❌ 打開ClaudeEditor失敗: {e}")
            return False
    
    def show_system_status(self):
        """顯示系統狀態"""
        print("\n" + "="*80)
        print("🎯 PowerAutomation驅動ClaudeEditor系統狀態")
        print("="*80)
        print(f"📱 ClaudeEditor Web界面: http://localhost:{self.web_port}/index.html")
        print(f"🔌 PowerAutomation WebSocket: ws://localhost:{self.websocket_port}")
        print(f"🚀 系統模式: PowerAutomation Core完全驅動ClaudeEditor")
        print("="*80)
        print("✨ 功能特性:")
        print("  🎯 六大工作流自動驅動")
        print("  🤖 Claude + K2雙AI模式")
        print("  💰 K2成本優化 (2元→8元)")
        print("  🧠 Memory RAG智能記憶")
        print("  ⚡ 實時目標對齊監控")
        print("  🔄 PowerAutomation Core雙向通信")
        print("  🔧 Claude Code Tool命令執行")
        print("="*80)
        print("💡 使用說明:")
        print("  1. ClaudeEditor會自動連接到PowerAutomation Core")
        print("  2. 所有操作都會被PowerAutomation Core驅動和記錄")
        print("  3. 工作流會根據目標自動調整和優化")
        print("  4. 實時監控確保開發不偏離目標")
        print("="*80)
        print("🔴 按Ctrl+C停止系統")
        print("="*80)
    
    def start_system(self):
        """啟動完整系統"""
        try:
            print("🚀 正在啟動PowerAutomation驅動ClaudeEditor系統...")
            print("⚡ 這可能需要幾秒鐘時間...")
            
            # 1. 啟動Web服務器
            if not self.start_web_server():
                print("❌ Web服務器啟動失敗，系統無法啟動")
                return False
            
            # 2. 啟動WebSocket服務器
            if not self.start_websocket_server():
                print("❌ WebSocket服務器啟動失敗，系統無法完全啟動")
                print("💡 ClaudeEditor仍可獨立使用，但無PowerAutomation驅動功能")
            
            # 3. 打開ClaudeEditor
            self.open_claudeditor()
            
            # 4. 顯示系統狀態
            self.show_system_status()
            
            return True
            
        except Exception as e:
            print(f"❌ 系統啟動失敗: {e}")
            return False
    
    def stop_system(self):
        """停止系統"""
        print("\n🔄 正在停止PowerAutomation驅動ClaudeEditor系統...")
        
        # 停止WebSocket服務器
        if self.websocket_process:
            try:
                self.websocket_process.terminate()
                self.websocket_process.wait(timeout=5)
                print("✅ PowerAutomation WebSocket服務器已停止")
            except subprocess.TimeoutExpired:
                self.websocket_process.kill()
                print("🔥 強制停止PowerAutomation WebSocket服務器")
            except Exception as e:
                print(f"⚠️ 停止WebSocket服務器時出錯: {e}")
        
        # 停止Web服務器
        if self.web_server:
            try:
                self.web_server.shutdown()
                print("✅ Web服務器已停止")
            except Exception as e:
                print(f"⚠️ 停止Web服務器時出錯: {e}")
        
        # 停止所有子進程
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass
        
        print("✅ PowerAutomation驅動ClaudeEditor系統已完全停止")
        print("👋 感謝使用PowerAutomation！")
    
    def run(self):
        """運行系統主循環"""
        try:
            if not self.start_system():
                return 1
            
            # 等待中斷信號
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ 系統運行錯誤: {e}")
            return 1
        finally:
            self.stop_system()
        
        return 0

def signal_handler(signum, frame):
    """信號處理器"""
    print(f"\n🔴 收到停止信號 ({signum})")
    sys.exit(0)

def main():
    """主函數"""
    # 註冊信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🎯 PowerAutomation驅動ClaudeEditor")
    print("💫 讓開發永不偏離目標的智能系統")
    print("-" * 60)
    
    # 檢查必要文件
    current_dir = Path(__file__).parent
    required_files = [
        "index.html",
        "powerautomation_driver_api.js",
        "powerautomation_websocket_server.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        print("💡 請確保所有必要文件都在同一目錄下")
        return 1
    
    # 啟動系統
    system = PowerAutomationSystem()
    return system.run()

if __name__ == "__main__":
    sys.exit(main())