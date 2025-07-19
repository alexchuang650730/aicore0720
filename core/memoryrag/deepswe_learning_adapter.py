#!/usr/bin/env python3
"""
DeepSWE 增強的學習適配器
整合 MemoryRAG 的 learning_adapter 與 DeepSWE 模式
用於從對話數據中學習並優化 K2 使用
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import numpy as np
from abc import ABC, abstractmethod


class DeepSWELearningAdapter:
    """DeepSWE 增強的學習適配器"""
    
    def __init__(self, memoryrag_instance):
        self.memoryrag = memoryrag_instance
        self.learning_patterns = []
        self.optimization_strategies = {}
        self.deepswe_models = {}
        self.learned_prompts = {}
        
    async def learn_from_conversations(self):
        """從 MemoryRAG 的對話歷史中學習"""
        print("🧠 開始 DeepSWE 增強學習...")
        
        # 從 MemoryRAG 獲取對話數據
        conversations = await self.memoryrag.get_all_conversations()
        
        # 分析對話模式
        patterns = self._analyze_conversation_patterns(conversations)
        
        # 學習優化策略
        strategies = self._learn_optimization_strategies(patterns)
        
        # 訓練 DeepSWE 風格的提示優化器
        await self._train_prompt_optimizer(conversations)
        
        # 更新學習結果
        self.learning_patterns = patterns
        self.optimization_strategies = strategies
        
        return {
            'learned_patterns': len(patterns),
            'optimization_strategies': len(strategies),
            'training_examples': len(conversations)
        }
        
    def _analyze_conversation_patterns(self, conversations: List[Dict]) -> List[Dict]:
        """分析對話模式"""
        patterns = []
        
        # 按任務類型分組
        task_groups = {}
        for conv in conversations:
            task_type = self._classify_task(conv)
            if task_type not in task_groups:
                task_groups[task_type] = []
            task_groups[task_type].append(conv)
            
        # 為每個任務類型提取模式
        for task_type, convs in task_groups.items():
            pattern = {
                'task_type': task_type,
                'common_elements': self._extract_common_elements(convs),
                'success_patterns': self._identify_success_patterns(convs),
                'optimization_opportunities': self._find_optimization_opportunities(convs)
            }
            patterns.append(pattern)
            
        return patterns
        
    def _classify_task(self, conv: Dict) -> str:
        """分類任務類型"""
        user_input = conv.get('user_input', '').lower()
        
        task_keywords = {
            'implementation': ['實現', '創建', '生成', 'implement', 'create', 'build'],
            'debugging': ['錯誤', '修復', 'bug', 'error', 'fix', 'debug'],
            'optimization': ['優化', '改進', '提升', 'optimize', 'improve', 'enhance'],
            'integration': ['集成', '整合', '連接', 'integrate', 'connect', 'combine'],
            'analysis': ['分析', '解釋', '理解', 'analyze', 'explain', 'understand']
        }
        
        for task_type, keywords in task_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                return task_type
                
        return 'general'
        
    def _extract_common_elements(self, conversations: List[Dict]) -> Dict[str, Any]:
        """提取共同元素"""
        common_elements = {
            'input_patterns': [],
            'output_structures': [],
            'key_concepts': [],
            'technologies': set()
        }
        
        for conv in conversations:
            # 提取輸入模式
            input_pattern = self._extract_input_pattern(conv['user_input'])
            if input_pattern:
                common_elements['input_patterns'].append(input_pattern)
                
            # 提取輸出結構
            output_structure = self._analyze_output_structure(conv['assistant_response'])
            common_elements['output_structures'].append(output_structure)
            
            # 提取技術關鍵詞
            tech_keywords = self._extract_technologies(conv)
            common_elements['technologies'].update(tech_keywords)
            
        return common_elements
        
    def _identify_success_patterns(self, conversations: List[Dict]) -> List[Dict]:
        """識別成功模式"""
        success_patterns = []
        
        for conv in conversations:
            # 假設有質量評分或用戶反饋
            quality_score = conv.get('quality_score', 0.5)
            
            if quality_score > 0.8:  # 高質量對話
                pattern = {
                    'input_structure': self._analyze_input_structure(conv['user_input']),
                    'response_features': self._extract_response_features(conv['assistant_response']),
                    'key_success_factors': self._identify_success_factors(conv)
                }
                success_patterns.append(pattern)
                
        return success_patterns
        
    def _find_optimization_opportunities(self, conversations: List[Dict]) -> List[Dict]:
        """發現優化機會"""
        opportunities = []
        
        for conv in conversations:
            # 分析可以優化的地方
            if self._can_be_optimized(conv):
                opportunity = {
                    'original_prompt': conv['user_input'],
                    'optimization_type': self._determine_optimization_type(conv),
                    'suggested_improvements': self._suggest_improvements(conv)
                }
                opportunities.append(opportunity)
                
        return opportunities
        
    def _learn_optimization_strategies(self, patterns: List[Dict]) -> Dict[str, Any]:
        """學習優化策略"""
        strategies = {}
        
        for pattern in patterns:
            task_type = pattern['task_type']
            
            # 基於成功模式創建優化策略
            strategy = {
                'prompt_template': self._create_optimal_prompt_template(pattern),
                'key_elements': pattern['common_elements']['key_concepts'],
                'best_practices': self._extract_best_practices(pattern),
                'avoid_patterns': self._identify_antipatterns(pattern)
            }
            
            strategies[task_type] = strategy
            
        return strategies
        
    async def _train_prompt_optimizer(self, conversations: List[Dict]):
        """訓練提示優化器"""
        print("🔧 訓練 DeepSWE 風格的提示優化器...")
        
        # 準備訓練數據
        training_data = []
        for conv in conversations:
            # 創建訓練樣本
            sample = {
                'original_prompt': conv['user_input'],
                'optimized_prompt': self._create_optimized_prompt(conv),
                'expected_output': conv['assistant_response'],
                'metadata': {
                    'task_type': self._classify_task(conv),
                    'quality_score': conv.get('quality_score', 0.5)
                }
            }
            training_data.append(sample)
            
        # 訓練優化模型（這裡是簡化版本）
        self.learned_prompts = self._train_simple_optimizer(training_data)
        
    def _create_optimized_prompt(self, conv: Dict) -> str:
        """創建優化的提示"""
        task_type = self._classify_task(conv)
        original_prompt = conv['user_input']
        
        # DeepSWE 風格的優化
        optimized = f"""<thinking>
