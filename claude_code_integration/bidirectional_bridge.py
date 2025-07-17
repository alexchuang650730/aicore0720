"""
ClaudeEditor ↔ Claude Code Tool 双向通信桥梁
实现文件同步、命令执行、WebUI交互等功能
"""

import asyncio
import json
import logging
import os
import subprocess
import websockets
from typing import Any, Dict, List, Optional
from pathlib import Path
import aiofiles
import httpx
from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil

logger = logging.getLogger(__name__)

class ClaudeCodeBridge:
    """Claude Code Tool 双向通信桥梁"""
    
    def __init__(self, claude_code_executable: str = "claude-code"):
        """
        初始化双向通信桥梁
        
        Args:
            claude_code_executable: Claude Code Tool可执行文件路径
        """
        self.claude_code_executable = claude_code_executable
        self.websocket_connections: List[WebSocket] = []
        self.download_directory = Path.home() / "Downloads" / "ClaudeEditor"
        self.download_directory.mkdir(parents=True, exist_ok=True)
        
        # 创建FastAPI应用
        self.app = FastAPI(title="ClaudeEditor Bridge", version="1.0.0")
        self._setup_routes()
        self._setup_cors()
    
    def _setup_cors(self):
        """设置CORS"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 生产环境中应该限制具体域名
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.websocket("/ws/claude-code")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket连接端点"""
            await websocket.accept()
            self.websocket_connections.append(websocket)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # 处理不同类型的消息
                    if message["type"] == "claude_code_command":
                        result = await self.execute_claude_code_command(message["command"])
                        await websocket.send_text(json.dumps({
                            "type": "command_result",
                            "result": result
                        }))
                    
                    elif message["type"] == "file_request":
                        file_info = await self.prepare_file_download(message["file_path"])
                        await websocket.send_text(json.dumps({
                            "type": "file_ready",
                            "file_info": file_info
                        }))
                        
            except Exception as e:
                logger.error(f"WebSocket错误: {e}")
            finally:
                self.websocket_connections.remove(websocket)
        
        @self.app.post("/api/claude-code/command")
        async def execute_command(command_data: Dict[str, Any]):
            """执行Claude Code命令"""
            try:
                result = await self.execute_claude_code_command(command_data["command"])
                return {"success": True, "result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/claude-code/download/{file_id}")
        async def download_file(file_id: str):
            """下载文件"""
            try:
                file_path = self.download_directory / f"{file_id}"
                if not file_path.exists():
                    raise HTTPException(status_code=404, detail="文件不存在")
                
                return FileResponse(
                    path=str(file_path),
                    filename=file_path.name,
                    media_type='application/octet-stream'
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/claude-code/upload")
        async def upload_file(file: UploadFile = File(...)):
            """上传文件到Claude Code工作目录"""
            try:
                # 获取当前工作目录
                current_dir = Path.cwd()
                file_path = current_dir / file.filename
                
                # 保存文件
                async with aiofiles.open(file_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                
                # 通知Claude Code有新文件
                await self.notify_claude_code_file_change(str(file_path))
                
                return {"success": True, "file_path": str(file_path)}
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/claude-code/status")
        async def get_status():
            """获取Claude Code状态"""
            try:
                # 检查Claude Code是否可用
                result = await self.check_claude_code_availability()
                return {
                    "claude_code_available": result["available"],
                    "version": result.get("version", "unknown"),
                    "active_connections": len(self.websocket_connections),
                    "download_directory": str(self.download_directory)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/claude-code/sync")
        async def sync_with_claude_code():
            """与Claude Code同步"""
            try:
                # 同步文件状态
                sync_result = await self.sync_files_with_claude_code()
                
                # 广播同步结果
                await self.broadcast_to_websockets({
                    "type": "sync_complete",
                    "result": sync_result
                })
                
                return {"success": True, "sync_result": sync_result}
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def execute_claude_code_command(self, command: str) -> Dict[str, Any]:
        """
        执行Claude Code命令
        
        Args:
            command: 要执行的命令
            
        Returns:
            命令执行结果
        """
        try:
            logger.info(f"🔧 执行Claude Code命令: {command}")
            
            # 构建完整命令
            full_command = f"{self.claude_code_executable} {command}"
            
            # 执行命令
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "command": command,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "success": process.returncode == 0
            }
            
            logger.info(f"✅ 命令执行完成: {command}")
            
            # 广播结果给所有WebSocket连接
            await self.broadcast_to_websockets({
                "type": "claude_code_result",
                "result": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 命令执行失败: {e}")
            return {
                "command": command,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    async def prepare_file_download(self, file_path: str) -> Dict[str, Any]:
        """
        准备文件下载
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息
        """
        try:
            source_path = Path(file_path)
            
            if not source_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 生成唯一文件ID
            file_id = f"{source_path.stem}_{hash(str(source_path))}.{source_path.suffix}"
            
            # 复制文件到下载目录
            destination = self.download_directory / file_id
            shutil.copy2(source_path, destination)
            
            file_info = {
                "file_id": file_id,
                "original_path": str(source_path),
                "file_name": source_path.name,
                "file_size": source_path.stat().st_size,
                "download_url": f"/api/claude-code/download/{file_id}",
                "ready": True
            }
            
            logger.info(f"📁 文件准备完成: {file_path}")
            return file_info
            
        except Exception as e:
            logger.error(f"❌ 文件准备失败: {e}")
            return {
                "file_id": None,
                "original_path": file_path,
                "error": str(e),
                "ready": False
            }
    
    async def check_claude_code_availability(self) -> Dict[str, Any]:
        """检查Claude Code是否可用"""
        try:
            # 尝试获取版本信息
            process = await asyncio.create_subprocess_shell(
                f"{self.claude_code_executable} --version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                version_info = stdout.decode('utf-8').strip()
                return {
                    "available": True,
                    "version": version_info,
                    "executable": self.claude_code_executable
                }
            else:
                return {
                    "available": False,
                    "error": stderr.decode('utf-8').strip(),
                    "executable": self.claude_code_executable
                }
                
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "executable": self.claude_code_executable
            }
    
    async def sync_files_with_claude_code(self) -> Dict[str, Any]:
        """与Claude Code同步文件"""
        try:
            # 获取当前工作目录的文件状态
            current_dir = Path.cwd()
            files_info = []
            
            for file_path in current_dir.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    files_info.append({
                        "path": str(file_path.relative_to(current_dir)),
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
            
            sync_result = {
                "timestamp": asyncio.get_event_loop().time(),
                "files_count": len(files_info),
                "files": files_info[:50],  # 限制返回文件数量
                "working_directory": str(current_dir)
            }
            
            logger.info(f"🔄 文件同步完成: {len(files_info)} 个文件")
            return sync_result
            
        except Exception as e:
            logger.error(f"❌ 文件同步失败: {e}")
            return {
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def notify_claude_code_file_change(self, file_path: str):
        """通知Claude Code文件变化"""
        try:
            # 广播文件变化通知
            await self.broadcast_to_websockets({
                "type": "file_change",
                "file_path": file_path,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            logger.info(f"📢 文件变化通知已发送: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 文件变化通知失败: {e}")
    
    async def broadcast_to_websockets(self, message: Dict[str, Any]):
        """广播消息到所有WebSocket连接"""
        if not self.websocket_connections:
            return
        
        message_str = json.dumps(message)
        
        # 移除已关闭的连接
        active_connections = []
        
        for ws in self.websocket_connections:
            try:
                await ws.send_text(message_str)
                active_connections.append(ws)
            except Exception as e:
                logger.warning(f"WebSocket连接已关闭: {e}")
        
        self.websocket_connections = active_connections
    
    async def start_server(self, host: str = "localhost", port: int = 8765):
        """启动桥梁服务器"""
        import uvicorn
        
        logger.info(f"🚀 启动ClaudeEditor桥梁服务器: http://{host}:{port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()

# 使用示例
async def main():
    """主函数示例"""
    bridge = ClaudeCodeBridge()
    await bridge.start_server()

if __name__ == "__main__":
    asyncio.run(main())