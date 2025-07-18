#!/usr/bin/env python3
"""
清理冗餘的 MCP 組件
基於分析結果，移除重複和低集成度的 MCP
"""

import os
import shutil
import json
from datetime import datetime
from typing import List, Dict, Any

class MCPCleanupManager:
    """MCP 清理管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.backup_dir = os.path.join(project_root, f"mcp_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.cleanup_report = {
            "removed_directories": [],
            "removed_files": [],
            "moved_files": [],
            "errors": []
        }
        
    def execute_cleanup(self):
        """執行清理計劃"""
        print("🧹 開始清理冗餘的 MCP 組件")
        print("="*70)
        
        # 1. 創建備份目錄
        self._create_backup_directory()
        
        # 2. 清理重複的 MCP 目錄
        self._cleanup_duplicate_mcp_directories()
        
        # 3. 清理備份文件
        self._cleanup_backup_files()
        
        # 4. 移除低集成度的非核心 MCP
        self._remove_low_integration_mcps()
        
        # 5. 生成清理報告
        self._generate_cleanup_report()
        
        print("\n✅ 清理完成！")
        
    def _create_backup_directory(self):
        """創建備份目錄"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"📦 創建備份目錄: {self.backup_dir}")
            
    def _cleanup_duplicate_mcp_directories(self):
        """清理重複的 MCP 目錄"""
        print("\n📂 清理重複的 MCP 目錄...")
        
        # 移除 core/mcp_components 目錄（與 core/components 重複）
        mcp_components_dir = os.path.join(self.project_root, "core", "mcp_components")
        if os.path.exists(mcp_components_dir):
            try:
                # 備份
                backup_path = os.path.join(self.backup_dir, "mcp_components")
                shutil.copytree(mcp_components_dir, backup_path)
                
                # 刪除
                shutil.rmtree(mcp_components_dir)
                self.cleanup_report["removed_directories"].append(mcp_components_dir)
                print(f"✅ 已移除重複目錄: {mcp_components_dir}")
            except Exception as e:
                self.cleanup_report["errors"].append(f"Failed to remove {mcp_components_dir}: {str(e)}")
                print(f"❌ 移除失敗: {mcp_components_dir} - {str(e)}")
                
    def _cleanup_backup_files(self):
        """清理備份文件"""
        print("\n📄 清理備份文件...")
        
        components_dir = os.path.join(self.project_root, "core", "components")
        if os.path.exists(components_dir):
            for root, dirs, files in os.walk(components_dir):
                for file in files:
                    if file.endswith("_backup.py"):
                        file_path = os.path.join(root, file)
                        try:
                            # 備份
                            relative_path = os.path.relpath(file_path, self.project_root)
                            backup_file_path = os.path.join(self.backup_dir, relative_path)
                            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                            shutil.copy2(file_path, backup_file_path)
                            
                            # 刪除
                            os.remove(file_path)
                            self.cleanup_report["removed_files"].append(file_path)
                            print(f"✅ 已移除備份文件: {file}")
                        except Exception as e:
                            self.cleanup_report["errors"].append(f"Failed to remove {file_path}: {str(e)}")
                            print(f"❌ 移除失敗: {file_path} - {str(e)}")
                            
    def _remove_low_integration_mcps(self):
        """移除低集成度的非核心 MCP"""
        print("\n🔧 移除低集成度的非核心 MCP...")
        
        # 定義要移除的 MCP（P3 優先級）
        mcps_to_remove = [
            "k2_hitl_mcp",           # 人機交互（35% 集成度）
            "k2_new_commands_mcp",   # 新命令擴展（35% 集成度）
            "trae_agent_mcp",        # 智能代理（35% 集成度）
            "release_trigger_mcp",   # 發布觸發（35% 集成度）
            "deepgraph_mcp",         # 深度圖分析（非核心）
            "project_analyzer_mcp"   # 項目分析（非核心）
        ]
        
        components_dir = os.path.join(self.project_root, "core", "components")
        
        for mcp_name in mcps_to_remove:
            mcp_file = os.path.join(components_dir, f"{mcp_name}.py")
            if os.path.exists(mcp_file):
                try:
                    # 備份
                    backup_file_path = os.path.join(self.backup_dir, "removed_mcps", f"{mcp_name}.py")
                    os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                    shutil.copy2(mcp_file, backup_file_path)
                    
                    # 刪除
                    os.remove(mcp_file)
                    self.cleanup_report["removed_files"].append(mcp_file)
                    print(f"✅ 已移除低集成度 MCP: {mcp_name}")
                except Exception as e:
                    self.cleanup_report["errors"].append(f"Failed to remove {mcp_file}: {str(e)}")
                    print(f"❌ 移除失敗: {mcp_file} - {str(e)}")
                    
    def _generate_cleanup_report(self):
        """生成清理報告"""
        report_path = os.path.join(self.project_root, "mcp_cleanup_report.json")
        
        # 添加統計信息
        self.cleanup_report["summary"] = {
            "total_directories_removed": len(self.cleanup_report["removed_directories"]),
            "total_files_removed": len(self.cleanup_report["removed_files"]),
            "total_files_moved": len(self.cleanup_report["moved_files"]),
            "total_errors": len(self.cleanup_report["errors"]),
            "cleanup_date": datetime.now().isoformat(),
            "backup_location": self.backup_dir
        }
        
        # 保存報告
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.cleanup_report, f, indent=2, ensure_ascii=False)
            
        print(f"\n📊 清理報告已保存到: {report_path}")
        
        # 打印摘要
        print("\n清理摘要:")
        print(f"- 移除目錄: {self.cleanup_report['summary']['total_directories_removed']}")
        print(f"- 移除文件: {self.cleanup_report['summary']['total_files_removed']}")
        print(f"- 移動文件: {self.cleanup_report['summary']['total_files_moved']}")
        print(f"- 錯誤數量: {self.cleanup_report['summary']['total_errors']}")
        print(f"- 備份位置: {self.backup_dir}")

