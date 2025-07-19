#!/usr/bin/env python3
"""
快速分析前20個 Manus 任務
測試分析流程
"""

import asyncio
from manus_advanced_analyzer import ManusAdvancedAnalyzer
import json
from datetime import datetime

async def quick_analysis():
    """快速分析前20個任務"""
    print("🚀 開始快速分析前20個 Manus 任務...\n")
    
    analyzer = ManusAdvancedAnalyzer()
    
    # 載入任務
    tasks = analyzer.load_tasks()
    print(f"總共載入 {len(tasks)} 個任務")
    
    # 只分析前20個
    sample_tasks = tasks[:20]
    print(f"將分析前 {len(sample_tasks)} 個任務作為樣本\n")
    
    # 下載並分析
    results = await analyzer.batch_download(sample_tasks)
    
    patterns = []
    success_count = 0
    
    for result in results:
        if result['success']:
            success_count += 1
            pattern = analyzer.extract_advanced_patterns(result['html'])
            pattern['task_info'] = result['task']
            patterns.append(pattern)
            
            # 保存 HTML
            html_file = analyzer.output_dir / f"sample_{result['task']['id']}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(result['html'])
                
    print(f"\n✅ 成功下載並分析 {success_count}/{len(sample_tasks)} 個任務")
    
    # 快速統計
    tool_count = {}
    code_languages = {}
    
    for pattern in patterns:
        # 統計工具
        for tool in pattern.get('tool_sequences', []):
            tool_type = tool['type']
            tool_count[tool_type] = tool_count.get(tool_type, 0) + 1
            
        # 統計語言
        for code in pattern.get('code_blocks', []):
            lang = code['language']
            code_languages[lang] = code_languages.get(lang, 0) + 1
            
    # 生成快速報告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = analyzer.output_dir / f'quick_report_{timestamp}.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Manus 快速分析報告（前20個任務）\n\n")
        f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 概覽\n\n")
        f.write(f"- 分析任務數: {len(sample_tasks)}\n")
        f.write(f"- 成功分析: {success_count}\n\n")
        
        f.write("## 工具使用統計\n\n")
        for tool, count in sorted(tool_count.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {tool}: {count} 次\n")
            
        f.write("\n## 編程語言統計\n\n")
        for lang, count in sorted(code_languages.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {lang}: {count} 個代碼塊\n")
            
        f.write("\n## 樣本任務\n\n")
        for i, pattern in enumerate(patterns[:5]):
            f.write(f"### 任務 {i+1}: {pattern.get('title', 'Unknown')}\n")
            f.write(f"- 工具序列: {len(pattern.get('tool_sequences', []))} 個\n")
            f.write(f"- 代碼塊: {len(pattern.get('code_blocks', []))} 個\n")
            f.write(f"- 執行步驟: {len(pattern.get('execution_steps', []))} 個\n\n")
            
    print(f"\n📄 快速分析報告已生成: {report_file}")
    
    # 保存樣本數據
    sample_file = analyzer.output_dir / f'sample_patterns_{timestamp}.json'
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)
        
    print(f"💾 樣本數據已保存: {sample_file}")
    
    return {
        'success_count': success_count,
        'tool_count': tool_count,
        'code_languages': code_languages,
        'patterns': patterns
    }

async def main():
    """主函數"""
    print("=" * 60)
    print("🔍 Manus 快速分析工具")
    print("=" * 60)
    print("\n這個工具會分析前20個任務作為樣本")
    print("用於測試分析流程和查看初步結果\n")
    
    results = await quick_analysis()
    
    print("\n" + "=" * 60)
    print("✅ 快速分析完成！")
    print("=" * 60)
    
    print(f"\n關鍵發現：")
    if results['tool_count']:
        top_tool = max(results['tool_count'].items(), key=lambda x: x[1])
        print(f"- 最常用工具類型: {top_tool[0]} ({top_tool[1]} 次)")
        
    if results['code_languages']:
        top_lang = max(results['code_languages'].items(), key=lambda x: x[1])
        print(f"- 最常見編程語言: {top_lang[0]} ({top_lang[1]} 個代碼塊)")
        
    print(f"\n下一步：")
    print(f"1. 如果結果看起來合理，運行完整分析")
    print(f"2. 調整分析參數以更好地捕捉 Manus 的模式")
    print(f"3. 繼續收集更多任務達到200個目標")

if __name__ == "__main__":
    asyncio.run(main())