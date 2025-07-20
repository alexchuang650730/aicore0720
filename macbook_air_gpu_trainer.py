#!/usr/bin/env python3
"""
MacBook Air 2025 GPU端側訓練引擎
利用Apple Silicon GPU進行K2+DeepSWE模型本地訓練
"""

import json
import logging
import asyncio
import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import platform
import psutil

# 檢查和安裝依賴
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """訓練配置"""
    model_name: str = "microsoft/DialoGPT-small"  # 輕量級起始模型
    max_length: int = 512
    batch_size: int = 2  # MacBook Air適用的小批次
    learning_rate: float = 5e-5
    num_epochs: int = 3
    save_steps: int = 10
    eval_steps: int = 5
    warmup_steps: int = 5
    gradient_accumulation_steps: int = 4  # 模擬更大的批次
    fp16: bool = True  # 混合精度訓練節省內存
    dataloader_num_workers: int = 2
    use_mps: bool = True  # 使用Apple Silicon GPU

class K2TrainingDataset(Dataset):
    """K2訓練數據集"""
    
    def __init__(self, data_file: str, tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.examples = []
        
        # 加載訓練數據
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    self.examples.append(data)
        
        logger.info(f"加載了 {len(self.examples)} 個訓練樣本")
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        example = self.examples[idx]
        
        # K2格式處理
        if "messages" in example:
            # 構建對話文本
            conversation = ""
            for msg in example["messages"]:
                role = msg["role"]
                content = msg["content"]
                conversation += f"{role}: {content}\n"
            
            text = conversation.strip()
        else:
            # DeepSWE格式處理
            instruction = example.get("instruction", "")
            input_text = example.get("input", "")
            output_text = example.get("output", "")
            text = f"指令: {instruction}\n輸入: {input_text}\n輸出: {output_text}"
        
        # 分詞
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": encoding["input_ids"].squeeze()  # 對於語言模型，標籤就是輸入
        }

