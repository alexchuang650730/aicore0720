#!/usr/bin/env python3
"""
執行 MCP 清理計劃
移除所有未集成到六大工作流的 MCP 和冗餘代碼
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set

class MCPWorkflowIntegrationExecutor:
    """MCP 工作流集成執行器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / f"backup_mcp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.cleanup_log = []
        
        # P0 核心 MCP（必須保留）
        self.p0_core_mcps = {
            "memoryos_mcp",
            "aws_bedrock_mcp",  # AWS RAG 核心組件
            "enhanced_command_mcp", 
            "mcp_coordinator_mcp",
            "claude_router_mcp",
            "local_adapter_mcp",
            "command_mcp",
            "smartui_mcp",
            "ag_ui_mcp"
        }
        
        # P1 工作流 MCP（必須集成到工作流）
        self.p1_workflow_mcps = {
            "codeflow_mcp",
            "test_mcp",
            "zen_mcp",
            "xmasters_mcp",
            "stagewise_mcp"
        }
        
        # 要移除的 MCP（排除與 ClaudeEditor 相關的）
        self.mcps_to_remove = {
            "intelligent_error_handler_mcp",
            "collaboration_mcp",
            "operations_mcp",
            "security_mcp",
            "config_mcp",
            "monitoring_mcp"
        }
        
        # ClaudeEditor 相關文件（絕對不能刪除）
        self.claudeditor_protected_patterns = [
            "**/claudeditor/**",
            "**/claudeditor_*",
            "**/ClaudeEditor*",
            "**/claude_editor*",
            "**/smartui_mcp/**",  # SmartUI 用於 ClaudeEditor UI
            "**/ag_ui_mcp/**"     # AG-UI 用於 ClaudeEditor 適應性
        ]
        
        # 要移除的冗餘文件
        self.redundant_files = [
            "core/data_collection_system.py",
            "core/deployment/multi_platform_deployer.py",
            "core/performance_optimization_system.py",
            "core/intelligent_context_enhancement.py",
            "core/learning_integration.py"
        ]
    
    def execute_cleanup(self):
        """執行清理計劃"""
        print("🧹 開始執行 MCP 工作流集成清理...")
        print("=" * 70)
        
        # 1. 創建備份
        self._create_backup()
        
        # 2. 移除未集成的 MCP
        self._remove_non_integrated_mcps()
        
        # 3. 移除冗餘文件
        self._remove_redundant_files()
        
        # 4. 清理空目錄
        self._cleanup_empty_directories()
        
        # 5. 更新 import 語句
        self._update_imports()
        
        # 6. 生成清理報告
        self._generate_cleanup_report()
        
        print("\n✅ MCP 工作流集成清理完成！")
    
    def _create_backup(self):
        """創建備份"""
        print(f"\n📦 創建備份: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 備份要刪除的 MCP
        components_dir = self.project_root / "core" / "components"
        for mcp in self.mcps_to_remove:
            mcp_path = components_dir / mcp
            if mcp_path.exists():
                backup_path = self.backup_dir / "components" / mcp
                shutil.copytree(mcp_path, backup_path)
                self.cleanup_log.append(f"備份 MCP: {mcp}")
        
        # 備份冗餘文件
        for file_path in self.redundant_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(full_path, backup_path)
                self.cleanup_log.append(f"備份文件: {file_path}")
    
    def _remove_non_integrated_mcps(self):
        """移除未集成到工作流的 MCP"""
        print("\n🗑️ 移除未集成的 MCP...")
        
        components_dir = self.project_root / "core" / "components"
        removed_count = 0
        
        for mcp in self.mcps_to_remove:
            mcp_path = components_dir / mcp
            if mcp_path.exists():
                try:
                    shutil.rmtree(mcp_path)
                    print(f"  ✅ 已移除: {mcp}")
                    self.cleanup_log.append(f"移除 MCP: {mcp}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ 移除失敗 {mcp}: {e}")
                    self.cleanup_log.append(f"移除失敗: {mcp} - {e}")
        
        print(f"  共移除 {removed_count} 個未集成的 MCP")
    
    def _is_protected_file(self, file_path: Path) -> bool:
        """檢查文件是否受保護（ClaudeEditor 相關）"""
        file_str = str(file_path).lower()
        protected_keywords = [
            'claudeditor',
            'claude_editor',
            'smartui',
            'ag_ui',
            'agui'
        ]
        return any(keyword in file_str for keyword in protected_keywords)
    
    def _remove_redundant_files(self):
        """移除冗餘文件（保護 ClaudeEditor 相關文件）"""
        print("\n📄 移除冗餘文件...")
        
        removed_count = 0
        protected_count = 0
        
        for file_path in self.redundant_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # 檢查是否為受保護的文件
                if self._is_protected_file(full_path):
                    print(f"  🛡️ 受保護: {file_path} (ClaudeEditor 相關)")
                    protected_count += 1
                    continue
                    
                try:
                    full_path.unlink()
                    print(f"  ✅ 已移除: {file_path}")
                    self.cleanup_log.append(f"移除文件: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ 移除失敗 {file_path}: {e}")
                    self.cleanup_log.append(f"移除失敗: {file_path} - {e}")
        
        print(f"  共移除 {removed_count} 個冗餘文件，保護 {protected_count} 個文件")
    
    def _cleanup_empty_directories(self):
        """清理空目錄"""
        print("\n📁 清理空目錄...")
        
        core_dir = self.project_root / "core"
        empty_dirs = []
        
        for root, dirs, files in os.walk(core_dir, topdown=False):
            if not dirs and not files:
                empty_dirs.append(root)
                try:
                    os.rmdir(root)
                    self.cleanup_log.append(f"移除空目錄: {root}")
                except:
                    pass
        
        print(f"  共清理 {len(empty_dirs)} 個空目錄")
    
    def _update_imports(self):
        """更新相關文件的 import 語句"""
        print("\n📝 更新 import 語句...")
        
        # 需要檢查和更新的文件
        files_to_check = [
            "core/powerautomation_core.py",
            "core/powerautomation_main.py", 
            "core/mcp_config.py",
            "core/workflows/six_core_workflows.py"
        ]
        
        updated_count = 0
        for file_path in files_to_check:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    original_content = content
                    
                    # 移除對已刪除 MCP 的引用
                    for mcp in self.mcps_to_remove:
                        content = content.replace(f"from core.components.{mcp}", "# Removed: ")
                        content = content.replace(f"import {mcp}", "# Removed: ")
                    
                    if content != original_content:
                        full_path.write_text(content, encoding='utf-8')
                        print(f"  ✅ 已更新: {file_path}")
                        updated_count += 1
                        self.cleanup_log.append(f"更新 import: {file_path}")
                except Exception as e:
                    print(f"  ❌ 更新失敗 {file_path}: {e}")
        
        print(f"  共更新 {updated_count} 個文件")
    
    def _generate_cleanup_report(self):
        """生成清理報告"""
        report_path = self.project_root / "deployment" / "v4.73" / "MCP_CLEANUP_REPORT.md"
        
        report = f"""# MCP 工作流集成清理報告

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
備份位置: {self.backup_dir}

## 📊 清理統計

### 保留的 MCP
#### P0 核心 MCP ({len(self.p0_core_mcps)} 個)
{chr(10).join(f"- ✅ {mcp}" for mcp in sorted(self.p0_core_mcps))}

#### P1 工作流 MCP ({len(self.p1_workflow_mcps)} 個)
{chr(10).join(f"- ✅ {mcp}" for mcp in sorted(self.p1_workflow_mcps))}

### 移除的 MCP ({len(self.mcps_to_remove)} 個)
{chr(10).join(f"- ❌ {mcp}" for mcp in sorted(self.mcps_to_remove))}

### 移除的冗餘文件 ({len(self.redundant_files)} 個)
{chr(10).join(f"- ❌ {file}" for file in self.redundant_files)}

## 📝 清理日誌

{chr(10).join(f"- {log}" for log in self.cleanup_log)}

## ✅ 清理後的架構

總 MCP 數量: {len(self.p0_core_mcps) + len(self.p1_workflow_mcps)} 個
- P0 核心: {len(self.p0_core_mcps)} 個
- P1 工作流: {len(self.p1_workflow_mcps)} 個

## 🎯 下一步行動

1. 運行測試確保系統正常
2. 驗證六大工作流功能完整
3. 更新相關文檔
4. 提交代碼變更
"""
        
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding='utf-8')
        
        print(f"\n📄 清理報告已保存: {report_path}")
    
    def verify_workflow_integration(self):
        """驗證工作流集成狀態"""
        print("\n🔍 驗證工作流集成...")
        
        workflow_mcp_mapping = {
            "requirement_analysis": ["codeflow_mcp", "stagewise_mcp"],
            "architecture_design": ["zen_mcp", "smartui_mcp", "stagewise_mcp"],
            "coding_implementation": ["codeflow_mcp", "zen_mcp", "xmasters_mcp", 
                                    "smartui_mcp", "ag_ui_mcp", "stagewise_mcp"],
            "testing_validation": ["test_mcp", "ag_ui_mcp", "stagewise_mcp"],
            "deployment_release": ["smartui_mcp", "stagewise_mcp"],
            "monitoring_operations": ["codeflow_mcp", "xmasters_mcp", "stagewise_mcp"]
        }
        
        print("\n工作流 MCP 集成映射:")
        for workflow, mcps in workflow_mcp_mapping.items():
            print(f"\n{workflow}:")
            for mcp in mcps:
                status = "✅" if mcp in (self.p0_core_mcps | self.p1_workflow_mcps) else "❌"
                print(f"  {status} {mcp}")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="執行 MCP 工作流集成清理")
    parser.add_argument("--dry-run", action="store_true", help="只顯示計劃，不執行")
    parser.add_argument("--verify", action="store_true", help="驗證工作流集成狀態")
    
    args = parser.parse_args()
    
    executor = MCPWorkflowIntegrationExecutor()
    
    if args.verify:
        executor.verify_workflow_integration()
    elif args.dry_run:
        print("🔍 模擬執行模式\n")
        print("將移除以下 MCP:")
        for mcp in sorted(executor.mcps_to_remove):
            print(f"  - {mcp}")
        print("\n將移除以下冗餘文件:")
        for file in executor.redundant_files:
            print(f"  - {file}")
    else:
        executor.execute_cleanup()
        print("\n運行驗證:")
        executor.verify_workflow_integration()


if __name__ == "__main__":
    main()