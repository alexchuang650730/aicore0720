#!/usr/bin/env python3
"""
DeepSWE POC 測試腳本
用於驗證 DeepSWE 模型的代碼生成能力
"""

import asyncio
import time
import json
from typing import Dict, Any, List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class DeepSWEPOCTester:
    """DeepSWE POC 測試器"""
    
    def __init__(self):
        self.model_name = "agentica-org/DeepSWE-Preview"
        self.model = None
        self.tokenizer = None
        self.test_results = []
        
    async def initialize(self):
        """初始化模型"""
        print(f"🚀 正在加載 DeepSWE 模型: {self.model_name}")
        start_time = time.time()
        
        try:
            # 加載 tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # 加載模型（使用 float16 節省內存）
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            
            load_time = time.time() - start_time
            print(f"✅ 模型加載完成，耗時: {load_time:.2f} 秒")
            
        except Exception as e:
            print(f"❌ 模型加載失敗: {e}")
            raise
    
    async def test_code_generation(self) -> Dict[str, Any]:
        """測試代碼生成能力"""
        print("\n📝 測試 1: 代碼生成")
        
        test_cases = [
            {
                "name": "Python FastAPI 端點",
                "prompt": """<thinking>
需要創建一個 FastAPI 端點來處理用戶註冊
需要包含：輸入驗證、密碼加密、數據庫操作
</thinking>

請生成一個 FastAPI 端點，實現用戶註冊功能，包含：
1. 郵箱和密碼驗證
2. 密碼加密存儲
3. 返回 JWT token
"""
            },
            {
                "name": "React Hook",
                "prompt": """<thinking>
需要創建一個自定義 React Hook 來管理表單狀態
應該支持驗證和錯誤處理
</thinking>

請生成一個自定義 React Hook useForm，功能包括：
1. 管理表單字段狀態
2. 字段驗證
3. 錯誤信息顯示
4. 提交處理
"""
            }
        ]
        
        results = []
        for test_case in test_cases:
            start_time = time.time()
            
            # 生成代碼
            inputs = self.tokenizer(test_case["prompt"], return_tensors="pt")
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=500,
                temperature=0.7,
                do_sample=True,
                top_p=0.95
            )
            
            generated_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            generation_time = time.time() - start_time
            
            result = {
                "test_name": test_case["name"],
                "generation_time": generation_time,
                "generated_code": generated_code,
                "tokens_generated": len(outputs[0])
            }
            
            results.append(result)
            print(f"✅ {test_case['name']}: 生成耗時 {generation_time:.2f} 秒")
        
        return {"code_generation_results": results}
    
    async def test_bug_fixing(self) -> Dict[str, Any]:
        """測試 Bug 修復能力"""
        print("\n🐛 測試 2: Bug 修復")
        
        buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)  # Bug: 沒有處理空列表

result = calculate_average([])
print(f"Average: {result}")
"""
        
        prompt = f"""<thinking>
這段代碼有一個除零錯誤
需要添加空列表檢查
</thinking>

請修復以下代碼中的 bug：
```python
{buggy_code}
```

錯誤：ZeroDivisionError: division by zero
"""
        
        start_time = time.time()
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.3,  # 降低溫度以獲得更確定的修復
            do_sample=True
        )
        
        fixed_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        fix_time = time.time() - start_time
        
        return {
            "bug_fix_result": {
                "original_code": buggy_code,
                "fixed_code": fixed_code,
                "fix_time": fix_time
            }
        }
    
    async def test_code_optimization(self) -> Dict[str, Any]:
        """測試代碼優化能力"""
        print("\n⚡ 測試 3: 代碼優化")
        
        slow_code = """
def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] == lst[j] and lst[i] not in duplicates:
                duplicates.append(lst[i])
    return duplicates
"""
        
        prompt = f"""<thinking>
這個函數的時間複雜度是 O(n²)
可以使用集合來優化到 O(n)
</thinking>

請優化以下代碼的性能：
```python
{slow_code}
```
"""
        
        start_time = time.time()
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.5,
            do_sample=True
        )
        
        optimized_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        optimization_time = time.time() - start_time
        
        return {
            "optimization_result": {
                "original_code": slow_code,
                "optimized_code": optimized_code,
                "optimization_time": optimization_time
            }
        }
    
    async def run_all_tests(self):
        """運行所有測試"""
        print("=" * 50)
        print("🧪 開始 DeepSWE POC 測試")
        print("=" * 50)
        
        # 初始化模型
        await self.initialize()
        
        # 運行測試
        test_results = {
            "model": self.model_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {}
        }
        
        # 測試 1: 代碼生成
        test_results["tests"]["code_generation"] = await self.test_code_generation()
        
        # 測試 2: Bug 修復
        test_results["tests"]["bug_fixing"] = await self.test_bug_fixing()
        
        # 測試 3: 代碼優化
        test_results["tests"]["code_optimization"] = await self.test_code_optimization()
        
        # 計算總體性能指標
        total_time = sum([
            sum(r["generation_time"] for r in test_results["tests"]["code_generation"]["code_generation_results"]),
            test_results["tests"]["bug_fixing"]["bug_fix_result"]["fix_time"],
            test_results["tests"]["code_optimization"]["optimization_result"]["optimization_time"]
        ])
        
        test_results["summary"] = {
            "total_tests": 4,
            "total_time": total_time,
            "average_time_per_task": total_time / 4,
            "model_size": "32B parameters",
            "hardware_used": torch.cuda.get_device_name() if torch.cuda.is_available() else "CPU"
        }
        
        # 保存結果
        output_file = f"deepswe_poc_results_{int(time.time())}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 測試完成！結果已保存到: {output_file}")
        print(f"📊 總耗時: {total_time:.2f} 秒")
        print(f"📊 平均每個任務耗時: {total_time/4:.2f} 秒")
        
        return test_results


async def main():
    """主函數"""
    tester = DeepSWEPOCTester()
    
    try:
        results = await tester.run_all_tests()
        
        # 打印摘要
        print("\n" + "=" * 50)
        print("📊 測試摘要")
        print("=" * 50)
        print(f"✅ 模型: {results['model']}")
        print(f"✅ 總測試數: {results['summary']['total_tests']}")
        print(f"✅ 總耗時: {results['summary']['total_time']:.2f} 秒")
        print(f"✅ 平均耗時: {results['summary']['average_time_per_task']:.2f} 秒/任務")
        print(f"✅ 硬件: {results['summary']['hardware_used']}")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())