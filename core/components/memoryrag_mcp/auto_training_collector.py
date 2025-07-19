#!/usr/bin/env python3
"""
自動訓練數據收集器
每次 Claude Code 使用都自動收集並加入訓練數據
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoTrainingCollector:
    """自動訓練數據收集器"""
    
    def __init__(self):
        # 獲取項目根目錄
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.data_dir = self.base_dir / "data/claude_conversations"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 今日數據文件
        today = datetime.now().strftime("%Y%m%d")
        self.daily_file = self.data_dir / f"training_data_{today}.jsonl"
        
        # 會話數據
        self.current_session = {
            'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'interactions': []
        }
        
    def collect_interaction(self, user_input: str, assistant_response: str, tools_used: List[str] = None, context: Dict = None):
        """收集一次交互數據"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input[:1000],  # 限制長度
            'assistant_response': assistant_response[:2000],  # 限制長度
            'tools_used': tools_used or [],
            'context': context or {},
            'session_id': self.current_session['session_id']
        }
        
        # 分析交互類型
        interaction_type = self._classify_interaction(user_input, assistant_response, tools_used)
        interaction['interaction_type'] = interaction_type
        
        # 提取任務和解決方案
        task = self._extract_task(user_input)
        solution = self._extract_solution(assistant_response, tools_used)
        
        # 生成訓練樣本
        training_sample = {
            'instruction': "分析並執行任務",
            'input': task,
            'output': solution,
            'category': interaction_type,
            'tools_used': tools_used or [],
            'confidence': self._calculate_confidence(interaction),
            'source': 'claude_code_auto',
            'metadata': {
                'session_id': self.current_session['session_id'],
                'timestamp': interaction['timestamp'],
                'user_input_length': len(user_input),
                'response_length': len(assistant_response)
            }
        }
        
        # 保存數據
        self._save_training_sample(training_sample)
        self.current_session['interactions'].append(interaction)
        
        logger.info(f"✅ 收集訓練數據: {interaction_type} - {len(tools_used or [])} 個工具")
        
        return training_sample
    
    def _classify_interaction(self, user_input: str, assistant_response: str, tools_used: List[str]) -> str:
        """分類交互類型"""
        user_lower = user_input.lower()
        response_lower = assistant_response.lower()
        
        # 動作類：使用了工具或執行了命令
        if tools_used or any(keyword in response_lower for keyword in [
            '執行', '運行', '創建', '修改', '刪除', '部署', '安裝', '配置'
        ]):
            return 'action'
        
        # 觀察類：檢查結果或狀態
        if any(keyword in user_lower for keyword in [
            '檢查', '查看', '狀態', '結果', '是否', '有沒有'
        ]):
            return 'observation'
        
        # 思考類：分析或規劃
        return 'thinking'
    
    def _extract_task(self, user_input: str) -> str:
        """提取任務描述"""
        # 移除多餘的空白和換行
        task = " ".join(user_input.split())
        
        # 如果太長，截取關鍵部分
        if len(task) > 200:
            # 尋找關鍵動詞
            key_verbs = ['實現', '創建', '修復', '優化', '部署', '分析', '檢查', '修改']
            for verb in key_verbs:
                if verb in task:
                    # 從動詞開始截取
                    verb_pos = task.find(verb)
                    task = task[max(0, verb_pos-20):verb_pos+180]
                    break
            else:
                task = task[:200]
        
        return task
    
    def _extract_solution(self, assistant_response: str, tools_used: List[str]) -> str:
        """提取解決方案"""
        solution_parts = []
        
        # 添加工具使用信息
        if tools_used:
            solution_parts.append(f"使用工具: {', '.join(tools_used)}")
        
        # 提取關鍵執行步驟
        response_lines = assistant_response.split('\n')
        key_lines = []
        
        for line in response_lines:
            line = line.strip()
            if not line:
                continue
                
            # 保留重要的行
            if any(keyword in line for keyword in [
                '執行', '創建', '修改', '檢查', '部署', '配置', '安裝',
                '```', 'bash', 'python', 'npm', 'git'
            ]):
                key_lines.append(line)
            
            # 限制長度
            if len('\n'.join(key_lines)) > 500:
                break
        
        if key_lines:
            solution_parts.extend(key_lines[:5])  # 最多5行
        else:
            # 如果沒有找到關鍵行，取前面部分
            solution_parts.append(assistant_response[:300])
        
        return '\n'.join(solution_parts)
    
    def _calculate_confidence(self, interaction: Dict) -> float:
        """計算置信度"""
        confidence = 0.5  # 基礎置信度
        
        # 基於工具使用
        tools_count = len(interaction.get('tools_used', []))
        if tools_count > 0:
            confidence += min(tools_count * 0.1, 0.3)
        
        # 基於響應長度
        response_length = len(interaction.get('assistant_response', ''))
        if response_length > 200:
            confidence += 0.1
        if response_length > 500:
            confidence += 0.1
        
        # 基於用戶輸入清晰度
        user_input = interaction.get('user_input', '')
        if len(user_input) > 50:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _save_training_sample(self, sample: Dict):
        """保存訓練樣本"""
        try:
            with open(self.daily_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"保存訓練樣本失敗: {e}")
    
    def get_session_summary(self) -> Dict:
        """獲取會話摘要"""
        interactions = self.current_session['interactions']
        
        if not interactions:
            return {'message': '當前會話暫無交互數據'}
        
        # 統計信息
        total_interactions = len(interactions)
        tools_used = set()
        interaction_types = {}
        
        for interaction in interactions:
            # 統計工具使用
            tools_used.update(interaction.get('tools_used', []))
            
            # 統計交互類型
            itype = interaction.get('interaction_type', 'unknown')
            interaction_types[itype] = interaction_types.get(itype, 0) + 1
        
        summary = {
            'session_id': self.current_session['session_id'],
            'start_time': self.current_session['start_time'],
            'total_interactions': total_interactions,
            'tools_used': list(tools_used),
            'interaction_types': interaction_types,
            'data_file': str(self.daily_file),
            'estimated_training_samples': total_interactions
        }
        
        return summary
    
    def end_session(self):
        """結束當前會話"""
        if self.current_session:
            self.current_session['end_time'] = datetime.now().isoformat()
            
            # 保存會話摘要
            summary_file = self.data_dir / f"session_summary_{self.current_session['session_id']}.json"
            try:
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_session, f, ensure_ascii=False, indent=2)
                logger.info(f"會話摘要已保存: {summary_file}")
            except Exception as e:
                logger.error(f"保存會話摘要失敗: {e}")

