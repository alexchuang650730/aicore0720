"""
AWS Bedrock Manager - PowerAutomation v4.8

负责 AWS 服务的管理和配置，包括:
- S3 存储桶管理
- IAM 权限配置
- 成本监控和追踪
- 服务健康检查

设计原则:
- 仅使用 AWS S3 进行 RAG 存储，不使用 Bedrock LLM
- 与 Kimi K2 配合实现零余额消耗
- 企业级安全和可靠性
"""

import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError, NoCredentialsError

class BedrockManager:
    """AWS Bedrock 服务管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化 Bedrock 管理器
        
        Args:
            config: 配置字典，包含 AWS 区域、S3 桶名等
        """
        self.config = config or {}
        self.aws_region = self.config.get("aws_region", "us-east-1")
        self.s3_bucket = self.config.get("s3_bucket", "powerautomation-rag-storage")
        
        # 初始化 AWS 客户端
        try:
            self.s3_client = boto3.client('s3', region_name=self.aws_region)
            self.iam_client = boto3.client('iam', region_name=self.aws_region)
            self.cloudwatch_client = boto3.client('cloudwatch', region_name=self.aws_region)
        except NoCredentialsError:
            logging.error("AWS 凭证未配置，请设置 AWS_ACCESS_KEY_ID 和 AWS_SECRET_ACCESS_KEY")
            raise
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 成本追踪
        self.cost_tracker = {
            "s3_storage_gb": 0,
            "s3_requests": 0,
            "monthly_cost": 0.0,
            "last_updated": datetime.now()
        }
    
    async def initialize_infrastructure(self) -> Dict[str, Any]:
        """
        初始化 AWS 基础设施
        
        Returns:
            初始化结果和状态信息
        """
        try:
            # 1. 创建 S3 存储桶
            bucket_result = await self._create_s3_bucket()
            
            # 2. 配置 IAM 权限
            iam_result = await self._setup_iam_permissions()
            
            # 3. 设置监控
            monitoring_result = await self._setup_monitoring()
            
            result = {
                "status": "success",
                "s3_bucket": bucket_result,
                "iam_permissions": iam_result,
                "monitoring": monitoring_result,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"AWS 基础设施初始化完成: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"AWS 基础设施初始化失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _create_s3_bucket(self) -> Dict[str, Any]:
        """创建 S3 存储桶用于 RAG 数据存储"""
        try:
            # 检查桶是否已存在
            try:
                self.s3_client.head_bucket(Bucket=self.s3_bucket)
                return {
                    "status": "exists",
                    "bucket_name": self.s3_bucket,
                    "message": "S3 存储桶已存在"
                }
            except ClientError as e:
                if e.response['Error']['Code'] != '404':
                    raise
            
            # 创建新桶
            if self.aws_region == 'us-east-1':
                # us-east-1 不需要 LocationConstraint
                self.s3_client.create_bucket(Bucket=self.s3_bucket)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.s3_bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.aws_region}
                )
            
            # 配置桶策略和加密
            await self._configure_bucket_security()
            
            return {
                "status": "created",
                "bucket_name": self.s3_bucket,
                "region": self.aws_region,
                "message": "S3 存储桶创建成功"
            }
            
        except Exception as e:
            self.logger.error(f"S3 存储桶创建失败: {str(e)}")
            raise
    
    async def _configure_bucket_security(self):
        """配置 S3 存储桶安全策略"""
        try:
            # 启用服务器端加密
            encryption_config = {
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }
                ]
            }
            
            self.s3_client.put_bucket_encryption(
                Bucket=self.s3_bucket,
                ServerSideEncryptionConfiguration=encryption_config
            )
            
            # 阻止公共访问
            public_access_block = {
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
            
            self.s3_client.put_public_access_block(
                Bucket=self.s3_bucket,
                PublicAccessBlockConfiguration=public_access_block
            )
            
            self.logger.info(f"S3 存储桶安全配置完成: {self.s3_bucket}")
            
        except Exception as e:
            self.logger.error(f"S3 安全配置失败: {str(e)}")
            raise
    
    async def _setup_iam_permissions(self) -> Dict[str, Any]:
        """设置 IAM 权限和角色"""
        try:
            # 创建 PowerAutomation 服务角色
            role_name = "PowerAutomationRAGRole"
            
            # 信任策略
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            # 权限策略
            permissions_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:DeleteObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{self.s3_bucket}",
                            f"arn:aws:s3:::{self.s3_bucket}/*"
                        ]
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "cloudwatch:PutMetricData",
                            "cloudwatch:GetMetricStatistics"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            
            try:
                # 创建角色
                self.iam_client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description="PowerAutomation RAG 服务角色"
                )
                
                # 附加权限策略
                self.iam_client.put_role_policy(
                    RoleName=role_name,
                    PolicyName="PowerAutomationRAGPolicy",
                    PolicyDocument=json.dumps(permissions_policy)
                )
                
                return {
                    "status": "created",
                    "role_name": role_name,
                    "message": "IAM 角色和权限创建成功"
                }
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'EntityAlreadyExists':
                    return {
                        "status": "exists",
                        "role_name": role_name,
                        "message": "IAM 角色已存在"
                    }
                else:
                    raise
                    
        except Exception as e:
            self.logger.error(f"IAM 权限设置失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _setup_monitoring(self) -> Dict[str, Any]:
        """设置 CloudWatch 监控"""
        try:
            # 创建自定义指标
            metrics = [
                "PowerAutomation/RAG/RequestCount",
                "PowerAutomation/RAG/ResponseTime",
                "PowerAutomation/RAG/StorageUsage",
                "PowerAutomation/RAG/CostTracking"
            ]
            
            for metric in metrics:
                self.cloudwatch_client.put_metric_data(
                    Namespace=metric.split('/')[0],
                    MetricData=[
                        {
                            'MetricName': metric.split('/')[-1],
                            'Value': 0,
                            'Unit': 'Count',
                            'Timestamp': datetime.now()
                        }
                    ]
                )
            
            return {
                "status": "configured",
                "metrics": metrics,
                "message": "CloudWatch 监控配置完成"
            }
            
        except Exception as e:
            self.logger.error(f"监控设置失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def upload_rag_data(self, data: bytes, key: str, metadata: Dict[str, str] = None) -> Dict[str, Any]:
        """
        上传 RAG 数据到 S3
        
        Args:
            data: 要上传的数据
            key: S3 对象键
            metadata: 可选的元数据
            
        Returns:
            上传结果
        """
        try:
            # 准备上传参数
            upload_args = {
                'Bucket': self.s3_bucket,
                'Key': key,
                'Body': data,
                'ServerSideEncryption': 'AES256'
            }
            
            if metadata:
                upload_args['Metadata'] = metadata
            
            # 执行上传
            self.s3_client.put_object(**upload_args)
            
            # 更新成本追踪
            await self._update_cost_tracking('upload', len(data))
            
            result = {
                "status": "success",
                "bucket": self.s3_bucket,
                "key": key,
                "size_bytes": len(data),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"RAG 数据上传成功: {key}")
            return result
            
        except Exception as e:
            self.logger.error(f"RAG 数据上传失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "key": key
            }
    
    async def download_rag_data(self, key: str) -> Dict[str, Any]:
        """
        从 S3 下载 RAG 数据
        
        Args:
            key: S3 对象键
            
        Returns:
            下载的数据和元信息
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=key
            )
            
            data = response['Body'].read()
            
            # 更新成本追踪
            await self._update_cost_tracking('download', len(data))
            
            result = {
                "status": "success",
                "data": data,
                "metadata": response.get('Metadata', {}),
                "size_bytes": len(data),
                "last_modified": response['LastModified'].isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"RAG 数据下载成功: {key}")
            return result
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return {
                    "status": "not_found",
                    "error": f"对象不存在: {key}"
                }
            else:
                self.logger.error(f"RAG 数据下载失败: {str(e)}")
                return {
                    "status": "error",
                    "error": str(e),
                    "key": key
                }
    
    async def _update_cost_tracking(self, operation: str, data_size: int):
        """更新成本追踪信息"""
        try:
            # 更新请求计数
            self.cost_tracker["s3_requests"] += 1
            
            # 更新存储大小 (仅对上传操作)
            if operation == "upload":
                self.cost_tracker["s3_storage_gb"] += data_size / (1024 * 1024 * 1024)
            
            # 计算月度成本
            storage_cost = self.cost_tracker["s3_storage_gb"] * 0.023  # $0.023 per GB
            request_cost = self.cost_tracker["s3_requests"] * 0.0004  # $0.0004 per 1000 requests
            
            self.cost_tracker["monthly_cost"] = storage_cost + request_cost
            self.cost_tracker["last_updated"] = datetime.now()
            
            # 发送到 CloudWatch
            self.cloudwatch_client.put_metric_data(
                Namespace='PowerAutomation/RAG',
                MetricData=[
                    {
                        'MetricName': 'CostTracking',
                        'Value': self.cost_tracker["monthly_cost"],
                        'Unit': 'None',
                        'Timestamp': datetime.now()
                    }
                ]
            )
            
        except Exception as e:
            self.logger.error(f"成本追踪更新失败: {str(e)}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        try:
            # 检查 S3 连接
            s3_status = "healthy"
            try:
                self.s3_client.head_bucket(Bucket=self.s3_bucket)
            except Exception:
                s3_status = "unhealthy"
            
            # 检查 IAM 权限
            iam_status = "healthy"
            try:
                self.iam_client.get_role(RoleName="PowerAutomationRAGRole")
            except Exception:
                iam_status = "unhealthy"
            
            # 获取成本信息
            cost_info = self.cost_tracker.copy()
            
            return {
                "status": "healthy" if s3_status == "healthy" and iam_status == "healthy" else "degraded",
                "services": {
                    "s3": s3_status,
                    "iam": iam_status
                },
                "cost_tracking": cost_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

