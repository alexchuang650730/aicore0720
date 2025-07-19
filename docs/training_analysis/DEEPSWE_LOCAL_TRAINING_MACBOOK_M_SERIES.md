# DeepSWE 本地訓練方案 - MacBook M 系列

## 🖥️ 硬件要求

### MacBook Pro 2025 預期配置
- **芯片**: M4 Pro/Max (預計 40-60 GPU cores)
- **統一內存**: 64GB-128GB
- **Neural Engine**: 32-40 cores
- **存儲**: 2TB+ SSD

## 🚀 訓練策略

### 1. **模型量化和優化**

由於 DeepSWE 基於 32B 參數的模型，需要針對 MacBook 進行優化：

```python
# core/training/macbook_optimizer.py
import torch
import mlx  # Apple 的機器學習框架
from transformers import AutoModelForCausalLM, AutoTokenizer

class MacBookDeepSWETrainer:
    """針對 MacBook M 系列優化的 DeepSWE 訓練器"""
    
    def __init__(self):
        self.device = "mps"  # Metal Performance Shaders
        self.use_mlx = True  # 使用 Apple MLX 框架
        
    def prepare_model_for_macbook(self):
        """準備適合 MacBook 的模型"""
        
        # 1. 使用 4-bit 量化
        from transformers import BitsAndBytesConfig
        
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        # 2. 加載量化模型
        model = AutoModelForCausalLM.from_pretrained(
            "agentica-org/DeepSWE-Preview",
            quantization_config=quantization_config,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        return model
    
    def setup_lora_training(self):
        """設置 LoRA 微調（適合有限內存）"""
        from peft import LoraConfig, get_peft_model
        
        lora_config = LoraConfig(
            r=16,  # LoRA rank
            lora_alpha=32,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
            lora_dropout=0.1,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        return lora_config
```

### 2. **使用 Apple MLX 框架**

```python
# core/training/mlx_trainer.py
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

class MLXDeepSWETrainer:
    """使用 Apple MLX 的高效訓練器"""
    
    def __init__(self):
        self.model = None
        self.optimizer = None
        
    def load_model_mlx(self):
        """使用 MLX 加載模型"""
        # MLX 支持高效的統一內存訪問
        # 特別適合 M 系列芯片
        
        # 將 PyTorch 模型轉換為 MLX
        from mlx_lm import load, generate
        
        model, tokenizer = load("agentica-org/DeepSWE-Preview")
        return model, tokenizer
    
    def train_on_macbook(self, dataset):
        """在 MacBook 上訓練"""
        # 使用 MLX 的優化器
        self.optimizer = optim.AdamW(
            learning_rate=1e-5,
            weight_decay=0.01
        )
        
        # 訓練循環
        for epoch in range(num_epochs):
            for batch in dataset:
                # MLX 自動處理統一內存
                loss = self.model.loss(batch)
                loss.backward()
                self.optimizer.step()
```

### 3. **數據集準備**

```python
# core/training/dataset_preparation.py
class CodeDatasetForMacBook:
    """針對 MacBook 優化的數據集"""
    
    def __init__(self, max_length=512):
        self.max_length = max_length  # 限制序列長度以節省內存
        
    def prepare_powerautomation_dataset(self):
        """準備 PowerAutomation 特定的訓練數據"""
        
        dataset = []
        
        # 1. 收集我們的代碼庫
        code_examples = self._collect_codebase_examples()
        
        # 2. 添加 K2 優化模式
        k2_patterns = self._extract_k2_optimization_patterns()
        
        # 3. 創建訓練樣本
        for example in code_examples:
            dataset.append({
                "input": self._create_deepswe_prompt(example),
                "output": example["optimized_code"],
                "task_type": example["type"]
            })
        
        return dataset
    
    def _create_deepswe_prompt(self, example):
        """創建 DeepSWE 風格的提示"""
        return f"""<thinking>
任務：{example['task']}
要求：{example['requirements']}
約束：{example['constraints']}
</thinking>

請生成滿足以上要求的代碼。
"""
```

### 4. **高效訓練腳本**

