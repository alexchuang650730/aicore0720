#!/usr/bin/env python3
"""
PowerAutomation v4.75 - 技術指標和體驗指標系統
建立 P0-P2 MCP 技術指標和 ClaudeEditor 體驗指標
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPPriority(Enum):
    """MCP 優先級"""
    P0 = "P0"  # 核心中的核心
    P1 = "P1"  # 核心
    P2 = "P2"  # 重要

@dataclass
class TechnicalMetric:
    """技術指標"""
    name: str
    description: str
    unit: str
    target_value: float
    current_value: float = 0.0
    threshold_warning: float = 0.8  # 警告閾值
    threshold_critical: float = 0.6  # 危險閾值

@dataclass
class ExperienceMetric:
    """體驗指標"""
    name: str
    description: str
    area: str  # UI 區域
    measurement: str  # 測量方式
    target_score: float
    current_score: float = 0.0

class MetricsSystem:
    """指標系統"""
    
    def __init__(self):
        self.mcp_metrics = self._define_mcp_metrics()
        self.experience_metrics = self._define_experience_metrics()
        self.metrics_data = {
            "technical": {},
            "experience": {},
            "timestamp": datetime.now().isoformat()
        }
        
    def _define_mcp_metrics(self) -> Dict[str, Dict[str, List[TechnicalMetric]]]:
        """定義 MCP 技術指標"""
        return {
            # P0 級 MCP
            "P0": {
                "smart_intervention": [
                    TechnicalMetric(
                        name="detection_accuracy",
                        description="任務類型檢測準確率",
                        unit="%",
                        target_value=95.0
                    ),
                    TechnicalMetric(
                        name="switch_latency",
                        description="切換延遲",
                        unit="ms",
                        target_value=100.0
                    ),
                    TechnicalMetric(
                        name="keyword_coverage",
                        description="關鍵詞覆蓋率",
                        unit="%",
                        target_value=90.0
                    )
                ],
                "codeflow_mcp": [
                    TechnicalMetric(
                        name="generation_speed",
                        description="代碼生成速度",
                        unit="tokens/s",
                        target_value=1000.0
                    ),
                    TechnicalMetric(
                        name="syntax_accuracy",
                        description="語法正確率",
                        unit="%",
                        target_value=98.0
                    ),
                    TechnicalMetric(
                        name="test_coverage",
                        description="測試覆蓋率生成",
                        unit="%",
                        target_value=85.0
                    )
                ],
                "smartui_mcp": [
                    TechnicalMetric(
                        name="component_generation_time",
                        description="組件生成時間",
                        unit="s",
                        target_value=2.0
                    ),
                    TechnicalMetric(
                        name="responsive_accuracy",
                        description="響應式設計準確度",
                        unit="%",
                        target_value=95.0
                    ),
                    TechnicalMetric(
                        name="theme_consistency",
                        description="主題一致性",
                        unit="%",
                        target_value=100.0
                    )
                ],
                "memoryrag_mcp": [
                    TechnicalMetric(
                        name="retrieval_accuracy",
                        description="檢索準確率",
                        unit="%",
                        target_value=92.0
                    ),
                    TechnicalMetric(
                        name="memory_efficiency",
                        description="記憶體使用效率",
                        unit="%",
                        target_value=85.0
                    ),
                    TechnicalMetric(
                        name="k2_optimization_rate",
                        description="K2 優化率",
                        unit="%",
                        target_value=30.0
                    )
                ]
            },
            
            # P1 級 MCP
            "P1": {
                "smarttool_mcp": [
                    TechnicalMetric(
                        name="tool_integration_count",
                        description="集成工具數量",
                        unit="個",
                        target_value=50.0
                    ),
                    TechnicalMetric(
                        name="api_response_time",
                        description="API 響應時間",
                        unit="ms",
                        target_value=200.0
                    ),
                    TechnicalMetric(
                        name="success_rate",
                        description="調用成功率",
                        unit="%",
                        target_value=99.0
                    )
                ],
                "test_mcp": [
                    TechnicalMetric(
                        name="test_generation_accuracy",
                        description="測試生成準確率",
                        unit="%",
                        target_value=90.0
                    ),
                    TechnicalMetric(
                        name="execution_speed",
                        description="執行速度",
                        unit="tests/s",
                        target_value=100.0
                    ),
                    TechnicalMetric(
                        name="coverage_analysis",
                        description="覆蓋率分析準確度",
                        unit="%",
                        target_value=95.0
                    )
                ],
                "claude_router_mcp": [
                    TechnicalMetric(
                        name="routing_accuracy",
                        description="路由準確率",
                        unit="%",
                        target_value=98.0
                    ),
                    TechnicalMetric(
                        name="k2_switch_time",
                        description="K2 切換時間",
                        unit="ms",
                        target_value=50.0
                    ),
                    TechnicalMetric(
                        name="conversation_sync_rate",
                        description="對話同步率",
                        unit="%",
                        target_value=100.0
                    )
                ]
            },
            
            # P2 級 MCP
            "P2": {
                "command_mcp": [
                    TechnicalMetric(
                        name="command_recognition",
                        description="命令識別率",
                        unit="%",
                        target_value=99.0
                    ),
                    TechnicalMetric(
                        name="execution_time",
                        description="執行時間",
                        unit="ms",
                        target_value=100.0
                    )
                ],
                "local_adapter_mcp": [
                    TechnicalMetric(
                        name="file_operation_speed",
                        description="文件操作速度",
                        unit="ops/s",
                        target_value=1000.0
                    ),
                    TechnicalMetric(
                        name="sync_accuracy",
                        description="同步準確率",
                        unit="%",
                        target_value=100.0
                    )
                ],
                "mcp_coordinator_mcp": [
                    TechnicalMetric(
                        name="coordination_latency",
                        description="協調延遲",
                        unit="ms",
                        target_value=20.0
                    ),
                    TechnicalMetric(
                        name="conflict_resolution",
                        description="衝突解決率",
                        unit="%",
                        target_value=95.0
                    )
                ],
                "docs_mcp": [
                    TechnicalMetric(
                        name="scan_speed",
                        description="掃描速度",
                        unit="files/s",
                        target_value=100.0
                    ),
                    TechnicalMetric(
                        name="categorization_accuracy",
                        description="分類準確率",
                        unit="%",
                        target_value=90.0
                    )
                ]
            }
        }
    
    def _define_experience_metrics(self) -> Dict[str, List[ExperienceMetric]]:
        """定義 ClaudeEditor 體驗指標"""
        return {
            "ai_model_control": [
                ExperienceMetric(
                    name="model_switch_time",
                    description="模型切換時間",
                    area="AI模型控制區",
                    measurement="從點擊到完成切換的時間",
                    target_score=1.0  # 秒
                ),
                ExperienceMetric(
                    name="model_status_visibility",
                    description="模型狀態可見性",
                    area="AI模型控制區",
                    measurement="狀態信息的清晰度評分",
                    target_score=9.0  # 1-10分
                ),
                ExperienceMetric(
                    name="k2_indicator_clarity",
                    description="K2 模式指示清晰度",
                    area="AI模型控制區",
                    measurement="用戶識別當前模式的準確率",
                    target_score=95.0  # %
                )
            ],
            
            "workflow_area": [
                ExperienceMetric(
                    name="workflow_discovery",
                    description="工作流發現便利性",
                    area="六大工作流區",
                    measurement="找到所需工作流的平均時間",
                    target_score=3.0  # 秒
                ),
                ExperienceMetric(
                    name="workflow_execution",
                    description="工作流執行流暢度",
                    area="六大工作流區",
                    measurement="執行過程中的中斷次數",
                    target_score=0.0  # 次
                ),
                ExperienceMetric(
                    name="workflow_monitoring",
                    description="監控運維體驗",
                    area="六大工作流區-監控運維",
                    measurement="關鍵指標的實時更新延遲",
                    target_score=1.0  # 秒
                )
            ],
            
            "code_editor": [
                ExperienceMetric(
                    name="auto_completion_speed",
                    description="自動完成速度",
                    area="代碼編輯器",
                    measurement="從輸入到建議出現的時間",
                    target_score=50.0  # ms
                ),
                ExperienceMetric(
                    name="syntax_highlight_accuracy",
                    description="語法高亮準確性",
                    area="代碼編輯器",
                    measurement="正確高亮的代碼比例",
                    target_score=99.0  # %
                ),
                ExperienceMetric(
                    name="error_detection_rate",
                    description="錯誤檢測率",
                    area="代碼編輯器",
                    measurement="實時檢測到的錯誤比例",
                    target_score=95.0  # %
                )
            ],
            
            "ui_designer": [
                ExperienceMetric(
                    name="drag_drop_responsiveness",
                    description="拖放響應性",
                    area="UI設計器",
                    measurement="拖放操作的延遲",
                    target_score=16.0  # ms (60fps)
                ),
                ExperienceMetric(
                    name="preview_accuracy",
                    description="預覽準確性",
                    area="UI設計器",
                    measurement="預覽與實際效果的一致性",
                    target_score=98.0  # %
                ),
                ExperienceMetric(
                    name="component_library_access",
                    description="組件庫訪問速度",
                    area="UI設計器",
                    measurement="打開組件庫的時間",
                    target_score=0.5  # 秒
                )
            ],
            
            "command_center": [
                ExperienceMetric(
                    name="command_discovery",
                    description="命令發現效率",
                    area="命令中心",
                    measurement="找到目標命令的平均擊鍵數",
                    target_score=3.0  # 次
                ),
                ExperienceMetric(
                    name="command_execution_feedback",
                    description="命令執行反饋",
                    area="命令中心",
                    measurement="執行後反饋出現的時間",
                    target_score=100.0  # ms
                ),
                ExperienceMetric(
                    name="shortcut_effectiveness",
                    description="快捷鍵有效性",
                    area="命令中心",
                    measurement="快捷鍵使用成功率",
                    target_score=100.0  # %
                )
            ],
            
            "collaboration": [
                ExperienceMetric(
                    name="real_time_sync",
                    description="實時同步延遲",
                    area="協作區",
                    measurement="操作同步到其他用戶的時間",
                    target_score=200.0  # ms
                ),
                ExperienceMetric(
                    name="conflict_resolution_ui",
                    description="衝突解決界面友好度",
                    area="協作區",
                    measurement="用戶解決衝突的平均時間",
                    target_score=30.0  # 秒
                ),
                ExperienceMetric(
                    name="presence_awareness",
                    description="協作者存在感知",
                    area="協作區",
                    measurement="顯示其他用戶狀態的準確性",
                    target_score=100.0  # %
                )
            ],
            
            "performance_monitor": [
                ExperienceMetric(
                    name="metrics_refresh_rate",
                    description="指標刷新率",
                    area="性能監控",
                    measurement="關鍵指標的更新頻率",
                    target_score=1.0  # Hz
                ),
                ExperienceMetric(
                    name="alert_response_time",
                    description="告警響應時間",
                    area="性能監控",
                    measurement="從問題發生到告警顯示的時間",
                    target_score=1000.0  # ms
                ),
                ExperienceMetric(
                    name="visualization_clarity",
                    description="可視化清晰度",
                    area="性能監控",
                    measurement="圖表信息的可理解性評分",
                    target_score=8.5  # 1-10分
                )
            ],
            
            "smart_intervention": [
                ExperienceMetric(
                    name="intervention_accuracy",
                    description="干預準確性",
                    area="智能干預",
                    measurement="正確識別需要切換場景的比例",
                    target_score=90.0  # %
                ),
                ExperienceMetric(
                    name="suggestion_relevance",
                    description="建議相關性",
                    area="智能干預",
                    measurement="用戶接受建議的比例",
                    target_score=80.0  # %
                ),
                ExperienceMetric(
                    name="non_intrusive_score",
                    description="非侵入性評分",
                    area="智能干預",
                    measurement="用戶對干預時機的滿意度",
                    target_score=8.0  # 1-10分
                )
            ]
        }
    
    async def collect_technical_metrics(self) -> Dict[str, Any]:
        """收集技術指標"""
        logger.info("📊 收集技術指標...")
        
        results = {}
        
        for priority in ["P0", "P1", "P2"]:
            results[priority] = {}
            
            for mcp_name, metrics in self.mcp_metrics[priority].items():
                mcp_results = []
                
                for metric in metrics:
                    # 模擬收集指標數據
                    current_value = await self._measure_technical_metric(mcp_name, metric)
                    metric.current_value = current_value
                    
                    # 計算健康度
                    health_score = current_value / metric.target_value
                    if metric.unit == "ms" or metric.unit == "s":  # 時間類指標，越小越好
                        health_score = metric.target_value / current_value if current_value > 0 else 1.0
                    
                    status = "healthy"
                    if health_score < metric.threshold_critical:
                        status = "critical"
                    elif health_score < metric.threshold_warning:
                        status = "warning"
                    
                    mcp_results.append({
                        "metric": asdict(metric),
                        "health_score": round(health_score, 2),
                        "status": status
                    })
                
                results[priority][mcp_name] = {
                    "metrics": mcp_results,
                    "overall_health": self._calculate_overall_health(mcp_results)
                }
        
        return results
    
    async def collect_experience_metrics(self) -> Dict[str, Any]:
        """收集體驗指標"""
        logger.info("🎯 收集體驗指標...")
        
        results = {}
        
        for area, metrics in self.experience_metrics.items():
            area_results = []
            
            for metric in metrics:
                # 模擬收集體驗數據
                current_score = await self._measure_experience_metric(area, metric)
                metric.current_score = current_score
                
                # 計算體驗分數
                if metric.measurement.endswith("時間") or "延遲" in metric.name:
                    # 時間類指標，越小越好
                    experience_score = (metric.target_score / current_score * 100) if current_score > 0 else 100
                else:
                    # 其他指標，越大越好
                    experience_score = (current_score / metric.target_score * 100)
                
                experience_score = min(100, experience_score)  # 限制在100%以內
                
                area_results.append({
                    "metric": asdict(metric),
                    "experience_score": round(experience_score, 1),
                    "grade": self._get_experience_grade(experience_score)
                })
            
            results[area] = {
                "metrics": area_results,
                "area_score": round(sum(m["experience_score"] for m in area_results) / len(area_results), 1)
            }
        
        return results
    
    async def _measure_technical_metric(self, mcp_name: str, metric: TechnicalMetric) -> float:
        """測量技術指標（模擬）"""
        # 實際實現中應該調用相應的 MCP 獲取真實數據
        import random
        
        # 模擬不同的測量值
        if metric.unit == "%":
            return random.uniform(metric.target_value * 0.8, min(100, metric.target_value * 1.1))
        elif metric.unit == "ms" or metric.unit == "s":
            return random.uniform(metric.target_value * 0.7, metric.target_value * 1.3)
        else:
            return random.uniform(metric.target_value * 0.9, metric.target_value * 1.1)
    
    async def _measure_experience_metric(self, area: str, metric: ExperienceMetric) -> float:
        """測量體驗指標（模擬）"""
        # 實際實現中應該通過用戶行為分析獲取
        import random
        
        # 模擬測量值，略有波動
        return random.uniform(metric.target_score * 0.85, metric.target_score * 1.05)
    
    def _calculate_overall_health(self, mcp_results: List[Dict]) -> Dict[str, Any]:
        """計算整體健康度"""
        health_scores = [r["health_score"] for r in mcp_results]
        
        return {
            "average_health": round(sum(health_scores) / len(health_scores), 2),
            "min_health": round(min(health_scores), 2),
            "critical_count": sum(1 for r in mcp_results if r["status"] == "critical"),
            "warning_count": sum(1 for r in mcp_results if r["status"] == "warning"),
            "healthy_count": sum(1 for r in mcp_results if r["status"] == "healthy")
        }
    
    def _get_experience_grade(self, score: float) -> str:
        """獲取體驗等級"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        else:
            return "D"
    
    async def generate_dashboard_data(self) -> Dict[str, Any]:
        """生成儀表板數據"""
        technical_metrics = await self.collect_technical_metrics()
        experience_metrics = await self.collect_experience_metrics()
        
        # 計算總體分數
        tech_scores = []
        for priority, mcps in technical_metrics.items():
            for mcp_name, data in mcps.items():
                tech_scores.append(data["overall_health"]["average_health"])
        
        exp_scores = [data["area_score"] for data in experience_metrics.values()]
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "overall_scores": {
                "technical_health": round(sum(tech_scores) / len(tech_scores) * 100, 1),
                "experience_score": round(sum(exp_scores) / len(exp_scores), 1)
            },
            "technical_metrics": technical_metrics,
            "experience_metrics": experience_metrics,
            "recommendations": self._generate_recommendations(technical_metrics, experience_metrics),
            "alerts": self._generate_alerts(technical_metrics, experience_metrics)
        }
        
        return dashboard
    
    def _generate_recommendations(self, tech_metrics: Dict, exp_metrics: Dict) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        # 技術建議
        for priority, mcps in tech_metrics.items():
            for mcp_name, data in mcps.items():
                if data["overall_health"]["critical_count"] > 0:
                    recommendations.append(f"🚨 {mcp_name} 有 {data['overall_health']['critical_count']} 個關鍵指標需要立即優化")
                elif data["overall_health"]["warning_count"] > 1:
                    recommendations.append(f"⚠️ {mcp_name} 有多個指標接近警告閾值，建議檢查")
        
        # 體驗建議
        for area, data in exp_metrics.items():
            if data["area_score"] < 80:
                area_name = {
                    "ai_model_control": "AI模型控制",
                    "workflow_area": "工作流區域",
                    "code_editor": "代碼編輯器",
                    "ui_designer": "UI設計器",
                    "command_center": "命令中心",
                    "collaboration": "協作功能",
                    "performance_monitor": "性能監控",
                    "smart_intervention": "智能干預"
                }.get(area, area)
                
                recommendations.append(f"💡 {area_name} 體驗評分較低 ({data['area_score']}%)，建議優化用戶交互")
        
        return recommendations[:5]  # 返回前5個最重要的建議
    
    def _generate_alerts(self, tech_metrics: Dict, exp_metrics: Dict) -> List[Dict[str, Any]]:
        """生成告警"""
        alerts = []
        
        # 技術告警
        for priority, mcps in tech_metrics.items():
            for mcp_name, data in mcps.items():
                for metric_data in data["metrics"]:
                    if metric_data["status"] == "critical":
                        alerts.append({
                            "type": "technical",
                            "severity": "critical",
                            "mcp": mcp_name,
                            "metric": metric_data["metric"]["name"],
                            "message": f"{mcp_name} 的 {metric_data['metric']['description']} 嚴重低於目標值",
                            "current": metric_data["metric"]["current_value"],
                            "target": metric_data["metric"]["target_value"]
                        })
        
        # 體驗告警
        for area, data in exp_metrics.items():
            if data["area_score"] < 70:
                alerts.append({
                    "type": "experience",
                    "severity": "warning",
                    "area": area,
                    "message": f"{area} 區域體驗評分過低",
                    "score": data["area_score"]
                })
        
        return alerts
    
    def export_metrics_report(self, dashboard_data: Dict[str, Any]) -> str:
        """導出指標報告"""
        report = f"""# PowerAutomation v4.75 指標報告

生成時間：{dashboard_data['timestamp']}

## 總體評分
- 技術健康度：{dashboard_data['overall_scores']['technical_health']}%
- 用戶體驗分：{dashboard_data['overall_scores']['experience_score']}%

## 技術指標詳情

"""
        
        # 技術指標
        for priority in ["P0", "P1", "P2"]:
            if priority in dashboard_data["technical_metrics"]:
                report += f"### {priority} 級 MCP\n\n"
                
                for mcp_name, data in dashboard_data["technical_metrics"][priority].items():
                    health = data["overall_health"]
                    report += f"#### {mcp_name}\n"
                    report += f"- 平均健康度：{health['average_health'] * 100:.1f}%\n"
                    report += f"- 健康/警告/危險：{health['healthy_count']}/{health['warning_count']}/{health['critical_count']}\n\n"
                    
                    # 詳細指標
                    for metric_data in data["metrics"]:
                        metric = metric_data["metric"]
                        status_icon = {
                            "healthy": "✅",
                            "warning": "⚠️",
                            "critical": "🚨"
                        }[metric_data["status"]]
                        
                        report += f"  - {metric['name']} {status_icon}: {metric['current_value']:.2f} / {metric['target_value']} {metric['unit']}\n"
                    
                    report += "\n"
        
        # 體驗指標
        report += "## 用戶體驗指標\n\n"
        
        for area, data in dashboard_data["experience_metrics"].items():
            area_name = area.replace("_", " ").title()
            report += f"### {area_name} (評分: {data['area_score']}%)\n\n"
            
            for metric_data in data["metrics"]:
                metric = metric_data["metric"]
                grade = metric_data["grade"]
                score = metric_data["experience_score"]
                
                report += f"- **{metric['name']}** [{grade}]: {score:.1f}%\n"
                report += f"  - {metric['description']}\n"
                report += f"  - 當前: {metric['current_score']:.2f} / 目標: {metric['target_score']}\n\n"
        
        # 建議和告警
        if dashboard_data["recommendations"]:
            report += "## 改進建議\n\n"
            for rec in dashboard_data["recommendations"]:
                report += f"- {rec}\n"
        
        if dashboard_data["alerts"]:
            report += "\n## 告警\n\n"
            for alert in dashboard_data["alerts"]:
                icon = "🚨" if alert["severity"] == "critical" else "⚠️"
                report += f"- {icon} {alert['message']}\n"
        
        return report


