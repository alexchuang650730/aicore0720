#!/usr/bin/env python3
"""
AWS Bedrock MCP CLI - PowerAutomation v4.8

命令行接口工具，用于管理和操作 AWS Bedrock MCP 组件，包括:
- 智能路由 MCP 服务器管理
- 知识库管理和文档导入
- 系统状态监控和配置
- 开发和调试工具

设计原则:
- 遵循 PowerAutomation MCP CLI 规范
- 提供直观的命令行界面
- 支持批量操作和自动化
- 集成开发和运维工具
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from .integration_manager import IntegrationManager, IntegrationConfig
from .smart_routing_mcp import SmartRoutingMCP
from .k2_router import K2Router

class BedrockMCPCLI:
    """AWS Bedrock MCP CLI 工具"""
    
    def __init__(self):
        self.config = {}
        self.logger = None
        
    def setup_logging(self, level: str = "INFO"):
        """设置日志"""
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("bedrock-mcp-cli")
    
    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info(f"配置文件已加载: {config_path}")
            except Exception as e:
                self.logger.error(f"配置文件加载失败: {str(e)}")
                self.config = {}
        else:
            # 默认配置
            self.config = {
                "integration": {
                    "aws_region": "us-east-1",
                    "s3_bucket": "powerautomation-rag-storage",
                    "kimi_k2_endpoint": "https://api.moonshot.cn/v1",
                    "kimi_k2_api_key": os.getenv("KIMI_K2_API_KEY", ""),
                    "embedding_model": "all-MiniLM-L6-v2",
                    "chunk_size": 1000,
                    "chunk_overlap": 200
                },
                "k2_router": {
                    "api_endpoint": "https://api.moonshot.cn/v1",
                    "api_key": os.getenv("KIMI_K2_API_KEY", ""),
                    "enable_smart_routing": True,
                    "enable_context_optimization": True,
                    "max_concurrent_requests": 10,
                    "rate_limit_per_minute": 60
                },
                "routing": {
                    "enable_local_model": False,
                    "local_model_endpoint": "http://localhost:11434",
                    "fallback_strategy": "cloud_first",
                    "load_balancing": "round_robin"
                }
            }
            self.logger.info("使用默认配置")
        
        return self.config
    
    async def cmd_server(self, args):
        """启动智能路由 MCP 服务器"""
        try:
            self.logger.info("启动智能路由 MCP 服务器...")
            
            # 创建服务器实例
            server = SmartRoutingMCP(self.config)
            
            # 运行服务器
            await server.run_server(args.transport)
            
        except KeyboardInterrupt:
            self.logger.info("服务器已停止")
        except Exception as e:
            self.logger.error(f"服务器启动失败: {str(e)}")
            return 1
        
        return 0
    
    async def cmd_init(self, args):
        """初始化 AWS Bedrock MCP 环境"""
        try:
            self.logger.info("初始化 AWS Bedrock MCP 环境...")
            
            # 创建集成管理器
            integration_config = IntegrationConfig(**self.config.get("integration", {}))
            manager = IntegrationManager(integration_config)
            
            # 初始化
            result = await manager.initialize()
            
            if result["status"] == "success":
                self.logger.info("✅ 环境初始化成功")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0
            else:
                self.logger.error(f"❌ 环境初始化失败: {result.get('error')}")
                return 1
                
        except Exception as e:
            self.logger.error(f"初始化失败: {str(e)}")
            return 1
    
    async def cmd_add_docs(self, args):
        """添加文档到知识库"""
        try:
            self.logger.info(f"添加文档: {args.directory} -> 知识库: {args.kb_name or '默认'}")
            
            # 检查目录是否存在
            if not os.path.exists(args.directory):
                self.logger.error(f"目录不存在: {args.directory}")
                return 1
            
            # 创建集成管理器
            integration_config = IntegrationConfig(**self.config.get("integration", {}))
            manager = IntegrationManager(integration_config)
            
            # 初始化
            init_result = await manager.initialize()
            if init_result["status"] != "success":
                self.logger.error(f"初始化失败: {init_result.get('error')}")
                return 1
            
            # 添加文档
            result = await manager.add_documents_from_directory(
                directory_path=args.directory,
                kb_name=args.kb_name
            )
            
            if result["status"] == "success":
                self.logger.info("✅ 文档添加成功")
                print(f"处理文件: {result['successful_files']}")
                print(f"失败文件: {len(result['failed_files'])}")
                print(f"总分块数: {result['total_chunks']}")
                print(f"处理时间: {result['processing_time_seconds']:.2f}秒")
                return 0
            else:
                self.logger.error(f"❌ 文档添加失败: {result.get('error')}")
                return 1
                
        except Exception as e:
            self.logger.error(f"文档添加失败: {str(e)}")
            return 1
    
    async def cmd_query(self, args):
        """执行智能查询"""
        try:
            self.logger.info(f"执行查询: {args.query[:50]}...")
            
            # 创建集成管理器
            integration_config = IntegrationConfig(**self.config.get("integration", {}))
            manager = IntegrationManager(integration_config)
            
            # 初始化
            init_result = await manager.initialize()
            if init_result["status"] != "success":
                self.logger.error(f"初始化失败: {init_result.get('error')}")
                return 1
            
            # 执行查询
            result = await manager.query(
                query=args.query,
                kb_id=args.kb_id,
                top_k=args.top_k
            )
            
            if result.status == "success":
                self.logger.info("✅ 查询成功")
                print("\n" + "="*60)
                print("📝 查询结果:")
                print("="*60)
                print(result.answer)
                print("\n" + "="*60)
                print(f"⏱️  响应时间: {result.processing_time_ms:.2f}ms")
                print(f"🎯 质量评分: {result.cost_info}")
                print(f"📚 数据源: {len(result.sources)} 个")
                return 0
            else:
                self.logger.error(f"❌ 查询失败: {result.answer}")
                return 1
                
        except Exception as e:
            self.logger.error(f"查询失败: {str(e)}")
            return 1
    
    async def cmd_status(self, args):
        """获取系统状态"""
        try:
            self.logger.info("获取系统状态...")
            
            # 创建集成管理器
            integration_config = IntegrationConfig(**self.config.get("integration", {}))
            manager = IntegrationManager(integration_config)
            
            # 初始化
            init_result = await manager.initialize()
            if init_result["status"] != "success":
                self.logger.error(f"初始化失败: {init_result.get('error')}")
                return 1
            
            # 获取状态
            health = await manager.get_health_status()
            system_info = await manager.get_system_info()
            
            print("\n" + "="*60)
            print("🏥 系统健康状态")
            print("="*60)
            print(f"总体状态: {health['status']}")
            print(f"运行时间: {health.get('uptime_seconds', 0):.0f} 秒")
            
            if 'components' in health:
                print("\n组件状态:")
                for component, status in health['components'].items():
                    status_icon = "✅" if status == "healthy" else "❌"
                    print(f"  {status_icon} {component}: {status}")
            
            if 'stats' in health:
                stats = health['stats']
                print(f"\n📊 统计信息:")
                print(f"  总查询数: {stats.get('total_queries', 0)}")
                print(f"  处理文档: {stats.get('total_documents_processed', 0)}")
                print(f"  知识库数: {stats.get('total_knowledge_bases', 0)}")
                print(f"  平均响应: {stats.get('avg_response_time', 0):.2f}ms")
            
            print("\n" + "="*60)
            print("ℹ️  系统信息")
            print("="*60)
            print(f"版本: {system_info.get('version', 'unknown')}")
            print(f"架构: {system_info.get('architecture', 'unknown')}")
            
            if args.verbose and 'runtime_info' in system_info:
                runtime = system_info['runtime_info']
                print(f"\n运行时信息:")
                print(f"  知识库: {runtime.get('knowledge_bases', 0)}")
                print(f"  文档总数: {runtime.get('total_documents', 0)}")
                print(f"  向量索引: {runtime.get('vector_index_size', 0)}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"状态获取失败: {str(e)}")
            return 1
    
    async def cmd_test(self, args):
        """测试系统功能"""
        try:
            self.logger.info("开始系统功能测试...")
            
            # 测试 K2 路由器
            print("🧪 测试 Kimi K2 路由器...")
            k2_config = self.config.get("k2_router", {})
            k2_router = K2Router(k2_config)
            
            k2_result = await k2_router.initialize()
            if k2_result["status"] == "success":
                print("  ✅ K2 路由器初始化成功")
            else:
                print(f"  ❌ K2 路由器初始化失败: {k2_result.get('error')}")
            
            # 测试集成管理器
            print("\n🧪 测试集成管理器...")
            integration_config = IntegrationConfig(**self.config.get("integration", {}))
            manager = IntegrationManager(integration_config)
            
            manager_result = await manager.initialize()
            if manager_result["status"] == "success":
                print("  ✅ 集成管理器初始化成功")
                
                # 测试简单查询
                if args.test_query:
                    print("\n🧪 测试查询功能...")
                    test_result = await manager.query("测试查询")
                    if test_result.status == "success":
                        print("  ✅ 查询功能正常")
                    else:
                        print(f"  ❌ 查询功能异常: {test_result.answer}")
            else:
                print(f"  ❌ 集成管理器初始化失败: {manager_result.get('error')}")
            
            # 清理资源
            await k2_router.cleanup()
            
            print("\n🎉 测试完成")
            return 0
            
        except Exception as e:
            self.logger.error(f"测试失败: {str(e)}")
            return 1
    
    def cmd_config(self, args):
        """配置管理"""
        try:
            if args.action == "show":
                print("📋 当前配置:")
                print(json.dumps(self.config, ensure_ascii=False, indent=2))
            
            elif args.action == "generate":
                config_path = args.output or "bedrock_mcp_config.json"
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                print(f"✅ 配置文件已生成: {config_path}")
            
            elif args.action == "validate":
                # 验证配置
                required_keys = ["integration", "k2_router", "routing"]
                missing_keys = [key for key in required_keys if key not in self.config]
                
                if missing_keys:
                    print(f"❌ 配置验证失败，缺少: {missing_keys}")
                    return 1
                else:
                    print("✅ 配置验证通过")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"配置操作失败: {str(e)}")
            return 1

def create_parser():
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        description="PowerAutomation AWS Bedrock MCP CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 启动 MCP 服务器
  python -m aws_bedrock_mcp.cli server
  
  # 初始化环境
  python -m aws_bedrock_mcp.cli init
  
  # 添加文档到知识库
  python -m aws_bedrock_mcp.cli add-docs /path/to/docs --kb-name "项目文档"
  
  # 执行查询
  python -m aws_bedrock_mcp.cli query "如何使用这个API？"
  
  # 查看系统状态
  python -m aws_bedrock_mcp.cli status --verbose
  
  # 测试系统功能
  python -m aws_bedrock_mcp.cli test --test-query
        """
    )
    
    # 全局参数
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--log-level", type=str, default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别")
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # server 命令
    server_parser = subparsers.add_parser("server", help="启动智能路由 MCP 服务器")
    server_parser.add_argument("--transport", type=str, default="stdio", 
                              choices=["stdio"], help="传输类型")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化环境")
    
    # add-docs 命令
    add_docs_parser = subparsers.add_parser("add-docs", help="添加文档到知识库")
    add_docs_parser.add_argument("directory", type=str, help="文档目录路径")
    add_docs_parser.add_argument("--kb-name", type=str, help="知识库名称")
    
    # query 命令
    query_parser = subparsers.add_parser("query", help="执行智能查询")
    query_parser.add_argument("query", type=str, help="查询内容")
    query_parser.add_argument("--kb-id", type=str, help="知识库 ID")
    query_parser.add_argument("--top-k", type=int, default=5, help="返回结果数量")
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="获取系统状态")
    status_parser.add_argument("--verbose", action="store_true", help="显示详细信息")
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="测试系统功能")
    test_parser.add_argument("--test-query", action="store_true", help="测试查询功能")
    
    # config 命令
    config_parser = subparsers.add_parser("config", help="配置管理")
    config_parser.add_argument("action", choices=["show", "generate", "validate"], 
                              help="配置操作")
    config_parser.add_argument("--output", type=str, help="输出文件路径（用于 generate）")
    
    return parser

async def main():
    """主入口函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 创建 CLI 实例
    cli = BedrockMCPCLI()
    cli.setup_logging(args.log_level)
    cli.load_config(args.config)
    
    # 执行命令
    try:
        if args.command == "server":
            return await cli.cmd_server(args)
        elif args.command == "init":
            return await cli.cmd_init(args)
        elif args.command == "add-docs":
            return await cli.cmd_add_docs(args)
        elif args.command == "query":
            return await cli.cmd_query(args)
        elif args.command == "status":
            return await cli.cmd_status(args)
        elif args.command == "test":
            return await cli.cmd_test(args)
        elif args.command == "config":
            return cli.cmd_config(args)
        else:
            print(f"未知命令: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 1
    except Exception as e:
        print(f"执行失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

