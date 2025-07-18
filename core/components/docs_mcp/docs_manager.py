"""
Documentation MCP - 統一文檔管理平台
負責生成、維護、版本化所有文檔
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import markdown
import yaml

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """文檔元數據"""
    id: str
    title: str
    category: str  # api, guide, tutorial, reference, changelog
    version: str
    created_at: str
    updated_at: str
    author: str
    tags: List[str]
    status: str  # draft, review, published, deprecated
    
    
class DocumentationManager:
    """文檔管理器"""
    
    def __init__(self, version: str = "4.73"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.version = version
        self.root_path = Path("/Users/alexchuang/alexchuangtest/aicore0718")
        self.deploy_path = Path(f"/Users/alexchuang/alexchuangtest/aicore0718/deploy/v{version}")
        self.docs_path = self.deploy_path / "docs"
        
    async def initialize(self):
        """初始化 Documentation MCP"""
        self.logger.info("📚 初始化 Documentation MCP")
        
        # 創建文檔結構
        await self._create_doc_structure()
        
        # 載入現有文檔
        await self._load_existing_docs()
        
        self.logger.info("✅ Documentation MCP 初始化完成")
        
    async def _create_doc_structure(self):
        """創建標準文檔結構"""
        # 版本化文檔目錄結構
        categories = [
            "api",           # API 文檔
            "guides",        # 使用指南
            "tutorials",     # 教程
            "references",    # 參考文檔
            "architecture",  # 架構文檔
            "changelog",     # 變更日誌
            "migration",     # 遷移指南
        ]
        
        # 在 deploy/version/docs 下創建目錄
        for category in categories:
            category_path = self.docs_path / category
            category_path.mkdir(parents=True, exist_ok=True)
            
    async def generate_api_documentation(self, mcp_name: str) -> Dict[str, Any]:
        """為 MCP 生成 API 文檔"""
        self.logger.info(f"生成 {mcp_name} 的 API 文檔")
        
        # 分析 MCP 代碼獲取 API 信息
        api_info = await self._analyze_mcp_apis(mcp_name)
        
        # 生成 OpenAPI/Swagger 規範
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{mcp_name} API",
                "version": "1.0.0",
                "description": f"API documentation for {mcp_name} MCP"
            },
            "paths": api_info.get("endpoints", {}),
            "components": {
                "schemas": api_info.get("schemas", {})
            }
        }
        
        # 保存 API 文檔到版本目錄
        api_doc_path = self.docs_path / "api" / f"{mcp_name}_api.json"
        with open(api_doc_path, 'w', encoding='utf-8') as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
            
        # 生成 Markdown 版本
        markdown_content = await self._generate_api_markdown(mcp_name, api_info)
        markdown_path = self.docs_path / "api" / f"{mcp_name}_api.md"
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return {
            "mcp_name": mcp_name,
            "api_doc_path": str(api_doc_path),
            "markdown_path": str(markdown_path),
            "endpoints_count": len(api_info.get("endpoints", {}))
        }
        
    async def generate_user_guide(self, topic: str, content_outline: Dict[str, Any]) -> str:
        """生成用戶指南"""
        self.logger.info(f"生成用戶指南: {topic}")
        
        guide_content = f"""# {topic} 使用指南

## 目錄
"""
        
        # 生成目錄
        for i, section in enumerate(content_outline.get("sections", []), 1):
            guide_content += f"{i}. [{section['title']}](#{section['id']})\n"
            
        guide_content += "\n---\n\n"
        
        # 生成各章節內容
        for section in content_outline.get("sections", []):
            guide_content += f"""## {section['title']} {{#{section['id']}}}

{section.get('content', '')}

"""
            
            # 添加代碼示例
            if "code_examples" in section:
                for example in section["code_examples"]:
                    guide_content += f"""### 示例：{example['title']}

```{example.get('language', 'python')}
{example['code']}
```

{example.get('explanation', '')}

"""
        
        # 保存指南到版本目錄
        guide_path = self.docs_path / "guides" / f"{topic.lower().replace(' ', '_')}_guide.md"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
            
        return str(guide_path)
        
    async def generate_architecture_docs(self) -> Dict[str, Any]:
        """生成架構文檔"""
        self.logger.info("生成架構文檔")
        
        # 分析項目結構
        architecture_info = await self._analyze_project_architecture()
        
        # 生成架構圖（使用 Mermaid）
        mermaid_diagram = """```mermaid
graph TD
    A[PowerAutomation v4.73] --> B[Core]
    A --> C[MCP Components]
    A --> D[ClaudeEditor]
    
    B --> B1[MCP-Zero Engine]
    B --> B2[Workflows]
    B --> B3[API Server]
    
    C --> C1[Test MCP]
    C --> C2[Docs MCP]
    C --> C3[CodeFlow MCP]
    C --> C4[Other MCPs...]
    
    D --> D1[UI Components]
    D --> D2[Services]
    D --> D3[Integration]
```"""
        
        # 生成架構文檔
        arch_content = f"""# PowerAutomation 架構文檔