# 創建實時監控儀表板
def create_metrics_dashboard_ui() -> str:
    """創建指標儀表板 UI"""
    return """
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function MetricsDashboard({ metricsData }) {
    const [selectedPriority, setSelectedPriority] = useState('P0');
    const [selectedArea, setSelectedArea] = useState('ai_model_control');
    
    // 顏色配置
    const statusColors = {
        healthy: '#10b981',
        warning: '#f59e0b',
        critical: '#ef4444'
    };
    
    const gradeColors = {
        'A+': '#065f46',
        'A': '#10b981',
        'B+': '#34d399',
        'B': '#fbbf24',
        'C': '#f97316',
        'D': '#ef4444'
    };
    
    // 技術指標卡片
    const TechnicalMetricCard = ({ mcp, data }) => {
        const health = data.overall_health;
        const healthPercent = health.average_health * 100;
        
        return (
            <Card className="mb-4">
                <CardHeader>
                    <CardTitle className="flex justify-between items-center">
                        <span>{mcp}</span>
                        <Badge variant={healthPercent > 80 ? 'success' : healthPercent > 60 ? 'warning' : 'destructive'}>
                            {healthPercent.toFixed(1)}%
                        </Badge>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {data.metrics.map((metric, idx) => (
                            <div key={idx}>
                                <div className="flex justify-between text-sm mb-1">
                                    <span>{metric.metric.description}</span>
                                    <span className={`font-medium text-${statusColors[metric.status]}`}>
                                        {metric.metric.current_value.toFixed(2)} {metric.metric.unit}
                                    </span>
                                </div>
                                <Progress 
                                    value={metric.health_score * 100} 
                                    className={`h-2 bg-${statusColors[metric.status]}/20`}
                                />
                            </div>
                        ))}
                    </div>
                    
                    <div className="mt-4 flex justify-around text-center">
                        <div>
                            <div className="text-2xl font-bold text-green-600">{health.healthy_count}</div>
                            <div className="text-xs text-muted-foreground">健康</div>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-yellow-600">{health.warning_count}</div>
                            <div className="text-xs text-muted-foreground">警告</div>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-red-600">{health.critical_count}</div>
                            <div className="text-xs text-muted-foreground">危險</div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    };
    
    // 體驗指標卡片
    const ExperienceMetricCard = ({ area, data }) => {
        const areaScore = data.area_score;
        const scoreColor = areaScore >= 90 ? 'text-green-600' : areaScore >= 80 ? 'text-yellow-600' : 'text-red-600';
        
        return (
            <Card className="mb-4">
                <CardHeader>
                    <CardTitle className="flex justify-between items-center">
                        <span>{area.replace(/_/g, ' ').toUpperCase()}</span>
                        <span className={`text-2xl font-bold ${scoreColor}`}>
                            {areaScore.toFixed(1)}%
                        </span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {data.metrics.map((metric, idx) => (
                            <div key={idx} className="border-l-4 pl-3" 
                                 style={{borderColor: gradeColors[metric.grade]}}>
                                <div className="flex justify-between items-start">
                                    <div>
                                        <div className="font-medium">{metric.metric.name}</div>
                                        <div className="text-sm text-muted-foreground">
                                            {metric.metric.description}
                                        </div>
                                    </div>
                                    <Badge className="ml-2" style={{backgroundColor: gradeColors[metric.grade]}}>
                                        {metric.grade}
                                    </Badge>
                                </div>
                                <div className="mt-2 text-sm">
                                    <span className="text-muted-foreground">測量方式：</span>
                                    {metric.metric.measurement}
                                </div>
                                <Progress 
                                    value={metric.experience_score} 
                                    className="mt-2 h-2"
                                />
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        );
    };
    
    // 總覽圖表
    const OverviewCharts = ({ technicalHealth, experienceScore }) => {
        const overviewData = [
            { name: '技術健康度', value: technicalHealth, fill: '#10b981' },
            { name: '用戶體驗分', value: experienceScore, fill: '#3b82f6' }
        ];
        
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <Card>
                    <CardHeader>
                        <CardTitle>總體評分</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={overviewData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis domain={[0, 100]} />
                                <Tooltip />
                                <Bar dataKey="value" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
                
                <Card>
                    <CardHeader>
                        <CardTitle>核心指標</CardTitle>
                    </CardHeader>
                    <CardContent className="flex items-center justify-center">
                        <div className="text-center">
                            <div className="text-5xl font-bold text-primary">
                                {((technicalHealth + experienceScore) / 2).toFixed(1)}%
                            </div>
                            <div className="text-muted-foreground mt-2">
                                PowerAutomation Core 健康度
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    };
    
    return (
        <div className="p-6 space-y-6">
            <h1 className="text-3xl font-bold mb-6">PowerAutomation v4.75 指標儀表板</h1>
            
            {/* 總覽 */}
            <OverviewCharts 
                technicalHealth={metricsData.overall_scores.technical_health}
                experienceScore={metricsData.overall_scores.experience_score}
            />
            
            {/* 告警 */}
            {metricsData.alerts.length > 0 && (
                <Card className="border-red-200 bg-red-50">
                    <CardHeader>
                        <CardTitle className="text-red-700">告警</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {metricsData.alerts.map((alert, idx) => (
                                <div key={idx} className="flex items-center gap-2">
                                    <span className="text-2xl">
                                        {alert.severity === 'critical' ? '🚨' : '⚠️'}
                                    </span>
                                    <span className="text-sm">{alert.message}</span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}
            
            <Tabs defaultValue="technical">
                <TabsList>
                    <TabsTrigger value="technical">技術指標</TabsTrigger>
                    <TabsTrigger value="experience">體驗指標</TabsTrigger>
                    <TabsTrigger value="recommendations">建議</TabsTrigger>
                </TabsList>
                
                <TabsContent value="technical" className="mt-4">
                    <Tabs value={selectedPriority} onValueChange={setSelectedPriority}>
                        <TabsList>
                            <TabsTrigger value="P0">P0 核心</TabsTrigger>
                            <TabsTrigger value="P1">P1 重要</TabsTrigger>
                            <TabsTrigger value="P2">P2 輔助</TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value={selectedPriority} className="mt-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {Object.entries(metricsData.technical_metrics[selectedPriority] || {}).map(([mcp, data]) => (
                                    <TechnicalMetricCard key={mcp} mcp={mcp} data={data} />
                                ))}
                            </div>
                        </TabsContent>
                    </Tabs>
                </TabsContent>
                
                <TabsContent value="experience" className="mt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(metricsData.experience_metrics).map(([area, data]) => (
                            <ExperienceMetricCard key={area} area={area} data={data} />
                        ))}
                    </div>
                </TabsContent>
                
                <TabsContent value="recommendations" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>改進建議</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {metricsData.recommendations.map((rec, idx) => (
                                    <div key={idx} className="flex items-start gap-2">
                                        <span className="text-xl mt-0.5">{rec.charAt(0)}</span>
                                        <span>{rec.substring(2)}</span>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
"""


