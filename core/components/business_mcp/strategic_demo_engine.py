#!/usr/bin/env python3
"""
Strategic Demo Engine - 基於 Business MCP 的智能演示引擎
根據用戶畫像、市場策略、ROI分析動態生成演示內容
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random

from .business_manager import business_manager

logger = logging.getLogger(__name__)

class UserSegment(Enum):
    """用戶細分"""
    INDIVIDUAL_DEVELOPER = "individual_developer"    # 個人開發者
    STARTUP_TEAM = "startup_team"                   # 創業團隊
    SME_COMPANY = "sme_company"                     # 中小企業
    ENTERPRISE = "enterprise"                       # 大型企業
    STUDENT = "student"                            # 學生/學習者

class DemoType(Enum):
    """演示類型"""
    EFFICIENCY_BOOST = "efficiency_boost"           # 效率提升演示
    COST_SAVINGS = "cost_savings"                  # 成本節省演示
    QUALITY_IMPROVEMENT = "quality_improvement"     # 質量提升演示
    TEAM_COLLABORATION = "team_collaboration"       # 團隊協作演示
    ENTERPRISE_INTEGRATION = "enterprise_integration" # 企業集成演示

@dataclass
class DemoScenario:
    """演示場景"""
    scenario_id: str
    title: str
    description: str
    target_segment: UserSegment
    demo_type: DemoType
    estimated_time: int  # 分鐘
    key_features: List[str]
    expected_outcome: str
    roi_potential: float
    conversion_probability: float

@dataclass
class CustomerProfile:
    """客戶畫像"""
    user_id: str
    company_size: int
    industry: str
    role: str
    pain_points: List[str]
    budget_range: str
    tech_stack: List[str]
    decision_timeline: str  # "immediate", "1-3months", "3-6months"

class StrategicDemoEngine:
    """戰略演示引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 演示場景庫
        self.demo_scenarios = self._create_demo_scenarios()
        
        # 用戶細分策略
        self.segmentation_rules = self._create_segmentation_rules()
        
        # 演示效果跟踪
        self.demo_analytics = {}
        
    def _create_demo_scenarios(self) -> List[DemoScenario]:
        """創建演示場景庫"""
        scenarios = [
            # 效率提升演示
            DemoScenario(
                scenario_id="efficiency_coding_speed",
                title="10倍編程效率提升演示",
                description="展示如何使用 Smart Intervention 將編程效率提升10倍",
                target_segment=UserSegment.INDIVIDUAL_DEVELOPER,
                demo_type=DemoType.EFFICIENCY_BOOST,
                estimated_time=15,
                key_features=["Smart Intervention", "K2模型", "代碼生成", "自動修復"],
                expected_outcome="用戶看到從30分鐘縮短到3分鐘完成功能開發",
                roi_potential=1000.0,  # 10倍效率提升
                conversion_probability=0.35
            ),
            
            DemoScenario(
                scenario_id="team_productivity_boost",
                title="團隊生產力翻倍演示",
                description="展示團隊如何通過 PowerAutomation 將整體生產力提升2.5倍",
                target_segment=UserSegment.STARTUP_TEAM,
                demo_type=DemoType.EFFICIENCY_BOOST,
                estimated_time=20,
                key_features=["六大工作流", "團隊協作", "進度跟踪", "智能分配"],
                expected_outcome="團隊sprint速度從2週縮短到1週",
                roi_potential=250.0,
                conversion_probability=0.45
            ),
            
            # 成本節省演示  
            DemoScenario(
                scenario_id="k2_cost_optimization",
                title="AI成本節省60%演示",
                description="對比 Claude vs K2 模型，展示如何節省60%的AI調用成本",
                target_segment=UserSegment.SME_COMPANY,
                demo_type=DemoType.COST_SAVINGS,
                estimated_time=12,
                key_features=["K2模型", "智能路由", "成本監控", "質量保證"],
                expected_outcome="月AI成本從¥10,000降到¥4,000",
                roi_potential=600.0,  # 每年節省¥72,000
                conversion_probability=0.55
            ),
            
            DemoScenario(
                scenario_id="infrastructure_savings",
                title="基礎設施成本優化演示",
                description="展示如何通過智能資源管理降低50%基礎設施成本",
                target_segment=UserSegment.ENTERPRISE,
                demo_type=DemoType.COST_SAVINGS,
                estimated_time=25,
                key_features=["資源監控", "自動擴縮容", "成本分析", "預算控制"],
                expected_outcome="年度基礎設施成本從¥500,000降到¥250,000",
                roi_potential=2500.0,
                conversion_probability=0.40
            ),
            
            # 質量提升演示
            DemoScenario(
                scenario_id="code_quality_improvement",
                title="代碼質量提升90%演示",
                description="展示如何通過AI輔助將代碼質量提升90%，bug率降低80%",
                target_segment=UserSegment.INDIVIDUAL_DEVELOPER,
                demo_type=DemoType.QUALITY_IMPROVEMENT,
                estimated_time=18,
                key_features=["代碼審查", "自動測試", "質量監控", "重構建議"],
                expected_outcome="代碼審查通過率從60%提升到95%",
                roi_potential=400.0,
                conversion_probability=0.38
            ),
            
            # 企業集成演示
            DemoScenario(
                scenario_id="enterprise_integration",
                title="企業級系統集成演示",
                description="展示 PowerAutomation 如何無縫集成企業現有系統",
                target_segment=UserSegment.ENTERPRISE,
                demo_type=DemoType.ENTERPRISE_INTEGRATION,
                estimated_time=30,
                key_features=["API集成", "SSO", "權限管理", "數據同步", "合規性"],
                expected_outcome="2週內完成與現有系統集成，無業務中斷",
                roi_potential=5000.0,
                conversion_probability=0.25
            )
        ]
        
        return scenarios
    
    def _create_segmentation_rules(self) -> Dict[str, Any]:
        """創建用戶細分規則"""
        return {
            "company_size_mapping": {
                "1-10": UserSegment.STARTUP_TEAM,
                "11-50": UserSegment.SME_COMPANY,
                "51-500": UserSegment.SME_COMPANY,
                "500+": UserSegment.ENTERPRISE
            },
            "role_mapping": {
                "developer": UserSegment.INDIVIDUAL_DEVELOPER,
                "student": UserSegment.STUDENT,
                "cto": UserSegment.STARTUP_TEAM,
                "tech_lead": UserSegment.SME_COMPANY,
                "architect": UserSegment.ENTERPRISE
            },
            "pain_point_priorities": {
                UserSegment.INDIVIDUAL_DEVELOPER: ["efficiency", "learning", "quality"],
                UserSegment.STARTUP_TEAM: ["speed", "cost", "scalability"],
                UserSegment.SME_COMPANY: ["productivity", "cost_control", "integration"],
                UserSegment.ENTERPRISE: ["security", "compliance", "scale", "roi"]
            }
        }
    
    async def analyze_customer_profile(self, user_data: Dict[str, Any]) -> CustomerProfile:
        """分析客戶畫像"""
        # 提取基本信息
        company_size = user_data.get('company_size', 1)
        role = user_data.get('role', 'developer').lower()
        industry = user_data.get('industry', 'technology')
        
        # 根據規則確定用戶細分
        if company_size <= 10:
            if role in ['student', 'learner']:
                segment = UserSegment.STUDENT
            elif role in ['developer', 'engineer']:
                segment = UserSegment.INDIVIDUAL_DEVELOPER
            else:
                segment = UserSegment.STARTUP_TEAM
        elif company_size <= 500:
            segment = UserSegment.SME_COMPANY
        else:
            segment = UserSegment.ENTERPRISE
            
        # 分析痛點
        pain_points = user_data.get('pain_points', [])
        if not pain_points:
            pain_points = self._infer_pain_points(segment, role, industry)
            
        profile = CustomerProfile(
            user_id=user_data.get('user_id', 'unknown'),
            company_size=company_size,
            industry=industry,
            role=role,
            pain_points=pain_points,
            budget_range=user_data.get('budget_range', 'unknown'),
            tech_stack=user_data.get('tech_stack', []),
            decision_timeline=user_data.get('decision_timeline', '1-3months')
        )
        
        self.logger.info(f"分析客戶畫像: {segment.value} - {pain_points}")
        return profile
    
    def _infer_pain_points(self, segment: UserSegment, role: str, industry: str) -> List[str]:
        """推斷用戶痛點"""
        pain_point_map = {
            UserSegment.INDIVIDUAL_DEVELOPER: [
                "編程效率低", "重複工作多", "代碼質量不穩定", "學習曲線陡峭"
            ],
            UserSegment.STARTUP_TEAM: [
                "開發速度慢", "人力成本高", "產品上市時間長", "技術債務累積"
            ],
            UserSegment.SME_COMPANY: [
                "開發成本高", "項目延期", "質量不穩定", "團隊效率低"
            ],
            UserSegment.ENTERPRISE: [
                "數字化轉型困難", "系統集成複雜", "合規要求嚴格", "創新速度慢"
            ],
            UserSegment.STUDENT: [
                "學習資源有限", "實踐機會少", "技能提升慢", "就業競爭力不足"
            ]
        }
        
        return pain_point_map.get(segment, ["效率提升需求"])
    
    async def recommend_demo_scenarios(self, profile: CustomerProfile) -> List[Dict[str, Any]]:
        """推薦演示場景"""
        # 根據用戶畫像篩選合適的演示場景
        suitable_scenarios = []
        
        for scenario in self.demo_scenarios:
            # 基礎匹配：用戶細分
            segment_match = self._calculate_segment_match(profile, scenario)
            
            # 痛點匹配度
            pain_point_match = self._calculate_pain_point_match(profile, scenario)
            
            # ROI匹配度  
            roi_match = self._calculate_roi_match(profile, scenario)
            
            # 綜合評分
            overall_score = (segment_match * 0.4 + pain_point_match * 0.4 + roi_match * 0.2)
            
            if overall_score > 0.3:  # 閾值過濾
                suitable_scenarios.append({
                    "scenario": scenario,
                    "match_score": overall_score,
                    "segment_match": segment_match,
                    "pain_point_match": pain_point_match,
                    "roi_match": roi_match,
                    "recommended_order": len(suitable_scenarios) + 1
                })
        
        # 按評分排序
        suitable_scenarios.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 選擇前3個最佳場景
        top_scenarios = suitable_scenarios[:3]
        
        self.logger.info(f"推薦演示場景: {len(top_scenarios)}個，最高評分: {top_scenarios[0]['match_score']:.2f}")
        
        return top_scenarios
    
    def _calculate_segment_match(self, profile: CustomerProfile, scenario: DemoScenario) -> float:
        """計算用戶細分匹配度"""
        # 直接匹配
        if self._infer_user_segment(profile) == scenario.target_segment:
            return 1.0
        
        # 相似細分匹配
        similarity_map = {
            UserSegment.INDIVIDUAL_DEVELOPER: {
                UserSegment.STUDENT: 0.6,
                UserSegment.STARTUP_TEAM: 0.4
            },
            UserSegment.STARTUP_TEAM: {
                UserSegment.INDIVIDUAL_DEVELOPER: 0.4,
                UserSegment.SME_COMPANY: 0.7
            },
            UserSegment.SME_COMPANY: {
                UserSegment.STARTUP_TEAM: 0.7,
                UserSegment.ENTERPRISE: 0.5
            },
            UserSegment.ENTERPRISE: {
                UserSegment.SME_COMPANY: 0.5
            }
        }
        
        user_segment = self._infer_user_segment(profile)
        return similarity_map.get(user_segment, {}).get(scenario.target_segment, 0.0)
    
    def _infer_user_segment(self, profile: CustomerProfile) -> UserSegment:
        """推斷用戶細分"""
        if profile.company_size <= 1:
            if profile.role in ['student', 'learner']:
                return UserSegment.STUDENT
            else:
                return UserSegment.INDIVIDUAL_DEVELOPER
        elif profile.company_size <= 50:
            return UserSegment.STARTUP_TEAM
        elif profile.company_size <= 500:
            return UserSegment.SME_COMPANY
        else:
            return UserSegment.ENTERPRISE
    
    def _calculate_pain_point_match(self, profile: CustomerProfile, scenario: DemoScenario) -> float:
        """計算痛點匹配度"""
        if not profile.pain_points:
            return 0.5
        
        # 痛點關鍵詞映射
        pain_point_keywords = {
            "效率": ["efficiency", "speed", "productivity"],
            "成本": ["cost", "savings", "budget"],
            "質量": ["quality", "bug", "reliability"], 
            "團隊": ["team", "collaboration", "coordination"],
            "集成": ["integration", "enterprise", "system"]
        }
        
        scenario_keywords = []
        for feature in scenario.key_features:
            scenario_keywords.extend(feature.lower().split())
        scenario_keywords.extend(scenario.description.lower().split())
        
        matches = 0
        total_pain_points = len(profile.pain_points)
        
        for pain_point in profile.pain_points:
            for keyword_group in pain_point_keywords.values():
                if any(keyword in pain_point.lower() for keyword in keyword_group):
                    if any(keyword in " ".join(scenario_keywords) for keyword in keyword_group):
                        matches += 1
                        break
        
        return matches / total_pain_points if total_pain_points > 0 else 0.0
    
    def _calculate_roi_match(self, profile: CustomerProfile, scenario: DemoScenario) -> float:
        """計算ROI匹配度"""
        # 根據預算範圍和公司規模調整ROI期望
        budget_multiplier = {
            "low": 0.5,
            "medium": 1.0, 
            "high": 1.5,
            "unknown": 0.8
        }
        
        company_size_multiplier = {
            UserSegment.STUDENT: 0.3,
            UserSegment.INDIVIDUAL_DEVELOPER: 0.5,
            UserSegment.STARTUP_TEAM: 0.8,
            UserSegment.SME_COMPANY: 1.0,
            UserSegment.ENTERPRISE: 1.2
        }
        
        budget_factor = budget_multiplier.get(profile.budget_range, 0.8)
        size_factor = company_size_multiplier.get(self._infer_user_segment(profile), 1.0)
        
        # 標準化ROI得分
        roi_score = min(scenario.roi_potential / 1000.0, 1.0)  # 最高1000%ROI = 1.0分
        
        return roi_score * budget_factor * size_factor
    
    async def generate_demo_script(self, scenario: DemoScenario, profile: CustomerProfile) -> Dict[str, Any]:
        """生成演示腳本"""
        # 獲取 Business MCP 數據支持
        business_data = await self._get_business_context(profile)
        
        # 構建個性化演示腳本
        script = {
            "demo_id": f"demo_{scenario.scenario_id}_{profile.user_id}_{int(datetime.now().timestamp())}",
            "scenario": {
                "title": scenario.title,
                "description": scenario.description,
                "estimated_time": scenario.estimated_time
            },
            "personalization": {
                "customer_segment": self._infer_user_segment(profile).value,
                "company_size": profile.company_size,
                "industry": profile.industry,
                "key_pain_points": profile.pain_points[:3]  # 前3個主要痛點
            },
            "demo_flow": self._create_demo_flow(scenario, profile),
            "roi_calculation": self._calculate_demo_roi(scenario, profile, business_data),
            "next_steps": self._generate_next_steps(scenario, profile),
            "conversion_strategy": self._create_conversion_strategy(scenario, profile)
        }
        
        self.logger.info(f"生成演示腳本: {script['demo_id']}")
        return script
    
    async def _get_business_context(self, profile: CustomerProfile) -> Dict[str, Any]:
        """獲取商業上下文數據"""
        # 調用 Business MCP APIs
        roi_scenario = {
            "team_size": min(profile.company_size, 50),  # 限制團隊大小
            "avg_salary": 25000,  # 假設平均月薪
            "current_productivity": 0.6
        }
        
        roi_analysis = await business_manager.generate_roi_analysis(roi_scenario)
        pricing_strategy = await business_manager.generate_pricing_strategy()
        market_analysis = await business_manager.generate_market_analysis()
        
        return {
            "roi_analysis": roi_analysis,
            "pricing": pricing_strategy,
            "market": market_analysis
        }
    
    def _create_demo_flow(self, scenario: DemoScenario, profile: CustomerProfile) -> List[Dict[str, Any]]:
        """創建演示流程"""
        base_flow = [
            {
                "step": 1,
                "title": "問題識別",
                "duration": 2,
                "content": f"針對{profile.industry}行業，{profile.company_size}人規模的{profile.pain_points[0]}問題",
                "demo_action": "show_current_workflow"
            },
            {
                "step": 2, 
                "title": "解決方案展示",
                "duration": scenario.estimated_time - 5,
                "content": f"展示如何通過{', '.join(scenario.key_features[:3])}解決問題",
                "demo_action": "live_demonstration"
            },
            {
                "step": 3,
                "title": "效果對比",
                "duration": 2,
                "content": scenario.expected_outcome,
                "demo_action": "show_before_after_metrics"
            },
            {
                "step": 4,
                "title": "ROI分析",
                "duration": 1,
                "content": f"預計ROI: {scenario.roi_potential:.0f}%",
                "demo_action": "present_roi_calculation"
            }
        ]
        
        return base_flow
    
    def _calculate_demo_roi(self, scenario: DemoScenario, profile: CustomerProfile, business_data: Dict) -> Dict[str, Any]:
        """計算演示ROI"""
        # 基於 Business MCP 數據計算個性化ROI
        team_size = min(profile.company_size, 50)
        monthly_cost = 999 if team_size > 5 else 299  # 簡化定價邏輯
        
        # 計算月度收益
        efficiency_gain = scenario.roi_potential / 100
        avg_salary = 25000  # 月薪
        monthly_savings = team_size * avg_salary * (efficiency_gain / 10)  # 10%效率提升 = 月薪的10%節省
        
        roi_percentage = ((monthly_savings - monthly_cost) / monthly_cost) * 100
        payback_months = monthly_cost / monthly_savings if monthly_savings > 0 else 99
        
        return {
            "monthly_investment": monthly_cost,
            "monthly_savings": round(monthly_savings, 2),
            "roi_percentage": round(roi_percentage, 1),
            "payback_period_months": round(payback_months, 1),
            "annual_net_benefit": round((monthly_savings - monthly_cost) * 12, 2),
            "efficiency_improvement": f"{efficiency_gain:.0f}%"
        }
    
    def _generate_next_steps(self, scenario: DemoScenario, profile: CustomerProfile) -> List[str]:
        """生成後續步驟"""
        segment = self._infer_user_segment(profile)
        
        if segment == UserSegment.INDIVIDUAL_DEVELOPER:
            return [
                "註冊免費試用帳號",
                "完成入門教程",
                "使用個人專案測試核心功能",
                "考慮升級到個人版"
            ]
        elif segment == UserSegment.STARTUP_TEAM:
            return [
                "安排團隊試用",
                "設置團隊工作區",
                "評估投資回報率",
                "制定部署計劃"
            ]
        elif segment == UserSegment.SME_COMPANY:
            return [
                "進行技術評估",
                "與現有工具集成測試",
                "計算詳細ROI",
                "申請概念驗證"
            ]
        else:  # Enterprise
            return [
                "安排技術深度評估",
                "企業安全與合規審查",
                "制定分階段部署方案",
                "商務談判與合約簽署"
            ]
    
    def _create_conversion_strategy(self, scenario: DemoScenario, profile: CustomerProfile) -> Dict[str, Any]:
        """創建轉換策略"""
        segment = self._infer_user_segment(profile)
        
        strategies = {
            UserSegment.INDIVIDUAL_DEVELOPER: {
                "primary_cta": "立即免費試用",
                "urgency": "限時30天免費試用",
                "incentive": "首月免費，新用戶獲得500積分",
                "follow_up": "7天後發送教程郵件"
            },
            UserSegment.STARTUP_TEAM: {
                "primary_cta": "預約團隊演示",
                "urgency": "本月簽約享受20%折扣",
                "incentive": "免費3個月技術支持",
                "follow_up": "3天內銷售跟進"
            },
            UserSegment.SME_COMPANY: {
                "primary_cta": "申請企業試用",
                "urgency": "Q4預算優惠，最高30%折扣",
                "incentive": "免費定制集成服務",
                "follow_up": "1天內技術顧問聯繫"
            },
            UserSegment.ENTERPRISE: {
                "primary_cta": "聯繫企業銷售",
                "urgency": "年度合約特殊優惠",
                "incentive": "專屬客戶成功經理",
                "follow_up": "當天內高級銷售聯繫"
            }
        }
        
        return strategies.get(segment, strategies[UserSegment.INDIVIDUAL_DEVELOPER])

