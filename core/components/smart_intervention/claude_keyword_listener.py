#!/usr/bin/env python3
"""
Claude 關鍵詞監聽器
監聽特定關鍵詞並自動啟動 ClaudeEditor & PowerAutomation
"""

import asyncio
import json
import logging
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import os
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeKeywordListener:
    """Claude 關鍵詞監聽器"""
    
    def __init__(self):
        # 啟動關鍵詞
        self.launch_keywords = {
            # 直接啟動指令
            "啟動claudeditor": ["direct", "launch"],
            "啟動powerautomation": ["direct", "launch"],
            "launch claudeditor": ["direct", "launch"],
            "launch powerautomation": ["direct", "launch"],
            "start claudeditor": ["direct", "launch"],
            "start powerautomation": ["direct", "launch"],
            "打開claudeditor": ["direct", "launch"],
            "打開powerautomation": ["direct", "launch"],
            
            # 工作流觸發
            "我要寫代碼": ["workflow", "code"],
            "幫我創建": ["workflow", "create"],
            "生成ui": ["workflow", "ui"],
            "設計界面": ["workflow", "ui"],
            "寫測試": ["workflow", "test"],
            "部署應用": ["workflow", "deploy"],
            
            # 特定任務觸發
            "使用manus": ["task", "manus"],
            "收集數據": ["task", "collect"],
            "訓練模型": ["task", "training"],
            
            # 快捷指令
            "ce": ["shortcut", "claudeditor"],
            "pa": ["shortcut", "powerautomation"],
            "cep": ["shortcut", "both"]
        }
        
        # 功能映射
        self.feature_triggers = {
            "code": ["代碼", "編程", "開發", "function", "class", "api"],
            "ui": ["界面", "ui", "組件", "component", "design", "頁面"],
            "test": ["測試", "test", "檢查", "驗證", "check"],
            "data": ["數據", "data", "收集", "分析", "統計"],
            "deploy": ["部署", "deploy", "發布", "release", "上線"]
        }
        
        # 運行狀態
        self.is_running = False
        self.processes = {}
        self.launch_history = []
        
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """分析消息內容"""
        message_lower = message.lower()
        
        # 檢查直接啟動關鍵詞
        for keyword, (trigger_type, target) in self.launch_keywords.items():
            if keyword in message_lower:
                return {
                    "should_launch": True,
                    "trigger_type": trigger_type,
                    "target": target,
                    "keyword": keyword,
                    "features": self._detect_features(message_lower)
                }
        
        # 檢查功能觸發詞
        detected_features = self._detect_features(message_lower)
        if len(detected_features) >= 2:  # 至少檢測到2個相關功能
            return {
                "should_launch": True,
                "trigger_type": "auto",
                "target": "both",
                "features": detected_features
            }
        
        return {"should_launch": False}
    
    def _detect_features(self, message: str) -> List[str]:
        """檢測需要的功能"""
        detected = []
        for feature, keywords in self.feature_triggers.items():
            if any(keyword in message for keyword in keywords):
                detected.append(feature)
        return detected
    
    async def launch_system(self, analysis: Dict[str, Any]) -> bool:
        """根據分析結果啟動系統"""
        if self.is_running:
            logger.info("系統已在運行中")
            return True
        
        target = analysis.get("target", "both")
        features = analysis.get("features", [])
        
        logger.info(f"🚀 啟動系統: {target}")
        logger.info(f"📋 檢測到功能需求: {features}")
        
        try:
            # 創建啟動配置
            launch_config = self._create_launch_config(target, features)
            
            # 保存配置
            config_file = Path("launch_config.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(launch_config, f, ensure_ascii=False, indent=2)
            
            # 啟動系統
            if target in ["launch", "both", "claudeditor"]:
                process = subprocess.Popen([
                    "bash", "start_claudeditor.sh"
                ], env={**os.environ, "LAUNCH_CONFIG": str(config_file)})
                
                self.processes["claudeditor"] = process
                self.is_running = True
                
                # 記錄啟動歷史
                self.launch_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "trigger": analysis,
                    "config": launch_config
                })
                
                logger.info("✅ ClaudeEditor & PowerAutomation 已啟動")
                
                # 等待系統穩定
                await asyncio.sleep(3)
                
                # 自動打開相關功能
                await self._auto_open_features(features)
                
                return True
            
        except Exception as e:
            logger.error(f"啟動失敗: {str(e)}")
            return False
    
    def _create_launch_config(self, target: str, features: List[str]) -> Dict[str, Any]:
        """創建啟動配置"""
        config = {
            "target": target,
            "features": features,
            "timestamp": datetime.now().isoformat(),
            "settings": {
                "auto_open": True,
                "data_collection": True,
                "show_welcome": True
            }
        }
        
        # 根據功能配置不同的設置
        if "code" in features:
            config["settings"]["open_editor"] = True
            config["settings"]["language_servers"] = ["python", "javascript", "typescript"]
        
        if "ui" in features:
            config["settings"]["open_designer"] = True
            config["settings"]["preview_mode"] = True
        
        if "test" in features:
            config["settings"]["test_runner"] = True
            config["settings"]["coverage"] = True
        
        if "data" in features:
            config["settings"]["data_collector"] = True
            config["settings"]["analytics_dashboard"] = True
        
        if "deploy" in features:
            config["settings"]["deployment_panel"] = True
            config["settings"]["ci_cd_integration"] = True
        
        return config
    
    async def _auto_open_features(self, features: List[str]):
        """自動打開相關功能面板"""
        if not features:
            return
        
        # 通過 API 打開相應功能
        api_url = "http://localhost:8000/api/v1"
        
        feature_endpoints = {
            "code": f"{api_url}/editor/open",
            "ui": f"{api_url}/designer/open",
            "test": f"{api_url}/test-runner/open",
            "data": f"{api_url}/analytics/open",
            "deploy": f"{api_url}/deployment/open"
        }
        
        for feature in features:
            if feature in feature_endpoints:
                try:
                    # 這裡應該使用 aiohttp 發送請求
                    logger.info(f"打開功能面板: {feature}")
                except Exception as e:
                    logger.error(f"打開 {feature} 失敗: {str(e)}")
    
    def stop_system(self):
        """停止系統"""
        if not self.is_running:
            return
        
        logger.info("🛑 停止系統...")
        
        for name, process in self.processes.items():
            if process.poll() is None:
                process.terminate()
                logger.info(f"終止進程: {name}")
        
        self.processes.clear()
        self.is_running = False
        
        logger.info("✅ 系統已停止")
    
    def get_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "is_running": self.is_running,
            "processes": list(self.processes.keys()),
            "launch_count": len(self.launch_history),
            "last_launch": self.launch_history[-1] if self.launch_history else None
        }