```python
#!/usr/bin/env python3
# train_deepswe_macbook.py

import os
import time
import argparse
from pathlib import Path

def main():
    """主訓練函數"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-size", default="7B", help="使用的模型大小")
    parser.add_argument("--use-mlx", action="store_true", help="使用 MLX 框架")
    parser.add_argument("--batch-size", type=int, default=1, help="批次大小")
    parser.add_argument("--gradient-accumulation", type=int, default=8)
    args = parser.parse_args()
    
    print(f"""
    🎯 DeepSWE MacBook 訓練配置
    ============================
    模型大小: {args.model_size}
    框架: {'MLX' if args.use_mlx else 'PyTorch MPS'}
    批次大小: {args.batch_size}
    梯度累積: {args.gradient_accumulation}
    預計內存使用: ~{estimate_memory_usage(args.model_size)}GB
    """)
    
    # 1. 檢查系統
    check_system_requirements()
    
    # 2. 準備模型
    if args.use_mlx:
        trainer = MLXDeepSWETrainer()
    else:
        trainer = MacBookDeepSWETrainer()
    
    # 3. 準備數據
    dataset = prepare_dataset()
    
    # 4. 開始訓練
    trainer.train(dataset, args)

def check_system_requirements():
    """檢查系統要求"""
    import subprocess
    
    # 檢查 macOS 版本
    macos_version = subprocess.check_output(['sw_vers', '-productVersion']).decode().strip()
    print(f"✅ macOS 版本: {macos_version}")
    
    # 檢查可用內存
    import psutil
    memory = psutil.virtual_memory()
    print(f"✅ 可用內存: {memory.available / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB")
    
    # 檢查 GPU
    try:
        import torch
        if torch.backends.mps.is_available():
            print("✅ Metal Performance Shaders (MPS) 可用")
    except:
        pass

def estimate_memory_usage(model_size):
    """估算內存使用"""
    size_map = {
        "7B": 14,   # 4-bit 量化
        "13B": 26,  # 4-bit 量化
        "32B": 64   # 4-bit 量化
    }
    return size_map.get(model_size, 32)

if __name__ == "__main__":
    main()
```

## 📊 訓練配置建議

### MacBook Pro M4 Max (預計配置)
```yaml
model_config:
  base_model: "deepseek-ai/deepseek-coder-7b-base"  # 先用小模型測試
  quantization: "4bit"
  use_lora: true
  lora_rank: 16

training_config:
  batch_size: 1
  gradient_accumulation_steps: 8
  learning_rate: 1e-5
  num_epochs: 3
  max_length: 512
  
optimization:
  use_mlx: true  # Apple 優化框架
  use_unified_memory: true
  gradient_checkpointing: true
  
data:
  dataset_size: 10000  # 開始時用小數據集
  focus_areas:
    - k2_optimization_patterns
    - powerautomation_workflows
    - mcp_integration_examples
```

## 🔧 安裝步驟

```bash
# 1. 安裝 MLX (Apple 的 ML 框架)
pip install mlx mlx-lm

# 2. 安裝訓練依賴
pip install transformers peft bitsandbytes accelerate

# 3. 準備訓練環境
export PYTORCH_ENABLE_MPS_FALLBACK=1
export TOKENIZERS_PARALLELISM=false

# 4. 開始訓練
python train_deepswe_macbook.py \
  --model-size 7B \
  --use-mlx \
  --batch-size 1 \
  --gradient-accumulation 8
```

## 📈 訓練監控

```python
# core/training/monitor.py
class TrainingMonitor:
    """訓練監控器"""
    
    def __init__(self):
        self.metrics = []
        
    def log_metrics(self, step, loss, learning_rate, memory_used):
        """記錄訓練指標"""
        import psutil
        
        metrics = {
            "step": step,
            "loss": loss,
            "learning_rate": learning_rate,
            "memory_gb": psutil.Process().memory_info().rss / (1024**3),
            "gpu_memory_gb": self._get_mps_memory()
        }
        
        self.metrics.append(metrics)
        
        # 實時顯示
        print(f"Step {step}: Loss={loss:.4f}, Mem={metrics['memory_gb']:.1f}GB")
```

## 🎯 預期成果

### 第一週：基礎訓練
- 使用 7B 模型進行概念驗證
- 訓練 K2 優化模式
- 驗證 MacBook 性能

### 第二週：擴展訓練
- 嘗試更大的模型（如果內存允許）
- 增加 PowerAutomation 特定數據
- 優化訓練效率

### 第三週：部署測試
- 導出優化後的模型
- 集成到 K2 優化器
- A/B 測試效果

## 💡 優化建議

1. **使用 MLX 而非 PyTorch**
   - MLX 專為 Apple Silicon 優化
   - 更好的統一內存利用
   - 更快的訓練速度

2. **分階段訓練**
   - 先用小模型驗證流程
   - 逐步增加模型大小
   - 根據效果調整策略

3. **專注於提示優化**
   - 不需要訓練完整模型
   - 只需要學習優化模式
   - 可以用 LoRA 微調

這個方案充分利用了 MacBook M 系列的優勢，同時保持訓練的可行性和效率。