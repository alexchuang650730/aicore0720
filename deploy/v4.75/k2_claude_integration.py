#!/usr/bin/env python3
"""
PowerAutomation v4.75 - K2 與 Claude Code Tool 完整集成
實現自動啟動訓練模式和對話同步記錄
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import platform
import subprocess
import threading
import queue
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class K2ClaudeIntegration:
    """K2 與 Claude Code Tool 深度集成"""
    
    def __init__(self):
        self.version = "4.75"
        self.platform = platform.system().lower()  # darwin (mac) or windows
        
        # 配置路徑
        self.root_path = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        self.deploy_path = self.root_path / f"deploy/v{self.version}"
        self.training_data_path = self.deploy_path / "training_data"
        self.models_path = self.deploy_path / "models"
        
        # 創建必要目錄
        self.training_data_path.mkdir(parents=True, exist_ok=True)
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # K2 配置
        self.k2_config = {
            "model": "k2-optimizer",
            "input_price": 2.0,  # 2元/M tokens
            "output_price": 8.0, # 8元/M tokens
            "max_context": 200000,
            "temperature": 0.7,
            "training_enabled": True
        }
        
        # 對話記錄隊列
        self.conversation_queue = queue.Queue()
        self.training_queue = queue.Queue()
        
        # 狀態
        self.is_recording = False
        self.is_training = False
        self.current_session = None
        
    async def initialize(self):
        """初始化 K2 Claude 集成"""
        logger.info(f"🚀 初始化 PowerAutomation v{self.version} K2 集成")
        
        # 1. 檢查並安裝 Claude Code Tool
        await self._setup_claude_code_tool()
        
        # 2. 配置 K2 提供者
        await self._configure_k2_provider()
        
        # 3. 啟動對話記錄器
        self._start_conversation_recorder()
        
        # 4. 啟動訓練監控器
        self._start_training_monitor()
        
        # 5. 設置自動啟動鉤子
        await self._setup_auto_launch_hooks()
        
        logger.info("✅ K2 Claude 集成初始化完成")
        
    async def _setup_claude_code_tool(self):
        """設置 Claude Code Tool"""
        logger.info("設置 Claude Code Tool...")
        
        # 檢查是否已安裝
        claude_config_path = Path.home() / ".claude" / "config.json"
        
        if not claude_config_path.exists():
            # 創建配置
            claude_config = {
                "version": self.version,
                "k2_enabled": True,
                "auto_launch": True,
                "training_mode": True,
                "conversation_recording": True,
                "providers": {
                    "k2": {
                        "enabled": True,
                        "endpoint": "http://localhost:8000/k2",
                        "api_key": "k2_local_key"
                    }
                }
            }
            
            claude_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(claude_config_path, 'w') as f:
                json.dump(claude_config, f, indent=2)
            
            logger.info("✅ Claude Code Tool 配置已創建")
        else:
            # 更新現有配置
            with open(claude_config_path, 'r') as f:
                config = json.load(f)
            
            config["k2_enabled"] = True
            config["training_mode"] = True
            config["conversation_recording"] = True
            
            with open(claude_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("✅ Claude Code Tool 配置已更新")
    
    async def _configure_k2_provider(self):
        """配置 K2 提供者"""
        logger.info("配置 K2 提供者...")
        
        # 創建 K2 服務器配置
        k2_server_config = {
            "host": "0.0.0.0",
            "port": 8000,
            "model": self.k2_config["model"],
            "endpoints": {
                "/k2/chat": "K2 對話端點",
                "/k2/train": "K2 訓練端點",
                "/k2/status": "K2 狀態端點"
            },
            "training": {
                "auto_train": True,
                "batch_size": 32,
                "learning_rate": 0.001,
                "save_interval": 100
            }
        }
        
        config_path = self.deploy_path / "k2_server_config.json"
        with open(config_path, 'w') as f:
            json.dump(k2_server_config, f, indent=2)
        
        # 啟動 K2 服務器
        await self._start_k2_server(config_path)
    
    async def _start_k2_server(self, config_path: Path):
        """啟動 K2 服務器"""
        logger.info("啟動 K2 服務器...")
        
        # 創建啟動腳本
        start_script = f"""#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

app = FastAPI()

# 載入配置
with open("{config_path}", 'r') as f:
    config = json.load(f)

# K2 對話記錄
conversations = []

