"""
Claude Code Release 監聽系統
監聽 Claude Code 輸出，自動分類文件和項目
整合快速操作區、Monaco Editor 和演示系統
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import mimetypes
import logging

logger = logging.getLogger(__name__)

class ReleaseType(Enum):
    """Release 類型"""
    SINGLE_FILE = "single_file"        # 單個文件
    PROJECT = "project"                # 完整項目
    CODE_SNIPPET = "code_snippet"     # 代碼片段
    DOCUMENTATION = "documentation"   # 文檔
    CONFIGURATION = "configuration"   # 配置文件
    DEPLOYMENT = "deployment"         # 部署相關

class FileCategory(Enum):
    """文件類別"""
    CODE = "code"                     # 代碼文件
    MARKUP = "markup"                 # 標記語言
    CONFIG = "config"                 # 配置文件
    DATA = "data"                     # 數據文件
    MEDIA = "media"                   # 媒體文件
    DOCUMENT = "document"             # 文檔
    UNKNOWN = "unknown"               # 未知類型

@dataclass
class ClaudeCodeRelease:
    """Claude Code Release 對象"""
    release_id: str
    release_type: ReleaseType
    title: str
    description: str
    file_paths: List[str]
    main_file: Optional[str]
    project_root: Optional[str]
    created_at: float
    metadata: Dict[str, Any]
    is_deployable: bool
    demo_config: Optional[Dict[str, Any]]

@dataclass
class FileInfo:
    """文件信息"""
    file_path: str
    file_name: str
    file_category: FileCategory
    file_size: int
    modified_at: float
    language: Optional[str]
    is_executable: bool
    preview_content: str

class ClaudeCodeReleaseMonitor:
    """Claude Code Release 監聽器"""
    
    def __init__(self, monitor_paths: List[str] = None):
        self.monitor_paths = monitor_paths or [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
            os.getcwd()
        ]
        
        self.recent_files: List[FileInfo] = []
        self.deployable_projects: List[ClaudeCodeRelease] = []
        self.file_watchers: List[Observer] = []
        
        # 文件類型映射
        self.language_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bat': 'batch',
            '.ps1': 'powershell',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        # 項目文件指標
        self.project_indicators = [
            'package.json',
            'requirements.txt',
            'Cargo.toml',
            'pom.xml',
            'build.gradle',
            'Dockerfile',
            'docker-compose.yml',
            'README.md',
            '.gitignore'
        ]
        
        logger.info("🚀 Claude Code Release Monitor 初始化完成")
    
    async def start_monitoring(self) -> None:
        """開始監聽"""
        
        for path in self.monitor_paths:
            if os.path.exists(path):
                observer = Observer()
                handler = ClaudeCodeFileHandler(self)
                observer.schedule(handler, path, recursive=True)
                observer.start()
                self.file_watchers.append(observer)
                logger.info(f"📁 開始監聽目錄: {path}")
        
        # 初始掃描現有文件
        await self._initial_scan()
    
    async def stop_monitoring(self) -> None:
        """停止監聽"""
        
        for observer in self.file_watchers:
            observer.stop()
            observer.join()
        
        self.file_watchers.clear()
        logger.info("⏹️ 停止文件監聽")
    
    async def _initial_scan(self) -> None:
        """初始掃描"""
        
        logger.info("🔍 執行初始文件掃描...")
        
        for path in self.monitor_paths:
            if os.path.exists(path):
                await self._scan_directory(path)
        
        logger.info(f"✅ 初始掃描完成，發現 {len(self.recent_files)} 個文件")
    
    async def _scan_directory(self, directory: str) -> None:
        """掃描目錄"""
        
        try:
            for root, dirs, files in os.walk(directory):
                # 跳過隱藏目錄和常見的忽略目錄
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'dist', 'build']]
                
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        await self._process_file(file_path, is_new=False)
        
        except Exception as e:
            logger.error(f"掃描目錄失敗 {directory}: {e}")
    
    async def handle_file_event(self, file_path: str, event_type: str) -> None:
        """處理文件事件"""
        
        if event_type in ['created', 'modified']:
            await self._process_file(file_path, is_new=(event_type == 'created'))
        elif event_type == 'deleted':
            await self._remove_file(file_path)
    
    async def _process_file(self, file_path: str, is_new: bool = True) -> None:
        """處理文件"""
        
        try:
            if not os.path.exists(file_path) or os.path.isdir(file_path):
                return
            
            # 創建文件信息
            file_info = await self._create_file_info(file_path)
            
            # 添加到最近文件列表
            await self._add_to_recent_files(file_info)
            
            # 檢查是否為項目的一部分
            if is_new:
                await self._check_for_project(file_path)
            
            # 通知 ClaudeEditor 更新
            await self._notify_claudeditor_update(file_info, is_new)
            
            logger.info(f"{'🆕' if is_new else '📝'} 處理文件: {file_info.file_name}")
        
        except Exception as e:
            logger.error(f"處理文件失敗 {file_path}: {e}")
    
    async def _create_file_info(self, file_path: str) -> FileInfo:
        """創建文件信息"""
        
        stat = os.stat(file_path)
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # 確定文件類別
        file_category = self._determine_file_category(file_ext, file_name)
        
        # 確定編程語言
        language = self.language_extensions.get(file_ext)
        
        # 讀取預覽內容
        preview_content = await self._read_preview_content(file_path)
        
        return FileInfo(
            file_path=file_path,
            file_name=file_name,
            file_category=file_category,
            file_size=stat.st_size,
            modified_at=stat.st_mtime,
            language=language,
            is_executable=os.access(file_path, os.X_OK),
            preview_content=preview_content
        )
    
    def _determine_file_category(self, file_ext: str, file_name: str) -> FileCategory:
        """確定文件類別"""
        
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt'}
        markup_extensions = {'.html', '.xml', '.md', '.rst'}
        config_extensions = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}
        data_extensions = {'.csv', '.tsv', '.sql', '.db', '.sqlite'}
        media_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.mp4', '.mp3', '.wav'}
        document_extensions = {'.txt', '.pdf', '.doc', '.docx', '.rtf'}
        
        if file_ext in code_extensions:
            return FileCategory.CODE
        elif file_ext in markup_extensions:
            return FileCategory.MARKUP
        elif file_ext in config_extensions or file_name in ['Dockerfile', 'Makefile']:
            return FileCategory.CONFIG
        elif file_ext in data_extensions:
            return FileCategory.DATA
        elif file_ext in media_extensions:
            return FileCategory.MEDIA
        elif file_ext in document_extensions:
            return FileCategory.DOCUMENT
        else:
            return FileCategory.UNKNOWN
    
    async def _read_preview_content(self, file_path: str, max_chars: int = 500) -> str:
        """讀取預覽內容"""
        
        try:
            # 檢查文件是否為文本文件
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and not mime_type.startswith('text'):
                return f"[二進制文件: {mime_type}]"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_chars)
                if len(content) >= max_chars:
                    content += "..."
                return content
        
        except Exception as e:
            return f"[無法讀取: {str(e)}]"
    
    async def _add_to_recent_files(self, file_info: FileInfo) -> None:
        """添加到最近文件列表"""
        
        # 移除重複的文件
        self.recent_files = [f for f in self.recent_files if f.file_path != file_info.file_path]
        
        # 添加到列表開頭
        self.recent_files.insert(0, file_info)
        
        # 保持最近 50 個文件
        if len(self.recent_files) > 50:
            self.recent_files = self.recent_files[:50]
    
    async def _check_for_project(self, file_path: str) -> None:
        """檢查是否為項目"""
        
        directory = os.path.dirname(file_path)
        
        # 檢查目錄中是否有項目指標文件
        has_project_indicators = False
        for indicator in self.project_indicators:
            if os.path.exists(os.path.join(directory, indicator)):
                has_project_indicators = True
                break
        
        if has_project_indicators:
            await self._create_project_release(directory)
    
    async def _create_project_release(self, project_root: str) -> None:
        """創建項目 Release"""
        
        # 檢查是否已經存在
        existing_project = next(
            (p for p in self.deployable_projects if p.project_root == project_root),
            None
        )
        
        if existing_project:
            return  # 已存在，不重複創建
        
        # 分析項目
        project_analysis = await self._analyze_project(project_root)
        
        release = ClaudeCodeRelease(
            release_id=f"project_{int(time.time())}",
            release_type=ReleaseType.PROJECT,
            title=project_analysis["name"],
            description=project_analysis["description"],
            file_paths=project_analysis["files"],
            main_file=project_analysis.get("main_file"),
            project_root=project_root,
            created_at=time.time(),
            metadata=project_analysis["metadata"],
            is_deployable=project_analysis["is_deployable"],
            demo_config=project_analysis.get("demo_config")
        )
        
        self.deployable_projects.append(release)
        
        # 通知 ClaudeEditor
        await self._notify_claudeditor_project_update(release)
        
        logger.info(f"🚀 發現新項目: {release.title}")
    
    async def _analyze_project(self, project_root: str) -> Dict[str, Any]:
        """分析項目"""
        
        project_name = os.path.basename(project_root)
        project_files = []
        main_file = None
        is_deployable = False
        demo_config = None
        
        # 掃描項目文件
        for root, dirs, files in os.walk(project_root):
            # 跳過隱藏目錄和 node_modules 等
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'dist', 'build']]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    project_files.append(file_path)
        
        # 確定主文件
        main_candidates = ['index.html', 'index.js', 'main.py', 'app.py', 'server.js', 'app.js']
        for candidate in main_candidates:
            candidate_path = os.path.join(project_root, candidate)
            if os.path.exists(candidate_path):
                main_file = candidate_path
                break
        
        # 檢查是否可部署
        deployment_indicators = ['package.json', 'requirements.txt', 'Dockerfile', 'index.html']
        for indicator in deployment_indicators:
            if os.path.exists(os.path.join(project_root, indicator)):
                is_deployable = True
                break
        
        # 生成演示配置
        if is_deployable:
            demo_config = await self._generate_demo_config(project_root)
        
        # 讀取項目描述
        description = await self._extract_project_description(project_root)
        
        return {
            "name": project_name,
            "description": description,
            "files": project_files,
            "main_file": main_file,
            "is_deployable": is_deployable,
            "demo_config": demo_config,
            "metadata": {
                "file_count": len(project_files),
                "project_type": self._detect_project_type(project_root),
                "technologies": self._detect_technologies(project_files)
            }
        }
    
    async def _generate_demo_config(self, project_root: str) -> Dict[str, Any]:
        """生成演示配置"""
        
        demo_config = {
            "type": "web_app",
            "entry_point": None,
            "build_command": None,
            "start_command": None,
            "port": 3000,
            "environment": {}
        }
        
        # 檢查 package.json
        package_json_path = os.path.join(project_root, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                    scripts = package_data.get('scripts', {})
                    demo_config["build_command"] = scripts.get('build', 'npm run build')
                    demo_config["start_command"] = scripts.get('start', 'npm start')
                    demo_config["entry_point"] = package_data.get('main', 'index.js')
            except:
                pass
        
        # 檢查 Python 項目
        if os.path.exists(os.path.join(project_root, 'requirements.txt')):
            demo_config["type"] = "python_app"
            demo_config["start_command"] = "python app.py"
            demo_config["port"] = 5000
        
        # 檢查靜態網站
        if os.path.exists(os.path.join(project_root, 'index.html')):
            demo_config["type"] = "static_site"
            demo_config["entry_point"] = "index.html"
            demo_config["start_command"] = "python -m http.server 8000"
            demo_config["port"] = 8000
        
        return demo_config
    
    async def _extract_project_description(self, project_root: str) -> str:
        """提取項目描述"""
        
        # 嘗試從 README 文件中提取
        readme_files = ['README.md', 'README.txt', 'README.rst', 'README']
        for readme_file in readme_files:
            readme_path = os.path.join(project_root, readme_file)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(500)  # 讀取前 500 字符
                        # 提取第一段作為描述
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                return line
                except:
                    continue
        
        # 嘗試從 package.json 中提取
        package_json_path = os.path.join(project_root, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    return package_data.get('description', '無描述')
            except:
                pass
        
        return f"Claude Code 生成的項目 - {os.path.basename(project_root)}"
    
    def _detect_project_type(self, project_root: str) -> str:
        """檢測項目類型"""
        
        if os.path.exists(os.path.join(project_root, 'package.json')):
            return "javascript"
        elif os.path.exists(os.path.join(project_root, 'requirements.txt')):
            return "python"
        elif os.path.exists(os.path.join(project_root, 'Cargo.toml')):
            return "rust"
        elif os.path.exists(os.path.join(project_root, 'pom.xml')):
            return "java"
        elif os.path.exists(os.path.join(project_root, 'go.mod')):
            return "go"
        elif os.path.exists(os.path.join(project_root, 'index.html')):
            return "static"
        else:
            return "unknown"
    
    def _detect_technologies(self, file_paths: List[str]) -> List[str]:
        """檢測技術棧"""
        
        technologies = set()
        
        for file_path in file_paths:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.js', '.jsx']:
                technologies.add('JavaScript')
            elif ext in ['.ts', '.tsx']:
                technologies.add('TypeScript')
            elif ext == '.py':
                technologies.add('Python')
            elif ext in ['.html']:
                technologies.add('HTML')
            elif ext in ['.css', '.scss', '.sass']:
                technologies.add('CSS')
            elif ext == '.rs':
                technologies.add('Rust')
            elif ext == '.java':
                technologies.add('Java')
            elif ext == '.go':
                technologies.add('Go')
        
        return list(technologies)
    
    async def _remove_file(self, file_path: str) -> None:
        """移除文件"""
        
        self.recent_files = [f for f in self.recent_files if f.file_path != file_path]
        
        # 通知 ClaudeEditor
        await self._notify_claudeditor_file_removed(file_path)
    
    async def _notify_claudeditor_update(self, file_info: FileInfo, is_new: bool) -> None:
        """通知 ClaudeEditor 更新"""
        
        # 這裡會通過 WebSocket 或其他方式通知 ClaudeEditor
        notification = {
            "type": "file_update",
            "is_new": is_new,
            "file_info": asdict(file_info),
            "timestamp": time.time()
        }
        
        logger.debug(f"通知 ClaudeEditor: {notification}")
    
    async def _notify_claudeditor_project_update(self, release: ClaudeCodeRelease) -> None:
        """通知 ClaudeEditor 項目更新"""
        
        notification = {
            "type": "project_update",
            "release": asdict(release),
            "timestamp": time.time()
        }
        
        logger.debug(f"通知 ClaudeEditor 項目: {notification}")
    
    async def _notify_claudeditor_file_removed(self, file_path: str) -> None:
        """通知 ClaudeEditor 文件移除"""
        
        notification = {
            "type": "file_removed",
            "file_path": file_path,
            "timestamp": time.time()
        }
        
        logger.debug(f"通知 ClaudeEditor 移除: {notification}")
    
    # API 方法
    async def get_recent_files(self, limit: int = 20) -> List[Dict[str, Any]]:
        """獲取最近文件列表"""
        
        return [asdict(f) for f in self.recent_files[:limit]]
    
    async def get_deployable_projects(self) -> List[Dict[str, Any]]:
        """獲取可部署項目列表"""
        
        return [asdict(p) for p in self.deployable_projects]
    
    async def open_file_in_monaco(self, file_path: str) -> Dict[str, Any]:
        """在 Monaco Editor 中打開文件"""
        
        try:
            file_info = await self._create_file_info(file_path)
            
            return {
                "success": True,
                "file_info": asdict(file_info),
                "editor_config": {
                    "language": file_info.language,
                    "theme": "vs-dark",
                    "readOnly": False,
                    "minimap": {"enabled": True},
                    "wordWrap": "on"
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_project_demo(self, project_id: str) -> Dict[str, Any]:
        """啟動項目演示"""
        
        project = next(
            (p for p in self.deployable_projects if p.release_id == project_id),
            None
        )
        
        if not project:
            return {"success": False, "error": "項目不存在"}
        
        if not project.is_deployable:
            return {"success": False, "error": "項目不可部署"}
        
        try:
            # 啟動演示服務
            demo_result = await self._start_demo_service(project)
            
            return {
                "success": True,
                "demo_url": demo_result["url"],
                "demo_port": demo_result["port"],
                "project_info": asdict(project)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_demo_service(self, project: ClaudeCodeRelease) -> Dict[str, Any]:
        """啟動演示服務"""
        
        demo_config = project.demo_config
        port = demo_config.get("port", 3000)
        
        # 這裡會實際啟動演示服務
        # 實際實現中需要根據項目類型執行相應的命令
        
        return {
            "url": f"http://localhost:{port}",
            "port": port,
            "status": "running"
        }

class ClaudeCodeFileHandler(FileSystemEventHandler):
    """文件系統事件處理器"""
    
    def __init__(self, monitor: ClaudeCodeReleaseMonitor):
        self.monitor = monitor
    
    def on_created(self, event):
        if not event.is_directory:
            asyncio.create_task(
                self.monitor.handle_file_event(event.src_path, "created")
            )
    
    def on_modified(self, event):
        if not event.is_directory:
            asyncio.create_task(
                self.monitor.handle_file_event(event.src_path, "modified")
            )
    
    def on_deleted(self, event):
        if not event.is_directory:
            asyncio.create_task(
                self.monitor.handle_file_event(event.src_path, "deleted")
            )

# 使用示例
async def main():
    """主函數示例"""
    
    # 創建監聽器
    monitor = ClaudeCodeReleaseMonitor([
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop"),
        os.getcwd()
    ])
    
    # 開始監聽
    await monitor.start_monitoring()
    
    print("🚀 Claude Code Release Monitor 已啟動")
    print("📁 監聽 Claude Code 輸出文件...")
    
    try:
        # 運行一段時間來測試
        await asyncio.sleep(10)
        
        # 獲取最近文件
        recent_files = await monitor.get_recent_files(10)
        print(f"\n📄 最近文件 ({len(recent_files)}):")
        for file_info in recent_files:
            print(f"  - {file_info['file_name']} ({file_info['file_category']})")
        
        # 獲取可部署項目
        projects = await monitor.get_deployable_projects()
        print(f"\n🚀 可部署項目 ({len(projects)}):")
        for project in projects:
            print(f"  - {project['title']} ({project['metadata']['project_type']})")
    
    finally:
        await monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())