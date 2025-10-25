/**
 * 智能错误处理系统
 * 提供错误分析、分类、智能提示和自动重试功能
 */
class SmartErrorHandler {
    constructor() {
        this.errorHistory = [];
        this.retryAttempts = new Map();
        this.maxRetryAttempts = 3;
        this.retryDelays = [1000, 3000, 5000]; // 递增延迟
        this.errorPatterns = this.initializeErrorPatterns();
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        window.controlledLog?.log('🔧 智能错误处理系统已初始化');
        this.isInitialized = true;
        
        // 监听全局错误事件
        window.addEventListener('error', (event) => {
            this.handleGlobalError(event);
        });
        
        // 监听未处理的Promise拒绝
        window.addEventListener('unhandledrejection', (event) => {
            this.handlePromiseRejection(event);
        });
    }
    
    /**
     * 初始化错误模式识别
     */
    initializeErrorPatterns() {
        return {
            // WebSocket连接错误
            websocket: {
                patterns: [
                    /WebSocket connection failed/i,
                    /WebSocket connection to .* failed/i,
                    /Connection closed/i,
                    /Connection lost/i
                ],
                severity: 'high',
                category: 'connection',
                suggestions: [
                    '检查网络连接',
                    '尝试重新连接',
                    '检查服务器状态'
                ]
            },
            
            // 音频处理错误
            audio: {
                patterns: [
                    /AudioContext/i,
                    /getUserMedia/i,
                    /audio.*error/i,
                    /microphone.*access/i
                ],
                severity: 'medium',
                category: 'audio',
                suggestions: [
                    '检查麦克风权限',
                    '尝试刷新页面',
                    '检查浏览器音频支持'
                ]
            },
            
            // 语音合成错误
            tts: {
                patterns: [
                    /speech.*synthesis/i,
                    /TTS.*error/i,
                    /voice.*synthesis/i,
                    /audio.*playback/i
                ],
                severity: 'medium',
                category: 'tts',
                suggestions: [
                    '检查语音合成服务',
                    '尝试重新播放',
                    '检查音频设备'
                ]
            },
            
            // 网络错误
            network: {
                patterns: [
                    /fetch.*failed/i,
                    /network.*error/i,
                    /timeout/i,
                    /connection.*timeout/i
                ],
                severity: 'high',
                category: 'network',
                suggestions: [
                    '检查网络连接',
                    '尝试重新请求',
                    '检查服务器状态'
                ]
            },
            
            // 状态管理错误
            state: {
                patterns: [
                    /state.*error/i,
                    /callback.*error/i,
                    /component.*error/i,
                    /render.*error/i
                ],
                severity: 'low',
                category: 'state',
                suggestions: [
                    '刷新页面',
                    '检查组件状态',
                    '重新初始化'
                ]
            }
        };
    }
    
    /**
     * 分析错误并分类
     */
    analyzeError(error) {
        const errorMessage = error.message || error.toString();
        const errorStack = error.stack || '';
        const fullError = `${errorMessage} ${errorStack}`;
        
        // 遍历错误模式
        for (const [category, config] of Object.entries(this.errorPatterns)) {
            for (const pattern of config.patterns) {
                if (pattern.test(fullError)) {
                    return {
                        category,
                        severity: config.severity,
                        suggestions: config.suggestions,
                        originalError: error,
                        timestamp: Date.now()
                    };
                }
            }
        }
        
        // 默认分类
        return {
            category: 'unknown',
            severity: 'medium',
            suggestions: ['尝试刷新页面', '检查控制台错误', '联系技术支持'],
            originalError: error,
            timestamp: Date.now()
        };
    }
    
    /**
     * 处理全局错误
     */
    handleGlobalError(event) {
        const error = {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            stack: event.error?.stack
        };
        
        this.handleError(error, 'global');
    }
    
    /**
     * 处理Promise拒绝
     */
    handlePromiseRejection(event) {
        const error = event.reason;
        this.handleError(error, 'promise');
    }
    
    /**
     * 处理错误
     */
    handleError(error, source = 'manual') {
        const analysis = this.analyzeError(error);
        
        // 记录错误历史
        this.errorHistory.push({
            ...analysis,
            source,
            id: this.generateErrorId()
        });
        
        // 限制历史记录长度
        if (this.errorHistory.length > 100) {
            this.errorHistory = this.errorHistory.slice(-50);
        }
        
        // 显示智能错误提示
        this.showSmartError(analysis);
        
        // 根据严重程度决定是否自动重试
        if (analysis.severity === 'high' && this.shouldAutoRetry(analysis)) {
            this.scheduleRetry(analysis);
        }
        
        console.error('🔧 智能错误处理:', analysis);
    }
    
