#!/usr/bin/env python3
"""
MCP-Zero 與 SmartTool MCP 整合示例
展示如何通過 MCP-Zero 自動調用外部工具
"""

import asyncio
from typing import Dict, Any

# 模擬的整合示例代碼
class MCPZeroSmartToolExample:
    """展示 MCP-Zero 如何與 SmartTool 協同工作"""
    
    async def example_1_simple_format(self):
        """示例 1：簡單的代碼格式化"""
        print("=== 示例 1：代碼格式化 ===")
        
        # 用戶請求
        user_request = "幫我格式化這段 JavaScript 代碼"
        code = "const x=1;const y=2;function test(){return x+y;}"
        
        # MCP-Zero 自動識別需要 SmartTool MCP
        # 並調用 Prettier 工具
        result = {
            "formatted_code": """const x = 1;
const y = 2;
function test() {
  return x + y;
}""",
            "tool_used": "mcp_prettier",
            "mcp_used": "smarttool_mcp"
        }
        
        print(f"原始代碼：{code}")
        print(f"格式化後：{result['formatted_code']}")
        print(f"使用工具：{result['tool_used']}")
        return result
    
    async def example_2_workflow(self):
        """示例 2：完整的工作流"""
        print("\n=== 示例 2：代碼檢查工作流 ===")
        
        # 用戶請求
        user_request = "檢查代碼質量，修復問題，運行測試，然後通知我結果"
        
        # MCP-Zero 分解為多步驟工作流
        workflow_steps = [
            {
                "step": 1,
                "mcp": "smarttool_mcp",
                "tool": "mcp_eslint",
                "action": "檢查代碼質量",
                "result": "發現 2 個警告"
            },
            {
                "step": 2,
                "mcp": "smarttool_mcp",
                "tool": "mcp_prettier",
                "action": "自動修復格式問題",
                "result": "已修復所有格式問題"
            },
            {
                "step": 3,
                "mcp": "smarttool_mcp",
                "tool": "mcp_jest_runner",
                "action": "運行單元測試",
                "result": "10/10 測試通過"
            },
            {
                "step": 4,
                "mcp": "smarttool_mcp",
                "tool": "zapier_slack",
                "action": "發送 Slack 通知",
                "result": "已通知到 #dev 頻道"
            }
        ]
        
        for step in workflow_steps:
            print(f"步驟 {step['step']}: {step['action']}")
            print(f"  使用 MCP: {step['mcp']}")
            print(f"  使用工具: {step['tool']}")
            print(f"  結果: {step['result']}")
        
        return workflow_steps
    
    async def example_3_cross_mcp(self):
        """示例 3：跨 MCP 協作"""
        print("\n=== 示例 3：跨 MCP 協作 ===")
        
        # 用戶請求
        user_request = "分析這個項目的代碼結構，生成文檔，並部署到 GitHub Pages"
        
        # MCP-Zero 協調多個 MCP
        collaboration_flow = [
            {
                "phase": "分析",
                "mcp": "codeflow_mcp",
                "action": "分析項目結構和依賴",
                "output": "項目結構圖"
            },
            {
                "phase": "文檔生成",
                "mcp": "docs_mcp",
                "action": "根據代碼生成 API 文檔",
                "output": "API 文檔"
            },
            {
                "phase": "格式化",
                "mcp": "smarttool_mcp",
                "tool": "mcp_prettier",
                "action": "格式化生成的文檔",
                "output": "格式化的文檔"
            },
            {
                "phase": "部署",
                "mcp": "smarttool_mcp",
                "tool": "zapier_github",
                "action": "創建 GitHub Pages 部署",
                "output": "部署成功"
            }
        ]
        
        for phase in collaboration_flow:
            print(f"\n階段：{phase['phase']}")
            print(f"  使用 MCP: {phase['mcp']}")
            if 'tool' in phase:
                print(f"  使用工具: {phase['tool']}")
            print(f"  執行操作: {phase['action']}")
            print(f"  輸出結果: {phase['output']}")
        
        return collaboration_flow
    
    async def example_4_intelligent_routing(self):
        """示例 4：智能路由和工具選擇"""
        print("\n=== 示例 4：智能工具選擇 ===")
        
        # 不同的請求場景
        scenarios = [
            {
                "request": "優化這段 Python 代碼的性能",
                "mcp_zero_analysis": {
                    "intent": "performance_optimization",
                    "language": "python",
                    "selected_mcp": "smarttool_mcp",
                    "selected_tool": "aci_performance_profiler",
                    "reason": "ACI.dev 的性能分析器最適合 Python 性能優化"
                }
            },
            {
                "request": "檢查代碼安全漏洞",
                "mcp_zero_analysis": {
                    "intent": "security_scan",
                    "language": "any",
                    "selected_mcp": "smarttool_mcp",
                    "selected_tool": "aci_security_scanner",
                    "reason": "ACI.dev 的安全掃描器提供全面的漏洞檢測"
                }
            },
            {
                "request": "每天早上 9 點自動運行測試",
                "mcp_zero_analysis": {
                    "intent": "automation",
                    "frequency": "daily",
                    "selected_mcp": "smarttool_mcp",
                    "selected_tool": "zapier_automation",
                    "reason": "Zapier 最適合定時任務自動化"
                }
            }
        ]
        
        for scenario in scenarios:
            print(f"\n請求：{scenario['request']}")
            analysis = scenario['mcp_zero_analysis']
            print(f"  意圖識別：{analysis['intent']}")
            print(f"  選擇 MCP：{analysis['selected_mcp']}")
            print(f"  選擇工具：{analysis['selected_tool']}")
            print(f"  選擇原因：{analysis['reason']}")
        
        return scenarios

    async def example_5_error_handling(self):
        """示例 5：錯誤處理和降級"""
        print("\n=== 示例 5：錯誤處理 ===")
        
        # 模擬工具失敗場景
        error_scenario = {
            "request": "發送測試報告到 Slack",
            "primary_attempt": {
                "mcp": "smarttool_mcp",
                "tool": "zapier_slack",
                "status": "failed",
                "error": "Slack API 限流"
            },
            "fallback_strategy": {
                "option_1": {
                    "action": "重試",
                    "delay": "5 秒後重試",
                    "result": "成功"
                },
                "option_2": {
                    "action": "使用備選工具",
                    "tool": "zapier_email",
                    "result": "通過郵件發送報告"
                },
                "option_3": {
                    "action": "本地存儲",
                    "mcp": "local_adapter_mcp",
                    "result": "保存報告到本地，稍後發送"
                }
            }
        }
        
        print(f"請求：{error_scenario['request']}")
        print(f"主要嘗試：{error_scenario['primary_attempt']['tool']} - {error_scenario['primary_attempt']['status']}")
        print(f"錯誤：{error_scenario['primary_attempt']['error']}")
        print("\n降級策略：")
        for option, strategy in error_scenario['fallback_strategy'].items():
            print(f"  {option}: {strategy['action']} - {strategy['result']}")
        
        return error_scenario

async def main():
    """運行所有示例"""
    example = MCPZeroSmartToolExample()
    
    # 運行所有示例
    await example.example_1_simple_format()
    await example.example_2_workflow()
    await example.example_3_cross_mcp()
    await example.example_4_intelligent_routing()
    await example.example_5_error_handling()
    
    print("\n=== 總結 ===")
    print("MCP-Zero 與 SmartTool MCP 的整合提供了：")
    print("1. 自動化的外部工具調用")
    print("2. 智能的工具選擇和路由")
    print("3. 跨 MCP 的無縫協作")
    print("4. 完善的錯誤處理機制")
    print("5. 高效的工作流執行")

if __name__ == "__main__":
    asyncio.run(main())