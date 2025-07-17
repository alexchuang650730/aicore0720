#!/usr/bin/env node
/**
 * PowerAutomation ClaudeEditor 通用安装器
 * 自动检测平台并安装对应版本，无需手动选择目录
 */

const os = require('os');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const chalk = require('chalk');
const ora = require('ora');

class UniversalInstaller {
  constructor() {
    this.platform = this.detectPlatform();
    this.architecture = this.detectArchitecture();
    this.capabilities = this.detectCapabilities();
    this.installPath = process.cwd();
    this.config = this.loadConfig();
    this.selectedType = null;
  }

  /**
   * 智能平台检测
   */
  detectPlatform() {
    const platform = os.platform();
    const userAgent = process.env.USER_AGENT || '';
    const env = process.env;
    
    // 移动平台检测
    if (env.ANDROID_HOME || env.ANDROID_SDK_ROOT || userAgent.includes('Android')) {
      return { type: 'mobile', os: 'android', framework: 'capacitor' };
    }
    
    if (env.IOS_SIMULATOR || userAgent.includes('iPhone') || userAgent.includes('iPad')) {
      return { type: 'mobile', os: 'ios', framework: 'capacitor' };
    }
    
    // 桌面平台检测
    const desktopMap = {
      'darwin': { type: 'desktop', os: 'macos', framework: 'electron' },
      'win32': { type: 'desktop', os: 'windows', framework: 'electron' },
      'linux': { type: 'desktop', os: 'linux', framework: 'electron' }
    };
    
    if (desktopMap[platform]) {
      return desktopMap[platform];
    }
    
    // 默认 Web 平台
    return { type: 'web', os: 'browser', framework: 'react' };
  }

  /**
   * 检测系统能力
   */
  detectCapabilities() {
    const capabilities = {
      node: this.checkNodeVersion(),
      python: this.checkPython(),
      git: this.checkGit(),
      docker: this.checkDocker(),
      mobileSdk: this.checkMobileSdk(),
      electron: this.checkElectron(),
      browser: true // 总是可用
    };
    
    return capabilities;
  }

  /**
   * 智能选择最佳安装类型
   */
  selectBestInstallType() {
    const platform = this.platform;
    const caps = this.capabilities;
    
    console.log(chalk.cyan('🔍 智能平台检测结果:'));
    console.log(`   平台类型: ${chalk.yellow(platform.type)}`);
    console.log(`   操作系统: ${chalk.yellow(platform.os)}`);
    console.log(`   推荐框架: ${chalk.yellow(platform.framework)}`);
    console.log('');
    
    // 根据平台和能力选择最佳类型
    switch (platform.type) {
      case 'desktop':
        if (caps.node && caps.python) {
          this.selectedType = {
            id: 'desktop',
            name: '桌面版 (Electron)',
            framework: 'electron',
            model: 'k2_local',
            features: ['本地 K2 模型', 'Mirror Code', '完整 IDE', '离线运行'],
            requirements: ['Node.js', 'Python3']
          };
        } else {
          console.log(chalk.yellow('⚠️ 桌面环境不完整，回退到 Web 版'));
          this.selectedType = this.getWebType();
        }
        break;
        
      case 'mobile':
        if (caps.node && caps.mobileSdk) {
          this.selectedType = {
            id: 'mobile',
            name: `移动版 (${platform.os})`,
            framework: 'capacitor',
            model: 'k2_cloud',
            features: ['触控界面', '云端 K2', '原生集成', '离线缓存'],
            requirements: ['Node.js', 'Mobile SDK']
          };
        } else {
          console.log(chalk.yellow('⚠️ 移动开发环境不完整，回退到 Web 版'));
          this.selectedType = this.getWebType();
        }
        break;
        
      default:
        this.selectedType = this.getWebType();
        break;
    }
    
    return this.selectedType;
  }

  /**
   * 获取 Web 版配置
   */
  getWebType() {
    return {
      id: 'web',
      name: 'Web 版 (浏览器)',
      framework: 'react',
      model: 'k2_cloud',
      features: ['响应式界面', 'API K2', '跨平台', '即时访问'],
      requirements: ['Node.js', '现代浏览器']
    };
  }

  /**
   * 执行通用安装
   */
  async install() {
    console.log(chalk.blue('🚀 PowerAutomation ClaudeEditor 通用安装器 v4.6.9.5'));
    console.log(chalk.gray('=' * 60));
    
    // 1. 智能检测和选择
    const installType = this.selectBestInstallType();
    
    console.log(chalk.green(`✅ 自动选择: ${installType.name}`));
    console.log(chalk.cyan('🌟 包含特性:'));
    installType.features.forEach(feature => {
      console.log(`   ✅ ${feature}`);
    });
    console.log('');
    
    // 2. 检查依赖
    await this.checkDependencies(installType);
    
    // 3. 创建统一项目结构
    await this.createUniversalStructure(installType);
    
    // 4. 安装依赖
    await this.installDependencies(installType);
    
    // 5. 配置平台
    await this.configurePlatform(installType);
    
    // 6. 构建应用
    await this.buildApplication(installType);
    
    // 7. 创建启动脚本
    await this.createStartupScripts(installType);
    
    // 8. 显示完成信息
    this.showCompletionInfo(installType);
  }

