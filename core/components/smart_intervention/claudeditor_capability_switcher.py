#!/usr/bin/env python3
"""
ClaudeEditor 能力切換器
檢測 Claude 不擅長但 ClaudeEditor 擅長的任務，自動提示切換
"""

import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeEditorCapabilitySwitcher:
    """ClaudeEditor 能力切換器"""
    
    def __init__(self):
        # Claude 不擅長但 ClaudeEditor 擅長的任務
        self.claudeditor_superior_tasks = {
            # 可視化相關
            "visualization": {
                "keywords": ["可視化", "圖表", "視覺化", "visualization", "chart", "graph", "diagram", "流程圖", "架構圖"],
                "message": "我檢測到您需要創建可視化內容。ClaudeEditor 有專業的圖表和視覺化工具，可以幫您更好地完成這個任務。",
                "features": ["diagram_editor", "chart_builder", "flow_designer"]
            },
            
            # 文件下載和管理
            "file_download": {
                "keywords": ["下載", "保存文件", "導出", "download", "save file", "export", "打包", "壓縮"],
                "message": "我注意到您需要下載或管理文件。ClaudeEditor 提供完整的文件管理功能，包括批量下載、打包和導出。",
                "features": ["file_manager", "download_manager", "export_tools"]
            },
            
            # 部署相關
            "deployment": {
                "keywords": ["部署", "發布", "上線", "deploy", "publish", "release", "docker", "kubernetes", "ci/cd"],
                "message": "部署任務需要複雜的配置和多步驟操作。ClaudeEditor 的部署工作流可以自動化整個過程。",
                "features": ["deployment_pipeline", "docker_integration", "ci_cd_tools"]
            },
            
            # 實時預覽和交互
            "live_preview": {
                "keywords": ["預覽", "實時", "互動", "preview", "live", "interactive", "hot reload", "即時"],
                "message": "ClaudeEditor 提供實時預覽和熱重載功能，讓您能即時看到代碼修改的效果。",
                "features": ["live_preview", "hot_reload", "interactive_mode"]
            },
            
            # 複雜 UI 設計
            "ui_design": {
                "keywords": ["設計界面", "ui設計", "響應式", "design ui", "responsive", "layout", "樣式", "css", "組件庫"],
                "message": "設計複雜的用戶界面需要視覺化工具。ClaudeEditor 的 UI 設計器可以拖放創建界面。",
                "features": ["ui_designer", "component_library", "style_editor"]
            },
            
            # 數據庫設計和管理
            "database": {
                "keywords": ["數據庫", "資料庫", "database", "sql", "schema", "migration", "查詢優化"],
                "message": "數據庫設計和管理需要專業工具。ClaudeEditor 提供視覺化的數據庫設計器和查詢構建器。",
                "features": ["db_designer", "query_builder", "migration_tools"]
            },
            
            # 性能分析和優化
            "performance": {
                "keywords": ["性能", "優化", "分析", "performance", "optimize", "profiling", "benchmark", "瓶頸"],
                "message": "性能分析需要專業的分析工具。ClaudeEditor 集成了多種性能分析器和優化建議。",
                "features": ["profiler", "performance_monitor", "optimization_advisor"]
            },
            
            # 團隊協作
            "collaboration": {
                "keywords": ["協作", "團隊", "共享", "collaborate", "team", "share", "實時編輯", "code review"],
                "message": "團隊協作需要實時同步功能。ClaudeEditor 支持多人實時編輯和代碼審查。",
                "features": ["real_time_collab", "code_review", "shared_workspace"]
            },
            
            # 大型項目重構
            "refactoring": {
                "keywords": ["重構", "重組", "refactor", "restructure", "大規模修改", "批量修改"],
                "message": "大規模重構需要智能的代碼分析工具。ClaudeEditor 提供自動化重構功能。",
                "features": ["refactoring_tools", "code_analysis", "batch_operations"]
            },
            
            # API 測試和文檔
            "api_testing": {
                "keywords": ["api測試", "接口測試", "api文檔", "swagger", "postman", "api test", "endpoint"],
                "message": "API 測試和文檔生成需要專門工具。ClaudeEditor 內置 API 測試客戶端和文檔生成器。",
                "features": ["api_tester", "swagger_editor", "doc_generator"]
            }
        }
        
        # 自動切換配置
        self.auto_switch_config = {
            "enabled": True,
            "confidence_threshold": 0.8,
            "prompt_before_switch": True,
            "switch_delay": 2.0
        }
        
        # 切換歷史
        self.switch_history = []
        
    def analyze_task(self, message: str) -> Tuple[bool, Optional[str], List[str]]:
        """分析任務是否適合 ClaudeEditor"""
        message_lower = message.lower()
        
        for task_type, config in self.claudeditor_superior_tasks.items():
            keywords = config["keywords"]
            matched_keywords = [kw for kw in keywords if kw in message_lower]
            
            if matched_keywords:
                # 計算匹配度
                confidence = len(matched_keywords) / len(keywords.split())
                
                if confidence >= self.auto_switch_config["confidence_threshold"]:
                    return True, task_type, config["features"]
        
        return False, None, []
    
    async def suggest_switch(self, message: str, task_type: str) -> Dict[str, Any]:
        """建議切換到 ClaudeEditor"""
        config = self.claudeditor_superior_tasks[task_type]
        
        suggestion = {
            "should_switch": True,
            "task_type": task_type,
            "reason": config["message"],
            "features": config["features"],
            "user_message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # 記錄建議
        self.switch_history.append(suggestion)
        
        # 生成切換提示
        prompt = f"""
🚀 **ClaudeEditor 可以更好地處理這個任務！**

{config['message']}

**將啟用的功能：**
"""
        for feature in config["features"]:
            prompt += f"• {self._get_feature_name(feature)}\n"
        
        prompt += "\n是否要啟動 ClaudeEditor？（將在 2 秒後自動啟動）"
        
        logger.info(prompt)
        
        return {
            "prompt": prompt,
            "suggestion": suggestion
        }
    
    def _get_feature_name(self, feature: str) -> str:
        """獲取功能的友好名稱"""
        feature_names = {
            "diagram_editor": "圖表編輯器",
            "chart_builder": "圖表構建器",
            "flow_designer": "流程設計器",
            "file_manager": "文件管理器",
            "download_manager": "下載管理器",
            "export_tools": "導出工具",
            "deployment_pipeline": "部署流水線",
            "docker_integration": "Docker 集成",
            "ci_cd_tools": "CI/CD 工具",
            "live_preview": "實時預覽",
            "hot_reload": "熱重載",
            "interactive_mode": "互動模式",
            "ui_designer": "UI 設計器",
            "component_library": "組件庫",
            "style_editor": "樣式編輯器",
            "db_designer": "數據庫設計器",
            "query_builder": "查詢構建器",
            "migration_tools": "遷移工具",
            "profiler": "性能分析器",
            "performance_monitor": "性能監控",
            "optimization_advisor": "優化顧問",
            "real_time_collab": "實時協作",
            "code_review": "代碼審查",
            "shared_workspace": "共享工作區",
            "refactoring_tools": "重構工具",
            "code_analysis": "代碼分析",
            "batch_operations": "批量操作",
            "api_tester": "API 測試器",
            "swagger_editor": "Swagger 編輯器",
            "doc_generator": "文檔生成器"
        }
        
        return feature_names.get(feature, feature)
    
    async def auto_switch_to_claudeditor(self, task_type: str, features: List[str]) -> bool:
        """自動切換到 ClaudeEditor"""
        try:
            # 等待用戶確認（如果配置需要）
            if self.auto_switch_config["prompt_before_switch"]:
                await asyncio.sleep(self.auto_switch_config["switch_delay"])
            
            # 創建啟動配置
            launch_config = {
                "trigger": "capability_switch",
                "task_type": task_type,
                "requested_features": features,
                "timestamp": datetime.now().isoformat(),
                "auto_open_features": True
            }
            
            # 保存配置
            config_file = Path("capability_switch_config.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(launch_config, f, ensure_ascii=False, indent=2)
            
            # 啟動 ClaudeEditor
            logger.info(f"🚀 正在啟動 ClaudeEditor (任務類型: {task_type})...")
            
            process = subprocess.Popen([
                "bash", "start_claudeditor.sh"
            ], env={
                **os.environ,
                "LAUNCH_REASON": "capability_switch",
                "TASK_TYPE": task_type,
                "FEATURES": ",".join(features)
            })
            
            # 等待啟動
            await asyncio.sleep(3)
            
            # 自動打開相關功能面板
            await self._open_feature_panels(features)
            
            logger.info("✅ ClaudeEditor 已啟動並配置完成")
            return True
            
        except Exception as e:
            logger.error(f"切換失敗: {str(e)}")
            return False
    
    async def _open_feature_panels(self, features: List[str]):
        """打開功能面板"""
        # 通過 API 或 IPC 通知 ClaudeEditor 打開特定功能
        feature_commands = {
            "diagram_editor": {"panel": "tools", "tab": "diagram"},
            "file_manager": {"panel": "files", "expanded": True},
            "deployment_pipeline": {"panel": "deploy", "tab": "pipeline"},
            "live_preview": {"panel": "preview", "auto_refresh": True},
            "ui_designer": {"panel": "design", "tab": "visual"},
            "db_designer": {"panel": "database", "tab": "schema"},
            "profiler": {"panel": "performance", "tab": "profiler"},
            "api_tester": {"panel": "api", "tab": "tester"}
        }
        
        for feature in features:
            if feature in feature_commands:
                command = feature_commands[feature]
                # 發送命令到 ClaudeEditor
                logger.info(f"打開功能: {feature}")
    
    def get_switch_statistics(self) -> Dict[str, Any]:
        """獲取切換統計"""
        if not self.switch_history:
            return {"total_switches": 0}
        
        stats = {
            "total_switches": len(self.switch_history),
            "task_types": {},
            "features_used": {},
            "last_switch": self.switch_history[-1]["timestamp"] if self.switch_history else None
        }
        
        for switch in self.switch_history:
            task_type = switch["task_type"]
            stats["task_types"][task_type] = stats["task_types"].get(task_type, 0) + 1
            
            for feature in switch["features"]:
                stats["features_used"][feature] = stats["features_used"].get(feature, 0) + 1
        
        return stats


# 全局切換器實例
capability_switcher = ClaudeEditorCapabilitySwitcher()

async def check_and_switch(message: str) -> bool:
    """檢查並切換到 ClaudeEditor"""
    should_switch, task_type, features = capability_switcher.analyze_task(message)
    
    if should_switch:
        suggestion = await capability_switcher.suggest_switch(message, task_type)
        logger.info(suggestion["prompt"])
        
        # 自動切換
        success = await capability_switcher.auto_switch_to_claudeditor(task_type, features)
        return success
    
    return False


# 測試函數
async def test_capability_switcher():
    """測試能力切換器"""
    print("🧪 測試 ClaudeEditor 能力切換器")
    print("=" * 50)
    
    test_messages = [
        "我需要創建一個流程圖來展示系統架構",
        "幫我下載這些文件並打包成 zip",
        "部署這個應用到 Kubernetes",
        "我想要實時預覽我的網頁修改",
        "設計一個響應式的用戶界面",
        "優化數據庫查詢性能",
        "和團隊成員一起編輯代碼",
        "重構整個項目結構",
        "創建 API 文檔和測試",
        "生成數據可視化圖表"
    ]
    
    for msg in test_messages:
        print(f"\n測試消息: {msg}")
        should_switch, task_type, features = capability_switcher.analyze_task(msg)
        
        if should_switch:
            print(f"✅ 應該切換到 ClaudeEditor")
            print(f"   任務類型: {task_type}")
            print(f"   推薦功能: {', '.join(features)}")
            
            suggestion = await capability_switcher.suggest_switch(msg, task_type)
            print(f"   建議: {capability_switcher.claudeditor_superior_tasks[task_type]['message']}")
        else:
            print("❌ 無需切換")
    
    # 顯示統計
    print("\n統計信息:")
    stats = capability_switcher.get_switch_statistics()
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(test_capability_switcher())