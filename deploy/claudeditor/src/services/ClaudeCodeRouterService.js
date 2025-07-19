/**
 * Claude Code Router Service - Claude 代码路由服务
 * 与 claude_code_router_mcp 集成，提供智能模型路由功能
 */

class ClaudeCodeRouterService {
    constructor() {
        this.baseUrl = 'http://localhost:8080';
        this.wsUrl = 'ws://localhost:8080/ws';
        this.websocket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        // 路由统计
        this.routingStats = {
            totalRequests: 0,
            successfulRoutes: 0,
            failedRoutes: 0,
            averageResponseTime: 0,
            modelUsage: {},
            costSavings: 0
        };
        
        // 模型配置
        this.availableModels = [
            { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet', provider: 'anthropic', cost: 'high' },
            { id: 'claude-3-haiku', name: 'Claude 3 Haiku', provider: 'anthropic', cost: 'low' },
            { id: 'kimi-k2', name: 'Kimi K2', provider: 'moonshot', cost: 'very_low' },
            { id: 'gpt-4', name: 'GPT-4', provider: 'openai', cost: 'high' },
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai', cost: 'medium' }
        ];
        
        // 事件监听器
        this.eventListeners = {
            'route_success': [],
            'route_error': [],
            'model_switch': [],
            'cost_update': [],
            'connection_change': []
        };
        
        this.init();
    }
    
    async init() {
        try {
            console.log('初始化 Claude Code Router Service...');
            
            // 检查路由器状态
            await this.checkRouterStatus();
            
            // 建立 WebSocket 连接
            this.connectWebSocket();
            
            // 加载路由统计
            await this.loadRoutingStats();
            
            console.log('Claude Code Router Service 初始化完成');
            
        } catch (error) {
            console.error('Claude Code Router Service 初始化失败:', error);
        }
    }
    
    async checkRouterStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/api/router/status`);
            if (response.ok) {
                const status = await response.json();
                console.log('路由器状态:', status);
                return status;
            } else {
                throw new Error(`路由器状态检查失败: ${response.status}`);
            }
        } catch (error) {
            console.warn('路由器服务未启动，使用本地模式');
            return { status: 'offline', mode: 'local' };
        }
    }
    
    connectWebSocket() {
        try {
            if (this.websocket) {
                this.websocket.close();
            }
            
            this.websocket = new WebSocket(this.wsUrl);
            
            this.websocket.onopen = () => {
                console.log('Claude Code Router WebSocket 连接已建立');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.emit('connection_change', { connected: true });
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('WebSocket 消息解析失败:', error);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('Claude Code Router WebSocket 连接已关闭');
                this.isConnected = false;
                this.emit('connection_change', { connected: false });
                this.handleReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('Claude Code Router WebSocket 错误:', error);
                this.emit('connection_change', { connected: false, error });
            };
            
        } catch (error) {
            console.error('WebSocket 连接失败:', error);
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'route_result':
                this.handleRouteResult(data);
                break;
            case 'model_switch':
                this.handleModelSwitch(data);
                break;
            case 'cost_update':
                this.handleCostUpdate(data);
                break;
            case 'stats_update':
                this.handleStatsUpdate(data);
                break;
            default:
                console.log('未知的 WebSocket 消息类型:', data.type);
        }
    }
    
    handleRouteResult(data) {
        this.routingStats.totalRequests++;
        
        if (data.success) {
            this.routingStats.successfulRoutes++;
            this.emit('route_success', data);
        } else {
            this.routingStats.failedRoutes++;
            this.emit('route_error', data);
        }
        
        // 更新模型使用统计
        if (data.model) {
            if (!this.routingStats.modelUsage[data.model]) {
                this.routingStats.modelUsage[data.model] = 0;
            }
            this.routingStats.modelUsage[data.model]++;
        }
        
        // 更新平均响应时间
        if (data.responseTime) {
            this.routingStats.averageResponseTime = 
                (this.routingStats.averageResponseTime + data.responseTime) / 2;
        }
    }
    
    handleModelSwitch(data) {
        console.log('模型切换:', data);
        this.emit('model_switch', data);
    }
    
    handleCostUpdate(data) {
        if (data.savings) {
            this.routingStats.costSavings += data.savings;
        }
        this.emit('cost_update', data);
    }
    
    handleStatsUpdate(data) {
        Object.assign(this.routingStats, data);
    }
    
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`尝试重连 Claude Code Router WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, delay);
        } else {
            console.error('Claude Code Router WebSocket 重连失败，已达到最大重试次数');
        }
    }
    
    async routeRequest(request) {
        try {
            const startTime = Date.now();
            
            const response = await fetch(`${this.baseUrl}/api/router/route`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: request.messages,
                    context: request.context || {},
                    preferences: request.preferences || {},
                    timestamp: new Date().toISOString()
                })
            });
            
            const responseTime = Date.now() - startTime;
            
            if (response.ok) {
                const result = await response.json();
                
                // 记录成功路由
                this.handleRouteResult({
                    success: true,
                    model: result.model,
                    responseTime,
                    cost: result.cost,
                    savings: result.savings
                });
                
                return result;
            } else {
                throw new Error(`路由请求失败: ${response.status}`);
            }
            
        } catch (error) {
            console.error('路由请求失败:', error);
            
            // 记录失败路由
            this.handleRouteResult({
                success: false,
                error: error.message
            });
            
            // 返回默认路由
            return this.getDefaultRoute(request);
        }
    }
    
    getDefaultRoute(request) {
        // 简单的本地路由逻辑
        const messageLength = JSON.stringify(request.messages).length;
        
        if (messageLength < 1000) {
            return {
                model: 'kimi-k2',
                provider: 'moonshot',
                reason: 'short_message_k2_optimization'
            };
        } else if (messageLength < 5000) {
            return {
                model: 'claude-3-haiku',
                provider: 'anthropic',
                reason: 'medium_message_haiku_balance'
            };
        } else {
            return {
                model: 'claude-3-5-sonnet',
                provider: 'anthropic',
                reason: 'long_message_sonnet_quality'
            };
        }
    }
    
    async loadRoutingStats() {
        try {
            const response = await fetch(`${this.baseUrl}/api/router/stats`);
            if (response.ok) {
                const stats = await response.json();
                Object.assign(this.routingStats, stats);
            }
        } catch (error) {
            console.warn('加载路由统计失败:', error);
        }
    }
    
    async getModelRecommendation(context) {
        try {
            const response = await fetch(`${this.baseUrl}/api/router/recommend`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(context)
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('获取模型推荐失败:', error);
        }
        
        // 返回默认推荐
        return {
            model: 'kimi-k2',
            reason: 'cost_optimization',
            confidence: 0.7
        };
    }
    
    async switchModel(modelId, reason = 'user_preference') {
        try {
            const response = await fetch(`${this.baseUrl}/api/router/switch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: modelId,
                    reason,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.emit('model_switch', result);
                return result;
            } else {
                throw new Error(`模型切换失败: ${response.status}`);
            }
            
        } catch (error) {
            console.error('模型切换失败:', error);
            return { success: false, error: error.message };
        }
    }
    
    getAvailableModels() {
        return this.availableModels;
    }
    
    getRoutingStats() {
        return {
            ...this.routingStats,
            isConnected: this.isConnected,
            lastUpdate: new Date().toISOString()
        };
    }
    
    getCostSavings() {
        return {
            totalSavings: this.routingStats.costSavings,
            currency: 'USD',
            period: 'session',
            k2Usage: this.routingStats.modelUsage['kimi-k2'] || 0,
            totalRequests: this.routingStats.totalRequests
        };
    }
    
    // 事件系统
    on(event, callback) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].push(callback);
        }
    }
    
    off(event, callback) {
        if (this.eventListeners[event]) {
            const index = this.eventListeners[event].indexOf(callback);
            if (index > -1) {
                this.eventListeners[event].splice(index, 1);
            }
        }
    }
    
    emit(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`事件监听器错误 (${event}):`, error);
                }
            });
        }
    }
    
    // 清理资源
    destroy() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        this.eventListeners = {};
        this.isConnected = false;
        
        console.log('Claude Code Router Service 已销毁');
    }
}

// 创建全局实例
const claudeCodeRouterService = new ClaudeCodeRouterService();

export default claudeCodeRouterService;

