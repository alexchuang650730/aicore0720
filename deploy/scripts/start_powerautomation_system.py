#!/usr/bin/env python3
"""
PowerAutomation 完整系統啟動腳本
7/30上線版本 - 集成所有核心功能
"""

import asyncio
import subprocess
import time
import os
import sys
import logging
from pathlib import Path
import json
import webbrowser
from typing import Dict, Any

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PowerAutomationSystemLauncher:
    """PowerAutomation系統啟動器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        self.config = {
            "core_port": 8080,
            "claudeditor_port": 8000,
            "websocket_port": 8081,
            "membership_api_port": 8082,
            "mcp_server_port": 8765
        }
        
        # 系統組件配置
        self.components = {
            "membership_api": {
                "name": "會員積分系統API",
                "script": "claudeditor/backend/membership_api.py",
                "port": 8082,
                "health_endpoint": "/api/system/config"
            },
            "powerautomation_core": {
                "name": "PowerAutomation Core",
                "script": "core/powerautomation_core.py",
                "port": 8080,
                "health_endpoint": "/health"
            },
            "claudeditor_frontend": {
                "name": "ClaudeEditor Frontend",
                "command": ["npm", "run", "dev"],
                "cwd": "claudeditor",
                "port": 8000,
                "health_endpoint": "/"
            },
            "mcp_server": {
                "name": "MCP服務器",
                "script": "mcp_server/main.py",
                "port": 8765,
                "health_endpoint": "/health"
            }
        }
    
    async def check_dependencies(self) -> Dict[str, bool]:
        """檢查系統依賴"""
        logger.info("🔍 檢查系統依賴...")
        
        dependencies = {
            "python": True,
            "node": True,
            "npm": True,
            "virtual_env": True,
            "required_packages": True
        }
        
        # 檢查Python
        try:
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Python: {result.stdout.strip()}")
            else:
                dependencies["python"] = False
                logger.error("❌ Python不可用")
        except:
            dependencies["python"] = False
            logger.error("❌ Python不可用")
        
        # 檢查Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Node.js: {result.stdout.strip()}")
            else:
                dependencies["node"] = False
                logger.error("❌ Node.js不可用")
        except:
            dependencies["node"] = False
            logger.error("❌ Node.js不可用")
        
        # 檢查npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ npm: {result.stdout.strip()}")
            else:
                dependencies["npm"] = False
                logger.error("❌ npm不可用")
        except:
            dependencies["npm"] = False
            logger.error("❌ npm不可用")
        
        # 檢查虛擬環境
        venv_path = self.project_root / "venv"
        if venv_path.exists():
            logger.info("✅ 虛擬環境已存在")
        else:
            dependencies["virtual_env"] = False
            logger.warning("⚠️ 虛擬環境不存在，將自動創建")
        
        return dependencies
    
    async def setup_environment(self):
        """設置環境"""
        logger.info("🔧 設置開發環境...")
        
        # 創建虛擬環境（如果不存在）
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            logger.info("創建Python虛擬環境...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=self.project_root)
        
        # 激活虛擬環境並安裝依賴
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        # 安裝Python依賴
        logger.info("安裝Python依賴...")
        subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], cwd=self.project_root)
        
        # 安裝Node.js依賴
        claudeditor_path = self.project_root / "claudeditor"
        if claudeditor_path.exists() and (claudeditor_path / "package.json").exists():
            logger.info("安裝Node.js依賴...")
            subprocess.run(["npm", "install"], cwd=claudeditor_path)
        
        # 創建必要目錄
        for directory in ["logs", "data", "uploads", "exports", "temp"]:
            (self.project_root / directory).mkdir(exist_ok=True)
        
        # 初始化配置文件
        await self._create_config_files()
        
        logger.info("✅ 環境設置完成")
    
    async def _create_config_files(self):
        """創建配置文件"""
        # 創建.env文件
        env_file = self.project_root / ".env"
        if not env_file.exists():
            env_content = f"""# PowerAutomation 環境配置
# 服務端口
CORE_PORT={self.config['core_port']}
CLAUDEDITOR_PORT={self.config['claudeditor_port']}
WEBSOCKET_PORT={self.config['websocket_port']}
MEMBERSHIP_API_PORT={self.config['membership_api_port']}
MCP_SERVER_PORT={self.config['mcp_server_port']}