## 系統概覽

{mermaid_diagram}

## 核心組件

### 1. MCP-Zero 動態加載架構
- 智能任務分解
- 按需加載 MCP
- 上下文優化

### 2. 六大工作流
1. 需求分析
2. 架構設計
3. 編碼實現
4. 測試驗證
5. 部署發布
6. 監控運維

### 3. MCP 組件
{self._generate_mcp_list()}

## 技術棧
- 後端：Python 3.9+, FastAPI
- 前端：React, TypeScript, Monaco Editor
- 測試：pytest, Playwright
- 部署：Docker, K8s

更新時間：{datetime.now().isoformat()}
"""
        
        arch_path = self.docs_path / "architecture" / "system_architecture.md"
        with open(arch_path, 'w', encoding='utf-8') as f:
            f.write(arch_content)
            
        return {
            "architecture_doc": str(arch_path),
            "components_count": len(architecture_info.get("components", [])),
            "last_updated": datetime.now().isoformat()
        }
        
    async def generate_changelog(self, version: str, changes: List[Dict[str, Any]]) -> str:
        """生成變更日誌"""
        self.logger.info(f"生成版本 {version} 的變更日誌")
        
        changelog_content = f"""# 變更日誌 - v{version}

發布日期：{datetime.now().strftime('%Y-%m-%d')}

## 🎯 主要更新

"""
        
        # 按類型組織變更
        features = [c for c in changes if c["type"] == "feature"]
        fixes = [c for c in changes if c["type"] == "fix"]
        improvements = [c for c in changes if c["type"] == "improvement"]
        
        if features:
            changelog_content += "### ✨ 新功能\n\n"
            for feature in features:
                changelog_content += f"- {feature['description']}\n"
            changelog_content += "\n"
            
        if improvements:
            changelog_content += "### 🚀 改進\n\n"
            for imp in improvements:
                changelog_content += f"- {imp['description']}\n"
            changelog_content += "\n"
            
        if fixes:
            changelog_content += "### 🐛 修復\n\n"
            for fix in fixes:
                changelog_content += f"- {fix['description']}\n"
            changelog_content += "\n"
            
        # 保存變更日誌到版本目錄
        changelog_path = self.docs_path / "changelog" / f"CHANGELOG_v{version}.md"
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(changelog_content)
            
        # 更新主 CHANGELOG
        await self._update_main_changelog(version, changelog_content)
        
        return str(changelog_path)
        
    async def version_docs(self, version: str):
        """版本化文檔"""
        self.logger.info(f"創建版本 {version} 的文檔快照")
        
        # 目標路徑
        version_docs_path = self.versioned_docs_path / f"v{version}" / "docs"
        version_docs_path.mkdir(parents=True, exist_ok=True)
        
        # 複製當前文檔到版本目錄
        import shutil
        for category in ["api", "guides", "tutorials", "references", "architecture"]:
            src = self.docs_base_path / category
            dst = version_docs_path / category
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                
        # 生成版本索引
        index_content = f"""# PowerAutomation v{version} 文檔

## 文檔目錄

- [API 文檔](./api/)
- [使用指南](./guides/)
- [教程](./tutorials/)
- [參考文檔](./references/)
- [架構文檔](./architecture/)
- [變更日誌](./changelog/)

生成時間：{datetime.now().isoformat()}
"""
        
        index_path = version_docs_path / "README.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
            
        self.logger.info(f"文檔已版本化到: {version_docs_path}")
        
    async def search_docs(self, query: str) -> List[Dict[str, Any]]:
        """搜索文檔"""
        results = []
        
        # 搜索版本目錄下的所有 markdown 文件
        for md_file in self.docs_path.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if query.lower() in content.lower():
                # 提取相關段落
                lines = content.split('\n')
                relevant_lines = []
                
                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        # 獲取上下文（前後各2行）
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        relevant_lines.extend(lines[start:end])
                        
                results.append({
                    "file": str(md_file.relative_to(self.docs_path)),
                    "category": md_file.parent.name,
                    "preview": '\n'.join(relevant_lines[:5]),
                    "score": content.lower().count(query.lower())
                })
                
        # 按相關性排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:10]  # 返回前10個結果
        
    async def _analyze_mcp_apis(self, mcp_name: str) -> Dict[str, Any]:
        """分析 MCP 的 API"""
        # 這裡應該實際分析代碼，現在返回示例數據
        return {
            "endpoints": {
                f"/api/{mcp_name}/status": {
                    "get": {
                        "summary": f"Get {mcp_name} status",
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": f"#/components/schemas/{mcp_name}Status"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "schemas": {
                f"{mcp_name}Status": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "version": {"type": "string"}
                    }
                }
            }
        }
        
    async def _generate_api_markdown(self, mcp_name: str, api_info: Dict[str, Any]) -> str:
        """生成 API Markdown 文檔"""
        content = f"""# {mcp_name} API 文檔