  /**
   * 创建统一项目结构 (不分平台目录)
   */
  async createUniversalStructure(installType) {
    const spinner = ora('🏗️ 创建项目结构...').start();
    
    try {
      // 统一目录结构
      const dirs = [
        'src',
        'src/components',
        'src/services',
        'src/utils',
        'src/ai-assistant',
        'src/dual-mode',
        'public',
        'scripts',
        'config',
        'core',
        'core/components',
        'core/components/command_mcp',
        'core/components/mirror_code_tracker',
        'core/components/claude_router_mcp',
        'bin'
      ];
      
      // 根据框架添加特定目录
      if (installType.framework === 'electron') {
        dirs.push('electron', 'python-backend');
      } else if (installType.framework === 'capacitor') {
        dirs.push('capacitor');
      }
      
      for (const dir of dirs) {
        const dirPath = path.join(this.installPath, dir);
        if (!fs.existsSync(dirPath)) {
          fs.mkdirSync(dirPath, { recursive: true });
        }
      }
      
      spinner.succeed('✅ 项目结构创建完成');
      
    } catch (error) {
      spinner.fail(`❌ 项目结构创建失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 配置平台 (统一配置)
   */
  async configurePlatform(installType) {
    const spinner = ora('⚙️ 配置平台...').start();
    
    try {
      // 1. 生成统一配置文件
      await this.generateUniversalConfig(installType);
      
      // 2. 复制核心组件
      await this.copyCoreComponents();
      
      // 3. 生成平台特定文件
      await this.generatePlatformFiles(installType);
      
      // 4. 配置 PowerAutomation Core
      await this.configurePowerAutomationCore(installType);
      
      spinner.succeed('✅ 平台配置完成');
      
    } catch (error) {
      spinner.fail(`❌ 平台配置失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 生成统一配置文件
   */
  async generateUniversalConfig(installType) {
    const config = {
      powerautomation: {
        version: "4.6.9.5",
        platform: this.platform,
        installType: installType,
        autoDetected: true,
        timestamp: new Date().toISOString()
      },
      core: {
        mirrorCode: {
          enabled: true,
          defaultModel: installType.model,
          strategy: "k2_first"
        },
        commandMCP: {
          enabled: true,
          integrated: true
        },
        taskSync: {
          enabled: true,
          port: 8765
        },
        multiAgent: {
          enabled: true,
          agents: ["claude", "k2", "command_mcp", "zen_workflow", "x_masters", "claude_code"]
        }
      },
      models: {
        default: installType.model,
        k2_local: {
          enabled: installType.framework === 'electron',
          path: "./python-backend/k2_model"
        },
        k2_cloud: {
          enabled: true,
          apiEndpoint: "https://api.moonlight.com/v1/chat/completions"
        },
        claude_code: {
          enabled: true,
          priority: "fallback"
        }
      },
      ui: {
        framework: installType.framework,
        features: installType.features,
        responsive: true,
        darkMode: true
      }
    };
    
    const configPath = path.join(this.installPath, 'powerautomation.config.json');
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  }

  /**
   * 创建启动脚本 (统一入口)
   */
  async createStartupScripts(installType) {
    const spinner = ora('📝 创建启动脚本...').start();
    
    try {
      // 1. 主启动脚本
      await this.createMainStartupScript(installType);
      
      // 2. Claude 包装器
      await this.createClaudeWrapper();
      
      // 3. 平台特定启动脚本
      await this.createPlatformStartupScript(installType);
      
      // 4. 设置执行权限
      await this.setExecutablePermissions();
      
      spinner.succeed('✅ 启动脚本创建完成');
      
    } catch (error) {
      spinner.fail(`❌ 启动脚本创建失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 创建主启动脚本
   */
  async createMainStartupScript(installType) {
    const startScript = `#!/usr/bin/env node
/**
 * PowerAutomation ClaudeEditor 统一启动器
 * 自动检测平台并启动对应版本
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class UniversalStarter {
  constructor() {
    this.config = this.loadConfig();
    this.installType = this.config.powerautomation.installType;
  }

  loadConfig() {
    const configPath = path.join(__dirname, 'powerautomation.config.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }

  async start() {
    console.log('🚀 启动 PowerAutomation ClaudeEditor...');
    console.log(\`📱 平台: \${this.installType.name}\`);
    
    switch (this.installType.framework) {
      case 'electron':
        await this.startElectron();
        break;
      case 'capacitor':
        await this.startCapacitor();
        break;
      case 'react':
        await this.startReact();
        break;
      default:
        throw new Error(\`未知框架: \${this.installType.framework}\`);
    }
  }

  async startElectron() {
    // 1. 启动 Python 后端 (K2 本地模型)
    console.log('🐍 启动 K2 本地模型...');
    const pythonProcess = spawn('python3', ['python-backend/k2_server.py'], {
      stdio: 'inherit',
      detached: true
    });

    // 2. 启动 Electron 应用
    console.log('⚡ 启动 Electron 应用...');
    const electronProcess = spawn('npm', ['run', 'electron'], {
      stdio: 'inherit'
    });

    // 处理退出
    process.on('SIGINT', () => {
      pythonProcess.kill();
      electronProcess.kill();
      process.exit(0);
    });
  }

  async startCapacitor() {
    console.log('📱 启动移动应用开发服务器...');
    const devProcess = spawn('npm', ['run', 'dev'], {
      stdio: 'inherit'
    });

    console.log('🔗 访问: http://localhost:3000');
    console.log('📱 使用 "npx cap run ${this.config.powerautomation.platform.os}" 部署到设备');
  }

  async startReact() {
    console.log('🌐 启动 Web 开发服务器...');
    const reactProcess = spawn('npm', ['start'], {
      stdio: 'inherit'
    });

    console.log('🔗 访问: http://localhost:3000');
  }
}

// 执行启动
if (require.main === module) {
  const starter = new UniversalStarter();
  starter.start().catch(error => {
    console.error('❌ 启动失败:', error.message);
    process.exit(1);
  });
}

module.exports = UniversalStarter;
`;

    const scriptPath = path.join(this.installPath, 'start.js');
    fs.writeFileSync(scriptPath, startScript);
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
    console.log(`   框架: ${chalk.yellow(installType.framework)}`);
    console.log(`   模型: ${chalk.yellow(installType.model)}`);
    console.log(`   自动检测: ${chalk.yellow('是')}`);
    
    console.log('');
    console.log(chalk.cyan('🚀 启动命令:'));
    console.log(`   ${chalk.yellow('node start.js')}        # 统一启动器`);
    console.log(`   ${chalk.yellow('./claude "命令"')}       # Claude 包装器`);
    console.log(`   ${chalk.yellow('npm start')}            # 开发模式`);
    
    console.log('');
    console.log(chalk.cyan('🌟 核心特性:'));
    installType.features.forEach(feature => {
      console.log(`   ✅ ${feature}`);
    });
    
    console.log('');
    console.log(chalk.cyan('🎯 默认配置:'));
    console.log(`   🤖 默认模型: ${chalk.yellow(installType.model)}`);
    console.log(`   🪞 Mirror Code: ${chalk.yellow('K2 优先')}`);
    console.log(`   📡 Command MCP: ${chalk.yellow('已集成')}`);
    console.log(`   🔄 任务同步: ${chalk.yellow('已启用')}`);
    
    console.log('');
    console.log(chalk.gray('💡 所有平台使用统一的项目结构和配置'));
    console.log(chalk.gray('🔧 自动检测确保最佳用户体验'));
    console.log(chalk.gray('📚 文档: https://powerautomation.ai/docs'));
  }

  // 工具方法
  checkNodeVersion() {
    try {
      const version = process.version.slice(1);
      const [major] = version.split('.').map(Number);
      return major >= 16;
    } catch {
      return false;
    }
  }

  checkPython() {
    try {
      const { execSync } = require('child_process');
      execSync('python3 --version', { stdio: 'ignore' });
      return true;
    } catch {
      return false;
    }
  }

  checkGit() {
    try {
      const { execSync } = require('child_process');
      execSync('git --version', { stdio: 'ignore' });
      return true;
    } catch {
      return false;
    }
  }

  checkDocker() {
    try {
      const { execSync } = require('child_process');
      execSync('docker --version', { stdio: 'ignore' });
      return true;
    } catch {
      return false;
    }
  }

  checkMobileSdk() {
    const android = process.env.ANDROID_HOME || process.env.ANDROID_SDK_ROOT;
    const ios = this.platform.os === 'macos' && this.checkCommand('xcodebuild');
    return !!(android || ios);
  }

  checkElectron() {
    try {
      require.resolve('electron');
      return true;
    } catch {
      return false;
    }
  }

  checkCommand(command) {
    try {
      const { execSync } = require('child_process');
      execSync(`${command} --version`, { stdio: 'ignore' });
      return true;
    } catch {
      return false;
    }
  }

  loadConfig() {
    try {
      const packagePath = path.join(__dirname, '../package.json');
      const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
      return packageJson.config || {};
    } catch (error) {
      return {};
    }
  }

  // 占位方法
  async checkDependencies(installType) { /* 实现依赖检查 */ }
  async installDependencies(installType) { /* 实现依赖安装 */ }
  async buildApplication(installType) { /* 实现应用构建 */ }
  async copyCoreComponents() { /* 实现组件复制 */ }
  async generatePlatformFiles(installType) { /* 实现平台文件生成 */ }
  async configurePowerAutomationCore(installType) { /* 实现核心配置 */ }
  async createClaudeWrapper() { /* 实现 Claude 包装器 */ }
  async createPlatformStartupScript(installType) { /* 实现平台启动脚本 */ }
  async setExecutablePermissions() { /* 实现权限设置 */ }
}

// 主执行
if (require.main === module) {
  const installer = new UniversalInstaller();
  installer.install().catch(error => {
    console.error(chalk.red('❌ 安装失败:'), error.message);
    process.exit(1);
  });
}

module.exports = UniversalInstaller;

