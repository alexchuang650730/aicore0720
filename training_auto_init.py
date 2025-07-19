#!/usr/bin/env python3
"""
訓練數據收集自動初始化
通過 Python 導入掛鉤實現完全自動啟動
"""

import sys
import os
from pathlib import Path

# 將此文件添加到 PYTHONPATH 或站點包中，實現自動導入

def install_import_hook():
    """安裝導入掛鉤"""
    try:
        # 檢查是否已經安裝
        if hasattr(sys, '_claude_training_hook_installed'):
            return
        
        # 標記已安裝
        sys._claude_training_hook_installed = True
        
        # 獲取項目根目錄
        current_file = Path(__file__)
        project_root = current_file.parent
        
        # 確保項目在 Python 路徑中
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # 嘗試啟動自動收集
        try:
            from auto_start_collection import setup_auto_collection
            setup_auto_collection()
        except ImportError:
            # 如果無法導入，嘗試直接設置
            os.environ['CLAUDE_CODE_TRAINING'] = '1'
        
    except Exception:
        # 靜默失敗，不影響正常使用
        pass

# 創建 .pth 文件內容以實現自動導入
PTH_CONTENT = f"""# Claude Code 訓練數據自動收集
import sys; sys.path.insert(0, r'{Path(__file__).parent}')
import training_auto_init; training_auto_init.install_import_hook()
"""

def setup_automatic_collection():
    """設置完全自動的收集系統"""
    
    methods = []
    
    # 方法1: 創建 .pth 文件（需要管理員權限）
    try:
        import site
        site_packages = site.getsitepackages()
        
        for sp in site_packages:
            if os.path.exists(sp) and os.access(sp, os.W_OK):
                pth_file = Path(sp) / "claude_training_auto.pth"
                try:
                    with open(pth_file, 'w', encoding='utf-8') as f:
                        f.write(PTH_CONTENT)
                    methods.append(f"✅ 已安裝 .pth 文件: {pth_file}")
                    break
                except Exception as e:
                    methods.append(f"❌ .pth 安裝失敗: {e}")
        else:
            methods.append("❌ 無權限創建 .pth 文件")
    
    except Exception as e:
        methods.append(f"❌ .pth 方法失敗: {e}")
    
    # 方法2: 環境變量 PYTHONPATH
    try:
        current_pythonpath = os.environ.get('PYTHONPATH', '')
        project_root = str(Path(__file__).parent)
        
        if project_root not in current_pythonpath:
            new_pythonpath = f"{project_root}{os.pathsep}{current_pythonpath}" if current_pythonpath else project_root
            
            # 創建啟動腳本
            startup_script = Path.home() / ".claude_code_training_setup.sh"
            script_content = f"""#!/bin/bash
# Claude Code 訓練數據收集環境設置
export PYTHONPATH="{new_pythonpath}"
export CLAUDE_CODE_TRAINING=1

# 如果是通過 shell 啟動，自動加載
if [ "${{SHELL##*/}}" = "bash" ] || [ "${{SHELL##*/}}" = "zsh" ]; then
    echo "🤖 Claude Code 訓練數據收集已啟用"
fi
"""
            
            with open(startup_script, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            os.chmod(startup_script, 0o755)
            methods.append(f"✅ 已創建啟動腳本: {startup_script}")
            
            # 提示用戶添加到 shell 配置
            shell_config = None
            if os.environ.get('SHELL', '').endswith('bash'):
                shell_config = Path.home() / ".bashrc"
            elif os.environ.get('SHELL', '').endswith('zsh'):
                shell_config = Path.home() / ".zshrc"
            
            if shell_config and shell_config.exists():
                source_line = f"source {startup_script}"
                try:
                    with open(shell_config, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if source_line not in content:
                        with open(shell_config, 'a', encoding='utf-8') as f:
                            f.write(f"\n# Claude Code 訓練數據收集\n{source_line}\n")
                        methods.append(f"✅ 已添加到 {shell_config}")
                    else:
                        methods.append(f"ℹ️ 已存在於 {shell_config}")
                        
                except Exception as e:
                    methods.append(f"⚠️ 無法自動添加到 {shell_config}: {e}")
                    methods.append(f"💡 請手動添加: echo 'source {startup_script}' >> {shell_config}")
        
    except Exception as e:
        methods.append(f"❌ 環境變量方法失敗: {e}")
    
    # 方法3: 創建符號鏈接到用戶站點包
    try:
        import site
        user_site = site.getusersitepackages()
        
        if user_site and os.path.exists(user_site):
            link_file = Path(user_site) / "claude_training_auto.py"
            source_file = Path(__file__).parent / "auto_start_collection.py"
            
            if not link_file.exists():
                try:
                    if os.name == 'nt':  # Windows
                        import shutil
                        shutil.copy2(source_file, link_file)
                    else:  # Unix/Linux/macOS
                        link_file.symlink_to(source_file)
                    
                    methods.append(f"✅ 已創建用戶站點包鏈接: {link_file}")
                except Exception as e:
                    methods.append(f"❌ 符號鏈接創建失敗: {e}")
    
    except Exception as e:
        methods.append(f"❌ 用戶站點包方法失敗: {e}")
    
    return methods

if __name__ == "__main__":
    print("🔧 設置 Claude Code 訓練數據自動收集...")
    print("=" * 60)
    
    # 安裝導入掛鉤
    install_import_hook()
    print("✅ 已安裝導入掛鉤")
    
    # 設置自動收集
    methods = setup_automatic_collection()
    
    print("\n📋 安裝結果:")
    for method in methods:
        print(f"   {method}")
    
    print(f"\n💡 建議:")
    print(f"   1. 重新啟動終端或執行: source ~/.bashrc (或 ~/.zshrc)")
    print(f"   2. 在新的 Claude Code 會話中，數據收集將自動啟動")
    print(f"   3. 可以通過設置 DISABLE_TRAINING_COLLECTION=1 來禁用")
    
    # 測試當前環境
    print(f"\n🧪 測試當前環境:")
    try:
        from auto_start_collection import is_claude_code_environment, setup_auto_collection
        
        is_claude = is_claude_code_environment()
        print(f"   Claude Code 環境: {'是' if is_claude else '否'}")
        
        if is_claude:
            success = setup_auto_collection()
            print(f"   自動啟動: {'成功' if success else '失敗'}")
    
    except Exception as e:
        print(f"   測試失敗: {e}")

# 如果被導入，自動安裝掛鉤
if __name__ != "__main__":
    install_import_hook()