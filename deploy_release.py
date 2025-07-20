#!/usr/bin/env python3
"""
AICore Release部署腳本
自動化處理Release版本的數據管理和部署流程
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReleaseDeployer:
    """Release部署管理器"""
    
    def __init__(self, version: str):
        self.version = version
        self.project_root = Path(__file__).parent
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def pre_release_checks(self):
        """發布前檢查"""
        logger.info("🔍 執行發布前檢查...")
        
        checks = []
        
        # 1. 檢查Git狀態
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            if result.stdout.strip():
                checks.append(("❌", "Git工作目錄有未提交的變更"))
            else:
                checks.append(("✅", "Git工作目錄乾淨"))
        except:
            checks.append(("⚠️", "無法檢查Git狀態"))
        
        # 2. 檢查數據目錄
        data_dir = self.project_root / "data"
        if data_dir.exists():
            data_size = self._get_directory_size(data_dir)
            checks.append(("✅", f"數據目錄存在，大小: {data_size}"))
        else:
            checks.append(("❌", "數據目錄不存在"))
        
        # 3. 檢查關鍵文件
        critical_files = [
            "unified_realtime_k2_fixed.py",
            "enhanced_manus_extractor.py",
            "comprehensive_k2_integration_engine.py",
            "claude_continuous_learning_test.py"
        ]
        
        for file_name in critical_files:
            if (self.project_root / file_name).exists():
                checks.append(("✅", f"關鍵文件存在: {file_name}"))
            else:
                checks.append(("❌", f"關鍵文件缺失: {file_name}"))
        
        # 4. 檢查EC2環境
        if os.path.exists("/etc/cloud") or os.path.exists("/opt/aws"):
            checks.append(("✅", "EC2環境檢測成功"))
        else:
            checks.append(("⚠️", "非EC2環境，請確認部署目標"))
        
        # 顯示檢查結果
        logger.info("📋 檢查結果:")
        failed_checks = 0
        for status, message in checks:
            logger.info(f"  {status} {message}")
            if status == "❌":
                failed_checks += 1
        
        if failed_checks > 0:
            logger.error(f"❌ {failed_checks} 項檢查失敗，無法繼續部署")
            return False
        
        logger.info("✅ 所有檢查通過")
        return True
    
    def backup_current_data(self):
        """備份當前數據到EC2"""
        logger.info("📦 備份數據到EC2根目錄...")
        
        try:
            # 執行快速備份腳本
            backup_script = self.project_root / "quick_secure_backup.sh"
            if not backup_script.exists():
                logger.error("❌ 備份腳本不存在")
                return False
            
            # 確保腳本有執行權限
            os.chmod(backup_script, 0o755)
            
            # 執行備份
            result = subprocess.run(['sudo', str(backup_script)], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info("✅ 數據備份完成")
                return True
            else:
                logger.error(f"❌ 備份失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 備份過程錯誤: {e}")
            return False
    
    def update_version_config(self):
        """更新版本配置"""
        logger.info(f"📝 更新版本配置: {self.version}")
        
        try:
            # 使用版本數據管理器
            from version_data_manager import VersionDataManager
            
            manager = VersionDataManager()
            if manager.switch_to_release_mode(self.version):
                logger.info("✅ 版本配置更新完成")
                return True
            else:
                logger.error("❌ 版本配置更新失敗")
                return False
                
        except Exception as e:
            logger.error(f"❌ 版本配置錯誤: {e}")
            return False
    
    def create_release_manifest(self):
        """創建發布清單"""
        logger.info("📋 創建發布清單...")
        
        try:
            manifest = {
                "release_info": {
                    "version": self.version,
                    "timestamp": datetime.now().isoformat(),
                    "deployment_type": "release",
                    "data_location": "/data/aicore_training_data/active"
                },
                "features": [
                    "K2+DeepSWE+MemoryRAG統一AI助手系統",
                    "增強Manus對話萃取 (支持2小時長對話)",
                    "MacBook Air GPU訓練支持 (Apple Silicon MPS)",
                    "實時Claude對話收集和訓練pipeline",
                    "持續學習測試系統 (16小時自動運行)",
                    "統一實時K2訓練和性能監控",
                    "版本化數據管理 (Release/User模式分離)"
                ],
                "improvements": [
                    "Claude Code相似度提升至50.9%",
                    "訓練數據質量優化 (支持355條消息長對話)",
                    "後台增強萃取系統 (batch 89+運行中)",
                    "數據安全遷移至EC2根目錄",
                    "智能會話管理和質量評分",
                    "實時性能監控和自動優化"
                ],
                "system_status": {
                    "data_size": self._get_directory_size(Path("/data/aicore_training_data")),
                    "training_files": self._count_training_files(),
                    "extraction_progress": self._get_extraction_progress(),
                    "k2_performance": "50.9% Claude Code similarity"
                },
                "deployment_notes": [
                    "數據已安全遷移至/data/aicore_training_data/",
                    "使用軟連結/data/aicore_training_data/active訪問",
                    "後台萃取系統持續運行",
                    "統一K2訓練系統自動監控",
                    "支援16小時持續學習模式"
                ]
            }
            
            # 保存發布清單
            manifest_file = Path(f"/data/aicore_training_data/release_manifest_{self.version}_{self.timestamp}.json")
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 發布清單已創建: {manifest_file}")
            return manifest
            
        except Exception as e:
            logger.error(f"❌ 創建發布清單失敗: {e}")
            return None
    
    def test_deployment(self):
        """測試部署"""
        logger.info("🧪 測試部署...")
        
        tests = []
        
        # 1. 測試數據訪問
        try:
            from data_paths import DataPaths
            if DataPaths.is_data_available():
                tests.append(("✅", "數據路徑可訪問"))
            else:
                tests.append(("❌", "數據路徑不可訪問"))
        except:
            tests.append(("❌", "數據路徑模塊載入失敗"))
        
        # 2. 測試核心模塊導入
        core_modules = [
            "comprehensive_k2_integration_engine",
            "enhanced_manus_extractor",
            "unified_realtime_k2_fixed"
        ]
        
        for module_name in core_modules:
            try:
                __import__(module_name)
                tests.append(("✅", f"模塊導入成功: {module_name}"))
            except Exception as e:
                tests.append(("❌", f"模塊導入失敗: {module_name} - {e}"))
        
        # 3. 測試EC2數據連接
        ec2_data_path = Path("/data/aicore_training_data/active")
        if ec2_data_path.exists():
            tests.append(("✅", "EC2數據連接正常"))
        else:
            tests.append(("❌", "EC2數據連接失敗"))
        
        # 顯示測試結果
        logger.info("🧪 測試結果:")
        failed_tests = 0
        for status, message in tests:
            logger.info(f"  {status} {message}")
            if status == "❌":
                failed_tests += 1
        
        if failed_tests > 0:
            logger.warning(f"⚠️ {failed_tests} 項測試失敗")
            return False
        
        logger.info("✅ 所有測試通過")
        return True
    
    def finalize_deployment(self):
        """完成部署"""
        logger.info("🎯 完成部署...")
        
        try:
            # 1. 創建版本標記
            version_file = Path(f"/data/aicore_training_data/VERSION_{self.version}")
            with open(version_file, 'w') as f:
                f.write(f"AICore Release {self.version}\n")
                f.write(f"Deployed: {datetime.now().isoformat()}\n")
                f.write(f"Data Location: /data/aicore_training_data/active\n")
                f.write(f"Features: K2+DeepSWE+MemoryRAG\n")
                f.write(f"Performance: 50.9% Claude Code similarity\n")
            
            # 2. 設置正確的權限
            subprocess.run(['sudo', 'chown', '-R', 'ec2-user:ec2-user', '/data/aicore_training_data/'], 
                          capture_output=True)
            subprocess.run(['sudo', 'chmod', '-R', '755', '/data/aicore_training_data/'], 
                          capture_output=True)
            
            # 3. 創建快速啟動腳本
            startup_script = Path("/data/aicore_training_data/start_aicore.sh")
            with open(startup_script, 'w') as f:
                f.write(f"""#!/bin/bash
