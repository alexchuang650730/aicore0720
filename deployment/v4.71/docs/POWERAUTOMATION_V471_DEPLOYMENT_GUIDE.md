# PowerAutomation v4.71 Memory RAG Edition 部署指南

## 📋 **部署概览**

PowerAutomation v4.71 Memory RAG Edition 提供多种部署方式，适合不同的使用场景和环境需求。

### **部署方式对比**

| 部署方式 | 适用场景 | 复杂度 | 性能 | 可扩展性 |
|----------|----------|--------|------|----------|
| 一键安装 | 个人开发、快速体验 | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| 手动安装 | 自定义配置、企业环境 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 容器部署 | 云端部署、微服务架构 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 集群部署 | 高可用、大规模生产 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚀 **一键安装部署**

### **系统要求**
- **操作系统**: macOS 10.15+ 或 Linux (Ubuntu 18.04+, CentOS 7+)
- **Python**: 3.8 或更高版本
- **内存**: 最少 4GB，推荐 8GB+
- **存储**: 最少 2GB 可用空间
- **网络**: 稳定的互联网连接

### **安装命令**
```bash
# 一键安装
curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/deployment/v4.71/scripts/one_click_install_memory_rag.sh | bash
```

### **安装过程**
1. **依赖检查** - 自动检查 Python、pip、git
2. **环境创建** - 创建虚拟环境（macOS）或系统安装（Linux）
3. **代码下载** - 从 GitHub 克隆最新代码
4. **依赖安装** - 安装所有 Python 依赖包
5. **配置生成** - 生成默认配置文件
6. **服务配置** - 创建启动脚本和命令
7. **环境配置** - 配置环境变量和 PATH
8. **功能测试** - 验证安装是否成功

### **安装后配置**
```bash
# 重新加载 shell 配置
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS

# 配置 HuggingFace Token
export HF_TOKEN="your_huggingface_token"

# 启动服务
powerautomation start

# 验证安装
powerautomation status
powerautomation test
```

---

## 🔧 **手动安装部署**

### **详细安装步骤**

#### **1. 环境准备**
```bash
# 检查 Python 版本
python3 --version  # 需要 3.8+

# 创建安装目录
mkdir -p ~/.powerautomation
cd ~/.powerautomation

# 创建虚拟环境
python3 -m venv powerautomation_env
source powerautomation_env/bin/activate

# 升级 pip
pip install --upgrade pip
```

#### **2. 下载源码**
```bash
# 克隆仓库
git clone https://github.com/alexchuang650730/aicore0716.git
cd aicore0716

# 检出特定版本（可选）
git checkout v4.71-memory-rag
```

#### **3. 安装依赖**
```bash
# 安装核心依赖
pip install sentence-transformers faiss-cpu huggingface-hub

# 安装 Web 服务依赖
pip install aiohttp websockets aiofiles

# 安装数据处理依赖
pip install numpy pandas scikit-learn

# 安装 AWS 依赖（可选）
pip install boto3

# 安装其他依赖
pip install requests beautifulsoup4 lxml
```

#### **4. 配置文件**
```bash
# 创建配置目录
mkdir -p ~/.powerautomation/config

# 创建主配置文件
cat > ~/.powerautomation/config/memory_rag_config.json << 'EOF'
{
    "memory_rag": {
        "enabled": true,
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_store": "faiss",
        "max_documents": 10000,
        "chunk_size": 512,
        "chunk_overlap": 50
    },
    "providers": {
        "groq": {
            "enabled": true,
            "priority": 1,
            "max_tps": 120,
            "max_latency": 0.5
        },
        "together": {
            "enabled": true,
            "priority": 2,
            "max_tps": 100,
            "max_latency": 1.0
        },
        "novita": {
            "enabled": true,
            "priority": 3,
            "max_tps": 80,
            "max_latency": 1.5
        }
    },
    "modes": {
        "teacher_mode": {
            "enabled": true,
            "detail_level": "high",
            "code_review": true
        },
        "assistant_mode": {
            "enabled": true,
            "detail_level": "medium",
            "efficiency_focus": true
        }
    },
    "aws_s3": {
        "enabled": false,
        "bucket": "",
        "region": "us-east-1"
    },
    "logging": {
        "level": "INFO",
        "file": "~/.powerautomation/logs/memory_rag.log",
        "max_size": "100MB",
        "backup_count": 5
    }
}
EOF

# 创建环境变量文件
cat > ~/.powerautomation/config/env.sh << 'EOF'
#!/bin/bash
# PowerAutomation v4.71 Memory RAG Edition 环境变量

# 必需配置
export HF_TOKEN="${HF_TOKEN:-demo-token}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"

# 版本信息
export POWERAUTOMATION_VERSION="4.71"
export POWERAUTOMATION_EDITION="Memory RAG Edition"

# 路径配置
export PYTHONPATH="$HOME/.powerautomation/aicore0716:$PYTHONPATH"
export MEMORY_RAG_CONFIG="$HOME/.powerautomation/config/memory_rag_config.json"
export MEMORY_RAG_DATA_DIR="$HOME/.powerautomation/data"
export MEMORY_RAG_LOGS_DIR="$HOME/.powerautomation/logs"

# 创建必要目录
mkdir -p "$MEMORY_RAG_DATA_DIR"
mkdir -p "$MEMORY_RAG_LOGS_DIR"

# 性能配置
export MEMORY_RAG_MAX_WORKERS="4"
export MEMORY_RAG_CACHE_SIZE="1000"
export MEMORY_RAG_BATCH_SIZE="32"
EOF
```