任務類型: {task_type}
核心需求: {self._extract_core_requirements(original_prompt)}
上下文: PowerAutomation 開發
</thinking>

<task>
{original_prompt}
</task>

<requirements>
1. 提供完整的解決方案
2. 包含錯誤處理
3. 遵循最佳實踐
4. 考慮邊界情況
</requirements>"""
        
        return optimized
        
    def _train_simple_optimizer(self, training_data: List[Dict]) -> Dict[str, Any]:
        """訓練簡單的優化器"""
        # 這是一個簡化的實現
        # 實際應該使用機器學習模型
        
        learned_templates = {}
        
        # 按任務類型分組
        by_type = {}
        for sample in training_data:
            task_type = sample['metadata']['task_type']
            if task_type not in by_type:
                by_type[task_type] = []
            by_type[task_type].append(sample)
            
        # 為每種類型學習最佳模板
        for task_type, samples in by_type.items():
            # 選擇質量最高的樣本作為模板
            best_samples = sorted(
                samples, 
                key=lambda x: x['metadata']['quality_score'], 
                reverse=True
            )[:5]
            
            learned_templates[task_type] = {
                'templates': [s['optimized_prompt'] for s in best_samples],
                'average_quality': np.mean([s['metadata']['quality_score'] for s in best_samples])
            }
            
        return learned_templates
        
    def optimize_prompt_for_k2(self, user_input: str) -> str:
        """使用學習的模式優化 K2 提示"""
        # 分類任務
        task_type = self._classify_task({'user_input': user_input})
        
        # 獲取優化策略
        strategy = self.optimization_strategies.get(task_type, {})
        
        # 應用優化
        if task_type in self.learned_prompts:
            # 使用學習的模板
            templates = self.learned_prompts[task_type]['templates']
            if templates:
                # 選擇最相似的模板並適配
                template = templates[0]  # 簡化：選擇第一個
                optimized = self._adapt_template(template, user_input)
                return optimized
                
        # 默認優化
        return self._create_default_optimized_prompt(user_input, task_type)
        
    def _adapt_template(self, template: str, user_input: str) -> str:
        """適配模板到新輸入"""
        # 簡單的模板適配
        # 實際應該使用更智能的方法
        
        # 提取核心需求
        core_requirements = self._extract_core_requirements(user_input)
        
        # 替換模板中的佔位符
        adapted = template.replace('<task>', f'<task>\n{user_input}\n</task>')
        adapted = adapted.replace('核心需求:', f'核心需求: {core_requirements}')
        
        return adapted
        
    def _create_default_optimized_prompt(self, user_input: str, task_type: str) -> str:
        """創建默認優化提示"""
        return f"""<context>
