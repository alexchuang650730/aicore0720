#!/usr/bin/env python3
"""
AG-UI/SmartUI 增強系統
專注於規範遵循、規格覆蓋率和測試覆蓋率
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

@dataclass
class SmartUICompliance:
    """SmartUI 規範遵循度"""
    naming_convention: float  # 命名規範
    component_structure: float  # 組件結構
    state_management: float  # 狀態管理
    accessibility: float  # 無障礙支持
    performance: float  # 性能優化
    documentation: float  # 文檔完整性

@dataclass
class SpecCoverage:
    """規格覆蓋率"""
    technical_spec_coverage: float  # 技術規格覆蓋率
    experience_spec_coverage: float  # 體驗規格覆蓋率
    uncovered_technical_specs: List[str]
    uncovered_experience_specs: List[str]

@dataclass
class TestCoverage:
    """測試覆蓋率"""
    technical_test_coverage: float  # 技術測試覆蓋率
    experience_test_coverage: float  # 體驗測試覆蓋率
    unit_test_coverage: float
    integration_test_coverage: float
    e2e_test_coverage: float

class SmartUIStandard:
    """SmartUI 標準規範"""
    
    # 命名規範
    NAMING_PATTERNS = {
        "component": r"^[A-Z][a-zA-Z0-9]*$",  # PascalCase
        "function": r"^(handle|on|get|set|is|has)[A-Z][a-zA-Z0-9]*$",  # camelCase with prefix
        "constant": r"^[A-Z_]+$",  # UPPER_SNAKE_CASE
        "interface": r"^I[A-Z][a-zA-Z0-9]*$",  # IPascalCase
        "type": r"^T[A-Z][a-zA-Z0-9]*$"  # TPascalCase
    }
    
    # 組件結構規範
    COMPONENT_STRUCTURE = {
        "imports": ["React imports", "Third-party imports", "Local imports"],
        "types": ["Interface definitions", "Type definitions"],
        "constants": ["Constants outside component"],
        "component": ["Props interface", "Component function", "Hooks", "Handlers", "Render"],
        "exports": ["Default export or named exports"]
    }
    
    # 必需的無障礙屬性
    ACCESSIBILITY_REQUIREMENTS = [
        "aria-label",
        "role",
        "tabIndex",
        "alt (for images)",
        "keyboard navigation"
    ]
    
    # 性能最佳實踐
    PERFORMANCE_PRACTICES = [
        "React.memo for pure components",
        "useMemo for expensive calculations",
        "useCallback for event handlers",
        "lazy loading for routes",
        "code splitting"
    ]

class AGUISmartUISystem:
    """AG-UI/SmartUI 增強系統"""
    
    def __init__(self):
        self.root_path = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        self.standards = SmartUIStandard()
        self.compliance_threshold = 80.0  # 80% 合規閾值
        
    async def analyze_smartui_compliance(self, component_path: Path) -> SmartUICompliance:
        """分析 SmartUI 規範遵循度"""
        print(f"🔍 分析 SmartUI 規範遵循: {component_path.name}")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 1. 檢查命名規範
        naming_score = self._check_naming_convention(code)
        
        # 2. 檢查組件結構
        structure_score = self._check_component_structure(code)
        
        # 3. 檢查狀態管理
        state_score = self._check_state_management(code)
        
        # 4. 檢查無障礙支持
        a11y_score = self._check_accessibility(code)
        
        # 5. 檢查性能優化
        perf_score = self._check_performance_practices(code)
        
        # 6. 檢查文檔
        doc_score = self._check_documentation(code)
        
        return SmartUICompliance(
            naming_convention=naming_score,
            component_structure=structure_score,
            state_management=state_score,
            accessibility=a11y_score,
            performance=perf_score,
            documentation=doc_score
        )
    
    def _check_naming_convention(self, code: str) -> float:
        """檢查命名規範"""
        violations = 0
        checks = 0
        
        # 檢查組件名稱
        component_pattern = r'(?:function|const)\s+([A-Z][a-zA-Z0-9]*)\s*(?:\(|=)'
        components = re.findall(component_pattern, code)
        for comp in components:
            checks += 1
            if not re.match(self.standards.NAMING_PATTERNS["component"], comp):
                violations += 1
        
        # 檢查函數名稱
        function_pattern = r'const\s+([a-z][a-zA-Z0-9]*)\s*='
        functions = re.findall(function_pattern, code)
        for func in functions:
            checks += 1
            if func.startswith(('handle', 'on', 'get', 'set', 'is', 'has')):
                if not re.match(self.standards.NAMING_PATTERNS["function"], func):
                    violations += 1
        
        # 檢查常量
        const_pattern = r'const\s+([A-Z_]+)\s*='
        constants = re.findall(const_pattern, code)
        for const in constants:
            checks += 1
            if not re.match(self.standards.NAMING_PATTERNS["constant"], const):
                violations += 1
        
        score = ((checks - violations) / checks * 100) if checks > 0 else 100
        return score
    
    def _check_component_structure(self, code: str) -> float:
        """檢查組件結構"""
        structure_score = 100.0
        penalties = 0
        
        lines = code.split('\n')
        
        # 檢查 import 順序
        import_lines = [i for i, line in enumerate(lines) if line.strip().startswith('import')]
        if import_lines:
            # 簡化檢查：React imports 應該在最前面
            first_import = lines[import_lines[0]]
            if 'react' not in first_import.lower():
                penalties += 10
        
        # 檢查是否有 Props 接口定義
        if 'Props' not in code and 'props:' not in code:
            penalties += 20
        
        # 檢查是否有適當的導出
        if 'export' not in code:
            penalties += 10
        
        structure_score -= penalties
        return max(0, structure_score)
    
    def _check_state_management(self, code: str) -> float:
        """檢查狀態管理"""
        state_count = code.count('useState')
        reducer_count = code.count('useReducer')
        context_count = code.count('useContext')
        
        # 評分邏輯
        score = 100.0
        
        # 如果有超過 5 個 useState，建議使用 useReducer
        if state_count > 5 and reducer_count == 0:
            score -= 20
        
        # 如果有複雜狀態但沒有使用 Context
        if state_count > 3 and context_count == 0:
            score -= 10
        
        # 檢查是否有狀態提升的跡象
        if 'prop drilling' in code.lower() or code.count('props.') > 20:
            score -= 15
        
        return max(0, score)
    
    def _check_accessibility(self, code: str) -> float:
        """檢查無障礙支持"""
        a11y_score = 100.0
        penalties = 0
        
        # 檢查按鈕是否有 aria-label
        button_count = code.count('<button') + code.count('<Button')
        aria_label_count = code.count('aria-label')
        if button_count > 0 and aria_label_count < button_count:
            penalties += 20
        
        # 檢查圖片是否有 alt 屬性
        img_count = code.count('<img')
        alt_count = code.count('alt=')
        if img_count > 0 and alt_count < img_count:
            penalties += 20
        
        # 檢查是否有鍵盤事件處理
        if 'onClick' in code and 'onKeyPress' not in code and 'onKeyDown' not in code:
            penalties += 15
        
        # 檢查是否有 role 屬性
        if 'role=' not in code and ('<div' in code or '<span' in code):
            penalties += 10
        
        a11y_score -= penalties
        return max(0, a11y_score)
    
    def _check_performance_practices(self, code: str) -> float:
        """檢查性能優化實踐"""
        perf_score = 100.0
        
        # 檢查是否使用了性能優化 hooks
        has_memo = 'React.memo' in code or 'memo(' in code
        has_useMemo = 'useMemo' in code
        has_useCallback = 'useCallback' in code
        
        # 評分邏輯
        component_count = code.count('function') + code.count('const')
        if component_count > 2 and not has_memo:
            perf_score -= 20
        
        # 如果有複雜計算但沒有使用 useMemo
        if ('map' in code or 'filter' in code or 'reduce' in code) and not has_useMemo:
            perf_score -= 15
        
        # 如果有事件處理器但沒有使用 useCallback
        if ('onClick' in code or 'onChange' in code) and not has_useCallback:
            perf_score -= 10
        
        return max(0, perf_score)
    
    def _check_documentation(self, code: str) -> float:
        """檢查文檔完整性"""
        doc_score = 100.0
        
        # 檢查是否有組件級註釋
        if '/**' not in code:
            doc_score -= 30
        
        # 檢查是否有 Props 文檔
        if 'Props' in code and '@param' not in code and '@prop' not in code:
            doc_score -= 20
        
        # 檢查是否有函數註釋
        function_count = code.count('const') + code.count('function')
        comment_count = code.count('//') + code.count('/*')
        if function_count > 3 and comment_count < function_count:
            doc_score -= 20
        
        return max(0, doc_score)
    
    async def analyze_spec_coverage(self, spec_path: Path, implementation_path: Path) -> SpecCoverage:
        """分析規格覆蓋率"""
        print(f"📊 分析規格覆蓋率...")
        
        # 讀取規格文件
        with open(spec_path, 'r', encoding='utf-8') as f:
            specs = json.load(f)
        
        # 分析技術規格
        tech_specs = self._extract_technical_specs(specs)
        exp_specs = self._extract_experience_specs(specs)
        
        # 檢查實現
        implemented_tech = []
        implemented_exp = []
        
        # 掃描實現目錄
        for file_path in implementation_path.rglob("*.jsx"):
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            # 檢查技術規格實現
            for spec in tech_specs:
                if self._is_spec_implemented(spec, code):
                    implemented_tech.append(spec)
            
            # 檢查體驗規格實現
            for spec in exp_specs:
                if self._is_spec_implemented(spec, code):
                    implemented_exp.append(spec)
        
        # 計算覆蓋率
        tech_coverage = (len(implemented_tech) / len(tech_specs) * 100) if tech_specs else 0
        exp_coverage = (len(implemented_exp) / len(exp_specs) * 100) if exp_specs else 0
        
        # 找出未覆蓋的規格
        uncovered_tech = [s for s in tech_specs if s not in implemented_tech]
        uncovered_exp = [s for s in exp_specs if s not in implemented_exp]
        
        return SpecCoverage(
            technical_spec_coverage=tech_coverage,
            experience_spec_coverage=exp_coverage,
            uncovered_technical_specs=uncovered_tech,
            uncovered_experience_specs=uncovered_exp
        )
    
    def _extract_technical_specs(self, specs: Dict) -> List[str]:
        """提取技術規格"""
        tech_specs = []
        
        # API 規格
        if "apis" in specs:
            tech_specs.extend([f"API_{api['name']}" for api in specs["apis"]])
        
        # 數據模型規格
        if "models" in specs:
            tech_specs.extend([f"Model_{model['name']}" for model in specs["models"]])
        
        # 業務邏輯規格
        if "business_logic" in specs:
            tech_specs.extend([f"Logic_{logic['name']}" for logic in specs["business_logic"]])
        
        # 性能規格
        if "performance" in specs:
            tech_specs.extend([f"Perf_{req['name']}" for req in specs["performance"]])
        
        return tech_specs
    
    def _extract_experience_specs(self, specs: Dict) -> List[str]:
        """提取體驗規格"""
        exp_specs = []
        
        # UI 組件規格
        if "ui_components" in specs:
            exp_specs.extend([f"UI_{comp['name']}" for comp in specs["ui_components"]])
        
        # 交互規格
        if "interactions" in specs:
            exp_specs.extend([f"Interaction_{inter['name']}" for inter in specs["interactions"]])
        
        # 響應式規格
        if "responsive" in specs:
            exp_specs.extend([f"Responsive_{resp['name']}" for resp in specs["responsive"]])
        
        # 無障礙規格
        if "accessibility" in specs:
            exp_specs.extend([f"A11y_{a11y['name']}" for a11y in specs["accessibility"]])
        
        return exp_specs
    
    def _is_spec_implemented(self, spec: str, code: str) -> bool:
        """檢查規格是否已實現"""
        # 簡化的實現檢查
        spec_keywords = spec.lower().split('_')
        
        # 檢查代碼中是否包含相關關鍵詞
        for keyword in spec_keywords:
            if keyword in code.lower():
                return True
        
        return False
    
    async def analyze_test_coverage(self, implementation_path: Path, test_path: Path) -> TestCoverage:
        """分析測試覆蓋率"""
        print(f"🧪 分析測試覆蓋率...")
        
        # 統計組件和測試文件
        component_files = list(implementation_path.rglob("*.jsx"))
        test_files = list(test_path.rglob("*.test.js")) + list(test_path.rglob("*.spec.js"))
        
        # 技術測試覆蓋率（API、邏輯、性能測試）
        tech_tests = 0
        tech_components = 0
        
        # 體驗測試覆蓋率（UI、交互、無障礙測試）
        exp_tests = 0
        exp_components = 0
        
        for comp_file in component_files:
            comp_name = comp_file.stem
            
            # 判斷組件類型
            with open(comp_file, 'r', encoding='utf-8') as f:
                code = f.read()
                
            is_technical = any(keyword in code.lower() for keyword in ['api', 'service', 'logic', 'util'])
            is_experience = any(keyword in code.lower() for keyword in ['ui', 'component', 'view', 'page'])
            
            if is_technical:
                tech_components += 1
                # 查找對應的測試文件
                if any(comp_name in str(test_file) for test_file in test_files):
                    tech_tests += 1
            
            if is_experience:
                exp_components += 1
                # 查找對應的測試文件
                if any(comp_name in str(test_file) for test_file in test_files):
                    exp_tests += 1
        
        # 計算覆蓋率
        tech_test_coverage = (tech_tests / tech_components * 100) if tech_components > 0 else 0
        exp_test_coverage = (exp_tests / exp_components * 100) if exp_components > 0 else 0
        
        # 分析測試類型覆蓋率
        unit_tests = sum(1 for f in test_files if 'unit' in str(f) or not any(t in str(f) for t in ['integration', 'e2e']))
        integration_tests = sum(1 for f in test_files if 'integration' in str(f))
        e2e_tests = sum(1 for f in test_files if 'e2e' in str(f))
        
        total_components = len(component_files)
        unit_coverage = (unit_tests / total_components * 100) if total_components > 0 else 0
        integration_coverage = (integration_tests / total_components * 100) if total_components > 0 else 0
        e2e_coverage = (e2e_tests / total_components * 100) if total_components > 0 else 0
        
        return TestCoverage(
            technical_test_coverage=tech_test_coverage,
            experience_test_coverage=exp_test_coverage,
            unit_test_coverage=unit_coverage,
            integration_test_coverage=integration_coverage,
            e2e_test_coverage=e2e_coverage
        )
    
    async def generate_compliance_dashboard(self, 
                                          compliance: SmartUICompliance,
                                          spec_coverage: SpecCoverage,
                                          test_coverage: TestCoverage) -> str:
        """生成合規性儀表板"""
        dashboard_code = f"""import React from 'react';
