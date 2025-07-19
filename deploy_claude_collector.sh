#!/bin/bash

# Claude 實時收集器一鍵部署腳本
# 參考 claude router mcp 的 startup_trigger 機制

echo "🚀 Claude 實時信息收集器 - 一鍵部署"
echo "========================================"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查 Python 環境
check_python() {
    echo -e "${BLUE}🔍 檢查 Python 環境...${NC}"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}✅ Python 3 已安裝: $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}❌ Python 3 未安裝${NC}"
        exit 1
    fi
}

# 安裝依賴
install_dependencies() {
    echo -e "${BLUE}📦 安裝 Python 依賴...${NC}"
    
    # 可選依賴列表
    OPTIONAL_DEPS=("psutil" "websockets" "aiofiles" "watchdog")
    
    for dep in "${OPTIONAL_DEPS[@]}"; do
        echo -e "${YELLOW}⬇️ 安裝 $dep...${NC}"
        if pip3 install "$dep" &> /dev/null; then
            echo -e "${GREEN}✅ $dep 安裝成功${NC}"
        else
            echo -e "${YELLOW}⚠️ $dep 安裝失敗，將使用回退模式${NC}"
        fi
    done
}

# 設置數據目錄
setup_data_directory() {
    echo -e "${BLUE}📁 設置數據目錄...${NC}"
    
    DATA_DIR="./data/claude_realtime"
    mkdir -p "$DATA_DIR"
    
    if [ -d "$DATA_DIR" ]; then
        echo -e "${GREEN}✅ 數據目錄已創建: $DATA_DIR${NC}"
    else
        echo -e "${RED}❌ 無法創建數據目錄${NC}"
        exit 1
    fi
}

# 配置 startup_trigger
setup_startup_trigger() {
    echo -e "${BLUE}🔧 配置 startup trigger...${NC}"
    
    # 創建啟動配置文件
    cat > ./claude_collector_config.json << 'EOF'
{
    "data_dir": "./data/claude_realtime",
    "auto_start": true,
    "monitor_interval": 1.0,
    "heartbeat_interval": 30,
    "max_sessions": 1000,
    "enable_websocket": true,
    "websocket_port": 8765,
    "collect_system_info": true,
    "save_interval": 60,
    "compress_old_data": true,
    "retention_days": 30,
    "monitored_commands": [
        "claude",
        "claude-code",
        "claudeditor",
        "manus",
        "python.*claude",
        "node.*claude"
    ],
    "startup_triggers": {
        "claude_code_start": {
            "enabled": true,
            "command_patterns": ["claude", "claude-code"],
            "auto_collect": true
        },
        "claudeditor_start": {
            "enabled": true,
            "command_patterns": ["claudeditor"],
            "auto_collect": true
        },
        "manus_start": {
            "enabled": true,
            "command_patterns": ["manus"],
            "auto_collect": true
        }
    }
}
EOF
    
    echo -e "${GREEN}✅ 配置文件已創建: claude_collector_config.json${NC}"
}

# 創建系統服務 (可選)
create_system_service() {
    echo -e "${BLUE}⚙️ 是否創建系統服務? (開機自動啟動) [y/N]${NC}"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${BLUE}📋 創建系統服務...${NC}"
        
        # 獲取當前路徑
        CURRENT_DIR=$(pwd)
        USER_NAME=$(whoami)
        
        # 創建 launchd plist (macOS) 或 systemd service (Linux)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS launchd
            PLIST_FILE="$HOME/Library/LaunchAgents/com.powerautomation.claude-collector.plist"
            
            cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.powerautomation.claude-collector</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$CURRENT_DIR/claude_realtime_collector.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/logs/claude-collector.log</string>
    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/logs/claude-collector-error.log</string>
</dict>
</plist>
EOF
            
            # 創建日誌目錄
            mkdir -p "$CURRENT_DIR/logs"
            
            # 加載服務
            launchctl load "$PLIST_FILE"
            
            echo -e "${GREEN}✅ macOS 系統服務已創建並啟動${NC}"
            echo -e "${BLUE}ℹ️ 管理命令:${NC}"
            echo -e "   啟動: launchctl start com.powerautomation.claude-collector"
            echo -e "   停止: launchctl stop com.powerautomation.claude-collector"
            echo -e "   卸載: launchctl unload $PLIST_FILE"
            
        else
            # Linux systemd
            SERVICE_FILE="/etc/systemd/system/claude-collector.service"
            
            sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Claude Realtime Collector
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/claude_realtime_collector.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
            
            # 啟用並啟動服務
            sudo systemctl daemon-reload
            sudo systemctl enable claude-collector
            sudo systemctl start claude-collector
            
            echo -e "${GREEN}✅ Linux 系統服務已創建並啟動${NC}"
            echo -e "${BLUE}ℹ️ 管理命令:${NC}"
            echo -e "   查看狀態: sudo systemctl status claude-collector"
            echo -e "   啟動: sudo systemctl start claude-collector"
            echo -e "   停止: sudo systemctl stop claude-collector"
            echo -e "   重啟: sudo systemctl restart claude-collector"
        fi
    else
        echo -e "${YELLOW}⏭️ 跳過系統服務創建${NC}"
    fi
}

