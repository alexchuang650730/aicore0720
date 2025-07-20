#!/usr/bin/env python3
"""
真實的K2+DeepSWE+MemoryRAG端到端訓練腳本
使用MLX框架在Mac上進行GPU加速訓練
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Tuple

import mlx
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from tqdm import tqdm

# 導入我們的模型和數據加載器
from k2_deepswe_memoryrag_engine import UnifiedK2DeepSWEMemoryRAGModel
from k2_deepswe_memoryrag_engine_part3 import DataLoader, TrainingLoop, EvaluationMetrics, ModelConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProgressiveTrainer:
    """漸進式訓練策略，逐步提升模型性能"""
    
    def __init__(self, model_config: ModelConfig, data_path: str):
        self.config = model_config
        self.data_path = Path(data_path)
        self.model = UnifiedK2DeepSWEMemoryRAGModel(self.config)
        self.optimizer = optim.AdamW(learning_rate=1e-4)
        self.training_loop = TrainingLoop(self.model, self.optimizer, self.config)
        self.eval_metrics = EvaluationMetrics()
        
        # 載入訓練數據
        self.data_loader = DataLoader(
            data_path=data_path,
            batch_size=4,  # 小批次以適應Mac內存
            max_seq_len=self.config.max_seq_len
        )
        
        # 訓練階段定義
        self.training_phases = [
            {
                "name": "Phase 1: Language Modeling",
                "epochs": 5,
                "focus": "language",
                "lr": 1e-4
            },
            {
                "name": "Phase 2: Tool Calling",
                "epochs": 5,
                "focus": "tools",
                "lr": 5e-5
            },
            {
                "name": "Phase 3: Memory Integration",
                "epochs": 5,
                "focus": "memory",
                "lr": 3e-5
            },
            {
                "name": "Phase 4: Full Fine-tuning",
                "epochs": 10,
                "focus": "all",
                "lr": 1e-5
            }
        ]
        
    def train(self):
        """執行漸進式訓練"""
        logger.info("🚀 開始K2+DeepSWE+MemoryRAG漸進式訓練")
        
        initial_similarity = self._evaluate_similarity()
        logger.info(f"📊 初始語義相似度: {initial_similarity:.1%}")
        
        for phase_idx, phase in enumerate(self.training_phases):
            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 {phase['name']}")
            logger.info(f"{'='*60}")
            
            # 調整學習率
            self.optimizer.learning_rate = phase['lr']
            
            # 執行該階段的訓練
            self._train_phase(phase)
            
            # 評估階段結果
            metrics = self._evaluate_phase(phase_idx)
            self._log_phase_results(phase, metrics)
            
            # 保存檢查點
            self._save_checkpoint(phase_idx, metrics)
            
        # 最終評估
        final_similarity = self._evaluate_similarity()
        improvement = final_similarity - initial_similarity
        
        logger.info(f"\n🎉 訓練完成！")
        logger.info(f"📈 最終語義相似度: {final_similarity:.1%}")
        logger.info(f"📊 總體提升: +{improvement:.1%}")
        
    def _train_phase(self, phase: Dict):
        """訓練單個階段"""
        focus = phase['focus']
        epochs = phase['epochs']
        
        for epoch in range(epochs):
            logger.info(f"\n📅 Epoch {epoch+1}/{epochs}")
            
            # 重置epoch指標
            epoch_loss = 0
            epoch_tool_acc = 0
            batch_count = 0
            
            # 訓練進度條
            pbar = tqdm(self.data_loader, desc=f"Training {focus}")
            
            for batch in pbar:
                # 根據階段焦點調整損失權重
                if focus == "language":
                    weights = {"lm": 1.0, "tool": 0.1, "memory": 0.1}
                elif focus == "tools":
                    weights = {"lm": 0.3, "tool": 1.0, "memory": 0.2}
                elif focus == "memory":
                    weights = {"lm": 0.3, "tool": 0.3, "memory": 1.0}
                else:  # all
                    weights = {"lm": 0.4, "tool": 0.3, "memory": 0.3}
                
                # 執行訓練步驟
                loss, metrics = self.training_loop.train_step(batch, weights)
                
                # 累積指標
                epoch_loss += loss
                epoch_tool_acc += metrics.get('tool_accuracy', 0)
                batch_count += 1
                
                # 更新進度條
                pbar.set_postfix({
                    'loss': f'{loss:.4f}',
                    'tool_acc': f'{metrics.get("tool_accuracy", 0):.2%}'
                })
            
            # 記錄epoch結果
            avg_loss = epoch_loss / batch_count
            avg_tool_acc = epoch_tool_acc / batch_count
            
            logger.info(f"📊 Epoch {epoch+1} - Loss: {avg_loss:.4f}, Tool Acc: {avg_tool_acc:.2%}")
            
    def _evaluate_similarity(self) -> float:
        """評估與Claude Code的語義相似度"""
        logger.info("🧪 評估語義相似度...")
        
        # 使用驗證集評估
        similarities = []
        
        for batch in tqdm(self.data_loader.get_validation_loader(), desc="Evaluating"):
            # 生成模型輸出
            outputs = self.model.forward(
                input_ids=batch['input_ids'],
                attention_mask=batch.get('attention_mask'),
                memory_indices=batch.get('memory_indices'),
                tool_labels=batch.get('tool_labels')
            )
            
            # 計算相似度
            sim = self.eval_metrics.compute_similarity(
                outputs['lm_logits'],
                batch['target_ids']
            )
            similarities.append(sim)
        
        return np.mean(similarities)
    
    def _evaluate_phase(self, phase_idx: int) -> Dict:
        """評估訓練階段的結果"""
        logger.info("📊 評估階段性能...")
        
        metrics = {
            'phase': phase_idx,
            'similarity': self._evaluate_similarity(),
            'tool_accuracy': self._evaluate_tool_accuracy(),
            'memory_recall': self._evaluate_memory_recall()
        }
        
        return metrics
    
    def _evaluate_tool_accuracy(self) -> float:
        """評估工具調用準確率"""
        correct = 0
        total = 0
        
        for batch in self.data_loader.get_validation_loader():
            if 'tool_labels' not in batch:
                continue
                
            outputs = self.model.forward(
                input_ids=batch['input_ids'],
                attention_mask=batch.get('attention_mask')
            )
            
            predictions = mx.argmax(outputs['tool_logits'], axis=-1)
            correct += mx.sum(predictions == batch['tool_labels'])
            total += batch['tool_labels'].shape[0]
        
        return float(correct) / total if total > 0 else 0.0
    
    def _evaluate_memory_recall(self) -> float:
        """評估記憶檢索召回率"""
        recalls = []
        
        for batch in self.data_loader.get_validation_loader():
            if 'memory_indices' not in batch:
                continue
                
            outputs = self.model.forward(
                input_ids=batch['input_ids'],
                attention_mask=batch.get('attention_mask'),
                memory_indices=batch['memory_indices']
            )
            
            # 計算記憶檢索的相關性
            memory_scores = outputs.get('memory_scores', None)
            if memory_scores is not None:
                recall = self.eval_metrics.compute_recall(
                    memory_scores,
                    batch['memory_indices']
                )
                recalls.append(recall)
        
        return np.mean(recalls) if recalls else 0.0
    
    def _log_phase_results(self, phase: Dict, metrics: Dict):
        """記錄階段結果"""
        logger.info(f"\n📊 {phase['name']} 結果:")
        logger.info(f"  - 語義相似度: {metrics['similarity']:.1%}")
        logger.info(f"  - 工具準確率: {metrics['tool_accuracy']:.1%}")
        logger.info(f"  - 記憶召回率: {metrics['memory_recall']:.1%}")
    
    def _save_checkpoint(self, phase_idx: int, metrics: Dict):
        """保存訓練檢查點"""
        checkpoint_path = self.data_path / f"checkpoint_phase_{phase_idx}.npz"
        
        # 保存模型權重和指標
        mx.save(str(checkpoint_path), {
            'model_weights': self.model.state_dict(),
            'optimizer_state': self.optimizer.state,
            'metrics': metrics,
            'phase': phase_idx
        })
        
        logger.info(f"💾 檢查點已保存: {checkpoint_path}")


def main():
    parser = argparse.ArgumentParser(description="訓練K2+DeepSWE+MemoryRAG模型")
    parser.add_argument(
        "--data_path",
        type=str,
        default="data/training_data",
        help="訓練數據路徑"
    )
    parser.add_argument(
        "--vocab_size",
        type=int,
        default=50000,
        help="詞彙表大小"
    )
    parser.add_argument(
        "--model_dim",
        type=int,
        default=768,
        help="模型維度"
    )
    parser.add_argument(
        "--num_heads",
        type=int,
        default=12,
        help="注意力頭數"
    )
    parser.add_argument(
        "--num_layers",
        type=int,
        default=12,
        help="Transformer層數"
    )
    parser.add_argument(
        "--memory_size",
        type=int,
        default=1000,
        help="記憶庫大小"
    )
    
    args = parser.parse_args()
    
    # 創建模型配置
    config = ModelConfig(
        vocab_size=args.vocab_size,
        model_dim=args.model_dim,
        num_heads=args.num_heads,
        num_layers=args.num_layers,
        num_tools=20,
        memory_size=args.memory_size,
        max_seq_len=512
    )
    
    # 初始化訓練器
    trainer = ProgressiveTrainer(config, args.data_path)
    
    # 開始訓練
    start_time = time.time()
    trainer.train()
    
    elapsed_time = time.time() - start_time
    logger.info(f"\n⏱️ 總訓練時間: {elapsed_time/3600:.2f} 小時")


if __name__ == "__main__":
    main()