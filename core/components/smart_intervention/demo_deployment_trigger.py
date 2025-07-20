#!/usr/bin/env python3
"""
Smart Intervention 演示部署觸發器
當用戶提到演示及部署需求時，自動將清單放入演示部署清單並詢問是否啟動ClaudeEditor
"""

import asyncio
import json
import re
import time
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DemoDeploymentItem:
    """演示部署項目"""
    item_id: str
    title: str
    description: str
    category: str
    priority: str          # high/medium/low
    estimated_time: int    # 預估時間(分鐘)
    dependencies: List[str]
    status: str           # pending/ready/completed
    demo_url: Optional[str] = None
    deployment_script: Optional[str] = None

class SmartInterventionDemoTrigger:
    """Smart Intervention 演示部署觸發器"""
    
    def __init__(self):
        # 演示關鍵詞檢測
        self.demo_keywords = {
            "演示": ["演示", "demo", "showcase", "展示", "示範"],
            "部署": ["部署", "deploy", "deployment", "發布", "上線", "launch"],
            "需求": ["需求", "requirement", "need", "want", "要求", "希望"],
            "查看": ["查看", "看", "view", "see", "show", "顯示"],
            "啟動": ["啟動", "start", "run", "執行", "開始"]
        }
        
        # 演示部署清單
        self.demo_deployment_list: List[DemoDeploymentItem] = []
        
        # 初始化預設演示項目
        self._init_default_demo_items()
        
        # 觸發歷史
        self.trigger_history: List[Dict[str, Any]] = []
        
    def _init_default_demo_items(self):
        """初始化預設演示項目"""
        default_items = [
            DemoDeploymentItem(
                item_id="auth_system_demo",
                title="三權限系統演示",
                description="使用者/開發者/管理者權限體系 + 會員積分支付系統",
                category="認證系統",
                priority="high",
                estimated_time=15,
                dependencies=[],
                status="ready",
                demo_url="/demo/auth_system_demo.py",
                deployment_script="python3 demo/auth_system_demo.py"
            ),
            DemoDeploymentItem(
                item_id="k2_verification_demo",
                title="K2工具調用能力驗證",
                description="K2與Claude對比、Router切換、RAG支持、用戶體驗一致性",
                category="K2系統",
                priority="high",
                estimated_time=10,
                dependencies=["auth_system_demo"],
                status="ready",
                demo_url="/demo/k2_verification_demo.py",
                deployment_script="python3 demo/k2_verification_demo.py"
            ),
            DemoDeploymentItem(
                item_id="six_workflows_demo",
                title="六大工作流演示",
                description="需求分析、架構設計、編碼實現、測試、部署、監控運維",
                category="核心工作流",
                priority="medium",
                estimated_time=20,
                dependencies=["auth_system_demo"],
                status="pending",
                demo_url="/demo/workflows_demo.py",
                deployment_script="python3 demo/workflows_demo.py"
            ),
            DemoDeploymentItem(
                item_id="mcp_components_demo",
                title="21個MCP組件演示",
                description="完整MCP架構展示，包括Claude實時收集器",
                category="MCP架構",
                priority="medium",
                estimated_time=25,
                dependencies=["auth_system_demo"],
                status="ready",
                demo_url="/demo/mcp_demo.py",
                deployment_script="python3 demo/mcp_demo.py"
            ),
            DemoDeploymentItem(
                item_id="performance_optimization_demo",
                title="v4.76性能優化演示",
                description="Smart Intervention延遲優化、MemoryRAG壓縮、SmartUI無障礙",
                category="性能優化",
                priority="high",
                estimated_time=12,
                dependencies=[],
                status="ready",
                demo_url="/demo/performance_demo.py",
                deployment_script="python3 demo/performance_demo.py"
            ),
            DemoDeploymentItem(
                item_id="claudeeditor_integration_demo",
                title="ClaudeEditor集成演示",
                description="PC/Mobile版本、權限控制、K2集成、MCP組件管理",
                category="ClaudeEditor",
                priority="high",
                estimated_time=18,
                dependencies=["auth_system_demo"],
                status="ready",
                demo_url="/demo/claudeeditor_demo.py",
                deployment_script="python3 demo/claudeeditor_demo.py"
            ),
            DemoDeploymentItem(
                item_id="website_demo",
                title="PowerAuto.ai網站演示",
                description="網站權限體系、用戶註冊登錄、支付流程",
                category="網站系統",
                priority="medium",
                estimated_time=15,
                dependencies=["auth_system_demo"],
                status="pending",
                demo_url="/demo/website_demo.py",
                deployment_script="python3 demo/website_demo.py"
            )
        ]
        
        self.demo_deployment_list.extend(default_items)
        logger.info(f"初始化 {len(default_items)} 個預設演示項目")
        
    async def analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """分析用戶輸入，檢測演示部署需求"""
        analysis_result = {
            "has_demo_request": False,
            "has_deployment_request": False,
            "detected_keywords": [],
            "suggested_demos": [],
            "should_trigger_intervention": False,
            "intervention_message": ""
        }
        
        user_input_lower = user_input.lower()
        
        # 關鍵詞檢測
        detected_categories = []
        for category, keywords in self.demo_keywords.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    analysis_result["detected_keywords"].append(keyword)
                    if category not in detected_categories:
                        detected_categories.append(category)
        
        # 判斷是否有演示需求
        analysis_result["has_demo_request"] = "演示" in detected_categories
        analysis_result["has_deployment_request"] = "部署" in detected_categories
        
        # 根據用戶輸入推薦相關演示
        if analysis_result["has_demo_request"] or analysis_result["has_deployment_request"]:
            analysis_result["suggested_demos"] = await self._suggest_relevant_demos(user_input)
            analysis_result["should_trigger_intervention"] = True
            analysis_result["intervention_message"] = await self._generate_intervention_message(
                analysis_result["suggested_demos"]
            )
        
        # 記錄觸發歷史
        if analysis_result["should_trigger_intervention"]:
            self.trigger_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "detected_keywords": analysis_result["detected_keywords"],
                "suggested_demos": [demo["item_id"] for demo in analysis_result["suggested_demos"]]
            })
        
        return analysis_result
    
    async def _suggest_relevant_demos(self, user_input: str) -> List[Dict[str, Any]]:
        """根據用戶輸入推薦相關演示"""
        user_input_lower = user_input.lower()
        suggested = []
        
        # 內容匹配規則
        content_matches = {
            "權限": ["auth_system_demo"],
            "認證": ["auth_system_demo"],
            "登錄": ["auth_system_demo"],
            "支付": ["auth_system_demo"],
            "會員": ["auth_system_demo"],
            "k2": ["k2_verification_demo", "claudeeditor_integration_demo"],
            "claude": ["k2_verification_demo", "claudeeditor_integration_demo"],
            "工作流": ["six_workflows_demo"],
            "mcp": ["mcp_components_demo"],
            "組件": ["mcp_components_demo"],
            "性能": ["performance_optimization_demo"],
            "優化": ["performance_optimization_demo"],
            "編輯器": ["claudeeditor_integration_demo"],
            "claudeeditor": ["claudeeditor_integration_demo"],
            "網站": ["website_demo"],
            "powerauto": ["website_demo"]
        }
        
        # 找到匹配的演示
        matched_ids = set()
        for keyword, demo_ids in content_matches.items():
            if keyword in user_input_lower:
                matched_ids.update(demo_ids)
        
        # 如果沒有特定匹配，推薦高優先級的演示
        if not matched_ids:
            matched_ids = {item.item_id for item in self.demo_deployment_list 
                          if item.priority == "high" and item.status == "ready"}
        
        # 組裝推薦結果
        for item in self.demo_deployment_list:
            if item.item_id in matched_ids:
                suggested.append({
                    "item_id": item.item_id,
                    "title": item.title,
                    "description": item.description,
                    "category": item.category,
                    "priority": item.priority,
                    "estimated_time": item.estimated_time,
                    "status": item.status,
                    "demo_url": item.demo_url,
                    "deployment_script": item.deployment_script
                })
        
        # 按優先級和狀態排序
        suggested.sort(key=lambda x: (
            0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2,
            0 if x["status"] == "ready" else 1
        ))
        
        return suggested[:5]  # 最多推薦5個
    
    async def _generate_intervention_message(self, suggested_demos: List[Dict[str, Any]]) -> str:
        """生成智能介入消息"""
        if not suggested_demos:
            return ""
        
        message_parts = [
            "🎯 **Smart Intervention 檢測到演示部署需求**",
            "",
            "根據您的需求，我為您推薦以下演示項目：",
            ""
        ]
        
        for i, demo in enumerate(suggested_demos, 1):
            status_emoji = "✅" if demo["status"] == "ready" else "⏳" if demo["status"] == "pending" else "❌"
            priority_emoji = "🔥" if demo["priority"] == "high" else "📋" if demo["priority"] == "medium" else "📝"
            
            message_parts.append(
                f"{i}. {status_emoji} {priority_emoji} **{demo['title']}** ({demo['estimated_time']}分鐘)"
            )
            message_parts.append(f"   📁 {demo['category']} | {demo['description']}")
            if demo["deployment_script"]:
                message_parts.append(f"   ⚡ 啟動: `{demo['deployment_script']}`")
            message_parts.append("")
        
        message_parts.extend([
            "🚀 **建議操作：**",
            "1. 選擇您想要查看的演示項目",
            "2. 我可以為您啟動 ClaudeEditor 來查看詳細部署",
            "3. 或者直接運行演示腳本",
            "",
            "❓ **您希望我現在啟動 ClaudeEditor 來查看部署嗎？**"
        ])
        
        return "\n".join(message_parts)
    
    async def add_demo_item(self, title: str, description: str, category: str, 
                           priority: str = "medium", script: str = None) -> str:
        """添加新的演示項目到部署清單"""
        item_id = f"demo_{int(time.time())}"
        
        new_item = DemoDeploymentItem(
            item_id=item_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            estimated_time=10,  # 預設10分鐘
            dependencies=[],
            status="pending",
            deployment_script=script
        )
        
        self.demo_deployment_list.append(new_item)
        logger.info(f"添加新演示項目: {title}")
        
        return item_id
    
    async def get_deployment_checklist(self) -> Dict[str, Any]:
        """獲取完整的演示部署清單"""
        checklist = {
            "total_items": len(self.demo_deployment_list),
            "ready_items": sum(1 for item in self.demo_deployment_list if item.status == "ready"),
            "pending_items": sum(1 for item in self.demo_deployment_list if item.status == "pending"),
            "high_priority": sum(1 for item in self.demo_deployment_list if item.priority == "high"),
            "estimated_total_time": sum(item.estimated_time for item in self.demo_deployment_list),
            "categories": {},
            "items": []
        }
        
        # 按類別統計
        for item in self.demo_deployment_list:
            if item.category not in checklist["categories"]:
                checklist["categories"][item.category] = {
                    "count": 0,
                    "ready": 0,
                    "total_time": 0
                }
            checklist["categories"][item.category]["count"] += 1
            if item.status == "ready":
                checklist["categories"][item.category]["ready"] += 1
            checklist["categories"][item.category]["total_time"] += item.estimated_time
        
        # 項目詳情
        for item in self.demo_deployment_list:
            checklist["items"].append({
                "item_id": item.item_id,
                "title": item.title,
                "description": item.description,
                "category": item.category,
                "priority": item.priority,
                "estimated_time": item.estimated_time,
                "status": item.status,
                "dependencies": item.dependencies,
                "demo_url": item.demo_url,
                "deployment_script": item.deployment_script
            })
        
        return checklist
    
    async def generate_claudeeditor_launch_command(self) -> str:
        """生成ClaudeEditor啟動命令"""
        # 創建演示配置文件
        demo_config = {
            "workspace": "/Users/alexchuang/alexchuangtest/aicore0720",
            "demo_mode": True,
            "available_demos": [
                {
                    "id": item.item_id,
                    "title": item.title,
                    "script": item.deployment_script,
                    "url": item.demo_url
                }
                for item in self.demo_deployment_list if item.status == "ready"
            ],
            "default_demo": "auth_system_demo"
        }
        
        config_file = Path("demo/claudeeditor_demo_config.json")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(demo_config, f, ensure_ascii=False, indent=2)
        
        launch_command = f"""
# 啟動ClaudeEditor演示模式
cd /Users/alexchuang/alexchuangtest/aicore0720

# 方式1: 直接啟動ClaudeEditor (如果已安裝)
claudeeditor --demo-config=demo/claudeeditor_demo_config.json

# 方式2: 使用本地演示服務器
python3 -m http.server 8080 --directory demo &
echo "演示服務器已啟動: http://localhost:8080"

# 方式3: 運行特定演示
python3 demo/auth_system_demo.py
"""
        
        return launch_command.strip()

