#!/usr/bin/env python3
"""
v4.75 部署驗證腳本
確保所有組件正確集成並可以正常工作
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class DeploymentVerifier:
    def __init__(self):
        self.root_path = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "4.75",
            "checks": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
    
    def check(self, name, condition, details=""):
        """執行檢查並記錄結果"""
        result = {
            "name": name,
            "passed": condition,
            "details": details
        }
        self.results["checks"].append(result)
        self.results["summary"]["total"] += 1
        if condition:
            self.results["summary"]["passed"] += 1
            print(f"✅ {name}")
        else:
            self.results["summary"]["failed"] += 1
            print(f"❌ {name}: {details}")
        return condition
    
    def verify_ui_components(self):
        """驗證 UI 組件"""
        print("\n🎨 驗證 UI 組件...")
        
        # 檢查演示 UI 組件
        demo_ui_path = self.root_path / "core/components/demo_ui"
        self.check(
            "演示 UI 目錄存在",
            demo_ui_path.exists(),
            f"路徑: {demo_ui_path}"
        )
        
        # 檢查必要的 UI 組件
        ui_components = [
            "ClaudeEditorDemoPanel.jsx",
            "StageWiseCommandDemo.jsx",
            "UnifiedDeploymentUI.jsx",
            "WorkflowAutomationDashboard.jsx",
            "MetricsTrackingDashboard.jsx"
        ]
        
        for component in ui_components:
            component_path = demo_ui_path / component
            self.check(
                f"UI 組件: {component}",
                component_path.exists(),
                f"路徑: {component_path}"
            )
    
    def verify_mcp_systems(self):
        """驗證 MCP 系統"""
        print("\n🔧 驗證 MCP 系統...")
        
        mcp_path = self.root_path / "core/components"
        
        # 檢查 MCP 文件
        mcp_files = [
            "demo_mcp.py",
            "codeflow_mcp.py",
            "smartui_mcp.py"
        ]
        
        for mcp_file in mcp_files:
            file_path = mcp_path / mcp_file
            self.check(
                f"MCP 系統: {mcp_file}",
                file_path.exists(),
                f"路徑: {file_path}"
            )
    
    def verify_deployment_files(self):
        """驗證部署文件"""
        print("\n📦 驗證部署文件...")
        
        deploy_path = self.root_path / "deploy/v4.75"
        
        # 檢查關鍵部署文件
        deploy_files = [
            "deployment_manifest.json",
            "deployment_ui_manifest.json",
            "workflow_automation_config.json",
            "workflow_automation_metrics.json",
            "DEPLOYMENT_SUMMARY.md"
        ]
        
        for file_name in deploy_files:
            file_path = deploy_path / file_name
            self.check(
                f"部署文件: {file_name}",
                file_path.exists(),
                f"路徑: {file_path}"
            )
    
    def verify_python_systems(self):
        """驗證 Python 系統"""
        print("\n🐍 驗證 Python 系統...")
        
        deploy_path = self.root_path / "deploy/v4.75"
        
        python_systems = [
            "unified_deployment_system.py",
            "workflow_automation_metrics.py",
            "test_validation_metrics_system.py",
            "metrics_calculation_formulas.py"
        ]
        
        for system in python_systems:
            file_path = deploy_path / system
            self.check(
                f"Python 系統: {system}",
                file_path.exists(),
                f"路徑: {file_path}"
            )
    
    def verify_integration(self):
        """驗證集成配置"""
        print("\n🔌 驗證集成配置...")
        
        deploy_path = self.root_path / "deploy/v4.75"
        
        # 檢查集成文件
        integration_files = [
            "claudeditor_integration.js",
            "deploy_claude_code_tool.sh",
            "deploy_claudeditor.sh",
            "deploy_unified.sh"
        ]
        
        for file_name in integration_files:
            file_path = deploy_path / file_name
            self.check(
                f"集成文件: {file_name}",
                file_path.exists(),
                f"路徑: {file_path}"
            )
            
            # 檢查腳本是否可執行
            if file_name.endswith('.sh'):
                is_executable = os.access(file_path, os.X_OK)
                self.check(
                    f"{file_name} 可執行",
                    is_executable,
                    "需要執行權限"
                )
    
    def verify_metrics(self):
        """驗證指標系統"""
        print("\n📊 驗證指標系統...")
        
        # 嘗試加載指標數據
        metrics_file = self.root_path / "deploy/v4.75/workflow_automation_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                
                self.check(
                    "指標數據格式正確",
                    "github_metrics" in metrics_data,
                    "包含 GitHub 指標"
                )
                
                self.check(
                    "工作流指標存在",
                    "workflow_metrics" in metrics_data,
                    f"包含 {len(metrics_data.get('workflow_metrics', []))} 個工作流"
                )
            except Exception as e:
                self.check(
                    "指標數據可讀",
                    False,
                    str(e)
                )
    
    def generate_report(self):
        """生成驗證報告"""
        report_path = self.root_path / "deploy/v4.75/verification_report.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 驗證報告已保存: {report_path}")
        
        # 打印總結
        summary = self.results["summary"]
        print(f"\n{'='*50}")
        print(f"驗證總結 - PowerAutomation v4.75")
        print(f"{'='*50}")
        print(f"總檢查項: {summary['total']}")
        print(f"✅ 通過: {summary['passed']}")
        print(f"❌ 失敗: {summary['failed']}")
        print(f"成功率: {summary['passed']/summary['total']*100:.1f}%")
        
        if summary['failed'] > 0:
            print("\n⚠️ 發現問題，請檢查失敗項目")
        else:
            print("\n🎉 所有檢查通過！v4.75 部署完成")

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           PowerAutomation v4.75 部署驗證                 ║
╚══════════════════════════════════════════════════════════╝
""")
    
    verifier = DeploymentVerifier()
    
    # 執行所有驗證
    verifier.verify_ui_components()
    verifier.verify_mcp_systems()
    verifier.verify_deployment_files()
    verifier.verify_python_systems()
    verifier.verify_integration()
    verifier.verify_metrics()
    
    # 生成報告
    verifier.generate_report()

if __name__ == "__main__":
    main()