class MacBookAirGPUTrainer:
    """MacBook Air GPU訓練器"""
    
    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.device = self._setup_device()
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data" / "integrated_training"
        self.models_dir = self.base_dir / "models" / "local_training"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.training_stats = {
            "start_time": None,
            "end_time": None,
            "total_time": 0,
            "epochs_completed": 0,
            "final_loss": 0.0,
            "best_loss": float('inf'),
            "gpu_utilization": [],
            "memory_usage": []
        }
    
    def _setup_device(self) -> str:
        """設置訓練設備"""
        if not TORCH_AVAILABLE:
            logger.warning("❌ PyTorch未安裝，請運行: pip install torch")
            return "cpu"
        
        # 檢查Apple Silicon GPU支持
        if torch.backends.mps.is_available() and self.config.use_mps:
            device = "mps"
            logger.info("✅ 使用Apple Silicon GPU (MPS)")
        elif torch.cuda.is_available():
            device = "cuda"
            logger.info("✅ 使用NVIDIA GPU")
        else:
            device = "cpu"
            logger.info("⚠️ 使用CPU（建議使用GPU加速）")
        
        return device
    
    def _check_system_requirements(self) -> Dict[str, Any]:
        """檢查系統要求"""
        system_info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "python_version": sys.version,
            "total_memory_gb": psutil.virtual_memory().total / (1024**3),
            "available_memory_gb": psutil.virtual_memory().available / (1024**3),
            "cpu_count": psutil.cpu_count(),
            "torch_available": TORCH_AVAILABLE,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "mps_available": torch.backends.mps.is_available() if TORCH_AVAILABLE else False
        }
        
        logger.info("🖥️ 系統配置:")
        logger.info(f"   平台: {system_info['platform']}")
        logger.info(f"   處理器: {system_info['machine']}")
        logger.info(f"   內存: {system_info['available_memory_gb']:.1f}GB 可用 / {system_info['total_memory_gb']:.1f}GB 總計")
        logger.info(f"   CPU核心: {system_info['cpu_count']}")
        logger.info(f"   MPS支持: {system_info['mps_available']}")
        
        return system_info
    
    def _install_dependencies(self):
        """安裝必要依賴"""
        if not TORCH_AVAILABLE:
            logger.info("📦 安裝PyTorch...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "torch", "torchvision", "torchaudio"
            ])
        
        if not TRANSFORMERS_AVAILABLE:
            logger.info("📦 安裝Transformers...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "transformers", "datasets", "accelerate"
            ])
    
    async def train_k2_model(self, training_data_file: str) -> Dict[str, Any]:
        """訓練K2模型"""
        logger.info("🚀 開始K2模型端側訓練...")
        
        # 檢查系統要求
        system_info = self._check_system_requirements()
        
        if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
            logger.info("📦 安裝缺失的依賴...")
            self._install_dependencies()
            # 重新導入
            global torch, transformers, AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
            import torch
            import transformers
            from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
        
        try:
            self.training_stats["start_time"] = time.time()
            
            # 1. 加載分詞器和模型
            logger.info(f"📥 加載預訓練模型: {self.config.model_name}")
            tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            model = AutoModelForCausalLM.from_pretrained(self.config.model_name)
            
            # 設置padding token
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                model.config.pad_token_id = model.config.eos_token_id
            
            # 移動模型到設備
            model = model.to(self.device)
            logger.info(f"📱 模型已移動到設備: {self.device}")
            
            # 2. 準備數據集
            logger.info("📊 準備訓練數據...")
            dataset = K2TrainingDataset(training_data_file, tokenizer, self.config.max_length)
            
            # 3. 設置訓練參數
            output_dir = self.models_dir / f"k2_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            training_args = TrainingArguments(
                output_dir=str(output_dir),
                overwrite_output_dir=True,
                num_train_epochs=self.config.num_epochs,
                per_device_train_batch_size=self.config.batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                learning_rate=self.config.learning_rate,
                warmup_steps=self.config.warmup_steps,
                logging_steps=5,
                save_steps=self.config.save_steps,
                save_total_limit=2,
                prediction_loss_only=True,
                remove_unused_columns=False,
                dataloader_num_workers=self.config.dataloader_num_workers,
                fp16=self.config.fp16 and self.device != "cpu",
                use_mps_device=self.device == "mps",
                report_to=None,  # 禁用wandb等報告
            )
            
            # 4. 創建訓練器
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=dataset,
                tokenizer=tokenizer,
            )
            
            # 5. 開始訓練
            logger.info("🔥 開始端側訓練...")
            train_result = trainer.train()
            
            # 6. 保存模型
            logger.info("💾 保存訓練後的模型...")
            trainer.save_model()
            tokenizer.save_pretrained(str(output_dir))
            
            self.training_stats["end_time"] = time.time()
            self.training_stats["total_time"] = self.training_stats["end_time"] - self.training_stats["start_time"]
            self.training_stats["epochs_completed"] = self.config.num_epochs
            self.training_stats["final_loss"] = train_result.training_loss
            
            # 7. 生成訓練報告
            await self._generate_training_report(output_dir, system_info, train_result)
            
            logger.info("✅ K2模型訓練完成！")
            return {
                "success": True,
                "model_path": str(output_dir),
                "training_stats": self.training_stats,
                "system_info": system_info
            }
            
        except Exception as e:
            logger.error(f"❌ 訓練失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "training_stats": self.training_stats
            }
    
    async def test_inference(self, model_path: str, test_prompt: str) -> Dict[str, Any]:
        """測試推理"""
        try:
            logger.info("🎯 測試模型推理...")
            
            # 加載訓練好的模型
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            model = model.to(self.device)
            model.eval()
            
            # 編碼輸入
            inputs = tokenizer.encode(test_prompt, return_tensors="pt").to(self.device)
            
            # 生成回應
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    num_return_sequences=1,
                    pad_token_id=tokenizer.eos_token_id,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
            
            inference_time = time.time() - start_time
            
            # 解碼輸出
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = generated_text[len(test_prompt):].strip()
            
            logger.info(f"✅ 推理完成，耗時: {inference_time:.3f}秒")
            
            return {
                "success": True,
                "input": test_prompt,
                "output": response,
                "inference_time": inference_time,
                "device_used": self.device
            }
            
        except Exception as e:
            logger.error(f"❌ 推理測試失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_training_report(self, model_path: Path, system_info: Dict, train_result):
        """生成訓練報告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.base_dir / f"macbook_air_training_report_{timestamp}.md"
        
        report_content = f"""# MacBook Air GPU端側訓練報告
生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 🖥️ 系統配置
- 平台: {system_info['platform']}
- 處理器: {system_info['machine']}
- 總內存: {system_info['total_memory_gb']:.1f}GB
- 可用內存: {system_info['available_memory_gb']:.1f}GB
- CPU核心: {system_info['cpu_count']}
- 訓練設備: {self.device}
- MPS支持: {system_info['mps_available']}

## 🤖 模型配置
- 基礎模型: {self.config.model_name}
- 最大序列長度: {self.config.max_length}
- 批次大小: {self.config.batch_size}
- 學習率: {self.config.learning_rate}
- 訓練輪數: {self.config.num_epochs}
- 混合精度: {self.config.fp16}

## 📊 訓練結果
- 訓練時間: {self.training_stats['total_time']:.2f}秒 ({self.training_stats['total_time']/60:.1f}分鐘)
- 完成輪數: {self.training_stats['epochs_completed']}
- 最終Loss: {self.training_stats['final_loss']:.4f}
- 模型保存路徑: {model_path}

## 🎯 端側訓練優勢
- ✅ 數據隱私保護
- ✅ 無需網絡連接
- ✅ 自定義模型調優
- ✅ Apple Silicon GPU加速
- ✅ 實時訓練反饋

## 📈 性能分析
- 設備利用率: {'GPU' if self.device == 'mps' else 'CPU'}加速
- 內存效率: 混合精度訓練
- 訓練速度: 小批次 + 梯度累積
- 模型大小: 適合邊緣設備部署

## 🚀 後續改進
1. 增加更多訓練數據（511個replay處理完成後）
2. 實驗不同的超參數配置
3. 添加驗證集評估
4. 實現增量訓練
5. 優化推理速度

## ✅ 結論
MacBook Air 2025 GPU端側訓練成功！
模型已準備好進行實際推理任務。
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"📋 訓練報告已生成: {report_file}")

