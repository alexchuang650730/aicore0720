#!/usr/bin/env python3
"""
Smart Intervention 持續學習引擎
監控用戶需求模式，自動優化系統響應，最終實現一步直達
"""

import json
import re
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

@dataclass
class UserRequest:
    """用戶需求記錄"""
    timestamp: str
    request_text: str
    category: str
    required_steps: List[str]
    actual_steps: List[str]
    automation_potential: float  # 0.0-1.0
    one_step_achievable: bool

@dataclass
class OptimizationTarget:
    """優化目標"""
    target_id: str
    category: str
    description: str
    current_steps: int
    target_steps: int
    priority: str
    automation_strategy: str
    status: str  # pending/in_progress/completed

class ContinuousLearningEngine:
    """持續學習引擎"""
    
    def __init__(self):
        self.learning_data_file = Path("data/smart_intervention_learning.json")
        self.optimization_targets_file = Path("data/optimization_targets.json")
        
        # 確保數據目錄存在
        self.learning_data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 用戶需求歷史
        self.user_requests: List[UserRequest] = []
        self.optimization_targets: List[OptimizationTarget] = []
        
        # 監控模式
        self.monitoring_patterns = self._init_monitoring_patterns()
        
        # 載入歷史數據
        self._load_learning_data()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _init_monitoring_patterns(self) -> Dict[str, Dict[str, Any]]:
        """初始化監控模式"""
        return {
            "system_improvement": {
                "keywords": [
                    "documentation mcp", "readme", "版本說明", "文檔整理",
                    "部署問題", "網站不可用", "修復", "啟動失敗",
                    "演示需求", "demo", "展示", "驗證",
                    "檔案整理", "位置不對", "移動到適當位置",
                    "mcp協調", "組件集成", "系統優化"
                ],
                "expected_automation": 0.8,
                "current_steps_avg": 3.5,
                "target_steps": 1,
                "responsible_mcp": ["documentation_mcp", "monitoring_mcp", "smart_intervention"]
            },
            "visualization_operations": {
                "keywords": [
                    "下載文件", "download", "獲取", "保存",
                    "編輯文件", "修改", "edit", "更新",
                    "系統性能", "監控狀態", "metrics", "分析",
                    "可視化", "圖表", "界面", "顯示", "查看"
                ],
                "expected_automation": 0.9,
                "current_steps_avg": 4.2,
                "target_steps": 1,
                "responsible_mcp": ["smartui_mcp", "ag_ui_mcp", "stagewise_mcp"]
            },
            "claude_code_gaps": {
                "keywords": [
                    "響應慢", "需要多次確認", "不夠精準", 
                    "還需要手動", "步驟太多", "重複操作",
                    "延遲超過", "等待時間長", "效率低"
                ],
                "expected_automation": 0.95,
                "current_steps_avg": 5.1,
                "target_steps": 1,
                "responsible_mcp": ["claude_mcp", "smart_intervention", "codeflow_mcp"]
            }
        }
    
    def analyze_user_request(self, request_text: str) -> Dict[str, Any]:
        """分析用戶需求"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "request_text": request_text,
            "detected_patterns": [],
            "automation_potential": 0.0,
            "optimization_suggestions": [],
            "one_step_possible": False
        }
        
        request_lower = request_text.lower()
        
        # 檢測模式匹配
        for pattern_name, pattern_data in self.monitoring_patterns.items():
            for keyword in pattern_data["keywords"]:
                if keyword.lower() in request_lower:
                    analysis["detected_patterns"].append({
                        "pattern": pattern_name,
                        "keyword": keyword,
                        "current_automation": pattern_data["expected_automation"],
                        "responsible_mcp": pattern_data["responsible_mcp"]
                    })
                    break
        
        # 計算自動化潛力
        if analysis["detected_patterns"]:
            total_automation = sum(p["current_automation"] for p in analysis["detected_patterns"])
            analysis["automation_potential"] = min(total_automation / len(analysis["detected_patterns"]), 1.0)
            analysis["one_step_possible"] = analysis["automation_potential"] > 0.8
        
        # 生成優化建議
        analysis["optimization_suggestions"] = self._generate_optimization_suggestions(analysis)
        
        # 記錄到學習數據
        self._record_user_request(analysis)
        
        return analysis
    
    def _generate_optimization_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成優化建議"""
        suggestions = []
        
        for pattern in analysis["detected_patterns"]:
            pattern_name = pattern["pattern"]
            pattern_data = self.monitoring_patterns[pattern_name]
            
            suggestion = {
                "target": f"自動化{pattern_name}流程",
                "current_steps": pattern_data["current_steps_avg"],
                "target_steps": pattern_data["target_steps"],
                "automation_strategy": self._determine_automation_strategy(pattern_name),
                "responsible_mcp": pattern_data["responsible_mcp"],
                "priority": "high" if pattern_data["expected_automation"] > 0.8 else "medium",
                "implementation_approach": self._get_implementation_approach(pattern_name)
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def _determine_automation_strategy(self, pattern_name: str) -> str:
        """確定自動化策略"""
        strategies = {
            "system_improvement": "關鍵詞檢測 → 自動驅動對應MCP → 直接執行 → 結果驗證",
            "visualization_operations": "意圖識別 → 啟動可視化工具 → 自動處理 → 結果展示",
            "claude_code_gaps": "性能監控 → 問題識別 → 自動優化 → 持續學習"
        }
        return strategies.get(pattern_name, "通用自動化流程")
    
    def _get_implementation_approach(self, pattern_name: str) -> List[str]:
        """獲取實現方法"""
        approaches = {
            "system_improvement": [
                "擴展 Smart Intervention 關鍵詞庫",
                "增強 Documentation MCP 自動觸發",
                "優化 MCP 間通信協議",
                "建立自動驗證機制"
            ],
            "visualization_operations": [
                "集成 SmartUI MCP 可視化能力",
                "開發一鍵文件操作功能",
                "建立實時性能監控界面",
                "實現自動化工作流觸發"
            ],
            "claude_code_gaps": [
                "實時監控 Claude 響應性能",
                "建立用戶意圖學習模型",
                "優化多輪對話處理",
                "實現預測性任務執行"
            ]
        }
        return approaches.get(pattern_name, ["建立通用自動化機制"])
    
    def _record_user_request(self, analysis: Dict[str, Any]):
        """記錄用戶需求"""
        request = UserRequest(
            timestamp=analysis["timestamp"],
            request_text=analysis["request_text"],
            category=",".join([p["pattern"] for p in analysis["detected_patterns"]]),
            required_steps=["檢測需求", "分析意圖", "執行操作", "驗證結果"],
            actual_steps=["檢測需求", "分析意圖", "等待確認", "執行操作", "驗證結果"],
            automation_potential=analysis["automation_potential"],
            one_step_achievable=analysis["one_step_possible"]
        )
        
        self.user_requests.append(request)
        self._save_learning_data()
    
    def generate_optimization_targets(self) -> List[OptimizationTarget]:
        """生成優化目標"""
        targets = []
        
        # 分析用戶需求模式
        pattern_frequency = {}
        for request in self.user_requests:
            for category in request.category.split(","):
                if category:
                    pattern_frequency[category] = pattern_frequency.get(category, 0) + 1
        
        # 為高頻模式生成優化目標
        for pattern, frequency in pattern_frequency.items():
            if frequency >= 2:  # 出現2次以上的模式
                target = OptimizationTarget(
                    target_id=f"optimize_{pattern}_{int(time.time())}",
                    category=pattern,
                    description=f"自動化 {pattern} 相關操作，實現一步直達",
                    current_steps=int(self.monitoring_patterns.get(pattern, {}).get("current_steps_avg", 4)),
                    target_steps=1,
                    priority="high" if frequency >= 5 else "medium",
                    automation_strategy=self._determine_automation_strategy(pattern),
                    status="pending"
                )
                targets.append(target)
        
        self.optimization_targets.extend(targets)
        self._save_optimization_targets()
        
        return targets
    
    def get_one_step_solution_roadmap(self) -> Dict[str, Any]:
        """獲取一步直達解決方案路線圖"""
        roadmap = {
            "current_automation_level": self._calculate_current_automation(),
            "target_automation_level": 0.95,
            "phases": [
                {
                    "phase": "Phase 1: 關鍵詞智能檢測",
                    "targets": ["擴展關鍵詞庫", "提高檢測準確率", "減少誤觸發"],
                    "timeline": "1-2週",
                    "success_metrics": "檢測準確率 > 95%"
                },
                {
                    "phase": "Phase 2: 意圖理解優化", 
                    "targets": ["上下文分析", "用戶習慣學習", "預測性執行"],
                    "timeline": "2-3週",
                    "success_metrics": "意圖理解準確率 > 90%"
                },
                {
                    "phase": "Phase 3: 一步直達實現",
                    "targets": ["自動執行機制", "結果驗證", "錯誤自動修正"],
                    "timeline": "3-4週", 
                    "success_metrics": "90%操作實現一步完成"
                }
            ],
            "optimization_targets": [asdict(target) for target in self.optimization_targets],
            "next_actions": self._get_next_actions()
        }
        
        return roadmap
    
    def _calculate_current_automation(self) -> float:
        """計算當前自動化水平"""
        if not self.user_requests:
            return 0.0
        
        total_potential = sum(req.automation_potential for req in self.user_requests)
        return total_potential / len(self.user_requests)
    
    def _get_next_actions(self) -> List[str]:
        """獲取下一步行動"""
        return [
            "部署關鍵詞檢測增強模塊",
            "建立用戶操作模式學習系統", 
            "優化 MCP 組件間自動協調",
            "實現預測性任務執行機制",
            "建立自動化執行驗證系統"
        ]
    
    def _load_learning_data(self):
        """載入學習數據"""
        try:
            if self.learning_data_file.exists():
                with open(self.learning_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_requests = [UserRequest(**req) for req in data.get('user_requests', [])]
        except Exception as e:
            self.logger.warning(f"載入學習數據失敗: {e}")
    
    def _save_learning_data(self):
        """保存學習數據"""
        try:
            data = {
                'user_requests': [asdict(req) for req in self.user_requests],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.learning_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存學習數據失敗: {e}")
    
    def _save_optimization_targets(self):
        """保存優化目標"""
        try:
            data = {
                'optimization_targets': [asdict(target) for target in self.optimization_targets],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.optimization_targets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存優化目標失敗: {e}")

# 全局學習引擎實例
learning_engine = ContinuousLearningEngine()

# 演示功能
def demo_continuous_learning():
    """持續學習引擎演示"""
    print("🧠 Smart Intervention 持續學習引擎演示")
    print("=" * 60)
    
    # 模擬用戶需求
    test_requests = [
        "documentation mcp 沒遵守約定，需要建立v4.76架構說明",
        "PowerAuto.ai網站不可用，需要修復全功能問題", 
        "我想下載性能監控的可視化圖表",
        "需要編輯ClaudeEditor的配置文件",
        "系統響應太慢，能否優化一下",
        "演示部署清單能否自動生成？"
    ]
    
    print("\n1. 分析用戶需求模式")
    for i, request in enumerate(test_requests, 1):
        print(f"\n需求 {i}: {request}")
        analysis = learning_engine.analyze_user_request(request)
        
        print(f"檢測模式: {[p['pattern'] for p in analysis['detected_patterns']]}")
        print(f"自動化潛力: {analysis['automation_potential']:.1%}")
        print(f"一步直達可能: {'是' if analysis['one_step_possible'] else '否'}")
    
    print("\n2. 生成優化目標")
    targets = learning_engine.generate_optimization_targets()
    for target in targets:
        print(f"- {target.description} (優先級: {target.priority})")
    
    print("\n3. 一步直達路線圖")
    roadmap = learning_engine.get_one_step_solution_roadmap()
    print(f"當前自動化水平: {roadmap['current_automation_level']:.1%}")
    print(f"目標自動化水平: {roadmap['target_automation_level']:.1%}")
    
    for phase in roadmap['phases']:
        print(f"\n{phase['phase']} ({phase['timeline']})")
        print(f"成功指標: {phase['success_metrics']}")
    
    print(f"\n下一步行動:")
    for action in roadmap['next_actions']:
        print(f"- {action}")
    
    return {
        "analyzed_requests": len(test_requests),
        "optimization_targets": len(targets),
        "automation_level": roadmap['current_automation_level'],
        "demo_success": True
    }

if __name__ == "__main__":
    result = demo_continuous_learning()
    print(f"\n🎉 持續學習引擎演示完成！")
    print(f"分析需求: {result['analyzed_requests']}個")
    print(f"優化目標: {result['optimization_targets']}個") 
    print(f"自動化水平: {result['automation_level']:.1%}")