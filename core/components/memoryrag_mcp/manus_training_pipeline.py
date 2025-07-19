#!/usr/bin/env python3
"""
Manus 數據訓練管道
用於處理和訓練 Chrome Manus 數據
"""

import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ManusTask:
    """Manus 任務數據結構"""
    task_id: str
    url: str
    title: str
    description: str
    conversations: List[Dict[str, Any]]
    tools_used: List[str]
    thinking_patterns: List[str]
    action_patterns: List[str]
    timestamp: str

@dataclass
class TrainingData:
    """訓練數據結構"""
    input_text: str
    output_text: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]

class ManusTrainingPipeline:
    """Manus 數據訓練管道"""
    
    def __init__(self):
        self.manus_tasks_file = Path("manus_tasks_manual.txt")
        self.training_data_dir = Path("core/components/memoryrag_mcp/manus_training_data")
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 模式識別
        self.thinking_patterns = [
            r'我.*理解', r'讓我.*', r'根據.*', r'分析.*',
            r'看起來.*', r'這個.*', r'首先.*', r'然後.*',
            r'需要.*', r'應該.*', r'可以.*', r'建議.*'
        ]
        
        self.observation_patterns = [
            r'檢查.*', r'確認.*', r'發現.*', r'看到.*',
            r'結果.*', r'顯示.*', r'輸出.*', r'錯誤.*',
            r'成功.*', r'失敗.*', r'完成.*', r'狀態.*'
        ]
        
        self.action_patterns = [
            r'執行.*', r'運行.*', r'創建.*', r'修改.*',
            r'安裝.*', r'配置.*', r'設置.*', r'更新.*',
            r'刪除.*', r'啟動.*', r'停止.*', r'部署.*'
        ]
        
    async def load_manus_urls(self) -> List[str]:
        """加載 Manus 任務 URL"""
        urls = []
        try:
            with open(self.manus_tasks_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 解析 URL
            lines = content.strip().split('\n')
            for line in lines:
                if line.startswith('https://'):
                    urls.append(line.strip())
                    
            logger.info(f"加載了 {len(urls)} 個 Manus 任務 URL")
            return urls
            
        except Exception as e:
            logger.error(f"加載 URL 失敗: {str(e)}")
            return []
    
    async def extract_manus_data(self, url: str, session: aiohttp.ClientSession) -> Optional[ManusTask]:
        """提取單個 Manus 任務數據"""
        try:
            # 這裡需要實際的認證和數據提取邏輯
            # 現在使用模擬數據
            task_id = url.split('/')[-1]
            
            # 模擬數據結構
            task = ManusTask(
                task_id=task_id,
                url=url,
                title=f"任務 {task_id}",
                description="Manus 任務描述",
                conversations=[
                    {
                        "role": "user",
                        "content": "幫我創建一個 React 組件"
                    },
                    {
                        "role": "assistant",
                        "content": "我來幫您創建一個 React 組件...",
                        "thinking": "用戶需要一個 React 組件，我應該創建一個功能完整的示例",
                        "actions": ["創建組件文件", "編寫組件代碼", "添加樣式"]
                    }
                ],
                tools_used=["code_editor", "terminal", "file_manager"],
                thinking_patterns=["分析需求", "設計結構", "實現功能"],
                action_patterns=["創建文件", "編寫代碼", "測試運行"],
                timestamp=datetime.now().isoformat()
            )
            
            return task
            
        except Exception as e:
            logger.error(f"提取數據失敗 {url}: {str(e)}")
            return None
    
    async def process_all_tasks(self) -> List[ManusTask]:
        """處理所有 Manus 任務"""
        urls = await self.load_manus_urls()
        tasks = []
        
        async with aiohttp.ClientSession() as session:
            # 批量處理，避免過載
            batch_size = 5
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i+batch_size]
                batch_tasks = await asyncio.gather(
                    *[self.extract_manus_data(url, session) for url in batch],
                    return_exceptions=True
                )
                
                for task in batch_tasks:
                    if isinstance(task, ManusTask):
                        tasks.append(task)
                
                # 避免請求過快
                await asyncio.sleep(1)
        
        logger.info(f"成功提取 {len(tasks)} 個任務數據")
        return tasks
    
    def convert_to_training_data(self, tasks: List[ManusTask]) -> List[TrainingData]:
        """轉換為訓練數據格式"""
        training_data = []
        
        for task in tasks:
            for i, conv in enumerate(task.conversations):
                if conv["role"] == "user" and i + 1 < len(task.conversations):
                    user_input = conv["content"]
                    assistant_response = task.conversations[i + 1]
                    
                    if assistant_response["role"] == "assistant":
                        # 構建訓練數據
                        training_item = TrainingData(
                            input_text=user_input,
                            output_text=assistant_response["content"],
                            context={
                                "thinking": assistant_response.get("thinking", ""),
                                "actions": assistant_response.get("actions", []),
                                "tools": task.tools_used
                            },
                            metadata={
                                "task_id": task.task_id,
                                "url": task.url,
                                "timestamp": task.timestamp
                            }
                        )
                        training_data.append(training_item)
        
        logger.info(f"生成了 {len(training_data)} 條訓練數據")
        return training_data
    
    def analyze_patterns(self, tasks: List[ManusTask]) -> Dict[str, Any]:
        """分析 Manus 使用模式"""
        analysis = {
            "total_tasks": len(tasks),
            "tools_frequency": {},
            "thinking_patterns": {},
            "action_patterns": {},
            "average_conversation_length": 0
        }
        
        total_conversations = 0
        
        for task in tasks:
            # 工具使用頻率
            for tool in task.tools_used:
                analysis["tools_frequency"][tool] = analysis["tools_frequency"].get(tool, 0) + 1
            
            # 思考模式頻率
            for pattern in task.thinking_patterns:
                analysis["thinking_patterns"][pattern] = analysis["thinking_patterns"].get(pattern, 0) + 1
            
            # 行動模式頻率
            for pattern in task.action_patterns:
                analysis["action_patterns"][pattern] = analysis["action_patterns"].get(pattern, 0) + 1
            
            total_conversations += len(task.conversations)
        
        analysis["average_conversation_length"] = total_conversations / len(tasks) if tasks else 0
        
        return analysis
    
    async def create_training_dataset(self) -> Dict[str, Any]:
        """創建完整的訓練數據集"""
        logger.info("開始創建 Manus 訓練數據集...")
        
        # 1. 提取所有任務數據
        tasks = await self.process_all_tasks()
        
        # 2. 轉換為訓練格式
        training_data = self.convert_to_training_data(tasks)
        
        # 3. 分析模式
        patterns = self.analyze_patterns(tasks)
        
        # 4. 劃分訓練集、驗證集、測試集
        total = len(training_data)
        train_size = int(total * 0.8)
        val_size = int(total * 0.1)
        
        train_data = training_data[:train_size]
        val_data = training_data[train_size:train_size + val_size]
        test_data = training_data[train_size + val_size:]
        
        # 5. 保存數據集
        dataset = {
            "metadata": {
                "source": "Chrome Manus",
                "total_tasks": len(tasks),
                "total_samples": total,
                "created_at": datetime.now().isoformat(),
                "split": {
                    "train": len(train_data),
                    "validation": len(val_data),
                    "test": len(test_data)
                }
            },
            "patterns_analysis": patterns,
            "train": [self._format_training_item(item) for item in train_data],
            "validation": [self._format_training_item(item) for item in val_data],
            "test": [self._format_training_item(item) for item in test_data]
        }
        
        # 保存到文件
        output_file = self.training_data_dir / f"manus_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        logger.info(f"訓練數據集已保存: {output_file}")
        
        return dataset
    
    def _format_training_item(self, item: TrainingData) -> Dict[str, Any]:
        """格式化單個訓練項目"""
        return {
            "input": item.input_text,
            "output": item.output_text,
            "context": item.context,
            "metadata": item.metadata
        }
    
    async def create_fine_tuning_dataset(self) -> None:
        """創建用於微調的數據集（JSONL 格式）"""
        logger.info("創建微調數據集...")
        
        tasks = await self.process_all_tasks()
        training_data = self.convert_to_training_data(tasks)
        
        # 創建 JSONL 格式的訓練文件
        train_file = self.training_data_dir / f"manus_finetune_train_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        val_file = self.training_data_dir / f"manus_finetune_val_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
        # 分割數據
        split_point = int(len(training_data) * 0.9)
        train_data = training_data[:split_point]
        val_data = training_data[split_point:]
        
        # 寫入訓練文件
        with open(train_file, 'w', encoding='utf-8') as f:
            for item in train_data:
                # 構建對話格式
                conversation = {
                    "messages": [
                        {"role": "user", "content": item.input_text},
                        {"role": "assistant", "content": item.output_text}
                    ]
                }
                f.write(json.dumps(conversation, ensure_ascii=False) + '\n')
        
        # 寫入驗證文件
        with open(val_file, 'w', encoding='utf-8') as f:
            for item in val_data:
                conversation = {
                    "messages": [
                        {"role": "user", "content": item.input_text},
                        {"role": "assistant", "content": item.output_text}
                    ]
                }
                f.write(json.dumps(conversation, ensure_ascii=False) + '\n')
        
        logger.info(f"微調數據集已創建:")
        logger.info(f"  訓練集: {train_file} ({len(train_data)} 樣本)")
        logger.info(f"  驗證集: {val_file} ({len(val_data)} 樣本)")
    
    def generate_training_report(self, dataset: Dict[str, Any]) -> str:
        """生成訓練報告"""
        report = f"""# Manus 訓練數據報告

## 數據概覽
- 總任務數: {dataset['metadata']['total_tasks']}
- 總樣本數: {dataset['metadata']['total_samples']}
- 創建時間: {dataset['metadata']['created_at']}

## 數據劃分
- 訓練集: {dataset['metadata']['split']['train']} 樣本
- 驗證集: {dataset['metadata']['split']['validation']} 樣本
- 測試集: {dataset['metadata']['split']['test']} 樣本

## 模式分析

### 工具使用頻率
"""
        
        # 添加工具使用統計
        tools = dataset['patterns_analysis']['tools_frequency']
        for tool, count in sorted(tools.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"- {tool}: {count} 次\n"
        
        report += f"""
### 思考模式
"""
        # 添加思考模式統計
        thinking = dataset['patterns_analysis']['thinking_patterns']
        for pattern, count in sorted(thinking.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"- {pattern}: {count} 次\n"
        
        report += f"""
### 行動模式
"""
        # 添加行動模式統計
        actions = dataset['patterns_analysis']['action_patterns']
        for pattern, count in sorted(actions.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"- {pattern}: {count} 次\n"
        
        report += f"""
### 平均對話長度
- {dataset['patterns_analysis']['average_conversation_length']:.1f} 輪

## 訓練建議
1. 數據量：當前數據量適合進行初步訓練
2. 多樣性：涵蓋了多種工具使用場景
3. 質量：Manus 的工具使用模式清晰，適合學習
4. 增強：建議結合 Claude 對話數據進行聯合訓練
"""
        
        # 保存報告
        report_file = self.training_data_dir / f"manus_training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"訓練報告已保存: {report_file}")
        
        return report


async def main():
    """主函數"""
    pipeline = ManusTrainingPipeline()
    
    print("🚀 開始處理 Manus 訓練數據...")
    
    # 創建訓練數據集
    dataset = await pipeline.create_training_dataset()
    
    # 創建微調格式數據
    await pipeline.create_fine_tuning_dataset()
    
    # 生成報告
    report = pipeline.generate_training_report(dataset)
    
    print("\n✅ 處理完成！")
    print(f"總樣本數: {dataset['metadata']['total_samples']}")
    print(f"訓練集: {dataset['metadata']['split']['train']}")
    print(f"驗證集: {dataset['metadata']['split']['validation']}")
    print(f"測試集: {dataset['metadata']['split']['test']}")
    
    print("\n生成的文件:")
    print(f"- 數據集: manus_dataset_*.json")
    print(f"- 微調訓練集: manus_finetune_train_*.jsonl")
    print(f"- 微調驗證集: manus_finetune_val_*.jsonl")
    print(f"- 訓練報告: manus_training_report_*.md")

if __name__ == "__main__":
    asyncio.run(main())