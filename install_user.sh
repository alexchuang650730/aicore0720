#!/bin/bash
# PowerAutomation K2 - User Installation Script
# Simple one-line installation for end users
# Usage: curl -fsSL https://powerauto.ai/install | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 PowerAutomation K2 - Easy Installation${NC}"
echo "=============================================="
echo "Installing the simplest AI automation tool..."
echo ""

# Simple prerequisite check
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}📦 Docker is required but not installed.${NC}"
        echo ""
        echo "Please install Docker Desktop first:"
        echo -e "${BLUE}👉 https://www.docker.com/products/docker-desktop${NC}"
        echo ""
        echo "After installing Docker, run this command again:"
        echo -e "${GREEN}curl -fsSL https://powerauto.ai/install | bash${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${YELLOW}⚠️  Docker is installed but not running.${NC}"
        echo "Please start Docker Desktop and try again."
        exit 1
    fi
}

# Main installation
main() {
    check_docker
    
    echo -e "${GREEN}✅ Docker is ready${NC}"
    
    # Quick installation
    echo -e "${BLUE}📥 Installing PowerAutomation K2...${NC}"
    
    # Pull and run in one command
    docker run -d \
        --name powerautomation-k2 \
        --restart unless-stopped \
        -p 8888:8888 \
        -v "$HOME/.powerautomation:/data" \
        -v "$HOME/.claude:/claude:ro" \
        -e QUICK_START=true \
        powerauto/k2:latest 2>/dev/null || {
            
        # If official image doesn't exist, use backup
        echo -e "${YELLOW}Using alternative installation method...${NC}"
        
        # Create minimal setup
        mkdir -p "$HOME/.powerautomation"
        cd "$HOME/.powerautomation"
        
        # Download pre-built package
        curl -fsSL -o powerauto-k2.tar.gz \
            https://github.com/alexchuang650730/aicore0720/releases/latest/download/powerauto-k2.tar.gz || {
            
            # Fallback to git clone
            echo -e "${YELLOW}Downloading from source...${NC}"
            git clone --depth 1 https://github.com/alexchuang650730/aicore0720.git temp
            cd temp
            docker build -t powerauto/k2:latest -f docker/Dockerfile.k2 .
            cd ..
            rm -rf temp
            
            # Retry run
            docker run -d \
                --name powerautomation-k2 \
                --restart unless-stopped \
                -p 8888:8888 \
                -v "$HOME/.powerautomation:/data" \
                -v "$HOME/.claude:/claude:ro" \
                -e QUICK_START=true \
                powerauto/k2:latest
        }
    }
    
    # Configure Claude Code (if installed)
    if [ -d "$HOME/.claude" ]; then
        echo -e "${BLUE}🔧 Configuring Claude Code...${NC}"
        
        # Backup existing config
        if [ -f "$HOME/.claude/claude_desktop_config.json" ]; then
            cp "$HOME/.claude/claude_desktop_config.json" \
               "$HOME/.claude/claude_desktop_config.backup.$(date +%s).json"
        fi
        
        # Simple MCP config
        cat > "$HOME/.claude/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "powerautomation": {
      "command": "docker",
      "args": ["exec", "-i", "powerautomation-k2", "/app/mcp_unified.py"]
    }
  }
}
EOF
        echo -e "${GREEN}✅ Claude Code configured${NC}"
    fi
    
    # Create simple launcher
    cat > /usr/local/bin/powerauto << 'EOF'
#!/bin/bash
case "$1" in
    stop)
        docker stop powerautomation-k2
        echo "PowerAutomation stopped"
        ;;
    start)
        docker start powerautomation-k2
        echo "PowerAutomation started"
        ;;
    status)
        docker ps | grep powerautomation-k2
        ;;
    *)
        open http://localhost:8888
        ;;
esac
EOF
    chmod +x /usr/local/bin/powerauto 2>/dev/null || true
    
    # Wait for service
    echo -e "${BLUE}⏳ Starting services...${NC}"
    sleep 5
    
    # Success message
    clear
    echo -e "${GREEN}🎉 PowerAutomation K2 Successfully Installed!${NC}"
    echo "=============================================="
    echo ""
    echo -e "${BLUE}🚀 Getting Started:${NC}"
    echo ""
    echo "1️⃣  Restart Claude Code"
    echo ""
    echo "2️⃣  In Claude Code, type:"
    echo -e "   ${GREEN}/model k2${NC} - Use local AI"
    echo -e "   ${GREEN}/model claude${NC} - Use Claude AI"
    echo ""
    echo "3️⃣  Or say:"
    echo -e "   ${GREEN}\"Open ClaudeEditor\"${NC} - Launch visual editor"
    echo ""
    echo -e "${BLUE}📊 Dashboard:${NC} http://localhost:8888"
    echo ""
    echo -e "${YELLOW}💡 Tip:${NC} Your conversations are automatically improving the AI!"
    echo ""
    
    # Auto-open dashboard
    if command -v open &> /dev/null; then
        echo -e "${BLUE}Opening dashboard in 3 seconds...${NC}"
        sleep 3
        open http://localhost:8888
    fi
}

# Run installation
main