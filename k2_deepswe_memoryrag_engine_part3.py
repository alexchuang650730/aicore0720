#!/usr/bin/env python3
"""
K2+DeepSWE+MemoryRAG 訓練循環、數據加載器和評估指標
Part 3 - 訓練相關組件
"""

import json
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import random
from collections import defaultdict

import mlx
import mlx.core as mx
import mlx.nn as nn

logger = logging.getLogger(__name__)


class DataLoader:
    """訓練數據加載器"""
    
    def __init__(self, data_path: str, batch_size: int = 4, max_seq_len: int = 512):
        self.data_path = Path(data_path)
        self.batch_size = batch_size
        self.max_seq_len = max_seq_len
        
        # 加載數據
        self.train_data = self._load_data("train.json")
        self.val_data = self._load_data("val.json")
        
        # 詞彙表（簡化版）
        self.vocab = self._build_vocab()
        self.vocab_size = len(self.vocab)
        
        logger.info(f"📊 加載了 {len(self.train_data)} 個訓練樣本, {len(self.val_data)} 個驗證樣本")
        logger.info(f"📝 詞彙表大小: {self.vocab_size}")
        
    def _load_data(self, filename: str) -> List[Dict]:
        """加載數據文件"""
        file_path = self.data_path / filename
        if not file_path.exists():
            logger.warning(f"找不到數據文件: {file_path}")
            return []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_vocab(self) -> Dict[str, int]:
        """構建詞彙表"""
        vocab = {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3}
        vocab_idx = 4
        
        # 從所有數據中提取token
        all_texts = []
        for sample in self.train_data + self.val_data:
            all_texts.append(sample.get("input", ""))
            all_texts.append(sample.get("output", ""))
        
        # 簡單的字符級tokenization
        for text in all_texts:
            for char in text:
                if char not in vocab:
                    vocab[char] = vocab_idx
                    vocab_idx += 1
        
        return vocab
    
    def tokenize(self, text: str) -> List[int]:
        """將文本轉換為token ID"""
        tokens = [self.vocab.get(char, self.vocab["<unk>"]) for char in text]
        
        # 截斷或填充
        if len(tokens) > self.max_seq_len - 2:
            tokens = tokens[:self.max_seq_len - 2]
        
        # 添加開始和結束標記
        tokens = [self.vocab["<bos>"]] + tokens + [self.vocab["<eos>"]]
        
        # 填充
        while len(tokens) < self.max_seq_len:
            tokens.append(self.vocab["<pad>"])
        
        return tokens
    
    def __iter__(self):
        """迭代訓練批次"""
        # 打亂數據
        indices = list(range(len(self.train_data)))
        random.shuffle(indices)
        
        # 生成批次
        for i in range(0, len(indices), self.batch_size):
            batch_indices = indices[i:i + self.batch_size]
            batch = []
            
            for idx in batch_indices:
                sample = self.train_data[idx]
                
                # Tokenize輸入輸出
                input_ids = self.tokenize(sample["input"])
                target_ids = self.tokenize(sample["output"])
                
                # 提取工具標籤
                tool_labels = sample.get("tool_labels", [])
                if tool_labels:
                    tool_label = tool_labels[0]  # 簡化：只取第一個工具
                else:
                    tool_label = -1  # 無工具調用
                
                # 創建記憶索引（模擬）
                memory_indices = list(range(5))  # 簡化：固定5個記憶
                
                batch_sample = {
                    "input_ids": input_ids,
                    "target_ids": target_ids,
                    "tool_labels": tool_label,
                    "memory_indices": memory_indices,
                    "has_context": len(sample.get("context", [])) > 0
                }
                
                batch.append(batch_sample)
            
            # 轉換為MLX數組
            yield self._collate_batch(batch)
    
    def _collate_batch(self, batch: List[Dict]) -> Dict:
        """整理批次數據"""
        # 堆疊數據
        input_ids = mx.array([b["input_ids"] for b in batch])
        target_ids = mx.array([b["target_ids"] for b in batch])
        tool_labels = mx.array([b["tool_labels"] for b in batch])
        memory_indices = mx.array([b["memory_indices"] for b in batch])
        
        # 創建注意力掩碼
        attention_mask = (input_ids != self.vocab["<pad>"]).astype(mx.float32)
        
        return {
            "input_ids": input_ids,
            "target_ids": target_ids,
            "attention_mask": attention_mask,
            "tool_labels": tool_labels,
            "memory_indices": memory_indices
        }
    
    def get_validation_loader(self):
        """獲取驗證數據加載器"""
        for i in range(0, len(self.val_data), self.batch_size):
            batch = []
            
            for j in range(i, min(i + self.batch_size, len(self.val_data))):
                sample = self.val_data[j]
                
                input_ids = self.tokenize(sample["input"])
                target_ids = self.tokenize(sample["output"])
                tool_labels = sample.get("tool_labels", [])
                
                batch_sample = {
                    "input_ids": input_ids,
                    "target_ids": target_ids,
                    "tool_labels": tool_labels[0] if tool_labels else -1,
                    "memory_indices": list(range(5))
                }
                
                batch.append(batch_sample)
            
            yield self._collate_batch(batch)


