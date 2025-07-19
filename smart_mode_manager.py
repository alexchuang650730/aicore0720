#!/usr/bin/env python3
"""
智能模式管理器
管理 Claude 和 K2 模式的自動切換，以及訓練數據的智能採集
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartModeManager:
    """智能模式管理器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "data/mode_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 默認配置
        self.default_config = {
            "current_mode": "claude",  # claude 或 k2
            "auto_switch_enabled": True,
            "cost_threshold_daily": 50.0,  # 每日成本閾值（元）
            "k2_usage_hours": [],  # K2 使用的時間段
            "claude_usage_hours": [],  # Claude 使用的時間段
            "training_collection": {
                "enabled_in_claude_mode": True,
                "enabled_in_k2_mode": False,
                "auto_switch_threshold": 100  # 收集多少條數據後觸發 K2 重訓練
            },
            "deployment_integration": {
                "switch_to_k2_on_deploy": True,
                "products": ["claudeditor", "powerautomation"]
            },
            "last_updated": datetime.now().isoformat()
        }
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """載入配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合併默認配置（處理新增字段）
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                return self.default_config.copy()
        except Exception as e:
            logger.error(f"載入配置失敗: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        """保存配置"""
        try:
            self.config["last_updated"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置失敗: {e}")
    
    def switch_to_k2_mode(self, reason: str = "manual"):
        """切換到 K2 模式"""
        logger.info(f"🔄 切換到 K2 模式 - 原因: {reason}")
        
        self.config["current_mode"] = "k2"
        
        # 禁用訓練數據採集
        os.environ['DISABLE_TRAINING_COLLECTION'] = '1'
        
        # 設置 K2 環境變量
        os.environ['USE_K2_MODEL'] = '1'
        os.environ['K2_MODE_REASON'] = reason
        
        # 更新配置
        self.config["mode_switches"] = self.config.get("mode_switches", [])
        self.config["mode_switches"].append({
            "timestamp": datetime.now().isoformat(),
            "from_mode": "claude",
            "to_mode": "k2",
            "reason": reason
        })
        
        self.save_config()
        
        # 記錄切換
        self._log_mode_switch("k2", reason)
        
        return True
    
    def switch_to_claude_mode(self, reason: str = "manual"):
        """切換到 Claude 模式"""
        logger.info(f"🔄 切換到 Claude 模式 - 原因: {reason}")
        
        self.config["current_mode"] = "claude"
        
        # 啟用訓練數據採集
        if 'DISABLE_TRAINING_COLLECTION' in os.environ:
            del os.environ['DISABLE_TRAINING_COLLECTION']
        
        os.environ['CLAUDE_CODE_TRAINING'] = '1'
        
        # 清除 K2 環境變量
        if 'USE_K2_MODEL' in os.environ:
            del os.environ['USE_K2_MODEL']
        
        # 啟動自動採集
        self._start_training_collection()
        
        # 更新配置
        self.config["mode_switches"] = self.config.get("mode_switches", [])
        self.config["mode_switches"].append({
            "timestamp": datetime.now().isoformat(),
            "from_mode": "k2",
            "to_mode": "claude",
            "reason": reason
        })
        
        self.save_config()
        
        # 記錄切換
        self._log_mode_switch("claude", reason)
        
        return True
    
    def _start_training_collection(self):
        """啟動訓練數據採集"""
        try:
            # 導入並啟動採集系統
            sys.path.insert(0, str(self.base_dir))
            from auto_start_collection import setup_auto_collection
            
            success = setup_auto_collection()
            
            if success:
                logger.info("✅ 訓練數據採集已啟動")
            else:
                logger.warning("⚠️ 訓練數據採集啟動失敗")
                
        except Exception as e:
            logger.error(f"啟動訓練數據採集失敗: {e}")
    
    def _log_mode_switch(self, new_mode: str, reason: str):
        """記錄模式切換"""
        try:
            # 如果在 Claude 模式且採集已啟動，記錄這次切換
            if new_mode == "claude":
                from core.components.memoryrag_mcp.claude_code_hook import capture_claude_interaction
                
                capture_claude_interaction(
                    user_message=f"系統自動切換到 Claude 模式",
                    assistant_response=f"已切換到 Claude 模式，原因: {reason}。訓練數據採集已自動啟動，將收集後續交互用於 K2 模型改進。",
                    tools_used=["mode_manager", "auto_switch"],
                    context={
                        "mode_switch": True,
                        "new_mode": new_mode,
                        "reason": reason,
                        "timestamp": datetime.now().isoformat()
                    }
                )
        except Exception as e:
            logger.debug(f"記錄模式切換失敗: {e}")
    
    def on_deployment_start(self, product: str):
        """部署開始時的處理"""
        if not self.config["deployment_integration"]["switch_to_k2_on_deploy"]:
            return
        
        if product.lower() in [p.lower() for p in self.config["deployment_integration"]["products"]]:
            self.switch_to_k2_mode(f"deployment_{product}")
            
            logger.info(f"🚀 {product} 部署開始 - 已切換到 K2 模式以節省成本")
            
            return True
        
        return False
    
    def on_deployment_end(self, product: str):
        """部署結束時的處理"""
        # 部署結束後，可以選擇切回 Claude 模式開始收集數據
        if self.config["current_mode"] == "k2":
            # 詢問用戶是否切回 Claude 模式
            logger.info(f"💡 {product} 部署完成。建議切換回 Claude 模式以開始收集訓練數據")
            return "suggest_switch_to_claude"
        
        return None
    
    def should_auto_switch_to_k2(self) -> bool:
        """判斷是否應該自動切換到 K2"""
        if not self.config["auto_switch_enabled"]:
            return False
        
        # 檢查成本閾值
        daily_cost = self._get_daily_cost()
        if daily_cost > self.config["cost_threshold_daily"]:
            return True
        
        # 檢查時間段
        current_hour = datetime.now().hour
        if current_hour in self.config["k2_usage_hours"]:
            return True
        
        return False
    
    def should_auto_switch_to_claude(self) -> bool:
        """判斷是否應該自動切換到 Claude"""
        if not self.config["auto_switch_enabled"]:
            return False
        
        # 檢查時間段
        current_hour = datetime.now().hour
        if current_hour in self.config["claude_usage_hours"]:
            return True
        
        # 檢查是否需要收集訓練數據
        training_data_count = self._get_training_data_count()
        if training_data_count < self.config["training_collection"]["auto_switch_threshold"]:
            return True
        
        return False
    
    def _get_daily_cost(self) -> float:
        """獲取今日成本（模擬）"""
        # 這裡應該連接到實際的成本追蹤系統
        # 目前返回模擬值
        return 0.0
    
    def _get_training_data_count(self) -> int:
        """獲取今日收集的訓練數據數量"""
        try:
            today = datetime.now().strftime("%Y%m%d")
            data_file = self.base_dir / f"data/claude_conversations/training_data_{today}.jsonl"
            
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    return sum(1 for line in f if line.strip())
            
            return 0
        except Exception:
            return 0
    
    def get_status(self) -> Dict:
        """獲取當前狀態"""
        status = {
            "current_mode": self.config["current_mode"],
            "training_collection_enabled": os.environ.get('CLAUDE_CODE_TRAINING') == '1',
            "k2_mode_enabled": os.environ.get('USE_K2_MODEL') == '1',
            "auto_switch_enabled": self.config["auto_switch_enabled"],
            "daily_training_data_count": self._get_training_data_count(),
            "last_mode_switch": None,
            "environment_vars": {
                "CLAUDE_CODE_TRAINING": os.environ.get('CLAUDE_CODE_TRAINING'),
                "USE_K2_MODEL": os.environ.get('USE_K2_MODEL'),
                "DISABLE_TRAINING_COLLECTION": os.environ.get('DISABLE_TRAINING_COLLECTION')
            }
        }
        
        # 獲取最後一次模式切換
        mode_switches = self.config.get("mode_switches", [])
        if mode_switches:
            status["last_mode_switch"] = mode_switches[-1]
        
        return status
    
    def configure_auto_switch(self, cost_threshold: float = None, k2_hours: List[int] = None, claude_hours: List[int] = None):
        """配置自動切換"""
        if cost_threshold is not None:
            self.config["cost_threshold_daily"] = cost_threshold
        
        if k2_hours is not None:
            self.config["k2_usage_hours"] = k2_hours
        
        if claude_hours is not None:
            self.config["claude_usage_hours"] = claude_hours
        
        self.save_config()
        logger.info("✅ 自動切換配置已更新")

# 全局管理器實例
_global_manager = None

def get_mode_manager():
    """獲取全局模式管理器"""
    global _global_manager
    if _global_manager is None:
        _global_manager = SmartModeManager()
    return _global_manager

# 便捷函數
def switch_to_k2(reason: str = "manual"):
    """切換到 K2 模式"""
    return get_mode_manager().switch_to_k2_mode(reason)

def switch_to_claude(reason: str = "manual"):
    """切換到 Claude 模式"""
    return get_mode_manager().switch_to_claude_mode(reason)

def on_deployment_start(product: str):
    """部署開始處理"""
    return get_mode_manager().on_deployment_start(product)

def on_deployment_end(product: str):
    """部署結束處理"""
    return get_mode_manager().on_deployment_end(product)

def get_current_status():
    """獲取當前狀態"""
    return get_mode_manager().get_status()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='智能模式管理器')
    parser.add_argument('--mode', choices=['claude', 'k2'], help='切換模式')
    parser.add_argument('--reason', default='manual', help='切換原因')
    parser.add_argument('--status', action='store_true', help='顯示狀態')
    parser.add_argument('--deploy-start', help='部署開始 (產品名)')
    parser.add_argument('--deploy-end', help='部署結束 (產品名)')
    
    args = parser.parse_args()
    
    manager = SmartModeManager()
    
    if args.status:
        status = manager.get_status()
        print("📊 智能模式管理器狀態:")
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.mode:
        if args.mode == 'k2':
            success = manager.switch_to_k2_mode(args.reason)
        else:
            success = manager.switch_to_claude_mode(args.reason)
        
        print(f"✅ 已切換到 {args.mode} 模式" if success else f"❌ 切換到 {args.mode} 模式失敗")
    
    elif args.deploy_start:
        result = manager.on_deployment_start(args.deploy_start)
        print(f"🚀 {args.deploy_start} 部署開始 - K2模式: {'已啟用' if result else '未啟用'}")
    
    elif args.deploy_end:
        result = manager.on_deployment_end(args.deploy_end)
        if result == "suggest_switch_to_claude":
            print(f"💡 建議: 部署完成，可切換到 Claude 模式收集訓練數據")
        else:
            print(f"✅ {args.deploy_end} 部署完成")
    
    else:
        # 顯示當前狀態
        status = manager.get_status()
        print(f"當前模式: {status['current_mode']}")
        print(f"訓練數據採集: {'啟用' if status['training_collection_enabled'] else '禁用'}")
        print(f"今日訓練數據: {status['daily_training_data_count']} 條")