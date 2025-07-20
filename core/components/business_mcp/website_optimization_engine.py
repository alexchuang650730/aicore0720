#!/usr/bin/env python3
"""
Business MCP 驅動的網站增量優化引擎
基於戰略演示系統來持續優化網站性能和轉換率
"""

import asyncio
import json
import logging
import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib

from .strategic_demo_engine import strategic_demo_engine
from .business_manager import business_manager

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """優化類型"""
    CONVERSION_RATE = "conversion_rate"      # 轉換率優化
    USER_ENGAGEMENT = "user_engagement"      # 用戶參與度
    RETENTION = "retention"                  # 用戶留存
    MONETIZATION = "monetization"            # 變現優化
    PERFORMANCE = "performance"              # 性能優化

class TestStatus(Enum):
    """測試狀態"""
    DRAFT = "draft"                         # 草稿
    RUNNING = "running"                     # 運行中
    COMPLETED = "completed"                 # 已完成
    PAUSED = "paused"                      # 暫停
    FAILED = "failed"                      # 失敗

@dataclass
class OptimizationMetric:
    """優化指標"""
    metric_name: str
    current_value: float
    target_value: float
    improvement_percentage: float
    confidence_level: float
    statistical_significance: bool

@dataclass
class ABTestVariant:
    """A/B 測試變體"""
    variant_id: str
    name: str
    description: str
    traffic_allocation: float               # 流量分配百分比
    changes: Dict[str, Any]                # 變更內容
    performance_metrics: Dict[str, float]   # 性能指標
    conversion_rate: float
    sample_size: int
    created_at: datetime

@dataclass
class WebsiteOptimizationExperiment:
    """網站優化實驗"""
    experiment_id: str
    name: str
    description: str
    optimization_type: OptimizationType
    target_segment: str                     # 目標用戶群體
    hypothesis: str                         # 假設
    variants: List[ABTestVariant]
    control_group: ABTestVariant
    status: TestStatus
    start_date: datetime
    end_date: Optional[datetime]
    expected_impact: Dict[str, float]
    actual_results: Optional[Dict[str, float]]
    business_rationale: str                 # 商業邏輯

