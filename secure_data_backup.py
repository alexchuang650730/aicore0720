#!/usr/bin/env python3
"""
安全數據備份和遷移腳本
將重要的訓練數據備份到EC2根目錄，確保數據安全
"""

import os
import shutil
import json
import time
from pathlib import Path
from datetime import datetime
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureDataBackup:
    """安全數據備份管理器"""
    
    def __init__(self):
        self.local_data_dir = Path("data")
        self.backup_base_dir = Path("/data")  # EC2根目錄
        self.backup_dir = self.backup_base_dir / "aicore_training_data"
        
        # 創建時間戳備份目錄
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_backup_dir = self.backup_dir / f"backup_{timestamp}"
        
    def create_backup_structure(self):
        """創建備份目錄結構"""
        try:
            # 創建主備份目錄
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            self.current_backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 創建各子目錄
            subdirs = [
                "enhanced_extraction",
                "training_data", 
                "models",
                "logs",
                "continuous_learning",
                "active_data"
            ]
            
            for subdir in subdirs:
                (self.current_backup_dir / subdir).mkdir(exist_ok=True)
                
            logger.info(f"✅ 備份目錄結構創建完成: {self.current_backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 創建備份目錄失敗: {e}")
            return False
    
    def backup_critical_data(self):
        """備份關鍵數據"""
        try:
            if not self.local_data_dir.exists():
                logger.warning("⚠️ 本地data目錄不存在")
                return False
                
            # 1. 備份增強萃取數據
            enhanced_dir = self.local_data_dir / "enhanced_extraction"
            if enhanced_dir.exists():
                dest_dir = self.current_backup_dir / "enhanced_extraction"
                shutil.copytree(enhanced_dir, dest_dir, dirs_exist_ok=True)
                logger.info(f"✅ 增強萃取數據備份完成: {len(list(dest_dir.glob('*')))} 個文件")
            
            # 2. 備份訓練數據
            training_dirs = [
                "comprehensive_training",
                "claude_conversations", 
                "continuous_learning_sessions"
            ]
            
            for dir_name in training_dirs:
                src_dir = self.local_data_dir / dir_name
                if src_dir.exists():
                    dest_dir = self.current_backup_dir / "training_data" / dir_name
                    shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
                    logger.info(f"✅ {dir_name} 備份完成")
            
            # 3. 備份重要配置和統計文件
            config_files = [
                "all_replay_links_*.txt",
                "*.db",
                "*.json"
            ]
            
            for pattern in config_files:
                for file_path in self.local_data_dir.glob(pattern):
                    if file_path.is_file():
                        dest_file = self.current_backup_dir / "active_data" / file_path.name
                        shutil.copy2(file_path, dest_file)
                        logger.info(f"✅ 配置文件備份: {file_path.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 數據備份失敗: {e}")
            return False
    
    def create_backup_manifest(self):
        """創建備份清單"""
        try:
            manifest = {
                "backup_timestamp": datetime.now().isoformat(),
                "backup_location": str(self.current_backup_dir),
                "source_location": str(self.local_data_dir.absolute()),
                "backup_size_mb": self._calculate_backup_size(),
                "file_counts": self._count_backup_files(),
                "backup_status": "completed",
                "restore_instructions": {
                    "step1": "確保目標目錄存在",
                    "step2": f"cp -r {self.current_backup_dir}/training_data/* ./data/",
                    "step3": f"cp -r {self.current_backup_dir}/active_data/* ./data/",
                    "step4": "驗證數據完整性"
                }
            }
            
            manifest_file = self.current_backup_dir / "backup_manifest.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
                
            logger.info(f"✅ 備份清單創建完成: {manifest_file}")
            return manifest
            
        except Exception as e:
            logger.error(f"❌ 創建備份清單失敗: {e}")
            return None
    
    def _calculate_backup_size(self):
        """計算備份大小（MB）"""
        try:
            result = subprocess.run(
                ['du', '-sm', str(self.current_backup_dir)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return int(result.stdout.split()[0])
            return 0
        except:
            return 0
    
    def _count_backup_files(self):
        """統計備份文件數量"""
        counts = {}
        try:
            for subdir in self.current_backup_dir.iterdir():
                if subdir.is_dir():
                    file_count = len(list(subdir.rglob('*')))
                    counts[subdir.name] = file_count
            return counts
        except:
            return {}
    
    def setup_active_data_symlink(self):
        """設置活動數據軟連結"""
        try:
            # 創建一個active軟連結指向最新備份
            active_link = self.backup_dir / "active"
            
            # 移除舊的軟連結
            if active_link.is_symlink():
                active_link.unlink()
            
            # 創建新的軟連結
            active_link.symlink_to(self.current_backup_dir)
            
            logger.info(f"✅ 活動數據軟連結創建: {active_link} -> {self.current_backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 創建軟連結失敗: {e}")
            return False
    
    def update_gitignore_for_production(self):
        """更新.gitignore為生產模式"""
        try:
            gitignore_path = Path(".gitignore")
            if not gitignore_path.exists():
                logger.warning("⚠️ .gitignore 文件不存在")
                return False
            
            # 讀取當前內容
            with open(gitignore_path, 'r') as f:
                content = f.read()
            
            # 添加生產環境配置
            production_rules = f"""
# Production Data Security (Added by secure_data_backup.py)
data/
*.key
*.pem
*.env.production
/data_backup_*

# EC2 Backup Reference
# Active data location: {self.backup_dir}/active/
# Backup timestamp: {datetime.now().isoformat()}
"""
            
            if "Production Data Security" not in content:
                with open(gitignore_path, 'a') as f:
                    f.write(production_rules)
                
                logger.info("✅ .gitignore 已更新為生產模式")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新.gitignore失敗: {e}")
            return False

def main():
    """主函數"""
    print("🔒 AICore訓練數據安全備份系統")
    print("="*60)
    print(f"📂 源目錄: ./data/")
    print(f"🏠 目標目錄: /data/aicore_training_data/")
    print("="*60)
    
    backup_system = SecureDataBackup()
    
    # 檢查權限
    if not os.access("/", os.W_OK):
        print("❌ 錯誤: 需要root權限寫入EC2根目錄")
        print("請使用: sudo python3 secure_data_backup.py")
        return False
    
    try:
        # 1. 創建備份結構
        print("🏗️ 創建備份目錄結構...")
        if not backup_system.create_backup_structure():
            return False
        
        # 2. 備份關鍵數據
        print("📦 備份關鍵訓練數據...")
        if not backup_system.backup_critical_data():
            return False
        
        # 3. 創建備份清單
        print("📋 創建備份清單...")
        manifest = backup_system.create_backup_manifest()
        if not manifest:
            return False
        
        # 4. 設置活動數據軟連結
        print("🔗 設置活動數據軟連結...")
        if not backup_system.setup_active_data_symlink():
            return False
        
        # 5. 更新.gitignore
        print("🛡️ 更新.gitignore安全配置...")
        backup_system.update_gitignore_for_production()
        
        # 顯示備份摘要
        print("\n✅ 備份完成！")
        print("="*60)
        print(f"📂 備份位置: {backup_system.current_backup_dir}")
        print(f"📊 備份大小: {manifest['backup_size_mb']} MB")
        print(f"📄 文件數量: {sum(manifest['file_counts'].values())}")
        print(f"🔗 活動連結: {backup_system.backup_dir}/active")
        print("="*60)
        
        print("\n📝 後續步驟:")
        print("1. 驗證備份完整性")
        print("2. 更新應用程序配置指向新的數據位置")
        print("3. 測試從備份位置恢復")
        print("4. 設置定期備份任務")
        
        return True
        
    except Exception as e:
        print(f"❌ 備份過程中發生錯誤: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)