import {{ Card, CardContent, CardHeader, CardTitle }} from '@/components/ui/card';
import {{ Progress }} from '@/components/ui/progress';
import {{ Badge }} from '@/components/ui/badge';
import {{ Tabs, TabsContent, TabsList, TabsTrigger }} from '@/components/ui/tabs';
import {{ RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer }} from 'recharts';

export function AGUIComplianceDashboard({{ data }}) {{
  const complianceData = [
    {{ subject: '命名規範', value: {compliance.naming_convention:.1f} }},
    {{ subject: '組件結構', value: {compliance.component_structure:.1f} }},
    {{ subject: '狀態管理', value: {compliance.state_management:.1f} }},
    {{ subject: '無障礙', value: {compliance.accessibility:.1f} }},
    {{ subject: '性能', value: {compliance.performance:.1f} }},
    {{ subject: '文檔', value: {compliance.documentation:.1f} }}
  ];
  
  const coverageData = {{
    spec: {{
      technical: {spec_coverage.technical_spec_coverage:.1f},
      experience: {spec_coverage.experience_spec_coverage:.1f}
    }},
    test: {{
      technical: {test_coverage.technical_test_coverage:.1f},
      experience: {test_coverage.experience_test_coverage:.1f},
      unit: {test_coverage.unit_test_coverage:.1f},
      integration: {test_coverage.integration_test_coverage:.1f},
      e2e: {test_coverage.e2e_test_coverage:.1f}
    }}
  }};
  
  const getScoreColor = (score) => {{
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-yellow-600';
    return 'text-red-600';
  }};
  
  const getStatusBadge = (score) => {{
    if (score >= 90) return <Badge className="bg-green-500">優秀</Badge>;
    if (score >= 80) return <Badge className="bg-yellow-500">良好</Badge>;
    return <Badge className="bg-red-500">需改進</Badge>;
  }};
  
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold mb-6">AG-UI/SmartUI 合規性儀表板</h1>
      
      {{/* 三大核心指標 */}}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>SmartUI 規範遵循</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-4xl font-bold ${{getScoreColor({sum(vars(compliance).values())/6:.1f})}}`}}>
              {{((({sum(vars(compliance).values())}) / 6).toFixed(1))}}%
            </div>
            {{getStatusBadge({sum(vars(compliance).values())/6:.1f})}}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>規格覆蓋率</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>技術規格</span>
                <span className={`font-bold ${{getScoreColor(coverageData.spec.technical)}}`}}>
                  {{coverageData.spec.technical.toFixed(1)}}%
                </span>
              </div>
              <div className="flex justify-between">
                <span>體驗規格</span>
                <span className={`font-bold ${{getScoreColor(coverageData.spec.experience)}}`}}>
                  {{coverageData.spec.experience.toFixed(1)}}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>測試覆蓋率</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>技術測試</span>
                <span className={`font-bold ${{getScoreColor(coverageData.test.technical)}}`}}>
                  {{coverageData.test.technical.toFixed(1)}}%
                </span>
              </div>
              <div className="flex justify-between">
                <span>體驗測試</span>
                <span className={`font-bold ${{getScoreColor(coverageData.test.experience)}}`}}>
                  {{coverageData.test.experience.toFixed(1)}}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Tabs defaultValue="compliance">
        <TabsList>
          <TabsTrigger value="compliance">規範詳情</TabsTrigger>
          <TabsTrigger value="spec">規格覆蓋</TabsTrigger>
          <TabsTrigger value="test">測試覆蓋</TabsTrigger>
        </TabsList>
        
        <TabsContent value="compliance">
          <Card>
            <CardHeader>
              <CardTitle>SmartUI 規範遵循詳情</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={{complianceData}}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="subject" />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar name="合規度" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
                
                <div className="space-y-3">
                  {{complianceData.map(item => (
                    <div key={{item.subject}}>
                      <div className="flex justify-between mb-1">
                        <span>{{item.subject}}</span>
                        <span className={{getScoreColor(item.value)}}>{{item.value.toFixed(1)}}%</span>
                      </div>
                      <Progress value={{item.value}} />
                    </div>
                  ))}}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="spec">
          <Card>
            <CardHeader>
              <CardTitle>規格覆蓋詳情</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-4">技術規格覆蓋</h3>
                  <Progress value={{coverageData.spec.technical}} className="mb-2" />
                  <p className="text-sm text-gray-600">
                    已覆蓋 {{Math.round(coverageData.spec.technical)}}% 的技術規格
                  </p>
                  {len(spec_coverage.uncovered_technical_specs) > 0 and f'''
                  <div className="mt-4">
                    <p className="text-sm font-medium mb-2">未覆蓋項目：</p>
                    <ul className="text-sm text-red-600 list-disc ml-5">
                      {chr(10).join(f"<li>{spec}</li>" for spec in spec_coverage.uncovered_technical_specs[:5])}
                    </ul>
                  </div>
                  '''}
                </div>
                
                <div>
                  <h3 className="font-semibold mb-4">體驗規格覆蓋</h3>
                  <Progress value={{coverageData.spec.experience}} className="mb-2" />
                  <p className="text-sm text-gray-600">
                    已覆蓋 {{Math.round(coverageData.spec.experience)}}% 的體驗規格
                  </p>
                  {len(spec_coverage.uncovered_experience_specs) > 0 and f'''
                  <div className="mt-4">
                    <p className="text-sm font-medium mb-2">未覆蓋項目：</p>
                    <ul className="text-sm text-red-600 list-disc ml-5">
                      {chr(10).join(f"<li>{spec}</li>" for spec in spec_coverage.uncovered_experience_specs[:5])}
                    </ul>
                  </div>
                  '''}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="test">
          <Card>
            <CardHeader>
              <CardTitle>測試覆蓋詳情</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-4">技術測試覆蓋</h3>
                    <Progress value={{coverageData.test.technical}} className="mb-2" />
                    <p className="text-sm text-gray-600">
                      {{Math.round(coverageData.test.technical)}}% 的技術組件有測試
                    </p>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-4">體驗測試覆蓋</h3>
                    <Progress value={{coverageData.test.experience}} className="mb-2" />
                    <p className="text-sm text-gray-600">
                      {{Math.round(coverageData.test.experience)}}% 的 UI 組件有測試
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-4">測試類型分布</h3>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span>單元測試</span>
                        <span>{{coverageData.test.unit.toFixed(1)}}%</span>
                      </div>
                      <Progress value={{coverageData.test.unit}} />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span>集成測試</span>
                        <span>{{coverageData.test.integration.toFixed(1)}}%</span>
                      </div>
                      <Progress value={{coverageData.test.integration}} />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span>E2E 測試</span>
                        <span>{{coverageData.test.e2e.toFixed(1)}}%</span>
                      </div>
                      <Progress value={{coverageData.test.e2e}} />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}}"""
        
        return dashboard_code
    
    async def generate_improvement_plan(self,
                                      compliance: SmartUICompliance,
                                      spec_coverage: SpecCoverage,
                                      test_coverage: TestCoverage) -> Dict[str, Any]:
        """生成改進計劃"""
        plan = {
            "priority_actions": [],
            "compliance_improvements": [],
            "spec_coverage_improvements": [],
            "test_coverage_improvements": []
        }
        
        # 合規性改進
        compliance_dict = asdict(compliance)
        for key, value in compliance_dict.items():
            if value < self.compliance_threshold:
                plan["compliance_improvements"].append({
                    "area": key,
                    "current": value,
                    "target": self.compliance_threshold,
                    "actions": self._get_compliance_actions(key)
                })
        
        # 規格覆蓋改進
        if spec_coverage.technical_spec_coverage < 80:
            plan["spec_coverage_improvements"].append({
                "type": "technical",
                "current": spec_coverage.technical_spec_coverage,
                "target": 80,
                "uncovered": spec_coverage.uncovered_technical_specs[:10]
            })
        
        if spec_coverage.experience_spec_coverage < 80:
            plan["spec_coverage_improvements"].append({
                "type": "experience",
                "current": spec_coverage.experience_spec_coverage,
                "target": 80,
                "uncovered": spec_coverage.uncovered_experience_specs[:10]
            })
        
        # 測試覆蓋改進
        if test_coverage.technical_test_coverage < 80:
            plan["test_coverage_improvements"].append({
                "type": "technical_test",
                "current": test_coverage.technical_test_coverage,
                "target": 80,
                "priority": "high"
            })
        
        if test_coverage.experience_test_coverage < 80:
            plan["test_coverage_improvements"].append({
                "type": "experience_test",
                "current": test_coverage.experience_test_coverage,
                "target": 80,
                "priority": "high"
            })
        
        # 確定優先行動
        if sum(vars(compliance).values()) / 6 < 80:
            plan["priority_actions"].append("提升 SmartUI 規範遵循度")
        
        if (spec_coverage.technical_spec_coverage + spec_coverage.experience_spec_coverage) / 2 < 80:
            plan["priority_actions"].append("增加規格覆蓋率")
        
        if (test_coverage.technical_test_coverage + test_coverage.experience_test_coverage) / 2 < 80:
            plan["priority_actions"].append("提高測試覆蓋率")
        
        return plan
    
    def _get_compliance_actions(self, area: str) -> List[str]:
        """獲取合規性改進行動"""
        actions_map = {
            "naming_convention": [
                "統一組件命名為 PascalCase",
                "函數命名加上適當前綴 (handle, on, get, set)",
                "常量使用 UPPER_SNAKE_CASE"
            ],
            "component_structure": [
                "調整 import 順序：React → 第三方 → 本地",
                "添加 Props 接口定義",
                "確保有適當的導出語句"
            ],
            "state_management": [
                "將多個 useState 合併為 useReducer",
                "使用 Context 避免 prop drilling",
                "考慮狀態提升或狀態管理庫"
            ],
            "accessibility": [
                "為所有按鈕添加 aria-label",
                "為圖片添加 alt 屬性",
                "添加鍵盤事件處理",
                "為自定義組件添加適當的 role"
            ],
            "performance": [
                "使用 React.memo 包裝純組件",
                "對複雜計算使用 useMemo",
                "對事件處理器使用 useCallback",
                "實施代碼分割和懶加載"
            ],
            "documentation": [
                "添加組件級 JSDoc 註釋",
                "為 Props 添加類型和描述",
                "為複雜函數添加註釋",
                "創建使用示例"
            ]
        }
        
        return actions_map.get(area, ["改進 " + area])

# 主函數
async def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════════════════════╗
║      AG-UI/SmartUI 增強系統 - v4.75                     ║
║      規範遵循 · 規格覆蓋 · 測試覆蓋                      ║
╚══════════════════════════════════════════════════════════╝
""")
    
    system = AGUISmartUISystem()
    
    # 創建示例組件進行分析
    sample_component = Path("/Users/alexchuang/alexchuangtest/aicore0720/generated/smartui/SampleComponent.jsx")
    sample_component.parent.mkdir(parents=True, exist_ok=True)
    
    # 寫入示例組件代碼
    with open(sample_component, 'w', encoding='utf-8') as f:
        f.write("""import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';

/**
 * Sample component for demonstration
 */
export function SampleComponent({ onSubmit, data }) {
  const [formData, setFormData] = useState(data || {});
  
  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }, []);
  
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    onSubmit(formData);
  }, [formData, onSubmit]);
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        name="username"
        value={formData.username || ''}
        onChange={handleChange}
        aria-label="Username"
      />
      <Button type="submit">Submit</Button>
    </form>
  );
}
""")
    
    # 1. 分析 SmartUI 規範遵循度
    print("\n1️⃣ 分析 SmartUI 規範遵循度...")
    compliance = await system.analyze_smartui_compliance(sample_component)
    
    print(f"   - 命名規範: {compliance.naming_convention:.1f}%")
    print(f"   - 組件結構: {compliance.component_structure:.1f}%")
    print(f"   - 狀態管理: {compliance.state_management:.1f}%")
    print(f"   - 無障礙: {compliance.accessibility:.1f}%")
    print(f"   - 性能: {compliance.performance:.1f}%")
    print(f"   - 文檔: {compliance.documentation:.1f}%")
    
    # 2. 分析規格覆蓋率
    print("\n2️⃣ 分析規格覆蓋率...")
    
    # 創建示例規格文件
    spec_file = Path("/Users/alexchuang/alexchuangtest/aicore0720/specs/agui_spec.json")
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    
    sample_spec = {
        "apis": [
            {"name": "user_api", "endpoints": ["/users", "/users/:id"]},
            {"name": "auth_api", "endpoints": ["/login", "/logout"]}
        ],
        "models": [
            {"name": "User", "fields": ["id", "username", "email"]},
            {"name": "Session", "fields": ["token", "expires"]}
        ],
        "ui_components": [
            {"name": "LoginForm", "type": "form"},
            {"name": "UserList", "type": "table"},
            {"name": "Dashboard", "type": "dashboard"}
        ],
        "interactions": [
            {"name": "form_validation", "type": "client"},
            {"name": "data_fetch", "type": "async"}
        ]
    }
    
    with open(spec_file, 'w', encoding='utf-8') as f:
        json.dump(sample_spec, f, ensure_ascii=False, indent=2)
    
    spec_coverage = await system.analyze_spec_coverage(spec_file, sample_component.parent)
    
    print(f"   - 技術規格覆蓋率: {spec_coverage.technical_spec_coverage:.1f}%")
    print(f"   - 體驗規格覆蓋率: {spec_coverage.experience_spec_coverage:.1f}%")
    
    # 3. 分析測試覆蓋率
    print("\n3️⃣ 分析測試覆蓋率...")
    test_coverage = await system.analyze_test_coverage(sample_component.parent, sample_component.parent)
    
    print(f"   - 技術測試覆蓋率: {test_coverage.technical_test_coverage:.1f}%")
    print(f"   - 體驗測試覆蓋率: {test_coverage.experience_test_coverage:.1f}%")
    print(f"   - 單元測試覆蓋率: {test_coverage.unit_test_coverage:.1f}%")
    print(f"   - 集成測試覆蓋率: {test_coverage.integration_test_coverage:.1f}%")
    print(f"   - E2E測試覆蓋率: {test_coverage.e2e_test_coverage:.1f}%")
    
    # 4. 生成儀表板
    print("\n4️⃣ 生成合規性儀表板...")
    dashboard_code = await system.generate_compliance_dashboard(compliance, spec_coverage, test_coverage)
    
    dashboard_path = Path("/Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.75/AGUIComplianceDashboard.jsx")
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_code)
    
    print(f"   ✅ 儀表板已生成: {dashboard_path}")
    
    # 5. 生成改進計劃
    print("\n5️⃣ 生成改進計劃...")
    improvement_plan = await system.generate_improvement_plan(compliance, spec_coverage, test_coverage)
    
    plan_path = Path("/Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.75/agui_improvement_plan.json")
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(improvement_plan, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 改進計劃已生成: {plan_path}")
    
    if improvement_plan["priority_actions"]:
        print("\n   優先行動項目:")
        for action in improvement_plan["priority_actions"]:
            print(f"   - {action}")
    
    print("\n✅ AG-UI/SmartUI 增強分析完成！")

if __name__ == "__main__":
    import asyncio
    from datetime import datetime
    asyncio.run(main())