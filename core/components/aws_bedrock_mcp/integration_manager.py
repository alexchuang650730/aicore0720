"""
Integration Manager - PowerAutomation v4.8

统一的集成管理器，负责协调所有 aws_bedrock_mcp 组件，包括:
- 组件初始化和配置
- 与现有 MCP 架构的集成
- LocalFileManager 集成
- Claude Code 工具输出处理
- 统一的 API 接口

设计原则:
- 作为 aws_bedrock_mcp 的统一入口
- 与 PowerAutomation MCP 架构无缝集成
- 提供简单易用的 API
- 支持热插拔和动态配置
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from .bedrock_manager import BedrockManager
from .rag_service import RAGService, RAGQuery
from .knowledge_base_manager import KnowledgeBaseManager
from .document_processor import DocumentProcessor

@dataclass
class IntegrationConfig:
    """集成配置数据结构"""
    aws_region: str = "us-east-1"
    s3_bucket: str = "powerautomation-rag-storage"
    kimi_k2_endpoint: str = "https://api.moonshot.cn/v1"
    kimi_k2_api_key: str = ""
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_context_length: int = 32000
    top_k_default: int = 5
    enable_cost_tracking: bool = True
    enable_monitoring: bool = True

@dataclass
class QueryResult:
    """查询结果数据结构"""
    status: str
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    processing_time_ms: float
    cost_info: Dict[str, Any]
    metadata: Dict[str, Any]

class IntegrationManager:
    """集成管理器"""
    
    def __init__(self, config: IntegrationConfig = None):
        """
        初始化集成管理器
        
        Args:
            config: 集成配置对象
        """
        self.config = config or IntegrationConfig()
        
        # 初始化组件
        self.bedrock_manager = None
        self.rag_service = None
        self.knowledge_base_manager = None
        self.document_processor = None
        
        # 状态管理
        self.is_initialized = False
        self.initialization_error = None
        
        # 日志
        self.logger = logging.getLogger(__name__)
        
        # 统计信息
        self.stats = {
            "total_queries": 0,
            "total_documents_processed": 0,
            "total_knowledge_bases": 0,
            "avg_response_time": 0.0,
            "initialization_time": 0.0,
            "last_query_time": None,
            "uptime_start": datetime.now()
        }
    
    async def initialize(self) -> Dict[str, Any]:
        """
        初始化所有组件
        
        Returns:
            初始化结果
        """
        try:
            start_time = datetime.now()
            self.logger.info("开始初始化 PowerAutomation v4.8 集成管理器...")
            
            # 1. 初始化 Bedrock 管理器
            self.logger.info("初始化 AWS Bedrock 管理器...")
            self.bedrock_manager = BedrockManager({
                "aws_region": self.config.aws_region,
                "s3_bucket": self.config.s3_bucket
            })
            bedrock_result = await self.bedrock_manager.initialize_infrastructure()
            
            if bedrock_result["status"] != "success":
                raise Exception(f"Bedrock 管理器初始化失败: {bedrock_result.get('error')}")
            
            # 2. 初始化 RAG 服务
            self.logger.info("初始化 RAG 服务...")
            self.rag_service = RAGService(self.bedrock_manager, {
                "embedding_model": self.config.embedding_model,
                "max_context_length": self.config.max_context_length,
                "top_k_default": self.config.top_k_default,
                "kimi_k2_endpoint": self.config.kimi_k2_endpoint,
                "kimi_k2_api_key": self.config.kimi_k2_api_key
            })
            rag_result = await self.rag_service.initialize()
            
            if rag_result["status"] != "success":
                raise Exception(f"RAG 服务初始化失败: {rag_result.get('error')}")
            
            # 3. 初始化知识库管理器
            self.logger.info("初始化知识库管理器...")
            self.knowledge_base_manager = KnowledgeBaseManager(
                self.bedrock_manager, 
                self.rag_service, 
                {
                    "chunk_size": self.config.chunk_size,
                    "chunk_overlap": self.config.chunk_overlap
                }
            )
            kb_result = await self.knowledge_base_manager.initialize()
            
            if kb_result["status"] != "success":
                raise Exception(f"知识库管理器初始化失败: {kb_result.get('error')}")
            
            # 4. 初始化文档处理器
            self.logger.info("初始化文档处理器...")
            self.document_processor = DocumentProcessor({
                "preserve_code_structure": True,
                "extract_docstrings": True,
                "analyze_dependencies": True
            })
            
            # 计算初始化时间
            initialization_time = (datetime.now() - start_time).total_seconds()
            self.stats["initialization_time"] = initialization_time
            
            # 标记为已初始化
            self.is_initialized = True
            self.initialization_error = None
            
            result = {
                "status": "success",
                "message": "PowerAutomation v4.8 集成管理器初始化完成",
                "components": {
                    "bedrock_manager": bedrock_result,
                    "rag_service": rag_result,
                    "knowledge_base_manager": kb_result,
                    "document_processor": "initialized"
                },
                "initialization_time_seconds": initialization_time,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"集成管理器初始化完成，耗时 {initialization_time:.2f} 秒")
            return result
            
        except Exception as e:
            self.initialization_error = str(e)
            self.logger.error(f"集成管理器初始化失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def query(self, query: str, kb_id: str = None, top_k: int = None) -> QueryResult:
        """
        执行智能查询
        
        Args:
            query: 用户查询
            kb_id: 知识库 ID（可选，如果不指定则搜索所有）
            top_k: 返回结果数量
            
        Returns:
            查询结果
        """
        try:
            if not self.is_initialized:
                raise Exception("集成管理器未初始化")
            
            start_time = datetime.now()
            
            # 执行 RAG 查询
            result = await self.rag_service.query_with_kimi_k2(
                query=query,
                top_k=top_k or self.config.top_k_default
            )
            
            if result["status"] != "success":
                raise Exception(f"RAG 查询失败: {result.get('error')}")
            
            # 处理查询结果
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 提取源文档信息
            sources = []
            if "rag_documents_found" in result and result["rag_documents_found"] > 0:
                # 这里可以添加更详细的源文档信息提取
                sources.append({
                    "type": "rag_documents",
                    "count": result["rag_documents_found"],
                    "relevance": "high"
                })
            
            # 成本信息
            cost_info = {
                "kimi_k2_cost": 0.0,  # Kimi K2 免费
                "s3_storage_cost": 0.0001,  # 估算
                "total_cost": 0.0001
            }
            
            # 更新统计
            self.stats["total_queries"] += 1
            self.stats["last_query_time"] = datetime.now()
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (self.stats["total_queries"] - 1) + processing_time) 
                / self.stats["total_queries"]
            )
            
            query_result = QueryResult(
                status="success",
                query=query,
                answer=result["kimi_response"]["content"] if result["kimi_response"]["status"] == "success" else "查询失败",
                sources=sources,
                processing_time_ms=processing_time,
                cost_info=cost_info,
                metadata={
                    "model_used": "kimi-k2",
                    "rag_enabled": True,
                    "kb_id": kb_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"查询完成: {query[:50]}... ({processing_time:.2f}ms)")
            return query_result
            
        except Exception as e:
            self.logger.error(f"查询失败: {str(e)}")
            return QueryResult(
                status="error",
                query=query,
                answer=f"查询失败: {str(e)}",
                sources=[],
                processing_time_ms=0.0,
                cost_info={},
                metadata={"error": str(e)}
            )
    
    async def add_documents_from_directory(self, directory_path: str, kb_name: str = None) -> Dict[str, Any]:
        """
        从目录添加文档到知识库
        
        Args:
            directory_path: 目录路径
            kb_name: 知识库名称（如果不存在则创建）
            
        Returns:
            处理结果
        """
        try:
            if not self.is_initialized:
                raise Exception("集成管理器未初始化")
            
            # 确保知识库存在
            if kb_name:
                kb_list = await self.knowledge_base_manager.list_knowledge_bases()
                existing_kb = None
                
                for kb in kb_list["knowledge_bases"]:
                    if kb["name"] == kb_name:
                        existing_kb = kb
                        break
                
                if not existing_kb:
                    # 创建新知识库
                    create_result = await self.knowledge_base_manager.create_knowledge_base(
                        name=kb_name,
                        description=f"从目录 {directory_path} 创建的知识库"
                    )
                    if create_result["status"] != "success":
                        raise Exception(f"知识库创建失败: {create_result.get('error')}")
                    kb_id = create_result["kb_id"]
                else:
                    kb_id = existing_kb["kb_id"]
            else:
                # 使用默认知识库
                kb_id = "default"
                kb_list = await self.knowledge_base_manager.list_knowledge_bases()
                if not any(kb["kb_id"] == "default" for kb in kb_list["knowledge_bases"]):
                    create_result = await self.knowledge_base_manager.create_knowledge_base(
                        name="默认知识库",
                        description="默认的文档知识库"
                    )
                    if create_result["status"] == "success":
                        kb_id = create_result["kb_id"]
            
            # 添加文档
            result = await self.knowledge_base_manager.add_documents_from_directory(
                kb_id=kb_id,
                directory_path=directory_path,
                recursive=True
            )
            
            # 更新统计
            if result["status"] == "success":
                self.stats["total_documents_processed"] += result["successful_files"]
            
            self.logger.info(f"目录文档添加完成: {directory_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"目录文档添加失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "directory": directory_path
            }
    
    async def process_claude_code_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理 Claude Code 工具输出
        
        Args:
            output_data: Claude Code 输出数据
            
        Returns:
            处理结果
        """
        try:
            if not self.is_initialized:
                raise Exception("集成管理器未初始化")
            
            # 解析输出类型
            output_type = output_data.get("type", "unknown")
            
            if output_type == "file":
                # 处理文件输出
                file_path = output_data.get("path")
                content = output_data.get("content", "")
                
                if file_path and content:
                    # 使用文档处理器处理
                    processed_doc = await self.document_processor.process_document(
                        file_path=file_path,
                        content=content
                    )
                    
                    # 添加到默认知识库
                    add_result = await self.rag_service.add_document(
                        content=processed_doc.processed_content,
                        metadata={
                            **processed_doc.metadata,
                            "source": "claude_code",
                            "output_type": output_type
                        }
                    )
                    
                    return {
                        "status": "success",
                        "message": "Claude Code 文件输出已处理并添加到知识库",
                        "file_path": file_path,
                        "processing_result": add_result
                    }
            
            elif output_type == "project":
                # 处理项目输出
                project_path = output_data.get("path")
                
                if project_path:
                    # 批量处理项目文件
                    result = await self.add_documents_from_directory(
                        directory_path=project_path,
                        kb_name=f"claude_code_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                    
                    return {
                        "status": "success",
                        "message": "Claude Code 项目输出已处理",
                        "project_path": project_path,
                        "processing_result": result
                    }
            
            return {
                "status": "warning",
                "message": f"未知的 Claude Code 输出类型: {output_type}",
                "output_data": output_data
            }
            
        except Exception as e:
            self.logger.error(f"Claude Code 输出处理失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "output_data": output_data
            }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        try:
            if not self.is_initialized:
                return {
                    "status": "unhealthy",
                    "error": self.initialization_error or "未初始化",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 检查各组件健康状态
            bedrock_health = await self.bedrock_manager.get_health_status()
            rag_health = await self.rag_service.health_check()
            
            # 计算运行时间
            uptime = (datetime.now() - self.stats["uptime_start"]).total_seconds()
            
            overall_status = "healthy"
            if (bedrock_health["status"] != "healthy" or 
                rag_health["status"] != "healthy"):
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "components": {
                    "bedrock_manager": bedrock_health["status"],
                    "rag_service": rag_health["status"],
                    "knowledge_base_manager": "healthy",
                    "document_processor": "healthy"
                },
                "stats": self.stats.copy(),
                "uptime_seconds": uptime,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            info = {
                "version": "4.8.0",
                "name": "PowerAutomation AWS Bedrock MCP",
                "description": "零余额消耗的企业级 RAG 功能",
                "architecture": "Memory RAG MCP + AWS S3 + Kimi K2",
                "config": {
                    "aws_region": self.config.aws_region,
                    "s3_bucket": self.config.s3_bucket,
                    "embedding_model": self.config.embedding_model,
                    "chunk_size": self.config.chunk_size,
                    "max_context_length": self.config.max_context_length
                },
                "features": [
                    "零余额消耗",
                    "企业级 RAG",
                    "多格式文档支持",
                    "智能代码分析",
                    "实时成本追踪",
                    "Claude Code 集成"
                ],
                "is_initialized": self.is_initialized,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.is_initialized:
                # 添加运行时信息
                kb_list = await self.knowledge_base_manager.list_knowledge_bases()
                rag_stats = await self.rag_service.get_stats()
                
                info["runtime_info"] = {
                    "knowledge_bases": len(kb_list["knowledge_bases"]),
                    "total_documents": rag_stats["document_count"],
                    "vector_index_size": rag_stats["vector_index_size"],
                    "total_queries": self.stats["total_queries"]
                }
            
            return info
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'logger'):
            self.logger.info("集成管理器正在清理资源...")

