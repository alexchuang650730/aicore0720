"""
MCP系統配置 - 整合所有優化
"""

import os

# API密鑰配置
API_KEYS = {
    "MOONSHOT_API_KEY": "sk-ocQ1YiAJtB2yfaXVXFzkW0973MXXKLR0OCEi0BbVqqmc31UK",
    "GROQ_API_KEY": "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",
    "ANTHROPIC_API_KEY": "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",
    "HF_TOKEN": "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"
}

# 設置環境變量
for key, value in API_KEYS.items():
    os.environ[key] = value

# 系統配置
SYSTEM_CONFIG = {
    "default_provider": "moonshot",  # 默認使用K2
    "fallback_provider": "groq",     # 備用快速模型
    "rag_enabled": True,             # 啟用RAG增強
    "cache_enabled": True,           # 啟用緩存
    "target_latency_ms": 1800,       # 目標總延遲
    "cost_optimization": True        # 成本優化模式
}

# 性能目標
PERFORMANCE_TARGETS = {
    "k2_latency_ms": 1500,
    "rag_latency_ms": 200,
    "total_latency_ms": 1800,
    "cache_hit_rate": 0.3,
    "cost_savings": 0.7
}
