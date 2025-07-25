
# K2 與 Claude Code 比較測試報告

測試時間: 2025-07-21 00:13:48

## 總體指標

- **測試成功率**: 100.0%
- **平均語義相似度**: 6.5%
- **工具調用準確率**: 70.0%
- **總測試數**: 5
- **成功測試數**: 5

## 詳細測試結果


### basic_coding - 代碼生成

**提示**: 寫一個函數來計算斐波那契數列的第n項

**K2 工具調用**: 無

**預期工具**: 無

**工具準確率**: 100.0%

**語義相似度**: 10.8%

---

### file_operation - 文件操作

**提示**: 請幫我讀取 main.py 文件並找出所有的函數定義

**K2 工具調用**: Grep, Read

**預期工具**: Read, Grep

**工具準確率**: 100.0%

**語義相似度**: 21.9%

---

### code_refactor - 代碼重構

**提示**: 重構這段代碼，提高性能並添加類型註解

**K2 工具調用**: 無

**預期工具**: Read, Edit

**工具準確率**: 0.0%

**語義相似度**: 0.0%

---

### project_setup - 專案設置

**提示**: 創建一個新的 Python 專案結構，包含 src/, tests/, 和配置文件

**K2 工具調用**: Bash

**預期工具**: Write, Bash

**工具準確率**: 50.0%

**語義相似度**: 0.0%

---

### debug_analysis - 錯誤分析

**提示**: 分析這個錯誤: TypeError: 'NoneType' object is not iterable

**K2 工具調用**: 無

**預期工具**: 無

**工具準確率**: 100.0%

**語義相似度**: 0.0%

---