class WebsiteOptimizationEngine:
    """網站優化引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 實驗管理
        self.active_experiments: Dict[str, WebsiteOptimizationExperiment] = {}
        self.completed_experiments: List[WebsiteOptimizationExperiment] = []
        
        # 優化策略庫
        self.optimization_strategies = self._create_optimization_strategies()
        
        # 用戶行為追蹤
        self.user_behavior_data: Dict[str, List[Dict]] = {}
        
        # 性能基線
        self.performance_baseline = {
            "conversion_rate": 0.05,          # 5% 基線轉換率
            "bounce_rate": 0.65,              # 65% 跳出率
            "average_session_duration": 180,  # 3分鐘
            "pages_per_session": 2.5,
            "demo_completion_rate": 0.25,     # 25% 演示完成率
            "signup_rate": 0.12,              # 12% 註冊率
            "trial_to_paid_rate": 0.30        # 30% 試用轉付費率
        }
        
    def _create_optimization_strategies(self) -> Dict[str, Dict[str, Any]]:
        """創建優化策略庫"""
        return {
            "hero_section_optimization": {
                "type": OptimizationType.CONVERSION_RATE,
                "target_metrics": ["signup_rate", "demo_request_rate"],
                "variants": [
                    {
                        "name": "價值主張強化",
                        "changes": {
                            "headline": "10倍編程效率，60%成本節省 - PowerAuto.ai",
                            "subheadline": "Claude + K2雙AI架構，讓每個開發者都能享受AI超能力",
                            "cta_text": "立即免費體驗10倍效率",
                            "hero_image": "efficiency_visualization.png"
                        }
                    },
                    {
                        "name": "ROI焦點",
                        "changes": {
                            "headline": "每月節省¥50,000開發成本",
                            "subheadline": "智能AI助手讓你的團隊生產力提升250%",
                            "cta_text": "計算我的ROI",
                            "hero_image": "roi_calculator.png"
                        }
                    },
                    {
                        "name": "社會證明",
                        "changes": {
                            "headline": "1000+開發團隊的共同選擇",
                            "subheadline": "從創業公司到Fortune 500，都在用PowerAuto.ai提升效率",
                            "cta_text": "加入成功的開發者",
                            "hero_image": "social_proof.png"
                        }
                    }
                ]
            },
            "pricing_page_optimization": {
                "type": OptimizationType.MONETIZATION,
                "target_metrics": ["trial_to_paid_rate", "plan_upgrade_rate"],
                "variants": [
                    {
                        "name": "價值導向定價",
                        "changes": {
                            "pricing_model": "value_based",
                            "highlight_savings": True,
                            "show_roi_calculator": True,
                            "testimonials": "customer_success_stories"
                        }
                    },
                    {
                        "name": "錨定效應",
                        "changes": {
                            "pricing_model": "anchoring",
                            "enterprise_plan_prominent": True,
                            "discount_badges": True,
                            "urgency_elements": "limited_time_offer"
                        }
                    }
                ]
            },
            "demo_flow_optimization": {
                "type": OptimizationType.USER_ENGAGEMENT,
                "target_metrics": ["demo_completion_rate", "demo_to_signup_rate"],
                "variants": [
                    {
                        "name": "個性化演示路徑",
                        "changes": {
                            "demo_type": "personalized",
                            "user_segmentation": True,
                            "adaptive_content": True,
                            "real_time_roi": True
                        }
                    },
                    {
                        "name": "互動式演示",
                        "changes": {
                            "demo_type": "interactive",
                            "hands_on_experience": True,
                            "progress_indicators": True,
                            "gamification": True
                        }
                    }
                ]
            },
            "onboarding_optimization": {
                "type": OptimizationType.RETENTION,
                "target_metrics": ["user_activation_rate", "day7_retention"],
                "variants": [
                    {
                        "name": "漸進式入門",
                        "changes": {
                            "onboarding_type": "progressive",
                            "step_by_step_guidance": True,
                            "achievement_system": True,
                            "personal_assistant": True
                        }
                    },
                    {
                        "name": "快速成功體驗",
                        "changes": {
                            "onboarding_type": "quick_wins",
                            "immediate_value": True,
                            "template_gallery": True,
                            "one_click_setup": True
                        }
                    }
                ]
            }
        }
    
    async def analyze_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """分析優化機會"""
        self.logger.info("分析網站優化機會")
        
        # 獲取 Business MCP 數據
        market_analysis = await business_manager.generate_market_analysis()
        acquisition_strategy = await business_manager.generate_customer_acquisition_strategy()
        
        # 分析當前性能
        current_metrics = await self._get_current_performance_metrics()
        
        # 識別優化機會
        opportunities = []
        
        for strategy_name, strategy in self.optimization_strategies.items():
            opportunity_score = await self._calculate_opportunity_score(
                strategy, current_metrics, market_analysis
            )
            
            if opportunity_score > 0.6:  # 高潛力機會
                opportunities.append({
                    "strategy_name": strategy_name,
                    "opportunity_score": opportunity_score,
                    "expected_impact": await self._estimate_impact(strategy, current_metrics),
                    "implementation_complexity": self._assess_complexity(strategy),
                    "business_rationale": await self._generate_business_rationale(
                        strategy, market_analysis, acquisition_strategy
                    ),
                    "recommended_variants": strategy["variants"][:2]  # 推薦前2個變體
                })
        
        # 按機會分數排序
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        self.logger.info(f"識別出 {len(opportunities)} 個優化機會")
        return opportunities
    
    async def _get_current_performance_metrics(self) -> Dict[str, float]:
        """獲取當前性能指標"""
        # 在實際環境中，這裡會從分析工具獲取真實數據
        # 這裡使用模擬數據 + 一些隨機變化
        base_metrics = self.performance_baseline.copy()
        
        # 添加一些隨機變化來模擬真實波動
        for metric, value in base_metrics.items():
            variation = random.uniform(-0.1, 0.1)  # ±10% 變化
            base_metrics[metric] = value * (1 + variation)
        
        return base_metrics
    
    async def _calculate_opportunity_score(self, strategy: Dict[str, Any], 
                                         current_metrics: Dict[str, float],
                                         market_analysis: Dict[str, Any]) -> float:
        """計算優化機會分數"""
        score = 0.0
        
        # 基於當前性能差距
        target_metrics = strategy.get("target_metrics", [])
        for metric in target_metrics:
            if metric in current_metrics:
                current_value = current_metrics[metric]
                # 假設行業平均水平
                industry_benchmark = self.performance_baseline[metric] * 1.2
                if current_value < industry_benchmark:
                    gap_score = (industry_benchmark - current_value) / industry_benchmark
                    score += gap_score * 0.4
        
        # 基於市場潛力
        market_size = market_analysis.get("market_size", {})
        if "serviceable_obtainable_market" in market_size:
            market_potential = 0.3  # 假設我們能獲取30%的SOM
            score += market_potential * 0.3
        
        # 基於競爭優勢
        advantages = market_analysis.get("competitive_landscape", {}).get("our_advantages", [])
        if len(advantages) > 3:
            score += 0.3
        
        return min(score, 1.0)  # 限制在0-1之間
    
    async def _estimate_impact(self, strategy: Dict[str, Any], 
                             current_metrics: Dict[str, float]) -> Dict[str, float]:
        """估算優化影響"""
        impact = {}
        target_metrics = strategy.get("target_metrics", [])
        
        for metric in target_metrics:
            if metric in current_metrics:
                current_value = current_metrics[metric]
                # 基於優化類型估算提升幅度
                if strategy["type"] == OptimizationType.CONVERSION_RATE:
                    improvement = 0.15  # 15% 提升
                elif strategy["type"] == OptimizationType.USER_ENGAGEMENT:
                    improvement = 0.25  # 25% 提升
                elif strategy["type"] == OptimizationType.RETENTION:
                    improvement = 0.20  # 20% 提升
                elif strategy["type"] == OptimizationType.MONETIZATION:
                    improvement = 0.30  # 30% 提升
                else:
                    improvement = 0.10  # 10% 提升
                
                impact[metric] = {
                    "current": current_value,
                    "estimated": current_value * (1 + improvement),
                    "improvement_percentage": improvement * 100
                }
        
        return impact
    
    def _assess_complexity(self, strategy: Dict[str, Any]) -> str:
        """評估實施複雜度"""
        variants_count = len(strategy.get("variants", []))
        
        if variants_count <= 2:
            return "低"
        elif variants_count <= 4:
            return "中"
        else:
            return "高"
    
    async def _generate_business_rationale(self, strategy: Dict[str, Any],
                                         market_analysis: Dict[str, Any],
                                         acquisition_strategy: Dict[str, Any]) -> str:
        """生成商業邏輯說明"""
        strategy_type = strategy["type"]
        
        if strategy_type == OptimizationType.CONVERSION_RATE:
            return f"基於市場分析，我們在{market_analysis.get('target_segments', [])[0].get('segment', '目標市場')}有巨大潛力。通過優化轉換率，預計能將{acquisition_strategy.get('conversion_funnel', {}).get('purchase', {}).get('target', '600')}月度付費用戶提升30%。"
        elif strategy_type == OptimizationType.USER_ENGAGEMENT:
            return "提升用戶參與度能直接影響留存率和LTV。根據Business MCP分析，高參與度用戶的LTV是普通用戶的3倍。"
        elif strategy_type == OptimizationType.RETENTION:
            return f"用戶留存直接影響LTV/CAC比率。目標LTV/CAC比率為{acquisition_strategy.get('key_metrics', {}).get('ltv_cac_ratio', 20)}，優化留存能顯著改善單位經濟效益。"
        elif strategy_type == OptimizationType.MONETIZATION:
            return "根據定價策略分析，優化變現流程能提升ARPU。競爭優勢在於我們的成本節省價值主張，需要在定價頁面強化這一點。"
        else:
            return "性能優化能改善用戶體驗，間接提升所有漏斗指標。"
    
    async def create_ab_test_experiment(self, strategy_name: str, 
                                      variants_to_test: List[str]) -> WebsiteOptimizationExperiment:
        """創建 A/B 測試實驗"""
        self.logger.info(f"創建 A/B 測試實驗: {strategy_name}")
        
        strategy = self.optimization_strategies[strategy_name]
        experiment_id = f"exp_{int(time.time())}_{strategy_name}"
        
        # 創建控制組
        control_group = ABTestVariant(
            variant_id=f"{experiment_id}_control",
            name="控制組（當前版本）",
            description="當前網站版本，作為基線對比",
            traffic_allocation=0.5,
            changes={},
            performance_metrics={},
            conversion_rate=0.0,
            sample_size=0,
            created_at=datetime.now()
        )
        
        # 創建測試變體
        variants = []
        traffic_per_variant = 0.5 / len(variants_to_test)
        
        for i, variant_name in enumerate(variants_to_test):
            variant_config = next(
                (v for v in strategy["variants"] if v["name"] == variant_name), 
                strategy["variants"][0]
            )
            
            variant = ABTestVariant(
                variant_id=f"{experiment_id}_variant_{i+1}",
                name=variant_config["name"],
                description=f"測試變體: {variant_config['name']}",
                traffic_allocation=traffic_per_variant,
                changes=variant_config["changes"],
                performance_metrics={},
                conversion_rate=0.0,
                sample_size=0,
                created_at=datetime.now()
            )
            variants.append(variant)
        
        # 獲取商業邏輯
        market_analysis = await business_manager.generate_market_analysis()
        acquisition_strategy = await business_manager.generate_customer_acquisition_strategy()
        business_rationale = await self._generate_business_rationale(
            strategy, market_analysis, acquisition_strategy
        )
        
        # 創建實驗
        experiment = WebsiteOptimizationExperiment(
            experiment_id=experiment_id,
            name=f"{strategy_name} 優化實驗",
            description=f"測試 {strategy_name} 的不同優化方案",
            optimization_type=strategy["type"],
            target_segment="all_users",
            hypothesis=f"通過優化 {strategy_name}，能夠提升 {', '.join(strategy['target_metrics'])}",
            variants=variants,
            control_group=control_group,
            status=TestStatus.DRAFT,
            start_date=datetime.now(),
            end_date=None,
            expected_impact=await self._estimate_impact(strategy, await self._get_current_performance_metrics()),
            actual_results=None,
            business_rationale=business_rationale
        )
        
        self.active_experiments[experiment_id] = experiment
        
        self.logger.info(f"A/B 測試實驗已創建: {experiment_id}")
        return experiment
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """啟動實驗"""
        if experiment_id not in self.active_experiments:
            return False
        
        experiment = self.active_experiments[experiment_id]
        experiment.status = TestStatus.RUNNING
        experiment.start_date = datetime.now()
        
        self.logger.info(f"實驗已啟動: {experiment_id}")
        return True
    
    async def collect_experiment_data(self, experiment_id: str, 
                                    user_data: Dict[str, Any]) -> bool:
        """收集實驗數據"""
        if experiment_id not in self.active_experiments:
            return False
        
        experiment = self.active_experiments[experiment_id]
        user_id = user_data.get("user_id", "anonymous")
        variant_id = user_data.get("variant_id")
        action = user_data.get("action")  # 'view', 'click', 'signup', 'purchase'
        
        # 記錄用戶行為
        if user_id not in self.user_behavior_data:
            self.user_behavior_data[user_id] = []
        
        self.user_behavior_data[user_id].append({
            "experiment_id": experiment_id,
            "variant_id": variant_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "metadata": user_data.get("metadata", {})
        })
        
        # 更新變體統計
        if variant_id == experiment.control_group.variant_id:
            target_variant = experiment.control_group
        else:
            target_variant = next(
                (v for v in experiment.variants if v.variant_id == variant_id), 
                None
            )
        
        if target_variant:
            target_variant.sample_size += 1
            if action == "conversion":
                target_variant.conversion_rate = (
                    target_variant.conversion_rate * (target_variant.sample_size - 1) + 1
                ) / target_variant.sample_size
        
        return True
    
    async def analyze_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """分析實驗結果"""
        if experiment_id not in self.active_experiments:
            return {}
        
        experiment = self.active_experiments[experiment_id]
        
        # 計算統計顯著性
        results = {
            "experiment_id": experiment_id,
            "status": experiment.status.value,
            "runtime_days": (datetime.now() - experiment.start_date).days,
            "control_group": {
                "variant_id": experiment.control_group.variant_id,
                "sample_size": experiment.control_group.sample_size,
                "conversion_rate": experiment.control_group.conversion_rate,
                "confidence_interval": self._calculate_confidence_interval(
                    experiment.control_group.conversion_rate,
                    experiment.control_group.sample_size
                )
            },
            "test_variants": []
        }
        
        best_variant = experiment.control_group
        best_performance = experiment.control_group.conversion_rate
        
        for variant in experiment.variants:
            # 計算相對於控制組的提升
            lift = 0.0
            if experiment.control_group.conversion_rate > 0:
                lift = (variant.conversion_rate - experiment.control_group.conversion_rate) / experiment.control_group.conversion_rate
            
            # 計算統計顯著性
            significance = self._calculate_statistical_significance(
                experiment.control_group, variant
            )
            
            variant_result = {
                "variant_id": variant.variant_id,
                "name": variant.name,
                "sample_size": variant.sample_size,
                "conversion_rate": variant.conversion_rate,
                "lift_percentage": lift * 100,
                "statistical_significance": significance,
                "confidence_interval": self._calculate_confidence_interval(
                    variant.conversion_rate, variant.sample_size
                ),
                "changes": variant.changes
            }
            
            results["test_variants"].append(variant_result)
            
            # 追蹤最佳變體
            if variant.conversion_rate > best_performance:
                best_variant = variant
                best_performance = variant.conversion_rate
        
        # 生成建議
        results["recommendation"] = await self._generate_recommendation(
            experiment, best_variant, results
        )
        
        return results
    
    def _calculate_confidence_interval(self, conversion_rate: float, 
                                     sample_size: int, confidence: float = 0.95) -> Dict[str, float]:
        """計算置信區間"""
        if sample_size == 0:
            return {"lower": 0.0, "upper": 0.0}
        
        import math
        z_score = 1.96  # 95% 置信度
        margin_of_error = z_score * math.sqrt((conversion_rate * (1 - conversion_rate)) / sample_size)
        
        return {
            "lower": max(0.0, conversion_rate - margin_of_error),
            "upper": min(1.0, conversion_rate + margin_of_error)
        }
    
    def _calculate_statistical_significance(self, control: ABTestVariant, 
                                          test: ABTestVariant) -> bool:
        """計算統計顯著性"""
        # 簡化的統計顯著性計算
        if control.sample_size < 100 or test.sample_size < 100:
            return False
        
        # 使用Z檢驗的簡化版本
        p1, n1 = control.conversion_rate, control.sample_size
        p2, n2 = test.conversion_rate, test.sample_size
        
        if p1 == 0 and p2 == 0:
            return False
        
        p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
        se = (p_pool * (1 - p_pool) * (1/n1 + 1/n2)) ** 0.5
        
        if se == 0:
            return False
        
        z = abs(p1 - p2) / se
        return z > 1.96  # 95% 置信度
    
    async def _generate_recommendation(self, experiment: WebsiteOptimizationExperiment,
                                     best_variant: ABTestVariant,
                                     results: Dict[str, Any]) -> Dict[str, Any]:
        """生成優化建議"""
        if best_variant == experiment.control_group:
            return {
                "action": "keep_current",
                "reasoning": "沒有變體顯著優於當前版本，建議保持現狀並嘗試其他優化方向",
                "next_steps": ["分析用戶反饋", "嘗試其他優化策略", "增加樣本量重新測試"]
            }
        
        # 找到最佳測試變體的結果
        best_test_result = next(
            (r for r in results["test_variants"] if r["variant_id"] == best_variant.variant_id),
            None
        )
        
        if best_test_result and best_test_result["statistical_significance"]:
            return {
                "action": "implement_winner",
                "winning_variant": best_test_result["name"],
                "expected_improvement": f"{best_test_result['lift_percentage']:.1f}%",
                "reasoning": f"變體 '{best_test_result['name']}' 顯著優於控制組，提升 {best_test_result['lift_percentage']:.1f}%",
                "next_steps": [
                    "全量發布獲勝變體",
                    "監控實施後的性能指標",
                    "規劃下一輪優化實驗"
                ],
                "implementation_details": best_variant.changes
            }
        else:
            return {
                "action": "continue_testing",
                "reasoning": "雖然有變體表現更好，但統計顯著性不足，需要更多數據",
                "next_steps": ["延長測試時間", "增加流量分配", "優化變體設計"]
            }
    
    async def generate_optimization_roadmap(self) -> Dict[str, Any]:
        """生成優化路線圖"""
        self.logger.info("生成網站優化路線圖")
        
        # 分析優化機會
        opportunities = await self.analyze_optimization_opportunities()
        
        # 獲取 Business MCP 指導
        market_analysis = await business_manager.generate_market_analysis()
        acquisition_strategy = await business_manager.generate_customer_acquisition_strategy()
        financial_projection = await business_manager.generate_financial_projection(1)
        
        # 創建優化路線圖
        roadmap = {
            "executive_summary": {
                "total_opportunities": len(opportunities),
                "high_impact_opportunities": len([o for o in opportunities if o["opportunity_score"] > 0.8]),
                "estimated_annual_impact": sum(
                    self._calculate_annual_value(o["expected_impact"]) for o in opportunities
                ),
                "recommended_timeline": "3個月漸進式實施"
            },
            "quarter_plan": {
                "Q1": {
                    "focus": "轉換率基礎優化",
                    "experiments": opportunities[:2],
                    "expected_impact": "15-25% 轉換率提升",
                    "resource_requirement": "1 前端工程師 + 1 數據分析師"
                },
                "Q2": {
                    "focus": "用戶體驗深度優化",
                    "experiments": opportunities[2:4] if len(opportunities) > 2 else [],
                    "expected_impact": "20-30% 用戶留存提升",
                    "resource_requirement": "1 UX設計師 + 1 前端工程師"
                },
                "Q3": {
                    "focus": "變現流程優化",
                    "experiments": opportunities[4:] if len(opportunities) > 4 else [],
                    "expected_impact": "10-20% ARPU 提升",
                    "resource_requirement": "1 產品經理 + 1 數據科學家"
                }
            },
            "success_metrics": {
                "primary_kpis": [
                    "整體轉換率",
                    "用戶生命週期價值",
                    "獲客成本",
                    "月度經常性收入"
                ],
                "secondary_kpis": [
                    "頁面停留時間",
                    "跳出率",
                    "功能採用率",
                    "客戶滿意度"
                ]
            },
            "risk_mitigation": {
                "technical_risks": [
                    "A/B測試框架穩定性",
                    "性能影響監控",
                    "數據收集合規性"
                ],
                "business_risks": [
                    "用戶體驗負面影響",
                    "品牌一致性維護",
                    "競爭對手快速跟進"
                ]
            },
            "business_alignment": {
                "market_strategy": market_analysis.get("growth_strategy", {}),
                "acquisition_channels": acquisition_strategy.get("channels", []),
                "financial_targets": financial_projection.get("projections", [])
            }
        }
        
        return roadmap
    
    def _calculate_annual_value(self, expected_impact: Dict[str, Any]) -> float:
        """計算年度價值影響"""
        total_value = 0.0
        
        for metric, impact in expected_impact.items():
            if isinstance(impact, dict) and "improvement_percentage" in impact:
                improvement = impact["improvement_percentage"] / 100
                
                # 根據指標類型估算商業價值
                if "conversion" in metric:
                    # 假設每1%轉換率提升價值¥10,000/月
                    total_value += improvement * 10000 * 12
                elif "retention" in metric:
                    # 假設每1%留存提升價值¥5,000/月
                    total_value += improvement * 5000 * 12
                elif "engagement" in metric:
                    # 假設每1%參與度提升價值¥3,000/月
                    total_value += improvement * 3000 * 12
        
        return total_value

# 全局優化引擎實例
website_optimization_engine = WebsiteOptimizationEngine()

# 演示功能
async def demo_website_optimization():
    """網站優化引擎演示"""
    print("🚀 Business MCP 驅動的網站增量優化系統演示")
    print("=" * 70)
    
    # 1. 分析優化機會
    print("\n1. 分析優化機會")
    opportunities = await website_optimization_engine.analyze_optimization_opportunities()
    
    print(f"識別出 {len(opportunities)} 個優化機會:")
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"\n{i}. {opp['strategy_name']}")
        print(f"   機會分數: {opp['opportunity_score']:.2f}")
        print(f"   實施複雜度: {opp['implementation_complexity']}")
        print(f"   商業邏輯: {opp['business_rationale'][:100]}...")
        
        if opp['expected_impact']:
            print("   預期影響:")
            for metric, impact in list(opp['expected_impact'].items())[:2]:
                if isinstance(impact, dict):
                    print(f"     - {metric}: +{impact.get('improvement_percentage', 0):.1f}%")
    
    # 2. 創建 A/B 測試實驗
    print("\n2. 創建 A/B 測試實驗")
    if opportunities:
        best_opportunity = opportunities[0]
        experiment = await website_optimization_engine.create_ab_test_experiment(
            best_opportunity['strategy_name'],
            [var['name'] for var in best_opportunity['recommended_variants']]
        )
        
        print(f"實驗ID: {experiment.experiment_id}")
        print(f"實驗名稱: {experiment.name}")
        print(f"假設: {experiment.hypothesis}")
        print(f"測試變體數量: {len(experiment.variants)}")
        
        # 3. 啟動實驗
        print("\n3. 啟動實驗")
        success = await website_optimization_engine.start_experiment(experiment.experiment_id)
        print(f"實驗啟動: {'成功' if success else '失敗'}")
        
        # 4. 模擬數據收集
        print("\n4. 模擬數據收集")
        for i in range(1000):  # 模擬1000個用戶
            variant = random.choice([experiment.control_group] + experiment.variants)
            conversion = random.random() < (0.05 + random.random() * 0.03)  # 5-8% 轉換率
            
            await website_optimization_engine.collect_experiment_data(
                experiment.experiment_id,
                {
                    "user_id": f"user_{i}",
                    "variant_id": variant.variant_id,
                    "action": "conversion" if conversion else "view"
                }
            )
        
        # 5. 分析實驗結果
        print("\n5. 分析實驗結果")
        results = await website_optimization_engine.analyze_experiment_results(experiment.experiment_id)
        
        print(f"運行天數: {results.get('runtime_days', 0)}")
        print(f"控制組轉換率: {results['control_group']['conversion_rate']:.3f}")
        
        for variant in results['test_variants']:
            print(f"\n變體: {variant['name']}")
            print(f"  轉換率: {variant['conversion_rate']:.3f}")
            print(f"  提升: {variant['lift_percentage']:.1f}%")
            print(f"  統計顯著性: {'是' if variant['statistical_significance'] else '否'}")
        
        print(f"\n推薦行動: {results['recommendation']['action']}")
        print(f"推薦理由: {results['recommendation']['reasoning']}")
    
    # 6. 生成優化路線圖
    print("\n6. 生成優化路線圖")
    roadmap = await website_optimization_engine.generate_optimization_roadmap()
    
    print(f"總優化機會: {roadmap['executive_summary']['total_opportunities']}")
    print(f"高影響機會: {roadmap['executive_summary']['high_impact_opportunities']}")
    print(f"預估年度影響: ¥{roadmap['executive_summary']['estimated_annual_impact']:,.0f}")
    
    print("\nQ1 計劃:")
    q1 = roadmap['quarter_plan']['Q1']
    print(f"  焦點: {q1['focus']}")
    print(f"  預期影響: {q1['expected_impact']}")
    print(f"  資源需求: {q1['resource_requirement']}")
    
    print("\n主要成功指標:")
    for kpi in roadmap['success_metrics']['primary_kpis']:
        print(f"  - {kpi}")
    
    return {
        "opportunities_identified": len(opportunities),
        "experiments_created": 1 if opportunities else 0,
        "roadmap_generated": True,
        "system_ready": True
    }

if __name__ == "__main__":
    result = asyncio.run(demo_website_optimization())
    print(f"\n🎉 網站優化引擎演示完成！")