class TrainingLoop:
    """訓練循環實現"""
    
    def __init__(self, model, optimizer, config):
        self.model = model
        self.optimizer = optimizer
        self.config = config
        
        # 損失函數
        self.ce_loss = nn.losses.cross_entropy
        
        # 訓練統計
        self.step = 0
        self.total_loss = 0
        
    def train_step(self, batch: Dict, weights: Dict) -> Tuple[float, Dict]:
        """執行單個訓練步驟"""
        
        def loss_fn(model):
            # 前向傳播
            outputs = model.forward(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"]
            )
            
            # 計算語言模型損失
            lm_loss = self.ce_loss(
                outputs["lm_logits"].reshape(-1, outputs["lm_logits"].shape[-1]),
                batch["target_ids"].reshape(-1)
            )
            
            # 計算工具預測損失
            valid_tools = batch["tool_labels"] >= 0
            if mx.any(valid_tools):
                tool_loss = self.ce_loss(
                    outputs["tool_logits"][valid_tools],
                    batch["tool_labels"][valid_tools]
                )
            else:
                tool_loss = mx.array(0.0)
            
            # 計算記憶損失（簡化版）
            memory_loss = mx.mean(mx.square(outputs["retrieved_memories"]))
            
            # 加權總損失
            total_loss = (
                weights["lm"] * lm_loss +
                weights["tool"] * tool_loss +
                weights["memory"] * memory_loss
            )
            
            return total_loss, (lm_loss, tool_loss, memory_loss, outputs)
        
        # 計算梯度並更新
        (loss, (lm_loss, tool_loss, memory_loss, outputs)), grads = mx.value_and_grad(
            loss_fn, has_aux=True
        )(self.model)
        
        # 梯度裁剪
        grads = mx.clip(grads, -self.config.max_grad_norm, self.config.max_grad_norm)
        
        # 更新參數
        self.optimizer.update(self.model, grads)
        
        # 計算指標
        with mx.no_grad():
            # 工具準確率
            if mx.any(batch["tool_labels"] >= 0):
                tool_preds = mx.argmax(outputs["tool_logits"], axis=-1)
                tool_acc = mx.mean(
                    (tool_preds == batch["tool_labels"])[batch["tool_labels"] >= 0]
                )
            else:
                tool_acc = mx.array(0.0)
        
        self.step += 1
        self.total_loss += float(loss)
        
        metrics = {
            "lm_loss": float(lm_loss),
            "tool_loss": float(tool_loss),
            "memory_loss": float(memory_loss),
            "tool_accuracy": float(tool_acc)
        }
        
        return float(loss), metrics


class EvaluationMetrics:
    """評估指標計算"""
    
    def compute_similarity(self, pred_logits, target_ids):
        """計算預測與目標的語義相似度"""
        # 獲取預測token
        pred_ids = mx.argmax(pred_logits, axis=-1)
        
        # 計算準確率作為相似度的代理
        mask = target_ids != 0  # 忽略padding
        correct = (pred_ids == target_ids) & mask
        accuracy = mx.sum(correct) / mx.sum(mask)
        
        return float(accuracy)
    
    def compute_recall(self, memory_scores, target_indices):
        """計算記憶檢索召回率"""
        # 獲取top-k預測
        k = min(5, memory_scores.shape[-1])
        top_k_indices = mx.argsort(-memory_scores, axis=-1)[:, :k]
        
        # 計算召回率
        recalls = []
        for i in range(len(target_indices)):
            target_set = set(int(idx) for idx in target_indices[i])
            pred_set = set(int(idx) for idx in top_k_indices[i])
            
            if len(target_set) > 0:
                recall = len(target_set & pred_set) / len(target_set)
                recalls.append(recall)
        
        return np.mean(recalls) if recalls else 0.0


class ModelConfig:
    """模型配置類"""
    
    def __init__(
        self,
        vocab_size: int = 50000,
        model_dim: int = 768,
        num_heads: int = 12,
        num_layers: int = 12,
        num_k2_layers: int = 6,
        num_deepswe_layers: int = 6,
        mlp_dims: int = 3072,
        max_seq_len: int = 512,
        dropout_rate: float = 0.1,
        memory_dim: int = 256,
        num_memories: int = 1000,
        attention_heads: int = 8,
        num_tools: int = 20,
        memory_size: int = 1000,
        max_grad_norm: float = 1.0
    ):
        self.vocab_size = vocab_size
        self.model_dim = model_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.num_k2_layers = num_k2_layers
        self.num_deepswe_layers = num_deepswe_layers
        self.mlp_dims = mlp_dims
        self.max_seq_len = max_seq_len
        self.dropout_rate = dropout_rate
        self.memory_dim = memory_dim
        self.num_memories = num_memories
        self.attention_heads = attention_heads
        self.num_tools = num_tools
        self.memory_size = memory_size
        self.max_grad_norm = max_grad_norm