async def main():
    """主函數"""
    logger.info("🚀 MacBook Air GPU端側訓練引擎啟動...")
    
    # 檢查訓練數據
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data" / "integrated_training"
    
    # 查找K2訓練數據
    k2_files = list(data_dir.glob("k2_integrated_training_*.jsonl"))
    if not k2_files:
        logger.error("❌ 找不到K2訓練數據文件")
        return
    
    training_file = k2_files[0]
    logger.info(f"📊 使用訓練數據: {training_file}")
    
    # 創建訓練器
    config = TrainingConfig(
        batch_size=1,  # 小批次適合MacBook Air
        num_epochs=2,  # 快速測試
        max_length=256  # 減少內存使用
    )
    
    trainer = MacBookAirGPUTrainer(config)
    
    # 開始訓練
    result = await trainer.train_k2_model(str(training_file))
    
    if result["success"]:
        print("\n🎉 端側訓練成功！")
        print(f"⏱️ 訓練時間: {result['training_stats']['total_time']:.2f}秒")
        print(f"📱 使用設備: {trainer.device}")
        print(f"💾 模型路徑: {result['model_path']}")
        
        # 測試推理
        test_prompt = "user: 幫我創建一個Python函數\nassistant:"
        inference_result = await trainer.test_inference(
            result['model_path'], 
            test_prompt
        )
        
        if inference_result["success"]:
            print(f"\n🎯 推理測試成功！")
            print(f"輸入: {inference_result['input']}")
            print(f"輸出: {inference_result['output'][:100]}...")
            print(f"推理時間: {inference_result['inference_time']:.3f}秒")
        else:
            print(f"❌ 推理測試失敗: {inference_result['error']}")
    else:
        print(f"❌ 訓練失敗: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())