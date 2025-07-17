#!/bin/bash

# ClaudeEditor 恢复脚本
# 用法: ./restore_script.sh [备份文件名]

BACKUP_DIR="/home/ubuntu/aicore0716/backups"

if [ -z "$1" ]; then
    echo "📋 可用的备份版本:"
    ls -lt "$BACKUP_DIR"/*.html | while read line; do
        filename=$(echo $line | awk '{print $9}' | xargs basename)
        echo "  - $filename"
    done
    echo ""
    echo "用法: ./restore_script.sh [备份文件名]"
    echo "例如: ./restore_script.sh v4.7.1_baseline_20250717_055841.html"
    exit 1
fi

BACKUP_FILE="$BACKUP_DIR/$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 备份文件不存在: $1"
    exit 1
fi

# 在恢复前先备份当前版本
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp /home/ubuntu/aicore0716/index_working.html "$BACKUP_DIR/before_restore_${TIMESTAMP}.html"

# 恢复备份
cp "$BACKUP_FILE" /home/ubuntu/aicore0716/index_working.html

echo "✅ 已恢复到: $1"
echo "💾 当前版本已备份为: before_restore_${TIMESTAMP}.html"

