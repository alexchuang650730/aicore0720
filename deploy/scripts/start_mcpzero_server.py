#!/usr/bin/env python3
"""
啟動 MCP-Zero 服務器
"""

import sys
import os
import argparse
import logging

# 確保項目根目錄在 Python 路徑中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.api.main_api_server import run_server

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='PowerAutomation MCP-Zero Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服務器主機地址')
    parser.add_argument('--port', type=int, default=8000, help='服務器端口')
    parser.add_argument('--reload', action='store_true', help='開啟自動重載（開發模式）')
    
    args = parser.parse_args()
    
    logger.info(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║         PowerAutomation MCP-Zero Server v4.73                ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🚀 MCP-Zero 動態加載架構                                    ║
    ║  💰 成本節省 80%，性能提升 5 倍                              ║
    ║  🔧 六大工作流自動化                                         ║
    ║  🤖 K2 模型智能路由                                          ║
    ╚══════════════════════════════════════════════════════════════╝
    
    服務器啟動中...
    地址: http://{args.host}:{args.port}
    API 文檔: http://{args.host}:{args.port}/docs
    """)
    
    try:
        run_server(
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except KeyboardInterrupt:
        logger.info("\n服務器已停止")
    except Exception as e:
        logger.error(f"服務器錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()