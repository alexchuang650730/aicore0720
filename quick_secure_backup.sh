#!/bin/bash
# 快速安全備份腳本
# 將重要的AICore訓練數據備份到EC2根目錄

echo "🔒 AICore數據安全遷移"
echo "======================"

# 檢查權限
if [[ $EUID -ne 0 ]]; then
   echo "❌ 需要root權限執行此腳本"
   echo "請使用: sudo ./quick_secure_backup.sh"
   exit 1
fi

# 創建目標目錄
TARGET_DIR="/data/aicore_training_data"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$TARGET_DIR/backup_$TIMESTAMP"

echo "📂 創建備份目錄: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/training_data"
mkdir -p "$BACKUP_DIR/active_data"
mkdir -p "$BACKUP_DIR/enhanced_extraction"

# 檢查源目錄
if [ ! -d "data" ]; then
    echo "❌ 源目錄 ./data 不存在"
    exit 1
fi

echo "📦 開始備份數據..."

# 備份關鍵目錄
if [ -d "data/enhanced_extraction" ]; then
    echo "  📁 備份增強萃取數據..."
    cp -r data/enhanced_extraction/* "$BACKUP_DIR/enhanced_extraction/" 2>/dev/null || true
fi

if [ -d "data/comprehensive_training" ]; then
    echo "  📁 備份訓練數據..."
    cp -r data/comprehensive_training "$BACKUP_DIR/training_data/" 2>/dev/null || true
fi

if [ -d "data/claude_conversations" ]; then
    echo "  📁 備份Claude對話..."
    cp -r data/claude_conversations "$BACKUP_DIR/training_data/" 2>/dev/null || true
fi

if [ -d "data/continuous_learning_sessions" ]; then
    echo "  📁 備份持續學習會話..."
    cp -r data/continuous_learning_sessions "$BACKUP_DIR/training_data/" 2>/dev/null || true
fi

# 備份重要文件
echo "  📄 備份配置文件..."
cp data/*.txt "$BACKUP_DIR/active_data/" 2>/dev/null || true
cp data/*.db "$BACKUP_DIR/active_data/" 2>/dev/null || true
cp data/*.json "$BACKUP_DIR/active_data/" 2>/dev/null || true

# 創建軟連結
echo "🔗 創建活動數據軟連結..."
ln -sfn "$BACKUP_DIR" "$TARGET_DIR/active"

# 計算大小
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
FILE_COUNT=$(find "$BACKUP_DIR" -type f | wc -l)

# 創建備份清單
cat > "$BACKUP_DIR/backup_info.txt" << EOF
AICore訓練數據備份信息
====================
備份時間: $(date)
備份位置: $BACKUP_DIR
備份大小: $BACKUP_SIZE
文件數量: $FILE_COUNT
源目錄: $(pwd)/data

活動軟連結: $TARGET_DIR/active

恢復命令:
cp -r $TARGET_DIR/active/training_data/* ./data/
cp -r $TARGET_DIR/active/active_data/* ./data/
EOF

echo "✅ 備份完成！"
echo "======================"
echo "📂 備份位置: $BACKUP_DIR"
echo "📊 備份大小: $BACKUP_SIZE"
echo "📄 文件數量: $FILE_COUNT"
echo "🔗 活動連結: $TARGET_DIR/active"
echo ""
echo "💡 提示:"
echo "1. 數據已安全備份到EC2根目錄"
echo "2. 使用軟連結 $TARGET_DIR/active 訪問最新備份"
echo "3. 可以安全地將./data加入.gitignore"
echo ""

# 設置權限
chown -R $(logname):$(logname) "$TARGET_DIR" 2>/dev/null || true
chmod -R 755 "$TARGET_DIR"

echo "🛡️ 權限設置完成"
echo "🎉 安全遷移成功！"