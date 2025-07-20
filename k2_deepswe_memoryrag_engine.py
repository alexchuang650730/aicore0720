#!/usr/bin/env python3
"""
K2+DeepSWE+MemoryRAG 端到端訓練引擎
整合K2對話能力、DeepSWE程式理解和MemoryRAG記憶檢索
針對MacBook Air M系列晶片優化
"""

import json
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import hashlib
import re
from collections import defaultdict

# Apple Silicon優化
import mlx
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryRAGModule(nn.Module):
    """記憶檢索增強生成模組"""
    
    def __init__(self, config):
        super().__init__()
        self.memory_dim = config.memory_dim
        self.num_memories = config.num_memories
        self.attention_heads = config.attention_heads
        
        # 記憶庫（可訓練的參數）
        self.memory_bank = nn.Embedding(self.num_memories, self.memory_dim)
        
        # 記憶編碼器
        self.memory_encoder = nn.Sequential(
            nn.Linear(config.model_dim, self.memory_dim),
            nn.ReLU(),
            nn.LayerNorm(self.memory_dim)
        )
        
        # 檢索注意力機制
        self.retrieval_attention = nn.MultiHeadAttention(
            dims=self.memory_dim,
            num_heads=self.attention_heads,
            query_input_dims=self.memory_dim,
            key_input_dims=self.memory_dim,
            value_input_dims=self.memory_dim,
            value_dims=self.memory_dim,
            value_output_dims=self.memory_dim
        )
        
        # 記憶融合層
        self.memory_fusion = nn.Sequential(
            nn.Linear(config.model_dim + self.memory_dim, config.model_dim),
            nn.ReLU(),
            nn.LayerNorm(config.model_dim)
        )
        
        # 記憶更新門控
        self.update_gate = nn.Sequential(
            nn.Linear(self.memory_dim * 2, self.memory_dim),
            nn.Sigmoid()
        )
    
    def retrieve_memories(self, query, top_k=5):
        """檢索相關記憶"""
        # 編碼查詢
        query_encoded = self.memory_encoder(query)
        
        # 獲取所有記憶
        all_memories = self.memory_bank.weight
        
        # 計算相似度分數
        scores = mx.matmul(query_encoded, all_memories.T)
        scores = scores / mx.sqrt(mx.array(self.memory_dim, dtype=mx.float32))
        
        # 獲取top-k記憶
        top_k_indices = mx.argpartition(-scores, kth=top_k, axis=-1)[:, :top_k]
        top_k_memories = all_memories[top_k_indices]
        
        # 使用注意力機制融合記憶
        attended_memory, _ = self.retrieval_attention(
            query_encoded.unsqueeze(1),
            top_k_memories,
            top_k_memories
        )
        
        return attended_memory.squeeze(1)
    
    def update_memory(self, memory_idx, new_info, learning_rate=0.1):
        """更新特定記憶"""
        old_memory = self.memory_bank.weight[memory_idx]
        new_memory_encoded = self.memory_encoder(new_info)
        
        # 計算更新門控
        gate = self.update_gate(mx.concatenate([old_memory, new_memory_encoded], axis=-1))
        
        # 更新記憶
        updated_memory = gate * new_memory_encoded + (1 - gate) * old_memory
        self.memory_bank.weight[memory_idx] = updated_memory
        
        return updated_memory
    
    def forward(self, hidden_states):
        """前向傳播"""
        # 檢索相關記憶
        retrieved_memories = self.retrieve_memories(hidden_states)
        
        # 融合記憶和隱藏狀態
        fused_states = self.memory_fusion(
            mx.concatenate([hidden_states, retrieved_memories], axis=-1)
        )
        
        return fused_states, retrieved_memories

