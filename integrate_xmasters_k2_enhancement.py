#!/usr/bin/env python3
"""
X-Masters + K2 增強整合方案
使用X-Masters深度推理能力增強K2的工具調用體驗
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# 模擬的導入（實際環境中需要調整）
class XMastersK2Integration:
    """X-Masters與K2整合類"""
    
    def __init__(self):
        self.xmasters_engine = None  # X-Masters引擎
        self.k2_client = None        # K2客戶端
        self.tool_mapping = {}       # 工具映射
        self.reasoning_cache = {}    # 推理緩存
        
    async def initialize(self):
        """初始化整合系統"""
        print("🚀 初始化X-Masters + K2增強系統")
        print("="*70)
        
        # 初始化組件
        await self._init_xmasters()
        await self._init_k2_enhancement()
        await self._setup_tool_mapping()
        
        print("✅ 整合系統初始化完成")
        
    async def _init_xmasters(self):
        """初始化X-Masters"""
        print("\n1️⃣ 初始化X-Masters深度推理引擎")
        # 實際應調用: self.xmasters_engine = XMastersEngine()
        # await self.xmasters_engine.initialize()
        
        # 模擬初始化
        self.xmasters_agents = {
            "tool_reasoning_agent": {
                "name": "工具推理智能體",
                "capabilities": ["tool_selection", "parameter_inference", "result_validation"],
                "specialization": "工具調用優化"
            },
            "context_agent": {
                "name": "上下文分析智能體",
                "capabilities": ["context_extraction", "intent_recognition", "requirement_analysis"],
                "specialization": "理解用戶意圖"
            },
            "correction_agent": {
                "name": "錯誤修正智能體",
                "capabilities": ["error_detection", "parameter_correction", "retry_strategy"],
                "specialization": "工具調用修正"
            }
        }
        print(f"   ✅ 初始化{len(self.xmasters_agents)}個專業智能體")
        
    async def _init_k2_enhancement(self):
        """初始化K2增強"""
        print("\n2️⃣ 配置K2工具調用增強")
        
        # K2工具調用增強配置
        self.k2_enhancement_config = {
            "tool_call_optimization": {
                "enabled": True,
                "use_xmasters_reasoning": True,
                "confidence_threshold": 0.7
            },
            "parameter_inference": {
                "enabled": True,
                "use_context_analysis": True,
                "auto_correct": True
            },
            "error_handling": {
                "enabled": True,
                "max_retries": 3,
                "use_correction_agent": True
            }
        }
        print("   ✅ K2工具調用增強配置完成")
        
    async def _setup_tool_mapping(self):
        """設置工具映射"""
        print("\n3️⃣ 設置智能工具映射")
        
        # 增強的工具映射
        self.tool_mapping = {
            # 文件操作工具
            "file_operations": {
                "read_file": {
                    "description": "讀取文件內容",
                    "parameters": ["file_path"],
                    "xmasters_enhancement": {
                        "parameter_inference": True,
                        "context_aware": True,
                        "error_recovery": True
                    }
                },
                "write_file": {
                    "description": "寫入文件",
                    "parameters": ["file_path", "content"],
                    "xmasters_enhancement": {
                        "content_validation": True,
                        "path_suggestion": True
                    }
                }
            },
            # 代碼分析工具
            "code_analysis": {
                "analyze_code": {
                    "description": "分析代碼結構和質量",
                    "parameters": ["code", "language", "analysis_type"],
                    "xmasters_enhancement": {
                        "language_detection": True,
                        "type_recommendation": True
                    }
                },
                "refactor_code": {
                    "description": "重構代碼",
                    "parameters": ["code", "refactor_type", "options"],
                    "xmasters_enhancement": {
                        "best_practice_check": True,
                        "impact_analysis": True
                    }
                }
            },
            # 搜索工具
            "search_tools": {
                "search_codebase": {
                    "description": "搜索代碼庫",
                    "parameters": ["query", "file_pattern", "options"],
                    "xmasters_enhancement": {
                        "query_expansion": True,
                        "relevance_ranking": True
                    }
                }
            }
        }
        
        print(f"   ✅ 映射{sum(len(cat) for cat in self.tool_mapping.values())}個增強工具")
        
    async def enhance_k2_tool_call(self, user_input: str, k2_response: Dict[str, Any]) -> Dict[str, Any]:
        """增強K2的工具調用"""
        print("\n🔧 增強K2工具調用")
        print(f"用戶輸入: {user_input[:100]}...")
        
        # 1. 使用X-Masters分析用戶意圖
        intent_analysis = await self._analyze_user_intent(user_input)
        print(f"\n📊 意圖分析結果:")
        print(f"   - 主要意圖: {intent_analysis['primary_intent']}")
        print(f"   - 所需工具: {intent_analysis['required_tools']}")
        
        # 2. 檢查K2的工具調用
        k2_tool_calls = self._extract_k2_tool_calls(k2_response)
        print(f"\n🤖 K2原始工具調用: {len(k2_tool_calls)}個")
        
        # 3. 使用X-Masters優化工具調用
        optimized_calls = await self._optimize_tool_calls(
            intent_analysis, 
            k2_tool_calls,
            user_input
        )
        
        # 4. 生成增強響應
        enhanced_response = {
            "original_k2_response": k2_response,
            "xmasters_enhancement": {
                "intent_analysis": intent_analysis,
                "optimized_tool_calls": optimized_calls,
                "confidence": self._calculate_confidence(intent_analysis, optimized_calls),
                "recommendations": self._generate_recommendations(intent_analysis, optimized_calls)
            },
            "final_tool_calls": optimized_calls,
            "execution_plan": self._create_execution_plan(optimized_calls)
        }
        
        return enhanced_response
        
    async def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """使用X-Masters分析用戶意圖"""
        # 模擬X-Masters的深度意圖分析
        await asyncio.sleep(0.1)
        
        # 簡化的意圖分析
        intent = {
            "primary_intent": "unknown",
            "confidence": 0.0,
            "required_tools": [],
            "context_requirements": [],
            "parameters_needed": {}
        }
        
        # 基於關鍵詞的意圖識別
        if "讀取" in user_input or "打開" in user_input or "查看" in user_input:
            intent["primary_intent"] = "file_read"
            intent["required_tools"] = ["read_file"]
            intent["confidence"] = 0.9
        elif "寫入" in user_input or "保存" in user_input or "創建" in user_input:
            intent["primary_intent"] = "file_write"
            intent["required_tools"] = ["write_file"]
            intent["confidence"] = 0.85
        elif "分析" in user_input or "檢查" in user_input:
            intent["primary_intent"] = "code_analysis"
            intent["required_tools"] = ["analyze_code"]
            intent["confidence"] = 0.8
        elif "搜索" in user_input or "查找" in user_input:
            intent["primary_intent"] = "search"
            intent["required_tools"] = ["search_codebase"]
            intent["confidence"] = 0.85
            
        # 提取可能的參數
        if ".py" in user_input or ".js" in user_input or ".html" in user_input:
            intent["context_requirements"].append("file_path_mentioned")
            intent["parameters_needed"]["file_path"] = self._extract_file_path(user_input)
            
        return intent
        
    def _extract_file_path(self, text: str) -> Optional[str]:
        """提取文件路徑"""
        import re
        # 簡單的文件路徑提取
        pattern = r'[^\s]+\.(py|js|html|css|json|md|txt)'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
        
    def _extract_k2_tool_calls(self, k2_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取K2的工具調用"""
        # 模擬K2工具調用提取
        # 實際應解析K2的響應格式
        return k2_response.get("tool_calls", [])
        
    async def _optimize_tool_calls(self, intent: Dict[str, Any], 
                                  k2_calls: List[Dict[str, Any]], 
                                  user_input: str) -> List[Dict[str, Any]]:
        """使用X-Masters優化工具調用"""
        optimized_calls = []
        
        # 如果K2沒有生成工具調用，但意圖分析表明需要
        if not k2_calls and intent["required_tools"]:
            print("\n⚠️ K2未生成工具調用，X-Masters補充生成...")
            
            for tool_name in intent["required_tools"]:
                # 使用X-Masters推理參數
                parameters = await self._infer_tool_parameters(
                    tool_name, 
                    user_input, 
                    intent
                )
                
                optimized_calls.append({
                    "tool": tool_name,
                    "parameters": parameters,
                    "source": "xmasters_generated",
                    "confidence": intent["confidence"],
                    "reasoning": f"基於意圖分析，需要調用{tool_name}"
                })
                
        # 優化K2的工具調用
        else:
            for call in k2_calls:
                # 使用X-Masters驗證和修正參數
                validated_params = await self._validate_and_correct_parameters(
                    call["tool"],
                    call.get("parameters", {}),
                    intent
                )
                
                optimized_calls.append({
                    "tool": call["tool"],
                    "parameters": validated_params,
                    "source": "k2_optimized",
                    "confidence": self._calculate_tool_confidence(call, intent),
                    "corrections": validated_params.get("_corrections", [])
                })
                
        return optimized_calls
        
    async def _infer_tool_parameters(self, tool_name: str, 
                                    user_input: str, 
                                    intent: Dict[str, Any]) -> Dict[str, Any]:
        """使用X-Masters推理工具參數"""
        # 模擬參數推理
        parameters = {}
        
        if tool_name == "read_file":
            # 從用戶輸入推理文件路徑
            file_path = intent["parameters_needed"].get("file_path")
            if not file_path:
                # 使用上下文推理
                file_path = await self._infer_file_from_context(user_input)
            parameters["file_path"] = file_path
            
        elif tool_name == "analyze_code":
            # 推理分析類型
            if "性能" in user_input:
                parameters["analysis_type"] = "performance"
            elif "安全" in user_input:
                parameters["analysis_type"] = "security"
            else:
                parameters["analysis_type"] = "general"
                
        return parameters
        
    async def _infer_file_from_context(self, user_input: str) -> str:
        """從上下文推理文件"""
        # 簡化的上下文推理
        if "剛才" in user_input or "上一個" in user_input:
            # 返回最近訪問的文件
            return "last_accessed_file.py"
        else:
            # 返回當前文件
            return "current_file.py"
            
    async def _validate_and_correct_parameters(self, tool_name: str,
                                              parameters: Dict[str, Any],
                                              intent: Dict[str, Any]) -> Dict[str, Any]:
        """驗證和修正參數"""
        validated = parameters.copy()
        corrections = []
        
        # 檢查必需參數
        if tool_name == "read_file" and not validated.get("file_path"):
            # 嘗試從意圖中獲取
            if intent["parameters_needed"].get("file_path"):
                validated["file_path"] = intent["parameters_needed"]["file_path"]
                corrections.append("補充缺失的file_path參數")
                
        # 修正參數格式
        if tool_name == "write_file" and validated.get("content"):
            # 確保內容格式正確
            if isinstance(validated["content"], list):
                validated["content"] = "\n".join(validated["content"])
                corrections.append("將content從列表轉換為字符串")
                
        validated["_corrections"] = corrections
        return validated
        
    def _calculate_confidence(self, intent: Dict[str, Any], 
                            tool_calls: List[Dict[str, Any]]) -> float:
        """計算整體置信度"""
        if not tool_calls:
            return 0.0
            
        # 基於意圖匹配和工具調用質量計算
        intent_confidence = intent.get("confidence", 0.5)
        tool_confidence = sum(call.get("confidence", 0.5) for call in tool_calls) / len(tool_calls)
        
        return (intent_confidence + tool_confidence) / 2
        
    def _calculate_tool_confidence(self, tool_call: Dict[str, Any], 
                                 intent: Dict[str, Any]) -> float:
        """計算單個工具調用的置信度"""
        base_confidence = 0.5
        
        # 如果工具匹配意圖，增加置信度
        if tool_call["tool"] in intent.get("required_tools", []):
            base_confidence += 0.3
            
        # 如果參數完整，增加置信度
        if all(param for param in tool_call.get("parameters", {}).values()):
            base_confidence += 0.2
            
        return min(base_confidence, 1.0)
        
    def _generate_recommendations(self, intent: Dict[str, Any], 
                                tool_calls: List[Dict[str, Any]]) -> List[str]:
        """生成優化建議"""
        recommendations = []
        
        # 檢查工具調用完整性
        if intent["required_tools"]:
            called_tools = [call["tool"] for call in tool_calls]
            missing_tools = set(intent["required_tools"]) - set(called_tools)
            if missing_tools:
                recommendations.append(f"建議添加工具調用: {', '.join(missing_tools)}")
                
        # 檢查參數質量
        for call in tool_calls:
            if call.get("corrections"):
                recommendations.append(f"{call['tool']}參數已自動修正")
                
        # 性能建議
        if len(tool_calls) > 3:
            recommendations.append("建議批量執行工具調用以提高效率")
            
        return recommendations
        
    def _create_execution_plan(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """創建執行計劃"""
        return {
            "total_steps": len(tool_calls),
            "estimated_time": len(tool_calls) * 0.5,  # 估計執行時間
            "execution_order": [
                {
                    "step": i + 1,
                    "tool": call["tool"],
                    "ready": True,
                    "dependencies": []
                }
                for i, call in enumerate(tool_calls)
            ],
            "parallelizable": self._check_parallelizable(tool_calls)
        }
        
    def _check_parallelizable(self, tool_calls: List[Dict[str, Any]]) -> bool:
        """檢查是否可並行執行"""
        # 簡單規則：如果都是讀取操作，可以並行
        read_only_tools = ["read_file", "analyze_code", "search_codebase"]
        return all(call["tool"] in read_only_tools for call in tool_calls)

async def demonstrate_xmasters_k2_enhancement():
    """演示X-Masters增強K2工具調用"""
    print("🎯 X-Masters + K2 工具調用增強演示")
    print("="*70)
    
    # 初始化整合系統
    integration = XMastersK2Integration()
    await integration.initialize()
    
    # 測試場景
    test_scenarios = [
        {
            "name": "場景1: K2未能識別工具調用",
            "user_input": "幫我查看一下config.json文件的內容",
            "k2_response": {
                "text": "好的，我會幫您查看config.json文件",
                "tool_calls": []  # K2沒有生成工具調用
            }
        },
        {
            "name": "場景2: K2工具調用參數不完整",
            "user_input": "分析一下這個Python文件的代碼質量",
            "k2_response": {
                "text": "我來分析代碼質量",
                "tool_calls": [{
                    "tool": "analyze_code",
                    "parameters": {
                        "code": "# some code",
                        # 缺少 language 和 analysis_type
                    }
                }]
            }
        },
        {
            "name": "場景3: 複雜多步驟任務",
            "user_input": "搜索所有包含'error'的Python文件，然後分析它們的錯誤處理",
            "k2_response": {
                "text": "我會搜索並分析錯誤處理",
                "tool_calls": [{
                    "tool": "search_codebase",
                    "parameters": {"query": "error"}
                    # 缺少後續分析步驟
                }]
            }
        }
    ]
    
    # 執行測試
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*70}")
        print(f"🧪 {scenario['name']}")
        print(f"{'='*70}")
        
        # 增強K2響應
        enhanced = await integration.enhance_k2_tool_call(
            scenario["user_input"],
            scenario["k2_response"]
        )
        
        # 顯示結果
        print(f"\n📈 增強結果:")
        print(f"   原始K2工具調用數: {len(scenario['k2_response']['tool_calls'])}")
        print(f"   增強後工具調用數: {len(enhanced['final_tool_calls'])}")
        print(f"   整體置信度: {enhanced['xmasters_enhancement']['confidence']:.2f}")
        
        print(f"\n🔧 優化的工具調用:")
        for call in enhanced['final_tool_calls']:
            print(f"   - {call['tool']} (來源: {call['source']}, 置信度: {call['confidence']:.2f})")
            print(f"     參數: {json.dumps(call['parameters'], ensure_ascii=False)}")
            if call.get('corrections'):
                print(f"     修正: {', '.join(call['corrections'])}")
                
        print(f"\n💡 優化建議:")
        for rec in enhanced['xmasters_enhancement']['recommendations']:
            print(f"   - {rec}")
            
        print(f"\n📋 執行計劃:")
        plan = enhanced['execution_plan']
        print(f"   總步驟: {plan['total_steps']}")
        print(f"   預計時間: {plan['estimated_time']:.1f}秒")
        print(f"   可並行: {'是' if plan['parallelizable'] else '否'}")
    
    # 總結
    print(f"\n{'='*70}")
    print("📊 增強效果總結")
    print("="*70)
    print("\n✅ X-Masters為K2提供的增強能力:")
    print("1. 🎯 深度意圖理解 - 準確識別用戶真實需求")
    print("2. 🔧 智能參數推理 - 自動補全缺失參數")
    print("3. 🔄 錯誤自動修正 - 修正參數格式和類型")
    print("4. 📈 多步驟規劃 - 將複雜任務分解為工具調用序列")
    print("5. 🚀 執行優化 - 識別可並行執行的工具調用")
    
    print("\n🎯 集成架構:")
    print("```")
    print("用戶輸入 → K2生成初步響應 → X-Masters深度分析")
    print("    ↓           ↓                    ↓")
    print("    ↓      工具調用嘗試         意圖理解+參數推理")
    print("    ↓           ↓                    ↓")
    print("    └──────────→ 增強合併 ←──────────┘")
    print("                    ↓")
    print("              優化的工具調用")
    print("                    ↓")
    print("              執行並返回結果")
    print("```")

if __name__ == "__main__":
    asyncio.run(demonstrate_xmasters_k2_enhancement())