#### **5. 启动脚本**
```bash
# 创建启动脚本
cat > ~/.powerautomation/start_memory_rag.sh << 'EOF'
#!/bin/bash

# 激活虚拟环境
source "$HOME/.powerautomation/powerautomation_env/bin/activate"

# 加载环境变量
source "$HOME/.powerautomation/config/env.sh"

# 切换到工作目录
cd "$HOME/.powerautomation/aicore0716"

# 检查端口占用
if lsof -i :8080 &>/dev/null; then
    echo "⚠️ 端口 8080 已被占用，正在停止现有服务..."
    kill -9 $(lsof -ti:8080) 2>/dev/null || true
    sleep 2
fi

echo "🧠 启动 PowerAutomation v4.71 Memory RAG Edition..."
echo "📍 监听地址: http://127.0.0.1:8080"
echo ""

# 启动服务
python3 -m core.components.unified_memory_rag_interface_v2
EOF

chmod +x ~/.powerautomation/start_memory_rag.sh

# 创建主命令
cat > ~/.powerautomation/powerautomation << 'EOF'
#!/bin/bash
# PowerAutomation v4.71 Memory RAG Edition 主命令

INSTALL_DIR="$HOME/.powerautomation"

# 激活虚拟环境
if [ -f "$INSTALL_DIR/powerautomation_env/bin/activate" ]; then
    source "$INSTALL_DIR/powerautomation_env/bin/activate"
fi

# 加载环境变量
if [ -f "$INSTALL_DIR/config/env.sh" ]; then
    source "$INSTALL_DIR/config/env.sh"
fi

case "$1" in
    start)
        exec "$INSTALL_DIR/start_memory_rag.sh"
        ;;
    stop)
        pkill -f "unified_memory_rag_interface" || true
        if lsof -i :8080 &>/dev/null; then
            kill -9 $(lsof -ti:8080) 2>/dev/null || true
        fi
        echo "✅ 服务已停止"
        ;;
    status)
        if lsof -i :8080 &>/dev/null; then
            echo "✅ Memory RAG 服务正在运行"
            curl -s http://127.0.0.1:8080/health | python3 -m json.tool
        else
            echo "❌ Memory RAG 服务未运行"
        fi
        ;;
    *)
        echo "使用方法: powerautomation {start|stop|status}"
        ;;
esac
EOF

chmod +x ~/.powerautomation/powerautomation

# 添加到 PATH
echo 'export PATH="$HOME/.powerautomation:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🐳 **容器化部署**

### **Dockerfile**
```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制源码
COPY . /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir \
    sentence-transformers \
    faiss-cpu \
    huggingface-hub \
    aiohttp \
    websockets \
    aiofiles \
    numpy \
    pandas \
    scikit-learn \
    boto3 \
    requests \
    beautifulsoup4 \
    lxml

# 创建数据目录
RUN mkdir -p /app/data /app/logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV MEMORY_RAG_DATA_DIR=/app/data
ENV MEMORY_RAG_LOGS_DIR=/app/logs

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python3", "-m", "core.components.unified_memory_rag_interface_v2"]
```

### **Docker Compose**
```yaml
version: '3.8'

services:
  memory-rag:
    build: .
    ports:
      - "8080:8080"
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - memory-rag
    restart: unless-stopped

volumes:
  data:
  logs:
