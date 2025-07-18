"""
MCP系統配置 - 整合所有優化
"""

import os

# API密鑰配置
API_KEYS = {
    "MOONSHOT_API_KEY": os.getenv("MOONSHOT_API_KEY", ""),
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
    "HF_TOKEN": os.getenv("HF_TOKEN", "")
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
