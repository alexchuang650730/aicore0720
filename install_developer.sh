#!/bin/bash
# PowerAutomation K2 - Developer Installation Script
# Full source code installation with EC2 data sync
# Usage: bash <(curl -s https://dev.powerauto.ai/install)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🔧 PowerAutomation K2 - Developer Edition${NC}"
echo "=============================================="
echo "Full source installation with EC2 sync"
echo "For PowerAutomation development team only"
echo "=============================================="

# Developer authentication
authenticate_developer() {
    echo -e "${BLUE}🔐 Developer Authentication${NC}"
    
    # Check for dev key
    if [ -z "$POWERAUTO_DEV_KEY" ]; then
        echo -n "Enter developer key: "
        read -s DEV_KEY
        echo ""
    else
        DEV_KEY="$POWERAUTO_DEV_KEY"
    fi
    
    # Verify key
    VERIFY_URL="https://api.powerauto.ai/dev/verify"
    if ! curl -s -f -X POST "$VERIFY_URL" -d "key=$DEV_KEY" > /dev/null; then
        echo -e "${RED}❌ Invalid developer key${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Developer authenticated${NC}"
}

# EC2 configuration
setup_ec2_sync() {
    echo -e "${BLUE}☁️  Setting up EC2 data sync${NC}"
    
    # EC2 instance details
    EC2_HOST="ec2-powerauto-k2.us-west-2.compute.amazonaws.com"
    EC2_USER="ubuntu"
    EC2_DATA_PATH="/data/powerautomation"
    
    # Check SSH key
    if [ ! -f "$HOME/.ssh/powerauto-dev.pem" ]; then
        echo -e "${YELLOW}📥 Downloading EC2 SSH key...${NC}"
        curl -s -H "Authorization: Bearer $DEV_KEY" \
            https://api.powerauto.ai/dev/ec2-key \
            -o "$HOME/.ssh/powerauto-dev.pem"
        chmod 600 "$HOME/.ssh/powerauto-dev.pem"
    fi
    
    # Test connection
    if ssh -o ConnectTimeout=5 -i "$HOME/.ssh/powerauto-dev.pem" \
        "$EC2_USER@$EC2_HOST" "echo 'Connected'" &> /dev/null; then
        echo -e "${GREEN}✅ EC2 connection established${NC}"
        EC2_AVAILABLE=true
    else
        echo -e "${YELLOW}⚠️  EC2 not accessible, using local mode${NC}"
        EC2_AVAILABLE=false
    fi
}

