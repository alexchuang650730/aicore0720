#!/bin/bash
# PowerAutomation K2 - Enhanced User Installation Script v2
# Addresses common installation issues
# Usage: curl -fsSL https://powerauto.ai/install | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEFAULT_PORT=8888
ALTERNATIVE_PORTS=(8889 8890 8891 9000)
INSTALL_DIR="$HOME/.powerautomation"

echo -e "${BLUE}🚀 PowerAutomation K2 - Smart Installation v2${NC}"
echo "================================================"
echo ""

# Enhanced prerequisite check
check_system() {
    echo -e "${BLUE}🔍 Checking your system...${NC}"
    
    # OS Detection
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        DOCKER_INSTALL_URL="https://www.docker.com/products/docker-desktop"
        DOCKER_INSTALL_CMD="brew install --cask docker"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        DOCKER_INSTALL_URL="https://docs.docker.com/engine/install/"
        DOCKER_INSTALL_CMD="curl -fsSL https://get.docker.com | sh"
    else
        echo -e "${RED}❌ Unsupported OS: $OSTYPE${NC}"
        exit 1
    fi
    echo -e "  ✅ Operating System: $OS"
    
    # Docker check with helpful instructions
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}📦 Docker is not installed${NC}"
        echo ""
        echo "Docker is required for PowerAutomation. Here's how to install it:"
        echo ""
        echo -e "${GREEN}Option 1: Install via command line${NC}"
        echo "  $DOCKER_INSTALL_CMD"
        echo ""
        echo -e "${GREEN}Option 2: Download installer${NC}"
        echo "  $DOCKER_INSTALL_URL"
        echo ""
        echo "After installing Docker:"
        echo "1. Start Docker Desktop"
        echo "2. Run this installer again"
        echo ""
        exit 1
    fi
    
    # Docker running check
    if ! docker info &> /dev/null; then
        echo -e "${YELLOW}⚠️  Docker is installed but not running${NC}"
        echo ""
        if [[ "$OS" == "macOS" ]]; then
            echo "Please start Docker Desktop from Applications"
            # Try to start Docker
            echo "Attempting to start Docker..."
            open -a Docker 2>/dev/null || true
            echo "Waiting for Docker to start (30 seconds)..."
            
            for i in {1..30}; do
                if docker info &> /dev/null; then
                    echo -e "${GREEN}✅ Docker started successfully!${NC}"
                    break
                fi
                sleep 1
            done
            
            if ! docker info &> /dev/null; then
                echo -e "${RED}❌ Docker failed to start${NC}"
                echo "Please start Docker Desktop manually and try again"
                exit 1
            fi
        else
            echo "Please start Docker service:"
            echo "  sudo systemctl start docker"
            exit 1
        fi
    fi
    echo -e "  ✅ Docker: Running ($(docker --version))"
    
    # Check disk space
    if [[ "$OS" == "macOS" ]]; then
        DISK_AVAILABLE=$(df -g . | awk 'NR==2 {print $4}')
    else
        DISK_AVAILABLE=$(df -BG . | awk 'NR==2 {print int($4)}')
    fi
    
    if [ "$DISK_AVAILABLE" -lt 2 ]; then
        echo -e "${YELLOW}⚠️  Low disk space: ${DISK_AVAILABLE}GB available${NC}"
        echo "  Recommended: At least 2GB free space"
    else
        echo -e "  ✅ Disk Space: ${DISK_AVAILABLE}GB available"
    fi
    
    # Check Claude Code
    CLAUDE_INSTALLED=false
    if [ -d "$HOME/.claude" ] || [ -d "$HOME/Library/Application Support/Claude" ]; then
        echo -e "  ✅ Claude Code: Detected"
        CLAUDE_INSTALLED=true
    else
        echo -e "  ℹ️  Claude Code: Not detected (optional)"
        echo "     You can still use PowerAutomation via web interface"
    fi
    
    # Check ports
    check_ports
}

