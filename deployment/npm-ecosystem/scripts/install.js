#!/usr/bin/env node
/**
 * PowerAutomation ClaudeEditor 智能安装器
 * 根据平台自动安装 PC 版本或 Mobile 版本
 */

const os = require('os');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const chalk = require('chalk');
const ora = require('ora');
const inquirer = require('inquirer');

class PowerAutomationInstaller {
  constructor() {
    this.platform = this.detectPlatform();
    this.architecture = this.detectArchitecture();
    this.installPath = process.cwd();
    this.config = this.loadConfig();
  }

  /**
   * 检测平台
   */
  detectPlatform() {
    const platform = os.platform();
    const userAgent = process.env.USER_AGENT || '';
    
    // 检测移动平台
    if (userAgent.includes('Android') || process.env.ANDROID_HOME) {
      return 'android';
    }
    if (userAgent.includes('iPhone') || userAgent.includes('iPad') || process.env.IOS_SIMULATOR) {
      return 'ios';
    }
    
    // 桌面平台
    switch (platform) {
      case 'darwin': return 'macos';
      case 'win32': return 'windows';
      case 'linux': return 'linux';
      default: return 'unknown';
    }
  }

  /**
   * 检测架构
   */
  detectArchitecture() {
    const arch = os.arch();
    switch (arch) {
      case 'x64': return 'x64';
      case 'arm64': return 'arm64';
      case 'arm': return 'arm';
      default: return 'x64';
    }
  }

  /**
   * 加载配置
   */
  loadConfig() {
    try {
      const packagePath = path.join(__dirname, '../package.json');
      const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
      return packageJson.config || {};
    } catch (error) {
      console.error('❌ 无法加载配置文件:', error.message);
      process.exit(1);
    }
  }

  /**
   * 主安装流程
   */
  async install() {
    console.log(chalk.blue('🚀 PowerAutomation ClaudeEditor 智能安装器 v4.6.9.5'));
    console.log(chalk.gray('=' * 60));
    
    // 1. 显示平台信息
    this.showPlatformInfo();
    
    // 2. 选择安装类型
    const installType = await this.selectInstallType();
    
    // 3. 检查依赖
    await this.checkDependencies(installType);
    
    // 4. 执行安装
    await this.performInstall(installType);
    
    // 5. 配置和初始化
    await this.configureAndInitialize(installType);
    
    // 6. 显示完成信息
    this.showCompletionInfo(installType);
  }

  /**
   * 显示平台信息
   */
  showPlatformInfo() {
    console.log(chalk.cyan('🔍 检测到的平台信息:'));
    console.log(`   操作系统: ${chalk.yellow(this.platform)}`);
    console.log(`   架构: ${chalk.yellow(this.architecture)}`);
    console.log(`   Node.js: ${chalk.yellow(process.version)}`);
    console.log(`   安装路径: ${chalk.yellow(this.installPath)}`);
    console.log('');
  }

  /**
   * 选择安装类型
   */
  async selectInstallType() {
    const availableTypes = this.getAvailableInstallTypes();
    
    if (availableTypes.length === 1) {
      console.log(chalk.green(`✅ 自动选择安装类型: ${availableTypes[0].name}`));
      return availableTypes[0];
    }
    
    const { installType } = await inquirer.prompt([
      {
        type: 'list',
        name: 'installType',
        message: '请选择安装类型:',
        choices: availableTypes.map(type => ({
          name: `${type.name} - ${type.description}`,
          value: type
        }))
      }
    ]);
    
    return installType;
  }

  /**
   * 获取可用的安装类型
   */
  getAvailableInstallTypes() {
    const types = [];
    
    // 桌面版本
    if (['macos', 'windows', 'linux'].includes(this.platform)) {
      types.push({
        id: 'desktop',
        name: '桌面版 (Electron)',
        description: 'K2 本地模型 + 完整 IDE 功能',
        platform: 'desktop',
        framework: 'electron',
        features: ['本地 K2 模型', 'Mirror Code', '多窗口支持', '系统集成']
      });
    }
    
    // 移动版本
    if (['android', 'ios'].includes(this.platform)) {
      types.push({
        id: 'mobile',
        name: '移动版 (Capacitor)',
        description: 'K2 云端模型 + 触控优化界面',
        platform: 'mobile',
        framework: 'capacitor',
        features: ['云端 K2 模型', '触控界面', '离线缓存', '原生集成']
      });
    }
    
    // Web 版本 (总是可用)
    types.push({
      id: 'web',
      name: 'Web 版 (浏览器)',
      description: 'K2 API 模型 + 响应式界面',
      platform: 'web',
      framework: 'react',
      features: ['API K2 模型', '响应式设计', '跨平台兼容', '即时访问']
    });
    
    return types;
  }

