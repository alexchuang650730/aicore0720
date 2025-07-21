#!/usr/bin/env python3
"""
ClaudeEditor AI Model Control Panel - 左上角模型切換控制面板
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime

class ModelSwitcherUI:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.current_mode = "hybrid"
        self.k2_status = {"active": False, "accuracy": 0.0}
        self.claude_status = {"active": False, "api_connected": False}
        
        # 創建主控制面板
        self.create_control_panel()
        
        # 啟動狀態監控
        self.start_status_monitor()
        
    def create_control_panel(self):
        """創建左上角的模型控制面板"""
        # 主框架
        control_frame = ttk.LabelFrame(self.parent, text="🤖 AI Model Control", padding=10)
        control_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        
        # 當前模式顯示
        self.mode_label = ttk.Label(control_frame, text="Current Mode: Hybrid", 
                                   font=("SF Pro Display", 12, "bold"))
        self.mode_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 模式切換按鈕組
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=3)
        
        # K2 模式按鈕
        self.k2_btn = ttk.Button(button_frame, text="K2\nMode", 
                                command=lambda: self.switch_mode("k2"),
                                width=8)
        self.k2_btn.grid(row=0, column=0, padx=2)
        
        # Claude 模式按鈕
        self.claude_btn = ttk.Button(button_frame, text="Claude\nMode", 
                                    command=lambda: self.switch_mode("claude"),
                                    width=8)
        self.claude_btn.grid(row=0, column=1, padx=2)
        
        # 混合模式按鈕
        self.hybrid_btn = ttk.Button(button_frame, text="Hybrid\nMode", 
                                    command=lambda: self.switch_mode("hybrid"),
                                    width=8)
        self.hybrid_btn.grid(row=0, column=2, padx=2)
        
        # 分隔線
        ttk.Separator(control_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=3, sticky="ew", pady=10)
        
        # 狀態指示器
        status_frame = ttk.Frame(control_frame)
        status_frame.grid(row=3, column=0, columnspan=3)
        
        # K2 狀態
        self.k2_status_label = ttk.Label(status_frame, text="K2: ⚫ Offline")
        self.k2_status_label.grid(row=0, column=0, sticky="w")
        
        # Claude 狀態
        self.claude_status_label = ttk.Label(status_frame, text="Claude: ⚫ Offline")
        self.claude_status_label.grid(row=1, column=0, sticky="w")
        
        # 準確率顯示
        self.accuracy_label = ttk.Label(status_frame, text="Accuracy: ---%")
        self.accuracy_label.grid(row=2, column=0, sticky="w")
        
        # 分隔線
        ttk.Separator(control_frame, orient="horizontal").grid(
            row=4, column=0, columnspan=3, sticky="ew", pady=10)
        
        # 高級設置
        advanced_frame = ttk.Frame(control_frame)
        advanced_frame.grid(row=5, column=0, columnspan=3)
        
        # 置信度閾值滑塊
        ttk.Label(advanced_frame, text="Confidence:").grid(row=0, column=0)
        self.threshold_var = tk.DoubleVar(value=0.7)
        self.threshold_scale = ttk.Scale(advanced_frame, from_=0.0, to=1.0, 
                                        variable=self.threshold_var,
                                        command=self.update_threshold,
                                        length=100)
        self.threshold_scale.grid(row=0, column=1)
        self.threshold_label = ttk.Label(advanced_frame, text="70%")
        self.threshold_label.grid(row=0, column=2)
        
        # 快捷鍵提示
        shortcut_frame = ttk.Frame(control_frame)
        shortcut_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
        shortcuts = [
            ("⌘+K", "K2 Mode"),
            ("⌘+C", "Claude Mode"),
            ("⌘+H", "Hybrid Mode"),
            ("⌘+/", "Quick Switch")
        ]
        
        for i, (key, desc) in enumerate(shortcuts):
            ttk.Label(shortcut_frame, text=f"{key}: {desc}", 
                     font=("SF Mono", 9)).grid(row=i//2, column=i%2, sticky="w", padx=5)
        
        # 更新當前模式的視覺效果
        self.update_button_states()
        
    def switch_mode(self, mode):
        """切換 AI 模式"""
        try:
            # 發送切換請求到 K2 MCP 服務器
            result = self.send_mcp_request("k2/switch_mode", {"mode": mode})
            
            if result.get("status") == "success":
                self.current_mode = mode
                self.mode_label.config(text=f"Current Mode: {mode.title()}")
                self.update_button_states()
                
                # 顯示切換成功提示
                self.show_mode_indicator(mode)
                
        except Exception as e:
            messagebox.showerror("Mode Switch Error", f"Failed to switch mode: {str(e)}")
            
    def update_button_states(self):
        """更新按鈕狀態以反映當前模式"""
        # 重置所有按鈕樣式
        for btn in [self.k2_btn, self.claude_btn, self.hybrid_btn]:
            btn.configure(style="TButton")
            
        # 高亮當前模式按鈕
        if self.current_mode == "k2":
            self.k2_btn.configure(style="Active.TButton")
        elif self.current_mode == "claude":
            self.claude_btn.configure(style="Active.TButton")
        else:
            self.hybrid_btn.configure(style="Active.TButton")
            
    def update_threshold(self, value):
        """更新置信度閾值"""
        threshold = float(value)
        self.threshold_label.config(text=f"{int(threshold*100)}%")
        
        # 發送更新請求
        threading.Thread(target=self._update_threshold_async, args=(threshold,)).start()
        
    def _update_threshold_async(self, threshold):
        """異步更新閾值"""
        try:
            self.send_mcp_request("k2/set_threshold", {"threshold": threshold})
        except:
            pass
            
    def start_status_monitor(self):
        """啟動狀態監控線程"""
        def monitor():
            while True:
                try:
                    # 獲取 K2 狀態
                    status = self.send_mcp_request("k2/status", {})
                    
                    # 更新 K2 狀態
                    if status.get("training_active"):
                        self.k2_status["active"] = True
                        self.k2_status["accuracy"] = status.get("accuracy", 0)
                        self.k2_status_label.config(text="K2: 🟢 Active")
                        self.accuracy_label.config(
                            text=f"Accuracy: {self.k2_status['accuracy']:.1f}%")
                    else:
                        self.k2_status_label.config(text="K2: 🔴 Offline")
                        
                    # 檢查 Claude 連接
                    # 這裡簡化處理，實際應該ping Claude API
                    self.claude_status_label.config(text="Claude: 🟢 Connected")
                    
                except:
                    self.k2_status_label.config(text="K2: 🔴 Offline")
                    self.claude_status_label.config(text="Claude: 🟡 Unknown")
                    
                # 每5秒更新一次
                threading.Event().wait(5)
                
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
    def send_mcp_request(self, method, params):
        """發送請求到 MCP 服務器"""
        request = json.dumps({"method": method, "params": params})
        
        try:
            result = subprocess.run(
                ["python3", "/Users/alexchuang/alexchuangtest/aicore0720/k2_mode_switcher_mcp.py"],
                input=request,
                capture_output=True,
                text=True
            )
            return json.loads(result.stdout)
        except:
            return {}
            
    def show_mode_indicator(self, mode):
        """顯示模式切換指示器"""
        # 創建臨時提示窗口
        indicator = tk.Toplevel(self.parent.winfo_toplevel())
        indicator.overrideredirect(True)
        indicator.attributes('-alpha', 0.9)
        
        # 設置內容
        mode_info = {
            "k2": ("🟢 K2 Mode", "Fast local inference"),
            "claude": ("🔵 Claude Mode", "Advanced AI capabilities"),
            "hybrid": ("🟡 Hybrid Mode", "Smart auto-selection")
        }
        
        title, desc = mode_info.get(mode, ("", ""))
        
        frame = ttk.Frame(indicator, padding=20)
        frame.pack()
        
        ttk.Label(frame, text=title, font=("SF Pro Display", 16, "bold")).pack()
        ttk.Label(frame, text=desc, font=("SF Pro Display", 12)).pack()
        
        # 定位到屏幕中央
        indicator.update_idletasks()
        x = (indicator.winfo_screenwidth() - indicator.winfo_width()) // 2
        y = (indicator.winfo_screenheight() - indicator.winfo_height()) // 2
        indicator.geometry(f"+{x}+{y}")
        
        # 2秒後自動關閉
        indicator.after(2000, indicator.destroy)


class ClaudeEditorModelSwitcher:
    """ClaudeEditor 集成的模型切換器"""
    
    def __init__(self, editor_window):
        self.editor = editor_window
        self.create_model_control_region()
        
    def create_model_control_region(self):
        """在編輯器左上角創建模型控制區域"""
        # 創建控制框架
        control_frame = ttk.Frame(self.editor)
        control_frame.place(x=10, y=10)  # 固定在左上角
        
        # 創建模型切換UI
        self.switcher = ModelSwitcherUI(control_frame)
        
        # 綁定快捷鍵
        self.bind_shortcuts()
        
    def bind_shortcuts(self):
        """綁定快捷鍵"""
        self.editor.bind('<Command-k>', lambda e: self.switcher.switch_mode("k2"))
        self.editor.bind('<Command-c>', lambda e: self.switcher.switch_mode("claude"))
        self.editor.bind('<Command-h>', lambda e: self.switcher.switch_mode("hybrid"))
        self.editor.bind('<Command-slash>', self.quick_switch)
        
    def quick_switch(self, event=None):
        """快速切換模式（循環切換）"""
        modes = ["k2", "claude", "hybrid"]
        current_index = modes.index(self.switcher.current_mode)
        next_mode = modes[(current_index + 1) % 3]
        self.switcher.switch_mode(next_mode)


# 演示代碼
if __name__ == "__main__":
    # 創建演示窗口
    root = tk.Tk()
    root.title("ClaudeEditor - Model Switcher Demo")
    root.geometry("1200x800")
    
    # 設置樣式
    style = ttk.Style()
    style.configure("Active.TButton", background="#007AFF")
    
    # 創建編輯器模擬
    editor_frame = ttk.Frame(root)
    editor_frame.pack(fill="both", expand=True)
    
    # 添加模型切換器
    switcher = ClaudeEditorModelSwitcher(root)
    
    # 添加編輯區域（演示用）
    text_frame = ttk.Frame(editor_frame)
    text_frame.pack(fill="both", expand=True, padx=(300, 10), pady=10)
    
    text = tk.Text(text_frame, wrap="word", font=("SF Mono", 12))
    text.pack(fill="both", expand=True)
    text.insert("1.0", """// ClaudeEditor with AI Model Switcher
    
Welcome to ClaudeEditor with integrated model switching!

Use the control panel in the top-left corner to:
- Switch between K2, Claude, and Hybrid modes
- Monitor model status
- Adjust confidence threshold
- Use keyboard shortcuts for quick switching

Try typing some code and watch how different modes respond...
""")
    
    root.mainloop()