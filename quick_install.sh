#!/bin/bash
# PowerAutomation K2 Edition - Quick Install Script
# Usage: curl -fsSL https://powerauto.ai/install | bash

set -e

echo "🚀 PowerAutomation K2 Edition - Quick Installer"
echo "=============================================="
echo "Features:"
echo "✅ K2 AI Model with /model command"
echo "✅ ClaudeEditor integration" 
echo "✅ Automatic dialogue collection"
echo "✅ Docker-based deployment"
echo "=============================================="

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed"
        echo "📦 Installing Docker..."
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
            echo "Or run: brew install --cask docker"
            exit 1
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            curl -fsSL https://get.docker.com | sh
            sudo usermod -aG docker $USER
            echo "✅ Docker installed. Please log out and back in, then re-run this script."
            exit 0
        fi
    fi
    
    # Check Docker is running
    if ! docker info &> /dev/null; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    echo "✅ Docker: $(docker --version)"
}

# Main installation
main() {
    check_prerequisites
    
    # Create installation directory
    INSTALL_DIR="$HOME/.powerautomation"
    echo "📁 Creating installation directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Pull PowerAutomation Docker image
    echo "📥 Pulling PowerAutomation K2 Edition..."
    docker pull powerauto/k2-edition:latest || {
        echo "⚠️  Official image not available, building from source..."
        
        # Download Dockerfile
        curl -fsSL -o Dockerfile https://raw.githubusercontent.com/alexchuang650730/aicore0720/main/docker/Dockerfile.k2
        
        # Build image
        docker build -t powerauto/k2-edition:latest .
    }
    
    # Create docker-compose.yml
    echo "📝 Creating docker-compose configuration..."
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  powerautomation-k2:
    image: powerauto/k2-edition:latest
    container_name: powerautomation-k2
    restart: unless-stopped
    ports:
      - "8888:8888"  # ClaudeEditor port
      - "9999:9999"  # K2 API port
      - "7777:7777"  # MCP server port
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
      - $HOME/.claude:/app/claude_config:ro
      - $HOME/Library/Application Support/Claude:/app/claude_data:ro
    environment:
      - K2_MODE=hybrid
      - COLLECT_DIALOGUES=true
      - AUTO_TRAIN=true
      - CLAUDE_CONFIG_PATH=/app/claude_config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9999/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  dialogue-collector:
    image: powerauto/k2-edition:latest
    container_name: dialogue-collector
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - $HOME/Library/Application Support/Claude:/claude_data:ro
    environment:
      - COLLECTOR_MODE=true
      - WATCH_PATH=/claude_data
    command: python3 /app/dialogue_collector.py
EOF

    # Create MCP configuration
    echo "🔧 Configuring Claude Code MCP..."
    CLAUDE_CONFIG_DIR="$HOME/.claude"
    mkdir -p "$CLAUDE_CONFIG_DIR"
    
    # Backup existing config
    if [ -f "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" ]; then
        cp "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" "$CLAUDE_CONFIG_DIR/claude_desktop_config.backup.json"
    fi
    
    # Create new MCP config
    cat > "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "powerautomation-k2": {
      "command": "docker",
      "args": ["exec", "-i", "powerautomation-k2", "python3", "/app/k2_mcp_server.py"],
      "env": {
        "K2_ENABLED": "true"
      }
    },
    "model-switcher": {
      "command": "docker", 
      "args": ["exec", "-i", "powerautomation-k2", "python3", "/app/model_command_handler.py"],
      "env": {
        "SUPPORT_SLASH_COMMANDS": "true"
      }
    },
    "claudeeditor-launcher": {
      "command": "docker",
      "args": ["exec", "-i", "powerautomation-k2", "python3", "/app/claudeeditor_launcher.py"],
      "env": {
        "CLAUDEEDITOR_URL": "http://localhost:8888"
      }
    }
  }
}
EOF

    # Create launcher script
    echo "🚀 Creating launcher script..."
    cat > "$INSTALL_DIR/powerautomation" << 'EOF'
#!/bin/bash
# PowerAutomation K2 Edition Launcher

INSTALL_DIR="$HOME/.powerautomation"
cd "$INSTALL_DIR"

case "$1" in
    start)
        echo "🚀 Starting PowerAutomation K2 Edition..."
        docker-compose up -d
        echo "✅ PowerAutomation is running!"
        echo "📊 Dashboard: http://localhost:8888"
        echo "🤖 K2 API: http://localhost:9999"
        ;;
    stop)
        echo "🛑 Stopping PowerAutomation..."
        docker-compose down
        ;;
    status)
        docker-compose ps
        ;;
    logs)
        docker-compose logs -f ${2:-powerautomation-k2}
        ;;
    update)
        echo "📥 Updating PowerAutomation..."
        docker-compose pull
        docker-compose up -d
        ;;
    *)
        echo "PowerAutomation K2 Edition"
        echo "Usage: powerautomation {start|stop|status|logs|update}"
        ;;
esac
EOF

    chmod +x "$INSTALL_DIR/powerautomation"
    
    # Add to PATH
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.bashrc
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.zshrc 2>/dev/null || true
    fi
    
    # Create desktop app (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🖥️  Creating macOS app..."
        create_macos_app
    fi
    
    # Start services
    echo "🚀 Starting PowerAutomation services..."
    cd "$INSTALL_DIR"
    docker-compose up -d
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to start..."
    sleep 5
    
    # Verify installation
    if curl -s http://localhost:9999/health > /dev/null; then
        echo "✅ K2 API is running"
    else
        echo "⚠️  K2 API is not responding yet"
    fi
    
    echo ""
    echo "🎉 PowerAutomation K2 Edition installed successfully!"
    echo "=============================================="
    echo ""
    echo "🚀 Quick Start:"
    echo "1. Restart Claude Code to load MCP configuration"
    echo "2. In Claude Code, type: /model k2"
    echo "3. Or say: '啟動編輯器' to open ClaudeEditor"
    echo ""
    echo "📝 Available Commands:"
    echo "• /model k2      - Switch to K2 mode"
    echo "• /model claude  - Switch to Claude mode"
    echo "• /model hybrid  - Switch to hybrid mode"
    echo "• /model status  - Check current status"
    echo ""
    echo "🔧 Service Management:"
    echo "• powerautomation start  - Start services"
    echo "• powerautomation stop   - Stop services"
    echo "• powerautomation logs   - View logs"
    echo ""
    echo "📊 Web Dashboard: http://localhost:8888"
    echo ""
    echo "💡 Note: Dialogues are automatically collected for training!"
}

# Create macOS app
create_macos_app() {
    APP_DIR="/Applications/PowerAutomation K2.app"
    mkdir -p "$APP_DIR/Contents/MacOS"
    mkdir -p "$APP_DIR/Contents/Resources"
    
    # Create Info.plist
    cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>PowerAutomation</string>
    <key>CFBundleIdentifier</key>
    <string>ai.powerauto.k2</string>
    <key>CFBundleName</key>
    <string>PowerAutomation K2</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
</dict>
</plist>
EOF

    # Create launcher
    cat > "$APP_DIR/Contents/MacOS/PowerAutomation" << 'EOF'
#!/bin/bash
open http://localhost:8888
EOF
    
    chmod +x "$APP_DIR/Contents/MacOS/PowerAutomation"
    echo "✅ Created macOS app: PowerAutomation K2.app"
}

# Run installation
main "$@"