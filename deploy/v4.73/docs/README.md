# PowerAutomation v4.73 文檔中心

## 📚 文檔結構

所有文檔都集中在版本化目錄中，不再散落各處！

```
deploy/v4.73/docs/
├── api/              # API 文檔 (OpenAPI/Swagger)
├── guides/           # 使用指南
├── tutorials/        # 教程
├── references/       # 參考文檔
├── architecture/     # 架構文檔
├── changelog/        # 變更日誌
└── migration/        # 遷移指南
```

## 🎯 Documentation MCP 功能

1. **自動生成 API 文檔**
   - 掃描 MCP 組件的 API 端點
   - 生成 OpenAPI 3.0 規範
   - 同時生成 JSON 和 Markdown 格式

2. **版本化文檔管理**
   - 每個版本有獨立的文檔目錄
   - 保留歷史文檔快照
   - 支持文檔版本比較

3. **智能文檔搜索**
   - 全文搜索功能
   - 按類別過濾
   - 相關性排序

4. **自動更新根目錄文檔**
   - 只有架構和安裝說明會更新到根目錄 README.md
   - 其他文檔都在版本目錄中

## 📋 使用示例

### 生成 API 文檔
```python
from core.components.docs_mcp import docs_manager

# 為特定 MCP 生成 API 文檔
await docs_manager.generate_api_documentation("test_mcp")
```

### 生成用戶指南
```python
# 生成使用指南
content_outline = {
    "sections": [
        {
            "id": "getting-started",
            "title": "快速開始",
            "content": "...",
            "code_examples": [...]
        }
    ]
}
await docs_manager.generate_user_guide("MCP-Zero 使用指南", content_outline)
```

### 更新根目錄 README
```python
# 只更新架構部分
await docs_manager.update_root_readme("architecture", {
    "architecture": "新的架構說明..."
})

# 只更新安裝說明
await docs_manager.update_root_readme("installation", {
    "installation": "新的安裝步驟..."
})
```

## 🔄 文檔生命週期

1. **開發階段**: 文檔狀態為 `draft`
2. **審核階段**: 文檔狀態為 `review`
3. **發布階段**: 文檔狀態為 `published`
4. **廢棄階段**: 文檔狀態為 `deprecated`

## 📊 當前文檔統計

- API 文檔: 0 個
- 使用指南: 0 個
- 教程: 0 個
- 參考文檔: 0 個
- 架構文檔: 0 個

*由 Documentation MCP 自動管理和更新*