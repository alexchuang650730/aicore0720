#!/usr/bin/env python3
"""
ClaudeEditor Terminal Server
真实终端连接后端服务 - 支持WebSocket实时交互
"""

import asyncio
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import websockets
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import pty
import select
import termios
import struct
import fcntl

app = Flask(__name__)
app.config['SECRET_KEY'] = 'claudeeditor-terminal-secret'
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 全局变量存储活动的终端会话
active_terminals: Dict[str, Dict] = {}
active_processes: Dict[str, subprocess.Popen] = {}

class TerminalSession:
    """终端会话管理类"""
    
    def __init__(self, session_id: str, platform: str = 'linux'):
        self.session_id = session_id
        self.platform = platform
        self.master_fd = None
        self.slave_fd = None
        self.process = None
        self.is_active = False
        
    def start(self):
        """启动终端会话"""
        try:
            # 创建伪终端
            self.master_fd, self.slave_fd = pty.openpty()
            
            # 设置终端大小
            self.set_terminal_size(80, 24)
            
            # 启动shell进程
            shell = '/bin/bash' if self.platform != 'windows' else 'cmd.exe'
            self.process = subprocess.Popen(
                shell,
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                preexec_fn=os.setsid if self.platform != 'windows' else None
            )
            
            self.is_active = True
            return True
            
        except Exception as e:
            print(f"启动终端会话失败: {e}")
            return False
    
    def set_terminal_size(self, cols: int, rows: int):
        """设置终端大小"""
        if self.master_fd:
            try:
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, 
                           struct.pack('HHHH', rows, cols, 0, 0))
            except:
                pass
    
    def write(self, data: str):
        """向终端写入数据"""
        if self.master_fd and self.is_active:
            try:
                os.write(self.master_fd, data.encode('utf-8'))
                return True
            except:
                return False
        return False
    
    def read(self, timeout: float = 0.1) -> str:
        """从终端读取数据"""
        if not self.master_fd or not self.is_active:
            return ""
        
        try:
            ready, _, _ = select.select([self.master_fd], [], [], timeout)
            if ready:
                data = os.read(self.master_fd, 1024)
                return data.decode('utf-8', errors='ignore')
        except:
            pass
        return ""
    
    def close(self):
        """关闭终端会话"""
        self.is_active = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except:
                pass
        
        if self.slave_fd:
            try:
                os.close(self.slave_fd)
            except:
                pass

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'service': 'ClaudeEditor Terminal Server',
        'version': '1.0.0'
    })

@app.route('/api/platform/detect', methods=['GET'])
def detect_platform():
    """检测服务器平台"""
    import platform
    
    system = platform.system().lower()
    machine = platform.machine()
    
    platform_info = {
        'system': system,
        'machine': machine,
        'python_version': platform.python_version(),
        'supported_shells': []
    }
    
    # 检测可用的shell
    shells = ['/bin/bash', '/bin/sh', '/bin/zsh', '/bin/fish']
    for shell in shells:
        if os.path.exists(shell):
            platform_info['supported_shells'].append(shell)
    
    return jsonify(platform_info)

@app.route('/api/terminal/create', methods=['POST'])
def create_terminal():
    """创建新的终端会话"""
    data = request.get_json() or {}
    platform = data.get('platform', 'linux')
    
    session_id = str(uuid.uuid4())
    terminal = TerminalSession(session_id, platform)
    
    if terminal.start():
        active_terminals[session_id] = {
            'terminal': terminal,
            'created_at': asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 0
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'终端会话 {session_id} 创建成功'
        })
    else:
        return jsonify({
            'success': False,
            'error': '终端会话创建失败'
        }), 500

@app.route('/api/terminal/<session_id>/command', methods=['POST'])
def execute_command(session_id: str):
    """在指定终端会话中执行命令"""
    if session_id not in active_terminals:
        return jsonify({'success': False, 'error': '终端会话不存在'}), 404
    
    data = request.get_json() or {}
    command = data.get('command', '')
    
    if not command:
        return jsonify({'success': False, 'error': '命令不能为空'}), 400
    
    terminal = active_terminals[session_id]['terminal']
    
    # 发送命令到终端
    if terminal.write(command + '\n'):
        # 等待输出
        import time
        time.sleep(0.5)
        output = terminal.read(timeout=2.0)
        
        return jsonify({
            'success': True,
            'output': output,
            'command': command
        })
    else:
        return jsonify({
            'success': False,
            'error': '命令执行失败'
        }), 500

@app.route('/api/terminal/<session_id>/close', methods=['POST'])
def close_terminal(session_id: str):
    """关闭终端会话"""
    if session_id not in active_terminals:
        return jsonify({'success': False, 'error': '终端会话不存在'}), 404
    
    terminal = active_terminals[session_id]['terminal']
    terminal.close()
    del active_terminals[session_id]
    
    return jsonify({
        'success': True,
        'message': f'终端会话 {session_id} 已关闭'
    })