# Main installation
main() {
    # Authenticate first
    authenticate_developer
    
    # Setup directories
    DEV_ROOT="$HOME/powerautomation-dev"
    echo -e "${BLUE}📁 Creating development environment: $DEV_ROOT${NC}"
    mkdir -p "$DEV_ROOT"
    cd "$DEV_ROOT"
    
    # Clone full source
    echo -e "${BLUE}📥 Cloning complete source code...${NC}"
    if [ -d "aicore0720" ]; then
        cd aicore0720
        git pull origin main
    else
        git clone git@github.com:alexchuang650730/aicore0720.git
        cd aicore0720
    fi
    
    # Install all dependencies
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    
    # Python environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install requirements
    pip install -r requirements.txt
    pip install -r requirements-dev.txt 2>/dev/null || true
    
    # Node.js dependencies (if needed)
    if [ -f "package.json" ]; then
        npm install
    fi
    
    # Setup EC2 sync
    setup_ec2_sync
    
    # Sync data from EC2
    if [ "$EC2_AVAILABLE" = true ]; then
        echo -e "${BLUE}🔄 Syncing data from EC2...${NC}"
        
        # Create data directories
        mkdir -p data/dialogues data/models data/training
        
        # Sync dialogue data
        rsync -avz --progress \
            -e "ssh -i $HOME/.ssh/powerauto-dev.pem" \
            "$EC2_USER@$EC2_HOST:$EC2_DATA_PATH/dialogues/" \
            ./data/dialogues/
            
        # Sync trained models
        rsync -avz --progress \
            -e "ssh -i $HOME/.ssh/powerauto-dev.pem" \
            "$EC2_USER@$EC2_HOST:$EC2_DATA_PATH/models/" \
            ./data/models/
            
        echo -e "${GREEN}✅ Data sync completed${NC}"
    fi
    
    # Setup development environment
    echo -e "${BLUE}🛠️  Setting up development environment...${NC}"
    
    # Create dev config
    cat > .env.development << EOF
# Development Configuration
DEV_MODE=true
DEBUG=true
HOT_RELOAD=true

# EC2 Configuration
EC2_HOST=$EC2_HOST
EC2_DATA_PATH=$EC2_DATA_PATH
AUTO_SYNC=true
SYNC_INTERVAL=300

# K2 Development
K2_DEV_MODE=true
K2_TRAINING_VERBOSE=true
K2_MODEL_VERSIONING=true

# API Keys (development)
ANTHROPIC_API_KEY=$DEV_KEY
GROQ_API_KEY=gsk_development_key

# Ports
API_PORT=9999
EDITOR_PORT=8888
MCP_PORT=7777
DEBUG_PORT=5555

# Data Collection
COLLECT_ALL_DIALOGUES=true
ANONYMIZE_DATA=false
TRAINING_BATCH_SIZE=100
EOF

    # Create development scripts
    cat > dev.sh << 'EOF'
#!/bin/bash
# PowerAutomation Development Helper

source venv/bin/activate

case "$1" in
    start)
        echo "🚀 Starting development servers..."
        python3 main_server.py --dev &
        python3 dialogue_collector.py &
        python3 k2_training_server.py &
        npm run dev &
        ;;
    
    sync)
        echo "🔄 Syncing with EC2..."
        ./scripts/sync_ec2.sh
        ;;
    
    train)
        echo "🧠 Starting K2 training..."
        python3 unified_realtime_k2_fixed.py --dev
        ;;
    
    test)
        echo "🧪 Running tests..."
        pytest tests/ -v
        ;;
    
    deploy)
        echo "🚀 Deploying to production..."
        ./scripts/deploy_prod.sh
        ;;
    
    *)
        echo "Usage: ./dev.sh {start|sync|train|test|deploy}"
        ;;
esac
EOF
    chmod +x dev.sh
    
    # Create sync script
    mkdir -p scripts
    cat > scripts/sync_ec2.sh << 'EOF'
#!/bin/bash
# EC2 Data Synchronization

source ../.env.development

# Sync dialogues to EC2
echo "📤 Uploading new dialogues..."
rsync -avz --progress \
    -e "ssh -i $HOME/.ssh/powerauto-dev.pem" \
    ./data/dialogues/ \
    ubuntu@$EC2_HOST:$EC2_DATA_PATH/dialogues/

# Sync models from EC2
echo "📥 Downloading latest models..."
rsync -avz --progress \
    -e "ssh -i $HOME/.ssh/powerauto-dev.pem" \
    ubuntu@$EC2_HOST:$EC2_DATA_PATH/models/ \
    ./data/models/

echo "✅ Sync completed"
EOF
    chmod +x scripts/sync_ec2.sh
    
    # Setup auto-sync cron job
    echo -e "${BLUE}⏰ Setting up auto-sync...${NC}"
    (crontab -l 2>/dev/null; echo "*/5 * * * * cd $DEV_ROOT/aicore0720 && ./scripts/sync_ec2.sh > /dev/null 2>&1") | crontab -
    
    # Configure Claude Code for development
    echo -e "${BLUE}🔧 Configuring Claude Code (dev mode)...${NC}"
    
    cat > "$HOME/.claude/claude_desktop_config_dev.json" << EOF
{
  "mcpServers": {
    "powerautomation-dev": {
      "command": "python3",
      "args": ["$DEV_ROOT/aicore0720/mcp_dev_server.py"],
      "env": {
        "DEV_MODE": "true",
        "PROJECT_ROOT": "$DEV_ROOT/aicore0720"
      }
    }
  }
}
EOF

    # Create MCP development server
    cat > mcp_dev_server.py << 'EOF'
