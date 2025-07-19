/**
 * ClaudeEditor Core Dependency Checker
 * 确保claudeditor与core目录强绑定
 */

class CoreDependencyChecker {
    constructor() {
        this.coreBasePath = '../core';
        this.requiredCoreFiles = [
            'core/__init__.py',
            'core/powerautomation_main.py',
            'core/components/local_adapter_mcp',
            'core/components/mcp_coordinator_mcp',
            'core/components/smartui_mcp'
        ];
        this.coreApiEndpoint = 'http://localhost:8080';
    }

    /**
     * 检查core目录是否存在且完整
     */
    async checkCoreAvailability() {
        try {
            // 检查core目录结构
            const coreCheck = await this.validateCoreStructure();
            if (!coreCheck.valid) {
                throw new Error(`Core目录不完整: ${coreCheck.missing.join(', ')}`);
            }

            // 检查core API服务是否运行
            const apiCheck = await this.checkCoreApiService();
            if (!apiCheck.available) {
                console.warn('Core API服务未运行，尝试启动...');
                await this.startCoreService();
            }

            return {
                status: 'success',
                message: 'Core依赖检查通过',
                coreVersion: await this.getCoreVersion(),
                apiStatus: 'running'
            };

        } catch (error) {
            return {
                status: 'error',
                message: `Core依赖检查失败: ${error.message}`,
                error: error
            };
        }
    }

    /**
     * 验证core目录结构
     */
    async validateCoreStructure() {
        const missing = [];
        
        for (const file of this.requiredCoreFiles) {
            try {
                const response = await fetch(`/api/check-file?path=${file}`);
                if (!response.ok) {
                    missing.push(file);
                }
            } catch (error) {
                missing.push(file);
            }
        }

        return {
            valid: missing.length === 0,
            missing: missing
        };
    }

    /**
     * 检查core API服务状态
     */
    async checkCoreApiService() {
        try {
            const response = await fetch(`${this.coreApiEndpoint}/health`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                const data = await response.json();
                return {
                    available: true,
                    version: data.version,
                    status: data.status
                };
            }
        } catch (error) {
            console.log('Core API服务未响应:', error.message);
        }

        return { available: false };
    }

    /**
     * 启动core服务
     */
    async startCoreService() {
        try {
            const response = await fetch('/api/start-core-service', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    service: 'powerautomation_main',
                    path: 'core/powerautomation_main.py'
                })
            });

            if (!response.ok) {
                throw new Error('无法启动Core服务');
            }

            // 等待服务启动
            await this.waitForCoreService();
            
        } catch (error) {
            throw new Error(`启动Core服务失败: ${error.message}`);
        }
    }

    /**
     * 等待core服务启动
     */
    async waitForCoreService(maxAttempts = 10) {
        for (let i = 0; i < maxAttempts; i++) {
            const check = await this.checkCoreApiService();
            if (check.available) {
                return true;
            }
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        throw new Error('Core服务启动超时');
    }

    /**
     * 获取core版本信息
     */
    async getCoreVersion() {
        try {
            const response = await fetch(`${this.coreApiEndpoint}/version`);
            if (response.ok) {
                const data = await response.json();
                return data.version;
            }
        } catch (error) {
            console.warn('无法获取Core版本信息');
        }
        return 'unknown';
    }

    /**
     * 显示core依赖错误
     */
    showCoreError(error) {
        const errorHtml = `
            <div class="core-error-overlay">
                <div class="core-error-dialog">
                    <div class="error-icon">⚠️</div>
                    <h2>Core依赖缺失</h2>
                    <p>ClaudeEditor需要core目录才能正常运行</p>
                    <div class="error-details">
                        <strong>错误详情:</strong><br>
                        ${error.message}
                    </div>
                    <div class="error-actions">
                        <button onclick="location.reload()" class="retry-btn">重试</button>
                        <button onclick="this.showCoreHelp()" class="help-btn">获取帮助</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', errorHtml);
    }

    /**
     * 显示core帮助信息
     */
    showCoreHelp() {
        alert(`
Core目录恢复方法:

1. 从git恢复core目录:
   git checkout 75c33d5 -- core/

2. 启动PowerAutomation服务:
   cd core && python powerautomation_main.py

3. 重新加载ClaudeEditor

如需更多帮助，请联系技术支持。
        `);
    }
}

// 全局实例
window.coreDependencyChecker = new CoreDependencyChecker();

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CoreDependencyChecker;
}

