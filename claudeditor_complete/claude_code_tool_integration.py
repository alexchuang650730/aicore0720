#!/usr/bin/env python3
"""
PowerAutomation ClaudeEditor <-> Claude Code Tool 深度集成
提供Claude Code Tool缺失的可視化界面和工作流功能
"""

import asyncio
import json
import logging
import subprocess
import os
import sys
import time
import websockets
import aiohttp
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
import docker
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class ClaudeCodeToolStatus(Enum):
    """Claude Code Tool狀態"""
    NOT_INSTALLED = "not_installed"
    INSTALLING = "installing"
    INSTALLED = "installed"
    RUNNING = "running"
    ERROR = "error"
    UPDATING = "updating"

@dataclass
class ClaudeCodeToolConfig:
    """Claude Code Tool配置"""
    api_key: str
    model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4096
    temperature: float = 0.7
    workspace_path: str = None
    project_name: str = None

@dataclass
class DeploymentConfig:
    """部署配置"""
    project_path: str
    deployment_type: str  # local, docker, cloud
    environment: str  # dev, staging, prod
    config_overrides: Dict[str, Any] = None

class ClaudeCodeToolManager:
    """Claude Code Tool管理器 - 提供可視化界面"""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/claude_workspace")
        self.config_file = Path(self.workspace_dir) / "claude_config.json"
        self.status = ClaudeCodeToolStatus.NOT_INSTALLED
        self.current_config = None
        self.docker_client = None
        self.websocket_clients = set()
        
        # 確保工作區存在
        Path(self.workspace_dir).mkdir(parents=True, exist_ok=True)
        
        # 初始化Docker客戶端
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker不可用: {e}")
        
        logger.info(f"🚀 Claude Code Tool管理器初始化完成: {self.workspace_dir}")

    async def check_installation_status(self) -> Dict[str, Any]:
        """檢查Claude Code Tool安裝狀態"""
        try:
            # 檢查claude命令是否可用
            result = subprocess.run(
                ["claude", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                self.status = ClaudeCodeToolStatus.INSTALLED
                version = result.stdout.strip()
                
                # 檢查是否有運行中的實例
                is_running = await self._check_running_instances()
                if is_running:
                    self.status = ClaudeCodeToolStatus.RUNNING
                
                return {
                    "status": self.status.value,
                    "version": version,
                    "workspace": self.workspace_dir,
                    "config_exists": self.config_file.exists(),
                    "running_instances": is_running
                }
            else:
                self.status = ClaudeCodeToolStatus.NOT_INSTALLED
                return {
                    "status": self.status.value,
                    "message": "Claude Code Tool未安裝"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "命令執行超時"
            }
        except FileNotFoundError:
            self.status = ClaudeCodeToolStatus.NOT_INSTALLED
            return {
                "status": self.status.value,
                "message": "Claude Code Tool未安裝"
            }
        except Exception as e:
            self.status = ClaudeCodeToolStatus.ERROR
            return {
                "status": self.status.value,
                "error": str(e)
            }

    async def install_claude_code_tool(self, progress_callback=None) -> Dict[str, Any]:
        """安裝Claude Code Tool - 提供進度回調"""
        try:
            self.status = ClaudeCodeToolStatus.INSTALLING
            
            if progress_callback:
                await progress_callback(10, "開始安裝...")
            
            # 檢查系統依賴
            dependencies = await self._check_dependencies()
            if not dependencies["all_satisfied"]:
                if progress_callback:
                    await progress_callback(15, "安裝依賴...")
                await self._install_dependencies(dependencies["missing"])
            
            if progress_callback:
                await progress_callback(30, "下載Claude Code Tool...")
            
            # 安裝Claude Code Tool
            install_result = await self._install_claude_cli()
            
            if progress_callback:
                await progress_callback(70, "配置環境...")
            
            # 初始化配置
            config_result = await self._initialize_config()
            
            if progress_callback:
                await progress_callback(90, "驗證安裝...")
            
            # 驗證安裝
            verification = await self.check_installation_status()
            
            if verification["status"] == "installed":
                self.status = ClaudeCodeToolStatus.INSTALLED
                if progress_callback:
                    await progress_callback(100, "安裝完成！")
                
                return {
                    "success": True,
                    "message": "Claude Code Tool安裝成功",
                    "details": verification
                }
            else:
                raise Exception("安裝驗證失敗")
                
        except Exception as e:
            self.status = ClaudeCodeToolStatus.ERROR
            logger.error(f"安裝失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": self.status.value
            }

    async def _check_dependencies(self) -> Dict[str, Any]:
        """檢查系統依賴"""
        dependencies = {
            "python": {"command": "python3 --version", "satisfied": False},
            "pip": {"command": "pip3 --version", "satisfied": False},
            "git": {"command": "git --version", "satisfied": False},
            "node": {"command": "node --version", "satisfied": False},
            "npm": {"command": "npm --version", "satisfied": False}
        }
        
        missing = []
        
        for dep_name, dep_info in dependencies.items():
            try:
                result = subprocess.run(
                    dep_info["command"].split(),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                dep_info["satisfied"] = result.returncode == 0
                if not dep_info["satisfied"]:
                    missing.append(dep_name)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing.append(dep_name)
        
        return {
            "dependencies": dependencies,
            "missing": missing,
            "all_satisfied": len(missing) == 0
        }

    async def _install_dependencies(self, missing: List[str]) -> None:
        """安裝缺失的依賴"""
        system = os.uname().sysname.lower()
        
        if system == "darwin":  # macOS
            await self._install_macos_dependencies(missing)
        elif system == "linux":
            await self._install_linux_dependencies(missing)
        else:
            raise Exception(f"不支持的操作系統: {system}")

    async def _install_macos_dependencies(self, missing: List[str]) -> None:
        """在macOS上安裝依賴"""
        # 檢查是否有Homebrew
        try:
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception("需要安裝Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        
        # 安裝缺失的依賴
        for dep in missing:
            if dep == "python":
                subprocess.run(["brew", "install", "python@3.11"], check=True)
            elif dep == "node":
                subprocess.run(["brew", "install", "node"], check=True)
            elif dep == "git":
                subprocess.run(["brew", "install", "git"], check=True)

    async def _install_linux_dependencies(self, missing: List[str]) -> None:
        """在Linux上安裝依賴"""
        # 檢測包管理器
        if os.path.exists("/usr/bin/apt"):
            pkg_manager = "apt"
            install_cmd = ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y"]
        elif os.path.exists("/usr/bin/yum"):
            pkg_manager = "yum"
            install_cmd = ["sudo", "yum", "install", "-y"]
        else:
            raise Exception("不支持的Linux發行版")
        
        # 映射依賴名稱
        dep_mapping = {
            "python": "python3",
            "pip": "python3-pip",
            "node": "nodejs",
            "npm": "npm",
            "git": "git"
        }
        
        packages = [dep_mapping.get(dep, dep) for dep in missing]
        
        if packages:
            subprocess.run(install_cmd + packages, check=True)

    async def _install_claude_cli(self) -> Dict[str, Any]:
        """安裝Claude CLI"""
        try:
            # 使用pip安裝Claude CLI
            result = subprocess.run([
                "pip3", "install", "--upgrade", "anthropic-cli"
            ], capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            raise Exception(f"Claude CLI安裝失敗: {e.stderr}")

    async def _initialize_config(self) -> Dict[str, Any]:
        """初始化Claude配置"""
        # 創建默認配置
        default_config = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4096,
            "temperature": 0.7,
            "workspace": self.workspace_dir,
            "created_at": time.time()
        }
        
        # 保存配置
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.current_config = default_config
        return {"success": True, "config": default_config}

    async def _check_running_instances(self) -> bool:
        """檢查是否有運行中的Claude實例"""
        try:
            # 檢查進程
            result = subprocess.run([
                "pgrep", "-f", "claude"
            ], capture_output=True, text=True)
            
            return result.returncode == 0 and result.stdout.strip()
        except Exception:
            return False

    async def create_project(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """創建新項目 - 可視化界面"""
        try:
            project_name = project_config["name"]
            project_type = project_config.get("type", "general")
            project_path = Path(self.workspace_dir) / project_name
            
            # 創建項目目錄
            project_path.mkdir(parents=True, exist_ok=True)
            
            # 根據項目類型創建模板
            template_config = await self._create_project_template(project_path, project_type)
            
            # 初始化Git倉庫
            subprocess.run(["git", "init"], cwd=project_path, check=True)
            
            # 創建項目配置文件
            project_config_file = project_path / "claude_project.json"
            with open(project_config_file, 'w') as f:
                json.dump({
                    **project_config,
                    "created_at": time.time(),
                    "path": str(project_path),
                    "template": template_config
                }, f, indent=2)
            
            return {
                "success": True,
                "project_path": str(project_path),
                "config": project_config
            }
            
        except Exception as e:
            logger.error(f"項目創建失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_project_template(self, project_path: Path, project_type: str) -> Dict[str, Any]:
        """根據項目類型創建模板"""
        templates = {
            "web_app": {
                "files": {
                    "index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>My Web App</title>\n</head>\n<body>\n    <h1>Hello World</h1>\n</body>\n</html>",
                    "styles.css": "body { font-family: Arial, sans-serif; }",
                    "script.js": "console.log('Hello from PowerAutomation!');"
                },
                "folders": ["src", "assets", "tests"]
            },
            "api_service": {
                "files": {
                    "main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}",
                    "requirements.txt": "fastapi\nuvicorn",
                    "Dockerfile": "FROM python:3.11\nCOPY . /app\nWORKDIR /app\nRUN pip install -r requirements.txt\nCMD uvicorn main:app --host 0.0.0.0 --port 8000"
                },
                "folders": ["src", "tests", "docs"]
            },
            "data_analysis": {
                "files": {
                    "analysis.py": "import pandas as pd\nimport matplotlib.pyplot as plt\n\n# Data analysis starter",
                    "requirements.txt": "pandas\nmatplotlib\njupyter\nnumpy",
                    "README.md": "# Data Analysis Project\n\nPowered by PowerAutomation"
                },
                "folders": ["data", "notebooks", "outputs"]
            }
        }
        
        template = templates.get(project_type, templates["web_app"])
        
        # 創建文件夾
        for folder in template["folders"]:
            (project_path / folder).mkdir(exist_ok=True)
        
        # 創建文件
        for filename, content in template["files"].items():
            with open(project_path / filename, 'w') as f:
                f.write(content)
        
        return template

    async def deploy_project(self, deployment_config: DeploymentConfig, progress_callback=None) -> Dict[str, Any]:
        """部署項目 - 可視化進度"""
        try:
            if progress_callback:
                await progress_callback(5, "準備部署...")
            
            project_path = Path(deployment_config.project_path)
            
            # 驗證項目
            if not project_path.exists():
                raise Exception(f"項目路徑不存在: {project_path}")
            
            if progress_callback:
                await progress_callback(15, "檢查部署配置...")
            
            # 根據部署類型執行不同策略
            if deployment_config.deployment_type == "local":
                result = await self._deploy_local(project_path, deployment_config, progress_callback)
            elif deployment_config.deployment_type == "docker":
                result = await self._deploy_docker(project_path, deployment_config, progress_callback)
            elif deployment_config.deployment_type == "cloud":
                result = await self._deploy_cloud(project_path, deployment_config, progress_callback)
            else:
                raise Exception(f"不支持的部署類型: {deployment_config.deployment_type}")
            
            if progress_callback:
                await progress_callback(100, "部署完成！")
            
            return result
            
        except Exception as e:
            logger.error(f"部署失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _deploy_local(self, project_path: Path, config: DeploymentConfig, progress_callback) -> Dict[str, Any]:
        """本地部署"""
        if progress_callback:
            await progress_callback(30, "啟動本地服務...")
        
        # 檢查項目類型
        if (project_path / "main.py").exists():
            # Python FastAPI項目
            if progress_callback:
                await progress_callback(50, "安裝Python依賴...")
            
            # 安裝依賴
            subprocess.run([
                "pip3", "install", "-r", "requirements.txt"
            ], cwd=project_path, check=True)
            
            if progress_callback:
                await progress_callback(80, "啟動服務...")
            
            # 啟動服務
            process = subprocess.Popen([
                "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
            ], cwd=project_path)
            
            return {
                "success": True,
                "service_url": "http://localhost:8000",
                "process_id": process.pid,
                "type": "fastapi"
            }
            
        elif (project_path / "index.html").exists():
            # 靜態網站
            if progress_callback:
                await progress_callback(50, "啟動Web服務...")
            
            # 使用Python的HTTP服務器
            process = subprocess.Popen([
                "python3", "-m", "http.server", "8080"
            ], cwd=project_path)
            
            return {
                "success": True,
                "service_url": "http://localhost:8080",
                "process_id": process.pid,
                "type": "static"
            }
        else:
            raise Exception("無法識別項目類型")

    async def _deploy_docker(self, project_path: Path, config: DeploymentConfig, progress_callback) -> Dict[str, Any]:
        """Docker部署"""
        if not self.docker_client:
            raise Exception("Docker不可用")
        
        if progress_callback:
            await progress_callback(20, "構建Docker鏡像...")
        
        dockerfile_path = project_path / "Dockerfile"
        if not dockerfile_path.exists():
            # 創建默認Dockerfile
            await self._create_default_dockerfile(project_path)
        
        # 構建鏡像
        image_tag = f"powerautomation-{project_path.name}"
        image, build_logs = self.docker_client.images.build(
            path=str(project_path),
            tag=image_tag,
            rm=True
        )
        
        if progress_callback:
            await progress_callback(70, "啟動容器...")
        
        # 運行容器
        container = self.docker_client.containers.run(
            image_tag,
            ports={'8000/tcp': 8000},
            detach=True,
            name=f"powerautomation-{project_path.name}-{int(time.time())}"
        )
        
        return {
            "success": True,
            "container_id": container.id,
            "image_tag": image_tag,
            "service_url": "http://localhost:8000",
            "type": "docker"
        }

    async def _deploy_cloud(self, project_path: Path, config: DeploymentConfig, progress_callback) -> Dict[str, Any]:
        """雲端部署（示例：使用簡單的雲端API）"""
        if progress_callback:
            await progress_callback(30, "準備雲端部署...")
        
        # 這裡可以集成AWS、GCP、Azure等雲端平台
        # 目前提供模擬實現
        
        await asyncio.sleep(2)  # 模擬部署時間
        
        if progress_callback:
            await progress_callback(70, "配置域名...")
        
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "service_url": f"https://{project_path.name}.powerautomation.cloud",
            "deployment_id": f"dep_{int(time.time())}",
            "type": "cloud"
        }

    async def _create_default_dockerfile(self, project_path: Path) -> None:
        """創建默認Dockerfile"""
        if (project_path / "main.py").exists():
            # Python項目
            dockerfile_content = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        else:
            # 靜態項目
            dockerfile_content = """FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
        
        with open(project_path / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)

    async def get_system_monitoring(self) -> Dict[str, Any]:
        """獲取系統監控數據"""
        try:
            import psutil
            
            # CPU和內存使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(self.workspace_dir)
            
            # 進程信息
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                if 'claude' in proc.info['name'].lower():
                    processes.append(proc.info)
            
            # Docker容器狀態
            containers = []
            if self.docker_client:
                for container in self.docker_client.containers.list():
                    if 'powerautomation' in container.name:
                        containers.append({
                            "id": container.id[:12],
                            "name": container.name,
                            "status": container.status,
                            "image": container.image.tags[0] if container.image.tags else "unknown"
                        })
            
            return {
                "timestamp": time.time(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available // (1024**3),  # GB
                    "disk_percent": (disk.used / disk.total) * 100,
                    "disk_free": disk.free // (1024**3)  # GB
                },
                "processes": processes,
                "containers": containers,
                "workspace": {
                    "path": self.workspace_dir,
                    "projects": len(list(Path(self.workspace_dir).glob("*/")))
                }
            }
            
        except ImportError:
            return {
                "error": "psutil not installed",
                "message": "請安裝psutil以啟用系統監控: pip install psutil"
            }
        except Exception as e:
            return {
                "error": str(e)
            }

    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """獲取部署狀態"""
        # 這裡應該從數據庫或配置文件中獲取部署信息
        # 現在提供模擬實現
        
        return {
            "deployment_id": deployment_id,
            "status": "running",
            "health_check": "healthy",
            "uptime": "2h 34m",
            "requests_count": 1247,
            "avg_response_time": "156ms",
            "last_deployment": "2024-01-15 14:30:00"
        }

# WebSocket處理器，用於實時通信
class ClaudeCodeToolWebSocketHandler:
    """WebSocket處理器，提供實時狀態更新"""
    
    def __init__(self, claude_manager: ClaudeCodeToolManager):
        self.claude_manager = claude_manager
        self.connected_clients = set()
    
    async def handle_client(self, websocket, path):
        """處理WebSocket客戶端連接"""
        self.connected_clients.add(websocket)
        logger.info(f"客戶端已連接，當前連接數: {len(self.connected_clients)}")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                response = await self.handle_message(data)
                await websocket.send(json.dumps(response))
        except websockets.exceptions.ConnectionClosed:
            logger.info("客戶端連接已關閉")
        finally:
            self.connected_clients.remove(websocket)
    
    async def handle_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理客戶端消息"""
        action = data.get("action")
        
        if action == "check_status":
            return await self.claude_manager.check_installation_status()
        elif action == "install":
            return await self.claude_manager.install_claude_code_tool(
                progress_callback=lambda progress, message: self.broadcast_progress(progress, message)
            )
        elif action == "create_project":
            return await self.claude_manager.create_project(data.get("config", {}))
        elif action == "deploy_project":
            deployment_config = DeploymentConfig(**data.get("config", {}))
            return await self.claude_manager.deploy_project(
                deployment_config,
                progress_callback=lambda progress, message: self.broadcast_progress(progress, message)
            )
        elif action == "get_monitoring":
            return await self.claude_manager.get_system_monitoring()
        elif action == "get_deployment_status":
            return await self.claude_manager.get_deployment_status(data.get("deployment_id"))
        else:
            return {"error": f"未知操作: {action}"}
    
    async def broadcast_progress(self, progress: int, message: str):
        """廣播進度更新"""
        if self.connected_clients:
            progress_data = {
                "type": "progress",
                "progress": progress,
                "message": message,
                "timestamp": time.time()
            }
            
            # 廣播給所有連接的客戶端
            disconnected = set()
            for client in self.connected_clients:
                try:
                    await client.send(json.dumps(progress_data))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # 清理斷開的連接
            self.connected_clients -= disconnected

# 使用示例
async def main():
    """示例主函數"""
    # 初始化Claude Code Tool管理器
    claude_manager = ClaudeCodeToolManager()
    
    # 檢查安裝狀態
    status = await claude_manager.check_installation_status()
    print(f"安裝狀態: {json.dumps(status, indent=2)}")
    
    # 如果未安裝，進行安裝
    if status["status"] == "not_installed":
        print("開始安裝Claude Code Tool...")
        
        def progress_callback(progress, message):
            print(f"[{progress:3d}%] {message}")
        
        install_result = await claude_manager.install_claude_code_tool(progress_callback)
        print(f"安裝結果: {json.dumps(install_result, indent=2)}")
    
    # 創建示例項目
    project_config = {
        "name": "my_web_app",
        "type": "web_app",
        "description": "PowerAutomation演示項目"
    }
    
    project_result = await claude_manager.create_project(project_config)
    print(f"項目創建: {json.dumps(project_result, indent=2)}")
    
    # 部署項目
    if project_result["success"]:
        deployment_config = DeploymentConfig(
            project_path=project_result["project_path"],
            deployment_type="local",
            environment="dev"
        )
        
        deployment_result = await claude_manager.deploy_project(deployment_config)
        print(f"部署結果: {json.dumps(deployment_result, indent=2)}")
    
    # 獲取系統監控
    monitoring = await claude_manager.get_system_monitoring()
    print(f"系統監控: {json.dumps(monitoring, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())