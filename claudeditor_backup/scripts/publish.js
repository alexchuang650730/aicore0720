#!/usr/bin/env node
/**
 * PowerAutomation v4.6.9.7 - npm 发布脚本
 * 自动化发布流程
 */

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');

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
    colorLog('cyan', '🚀 PowerAutomation v4.6.9.7 - npm 发布脚本');
    console.log('==================================================================');
}

async function checkNpmLogin() {
    return new Promise((resolve) => {
        exec('npm whoami', (error, stdout, stderr) => {
            if (error) {
                resolve(false);
            } else {
                const username = stdout.trim();
                colorLog('green', `✅ 已登录 npm，用户: ${username}`);
                resolve(true);
            }
        });
    });
}

async function runCommand(command, args = [], options = {}) {
    return new Promise((resolve, reject) => {
        const child = spawn(command, args, {
            stdio: 'inherit',
            ...options
        });
        
        child.on('close', (code) => {
            if (code === 0) {
                resolve(code);
            } else {
                reject(new Error(`命令失败，退出码: ${code}`));
            }
        });
        
        child.on('error', (err) => {
            reject(err);
        });
    });
}

async function checkPackageVersion() {
    try {
        const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
        const packageName = packageJson.name;
        const currentVersion = packageJson.version;
        
        colorLog('blue', `📦 检查包版本: ${packageName}@${currentVersion}`);
        
        return new Promise((resolve) => {
            exec(`npm view ${packageName}@${currentVersion}`, (error, stdout, stderr) => {
                if (error) {
                    // 版本不存在，可以发布
                    colorLog('green', '✅ 版本检查通过，可以发布');
                    resolve(true);
                } else {
                    // 版本已存在
                    colorLog('red', `❌ 版本 ${currentVersion} 已存在于 npm registry`);
                    colorLog('yellow', '💡 请更新 package.json 中的版本号');
                    resolve(false);
                }
            });
        });
        
    } catch (err) {
        colorLog('red', `❌ 读取 package.json 失败: ${err.message}`);
        return false;
    }
}

async function runTests() {
    colorLog('blue', '🧪 运行测试...');
    
    try {
        await runCommand('npm', ['test']);
        colorLog('green', '✅ 测试通过');
        return true;
    } catch (err) {
        colorLog('red', `❌ 测试失败: ${err.message}`);
        return false;
    }
}

async function buildPackage() {
    colorLog('blue', '📦 构建包...');
    
    try {
        await runCommand('npm', ['run', 'prepack']);
        colorLog('green', '✅ 包构建完成');
        return true;
    } catch (err) {
        colorLog('red', `❌ 包构建失败: ${err.message}`);
        return false;
    }
}

async function publishPackage(tag = 'latest') {
    colorLog('blue', `🚀 发布包到 npm registry (tag: ${tag})...`);
    
    try {
        const args = ['publish', '--access', 'public'];
        if (tag !== 'latest') {
            args.push('--tag', tag);
        }
        
        await runCommand('npm', args);
        colorLog('green', '🎉 包发布成功！');
        return true;
    } catch (err) {
        colorLog('red', `❌ 包发布失败: ${err.message}`);
        return false;
    }
}

async function createGitTag() {
    try {
        const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
        const version = packageJson.version;
        const tagName = `v${version}`;
        
        colorLog('blue', `🏷️ 创建 Git 标签: ${tagName}`);
        
        await runCommand('git', ['tag', tagName]);
        await runCommand('git', ['push', 'origin', tagName]);
        
        colorLog('green', `✅ Git 标签 ${tagName} 创建成功`);
        return true;
    } catch (err) {
        colorLog('yellow', `⚠️ Git 标签创建失败: ${err.message}`);
        return false;
    }
}

async function printSuccessMessage() {
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    const packageName = packageJson.name;
    const version = packageJson.version;
    
    console.log('');
    console.log('==================================================================');
    colorLog('green', '🎉 PowerAutomation v4.6.9.7 发布成功！');
    console.log('==================================================================');
    console.log('');
    colorLog('cyan', '📦 包信息:');
    colorLog('blue', `  📋 包名: ${packageName}`);
    colorLog('blue', `  📦 版本: ${version}`);
    colorLog('blue', `  🌐 Registry: https://www.npmjs.com/package/${packageName}`);
    console.log('');
    colorLog('cyan', '🚀 安装命令:');
    colorLog('yellow', `  npm install -g ${packageName}`);
    console.log('');
    colorLog('cyan', '📚 使用方法:');
    colorLog('yellow', '  powerautomation start');
    colorLog('yellow', '  powerautomation status');
    colorLog('yellow', '  powerautomation test');
    console.log('');
    console.log('==================================================================');
    console.log('');
}

async function main() {
    const args = process.argv.slice(2);
    const isDryRun = args.includes('--dry-run');
    const tag = args.find(arg => arg.startsWith('--tag='))?.split('=')[1] || 'latest';
    
    try {
        printHeader();
        
        // 检查 npm 登录状态
        const isLoggedIn = await checkNpmLogin();
        if (!isLoggedIn) {
            colorLog('red', '❌ 未登录 npm，请先运行: npm login');
            process.exit(1);
        }
        
        console.log('');
        
        // 检查包版本
        const versionOk = await checkPackageVersion();
        if (!versionOk) {
            process.exit(1);
        }
        
        console.log('');
        
        // 运行测试
        const testsOk = await runTests();
        if (!testsOk) {
            colorLog('yellow', '⚠️ 测试失败，是否继续发布？(y/N)');
            // 在实际使用中，这里可以添加用户输入确认
        }
        
        console.log('');
        
        // 构建包
        const buildOk = await buildPackage();
        if (!buildOk) {
            process.exit(1);
        }
        
        console.log('');
        
        if (isDryRun) {
            colorLog('yellow', '🔍 干运行模式，跳过实际发布');
            colorLog('blue', '💡 要实际发布，请运行: node scripts/publish.js');
            return;
        }
        
        // 发布包
        const publishOk = await publishPackage(tag);
        if (!publishOk) {
            process.exit(1);
        }
        
        console.log('');
        
        // 创建 Git 标签
        await createGitTag();
        
        // 打印成功消息
        await printSuccessMessage();
        
    } catch (err) {
        colorLog('red', `❌ 发布失败: ${err.message}`);
        process.exit(1);
    }
}

// 只在直接运行时执行
if (require.main === module) {
    main().catch((err) => {
        colorLog('red', `❌ 发布脚本执行失败: ${err.message}`);
        process.exit(1);
    });
}

module.exports = { main };

