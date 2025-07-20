#!/usr/bin/env python3
"""
檢查replay數據使用情況
分析500多條replay數據是否被充分利用
"""

import json
import os
import glob
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_replay_usage():
    """分析replay數據使用情況"""
    
    base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
    
    # 1. 統計replay URLs
    logger.info("=== Replay URLs 統計 ===")
    
    # 查找所有replay URL文件
    url_files = list(base_dir.glob("**/replay*.txt")) + list(base_dir.glob("**/*replay*urls*.txt"))
    
    total_urls = set()
    for url_file in url_files:
        try:
            with open(url_file, 'r') as f:
                content = f.read()
                # 提取所有manus.im URLs
                import re
                urls = re.findall(r'https://manus\.im/share/[^?\s]+\?replay=1', content)
                total_urls.update(urls)
                if urls:
                    logger.info(f"{url_file.name}: {len(urls)} URLs")
        except:
            pass
    
    logger.info(f"\n總共發現 {len(total_urls)} 個唯一的replay URLs")
    
    # 2. 檢查實際下載的replay數據
    logger.info("\n=== 已下載的Replay數據 ===")
    
    replay_data_patterns = [
        "data/real_replays/*.json",
        "data/replay_analysis/*.json",
        "data/manus_conversations/*.json",
        "data/unified_realtime/conversation*.json"
    ]
    
    downloaded_replays = 0
    for pattern in replay_data_patterns:
        files = list(base_dir.glob(pattern))
        if files:
            logger.info(f"{pattern}: {len(files)} 個文件")
            downloaded_replays += len(files)
    
    logger.info(f"\n總共下載了 {downloaded_replays} 個replay數據文件")
    
    # 3. 檢查訓練數據生成情況
    logger.info("\n=== 訓練數據生成 ===")
    
    training_files = list(base_dir.glob("**/k2_training*.jsonl")) + \
                    list(base_dir.glob("**/k2_train*.jsonl"))
    
    total_training_samples = 0
    for tf in training_files:
        try:
            with open(tf, 'r') as f:
                lines = sum(1 for _ in f)
                logger.info(f"{tf.name}: {lines} 條訓練樣本")
                total_training_samples += lines
        except:
            pass
    
    logger.info(f"\n總共生成了 {total_training_samples} 條訓練樣本")
    
    # 4. 分析數據利用率
    logger.info("\n=== 數據利用率分析 ===")
    
    if len(total_urls) > 0:
        download_rate = (downloaded_replays / len(total_urls)) * 100
        logger.info(f"URL下載率: {download_rate:.1f}%")
        
        if downloaded_replays > 0:
            samples_per_replay = total_training_samples / downloaded_replays
            logger.info(f"每個replay平均生成樣本: {samples_per_replay:.1f}")
    
    # 5. 查找最新的數據收集情況
    logger.info("\n=== 最新數據收集 ===")
    
    # 查找unified_k2_training.log
    log_file = base_dir / "unified_k2_training.log"
    if log_file.exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # 查找最後幾個收集統計
            for line in lines[-100:]:
                if "總對話數" in line:
                    logger.info(line.strip())
    
    # 6. 建議
    logger.info("\n=== 改進建議 ===")
    
    if len(total_urls) > downloaded_replays:
        logger.info(f"❗ 還有 {len(total_urls) - downloaded_replays} 個URLs未下載")
    
    if downloaded_replays > 0 and total_training_samples < downloaded_replays * 10:
        logger.info("❗ 訓練樣本生成率偏低，建議優化數據提取邏輯")
    
    logger.info("\n建議的下一步行動：")
    logger.info("1. 使用 real_replay_collector.py 下載所有未處理的URLs")
    logger.info("2. 優化訓練數據生成邏輯，從每個對話提取更多樣本")
    logger.info("3. 實施MCP Zero自動工具發現，提升工具調用準確率")
    
    return {
        "total_urls": len(total_urls),
        "downloaded_replays": downloaded_replays,
        "training_samples": total_training_samples,
        "utilization_rate": (downloaded_replays / len(total_urls) * 100) if len(total_urls) > 0 else 0
    }


if __name__ == "__main__":
    results = analyze_replay_usage()