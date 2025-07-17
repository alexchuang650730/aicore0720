"""
Knowledge Base Manager - PowerAutomation v4.8

企业级知识库管理功能，包括:
- 文档预处理和分块
- 批量文档导入
- 知识库版本管理
- 智能文档分类
- 增量更新机制

设计原则:
- 支持多种文档格式 (PDF, MD, TXT, 代码文件)
- 智能分块策略，保持语义完整性
- 高效的批量处理能力
- 与现有 LocalFileManager 集成
"""

import os
import json
import logging
import hashlib
import mimetypes
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import asyncio
import aiofiles
import re

# 文档处理库
try:
    import PyPDF2
    import markdown
    from bs4 import BeautifulSoup
except ImportError:
    PyPDF2 = None
    markdown = None
    BeautifulSoup = None

from .bedrock_manager import BedrockManager
from .rag_service import RAGService, Document

@dataclass
class DocumentChunk:
    """文档分块数据结构"""
    chunk_id: str
    parent_doc_id: str
    content: str
    metadata: Dict[str, Any]
    chunk_index: int
    total_chunks: int
    overlap_content: str = ""

@dataclass
class KnowledgeBase:
    """知识库数据结构"""
    kb_id: str
    name: str
    description: str
    document_count: int
    total_chunks: int
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self, config: Dict[str, Any], rag_service=None):
        """
        初始化知识库管理器
        
        Args:
            config: 配置参数
            rag_service: RAG 服务实例（可选，用于向后兼容）
        """
        self.config = config or {}
        self.rag_service = rag_service
        
        # 配置参数
        self.chunk_size = self.config.get("chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunk_overlap", 200)
        self.max_file_size = self.config.get("max_file_size", 50 * 1024 * 1024)  # 50MB
        self.supported_formats = self.config.get("supported_formats", [
            ".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml", ".yml",
            ".pdf", ".rst", ".tex", ".csv", ".xml", ".sql", ".sh", ".bat"
        ])
        
        # 初始化组件
        self.logger = logging.getLogger(__name__)
        self.knowledge_bases = {}
        
        # 处理统计
        self.processing_stats = {
            "total_files_processed": 0,
            "total_chunks_created": 0,
            "total_processing_time": 0.0,
            "failed_files": [],
            "last_updated": datetime.now()
        }
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化知识库管理器"""
        try:
            self.logger.info("初始化知识库管理器...")
            
            # 加载现有知识库
            await self._load_knowledge_bases()
            
            # 验证文档处理库
            missing_libs = []
            if PyPDF2 is None:
                missing_libs.append("PyPDF2")
            if markdown is None:
                missing_libs.append("markdown")
            if BeautifulSoup is None:
                missing_libs.append("beautifulsoup4")
            
            result = {
                "status": "success",
                "knowledge_bases_loaded": len(self.knowledge_bases),
                "supported_formats": self.supported_formats,
                "missing_libraries": missing_libs,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "timestamp": datetime.now().isoformat()
            }
            
            if missing_libs:
                self.logger.warning(f"缺少文档处理库: {missing_libs}")
            
            self.logger.info(f"知识库管理器初始化完成: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"知识库管理器初始化失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def create_knowledge_base(self, name: str, description: str = "", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建新的知识库
        
        Args:
            name: 知识库名称
            description: 知识库描述
            metadata: 额外元数据
            
        Returns:
            创建结果
        """
        try:
            # 生成知识库 ID
            kb_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            # 检查名称是否已存在
            for kb in self.knowledge_bases.values():
                if kb.name == name:
                    return {
                        "status": "error",
                        "error": f"知识库名称已存在: {name}"
                    }
            
            # 创建知识库对象
            knowledge_base = KnowledgeBase(
                kb_id=kb_id,
                name=name,
                description=description,
                document_count=0,
                total_chunks=0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata=metadata or {}
            )
            
            # 添加到内存
            self.knowledge_bases[kb_id] = knowledge_base
            
            # 保存到 S3
            await self._save_knowledge_bases()
            
            result = {
                "status": "success",
                "kb_id": kb_id,
                "name": name,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"知识库创建成功: {name} ({kb_id})")
            return result
            
        except Exception as e:
            self.logger.error(f"知识库创建失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def add_documents_from_directory(self, kb_id: str, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        从目录批量添加文档到知识库
        
        Args:
            kb_id: 知识库 ID
            directory_path: 目录路径
            recursive: 是否递归处理子目录
            
        Returns:
            处理结果
        """
        try:
            start_time = datetime.now()
            
            if kb_id not in self.knowledge_bases:
                return {
                    "status": "error",
                    "error": f"知识库不存在: {kb_id}"
                }
            
            directory = Path(directory_path)
            if not directory.exists() or not directory.is_dir():
                return {
                    "status": "error",
                    "error": f"目录不存在或不是有效目录: {directory_path}"
                }
            
            # 收集文件
            files_to_process = []
            if recursive:
                for file_path in directory.rglob("*"):
                    if file_path.is_file() and self._is_supported_file(file_path):
                        files_to_process.append(file_path)
            else:
                for file_path in directory.iterdir():
                    if file_path.is_file() and self._is_supported_file(file_path):
                        files_to_process.append(file_path)
            
            # 批量处理文件
            results = await self._process_files_batch(kb_id, files_to_process)
            
            # 更新知识库统计
            kb = self.knowledge_bases[kb_id]
            kb.document_count += results["successful_files"]
            kb.total_chunks += results["total_chunks"]
            kb.updated_at = datetime.now()
            
            # 保存更新
            await self._save_knowledge_bases()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": "success",
                "kb_id": kb_id,
                "directory": str(directory),
                "files_found": len(files_to_process),
                "successful_files": results["successful_files"],
                "failed_files": results["failed_files"],
                "total_chunks": results["total_chunks"],
                "processing_time_seconds": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"目录文档批量添加完成: {directory_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"目录文档批量添加失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "directory": directory_path
            }
    
    async def add_single_document(self, kb_id: str, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        添加单个文档到知识库
        
        Args:
            kb_id: 知识库 ID
            file_path: 文件路径
            metadata: 文档元数据
            
        Returns:
            处理结果
        """
        try:
            if kb_id not in self.knowledge_bases:
                return {
                    "status": "error",
                    "error": f"知识库不存在: {kb_id}"
                }
            
            file_path = Path(file_path)
            if not file_path.exists() or not file_path.is_file():
                return {
                    "status": "error",
                    "error": f"文件不存在: {file_path}"
                }
            
            if not self._is_supported_file(file_path):
                return {
                    "status": "error",
                    "error": f"不支持的文件格式: {file_path.suffix}"
                }
            
            # 处理单个文件
            result = await self._process_single_file(kb_id, file_path, metadata)
            
            if result["status"] == "success":
                # 更新知识库统计
                kb = self.knowledge_bases[kb_id]
                kb.document_count += 1
                kb.total_chunks += result["chunks_created"]
                kb.updated_at = datetime.now()
                
                # 保存更新
                await self._save_knowledge_bases()
            
            return result
            
        except Exception as e:
            self.logger.error(f"单个文档添加失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "file_path": str(file_path)
            }
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """检查文件是否为支持的格式"""
        return file_path.suffix.lower() in self.supported_formats and file_path.stat().st_size <= self.max_file_size
    
    async def _process_files_batch(self, kb_id: str, file_paths: List[Path]) -> Dict[str, Any]:
        """批量处理文件"""
        successful_files = 0
        failed_files = []
        total_chunks = 0
        
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(5)  # 最多同时处理 5 个文件
        
        async def process_with_semaphore(file_path):
            async with semaphore:
                return await self._process_single_file(kb_id, file_path)
        
        # 并发处理文件
        tasks = [process_with_semaphore(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_files.append({
                    "file": str(file_paths[i]),
                    "error": str(result)
                })
            elif result["status"] == "success":
                successful_files += 1
                total_chunks += result["chunks_created"]
            else:
                failed_files.append({
                    "file": str(file_paths[i]),
                    "error": result.get("error", "未知错误")
                })
        
        return {
            "successful_files": successful_files,
            "failed_files": failed_files,
            "total_chunks": total_chunks
        }
    
    async def _process_single_file(self, kb_id: str, file_path: Path, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理单个文件"""
        try:
            start_time = datetime.now()
            
            # 读取文件内容
            content = await self._read_file_content(file_path)
            if not content:
                return {
                    "status": "error",
                    "error": "文件内容为空或读取失败"
                }
            
            # 生成文档 ID
            doc_id = hashlib.md5(f"{file_path}_{content[:100]}".encode()).hexdigest()
            
            # 准备文档元数据
            doc_metadata = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "file_type": file_path.suffix,
                "mime_type": mimetypes.guess_type(str(file_path))[0],
                "kb_id": kb_id,
                "processed_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # 文档分块
            chunks = await self._chunk_document(doc_id, content, doc_metadata)
            
            # 添加分块到 RAG 系统
            chunks_added = 0
            for chunk in chunks:
                chunk_doc = Document(
                    id=chunk.chunk_id,
                    content=chunk.content,
                    metadata={
                        **chunk.metadata,
                        "parent_doc_id": chunk.parent_doc_id,
                        "chunk_index": chunk.chunk_index,
                        "total_chunks": chunk.total_chunks
                    }
                )
                
                # 添加到 RAG 服务
                add_result = await self.rag_service.add_document(
                    chunk_doc.content,
                    chunk_doc.metadata
                )
                
                if add_result["status"] == "success":
                    chunks_added += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 更新统计
            self.processing_stats["total_files_processed"] += 1
            self.processing_stats["total_chunks_created"] += chunks_added
            self.processing_stats["total_processing_time"] += processing_time
            
            result = {
                "status": "success",
                "doc_id": doc_id,
                "file_path": str(file_path),
                "content_length": len(content),
                "chunks_created": chunks_added,
                "processing_time_seconds": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"文件处理成功: {file_path.name} ({chunks_added} 个分块)")
            return result
            
        except Exception as e:
            self.logger.error(f"文件处理失败 {file_path}: {str(e)}")
            self.processing_stats["failed_files"].append({
                "file": str(file_path),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return {
                "status": "error",
                "error": str(e),
                "file_path": str(file_path)
            }
    
    async def _read_file_content(self, file_path: Path) -> str:
        """读取文件内容"""
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension == ".pdf":
                return await self._read_pdf_content(file_path)
            elif file_extension == ".md":
                return await self._read_markdown_content(file_path)
            elif file_extension in [".html", ".htm"]:
                return await self._read_html_content(file_path)
            else:
                # 文本文件
                async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return await f.read()
                    
        except Exception as e:
            self.logger.error(f"文件读取失败 {file_path}: {str(e)}")
            return ""
    
    async def _read_pdf_content(self, file_path: Path) -> str:
        """读取 PDF 文件内容"""
        if PyPDF2 is None:
            self.logger.warning("PyPDF2 未安装，跳过 PDF 文件")
            return ""
        
        try:
            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            return content.strip()
        except Exception as e:
            self.logger.error(f"PDF 读取失败 {file_path}: {str(e)}")
            return ""
    
    async def _read_markdown_content(self, file_path: Path) -> str:
        """读取 Markdown 文件内容"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                md_content = await f.read()
            
            if markdown is not None:
                # 转换为 HTML 然后提取纯文本
                html = markdown.markdown(md_content)
                if BeautifulSoup is not None:
                    soup = BeautifulSoup(html, 'html.parser')
                    return soup.get_text()
                else:
                    # 简单的 HTML 标签移除
                    import re
                    clean_text = re.sub('<[^<]+?>', '', html)
                    return clean_text
            else:
                # 直接返回 Markdown 内容
                return md_content
                
        except Exception as e:
            self.logger.error(f"Markdown 读取失败 {file_path}: {str(e)}")
            return ""
    
    async def _read_html_content(self, file_path: Path) -> str:
        """读取 HTML 文件内容"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = await f.read()
            
            if BeautifulSoup is not None:
                soup = BeautifulSoup(html_content, 'html.parser')
                return soup.get_text()
            else:
                # 简单的 HTML 标签移除
                import re
                clean_text = re.sub('<[^<]+?>', '', html_content)
                return clean_text
                
        except Exception as e:
            self.logger.error(f"HTML 读取失败 {file_path}: {str(e)}")
            return ""
    
    async def _chunk_document(self, doc_id: str, content: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """将文档分块"""
        try:
            chunks = []
            
            # 按段落分割
            paragraphs = self._split_into_paragraphs(content)
            
            current_chunk = ""
            chunk_index = 0
            
            for paragraph in paragraphs:
                # 检查添加当前段落是否会超过分块大小
                if len(current_chunk) + len(paragraph) + 1 <= self.chunk_size:
                    current_chunk += paragraph + "\n"
                else:
                    # 保存当前分块
                    if current_chunk.strip():
                        chunk = self._create_chunk(
                            doc_id, current_chunk.strip(), metadata, chunk_index
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                    
                    # 开始新分块
                    current_chunk = paragraph + "\n"
                    
                    # 如果单个段落就超过分块大小，需要进一步分割
                    if len(current_chunk) > self.chunk_size:
                        sub_chunks = self._split_large_paragraph(current_chunk, self.chunk_size)
                        for sub_chunk in sub_chunks:
                            chunk = self._create_chunk(
                                doc_id, sub_chunk, metadata, chunk_index
                            )
                            chunks.append(chunk)
                            chunk_index += 1
                        current_chunk = ""
            
            # 保存最后一个分块
            if current_chunk.strip():
                chunk = self._create_chunk(
                    doc_id, current_chunk.strip(), metadata, chunk_index
                )
                chunks.append(chunk)
            
            # 更新总分块数
            for chunk in chunks:
                chunk.total_chunks = len(chunks)
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"文档分块失败: {str(e)}")
            return []
    
    def _split_into_paragraphs(self, content: str) -> List[str]:
        """将内容分割为段落"""
        # 按双换行符分割段落
        paragraphs = re.split(r'\n\s*\n', content)
        
        # 过滤空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _split_large_paragraph(self, paragraph: str, max_size: int) -> List[str]:
        """分割过大的段落"""
        chunks = []
        sentences = re.split(r'[.!?]+', paragraph)
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _create_chunk(self, doc_id: str, content: str, metadata: Dict[str, Any], chunk_index: int) -> DocumentChunk:
        """创建文档分块"""
        chunk_id = f"{doc_id}_chunk_{chunk_index}"
        
        chunk_metadata = {
            **metadata,
            "chunk_type": "text",
            "chunk_method": "paragraph_based"
        }
        
        return DocumentChunk(
            chunk_id=chunk_id,
            parent_doc_id=doc_id,
            content=content,
            metadata=chunk_metadata,
            chunk_index=chunk_index,
            total_chunks=0  # 将在后面更新
        )
    
    async def _load_knowledge_bases(self):
        """从 S3 加载知识库信息"""
        try:
            result = await self.bedrock_manager.download_rag_data("knowledge_bases.json")
            
            if result["status"] == "success":
                data = json.loads(result["data"].decode('utf-8'))
                
                # 重建知识库对象
                for kb_data in data:
                    kb = KnowledgeBase(
                        kb_id=kb_data["kb_id"],
                        name=kb_data["name"],
                        description=kb_data["description"],
                        document_count=kb_data["document_count"],
                        total_chunks=kb_data["total_chunks"],
                        created_at=datetime.fromisoformat(kb_data["created_at"]),
                        updated_at=datetime.fromisoformat(kb_data["updated_at"]),
                        metadata=kb_data["metadata"]
                    )
                    self.knowledge_bases[kb.kb_id] = kb
                
                self.logger.info(f"加载了 {len(self.knowledge_bases)} 个知识库")
            else:
                self.logger.info("未找到现有知识库，从空开始")
                
        except Exception as e:
            self.logger.warning(f"知识库加载失败: {str(e)}，从空开始")
            self.knowledge_bases = {}
    
    async def _save_knowledge_bases(self):
        """保存知识库信息到 S3"""
        try:
            # 序列化知识库数据
            kb_data = []
            for kb in self.knowledge_bases.values():
                kb_data.append({
                    "kb_id": kb.kb_id,
                    "name": kb.name,
                    "description": kb.description,
                    "document_count": kb.document_count,
                    "total_chunks": kb.total_chunks,
                    "created_at": kb.created_at.isoformat(),
                    "updated_at": kb.updated_at.isoformat(),
                    "metadata": kb.metadata
                })
            
            # 保存到 S3
            json_data = json.dumps(kb_data, ensure_ascii=False, indent=2)
            await self.bedrock_manager.upload_rag_data(
                data=json_data.encode('utf-8'),
                key="knowledge_bases.json",
                metadata={
                    "type": "knowledge_bases",
                    "count": str(len(self.knowledge_bases)),
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            self.logger.info("知识库信息已保存到 S3")
            
        except Exception as e:
            self.logger.error(f"知识库信息保存失败: {str(e)}")
    
    async def list_knowledge_bases(self) -> Dict[str, Any]:
        """列出所有知识库"""
        try:
            kb_list = []
            for kb in self.knowledge_bases.values():
                kb_list.append({
                    "kb_id": kb.kb_id,
                    "name": kb.name,
                    "description": kb.description,
                    "document_count": kb.document_count,
                    "total_chunks": kb.total_chunks,
                    "created_at": kb.created_at.isoformat(),
                    "updated_at": kb.updated_at.isoformat()
                })
            
            return {
                "status": "success",
                "knowledge_bases": kb_list,
                "total_count": len(kb_list),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            "processing_stats": self.processing_stats.copy(),
            "knowledge_bases_count": len(self.knowledge_bases),
            "total_documents": sum(kb.document_count for kb in self.knowledge_bases.values()),
            "total_chunks": sum(kb.total_chunks for kb in self.knowledge_bases.values()),
            "timestamp": datetime.now().isoformat()
        }

