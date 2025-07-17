#!/usr/bin/env python3
"""
PowerAutomation Monitoring MCP CLI
监控 MCP 命令行接口
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from core.components.monitoring_mcp.monitoring_manager import monitoring_manager

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PowerAutomation Monitoring MCP CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s status                    # 获取监控状态
  %(prog)s start                     # 启动监控服务
  %(prog)s stop                      # 停止监控服务
  %(prog)s milestone                 # 获取里程碑进度
  %(prog)s health                    # 获取系统健康状态
  %(prog)s report --type full        # 生成完整报告
  %(prog)s report --type milestone   # 生成里程碑报告
  %(prog)s report --type health      # 生成健康报告
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 状态命令
    status_parser = subparsers.add_parser('status', help='获取监控状态')
    
    # 启动命令
    start_parser = subparsers.add_parser('start', help='启动监控服务')
    
    # 停止命令
    stop_parser = subparsers.add_parser('stop', help='停止监控服务')
    
    # 里程碑命令
    milestone_parser = subparsers.add_parser('milestone', help='获取里程碑进度')
    
    # 健康状态命令
    health_parser = subparsers.add_parser('health', help='获取系统健康状态')
    
    # 报告命令
    report_parser = subparsers.add_parser('report', help='生成监控报告')
    report_parser.add_argument(
        '--type', 
        choices=['full', 'milestone', 'health'],
        default='full',
        help='报告类型 (默认: full)'
    )
    report_parser.add_argument(
        '--output', '-o',
        help='输出文件路径 (可选)'
    )
    
    # 工具列表命令
    tools_parser = subparsers.add_parser('tools', help='列出可用工具')
    
    # 配置命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    config_show_parser = config_subparsers.add_parser('show', help='显示当前配置')
    config_update_parser = config_subparsers.add_parser('update', help='更新配置')
    config_update_parser.add_argument('--file', help='配置文件路径')
    config_update_parser.add_argument('--json', help='JSON 格式配置')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # 执行命令
        result = None
        
        if args.command == 'status':
            result = await monitoring_manager.get_monitoring_status()
            
        elif args.command == 'start':
            result = await monitoring_manager.start_monitoring()
            
        elif args.command == 'stop':
            result = await monitoring_manager.stop_monitoring()
            
        elif args.command == 'milestone':
            result = await monitoring_manager.get_milestone_progress()
            
        elif args.command == 'health':
            result = await monitoring_manager.get_system_health()
            
        elif args.command == 'report':
            result = await monitoring_manager.generate_report(args.type)
            
            # 如果指定了输出文件，保存报告
            if args.output and result.get('status') == 'success':
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result['report'], f, indent=2, ensure_ascii=False)
                
                print(f"报告已保存到: {output_path}")
                return
                
        elif args.command == 'tools':
            result = await monitoring_manager.list_tools()
            
        elif args.command == 'config':
            if args.config_action == 'show':
                result = await monitoring_manager.get_monitoring_status()
                result = result.get('config', {})
                
            elif args.config_action == 'update':
                config_data = {}
                
                if args.file:
                    config_path = Path(args.file)
                    if config_path.exists():
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                    else:
                        print(f"错误: 配置文件不存在: {config_path}")
                        return
                        
                elif args.json:
                    config_data = json.loads(args.json)
                    
                else:
                    print("错误: 请指定 --file 或 --json 参数")
                    return
                
                result = await monitoring_manager.update_config(config_data)
            else:
                print("错误: 请指定配置操作 (show/update)")
                return
        
        # 输出结果
        if result is not None:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

def run_cli():
    """CLI 入口点"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"CLI 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()

