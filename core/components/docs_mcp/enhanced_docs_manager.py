#!/usr/bin/env python3
"""
Enhanced Documentation MCP - 主動文檔掃描和重構系統
自動掃描、整理、更新項目中的所有文檔
"""

import asyncio
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import re
import yaml
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentInfo:
    """文檔信息"""
    path: Path
    title: str
    category: str
    last_modified: datetime
    size: int
    format: str  # md, json, yaml, txt
    status: str  # active, outdated, duplicate, orphaned
    issues: List[str] = None
    
@dataclass
class ScanResult:
    """掃描結果"""
    total_files: int
    categorized_files: Dict[str, List[DocumentInfo]]
    issues_found: Dict[str, List[str]]
    suggestions: List[str]
    scan_time: datetime

class EnhancedDocumentationManager:
    """增強版文檔管理器 - 主動掃描和重構"""
    
    def __init__(self):
        self.root_path = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        
        # 定義掃描目錄
        self.scan_directories = [
            "docs/",
            "deploy/",
            "business/",
            "core/components/*/README.md",
            "core/components/*/docs/",
            "README.md",
            "CHANGELOG.md",
            "*.md"
        ]
        
        # 文檔分類規則
        self.categorization_rules = {
            "api": ["api", "endpoint", "swagger", "openapi"],
            "architecture": ["architecture", "design", "structure", "diagram"],
            "guide": ["guide", "tutorial", "howto", "getting-started"],
            "reference": ["reference", "spec", "specification"],
            "deployment": ["deploy", "installation", "setup", "docker", "k8s"],
            "business": ["business", "requirement", "roi", "value"],
            "changelog": ["changelog", "release", "version"],
            "readme": ["readme"],
            "mcp": ["mcp_", "_mcp"],
            "component": ["component", "module"]
        }
        
        # 文檔模板
        self.templates = self._load_templates()
        
        # 掃描結果緩存
        self.last_scan_result: Optional[ScanResult] = None
        
    def _load_templates(self) -> Dict[str, str]:
        """加載文檔模板"""
        return {
            "readme": """# {title}

## 概述
{description}

## 功能特性
- 

## 安裝使用
```bash
# 安裝
# 使用
```

## API 文檔
[API Documentation](./docs/api.md)

## 配置說明
{configuration}

## 常見問題
{faq}

## 貢獻指南
{contributing}

## 許可證
{license}
""",
            "api": """# {title} API 文檔

## 端點列表

### {endpoint_name}
- **方法**: {method}
- **路徑**: {path}
- **描述**: {description}

#### 請求參數
{parameters}

#### 響應格式
```json
{response_example}
```

#### 錯誤碼
{error_codes}
""",
            "mcp": """# {mcp_name} MCP

## 概述
{description}

## 能力列表
{capabilities}

## 優先級
{priority}

## 依賴關係
{dependencies}

## 使用方法
```python
{usage_example}
```

## 配置
{configuration}

## 性能指標
- 響應時間: {response_time}
- 成功率: {success_rate}
- 資源使用: {resource_usage}
"""
        }
    
    async def scan_all_documents(self) -> ScanResult:
        """掃描所有文檔"""
        logger.info("🔍 開始掃描項目文檔...")
        
        all_documents = []
        issues = {
            "missing": [],
            "outdated": [],
            "duplicate": [],
            "uncategorized": [],
            "format_issues": []
        }
        
        # 掃描各個目錄
        for pattern in self.scan_directories:
            if "*" in pattern:
                # 使用 glob 模式
                for file_path in self.root_path.glob(pattern):
                    if file_path.is_file():
                        doc_info = await self._analyze_document(file_path)
                        all_documents.append(doc_info)
            else:
                # 直接路徑
                target_path = self.root_path / pattern
                if target_path.exists():
                    if target_path.is_file():
                        doc_info = await self._analyze_document(target_path)
                        all_documents.append(doc_info)
                    else:
                        # 掃描目錄
                        for file_path in target_path.rglob("*"):
                            if file_path.is_file() and file_path.suffix in ['.md', '.json', '.yaml', '.yml', '.txt']:
                                doc_info = await self._analyze_document(file_path)
                                all_documents.append(doc_info)
        
        # 分類文檔
        categorized = self._categorize_documents(all_documents)
        
        # 檢查問題
        issues = await self._check_document_issues(all_documents, categorized)
        
        # 生成建議
        suggestions = self._generate_suggestions(categorized, issues)
        
        result = ScanResult(
            total_files=len(all_documents),
            categorized_files=categorized,
            issues_found=issues,
            suggestions=suggestions,
            scan_time=datetime.now()
        )
        
        self.last_scan_result = result
        logger.info(f"✅ 掃描完成：發現 {result.total_files} 個文檔")
        
        return result
    
    async def _analyze_document(self, file_path: Path) -> DocumentInfo:
        """分析單個文檔"""
        stat = file_path.stat()
        
        # 讀取文檔內容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            content = ""
        
        # 提取標題
        title = self._extract_title(file_path, content)
        
        # 判斷類別
        category = self._determine_category(file_path, content)
        
        # 檢查狀態
        status = self._check_document_status(file_path, content, stat.st_mtime)
        
        # 檢查問題
        issues = self._check_document_issues_single(file_path, content)
        
        return DocumentInfo(
            path=file_path,
            title=title,
            category=category,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            size=stat.st_size,
            format=file_path.suffix[1:] if file_path.suffix else 'unknown',
            status=status,
            issues=issues
        )
    
    def _extract_title(self, file_path: Path, content: str) -> str:
        """提取文檔標題"""
        # 從內容提取
        if content:
            # Markdown 標題
            match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if match:
                return match.group(1).strip()
            
            # JSON title 字段
            if file_path.suffix == '.json':
                try:
                    data = json.loads(content)
                    if isinstance(data, dict) and 'title' in data:
                        return data['title']
                except:
                    pass
        
        # 從文件名提取
        return file_path.stem.replace('_', ' ').replace('-', ' ').title()
    
    def _determine_category(self, file_path: Path, content: str) -> str:
        """判斷文檔類別"""
        path_str = str(file_path).lower()
        content_lower = content.lower() if content else ""
        
        for category, keywords in self.categorization_rules.items():
            for keyword in keywords:
                if keyword in path_str or keyword in content_lower:
                    return category
        
        return "uncategorized"
    
    def _check_document_status(self, file_path: Path, content: str, mtime: float) -> str:
        """檢查文檔狀態"""
        # 檢查是否過期（超過3個月未更新）
        if (datetime.now().timestamp() - mtime) > 90 * 24 * 3600:
            return "outdated"
        
        # 檢查是否為空或過小
        if len(content.strip()) < 100:
            return "incomplete"
        
        # 檢查是否包含 TODO 或 FIXME
        if "TODO" in content or "FIXME" in content:
            return "needs_update"
        
        return "active"
    
    def _check_document_issues_single(self, file_path: Path, content: str) -> List[str]:
        """檢查單個文檔的問題"""
        issues = []
        
        # 檢查格式問題
        if file_path.suffix == '.md':
            # 檢查是否缺少標題
            if not re.search(r'^#\s+', content, re.MULTILINE):
                issues.append("missing_title")
            
            # 檢查鏈接是否有效
            broken_links = self._check_broken_links(file_path, content)
            if broken_links:
                issues.append(f"broken_links: {len(broken_links)}")
        
        # 檢查編碼問題
        if '\ufffd' in content:
            issues.append("encoding_issue")
        
        return issues
    
    def _check_broken_links(self, file_path: Path, content: str) -> List[str]:
        """檢查損壞的鏈接"""
        broken = []
        
        # 提取所有相對鏈接
        links = re.findall(r'\[.*?\]\(((?!http).*?)\)', content)
        
        for link in links:
            # 解析相對路徑
            target = file_path.parent / link
            if not target.exists():
                broken.append(link)
        
        return broken
    
    def _categorize_documents(self, documents: List[DocumentInfo]) -> Dict[str, List[DocumentInfo]]:
        """分類文檔"""
        categorized = {}
        
        for doc in documents:
            if doc.category not in categorized:
                categorized[doc.category] = []
            categorized[doc.category].append(doc)
        
        return categorized
    
    async def _check_document_issues(self, all_docs: List[DocumentInfo], categorized: Dict[str, List[DocumentInfo]]) -> Dict[str, List[str]]:
        """檢查文檔問題"""
        issues = {
            "missing": [],
            "outdated": [],
            "duplicate": [],
            "uncategorized": [],
            "format_issues": []
        }
        
        # 檢查必需文檔是否存在
        required_docs = ["README.md", "CHANGELOG.md", "LICENSE"]
        existing_names = [doc.path.name for doc in all_docs]
        
        for req in required_docs:
            if req not in existing_names:
                issues["missing"].append(req)
        
        # 檢查過期文檔
        for doc in all_docs:
            if doc.status == "outdated":
                issues["outdated"].append(str(doc.path.relative_to(self.root_path)))
        
        # 檢查重複文檔
        seen_titles = {}
        for doc in all_docs:
            if doc.title in seen_titles:
                issues["duplicate"].append(f"{doc.title}: {doc.path} vs {seen_titles[doc.title]}")
            else:
                seen_titles[doc.title] = doc.path
        
        # 未分類文檔
        if "uncategorized" in categorized:
            for doc in categorized["uncategorized"]:
                issues["uncategorized"].append(str(doc.path.relative_to(self.root_path)))
        
        return issues
    
    def _generate_suggestions(self, categorized: Dict[str, List[DocumentInfo]], issues: Dict[str, List[str]]) -> List[str]:
        """生成改進建議"""
        suggestions = []
        
        # 基於問題生成建議
        if issues["missing"]:
            suggestions.append(f"創建缺失的文檔：{', '.join(issues['missing'])}")
        
        if issues["outdated"]:
            suggestions.append(f"更新過期文檔（{len(issues['outdated'])} 個）")
        
        if issues["duplicate"]:
            suggestions.append(f"合併或刪除重複文檔（{len(issues['duplicate'])} 組）")
        
        if issues["uncategorized"]:
            suggestions.append(f"為 {len(issues['uncategorized'])} 個文檔添加分類")
        
        # 結構化建議
        if "api" not in categorized or len(categorized.get("api", [])) < 5:
            suggestions.append("增加 API 文檔覆蓋率")
        
        if "guide" not in categorized or len(categorized.get("guide", [])) < 3:
            suggestions.append("創建更多用戶指南")
        
        # MCP 文檔建議
        mcp_docs = categorized.get("mcp", [])
        if len(mcp_docs) < 10:  # 假設有更多 MCP
            suggestions.append("為所有 MCP 組件創建文檔")
        
        return suggestions
    
    async def reorganize_documents(self, dry_run: bool = True) -> Dict[str, Any]:
        """重組文檔結構"""
        if not self.last_scan_result:
            await self.scan_all_documents()
        
        logger.info(f"📁 開始重組文檔結構 (dry_run={dry_run})")
        
        reorganization_plan = {
            "moves": [],
            "creates": [],
            "updates": []
        }
        
        # 創建標準目錄結構
        standard_structure = {
            "docs/api": "API 文檔",
            "docs/guides": "用戶指南", 
            "docs/architecture": "架構文檔",
            "docs/deployment": "部署文檔",
            "docs/components": "組件文檔",
            "docs/references": "參考文檔",
            "business": "業務文檔"
        }
        
        # 規劃文檔移動
        for category, docs in self.last_scan_result.categorized_files.items():
            if category == "uncategorized":
                continue
                
            target_dir = None
            if category == "api":
                target_dir = self.root_path / "docs" / "api"
            elif category == "guide":
                target_dir = self.root_path / "docs" / "guides"
            elif category == "architecture":
                target_dir = self.root_path / "docs" / "architecture"
            elif category == "deployment":
                target_dir = self.root_path / "docs" / "deployment"
            elif category == "mcp" or category == "component":
                target_dir = self.root_path / "docs" / "components"
            elif category == "business":
                target_dir = self.root_path / "business"
            
            if target_dir:
                for doc in docs:
                    # 檢查是否需要移動
                    if not str(doc.path).startswith(str(target_dir)):
                        new_path = target_dir / doc.path.name
                        reorganization_plan["moves"].append({
                            "from": str(doc.path.relative_to(self.root_path)),
                            "to": str(new_path.relative_to(self.root_path)),
                            "reason": f"歸類到 {category} 目錄"
                        })
        
        # 規劃創建缺失文檔
        for missing in self.last_scan_result.issues_found.get("missing", []):
            reorganization_plan["creates"].append({
                "path": missing,
                "template": "readme" if missing == "README.md" else "default",
                "reason": "必需文檔缺失"
            })
        
        # 執行重組
        if not dry_run:
            # 創建目錄
            for dir_path in standard_structure.keys():
                (self.root_path / dir_path).mkdir(parents=True, exist_ok=True)
            
            # 移動文件
            for move in reorganization_plan["moves"]:
                src = self.root_path / move["from"]
                dst = self.root_path / move["to"]
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dst))
                    logger.info(f"移動: {move['from']} -> {move['to']}")
            
            # 創建缺失文檔
            for create in reorganization_plan["creates"]:
                await self.create_document_from_template(
                    create["path"],
                    create["template"]
                )
        
        return reorganization_plan
    
    async def create_document_from_template(self, path: str, template_name: str) -> str:
        """從模板創建文檔"""
        template = self.templates.get(template_name, self.templates["readme"])
        
        # 填充模板
        content = template.format(
            title=Path(path).stem.replace('_', ' ').title(),
            description="待補充",
            configuration="待補充",
            faq="待補充",
            contributing="請參考貢獻指南",
            license="MIT"
        )
        
        file_path = self.root_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"創建文檔: {path}")
        return str(file_path)
    
    async def generate_documentation_index(self) -> str:
        """生成文檔索引"""
        if not self.last_scan_result:
            await self.scan_all_documents()
        
        index_content = """# PowerAutomation 文檔索引

> 自動生成於 {timestamp}

## 📚 文檔統計
- 總文檔數：{total_docs}
- 最後更新：{last_update}

## 📂 文檔分類

""".format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_docs=self.last_scan_result.total_files,
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        
        # 按類別生成索引
        for category, docs in sorted(self.last_scan_result.categorized_files.items()):
            if not docs:
                continue
                
            index_content += f"### {category.title()}\n\n"
            
            # 按最後修改時間排序
            sorted_docs = sorted(docs, key=lambda d: d.last_modified, reverse=True)
            
            for doc in sorted_docs[:10]:  # 每類最多顯示10個
                rel_path = doc.path.relative_to(self.root_path)
                index_content += f"- [{doc.title}](./{rel_path})"
                
                if doc.status != "active":
                    index_content += f" ⚠️ *{doc.status}*"
                
                index_content += f" - {doc.last_modified.strftime('%Y-%m-%d')}\n"
            
            if len(docs) > 10:
                index_content += f"- ... 還有 {len(docs) - 10} 個文檔\n"
            
            index_content += "\n"
        
        # 問題報告
        if any(self.last_scan_result.issues_found.values()):
            index_content += "## ⚠️ 發現的問題\n\n"
            
            for issue_type, items in self.last_scan_result.issues_found.items():
                if items:
                    index_content += f"### {issue_type.replace('_', ' ').title()}\n"
                    for item in items[:5]:
                        index_content += f"- {item}\n"
                    if len(items) > 5:
                        index_content += f"- ... 還有 {len(items) - 5} 個\n"
                    index_content += "\n"
        
        # 改進建議
        if self.last_scan_result.suggestions:
            index_content += "## 💡 改進建議\n\n"
            for suggestion in self.last_scan_result.suggestions:
                index_content += f"- {suggestion}\n"
        
        # 保存索引
        index_path = self.root_path / "docs" / "INDEX.md"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        logger.info(f"生成文檔索引: {index_path}")
        return str(index_path)
    
    async def watch_and_update(self, interval: int = 3600):
        """監視並自動更新文檔"""
        logger.info(f"啟動文檔監視器，每 {interval} 秒掃描一次")
        
        while True:
            try:
                # 掃描文檔
                result = await self.scan_all_documents()
                
                # 如果發現問題，生成報告
                if any(result.issues_found.values()):
                    await self.generate_documentation_index()
                    logger.warning(f"發現 {sum(len(v) for v in result.issues_found.values())} 個文檔問題")
                
                # 等待下一次掃描
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"文檔監視器錯誤: {str(e)}")
                await asyncio.sleep(60)  # 錯誤後短暫等待
    
    def get_scan_report(self) -> Dict[str, Any]:
        """獲取掃描報告"""
        if not self.last_scan_result:
            return {"status": "no_scan_performed"}
        
        return {
            "scan_time": self.last_scan_result.scan_time.isoformat(),
            "total_documents": self.last_scan_result.total_files,
            "categories": {
                cat: len(docs) for cat, docs in self.last_scan_result.categorized_files.items()
            },
            "issues": {
                issue_type: len(items) for issue_type, items in self.last_scan_result.issues_found.items()
            },
            "suggestions": self.last_scan_result.suggestions
        }