# API密鑰（請替換為實際密鑰）
CLAUDE_API_KEY=your_claude_api_key
KIMI_API_KEY=your_kimi_api_key
OPENAI_API_KEY=your_openai_api_key

# 系統配置
DEBUG=true
LOG_LEVEL=INFO
JWT_SECRET_KEY=powerautomation-secret-key-2025

# 數據庫配置
DATABASE_URL=sqlite:///powerautomation.db
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            logger.info("✅ .env配置文件已創建")
        
        # 創建系統配置文件
        config_file = self.project_root / "system_config.json"
        if not config_file.exists():
            config_data = {
                "system": {
                    "name": "PowerAutomation",
                    "version": "1.0.0",
                    "release_date": "2025-07-30"
                },
                "services": self.config,
                "features": {
                    "k2_model_switching": True,
                    "claude_code_integration": True,
                    "membership_system": True,
                    "manus_data_collection": True,
                    "smart_ui_generation": True,
                    "workflow_automation": True,
                    "memory_rag": True
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info("✅ 系統配置文件已創建")
    
    async def start_component(self, component_name: str) -> bool:
        """啟動單個組件"""
        component = self.components[component_name]
        logger.info(f"🚀 啟動 {component['name']}...")
        
        try:
            if "script" in component:
                # Python腳本
                if os.name == 'nt':  # Windows
                    python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
                else:  # Unix/Linux/macOS
                    python_exe = self.project_root / "venv" / "bin" / "python"
                
                process = subprocess.Popen(
                    [str(python_exe), component["script"]],
                    cwd=self.project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            elif "command" in component:
                # 其他命令
                cwd = self.project_root / component.get("cwd", ".")
                process = subprocess.Popen(
                    component["command"],
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                logger.error(f"❌ 組件 {component_name} 配置錯誤")
                return False
            
            self.processes[component_name] = process
            
            # 等待組件啟動
            await asyncio.sleep(3)
            
            # 檢查進程是否正常運行
            if process.poll() is None:
                logger.info(f"✅ {component['name']} 啟動成功 (PID: {process.pid})")
                return True
            else:
                logger.error(f"❌ {component['name']} 啟動失敗")
                return False
                
        except Exception as e:
            logger.error(f"❌ 啟動 {component['name']} 時發生錯誤: {e}")
            return False
    
    async def check_component_health(self, component_name: str) -> bool:
        """檢查組件健康狀態"""
        component = self.components[component_name]
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                url = f"http://localhost:{component['port']}{component['health_endpoint']}"
                response = await client.get(url, timeout=5.0)
                return response.status_code == 200
        except:
            return False
    
    async def start_all_components(self):
        """啟動所有組件"""
        logger.info("🚀 啟動PowerAutomation完整系統...")
        
        # 按順序啟動組件
        startup_order = [
            "membership_api",
            "mcp_server", 
            "powerautomation_core",
            "claudeditor_frontend"
        ]
        
        for component_name in startup_order:
            success = await self.start_component(component_name)
            if not success:
                logger.error(f"❌ 啟動 {component_name} 失敗，系統啟動中止")
                return False
            
            # 等待組件完全啟動
            await asyncio.sleep(2)
        
        # 等待所有服務準備就緒
        logger.info("⏳ 等待所有服務準備就緒...")
        await asyncio.sleep(10)
        
        # 檢查所有組件健康狀態
        all_healthy = True
        for component_name in startup_order:
            if component_name == "claudeditor_frontend":
                continue  # 前端健康檢查可能不同
            
            healthy = await self.check_component_health(component_name)
            component = self.components[component_name]
            
            if healthy:
                logger.info(f"✅ {component['name']} 健康檢查通過")
            else:
                logger.warning(f"⚠️ {component['name']} 健康檢查失敗")
                all_healthy = False
        
        return all_healthy
    
    async def show_system_info(self):
        """顯示系統信息"""
        logger.info("\n" + "="*60)
        logger.info("🎉 PowerAutomation 系統啟動完成！")
        logger.info("="*60)
        
        print("\n🌐 服務訪問地址：")
        print(f"  • ClaudeEditor Web界面: http://localhost:{self.config['claudeditor_port']}")
        print(f"  • 會員系統API: http://localhost:{self.config['membership_api_port']}")
        print(f"  • PowerAutomation Core: http://localhost:{self.config['core_port']}")
        print(f"  • MCP服務器: http://localhost:{self.config['mcp_server_port']}")
        
        print("\n🔧 系統功能：")
        print("  • ✅ 會員積分登錄系統")
        print("  • ✅ K2模型智能路由 (節省60-80%成本)")
        print("  • ✅ Claude Code Tool完整兼容")
        print("  • ✅ ClaudeEditor可視化界面")
        print("  • ✅ 六大工作流自動化")
        print("  • ✅ Memory RAG記憶增強")
        print("  • ✅ Manus數據收集準備")
        
        print("\n💡 使用說明：")
        print("  1. 在Claude Code Tool中使用：所有命令自動路由到K2模型")
        print("  2. 在ClaudeEditor中使用：訪問上面的Web界面")
        print("  3. 使用 /switch-k2 或 /switch-claude 切換模型")
        print("  4. 使用 /claudeditor-open 打開可視化界面")
        
        print("\n⚠️  重要提醒：")
        print("  • 請在.env文件中配置您的API密鑰")
        print("  • 系統支持本地Chrome/Safari認證收集Manus數據")
        print("  • 7/30正式上線版本，所有核心功能已就緒")
        
        print("\n📧 技術支持：")
        print("  • GitHub: https://github.com/alexchuang650730/aicore0718")
        print("  • 作者: Alex Chuang")
        
        # 自動打開瀏覽器
        try:
            webbrowser.open(f"http://localhost:{self.config['claudeditor_port']}")
            print(f"\n🌐 瀏覽器已自動打開 ClaudeEditor 界面")
        except:
            print(f"\n🌐 請手動打開瀏覽器訪問: http://localhost:{self.config['claudeditor_port']}")
    
    async def monitor_system(self):
        """監控系統運行狀態"""
        logger.info("👁️ 開始系統監控...")
        
        try:
            while True:
                await asyncio.sleep(30)  # 每30秒檢查一次
                
                # 檢查所有進程
                for component_name, process in self.processes.items():
                    if process.poll() is not None:
                        logger.error(f"❌ {self.components[component_name]['name']} 進程已停止")
                        # 這裡可以添加自動重啟邏輯
                        
        except KeyboardInterrupt:
            logger.info("📴 收到停止信號，正在關閉系統...")
            await self.shutdown_system()
        except Exception as e:
            logger.error(f"❌ 系統監控錯誤: {e}")
    
    async def shutdown_system(self):
        """關閉系統"""
        logger.info("📴 正在關閉PowerAutomation系統...")
        
        for component_name, process in self.processes.items():
            try:
                process.terminate()
                await asyncio.sleep(2)
                if process.poll() is None:
                    process.kill()
                logger.info(f"✅ {self.components[component_name]['name']} 已停止")
            except Exception as e:
                logger.error(f"❌ 停止 {component_name} 時發生錯誤: {e}")
        
        logger.info("✅ PowerAutomation系統已完全關閉")

async def main():
    """主函數"""
    launcher = PowerAutomationSystemLauncher()
    
    try:
        # 檢查依賴
        dependencies = await launcher.check_dependencies()
        if not all(dependencies.values()):
            logger.error("❌ 依賴檢查失敗，請解決依賴問題後重試")
            return
        
        # 設置環境
        await launcher.setup_environment()
        
        # 啟動所有組件
        success = await launcher.start_all_components()
        if not success:
            logger.error("❌ 系統啟動失敗")
            return
        
        # 顯示系統信息
        await launcher.show_system_info()
        
        # 開始監控
        await launcher.monitor_system()
        
    except KeyboardInterrupt:
        print("\n👋 感謝使用PowerAutomation！")
    except Exception as e:
        logger.error(f"❌ 系統啟動失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 設置事件循環策略（Windows兼容性）
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 運行主程序
    asyncio.run(main())