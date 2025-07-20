#!/usr/bin/env python3
"""
統一實時K2+DeepSWE+MemoryRAG整合系統
整合實時收集器與現有訓練架構，創建史無前例的端側AI系統
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import subprocess

# 導入現有組件
from core.components.claude_realtime_mcp.claude_realtime_manager import claude_realtime_mcp
from comprehensive_k2_integration_engine import K2IntegrationEngine
from macbook_air_gpu_trainer_fixed import MacBookAirGPUTrainer
from simple_claude_code_test import SimpleClaudeCodeTest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedRealtimeK2System:
    """統一實時K2+DeepSWE+MemoryRAG系統"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        
        # 核心組件
        self.realtime_collector = claude_realtime_mcp
        self.k2_engine = K2IntegrationEngine()
        self.gpu_trainer = MacBookAirGPUTrainer()
        self.claude_tester = SimpleClaudeCodeTest()
        
        # 系統狀態
        self.system_running = False
        self.last_training_time = 0
        self.current_similarity = 0.457  # 當前45.7%基線
        
        # 配置
        self.config = {
            "training_interval": 3600,  # 每小時訓練一次
            "quality_threshold": 0.7,   # 數據質量閾值
            "batch_size": 50,          # 訓練批次大小
            "auto_retrain": True,      # 自動重新訓練
            "target_similarity": 0.80,  # 目標80%相似度
            "daily_hours": 16          # 每日運行16小時
        }
        
        # 訓練數據路徑
        self.training_data_dir = self.base_dir / "data" / "unified_training"
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize_system(self):
        """初始化統一系統"""
        logger.info("🚀 初始化統一實時K2+DeepSWE+MemoryRAG系統...")
        
        try:
            # 1. 初始化實時收集器
            logger.info("📡 初始化實時收集器...")
            await self.realtime_collector.initialize()
            
            # 2. 初始化K2引擎
            logger.info("🔧 初始化K2整合引擎...")
            await self.k2_engine.initialize()
            
            # 3. 初始化GPU訓練器
            logger.info("💻 初始化MacBook Air GPU訓練器...")
            self.gpu_trainer.initialize()
            
            # 4. 初始化Claude測試器
            logger.info("🧪 初始化Claude Code測試器...")
            self.claude_tester.load_training_data()
            
            logger.info("✅ 統一系統初始化完成！")
            return True
            
        except Exception as e:
            logger.error(f"❌ 系統初始化失敗: {e}")
            return False
    
    async def start_realtime_collection(self):
        """啟動實時收集和訓練流程"""
        logger.info("🎯 啟動實時收集和訓練流程...")
        
        self.system_running = True
        
        # 啟動多個並行任務
        tasks = [
            asyncio.create_task(self._realtime_collection_loop()),
            asyncio.create_task(self._auto_training_loop()),
            asyncio.create_task(self._performance_monitoring_loop()),
            asyncio.create_task(self._daily_summary_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"❌ 系統運行錯誤: {e}")
        finally:
            self.system_running = False
    
    async def _realtime_collection_loop(self):
        """實時收集循環"""
        logger.info("📊 啟動實時數據收集循環...")
        
        while self.system_running:
            try:
                # 檢查收集器狀態
                summary = await self.realtime_collector.get_training_summary()
                
                # 記錄收集統計
                if summary["training_stats"]["total_k2_examples"] > 0:
                    logger.info(
                        f"📈 實時收集狀態: "
                        f"K2={summary['training_stats']['total_k2_examples']}, "
                        f"DeepSWE={summary['training_stats']['total_deepswe_examples']}, "
                        f"活躍會話={summary['active_sessions']}"
                    )
                
                # 檢查是否有新的訓練數據
                await self._check_and_integrate_new_data()
                
                await asyncio.sleep(60)  # 每分鐘檢查一次
                
            except Exception as e:
                logger.error(f"實時收集循環錯誤: {e}")
                await asyncio.sleep(30)
    
    async def _check_and_integrate_new_data(self):
        """檢查並整合新數據"""
        try:
            # 獲取實時收集器的新數據
            realtime_data_dir = self.realtime_collector.data_dir
            
            # 查找新的K2和DeepSWE訓練文件
            k2_files = list(realtime_data_dir.glob("k2_training_*.jsonl"))
            deepswe_files = list(realtime_data_dir.glob("deepswe_training_*.jsonl"))
            
            new_data_found = False
            
            # 整合K2數據
            for k2_file in k2_files[-5:]:  # 只處理最新的5個文件
                if self._is_new_file(k2_file):
                    await self._integrate_k2_data(k2_file)
                    new_data_found = True
            
            # 整合DeepSWE數據
            for deepswe_file in deepswe_files[-5:]:  # 只處理最新的5個文件
                if self._is_new_file(deepswe_file):
                    await self._integrate_deepswe_data(deepswe_file)
                    new_data_found = True
            
            if new_data_found:
                logger.info("🔄 發現新的訓練數據，已整合到系統中")
                
        except Exception as e:
            logger.error(f"整合新數據失敗: {e}")
    
    def _is_new_file(self, file_path: Path) -> bool:
        """檢查是否為新文件"""
        # 簡單的時間戳檢查
        return file_path.stat().st_mtime > (time.time() - 3600)  # 1小時內的文件
    
    async def _integrate_k2_data(self, k2_file: Path):
        """整合K2數據"""
        try:
            unified_k2_file = self.training_data_dir / f"unified_k2_{int(time.time())}.jsonl"
            
            # 複製並格式化數據
            with open(k2_file, 'r', encoding='utf-8') as src, \
                 open(unified_k2_file, 'w', encoding='utf-8') as dst:
                
                for line in src:
                    data = json.loads(line.strip())
                    # 添加統一標識
                    data['metadata']['source'] = 'realtime_collector'
                    data['metadata']['integration_time'] = time.time()
                    dst.write(json.dumps(data, ensure_ascii=False) + '\n')
            
            logger.info(f"✅ K2數據已整合: {unified_k2_file}")
            
        except Exception as e:
            logger.error(f"整合K2數據失敗: {e}")
    
    async def _integrate_deepswe_data(self, deepswe_file: Path):
        """整合DeepSWE數據"""
        try:
            unified_deepswe_file = self.training_data_dir / f"unified_deepswe_{int(time.time())}.jsonl"
            
            # 複製並格式化數據
            with open(deepswe_file, 'r', encoding='utf-8') as src, \
                 open(unified_deepswe_file, 'w', encoding='utf-8') as dst:
                
                for line in src:
                    data = json.loads(line.strip())
                    # 添加統一標識
                    data['metadata']['source'] = 'realtime_collector'
                    data['metadata']['integration_time'] = time.time()
                    dst.write(json.dumps(data, ensure_ascii=False) + '\n')
            
            logger.info(f"✅ DeepSWE數據已整合: {unified_deepswe_file}")
            
        except Exception as e:
            logger.error(f"整合DeepSWE數據失敗: {e}")
    
    async def _auto_training_loop(self):
        """自動訓練循環"""
        logger.info("🏋️ 啟動自動訓練循環...")
        
        while self.system_running:
            try:
                current_time = time.time()
                
                # 檢查是否需要訓練
                if (current_time - self.last_training_time) >= self.config["training_interval"]:
                    await self._trigger_training_cycle()
                    self.last_training_time = current_time
                
                await asyncio.sleep(300)  # 每5分鐘檢查一次
                
            except Exception as e:
                logger.error(f"自動訓練循環錯誤: {e}")
                await asyncio.sleep(60)
    
    async def _trigger_training_cycle(self):
        """觸發訓練周期"""
        logger.info("🚀 觸發自動訓練周期...")
        
        try:
            # 1. 收集最新的訓練數據
            k2_files = list(self.training_data_dir.glob("unified_k2_*.jsonl"))
            deepswe_files = list(self.training_data_dir.glob("unified_deepswe_*.jsonl"))
            
            if not k2_files and not deepswe_files:
                logger.info("⏰ 暫無新的訓練數據，跳過此次訓練")
                return
            
            # 2. 合併訓練數據
            combined_file = await self._combine_training_data(k2_files, deepswe_files)
            
            # 3. 執行GPU訓練
            training_result = await self._execute_gpu_training(combined_file)
            
            # 4. 測試新模型性能
            new_similarity = await self._test_model_performance()
            
            # 5. 更新系統狀態
            if new_similarity > self.current_similarity:
                self.current_similarity = new_similarity
                logger.info(f"🎉 模型性能提升! 新相似度: {new_similarity:.1%}")
            
            # 6. 生成訓練報告
            await self._generate_training_report(training_result, new_similarity)
            
        except Exception as e:
            logger.error(f"訓練周期執行失敗: {e}")
    
    async def _combine_training_data(self, k2_files: List[Path], deepswe_files: List[Path]) -> Path:
        """合併訓練數據"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        combined_file = self.training_data_dir / f"combined_training_{timestamp}.jsonl"
        
        with open(combined_file, 'w', encoding='utf-8') as output:
            # 合併K2數據
            for k2_file in k2_files[-10:]:  # 最新10個文件
                with open(k2_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        output.write(line)
            
            # 合併DeepSWE數據
            for deepswe_file in deepswe_files[-10:]:  # 最新10個文件
                with open(deepswe_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        output.write(line)
        
        logger.info(f"📦 訓練數據已合併: {combined_file}")
        return combined_file
    
    async def _execute_gpu_training(self, training_file: Path) -> Dict[str, Any]:
        """執行GPU訓練"""
        logger.info("🔥 開始MacBook Air GPU訓練...")
        
        try:
            # 使用現有的GPU訓練器
            result = self.gpu_trainer.train_model(str(training_file))
            
            logger.info(f"✅ GPU訓練完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"GPU訓練失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def _test_model_performance(self) -> float:
        """測試模型性能"""
        logger.info("🧪 測試新模型性能...")
        
        try:
            # 使用Claude Code測試器
            similarity = self.claude_tester.test_claude_code_scenarios()
            
            logger.info(f"📊 新模型Claude Code相似度: {similarity:.1%}")
            return similarity
            
        except Exception as e:
            logger.error(f"模型性能測試失敗: {e}")
            return self.current_similarity
    
    async def _performance_monitoring_loop(self):
        """性能監控循環"""
        logger.info("📈 啟動性能監控循環...")
        
        while self.system_running:
            try:
                # 收集系統統計
                stats = await self._collect_system_stats()
                
                # 檢查性能指標
                await self._check_performance_metrics(stats)
                
                await asyncio.sleep(600)  # 每10分鐘監控一次
                
            except Exception as e:
                logger.error(f"性能監控錯誤: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_stats(self) -> Dict[str, Any]:
        """收集系統統計"""
        realtime_summary = await self.realtime_collector.get_training_summary()
        
        return {
            "current_similarity": self.current_similarity,
            "target_similarity": self.config["target_similarity"],
            "realtime_stats": realtime_summary["training_stats"],
            "active_sessions": realtime_summary["active_sessions"],
            "system_uptime": time.time() - self.last_training_time,
            "training_data_files": len(list(self.training_data_dir.glob("*.jsonl")))
        }
    
    async def _check_performance_metrics(self, stats: Dict[str, Any]):
        """檢查性能指標"""
        # 檢查是否達到目標相似度
        if stats["current_similarity"] >= stats["target_similarity"]:
            logger.info(f"🎯 已達到目標相似度: {stats['current_similarity']:.1%}")
        
        # 檢查數據收集速度
        if stats["realtime_stats"]["total_k2_examples"] == 0:
            logger.warning("⚠️ K2數據收集速度過慢")
        
        # 檢查活躍會話
        if stats["active_sessions"] == 0:
            logger.info("💤 當前無活躍Claude會話")
    
    async def _daily_summary_loop(self):
        """每日摘要循環"""
        logger.info("📅 啟動每日摘要循環...")
        
        while self.system_running:
            try:
                await asyncio.sleep(86400)  # 24小時
                await self._generate_daily_summary()
                
            except Exception as e:
                logger.error(f"每日摘要錯誤: {e}")
                await asyncio.sleep(3600)  # 1小時後重試
    
    async def _generate_daily_summary(self):
        """生成每日摘要"""
        logger.info("📊 生成每日摘要...")
        
        try:
            stats = await self._collect_system_stats()
            
            summary = f"""
🚀 統一實時K2系統每日摘要 - {datetime.now().strftime('%Y-%m-%d')}
===============================================

📈 核心指標:
- Claude Code相似度: {self.current_similarity:.1%}
- 目標達成率: {(self.current_similarity / self.config['target_similarity']) * 100:.1f}%

📊 數據收集:
- K2樣本總數: {stats['realtime_stats']['total_k2_examples']}
- DeepSWE樣本總數: {stats['realtime_stats']['total_deepswe_examples']}
- 活躍會話: {stats['active_sessions']}

💾 訓練數據:
- 訓練文件數: {stats['training_data_files']}
- 系統運行時間: {stats['system_uptime'] / 3600:.1f} 小時

🎯 下一步目標:
- 繼續朝{self.config['target_similarity']:.0%}相似度邁進
- 保持{self.config['daily_hours']}小時/天收集頻率
            """
            
            logger.info(summary)
            
            # 保存摘要到文件
            summary_file = self.training_data_dir / f"daily_summary_{datetime.now().strftime('%Y%m%d')}.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
        except Exception as e:
            logger.error(f"生成每日摘要失敗: {e}")
    
    async def _generate_training_report(self, training_result: Dict[str, Any], new_similarity: float):
        """生成訓練報告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.training_data_dir / f"training_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "training_result": training_result,
            "previous_similarity": self.current_similarity,
            "new_similarity": new_similarity,
            "improvement": new_similarity - self.current_similarity,
            "target_similarity": self.config["target_similarity"],
            "progress_to_target": (new_similarity / self.config["target_similarity"]) * 100
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📋 訓練報告已生成: {report_file}")
    
    async def shutdown(self):
        """關閉系統"""
        logger.info("🛑 正在關閉統一實時K2系統...")
        
        self.system_running = False
        
        # 關閉各個組件
        await self.realtime_collector.shutdown()
        
        logger.info("✅ 統一實時K2系統已關閉")

async def main():
    """主函數"""
    print("🚀 啟動統一實時K2+DeepSWE+MemoryRAG系統")
    print("=" * 60)
    print("🎯 功能特性:")
    print("  ✅ 實時Claude對話收集")
    print("  ✅ 自動K2/DeepSWE數據分類")
    print("  ✅ MacBook Air GPU訓練")
    print("  ✅ Claude Code性能測試")
    print("  ✅ 16小時/天自動運行")
    print("  ✅ 目標: 30天內達到80%相似度")
    print("=" * 60)
    
    # 創建統一系統
    unified_system = UnifiedRealtimeK2System()
    
    try:
        # 初始化系統
        success = await unified_system.initialize_system()
        
        if not success:
            print("❌ 系統初始化失敗")
            return
        
        print("✅ 系統初始化成功!")
        print("🔥 開始實時收集和訓練...")
        print("📊 當前Claude Code相似度: 45.7%")
        print("🎯 目標Claude Code相似度: 80%")
        print("\n按 Ctrl+C 停止系統")
        
        # 啟動實時收集和訓練
        await unified_system.start_realtime_collection()
        
    except KeyboardInterrupt:
        print("\n🛑 收到停止信號...")
    except Exception as e:
        print(f"❌ 系統運行錯誤: {e}")
    finally:
        await unified_system.shutdown()
        print("✅ 系統已安全關閉")

if __name__ == "__main__":
    asyncio.run(main())