class UnifiedK2DeepSWEMemoryRAGModel(nn.Module):
    """K2+DeepSWE+MemoryRAG統一模型"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Token嵌入
        self.token_embedding = nn.Embedding(config.vocab_size, config.model_dim)
        self.position_embedding = nn.Embedding(config.max_seq_len, config.model_dim)
        
        # K2對話理解層
        self.k2_layers = []
        for _ in range(config.num_k2_layers):
            self.k2_layers.append(nn.TransformerEncoderLayer(
                dims=config.model_dim,
                num_heads=config.num_heads,
                mlp_dims=config.mlp_dims
            ))
        
        # DeepSWE程式理解層
        self.deepswe_layers = []
        for _ in range(config.num_deepswe_layers):
            self.deepswe_layers.append(nn.TransformerEncoderLayer(
                dims=config.model_dim,
                num_heads=config.num_heads,
                mlp_dims=config.mlp_dims
            ))
        
        # MemoryRAG記憶模組
        self.memory_rag = MemoryRAGModule(config)
        
        # 工具預測頭（20個MCP工具）
        self.tool_prediction = nn.Sequential(
            nn.Linear(config.model_dim, config.mlp_dims),
            nn.ReLU(),
            nn.LayerNorm(config.mlp_dims),
            nn.Linear(config.mlp_dims, 20)  # 20個MCP工具
        )
        
        # 語言模型頭
        self.lm_head = nn.Linear(config.model_dim, config.vocab_size)
        
        # 上下文感知層
        self.context_attention = nn.MultiHeadAttention(
            dims=config.model_dim,
            num_heads=config.num_heads,
            query_input_dims=config.model_dim,
            key_input_dims=config.model_dim,
            value_input_dims=config.model_dim,
            value_dims=config.model_dim,
            value_output_dims=config.model_dim
        )
        
        # Dropout層
        self.dropout = nn.Dropout(config.dropout_rate)
    
    def forward(self, input_ids, attention_mask=None, context_memory=None, memory_indices=None, tool_labels=None):
        """前向傳播"""
        batch_size, seq_len = input_ids.shape
        
        # Token和位置嵌入
        token_embeds = self.token_embedding(input_ids)
        position_ids = mx.broadcast_to(mx.arange(seq_len)[None, :], (batch_size, seq_len))
        position_embeds = self.position_embedding(position_ids)
        
        hidden_states = token_embeds + position_embeds
        hidden_states = self.dropout(hidden_states)
        
        # K2對話理解
        for k2_layer in self.k2_layers:
            hidden_states = k2_layer(hidden_states, mask=attention_mask)
        
        # 整合記憶和上下文
        if context_memory is not None:
            # 使用上下文注意力
            context_aware_states, _ = self.context_attention(
                hidden_states,
                context_memory,
                context_memory
            )
            hidden_states = hidden_states + context_aware_states
        
        # MemoryRAG檢索增強
        memory_enhanced_states, retrieved_memories = self.memory_rag(hidden_states)
        hidden_states = memory_enhanced_states
        
        # DeepSWE程式理解
        for deepswe_layer in self.deepswe_layers:
            hidden_states = deepswe_layer(hidden_states, mask=attention_mask)
        
        # 輸出預測
        lm_logits = self.lm_head(hidden_states)
        tool_logits = self.tool_prediction(hidden_states.mean(axis=1))  # 池化
        
        return {
            "lm_logits": lm_logits,
            "tool_logits": tool_logits,
            "hidden_states": hidden_states,
            "retrieved_memories": retrieved_memories
        }

class TrainingConfig:
    """訓練配置"""
    def __init__(self):
        # 模型配置
        self.vocab_size = 32000
        self.model_dim = 768
        self.num_heads = 12
        self.num_k2_layers = 6
        self.num_deepswe_layers = 6
        self.mlp_dims = 3072
        self.max_seq_len = 512
        self.dropout_rate = 0.1
        
        # MemoryRAG配置
        self.memory_dim = 256
        self.num_memories = 10000
        self.attention_heads = 8
        
        # 訓練配置
        self.batch_size = 2  # MacBook Air友好
        self.learning_rate = 5e-5
        self.num_epochs = 5
        self.gradient_accumulation_steps = 8
        self.warmup_steps = 1000
        self.weight_decay = 0.01
        self.max_grad_norm = 1.0
        
        # 設備配置
        self.device = mx.gpu if mx.metal.is_available() else mx.cpu
        self.mixed_precision = False  # Apple Silicon暫不支持

class K2DeepSWEMemoryRAGTrainer:
    """統一訓練器"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.model = UnifiedK2DeepSWEMemoryRAGModel(config)
        self.optimizer = optim.AdamW(
            learning_rate=config.learning_rate,
            weight_decay=config.weight_decay
        )
        
        # 統計
        self.stats = defaultdict(float)
        self.training_history = []
        
        # 上下文管理器
        self.context_buffer = []
        self.max_context_size = 10
    
    def prepare_training_data(self):
        """準備訓練數據"""
        logger.info("📊 準備K2+DeepSWE+MemoryRAG訓練數據...")
        
        # 加載各種數據源
        training_samples = []
        
        # 1. 加載Manus對話數據
        manus_data = self._load_manus_conversations()
        training_samples.extend(manus_data)
        
        # 2. 創建模擬的Claude Code工具調用數據
        tool_data = self._create_tool_training_data()
        training_samples.extend(tool_data)
        
        # 3. 創建程式理解訓練數據
        code_data = self._create_code_understanding_data()
        training_samples.extend(code_data)
        
        logger.info(f"✅ 準備了 {len(training_samples)} 個訓練樣本")
        return training_samples
    
    def _load_manus_conversations(self):
        """加載Manus對話數據"""
        samples = []
        data_dir = Path("data/enhanced_extracted_chats")
        
        if data_dir.exists():
            for json_file in data_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    conversation = data.get("conversation", [])
                    for i in range(0, len(conversation) - 1, 2):
                        if i + 1 < len(conversation):
                            user_msg = conversation[i]
                            assistant_msg = conversation[i + 1]
                            
                            if user_msg.get("role") == "user" and assistant_msg.get("role") == "assistant":
                                samples.append({
                                    "input": user_msg["content"],
                                    "output": assistant_msg["content"],
                                    "type": "conversation",
                                    "source": "manus",
                                    "has_context": True
                                })
                
                except Exception as e:
                    logger.warning(f"處理文件失敗 {json_file}: {e}")
        
        return samples
    
    def _create_tool_training_data(self):
        """創建工具調用訓練數據"""
        tool_samples = []
        
        # MCP工具定義
        mcp_tools = {
            "Read": "讀取文件內容",
            "Write": "寫入文件", 
            "Edit": "編輯文件",
            "MultiEdit": "批量編輯文件",
            "Grep": "搜索文件內容",
            "Glob": "查找文件",
            "LS": "列出目錄",
            "Task": "執行任務搜索",
            "Bash": "執行shell命令",
            "TodoWrite": "管理待辦事項"
        }
        
        # 創建工具調用示例
        for tool_name, description in mcp_tools.items():
            # 基本工具調用
            sample = {
                "input": f"請{description}",
                "output": f"我將使用{tool_name}工具來{description}。\n\n<function_calls>\n<invoke name=\"{tool_name}\">\n<parameter name=\"example_param\">value</parameter>\n</invoke>\n</function_calls>",
                "type": "tool_training",
                "source": "synthetic"
            }
            tool_samples.append(sample)
        
        return tool_samples
    
    def _create_code_understanding_data(self):
        """創建程式理解數據"""
        code_samples = []
        
        # 簡化的程式理解示例
        examples = [
            {
                "input": "這段代碼是做什麼的？def add(a, b): return a + b",
                "output": "這是一個簡單的加法函數，接受兩個參數 a 和 b，返回它們的和。",
                "type": "code_understanding"
            },
            {
                "input": "如何優化這段循環？",
                "output": "我需要先查看您的代碼來提供優化建議。讓我幫您檢查代碼。",
                "type": "code_optimization"
            }
        ]
        
        for example in examples:
            code_samples.append({
                "input": example["input"],
                "output": example["output"],
                "type": "code_understanding",
                "source": "synthetic"
            })
        
        return code_samples