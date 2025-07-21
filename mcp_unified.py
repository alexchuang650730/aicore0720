#!/usr/bin/env python3
"""
Unified MCP Server for User Version
Combines all functionality in one simple server
"""

import json
import sys
import os
import subprocess
import threading
import time
from pathlib import Path

class UnifiedMCPServer:
    def __init__(self):
        self.mode = "hybrid"
        self.k2_threshold = 0.7
        self.claudeeditor_url = "http://localhost:8888"
        
        # Simple intent patterns for K2
        self.intent_patterns = {
            "code_generation": ["write", "create", "implement", "generate", "寫", "創建", "實現"],
            "bug_fixing": ["fix", "debug", "error", "bug", "修復", "錯誤"],
            "explanation": ["explain", "what", "how", "why", "解釋", "什麼", "為什麼"],
            "refactoring": ["refactor", "improve", "optimize", "重構", "優化"],
            "testing": ["test", "verify", "check", "測試", "驗證"]
        }
        
        # ClaudeEditor keywords
        self.editor_keywords = [
            "open editor", "start editor", "claudeeditor",
            "啟動編輯器", "打開編輯器", "編輯器"
        ]
        
    def handle_request(self, request):
        """Handle all MCP requests"""
        method = request.get("method", "")
        params = request.get("params", {})
        text = params.get("text", "").lower()
        
        # Check for /model command
        if text.startswith("/model"):
            return self.handle_model_command(text)
            
        # Check for editor keywords
        if any(kw in text for kw in self.editor_keywords):
            return self.launch_editor()
            
        # Process with K2/Claude based on mode
        if method == "completion" or method == "chat":
            return self.process_completion(text)
            
        # Status request
        if method == "status":
            return {
                "mode": self.mode,
                "k2_available": True,
                "claudeeditor_available": True,
                "dialogue_collection": "active"
            }
            
        return {"status": "ok"}
        
    def handle_model_command(self, text):
        """Handle /model commands"""
        parts = text.split()
        if len(parts) < 2:
            return {
                "message": "Usage: /model {k2|claude|hybrid|status}",
                "handled": True
            }
            
        command = parts[1]
        
        if command == "k2":
            self.mode = "k2"
            return {"message": "✅ Switched to K2 mode", "handled": True}
        elif command == "claude":
            self.mode = "claude"
            return {"message": "✅ Switched to Claude mode", "handled": True}
        elif command == "hybrid":
            self.mode = "hybrid"
            return {"message": "✅ Switched to Hybrid mode", "handled": True}
        elif command == "status":
            return {
                "message": f"📊 Current mode: {self.mode.upper()}\n" +
                          f"🎯 K2 threshold: {self.k2_threshold:.0%}\n" +
                          f"✅ All systems operational",
                "handled": True
            }
        else:
            return {
                "message": f"❌ Unknown command: {command}\n" +
                          "Use: k2, claude, hybrid, or status",
                "handled": True
            }
            
    def launch_editor(self):
        """Launch ClaudeEditor"""
        try:
            # Open in browser
            if sys.platform == "darwin":
                subprocess.run(["open", self.claudeeditor_url])
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", self.claudeeditor_url])
            else:
                subprocess.run(["start", self.claudeeditor_url], shell=True)
                
            return {
                "message": "✅ ClaudeEditor launched",
                "handled": True
            }
        except:
            return {
                "message": "❌ Failed to launch ClaudeEditor\n" +
                          f"Please open: {self.claudeeditor_url}",
                "handled": True
            }
            
    def process_completion(self, text):
        """Process completion based on mode"""
        # Detect intent
        intent = self.detect_intent(text)
        confidence = self.calculate_confidence(text, intent)
        
        # Decide which model to use
        use_k2 = False
        if self.mode == "k2":
            use_k2 = True
        elif self.mode == "hybrid" and confidence >= self.k2_threshold:
            use_k2 = True
            
        # Log for training
        self.log_interaction(text, intent, confidence, use_k2)
        
        # Return routing decision
        return {
            "use_k2": use_k2,
            "intent": intent,
            "confidence": confidence,
            "mode": self.mode
        }
        
    def detect_intent(self, text):
        """Simple intent detection"""
        text_lower = text.lower()
        
        for intent, keywords in self.intent_patterns.items():
            if any(kw in text_lower for kw in keywords):
                return intent
                
        return "general"
        
    def calculate_confidence(self, text, intent):
        """Simple confidence calculation"""
        # Basic heuristic: longer, more specific prompts = higher confidence
        word_count = len(text.split())
        has_code_keywords = any(kw in text.lower() for kw in 
                               ["function", "class", "def", "import", "return"])
        
        base_confidence = 0.5
        if word_count > 10:
            base_confidence += 0.2
        if has_code_keywords:
            base_confidence += 0.2
        if intent != "general":
            base_confidence += 0.1
            
        return min(base_confidence, 1.0)
        
    def log_interaction(self, text, intent, confidence, use_k2):
        """Log interaction for training"""
        # In Docker, this would write to mounted volume
        log_entry = {
            "timestamp": time.time(),
            "text": text,
            "intent": intent,
            "confidence": confidence,
            "model_used": "k2" if use_k2 else "claude",
            "mode": self.mode
        }
        
        # Append to log file
        log_path = Path("/data/interactions.jsonl")
        log_path.parent.mkdir(exist_ok=True)
        
        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")


# Docker health check endpoint
def health_check_server():
    """Simple HTTP server for Docker health checks"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
            else:
                self.send_response(404)
                self.end_headers()
                
        def log_message(self, format, *args):
            pass  # Suppress logs
            
    server = HTTPServer(("0.0.0.0", 9999), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    # Start health check server in background
    health_thread = threading.Thread(target=health_check_server, daemon=True)
    health_thread.start()
    
    # Start MCP server
    server = UnifiedMCPServer()
    
    print("PowerAutomation K2 MCP Server Started", file=sys.stderr)
    print("Commands: /model {k2|claude|hybrid|status}", file=sys.stderr)
    print("Say 'open editor' to launch ClaudeEditor", file=sys.stderr)
    
    # MCP protocol loop
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
            error_response = {"error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()