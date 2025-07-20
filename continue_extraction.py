#!/usr/bin/env python3
"""
繼續Manus聊天萃取，從已處理的文件開始
"""

import asyncio
import os
from manus_chat_extractor import ManusChatExtractor

async def continue_extraction():
    """繼續萃取未處理的URL"""
    extractor = ManusChatExtractor()
    
    # 讀取所有URL
    urls_file = "/Users/alexchuang/alexchuangtest/aicore0720/data/replay_links/replay_urls_fixed.txt"
    with open(urls_file, 'r', encoding='utf-8') as f:
        all_urls = [line.strip() for line in f if line.strip()]
    
    # 檢查已經處理過的文件
    extracted_dir = "/Users/alexchuang/alexchuangtest/aicore0720/data/extracted_chats"
    processed_ids = set()
    
    if os.path.exists(extracted_dir):
        for filename in os.listdir(extracted_dir):
            if filename.startswith("chat_") and filename.endswith(".json"):
                # 提取replay_id
                parts = filename.split("_")
                if len(parts) >= 3:
                    replay_id = "_".join(parts[2:]).replace(".json", "")
                    processed_ids.add(replay_id)
    
    print(f"📊 總共 {len(all_urls)} 個URL")
    print(f"✅ 已處理 {len(processed_ids)} 個")
    
    # 過濾出未處理的URL
    remaining_urls = []
    for url in all_urls:
        replay_id = url.split('/')[-1].split('?')[0]
        if replay_id not in processed_ids:
            remaining_urls.append(url)
    
    print(f"🔄 剩餘 {len(remaining_urls)} 個需要處理")
    
    if not remaining_urls:
        print("🎉 所有URL已經處理完成！")
        return
    
    # 寫入剩餘URL到臨時文件
    temp_urls_file = "/tmp/remaining_urls.txt"
    with open(temp_urls_file, 'w', encoding='utf-8') as f:
        for url in remaining_urls:
            f.write(url + "\n")
    
    # 繼續萃取
    result = await extractor.extract_chat_batch(temp_urls_file, batch_size=15)
    
    if result["success"]:
        print("\n🎉 繼續萃取成功！")
        print(f"📊 本次萃取了 {result['stats']['extracted']} 個對話")
        print(f"💬 總消息數: {result['stats']['total_messages']}")
        print(f"📈 平均每對話: {result['stats']['total_messages']/max(result['stats']['total_conversations'], 1):.1f} 條消息")
        
        # 統計總體進度
        total_processed = len(processed_ids) + result['stats']['extracted']
        progress = total_processed / len(all_urls) * 100
        print(f"🚀 總體進度: {total_processed}/{len(all_urls)} ({progress:.1f}%)")
    
    # 清理臨時文件
    os.remove(temp_urls_file)

if __name__ == "__main__":
    asyncio.run(continue_extraction())