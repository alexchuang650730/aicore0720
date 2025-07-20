#!/bin/bash
# 準備GitHub上傳腳本

echo "🚀 準備AICore 0720階段性上傳..."

# 1. 創建.gitignore（如果不存在）
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/
.pytest_cache/

# Logs
*.log
logs/
monitoring/*.jsonl
monitoring/*.json

# Data files
data/real_replays/
data/enhanced_replays/
data/optimized_replays/
data/replay_analysis/
data/manus_conversations/
data/training_ready/
data/k2_training*/
*.jsonl

# Model files
models/
*.pth
*.pkl
*.onnx
*.mlx

# Temporary files
*.tmp
*.temp
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo

# API Keys and Secrets
.env
.env.local
config/secrets.json
groq_api_key.txt
*api_key*
*secret*

# Large files
*.tar
*.zip
*.gz

# Binary files
*.pdf
*.docx
*.xlsx

# Test outputs
test_results/
coverage/

# Node modules
node_modules/
package-lock.json

# Deployment
deploy/temp/
deploy/dist/

# Personal data
manus_tasks_manual.txt
*personal*
*private*

# Training logs
unified_k2_training.log
EOF
    echo "✅ 創建.gitignore"
fi

# 2. 清理敏感信息
echo "🔍 檢查敏感信息..."

# 移除包含API密鑰的文件
find . -name "*api_key*" -type f -exec rm -f {} \;
find . -name "*secret*" -type f -exec rm -f {} \;

# 3. 創建必要的README
if [ ! -f README.md ]; then
    cp README_STAGE_UPLOAD.md README.md
    echo "✅ 創建README.md"
fi

# 4. 整理文件結構
echo "📁 整理文件結構..."

# 創建文檔目錄
mkdir -p docs/architecture
mkdir -p docs/deployment
mkdir -p docs/api

# 移動相關文檔
[ -f "K2_DEEPSWE_MEMORYRAG_FINAL_REPORT.md" ] && mv K2_DEEPSWE_MEMORYRAG_FINAL_REPORT.md docs/
[ -f "MCP_ZERO_QUICK_START.md" ] && mv MCP_ZERO_QUICK_START.md docs/deployment/

# 5. 生成項目統計
echo "📊 生成項目統計..."

cat > PROJECT_STATS.md << EOF
# 項目統計

生成時間: $(date +"%Y-%m-%d %H:%M:%S")

## 代碼統計
- Python文件數: $(find . -name "*.py" -type f | wc -l)
- 總代碼行數: $(find . -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
- MCP模塊數: $(find core/components -name "*_mcp" -type d | wc -l)

## 訓練數據
- Replay URLs總數: 533
- 已處理: $(find data -name "replay_*.json" 2>/dev/null | wc -l)
- 訓練樣本: $(find data -name "*.jsonl" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')

## 系統狀態
- 目標達成率: 92.6%
- 工具準確率: 74.1%
- 目標: 89%（3天內）
EOF

# 6. 創建上傳清單
echo "📋 創建上傳清單..."

cat > UPLOAD_CHECKLIST.md << EOF
# GitHub上傳清單

## 必要文件
- [x] README.md
- [x] .gitignore
- [x] 核心Python文件
- [x] MCP架構
- [x] 部署腳本

## 已排除
- [ ] API密鑰
- [ ] 個人數據
- [ ] 大型數據文件
- [ ] 二進制文件
- [ ] 日誌文件

## 上傳步驟
1. git add .
2. git commit -m "feat: AICore 0720階段性成果 - MCP運維架構完成"
3. git push origin main
EOF

echo "✅ 準備完成！"
echo ""
echo "下一步："
echo "1. 檢查 git status"
echo "2. 添加文件: git add ."
echo "3. 提交: git commit -m 'feat: AICore 0720階段性成果 - MCP運維架構完成'"
echo "4. 推送: git push origin main"