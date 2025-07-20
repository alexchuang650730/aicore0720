#!/usr/bin/env python3
"""
更新應用程序數據路徑配置
將所有數據路徑指向EC2根目錄的安全位置
"""

import re
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPathUpdater:
    """數據路徑更新器"""
    
    def __init__(self):
        self.ec2_data_root = "/data/aicore_training_data/active"
        self.files_to_update = [
            "unified_realtime_k2_fixed.py",
            "enhanced_manus_extractor.py", 
            "comprehensive_k2_integration_engine.py",
            "macbook_air_gpu_trainer_fixed.py",
            "claude_continuous_learning_test.py",
            "simple_claude_code_test.py"
        ]
        
    def update_file_paths(self, file_path: str):
        """更新單個文件中的數據路徑"""
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                logger.warning(f"⚠️ 文件不存在: {file_path}")
                return False
            
            # 讀取文件內容
            with open(path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 路徑替換規則
            replacements = [
                # 基本數據目錄
                (r'Path\("data"\)', f'Path("{self.ec2_data_root}/training_data")'),
                (r'"data"', f'"{self.ec2_data_root}/training_data"'),
                (r"'data'", f"'{self.ec2_data_root}/training_data'"),
                (r'self\.base_dir / "data"', f'Path("{self.ec2_data_root}/training_data")'),
                
                # 增強萃取數據
                (r'Path\("data/enhanced_extraction"\)', f'Path("{self.ec2_data_root}/enhanced_extraction")'),
                (r'"data/enhanced_extraction"', f'"{self.ec2_data_root}/enhanced_extraction"'),
                
                # 訓練數據目錄
                (r'"data/comprehensive_training"', f'"{self.ec2_data_root}/training_data/comprehensive_training"'),
                (r'"data/claude_conversations"', f'"{self.ec2_data_root}/training_data/claude_conversations"'),
                (r'"data/continuous_learning_sessions"', f'"{self.ec2_data_root}/training_data/continuous_learning_sessions"'),
                
                # 相對路徑替換
                (r'\./"data"', f'"{self.ec2_data_root}/training_data"'),
                (r'\./data/', f'{self.ec2_data_root}/training_data/'),
                
                # 配置文件路徑
                (r'data/all_replay_links', f'{self.ec2_data_root}/active_data/all_replay_links'),
                (r'data/.*\.db', f'{self.ec2_data_root}/active_data/behavior_alignment.db'),
            ]
            
            # 執行替換
            changes_made = 0
            for pattern, replacement in replacements:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    changes_made += 1
                    
            # 如果有變更，寫回文件
            if content != original_content:
                # 備份原文件
                backup_path = path_obj.with_suffix(path_obj.suffix + '.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # 寫入更新後的內容
                with open(path_obj, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"✅ 更新文件: {file_path} (變更: {changes_made})")
                return True
            else:
                logger.info(f"➡️ 無需更新: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 更新文件失敗 {file_path}: {e}")
            return False
    
    def create_data_access_module(self):
        """創建統一的數據訪問模塊"""
        module_content = f'''#!/usr/bin/env python3
"""
統一數據訪問模塊
提供標準化的數據路徑訪問接口
"""

from pathlib import Path
import os

class DataPaths:
    """統一數據路徑管理"""
    
    # EC2根目錄數據路徑
    EC2_DATA_ROOT = Path("{self.ec2_data_root}")
    
    # 主要數據目錄
    TRAINING_DATA = EC2_DATA_ROOT / "training_data"
    ENHANCED_EXTRACTION = EC2_DATA_ROOT / "enhanced_extraction" 
    ACTIVE_DATA = EC2_DATA_ROOT / "active_data"
    
    # 子目錄
    COMPREHENSIVE_TRAINING = TRAINING_DATA / "comprehensive_training"
    CLAUDE_CONVERSATIONS = TRAINING_DATA / "claude_conversations"
    CONTINUOUS_LEARNING = TRAINING_DATA / "continuous_learning_sessions"
    
    # 配置文件
    REPLAY_LINKS = ACTIVE_DATA / "all_replay_links_20250720_184947.txt"
    BEHAVIOR_DB = ACTIVE_DATA / "behavior_alignment.db"
    
    @classmethod
    def ensure_directories(cls):
        """確保所有目錄存在"""
        directories = [
            cls.TRAINING_DATA,
            cls.ENHANCED_EXTRACTION,
            cls.ACTIVE_DATA,
            cls.COMPREHENSIVE_TRAINING,
            cls.CLAUDE_CONVERSATIONS,
            cls.CONTINUOUS_LEARNING
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_data_size(cls):
        """獲取數據目錄大小"""
        import subprocess
        try:
            result = subprocess.run(
                ['du', '-sh', str(cls.EC2_DATA_ROOT)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.split()[0]
        except:
            pass
        return "未知"
    
    @classmethod
    def is_data_available(cls):
        """檢查數據是否可用"""
        return cls.EC2_DATA_ROOT.exists() and cls.TRAINING_DATA.exists()

# 便捷函數
def get_training_data_path():
    """獲取訓練數據路徑"""
    return DataPaths.TRAINING_DATA

def get_enhanced_extraction_path():
    """獲取增強萃取數據路徑"""
    return DataPaths.ENHANCED_EXTRACTION

def get_active_data_path():
    """獲取活動數據路徑"""
    return DataPaths.ACTIVE_DATA

# 初始化檢查
if __name__ == "__main__":
    print("🔍 AICore數據路徑檢查")
    print("=" * 40)
    print(f"EC2數據根目錄: {{DataPaths.EC2_DATA_ROOT}}")
    print(f"數據可用性: {{DataPaths.is_data_available()}}")
    print(f"數據大小: {{DataPaths.get_data_size()}}")
    
    if DataPaths.is_data_available():
        print("✅ 數據路徑配置正確")
    else:
        print("❌ 數據路徑未找到，請檢查備份")
'''
        
        # 寫入數據訪問模塊
        module_path = Path("data_paths.py")
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(module_content)
            
        logger.info(f"✅ 創建數據訪問模塊: {module_path}")
        return True
    
    def update_all_files(self):
        """更新所有相關文件"""
        success_count = 0
        
        logger.info("🔄 開始更新應用程序數據路徑...")
        
        for file_path in self.files_to_update:
            if self.update_file_paths(file_path):
                success_count += 1
        
        # 創建統一數據訪問模塊
        if self.create_data_access_module():
            success_count += 1
            
        logger.info(f"✅ 路徑更新完成: {success_count}/{len(self.files_to_update) + 1} 成功")
        
        return success_count == len(self.files_to_update) + 1

def main():
    """主函數"""
    print("🔧 AICore數據路徑配置更新")
    print("=" * 40)
    print("📂 目標: 將數據路徑指向EC2根目錄")
    print("🔒 位置: /data/aicore_training_data/active")
    print("=" * 40)
    
    updater = DataPathUpdater()
    
    # 檢查EC2數據目錄是否存在
    if not Path(updater.ec2_data_root).exists():
        print(f"❌ EC2數據目錄不存在: {updater.ec2_data_root}")
        print("請先運行備份腳本: sudo ./quick_secure_backup.sh")
        return False
    
    # 更新所有文件
    if updater.update_all_files():
        print("\n✅ 所有文件路徑更新完成！")
        print("=" * 40)
        print("📝 下一步:")
        print("1. 測試應用程序能否正常訪問新的數據位置")
        print("2. 驗證訓練和萃取功能正常")
        print("3. 刪除備份文件 (*.bak)")
        print("4. 提交更新到Git")
        return True
    else:
        print("❌ 部分文件更新失敗，請檢查日誌")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)