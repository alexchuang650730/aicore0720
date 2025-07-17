#!/usr/bin/env python3
"""
File System Adapter - 文件系统适配器
基于 local_adapter_mcp 扩展，支持本地 folder 管理和 Claude Code tool 集成
"""

import asyncio
import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

logger = logging.getLogger(__name__)

class ClaudeCodeOutputHandler(FileSystemEventHandler):
    """Claude Code 输出监听器"""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.claude_patterns = [
            '.md', '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css',
            '.json', '.yaml', '.yml', '.txt', '.sh', '.bat'
        ]
        self.release_patterns = [
            'dist/', 'build/', 'release/', 'deploy/', '.zip', '.tar.gz'
        ]
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_event('created', event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_event('modified', event.src_path)
    
    def _handle_file_event(self, event_type: str, file_path: str):
        """处理文件事件"""
        try:
            file_info = self._analyze_file(file_path)
            if file_info:
                asyncio.create_task(self.callback(event_type, file_info))
        except Exception as e:
            logger.error(f"处理文件事件失败: {e}")
    
    def _analyze_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """分析文件类型和内容"""
        path = Path(file_path)
        
        # 检查是否为 Claude Code 生成的文件
        if not any(str(path).endswith(pattern) for pattern in self.claude_patterns):
            return None
        
        # 检查是否为 release 文件
        is_release = any(pattern in str(path) for pattern in self.release_patterns)
        
        try:
            stat = path.stat()
            return {
                'path': str(path),
                'name': path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': 'release' if is_release else 'file',
                'extension': path.suffix,
                'is_claude_generated': True,
                'content_preview': self._get_content_preview(path) if not is_release else None
            }
        except Exception as e:
            logger.error(f"分析文件失败 {file_path}: {e}")
            return None
    
    def _get_content_preview(self, path: Path, max_lines: int = 10) -> str:
        """获取文件内容预览"""
        try:
            if path.suffix in ['.md', '.txt', '.py', '.js', '.jsx', '.ts', '.tsx']:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:max_lines]
                    return ''.join(lines)
        except Exception:
            pass
        return ""