  /**
   * 检查依赖
   */
  async checkDependencies(installType) {
    const spinner = ora('🔍 检查依赖项...').start();
    
    try {
      // 检查 Node.js 版本
      const nodeVersion = process.version;
      const requiredNodeVersion = '16.0.0';
      if (!this.compareVersions(nodeVersion.slice(1), requiredNodeVersion)) {
        throw new Error(`需要 Node.js >= ${requiredNodeVersion}，当前版本: ${nodeVersion}`);
      }
      
      // 检查平台特定依赖
      await this.checkPlatformDependencies(installType);
      
      spinner.succeed('✅ 依赖检查通过');
      
    } catch (error) {
      spinner.fail(`❌ 依赖检查失败: ${error.message}`);
      process.exit(1);
    }
  }

  /**
   * 检查平台特定依赖
   */
  async checkPlatformDependencies(installType) {
    switch (installType.framework) {
      case 'electron':
        // 检查 Electron 依赖
        await this.checkCommand('python3', 'Python 3 (用于 K2 本地模型)');
        break;
        
      case 'capacitor':
        // 检查移动开发依赖
        if (this.platform === 'android') {
          await this.checkAndroidDependencies();
        } else if (this.platform === 'ios') {
          await this.checkIOSDependencies();
        }
        break;
        
      case 'react':
        // Web 版本无特殊依赖
        break;
    }
  }

  /**
   * 检查 Android 依赖
   */
  async checkAndroidDependencies() {
    // 检查 Android SDK
    if (!process.env.ANDROID_HOME && !process.env.ANDROID_SDK_ROOT) {
      console.log(chalk.yellow('⚠️ 未检测到 Android SDK，将使用 Web 版本'));
    }
    
    // 检查 Java
    try {
      await this.checkCommand('java', 'Java (Android 开发必需)');
    } catch (error) {
      console.log(chalk.yellow('⚠️ 未检测到 Java，将使用 Web 版本'));
    }
  }

  /**
   * 检查 iOS 依赖
   */
  async checkIOSDependencies() {
    if (this.platform !== 'macos') {
      throw new Error('iOS 开发需要 macOS 系统');
    }
    
    try {
      await this.checkCommand('xcodebuild', 'Xcode (iOS 开发必需)');
    } catch (error) {
      console.log(chalk.yellow('⚠️ 未检测到 Xcode，将使用 Web 版本'));
    }
  }

