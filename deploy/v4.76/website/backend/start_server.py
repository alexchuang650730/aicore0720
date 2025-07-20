#!/usr/bin/env python3
"""
PowerAuto.ai 服務器啟動腳本
包含支付系統的完整後端服務
"""

import os
import sys
import logging
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('powerauto_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """檢查依賴項"""
    logger.info("檢查系統依賴項...")
    
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_bcrypt', 'flask_cors',
        'stripe', 'jwt', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"缺少依賴包: {missing_packages}")
        logger.info("請運行: pip install " + " ".join(missing_packages))
        return False
    
    logger.info("✅ 所有依賴項已安裝")
    return True

def check_business_mcp():
    """檢查Business MCP系統"""
    logger.info("檢查Business MCP系統...")
    
    try:
        sys.path.append('/Users/alexchuang/alexchuangtest/aicore0720')
        from core.components.business_mcp.business_manager import business_manager
        logger.info("✅ Business MCP系統可用")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Business MCP系統不可用: {e}")
        return False

def check_payment_system():
    """檢查支付系統"""
    logger.info("檢查支付系統...")
    
    try:
        from payment_system import payment_system
        logger.info("✅ 支付系統可用")
        
        # 測試支付系統基本功能
        plans = payment_system.get_pricing_plans()
        logger.info(f"✅ 載入了 {len(plans)} 個定價方案")
        
        methods = payment_system.get_payment_methods()
        logger.info(f"✅ 載入了 {len(methods)} 種支付方式")
        
        return True
    except Exception as e:
        logger.error(f"❌ 支付系統不可用: {e}")
        return False

def initialize_database():
    """初始化數據庫"""
    logger.info("初始化數據庫...")
    
    try:
        from app import app, db, create_tables
        
        with app.app_context():
            create_tables()
            logger.info("✅ 數據庫初始化完成")
        
        return True
    except Exception as e:
        logger.error(f"❌ 數據庫初始化失敗: {e}")
        return False

def start_server():
    """啟動服務器"""
    logger.info("🚀 啟動PowerAuto.ai服務器...")
    
    # 系統檢查
    if not check_dependencies():
        return False
    
    business_mcp_ok = check_business_mcp()
    payment_system_ok = check_payment_system()
    
    if not payment_system_ok:
        logger.error("❌ 支付系統檢查失敗，無法啟動服務器")
        return False
    
    if not initialize_database():
        return False
    
    # 顯示啟動信息
    logger.info("=" * 60)
    logger.info("🎉 PowerAuto.ai 服務器啟動成功！")
    logger.info("=" * 60)
    logger.info("📋 系統狀態:")
    logger.info(f"   - Business MCP: {'✅ 可用' if business_mcp_ok else '⚠️  不可用'}")
    logger.info(f"   - 支付系統: {'✅ 可用' if payment_system_ok else '❌ 不可用'}")
    logger.info(f"   - 數據庫: ✅ 已初始化")
    logger.info("")
    logger.info("🌐 可用頁面:")
    logger.info("   - 產品展示: http://localhost:5001/products")
    logger.info("   - 結帳頁面: http://localhost:5001/checkout")
    logger.info("   - 支付成功: http://localhost:5001/success")
    logger.info("   - API文檔: http://localhost:5001/api/plans")
    logger.info("")
    logger.info("💡 測試命令:")
    logger.info("   python test_payment_system.py")
    logger.info("=" * 60)
    
    # 啟動Flask應用
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        logger.error(f"❌ 服務器啟動失敗: {e}")
        return False

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        logger.info("\n⏹️  服務器已停止")
    except Exception as e:
        logger.error(f"❌ 意外錯誤: {e}")
        sys.exit(1)