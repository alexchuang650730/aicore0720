#!/bin/bash
# PowerAutomation v4.71 Memory RAG Edition 一键安装快捷脚本
# 这是主安装脚本的快捷方式，放在根目录便于访问

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 执行主安装脚本
exec "$SCRIPT_DIR/deployment/scripts/install_powerautomation_v471_memory_rag.sh" "$@"