#!/usr/bin/env python3
"""MCP Development Server with hot reload and debugging"""

import sys
import os
sys.path.insert(0, os.environ.get('PROJECT_ROOT'))

from k2_mode_switcher_mcp import K2ModeSwitcherMCP
from model_command_handler import ModelCommandHandler
from dialogue_collector import DialogueCollector
import json
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

class DevMCPServer:
    def __init__(self):
        self.k2_switcher = K2ModeSwitcherMCP()
        self.command_handler = ModelCommandHandler()
        self.collector = DialogueCollector()
        
    def handle_request(self, request):
        # Log all requests in dev mode
        logging.debug(f"MCP Request: {json.dumps(request)}")
        
        # Route to appropriate handler
        method = request.get("method", "")
        
        if method.startswith("k2/"):
            return self.k2_switcher.handle_request(request)
        elif method.startswith("command/"):
            return {"result": self.command_handler.process_input(
                request.get("params", {}).get("text", "")
            )}
        else:
            return {"error": "Unknown method", "available": [
                "k2/predict", "k2/switch_mode", "k2/status",
                "command/process"
            ]}

if __name__ == "__main__":
    server = DevMCPServer()
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            logging.error(f"Error: {e}")
            print(json.dumps({"error": str(e), "dev_mode": True}))
            sys.stdout.flush()
EOF

    # Final setup
    echo -e "${BLUE}🎯 Running initial setup...${NC}"
    
    # Download initial training data from EC2
    if [ "$EC2_AVAILABLE" = true ]; then
        echo "📥 Downloading training datasets..."
        scp -i "$HOME/.ssh/powerauto-dev.pem" \
            "$EC2_USER@$EC2_HOST:$EC2_DATA_PATH/training/*.json" \
            ./data/training/ 2>/dev/null || true
    fi
    
    # Initialize database
    python3 -c "from dialogue_collector import DialogueCollector; DialogueCollector().init_database()"
    
    # Success message
    clear
    echo -e "${GREEN}🎉 PowerAutomation K2 Developer Edition Installed!${NC}"
    echo "=============================================="
    echo ""
    echo -e "${PURPLE}📁 Installation location:${NC} $DEV_ROOT/aicore0720"
    echo ""
    echo -e "${BLUE}🚀 Quick Start:${NC}"
    echo "   cd $DEV_ROOT/aicore0720"
    echo "   ./dev.sh start"
    echo ""
    echo -e "${BLUE}📊 Development Commands:${NC}"
    echo "   ./dev.sh sync   - Sync with EC2"
    echo "   ./dev.sh train  - Run K2 training"
    echo "   ./dev.sh test   - Run test suite"
    echo "   ./dev.sh deploy - Deploy to production"
    echo ""
    echo -e "${BLUE}🔧 Configuration:${NC}"
    echo "   Config: .env.development"
    echo "   Claude: ~/.claude/claude_desktop_config_dev.json"
    echo ""
    if [ "$EC2_AVAILABLE" = true ]; then
        echo -e "${GREEN}☁️  EC2 Status:${NC} Connected & Syncing"
        echo "   Auto-sync: Every 5 minutes"
    else
        echo -e "${YELLOW}☁️  EC2 Status:${NC} Local mode"
    fi
    echo ""
    echo -e "${PURPLE}Happy Developing! 🚀${NC}"
    
    # Start development environment
    echo ""
    echo -n "Start development servers now? [Y/n] "
    read -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        ./dev.sh start
    fi
}

# Run installation
main "$@"