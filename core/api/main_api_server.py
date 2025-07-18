#!/usr/bin/env python3
"""
主 API 服務器
整合所有 API 端點，包括 MCP-Zero、CodeFlow 等
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from datetime import datetime

# 導入各個 API 路由
from .mcp_zero_api import router as mcp_zero_router
from .codeflow_api_endpoints import router as codeflow_router
from ...api.workflows_integration_api import router as workflows_router

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="PowerAutomation API Server",
    description="整合 MCP-Zero 動態加載架構的 API 服務",
    version="4.73"
)

# CORS 設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應該限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(mcp_zero_router, prefix="/api/mcpzero", tags=["MCP-Zero"])
app.include_router(codeflow_router, prefix="/api/codeflow", tags=["CodeFlow"])
app.include_router(workflows_router, tags=["Workflows Integration"])

# 靜態文件服務（如果需要）
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 健康檢查端點
@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "4.73",
        "features": {
            "mcp_zero": True,
            "codeflow": True,
            "k2_integration": True
        }
    }

# 根路徑
@app.get("/", response_class=HTMLResponse)
async def root():
    """根路徑 - 返回 API 文檔鏈接"""
    return """
    <html>
        <head>
            <title>PowerAutomation API Server</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #1890ff;
                }
                .feature {
                    margin: 10px 0;
                    padding: 10px;
                    background: #e6f7ff;
                    border-radius: 4px;
                }
                a {
                    color: #1890ff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 PowerAutomation API Server v4.73</h1>
                
                <h2>核心功能</h2>
                <div class="feature">
                    <strong>MCP-Zero 動態加載：</strong>節省 80% 上下文，提升 5 倍性能
                </div>
                <div class="feature">
                    <strong>六大工作流：</strong>需求分析、架構設計、編碼實現、測試驗證、部署發布、監控運維
                </div>
                <div class="feature">
                    <strong>K2 模型集成：</strong>成本節省 60-80%，提供近似 Claude 體驗
                </div>
                
                <h2>API 文檔</h2>
                <ul>
                    <li><a href="/docs">交互式 API 文檔 (Swagger UI)</a></li>
                    <li><a href="/redoc">API 文檔 (ReDoc)</a></li>
                </ul>
                
                <h2>主要端點</h2>
                <ul>
                    <li><code>POST /api/mcpzero/execute</code> - 執行 MCP-Zero 任務</li>
                    <li><code>GET /api/mcpzero/mcps</code> - 列出所有可用 MCP</li>
                    <li><code>POST /api/codeflow/generate</code> - 生成代碼</li>
                    <li><code>POST /api/codeflow/code-to-spec</code> - 代碼轉規格</li>
                    <li><code>WS /api/mcpzero/ws/{client_id}</code> - WebSocket 實時通信</li>
                </ul>
                
                <h2>狀態</h2>
                <p>服務器運行正常 ✅</p>
                <p>當前時間：<span id="time"></span></p>
            </div>
            
            <script>
                document.getElementById('time').textContent = new Date().toLocaleString();
                setInterval(() => {
                    document.getElementById('time').textContent = new Date().toLocaleString();
                }, 1000);
            </script>
        </body>
    </html>
    """

# 錯誤處理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局異常: {str(exc)}", exc_info=True)
    return {
        "error": "內部服務器錯誤",
        "message": str(exc),
        "path": request.url.path
    }

# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動時執行"""
    logger.info("PowerAutomation API Server 啟動")
    logger.info("MCP-Zero 動態加載架構已啟用")
    
    # 初始化 MCP 註冊表
    from ..mcp_zero import mcp_registry
    logger.info(f"已註冊 {len(mcp_registry.mcp_catalog)} 個 MCP")
    
    # 預加載 P0 級別的 MCP（可選）
    p0_mcps = [name for name, meta in mcp_registry.mcp_catalog.items() if meta.priority == "P0"]
    logger.info(f"P0 核心 MCP: {p0_mcps}")

# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時執行"""
    logger.info("PowerAutomation API Server 關閉")
    
    # 清理資源
    from ..mcp_zero import mcp_registry
    loaded_mcps = await mcp_registry.get_loaded_mcps()
    for mcp in loaded_mcps:
        await mcp_registry.unload_mcp(mcp)
    
    logger.info("所有 MCP 已卸載")


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """運行服務器"""
    uvicorn.run(
        "core.api.main_api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    # 直接運行
    run_server(reload=True)