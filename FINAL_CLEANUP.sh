#!/bin/bash

echo "開始最終清理..."

# 切換到 core 目錄
cd /Users/alexchuang/alexchuangtest/aicore0718/core

# 列出要刪除的文件
echo "即將刪除以下文件："
ls -la k2_learning_alignment_system.py 2>/dev/null
ls -la memoryos_mcp_adapter.py 2>/dev/null
ls -la mcpzero_integration_design.md 2>/dev/null
ls -la powerautomation_main.py 2>/dev/null
ls -la powerautomation_core_driver.py 2>/dev/null
ls -la powerautomation_core.py 2>/dev/null
ls -la TO_DELETE.txt 2>/dev/null
ls -la cleanup_files.sh 2>/dev/null

echo ""
echo "開始刪除..."

# 強制刪除根目錄文件
sudo rm -fv k2_learning_alignment_system.py
sudo rm -fv memoryos_mcp_adapter.py
sudo rm -fv mcpzero_integration_design.md
sudo rm -fv powerautomation_main.py
sudo rm -fv powerautomation_core_driver.py
sudo rm -fv powerautomation_core.py
sudo rm -fv TO_DELETE.txt
sudo rm -fv cleanup_files.sh

# 刪除 components 下的文件
echo ""
echo "刪除 components 目錄下的文件..."
sudo rm -fv components/unified_memory_rag_interface_old.py
sudo rm -fv components/unified_memory_rag_interface.py
sudo rm -fv components/codeflow_mcp_integration.py
sudo rm -fv components/integrated_test_framework.py
sudo rm -fv components/integrate_zen_trae_xmasters.py
sudo rm -fv components/claudeditor_powerautomation_mapping.py

# 刪除目錄
echo ""
echo "刪除目錄..."
sudo rm -rfv components/enhanced_command_mcp
sudo rm -rfv components/claudeditor_mcp

# 清理根目錄的腳本
cd ..
sudo rm -fv force_delete.py
sudo rm -fv delete_commands.txt
sudo rm -fv FINAL_CLEANUP.sh

echo ""
echo "清理完成！"