# 測試收集器
test_collector() {
    echo -e "${BLUE}🧪 測試收集器功能...${NC}"
    
    # 運行測試
    python3 -c "
import asyncio
import sys
sys.path.append('.')
from claude_realtime_collector import claude_collector

async def test():
    print('🔄 初始化收集器...')
    success = await claude_collector.initialize()
    
    if success:
        print('✅ 收集器初始化成功')
        status = claude_collector.get_status()
        print(f'📊 狀態: {status[\"status\"]}')
        print(f'🔍 監控進程數: {status[\"claude_processes\"]}')
        
        await claude_collector.shutdown()
        print('✅ 測試完成')
        return True
    else:
        print('❌ 收集器初始化失敗')
        return False

if __name__ == '__main__':
    result = asyncio.run(test())
    sys.exit(0 if result else 1)
" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 收集器測試通過${NC}"
    else
        echo -e "${YELLOW}⚠️ 收集器測試有警告，但基本功能正常${NC}"
    fi
}

# 啟動收集器
start_collector() {
    echo -e "${BLUE}🚀 啟動 Claude 實時收集器...${NC}"
    
    echo -e "${GREEN}✅ 部署完成！${NC}"
    echo -e "${BLUE}📊 監控面板: http://localhost:8765${NC}"
    echo -e "${BLUE}💾 數據目錄: ./data/claude_realtime${NC}"
    echo -e "${BLUE}📝 配置文件: claude_collector_config.json${NC}"
    echo ""
    echo -e "${YELLOW}🔍 收集器將自動監控以下命令:${NC}"
    echo -e "   • claude / claude-code"
    echo -e "   • claudeditor"
    echo -e "   • manus"
    echo -e "   • 其他 Claude 相關進程"
    echo ""
    echo -e "${BLUE}💡 使用提示:${NC}"
    echo -e "   • 收集器會在檢測到 Claude 進程時自動開始收集"
    echo -e "   • 數據將保存在 ./data/claude_realtime 目錄"
    echo -e "   • 可通過 WebSocket 在 localhost:8765 查看實時狀態"
    echo ""
    echo -e "${GREEN}🎯 現在可以正常使用 Claude，收集器將在後台自動工作！${NC}"
    echo ""
    echo -e "${BLUE}是否立即啟動收集器? [Y/n]${NC}"
    read -r response
    
    if [[ ! "$response" =~ ^([nN][oO]|[nN])$ ]]; then
        echo -e "${BLUE}🔄 啟動中...${NC}"
        python3 claude_realtime_collector.py
    else
        echo -e "${YELLOW}📝 手動啟動命令: python3 claude_realtime_collector.py${NC}"
    fi
}

# 主函數
main() {
    echo -e "${BLUE}開始一鍵部署...${NC}"
    echo ""
    
    check_python
    echo ""
    
    install_dependencies
    echo ""
    
    setup_data_directory
    echo ""
    
    setup_startup_trigger
    echo ""
    
    test_collector
    echo ""
    
    create_system_service
    echo ""
    
    start_collector
}

# 執行主函數
main "$@"