  /**
   * 执行安装
   */
  async performInstall(installType) {
    const spinner = ora(`🚀 安装 ${installType.name}...`).start();
    
    try {
      // 1. 创建项目目录
      await this.createProjectStructure(installType);
      
      // 2. 安装依赖
      await this.installDependencies(installType);
      
      // 3. 配置平台特定文件
      await this.configurePlatform(installType);
      
      // 4. 构建应用
      await this.buildApplication(installType);
      
      spinner.succeed(`✅ ${installType.name} 安装完成`);
      
    } catch (error) {
      spinner.fail(`❌ 安装失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 创建项目结构
   */
  async createProjectStructure(installType) {
    const dirs = [
      'src',
      'src/components',
      'src/services',
      'src/utils',
      'public',
      'scripts',
      'config'
    ];
    
    // 平台特定目录
    if (installType.framework === 'electron') {
      dirs.push('electron', 'python-backend');
    } else if (installType.framework === 'capacitor') {
      dirs.push('android', 'ios', 'capacitor');
    }
    
    for (const dir of dirs) {
      const dirPath = path.join(this.installPath, dir);
      if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
      }
    }
  }

  /**
   * 安装依赖
   */
  async installDependencies(installType) {
    const dependencies = this.getDependencies(installType);
    
    // 安装 npm 依赖
    await this.runCommand('npm', ['install', ...dependencies.npm]);
    
    // 安装平台特定依赖
    if (dependencies.platform) {
      for (const cmd of dependencies.platform) {
        await this.runCommand(cmd.command, cmd.args);
      }
    }
  }

  /**
   * 获取依赖列表
   */
  getDependencies(installType) {
    const baseDependencies = [
      'react@^18.0.0',
      'react-dom@^18.0.0',
      'axios@^1.3.0',
      'ws@^8.12.0'
    ];
    
    const dependencies = { npm: baseDependencies };
    
    switch (installType.framework) {
      case 'electron':
        dependencies.npm.push(
          'electron@^22.0.0',
          'electron-builder@^23.6.0'
        );
        dependencies.platform = [
          { command: 'pip3', args: ['install', 'flask', 'websockets'] }
        ];
        break;
        
      case 'capacitor':
        dependencies.npm.push(
          '@capacitor/core@^4.6.1',
          '@capacitor/cli@^4.6.1',
          `@capacitor/${this.platform}@^4.6.1`
        );
        break;
        
      case 'react':
        dependencies.npm.push(
          'webpack@^5.75.0',
          'webpack-cli@^5.0.1'
        );
        break;
    }
    
    return dependencies;
  }

  /**
   * 配置平台
   */
  async configurePlatform(installType) {
    // 复制模板文件
    await this.copyTemplates(installType);
    
    // 生成配置文件
    await this.generateConfig(installType);
    
    // 平台特定配置
    switch (installType.framework) {
      case 'electron':
        await this.configureElectron();
        break;
      case 'capacitor':
        await this.configureCapacitor();
        break;
      case 'react':
        await this.configureReact();
        break;
    }
  }

  /**
   * 构建应用
   */
  async buildApplication(installType) {
    switch (installType.framework) {
      case 'electron':
        await this.runCommand('npm', ['run', 'build:desktop']);
        break;
      case 'capacitor':
        await this.runCommand('npm', ['run', 'build:mobile']);
        break;
      case 'react':
        await this.runCommand('npm', ['run', 'build']);
        break;
    }
  }

  /**
   * 配置和初始化
   */
  async configureAndInitialize(installType) {
    const spinner = ora('⚙️ 配置和初始化...').start();
    
    try {
      // 1. 生成启动脚本
      await this.generateStartupScripts(installType);
      
      // 2. 配置 PowerAutomation Core
      await this.configurePowerAutomationCore(installType);
      
      // 3. 初始化 K2 模型
      await this.initializeK2Model(installType);
      
      spinner.succeed('✅ 配置完成');
      
    } catch (error) {
      spinner.fail(`❌ 配置失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 显示完成信息
   */
  showCompletionInfo(installType) {
    console.log('');
    console.log(chalk.green('🎉 PowerAutomation ClaudeEditor 安装完成！'));
    console.log(chalk.gray('=' * 60));
    
    console.log(chalk.cyan('📋 安装信息:'));
    console.log(`   版本: ${chalk.yellow('v4.6.9.5')}`);
    console.log(`   类型: ${chalk.yellow(installType.name)}`);
    console.log(`   平台: ${chalk.yellow(this.platform)}`);
    console.log(`   框架: ${chalk.yellow(installType.framework)}`);
    
    console.log('');
    console.log(chalk.cyan('🚀 启动命令:'));
    
    switch (installType.framework) {
      case 'electron':
        console.log(`   ${chalk.yellow('npm start')}          # 开发模式`);
        console.log(`   ${chalk.yellow('npm run build')}      # 构建应用`);
        console.log(`   ${chalk.yellow('./powerautomation')}  # 直接启动`);
        break;
        
      case 'capacitor':
        console.log(`   ${chalk.yellow('npm run dev')}        # 开发模式`);
        console.log(`   ${chalk.yellow('npm run build')}      # 构建应用`);
        console.log(`   ${chalk.yellow('npx cap run ' + this.platform)} # 运行到设备`);
        break;
        
      case 'react':
        console.log(`   ${chalk.yellow('npm start')}          # 开发服务器`);
        console.log(`   ${chalk.yellow('npm run build')}      # 构建生产版本`);
        break;
    }
    
    console.log('');
    console.log(chalk.cyan('🌟 特性:'));
    for (const feature of installType.features) {
      console.log(`   ✅ ${feature}`);
    }
    
    console.log('');
    console.log(chalk.cyan('🔗 访问地址:'));
    if (installType.framework === 'react') {
      console.log(`   🌐 http://localhost:3000`);
    } else {
      console.log(`   📱 原生应用已安装`);
    }
    
    console.log('');
    console.log(chalk.gray('💡 使用 --help 查看更多选项'));
    console.log(chalk.gray('📚 文档: https://powerautomation.ai/docs'));
  }

  // 工具方法
  async checkCommand(command, description) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, ['--version'], { stdio: 'ignore' });
      child.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`${description} 未安装或不可用`));
        }
      });
    });
  }

  async runCommand(command, args) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, args, { stdio: 'inherit' });
      child.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`命令执行失败: ${command} ${args.join(' ')}`));
        }
      });
    });
  }

  compareVersions(version1, version2) {
    const v1 = version1.split('.').map(Number);
    const v2 = version2.split('.').map(Number);
    
    for (let i = 0; i < Math.max(v1.length, v2.length); i++) {
      const a = v1[i] || 0;
      const b = v2[i] || 0;
      if (a > b) return true;
      if (a < b) return false;
    }
    return true;
  }

  // 占位方法 - 实际实现会更复杂
  async copyTemplates(installType) { /* 实现模板复制 */ }
  async generateConfig(installType) { /* 实现配置生成 */ }
  async configureElectron() { /* 实现 Electron 配置 */ }
  async configureCapacitor() { /* 实现 Capacitor 配置 */ }
  async configureReact() { /* 实现 React 配置 */ }
  async generateStartupScripts(installType) { /* 实现启动脚本生成 */ }
  async configurePowerAutomationCore(installType) { /* 实现 Core 配置 */ }
  async initializeK2Model(installType) { /* 实现 K2 模型初始化 */ }
}

// 主执行
if (require.main === module) {
  const installer = new PowerAutomationInstaller();
  installer.install().catch(error => {
    console.error(chalk.red('❌ 安装失败:'), error.message);
    process.exit(1);
  });
}

module.exports = PowerAutomationInstaller;

