#!/usr/bin/env python3
"""
PowerAutomation v4.75 - 命令支持系統
檢查 K2 模式下的命令支持度，並提供統一的命令列表
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandSource(Enum):
    """命令來源"""
    CLAUDE_NATIVE = "claude_native"      # Claude Code Tool 原生命令
    COMMAND_MCP = "command_mcp"          # Command MCP 提供的命令
    CLAUDEDITOR = "claudeditor"          # ClaudeEditor 專屬命令
    K2_ENHANCED = "k2_enhanced"          # K2 增強命令

class SupportLevel(Enum):
    """支持級別"""
    FULL = "full"                        # 完全支持
    PARTIAL = "partial"                  # 部分支持
    NOT_SUPPORTED = "not_supported"      # 不支持
    ENHANCED = "enhanced"                # K2 增強版

@dataclass
class Command:
    """命令定義"""
    name: str
    description: str
    source: CommandSource
    category: str
    syntax: str
    examples: List[str]
    k2_support: SupportLevel
    k2_notes: Optional[str] = None
    shortcuts: List[str] = None
    
class CommandSupportSystem:
    """命令支持系統"""
    
    def __init__(self):
        self.commands = self._define_all_commands()
        self.categories = self._organize_by_category()
        
    def _define_all_commands(self) -> List[Command]:
        """定義所有命令"""
        commands = []
        
        # Claude Code Tool 原生命令
        claude_native_commands = [
            Command(
                name="/model",
                description="查看或切換當前模型",
                source=CommandSource.CLAUDE_NATIVE,
                category="模型管理",
                syntax="/model [info|k2|switch]",
                examples=["/model", "/model k2", "/model info"],
                k2_support=SupportLevel.ENHANCED,
                k2_notes="K2 模式下返回 K2-Optimizer 信息",
                shortcuts=["m"]
            ),
            Command(
                name="/help",
                description="顯示幫助信息",
                source=CommandSource.CLAUDE_NATIVE,
                category="系統",
                syntax="/help [command]",
                examples=["/help", "/help model"],
                k2_support=SupportLevel.FULL,
                shortcuts=["h", "?"]
            ),
            Command(
                name="/clear",
                description="清除對話歷史",
                source=CommandSource.CLAUDE_NATIVE,
                category="系統",
                syntax="/clear",
                examples=["/clear"],
                k2_support=SupportLevel.FULL,
                shortcuts=["c"]
            ),
            Command(
                name="/save",
                description="保存當前對話",
                source=CommandSource.CLAUDE_NATIVE,
                category="文件操作",
                syntax="/save [filename]",
                examples=["/save", "/save conversation.json"],
                k2_support=SupportLevel.ENHANCED,
                k2_notes="K2 模式下自動添加訓練標記",
                shortcuts=["s"]
            ),
            Command(
                name="/load",
                description="加載保存的對話",
                source=CommandSource.CLAUDE_NATIVE,
                category="文件操作",
                syntax="/load <filename>",
                examples=["/load conversation.json"],
                k2_support=SupportLevel.FULL,
                shortcuts=["l"]
            ),
            Command(
                name="/history",
                description="查看命令歷史",
                source=CommandSource.CLAUDE_NATIVE,
                category="系統",
                syntax="/history [n]",
                examples=["/history", "/history 10"],
                k2_support=SupportLevel.FULL,
                shortcuts=["hist"]
            ),
            Command(
                name="/export",
                description="導出對話或代碼",
                source=CommandSource.CLAUDE_NATIVE,
                category="文件操作",
                syntax="/export [format]",
                examples=["/export markdown", "/export json"],
                k2_support=SupportLevel.ENHANCED,
                k2_notes="K2 模式下支持導出為訓練格式",
                shortcuts=["e"]
            )
        ]
        
        # Command MCP 提供的命令
        command_mcp_commands = [
            Command(
                name="/run",
                description="執行命令或腳本",
                source=CommandSource.COMMAND_MCP,
                category="執行",
                syntax="/run <command>",
                examples=["/run python script.py", "/run npm test"],
                k2_support=SupportLevel.FULL,
                shortcuts=["r", "exec"]
            ),
            Command(
                name="/test",
                description="運行測試",
                source=CommandSource.COMMAND_MCP,
                category="測試",
                syntax="/test [pattern]",
                examples=["/test", "/test unit", "/test *.spec.js"],
                k2_support=SupportLevel.FULL,
                shortcuts=["t"]
            ),
            Command(
                name="/deploy",
                description="部署應用",
                source=CommandSource.COMMAND_MCP,
                category="部署",
                syntax="/deploy [environment]",
                examples=["/deploy", "/deploy production"],
                k2_support=SupportLevel.PARTIAL,
                k2_notes="K2 模式下需要額外配置",
                shortcuts=["d"]
            ),
            Command(
                name="/build",
                description="構建項目",
                source=CommandSource.COMMAND_MCP,
                category="構建",
                syntax="/build [target]",
                examples=["/build", "/build production"],
                k2_support=SupportLevel.FULL,
                shortcuts=["b"]
            ),
            Command(
                name="/analyze",
                description="分析代碼",
                source=CommandSource.COMMAND_MCP,
                category="分析",
                syntax="/analyze [type]",
                examples=["/analyze", "/analyze performance"],
                k2_support=SupportLevel.ENHANCED,
                k2_notes="K2 提供更深入的分析",
                shortcuts=["a"]
            )
        ]
        
        # ClaudeEditor 專屬命令
        claudeditor_commands = [
            Command(
                name="/ui",
                description="打開 UI 設計器",
                source=CommandSource.CLAUDEDITOR,
                category="設計",
                syntax="/ui [component]",
                examples=["/ui", "/ui dashboard"],
                k2_support=SupportLevel.FULL,
                shortcuts=["u"]
            ),
            Command(
                name="/preview",
                description="預覽當前文件",
                source=CommandSource.CLAUDEDITOR,
                category="預覽",
                syntax="/preview [file]",
                examples=["/preview", "/preview index.html"],
                k2_support=SupportLevel.FULL,
                shortcuts=["p"]
            ),
            Command(
                name="/collaborate",
                description="開始協作會話",
                source=CommandSource.CLAUDEDITOR,
                category="協作",
                syntax="/collaborate [session]",
                examples=["/collaborate", "/collaborate team-session"],
                k2_support=SupportLevel.PARTIAL,
                k2_notes="K2 模式下協作數據會用於訓練",
                shortcuts=["collab"]
            ),
            Command(
                name="/workflow",
                description="管理工作流",
                source=CommandSource.CLAUDEDITOR,
                category="工作流",
                syntax="/workflow [action]",
                examples=["/workflow create", "/workflow list"],
                k2_support=SupportLevel.FULL,
                shortcuts=["w", "wf"]
            ),
            Command(
                name="/mcp",
                description="管理 MCP 組件",
                source=CommandSource.CLAUDEDITOR,
                category="MCP",
                syntax="/mcp [list|status|enable|disable]",
                examples=["/mcp list", "/mcp status codeflow_mcp"],
                k2_support=SupportLevel.FULL,
                shortcuts=["mcp"]
            )
        ]
        
        # K2 增強命令
        k2_enhanced_commands = [
            Command(
                name="/train",
                description="管理 K2 訓練",
                source=CommandSource.K2_ENHANCED,
                category="K2",
                syntax="/train [start|stop|status]",
                examples=["/train start", "/train status"],
                k2_support=SupportLevel.ENHANCED,
                k2_notes="K2 專屬命令",
                shortcuts=["tr"]
            ),
            Command(
                name="/optimize",
                description="優化代碼或查詢",
                source=CommandSource.K2_ENHANCED,
                category="K2",
                syntax="/optimize <code|query>",
                examples=["/optimize function", "/optimize sql"],
                k2_support=SupportLevel.ENHANCED,
                k2_notes="使用 K2 優化器",
                shortcuts=["opt"]
            ),
            Command(
                name="/metrics",
                description="查看 K2 性能指標",
                source=CommandSource.K2_ENHANCED,
                category="K2",
                syntax="/metrics [mcp|conversation|all]",
                examples=["/metrics", "/metrics mcp"],
                k2_support=SupportLevel.ENHANCED,
                k2_notes="K2 專屬指標系統",
                shortcuts=["m", "stats"]
            ),
            Command(
                name="/record",
                description="控制對話記錄",
                source=CommandSource.K2_ENHANCED,
                category="K2",
                syntax="/record [on|off|status]",
                examples=["/record on", "/record status"],
                k2_support=SupportLevel.ENHANCED,
                k2_notes="控制訓練數據收集",
                shortcuts=["rec"]
            )
        ]
        
        # 合併所有命令
        commands.extend(claude_native_commands)
        commands.extend(command_mcp_commands)
        commands.extend(claudeditor_commands)
        commands.extend(k2_enhanced_commands)
        
        return commands
    
    def _organize_by_category(self) -> Dict[str, List[Command]]:
        """按類別組織命令"""
        categories = {}
        for cmd in self.commands:
            if cmd.category not in categories:
                categories[cmd.category] = []
            categories[cmd.category].append(cmd)
        return categories
    
    def get_k2_support_report(self) -> Dict[str, Any]:
        """獲取 K2 支持報告"""
        total = len(self.commands)
        support_stats = {
            SupportLevel.FULL: 0,
            SupportLevel.PARTIAL: 0,
            SupportLevel.NOT_SUPPORTED: 0,
            SupportLevel.ENHANCED: 0
        }
        
        by_source = {}
        
        for cmd in self.commands:
            support_stats[cmd.k2_support] += 1
            
            source_name = cmd.source.value
            if source_name not in by_source:
                by_source[source_name] = {
                    "total": 0,
                    "full": 0,
                    "partial": 0,
                    "not_supported": 0,
                    "enhanced": 0
                }
            
            by_source[source_name]["total"] += 1
            by_source[source_name][cmd.k2_support.value] += 1
        
        return {
            "total_commands": total,
            "support_summary": {
                "full_support": support_stats[SupportLevel.FULL],
                "partial_support": support_stats[SupportLevel.PARTIAL],
                "not_supported": support_stats[SupportLevel.NOT_SUPPORTED],
                "enhanced": support_stats[SupportLevel.ENHANCED]
            },
            "support_percentage": {
                "full": round(support_stats[SupportLevel.FULL] / total * 100, 1),
                "partial": round(support_stats[SupportLevel.PARTIAL] / total * 100, 1),
                "not_supported": round(support_stats[SupportLevel.NOT_SUPPORTED] / total * 100, 1),
                "enhanced": round(support_stats[SupportLevel.ENHANCED] / total * 100, 1)
            },
            "by_source": by_source
        }
    
    def generate_command_reference(self) -> str:
        """生成命令參考文檔"""
        doc = """# PowerAutomation v4.75 命令參考