    /**
     * 记录错误到历史记录
     */
    recordError(analysis) {
        try {
            // 添加到错误历史
            this.errorHistory.push({
                timestamp: new Date().toISOString(),
                analysis: analysis,
                userAgent: navigator.userAgent,
                url: window.location.href
            });
            
            // 限制历史记录数量（保留最近100条）
            if (this.errorHistory.length > 100) {
                this.errorHistory = this.errorHistory.slice(-100);
            }
            
            window.controlledLog?.log('🔧 错误已记录到历史:', analysis.type);
        } catch (error) {
            console.error('记录错误时发生异常:', error);
        }
    }

    /**
     * 显示智能错误提示
     */
    showSmartError(analysis) {
        // 🔧 默认隐藏错误弹出框，只在控制台记录
        console.warn('🔧 智能错误处理（已隐藏弹出框）:', analysis);
        
        // 只记录错误历史，不显示弹出框
        this.recordError(analysis);
        
        // 注释掉原来的弹出框逻辑
        /*
        const errorId = `error-${Date.now()}`;
        const container = this.createErrorContainer(errorId, analysis);
        
        // 添加到页面
        document.body.appendChild(container);
        
        // 自动隐藏（根据严重程度）
        const hideDelay = this.getHideDelay(analysis.severity);
        if (hideDelay > 0) {
            setTimeout(() => {
                this.hideError(errorId);
            }, hideDelay);
        }
        */
    }
    
    /**
     * 创建错误容器
     */
    createErrorContainer(errorId, analysis) {
        const container = document.createElement('div');
        container.id = errorId;
        container.className = 'smart-error-container';
        
        const severityClass = `error-${analysis.severity}`;
        const categoryIcon = this.getCategoryIcon(analysis.category);
        
        container.innerHTML = `
            <div class="smart-error-content ${severityClass}">
                <div class="error-header">
                    <span class="error-icon">${categoryIcon}</span>
                    <span class="error-title">${this.getErrorTitle(analysis)}</span>
                    <button class="error-close" onclick="window.smartErrorHandler.hideError('${errorId}')">×</button>
                </div>
                <div class="error-suggestions">
                    <p>建议操作：</p>
                    <ul>
                        ${analysis.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                </div>
                <div class="error-actions">
                    ${this.createErrorActions(errorId, analysis)}
                </div>
            </div>
        `;
        
        // 添加样式
        this.addErrorStyles();
        
        return container;
    }
    
    /**
     * 创建错误操作按钮
     */
    createErrorActions(errorId, analysis) {
        let actions = '';
        
        // 重试按钮
        if (this.canRetry(analysis)) {
            actions += `<button class="error-retry-btn" onclick="window.smartErrorHandler.retryError('${errorId}')">重试</button>`;
        }
        
        // 忽略按钮
        actions += `<button class="error-ignore-btn" onclick="window.smartErrorHandler.ignoreError('${errorId}')">忽略</button>`;
        
        // 详细信息按钮
        actions += `<button class="error-details-btn" onclick="window.smartErrorHandler.showErrorDetails('${errorId}')">详情</button>`;
        
        return actions;
    }
    
    /**
     * 获取错误标题
     */
    getErrorTitle(analysis) {
        const titles = {
            connection: '连接错误',
            audio: '音频错误',
            tts: '语音合成错误',
            network: '网络错误',
            state: '状态错误',
            unknown: '未知错误'
        };
        
        return titles[analysis.category] || '系统错误';
    }
    
    /**
     * 获取分类图标
     */
    getCategoryIcon(category) {
        const icons = {
            connection: '🔌',
            audio: '🎵',
            tts: '🗣️',
            network: '🌐',
            state: '⚙️',
            unknown: '❓'
        };
        
        return icons[category] || '❓';
    }
    
    /**
     * 获取隐藏延迟
     */
    getHideDelay(severity) {
        const delays = {
            high: 0,      // 不自动隐藏
            medium: 10000, // 10秒
            low: 5000     // 5秒
        };
        
        return delays[severity] || 5000;
    }
    
    /**
     * 判断是否应该自动重试
     */
    shouldAutoRetry(analysis) {
        return analysis.category === 'connection' || analysis.category === 'network';
    }
    
    /**
     * 判断是否可以重试
     */
    canRetry(analysis) {
        return analysis.category !== 'state' && analysis.severity !== 'low';
    }
    
    /**
     * 安排重试
     */
    scheduleRetry(analysis) {
        const retryKey = analysis.category;
        const attempts = this.retryAttempts.get(retryKey) || 0;
        
        if (attempts >= this.maxRetryAttempts) {
            window.controlledLog?.log(`🔧 已达到最大重试次数: ${retryKey}`);
            return;
        }
        
        const delay = this.retryDelays[attempts] || 5000;
        window.controlledLog?.log(`🔧 安排重试 ${retryKey}，延迟 ${delay}ms`);
        
        setTimeout(() => {
            this.executeRetry(analysis);
        }, delay);
        
        this.retryAttempts.set(retryKey, attempts + 1);
    }
    
