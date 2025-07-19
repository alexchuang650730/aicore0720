#!/usr/bin/env python3
"""
驗證新工具是否正確複製到 aicore0720
"""

import os
from pathlib import Path

def verify_tools():
    """驗證所有新工具文件"""
    
    # 定義需要檢查的文件
    required_files = [
        "enhanced_codeflow_mcp.py",
        "k2_optimizer_trainer.py", 
        "k2_pricing_system.py",
        "cleanup_redundant_code.py",
        "mcp_consolidation_analyzer.py",
        "manus_enhanced_analyzer.py",
        "manus_tasks_manual.txt"
    ]
    
    # 檢查當前目錄
    current_dir = Path.cwd()
    print(f"當前目錄: {current_dir}")
    print("=" * 60)
    
    # 驗證每個文件
    all_present = True
    for file_name in required_files:
        file_path = current_dir / file_name
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"✅ {file_name:<40} 大小: {file_size:,} bytes")
        else:
            print(f"❌ {file_name:<40} 未找到！")
            all_present = False
    
    print("=" * 60)
    
    if all_present:
        print("✅ 所有新工具都已成功複製！")
        
        # 檢查 README.md 是否已更新
        readme_path = current_dir / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "新增工具使用說明" in content or "新增工具使用说明" in content:
                    print("✅ README.md 已更新包含新工具說明")
                else:
                    print("⚠️  README.md 可能需要更新")
    else:
        print("❌ 部分文件缺失，請檢查！")
        return False
    
    return True

if __name__ == "__main__":
    verify_tools()