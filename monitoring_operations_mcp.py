#!/usr/bin/env python3
"""
監控運維MCP - 全面監控AICore系統和EC2備份
"""

import json
import logging
import asyncio
import psutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import smtplib
from email.mime.text import MIMEText
import boto3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringOperationsMCP:
    """監控運維MCP - 全方位系統監控"""
    
    def __init__(self):
        self.base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        self.monitoring_config = {
            "check_interval": 300,  # 5分鐘檢查一次
            "alert_threshold": {
                "accuracy_drop": 2.0,  # 準確率下降2%觸發警報
                "disk_usage": 90,      # 磁盤使用率90%觸發警報
                "memory_usage": 85,    # 內存使用率85%觸發警報
                "backup_age": 24,      # 備份超過24小時觸發警報
                "training_stuck": 30   # 訓練卡住30分鐘觸發警報
            }
        }
        
        # 監控指標
        self.metrics = {
            "system_health": {},
            "training_status": {},
            "accuracy_metrics": {},
            "backup_status": {},
            "ec2_status": {},
            "alerts": []
        }
        
        # EC2監控配置
        self.ec2_config = {
            "instance_id": "i-0123456789abcdef0",
            "region": "us-west-2",
            "backup_path": "/home/ubuntu/aicore_backups/"
        }
        
        # 警報配置
        self.alert_config = {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender": "aicore.monitor@gmail.com",
                "recipients": ["alex@example.com"],
                "password": "your_app_password"
            },
            "slack": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz"
            },
            "log_file": self.base_dir / "monitoring_alerts.log"
        }
    
    async def start_monitoring(self):
        """啟動監控系統"""
        logger.info("🚀 啟動監控運維MCP...")
        
        # 創建監控任務
        tasks = [
            self.monitor_system_health(),
            self.monitor_training_progress(),
            self.monitor_accuracy_metrics(),
            self.monitor_backup_status(),
            self.monitor_ec2_health(),
            self.process_alerts()
        ]
        
        # 並行執行所有監控任務
        await asyncio.gather(*tasks)
    
    async def monitor_system_health(self):
        """監控系統健康狀態"""
        while True:
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # 內存使用
                memory = psutil.virtual_memory()
                
                # 磁盤使用
                disk = psutil.disk_usage(str(self.base_dir))
                
                # GPU使用（如果有）
                gpu_usage = await self.get_gpu_usage()
                
                # 進程狀態
                claude_processes = len([p for p in psutil.process_iter(['name']) 
                                      if 'claude' in p.info['name'].lower()])
                
                self.metrics["system_health"] = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3),
                    "gpu_usage": gpu_usage,
                    "claude_processes": claude_processes
                }
                
                # 檢查警報條件
                if memory.percent > self.monitoring_config["alert_threshold"]["memory_usage"]:
                    await self.create_alert(
                        "HIGH_MEMORY_USAGE",
                        f"內存使用率過高: {memory.percent:.1f}%",
                        "warning"
                    )
                
                if disk.percent > self.monitoring_config["alert_threshold"]["disk_usage"]:
                    await self.create_alert(
                        "HIGH_DISK_USAGE",
                        f"磁盤使用率過高: {disk.percent:.1f}%",
                        "critical"
                    )
                
                logger.info(f"💻 系統健康: CPU {cpu_percent:.1f}% | "
                          f"內存 {memory.percent:.1f}% | "
                          f"磁盤 {disk.percent:.1f}%")
                
            except Exception as e:
                logger.error(f"系統健康監控錯誤: {str(e)}")
            
            await asyncio.sleep(self.monitoring_config["check_interval"])
    
    async def monitor_training_progress(self):
        """監控訓練進度"""
        while True:
            try:
                # 檢查訓練日誌
                log_path = self.base_dir / "unified_k2_training.log"
                if log_path.exists():
                    # 獲取最後修改時間
                    last_modified = datetime.fromtimestamp(log_path.stat().st_mtime)
                    time_since_update = datetime.now() - last_modified
                    
                    # 檢查是否卡住
                    if time_since_update > timedelta(minutes=self.monitoring_config["alert_threshold"]["training_stuck"]):
                        await self.create_alert(
                            "TRAINING_STUCK",
                            f"訓練可能卡住了，{time_since_update.seconds//60}分鐘沒有更新",
                            "warning"
                        )
                    
                    # 讀取最新狀態
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        last_lines = lines[-10:] if len(lines) > 10 else lines
                        
                        # 提取關鍵信息
                        for line in last_lines:
                            if "目標達成率" in line:
                                achievement_rate = float(line.split(": ")[1].rstrip("%\n"))
                                self.metrics["training_status"]["achievement_rate"] = achievement_rate
                            elif "訓練周期" in line:
                                training_cycle = int(line.split(": ")[1])
                                self.metrics["training_status"]["training_cycle"] = training_cycle
                
                self.metrics["training_status"]["last_update"] = datetime.now().isoformat()
                self.metrics["training_status"]["is_running"] = time_since_update < timedelta(minutes=5)
                
            except Exception as e:
                logger.error(f"訓練進度監控錯誤: {str(e)}")
            
            await asyncio.sleep(self.monitoring_config["check_interval"])
    
    async def monitor_accuracy_metrics(self):
        """監控準確率指標"""
        while True:
            try:
                metrics_file = self.base_dir / "accuracy_metrics.json"
                if metrics_file.exists():
                    with open(metrics_file, 'r') as f:
                        current_metrics = json.load(f)
                    
                    current_accuracy = current_metrics.get("tool_call_accuracy", 0)
                    
                    # 檢查準確率是否下降
                    if hasattr(self, 'last_accuracy'):
                        accuracy_drop = self.last_accuracy - current_accuracy
                        if accuracy_drop > self.monitoring_config["alert_threshold"]["accuracy_drop"]:
                            await self.create_alert(
                                "ACCURACY_DROP",
                                f"準確率下降: {self.last_accuracy:.1f}% -> {current_accuracy:.1f}%",
                                "critical"
                            )
                    
                    self.last_accuracy = current_accuracy
                    
                    self.metrics["accuracy_metrics"] = {
                        "timestamp": datetime.now().isoformat(),
                        "current_accuracy": current_accuracy,
                        "memoryrag_impact": current_metrics.get("memoryrag_impact", 0),
                        "day1_achieved": current_metrics.get("day1_achieved", False),
                        "components_status": current_metrics.get("components", {})
                    }
                    
                    logger.info(f"📊 準確率監控: {current_accuracy:.1f}%")
                
            except Exception as e:
                logger.error(f"準確率監控錯誤: {str(e)}")
            
            await asyncio.sleep(self.monitoring_config["check_interval"])
    
    async def monitor_backup_status(self):
        """監控備份狀態"""
        while True:
            try:
                # 檢查本地備份
                backup_files = list(self.base_dir.glob("aicore_backup_*.tar.gz"))
                
                if backup_files:
                    latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
                    backup_age = datetime.now() - datetime.fromtimestamp(latest_backup.stat().st_mtime)
                    
                    self.metrics["backup_status"]["local"] = {
                        "latest_backup": latest_backup.name,
                        "backup_time": datetime.fromtimestamp(latest_backup.stat().st_mtime).isoformat(),
                        "backup_age_hours": backup_age.total_seconds() / 3600,
                        "backup_size_mb": latest_backup.stat().st_size / (1024**2)
                    }
                    
                    # 檢查備份年齡
                    if backup_age.total_seconds() / 3600 > self.monitoring_config["alert_threshold"]["backup_age"]:
                        await self.create_alert(
                            "OLD_BACKUP",
                            f"備份已超過{self.monitoring_config['alert_threshold']['backup_age']}小時",
                            "warning"
                        )
                else:
                    self.metrics["backup_status"]["local"] = {
                        "status": "no_backup_found",
                        "message": "未找到本地備份"
                    }
                    
                    await self.create_alert(
                        "NO_BACKUP",
                        "未找到任何備份文件",
                        "critical"
                    )
                
                # 檢查備份清單
                manifest_files = list(self.base_dir.glob("backup_manifest_*.json"))
                if manifest_files:
                    latest_manifest = max(manifest_files, key=lambda p: p.stat().st_mtime)
                    with open(latest_manifest, 'r') as f:
                        manifest = json.load(f)
                    
                    self.metrics["backup_status"]["manifest"] = {
                        "total_samples": manifest["statistics"]["total_training_samples"],
                        "replay_urls": manifest["statistics"]["total_replay_urls"],
                        "file_size_mb": manifest["file_size_mb"]
                    }
                
                logger.info(f"💾 備份監控: {len(backup_files)}個備份文件")
                
            except Exception as e:
                logger.error(f"備份監控錯誤: {str(e)}")
            
            await asyncio.sleep(self.monitoring_config["check_interval"])
    
    async def monitor_ec2_health(self):
        """監控EC2健康狀態"""
        while True:
            try:
                ec2_client = boto3.client('ec2', region_name=self.ec2_config["region"])
                
                # 檢查EC2實例狀態
                response = ec2_client.describe_instance_status(
                    InstanceIds=[self.ec2_config["instance_id"]]
                )
                
                if response['InstanceStatuses']:
                    status = response['InstanceStatuses'][0]
                    instance_state = status['InstanceState']['Name']
                    system_status = status['SystemStatus']['Status']
                    instance_status = status['InstanceStatus']['Status']
                    
                    self.metrics["ec2_status"] = {
                        "timestamp": datetime.now().isoformat(),
                        "instance_state": instance_state,
                        "system_status": system_status,
                        "instance_status": instance_status
                    }
                    
                    # 檢查異常狀態
                    if instance_state != "running":
                        await self.create_alert(
                            "EC2_NOT_RUNNING",
                            f"EC2實例狀態異常: {instance_state}",
                            "critical"
                        )
                    
                    if system_status != "ok" or instance_status != "ok":
                        await self.create_alert(
                            "EC2_HEALTH_CHECK_FAILED",
                            f"EC2健康檢查失敗: 系統{system_status}, 實例{instance_status}",
                            "warning"
                        )
                    
                    # 檢查EC2上的備份
                    await self.check_ec2_backups()
                    
                else:
                    self.metrics["ec2_status"] = {
                        "status": "instance_not_found",
                        "message": "EC2實例未找到"
                    }
                
                logger.info(f"☁️ EC2監控: 實例{instance_state}")
                
            except Exception as e:
                logger.error(f"EC2監控錯誤: {str(e)}")
                self.metrics["ec2_status"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            await asyncio.sleep(self.monitoring_config["check_interval"] * 2)  # EC2檢查頻率降低
    
    async def check_ec2_backups(self):
        """檢查EC2上的備份"""
        try:
            # SSH連接檢查備份
            ssh_cmd = [
                "ssh",
                "-i", "/Users/alexchuang/alexchuang.pem",
                f"ubuntu@{self.ec2_config['instance_id']}.compute.amazonaws.com",
                f"ls -la {self.ec2_config['backup_path']} | grep aicore_backup"
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                backup_lines = result.stdout.strip().split('\n')
                self.metrics["ec2_status"]["backup_count"] = len(backup_lines)
                logger.info(f"EC2備份數量: {len(backup_lines)}")
            
        except Exception as e:
            logger.error(f"EC2備份檢查錯誤: {str(e)}")
    
    async def get_gpu_usage(self) -> Optional[float]:
        """獲取GPU使用率"""
        try:
            # macOS Metal Performance Shaders
            result = subprocess.run(
                ["ioreg", "-l", "-w0", "|", "grep", "PerformanceStatistics"],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0 and result.stdout:
                # 簡單解析，實際需要更複雜的邏輯
                return 0.0  # 佔位符
            
        except Exception:
            pass
        
        return None
    
    async def create_alert(self, alert_type: str, message: str, severity: str = "info"):
        """創建警報"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": severity,
            "handled": False
        }
        
        self.metrics["alerts"].append(alert)
        
        # 記錄到日誌
        logger.warning(f"🚨 警報: [{severity.upper()}] {alert_type} - {message}")
        
        # 寫入警報日誌
        with open(self.alert_config["log_file"], 'a') as f:
            f.write(f"{json.dumps(alert)}\n")
    
    async def process_alerts(self):
        """處理警報"""
        while True:
            try:
                unhandled_alerts = [a for a in self.metrics["alerts"] if not a["handled"]]
                
                if unhandled_alerts:
                    # 批量發送警報
                    critical_alerts = [a for a in unhandled_alerts if a["severity"] == "critical"]
                    warning_alerts = [a for a in unhandled_alerts if a["severity"] == "warning"]
                    
                    if critical_alerts:
                        await self.send_alert_notification(critical_alerts, "critical")
                    
                    if warning_alerts and len(warning_alerts) >= 3:  # 累積3個警告才發送
                        await self.send_alert_notification(warning_alerts, "warning")
                    
                    # 標記為已處理
                    for alert in unhandled_alerts:
                        alert["handled"] = True
                
                # 清理舊警報（保留最近100條）
                if len(self.metrics["alerts"]) > 100:
                    self.metrics["alerts"] = self.metrics["alerts"][-100:]
                
            except Exception as e:
                logger.error(f"警報處理錯誤: {str(e)}")
            
            await asyncio.sleep(60)  # 每分鐘處理一次警報
    
    async def send_alert_notification(self, alerts: List[Dict], level: str):
        """發送警報通知"""
        # 發送Email
        if self.alert_config["email"]["enabled"]:
            await self.send_email_alert(alerts, level)
        
        # 發送Slack
        if self.alert_config["slack"]["enabled"]:
            await self.send_slack_alert(alerts, level)
    
    async def send_email_alert(self, alerts: List[Dict], level: str):
        """發送郵件警報"""
        try:
            subject = f"[AICore監控] {level.upper()} 警報 - {len(alerts)}條"
            
            body = f"AICore監控系統檢測到以下{level}級警報：\n\n"
            for alert in alerts:
                body += f"時間: {alert['timestamp']}\n"
                body += f"類型: {alert['type']}\n"
                body += f"消息: {alert['message']}\n"
                body += "-" * 50 + "\n"
            
            body += f"\n當前系統狀態:\n"
            body += f"準確率: {self.metrics.get('accuracy_metrics', {}).get('current_accuracy', 'N/A')}%\n"
            body += f"CPU: {self.metrics.get('system_health', {}).get('cpu_percent', 'N/A')}%\n"
            body += f"內存: {self.metrics.get('system_health', {}).get('memory_percent', 'N/A')}%\n"
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.alert_config["email"]["sender"]
            msg['To'] = ", ".join(self.alert_config["email"]["recipients"])
            
            # 發送郵件（需要配置SMTP）
            logger.info(f"📧 發送郵件警報: {subject}")
            
        except Exception as e:
            logger.error(f"郵件發送錯誤: {str(e)}")
    
    async def send_slack_alert(self, alerts: List[Dict], level: str):
        """發送Slack警報"""
        try:
            # 構建Slack消息
            color = "#ff0000" if level == "critical" else "#ffaa00"
            
            slack_message = {
                "attachments": [{
                    "color": color,
                    "title": f"AICore {level.upper()} 警報",
                    "fields": [
                        {
                            "title": alert["type"],
                            "value": alert["message"],
                            "short": False
                        } for alert in alerts
                    ],
                    "footer": "AICore監控系統",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            # 發送到Slack（需要webhook URL）
            logger.info(f"💬 發送Slack警報: {len(alerts)}條{level}警報")
            
        except Exception as e:
            logger.error(f"Slack發送錯誤: {str(e)}")
    
    def generate_monitoring_dashboard(self) -> str:
        """生成監控儀表板"""
        dashboard = f"""
# AICore監控運維儀表板

更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🖥️ 系統健康
- CPU使用率: {self.metrics.get('system_health', {}).get('cpu_percent', 'N/A')}%
- 內存使用率: {self.metrics.get('system_health', {}).get('memory_percent', 'N/A')}%
- 磁盤使用率: {self.metrics.get('system_health', {}).get('disk_percent', 'N/A')}%
- Claude進程數: {self.metrics.get('system_health', {}).get('claude_processes', 'N/A')}

## 📊 準確率指標
- 當前準確率: {self.metrics.get('accuracy_metrics', {}).get('current_accuracy', 'N/A')}%
- MemoryRAG提升: {self.metrics.get('accuracy_metrics', {}).get('memoryrag_impact', 'N/A')}%
- Day 1目標達成: {self.metrics.get('accuracy_metrics', {}).get('day1_achieved', 'N/A')}

## 🏃 訓練狀態
- 運行狀態: {'運行中' if self.metrics.get('training_status', {}).get('is_running', False) else '已停止'}
- 目標達成率: {self.metrics.get('training_status', {}).get('achievement_rate', 'N/A')}%
- 訓練周期: {self.metrics.get('training_status', {}).get('training_cycle', 'N/A')}

## 💾 備份狀態
- 最新備份: {self.metrics.get('backup_status', {}).get('local', {}).get('latest_backup', 'N/A')}
- 備份年齡: {self.metrics.get('backup_status', {}).get('local', {}).get('backup_age_hours', 'N/A'):.1f}小時
- 訓練樣本數: {self.metrics.get('backup_status', {}).get('manifest', {}).get('total_samples', 'N/A')}

## ☁️ EC2狀態
- 實例狀態: {self.metrics.get('ec2_status', {}).get('instance_state', 'N/A')}
- 系統檢查: {self.metrics.get('ec2_status', {}).get('system_status', 'N/A')}
- EC2備份數: {self.metrics.get('ec2_status', {}).get('backup_count', 'N/A')}

## 🚨 最近警報
"""
        
        recent_alerts = self.metrics.get("alerts", [])[-5:]
        if recent_alerts:
            for alert in recent_alerts:
                dashboard += f"- [{alert['severity'].upper()}] {alert['type']}: {alert['message']}\n"
        else:
            dashboard += "- 無警報\n"
        
        return dashboard
    
    async def save_monitoring_report(self):
        """保存監控報告"""
        while True:
            try:
                # 生成儀表板
                dashboard = self.generate_monitoring_dashboard()
                
                # 保存到文件
                report_path = self.base_dir / "monitoring_dashboard.md"
                with open(report_path, 'w') as f:
                    f.write(dashboard)
                
                # 保存指標JSON
                metrics_path = self.base_dir / "monitoring_metrics.json"
                with open(metrics_path, 'w') as f:
                    json.dump(self.metrics, f, indent=2)
                
                logger.info("📊 監控報告已更新")
                
            except Exception as e:
                logger.error(f"保存監控報告錯誤: {str(e)}")
            
            await asyncio.sleep(300)  # 每5分鐘保存一次


async def main():
    """主函數"""
    monitor = MonitoringOperationsMCP()
    
    logger.info("🎯 AICore監控運維MCP啟動")
    logger.info("監控內容:")
    logger.info("  - 系統健康狀態")
    logger.info("  - 訓練進度")
    logger.info("  - 準確率指標")
    logger.info("  - 備份狀態")
    logger.info("  - EC2健康")
    logger.info("  - 警報處理")
    
    # 添加報告保存任務
    tasks = [
        monitor.start_monitoring(),
        monitor.save_monitoring_report()
    ]
    
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())