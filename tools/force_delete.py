#!/usr/bin/env python3
"""
強制刪除 core 目錄中的無用文件
"""

import os
import sys
import shutil
from pathlib import Path

def force_remove(path):
    """強制刪除文件或目錄"""
    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.chmod(path, 0o777)  # 更改權限
            os.remove(path)
            return True
        elif os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            return True
    except Exception as e:
        print(f"Error removing {path}: {e}")
        return False

# 設置基礎路徑
base_path = "/Users/alexchuang/alexchuangtest/aicore0718/core"
os.chdir(base_path)

# 需要刪除的文件（使用完整路徑）
files_to_delete = [
    # 根目錄下的文件
    f"{base_path}/bidirectional_communication_system.py",
    f"{base_path}/deepswe_memory_enhancement_system.py",
    f"{base_path}/k2_learning_alignment_system.py",
    f"{base_path}/memoryos_mcp_adapter.py",
    f"{base_path}/shared_conversation_memory_system.py",
    f"{base_path}/mcpzero_integration_design.md",
    f"{base_path}/powerautomation_main.py",
    f"{base_path}/powerautomation_core_driver.py",
    f"{base_path}/powerautomation_core.py",  # 這個也是舊文件
    
    # components 目錄下的文件
    f"{base_path}/components/unified_memory_rag_interface_old.py",
    f"{base_path}/components/codeflow_mcp_integration.py",
    f"{base_path}/components/integrated_test_framework.py",
    f"{base_path}/components/integrate_zen_trae_xmasters.py",
    f"{base_path}/components/claudeditor_powerautomation_mapping.py",
    f"{base_path}/components/unified_memory_rag_interface.py",  # 也是舊的
    
    # 臨時文件
    f"{base_path}/TO_DELETE.txt",
    f"{base_path}/cleanup_files.sh"
]

# 需要刪除的目錄
dirs_to_delete = [
    f"{base_path}/components/enhanced_command_mcp",
    f"{base_path}/components/claudeditor_mcp"  # 空目錄
]

print("開始刪除文件...")
print("-" * 50)

# 刪除文件
deleted_count = 0
for file_path in files_to_delete:
    if os.path.exists(file_path):
        if force_remove(file_path):
            print(f"✅ 已刪除: {os.path.basename(file_path)}")
            deleted_count += 1
        else:
            print(f"❌ 無法刪除: {os.path.basename(file_path)}")
    else:
        print(f"⚠️  不存在: {os.path.basename(file_path)}")

# 刪除目錄
for dir_path in dirs_to_delete:
    if os.path.exists(dir_path):
        if force_remove(dir_path):
            print(f"✅ 已刪除目錄: {os.path.basename(dir_path)}")
            deleted_count += 1
        else:
            print(f"❌ 無法刪除目錄: {os.path.basename(dir_path)}")

# 刪除其他文件
other_files = [
    "/Users/alexchuang/alexchuangtest/aicore0718/cleanup_core.sh",
    "/Users/alexchuang/alexchuangtest/aicore0718/delete_files.py"
]

for file_path in other_files:
    if os.path.exists(file_path):
        if force_remove(file_path):
            print(f"✅ 已刪除: {os.path.basename(file_path)}")
            deleted_count += 1

print("-" * 50)
print(f"清理完成！共刪除 {deleted_count} 個文件/目錄")

# 刪除這個腳本本身
print("\n最後刪除這個腳本...")
script_path = "/Users/alexchuang/alexchuangtest/aicore0718/force_delete.py"
if os.path.exists(script_path):
    print("請執行: rm force_delete.py")