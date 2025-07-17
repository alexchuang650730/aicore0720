#!/usr/bin/env python3
"""
PowerAutomation 安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="powerautomation",
    version="1.0.0",
    author="Alex Chuang",
    author_email="alex.chuang@powerautomation.ai",
    description="业界领先的个人/企业工作流自动化解决方案",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexchuang650730/aicore0718",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "full": [
            "claude-code",
            "openai",
            "anthropic",
        ],
    },
    entry_points={
        "console_scripts": [
            "powerautomation=core.powerautomation_core_driver:main",
            "claudeditor=claude_code_integration.claudeditor_enhanced:main",
            "mcp-server=mcp_server.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yaml", "*.yml", "*.json", "*.html", "*.css", "*.js"],
    },
    project_urls={
        "Bug Reports": "https://github.com/alexchuang650730/aicore0718/issues",
        "Source": "https://github.com/alexchuang650730/aicore0718",
        "Documentation": "https://github.com/alexchuang650730/aicore0718/blob/main/README.md",
    },
)