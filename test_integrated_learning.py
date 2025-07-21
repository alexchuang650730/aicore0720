#!/usr/bin/env python3
"""測試整合學習系統"""

import asyncio
from integrated_continuous_learning import IntegratedContinuousLearning

async def test_run():
    system = IntegratedContinuousLearning()
    
    print("🧪 測試整合持續學習系統...")
    print("- 同步收集人類輸入和生成數據")
    print("- 自動生成訓練樣本")
    print("- 監控文件變化")
    
    # 運行10秒測試
    task = asyncio.create_task(system.start_integrated_learning())
    await asyncio.sleep(10)
    task.cancel()
    
    print("\n✅ 測試完成!")
    print(f"- 人類輸入: {system.stats['human_inputs']}")
    print(f"- 生成數據: {system.stats['generated_inputs']}")
    print(f"- 總處理量: {system.stats['total_processed']}")

if __name__ == "__main__":
    asyncio.run(test_run())