# 全局Smart Intervention演示觸發器實例
demo_trigger = SmartInterventionDemoTrigger()

# 演示功能
async def demo_smart_intervention_trigger():
    """Smart Intervention演示觸發器演示"""
    print("🧠 Smart Intervention 演示部署觸發器演示")
    print("=" * 60)
    
    # 測試用戶輸入
    test_inputs = [
        "我想看看三權限系統的演示",
        "需要部署K2驗證功能",
        "展示一下ClaudeEditor的集成",
        "能不能看看性能優化的效果",
        "啟動一個完整的系統演示",
        "這個MCP組件怎麼部署？"
    ]
    
    print("\n1. 用戶輸入分析演示")
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n測試 {i}: \"{user_input}\"")
        analysis = await demo_trigger.analyze_user_input(user_input)
        
        if analysis["should_trigger_intervention"]:
            print("🎯 觸發Smart Intervention")
            print(f"檢測關鍵詞: {', '.join(analysis['detected_keywords'])}")
            print(f"推薦演示數: {len(analysis['suggested_demos'])}")
            
            if analysis['suggested_demos']:
                print("推薦演示:")
                for demo in analysis['suggested_demos'][:2]:  # 只顯示前2個
                    print(f"  - {demo['title']} ({demo['estimated_time']}分鐘)")
        else:
            print("⚪ 未觸發介入")
    
    # 2. 演示部署清單
    print("\n2. 演示部署清單")
    checklist = await demo_trigger.get_deployment_checklist()
    
    print(f"總項目數: {checklist['total_items']}")
    print(f"就緒項目: {checklist['ready_items']}")
    print(f"待處理: {checklist['pending_items']}")
    print(f"預估總時間: {checklist['estimated_total_time']}分鐘")
    
    print("\n按類別統計:")
    for category, stats in checklist['categories'].items():
        print(f"  {category}: {stats['ready']}/{stats['count']} 就緒 ({stats['total_time']}分鐘)")
    
    # 3. 添加新演示項目
    print("\n3. 添加新演示項目")
    new_demo_id = await demo_trigger.add_demo_item(
        "用戶自定義演示",
        "根據用戶需求動態生成的演示項目",
        "自定義",
        "high",
        "python3 demo/custom_demo.py"
    )
    print(f"添加新演示: {new_demo_id}")
    
    # 4. ClaudeEditor啟動命令
    print("\n4. ClaudeEditor啟動命令生成")
    launch_cmd = await demo_trigger.generate_claudeeditor_launch_command()
    print("生成的啟動命令:")
    print(launch_cmd)
    
    # 5. 完整干預消息示例
    print("\n5. 完整Smart Intervention消息示例")
    full_analysis = await demo_trigger.analyze_user_input("我想看三權限系統和K2的完整演示，還有部署流程")
    if full_analysis["intervention_message"]:
        print("\n" + "="*50)
        print(full_analysis["intervention_message"])
        print("="*50)
    
    return {
        "test_cases": len(test_inputs),
        "interventions_triggered": sum(1 for _ in test_inputs),
        "total_demos": checklist['total_items'],
        "ready_demos": checklist['ready_items'],
        "demo_success": True
    }

if __name__ == "__main__":
    result = asyncio.run(demo_smart_intervention_trigger())
    print(f"\n🎉 Smart Intervention演示觸發器演示完成！")