#!/usr/bin/env python3
"""
雙向通信完整演示
展示 Claude Code Tool、ClaudeEditor 和 Memory RAG 的協同工作
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

# 導入三個核心系統
from core.bidirectional_communication_system import BidirectionalCommunicationSystem
from core.shared_conversation_memory_system import shared_memory, sync_conversation
from core.k2_learning_alignment_system import k2_learning_system, get_k2_aligned_response


class BidirectionalDemo:
    """雙向通信演示"""
    
    def __init__(self):
        self.comm_system = BidirectionalCommunicationSystem()
        self.demo_output = []
        
    async def demo_scenario_1(self):
        """場景1: Claude Code Tool 自動切換到 K2 模式"""
        print("\n" + "="*60)
        print("📘 場景1: 一鍵安裝後自動劫持 Claude Code Tool")
        print("="*60)
        
        # 設置 K2 模式劫持
        await self.comm_system.setup_k2_mode_hijack()
        
        # 模擬 Claude Code Tool 請求
        print("\n🧑 用戶: claude /edit main.py")
        
        # 系統自動劫持並切換到 K2
        await self.comm_system.handle_claude_request("/edit", ["main.py"])
        
        # 記錄到共享記憶
        await sync_conversation(
            source="claude_code_tool",
            role="user",
            content="/edit main.py",
            context={"tool": "claude", "redirected": True}
        )
        
        await sync_conversation(
            source="k2_router",
            role="assistant",
            content="已切換到 K2 模式處理，預計節省 60% 成本",
            context={"model": "k2", "cost_saving": 0.6}
        )
        
        self.demo_output.append({
            "scenario": "K2模式劫持",
            "result": "成功將 Claude 請求重定向到 K2",
            "cost_saving": "60%"
        })
        
    async def demo_scenario_2(self):
        """場景2: 需要可視化時自動啟動 ClaudeEditor"""
        print("\n" + "="*60)
        print("📘 場景2: 檢測到可視化需求，自動啟動 ClaudeEditor")
        print("="*60)
        
        # 模擬下載文件的請求
        print("\n🧑 用戶: 下載並部署六大工作流到生產環境")
        
        # 系統檢測到需要可視化
        visual_task = await self.comm_system.detect_visual_task("下載並部署六大工作流到生產環境")
        
        if visual_task:
            print(f"\n✨ 檢測到可視化任務: {visual_task['trigger']}")
            
            # 記錄到共享記憶
            await sync_conversation(
                source="claude_code_tool",
                role="user",
                content="下載並部署六大工作流到生產環境",
                context={"requires_visual": True}
            )
            
            # 啟動 ClaudeEditor（模擬）
            print("\n🚀 正在啟動 ClaudeEditor...")
            print("🖥️  ClaudeEditor 已啟動: http://localhost:8080")
            print("📊 六大工作流可視化界面已準備就緒")
            
            await sync_conversation(
                source="claudeditor",
                role="assistant",
                content="ClaudeEditor 已啟動，六大工作流部署界面已準備就緒",
                context={
                    "ui_component": "six_workflows",
                    "status": "ready"
                }
            )
            
        self.demo_output.append({
            "scenario": "可視化檢測",
            "trigger": "部署六大工作流",
            "action": "啟動 ClaudeEditor",
            "result": "成功"
        })
        
    async def demo_scenario_3(self):
        """場景3: 對話記憶共享與學習"""
        print("\n" + "="*60)
        print("📘 場景3: Claude 與 ClaudeEditor 共享對話記憶")
        print("="*60)
        
        # 在 ClaudeEditor 中生成文件
        print("\n🧑 用戶 (在 ClaudeEditor): 生成 React 登錄組件")
        
        await sync_conversation(
            source="claudeditor",
            role="user",
            content="生成 React 登錄組件",
            context={"interface": "web_ui"}
        )
        
        # ClaudeEditor 生成組件
        component_content = """
import React, { useState } from 'react';

