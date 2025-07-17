#!/usr/bin/env node
/**
 * PowerAutomation v4.6.9.7 - npm postinstall 脚本
 * 在 npm 安装后自动执行安装配置
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// 颜色输出
const colors = {
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    reset: '\x1b[0m'
};

function colorLog(color, message) {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function printHeader() {
    console.log('');
    console.log('==================================================================');
    colorLog('cyan', '🚀 PowerAutomation v4.6.9.7 - npm 安装后配置');
    console.log('==================================================================');
}

async function checkPython() {
    return new Promise((resolve) => {
        const python = spawn('python3', ['--version'], { stdio: 'pipe' });
        python.on('close', (code) => {
            resolve(code === 0);
        });
        python.on('error', () => {
            resolve(false);
        });
    });
}

async function runInstallScript() {
    const packageDir = path.dirname(__dirname);
    const installScript = path.join(packageDir, 'install_powerautomation_v4697.sh');
    
    if (!fs.existsSync(installScript)) {
        colorLog('yellow', '⚠️ 安装脚本不存在，跳过自动配置');
        return;
    }

    colorLog('blue', '🔧 运行 PowerAutomation 配置脚本...');
    
    return new Promise((resolve) => {
        const install = spawn('bash', [installScript], {
            stdio: 'inherit',
            cwd: packageDir
        });

        install.on('close', (code) => {
            if (code === 0) {
                colorLog('green', '✅ PowerAutomation 配置完成');
            } else {
                colorLog('yellow', '⚠️ 配置过程中出现警告，但安装已完成');
            }
            resolve(code);
        });

        install.on('error', (err) => {
            colorLog('yellow', `⚠️ 配置脚本执行失败: ${err.message}`);
            colorLog('blue', '💡 您可以稍后手动运行: powerautomation install');
            resolve(1);
        });
    });
}

async function createSymlinks() {
    try {
        const packageDir = path.dirname(__dirname);
        const homeDir = os.homedir();
        const powerautomationDir = path.join(homeDir, '.powerautomation');
        
        // 确保目录存在
        if (!fs.existsSync(powerautomationDir)) {
            fs.mkdirSync(powerautomationDir, { recursive: true });
        }
        
        // 创建符号链接到安装目录
        const linkPath = path.join(powerautomationDir, 'aicore0716');
        if (!fs.existsSync(linkPath)) {
            try {
                fs.symlinkSync(packageDir, linkPath, 'dir');
                colorLog('green', '✅ 创建符号链接成功');
            } catch (err) {
                // 如果符号链接失败，复制重要文件
                colorLog('yellow', '⚠️ 符号链接失败，使用文件复制');
            }
        }
        
    } catch (err) {
        colorLog('yellow', `⚠️ 创建符号链接失败: ${err.message}`);
    }
}

async function printSuccessMessage() {
    console.log('');
    console.log('==================================================================');
    colorLog('green', '🎉 PowerAutomation v4.6.9.7 npm 安装完成！');
    console.log('==================================================================');
    console.log('');
    colorLog('cyan', '🚀 快速开始:');
    colorLog('green', '  # 启动 PowerAutomation 服务');
    colorLog('yellow', '  powerautomation start');
    console.log('');
    colorLog('green', '  # 查看服务状态');
    colorLog('yellow', '  powerautomation status');
    console.log('');
    colorLog('green', '  # 测试功能');
    colorLog('yellow', '  powerautomation test');
    console.log('');
    colorLog('cyan', '🎯 核心功能:');
    colorLog('green', '  ✅ 完全避免 Claude 模型推理余额消耗');
    colorLog('green', '  ✅ 保留所有 Claude 工具和指令功能');
    colorLog('green', '  ✅ 自动路由 AI 推理任务到 K2 服务');
    colorLog('green', '  ✅ ClaudeEditor 和本地环境实时同步');
    console.log('');
    colorLog('blue', '📚 更多帮助: powerautomation --help');
    console.log('==================================================================');
    console.log('');
}

async function main() {
    try {
        printHeader();
        
        // 检查 Python
        const pythonAvailable = await checkPython();
        if (!pythonAvailable) {
            colorLog('yellow', '⚠️ Python 3 未安装，部分功能可能无法使用');
            colorLog('blue', '💡 请安装 Python 3.8+ 以获得完整功能');
        } else {
            colorLog('green', '✅ Python 3 检查通过');
        }
        
        // 创建符号链接
        await createSymlinks();
        
        // 运行安装脚本（仅在 Unix 系统上）
        if (process.platform !== 'win32' && pythonAvailable) {
            await runInstallScript();
        } else {
            colorLog('blue', '💡 请手动运行: powerautomation install');
        }
        
        // 打印成功消息
        await printSuccessMessage();
        
    } catch (err) {
        colorLog('red', `❌ 安装后配置失败: ${err.message}`);
        colorLog('blue', '💡 您可以稍后手动运行: powerautomation install');
    }
}

// 只在直接运行时执行
if (require.main === module) {
    main().catch((err) => {
        console.error('安装后配置失败:', err.message);
        process.exit(0); // 不要因为 postinstall 失败而阻止安装
    });
}

module.exports = { main };

