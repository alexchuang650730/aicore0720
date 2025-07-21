#!/usr/bin/env python3
"""
查找剩餘未處理的replay URLs
"""

import json
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_all_replay_urls():
    """查找所有replay URLs"""
    base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
    all_urls = set()
    
    # 搜索模式
    patterns = [
        "**/replay*.txt",
        "**/*replay*urls*.txt",
        "**/manus*.txt",
        "**/*manus*urls*.txt"
    ]
    
    for pattern in patterns:
        for file_path in base_dir.glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    urls = re.findall(r'https://manus\.im/share/[^?\s]+\?replay=1', content)
                    if urls:
                        logger.info(f"{file_path.name}: {len(urls)} URLs")
                        all_urls.update(urls)
            except:
                pass
    
    # 檢查JSON文件中的URLs
    json_patterns = ["**/*replay*.json", "**/*manus*.json"]
    for pattern in json_patterns:
        for file_path in base_dir.glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # 遞歸搜索JSON中的URLs
                    urls = extract_urls_from_json(data)
                    if urls:
                        logger.info(f"{file_path.name}: {len(urls)} URLs (from JSON)")
                        all_urls.update(urls)
            except:
                pass
    
    return list(all_urls)


def extract_urls_from_json(obj):
    """從JSON對象中提取URLs"""
    urls = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and 'manus.im/share' in value:
                matches = re.findall(r'https://manus\.im/share/[^?\s]+\?replay=1', value)
                urls.extend(matches)
            else:
                urls.extend(extract_urls_from_json(value))
    elif isinstance(obj, list):
        for item in obj:
            urls.extend(extract_urls_from_json(item))
    elif isinstance(obj, str) and 'manus.im/share' in obj:
        matches = re.findall(r'https://manus\.im/share/[^?\s]+\?replay=1', obj)
        urls.extend(matches)
    
    return urls


def check_processed_status():
    """檢查已處理的URLs"""
    base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
    processed_ids = set()
    
    # 檢查已下載的replay文件
    patterns = [
        "data/**/replay_*.json",
        "data/**/conversation_*.json"
    ]
    
    for pattern in patterns:
        for file_path in base_dir.glob(pattern):
            # 從文件名提取ID
            match = re.search(r'([a-zA-Z0-9]{22})', file_path.name)
            if match:
                processed_ids.add(match.group(1))
    
    return processed_ids


def main():
    # 1. 查找所有URLs
    all_urls = find_all_replay_urls()
    logger.info(f"\n總共找到 {len(all_urls)} 個獨特的replay URLs")
    
    # 2. 檢查已處理的
    processed_ids = check_processed_status()
    logger.info(f"已處理 {len(processed_ids)} 個replays")
    
    # 3. 找出未處理的
    unprocessed_urls = []
    for url in all_urls:
        match = re.search(r'/share/([^?]+)', url)
        if match:
            replay_id = match.group(1)
            if replay_id not in processed_ids:
                unprocessed_urls.append(url)
    
    logger.info(f"待處理 {len(unprocessed_urls)} 個URLs")
    
    # 4. 保存未處理的URLs
    if unprocessed_urls:
        output_file = Path("data/unprocessed_replay_urls.txt")
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            for url in unprocessed_urls:
                f.write(url + '\n')
        logger.info(f"未處理URLs已保存到: {output_file}")
    
    # 5. 生成統計報告
    report = f"""
# Replay URLs 完整統計

## 總覽
- 找到的所有URLs: {len(all_urls)}
- 已處理: {len(processed_ids)}
- 待處理: {len(unprocessed_urls)}
- 處理率: {len(processed_ids) / len(all_urls) * 100:.1f}%

## 未處理URLs樣本（前10個）
"""
    for url in unprocessed_urls[:10]:
        report += f"- {url}\n"
    
    with open("replay_urls_complete_report.md", 'w') as f:
        f.write(report)
    
    logger.info("統計報告已生成: replay_urls_complete_report.md")
    
    return {
        "total": len(all_urls),
        "processed": len(processed_ids),
        "unprocessed": len(unprocessed_urls)
    }


if __name__ == "__main__":
    stats = main()
    print(json.dumps(stats, indent=2))