# 主函數
async def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════════╗
║   PowerAutomation v4.75 指標系統             ║
║   技術指標 + 體驗指標 = Core 驅動 Editor     ║
╚══════════════════════════════════════════════╝
""")
    
    system = MetricsSystem()
    
    # 生成儀表板數據
    print("\n📊 收集指標數據...")
    dashboard_data = await system.generate_dashboard_data()
    
    # 顯示總體評分
    print(f"\n總體評分：")
    print(f"- 技術健康度：{dashboard_data['overall_scores']['technical_health']}%")
    print(f"- 用戶體驗分：{dashboard_data['overall_scores']['experience_score']}%")
    
    # 顯示告警
    if dashboard_data["alerts"]:
        print(f"\n⚠️ 發現 {len(dashboard_data['alerts'])} 個告警")
    
    # 保存數據
    data_path = Path("deploy/v4.75/metrics_dashboard_data.json")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 儀表板數據已保存：{data_path}")
    
    # 生成報告
    report = system.export_metrics_report(dashboard_data)
    report_path = Path("deploy/v4.75/METRICS_REPORT.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 指標報告已生成：{report_path}")
    
    # 生成 UI
    ui_path = Path("deploy/v4.75/MetricsDashboard.jsx")
    with open(ui_path, 'w', encoding='utf-8') as f:
        f.write(create_metrics_dashboard_ui())
    print(f"✅ UI 組件已生成：{ui_path}")
    
    print("\n💡 PowerAutomation Core 通過這些指標驅動 ClaudeEditor 體驗")


if __name__ == "__main__":
    asyncio.run(main())