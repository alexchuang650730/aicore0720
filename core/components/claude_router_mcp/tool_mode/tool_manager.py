#!/usr/bin/env python3
"""
Tool Mode Manager - Claude 工具模式管理器
管理 Claude 工具模式，确保只使用工具功能，避免模型推理消耗
"""

import json
import logging
import os
import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ToolModeConfig:
    """工具模式配置"""
    enabled: bool = True
    disable_model_inference: bool = True
    allow_tools_only: bool = True
    route_ai_requests_to_k2: bool = True
    blocked_endpoints: List[str] = None
    allowed_tools: List[str] = None
    
    def __post_init__(self):
        if self.blocked_endpoints is None:
            self.blocked_endpoints = [
                "/v1/messages",
                "/v1/chat/completions", 
                "/v1/completions"
            ]
        if self.allowed_tools is None:
            self.allowed_tools = [
                "file_read", "file_write", "file_append", "file_replace",
                "shell_exec", "shell_view", "shell_wait", "shell_input",
                "browser_navigate", "browser_view", "browser_click",
                "browser_input", "browser_scroll_up", "browser_scroll_down",
                "media_generate_image", "media_generate_video",
                "info_search_web", "info_search_image"
            ]

class ToolModeManager:
    """Claude 工具模式管理器"""
    
    def __init__(self, config_path: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 配置文件路径
        self.config_path = config_path or os.path.expanduser("~/.powerautomation/tool_mode.json")
        
        # 确保配置目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        
        # 统计信息
        self.stats = {
            "blocked_requests": 0,
            "allowed_tools": 0,
            "k2_routes": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # 请求历史
        self.request_history = []
        self.max_history_size = 100
        
        self.logger.info(f"已加载 Claude 工具模式配置: {self.config_path}")
    
    def _load_config(self) -> ToolModeConfig:
        """加载配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return ToolModeConfig(**data)
            else:
                # 创建默认配置
                config = ToolModeConfig()
                self._save_config(config)
                return config
                
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            return ToolModeConfig()
    
    def _save_config(self, config: ToolModeConfig = None):
        """保存配置"""
        try:
            config = config or self.config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"已保存 Claude 工具模式配置: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
    
    def enable_tool_mode(self):
        """启用工具模式"""
        self.config.enabled = True
        self.config.disable_model_inference = True
        self.config.allow_tools_only = True
        self.config.route_ai_requests_to_k2 = True
        
        self._save_config()
        self.logger.info("🔧 已启用 Claude 工具模式")
    
    def disable_tool_mode(self):
        """禁用工具模式"""
        self.config.enabled = False
        self.config.disable_model_inference = False
        self.config.allow_tools_only = False
        self.config.route_ai_requests_to_k2 = False
        
        self._save_config()
        self.logger.info("🔓 已禁用 Claude 工具模式")
    
    def is_tool_mode_enabled(self) -> bool:
        """检查工具模式是否启用"""
        return self.config.enabled
    
    def is_model_inference_disabled(self) -> bool:
        """检查模型推理是否被禁用"""
        return self.config.disable_model_inference
    
    def should_route_to_k2(self, request_type: str) -> bool:
        """检查是否应该路由到 K2 服务"""
        if not self.config.route_ai_requests_to_k2:
            return False
        
        # AI 推理相关的请求类型
        ai_request_types = {
            "chat_completion", "text_generation", "code_generation",
            "analysis", "summarization", "translation", "question_answering"
        }
        
        return request_type in ai_request_types
    
    def is_endpoint_blocked(self, endpoint: str) -> bool:
        """检查端点是否被阻止"""
        if not self.config.enabled:
            return False
        
        for blocked_endpoint in self.config.blocked_endpoints:
            if endpoint.startswith(blocked_endpoint):
                self.stats["blocked_requests"] += 1
                self._add_to_history("blocked_endpoint", endpoint)
                return True
        
        return False
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """检查工具是否被允许"""
        if not self.config.enabled:
            return True
        
        if not self.config.allow_tools_only:
            return True
        
        allowed = tool_name in self.config.allowed_tools
        
        if allowed:
            self.stats["allowed_tools"] += 1
            self._add_to_history("allowed_tool", tool_name)
        else:
            self._add_to_history("blocked_tool", tool_name)
        
        return allowed
    
    def intercept_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """拦截请求"""
        try:
            # 检查是否启用工具模式
            if not self.config.enabled:
                return {"action": "allow", "reason": "工具模式未启用"}
            
            # 获取请求信息
            endpoint = request_data.get("endpoint", "")
            method = request_data.get("method", "")
            headers = request_data.get("headers", {})
            body = request_data.get("body", {})
            
            # 检查端点是否被阻止
            if self.is_endpoint_blocked(endpoint):
                return {
                    "action": "block",
                    "reason": f"端点被阻止: {endpoint}",
                    "alternative": "route_to_k2"
                }
            
            # 检查是否为工具请求
            if self._is_tool_request(request_data):
                tool_name = self._extract_tool_name(request_data)
                
                if self.is_tool_allowed(tool_name):
                    return {"action": "allow", "reason": f"允许工具: {tool_name}"}
                else:
                    return {"action": "block", "reason": f"工具未被允许: {tool_name}"}
            
            # 检查是否为 AI 推理请求
            if self._is_ai_inference_request(request_data):
                if self.config.disable_model_inference:
                    request_type = self._extract_request_type(request_data)
                    
                    if self.should_route_to_k2(request_type):
                        self.stats["k2_routes"] += 1
                        self._add_to_history("k2_route", request_type)
                        
                        return {
                            "action": "route_to_k2",
                            "reason": f"路由 AI 推理到 K2: {request_type}",
                            "request_type": request_type,
                            "content": self._extract_content(request_data)
                        }
                    else:
                        return {
                            "action": "block",
                            "reason": "模型推理被禁用"
                        }
            
            # 默认允许
            return {"action": "allow", "reason": "默认允许"}
            
        except Exception as e:
            self.logger.error(f"请求拦截失败: {e}")
            return {"action": "allow", "reason": f"拦截器错误: {str(e)}"}
    
    def _is_tool_request(self, request_data: Dict[str, Any]) -> bool:
        """检查是否为工具请求"""
        # 检查 URL 路径
        endpoint = request_data.get("endpoint", "")
        if "/tools" in endpoint or "/functions" in endpoint:
            return True
        
        # 检查请求体
        body = request_data.get("body", {})
        if "tools" in body or "functions" in body:
            return True
        
        # 检查 Content-Type
        headers = request_data.get("headers", {})
        content_type = headers.get("content-type", "")
        if "application/vnd.anthropic.tool" in content_type:
            return True
        
        return False
    
    def _extract_tool_name(self, request_data: Dict[str, Any]) -> str:
        """提取工具名称"""
        try:
            body = request_data.get("body", {})
            
            # 从工具调用中提取
            if "tools" in body:
                tools = body["tools"]
                if isinstance(tools, list) and len(tools) > 0:
                    return tools[0].get("name", "unknown_tool")
            
            # 从函数调用中提取
            if "functions" in body:
                functions = body["functions"]
                if isinstance(functions, list) and len(functions) > 0:
                    return functions[0].get("name", "unknown_function")
            
            # 从 URL 中提取
            endpoint = request_data.get("endpoint", "")
            if "/tools/" in endpoint:
                parts = endpoint.split("/tools/")
                if len(parts) > 1:
                    return parts[1].split("/")[0]
            
            return "unknown_tool"
            
        except Exception as e:
            self.logger.error(f"提取工具名称失败: {e}")
            return "unknown_tool"
    
    def _is_ai_inference_request(self, request_data: Dict[str, Any]) -> bool:
        """检查是否为 AI 推理请求"""
        endpoint = request_data.get("endpoint", "")
        
        # 检查端点
        ai_endpoints = ["/v1/messages", "/v1/chat/completions", "/v1/completions"]
        for ai_endpoint in ai_endpoints:
            if endpoint.startswith(ai_endpoint):
                return True
        
        # 检查请求体
        body = request_data.get("body", {})
        if "messages" in body or "prompt" in body:
            return True
        
        return False
    
    def _extract_request_type(self, request_data: Dict[str, Any]) -> str:
        """提取请求类型"""
        endpoint = request_data.get("endpoint", "")
        
        if "/chat/completions" in endpoint:
            return "chat_completion"
        elif "/completions" in endpoint:
            return "text_generation"
        elif "/messages" in endpoint:
            return "chat_completion"
        else:
            return "unknown_ai_request"
    
    def _extract_content(self, request_data: Dict[str, Any]) -> str:
        """提取请求内容"""
        try:
            body = request_data.get("body", {})
            
            # 从消息中提取
            if "messages" in body:
                messages = body["messages"]
                if isinstance(messages, list) and len(messages) > 0:
                    last_message = messages[-1]
                    return last_message.get("content", "")
            
            # 从提示中提取
            if "prompt" in body:
                return body["prompt"]
            
            return ""
            
        except Exception as e:
            self.logger.error(f"提取请求内容失败: {e}")
            return ""
    
    def _add_to_history(self, action: str, details: str):
        """添加到历史记录"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        
        self.request_history.append(history_entry)
        
        # 保持历史大小限制
        if len(self.request_history) > self.max_history_size:
            self.request_history.pop(0)
    
    def add_allowed_tool(self, tool_name: str):
        """添加允许的工具"""
        if tool_name not in self.config.allowed_tools:
            self.config.allowed_tools.append(tool_name)
            self._save_config()
            self.logger.info(f"添加允许的工具: {tool_name}")
    
    def remove_allowed_tool(self, tool_name: str):
        """移除允许的工具"""
        if tool_name in self.config.allowed_tools:
            self.config.allowed_tools.remove(tool_name)
            self._save_config()
            self.logger.info(f"移除允许的工具: {tool_name}")
    
    def add_blocked_endpoint(self, endpoint: str):
        """添加阻止的端点"""
        if endpoint not in self.config.blocked_endpoints:
            self.config.blocked_endpoints.append(endpoint)
            self._save_config()
            self.logger.info(f"添加阻止的端点: {endpoint}")
    
    def remove_blocked_endpoint(self, endpoint: str):
        """移除阻止的端点"""
        if endpoint in self.config.blocked_endpoints:
            self.config.blocked_endpoints.remove(endpoint)
            self._save_config()
            self.logger.info(f"移除阻止的端点: {endpoint}")
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return asdict(self.config)
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"更新配置: {key} = {value}")
        
        self._save_config()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds()
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "config": asdict(self.config)
        }
    
    def get_recent_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取最近的历史记录"""
        return self.request_history[-limit:] if self.request_history else []
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "blocked_requests": 0,
            "allowed_tools": 0,
            "k2_routes": 0,
            "start_time": datetime.now().isoformat()
        }
        self.request_history.clear()
        self.logger.info("统计信息已重置")


# 全局工具模式管理器实例
tool_mode_manager = ToolModeManager()


def get_tool_mode_manager() -> ToolModeManager:
    """获取工具模式管理器实例"""
    return tool_mode_manager


# CLI 接口
if __name__ == "__main__":
    import argparse
    import sys
    
    def main():
        parser = argparse.ArgumentParser(description="Claude 工具模式管理器")
        parser.add_argument("--action", choices=["enable", "disable", "status", "config", "test"], 
                           default="status", help="执行的动作")
        parser.add_argument("--tool", type=str, help="工具名称（用于添加/移除）")
        parser.add_argument("--endpoint", type=str, help="端点（用于添加/移除）")
        parser.add_argument("--add", action="store_true", help="添加工具或端点")
        parser.add_argument("--remove", action="store_true", help="移除工具或端点")
        
        args = parser.parse_args()
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        
        manager = ToolModeManager()
        
        if args.action == "enable":
            manager.enable_tool_mode()
            print("✅ Claude 工具模式已启用")
        
        elif args.action == "disable":
            manager.disable_tool_mode()
            print("❌ Claude 工具模式已禁用")
        
        elif args.action == "status":
            stats = manager.get_stats()
            print("📊 Claude 工具模式状态:")
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif args.action == "config":
            config = manager.get_config()
            print("⚙️ Claude 工具模式配置:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
        
        elif args.action == "test":
            print("🧪 测试工具模式拦截...")
            
            # 测试工具请求
            tool_request = {
                "endpoint": "/v1/tools/file_read",
                "method": "POST",
                "body": {"tools": [{"name": "file_read"}]}
            }
            
            result = manager.intercept_request(tool_request)
            print(f"工具请求结果: {result}")
            
            # 测试 AI 推理请求
            ai_request = {
                "endpoint": "/v1/messages",
                "method": "POST",
                "body": {"messages": [{"role": "user", "content": "Hello"}]}
            }
            
            result = manager.intercept_request(ai_request)
            print(f"AI 推理请求结果: {result}")
        
        # 工具管理
        if args.tool:
            if args.add:
                manager.add_allowed_tool(args.tool)
                print(f"✅ 已添加允许的工具: {args.tool}")
            elif args.remove:
                manager.remove_allowed_tool(args.tool)
                print(f"❌ 已移除允许的工具: {args.tool}")
        
        # 端点管理
        if args.endpoint:
            if args.add:
                manager.add_blocked_endpoint(args.endpoint)
                print(f"✅ 已添加阻止的端点: {args.endpoint}")
            elif args.remove:
                manager.remove_blocked_endpoint(args.endpoint)
                print(f"❌ 已移除阻止的端点: {args.endpoint}")
    
    main()