# Smart port selection
check_ports() {
    echo -e "${BLUE}🔌 Checking available ports...${NC}"
    
    SELECTED_PORT=""
    
    # Check default port first
    if ! lsof -Pi :$DEFAULT_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        SELECTED_PORT=$DEFAULT_PORT
        echo -e "  ✅ Port $DEFAULT_PORT is available"
    else
        echo -e "  ⚠️  Port $DEFAULT_PORT is in use"
        
        # Try alternative ports
        for port in "${ALTERNATIVE_PORTS[@]}"; do
            if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                SELECTED_PORT=$port
                echo -e "  ✅ Using alternative port: $port"
                break
            fi
        done
        
        if [ -z "$SELECTED_PORT" ]; then
            echo -e "${RED}❌ No available ports found${NC}"
            echo "Please free up one of these ports: $DEFAULT_PORT ${ALTERNATIVE_PORTS[@]}"
            exit 1
        fi
    fi
}

# Installation with error handling
install_powerautomation() {
    echo -e "${BLUE}📦 Installing PowerAutomation K2...${NC}"
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Try to pull official image
    echo "Downloading PowerAutomation..."
    if docker pull powerauto/k2:latest 2>/dev/null; then
        echo -e "${GREEN}✅ Downloaded official image${NC}"
    else
        echo -e "${YELLOW}Building from source...${NC}"
        
        # Create minimal Dockerfile
        cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/alexchuang650730/aicore0720.git .
RUN pip install flask flask-cors watchdog
COPY mcp_unified.py /app/
EXPOSE 8888 9999
CMD ["python3", "mcp_unified.py"]
EOF
        
        # Copy MCP server
        curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0720/main/mcp_unified.py \
            -o mcp_unified.py
        
        # Build image
        docker build -t powerauto/k2:latest . || {
            echo -e "${RED}❌ Build failed${NC}"
            exit 1
        }
    fi
    
    # Stop existing container if any
    docker stop powerautomation-k2 2>/dev/null || true
    docker rm powerautomation-k2 2>/dev/null || true
    
    # Run container with selected port
    echo -e "${BLUE}🚀 Starting PowerAutomation...${NC}"
    docker run -d \
        --name powerautomation-k2 \
        --restart unless-stopped \
        -p $SELECTED_PORT:8888 \
        -p 9999:9999 \
        -v "$INSTALL_DIR/data:/data" \
        -v "$HOME/.claude:/claude:ro" \
        -v "$HOME/Library/Application Support/Claude:/claude_data:ro" \
        -e PORT=$SELECTED_PORT \
        powerauto/k2:latest || {
            echo -e "${RED}❌ Failed to start container${NC}"
            docker logs powerautomation-k2
            exit 1
        }
    
    # Configure Claude Code if installed
    if [ "$CLAUDE_INSTALLED" = true ]; then
        configure_claude_code
    fi
    
    # Create management script
    create_management_script
    
    # Verify installation
    verify_installation
}

# Configure Claude Code MCP
configure_claude_code() {
    echo -e "${BLUE}🔧 Configuring Claude Code...${NC}"
    
    CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"
    
    # Backup existing config
    if [ -f "$CLAUDE_CONFIG" ]; then
        cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup.$(date +%s)"
        echo "  ✅ Backed up existing configuration"
    fi
    
    # Create MCP config
    cat > "$CLAUDE_CONFIG" << EOF
{
  "mcpServers": {
    "powerautomation": {
      "command": "docker",
      "args": ["exec", "-i", "powerautomation-k2", "python3", "/app/mcp_unified.py"],
      "env": {
        "AUTOCOMPLETE": "true"
      }
    }
  }
}
EOF
    
    echo -e "  ✅ Claude Code configured"
    echo -e "  ${YELLOW}⚠️  Please restart Claude Code to activate${NC}"
}