## 端點列表

"""
        for endpoint, methods in api_info.get("endpoints", {}).items():
            for method, details in methods.items():
                content += f"### {method.upper()} {endpoint}\n\n"
                content += f"{details.get('summary', '')}\n\n"
                
        return content
        
    def _generate_mcp_list(self) -> str:
        """生成 MCP 列表"""
        from core.mcp_zero import mcp_registry
        
        mcp_list = ""
        for name, meta in mcp_registry.mcp_catalog.items():
            mcp_list += f"- **{name}**: {meta.description}\n"
            
        return mcp_list
        
    async def _analyze_project_architecture(self) -> Dict[str, Any]:
        """分析項目架構"""
        return {
            "components": ["core", "mcp_components", "claudeditor", "deployment"],
            "layers": ["presentation", "business", "data"],
            "patterns": ["MCP", "Plugin", "Observer"]
        }
        
    async def update_root_readme(self, update_type: str, content: Dict[str, Any]):
        """更新根目錄的 README.md"""
        readme_path = self.root_path / "README.md"
        
        if update_type == "architecture":
            # 更新架構部分
            await self._update_readme_section(readme_path, "## 系統架構", content.get("architecture", ""))
        elif update_type == "installation":
            # 更新安裝說明
            await self._update_readme_section(readme_path, "## 安裝說明", content.get("installation", ""))
        elif update_type == "version":
            # 更新版本信息
            await self._update_readme_section(readme_path, "## 當前版本", f"v{self.version}")
            
    async def _update_readme_section(self, readme_path: Path, section_title: str, new_content: str):
        """更新 README 的特定章節"""
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = ["# PowerAutomation\n", "\n"]
            
        # 查找章節位置
        section_start = -1
        next_section_start = len(lines)
        
        for i, line in enumerate(lines):
            if line.strip() == section_title:
                section_start = i
            elif section_start >= 0 and line.startswith("## "):
                next_section_start = i
                break
                
        # 更新章節內容
        if section_start >= 0:
            # 替換現有章節
            new_lines = lines[:section_start+1] + ["\n", new_content, "\n"] + lines[next_section_start:]
        else:
            # 添加新章節
            new_lines = lines + ["\n", section_title, "\n", new_content, "\n"]
            
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
    async def _update_main_changelog(self, version: str, content: str):
        """更新主變更日誌"""
        # 主 CHANGELOG 放在根目錄
        main_changelog = self.root_path / "CHANGELOG.md"
        
        if main_changelog.exists():
            with open(main_changelog, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        else:
            existing_content = "# PowerAutomation 變更日誌\n\n"
            
        # 在開頭插入新版本
        new_content = existing_content.replace(
            "# PowerAutomation 變更日誌\n\n",
            f"# PowerAutomation 變更日誌\n\n{content}\n---\n\n"
        )
        
        with open(main_changelog, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    async def _load_existing_docs(self):
        """載入現有文檔"""
        self.logger.info("載入現有文檔...")
        # 實際實現中應該掃描並索引所有文檔
        
    def get_status(self) -> Dict[str, Any]:
        """獲取 Documentation MCP 狀態"""
        # 統計文檔數量
        doc_count = {}
        if self.docs_path.exists():
            doc_count = {
                "api": len(list((self.docs_path / "api").glob("*.md"))) if (self.docs_path / "api").exists() else 0,
                "guides": len(list((self.docs_path / "guides").glob("*.md"))) if (self.docs_path / "guides").exists() else 0,
                "tutorials": len(list((self.docs_path / "tutorials").glob("*.md"))) if (self.docs_path / "tutorials").exists() else 0,
                "references": len(list((self.docs_path / "references").glob("*.md"))) if (self.docs_path / "references").exists() else 0,
                "architecture": len(list((self.docs_path / "architecture").glob("*.md"))) if (self.docs_path / "architecture").exists() else 0,
            }
        
        return {
            "component": "Documentation MCP",
            "version": self.version,
            "status": "running",
            "document_count": doc_count,
            "total_documents": sum(doc_count.values()) if doc_count else 0,
            "docs_path": str(self.docs_path),
            "deploy_path": str(self.deploy_path)
        }


# 單例實例
docs_manager = DocumentationManager()