# 鉤子系統集成
class ClaudeHookSystem:
    """Claude 鉤子系統"""
    
    def __init__(self):
        self.listener = ClaudeKeywordListener()
        self.hooks = []
        
    def register_hook(self, pattern: str, action: str, priority: int = 0):
        """註冊鉤子"""
        hook = {
            "pattern": re.compile(pattern, re.IGNORECASE),
            "action": action,
            "priority": priority
        }
        self.hooks.append(hook)
        self.hooks.sort(key=lambda x: x["priority"], reverse=True)
        
        logger.info(f"註冊鉤子: {pattern} -> {action}")
    
    async def process_message(self, message: str) -> bool:
        """處理消息"""
        # 先檢查鉤子
        for hook in self.hooks:
            if hook["pattern"].search(message):
                logger.info(f"觸發鉤子: {hook['action']}")
                
                if hook["action"] == "launch_claudeditor":
                    analysis = {
                        "should_launch": True,
                        "trigger_type": "hook",
                        "target": "claudeditor"
                    }
                    return await self.listener.launch_system(analysis)
        
        # 再進行關鍵詞分析
        analysis = self.listener.analyze_message(message)
        if analysis["should_launch"]:
            return await self.listener.launch_system(analysis)
        
        return False
    
    def setup_default_hooks(self):
        """設置默認鉤子"""
        # 開發相關
        self.register_hook(
            r"(創建|寫|開發|編寫).*(應用|app|網站|程序)",
            "launch_claudeditor",
            priority=10
        )
        
        # UI 設計相關
        self.register_hook(
            r"(設計|製作|生成).*(界面|ui|頁面|組件)",
            "launch_claudeditor",
            priority=10
        )
        
        # 測試相關
        self.register_hook(
            r"(運行|執行|寫).*(測試|test|檢查)",
            "launch_claudeditor",
            priority=5
        )
        
        # 部署相關
        self.register_hook(
            r"(部署|發布|上線).*(應用|網站|服務)",
            "launch_claudeditor",
            priority=5
        )


# 全局實例
hook_system = ClaudeHookSystem()

async def main():
    """主函數 - 用於測試"""
    print("🎯 Claude 關鍵詞監聽器")
    print("=" * 50)
    
    # 設置默認鉤子
    hook_system.setup_default_hooks()
    
    # 測試消息
    test_messages = [
        "我要創建一個新的網站應用",
        "幫我設計一個漂亮的用戶界面",
        "啟動 ClaudeEditor",
        "寫一些測試代碼",
        "部署應用到生產環境",
        "CE"  # 快捷指令
    ]
    
    for msg in test_messages:
        print(f"\n測試消息: {msg}")
        result = await hook_system.process_message(msg)
        print(f"結果: {'啟動成功' if result else '未觸發啟動'}")
        
        # 如果啟動了，等待一下再測試下一個
        if result:
            await asyncio.sleep(2)
            hook_system.listener.stop_system()


if __name__ == "__main__":
    asyncio.run(main())