# 創建全局實例
enhanced_docs_manager = EnhancedDocumentationManager()

# 便捷函數
async def scan_documents():
    """掃描所有文檔"""
    return await enhanced_docs_manager.scan_all_documents()

async def reorganize_docs(dry_run: bool = True):
    """重組文檔"""
    return await enhanced_docs_manager.reorganize_documents(dry_run)

async def generate_index():
    """生成文檔索引"""
    return await enhanced_docs_manager.generate_documentation_index()

# 測試函數
async def test_documentation_mcp():
    """測試 Documentation MCP"""
    print("🧪 測試 Enhanced Documentation MCP")
    print("=" * 50)
    
    # 掃描文檔
    print("\n1. 掃描所有文檔...")
    result = await scan_documents()
    print(f"   發現 {result.total_files} 個文檔")
    print(f"   分類：{list(result.categorized_files.keys())}")
    print(f"   問題：{sum(len(v) for v in result.issues_found.values())} 個")
    
    # 生成重組計劃
    print("\n2. 生成重組計劃...")
    plan = await reorganize_docs(dry_run=True)
    print(f"   計劃移動：{len(plan['moves'])} 個文件")
    print(f"   計劃創建：{len(plan['creates'])} 個文件")
    
    # 生成索引
    print("\n3. 生成文檔索引...")
    index_path = await generate_index()
    print(f"   索引已生成：{index_path}")
    
    # 顯示報告
    print("\n4. 掃描報告：")
    report = enhanced_docs_manager.get_scan_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(test_documentation_mcp())