def generate_mcp_optimization_plan():
    """生成 MCP 優化計劃"""
    optimization_plan = {
        "phase1_immediate": {
            "description": "立即執行的清理任務",
            "tasks": [
                "刪除 core/mcp_components 目錄",
                "刪除所有 *_backup.py 文件",
                "移除 P3 優先級的 MCP"
            ],
            "status": "ready"
        },
        "phase2_short_term": {
            "description": "短期優化任務（1-2週）",
            "tasks": [
                "完善 codeflow_mcp 的前端集成",
                "提升核心 MCP 的集成度到 100%",
                "合併功能重複的 MCP（aws_bedrock_mcp -> memory_rag）",
                "合併 data_collection_mcp -> monitoring_mcp"
            ],
            "status": "planned"
        },
        "phase3_long_term": {
            "description": "長期優化任務（1個月）",
            "tasks": [
                "建立 MCP 依賴關係圖",
                "優化 MCP 間的通信機制",
                "建立自動化測試套件",
                "實現 MCP 熱加載機制"
            ],
            "status": "planned"
        }
    }
    
    # 核心 MCP 優先級分類
    mcp_priority_classification = {
        "P0_core_essential": {
            "description": "核心必需（絕對不能移除）",
            "mcps": [
                "memoryos_mcp",
                "enhanced_command_mcp",
                "mcp_coordinator_mcp",
                "claude_router_mcp",
                "local_adapter_mcp",
                "command_mcp",
                "smartui_mcp",
                "ag_ui_mcp"
            ]
        },
        "P1_workflow_essential": {
            "description": "工作流必需（需要改進但必須保留）",
            "mcps": [
                "codeflow_mcp",
                "test_mcp",
                "zen_mcp",
                "xmasters_mcp",
                "stagewise_mcp"
            ]
        },
        "P2_support_functions": {
            "description": "支撐功能（可以優化或合併）",
            "mcps": [
                "monitoring_mcp",
                "config_mcp",
                "security_mcp",
                "collaboration_mcp",
                "operations_mcp"
            ]
        },
        "P3_optional": {
            "description": "可選功能（可以考慮移除）",
            "mcps": [
                "k2_hitl_mcp",
                "k2_new_commands_mcp",
                "trae_agent_mcp",
                "release_trigger_mcp",
                "deepgraph_mcp",
                "project_analyzer_mcp"
            ]
        }
    }
    
    # 保存優化計劃
    plan_path = "mcp_optimization_plan.json"
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump({
            "optimization_phases": optimization_plan,
            "priority_classification": mcp_priority_classification,
            "generated_date": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
        
    print(f"\n📋 MCP 優化計劃已保存到: {plan_path}")
    
    return optimization_plan, mcp_priority_classification

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="清理冗餘的 MCP 組件")
    parser.add_argument("--project-root", type=str, default=".", 
                       help="項目根目錄路徑")
    parser.add_argument("--dry-run", action="store_true", 
                       help="只顯示計劃，不實際執行")
    parser.add_argument("--generate-plan", action="store_true",
                       help="生成優化計劃")
    
    args = parser.parse_args()
    
    if args.generate_plan:
        print("📋 生成 MCP 優化計劃...")
        optimization_plan, priority_classification = generate_mcp_optimization_plan()
        
        print("\n優化階段:")
        for phase_name, phase_info in optimization_plan.items():
            print(f"\n{phase_name}: {phase_info['description']}")
            for task in phase_info['tasks']:
                print(f"  - {task}")
                
        print("\n\nMCP 優先級分類:")
        for priority, info in priority_classification.items():
            print(f"\n{priority}: {info['description']}")
            print(f"  MCP 數量: {len(info['mcps'])}")
            
    elif args.dry_run:
        print("🔍 模擬運行模式（不會實際刪除文件）")
        print("\n將執行以下操作:")
        print("1. 刪除 core/mcp_components 目錄")
        print("2. 刪除所有 *_backup.py 文件")
        print("3. 移除以下低集成度 MCP:")
        print("   - k2_hitl_mcp")
        print("   - k2_new_commands_mcp")
        print("   - trae_agent_mcp")
        print("   - release_trigger_mcp")
        print("   - deepgraph_mcp")
        print("   - project_analyzer_mcp")
    else:
        # 執行清理
        cleanup_manager = MCPCleanupManager(args.project_root)
        cleanup_manager.execute_cleanup()
        
        print("\n🎯 建議後續行動:")
        print("1. 審查清理報告，確認沒有誤刪重要文件")
        print("2. 運行測試確保系統功能正常")
        print("3. 提交更改到版本控制")
        print("4. 執行 --generate-plan 查看後續優化計劃")

if __name__ == "__main__":
    main()