#!/usr/bin/env python3
"""
DeepSWE強化學習獎勵系統定義
針對軟體工程任務的多層次獎勵設計
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np


class ActionType(Enum):
    """動作類型"""
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    EDIT_FILE = "edit_file"
    SEARCH_CODE = "search_code"
    RUN_TEST = "run_test"
    DEBUG = "debug"
    REFACTOR = "refactor"
    GENERATE_CODE = "generate_code"
    ANALYZE_ERROR = "analyze_error"
    FIX_BUG = "fix_bug"


@dataclass
class SWEState:
    """軟體工程環境狀態"""
    task_description: str
    current_files: List[str]
    error_messages: List[str]
    test_results: Dict[str, bool]
    code_coverage: float
    build_status: bool
    execution_trace: List[str]
    time_spent: float
    actions_taken: List[ActionType]


@dataclass
class SWEAction:
    """軟體工程動作"""
    action_type: ActionType
    target_file: Optional[str]
    content: Optional[str]
    parameters: Dict


class DeepSWERewardSystem:
    """DeepSWE獎勵系統"""
    
    def __init__(self):
        # 獎勵權重配置
        self.reward_weights = {
            "task_completion": 0.3,      # 任務完成度
            "code_quality": 0.2,         # 代碼質量
            "efficiency": 0.15,          # 效率
            "test_coverage": 0.15,       # 測試覆蓋率
            "error_handling": 0.1,       # 錯誤處理
            "best_practices": 0.1        # 最佳實踐
        }
        
        # 獎勵參數
        self.reward_params = {
            "max_episode_reward": 100.0,
            "min_episode_reward": -50.0,
            "step_penalty": -0.1,        # 每步懲罰（鼓勵效率）
            "error_penalty": -5.0,       # 錯誤懲罰
            "test_pass_reward": 10.0,    # 測試通過獎勵
            "bug_fix_reward": 15.0,      # 修復bug獎勵
            "refactor_reward": 5.0       # 重構獎勵
        }
    
    def calculate_reward(self, 
                        prev_state: SWEState, 
                        action: SWEAction, 
                        new_state: SWEState) -> Tuple[float, Dict[str, float]]:
        """
        計算獎勵函數
        
        Returns:
            總獎勵和各項分解
        """
        reward_components = {}
        
        # 1. 任務完成度獎勵
        reward_components["task_completion"] = self._calculate_task_completion_reward(
            prev_state, new_state
        )
        
        # 2. 代碼質量獎勵
        reward_components["code_quality"] = self._calculate_code_quality_reward(
            action, new_state
        )
        
        # 3. 效率獎勵
        reward_components["efficiency"] = self._calculate_efficiency_reward(
            action, new_state
        )
        
        # 4. 測試覆蓋率獎勵
        reward_components["test_coverage"] = self._calculate_test_coverage_reward(
            prev_state, new_state
        )
        
        # 5. 錯誤處理獎勵
        reward_components["error_handling"] = self._calculate_error_handling_reward(
            prev_state, action, new_state
        )
        
        # 6. 最佳實踐獎勵
        reward_components["best_practices"] = self._calculate_best_practices_reward(
            action, new_state
        )
        
        # 計算總獎勵
        total_reward = sum(
            self.reward_weights[key] * value 
            for key, value in reward_components.items()
        )
        
        # 添加步驟懲罰
        total_reward += self.reward_params["step_penalty"]
        
        return total_reward, reward_components
    
    def _calculate_task_completion_reward(self, 
                                        prev_state: SWEState, 
                                        new_state: SWEState) -> float:
        """計算任務完成度獎勵"""
        reward = 0.0
        
        # 測試通過情況
        prev_passing = sum(prev_state.test_results.values())
        new_passing = sum(new_state.test_results.values())
        test_improvement = new_passing - prev_passing
        
        if test_improvement > 0:
            reward += test_improvement * self.reward_params["test_pass_reward"]
        
        # 構建成功
        if not prev_state.build_status and new_state.build_status:
            reward += 20.0
        elif prev_state.build_status and not new_state.build_status:
            reward -= 20.0  # 破壞構建的懲罰
        
        # 錯誤減少
        error_reduction = len(prev_state.error_messages) - len(new_state.error_messages)
        reward += error_reduction * 5.0
        
        return reward
    
    def _calculate_code_quality_reward(self, 
                                     action: SWEAction, 
                                     new_state: SWEState) -> float:
        """計算代碼質量獎勵"""
        reward = 0.0
        
        # 重構動作獎勵
        if action.action_type == ActionType.REFACTOR:
            # 檢查是否真的改善了代碼
            if new_state.build_status and len(new_state.error_messages) == 0:
                reward += self.reward_params["refactor_reward"]
        
        # 代碼覆蓋率提升
        if new_state.code_coverage > 0.8:
            reward += 10.0
        elif new_state.code_coverage > 0.6:
            reward += 5.0
        
        return reward
    
    def _calculate_efficiency_reward(self, 
                                   action: SWEAction, 
                                   new_state: SWEState) -> float:
        """計算效率獎勵"""
        reward = 0.0
        
        # 避免重複動作
        recent_actions = new_state.actions_taken[-5:]
        if len(recent_actions) >= 2 and all(a == action.action_type for a in recent_actions):
            reward -= 5.0  # 重複相同動作的懲罰
        
        # 時間效率
        if new_state.time_spent < 60:  # 1分鐘內完成
            reward += 10.0
        elif new_state.time_spent < 300:  # 5分鐘內
            reward += 5.0
        elif new_state.time_spent > 600:  # 超過10分鐘
            reward -= 5.0
        
        return reward
    
    def _calculate_test_coverage_reward(self, 
                                      prev_state: SWEState, 
                                      new_state: SWEState) -> float:
        """計算測試覆蓋率獎勵"""
        coverage_improvement = new_state.code_coverage - prev_state.code_coverage
        
        reward = 0.0
        if coverage_improvement > 0:
            reward += coverage_improvement * 50.0  # 覆蓋率提升獎勵
        
        # 額外的里程碑獎勵
        if prev_state.code_coverage < 0.8 and new_state.code_coverage >= 0.8:
            reward += 20.0
        
        return reward
    
    def _calculate_error_handling_reward(self, 
                                       prev_state: SWEState, 
                                       action: SWEAction,
                                       new_state: SWEState) -> float:
        """計算錯誤處理獎勵"""
        reward = 0.0
        
        # 修復bug
        if action.action_type == ActionType.FIX_BUG:
            if len(new_state.error_messages) < len(prev_state.error_messages):
                reward += self.reward_params["bug_fix_reward"]
            else:
                reward -= 5.0  # 未能修復的懲罰
        
        # 錯誤分析
        if action.action_type == ActionType.ANALYZE_ERROR:
            # 如果下一步成功修復，給予獎勵
            if len(new_state.actions_taken) > 0 and \
               new_state.actions_taken[-1] == ActionType.FIX_BUG:
                reward += 5.0
        
        # 新增錯誤的懲罰
        new_errors = len(new_state.error_messages) - len(prev_state.error_messages)
        if new_errors > 0:
            reward += new_errors * self.reward_params["error_penalty"]
        
        return reward
    
    def _calculate_best_practices_reward(self, 
                                       action: SWEAction, 
                                       new_state: SWEState) -> float:
        """計算最佳實踐獎勵"""
        reward = 0.0
        
        # 寫測試
        if action.action_type == ActionType.RUN_TEST:
            reward += 3.0
        
        # 適當的調試
        if action.action_type == ActionType.DEBUG and len(new_state.error_messages) > 0:
            reward += 2.0
        
        # 讀取文件後再編輯（理解上下文）
        if len(new_state.actions_taken) >= 2:
            if new_state.actions_taken[-2] == ActionType.READ_FILE and \
               action.action_type in [ActionType.EDIT_FILE, ActionType.WRITE_FILE]:
                reward += 5.0
        
        return reward
    
    def get_shaped_reward(self, 
                         prev_state: SWEState, 
                         action: SWEAction, 
                         new_state: SWEState,
                         is_terminal: bool) -> float:
        """
        獲取shaped reward（用於訓練）
        包含中間獎勵和終端獎勵
        """
        total_reward, components = self.calculate_reward(prev_state, action, new_state)
        
        # 終端狀態的額外獎勵
        if is_terminal:
            if all(new_state.test_results.values()) and new_state.build_status:
                # 完美完成任務
                total_reward += 50.0
            elif new_state.build_status:
                # 部分完成
                total_reward += 20.0
            else:
                # 失敗
                total_reward -= 20.0
        
        # 裁剪到合理範圍
        total_reward = np.clip(
            total_reward, 
            self.reward_params["min_episode_reward"],
            self.reward_params["max_episode_reward"]
        )
        
        return total_reward
    
    def get_reward_explanation(self) -> str:
        """獲取獎勵系統說明"""
        return """
