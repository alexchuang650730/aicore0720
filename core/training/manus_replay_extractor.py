#!/usr/bin/env python3
"""
Manus Replay 數據提取器
從 Manus.im 的 replay 連結中提取對話數據用於訓練
"""

import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class ManusReplayExtractor:
    """Manus Replay 數據提取器"""
    
    def __init__(self, output_dir: str = "./manus_training_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = None
        self.extracted_conversations = []
        
    async def extract_replay(self, replay_url: str) -> Dict[str, Any]:
        """從單個 replay URL 提取對話數據"""
        print(f"📥 提取: {replay_url}")
        
        try:
            # 解析 replay ID
            replay_id = self._extract_replay_id(replay_url)
            
            # 獲取對話數據
            conversation_data = await self._fetch_replay_data(replay_url)
            
            # 處理對話
            processed_data = self._process_conversation(conversation_data, replay_id)
            
            # 保存原始數據
            self._save_raw_data(replay_id, conversation_data)
            
            return processed_data
            
        except Exception as e:
            print(f"❌ 提取失敗 {replay_url}: {e}")
            return None
    
    def _extract_replay_id(self, url: str) -> str:
        """從 URL 提取 replay ID"""
        # https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1
        parsed = urlparse(url)
        parts = parsed.path.split('/')
        return parts[-1] if parts[-1] else parts[-2]
    
    async def _fetch_replay_data(self, url: str) -> Dict[str, Any]:
        """獲取 replay 數據"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        async with self.session.get(url) as response:
            html = await response.text()
            
        # 從 HTML 中提取數據
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找包含對話數據的 script 標籤
        script_tags = soup.find_all('script')
        conversation_data = None
        
        for script in script_tags:
            if script.string and 'conversationData' in script.string:
                # 提取 JSON 數據
                match = re.search(r'conversationData\s*=\s*({.*?});', script.string, re.DOTALL)
                if match:
                    conversation_data = json.loads(match.group(1))
                    break
                    
        # 如果找不到，嘗試其他模式
        if not conversation_data:
            # 可能數據在 window.__INITIAL_STATE__ 中
            for script in script_tags:
                if script.string and '__INITIAL_STATE__' in script.string:
                    match = re.search(r'__INITIAL_STATE__\s*=\s*({.*?});', script.string, re.DOTALL)
                    if match:
                        initial_state = json.loads(match.group(1))
                        conversation_data = initial_state.get('conversation', {})
                        break
        
        return conversation_data
    
    def _process_conversation(self, data: Dict, replay_id: str) -> Dict[str, Any]:
        """處理對話數據"""
        messages = data.get('messages', [])
        processed_messages = []
        code_blocks = []
        
        for i, msg in enumerate(messages):
            processed_msg = {
                'role': msg.get('role', 'user'),
                'content': msg.get('content', ''),
                'timestamp': msg.get('timestamp', ''),
                'index': i
            }
            
            # 提取代碼塊
            code_blocks.extend(self._extract_code_blocks(msg.get('content', '')))
            
            processed_messages.append(processed_msg)
        
        # 創建訓練對
        training_pairs = self._create_training_pairs(processed_messages)
        
        return {
            'replay_id': replay_id,
            'message_count': len(messages),
            'messages': processed_messages,
            'code_blocks': code_blocks,
            'training_pairs': training_pairs,
            'metadata': {
                'extracted_at': datetime.now().isoformat(),
                'has_code': len(code_blocks) > 0,
                'conversation_type': self._classify_conversation(messages)
            }
        }
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """提取代碼塊"""
        code_blocks = []
        
        # 匹配 ```language\ncode\n``` 格式
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            language = match.group(1) or 'plaintext'
            code = match.group(2)
            
            code_blocks.append({
                'language': language,
                'code': code,
                'length': len(code),
                'type': self._classify_code_type(code, language)
            })
            
        return code_blocks
    
    def _create_training_pairs(self, messages: List[Dict]) -> List[Dict]:
        """創建訓練對"""
        pairs = []
        
        for i in range(len(messages) - 1):
            if messages[i]['role'] == 'user' and messages[i + 1]['role'] == 'assistant':
                user_msg = messages[i]['content']
                assistant_msg = messages[i + 1]['content']
                
                # 判斷是否為高質量訓練數據
                if self._is_quality_pair(user_msg, assistant_msg):
                    pair = {
                        'input': user_msg,
                        'output': assistant_msg,
                        'type': self._classify_interaction_type(user_msg, assistant_msg),
                        'quality_score': self._calculate_quality_score(user_msg, assistant_msg),
                        'has_code': '```' in assistant_msg,
                        'deepswe_format': self._convert_to_deepswe_format(user_msg, assistant_msg)
                    }
                    pairs.append(pair)
                    
        return pairs
    
    def _convert_to_deepswe_format(self, user_input: str, assistant_output: str) -> Dict[str, str]:
        """轉換為 DeepSWE 訓練格式"""
        
        # 提取思考過程（如果有）
        thinking_match = re.search(r'讓我.*?[。\n]|首先.*?[。\n]|這個.*?需要.*?[。\n]', assistant_output)
        thinking = thinking_match.group(0) if thinking_match else ""
        
        # 構建 DeepSWE 格式
        deepswe_prompt = f"""<thinking>
{thinking if thinking else "分析用戶需求，準備生成相應的解決方案。"}
</thinking>

用戶請求：
{user_input}

請提供解決方案。
"""
        
        return {
            'prompt': deepswe_prompt,
            'completion': assistant_output,
            'metadata': {
                'source': 'manus_replay',
                'has_thinking': bool(thinking)
            }
        }
    
    def _classify_code_type(self, code: str, language: str) -> str:
        """分類代碼類型"""
        if language in ['python', 'py']:
            if 'class ' in code:
                return 'class_definition'
            elif 'def ' in code:
                return 'function_definition'
            elif 'import ' in code:
                return 'imports'
        elif language in ['javascript', 'js', 'jsx', 'tsx']:
            if 'function' in code or '=>' in code:
                return 'function_definition'
            elif 'class' in code:
                return 'class_definition'
            elif 'import' in code or 'require' in code:
                return 'imports'
        
        return 'general'
    
    def _classify_conversation(self, messages: List[Dict]) -> str:
        """分類對話類型"""
        combined_text = ' '.join([msg.get('content', '') for msg in messages])
        
        if any(word in combined_text for word in ['錯誤', 'error', 'bug', '修復', 'fix']):
            return 'debugging'
        elif any(word in combined_text for word in ['實現', 'implement', '創建', 'create', '生成']):
            return 'implementation'
        elif any(word in combined_text for word in ['優化', 'optimize', '改進', 'improve']):
            return 'optimization'
        elif any(word in combined_text for word in ['解釋', 'explain', '理解', 'understand']):
            return 'explanation'
        else:
            return 'general'
    
    def _classify_interaction_type(self, user_msg: str, assistant_msg: str) -> str:
        """分類交互類型"""
        if '```' in assistant_msg:
            if '錯誤' in user_msg or 'error' in user_msg:
                return 'error_fixing'
            elif '優化' in user_msg or 'optimize' in user_msg:
                return 'code_optimization'
            else:
                return 'code_generation'
        else:
            return 'explanation'
    
    def _is_quality_pair(self, user_msg: str, assistant_msg: str) -> bool:
        """判斷是否為高質量訓練對"""
        # 基本長度要求
        if len(user_msg) < 10 or len(assistant_msg) < 50:
            return False
            
        # 必須有實質內容
        if not any(char.isalnum() for char in user_msg):
            return False
            
        # 助手回應應該有代碼或詳細解釋
        has_code = '```' in assistant_msg
        has_explanation = len(assistant_msg) > 200
        
        return has_code or has_explanation
    
    def _calculate_quality_score(self, user_msg: str, assistant_msg: str) -> float:
        """計算質量分數"""
        score = 0.5  # 基礎分
        
        # 有代碼加分
        if '```' in assistant_msg:
            score += 0.2
            
        # 有解釋加分
        if any(word in assistant_msg for word in ['因為', '所以', '首先', '然後', 'because', 'therefore']):
            score += 0.1
            
        # 長度適中加分
        if 100 < len(assistant_msg) < 2000:
            score += 0.1
            
        # 有多個步驟加分
        if any(pattern in assistant_msg for pattern in ['1.', '2.', '步驟', 'Step']):
            score += 0.1
            
        return min(score, 1.0)
    
    def _save_raw_data(self, replay_id: str, data: Dict):
        """保存原始數據"""
        output_file = self.output_dir / f"raw/{replay_id}.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def process_batch(self, replay_urls: List[str], max_concurrent: int = 5):
        """批量處理 replay URLs"""
        print(f"🚀 開始批量處理 {len(replay_urls)} 個 replays")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_limit(url):
            async with semaphore:
                return await self.extract_replay(url)
        
        tasks = [process_with_limit(url) for url in replay_urls]
        results = await asyncio.gather(*tasks)
        
        # 過濾成功的結果
        successful = [r for r in results if r is not None]
        
        print(f"✅ 成功提取 {len(successful)}/{len(replay_urls)} 個對話")
        
        # 合併所有訓練對
        all_training_pairs = []
        for result in successful:
            all_training_pairs.extend(result['training_pairs'])
        
        # 保存合併的訓練數據
        self._save_training_dataset(all_training_pairs)
        
        return {
            'total_processed': len(replay_urls),
            'successful': len(successful),
            'total_training_pairs': len(all_training_pairs),
            'training_data_path': str(self.output_dir / 'training_dataset.json')
        }
    
    def _save_training_dataset(self, training_pairs: List[Dict]):
        """保存訓練數據集"""
        # 按類型分組
        by_type = {}
        for pair in training_pairs:
            pair_type = pair['type']
            if pair_type not in by_type:
                by_type[pair_type] = []
            by_type[pair_type].append(pair)
        
        # 保存完整數據集
        output_file = self.output_dir / 'training_dataset.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_pairs': len(training_pairs),
                'by_type': {k: len(v) for k, v in by_type.items()},
                'pairs': training_pairs
            }, f, ensure_ascii=False, indent=2)
        
        # 保存 DeepSWE 格式
        deepswe_file = self.output_dir / 'deepswe_format.jsonl'
        with open(deepswe_file, 'w', encoding='utf-8') as f:
            for pair in training_pairs:
                if pair.get('deepswe_format'):
                    f.write(json.dumps(pair['deepswe_format'], ensure_ascii=False) + '\n')
        
        print(f"💾 訓練數據已保存:")
        print(f"   - 完整數據集: {output_file}")
        print(f"   - DeepSWE 格式: {deepswe_file}")
        print(f"   - 總訓練對: {len(training_pairs)}")
        for pair_type, pairs in by_type.items():
            print(f"   - {pair_type}: {len(pairs)} 對")
    
    async def close(self):
        """關閉會話"""
        if self.session:
            await self.session.close()


async def main():
    """主函數示例"""
    # 準備 replay URLs
    replay_urls = [
        "https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1",
        # 添加更多 URLs...
    ]
    
    # 或從文件讀取
    # with open('replay_urls.txt', 'r') as f:
    #     replay_urls = [line.strip() for line in f if line.strip()]
    
    extractor = ManusReplayExtractor()
    
    try:
        # 批量處理
        results = await extractor.process_batch(replay_urls)
        
        print("\n📊 處理完成！")
        print(f"✅ 成功率: {results['successful']}/{results['total_processed']}")
        print(f"📚 總訓練對: {results['total_training_pairs']}")
        print(f"💾 數據保存位置: {results['training_data_path']}")
        
    finally:
        await extractor.close()


if __name__ == "__main__":
    asyncio.run(main())