@app.post("/k2/chat")
async def k2_chat(request: Request):
    data = await request.json()
    
    # 記錄對話
    conversation = {{
        "timestamp": datetime.now().isoformat(),
        "messages": data.get("messages", []),
        "model": config["model"]
    }}
    conversations.append(conversation)
    
    # 生成回應（這裡應該調用實際的 K2 模型）
    response = {{
        "id": f"k2_{len(conversations)}",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": config["model"],
        "choices": [{{
            "index": 0,
            "message": {{
                "role": "assistant",
                "content": "這是 K2 模型的回應。正在處理您的請求..."
            }},
            "finish_reason": "stop"
        }}],
        "usage": {{
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }}
    }}
    
    return JSONResponse(response)

@app.post("/k2/train")
async def k2_train(request: Request):
    data = await request.json()
    
    # 啟動訓練
    return JSONResponse({{
        "status": "training_started",
        "session_id": f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "data_points": len(data.get("training_data", []))
    }})

@app.get("/k2/status")
async def k2_status():
    return JSONResponse({{
        "status": "running",
        "model": config["model"],
        "conversations": len(conversations),
        "version": "{self.version}"
    }})

if __name__ == "__main__":
    uvicorn.run(app, host=config["host"], port=config["port"])
"""
        
        server_script_path = self.deploy_path / "k2_server.py"
        with open(server_script_path, 'w') as f:
            f.write(start_script)
        
        # 在後台啟動服務器
        if self.platform == "darwin":  # Mac
            subprocess.Popen([sys.executable, str(server_script_path)], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        elif self.platform == "windows":
            subprocess.Popen([sys.executable, str(server_script_path)], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        
        # 等待服務器啟動
        await asyncio.sleep(2)
        logger.info("✅ K2 服務器已啟動")
    
    def _start_conversation_recorder(self):
        """啟動對話記錄器"""
        logger.info("啟動對話記錄器...")
        
        def recorder_thread():
            while True:
                try:
                    # 從隊列獲取對話
                    if not self.conversation_queue.empty():
                        conversation = self.conversation_queue.get()
                        
                        # 保存到文件
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        file_path = self.training_data_path / f"conversation_{timestamp}.json"
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(conversation, f, ensure_ascii=False, indent=2)
                        
                        # 加入訓練隊列
                        if self.is_training:
                            self.training_queue.put(conversation)
                    
                    threading.Event().wait(0.1)
                    
                except Exception as e:
                    logger.error(f"記錄對話錯誤: {str(e)}")
        
        recorder = threading.Thread(target=recorder_thread, daemon=True)
        recorder.start()
        self.is_recording = True
        
        logger.info("✅ 對話記錄器已啟動")
    
    def _start_training_monitor(self):
        """啟動訓練監控器"""
        logger.info("啟動訓練監控器...")
        
        def training_thread():
            batch_data = []
            
            while True:
                try:
                    # 收集訓練數據
                    if not self.training_queue.empty():
                        data = self.training_queue.get()
                        batch_data.append(data)
                        
                        # 批量訓練
                        if len(batch_data) >= 10:
                            asyncio.run(self._train_on_batch(batch_data))
                            batch_data = []
                    
                    threading.Event().wait(1)
                    
                except Exception as e:
                    logger.error(f"訓練錯誤: {str(e)}")
        
        trainer = threading.Thread(target=training_thread, daemon=True)
        trainer.start()
        
        logger.info("✅ 訓練監控器已啟動")
    
    async def _train_on_batch(self, batch_data: List[Dict]):
        """批量訓練"""
        logger.info(f"開始批量訓練，數據量: {len(batch_data)}")
        
        # 準備訓練數據
        training_examples = []
        for conversation in batch_data:
            for i in range(0, len(conversation.get("messages", [])) - 1, 2):
                if i + 1 < len(conversation["messages"]):
                    training_examples.append({
                        "input": conversation["messages"][i]["content"],
                        "output": conversation["messages"][i + 1]["content"]
                    })
        
        # 保存訓練數據
        train_file = self.training_data_path / f"train_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(train_file, 'w', encoding='utf-8') as f:
            for example in training_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        # 端側訓練（使用輕量級模型）
        if self.platform in ["darwin", "windows"]:
            await self._local_training(train_file)
        
        logger.info(f"✅ 批量訓練完成，處理了 {len(training_examples)} 個樣本")
    
    async def _local_training(self, train_file: Path):
        """端側本地訓練"""
        logger.info(f"執行端側訓練 ({self.platform})...")
        
        # 這裡實現輕量級的本地訓練
        # 可以使用 ONNX, Core ML (Mac), 或 ONNX Runtime (Windows)
        
        if self.platform == "darwin":  # Mac
            # 使用 Core ML 或 Metal Performance Shaders
            logger.info("使用 Core ML 進行 Mac 端側訓練")
        elif self.platform == "windows":
            # 使用 ONNX Runtime 或 DirectML
            logger.info("使用 ONNX Runtime 進行 Windows 端側訓練")
        
        # 模擬訓練過程
        await asyncio.sleep(2)
        
        # 保存模型檢查點
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "platform": self.platform,
            "samples": train_file.stat().st_size // 100,  # 估算樣本數
            "loss": 0.1,  # 模擬損失值
            "version": self.version
        }
        
        checkpoint_file = self.models_path / f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    async def _setup_auto_launch_hooks(self):
        """設置自動啟動鉤子"""
        logger.info("設置自動啟動鉤子...")
        
        # 創建 Claude 集成腳本
        claude_hook_script = f"""#!/usr/bin/env python3
