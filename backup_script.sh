#!/bin/bash

# ClaudeEditor 自动备份脚本
# 用法: ./backup_script.sh "描述信息"

BACKUP_DIR="/home/ubuntu/aicore0716/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DESCRIPTION=${1:-"自动备份"}

# 创建备份
cp /home/ubuntu/aicore0716/index_working.html "$BACKUP_DIR/v4.7.2_dev_${TIMESTAMP}.html"

# 更新版本日志
echo "- v4.7.2_dev_${TIMESTAMP}.html - ${DESCRIPTION}" >> "$BACKUP_DIR/VERSION_LOG.md"

echo "✅ 备份完成: v4.7.2_dev_${TIMESTAMP}.html"
echo "📝 描述: ${DESCRIPTION}"

# 显示最近5个备份
echo ""
echo "📋 最近备份:"
ls -lt "$BACKUP_DIR"/*.html | head -5

