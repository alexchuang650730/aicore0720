#!/usr/bin/env python3
"""
清理冗餘代碼工具
移除項目中無用的文件和目錄
"""

import os
import shutil
from pathlib import Path
from typing import List, Set
import json
from datetime import datetime

class RedundantCodeCleaner:
    def __init__(self):
        self.to_remove = []
        self.removed = []
        self.errors = []
        
        # 定義要清理的模式
        self.redundant_patterns = {
            'directories': [
                'mirrorcode',
                'mirror_code',
                'workflow',
                'workflows',
                'ai_assistants',
                'ai_assistant',
                '__pycache__',
                '.pytest_cache',
                'test_output',
                'temp',
                'tmp',
                'backup',
                'old',
                'deprecated'
            ],
            'files': [
                '*_backup.py',
                '*_old.py',
                '*_deprecated.py',
                '*_test_*.py',
                'test_*.py',
                '*.pyc',
                '.DS_Store',
                'Thumbs.db'
            ],
            'specific_files': [
                # 具體的冗餘文件
                'integrate_optimizations_to_mcp.py',
                'strengthen_mcp_architecture.py',
                'external_tools_mcp_integration.py',
                'advanced_tool_intelligence_system.py',
                'codeflow_spec_generator.py',  # 如果有 enhanced 版本
                'codeflow_enhanced_spec_generator.py'  # 重複功能
            ]
        }
        
    def analyze_project(self, project_root: str = "."):
        """分析項目中的冗餘代碼"""
        print("🔍 開始分析冗餘代碼...")
        
        root_path = Path(project_root)
        
        # 查找冗餘目錄
        for dir_pattern in self.redundant_patterns['directories']:
            for path in root_path.rglob(dir_pattern):
                if path.is_dir() and 'venv' not in str(path):
                    self.to_remove.append(('directory', path))
        
        # 查找冗餘文件
        for file_pattern in self.redundant_patterns['files']:
            for path in root_path.rglob(file_pattern):
                if path.is_file() and 'venv' not in str(path):
                    self.to_remove.append(('file', path))
        
        # 查找特定文件
        for file_name in self.redundant_patterns['specific_files']:
            file_path = root_path / file_name
            if file_path.exists():
                self.to_remove.append(('file', file_path))
        
        # 查找空目錄
        for path in root_path.rglob('*'):
            if path.is_dir() and not any(path.iterdir()) and 'venv' not in str(path):
                self.to_remove.append(('empty_dir', path))
        
        # 生成報告
        return self._generate_analysis_report()
    
    def _generate_analysis_report(self) -> str:
        """生成分析報告"""
        report = []
        report.append("=" * 80)
        report.append("冗餘代碼分析報告")
        report.append("=" * 80)
        report.append(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 統計
        dirs = [item for item in self.to_remove if item[0] == 'directory']
        files = [item for item in self.to_remove if item[0] == 'file']
        empty_dirs = [item for item in self.to_remove if item[0] == 'empty_dir']
        
        report.append("## 📊 統計")
        report.append(f"- 發現冗餘目錄: {len(dirs)} 個")
        report.append(f"- 發現冗餘文件: {len(files)} 個")
        report.append(f"- 發現空目錄: {len(empty_dirs)} 個")
        report.append(f"- 總計需要清理: {len(self.to_remove)} 項\n")
        
        # 詳細列表
        if dirs:
            report.append("## 📁 冗餘目錄")
            for _, path in dirs:
                size = self._get_dir_size(path)
                report.append(f"- {path} ({self._format_size(size)})")
        
        if files:
            report.append("\n## 📄 冗餘文件")
            for _, path in files[:20]:  # 只顯示前20個
                size = path.stat().st_size if path.exists() else 0
                report.append(f"- {path} ({self._format_size(size)})")
            if len(files) > 20:
                report.append(f"... 還有 {len(files) - 20} 個文件")
        
        if empty_dirs:
            report.append("\n## 📂 空目錄")
            for _, path in empty_dirs[:10]:
                report.append(f"- {path}")
            if len(empty_dirs) > 10:
                report.append(f"... 還有 {len(empty_dirs) - 10} 個空目錄")
        
        # 計算總大小
        total_size = sum(self._get_item_size(item) for item in self.to_remove)
        report.append(f"\n## 💾 空間回收")
        report.append(f"預計可回收空間: {self._format_size(total_size)}")
        
        return "\n".join(report)
    
    def clean(self, dry_run: bool = True):
        """執行清理"""
        if dry_run:
            print("\n🔍 模擬清理模式 (不會真正刪除)")
        else:
            print("\n🗑️ 開始清理冗餘代碼...")
        
        # 創建備份目錄
        backup_dir = Path(f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if not dry_run:
            backup_dir.mkdir(exist_ok=True)
        
        for item_type, path in self.to_remove:
            try:
                if dry_run:
                    print(f"[模擬] 將刪除 {item_type}: {path}")
                else:
                    # 備份
                    backup_path = backup_dir / path.relative_to('.')
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if path.is_dir():
                        shutil.copytree(path, backup_path)
                        shutil.rmtree(path)
                    else:
                        shutil.copy2(path, backup_path)
                        path.unlink()
                    
                    self.removed.append((item_type, str(path)))
                    print(f"✅ 已刪除 {item_type}: {path}")
                    
            except Exception as e:
                self.errors.append((str(path), str(e)))
                print(f"❌ 刪除失敗 {path}: {e}")
        
        # 生成清理報告
        if not dry_run:
            self._save_cleanup_report(backup_dir)
    
    def _get_dir_size(self, path: Path) -> int:
        """獲取目錄大小"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            pass
        return total
    
    def _get_item_size(self, item: tuple) -> int:
        """獲取項目大小"""
        _, path = item
        if path.is_dir():
            return self._get_dir_size(path)
        elif path.is_file() and path.exists():
            return path.stat().st_size
        return 0
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _save_cleanup_report(self, backup_dir: Path):
        """保存清理報告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'removed': self.removed,
            'errors': self.errors,
            'backup_location': str(backup_dir)
        }
        
        with open('cleanup_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 清理報告已保存: cleanup_report.json")
        print(f"🗂️ 備份位置: {backup_dir}")

def main():
    """主函數"""
    cleaner = RedundantCodeCleaner()
    
    # 分析
    report = cleaner.analyze_project()
    print(report)
    
    # 保存分析報告
    with open('redundant_code_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("\n📄 分析報告已保存: redundant_code_analysis.txt")
    
    # 詢問是否清理
    if cleaner.to_remove:
        print("\n" + "=" * 60)
        response = input("\n是否執行清理? (y/n/dry): ").lower()
        
        if response == 'y':
            cleaner.clean(dry_run=False)
        elif response == 'dry':
            cleaner.clean(dry_run=True)
        else:
            print("已取消清理")

if __name__ == "__main__":
    main()