# 全局演示引擎實例
strategic_demo_engine = StrategicDemoEngine()

# 演示功能
async def demo_strategic_demo_engine():
    """戰略演示引擎演示"""
    print("🎯 PowerAutomation 戰略演示引擎演示")
    print("=" * 60)
    
    # 模擬不同類型的客戶
    test_customers = [
        {
            "user_id": "dev_001",
            "company_size": 1,
            "role": "developer", 
            "industry": "fintech",
            "pain_points": ["編程效率低", "代碼質量不穩定"],
            "budget_range": "low",
            "decision_timeline": "immediate"
        },
        {
            "user_id": "startup_001",
            "company_size": 15,
            "role": "cto",
            "industry": "e-commerce",
            "pain_points": ["開發速度慢", "人力成本高"],
            "budget_range": "medium",
            "decision_timeline": "1-3months"
        },
        {
            "user_id": "enterprise_001", 
            "company_size": 500,
            "role": "architect",
            "industry": "manufacturing",
            "pain_points": ["數字化轉型困難", "系統集成複雜"],
            "budget_range": "high",
            "decision_timeline": "3-6months"
        }
    ]
    
    for i, customer_data in enumerate(test_customers, 1):
        print(f"\n{i}. 客戶畫像分析: {customer_data['role']} @ {customer_data['industry']}")
        print("-" * 50)
        
        # 分析客戶畫像
        profile = await strategic_demo_engine.analyze_customer_profile(customer_data)
        print(f"用戶細分: {strategic_demo_engine._infer_user_segment(profile).value}")
        print(f"公司規模: {profile.company_size}人")
        print(f"主要痛點: {', '.join(profile.pain_points[:2])}")
        
        # 推薦演示場景
        recommendations = await strategic_demo_engine.recommend_demo_scenarios(profile)
        print(f"\n推薦演示場景 (共{len(recommendations)}個):")
        
        for j, rec in enumerate(recommendations, 1):
            scenario = rec["scenario"]
            print(f"  {j}. {scenario.title}")
            print(f"     匹配度: {rec['match_score']:.2f} | 轉換率: {scenario.conversion_probability:.1%}")
            print(f"     預估ROI: {scenario.roi_potential:.0f}% | 時長: {scenario.estimated_time}分鐘")
        
        # 生成最佳演示腳本
        if recommendations:
            best_scenario = recommendations[0]["scenario"]
            demo_script = await strategic_demo_engine.generate_demo_script(best_scenario, profile)
            
            print(f"\n最佳演示腳本: {demo_script['demo_id']}")
            print(f"演示主題: {demo_script['scenario']['title']}")
            print(f"個性化ROI:")
            roi = demo_script['roi_calculation']
            print(f"  - 月度投資: ¥{roi['monthly_investment']}")
            print(f"  - 月度節省: ¥{roi['monthly_savings']}")
            print(f"  - ROI: {roi['roi_percentage']}%")
            print(f"  - 回本期: {roi['payback_period_months']}個月")
            
            conversion = demo_script['conversion_strategy']
            print(f"轉換策略: {conversion['primary_cta']} | {conversion['urgency']}")
        
        print()
    
    return {
        "customers_analyzed": len(test_customers),
        "scenarios_generated": sum(len(rec) for customer_data in test_customers 
                                 for rec in [await strategic_demo_engine.recommend_demo_scenarios(
                                     await strategic_demo_engine.analyze_customer_profile(customer_data))]),
        "engine_ready": True
    }

if __name__ == "__main__":
    result = asyncio.run(demo_strategic_demo_engine())
    print(f"\n🎉 戰略演示引擎演示完成！")