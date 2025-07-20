FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製requirements文件
COPY requirements.txt .

# 安裝Python依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建數據和日誌目錄
RUN mkdir -p data logs

# 設置環境變量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py

# 暴露端口
EXPOSE 5000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/subscription/plans || exit 1

# 啟動命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]