```

### **部署命令**
```bash
# 构建镜像
docker build -t powerautomation-memory-rag:v4.71 .

# 运行容器
docker run -d \
  --name memory-rag \
  -p 8080:8080 \
  -e HF_TOKEN="your_token" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  powerautomation-memory-rag:v4.71

# 使用 Docker Compose
docker-compose up -d

# 查看日志
docker logs -f memory-rag

# 健康检查
curl http://localhost:8080/health
```

---

## ☁️ **云端部署**

### **AWS 部署**

#### **EC2 部署**
```bash
# 创建 EC2 实例
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx \
  --user-data file://user-data.sh

# user-data.sh 内容
#!/bin/bash
yum update -y
yum install -y python3 python3-pip git
curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/deployment/v4.71/scripts/one_click_install_memory_rag.sh | bash
```

#### **ECS 部署**
```json
{
  "family": "powerautomation-memory-rag",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "memory-rag",
      "image": "your-account.dkr.ecr.region.amazonaws.com/powerautomation-memory-rag:v4.71",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "HF_TOKEN",
          "value": "your_token"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/powerautomation-memory-rag",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### **Google Cloud 部署**

#### **Cloud Run 部署**
```bash
# 构建并推送镜像
gcloud builds submit --tag gcr.io/your-project/powerautomation-memory-rag:v4.71

# 部署到 Cloud Run
gcloud run deploy memory-rag \
  --image gcr.io/your-project/powerautomation-memory-rag:v4.71 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars HF_TOKEN=your_token \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10
```

### **Azure 部署**

#### **Container Instances 部署**
```bash
# 创建资源组
az group create --name powerautomation-rg --location eastus

# 部署容器实例
az container create \
  --resource-group powerautomation-rg \
  --name memory-rag \
  --image your-registry.azurecr.io/powerautomation-memory-rag:v4.71 \
  --cpu 1 \
  --memory 2 \
  --ports 8080 \
  --environment-variables HF_TOKEN=your_token \
  --restart-policy Always
```

---

## 🔧 **高级配置**

### **性能调优**

#### **内存优化**
```json
{
  "memory_rag": {
    "vector_cache_size": 5000,
    "query_cache_size": 2000,
    "batch_size": 64,
    "max_workers": 8
  },
  "faiss": {
    "index_type": "IndexFlatIP",
    "nprobe": 10,
    "use_gpu": false
  }
}
```

#### **并发优化**
```json
{
  "server": {
    "max_connections": 1000,
    "keepalive_timeout": 30,
    "request_timeout": 60,
    "worker_processes": 4
  },
  "providers": {
    "max_concurrent_requests": 50,
    "request_timeout": 30,
    "retry_attempts": 3,
    "circuit_breaker_threshold": 5
  }
}
```

### **安全配置**

#### **API 安全**
```json
{
  "security": {
    "api_key_required": true,
    "rate_limiting": {
      "requests_per_minute": 100,
      "burst_size": 20
    },
    "cors": {
      "allowed_origins": ["https://your-domain.com"],
      "allowed_methods": ["GET", "POST"],
      "allowed_headers": ["Content-Type", "Authorization"]
    }
  }
}
```

#### **数据加密**
```json
{
  "encryption": {
    "data_at_rest": true,
    "encryption_key": "your-encryption-key",
    "algorithm": "AES-256-GCM"
  },
  "ssl": {
    "enabled": true,
    "cert_file": "/path/to/cert.pem",
    "key_file": "/path/to/key.pem"
  }
}
```

### **监控配置**

#### **Prometheus 监控**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'memory-rag'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

#### **日志配置**
```json
{
  "logging": {
    "level": "INFO",
    "format": "json",
    "handlers": {
      "file": {
        "filename": "/app/logs/memory_rag.log",
        "max_size": "100MB",
        "backup_count": 10,
        "rotation": "daily"
      },
      "elasticsearch": {
        "enabled": false,
        "host": "localhost:9200",
        "index": "memory-rag-logs"
      }
    }
  }
}
```

---

## 🔍 **故障排除**

### **常见部署问题**

#### **1. 依赖安装失败**
```bash
# 问题：pip 安装失败
# 解决：升级 pip 和使用国内镜像
pip install --upgrade pip
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ sentence-transformers

# 问题：FAISS 安装失败
# 解决：使用 conda 安装
conda install -c conda-forge faiss-cpu
```

#### **2. 端口占用问题**
```bash
# 查看端口占用
lsof -i :8080
netstat -tulpn | grep 8080

# 杀死占用进程
kill -9 $(lsof -ti:8080)

# 使用其他端口
export MEMORY_RAG_PORT=8081
```

#### **3. 内存不足问题**
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 优化配置
export MEMORY_RAG_BATCH_SIZE=16
export MEMORY_RAG_MAX_WORKERS=2
```

#### **4. 网络连接问题**
```bash
# 测试 HuggingFace 连接
curl -H "Authorization: Bearer $HF_TOKEN" \
  https://huggingface.co/api/whoami

# 测试 Provider 连接
python3 -c "
from huggingface_hub import InferenceClient
client = InferenceClient(provider='groq', api_key='$HF_TOKEN')
print('连接成功')
"
```

### **性能问题诊断**

#### **1. 响应时间过长**
```bash
# 检查 Provider 性能
curl -w "@curl-format.txt" -s -o /dev/null \
  -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# curl-format.txt 内容
time_namelookup:  %{time_namelookup}\n
time_connect:     %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer: %{time_pretransfer}\n
time_redirect:    %{time_redirect}\n
time_starttransfer: %{time_starttransfer}\n
time_total:       %{time_total}\n
```

#### **2. 内存泄漏检查**
```bash
# 监控内存使用
while true; do
  ps aux | grep memory_rag | grep -v grep
  sleep 60
done

# 使用 memory_profiler
pip install memory_profiler
python3 -m memory_profiler your_script.py
```

### **日志分析**

#### **查看关键日志**
```bash
# 查看启动日志
tail -f ~/.powerautomation/logs/memory_rag.log

# 查看错误日志
grep ERROR ~/.powerautomation/logs/memory_rag.log

# 查看性能日志
grep "response_time" ~/.powerautomation/logs/memory_rag.log
```

#### **日志级别调整**
```bash
# 临时调整日志级别
export MEMORY_RAG_LOG_LEVEL=DEBUG

# 永久调整（修改配置文件）
sed -i 's/"level": "INFO"/"level": "DEBUG"/' \
  ~/.powerautomation/config/memory_rag_config.json
```

---

## 📊 **部署验证**

### **功能测试**
```bash
# 健康检查
curl http://localhost:8080/health

# 基本查询测试
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何使用 Python 创建 FastAPI 应用？",
    "context": {"current_tool": "assistant_mode"},
    "top_k": 5
  }'

