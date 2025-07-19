# 項目清理計劃

## 需要刪除的目錄和文件

### 1. 冗餘目錄
- `mcp_server/` - 已被 MCP-Zero 架構取代
- `goal_alignment_system/` - 功能已整合到其他模塊
- `deployment/` - 統一使用 `deploy/` 目錄

### 2. 數據庫文件（確認後刪除）
- `goal_alignment.db`
- `behavior_alignment.db` 
- `data_collection.db`
- `memory.db`
- `member_system.db`
- `powerautomation.db`
- `unified_memory.db`

### 3. 臨時和備份文件
- `backup_mcp_*/` - 舊的備份目錄
- `mcp_backup_*/` - 舊的備份目錄
- `temp/` - 臨時文件

### 4. 測試和演示文件（整理後刪除）
- 根目錄下的測試文件 (test_*.py)
- 各種 demo 和 simple 測試文件

## 保留的核心結構

```
aicore0718/
├── core/                    # 核心代碼
│   ├── mcp_zero/           # MCP-Zero 架構
│   ├── components/         # MCP 組件
│   ├── workflows/          # 六大工作流
│   └── api/               # API 端點
│
├── deploy/                 # 統一部署目錄
│   ├── v4.73/             # 當前版本
│   │   ├── mobile/        
│   │   ├── desktop/       
│   │   └── web/           
│   └── common/            # 通用資源
│
├── showcase/              # 營銷展示
│   ├── README.md         
│   └── images/           
│
├── claudeditor/          # ClaudeEditor 前端
│
└── docs/                 # 文檔
```

## 執行步驟

1. **備份重要數據**
   ```bash
   mkdir backup_20250719
   cp *.db backup_20250719/
   ```

2. **刪除冗餘目錄**
   ```bash
   rm -rf mcp_server/
   rm -rf goal_alignment_system/
   rm -rf deployment/  # 先確保內容已遷移到 deploy/
   ```

3. **清理測試文件**
   ```bash
   # 移動有價值的測試到 tests/
   mv test_*.py tests/archive/
   ```

4. **更新 Git**
   ```bash
   git add -A
   git commit -m "清理冗餘目錄和文件，優化項目結構"
   ```

## 注意事項

1. 在刪除 `deployment/` 之前，確保所有重要文件已遷移到 `deploy/`
2. 數據庫文件可能包含重要數據，建議先備份
3. 某些測試文件可能還有參考價值，建議歸檔而非直接刪除