## K2 模式命令支持度報告

"""
        report = self.get_k2_support_report()
        
        doc += f"""### 總體支持情況
- 總命令數：{report['total_commands']}
- 完全支持：{report['support_summary']['full_support']} ({report['support_percentage']['full']}%)
- 部分支持：{report['support_summary']['partial_support']} ({report['support_percentage']['partial']}%)
- K2 增強：{report['support_summary']['enhanced']} ({report['support_percentage']['enhanced']}%)
- 不支持：{report['support_summary']['not_supported']} ({report['support_percentage']['not_supported']}%)

## 命令分類

"""
        
        # 按類別生成文檔
        for category, cmds in sorted(self.categories.items()):
            doc += f"### {category}\n\n"
            
            for cmd in sorted(cmds, key=lambda x: x.name):
                support_emoji = {
                    SupportLevel.FULL: "✅",
                    SupportLevel.PARTIAL: "⚠️",
                    SupportLevel.NOT_SUPPORTED: "❌",
                    SupportLevel.ENHANCED: "🚀"
                }[cmd.k2_support]
                
                doc += f"#### {cmd.name} {support_emoji}\n"
                doc += f"- **描述**：{cmd.description}\n"
                doc += f"- **語法**：`{cmd.syntax}`\n"
                doc += f"- **來源**：{cmd.source.value}\n"
                doc += f"- **K2 支持**：{cmd.k2_support.value}\n"
                
                if cmd.k2_notes:
                    doc += f"- **K2 說明**：{cmd.k2_notes}\n"
                
                if cmd.shortcuts:
                    doc += f"- **快捷方式**：{', '.join(cmd.shortcuts)}\n"
                
                doc += f"- **示例**：\n"
                for example in cmd.examples:
                    doc += f"  - `{example}`\n"
                
                doc += "\n"
        
        return doc
    
    def export_for_ui(self) -> Dict[str, Any]:
        """導出給 UI 使用的命令數據"""
        ui_data = {
            "version": "4.75",
            "generated_at": datetime.now().isoformat(),
            "categories": {}
        }
        
        for category, cmds in self.categories.items():
            ui_data["categories"][category] = []
            
            for cmd in cmds:
                cmd_data = {
                    "name": cmd.name,
                    "description": cmd.description,
                    "syntax": cmd.syntax,
                    "category": cmd.category,
                    "source": cmd.source.value,
                    "k2_support": cmd.k2_support.value,
                    "k2_notes": cmd.k2_notes,
                    "shortcuts": cmd.shortcuts or [],
                    "examples": cmd.examples
                }
                ui_data["categories"][category].append(cmd_data)
        
        # 添加快速訪問列表
        ui_data["quick_access"] = [
            cmd.name for cmd in self.commands 
            if cmd.k2_support in [SupportLevel.FULL, SupportLevel.ENHANCED]
        ][:10]  # 前10個最常用命令
        
        # 添加搜索索引
        ui_data["search_index"] = {}
        for cmd in self.commands:
            # 命令名索引
            ui_data["search_index"][cmd.name] = cmd.name
            
            # 快捷方式索引
            if cmd.shortcuts:
                for shortcut in cmd.shortcuts:
                    ui_data["search_index"][shortcut] = cmd.name
            
            # 關鍵詞索引
            keywords = cmd.description.split() + cmd.category.split()
            for keyword in keywords:
                if len(keyword) > 2:  # 忽略太短的詞
                    if keyword not in ui_data["search_index"]:
                        ui_data["search_index"][keyword] = []
                    if isinstance(ui_data["search_index"][keyword], list):
                        ui_data["search_index"][keyword].append(cmd.name)
        
        return ui_data
    
    def check_command_availability(self, command: str, mode: str = "k2") -> Dict[str, Any]:
        """檢查命令可用性"""
        # 查找命令
        cmd = None
        for c in self.commands:
            if c.name == command or (c.shortcuts and command in c.shortcuts):
                cmd = c
                break
        
        if not cmd:
            return {
                "available": False,
                "reason": "命令不存在",
                "suggestions": self._get_similar_commands(command)
            }
        
        if mode == "k2":
            if cmd.k2_support == SupportLevel.NOT_SUPPORTED:
                return {
                    "available": False,
                    "reason": "K2 模式不支持此命令",
                    "command": cmd.name,
                    "alternatives": self._get_alternatives(cmd)
                }
            elif cmd.k2_support == SupportLevel.PARTIAL:
                return {
                    "available": True,
                    "limited": True,
                    "command": cmd.name,
                    "notes": cmd.k2_notes,
                    "limitations": "部分功能可能受限"
                }
            else:
                return {
                    "available": True,
                    "command": cmd.name,
                    "enhanced": cmd.k2_support == SupportLevel.ENHANCED,
                    "notes": cmd.k2_notes
                }
        
        return {
            "available": True,
            "command": cmd.name
        }
    
    def _get_similar_commands(self, input_cmd: str) -> List[str]:
        """獲取相似命令"""
        similar = []
        input_lower = input_cmd.lower()
        
        for cmd in self.commands:
            if input_lower in cmd.name.lower() or cmd.name.lower() in input_lower:
                similar.append(cmd.name)
            elif cmd.shortcuts:
                for shortcut in cmd.shortcuts:
                    if input_lower in shortcut or shortcut in input_lower:
                        similar.append(cmd.name)
                        break
        
        return similar[:5]  # 返回前5個
    
    def _get_alternatives(self, cmd: Command) -> List[str]:
        """獲取替代命令"""
        alternatives = []
        
        # 查找同類別的其他命令
        for other_cmd in self.categories.get(cmd.category, []):
            if (other_cmd.name != cmd.name and 
                other_cmd.k2_support in [SupportLevel.FULL, SupportLevel.ENHANCED]):
                alternatives.append(other_cmd.name)
        
        return alternatives[:3]


# 創建 UI 組件
def create_command_palette_ui() -> str:
    """創建命令面板 UI 組件"""
    return """
