# PowerAutomation Docker 鏡像
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    sqlite3 \
    supervisor \
    nginx \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# 複製依賴文件
COPY requirements.txt .
COPY claudeditor/package.json claudeditor/package-lock.json ./claudeditor/

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 Node.js 依賴
RUN cd claudeditor && npm install

# 複製應用代碼
COPY . .

# 構建前端
RUN cd claudeditor && npm run build

# 創建必要目錄
RUN mkdir -p logs data uploads downloads temp

# 設置權限
RUN chmod +x deploy/docker-entrypoint.sh

# 創建非root用戶
RUN useradd -m -s /bin/bash powerautomation
RUN chown -R powerautomation:powerautomation /app

# 切換到非root用戶
USER powerautomation

# 暴露端口
EXPOSE 8000 8001 8765 5173

# 設置環境變量
ENV PYTHONPATH=/app:/app/core:/app/mcp_server:/app/goal_alignment_system
ENV POWERAUTOMATION_ROOT=/app

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 入口點
ENTRYPOINT ["./deploy/docker-entrypoint.sh"]