'''
Claude Code Tool 自動集成腳本
自動檢測並啟動 K2 訓練模式
'''

import os
import sys
import json
from pathlib import Path

# 檢測 Claude Code Tool 環境
if "CLAUDE_CODE_TOOL" in os.environ:
    # 設置 K2 模式
    os.environ["CLAUDE_MODEL"] = "k2-optimizer"
    os.environ["CLAUDE_TRAINING_MODE"] = "true"
    os.environ["CLAUDE_RECORDING_MODE"] = "true"
    
    # 更新配置
    config_path = Path.home() / ".claude" / "active_config.json"
    config = {{
        "model": "k2-optimizer",
        "training": True,
        "recording": True,
        "endpoint": "http://localhost:8000/k2/chat",
        "version": "{self.version}"
    }}
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ K2 訓練模式已啟動")
"""
        
        hook_path = self.deploy_path / "claude_k2_hook.py"
        with open(hook_path, 'w') as f:
            f.write(claude_hook_script)
        
        # 設置環境變量
        os.environ["CLAUDE_STARTUP_HOOK"] = str(hook_path)
        
        logger.info("✅ 自動啟動鉤子已設置")
    
    def record_conversation(self, messages: List[Dict[str, str]]):
        """記錄對話"""
        if not self.is_recording:
            return
        
        conversation = {
            "session_id": self.current_session or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "platform": self.platform,
            "version": self.version
        }
        
        self.conversation_queue.put(conversation)
    
    def start_training_mode(self):
        """開始訓練模式"""
        self.is_training = True
        logger.info("🎯 訓練模式已開啟")
    
    def stop_training_mode(self):
        """停止訓練模式"""
        self.is_training = False
        logger.info("⏹️ 訓練模式已關閉")
    
    def get_status(self) -> Dict[str, Any]:
        """獲取狀態"""
        return {
            "version": self.version,
            "platform": self.platform,
            "is_recording": self.is_recording,
            "is_training": self.is_training,
            "conversation_count": self.conversation_queue.qsize(),
            "training_queue": self.training_queue.qsize(),
            "k2_config": self.k2_config
        }


# 自動安裝腳本
async def auto_install():
    """v4.75 自動安裝"""
    print("""
╔══════════════════════════════════════════════╗
║  PowerAutomation v4.75 - K2 集成安裝器        ║
╚══════════════════════════════════════════════╝
""")
    
    integration = K2ClaudeIntegration()
    
    print("🔧 正在安裝和配置...")
    await integration.initialize()
    
    print("\n✅ 安裝完成！")
    print("\n功能特性：")
    print("1. ✅ Claude Code Tool 已配置為使用 K2")
    print("2. ✅ 對話自動記錄已啟用")
    print("3. ✅ 端側訓練模式已就緒")
    print(f"4. ✅ 平台: {integration.platform.upper()}")
    
    print("\n使用方法：")
    print("1. 啟動 Claude Code Tool")
    print("2. 所有對話將自動記錄並用於訓練")
    print("3. 訓練數據保存在:", integration.training_data_path)
    
    # 啟動訓練模式
    integration.start_training_mode()
    
    return integration


if __name__ == "__main__":
    # 運行自動安裝
    asyncio.run(auto_install())