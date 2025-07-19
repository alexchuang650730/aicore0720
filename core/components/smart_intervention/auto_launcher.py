#!/usr/bin/env python3
"""
自動啟動器
結合關鍵詞監聽和 Claude 集成的智能啟動系統
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import os

from .claude_keyword_listener import ClaudeKeywordListener, ClaudeHookSystem
from .claude_integration import ClaudeIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoLauncher:
    """自動啟動器"""
    
    def __init__(self):
        self.keyword_listener = ClaudeKeywordListener()
        self.hook_system = ClaudeHookSystem()
        self.integration = ClaudeIntegration()
        
        # 啟動配置
        self.config = self._load_config()
        
        # 設置默認鉤子
        self._setup_hooks()
        
    def _load_config(self) -> Dict[str, Any]:
        """加載配置"""
        config_file = Path("auto_launcher_config.json")
        
        default_config = {
            "enabled": True,
            "auto_launch": {
                "threshold": 2,  # 觸發啟動的關鍵詞數量閾值
                "delay": 1.0,    # 啟動延遲（秒）
                "cooldown": 300  # 冷卻時間（秒）
            },
            "features": {
                "keyword_detection": True,
                "hook_system": True,
                "claude_integration": True,
                "data_collection": True,
                "smart_suggestions": True
            },
            "keywords": {
                "high_priority": [
                    "啟動claudeditor", "launch claudeditor",
                    "打開powerautomation", "start powerautomation"
                ],
                "medium_priority": [
                    "寫代碼", "創建應用", "設計界面",
                    "運行測試", "部署項目"
                ],
                "low_priority": [
                    "編程", "開發", "調試", "優化"
                ]
            }
        }
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 合併配置
                default_config.update(user_config)
        
        return default_config
    
    def _setup_hooks(self):
        """設置鉤子"""
        # 高優先級鉤子
        for keyword in self.config["keywords"]["high_priority"]:
            self.hook_system.register_hook(
                keyword,
                "launch_immediately",
                priority=10
            )
        
        # 中優先級鉤子
        for keyword in self.config["keywords"]["medium_priority"]:
            self.hook_system.register_hook(
                keyword,
                "launch_with_context",
                priority=5
            )
        
        # 功能特定鉤子
        self.hook_system.register_hook(
            r"(創建|開發|編寫).*(react|vue|angular).*應用",
            "launch_with_framework",
            priority=8
        )
        
        self.hook_system.register_hook(
            r"使用.*(manus|chrome).*數據",
            "launch_with_data_collection",
            priority=7
        )
    
    async def start(self):
        """啟動自動啟動器"""
        logger.info("🚀 啟動自動啟動器...")
        
        # 啟用各項功能
        if self.config["features"]["claude_integration"]:
            self.integration.enable_integration()
        
        # 開始監聽
        await self._start_listening()
    
    async def _start_listening(self):
        """開始監聽"""
        logger.info("👂 開始監聽關鍵詞和觸發器...")
        
        last_launch_time = None
        
        while True:
            try:
                # 這裡應該從實際的 Claude 對話中獲取消息
                # 現在使用模擬消息進行測試
                message = await self._get_next_message()
                
                if message:
                    # 檢查冷卻時間
                    if last_launch_time:
                        elapsed = (datetime.now() - last_launch_time).total_seconds()
                        if elapsed < self.config["auto_launch"]["cooldown"]:
                            logger.info(f"冷卻中... 還需等待 {self.config['auto_launch']['cooldown'] - elapsed:.0f} 秒")
                            continue
                    
                    # 處理消息
                    should_launch = await self._process_message(message)
                    
                    if should_launch:
                        # 延遲啟動
                        await asyncio.sleep(self.config["auto_launch"]["delay"])
                        
                        # 執行啟動
                        success = await self._execute_launch(message)
                        
                        if success:
                            last_launch_time = datetime.now()
                            logger.info("✅ 成功啟動 ClaudeEditor & PowerAutomation")
                
            except Exception as e:
                logger.error(f"處理消息時出錯: {str(e)}")
            
            # 短暫休眠
            await asyncio.sleep(0.5)
    
    async def _get_next_message(self) -> Optional[str]:
        """獲取下一條消息（模擬）"""
        # 在實際實現中，這裡應該從 Claude 對話流中獲取消息
        # 現在返回 None 表示沒有新消息
        return None
    
    async def _process_message(self, message: str) -> bool:
        """處理消息並決定是否啟動"""
        # 分析消息
        analysis = self.keyword_listener.analyze_message(message)
        
        # 檢查鉤子
        hook_result = await self.hook_system.process_message(message)
        
        # 決定是否啟動
        if hook_result:
            return True
        
        if analysis["should_launch"]:
            features = analysis.get("features", [])
            if len(features) >= self.config["auto_launch"]["threshold"]:
                return True
        
        return False
    
    async def _execute_launch(self, message: str) -> bool:
        """執行啟動"""
        try:
            # 創建啟動上下文
            launch_context = {
                "trigger_message": message,
                "timestamp": datetime.now().isoformat(),
                "detected_features": self.keyword_listener._detect_features(message.lower()),
                "integration_enabled": self.integration.is_active
            }
            
            # 如果集成已啟用，通過集成啟動
            if self.integration.is_active:
                self.integration._launch_claudeditor_async()
                
                # 發送初始化命令
                self.integration.send_to_claudeditor(
                    "initialize",
                    {"context": launch_context}
                )
            else:
                # 否則使用標準啟動
                analysis = self.keyword_listener.analyze_message(message)
                await self.keyword_listener.launch_system(analysis)
            
            # 記錄啟動
            self._log_launch(launch_context)
            
            return True
            
        except Exception as e:
            logger.error(f"啟動失敗: {str(e)}")
            return False
    
    def _log_launch(self, context: Dict[str, Any]):
        """記錄啟動信息"""
        log_dir = Path("logs/auto_launches")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": context["timestamp"],
            "trigger": context["trigger_message"],
            "features": context["detected_features"],
            "integration": context["integration_enabled"],
            "success": True
        }
        
        log_file = log_dir / f"launches_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_status(self) -> Dict[str, Any]:
        """獲取狀態"""
        return {
            "enabled": self.config["enabled"],
            "keyword_listener": self.keyword_listener.get_status(),
            "integration": {
                "active": self.integration.is_active,
                "session": self.integration.current_session["id"] if self.integration.current_session else None
            },
            "config": self.config
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置"""
        self.config.update(new_config)
        
        # 保存配置
        config_file = Path("auto_launcher_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        
        logger.info("配置已更新")
    
    async def stop(self):
        """停止自動啟動器"""
        logger.info("停止自動啟動器...")
        
        # 停止各組件
        self.keyword_listener.stop_system()
        self.integration.shutdown()
        
        logger.info("✅ 自動啟動器已停止")


# 便捷函數
async def start_auto_launcher():
    """啟動自動啟動器"""
    launcher = AutoLauncher()
    await launcher.start()

def get_launcher_status() -> Dict[str, Any]:
    """獲取啟動器狀態"""
    launcher = AutoLauncher()
    return launcher.get_status()


# 測試函數
async def test_auto_launcher():
    """測試自動啟動器"""
    print("🧪 測試自動啟動器")
    print("=" * 50)
    
    launcher = AutoLauncher()
    
    # 測試消息
    test_messages = [
        "我想創建一個 React 應用",
        "幫我設計一個漂亮的用戶界面",
        "使用 Manus 數據來訓練模型",
        "啟動 ClaudeEditor",
        "寫一些單元測試"
    ]
    
    for msg in test_messages:
        print(f"\n測試: {msg}")
        should_launch = await launcher._process_message(msg)
        print(f"應該啟動: {should_launch}")
        
        if should_launch:
            success = await launcher._execute_launch(msg)
            print(f"啟動結果: {'成功' if success else '失敗'}")
    
    # 顯示狀態
    print("\n當前狀態:")
    print(json.dumps(launcher.get_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(test_auto_launcher())