#!/bin/bash
# 清理 core 目錄中的無用文件

cd /Users/alexchuang/alexchuangtest/aicore0718/core

# 刪除無用的獨立系統文件（功能已整合到 MCP 組件中）
rm -f bidirectional_communication_system.py
rm -f deepswe_memory_enhancement_system.py
rm -f k2_learning_alignment_system.py
rm -f memoryos_mcp_adapter.py
rm -f shared_conversation_memory_system.py

# 刪除設計文檔（應該在 docs 目錄）
rm -f mcpzero_integration_design.md

# 刪除舊的啟動文件（已被 start_mcpzero_server.py 替代）
rm -f powerautomation_main.py
rm -f powerautomation_core_driver.py

# 刪除重複的文件
rm -f components/unified_memory_rag_interface_old.py
rm -f components/codeflow_mcp_integration.py
rm -f components/integrated_test_framework.py
rm -f components/integrate_zen_trae_xmasters.py
rm -f components/claudeditor_powerautomation_mapping.py

# 刪除 enhanced_command_mcp（功能已合併到 command_mcp）
rm -rf components/enhanced_command_mcp/

# 刪除空的 claudeditor_mcp 目錄
rmdir components/claudeditor_mcp/ 2>/dev/null

echo "Core 目錄清理完成"