# 全局收集器實例
_global_collector = None

def get_collector():
    """獲取全局收集器實例"""
    global _global_collector
    if _global_collector is None:
        _global_collector = AutoTrainingCollector()
    return _global_collector

def collect_claude_interaction(user_input: str, assistant_response: str, tools_used: List[str] = None, context: Dict = None):
    """便捷函數：收集 Claude 交互數據"""
    collector = get_collector()
    return collector.collect_interaction(user_input, assistant_response, tools_used, context)

def get_current_session_summary():
    """便捷函數：獲取當前會話摘要"""
    collector = get_collector()
    return collector.get_session_summary()

# 在模塊導入時自動啟動收集器（如果在 Claude Code 環境中）
if __name__ != "__main__":
    try:
        # 檢查是否在 Claude Code 環境中
        if os.environ.get('CLAUDE_CODE_SESSION') or 'claude' in sys.executable.lower():
            logger.info("🤖 自動訓練數據收集器已啟動")
            get_collector()
    except Exception as e:
        logger.warning(f"自動啟動收集器失敗: {e}")

if __name__ == "__main__":
    # 測試收集器
    collector = AutoTrainingCollector()
    
    # 模擬一些交互
    collector.collect_interaction(
        user_input="幫我創建一個Python腳本來處理JSON數據",
        assistant_response="我將創建一個Python腳本來處理JSON數據。\n\n```python\nimport json\ndef process_json(file_path):\n    with open(file_path, 'r') as f:\n        data = json.load(f)\n    return data\n```",
        tools_used=["Write", "Edit"],
        context={"task_type": "development"}
    )
    
    # 顯示摘要
    summary = collector.get_session_summary()
    print(f"\n會話摘要:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))