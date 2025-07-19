#!/usr/bin/env python3
"""
刪除 core 目錄中的無用文件
"""

import os
import shutil
from pathlib import Path

# 設置基礎路徑
base_path = Path("/Users/alexchuang/alexchuangtest/aicore0718/core")

# 需要刪除的文件列表
files_to_delete = [
    # 根目錄下的文件
    "bidirectional_communication_system.py",
    "deepswe_memory_enhancement_system.py",
    "k2_learning_alignment_system.py",
    "memoryos_mcp_adapter.py",
    "shared_conversation_memory_system.py",
    "mcpzero_integration_design.md",
    "powerautomation_main.py",
    "powerautomation_core_driver.py",
    
    # components 目錄下的文件
    "components/unified_memory_rag_interface_old.py",
    "components/codeflow_mcp_integration.py",
    "components/integrated_test_framework.py",
    "components/integrate_zen_trae_xmasters.py",
    "components/claudeditor_powerautomation_mapping.py",
    
    # 臨時文件
    "TO_DELETE.txt",
    "cleanup_files.sh"
]

# 需要刪除的目錄
dirs_to_delete = [
    "components/enhanced_command_mcp",
    "components/claudeditor_mcp"  # 空目錄
]

# 刪除文件
for file_path in files_to_delete:
    full_path = base_path / file_path
    if full_path.exists():
        try:
            os.remove(full_path)
            print(f"✅ 已刪除文件: {file_path}")
        except PermissionError:
            print(f"❌ 權限錯誤，無法刪除: {file_path}")
        except Exception as e:
            print(f"❌ 刪除失敗 {file_path}: {e}")
    else:
        print(f"⚠️  文件不存在: {file_path}")

# 刪除目錄
for dir_path in dirs_to_delete:
    full_path = base_path / dir_path
    if full_path.exists():
        try:
            if full_path.is_dir():
                shutil.rmtree(full_path)
                print(f"✅ 已刪除目錄: {dir_path}")
        except PermissionError:
            print(f"❌ 權限錯誤，無法刪除目錄: {dir_path}")
        except Exception as e:
            print(f"❌ 刪除目錄失敗 {dir_path}: {e}")
    else:
        print(f"⚠️  目錄不存在: {dir_path}")

# 刪除根目錄的 cleanup_core.sh
cleanup_script = Path("/Users/alexchuang/alexchuangtest/aicore0718/cleanup_core.sh")
if cleanup_script.exists():
    try:
        os.remove(cleanup_script)
        print("✅ 已刪除 cleanup_core.sh")
    except Exception as e:
        print(f"❌ 刪除 cleanup_core.sh 失敗: {e}")

print("\n清理完成！")
print("如果有權限錯誤，請使用 sudo python3 delete_files.py 運行")