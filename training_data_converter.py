#!/usr/bin/env python3
"""
訓練數據轉換器 - 將收集的對話轉換為K2+DeepSWE訓練格式
分析MCP工具調用成功率
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from collections import defaultdict, Counter
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPToolAnalyzer:
    """MCP工具分析器 - 分析P0-P3優先級工具的支持情況"""
    
    def __init__(self):
        # 定義MCP工具優先級
        self.tool_priorities = {
            # P0 - 核心文件操作（最高優先級）
            "P0": {
                "Read": {"description": "讀取文件內容", "success_pattern": r'<function_calls>.*?Read.*?file_path.*?</function_calls>'},
                "Write": {"description": "寫入文件", "success_pattern": r'<function_calls>.*?Write.*?file_path.*?content.*?</function_calls>'},
                "Edit": {"description": "編輯文件", "success_pattern": r'<function_calls>.*?Edit.*?file_path.*?old_string.*?new_string.*?</function_calls>'},
                "MultiEdit": {"description": "批量編輯", "success_pattern": r'<function_calls>.*?MultiEdit.*?edits.*?</function_calls>'}
            },
            # P1 - 搜索和導航
            "P1": {
                "Grep": {"description": "搜索文件內容", "success_pattern": r'<function_calls>.*?Grep.*?pattern.*?</function_calls>'},
                "Glob": {"description": "查找文件", "success_pattern": r'<function_calls>.*?Glob.*?pattern.*?</function_calls>'},
                "LS": {"description": "列出目錄", "success_pattern": r'<function_calls>.*?LS.*?path.*?</function_calls>'},
                "Task": {"description": "任務搜索", "success_pattern": r'<function_calls>.*?Task.*?description.*?prompt.*?</function_calls>'}
            },
            # P2 - 執行和任務管理
            "P2": {
                "Bash": {"description": "執行命令", "success_pattern": r'<function_calls>.*?Bash.*?command.*?</function_calls>'},
                "TodoWrite": {"description": "管理待辦事項", "success_pattern": r'<function_calls>.*?TodoWrite.*?todos.*?</function_calls>'},
                "exit_plan_mode": {"description": "退出計劃模式", "success_pattern": r'<function_calls>.*?exit_plan_mode.*?</function_calls>'}
            },
            # P3 - 特殊文件和網絡
            "P3": {
                "NotebookRead": {"description": "讀取Jupyter筆記本", "success_pattern": r'<function_calls>.*?NotebookRead.*?notebook_path.*?</function_calls>'},
                "NotebookEdit": {"description": "編輯Jupyter筆記本", "success_pattern": r'<function_calls>.*?NotebookEdit.*?notebook_path.*?</function_calls>'},
                "WebFetch": {"description": "獲取網頁內容", "success_pattern": r'<function_calls>.*?WebFetch.*?url.*?</function_calls>'},
                "WebSearch": {"description": "網絡搜索", "success_pattern": r'<function_calls>.*?WebSearch.*?query.*?</function_calls>'}
            }
        }
        
        self.tool_stats = defaultdict(lambda: {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "syntax_errors": 0,
            "parameter_errors": 0
        })
        
    def analyze_tool_call(self, text: str) -> Dict:
        """分析單個工具調用"""
        results = {
            "tools_used": [],
            "priorities": [],
            "success": True,
            "errors": []
        }
        
        # 查找所有工具調用
        tool_calls = re.findall(r'<function_calls>.*?</function_calls>', text, re.DOTALL)
        
        for call in tool_calls:
            # 提取工具名稱
            tool_match = re.search(r'<invoke name="(\w+)">', call)
            if tool_match:
                tool_name = tool_match.group(1)
                results["tools_used"].append(tool_name)
                
                # 檢查工具優先級
                for priority, tools in self.tool_priorities.items():
                    if tool_name in tools:
                        results["priorities"].append(priority)
                        
                        # 驗證調用格式
                        if self._validate_tool_call(call, tool_name, tools[tool_name]):
                            self.tool_stats[tool_name]["successful_calls"] += 1
                        else:
                            self.tool_stats[tool_name]["failed_calls"] += 1
                            results["success"] = False
                            results["errors"].append(f"{tool_name}: 參數格式錯誤")
                
                self.tool_stats[tool_name]["total_calls"] += 1
        
        return results
    
    def _validate_tool_call(self, call: str, tool_name: str, tool_info: Dict) -> bool:
        """驗證工具調用格式"""
        # 檢查必要參數
        if tool_name == "Read":
            return bool(re.search(r'<parameter name="file_path">', call))
        elif tool_name == "Write":
            return bool(re.search(r'<parameter name="file_path">', call) and 
                       re.search(r'<parameter name="content">', call))
        elif tool_name == "Edit":
            return all(re.search(f'<parameter name="{param}">', call) 
                      for param in ["file_path", "old_string", "new_string"])
        elif tool_name == "Bash":
            return bool(re.search(r'<parameter name="command">', call))
        elif tool_name == "Grep":
            return bool(re.search(r'<parameter name="pattern">', call))
        # ... 其他工具的驗證
        
        return True  # 默認通過
    
    def get_priority_summary(self) -> Dict:
        """獲取按優先級分組的統計摘要"""
        summary = {}
        
        for priority, tools in self.tool_priorities.items():
            priority_stats = {
                "total_calls": 0,
                "success_rate": 0.0,
                "tools": {}
            }
            
            for tool_name in tools:
                stats = self.tool_stats[tool_name]
                if stats["total_calls"] > 0:
                    success_rate = stats["successful_calls"] / stats["total_calls"]
                    priority_stats["tools"][tool_name] = {
                        "calls": stats["total_calls"],
                        "success_rate": success_rate
                    }
                    priority_stats["total_calls"] += stats["total_calls"]
            
            # 計算優先級整體成功率
            total_success = sum(self.tool_stats[tool]["successful_calls"] for tool in tools)
            total_calls = sum(self.tool_stats[tool]["total_calls"] for tool in tools)
            
            if total_calls > 0:
                priority_stats["success_rate"] = total_success / total_calls
            
            summary[priority] = priority_stats
        
        return summary

class TrainingDataConverter:
    """訓練數據轉換器"""
    
    def __init__(self, input_dir: str = "data/enhanced_extracted_chats"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path("data/training_data")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.tool_analyzer = MCPToolAnalyzer()
        self.stats = {
            "total_conversations": 0,
            "total_samples": 0,
            "code_samples": 0,
            "tool_samples": 0,
            "avg_message_length": 0,
            "priority_distribution": defaultdict(int)
        }
        
    def convert_conversations(self):
        """轉換所有對話數據"""
        logger.info("🔄 開始轉換對話數據為訓練格式...")
        
        # 獲取所有對話文件
        conversation_files = list(self.input_dir.glob("*.json"))
        logger.info(f"📁 找到 {len(conversation_files)} 個對話文件")
        
        all_samples = []
        
        for file_path in conversation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
                
                # 轉換單個對話
                samples = self._convert_conversation(conversation)
                all_samples.extend(samples)
                
                self.stats["total_conversations"] += 1
                
            except Exception as e:
                logger.warning(f"處理文件 {file_path} 時出錯: {e}")
        
        # 保存轉換後的數據
        self._save_training_data(all_samples)
        
        # 生成報告
        self._generate_report()
    
    def _convert_conversation(self, conversation: Dict) -> List[Dict]:
        """轉換單個對話為訓練樣本"""
        samples = []
        messages = conversation.get("messages", [])
        
        # 確保消息成對出現
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages):
                user_msg = messages[i]
                assistant_msg = messages[i + 1]
                
                # 確保角色正確
                if user_msg.get("role") == "user" and assistant_msg.get("role") == "assistant":
                    sample = self._create_training_sample(user_msg, assistant_msg)
                    if sample:
                        samples.append(sample)
                        self.stats["total_samples"] += 1
        
        return samples
    
    def _create_training_sample(self, user_msg: Dict, assistant_msg: Dict) -> Dict:
        """創建單個訓練樣本"""
        user_content = user_msg.get("content", "")
        assistant_content = assistant_msg.get("content", "")
        
        # 分析工具調用
        tool_analysis = self.tool_analyzer.analyze_tool_call(assistant_content)
        
        # 檢測代碼內容
        has_code = bool(re.search(r'```[\w]*\n.*?```', assistant_content, re.DOTALL))
        
        # 提取代碼塊
        code_blocks = re.findall(r'```([\w]*)\n(.*?)```', assistant_content, re.DOTALL)
        
        # 統計
        if has_code:
            self.stats["code_samples"] += 1
        if tool_analysis["tools_used"]:
            self.stats["tool_samples"] += 1
        for priority in tool_analysis["priorities"]:
            self.stats["priority_distribution"][priority] += 1
        
        return {
            "id": f"sample_{self.stats['total_samples']}",
            "input": user_content,
            "output": assistant_content,
            "metadata": {
                "has_code": has_code,
                "code_blocks": [{"language": lang, "code": code} for lang, code in code_blocks],
                "tools_used": tool_analysis["tools_used"],
                "tool_priorities": tool_analysis["priorities"],
                "tool_success": tool_analysis["success"],
                "message_length": len(assistant_content),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _save_training_data(self, samples: List[Dict]):
        """保存訓練數據"""
        # 按批次保存
        batch_size = 1000
        for i in range(0, len(samples), batch_size):
            batch = samples[i:i + batch_size]
            output_file = self.output_dir / f"training_batch_{i // batch_size}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "samples": batch,
                    "metadata": {
                        "batch_index": i // batch_size,
                        "sample_count": len(batch),
                        "created_at": datetime.now().isoformat()
                    }
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 保存訓練批次 {i // batch_size}: {len(batch)} 個樣本")
    
    def _generate_report(self):
        """生成轉換報告"""
        # 獲取工具優先級統計
        priority_summary = self.tool_analyzer.get_priority_summary()
        
        report = {
            "conversion_stats": self.stats,
            "tool_analysis": {
                "priority_summary": priority_summary,
                "detailed_stats": dict(self.tool_analyzer.tool_stats)
            },
            "recommendations": self._generate_recommendations(priority_summary)
        }
        
        # 保存報告
        report_path = self.output_dir / "conversion_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        self._print_summary(priority_summary)
    
    def _generate_recommendations(self, priority_summary: Dict) -> List[str]:
        """生成優化建議"""
        recommendations = []
        
        # P0工具建議
        p0_success = priority_summary.get("P0", {}).get("success_rate", 0)
        if p0_success < 0.9:
            recommendations.append(
                f"⚠️ P0核心工具成功率偏低 ({p0_success:.1%})，建議重點優化文件操作訓練"
            )
        
        # P1工具建議
        p1_success = priority_summary.get("P1", {}).get("success_rate", 0)
        if p1_success < 0.8:
            recommendations.append(
                f"🔍 P1搜索工具成功率需提升 ({p1_success:.1%})，加強搜索模式訓練"
            )
        
        # P2工具建議
        p2_tools = priority_summary.get("P2", {}).get("tools", {})
        if "Bash" in p2_tools and p2_tools["Bash"]["success_rate"] < 0.85:
            recommendations.append(
                "💻 Bash命令執行成功率需改進，建議增加命令語法訓練"
            )
        
        # 整體建議
        total_tool_calls = sum(p["total_calls"] for p in priority_summary.values())
        if total_tool_calls < 1000:
            recommendations.append(
                "📊 工具調用樣本量偏少，建議收集更多包含工具調用的對話"
            )
        
        return recommendations
    
    def _print_summary(self, priority_summary: Dict):
        """打印轉換摘要"""
        print("\n" + "=" * 60)
        print("📊 訓練數據轉換摘要")
        print("=" * 60)
        
        print(f"\n📈 基本統計:")
        print(f"  總對話數: {self.stats['total_conversations']}")
        print(f"  總樣本數: {self.stats['total_samples']}")
        print(f"  包含代碼: {self.stats['code_samples']} ({self.stats['code_samples']/max(1, self.stats['total_samples'])*100:.1f}%)")
        print(f"  包含工具: {self.stats['tool_samples']} ({self.stats['tool_samples']/max(1, self.stats['total_samples'])*100:.1f}%)")
        
        print(f"\n🛠️ MCP工具優先級分析:")
        for priority in ["P0", "P1", "P2", "P3"]:
            if priority in priority_summary:
                data = priority_summary[priority]
                print(f"\n  {priority} - {['核心文件操作', '搜索和導航', '執行和任務', '特殊文件'][int(priority[1])]}:")
                print(f"    總調用次數: {data['total_calls']}")
                print(f"    成功率: {data['success_rate']:.1%}")
                
                # 顯示前3個最常用的工具
                top_tools = sorted(data['tools'].items(), 
                                 key=lambda x: x[1]['calls'], 
                                 reverse=True)[:3]
                
                for tool_name, tool_data in top_tools:
                    print(f"    - {tool_name}: {tool_data['calls']} 次調用, "
                          f"{tool_data['success_rate']:.1%} 成功率")
        
        print("\n" + "=" * 60)

def main():
    """主函數"""
    converter = TrainingDataConverter()
    converter.convert_conversations()

if __name__ == "__main__":
    main()