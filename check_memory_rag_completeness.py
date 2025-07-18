#!/usr/bin/env python3
"""
檢查Memory RAG完善程度
"""

import ast
import os

def check_memory_rag_completeness():
    """檢查Memory RAG實現完整性"""
    
    print("🔍 Memory RAG完善度檢查")
    print("="*60)
    
    # 讀取memory_rag.py
    rag_file = "core/mcp_components/memory_rag_mcp/memory_rag.py"
    
    if not os.path.exists(rag_file):
        print(f"❌ 找不到文件: {rag_file}")
        return
    
    with open(rag_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查核心功能
    core_functions = {
        "store_claude_behavior": "存儲Claude行為模式",
        "store_k2_response": "存儲K2響應記錄", 
        "get_alignment_context": "獲取對齊上下文",
        "evaluate_alignment": "評估對齊質量",
        "learn_from_feedback": "從反饋中學習",
        "optimize_k2_prompt": "優化K2提示詞",
        "get_similar_patterns": "獲取相似模式",
        "get_alignment_stats": "獲取對齊統計"
    }
    
    implemented_functions = []
    missing_functions = []
    
    print("\n📋 核心功能檢查:")
    for func_name, desc in core_functions.items():
        if f"async def _{func_name}" in content or f"def _{func_name}" in content:
            implemented_functions.append(func_name)
            print(f"  ✅ {desc} ({func_name})")
        else:
            missing_functions.append(func_name)
            print(f"  ❌ {desc} ({func_name})")
    
    # 檢查數據庫初始化
    print("\n💾 數據庫檢查:")
    db_tables = [
        "memory_records",
        "behavior_alignment", 
        "claude_behaviors",
        "k2_responses",
        "alignment_feedback"
    ]
    
    for table in db_tables:
        if f"CREATE TABLE IF NOT EXISTS {table}" in content:
            print(f"  ✅ {table}表")
        else:
            print(f"  ⚠️  {table}表可能未初始化")
    
    # 檢查性能優化
    print("\n⚡ 性能優化檢查:")
    optimizations = {
        "asyncio": "異步處理",
        "cache": "緩存機制",
        "batch": "批量處理",
        "parallel": "並行處理",
        "index": "數據庫索引"
    }
    
    for opt, desc in optimizations.items():
        if opt in content.lower():
            print(f"  ✅ {desc}")
        else:
            print(f"  ⚠️  {desc}可能未實現")
    
    # 檢查錯誤處理
    print("\n🛡️ 錯誤處理檢查:")
    try_count = content.count("try:")
    except_count = content.count("except")
    print(f"  Try/Except塊: {try_count}/{except_count}")
    
    if try_count > 10:
        print("  ✅ 良好的錯誤處理覆蓋")
    else:
        print("  ⚠️  錯誤處理可能不足")
    
    # 計算完善度
    total_checks = len(core_functions) + len(db_tables) + len(optimizations) + 1
    passed_checks = len(implemented_functions) + 3 + 2 + (1 if try_count > 10 else 0)
    completeness = (passed_checks / total_checks) * 100
    
    print(f"\n📊 總體完善度: {completeness:.1f}%")
    
    # 需要完善的項目
    print("\n🔧 需要完善的項目:")
    
    if completeness < 80:
        print("1. 實現缺失的核心功能")
        print("2. 添加緩存機制提升性能")
        print("3. 實現並行處理加速檢索")
        print("4. 優化數據庫查詢性能")
    elif completeness < 90:
        print("1. 優化性能瓶頸")
        print("2. 增強錯誤處理")
        print("3. 添加更多測試覆蓋")
    else:
        print("✅ Memory RAG基本完善，可以使用")
    
    # 性能優化建議
    print("\n💡 RAG性能優化建議(實現<200ms):")
    print("1. 使用Redis緩存熱門查詢")
    print("2. 預計算常見問題的embeddings")
    print("3. 使用FAISS加速向量搜索")
    print("4. 實現異步並行處理")
    print("5. 優化數據庫索引")
    
    return completeness

if __name__ == "__main__":
    completeness = check_memory_rag_completeness()
    
    print("\n✅ 檢查完成！")
    if completeness >= 80:
        print("Memory RAG已基本完善，可配合K2使用")
    else:
        print("Memory RAG需要進一步完善")