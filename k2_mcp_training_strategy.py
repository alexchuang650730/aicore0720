#!/usr/bin/env python3
"""
K2+MCP 訓練策略
通過整合MCP工具和訓練數據達到100%工具調用準確率
"""

import json
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrainingPhase:
    """訓練階段"""
    name: str
    focus: str
    mcp_tools: List[str]
    training_samples: int
    expected_accuracy: float
    duration_days: int


class K2MCPTrainingStrategy:
    """K2+MCP訓練策略"""
    
    def __init__(self):
        self.current_accuracy = 0.74
        self.target_accuracy = 1.0
        
        # 定義訓練階段
        self.training_phases = [
            TrainingPhase(
                name="基礎工具選擇",
                focus="正確選擇基本工具",
                mcp_tools=["smarttool"],
                training_samples=5000,
                expected_accuracy=0.85,
                duration_days=3
            ),
            TrainingPhase(
                name="意圖理解強化",
                focus="深度理解用戶意圖",
                mcp_tools=["smarttool", "intent-analyzer"],
                training_samples=8000,
                expected_accuracy=0.92,
                duration_days=4
            ),
            TrainingPhase(
                name="工具組合優化",
                focus="多工具協同和順序",
                mcp_tools=["smarttool", "intent-analyzer", "tool-validator"],
                training_samples=10000,
                expected_accuracy=0.96,
                duration_days=5
            ),
            TrainingPhase(
                name="記憶學習整合",
                focus="從歷史模式學習",
                mcp_tools=["smarttool", "intent-analyzer", "tool-validator", "memory-context"],
                training_samples=12000,
                expected_accuracy=0.98,
                duration_days=7
            ),
            TrainingPhase(
                name="精細調優",
                focus="處理邊緣案例",
                mcp_tools=["all"],
                training_samples=15000,
                expected_accuracy=1.0,
                duration_days=7
            )
        ]
    
    def create_training_data_for_phase(self, phase: TrainingPhase) -> List[Dict]:
        """為特定階段創建訓練數據"""
        
        training_data = []
        
        if phase.name == "基礎工具選擇":
            # 基礎工具選擇訓練數據
            patterns = [
                {
                    "prompt": "讀取{file}文件",
                    "tools": ["Read"],
                    "negative_tools": ["Write", "Edit"]
                },
                {
                    "prompt": "搜索所有包含{keyword}的文件",
                    "tools": ["Grep"],
                    "negative_tools": ["Read", "Write"]
                },
                {
                    "prompt": "修改{file}中的{old}為{new}",
                    "tools": ["Read", "Edit"],
                    "sequence": ["Read", "Edit"],
                    "negative_tools": ["Write", "Bash"]
                },
                {
                    "prompt": "創建新的{type}項目",
                    "tools": ["Bash", "Write"],
                    "sequence": ["Bash", "Write"],
                    "max_calls": {"Bash": 3, "Write": 5}
                },
                {
                    "prompt": "運行{command}命令",
                    "tools": ["Bash"],
                    "max_calls": {"Bash": 1},
                    "negative_tools": ["Read", "Write", "Edit"]
                }
            ]
            
            # 生成訓練樣本
            for pattern in patterns:
                for i in range(phase.training_samples // len(patterns)):
                    # 創建變體
                    sample = self._create_training_sample(pattern, phase)
                    training_data.append(sample)
        
        elif phase.name == "意圖理解強化":
            # 複雜意圖訓練數據
            complex_patterns = [
                {
                    "prompt": "先{action1}，然後{action2}，最後{action3}",
                    "intent": "multi_step",
                    "tools": ["varies"],
                    "requires_decomposition": True
                },
                {
                    "prompt": "如果{condition}，就{action1}，否則{action2}",
                    "intent": "conditional",
                    "tools": ["varies"],
                    "requires_validation": True
                },
                {
                    "prompt": "找出所有{target}並{action}",
                    "intent": "batch_operation",
                    "tools": ["Grep", "Read", "Edit"],
                    "requires_iteration": True
                }
            ]
            
            for pattern in complex_patterns:
                for i in range(phase.training_samples // len(complex_patterns)):
                    sample = self._create_complex_training_sample(pattern, phase)
                    training_data.append(sample)
        
        return training_data
    
    def _create_training_sample(self, pattern: Dict, phase: TrainingPhase) -> Dict:
        """創建單個訓練樣本"""
        import random
        
        # 變量替換
        replacements = {
            "{file}": random.choice(["main.py", "config.js", "README.md", "test.tsx"]),
            "{keyword}": random.choice(["TODO", "FIXME", "error", "function", "class"]),
            "{old}": random.choice(["print", "console.log", "var", "def"]),
            "{new}": random.choice(["logger.info", "debug", "let", "async def"]),
            "{type}": random.choice(["Flask", "React", "Django", "Vue"]),
            "{command}": random.choice(["pytest", "npm install", "pip install", "yarn test"])
        }
        
        prompt = pattern["prompt"]
        for key, value in replacements.items():
            prompt = prompt.replace(key, value)
        
        # 創建正確的工具調用示例
        correct_response = self._generate_correct_response(pattern, replacements)
        
        # 創建錯誤的工具調用示例（用於對比學習）
        incorrect_response = self._generate_incorrect_response(pattern, replacements)
        
        return {
            "prompt": prompt,
            "correct_response": correct_response,
            "incorrect_response": incorrect_response,
            "tools": pattern["tools"],
            "phase": phase.name,
            "mcp_guidance": self._generate_mcp_guidance(pattern)
        }
    
    def _generate_correct_response(self, pattern: Dict, replacements: Dict) -> str:
        """生成正確的回應"""
        response = "我將幫助您完成這個任務。\n\n"
        
        if "sequence" in pattern:
            for tool in pattern["sequence"]:
                response += f"""<function_calls>
<invoke name="{tool}">
<parameter name="{"file_path" if tool in ["Read", "Edit", "Write"] else "command"}">示例參數</parameter>
</invoke>
</function_calls>\n\n"""
        else:
            for tool in pattern["tools"]:
                response += f"""<function_calls>
<invoke name="{tool}">
<parameter name="{"pattern" if tool == "Grep" else "file_path"}">示例參數</parameter>
</invoke>
</function_calls>\n\n"""
        
        return response
    
    def _generate_incorrect_response(self, pattern: Dict, replacements: Dict) -> str:
        """生成錯誤的回應（用於對比學習）"""
        response = "我將幫助您完成這個任務。\n\n"
        
        # 添加錯誤：重複調用
        for tool in pattern.get("negative_tools", []):
            response += f"""<function_calls>
<invoke name="{tool}">
<parameter name="path">錯誤參數</parameter>
</invoke>
</function_calls>\n\n"""
        
        # 添加錯誤：過多調用
        if pattern["tools"]:
            for _ in range(3):
                response += f"""<function_calls>
<invoke name="{pattern['tools'][0]}">
<parameter name="path">重複參數</parameter>
</invoke>
</function_calls>\n\n"""
        
        return response
    
    def _generate_mcp_guidance(self, pattern: Dict) -> Dict:
        """生成MCP指導"""
        return {
            "smarttool": {
                "recommended_tools": pattern["tools"],
                "avoid_tools": pattern.get("negative_tools", []),
                "max_calls": pattern.get("max_calls", {}),
                "sequence": pattern.get("sequence", [])
            },
            "intent_analyzer": {
                "intent_type": pattern.get("intent", "simple"),
                "requires_decomposition": pattern.get("requires_decomposition", False),
                "requires_validation": pattern.get("requires_validation", False)
            }
        }
    
    def _create_complex_training_sample(self, pattern: Dict, phase: TrainingPhase) -> Dict:
        """創建複雜訓練樣本"""
        # 實現複雜意圖的訓練數據生成
        return self._create_training_sample(pattern, phase)
    
    def generate_training_curriculum(self) -> Dict:
        """生成完整的訓練課程"""
        curriculum = {
            "total_duration_days": sum(phase.duration_days for phase in self.training_phases),
            "total_samples": sum(phase.training_samples for phase in self.training_phases),
            "phases": [],
            "milestones": []
        }
        
        current_day = 0
        for i, phase in enumerate(self.training_phases):
            phase_info = {
                "phase_number": i + 1,
                "name": phase.name,
                "focus": phase.focus,
                "start_day": current_day + 1,
                "end_day": current_day + phase.duration_days,
                "training_samples": phase.training_samples,
                "mcp_tools": phase.mcp_tools,
                "expected_accuracy": phase.expected_accuracy,
                "key_improvements": self._get_phase_improvements(phase)
            }
            
            curriculum["phases"].append(phase_info)
            
            # 添加里程碑
            curriculum["milestones"].append({
                "day": current_day + phase.duration_days,
                "milestone": f"{phase.name}完成",
                "accuracy": phase.expected_accuracy
            })
            
            current_day += phase.duration_days
        
        return curriculum
    
    def _get_phase_improvements(self, phase: TrainingPhase) -> List[str]:
        """獲取階段改進點"""
        improvements_map = {
            "基礎工具選擇": [
                "正確識別文件操作需要的工具",
                "避免使用不必要的工具",
                "單一任務不重複調用"
            ],
            "意圖理解強化": [
                "理解複雜的多步驟請求",
                "正確分解任務",
                "識別條件邏輯"
            ],
            "工具組合優化": [
                "多工具協同工作",
                "保持正確的執行順序",
                "優化工具調用數量"
            ],
            "記憶學習整合": [
                "從成功案例學習",
                "記住用戶偏好",
                "快速適應新模式"
            ],
            "精細調優": [
                "處理罕見情況",
                "100%準確率",
                "零錯誤容忍"
            ]
        }
        
        return improvements_map.get(phase.name, [])
    
    def create_evaluation_metrics(self) -> Dict:
        """創建評估指標"""
        return {
            "primary_metrics": {
                "tool_accuracy": {
                    "description": "工具選擇準確率",
                    "target": 1.0,
                    "weight": 0.4
                },
                "tool_efficiency": {
                    "description": "工具使用效率（無冗餘）",
                    "target": 0.95,
                    "weight": 0.3
                },
                "sequence_correctness": {
                    "description": "工具調用順序正確性",
                    "target": 1.0,
                    "weight": 0.2
                },
                "intent_understanding": {
                    "description": "意圖理解準確率",
                    "target": 0.98,
                    "weight": 0.1
                }
            },
            "secondary_metrics": {
                "response_time": "回應時間 < 2秒",
                "error_recovery": "錯誤恢復能力 > 95%",
                "user_satisfaction": "用戶滿意度 > 95%"
            }
        }
    
    def generate_final_report(self) -> str:
        """生成最終報告"""
        curriculum = self.generate_training_curriculum()
        metrics = self.create_evaluation_metrics()
        
        report = f"""# K2+MCP 訓練策略：達到100%工具調用準確率

## 執行摘要

- **當前準確率**: 74%
- **目標準確率**: 100%
- **總訓練時長**: {curriculum['total_duration_days']}天
- **總訓練樣本**: {curriculum['total_samples']:,}

## 訓練階段

"""
        
        for phase in curriculum["phases"]:
            report += f"""### 第{phase['phase_number']}階段：{phase['name']} (第{phase['start_day']}-{phase['end_day']}天)

**重點**: {phase['focus']}
**MCP工具**: {', '.join(phase['mcp_tools'])}
**訓練樣本**: {phase['training_samples']:,}
**預期準確率**: {phase['expected_accuracy']*100:.0f}%

**關鍵改進**:
"""
            for improvement in phase['key_improvements']:
                report += f"- {improvement}\n"
            report += "\n"
        
        report += """## 成功指標

### 主要指標
"""
        
        for metric_name, metric_info in metrics["primary_metrics"].items():
            report += f"- **{metric_info['description']}**: {metric_info['target']*100:.0f}% (權重: {metric_info['weight']*100:.0f}%)\n"
        
        report += "\n### 次要指標\n"
        for metric_name, metric_desc in metrics["secondary_metrics"].items():
            report += f"- {metric_desc}\n"
        
        report += f"""
## 實施建議

1. **立即開始第一階段**
   - 專注於基礎工具選擇
   - 使用SmartTool MCP
   - 預期3天內達到85%準確率

2. **持續監控和調整**
   - 每日評估準確率
   - 根據錯誤類型調整訓練數據
   - 及時整合新的MCP工具

3. **數據質量保證**
   - 人工審核關鍵訓練樣本
   - 確保正負樣本平衡
   - 涵蓋各種邊緣情況

## 預期成果時間線

"""
        
        for milestone in curriculum["milestones"]:
            report += f"- **第{milestone['day']}天**: {milestone['milestone']} - {milestone['accuracy']*100:.0f}%準確率\n"
        
        report += f"""
## 結論

通過系統化的訓練和MCP工具整合，我們有信心在{curriculum['total_duration_days']}天內將K2的工具調用準確率從74%提升至100%。關鍵在於：

1. 漸進式訓練策略
2. MCP工具的智能輔助
3. 高質量的訓練數據
4. 持續的監控和優化

這將使K2成為一個真正可靠的AI編程助手。
"""
        
        return report


def main():
    """主函數"""
    logger.info("🚀 生成K2+MCP訓練策略")
    
    strategy = K2MCPTrainingStrategy()
    
    # 生成訓練課程
    curriculum = strategy.generate_training_curriculum()
    with open("k2_mcp_training_curriculum.json", "w", encoding="utf-8") as f:
        json.dump(curriculum, f, ensure_ascii=False, indent=2)
    
    # 生成第一階段訓練數據樣本
    phase1_data = strategy.create_training_data_for_phase(strategy.training_phases[0])
    with open("phase1_training_samples.json", "w", encoding="utf-8") as f:
        json.dump(phase1_data[:10], f, ensure_ascii=False, indent=2)  # 保存前10個樣本
    
    # 生成最終報告
    report = strategy.generate_final_report()
    with open("k2_mcp_training_strategy.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("✅ 訓練策略生成完成！")
    logger.info("📊 預計26天內達到100%準確率")
    logger.info("\n生成的文件：")
    logger.info("- k2_mcp_training_strategy.md (完整策略)")
    logger.info("- k2_mcp_training_curriculum.json (訓練課程)")
    logger.info("- phase1_training_samples.json (第一階段樣本)")


if __name__ == "__main__":
    main()