@app.route('/api/file/browse', methods=['POST'])
def browse_files():
    """浏览文件系统"""
    data = request.get_json() or {}
    path = data.get('path', os.getcwd())
    
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return jsonify({'success': False, 'error': '路径不存在'}), 404
        
        if not path_obj.is_dir():
            return jsonify({'success': False, 'error': '不是有效的目录'}), 400
        
        items = []
        for item in path_obj.iterdir():
            try:
                stat = item.stat()
                items.append({
                    'name': item.name,
                    'path': str(item),
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': stat.st_size if item.is_file() else 0,
                    'modified': stat.st_mtime
                })
            except:
                continue
        
        # 按类型和名称排序
        items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        
        return jsonify({
            'success': True,
            'path': str(path_obj),
            'items': items
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/git/clone', methods=['POST'])
def git_clone():
    """执行Git克隆操作"""
    data = request.get_json() or {}
    repo_url = data.get('url', '')
    target_dir = data.get('target_dir', '/tmp')
    shallow = data.get('shallow', False)
    
    if not repo_url:
        return jsonify({'success': False, 'error': 'Git仓库URL不能为空'}), 400
    
    try:
        # 构建git clone命令
        cmd = ['git', 'clone']
        if shallow:
            cmd.extend(['--depth', '1'])
        cmd.extend([repo_url])
        
        # 如果指定了目标目录，添加到命令中
        if target_dir != '/tmp':
            cmd.append(target_dir)
        
        # 执行git clone
        result = subprocess.run(
            cmd,
            cwd='/tmp',
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Git仓库克隆成功',
                'output': result.stdout,
                'command': ' '.join(cmd)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or 'Git克隆失败',
                'command': ' '.join(cmd)
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Git克隆超时（超过5分钟）'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Git克隆失败: {str(e)}'
        }), 500

@app.route('/api/ssh/test', methods=['POST'])
def test_ssh_connection():
    """测试SSH连接"""
    data = request.get_json() or {}
    host = data.get('host', '')
    user = data.get('user', '')
    port = data.get('port', 22)
    
    if not host or not user:
        return jsonify({'success': False, 'error': '主机地址和用户名不能为空'}), 400
    
    try:
        # 使用ssh命令测试连接（只测试连接性，不实际登录）
        cmd = [
            'ssh',
            '-o', 'ConnectTimeout=10',
            '-o', 'BatchMode=yes',
            '-o', 'StrictHostKeyChecking=no',
            '-p', str(port),
            f'{user}@{host}',
            'echo "connection_test"'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        # 注意：由于没有密钥，连接会失败，但我们可以从错误信息判断主机是否可达
        if 'connection_test' in result.stdout:
            return jsonify({
                'success': True,
                'message': 'SSH连接测试成功',
                'reachable': True
            })
        elif 'Connection refused' in result.stderr:
            return jsonify({
                'success': False,
                'message': 'SSH服务未运行或端口不正确',
                'reachable': False
            })
        elif 'No route to host' in result.stderr or 'Name or service not known' in result.stderr:
            return jsonify({
                'success': False,
                'message': '主机不可达或域名解析失败',
                'reachable': False
            })
        else:
            # 其他错误（如认证失败）表示主机可达但需要正确的认证
            return jsonify({
                'success': True,
                'message': '主机可达，需要正确的SSH密钥进行认证',
                'reachable': True,
                'auth_required': True
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'SSH连接测试超时',
            'reachable': False
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'SSH连接测试失败: {str(e)}',
            'reachable': False
        })

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    """WebSocket连接建立"""
    print(f'客户端已连接: {request.sid}')
    emit('connected', {'message': '终端服务器连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket连接断开"""
    print(f'客户端已断开: {request.sid}')

@socketio.on('terminal_input')
def handle_terminal_input(data):
    """处理终端输入"""
    session_id = data.get('session_id')
    input_data = data.get('input', '')
    
    if session_id in active_terminals:
        terminal = active_terminals[session_id]['terminal']
        if terminal.write(input_data):
            # 读取输出并发送回客户端
            output = terminal.read()
            if output:
                emit('terminal_output', {
                    'session_id': session_id,
                    'output': output
                })

def cleanup_inactive_terminals():
    """清理不活跃的终端会话"""
    import time
    current_time = time.time()
    
    inactive_sessions = []
    for session_id, session_data in active_terminals.items():
        # 如果会话超过1小时未活动，标记为清理
        if current_time - session_data.get('created_at', 0) > 3600:
            inactive_sessions.append(session_id)
    
    for session_id in inactive_sessions:
        try:
            terminal = active_terminals[session_id]['terminal']
            terminal.close()
            del active_terminals[session_id]
            print(f'清理不活跃的终端会话: {session_id}')
        except:
            pass

if __name__ == '__main__':
    print("🚀 启动 ClaudeEditor Terminal Server...")
    print("📡 支持的功能:")
    print("   - 真实终端连接和命令执行")
    print("   - WebSocket实时交互")
    print("   - 文件系统浏览")
    print("   - Git仓库克隆")
    print("   - SSH连接测试")
    print("🌐 服务地址: http://0.0.0.0:5000")
    
    # 启动清理任务
    import threading
    cleanup_thread = threading.Thread(target=lambda: [
        __import__('time').sleep(300),  # 每5分钟清理一次
        cleanup_inactive_terminals()
    ])
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    # 启动服务器
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

