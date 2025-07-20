#!/usr/bin/env python3
"""
版本化數據管理系統
Release版本: 數據同步到EC2雲端
User版本: 數據保留在本地訓練
"""

import os
import json
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VersionDataManager:
    """版本化數據管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.local_data_dir = self.project_root / "data"
        self.ec2_data_dir = Path("/data/aicore_training_data")
        
        # 版本配置
        self.version_config_file = self.project_root / "version_config.json"
        self.load_version_config()
        
    def load_version_config(self):
        """加載版本配置"""
        default_config = {
            "version_type": "user",  # "release" or "user"
            "current_version": "v4.7.8",
            "data_strategy": {
                "release": {
                    "data_location": "/data/aicore_training_data/active",
                    "sync_to_ec2": True,
                    "local_backup": True,
                    "training_location": "ec2"
                },
                "user": {
                    "data_location": "./data",
                    "sync_to_ec2": False,
                    "local_backup": True,
                    "training_location": "local"
                }
            },
            "last_sync": None,
            "release_history": []
        }
        
        if self.version_config_file.exists():
            with open(self.version_config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_version_config()
    
    def save_version_config(self):
        """保存版本配置"""
        with open(self.version_config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def detect_version_type(self):
        """檢測當前版本類型"""
        # 檢查是否在發布環境（EC2）
        if os.path.exists("/etc/cloud") or os.path.exists("/opt/aws"):
            return "release"
        
        # 檢查是否有release標記
        release_marker = self.project_root / ".release_version"
        if release_marker.exists():
            return "release"
            
        return "user"
    
    def switch_to_release_mode(self, version: str):
        """切換到Release模式"""
        logger.info(f"🚀 切換到Release模式: {version}")
        
        try:
            # 1. 更新配置
            self.config["version_type"] = "release"
            self.config["current_version"] = version
            
            # 2. 確保EC2數據目錄存在
            if not self.ec2_data_dir.exists():
                logger.error("❌ EC2數據目錄不存在，請先執行備份")
                return False
            
            # 3. 同步本地數據到EC2
            if self.local_data_dir.exists():
                sync_result = self._sync_data_to_ec2()
                if not sync_result:
                    return False
            
            # 4. 創建Release標記
            release_marker = self.project_root / ".release_version"
            with open(release_marker, 'w') as f:
                f.write(f"release_version={version}\n")
                f.write(f"timestamp={datetime.now().isoformat()}\n")
                f.write(f"data_location={self.ec2_data_dir}/active\n")
            
            # 5. 更新應用程序配置指向EC2
            self._update_app_config_for_release()
            
            # 6. 記錄發布歷史
            self.config["release_history"].append({
                "version": version,
                "timestamp": datetime.now().isoformat(),
                "data_size": self._get_data_size(self.ec2_data_dir),
                "sync_status": "completed"
            })
            
            self.config["last_sync"] = datetime.now().isoformat()
            self.save_version_config()
            
            logger.info(f"✅ Release模式配置完成: {version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 切換Release模式失敗: {e}")
            return False
    
    def switch_to_user_mode(self):
        """切換到User模式"""
        logger.info("👤 切換到User模式")
        
        try:
            # 1. 更新配置
            self.config["version_type"] = "user"
            
            # 2. 確保本地數據目錄存在
            self.local_data_dir.mkdir(parents=True, exist_ok=True)
            
            # 3. 如果有EC2數據，創建本地副本（僅限首次）
            if not self._has_local_training_data() and self.ec2_data_dir.exists():
                logger.info("📦 從EC2創建本地訓練數據副本...")
                self._create_local_copy_from_ec2()
            
            # 4. 移除Release標記
            release_marker = self.project_root / ".release_version"
            if release_marker.exists():
                release_marker.unlink()
            
            # 5. 更新應用程序配置指向本地
            self._update_app_config_for_user()
            
            self.save_version_config()
            
            logger.info("✅ User模式配置完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 切換User模式失敗: {e}")
            return False
    
    def _sync_data_to_ec2(self):
        """同步數據到EC2"""
        try:
            logger.info("📤 同步數據到EC2...")
            
            # 創建時間戳備份
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.ec2_data_dir / f"release_{self.config['current_version']}_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 同步各個數據目錄
            sync_dirs = [
                ("enhanced_extraction", "enhanced_extraction"),
                ("comprehensive_training", "training_data/comprehensive_training"),
                ("claude_conversations", "training_data/claude_conversations"),
                ("continuous_learning_sessions", "training_data/continuous_learning_sessions")
            ]
            
            for local_subdir, ec2_subdir in sync_dirs:
                local_path = self.local_data_dir / local_subdir
                ec2_path = backup_dir / ec2_subdir
                
                if local_path.exists():
                    ec2_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(local_path, ec2_path, dirs_exist_ok=True)
                    logger.info(f"  ✅ 同步 {local_subdir}")
            
            # 同步配置文件
            config_files = list(self.local_data_dir.glob("*.txt")) + list(self.local_data_dir.glob("*.db"))
            if config_files:
                active_data_dir = backup_dir / "active_data"
                active_data_dir.mkdir(exist_ok=True)
                for config_file in config_files:
                    shutil.copy2(config_file, active_data_dir / config_file.name)
            
            # 更新active軟連結
            active_link = self.ec2_data_dir / "active"
            if active_link.is_symlink():
                active_link.unlink()
            active_link.symlink_to(backup_dir)
            
            logger.info(f"✅ 數據同步完成: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 數據同步失敗: {e}")
            return False
    
    def _create_local_copy_from_ec2(self):
        """從EC2創建本地數據副本"""
        try:
            ec2_active = self.ec2_data_dir / "active"
            if not ec2_active.exists():
                logger.warning("⚠️ EC2活動數據不存在")
                return False
            
            # 創建本地數據結構
            subdirs = ["enhanced_extraction", "comprehensive_training", "claude_conversations", "continuous_learning_sessions"]
            for subdir in subdirs:
                (self.local_data_dir / subdir).mkdir(parents=True, exist_ok=True)
            
            # 複製部分訓練數據（用於本地開發）
            training_data_dir = ec2_active / "training_data"
            if training_data_dir.exists():
                # 只複製最新的訓練數據樣本
                for subdir in subdirs[1:]:  # 跳過enhanced_extraction
                    ec2_subdir = training_data_dir / subdir
                    local_subdir = self.local_data_dir / subdir
                    
                    if ec2_subdir.exists():
                        # 複製最新的50個文件作為開發數據
                        files = sorted(ec2_subdir.glob("*.json"), key=lambda x: x.stat().st_mtime)[-50:]
                        for file_path in files:
                            shutil.copy2(file_path, local_subdir / file_path.name)
            
            # 複製配置文件
            active_data_dir = ec2_active / "active_data"
            if active_data_dir.exists():
                for config_file in active_data_dir.glob("*"):
                    if config_file.is_file():
                        shutil.copy2(config_file, self.local_data_dir / config_file.name)
            
            logger.info("✅ 本地開發數據副本創建完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 創建本地副本失敗: {e}")
            return False
    
    def _has_local_training_data(self):
        """檢查是否有本地訓練數據"""
        if not self.local_data_dir.exists():
            return False
        
        training_dirs = ["comprehensive_training", "claude_conversations"]
        for dir_name in training_dirs:
            dir_path = self.local_data_dir / dir_name
            if dir_path.exists() and any(dir_path.glob("*.json")):
                return True
        
        return False
    
    def _update_app_config_for_release(self):
        """更新應用程序配置為Release模式"""
        # 這裡可以調用之前創建的update_data_paths.py
        pass
    
    def _update_app_config_for_user(self):
        """更新應用程序配置為User模式"""
        # 恢復本地數據路徑
        pass
    
    def _get_data_size(self, directory):
        """獲取目錄大小"""
        try:
            result = subprocess.run(['du', '-sh', str(directory)], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.split()[0]
        except:
            pass
        return "未知"
    
    def get_current_config(self):
        """獲取當前配置信息"""
        current_type = self.config["version_type"]
        strategy = self.config["data_strategy"][current_type]
        
        return {
            "version_type": current_type,
            "current_version": self.config["current_version"],
            "data_location": strategy["data_location"],
            "training_location": strategy["training_location"],
            "sync_to_ec2": strategy["sync_to_ec2"],
            "last_sync": self.config.get("last_sync"),
            "local_data_exists": self.local_data_dir.exists(),
            "ec2_data_exists": self.ec2_data_dir.exists()
        }

def main():
    """主函數"""
    print("🔄 AICore版本化數據管理系統")
    print("=" * 50)
    
    manager = VersionDataManager()
    current_config = manager.get_current_config()
    
    print(f"📦 當前版本: {current_config['current_version']}")
    print(f"🏷️ 版本類型: {current_config['version_type']}")
    print(f"📂 數據位置: {current_config['data_location']}")
    print(f"🎯 訓練位置: {current_config['training_location']}")
    print(f"☁️ 同步EC2: {current_config['sync_to_ec2']}")
    print("=" * 50)
    
    print("\n🔧 可用操作:")
    print("1. 切換到Release模式 (數據同步到EC2)")
    print("2. 切換到User模式 (本地訓練)")
    print("3. 檢查數據狀態")
    print("4. 顯示配置信息")
    
    try:
        choice = input("\n請選擇操作 (1-4): ")
    except EOFError:
        print("🤖 非交互模式，顯示當前配置")
        choice = "4"
    
    if choice == "1":
        version = input("請輸入Release版本號 (如 v4.7.9): ")
        if manager.switch_to_release_mode(version):
            print("✅ 已切換到Release模式")
        else:
            print("❌ 切換失敗")
    
    elif choice == "2":
        if manager.switch_to_user_mode():
            print("✅ 已切換到User模式")
        else:
            print("❌ 切換失敗")
    
    elif choice == "3":
        print("\n📊 數據狀態檢查:")
        print(f"本地數據: {'✅' if current_config['local_data_exists'] else '❌'}")
        print(f"EC2數據: {'✅' if current_config['ec2_data_exists'] else '❌'}")
        if current_config['last_sync']:
            print(f"最後同步: {current_config['last_sync']}")
    
    elif choice == "4":
        print("\n📋 詳細配置:")
        for key, value in current_config.items():
            print(f"  {key}: {value}")
    
    else:
        print("❌ 無效選擇")

if __name__ == "__main__":
    main()