# Create management script
create_management_script() {
    cat > "$INSTALL_DIR/powerauto" << 'EOF'
#!/bin/bash
# PowerAutomation Management Tool

case "$1" in
    start)
        docker start powerautomation-k2
        echo "✅ PowerAutomation started"
        ;;
    stop)
        docker stop powerautomation-k2
        echo "✅ PowerAutomation stopped"
        ;;
    restart)
        docker restart powerautomation-k2
        echo "✅ PowerAutomation restarted"
        ;;
    status)
        if docker ps | grep -q powerautomation-k2; then
            echo "✅ PowerAutomation is running"
            docker ps | grep powerautomation-k2
        else
            echo "❌ PowerAutomation is not running"
        fi
        ;;
    logs)
        docker logs -f powerautomation-k2
        ;;
    update)
        echo "📥 Updating PowerAutomation..."
        docker pull powerauto/k2:latest
        docker stop powerautomation-k2
        docker rm powerautomation-k2
        cd ~/.powerautomation && bash install_user_v2.sh
        ;;
    uninstall)
        read -p "Are you sure you want to uninstall? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker stop powerautomation-k2 2>/dev/null
            docker rm powerautomation-k2 2>/dev/null
            docker rmi powerauto/k2:latest 2>/dev/null
            rm -rf ~/.powerautomation
            echo "✅ PowerAutomation uninstalled"
        fi
        ;;
    doctor)
        echo "🏥 PowerAutomation Diagnostic"
        echo "============================="
        
        # Check Docker
        if docker info &> /dev/null; then
            echo "✅ Docker: Running"
        else
            echo "❌ Docker: Not running"
        fi
        
        # Check container
        if docker ps | grep -q powerautomation-k2; then
            echo "✅ Container: Running"
            
            # Check health
            if curl -s http://localhost:9999/health > /dev/null; then
                echo "✅ API: Healthy"
            else
                echo "❌ API: Not responding"
            fi
        else
            echo "❌ Container: Not running"
        fi
        
        # Check Claude Code
        if [ -f "$HOME/.claude/claude_desktop_config.json" ]; then
            echo "✅ Claude Code: Configured"
        else
            echo "ℹ️  Claude Code: Not configured"
        fi
        ;;
    *)
        echo "PowerAutomation Management"
        echo "Usage: powerauto {start|stop|restart|status|logs|update|uninstall|doctor}"
        ;;
esac
EOF
    
    chmod +x "$INSTALL_DIR/powerauto"
    
    # Add to PATH
    if ! grep -q "powerautomation" ~/.bashrc 2>/dev/null; then
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.bashrc
    fi
    if [ -f ~/.zshrc ] && ! grep -q "powerautomation" ~/.zshrc; then
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.zshrc
    fi
}

# Verify installation
verify_installation() {
    echo -e "${BLUE}🔍 Verifying installation...${NC}"
    
    # Wait for container to be ready
    for i in {1..30}; do
        if curl -s http://localhost:9999/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ PowerAutomation is ready!${NC}"
            break
        fi
        sleep 1
    done
    
    # Final status check
    if ! curl -s http://localhost:9999/health > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  PowerAutomation is taking longer to start${NC}"
        echo "Check logs with: docker logs powerautomation-k2"
    fi
}

# Success message
show_success() {
    clear
    echo -e "${GREEN}🎉 PowerAutomation K2 Successfully Installed!${NC}"
    echo "=============================================="
    echo ""
    
    if [ "$CLAUDE_INSTALLED" = true ]; then
        echo -e "${BLUE}🚀 Quick Start Guide:${NC}"
        echo ""
        echo "1️⃣  Restart Claude Code"
        echo ""
        echo "2️⃣  Use these commands in Claude Code:"
        echo -e "   ${GREEN}/model k2${NC}      - Switch to K2 AI"
        echo -e "   ${GREEN}/model claude${NC}  - Switch to Claude AI"
        echo -e "   ${GREEN}/model status${NC}  - Check current mode"
        echo ""
        echo "3️⃣  Or say these phrases:"
        echo -e "   ${GREEN}\"Open editor\"${NC}  - Launch ClaudeEditor"
        echo -e "   ${GREEN}\"啟動編輯器\"${NC}    - 啟動 ClaudeEditor"
    else
        echo -e "${BLUE}🚀 Quick Start Guide:${NC}"
        echo ""
        echo "PowerAutomation is running! Access it at:"
        echo -e "${GREEN}http://localhost:$SELECTED_PORT${NC}"
        echo ""
        echo "To get the full experience:"
        echo "1. Install Claude Code"
        echo "2. Run: powerauto restart"
    fi
    
    echo ""
    echo -e "${BLUE}🛠️  Management Commands:${NC}"
    echo "   powerauto status   - Check status"
    echo "   powerauto logs     - View logs"
    echo "   powerauto doctor   - Diagnose issues"
    echo "   powerauto update   - Update to latest"
    echo ""
    echo -e "${YELLOW}💡 Pro tip:${NC} Your conversations are automatically"
    echo "   improving the AI model!"
    echo ""
    
    # Open dashboard
    if command -v open &> /dev/null; then
        echo -e "${BLUE}Opening dashboard...${NC}"
        sleep 2
        open "http://localhost:$SELECTED_PORT"
    fi
}

# Main execution
main() {
    check_system
    install_powerautomation
    show_success
}

# Run installation
main "$@"