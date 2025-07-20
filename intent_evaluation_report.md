
# 意圖理解評估報告

測試時間: 2025-07-21 00:35:45

## 總體指標

- **平均工具準確率**: 74.0%
- **平均意圖滿足度**: 77.6%
- **距離目標差距**: 26.0%

## 詳細測試結果

### file_read_analyze

- **提示**: 請幫我讀取 main.py 文件並找出所有的函數定義
- **意圖**: 文件操作 → 文件操作
- **工具準確率**: 50.0%
- **預期工具**: Read, Grep
- **實際工具**: Read, Read
- **缺失工具**: Grep
- **順序正確**: ✅

---

### search_pattern

- **提示**: 在所有 Python 文件中搜索包含 'TODO' 的註釋
- **意圖**: 搜索代碼 → 搜索代碼
- **工具準確率**: 100.0%
- **預期工具**: Grep
- **實際工具**: Glob, Grep, Glob, Grep
- **缺失工具**: 無
- **順序正確**: ✅

---

### refactor_code

- **提示**: 將 config.py 中的所有 print 語句改為 logger.info
- **意圖**: 代碼重構 → 代碼重構
- **工具準確率**: 50.0%
- **預期工具**: Read, Edit
- **實際工具**: Read, Read
- **缺失工具**: Edit
- **順序正確**: ✅

---

### create_project

- **提示**: 創建一個新的 Flask 專案，包含基本的目錄結構和配置文件
- **意圖**: 專案設置 → 專案設置
- **工具準確率**: 100.0%
- **預期工具**: Bash, Write
- **實際工具**: Bash, Bash, Write, Write, Write, Write, Write, Write, Bash, Bash, Write, Write, Write, Write, Write
- **缺失工具**: 無
- **順序正確**: ✅

---

### run_tests

- **提示**: 運行所有的單元測試並顯示覆蓋率報告
- **意圖**: 測試相關 → 測試相關
- **工具準確率**: 100.0%
- **預期工具**: Bash
- **實際工具**: Bash, Bash, Bash, Bash, Bash, Bash
- **缺失工具**: 無
- **順序正確**: ✅

---

### analyze_error

- **提示**: 分析這個錯誤並給出解決方案: ImportError: No module named 'requests'
- **意圖**: 調試幫助 → 調試幫助
- **工具準確率**: 50.0%
- **預期工具**: 無
- **實際工具**: Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash
- **缺失工具**: 無
- **順序正確**: ✅

---

### multi_file_refactor

- **提示**: 將所有文件中的類名 UserManager 改為 UserService
- **意圖**: 代碼重構 → 文件操作
- **工具準確率**: 80.0%
- **預期工具**: Grep, Read, Edit
- **實際工具**: Grep, Read, Read, Bash, Bash, Edit, Grep, Read, Read, Bash, Bash
- **缺失工具**: 無
- **順序正確**: ✅

---

### complex_search

- **提示**: 找出所有定義了 async 函數但沒有使用 await 的文件
- **意圖**: 搜索代碼 → 文件操作
- **工具準確率**: 50.0%
- **預期工具**: Grep, Read
- **實際工具**: Grep, Grep
- **缺失工具**: Read
- **順序正確**: ✅

---

### create_documentation

- **提示**: 為這個專案創建一個詳細的 README.md 文件
- **意圖**: 文檔編寫 → 專案設置
- **工具準確率**: 80.0%
- **預期工具**: Write
- **實際工具**: Glob, Glob, Glob, Bash, Bash, Bash, Read, Read, Read, Read, Bash, Write, Glob, Glob, Glob, Bash, Bash, Bash, Read, Read, Read, Read, Bash
- **缺失工具**: 無
- **順序正確**: ✅

---

### install_dependencies

- **提示**: 安裝 requirements.txt 中的所有依賴並確保沒有版本衝突
- **意圖**: 執行命令 → 執行命令
- **工具準確率**: 80.0%
- **預期工具**: Bash
- **實際工具**: Bash, Read, Bash, Bash, Bash, Bash, Read, Bash, Bash, Bash
- **缺失工具**: 無
- **順序正確**: ✅

---
