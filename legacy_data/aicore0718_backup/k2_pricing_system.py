#!/usr/bin/env python3
"""
K2 定價系統
實現 K2 模型的定價機制：input 2元/M tokens, output 8元/M tokens
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import tiktoken
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class K2PricingConfig:
    """K2 定價配置"""
    input_price_per_million: float = 2.0    # 2元/M tokens
    output_price_per_million: float = 8.0   # 8元/M tokens
    currency: str = "CNY"
    
    # 折扣配置
    volume_discounts: Dict[int, float] = None  # {tokens: discount_rate}
    
    def __post_init__(self):
        if self.volume_discounts is None:
            self.volume_discounts = {
                1_000_000: 0.95,    # 100萬 tokens 95折
                5_000_000: 0.90,    # 500萬 tokens 9折
                10_000_000: 0.85,   # 1000萬 tokens 85折
                50_000_000: 0.80    # 5000萬 tokens 8折
            }

@dataclass
class TokenUsage:
    """Token 使用記錄"""
    timestamp: str
    request_id: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    discount_applied: float = 1.0
    metadata: Optional[Dict] = None

class K2PricingSystem:
    def __init__(self, config: K2PricingConfig = None):
        self.config = config or K2PricingConfig()
        self.usage_history: List[TokenUsage] = []
        self.total_usage = {
            'input_tokens': 0,
            'output_tokens': 0,
            'total_cost': 0
        }
        
        # 初始化 tokenizer（使用 GPT-3.5 的 tokenizer 作為參考）
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except:
            logger.warning("無法載入 tiktoken，將使用估算方式計算 tokens")
            self.tokenizer = None
    
    def count_tokens(self, text: str) -> int:
        """計算文本的 token 數"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # 簡單估算：平均每個字符約 0.75 個 token
            return int(len(text) * 0.75)
    
    def calculate_cost(self, input_text: str = None, output_text: str = None,
                      input_tokens: int = None, output_tokens: int = None,
                      request_id: str = None, metadata: Dict = None) -> TokenUsage:
        """計算使用成本"""
        # 計算 tokens
        if input_text and input_tokens is None:
            input_tokens = self.count_tokens(input_text)
        if output_text and output_tokens is None:
            output_tokens = self.count_tokens(output_text)
        
        input_tokens = input_tokens or 0
        output_tokens = output_tokens or 0
        
        # 計算基礎成本
        input_cost = (input_tokens / 1_000_000) * self.config.input_price_per_million
        output_cost = (output_tokens / 1_000_000) * self.config.output_price_per_million
        
        # 計算總 tokens 並應用批量折扣
        total_tokens = self.total_usage['input_tokens'] + self.total_usage['output_tokens'] + \
                      input_tokens + output_tokens
        
        discount = self._get_volume_discount(total_tokens)
        
        # 應用折扣
        input_cost *= discount
        output_cost *= discount
        total_cost = input_cost + output_cost
        
        # 創建使用記錄
        usage = TokenUsage(
            timestamp=datetime.now().isoformat(),
            request_id=request_id or f"req_{datetime.now().timestamp()}",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=round(input_cost, 4),
            output_cost=round(output_cost, 4),
            total_cost=round(total_cost, 4),
            discount_applied=discount,
            metadata=metadata
        )
        
        # 更新統計
        self._update_usage_stats(usage)
        
        return usage
    
    def _get_volume_discount(self, total_tokens: int) -> float:
        """獲取批量折扣"""
        discount = 1.0
        for threshold, rate in sorted(self.config.volume_discounts.items()):
            if total_tokens >= threshold:
                discount = rate
        return discount
    
    def _update_usage_stats(self, usage: TokenUsage):
        """更新使用統計"""
        self.usage_history.append(usage)
        self.total_usage['input_tokens'] += usage.input_tokens
        self.total_usage['output_tokens'] += usage.output_tokens
        self.total_usage['total_cost'] += usage.total_cost
    
    def get_usage_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """獲取使用摘要"""
        filtered_usage = self.usage_history
        
        if start_date:
            filtered_usage = [u for u in filtered_usage if u.timestamp >= start_date]
        if end_date:
            filtered_usage = [u for u in filtered_usage if u.timestamp <= end_date]
        
        if not filtered_usage:
            return {
                'period': {'start': start_date, 'end': end_date},
                'total_requests': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_cost': 0,
                'average_cost_per_request': 0
            }
        
        total_input = sum(u.input_tokens for u in filtered_usage)
        total_output = sum(u.output_tokens for u in filtered_usage)
        total_cost = sum(u.total_cost for u in filtered_usage)
        
        return {
            'period': {
                'start': start_date or filtered_usage[0].timestamp,
                'end': end_date or filtered_usage[-1].timestamp
            },
            'total_requests': len(filtered_usage),
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_input + total_output,
            'total_cost': round(total_cost, 2),
            'average_cost_per_request': round(total_cost / len(filtered_usage), 4),
            'current_discount': self._get_volume_discount(
                self.total_usage['input_tokens'] + self.total_usage['output_tokens']
            ),
            'currency': self.config.currency
        }
    
    def estimate_cost(self, input_text: str = None, output_text: str = None,
                     input_tokens: int = None, output_tokens: int = None) -> Dict:
        """估算成本（不記錄到使用歷史）"""
        # 計算 tokens
        if input_text and input_tokens is None:
            input_tokens = self.count_tokens(input_text)
        if output_text and output_tokens is None:
            output_tokens = self.count_tokens(output_text)
        
        input_tokens = input_tokens or 0
        output_tokens = output_tokens or 0
        
        # 計算成本
        input_cost = (input_tokens / 1_000_000) * self.config.input_price_per_million
        output_cost = (output_tokens / 1_000_000) * self.config.output_price_per_million
        
        # 獲取當前折扣
        current_total = self.total_usage['input_tokens'] + self.total_usage['output_tokens']
        current_discount = self._get_volume_discount(current_total)
        future_discount = self._get_volume_discount(current_total + input_tokens + output_tokens)
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': round(input_cost * future_discount, 4),
            'output_cost': round(output_cost * future_discount, 4),
            'total_cost': round((input_cost + output_cost) * future_discount, 4),
            'current_discount': current_discount,
            'future_discount': future_discount,
            'currency': self.config.currency
        }
    
    def export_usage_report(self, file_path: str = "k2_usage_report.json"):
        """導出使用報告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'config': asdict(self.config),
            'total_usage': self.total_usage,
            'usage_history': [asdict(u) for u in self.usage_history],
            'summary': self.get_usage_summary()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"使用報告已導出: {file_path}")
        return report
    
    def generate_invoice(self, customer_info: Dict, period: Dict = None) -> str:
        """生成發票"""
        summary = self.get_usage_summary(
            start_date=period.get('start') if period else None,
            end_date=period.get('end') if period else None
        )
        
        invoice = []
        invoice.append("=" * 60)
        invoice.append("K2 模型使用發票")
        invoice.append("=" * 60)
        invoice.append(f"\n發票日期: {datetime.now().strftime('%Y-%m-%d')}")
        invoice.append(f"發票編號: INV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # 客戶信息
        invoice.append("\n## 客戶信息")
        for key, value in customer_info.items():
            invoice.append(f"{key}: {value}")
        
        # 使用期間
        invoice.append("\n## 使用期間")
        invoice.append(f"開始: {summary['period']['start']}")
        invoice.append(f"結束: {summary['period']['end']}")
        
        # 使用詳情
        invoice.append("\n## 使用詳情")
        invoice.append(f"總請求數: {summary['total_requests']:,}")
        invoice.append(f"輸入 Tokens: {summary['total_input_tokens']:,}")
        invoice.append(f"輸出 Tokens: {summary['total_output_tokens']:,}")
        invoice.append(f"總 Tokens: {summary['total_tokens']:,}")
        
        # 費用明細
        invoice.append("\n## 費用明細")
        invoice.append(f"輸入單價: {self.config.input_price_per_million} 元/M tokens")
        invoice.append(f"輸出單價: {self.config.output_price_per_million} 元/M tokens")
        
        if summary['current_discount'] < 1.0:
            invoice.append(f"批量折扣: {(1 - summary['current_discount']) * 100:.0f}%")
        
        invoice.append(f"\n**應付總額: {summary['total_cost']} {summary['currency']}**")
        
        # 下一檔折扣提示
        current_total = self.total_usage['input_tokens'] + self.total_usage['output_tokens']
        next_threshold = None
        for threshold in sorted(self.config.volume_discounts.keys()):
            if threshold > current_total:
                next_threshold = threshold
                break
        
        if next_threshold:
            tokens_needed = next_threshold - current_total
            invoice.append(f"\n提示: 再使用 {tokens_needed:,} tokens 可享受更優惠折扣")
        
        invoice.append("\n" + "=" * 60)
        invoice.append("感謝您使用 K2 模型服務！")
        invoice.append("=" * 60)
        
        return "\n".join(invoice)

def demo():
    """演示 K2 定價系統"""
    print("🚀 K2 定價系統演示")
    print("=" * 60)
    
    # 創建定價系統
    pricing = K2PricingSystem()
    
    # 模擬幾次使用
    test_cases = [
        {
            'input': "請幫我分析這段代碼的性能問題",
            'output': "我分析了您的代碼，發現以下性能問題：\n1. 在循環中重複計算...\n2. 使用了低效的算法...\n3. 內存使用可以優化..."
        },
        {
            'input': "創建一個 Python Web 服務器",
            'output': "好的，我為您創建一個簡單的 Python Web 服務器：\n\n```python\nfrom flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello World!'\n\nif __name__ == '__main__':\n    app.run()\n```"
        },
        {
            'input_tokens': 1000,
            'output_tokens': 2000,
            'metadata': {'task': 'code_generation'}
        }
    ]
    
    print("\n## 使用記錄")
    for i, case in enumerate(test_cases, 1):
        usage = pricing.calculate_cost(**case)
        print(f"\n請求 {i}:")
        print(f"  輸入: {usage.input_tokens} tokens (￥{usage.input_cost})")
        print(f"  輸出: {usage.output_tokens} tokens (￥{usage.output_cost})")
        print(f"  總計: ￥{usage.total_cost}")
    
    # 顯示摘要
    summary = pricing.get_usage_summary()
    print(f"\n## 使用摘要")
    print(f"總請求數: {summary['total_requests']}")
    print(f"總 Tokens: {summary['total_tokens']:,}")
    print(f"總費用: ￥{summary['total_cost']}")
    print(f"平均每請求: ￥{summary['average_cost_per_request']}")
    
    # 成本估算
    print(f"\n## 成本估算")
    estimate = pricing.estimate_cost(
        input_tokens=100_000,
        output_tokens=50_000
    )
    print(f"10萬輸入 + 5萬輸出 tokens:")
    print(f"  預計費用: ￥{estimate['total_cost']}")
    print(f"  當前折扣: {(1 - estimate['current_discount']) * 100:.0f}%")
    
    # 生成發票
    print(f"\n## 示例發票")
    invoice = pricing.generate_invoice({
        '公司名稱': 'PowerAutomation 科技有限公司',
        '聯繫人': '張經理',
        '郵箱': 'zhang@powerautomation.ai'
    })
    print(invoice)
    
    # 導出報告
    pricing.export_usage_report("k2_demo_report.json")
    print(f"\n✅ 演示完成！報告已保存。")

if __name__ == "__main__":
    demo()