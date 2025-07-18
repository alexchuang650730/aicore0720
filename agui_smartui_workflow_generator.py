"""
AG-UI SmartUI 六大工作流 UI 生成器
基於規格驅動的 UI 自動生成系統
"""

import yaml
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class UIComponent:
    """UI 組件定義"""
    id: str
    type: str
    properties: Dict[str, Any]
    position: Optional[str] = None
    style: Optional[Dict[str, Any]] = None
    events: Optional[List[Dict[str, str]]] = None

@dataclass
class WorkflowUI:
    """工作流 UI 定義"""
    workflow_id: str
    name: str
    icon: str
    components: List[UIComponent]
    color_scheme: Dict[str, str]
    test_cases: List[Dict[str, Any]]

class AGUISmartUIGenerator:
    """AG-UI SmartUI 生成器"""
    
    def __init__(self, spec_file: str = "claudeditor_six_workflows_specification.yaml"):
        """初始化生成器"""
        self.spec_file = spec_file
        self.specification = self._load_specification()
        self.generated_components = {}
        self.test_suites = {}
        
    def _load_specification(self) -> Dict[str, Any]:
        """加載工作流規格"""
        try:
            with open(self.spec_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load specification: {e}")
            return {}
    
    async def generate_workflow_ui(self) -> Dict[str, WorkflowUI]:
        """生成六大工作流 UI"""
        workflows_ui = {}
        
        for workflow_id, workflow_spec in self.specification['workflows'].items():
            # 生成工作流 UI
            workflow_ui = await self._generate_single_workflow_ui(
                workflow_id, workflow_spec
            )
            workflows_ui[workflow_id] = workflow_ui
            
            # 生成測試用例
            test_suite = await self._generate_test_cases(
                workflow_id, workflow_spec, workflow_ui
            )
            self.test_suites[workflow_id] = test_suite
        
        return workflows_ui
    
    async def _generate_single_workflow_ui(self, workflow_id: str, 
                                         spec: Dict[str, Any]) -> WorkflowUI:
        """生成單個工作流 UI"""
        ui_spec = spec['ui_specification']
        
        # 生成 UI 組件
        components = []
        
        for component_spec in ui_spec['components']:
            component = UIComponent(
                id=f"{workflow_id}_{component_spec['type']}",
                type=component_spec['type'],
                properties=component_spec['properties'],
                position=ui_spec['position']
            )
            
            # 添加樣式
            component.style = self._generate_component_style(
                component_spec['type'], 
                ui_spec['color_scheme']
            )
            
            # 添加事件處理
            component.events = self._generate_component_events(
                component_spec['type'],
                workflow_id
            )
            
            components.append(component)
        
        # 生成測試用例引用
        test_cases = spec.get('test_cases', [])
        
        return WorkflowUI(
            workflow_id=spec['id'],
            name=spec['name'],
            icon=spec['icon'],
            components=components,
            color_scheme=ui_spec['color_scheme'],
            test_cases=test_cases
        )
    
    def _generate_component_style(self, component_type: str, 
                                color_scheme: Dict[str, str]) -> Dict[str, Any]:
        """生成組件樣式"""
        base_styles = {
            "workflow_card": {
                "backgroundColor": color_scheme['primary'],
                "color": "#FFFFFF",
                "borderRadius": "8px",
                "padding": "16px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "transition": "all 0.3s ease",
                "cursor": "pointer",
                ":hover": {
                    "transform": "translateY(-2px)",
                    "boxShadow": "0 4px 8px rgba(0,0,0,0.2)"
                }
            },
            "progress_indicator": {
                "width": "100%",
                "height": "8px",
                "backgroundColor": "#E0E0E0",
                "borderRadius": "4px",
                "overflow": "hidden",
                ".progress-bar": {
                    "height": "100%",
                    "backgroundColor": color_scheme['accent'],
                    "transition": "width 0.3s ease"
                }
            },
            "alignment_meter": {
                "width": "120px",
                "height": "120px",
                "position": "relative",
                ".meter-circle": {
                    "stroke": color_scheme['secondary'],
                    "strokeWidth": "10",
                    "fill": "none"
                },
                ".meter-value": {
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "textAnchor": "middle"
                }
            },
            "code_preview": {
                "backgroundColor": "#1E1E1E",
                "color": "#D4D4D4",
                "fontFamily": "monospace",
                "fontSize": "14px",
                "padding": "12px",
                "borderRadius": "4px",
                "overflow": "auto"
            },
            "quality_badge": {
                "display": "inline-flex",
                "alignItems": "center",
                "padding": "4px 8px",
                "borderRadius": "12px",
                "backgroundColor": color_scheme['secondary'],
                "color": "#FFFFFF",
                "fontSize": "12px",
                "fontWeight": "500"
            },
            "test_coverage_chart": {
                "width": "200px",
                "height": "200px",
                "position": "relative"
            },
            "test_results_panel": {
                "backgroundColor": "#F5F5F5",
                "borderRadius": "4px",
                "padding": "12px",
                ".result-item": {
                    "display": "flex",
                    "justifyContent": "space-between",
                    "padding": "4px 0"
                }
            }
        }
        
        return base_styles.get(component_type, {})
    
    def _generate_component_events(self, component_type: str, 
                                 workflow_id: str) -> List[Dict[str, str]]:
        """生成組件事件"""
        events = {
            "workflow_card": [
                {
                    "event": "click",
                    "handler": f"handleWorkflowClick_{workflow_id}",
                    "action": "expandWorkflow"
                },
                {
                    "event": "contextmenu",
                    "handler": f"handleWorkflowContextMenu_{workflow_id}",
                    "action": "showContextMenu"
                }
            ],
            "progress_indicator": [
                {
                    "event": "update",
                    "handler": f"updateProgress_{workflow_id}",
                    "action": "animateProgress"
                }
            ],
            "alignment_meter": [
                {
                    "event": "change",
                    "handler": f"updateAlignment_{workflow_id}",
                    "action": "updateMeter"
                }
            ]
        }
        
        return events.get(component_type, [])
    
    async def _generate_test_cases(self, workflow_id: str, 
                                 spec: Dict[str, Any], 
                                 workflow_ui: WorkflowUI) -> Dict[str, Any]:
        """生成測試用例"""
        test_suite = {
            "suite_name": f"{spec['name']}測試套件",
            "workflow_id": workflow_id,
            "test_cases": []
        }
        
        # UI 渲染測試
        test_suite["test_cases"].append({
            "id": f"tc_ui_render_{workflow_id}",
            "name": "UI 組件渲染測試",
            "type": "ui",
            "steps": [
                f"渲染 {spec['name']} 工作流卡片",
                "驗證所有組件正確顯示",
                "檢查樣式應用正確"
            ],
            "assertions": [
                f"expect(getByTestId('{workflow_id}_card')).toBeVisible()",
                f"expect(getByTestId('{workflow_id}_icon')).toHaveText('{spec['icon']}')",
                f"expect(getByTestId('{workflow_id}_title')).toHaveText('{spec['name']}')"
            ]
        })
        
        # 交互測試
        test_suite["test_cases"].append({
            "id": f"tc_interaction_{workflow_id}",
            "name": "用戶交互測試",
            "type": "interaction",
            "steps": [
                f"點擊 {spec['name']} 工作流卡片",
                "驗證展開動畫",
                "檢查詳細信息顯示"
            ],
            "assertions": [
                f"fireEvent.click(getByTestId('{workflow_id}_card'))",
                f"await waitFor(() => expect(getByTestId('{workflow_id}_details')).toBeVisible())",
                f"expect(getByTestId('{workflow_id}_stages')).toHaveLength({len(spec['stages'])})"
            ]
        })
        
        # 功能測試
        for test_case in spec.get('test_cases', []):
            test_suite["test_cases"].append({
                "id": test_case['id'],
                "name": test_case['name'],
                "type": test_case['type'],
                "steps": test_case['steps'],
                "expected_result": test_case['expected_result'],
                "workflow_specific": True
            })
        
        # 集成測試
        test_suite["test_cases"].append({
            "id": f"tc_integration_{workflow_id}",
            "name": "MCP 工具集成測試",
            "type": "integration",
            "steps": [
                f"啟動 {spec['name']} 工作流",
                "驗證 MCP 工具調用",
                "檢查結果返回"
            ],
            "mcp_tools": [tool['tool_id'] for tool in spec.get('mcp_tools', [])]
        })
        
        return test_suite
    
    async def generate_react_components(self) -> Dict[str, str]:
        """生成 React 組件代碼"""
        workflows_ui = await self.generate_workflow_ui()
        react_components = {}
        
        for workflow_id, workflow_ui in workflows_ui.items():
            component_code = self._generate_react_component(workflow_ui)
            react_components[workflow_id] = component_code
        
        # 生成主容器組件
        container_code = self._generate_container_component(workflows_ui)
        react_components['SixWorkflowsContainer'] = container_code
        
        return react_components
    
    def _generate_react_component(self, workflow_ui: WorkflowUI) -> str:
        """生成單個 React 組件"""
        component_name = ''.join(word.capitalize() for word in workflow_ui.workflow_id.split('_'))
        
        imports = """import React, { useState, useEffect } from 'react';
import { Card, Progress, Badge, Tooltip } from 'antd';
import { useMCPConnection } from '../hooks/useMCPConnection';
import './WorkflowCard.css';"""
        
        component_code = f"""
{imports}

export const {component_name}Card = ({{ onExpand, onAction }}) => {{
    const [alignment, setAlignment] = useState(100);
    const [progress, setProgress] = useState(0);
    const [expanded, setExpanded] = useState(false);
    const {{ callMCPTool }} = useMCPConnection();
    
    const handleClick = () => {{
        setExpanded(!expanded);
        onExpand && onExpand('{workflow_ui.workflow_id}');
    }};
    
    const handleAction = async (action) => {{
        const result = await callMCPTool(action.tool, action.params);
        onAction && onAction(action, result);
    }};
    
    return (
        <Card
            className="workflow-card"
            style={{{{
                backgroundColor: '{workflow_ui.color_scheme["primary"]}',
                color: '#FFFFFF'
            }}}}
            onClick={{handleClick}}
            data-testid="{workflow_ui.workflow_id}_card"
        >
            <div className="workflow-header">
                <span className="workflow-icon" data-testid="{workflow_ui.workflow_id}_icon">
                    {workflow_ui.icon}
                </span>
                <h3 data-testid="{workflow_ui.workflow_id}_title">{workflow_ui.name}</h3>
            </div>
            
            <Progress
                percent={{progress}}
                strokeColor={{{workflow_ui.color_scheme["accent"]}}}
                showInfo={{false}}
            />
            
            <div className="alignment-meter">
                <Tooltip title="目標對齊度">
                    <div className="meter-value">{{alignment}}%</div>
                </Tooltip>
            </div>
            
            {{expanded && (
                <div className="workflow-details" data-testid="{workflow_ui.workflow_id}_details">
                    {{/* 工作流詳細信息 */}}
                </div>
            )}}
        </Card>
    );
}};"""
        
        return component_code
    
    def _generate_container_component(self, workflows_ui: Dict[str, WorkflowUI]) -> str:
        """生成容器組件"""
        imports = """import React, { useState } from 'react';
import { Layout, Collapse } from 'antd';
import { AnimatePresence, motion } from 'framer-motion';"""
        
        # 導入所有工作流組件
        workflow_imports = '\n'.join([
            f"import {{ {''.join(word.capitalize() for word in wf_id.split('_'))}Card }} from './{wf_id}';"
            for wf_id in workflows_ui.keys()
        ])
        
        component_code = f"""
{imports}
{workflow_imports}
import './SixWorkflowsContainer.css';

const {{ Sider }} = Layout;

export const SixWorkflowsContainer = () => {{
    const [collapsed, setCollapsed] = useState(false);
    const [activeWorkflow, setActiveWorkflow] = useState(null);
    
    const workflows = [
        {', '.join([f'{{ id: "{wf_id}", Component: {"".join(word.capitalize() for word in wf_id.split("_"))}Card }}' 
                    for wf_id in workflows_ui.keys()])}
    ];
    
    return (
        <Sider
            width={{320}}
            collapsible
            collapsed={{collapsed}}
            onCollapse={{setCollapsed}}
            className="workflows-sidebar"
        >
            <div className="sidebar-header">
                <h2>六大核心工作流</h2>
            </div>
            
            <AnimatePresence>
                <div className="workflows-container">
                    {{workflows.map(({{ id, Component }}) => (
                        <motion.div
                            key={{id}}
                            initial={{{{ opacity: 0, x: -20 }}}}
                            animate={{{{ opacity: 1, x: 0 }}}}
                            exit={{{{ opacity: 0, x: -20 }}}}
                            transition={{{{ duration: 0.3 }}}}
                        >
                            <Component
                                onExpand={{setActiveWorkflow}}
                                onAction={{(action, result) => {{
                                    console.log('Workflow action:', action, result);
                                }}}}
                            />
                        </motion.div>
                    ))}}
                </div>
            </AnimatePresence>
        </Sider>
    );
}};"""
        
        return component_code
    
    async def generate_test_files(self) -> Dict[str, str]:
        """生成測試文件"""
        test_files = {}
        
        for workflow_id, test_suite in self.test_suites.items():
            test_code = self._generate_test_file(workflow_id, test_suite)
            test_files[f"{workflow_id}.test.js"] = test_code
        
        # 生成集成測試
        integration_test = self._generate_integration_test()
        test_files["six_workflows_integration.test.js"] = integration_test
        
        return test_files
    
    def _generate_test_file(self, workflow_id: str, test_suite: Dict[str, Any]) -> str:
        """生成測試文件"""
        component_name = ''.join(word.capitalize() for word in workflow_id.split('_'))
        
        test_code = f"""import {{ render, screen, fireEvent, waitFor }} from '@testing-library/react';
import {{ {component_name}Card }} from '../{workflow_id}';
import {{ mockMCPConnection }} from '../../test-utils/mockMCP';

jest.mock('../hooks/useMCPConnection', () => ({{
    useMCPConnection: () => mockMCPConnection
}}));

describe('{test_suite["suite_name"]}', () => {{
"""
        
        for test_case in test_suite["test_cases"]:
            test_code += f"""
    test('{test_case["name"]}', async () => {{
        // {test_case["name"]}
        const {{ getByTestId }} = render(<{component_name}Card />);
        
"""
            if test_case.get("assertions"):
                for assertion in test_case["assertions"]:
                    test_code += f"        {assertion};\n"
            
            test_code += "    });\n"
        
        test_code += "});"
        
        return test_code
    
    def _generate_integration_test(self) -> str:
        """生成集成測試"""
        return """import { render, screen, waitFor } from '@testing-library/react';
import { SixWorkflowsContainer } from '../SixWorkflowsContainer';
import { MCPProvider } from '../providers/MCPProvider';

describe('六大工作流集成測試', () => {
    test('所有工作流正確渲染', async () => {
        render(
            <MCPProvider>
                <SixWorkflowsContainer />
            </MCPProvider>
        );
        
        // 驗證六個工作流都渲染
        const workflowCards = screen.getAllByTestId(/.*_card/);
        expect(workflowCards).toHaveLength(6);
    });
    
    test('工作流間通信正常', async () => {
        // 測試工作流之間的數據傳遞和事件通信
    });
    
    test('MCP 連接穩定', async () => {
        // 測試 MCP 連接的穩定性和錯誤處理
    });
});"""
    
    async def generate_complete_ui_package(self) -> Dict[str, Any]:
        """生成完整的 UI 包"""
        # 生成組件
        react_components = await self.generate_react_components()
        
        # 生成測試
        test_files = await self.generate_test_files()
        
        # 生成樣式文件
        styles = self._generate_styles()
        
        # 生成配置文件
        config = self._generate_config()
        
        return {
            "components": react_components,
            "tests": test_files,
            "styles": styles,
            "config": config,
            "specification": self.specification,
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_styles(self) -> Dict[str, str]:
        """生成樣式文件"""
        return {
            "WorkflowCard.css": """
.workflow-card {
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.workflow-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.workflow-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.workflow-icon {
    font-size: 24px;
}

.alignment-meter {
    position: absolute;
    top: 16px;
    right: 16px;
}

.meter-value {
    font-size: 18px;
    font-weight: bold;
}

.workflow-details {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
}
""",
            "SixWorkflowsContainer.css": """
.workflows-sidebar {
    background: #f0f2f5;
    overflow-y: auto;
}

.sidebar-header {
    padding: 16px;
    background: #fff;
    border-bottom: 1px solid #e8e8e8;
}

.sidebar-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
}

.workflows-container {
    padding: 12px;
}
"""
        }
    
    def _generate_config(self) -> Dict[str, Any]:
        """生成配置文件"""
        return {
            "mcp": {
                "endpoint": self.specification['integration']['mcp_server']['endpoint'],
                "reconnectInterval": self.specification['integration']['mcp_server']['reconnect_interval'],
                "maxReconnectAttempts": self.specification['integration']['mcp_server']['max_reconnect_attempts']
            },
            "monitoring": self.specification['monitoring'],
            "testing": self.specification['testing']
        }


async def main():
    """主函數"""
    print("🎨 AG-UI SmartUI 六大工作流 UI 生成器")
    print("=" * 50)
    
    generator = AGUISmartUIGenerator()
    
    # 生成完整 UI 包
    ui_package = await generator.generate_complete_ui_package()
    
    # 保存生成的文件
    output_dir = Path("generated_ui")
    output_dir.mkdir(exist_ok=True)
    
    # 保存組件
    components_dir = output_dir / "components"
    components_dir.mkdir(exist_ok=True)
    
    for filename, code in ui_package["components"].items():
        filepath = components_dir / f"{filename}.jsx"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"✅ 生成組件: {filepath}")
    
    # 保存測試
    tests_dir = output_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    for filename, code in ui_package["tests"].items():
        filepath = tests_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"✅ 生成測試: {filepath}")
    
    # 保存樣式
    styles_dir = output_dir / "styles"
    styles_dir.mkdir(exist_ok=True)
    
    for filename, code in ui_package["styles"].items():
        filepath = styles_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"✅ 生成樣式: {filepath}")
    
    # 保存配置
    with open(output_dir / "config.json", 'w', encoding='utf-8') as f:
        json.dump(ui_package["config"], f, indent=2, ensure_ascii=False)
    print(f"✅ 生成配置: {output_dir / 'config.json'}")
    
    # 生成摘要報告
    summary = {
        "generated_at": ui_package["generated_at"],
        "components_count": len(ui_package["components"]),
        "tests_count": sum(len(suite["test_cases"]) for suite in generator.test_suites.values()),
        "workflows": list(generator.specification['workflows'].keys())
    }
    
    with open(output_dir / "generation_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n📊 生成摘要:")
    print(f"   組件數量: {summary['components_count']}")
    print(f"   測試用例: {summary['tests_count']}")
    print(f"   工作流數: {len(summary['workflows'])}")
    
    return ui_package


if __name__ == "__main__":
    asyncio.run(main())