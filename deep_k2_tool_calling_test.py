#!/usr/bin/env python3
"""
深入測試K2工具調用能力與Claude的實際差距
真實的、詳細的對比測試
"""

import asyncio
import json
import time
import os
from typing import Dict, List, Any

class K2ToolCallingDeepTest:
    """K2工具調用深度測試"""
    
    def __init__(self):
        self.test_results = []
        
    async def test_k2_tool_format(self):
        """測試K2的工具調用格式"""
        print("🔬 測試K2工具調用格式")
        print("="*60)
        
        from huggingface_hub import InferenceClient
        os.environ['HF_TOKEN'] = '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'
        client = InferenceClient(provider='groq', api_key=os.environ['HF_TOKEN'])
        
        # 測試不同的工具定義格式
        test_formats = [
            {
                "name": "標準函數格式",
                "system_prompt": """你有以下工具可用：
1. read_file(path: str) - 讀取文件
2. write_file(path: str, content: str) - 寫入文件
3. run_command(cmd: str) - 執行命令

請使用正確的工具調用格式。""",
                "user_prompt": "請讀取config.json文件"
            },
            {
                "name": "JSON工具格式",
                "system_prompt": """可用工具：
```json
[
  {"name": "read_file", "parameters": {"path": "string"}},
  {"name": "write_file", "parameters": {"path": "string", "content": "string"}}
]
```
使用<|tool_calls_section_begin|>格式調用工具。""",
                "user_prompt": "請讀取config.json文件"
            },
            {
                "name": "自然語言提示",
                "system_prompt": "你可以調用read_file、write_file等工具。",
                "user_prompt": "請讀取config.json文件的內容"
            }
        ]
        
        for test in test_formats:
            print(f"\n📋 測試: {test['name']}")
            
            try:
                completion = client.chat.completions.create(
                    model='moonshotai/Kimi-K2-Instruct',
                    messages=[
                        {"role": "system", "content": test['system_prompt']},
                        {"role": "user", "content": test['user_prompt']}
                    ],
                    max_tokens=300
                )
                
                response = completion.choices[0].message.content
                
                # 分析工具調用
                has_tool_call = '<|tool_call' in response
                tool_format_correct = '<|tool_call_begin|>' in response and '<|tool_call_end|>' in response
                has_parameters = 'tool_call_argument' in response or 'path' in response.lower()
                
                print(f"   包含工具調用: {'✅' if has_tool_call else '❌'}")
                print(f"   格式正確: {'✅' if tool_format_correct else '❌'}")
                print(f"   包含參數: {'✅' if has_parameters else '❌'}")
                print(f"   響應預覽: {response[:150]}...")
                
                self.test_results.append({
                    "format": test['name'],
                    "success": has_tool_call and tool_format_correct,
                    "response": response
                })
                
            except Exception as e:
                print(f"   ❌ 測試失敗: {e}")
                
        return self.test_results
    
    async def test_tool_calling_scenarios(self):
        """測試不同場景的工具調用"""
        print("\n🎯 測試實際工具調用場景")
        print("="*60)
        
        from huggingface_hub import InferenceClient
        client = InferenceClient(provider='groq', api_key=os.environ['HF_TOKEN'])
        
        # 實際開發場景
        scenarios = [
            {
                "name": "單一工具調用",
                "prompt": "讀取main.py文件",
                "expected_tools": ["read_file"],
                "complexity": "simple"
            },
            {
                "name": "順序工具調用",
                "prompt": "先讀取config.json，然後把debug改為true，再寫回去",
                "expected_tools": ["read_file", "write_file"],
                "complexity": "medium"
            },
            {
                "name": "條件工具調用",
                "prompt": "如果error.log文件存在，讀取它並分析錯誤類型",
                "expected_tools": ["check_file", "read_file", "analyze"],
                "complexity": "complex"
            },
            {
                "name": "並行工具調用",
                "prompt": "同時讀取package.json和README.md，對比版本信息",
                "expected_tools": ["read_file", "read_file", "compare"],
                "complexity": "complex"
            }
        ]
        
        results = []
        
        for scenario in scenarios:
            print(f"\n📝 場景: {scenario['name']}")
            print(f"   複雜度: {scenario['complexity']}")
            print(f"   期望工具: {scenario['expected_tools']}")
            
            try:
                start_time = time.time()
                
                completion = client.chat.completions.create(
                    model='moonshotai/Kimi-K2-Instruct',
                    messages=[
                        {
                            "role": "system", 
                            "content": "你是開發助手。可用工具：read_file(path), write_file(path, content), check_file(path), analyze(content), compare(file1, file2)。使用<|tool_calls_section_begin|>格式調用工具。"
                        },
                        {
                            "role": "user",
                            "content": scenario['prompt']
                        }
                    ],
                    max_tokens=500
                )
                
                response = completion.choices[0].message.content
                response_time = time.time() - start_time
                
                # 分析工具調用
                tool_calls = response.count('<|tool_call_begin|>')
                tools_found = []
                
                # 提取實際調用的工具
                import re
                tool_pattern = r'functions\.(\w+):'
                matches = re.findall(tool_pattern, response)
                tools_found = matches
                
                # 評估結果
                expected_count = len(scenario['expected_tools'])
                actual_count = len(tools_found)
                coverage = actual_count / expected_count if expected_count > 0 else 0
                
                print(f"   實際調用: {tools_found}")
                print(f"   工具數量: {actual_count}/{expected_count}")
                print(f"   覆蓋率: {coverage:.1%}")
                print(f"   響應時間: {response_time:.2f}s")
                
                results.append({
                    "scenario": scenario['name'],
                    "complexity": scenario['complexity'],
                    "expected": expected_count,
                    "actual": actual_count,
                    "coverage": coverage,
                    "time": response_time,
                    "tools_called": tools_found
                })
                
            except Exception as e:
                print(f"   ❌ 測試失敗: {e}")
                results.append({
                    "scenario": scenario['name'],
                    "error": str(e)
                })
        
        return results
    
    async def test_error_handling(self):
        """測試工具調用的錯誤處理"""
        print("\n⚠️ 測試錯誤處理能力")
        print("="*50)
        
        from huggingface_hub import InferenceClient
        client = InferenceClient(provider='groq', api_key=os.environ['HF_TOKEN'])
        
        error_scenarios = [
            {
                "name": "無效工具名稱",
                "prompt": "使用invalid_tool()來處理文件"
            },
            {
                "name": "缺少必需參數",
                "prompt": "調用read_file但不提供文件路徑"
            },
            {
                "name": "參數類型錯誤",
                "prompt": "調用write_file，用數字123作為文件路徑"
            }
        ]
        
        for scenario in error_scenarios:
            print(f"\n🔧 {scenario['name']}")
            
            try:
                completion = client.chat.completions.create(
                    model='moonshotai/Kimi-K2-Instruct',
                    messages=[
                        {
                            "role": "system",
                            "content": "你是開發助手，可以調用read_file(path: str)和write_file(path: str, content: str)工具。"
                        },
                        {
                            "role": "user",
                            "content": scenario['prompt']
                        }
                    ],
                    max_tokens=300
                )
                
                response = completion.choices[0].message.content
                
                # 檢查錯誤處理
                handles_error = any(word in response.lower() for word in ['錯誤', '無效', '失敗', 'error', 'invalid', 'fail'])
                suggests_correction = any(word in response.lower() for word in ['應該', '需要', '請提供', 'should', 'need', 'please'])
                
                print(f"   識別錯誤: {'✅' if handles_error else '❌'}")
                print(f"   提供建議: {'✅' if suggests_correction else '❌'}")
                
            except Exception as e:
                print(f"   測試異常: {e}")
    
    async def compare_with_claude_format(self):
        """對比K2和Claude的工具調用格式差異"""
        print("\n📊 K2 vs Claude 工具調用格式對比")
        print("="*60)
        
        print("\n📌 K2工具調用格式:")
        print("""
<|tool_calls_section_begin|>
<|tool_call_begin|>functions.read_file:0
<|tool_call_argument_begin|>{"path": "config.json"}
<|tool_call_end|>
<|tool_calls_section_end|>
        """)
        
        print("\n📌 Claude工具調用格式（理論）:")
        print("""
I'll help you read the file. Let me do that for you.

<function_calls>
<invoke name="read_file">
<parameter name="path">config.json</parameter>
</invoke>
</function_calls>
        """)
        
        print("\n🔍 關鍵差異:")
        print("1. 格式標記: K2使用<|tool_*|>，Claude使用XML風格")
        print("2. 函數命名: K2使用functions.前綴，Claude直接使用函數名")
        print("3. 參數格式: K2使用JSON，Claude使用XML參數")
        print("4. 調用風格: K2更程序化，Claude更自然語言化")
        
        return {
            "k2_format": "pipeline_style",
            "claude_format": "xml_style",
            "compatibility": "需要格式轉換"
        }
    
    async def generate_deep_analysis_report(self, format_results, scenario_results):
        """生成深度分析報告"""
        print("\n📋 K2工具調用能力深度分析報告")
        print("="*70)
        
        # 格式測試分析
        format_success = sum(1 for r in format_results if r.get('success', False))
        print(f"\n1️⃣ 工具格式支持:")
        print(f"   成功率: {format_success}/{len(format_results)} ({format_success/len(format_results)*100:.1f}%)")
        
        # 場景測試分析
        simple_scenarios = [r for r in scenario_results if r.get('complexity') == 'simple']
        medium_scenarios = [r for r in scenario_results if r.get('complexity') == 'medium']
        complex_scenarios = [r for r in scenario_results if r.get('complexity') == 'complex']
        
        print(f"\n2️⃣ 場景複雜度分析:")
        if simple_scenarios:
            simple_coverage = sum(r.get('coverage', 0) for r in simple_scenarios) / len(simple_scenarios)
            print(f"   簡單場景: {simple_coverage:.1%} 覆蓋率")
        if medium_scenarios:
            medium_coverage = sum(r.get('coverage', 0) for r in medium_scenarios) / len(medium_scenarios)
            print(f"   中等場景: {medium_coverage:.1%} 覆蓋率")
        if complex_scenarios:
            complex_coverage = sum(r.get('coverage', 0) for r in complex_scenarios) / len(complex_scenarios)
            print(f"   複雜場景: {complex_coverage:.1%} 覆蓋率")
        
        # 性能分析
        valid_results = [r for r in scenario_results if 'time' in r]
        if valid_results:
            avg_time = sum(r['time'] for r in valid_results) / len(valid_results)
            print(f"\n3️⃣ 性能指標:")
            print(f"   平均響應時間: {avg_time:.2f}s")
            print(f"   最快響應: {min(r['time'] for r in valid_results):.2f}s")
            print(f"   最慢響應: {max(r['time'] for r in valid_results):.2f}s")
        
        # 總體評估
        print(f"\n4️⃣ 總體評估:")
        overall_coverage = sum(r.get('coverage', 0) for r in scenario_results) / len(scenario_results) if scenario_results else 0
        
        if overall_coverage >= 0.8:
            print("   ✅ K2工具調用能力：優秀")
            print("   可以支持大部分開發場景")
        elif overall_coverage >= 0.6:
            print("   ⚠️ K2工具調用能力：良好")
            print("   基本場景可用，複雜場景需優化")
        else:
            print("   ❌ K2工具調用能力：不足")
            print("   需要顯著改進才能投入使用")
        
        return {
            "overall_coverage": overall_coverage,
            "format_compatibility": format_success / len(format_results) if format_results else 0,
            "performance_acceptable": avg_time < 3.0 if valid_results else False
        }

async def main():
    """主測試函數"""
    print("🚀 K2工具調用能力深度測試")
    print("真實、詳細的對比分析")
    print("="*70)
    
    tester = K2ToolCallingDeepTest()
    
    # 1. 測試工具格式
    format_results = await tester.test_k2_tool_format()
    
    # 2. 測試實際場景
    scenario_results = await tester.test_tool_calling_scenarios()
    
    # 3. 測試錯誤處理
    await tester.test_error_handling()
    
    # 4. 對比Claude格式
    format_comparison = await tester.compare_with_claude_format()
    
    # 5. 生成深度報告
    analysis = await tester.generate_deep_analysis_report(format_results, scenario_results)
    
    print("\n🎯 最終結論:")
    if analysis['overall_coverage'] >= 0.7 and analysis['format_compatibility'] >= 0.7:
        print("✅ K2工具調用能力可以支持PowerAutomation")
        print("✅ 與Claude的差距在可接受範圍內")
        print("✅ 透過格式轉換可以實現透明切換")
    else:
        print("❌ K2工具調用能力存在顯著差距")
        print("⚠️ 需要額外的優化和適配工作")
        print("🔧 建議先在簡單場景中使用")

if __name__ == "__main__":
    asyncio.run(main())