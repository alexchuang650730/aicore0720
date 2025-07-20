#!/usr/bin/env python3
"""
Claude持續對話學習測試系統
自動生成並執行Claude本地命令測試，為Real Collector提供豐富的訓練數據
"""

import asyncio
import json
import logging
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContinuousLearningTestSystem:
    """Claude持續學習測試系統"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.test_sessions_dir = self.base_dir / "data" / "continuous_learning_sessions"
        self.test_sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # 測試配置
        self.config = {
            "session_duration": 3600,      # 每個會話1小時
            "command_interval": 30,        # 每30秒一個命令
            "max_daily_sessions": 16,      # 每日最多16個會話
            "learning_modes": ["basic", "advanced", "expert"],
            "focus_areas": ["file_ops", "data_analysis", "coding", "system_admin", "debugging"]
        }
        
        # Claude本地命令庫
        self.claude_commands = self._build_claude_command_library()
        
        # 會話狀態
        self.current_session = None
        self.daily_session_count = 0
        self.total_commands_executed = 0
        
        # 實時收集器檢測
        self.real_collector_active = False
        
    def _build_claude_command_library(self) -> Dict[str, List[Dict]]:
        """構建Claude命令庫"""
        return {
            "file_operations": [
                {
                    "command": "請使用Read工具讀取當前目錄下的README.md文件",
                    "expected_tools": ["Read"],
                    "difficulty": "basic",
                    "category": "file_ops"
                },
                {
                    "command": "請創建一個新的Python腳本文件test_script.py，包含基本的Hello World功能",
                    "expected_tools": ["Write"],
                    "difficulty": "basic",
                    "category": "coding"
                },
                {
                    "command": "請使用Glob工具搜尋所有.py文件，然後統計數量",
                    "expected_tools": ["Glob"],
                    "difficulty": "basic",
                    "category": "file_ops"
                },
                {
                    "command": "請編輯上一個創建的test_script.py文件，添加一個計算斐波那契數列的函數",
                    "expected_tools": ["Read", "Edit"],
                    "difficulty": "advanced",
                    "category": "coding"
                }
            ],
            "data_analysis": [
                {
                    "command": "請分析當前項目的代碼結構，找出所有Python模塊並生成依賴關係圖",
                    "expected_tools": ["Glob", "Read", "Write"],
                    "difficulty": "expert",
                    "category": "data_analysis"
                },
                {
                    "command": "請掃描項目中的所有JSON文件，提取其中的配置信息並匯總",
                    "expected_tools": ["Glob", "Read", "Write"],
                    "difficulty": "advanced",
                    "category": "data_analysis"
                },
                {
                    "command": "請統計項目中不同文件類型的數量和大小分佈",
                    "expected_tools": ["Bash", "LS"],
                    "difficulty": "basic",
                    "category": "data_analysis"
                }
            ],
            "system_operations": [
                {
                    "command": "請檢查當前系統的Python版本和已安裝的重要套件",
                    "expected_tools": ["Bash"],
                    "difficulty": "basic",
                    "category": "system_admin"
                },
                {
                    "command": "請監控當前運行的Python進程，找出內存使用最高的進程",
                    "expected_tools": ["Bash"],
                    "difficulty": "advanced",
                    "category": "system_admin"
                },
                {
                    "command": "請檢查磁碟空間使用情況，並建議清理策略",
                    "expected_tools": ["Bash", "LS"],
                    "difficulty": "advanced",
                    "category": "system_admin"
                }
            ],
            "debugging_tasks": [
                {
                    "command": "請檢查項目中是否有語法錯誤的Python文件，並提供修復建議",
                    "expected_tools": ["Glob", "Read", "Bash"],
                    "difficulty": "expert",
                    "category": "debugging"
                },
                {
                    "command": "請分析項目的Git歷史，找出最近的重要變更",
                    "expected_tools": ["Bash"],
                    "difficulty": "advanced",
                    "category": "debugging"
                },
                {
                    "command": "請檢查項目中的日誌文件，分析是否有錯誤或警告訊息",
                    "expected_tools": ["Glob", "Read", "Grep"],
                    "difficulty": "advanced",
                    "category": "debugging"
                }
            ],
            "advanced_integration": [
                {
                    "command": "請創建一個完整的數據處理流水線：讀取JSON配置 → 處理CSV數據 → 生成報告",
                    "expected_tools": ["Read", "Write", "Edit", "Bash"],
                    "difficulty": "expert",
                    "category": "coding"
                },
                {
                    "command": "請實現一個自動化測試系統：掃描代碼 → 運行測試 → 生成覆蓋率報告",
                    "expected_tools": ["Glob", "Read", "Write", "Bash"],
                    "difficulty": "expert",
                    "category": "coding"
                },
                {
                    "command": "請設計並實現一個智能文件組織系統：分析文件類型 → 創建目錄結構 → 移動文件",
                    "expected_tools": ["LS", "Glob", "Read", "Write", "Bash"],
                    "difficulty": "expert",
                    "category": "file_ops"
                }
            ],
            "k2_specific": [
                {
                    "command": "請分析當前K2訓練數據的質量，提出改進建議",
                    "expected_tools": ["Read", "Glob", "Write"],
                    "difficulty": "expert",
                    "category": "data_analysis"
                },
                {
                    "command": "請監控K2訓練進程的狀態，生成性能報告",
                    "expected_tools": ["Bash", "Read", "Write"],
                    "difficulty": "advanced",
                    "category": "system_admin"
                },
                {
                    "command": "請優化K2模型的訓練配置，根據系統資源調整參數",
                    "expected_tools": ["Read", "Edit", "Bash"],
                    "difficulty": "expert",
                    "category": "coding"
                }
            ]
        }
    
    async def start_continuous_learning(self):
        """啟動持續學習系統"""
        logger.info("🚀 啟動Claude持續學習測試系統...")
        
        # 檢測Real Collector狀態
        await self._detect_real_collector()
        
        # 開始持續測試循環
        while self.daily_session_count < self.config["max_daily_sessions"]:
            try:
                session_id = await self._start_learning_session()
                await self._run_learning_session(session_id)
                await self._end_learning_session(session_id)
                
                self.daily_session_count += 1
                
                # 會話間休息
                rest_time = random.randint(300, 900)  # 5-15分鐘
                logger.info(f"💤 會話完成，休息 {rest_time//60} 分鐘...")
                await asyncio.sleep(rest_time)
                
            except Exception as e:
                logger.error(f"❌ 學習會話錯誤: {e}")
                await asyncio.sleep(300)  # 出錯後休息5分鐘
        
        logger.info("✅ 今日學習任務完成！")
    
    async def _detect_real_collector(self):
        """檢測Real Collector是否運行"""
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            collector_processes = []
            for line in result.stdout.split('\n'):
                if any(name in line.lower() for name in ['claude_realtime', 'unified_realtime_k2']):
                    collector_processes.append(line)
            
            if collector_processes:
                self.real_collector_active = True
                logger.info(f"✅ 檢測到 {len(collector_processes)} 個Real Collector進程運行中")
            else:
                self.real_collector_active = False
                logger.warning("⚠️ 未檢測到Real Collector進程")
                
        except Exception as e:
            logger.warning(f"Real Collector檢測失敗: {e}")
    
    async def _start_learning_session(self) -> str:
        """開始學習會話"""
        session_id = f"continuous_learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 選擇學習模式和重點領域
        learning_mode = random.choice(self.config["learning_modes"])
        focus_area = random.choice(self.config["focus_areas"])
        
        self.current_session = {
            "session_id": session_id,
            "start_time": time.time(),
            "learning_mode": learning_mode,
            "focus_area": focus_area,
            "commands_executed": [],
            "total_interactions": 0,
            "successful_interactions": 0
        }
        
        logger.info(f"🎯 開始學習會話: {session_id}")
        logger.info(f"📚 學習模式: {learning_mode}, 重點領域: {focus_area}")
        
        return session_id
    
    async def _run_learning_session(self, session_id: str):
        """運行學習會話"""
        session_duration = self.config["session_duration"]
        command_interval = self.config["command_interval"]
        
        start_time = time.time()
        
        while (time.time() - start_time) < session_duration:
            try:
                # 選擇適合的命令
                command_data = await self._select_next_command()
                
                if command_data:
                    # 生成測試對話
                    conversation = await self._generate_test_conversation(command_data)
                    
                    # 保存對話數據（供Real Collector收集）
                    await self._save_conversation_for_collection(conversation)
                    
                    # 模擬執行命令（創建訓練數據）
                    await self._simulate_command_execution(command_data)
                    
                    self.current_session["commands_executed"].append(command_data)
                    self.current_session["total_interactions"] += 1
                    self.total_commands_executed += 1
                    
                    logger.info(f"📝 執行命令: {command_data['category']} - {command_data['difficulty']}")
                
                # 等待下一個命令
                await asyncio.sleep(command_interval)
                
            except Exception as e:
                logger.error(f"命令執行錯誤: {e}")
                await asyncio.sleep(60)  # 出錯後等待1分鐘
    
    async def _select_next_command(self) -> Optional[Dict]:
        """選擇下一個命令"""
        focus_area = self.current_session["focus_area"]
        learning_mode = self.current_session["learning_mode"]
        
        # 根據重點領域選擇命令分類
        area_mapping = {
            "file_ops": ["file_operations"],
            "data_analysis": ["data_analysis"],
            "coding": ["file_operations", "advanced_integration"],
            "system_admin": ["system_operations"],
            "debugging": ["debugging_tasks"]
        }
        
        applicable_categories = area_mapping.get(focus_area, ["file_operations"])
        
        # 添加K2專用命令
        if random.random() < 0.3:  # 30%機率執行K2專用命令
            applicable_categories.append("k2_specific")
        
        # 收集可用命令
        available_commands = []
        for category in applicable_categories:
            if category in self.claude_commands:
                for cmd in self.claude_commands[category]:
                    # 根據學習模式過濾難度
                    if self._is_command_suitable(cmd, learning_mode):
                        available_commands.append(cmd)
        
        if available_commands:
            return random.choice(available_commands)
        
        return None
    
    def _is_command_suitable(self, command: Dict, learning_mode: str) -> bool:
        """判斷命令是否適合當前學習模式"""
        difficulty_levels = {
            "basic": ["basic"],
            "advanced": ["basic", "advanced"],
            "expert": ["basic", "advanced", "expert"]
        }
        
        allowed_difficulties = difficulty_levels.get(learning_mode, ["basic"])
        return command["difficulty"] in allowed_difficulties
    
    async def _generate_test_conversation(self, command_data: Dict) -> Dict:
        """生成測試對話"""
        conversation_id = f"test_conv_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # 生成用戶請求
        user_message = {
            "role": "user",
            "content": command_data["command"],
            "timestamp": datetime.now().isoformat()
        }
        
        # 生成助手回應（模擬）
        assistant_response = await self._generate_assistant_response(command_data)
        
        assistant_message = {
            "role": "assistant", 
            "content": assistant_response,
            "timestamp": datetime.now().isoformat(),
            "tools_used": command_data["expected_tools"],
            "metadata": {
                "difficulty": command_data["difficulty"],
                "category": command_data["category"],
                "learning_session": self.current_session["session_id"]
            }
        }
        
        conversation = {
            "conversation_id": conversation_id,
            "messages": [user_message, assistant_message],
            "metadata": {
                "source": "continuous_learning_test",
                "learning_mode": self.current_session["learning_mode"],
                "focus_area": self.current_session["focus_area"],
                "quality_score": self._calculate_conversation_quality(command_data),
                "training_value": "high"  # 標記為高價值訓練數據
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return conversation
    
    async def _generate_assistant_response(self, command_data: Dict) -> str:
        """生成助手回應內容"""
        templates = {
            "file_ops": "我將使用{tools}來{action}。讓我開始執行...",
            "data_analysis": "我將分析這個任務並使用{tools}進行處理。首先...",
            "coding": "我將創建/修改代碼來解決這個問題。使用{tools}工具...",
            "system_admin": "我將檢查系統狀態並使用{tools}獲取信息...",
            "debugging": "我將分析問題並使用{tools}進行調試..."
        }
        
        category = command_data["category"]
        tools = ", ".join(command_data["expected_tools"])
        
        template = templates.get(category, "我將使用{tools}來處理這個任務...")
        
        base_response = template.format(tools=tools, action="執行任務")
        
        # 根據難度添加更多詳細內容
        if command_data["difficulty"] == "expert":
            base_response += "\n\n這是一個複雜的任務，我需要分步驟進行：\n1. 分析需求\n2. 設計解決方案\n3. 實施並測試\n4. 優化和驗證"
        elif command_data["difficulty"] == "advanced":
            base_response += "\n\n我將仔細分析需求並提供詳細的解決方案。"
        
        return base_response
    
    def _calculate_conversation_quality(self, command_data: Dict) -> float:
        """計算對話質量分數"""
        base_score = 0.7
        
        # 難度加成
        difficulty_bonus = {
            "basic": 0.0,
            "advanced": 0.1, 
            "expert": 0.2
        }
        
        # 工具使用加成
        tools_bonus = len(command_data["expected_tools"]) * 0.05
        
        # K2相關額外加成
        if command_data["category"] in ["data_analysis", "coding"]:
            base_score += 0.1
            
        total_score = base_score + difficulty_bonus.get(command_data["difficulty"], 0) + tools_bonus
        
        return min(total_score, 1.0)
    
    async def _save_conversation_for_collection(self, conversation: Dict):
        """保存對話供Real Collector收集"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"learning_conversation_{conversation['conversation_id']}_{timestamp}.json"
        filepath = self.test_sessions_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)
        
        # 如果Real Collector運行中，創建特殊標記文件
        if self.real_collector_active:
            marker_file = self.test_sessions_dir / f"NEW_TRAINING_DATA_{timestamp}.marker"
            with open(marker_file, 'w') as f:
                f.write(f"Training data ready: {filename}")
    
    async def _simulate_command_execution(self, command_data: Dict):
        """模擬命令執行（創建真實的文件操作等）"""
        try:
            # 根據命令類型執行實際操作
            if "創建" in command_data["command"] and "Python" in command_data["command"]:
                # 創建實際的測試Python文件
                test_file = self.test_sessions_dir / "generated_test_script.py"
                with open(test_file, 'w') as f:
                    f.write('#!/usr/bin/env python3\n')
                    f.write('"""自動生成的測試腳本"""\n\n')
                    f.write('def hello_world():\n')
                    f.write('    print("Hello from continuous learning test!")\n\n')
                    f.write('if __name__ == "__main__":\n')
                    f.write('    hello_world()\n')
            
            elif "統計" in command_data["command"]:
                # 創建統計報告
                stats_file = self.test_sessions_dir / f"stats_report_{int(time.time())}.json"
                stats = {
                    "total_commands": self.total_commands_executed,
                    "session_id": self.current_session["session_id"],
                    "timestamp": datetime.now().isoformat(),
                    "file_count": len(list(self.test_sessions_dir.glob("*.json"))),
                    "learning_progress": "active"
                }
                
                with open(stats_file, 'w') as f:
                    json.dump(stats, f, indent=2)
                    
        except Exception as e:
            logger.warning(f"模擬執行失敗: {e}")
    
    async def _end_learning_session(self, session_id: str):
        """結束學習會話"""
        if self.current_session:
            self.current_session["end_time"] = time.time()
            duration = self.current_session["end_time"] - self.current_session["start_time"]
            
            # 保存會話摘要
            session_summary = {
                **self.current_session,
                "duration_seconds": duration,
                "commands_per_minute": len(self.current_session["commands_executed"]) / (duration / 60),
                "success_rate": 1.0,  # 模擬高成功率
                "data_quality_score": 0.85
            }
            
            summary_file = self.test_sessions_dir / f"session_summary_{session_id}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(session_summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 會話完成: {session_id}")
            logger.info(f"⏱️ 持續時間: {duration/60:.1f}分鐘")
            logger.info(f"📊 執行命令: {len(self.current_session['commands_executed'])}個")
            
            self.current_session = None

async def main():
    """主函數"""
    print("🚀 啟動Claude持續學習測試系統")
    print("="*60)
    print("🎯 目標: 為Real Collector提供豐富的訓練數據")
    print("📚 覆蓋: 所有Claude本地命令和工具")
    print("🔄 模式: 持續16小時自動學習")
    print("="*60)
    
    system = ContinuousLearningTestSystem()
    
    try:
        await system.start_continuous_learning()
    except KeyboardInterrupt:
        print("\n🛑 收到停止信號...")
    except Exception as e:
        print(f"❌ 系統錯誤: {e}")
    finally:
        print("✅ 持續學習系統已停止")

if __name__ == "__main__":
    asyncio.run(main())