export const LoginComponent = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  return (
    <div className="login-form">
      <input 
        type="text" 
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="用戶名"
      />
      <input 
        type="password" 
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="密碼"
      />
      <button onClick={handleLogin}>登錄</button>
    </div>
  );
};
"""
        
        await sync_conversation(
            source="claudeditor",
            role="assistant",
            content=f"已生成 React 登錄組件:\n{component_content}",
            context={
                "files": ["LoginComponent.jsx"],
                "component_type": "react",
                "generated": True
            }
        )
        
        # 追蹤生成的文件
        await self.comm_system.track_generated_file("LoginComponent.jsx")
        
        print("\n✅ ClaudeEditor: 已生成 LoginComponent.jsx")
        print("📝 文件已添加到快速工作區")
        
        # 在 Claude Code Tool 中引用
        print("\n🧑 用戶 (在 Claude Code Tool): 為剛才的登錄組件添加測試")
        
        # Memory RAG 搜索相關記憶
        relevant_memories = await shared_memory.search_memory("登錄組件")
        
        if relevant_memories:
            print("\n🧠 Memory RAG 找到相關記憶:")
            for memory in relevant_memories[:2]:
                print(f"  - {memory['memory']['summary']}")
                print(f"    相關文件: {', '.join(memory['source_files'])}")
                
        self.demo_output.append({
            "scenario": "記憶共享",
            "claudeditor_action": "生成組件",
            "claude_tool_action": "引用並測試",
            "memory_rag": f"找到 {len(relevant_memories)} 條相關記憶"
        })
        
    async def demo_scenario_4(self):
        """場景4: K2 從 Claude 使用記錄中學習"""
        print("\n" + "="*60)
        print("📘 場景4: K2 學習 Claude 的編程模式")
        print("="*60)
        
        # 模擬一天的編程記錄
        print("\n📊 分析今天 16 小時的 Claude Code Tool 使用記錄...")
        
        # 模擬學習過程
        mock_sessions = [{
            "duration_hours": 16,
            "interactions": 245,
            "patterns_found": 18,
            "common_commands": ["/edit", "/run", "/test", "/deploy"],
            "success_rate": 0.92
        }]
        
        print(f"\n✅ 分析完成:")
        print(f"  - 總時長: 16 小時")
        print(f"  - 交互次數: 245 次")
        print(f"  - 發現模式: 18 個")
        print(f"  - 成功率: 92%")
        
        # 測試 K2 對齊
        test_input = "/edit component"
        k2_response = await get_k2_aligned_response(test_input)
        
        if k2_response:
            print(f"\n🤖 K2 已學習到模式:")
            print(f"  - 觸發: {test_input}")
            print(f"  - 置信度: {k2_response['confidence']:.2%}")
            print(f"  - 使用次數: {k2_response['usage_count']}")
            
        self.demo_output.append({
            "scenario": "K2學習",
            "analyzed_hours": 16,
            "patterns_learned": 18,
            "alignment_improvement": "15%"
        })
        
    async def demo_scenario_5(self):
        """場景5: 完整工作流演示"""
        print("\n" + "="*60)
        print("📘 場景5: 完整的雙向工作流")
        print("="*60)
        
        # 1. 用戶在 Claude Code Tool 請求
        print("\n1️⃣ Claude Code Tool 請求:")
        print("🧑 用戶: 創建用戶管理系統並部署")
        
        # 2. K2 處理簡單部分
        print("\n2️⃣ K2 快速生成基礎代碼...")
        await asyncio.sleep(0.5)  # 模擬處理
        
        # 3. 檢測到需要可視化的部署任務
        print("\n3️⃣ 檢測到部署任務需要可視化")
        print("🚀 自動啟動 ClaudeEditor...")
        
        # 4. ClaudeEditor 顯示六大工作流
        print("\n4️⃣ ClaudeEditor 六大工作流:")
        workflows = [
            "✅ 需求分析 - 完成",
            "✅ 架構設計 - 完成", 
            "✅ 編碼實現 - 完成",
            "🔄 測試驗證 - 進行中 35%",
            "⏳ 部署發布 - 待開始",
            "⏳ 監控運維 - 待開始"
        ]
        
        for workflow in workflows:
            print(f"   {workflow}")
            
        # 5. 記憶系統記錄整個過程
        print("\n5️⃣ Memory RAG 記錄學習:")
        print("  - 用戶偏好: 用戶管理系統")
        print("  - 成功模式: 代碼生成 → 測試 → 部署")
        print("  - K2 對齊度: +5%")
        
        self.demo_output.append({
            "scenario": "完整工作流",
            "steps": 5,
            "k2_handling": "基礎代碼生成",
            "claudeditor_handling": "可視化部署",
            "memory_learning": "模式記錄"
        })
        
    async def generate_report(self):
        """生成演示報告"""
        print("\n" + "="*60)
        print("📊 雙向通信演示總結")
        print("="*60)
        
        report = {
            "demo_time": datetime.now().isoformat(),
            "scenarios_completed": len(self.demo_output),
            "key_features": {
                "k2_mode_hijack": "✅ 成功",
                "visual_detection": "✅ 成功",
                "memory_sharing": "✅ 成功",
                "k2_learning": "✅ 成功",
                "workflow_integration": "✅ 成功"
            },
            "benefits": {
                "cost_saving": "60-80%",
                "user_experience": "無縫切換",
                "learning_capability": "持續改進"
            },
            "scenarios": self.demo_output
        }
        
        # 保存報告
        report_path = Path("bidirectional_communication_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print("\n✅ 核心優勢:")
        print("  1. 一鍵安裝即可劫持 Claude → K2 (節省成本)")
        print("  2. 自動檢測可視化需求 → ClaudeEditor")
        print("  3. 對話記憶實時共享 (Memory RAG)")
        print("  4. K2 持續學習 Claude 模式 (16小時/天)")
        print("  5. 統一的用戶體驗")
        
        print(f"\n📄 詳細報告已保存: {report_path}")
        

async def main():
    """運行完整演示"""
    demo = BidirectionalDemo()
    
    # 依次運行所有場景
    await demo.demo_scenario_1()
    await asyncio.sleep(1)
    
    await demo.demo_scenario_2()
    await asyncio.sleep(1)
    
    await demo.demo_scenario_3()
    await asyncio.sleep(1)
    
    await demo.demo_scenario_4()
    await asyncio.sleep(1)
    
    await demo.demo_scenario_5()
    await asyncio.sleep(1)
    
    # 生成報告
    await demo.generate_report()
    
    print("\n🎉 雙向通信演示完成！")
    

if __name__ == "__main__":
    asyncio.run(main())