import React, { useState, useMemo } from 'react';
import { Command, CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { Badge } from '@/components/ui/badge';

export function CommandPalette({ commands, onSelect }) {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState('');
    
    // 支持級別顏色
    const supportColors = {
        full: 'bg-green-500',
        partial: 'bg-yellow-500',
        not_supported: 'bg-red-500',
        enhanced: 'bg-blue-500'
    };
    
    // 支持級別圖標
    const supportIcons = {
        full: '✅',
        partial: '⚠️',
        not_supported: '❌',
        enhanced: '🚀'
    };
    
    // 過濾命令
    const filteredCommands = useMemo(() => {
        if (!search) return commands;
        
        const searchLower = search.toLowerCase();
        return commands.filter(cmd => 
            cmd.name.toLowerCase().includes(searchLower) ||
            cmd.description.toLowerCase().includes(searchLower) ||
            cmd.shortcuts?.some(s => s.toLowerCase().includes(searchLower)) ||
            cmd.category.toLowerCase().includes(searchLower)
        );
    }, [search, commands]);
    
    // 按類別分組
    const groupedCommands = useMemo(() => {
        const groups = {};
        filteredCommands.forEach(cmd => {
            if (!groups[cmd.category]) {
                groups[cmd.category] = [];
            }
            groups[cmd.category].push(cmd);
        });
        return groups;
    }, [filteredCommands]);
    
    return (
        <>
            <button
                onClick={() => setOpen(true)}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
                命令面板 (⌘K)
            </button>
            
            <CommandDialog open={open} onOpenChange={setOpen}>
                <Command className="rounded-lg border shadow-md">
                    <CommandInput 
                        placeholder="搜索命令..." 
                        value={search}
                        onValueChange={setSearch}
                    />
                    <CommandList>
                        <CommandEmpty>未找到匹配的命令</CommandEmpty>
                        
                        {Object.entries(groupedCommands).map(([category, cmds]) => (
                            <CommandGroup key={category} heading={category}>
                                {cmds.map(cmd => (
                                    <CommandItem
                                        key={cmd.name}
                                        value={cmd.name}
                                        onSelect={() => {
                                            onSelect(cmd);
                                            setOpen(false);
                                        }}
                                        className="flex items-center justify-between"
                                    >
                                        <div className="flex items-center gap-2">
                                            <span className="font-mono">{cmd.name}</span>
                                            <span className="text-sm text-muted-foreground">
                                                {cmd.description}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {cmd.shortcuts && (
                                                <Badge variant="outline" className="text-xs">
                                                    {cmd.shortcuts[0]}
                                                </Badge>
                                            )}
                                            <span title={`K2 支持: ${cmd.k2_support}`}>
                                                {supportIcons[cmd.k2_support]}
                                            </span>
                                        </div>
                                    </CommandItem>
                                ))}
                            </CommandGroup>
                        ))}
                    </CommandList>
                </Command>
            </CommandDialog>
        </>
    );
}

// 快速操作欄組件
export function QuickCommandBar({ commands, onExecute }) {
    const quickCommands = commands.filter(cmd => 
        cmd.k2_support === 'full' || cmd.k2_support === 'enhanced'
    ).slice(0, 8);
    
    return (
        <div className="flex items-center gap-2 p-2 bg-secondary rounded-md">
            <span className="text-sm font-medium">快速命令：</span>
            {quickCommands.map(cmd => (
                <button
                    key={cmd.name}
                    onClick={() => onExecute(cmd)}
                    className="px-3 py-1 text-sm bg-background hover:bg-accent rounded-md transition-colors"
                    title={cmd.description}
                >
                    {cmd.shortcuts?.[0] || cmd.name}
                </button>
            ))}
            <button
                onClick={() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true }))}
                className="ml-auto px-3 py-1 text-sm bg-primary text-primary-foreground rounded-md"
            >
                更多... ⌘K
            </button>
        </div>
    );
}
"""


# 測試和演示
def main():
    """主函數"""
    system = CommandSupportSystem()
    
    print("=" * 60)
    print("PowerAutomation v4.75 - 命令支持系統")
    print("=" * 60)
    
    # 生成支持報告
    report = system.get_k2_support_report()
    print("\nK2 模式支持度報告：")
    print(f"- 總命令數：{report['total_commands']}")
    print(f"- 完全支持：{report['support_percentage']['full']}%")
    print(f"- 部分支持：{report['support_percentage']['partial']}%")
    print(f"- K2 增強：{report['support_percentage']['enhanced']}%")
    
    # 生成文檔
    doc_path = Path("deploy/v4.75/COMMAND_REFERENCE.md")
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(system.generate_command_reference())
    print(f"\n✅ 命令參考文檔已生成：{doc_path}")
    
    # 生成 UI 數據
    ui_data_path = Path("deploy/v4.75/commands_ui_data.json")
    with open(ui_data_path, 'w', encoding='utf-8') as f:
        json.dump(system.export_for_ui(), f, ensure_ascii=False, indent=2)
    print(f"✅ UI 數據已生成：{ui_data_path}")
    
    # 生成 UI 組件
    ui_component_path = Path("deploy/v4.75/CommandPalette.jsx")
    with open(ui_component_path, 'w', encoding='utf-8') as f:
        f.write(create_command_palette_ui())
    print(f"✅ UI 組件已生成：{ui_component_path}")
    
    # 測試命令可用性
    print("\n測試命令可用性：")
    test_commands = ["/model", "/deploy", "/train", "/unknown"]
    for cmd in test_commands:
        result = system.check_command_availability(cmd)
        print(f"- {cmd}: {result}")


if __name__ == "__main__":
    main()