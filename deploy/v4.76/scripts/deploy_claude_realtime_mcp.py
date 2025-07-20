#!/usr/bin/env python3
"""
一鍵部署Claude實時收集器MCP - 第21個MCP組件
解決K2和DeepSWE訓練數據不足問題的關鍵工具
"""

import asyncio
import logging
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加項目路徑
sys.path.append(str(Path(__file__).parent))

from core.components.claude_realtime_mcp.claude_realtime_manager import ClaudeRealtimeMCPManager
from core.mcp_zero.mcp_registry import mcp_registry

class ClaudeRealtimeMCPDeployer:
    """Claude實時收集器MCP部署器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mcp_manager = None
        self.deployment_success = False
        
    async def deploy(self):
        """一鍵部署Claude實時收集器MCP"""
        print("🚀 Claude實時收集器MCP - 第21個MCP組件部署器")
        print("=" * 60)
        print("🎯 目標：解決K2和DeepSWE訓練數據不足問題")
        print("📊 當前K2訓練數據：僅48行（嚴重不足！）")
        print("🔧 DeepSWE訓練數據：幾乎為空")
        print("💡 解決方案：實時收集Claude對話，自動生成高質量訓練數據")
        print("=" * 60)
        
        try:
            # 1. 配置日誌
            await self._setup_logging()
            
            # 2. 檢查環境依賴
            await self._check_dependencies()
            
            # 3. 初始化MCP管理器
            await self._initialize_mcp_manager()
            
            # 4. 註冊到MCP註冊中心
            await self._register_to_mcp_registry()
            
            # 5. 啟動實時收集
            await self._start_realtime_collection()
            
            # 6. 顯示部署狀態
            await self._show_deployment_status()
            
            # 7. 開始監控循環
            await self._start_monitoring_loop()
            
        except KeyboardInterrupt:
            print("\n🛑 用戶中斷，正在停止收集器...")
        except Exception as e:
            print(f"❌ 部署失敗: {e}")
            self.logger.error(f"部署失敗: {e}")
        finally:
            await self._cleanup()
    
    async def _setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('claude_realtime_mcp.log'),
                logging.StreamHandler()
            ]
        )
        print("✅ 日誌系統已配置")
    
    async def _check_dependencies(self):
        """檢查環境依賴"""
        print("🔍 檢查環境依賴...")
        
        try:
            import psutil
            print("  ✅ psutil - 進程監控")
        except ImportError:
            print("  ⚠️  psutil 未安裝，將使用回退方案")
        
        try:
            import websockets
            print("  ✅ websockets - 實時通信")
        except ImportError:
            print("  ⚠️  websockets 未安裝，WebSocket服務器將被禁用")
        
        # 檢查數據目錄
        data_dir = Path("./data/claude_realtime_mcp")
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ 數據目錄: {data_dir}")
        
        print("✅ 環境檢查完成")
    
    async def _initialize_mcp_manager(self):
        """初始化MCP管理器"""
        print("⚙️  初始化Claude實時收集器MCP管理器...")
        
        self.mcp_manager = ClaudeRealtimeMCPManager()
        success = await self.mcp_manager.initialize()
        
        if success:
            print("✅ MCP管理器初始化成功")
            self.deployment_success = True
        else:
            raise Exception("MCP管理器初始化失敗")
    
    async def _register_to_mcp_registry(self):
        """註冊到MCP註冊中心"""
        print("📝 註冊到MCP註冊中心...")
        
        try:
            # 加載到註冊中心
            mcp_instance = await mcp_registry.load_mcp("claude_realtime_mcp")
            
            if mcp_instance:
                print("✅ 成功註冊為第21個MCP組件")
                
                # 顯示MCP元數據
                metadata = await mcp_registry.get_mcp_metadata("claude_realtime_mcp")
                if metadata:
                    print(f"  📊 優先級: {metadata.priority}")
                    print(f"  🎯 性能評分: {metadata.performance_score}")
                    print(f"  📈 成功率: {metadata.success_rate}")
                    print(f"  🧠 上下文大小: {metadata.context_size}")
            else:
                print("⚠️  MCP註冊失敗，但將繼續以獨立模式運行")
                
        except Exception as e:
            print(f"⚠️  MCP註冊出錯: {e}")
            print("將以獨立模式運行")
    
    async def _start_realtime_collection(self):
        """啟動實時收集"""
        print("🎯 啟動Claude實時數據收集...")
        
        await self.mcp_manager.start_collection()
        print("✅ 實時收集已啟動")
        print("🔍 正在監控以下Claude進程:")
        
        for cmd in self.mcp_manager.monitored_commands:
            print(f"  - {cmd}")
    
    async def _show_deployment_status(self):
        """顯示部署狀態"""
        print("\n" + "=" * 60)
        print("🎉 Claude實時收集器MCP部署成功！")
        print("=" * 60)
        
        # 獲取訓練摘要
        summary = await self.mcp_manager.get_training_summary()
        
        print("📊 當前狀態:")
        print(f"  活躍會話: {summary['active_sessions']}")
        print(f"  已完成會話: {summary['completed_sessions']}")
        print(f"  收集狀態: {'運行中' if summary['collection_running'] else '已停止'}")
        print(f"  監控進程數: {summary['monitored_processes']}")
        
        print("\n📈 訓練數據統計:")
        stats = summary['training_stats']
        print(f"  K2訓練樣本: {stats['total_k2_examples']}")
        print(f"  DeepSWE訓練樣本: {stats['total_deepswe_examples']}")
        print(f"  通用訓練樣本: {stats['total_general_examples']}")
        print(f"  數據質量分數: {stats['data_quality_score']:.2f}")
        
        print(f"\n💾 數據存儲位置: {summary['data_directory']}")
        
        print("\n🔄 自動功能:")
        print("  ✅ 實時監控Claude會話")
        print("  ✅ 自動分類訓練數據 (K2/DeepSWE/通用)")
        print("  ✅ 質量評估和過濾")
        print("  ✅ 自動生成JSONL訓練文件")
        print("  ✅ 會話統計和分析")
        
        print("\n⚡ 預期效果:")
        print("  📈 每小時收集10-50個高質量訓練樣本")
        print("  🎯 30天內積累1000+ K2訓練樣本")
        print("  🔧 30天內積累500+ DeepSWE訓練樣本")
        print("  🚀 訓練數據從48行提升到10000+行！")
    
    async def _start_monitoring_loop(self):
        """開始監控循環"""
        print("\n🔄 進入監控模式...")
        print("按 Ctrl+C 停止收集器")
        print("-" * 40)
        
        try:
            while True:
                # 每30秒顯示一次狀態更新
                await asyncio.sleep(30)
                
                summary = await self.mcp_manager.get_training_summary()
                stats = summary['training_stats']
                
                print(f"\r⏰ {datetime.now().strftime('%H:%M:%S')} | "
                      f"會話: {summary['active_sessions']} | "
                      f"K2: {stats['total_k2_examples']} | "
                      f"DeepSWE: {stats['total_deepswe_examples']} | "
                      f"質量: {stats['data_quality_score']:.2f}", end="")
                
        except KeyboardInterrupt:
            raise
    
    async def _cleanup(self):
        """清理資源"""
        print("\n🧹 正在清理資源...")
        
        if self.mcp_manager:
            try:
                await self.mcp_manager.shutdown()
                print("✅ MCP管理器已關閉")
            except Exception as e:
                print(f"⚠️  MCP管理器關閉時出錯: {e}")
        
        if self.deployment_success:
            print("\n📊 最終統計:")
            try:
                summary = await self.mcp_manager.get_training_summary()
                stats = summary['training_stats']
                
                print(f"  總K2樣本: {stats['total_k2_examples']}")
                print(f"  總DeepSWE樣本: {stats['total_deepswe_examples']}")
                print(f"  總會話數: {stats['sessions_completed']}")
                print(f"  數據質量: {stats['data_quality_score']:.2f}")
                
                # 嘗試匯出最終數據
                if stats['total_k2_examples'] > 0 or stats['total_deepswe_examples'] > 0:
                    export_file = await self.mcp_manager.export_training_data("combined")
                    print(f"  📁 訓練數據已匯出: {export_file}")
                
            except Exception as e:
                print(f"⚠️  獲取最終統計時出錯: {e}")
        
        print("✅ 清理完成")

async def main():
    """主函數"""
    deployer = ClaudeRealtimeMCPDeployer()
    await deployer.deploy()

if __name__ == "__main__":
    asyncio.run(main())