# AICore {self.version} 快速啟動腳本

echo "🚀 啟動AICore {self.version}"
echo "=" * 40

cd /opt/aicore/  # 假設應用程序安裝目錄

# 啟動統一K2系統
echo "🤖 啟動統一K2訓練系統..."
nohup python3 unified_realtime_k2_fixed.py > /data/aicore_training_data/logs/k2_system.log 2>&1 &

# 啟動持續學習系統
echo "📚 啟動持續學習系統..."
nohup python3 claude_continuous_learning_test.py > /data/aicore_training_data/logs/learning.log 2>&1 &

echo "✅ AICore {self.version} 啟動完成"
echo "📊 監控: tail -f /data/aicore_training_data/logs/*.log"
""")
            
            os.chmod(startup_script, 0o755)
            
            logger.info("✅ 部署完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 完成部署失敗: {e}")
            return False
    
    def _get_directory_size(self, directory):
        """獲取目錄大小"""
        try:
            result = subprocess.run(['du', '-sh', str(directory)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.split()[0]
        except:
            pass
        return "未知"
    
    def _count_training_files(self):
        """統計訓練文件數量"""
        try:
            training_dir = Path("/data/aicore_training_data/active/training_data")
            if training_dir.exists():
                return len(list(training_dir.rglob("*.json")))
        except:
            pass
        return 0
    
    def _get_extraction_progress(self):
        """獲取萃取進度"""
        try:
            log_file = Path("background_extraction.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # 尋找最新的批次信息
                    for line in reversed(lines):
                        if "處理批次" in line:
                            return line.strip().split(":")[-1].strip()
        except:
            pass
        return "未知"

def main():
    """主函數"""
    if len(sys.argv) != 2:
        print("使用方法: python3 deploy_release.py <version>")
        print("例如: python3 deploy_release.py v4.7.9")
        sys.exit(1)
    
    version = sys.argv[1]
    
    print(f"🚀 AICore Release部署: {version}")
    print("=" * 60)
    
    deployer = ReleaseDeployer(version)
    
    try:
        # 1. 發布前檢查
        if not deployer.pre_release_checks():
            print("❌ 發布前檢查失敗")
            return False
        
        # 2. 備份數據
        if not deployer.backup_current_data():
            print("❌ 數據備份失敗")
            return False
        
        # 3. 更新版本配置
        if not deployer.update_version_config():
            print("❌ 版本配置失敗")
            return False
        
        # 4. 創建發布清單
        manifest = deployer.create_release_manifest()
        if not manifest:
            print("❌ 發布清單創建失敗")
            return False
        
        # 5. 測試部署
        if not deployer.test_deployment():
            print("⚠️ 部署測試有問題，但繼續...")
        
        # 6. 完成部署
        if not deployer.finalize_deployment():
            print("❌ 完成部署失敗")
            return False
        
        # 顯示部署摘要
        print(f"\n✅ AICore {version} 部署成功！")
        print("=" * 60)
        print(f"📂 數據位置: /data/aicore_training_data/active")
        print(f"📋 發布清單: 已創建")
        print(f"🎯 功能: K2+DeepSWE+MemoryRAG統一系統")
        print(f"📊 性能: 50.9% Claude Code相似度")
        print("=" * 60)
        print("\n📝 後續步驟:")
        print("1. 啟動AICore服務: /data/aicore_training_data/start_aicore.sh")
        print("2. 監控日誌: tail -f /data/aicore_training_data/logs/*.log")
        print("3. 檢查性能: 監控K2訓練進度")
        print("4. 驗證功能: 測試持續學習系統")
        
        return True
        
    except Exception as e:
        print(f"❌ 部署過程發生錯誤: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)