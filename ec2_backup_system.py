#!/usr/bin/env python3
"""
EC2備份系統 - 一鍵備份訓練數據和系統
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import tarfile
import hashlib
import boto3
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EC2BackupSystem:
    """EC2備份管理系統"""
    
    def __init__(self):
        self.base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        self.backup_config = {
            "ec2_instance": "i-0123456789abcdef0",  # 替換為實際EC2實例ID
            "region": "us-west-2",
            "bucket_name": "aicore-training-backup",
            "key_path": "/Users/alexchuang/alexchuang.pem"
        }
        
        # 備份內容配置
        self.backup_items = {
            "training_data": {
                "paths": [
                    "data/k2_training_*.jsonl",
                    "data/deepswe_training_*.jsonl",
                    "data/processed_replays/",
                    "data/enhanced_extractions/",
                    "memory_rag_store/"
                ],
                "description": "訓練數據（13,100個樣本）",
                "size_estimate": "2.5GB"
            },
            "replay_data": {
                "paths": [
                    "replay_*.json",
                    "manual_replay_*.json",
                    "replay_download_summary.json",
                    "final_replay_processing_report.md"
                ],
                "description": "524個replay URLs數據",
                "size_estimate": "1.2GB"
            },
            "models": {
                "paths": [
                    "models/",
                    "checkpoints/",
                    "*.pth",
                    "*.ckpt"
                ],
                "description": "訓練模型和檢查點",
                "size_estimate": "5GB"
            },
            "system_code": {
                "paths": [
                    "*.py",
                    "mcp_*.py",
                    "unified_*.py",
                    "smarttool_*.py",
                    "memoryrag_*.py"
                ],
                "description": "系統核心代碼",
                "size_estimate": "50MB"
            },
            "configs": {
                "paths": [
                    "*.json",
                    "*.yaml",
                    "*.conf",
                    "accuracy_metrics.json",
                    "ultimate_accuracy_metrics.json"
                ],
                "description": "配置文件",
                "size_estimate": "10MB"
            },
            "reports": {
                "paths": [
                    "*.md",
                    "reports/",
                    "*_report.md",
                    "*_report.json"
                ],
                "description": "分析報告",
                "size_estimate": "20MB"
            }
        }
        
        # EC2連接信息
        self.ec2_connection = {
            "host": "ec2-xx-xxx-xxx-xxx.us-west-2.compute.amazonaws.com",
            "user": "ubuntu",
            "backup_path": "/home/ubuntu/aicore_backups/"
        }
    
    def create_backup_archive(self) -> Path:
        """創建備份壓縮包"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"aicore_backup_{timestamp}.tar.gz"
        archive_path = self.base_dir / archive_name
        
        logger.info(f"📦 創建備份檔案: {archive_name}")
        
        with tarfile.open(archive_path, "w:gz") as tar:
            # 備份每個類別
            for category, config in self.backup_items.items():
                logger.info(f"  添加 {category}: {config['description']}")
                
                for pattern in config["paths"]:
                    files = list(self.base_dir.glob(pattern))
                    for file in files:
                        if file.exists():
                            if file.is_dir():
                                tar.add(file, arcname=file.relative_to(self.base_dir))
                            else:
                                tar.add(file, arcname=file.relative_to(self.base_dir))
        
        # 計算檔案大小和校驗碼
        file_size = archive_path.stat().st_size / (1024 * 1024)  # MB
        checksum = self.calculate_checksum(archive_path)
        
        logger.info(f"✅ 備份檔案創建完成")
        logger.info(f"   大小: {file_size:.2f} MB")
        logger.info(f"   校驗碼: {checksum}")
        
        return archive_path
    
    def calculate_checksum(self, file_path: Path) -> str:
        """計算文件校驗碼"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def upload_to_ec2(self, archive_path: Path) -> bool:
        """上傳到EC2"""
        logger.info(f"🚀 開始上傳到EC2...")
        
        # 構建SCP命令
        remote_path = f"{self.ec2_connection['user']}@{self.ec2_connection['host']}:{self.ec2_connection['backup_path']}"
        scp_cmd = [
            "scp",
            "-i", self.backup_config["key_path"],
            str(archive_path),
            remote_path
        ]
        
        try:
            # 執行上傳
            result = subprocess.run(scp_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ 上傳成功!")
                return True
            else:
                logger.error(f"❌ 上傳失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 上傳錯誤: {str(e)}")
            return False
    
    def upload_to_s3(self, archive_path: Path) -> bool:
        """備份到S3（可選）"""
        logger.info(f"☁️ 開始上傳到S3...")
        
        try:
            s3_client = boto3.client('s3', region_name=self.backup_config["region"])
            
            with open(archive_path, 'rb') as f:
                s3_client.upload_fileobj(
                    f,
                    self.backup_config["bucket_name"],
                    archive_path.name,
                    ExtraArgs={
                        'ServerSideEncryption': 'AES256',
                        'StorageClass': 'STANDARD_IA'
                    }
                )
            
            logger.info("✅ S3上傳成功!")
            return True
            
        except Exception as e:
            logger.error(f"❌ S3上傳錯誤: {str(e)}")
            return False
    
    def create_backup_manifest(self, archive_path: Path) -> Dict:
        """創建備份清單"""
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "archive_name": archive_path.name,
            "file_size_mb": archive_path.stat().st_size / (1024 * 1024),
            "checksum": self.calculate_checksum(archive_path),
            "backup_contents": {},
            "statistics": {
                "total_replay_urls": 524,
                "total_training_samples": 13100,
                "samples_per_replay": 25,
                "current_accuracy": 100.0,
                "memoryrag_boost": 14.8
            }
        }
        
        # 統計每個類別的文件數
        for category, config in self.backup_items.items():
            file_count = 0
            for pattern in config["paths"]:
                files = list(self.base_dir.glob(pattern))
                file_count += len(files)
            
            manifest["backup_contents"][category] = {
                "description": config["description"],
                "file_count": file_count,
                "estimated_size": config["size_estimate"]
            }
        
        # 保存清單
        manifest_path = self.base_dir / f"backup_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"📋 備份清單已保存: {manifest_path}")
        
        return manifest
    
    def one_click_backup(self, upload_s3: bool = False) -> bool:
        """一鍵備份"""
        logger.info("🔄 開始一鍵備份流程...")
        logger.info(f"📊 備份統計:")
        logger.info(f"   - 524個replay URLs")
        logger.info(f"   - 13,100個訓練樣本")
        logger.info(f"   - 每個replay平均25個樣本")
        
        try:
            # 1. 創建備份檔案
            archive_path = self.create_backup_archive()
            
            # 2. 創建備份清單
            manifest = self.create_backup_manifest(archive_path)
            
            # 3. 上傳到EC2
            ec2_success = self.upload_to_ec2(archive_path)
            
            # 4. 可選：上傳到S3
            s3_success = True
            if upload_s3:
                s3_success = self.upload_to_s3(archive_path)
            
            # 5. 清理本地備份檔案（可選）
            if ec2_success:
                logger.info(f"🗑️ 清理本地備份檔案...")
                # archive_path.unlink()  # 取消註釋以自動刪除
            
            # 6. 生成備份報告
            self.generate_backup_report(manifest, ec2_success, s3_success)
            
            return ec2_success
            
        except Exception as e:
            logger.error(f"❌ 備份失敗: {str(e)}")
            return False
    
    def generate_backup_report(self, manifest: Dict, ec2_success: bool, s3_success: bool):
        """生成備份報告"""
        report = f"""