    /**
     * 执行重试
     */
    executeRetry(analysis) {
        window.controlledLog?.log(`🔧 执行重试: ${analysis.category}`);
        
        switch (analysis.category) {
            case 'connection':
                this.retryConnection();
                break;
            case 'network':
                this.retryNetwork();
                break;
            case 'audio':
                this.retryAudio();
                break;
            case 'tts':
                this.retryTTS();
                break;
        }
    }
    
    /**
     * 重试连接
     */
    retryConnection() {
        if (window.voiceWebSocketManager) {
            window.voiceWebSocketManager.reconnect();
        }
    }
    
    /**
     * 重试网络
     */
    retryNetwork() {
        // 触发网络重试逻辑
        window.dispatchEvent(new CustomEvent('smart-error-retry-network'));
    }
    
    /**
     * 重试音频
     */
    retryAudio() {
        // 触发音频重试逻辑
        window.dispatchEvent(new CustomEvent('smart-error-retry-audio'));
    }
    
    /**
     * 重试TTS
     */
    retryTTS() {
        // 触发TTS重试逻辑
        window.dispatchEvent(new CustomEvent('smart-error-retry-tts'));
    }
    
    /**
     * 重试错误
     */
    retryError(errorId) {
        const container = document.getElementById(errorId);
        if (!container) return;
        
        // 执行重试逻辑
        this.executeRetry({ category: 'manual' });
        
        // 隐藏错误
        this.hideError(errorId);
    }
    
    /**
     * 忽略错误
     */
    ignoreError(errorId) {
        this.hideError(errorId);
    }
    
    /**
     * 显示错误详情
     */
    showErrorDetails(errorId) {
        const container = document.getElementById(errorId);
        if (!container) return;
        
        const detailsDiv = container.querySelector('.error-details');
        if (detailsDiv) {
            detailsDiv.style.display = detailsDiv.style.display === 'none' ? 'block' : 'none';
        } else {
            // 创建详情显示
            const details = document.createElement('div');
            details.className = 'error-details';
            details.innerHTML = `
                <h4>错误详情</h4>
                <pre>${JSON.stringify(this.errorHistory.slice(-5), null, 2)}</pre>
            `;
            container.querySelector('.smart-error-content').appendChild(details);
        }
    }
    
    /**
     * 隐藏错误
     */
    hideError(errorId) {
        const container = document.getElementById(errorId);
        if (container) {
            container.style.opacity = '0';
            container.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                container.remove();
            }, 300);
        }
    }
    
    /**
     * 添加错误样式
     */
    addErrorStyles() {
        if (document.getElementById('smart-error-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'smart-error-styles';
        style.textContent = `
            .smart-error-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
                transition: all 0.3s ease;
            }
            
            .smart-error-content {
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 16px;
                border-left: 4px solid #ff4d4f;
            }
            
            .error-high { border-left-color: #ff4d4f; }
            .error-medium { border-left-color: #faad14; }
            .error-low { border-left-color: #52c41a; }
            
            .error-header {
                display: flex;
                align-items: center;
                margin-bottom: 12px;
            }
            
            .error-icon {
                font-size: 20px;
                margin-right: 8px;
            }
            
            .error-title {
                font-weight: bold;
                flex: 1;
            }
            
            .error-close {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                color: #999;
            }
            
            .error-suggestions {
                margin-bottom: 12px;
            }
            
            .error-suggestions ul {
                margin: 8px 0;
                padding-left: 20px;
            }
            
            .error-actions {
                display: flex;
                gap: 8px;
            }
            
            .error-actions button {
                padding: 6px 12px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                background: white;
                cursor: pointer;
                font-size: 12px;
            }
            
            .error-retry-btn {
                background: #1890ff;
                color: white;
                border-color: #1890ff;
            }
            
            .error-details {
                margin-top: 12px;
                padding: 12px;
                background: #f5f5f5;
                border-radius: 4px;
                font-size: 12px;
            }
        `;
        
        document.head.appendChild(style);
    }
    
    /**
     * 生成错误ID
     */
    generateErrorId() {
        return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * 获取错误统计
     */
    getErrorStats() {
        const stats = {
            total: this.errorHistory.length,
            byCategory: {},
            bySeverity: {},
            recent: this.errorHistory.slice(-10)
        };
        
        this.errorHistory.forEach(error => {
            stats.byCategory[error.category] = (stats.byCategory[error.category] || 0) + 1;
            stats.bySeverity[error.severity] = (stats.bySeverity[error.severity] || 0) + 1;
        });
        
        return stats;
    }
    
    /**
     * 清除错误历史
     */
    clearErrorHistory() {
        this.errorHistory = [];
        this.retryAttempts.clear();
        window.controlledLog?.log('🔧 错误历史已清除');
    }
}

// 初始化智能错误处理系统
let smartErrorHandler;

function initSmartErrorHandler() {
    if (!smartErrorHandler) {
        smartErrorHandler = new SmartErrorHandler();
        window.smartErrorHandler = smartErrorHandler;
        window.controlledLog?.log('🔧 智能错误处理系统已启动');
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSmartErrorHandler);
} else {
    initSmartErrorHandler();
}