DeepSWE強化學習獎勵系統

總獎勵 = Σ(權重i × 獎勵分量i) + 步驟懲罰 + 終端獎勵

獎勵分量：
1. 任務完成度 (30%)
   - 測試通過: +10/個
   - 構建成功: +20
   - 錯誤減少: +5/個

2. 代碼質量 (20%)
   - 成功重構: +5
   - 高覆蓋率(>80%): +10

3. 效率 (15%)
   - 快速完成(<1分鐘): +10
   - 避免重複動作: -5

4. 測試覆蓋率 (15%)
   - 覆蓋率提升: +50×提升百分比
   - 達到80%: +20（里程碑）

5. 錯誤處理 (10%)
   - 修復bug: +15
   - 引入錯誤: -5/個

6. 最佳實踐 (10%)
   - 運行測試: +3
   - 先讀後寫: +5

特殊獎勵：
- 步驟懲罰: -0.1/步（鼓勵效率）
- 完美完成: +50（終端）
- 任務失敗: -20（終端）

設計原則：
1. 鼓勵正確性優先於速度
2. 獎勵漸進式改進
3. 懲罰破壞性行為
4. 引導最佳實踐
"""


def demonstrate_reward_calculation():
    """演示獎勵計算"""
    reward_system = DeepSWERewardSystem()
    
    # 創建示例狀態
    prev_state = SWEState(
        task_description="Fix the login bug",
        current_files=["login.py", "test_login.py"],
        error_messages=["TypeError in login.py line 45"],
        test_results={"test_login": False, "test_auth": True},
        code_coverage=0.65,
        build_status=False,
        execution_trace=[],
        time_spent=30.0,
        actions_taken=[ActionType.READ_FILE]
    )
    
    # 執行修復動作
    action = SWEAction(
        action_type=ActionType.FIX_BUG,
        target_file="login.py",
        content="Fixed type error",
        parameters={}
    )
    
    # 新狀態（修復成功）
    new_state = SWEState(
        task_description="Fix the login bug",
        current_files=["login.py", "test_login.py"],
        error_messages=[],  # 錯誤已修復
        test_results={"test_login": True, "test_auth": True},  # 測試通過
        code_coverage=0.75,  # 覆蓋率提升
        build_status=True,   # 構建成功
        execution_trace=["Fixed TypeError"],
        time_spent=45.0,
        actions_taken=[ActionType.READ_FILE, ActionType.FIX_BUG]
    )
    
    # 計算獎勵
    total_reward, components = reward_system.calculate_reward(
        prev_state, action, new_state
    )
    
    print("DeepSWE獎勵計算示例")
    print("=" * 50)
    print(f"動作: {action.action_type.value}")
    print(f"\n獎勵分解:")
    for key, value in components.items():
        weight = reward_system.reward_weights[key]
        contribution = weight * value
        print(f"  {key}: {value:.2f} × {weight} = {contribution:.2f}")
    print(f"\n步驟懲罰: -0.1")
    print(f"總獎勵: {total_reward:.2f}")
    
    # 顯示獎勵說明
    print("\n" + "=" * 50)
    print(reward_system.get_reward_explanation())


if __name__ == "__main__":
    demonstrate_reward_calculation()