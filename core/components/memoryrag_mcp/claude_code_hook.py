#!/usr/bin/env python3
"""
Claude Code 工作流掛鉤
自動捕獲每次 Claude Code 使用並收集訓練數據
"""

import os
import sys
import functools
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import logging

# 添加當前項目到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.components.memoryrag_mcp.auto_training_collector import collect_claude_interaction
    COLLECTOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"訓練數據收集器不可用: {e}")
    COLLECTOR_AVAILABLE = False

logger = logging.getLogger(__name__)

class ClaudeCodeHook:
    """Claude Code 工作流掛鉤"""
    
    def __init__(self):
        self.session_data = {
            'start_time': datetime.now().isoformat(),
            'interactions': []
        }
        self.enabled = COLLECTOR_AVAILABLE and self._should_enable_collection()
        
        if self.enabled:
            logger.info("🎣 Claude Code 訓練數據掛鉤已啟動")
    
    def _should_enable_collection(self) -> bool:
        """判斷是否應該啟用數據收集"""
        # 檢查環境變量
        if os.environ.get('DISABLE_TRAINING_COLLECTION', '').lower() in ['1', 'true', 'yes']:
            return False
        
        # 檢查是否在開發環境
        if os.environ.get('CLAUDE_CODE_TRAINING', '').lower() in ['1', 'true', 'yes']:
            return True
        
        # 默認啟用（如果收集器可用）
        return True
    
    def capture_interaction(self, user_message: str, assistant_response: str, tools_used: List[str] = None, context: Dict = None):
        """捕獲交互數據"""
        if not self.enabled:
            return
        
        try:
            # 清理和預處理數據
            user_message = self._clean_message(user_message)
            assistant_response = self._clean_message(assistant_response)
            tools_used = tools_used or []
            
            # 收集數據
            training_sample = collect_claude_interaction(
                user_input=user_message,
                assistant_response=assistant_response,
                tools_used=tools_used,
                context=context
            )
            
            # 記錄到會話數據
            self.session_data['interactions'].append({
                'timestamp': datetime.now().isoformat(),
                'user_message_length': len(user_message),
                'response_length': len(assistant_response),
                'tools_count': len(tools_used),
                'category': training_sample.get('category', 'unknown')
            })
            
        except Exception as e:
            logger.error(f"捕獲交互數據失敗: {e}")
    
    def _clean_message(self, message: str) -> str:
        """清理消息內容"""
        if not message:
            return ""
        
        # 移除多餘的空白
        message = " ".join(message.split())
        
        # 限制長度
        if len(message) > 2000:
            message = message[:2000] + "..."
        
        return message
    
    def get_session_stats(self) -> Dict:
        """獲取會話統計"""
        interactions = self.session_data['interactions']
        
        if not interactions:
            return {'enabled': self.enabled, 'interactions': 0}
        
        # 統計
        total_interactions = len(interactions)
        total_tools = sum(i['tools_count'] for i in interactions)
        categories = {}
        
        for interaction in interactions:
            category = interaction['category']
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'enabled': self.enabled,
            'start_time': self.session_data['start_time'],
            'total_interactions': total_interactions,
            'total_tools_used': total_tools,
            'category_distribution': categories,
            'avg_tools_per_interaction': total_tools / total_interactions if total_interactions > 0 else 0
        }

# 全局掛鉤實例
_global_hook = None

def get_hook():
    """獲取全局掛鉤實例"""
    global _global_hook
    if _global_hook is None:
        _global_hook = ClaudeCodeHook()
    return _global_hook

def capture_claude_interaction(user_message: str, assistant_response: str, tools_used: List[str] = None, context: Dict = None):
    """便捷函數：捕獲 Claude 交互"""
    hook = get_hook()
    hook.capture_interaction(user_message, assistant_response, tools_used, context)

def get_training_stats():
    """便捷函數：獲取訓練統計"""
    hook = get_hook()
    return hook.get_session_stats()

# 裝飾器：自動捕獲函數調用
def auto_capture(tools_used: List[str] = None):
    """裝飾器：自動捕獲函數的輸入輸出"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 執行原函數
            result = func(*args, **kwargs)
            
            # 嘗試提取輸入和輸出
            try:
                # 構建用戶輸入（從參數中提取）
                user_input = f"調用 {func.__name__}"
                if args:
                    user_input += f" 參數: {str(args)[:200]}"
                
                # 構建助手響應（從結果中提取）
                assistant_output = f"執行 {func.__name__} 完成"
                if result is not None:
                    assistant_output += f" 結果: {str(result)[:200]}"
                
                # 捕獲交互
                capture_claude_interaction(
                    user_message=user_input,
                    assistant_response=assistant_output,
                    tools_used=tools_used or [func.__name__],
                    context={'function_call': True, 'function_name': func.__name__}
                )
                
            except Exception as e:
                logger.debug(f"自動捕獲失敗: {e}")
            
            return result
        
        return wrapper
    return decorator

# 環境檢測和自動啟動
if __name__ != "__main__":
    # 當模塊被導入時自動啟動
    try:
        get_hook()
    except Exception as e:
        logger.warning(f"Claude Code 掛鉤啟動失敗: {e}")

if __name__ == "__main__":
    # 測試掛鉤功能
    print("測試 Claude Code 掛鉤...")
    
    # 測試捕獲交互
    capture_claude_interaction(
        user_message="測試用戶消息：請幫我創建一個文件",
        assistant_response="我將為您創建文件...",
        tools_used=["Write", "Edit"],
        context={"test": True}
    )
    
    # 顯示統計
    stats = get_training_stats()
    print("\n掛鉤統計:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    # 測試裝飾器
    @auto_capture(tools_used=["test_tool"])
    def test_function(param1, param2):
        return f"處理了 {param1} 和 {param2}"
    
    # 調用測試函數
    result = test_function("數據1", "數據2")
    print(f"\n測試函數結果: {result}")
    
    # 再次顯示統計
    final_stats = get_training_stats()
    print("\n最終統計:")
    print(json.dumps(final_stats, ensure_ascii=False, indent=2))