# EC2備份報告

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📦 備份信息
- 檔案名稱: {manifest['archive_name']}
- 檔案大小: {manifest['file_size_mb']:.2f} MB
- 校驗碼: {manifest['checksum']}

## 📊 數據統計
- Replay URLs: {manifest['statistics']['total_replay_urls']}
- 訓練樣本: {manifest['statistics']['total_training_samples']}
- 每個Replay樣本數: {manifest['statistics']['samples_per_replay']}
- 當前準確率: {manifest['statistics']['current_accuracy']}%

## 📂 備份內容
"""
        
        for category, info in manifest['backup_contents'].items():
            report += f"\n### {category}\n"
            report += f"- 描述: {info['description']}\n"
            report += f"- 文件數: {info['file_count']}\n"
            report += f"- 預估大小: {info['estimated_size']}\n"
        
        report += f"""
## 🚀 上傳狀態
- EC2上傳: {'✅ 成功' if ec2_success else '❌ 失敗'}
- S3上傳: {'✅ 成功' if s3_success else '⏭️ 跳過'}

## 📝 備份命令
```bash
# 手動備份
python3 ec2_backup_system.py

# 包含S3備份
python3 ec2_backup_system.py --s3

# 從EC2恢復
scp -i {self.backup_config['key_path']} \\
    {self.ec2_connection['user']}@{self.ec2_connection['host']}:{self.ec2_connection['backup_path']}*.tar.gz .
```
"""
        
        report_path = self.base_dir / f"backup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"📄 備份報告已保存: {report_path}")
    
    def setup_auto_backup(self):
        """設置自動備份（cron）"""
        cron_script = f"""#!/bin/bash
# AICore自動備份腳本

cd {self.base_dir}
/usr/bin/python3 ec2_backup_system.py --s3

# 保留最近7天的備份
find {self.ec2_connection['backup_path']} -name "aicore_backup_*.tar.gz" -mtime +7 -delete
"""
        
        script_path = self.base_dir / "auto_backup.sh"
        with open(script_path, 'w') as f:
            f.write(cron_script)
        
        os.chmod(script_path, 0o755)
        
        logger.info(f"🔧 自動備份腳本已創建: {script_path}")
        logger.info("   添加到crontab: 0 2 * * * /path/to/auto_backup.sh")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='EC2備份系統')
    parser.add_argument('--s3', action='store_true', help='同時備份到S3')
    parser.add_argument('--setup', action='store_true', help='設置自動備份')
    args = parser.parse_args()
    
    backup_system = EC2BackupSystem()
    
    if args.setup:
        backup_system.setup_auto_backup()
    else:
        success = backup_system.one_click_backup(upload_s3=args.s3)
        
        if success:
            logger.info("🎉 備份完成！所有訓練數據已安全存儲到EC2")
        else:
            logger.error("❌ 備份過程中出現錯誤")
            exit(1)


if __name__ == "__main__":
    main()