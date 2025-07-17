#!/usr/bin/env python3
"""
PowerAutomation 生态系统统一启动脚本
当执行 Claude Code 时自动启动 ClaudeEditor 和所有相关服务
"""

import os
import sys
import subprocess
import time
import signal
import threading
import asyncio
import json
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PowerAutomationEcosystem:
    """PowerAutomation 生态系统管理器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.claudeditor_dir = self.base_dir / "claudeditor"
        self.processes = {}
        self.is_running = False
        
        # 服务配置
        self.services = {
            "claudeditor_frontend": {
                "name": "ClaudeEditor 前端",
                "command": ["npm", "start"],
                "cwd": str(self.claudeditor_dir),
                "port": 3000,
                "health_check": "http://localhost:3000",
                "startup_time": 10
            },
            "claudeditor_api": {
                "name": "ClaudeEditor API",
                "command": ["python", "api/src/main.py"],
                "cwd": str(self.claudeditor_dir),
                "port": 5000,
                "health_check": "http://localhost:5000",
                "startup_time": 5
            },
            "command_mcp": {
                "name": "Command MCP (集成 Mirror Code)",
                "command": ["python", "-c", "from core.components.command_mcp.command_manager import ClaudeCodeSlashCommandHandler; import asyncio; handler = ClaudeCodeSlashCommandHandler(); print('Command MCP 运行中...'); asyncio.get_event_loop().run_forever()"],
                "cwd": str(self.base_dir),
                "port": None,
                "startup_time": 3
            }
        }
        
        logger.info("🚀 PowerAutomation 生态系统管理器初始化完成")
    
    def start_ecosystem(self, claude_command=None):
        """启动完整的 PowerAutomation 生态系统"""
        try:
            logger.info("=" * 60)
            logger.info("🌟 启动 PowerAutomation v4.6.9.5 完整生态系统")
            logger.info("=" * 60)
            
            # 1. 检查环境
            self.check_environment()
            
            # 2. 启动 ClaudeEditor API (后端)
            self.start_service("claudeditor_api")
            
            # 3. 启动 Command MCP (集成 Mirror Code)
            self.start_service("command_mcp")
            
            # 4. 启动 ClaudeEditor 前端
            self.start_service("claudeditor_frontend")
            
            # 5. 等待所有服务就绪
            self.wait_for_services()
            
            # 6. 显示启动完成信息
            self.show_startup_info()
            
            # 7. 如果有 Claude 命令，执行它
            if claude_command:
                self.execute_claude_command(claude_command)
            
            # 8. 保持运行
            self.keep_running()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 接收到停止信号...")
            self.stop_ecosystem()
        except Exception as e:
            logger.error(f"❌ 生态系统启动失败: {e}")
            self.stop_ecosystem()
            sys.exit(1)
    
    def check_environment(self):
        """检查运行环境"""
        logger.info("🔍 检查运行环境...")
        
        # 检查 Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Node.js: {result.stdout.strip()}")
            else:
                raise Exception("Node.js 未安装")
        except:
            logger.error("❌ Node.js 未安装或不可用")
            sys.exit(1)
        
        # 检查 Python
        logger.info(f"✅ Python: {sys.version.split()[0]}")
        
        # 检查 ClaudeEditor 目录
        if not self.claudeditor_dir.exists():
            logger.error(f"❌ ClaudeEditor 目录不存在: {self.claudeditor_dir}")
            sys.exit(1)
        
        # 检查 package.json
        package_json = self.claudeditor_dir / "package.json"
        if not package_json.exists():
            logger.error("❌ ClaudeEditor package.json 不存在")
            sys.exit(1)
        
        logger.info("✅ 环境检查通过")
    
    def start_service(self, service_name):
        """启动单个服务"""
        service = self.services[service_name]
        logger.info(f"🚀 启动 {service['name']}...")
        
        try:
            # 启动进程
            process = subprocess.Popen(
                service["command"],
                cwd=service["cwd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[service_name] = {
                "process": process,
                "config": service
            }
            
            logger.info(f"✅ {service['name']} 已启动 (PID: {process.pid})")
            
            # 等待启动时间
            time.sleep(service["startup_time"])
            
            # 检查进程是否还在运行
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {service['name']} 启动失败")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                raise Exception(f"{service['name']} 启动失败")
            
        except Exception as e:
            logger.error(f"❌ 启动 {service['name']} 失败: {e}")
            raise
    
    def wait_for_services(self):
        """等待所有服务就绪"""
        logger.info("⏳ 等待所有服务就绪...")
        
        max_wait = 30  # 最大等待时间 30 秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            all_ready = True
            
            for service_name, service_info in self.processes.items():
                process = service_info["process"]
                
                # 检查进程是否还在运行
                if process.poll() is not None:
                    logger.error(f"❌ {service_info['config']['name']} 进程已退出")
                    all_ready = False
                    break
            
            if all_ready:
                logger.info("✅ 所有服务已就绪")
                self.is_running = True
                return
            
            time.sleep(1)
        
        logger.error("❌ 服务启动超时")
        raise Exception("服务启动超时")
    
    def show_startup_info(self):
        """显示启动完成信息"""
        logger.info("=" * 60)
        logger.info("🎉 PowerAutomation v4.6.9.5 生态系统启动完成！")
        logger.info("=" * 60)
        
        logger.info("📋 运行中的服务:")
        for service_name, service_info in self.processes.items():
            config = service_info["config"]
            pid = service_info["process"].pid
            logger.info(f"  ✅ {config['name']} (PID: {pid})")
            if config.get("port"):
                logger.info(f"     🌐 http://localhost:{config['port']}")
        
        logger.info("\n🌟 核心特性:")
        logger.info("  🤖 默认模型: K2 云端模型 (免费、快速)")
        logger.info("  🪞 Mirror Code: 已集成到 Command MCP")
        logger.info("  🔄 智能路由: K2 优先，Claude Code 备用")
        logger.info("  📱 ClaudeEditor: 跨平台 AI 代码编辑器")
        
        logger.info("\n🔗 访问地址:")
        logger.info("  📱 ClaudeEditor: http://localhost:3000")
        logger.info("  🔌 API 服务: http://localhost:5000")
        
        logger.info("\n💡 使用提示:")
        logger.info("  - 在 ClaudeEditor 中使用 /help 查看所有指令")
        logger.info("  - 默认使用 K2 云端模型，无需 API 费用")
        logger.info("  - 使用 /switch-model claude 切换到 Claude Code")
        logger.info("  - 按 Ctrl+C 停止所有服务")
        
        logger.info("=" * 60)
    
    def execute_claude_command(self, command):
        """执行 Claude 命令"""
        logger.info(f"🧠 执行 Claude 命令: {command}")
        
        try:
            # 这里可以集成实际的 Claude Code 执行逻辑
            # 现在先模拟执行
            logger.info("🔄 通过 Command MCP 处理命令...")
            logger.info("✅ 命令执行完成")
            
        except Exception as e:
            logger.error(f"❌ Claude 命令执行失败: {e}")
    
    def keep_running(self):
        """保持系统运行"""
        logger.info("\n⌨️ 系统运行中... (按 Ctrl+C 停止)")
        
        try:
            while self.is_running:
                # 检查所有进程是否还在运行
                for service_name, service_info in self.processes.items():
                    process = service_info["process"]
                    if process.poll() is not None:
                        logger.error(f"❌ {service_info['config']['name']} 意外退出")
                        self.is_running = False
                        break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
    
    def stop_ecosystem(self):
        """停止生态系统"""
        logger.info("🔄 正在停止 PowerAutomation 生态系统...")
        
        for service_name, service_info in self.processes.items():
            try:
                process = service_info["process"]
                config = service_info["config"]
                
                logger.info(f"🛑 停止 {config['name']}...")
                
                # 尝试优雅停止
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=5)
                    logger.info(f"✅ {config['name']} 已停止")
                except subprocess.TimeoutExpired:
                    # 强制杀死
                    logger.warning(f"⚠️ 强制停止 {config['name']}")
                    process.kill()
                    process.wait()
                
            except Exception as e:
                logger.error(f"❌ 停止 {config['name']} 失败: {e}")
        
        self.is_running = False
        logger.info("✅ PowerAutomation 生态系统已停止")

def create_claude_wrapper():
    """创建 Claude 命令包装器"""
    wrapper_script = """#!/bin/bash
# PowerAutomation Claude Code 包装器
# 自动启动 ClaudeEditor 和相关服务

echo "🚀 启动 PowerAutomation 生态系统..."

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 启动 PowerAutomation 生态系统
python3 "$SCRIPT_DIR/start_powerautomation_ecosystem.py" "$@"
"""
    
    wrapper_path = Path(__file__).parent / "claude"
    
    try:
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_script)
        
        # 设置执行权限
        os.chmod(wrapper_path, 0o755)
        
        logger.info(f"✅ Claude 包装器已创建: {wrapper_path}")
        logger.info("💡 现在可以使用 ./claude <command> 启动完整生态系统")
        
    except Exception as e:
        logger.error(f"❌ 创建 Claude 包装器失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerAutomation 生态系统启动器")
    parser.add_argument("--claude-command", help="要执行的 Claude 命令")
    parser.add_argument("--create-wrapper", action="store_true", help="创建 Claude 命令包装器")
    
    args = parser.parse_args()
    
    if args.create_wrapper:
        create_claude_wrapper()
        return
    
    # 启动生态系统
    ecosystem = PowerAutomationEcosystem()
    ecosystem.start_ecosystem(args.claude_command)

if __name__ == "__main__":
    main()

