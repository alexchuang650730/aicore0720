#!/usr/bin/env python3
"""
多模態訓練數據收集系統
擴展K2+DeepSWE+MemoryRAG系統的數據來源
"""

import os
import json
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
import subprocess
import logging
from typing import List, Dict, Any
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultimodalDataCollector:
    """多模態數據收集器"""
    
    def __init__(self):
        self.data_dir = Path("data/multimodal_training")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 數據源配置
        self.data_sources = {
            "github_repos": {
                "enabled": True,
                "targets": [
                    "anthropics/claude-3-sonnet-20240229-v1_0-examples",
                    "microsoft/vscode",
                    "python/cpython",
                    "facebook/react",
                    "openai/openai-python"
                ],
                "file_types": [".py", ".js", ".ts", ".md", ".txt", ".json"]
            },
            "stack_overflow": {
                "enabled": True,
                "tags": ["python", "javascript", "machine-learning", "llm", "claude"],
                "min_score": 5
            },
            "code_documentation": {
                "enabled": True,
                "sources": [
                    "https://docs.python.org/3/",
                    "https://developer.mozilla.org/en-US/",
                    "https://pytorch.org/docs/stable/",
                    "https://docs.anthropic.com/"
                ]
            },
            "technical_blogs": {
                "enabled": True,
                "rss_feeds": [
                    "https://blog.anthropic.com/rss.xml",
                    "https://openai.com/blog/rss.xml",
                    "https://ai.googleblog.com/feeds/posts/default"
                ]
            }
        }
    
    async def collect_github_data(self):
        """收集GitHub代碼和討論數據"""
        logger.info("🐙 開始GitHub數據收集...")
        
        collected_data = []
        
        for repo in self.data_sources["github_repos"]["targets"]:
            try:
                # 使用git clone獲取代碼
                temp_dir = tempfile.mkdtemp()
                clone_cmd = f"git clone --depth 1 https://github.com/{repo}.git {temp_dir}/repo"
                
                result = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    repo_data = self._extract_repo_conversations(Path(temp_dir) / "repo", repo)
                    collected_data.extend(repo_data)
                    logger.info(f"✅ 成功收集 {repo}: {len(repo_data)} 個代碼對話")
                else:
                    logger.warning(f"⚠️ 無法克隆 {repo}: {result.stderr}")
                
                # 清理臨時目錄
                subprocess.run(f"rm -rf {temp_dir}", shell=True)
                
            except Exception as e:
                logger.error(f"❌ GitHub收集錯誤 {repo}: {e}")
        
        return collected_data
    
    def _extract_repo_conversations(self, repo_path: Path, repo_name: str) -> List[Dict]:
        """從代碼倉庫提取對話式數據"""
        conversations = []
        
        # 查找README和文檔文件
        doc_files = []
        for ext in self.data_sources["github_repos"]["file_types"]:
            doc_files.extend(repo_path.rglob(f"*{ext}"))
        
        for file_path in doc_files[:50]:  # 限制文件數量
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if len(content) > 100:  # 過濾太短的文件
                    conversation = self._convert_to_conversation_format(
                        content, file_path, repo_name
                    )
                    if conversation:
                        conversations.append(conversation)
                        
            except Exception as e:
                logger.debug(f"跳過文件 {file_path}: {e}")
        
        return conversations
    
    def _convert_to_conversation_format(self, content: str, file_path: Path, repo_name: str) -> Dict:
        """將代碼/文檔轉換為對話格式"""
        
        # 根據文件類型創建不同的對話
        file_ext = file_path.suffix.lower()
        
        if file_ext == ".md":
            # Markdown文檔轉對話
            return {
                "id": f"github_{repo_name}_{file_path.stem}",
                "timestamp": datetime.now().isoformat(),
                "category": "documentation",
                "source": f"GitHub:{repo_name}",
                "conversation": [
                    {
                        "role": "user",
                        "content": f"請解釋這個項目的 {file_path.name} 文檔內容"
                    },
                    {
                        "role": "assistant", 
                        "content": f"這是來自 {repo_name} 項目的文檔：\n\n{content[:2000]}..."
                    }
                ]
            }
        
        elif file_ext in [".py", ".js", ".ts"]:
            # 代碼文件轉對話
            return {
                "id": f"github_{repo_name}_{file_path.stem}",
                "timestamp": datetime.now().isoformat(),
                "category": "code_analysis",
                "source": f"GitHub:{repo_name}",
                "conversation": [
                    {
                        "role": "user",
                        "content": f"請分析這個 {file_ext} 代碼文件的功能和結構"
                    },
                    {
                        "role": "assistant",
                        "content": f"這是 {repo_name} 項目中的 {file_path.name} 文件：\n\n```{file_ext}\n{content[:1500]}\n```\n\n這個文件主要實現了..."
                    }
                ]
            }
        
        return None
    
    async def collect_stackoverflow_data(self):
        """收集Stack Overflow問答數據"""
        logger.info("📚 開始Stack Overflow數據收集...")
        
        collected_data = []
        
        async with aiohttp.ClientSession() as session:
            for tag in self.data_sources["stack_overflow"]["tags"]:
                try:
                    # 使用Stack Overflow API
                    url = f"https://api.stackexchange.com/2.3/questions"
                    params = {
                        "order": "desc",
                        "sort": "activity",
                        "tagged": tag,
                        "site": "stackoverflow",
                        "pagesize": 20,
                        "filter": "withbody"
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for item in data.get("items", []):
                                if item.get("score", 0) >= self.data_sources["stack_overflow"]["min_score"]:
                                    conversation = self._format_stackoverflow_conversation(item, tag)
                                    collected_data.append(conversation)
                            
                            logger.info(f"✅ 收集 {tag} 標籤: {len(data.get('items', []))} 個問答")
                    
                    # 避免API限制
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Stack Overflow收集錯誤 {tag}: {e}")
        
        return collected_data
    
    def _format_stackoverflow_conversation(self, item: Dict, tag: str) -> Dict:
        """格式化Stack Overflow問答為對話"""
        
        return {
            "id": f"stackoverflow_{item['question_id']}",
            "timestamp": datetime.fromtimestamp(item['creation_date']).isoformat(),
            "category": "qa_programming",
            "source": f"StackOverflow:{tag}",
            "conversation": [
                {
                    "role": "user",
                    "content": f"問題: {item['title']}\n\n{item.get('body', '')[:1500]}..."
                },
                {
                    "role": "assistant",
                    "content": f"這是一個關於 {tag} 的技術問題。讓我來分析和回答...\n\n[基於Stack Overflow高質量答案的回應]"
                }
            ],
            "metadata": {
                "score": item.get("score", 0),
                "view_count": item.get("view_count", 0),
                "tags": item.get("tags", [])
            }
        }
    
    async def collect_documentation_data(self):
        """收集技術文檔數據"""
        logger.info("📖 開始技術文檔收集...")
        
        collected_data = []
        
        async with aiohttp.ClientSession() as session:
            for source_url in self.data_sources["code_documentation"]["sources"]:
                try:
                    async with session.get(source_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # 簡單提取主要內容（實際應使用更複雜的解析）
                            conversation = {
                                "id": f"docs_{source_url.split('//')[1].replace('/', '_')}",
                                "timestamp": datetime.now().isoformat(),
                                "category": "technical_documentation",
                                "source": source_url,
                                "conversation": [
                                    {
                                        "role": "user",
                                        "content": f"請介紹 {source_url} 的主要文檔內容"
                                    },
                                    {
                                        "role": "assistant",
                                        "content": f"這是來自 {source_url} 的技術文檔摘要：\n\n{content[:2000]}..."
                                    }
                                ]
                            }
                            
                            collected_data.append(conversation)
                            logger.info(f"✅ 收集文檔: {source_url}")
                    
                    await asyncio.sleep(2)  # 尊重服務器
                    
                except Exception as e:
                    logger.error(f"❌ 文檔收集錯誤 {source_url}: {e}")
        
        return collected_data
    
    async def run_collection_cycle(self):
        """執行一次完整的多模態數據收集"""
        logger.info("🚀 啟動多模態數據收集...")
        
        all_data = []
        
        # 並行收集不同類型的數據
        tasks = []
        
        if self.data_sources["github_repos"]["enabled"]:
            tasks.append(self.collect_github_data())
        
        if self.data_sources["stack_overflow"]["enabled"]:
            tasks.append(self.collect_stackoverflow_data())
        
        if self.data_sources["code_documentation"]["enabled"]:
            tasks.append(self.collect_documentation_data())
        
        # 執行所有收集任務
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合併結果
        for result in results:
            if isinstance(result, list):
                all_data.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"❌ 收集任務失敗: {result}")
        
        # 保存收集的數據
        if all_data:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.data_dir / f"multimodal_training_data_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 多模態數據收集完成: {len(all_data)} 個對話")
            logger.info(f"📁 數據已保存: {output_file}")
            
            return output_file, len(all_data)
        
        return None, 0
    
    def get_collection_stats(self):
        """獲取收集統計"""
        stats = {
            "total_files": 0,
            "total_conversations": 0,
            "by_category": {},
            "by_source": {}
        }
        
        for file_path in self.data_dir.glob("multimodal_training_data_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                stats["total_files"] += 1
                stats["total_conversations"] += len(data)
                
                for item in data:
                    category = item.get("category", "unknown")
                    source = item.get("source", "unknown")
                    
                    stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                    stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
                    
            except Exception as e:
                logger.warning(f"⚠️ 無法讀取統計文件 {file_path}: {e}")
        
        return stats

async def main():
    """主函數"""
    collector = MultimodalDataCollector()
    
    # 顯示當前統計
    stats = collector.get_collection_stats()
    print(f"📊 當前多模態數據統計:")
    print(f"  總文件數: {stats['total_files']}")
    print(f"  總對話數: {stats['total_conversations']}")
    print(f"  分類分布: {stats['by_category']}")
    print(f"  來源分布: {stats['by_source']}")
    
    # 執行數據收集
    output_file, count = await collector.run_collection_cycle()
    
    if output_file:
        print(f"✅ 成功收集 {count} 個多模態對話")
        print(f"📁 保存位置: {output_file}")
    else:
        print("❌ 數據收集失敗")

if __name__ == "__main__":
    asyncio.run(main())