# 文档添加测试
curl -X POST http://localhost:8080/add_document \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "test_doc",
    "content": "这是一个测试文档",
    "metadata": {"type": "test"}
  }'
```

### **性能测试**
```bash
# 使用 ab 进行压力测试
ab -n 1000 -c 10 -T application/json \
  -p query.json http://localhost:8080/query

# query.json 内容
{"query": "test query", "top_k": 5}

# 使用 wrk 进行性能测试
wrk -t12 -c400 -d30s --script=post.lua http://localhost:8080/query
```

### **监控验证**
```bash
# 检查系统资源使用
htop
iotop
nethogs

# 检查服务状态
systemctl status powerautomation  # 如果使用 systemd
docker stats memory-rag           # 如果使用 Docker
```

---

## 🎯 **生产环境建议**

### **高可用部署**
1. **负载均衡**: 使用 Nginx 或 HAProxy 进行负载均衡
2. **多实例**: 部署多个 Memory RAG 实例
3. **健康检查**: 配置自动健康检查和故障转移
4. **数据备份**: 定期备份向量索引和配置文件

### **安全加固**
1. **网络安全**: 使用防火墙限制访问端口
2. **API 安全**: 启用 API 密钥认证和速率限制
3. **数据加密**: 启用数据传输和存储加密
4. **访问控制**: 配置适当的用户权限和访问控制

### **监控告警**
1. **性能监控**: 监控响应时间、TPS、错误率
2. **资源监控**: 监控 CPU、内存、磁盘使用率
3. **业务监控**: 监控查询成功率、Provider 状态
4. **告警配置**: 配置关键指标的告警阈值

### **运维自动化**
1. **自动部署**: 使用 CI/CD 管道自动部署
2. **自动扩缩容**: 根据负载自动调整实例数量
3. **自动备份**: 定期自动备份重要数据
4. **自动恢复**: 配置服务自动重启和故障恢复

---

**PowerAutomation v4.71 Memory RAG Edition 部署指南完成！** 🚀

如有任何部署问题，请参考故障排除部分或联系技术支持。

