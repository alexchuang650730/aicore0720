#!/usr/bin/env node
/**
 * PowerAutomation v4.6.9.7 - npm prepack 脚本
 * 在打包前进行必要的检查和准备
 */

const fs = require('fs');
const path = require('path');

// 颜色输出
const colors = {
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m'
};

function colorLog(color, message) {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkRequiredFiles() {
    const requiredFiles = [
        'core/components/claude_router_mcp/unified_mcp_server.py',
        'bin/powerautomation.js',
        'install_powerautomation_v4697.sh',
        'README.md',
        'LICENSE'
    ];
    
    let allFilesExist = true;
    
    colorLog('blue', '🔍 检查必需文件...');
    
    for (const file of requiredFiles) {
        if (fs.existsSync(file)) {
            colorLog('green', `  ✅ ${file}`);
        } else {
            colorLog('red', `  ❌ ${file} - 文件不存在`);
            allFilesExist = false;
        }
    }
    
    return allFilesExist;
}

function validatePackageJson() {
    colorLog('blue', '🔍 验证 package.json...');
    
    try {
        const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
        
        const requiredFields = ['name', 'version', 'description', 'main', 'bin', 'author', 'license'];
        let isValid = true;
        
        for (const field of requiredFields) {
            if (!packageJson[field]) {
                colorLog('red', `  ❌ 缺少必需字段: ${field}`);
                isValid = false;
            } else {
                colorLog('green', `  ✅ ${field}: ${typeof packageJson[field] === 'object' ? JSON.stringify(packageJson[field]) : packageJson[field]}`);
            }
        }
        
        return isValid;
        
    } catch (err) {
        colorLog('red', `❌ package.json 解析失败: ${err.message}`);
        return false;
    }
}

function checkExecutablePermissions() {
    colorLog('blue', '🔍 检查可执行文件权限...');
    
    const executableFiles = [
        'bin/powerautomation.js',
        'install_powerautomation_v4697.sh'
    ];
    
    let allExecutable = true;
    
    for (const file of executableFiles) {
        if (fs.existsSync(file)) {
            try {
                const stats = fs.statSync(file);
                const isExecutable = !!(stats.mode & parseInt('111', 8));
                
                if (isExecutable) {
                    colorLog('green', `  ✅ ${file} - 可执行`);
                } else {
                    colorLog('yellow', `  ⚠️ ${file} - 不可执行，正在修复...`);
                    fs.chmodSync(file, '755');
                    colorLog('green', `  ✅ ${file} - 权限已修复`);
                }
            } catch (err) {
                colorLog('red', `  ❌ ${file} - 权限检查失败: ${err.message}`);
                allExecutable = false;
            }
        }
    }
    
    return allExecutable;
}

function generateChangelog() {
    const changelogPath = 'CHANGELOG.md';
    
    if (!fs.existsSync(changelogPath)) {
        colorLog('blue', '📝 生成 CHANGELOG.md...');
        
        const changelog = `# Changelog

## [4.6.9.7] - ${new Date().toISOString().split('T')[0]}

### Added
- 统一 MCP 架构，整合所有相关组件
- Claude Code 同步服务，与 ClaudeEditor 无缝同步
- Claude 工具模式，完全避免模型推理余额消耗
- K2 服务路由，自动路由 AI 推理任务到 K2
- 一键安装脚本，支持 npm/curl 安装
- 统一命令行接口，简化操作

### Features
- ✅ 零余额消耗 - 完全避免 Claude 模型推理费用
- ✅ 无缝同步 - ClaudeEditor 和本地环境实时同步
- ✅ 智能路由 - AI 推理任务自动路由到 K2 服务
- ✅ 工具保留 - 保留所有 Claude 工具和指令功能
- ✅ 一键安装 - npm/curl 一键安装，开箱即用

### Technical
- 移除分散的组件目录，统一为 claude_router_mcp
- 优化 WebSocket 连接和 HTTP 回退机制
- 改进错误处理和日志记录
- 增强配置管理和状态监控

### Installation
\`\`\`bash
npm install -g powerautomation-unified
\`\`\`

### Usage
\`\`\`bash
powerautomation start
powerautomation status
powerautomation test
\`\`\`
`;
        
        fs.writeFileSync(changelogPath, changelog);
        colorLog('green', '✅ CHANGELOG.md 已生成');
    } else {
        colorLog('green', '✅ CHANGELOG.md 已存在');
    }
}

function main() {
    console.log('');
    console.log('==================================================================');
    colorLog('blue', '📦 PowerAutomation v4.6.9.7 - npm 打包前检查');
    console.log('==================================================================');
    console.log('');
    
    let success = true;
    
    // 检查必需文件
    if (!checkRequiredFiles()) {
        success = false;
    }
    
    console.log('');
    
    // 验证 package.json
    if (!validatePackageJson()) {
        success = false;
    }
    
    console.log('');
    
    // 检查可执行权限
    if (!checkExecutablePermissions()) {
        success = false;
    }
    
    console.log('');
    
    // 生成 CHANGELOG
    generateChangelog();
    
    console.log('');
    
    if (success) {
        colorLog('green', '🎉 打包前检查通过，准备发布！');
        console.log('==================================================================');
    } else {
        colorLog('red', '❌ 打包前检查失败，请修复上述问题后重试');
        console.log('==================================================================');
        process.exit(1);
    }
}

// 只在直接运行时执行
if (require.main === module) {
    main();
}

module.exports = { main };