class FileSystemAdapter:
    """文件系统适配器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.watched_folders = {}
        self.observers = {}
        self.file_cache = {}
        self.claude_output_callbacks = []
        
    async def initialize(self):
        """初始化文件系统适配器"""
        self.logger.info("🗂️ 初始化文件系统适配器")
        
        # 导入 local_adapter_manager
        try:
            from .local_adapter_manager import local_adapter_mcp
            self.local_adapter = local_adapter_mcp
            await self.local_adapter.initialize()
        except Exception as e:
            self.logger.error(f"导入 local_adapter_manager 失败: {e}")
            
        self.logger.info("✅ 文件系统适配器初始化完成")
    
    async def connect_local_folder(self, folder_path: str, watch_changes: bool = True) -> Dict[str, Any]:
        """连接本地文件夹"""
        try:
            path = Path(folder_path).resolve()
            
            if not path.exists():
                return {
                    'success': False,
                    'error': f'文件夹不存在: {folder_path}'
                }
            
            if not path.is_dir():
                return {
                    'success': False,
                    'error': f'路径不是文件夹: {folder_path}'
                }
            
            folder_id = str(path)
            
            # 扫描文件夹
            files = await self._scan_folder(path)
            
            # 缓存文件信息
            self.file_cache[folder_id] = {
                'path': str(path),
                'files': files,
                'last_scan': datetime.now().isoformat(),
                'watch_enabled': watch_changes
            }
            
            # 启动文件监听
            if watch_changes:
                await self._start_folder_watch(path, folder_id)
            
            self.logger.info(f"📁 已连接文件夹: {folder_path} ({len(files)} 个文件)")
            
            return {
                'success': True,
                'folder_id': folder_id,
                'path': str(path),
                'file_count': len(files),
                'files': files[:20],  # 返回前20个文件
                'watch_enabled': watch_changes
            }
            
        except Exception as e:
            self.logger.error(f"连接文件夹失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _scan_folder(self, path: Path, max_depth: int = 3, current_depth: int = 0) -> List[Dict[str, Any]]:
        """扫描文件夹内容"""
        files = []
        
        if current_depth >= max_depth:
            return files
        
        try:
            for item in path.iterdir():
                try:
                    stat = item.stat()
                    
                    file_info = {
                        'name': item.name,
                        'path': str(item),
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': stat.st_size if item.is_file() else 0,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'extension': item.suffix if item.is_file() else '',
                        'icon': self._get_file_icon(item),
                        'language': self._detect_language(item) if item.is_file() else None
                    }
                    
                    # 如果是目录，递归扫描
                    if item.is_dir() and current_depth < max_depth - 1:
                        file_info['children'] = await self._scan_folder(item, max_depth, current_depth + 1)
                    
                    files.append(file_info)
                    
                except (PermissionError, OSError) as e:
                    self.logger.warning(f"无法访问 {item}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"扫描文件夹失败 {path}: {e}")
        
        # 排序：目录在前，文件在后
        files.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        return files
    
    def _get_file_icon(self, path: Path) -> str:
        """获取文件图标"""
        if path.is_dir():
            return '📁'
        
        extension = path.suffix.lower()
        icon_map = {
            '.py': '🐍', '.js': '📄', '.jsx': '⚛️', '.ts': '📘', '.tsx': '⚛️',
            '.html': '🌐', '.css': '🎨', '.scss': '🎨', '.sass': '🎨',
            '.json': '📋', '.yaml': '📋', '.yml': '📋', '.xml': '📋',
            '.md': '📖', '.txt': '📄', '.pdf': '📕', '.doc': '📄', '.docx': '📄',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
            '.mp4': '🎬', '.avi': '🎬', '.mov': '🎬', '.mp3': '🎵', '.wav': '🎵',
            '.zip': '📦', '.tar': '📦', '.gz': '📦', '.rar': '📦',
            '.sh': '⚡', '.bat': '⚡', '.cmd': '⚡',
            '.git': '🔧', '.gitignore': '🙈', '.env': '⚙️',
            '.log': '📊', '.sql': '🗄️', '.db': '🗄️'
        }
        
        return icon_map.get(extension, '📄')
    
    def _detect_language(self, path: Path) -> Optional[str]:
        """检测文件语言"""
        extension = path.suffix.lower()
        language_map = {
            '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.html': 'html', '.css': 'css', '.scss': 'scss', '.sass': 'sass',
            '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml', '.xml': 'xml',
            '.md': 'markdown', '.txt': 'text',
            '.sh': 'bash', '.bat': 'batch', '.cmd': 'batch',
            '.sql': 'sql', '.php': 'php', '.java': 'java', '.cpp': 'cpp',
            '.c': 'c', '.go': 'go', '.rs': 'rust', '.rb': 'ruby'
        }
        
        return language_map.get(extension)
    
    async def _start_folder_watch(self, path: Path, folder_id: str):
        """启动文件夹监听"""
        try:
            if folder_id in self.observers:
                self.observers[folder_id].stop()
            
            # 创建事件处理器
            handler = ClaudeCodeOutputHandler(
                callback=lambda event_type, file_info: self._handle_claude_output(folder_id, event_type, file_info)
            )
            
            # 创建观察者
            observer = Observer()
            observer.schedule(handler, str(path), recursive=True)
            observer.start()
            
            self.observers[folder_id] = observer
            self.logger.info(f"👀 开始监听文件夹: {path}")
            
        except Exception as e:
            self.logger.error(f"启动文件夹监听失败: {e}")
    
    async def _handle_claude_output(self, folder_id: str, event_type: str, file_info: Dict[str, Any]):
        """处理 Claude Code 输出"""
        try:
            self.logger.info(f"🔍 检测到 Claude Code 输出: {file_info['name']} ({event_type})")
            
            # 更新文件缓存
            if folder_id in self.file_cache:
                # 重新扫描文件夹
                path = Path(self.file_cache[folder_id]['path'])
                files = await self._scan_folder(path)
                self.file_cache[folder_id]['files'] = files
                self.file_cache[folder_id]['last_scan'] = datetime.now().isoformat()
            
            # 通知所有回调函数
            for callback in self.claude_output_callbacks:
                try:
                    await callback(folder_id, event_type, file_info)
                except Exception as e:
                    self.logger.error(f"回调函数执行失败: {e}")
                    
        except Exception as e:
            self.logger.error(f"处理 Claude Code 输出失败: {e}")
    
    def register_claude_output_callback(self, callback: Callable):
        """注册 Claude Code 输出回调"""
        self.claude_output_callbacks.append(callback)
    
    async def get_file_content(self, file_path: str) -> Dict[str, Any]:
        """获取文件内容"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    'success': False,
                    'error': f'文件不存在: {file_path}'
                }
            
            if not path.is_file():
                return {
                    'success': False,
                    'error': f'路径不是文件: {file_path}'
                }
            
            # 读取文件内容
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(path, 'r', encoding='gbk') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    return {
                        'success': False,
                        'error': '无法读取文件内容（编码问题）'
                    }
            
            stat = path.stat()
            
            return {
                'success': True,
                'path': str(path),
                'name': path.name,
                'content': content,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': path.suffix,
                'language': self._detect_language(path),
                'lines': len(content.splitlines())
            }
            
        except Exception as e:
            self.logger.error(f"读取文件内容失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def save_file_content(self, file_path: str, content: str) -> Dict[str, Any]:
        """保存文件内容"""
        try:
            path = Path(file_path)
            
            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"💾 已保存文件: {file_path}")
            
            return {
                'success': True,
                'path': str(path),
                'size': len(content.encode('utf-8')),
                'lines': len(content.splitlines())
            }
            
        except Exception as e:
            self.logger.error(f"保存文件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_folder_files(self, folder_id: str) -> Dict[str, Any]:
        """获取文件夹文件列表"""
        if folder_id not in self.file_cache:
            return {
                'success': False,
                'error': f'文件夹未连接: {folder_id}'
            }
        
        cache = self.file_cache[folder_id]
        return {
            'success': True,
            'folder_id': folder_id,
            'path': cache['path'],
            'files': cache['files'],
            'file_count': len(cache['files']),
            'last_scan': cache['last_scan'],
            'watch_enabled': cache['watch_enabled']
        }
    
    async def refresh_folder(self, folder_id: str) -> Dict[str, Any]:
        """刷新文件夹"""
        if folder_id not in self.file_cache:
            return {
                'success': False,
                'error': f'文件夹未连接: {folder_id}'
            }
        
        try:
            path = Path(self.file_cache[folder_id]['path'])
            files = await self._scan_folder(path)
            
            self.file_cache[folder_id]['files'] = files
            self.file_cache[folder_id]['last_scan'] = datetime.now().isoformat()
            
            return {
                'success': True,
                'folder_id': folder_id,
                'file_count': len(files),
                'files': files
            }
            
        except Exception as e:
            self.logger.error(f"刷新文件夹失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            'component': 'File System Adapter',
            'connected_folders': len(self.file_cache),
            'active_watchers': len(self.observers),
            'claude_callbacks': len(self.claude_output_callbacks),
            'folders': [
                {
                    'id': folder_id,
                    'path': cache['path'],
                    'file_count': len(cache['files']),
                    'watch_enabled': cache['watch_enabled'],
                    'last_scan': cache['last_scan']
                }
                for folder_id, cache in self.file_cache.items()
            ]
        }
    
    async def cleanup(self):
        """清理资源"""
        for observer in self.observers.values():
            observer.stop()
            observer.join()
        
        self.observers.clear()
        self.file_cache.clear()
        self.claude_output_callbacks.clear()
        
        self.logger.info("🧹 文件系统适配器已清理")

# 全局实例
file_system_adapter = FileSystemAdapter()

