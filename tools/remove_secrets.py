#!/usr/bin/env python3
"""
移除代碼中的敏感信息
"""

import os
import re
from pathlib import Path

def remove_secrets_from_file(file_path):
    """從文件中移除敏感信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替換各種API密鑰模式
        patterns = [
            # Groq API Key
            (r'gsk_[A-Za-z0-9]{48,}', 'os.getenv("GROQ_API_KEY", "")'),
            # Hugging Face Token
            (r'hf_[A-Za-z0-9]{30,}', 'os.getenv("HF_TOKEN", "")'),
            # Anthropic API Key
            (r'sk-ant-[A-Za-z0-9\-]{90,}', 'os.getenv("ANTHROPIC_API_KEY", "")'),
            # Moonshot API Key
            (r'sk-[A-Za-z0-9]{48,}', 'os.getenv("MOONSHOT_API_KEY", "")'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # 如果內容有變化，寫回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已清理: {file_path}")
            return True
    except Exception as e:
        print(f"❌ 處理失敗 {file_path}: {e}")
    
    return False

def main():
    """主函數"""
    # 需要檢查的文件列表（從GitHub錯誤信息中提取）
    files_to_check = [
        "core/mcp_config.py",
        "integrate_optimizations_to_mcp.py",
        "test_groq_active_models.py",
        "test_k2_providers_complete.py",
        "one_click_setup_with_k2_binding.py",
        "powerautomation",
        "test_groq_k2_integration.py",
        "test_k2_vs_claude_tool_calling.py"
    ]
    
    cleaned_count = 0
    
    for file_path in files_to_check:
        full_path = Path(file_path)
        if full_path.exists():
            if remove_secrets_from_file(full_path):
                cleaned_count += 1
    
    print(f"\n總共清理了 {cleaned_count} 個文件")
    
    # 創建環境變量模板文件
    env_template = """# PowerAutomation 環境變量模板
# 請複製此文件為 .env 並填入您的API密鑰

# Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# Hugging Face Token
HF_TOKEN=your_huggingface_token_here

# Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Moonshot API Key
MOONSHOT_API_KEY=your_moonshot_api_key_here

# AWS 配置（可選）
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION=us-east-1
"""
    
    with open(".env.template", "w") as f:
        f.write(env_template)
    
    print("\n✅ 已創建 .env.template 文件")
    print("請複製為 .env 並填入您的API密鑰")

if __name__ == "__main__":
    main()