項目: PowerAutomation
任務類型: {task_type}
優先級: 高質量、可維護性
</context>

<user_request>
{user_input}
</user_request>

請提供：
1. 完整的解決方案
2. 詳細的實現步驟
3. 必要的錯誤處理
4. 最佳實踐建議"""
        
    def _extract_core_requirements(self, text: str) -> str:
        """提取核心需求"""
        # 簡化實現
        # 提取動詞和關鍵名詞
        keywords = []
        
        action_words = ['實現', '創建', '修復', '優化', '集成', '部署']
        for word in action_words:
            if word in text:
                keywords.append(word)
                
        return ' '.join(keywords) if keywords else '處理用戶請求'
        
    def _extract_technologies(self, conv: Dict) -> set:
        """提取技術關鍵詞"""
        tech_keywords = {
            'python', 'javascript', 'typescript', 'react', 'vue',
            'mcp', 'claude', 'api', 'database', 'docker', 'k2'
        }
        
        text = (conv['user_input'] + ' ' + conv['assistant_response']).lower()
        found_techs = set()
        
        for tech in tech_keywords:
            if tech in text:
                found_techs.add(tech)
                
        return found_techs
        
    def get_learning_report(self) -> Dict[str, Any]:
        """獲取學習報告"""
        return {
            'learned_patterns': len(self.learning_patterns),
            'optimization_strategies': len(self.optimization_strategies),
            'prompt_templates': sum(
                len(v.get('templates', [])) 
                for v in self.learned_prompts.values()
            ),
            'supported_task_types': list(self.optimization_strategies.keys()),
            'last_updated': datetime.now().isoformat()
        }
        
    async def continuous_learning(self):
        """持續學習模式"""
        print("🔄 啟動持續學習模式...")
        
        while True:
            try:
                # 每小時學習一次新對話
                await asyncio.sleep(3600)
                
                # 獲取新對話
                new_conversations = await self.memoryrag.get_recent_conversations(hours=1)
                
                if new_conversations:
                    # 增量學習
                    await self._incremental_learning(new_conversations)
                    
                    print(f"✅ 學習了 {len(new_conversations)} 個新對話")
                    
            except Exception as e:
                print(f"❌ 持續學習錯誤: {e}")
                await asyncio.sleep(300)  # 5分鐘後重試
                
    async def _incremental_learning(self, new_conversations: List[Dict]):
        """增量學習"""
        # 分析新模式
        new_patterns = self._analyze_conversation_patterns(new_conversations)
        
        # 更新現有模式
        for new_pattern in new_patterns:
            self._update_pattern(new_pattern)
            
        # 更新優化策略
        self._update_optimization_strategies(new_patterns)
        
    def _update_pattern(self, new_pattern: Dict):
        """更新模式"""
        # 查找相同類型的模式
        for i, pattern in enumerate(self.learning_patterns):
            if pattern['task_type'] == new_pattern['task_type']:
                # 合併模式
                self.learning_patterns[i] = self._merge_patterns(pattern, new_pattern)
                return
                
        # 新模式
        self.learning_patterns.append(new_pattern)
        
    def _merge_patterns(self, old_pattern: Dict, new_pattern: Dict) -> Dict:
        """合併模式"""
        merged = {
            'task_type': old_pattern['task_type'],
            'common_elements': self._merge_common_elements(
                old_pattern['common_elements'],
                new_pattern['common_elements']
            ),
            'success_patterns': old_pattern['success_patterns'] + new_pattern['success_patterns'],
            'optimization_opportunities': old_pattern['optimization_opportunities'] + new_pattern['optimization_opportunities']
        }
        
        return merged
        
    def _merge_common_elements(self, old: Dict, new: Dict) -> Dict:
        """合併共同元素"""
        return {
            'input_patterns': old.get('input_patterns', []) + new.get('input_patterns', []),
            'output_structures': old.get('output_structures', []) + new.get('output_structures', []),
            'key_concepts': list(set(old.get('key_concepts', []) + new.get('key_concepts', []))),
            'technologies': old.get('technologies', set()) | new.get('technologies', set())
        }
        
    def _update_optimization_strategies(self, new_patterns: List[Dict]):
        """更新優化策略"""
        new_strategies = self._learn_optimization_strategies(new_patterns)
        
        # 合併策略
        for task_type, strategy in new_strategies.items():
            if task_type in self.optimization_strategies:
                # 更新現有策略
                self.optimization_strategies[task_type] = self._merge_strategies(
                    self.optimization_strategies[task_type],
                    strategy
                )
            else:
                # 新策略
                self.optimization_strategies[task_type] = strategy
                
    def _merge_strategies(self, old_strategy: Dict, new_strategy: Dict) -> Dict:
        """合併策略"""
        return {
            'prompt_template': new_strategy['prompt_template'],  # 使用新模板
            'key_elements': list(set(
                old_strategy.get('key_elements', []) + 
                new_strategy.get('key_elements', [])
            )),
            'best_practices': old_strategy.get('best_practices', []) + new_strategy.get('best_practices', []),
            'avoid_patterns': list(set(
                old_strategy.get('avoid_patterns', []) + 
                new_strategy.get('avoid_patterns', [])
            ))
        }
        
    # 以下是輔助方法的簡化實現
    def _extract_input_pattern(self, text: str) -> Dict:
        return {'length': len(text), 'has_code': '```' in text}
        
    def _analyze_output_structure(self, text: str) -> Dict:
        return {
            'has_code_blocks': '```' in text,
            'has_numbered_steps': bool(re.search(r'\d+\.', text)),
            'length': len(text)
        }
        
    def _analyze_input_structure(self, text: str) -> Dict:
        return {'tokens': len(text.split()), 'lines': len(text.split('\n'))}
        
    def _extract_response_features(self, text: str) -> List[str]:
        features = []
        if '```' in text:
            features.append('contains_code')
        if re.search(r'\d+\.', text):
            features.append('structured_steps')
        return features
        
    def _identify_success_factors(self, conv: Dict) -> List[str]:
        return ['clear_structure', 'complete_solution', 'error_handling']
        
    def _can_be_optimized(self, conv: Dict) -> bool:
        return len(conv['user_input']) < 50 or conv.get('quality_score', 0) < 0.7
        
    def _determine_optimization_type(self, conv: Dict) -> str:
        if len(conv['user_input']) < 50:
            return 'needs_more_context'
        return 'needs_structure'
        
    def _suggest_improvements(self, conv: Dict) -> List[str]:
        return ['add_context', 'specify_requirements', 'clarify_constraints']
        
    def _create_optimal_prompt_template(self, pattern: Dict) -> str:
        return f"<task_type>{pattern['task_type']}</task_type>\n{{user_request}}"
        
    def _extract_best_practices(self, pattern: Dict) -> List[str]:
        return ['provide_examples', 'include_error_handling', 'follow_conventions']
        
    def _identify_antipatterns(self, pattern: Dict) -> List[str]:
        return ['vague_requirements', 'missing_context', 'ambiguous_terms']


# 使用示例
async def main():
    """示例用法"""
    # 假設已有 MemoryRAG 實例
    from core.memoryrag.memory_os import MemoryRAG
    
    memoryrag = MemoryRAG()
    
    # 創建 DeepSWE 學習適配器
    adapter = DeepSWELearningAdapter(memoryrag)
    
    # 從對話歷史學習
    result = await adapter.learn_from_conversations()
    print(f"學習完成: {result}")
    
    # 使用學習結果優化提示
    user_input = "實現一個 MCP 來處理測試自動化"
    optimized = adapter.optimize_prompt_for_k2(user_input)
    print(f"\n優化後的提示:\n{optimized}")
    
    # 獲取學習報告
    report = adapter.get_learning_report()
    print(f"\n學習報告: {report}")
    
    # 啟動持續學習（可選）
    # await adapter.continuous_learning()


if __name__ == "__main__":
    import re
    asyncio.run(main())