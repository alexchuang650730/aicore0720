"""
增强的命令管理器 - 通过Claude Router路由命令到Claude Code Tool
架构: ClaudeEditor → Claude Router → Command MCP + Local Adapter MCP
"""

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import os
import sys

logger = logging.getLogger(__name__)

class EnhancedCommandManager:
    """增强的命令管理器"""
    
    def __init__(self, local_adapter=None):
        """
        初始化增强命令管理器
        
        Args:
            local_adapter: 本地适配器实例
        """
        self.local_adapter = local_adapter
        self.claude_code_executable = "claude-code"
        self.command_history: List[Dict[str, Any]] = []
        self.active_sessions: Dict[str, Any] = {}
        
        # 命令类型映射
        self.command_types = {
            "claude_code": self._execute_claude_code_command,
            "local_system": self._execute_local_system_command,
            "file_operation": self._execute_file_operation,
            "workflow": self._execute_workflow_command,
            "mcp_internal": self._execute_mcp_internal_command
        }
    
    async def route_command(self, command_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        路由命令到相应的执行器
        
        Args:
            command_request: 命令请求
            {
                "command": "具体命令",
                "type": "命令类型",
                "session_id": "会话ID",
                "parameters": {},
                "context": {}
            }
            
        Returns:
            命令执行结果
        """
        try:
            command_type = command_request.get("type", "claude_code")
            command = command_request.get("command", "")
            session_id = command_request.get("session_id", "default")
            
            logger.info(f"🔄 路由命令: {command_type} - {command}")
            
            # 检查命令类型
            if command_type not in self.command_types:
                return {
                    "success": False,
                    "error": f"不支持的命令类型: {command_type}",
                    "available_types": list(self.command_types.keys())
                }
            
            # 执行命令
            result = await self.command_types[command_type](command_request)
            
            # 记录命令历史
            self._record_command_history(command_request, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 命令路由失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command_request.get("command", "")
            }
    
    async def _execute_claude_code_command(self, command_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Claude Code命令
        
        Args:
            command_request: 命令请求
            
        Returns:
            执行结果
        """
        try:
            command = command_request["command"]
            parameters = command_request.get("parameters", {})
            
            # 构建完整的Claude Code命令
            if parameters.get("working_directory"):
                os.chdir(parameters["working_directory"])
            
            full_command = f"{self.claude_code_executable} {command}"
            
            # 执行命令
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=parameters.get("working_directory", Path.cwd())
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "command": command,
                "type": "claude_code",
                "executed_at": asyncio.get_event_loop().time()
            }
            
            # 通过Local Adapter处理结果
            if self.local_adapter:
                result = await self.local_adapter.process_claude_code_result(result)
            
            logger.info(f"✅ Claude Code命令执行完成: {command}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Claude Code命令执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command_request.get("command", ""),
                "type": "claude_code"
            }
    
    async def _execute_local_system_command(self, command_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行本地系统命令
        
        Args:
            command_request: 命令请求
            
        Returns:
            执行结果
        """
        try:
            command = command_request["command"]
            parameters = command_request.get("parameters", {})
            
            # 安全检查
            if not self._is_safe_command(command):
                return {
                    "success": False,
                    "error": "不安全的命令被阻止",
                    "command": command,
                    "type": "local_system"
                }
            
            # 执行本地命令
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=parameters.get("working_directory", Path.cwd())
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "command": command,
                "type": "local_system",
                "executed_at": asyncio.get_event_loop().time()
            }
            
            # 通过Local Adapter处理结果
            if self.local_adapter:
                result = await self.local_adapter.process_local_command_result(result)
            
            logger.info(f"✅ 本地系统命令执行完成: {command}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 本地系统命令执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command_request.get("command", ""),
                "type": "local_system"
            }
    
    async def _execute_file_operation(self, command_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文件操作命令
        
        Args:
            command_request: 命令请求
            
        Returns:
            执行结果
        """
        try:
            operation = command_request["command"]
            parameters = command_request.get("parameters", {})
            
            if operation == "read":
                file_path = parameters.get("file_path")
                if not file_path or not Path(file_path).exists():
                    return {
                        "success": False,
                        "error": f"文件不存在: {file_path}",
                        "type": "file_operation"
                    }
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return {
                    "success": True,
                    "content": content,
                    "file_path": file_path,
                    "type": "file_operation",
                    "operation": "read"
                }
            
            elif operation == "write":
                file_path = parameters.get("file_path")
                content = parameters.get("content", "")
                
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "bytes_written": len(content.encode('utf-8')),
                    "type": "file_operation",
                    "operation": "write"
                }
            
            elif operation == "list":
                directory = parameters.get("directory", ".")
                pattern = parameters.get("pattern", "*")
                
                files = list(Path(directory).glob(pattern))
                file_info = []
                
                for file_path in files:
                    if file_path.is_file():
                        file_info.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "size": file_path.stat().st_size,
                            "modified": file_path.stat().st_mtime
                        })
                
                return {
                    "success": True,
                    "files": file_info,
                    "directory": directory,
                    "pattern": pattern,
                    "type": "file_operation",
                    "operation": "list"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"不支持的文件操作: {operation}",
                    "type": "file_operation"
                }
                
        except Exception as e:
            logger.error(f"❌ 文件操作失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "type": "file_operation"
            }
    
    async def _execute_workflow_command(self, command_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作流命令
        
        Args:
            command_request: 命令请求
            
        Returns:
            执行结果
        """
        try:
            workflow_type = command_request["command"]
            parameters = command_request.get("parameters", {})
            
            # 这里将集成重新定义的六大工作流
            workflow_results = {
                "goal_driven_development": await self._execute_goal_driven_workflow(parameters),
                "intelligent_code_generation": await self._execute_intelligent_code_workflow(parameters),
                "automated_testing_validation": await self._execute_automated_testing_workflow(parameters),
                "continuous_quality_assurance": await self._execute_quality_assurance_workflow(parameters),
                "smart_deployment_ops": await self._execute_smart_deployment_workflow(parameters),
                "adaptive_learning_optimization": await self._execute_adaptive_learning_workflow(parameters)
            }
            
            if workflow_type in workflow_results:
                return workflow_results[workflow_type]
            else:
                return {
                    "success": False,
                    "error": f"不支持的工作流类型: {workflow_type}",
                    "available_workflows": list(workflow_results.keys()),
                    "type": "workflow"
                }
                
        except Exception as e:
            logger.error(f"❌ 工作流执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "type": "workflow"
            }
    
    async def _execute_mcp_internal_command(self, command_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行MCP内部命令
        
        Args:
            command_request: 命令请求
            
        Returns:
            执行结果
        """
        try:
            command = command_request["command"]
            parameters = command_request.get("parameters", {})
            
            # MCP内部命令处理
            if command == "status":
                return {
                    "success": True,
                    "status": "running",
                    "active_sessions": len(self.active_sessions),
                    "command_history_count": len(self.command_history),
                    "type": "mcp_internal"
                }
            
            elif command == "reset":
                self.command_history.clear()
                self.active_sessions.clear()
                return {
                    "success": True,
                    "message": "MCP状态已重置",
                    "type": "mcp_internal"
                }
            
            elif command == "health_check":
                health_status = await self._perform_health_check()
                return {
                    "success": True,
                    "health_status": health_status,
                    "type": "mcp_internal"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"不支持的MCP内部命令: {command}",
                    "type": "mcp_internal"
                }
                
        except Exception as e:
            logger.error(f"❌ MCP内部命令执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "type": "mcp_internal"
            }
    
    # 六大工作流的占位符实现（将在后续重构中完善）
    async def _execute_goal_driven_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """目标驱动开发工作流"""
        return {
            "success": True,
            "workflow": "goal_driven_development",
            "status": "执行中",
            "message": "目标驱动开发工作流已启动",
            "type": "workflow"
        }
    
    async def _execute_intelligent_code_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """智能代码生成工作流"""
        return {
            "success": True,
            "workflow": "intelligent_code_generation",
            "status": "执行中",
            "message": "智能代码生成工作流已启动",
            "type": "workflow"
        }
    
    async def _execute_automated_testing_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """自动化测试验证工作流"""
        return {
            "success": True,
            "workflow": "automated_testing_validation",
            "status": "执行中",
            "message": "自动化测试验证工作流已启动",
            "type": "workflow"
        }
    
    async def _execute_quality_assurance_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """持续质量保证工作流"""
        return {
            "success": True,
            "workflow": "continuous_quality_assurance",
            "status": "执行中",
            "message": "持续质量保证工作流已启动",
            "type": "workflow"
        }
    
    async def _execute_smart_deployment_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """智能部署运维工作流"""
        return {
            "success": True,
            "workflow": "smart_deployment_ops",
            "status": "执行中",
            "message": "智能部署运维工作流已启动",
            "type": "workflow"
        }
    
    async def _execute_adaptive_learning_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """自适应学习优化工作流"""
        return {
            "success": True,
            "workflow": "adaptive_learning_optimization",
            "status": "执行中",
            "message": "自适应学习优化工作流已启动",
            "type": "workflow"
        }
    
    def _is_safe_command(self, command: str) -> bool:
        """检查命令是否安全"""
        dangerous_commands = [
            "rm -rf", "format", "del /", "rm /*", 
            "sudo rm", "chmod 777", "dd if=", ":(){ :|:& };:"
        ]
        
        return not any(dangerous in command.lower() for dangerous in dangerous_commands)
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """执行健康检查"""
        try:
            # 检查Claude Code Tool可用性
            claude_code_available = await self._check_claude_code_availability()
            
            # 检查Local Adapter状态
            local_adapter_status = "available" if self.local_adapter else "not_configured"
            
            return {
                "overall_status": "healthy",
                "claude_code_tool": claude_code_available,
                "local_adapter": local_adapter_status,
                "command_history_size": len(self.command_history),
                "active_sessions": len(self.active_sessions),
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def _check_claude_code_availability(self) -> str:
        """检查Claude Code Tool可用性"""
        try:
            process = await asyncio.create_subprocess_shell(
                f"{self.claude_code_executable} --version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return "available"
            else:
                return "error"
                
        except Exception:
            return "not_found"
    
    def _record_command_history(self, command_request: Dict[str, Any], result: Dict[str, Any]):
        """记录命令历史"""
        history_entry = {
            "timestamp": asyncio.get_event_loop().time(),
            "command_request": command_request,
            "result": result,
            "session_id": command_request.get("session_id", "default")
        }
        
        self.command_history.append(history_entry)
        
        # 限制历史记录大小
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-500:]
    
    async def get_command_history(self, session_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取命令历史"""
        if session_id:
            filtered_history = [
                entry for entry in self.command_history
                if entry.get("session_id") == session_id
            ]
        else:
            filtered_history = self.command_history
        
        return filtered_history[-limit:]
    
    async def clear_command_history(self, session_id: str = None):
        """清空命令历史"""
        if session_id:
            self.command_history = [
                entry for entry in self.command_history
                if entry.get("session_id") != session_id
            ]
        else:
            self.command_history.clear()
        
        logger.info(f"📝 命令历史已清空 - 会话: {session_id or 'all'}")

# 使用示例
async def main():
    """主函数示例"""
    command_manager = EnhancedCommandManager()
    
    # 示例命令请求
    command_request = {
        "command": "--version",
        "type": "claude_code",
        "session_id": "test_session",
        "parameters": {},
        "context": {}
    }
    
    result = await command_manager.route_command(command_request)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())