/**
 * 语音工具类 - 提供公共功能
 * 统一管理WebSocket初始化、状态更新、错误处理等公共逻辑
 */

class VoiceUtils {
    /**
     * 统一的WebSocket初始化
     * @param {Object} manager - WebSocket管理器
     * @param {Object} messageHandlers - 消息处理器映射
     * @returns {Promise<WebSocket>} WebSocket连接
     */
    static async initWebSocket(manager, messageHandlers = {}) {
        try {
            if (window.voiceWebSocketManager) {
                const ws = await window.voiceWebSocketManager.waitForConnection();
                if (ws) {
                    console.log('使用共享WebSocket连接');
                    // 注册消息处理器
                    Object.entries(messageHandlers).forEach(([type, handler]) => {
                        window.voiceWebSocketManager.registerMessageHandler(type, handler);
                    });
                    return ws;
                } else {
                    console.warn('WebSocket管理器未连接，等待连接...');
                    // 等待连接建立
                    return new Promise((resolve, reject) => {
                        const checkConnection = () => {
                            if (window.voiceWebSocketManager && window.voiceWebSocketManager.isConnected) {
                                const ws = window.voiceWebSocketManager.getConnection();
                                if (ws) {
                                    // 注册消息处理器
                                    Object.entries(messageHandlers).forEach(([type, handler]) => {
                                        window.voiceWebSocketManager.registerMessageHandler(type, handler);
                                    });
                                    resolve(ws);
                                } else {
                                    setTimeout(checkConnection, 100);
                                }
                            } else {
                                setTimeout(checkConnection, 100);
                            }
                        };
                        setTimeout(() => reject(new Error('WebSocket连接超时')), 5000);
                        checkConnection();
                    });
                }
            } else {
                throw new Error('WebSocket管理器不可用');
            }
        } catch (error) {
            console.error('WebSocket初始化失败:', error);
            throw error;
        }
    }
    
    /**
     * 统一的状态更新
     * @param {string} state - 状态
     * @param {string} scenario - 场景
     * @param {Object} metadata - 元数据
     */
    static updateState(state, scenario, metadata = {}) {
        try {
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('unified-button-state', {
                    data: { 
                        state, 
                        scenario, 
                        timestamp: Date.now(), 
                        metadata 
                    }
                });
                console.log('状态已更新:', { state, scenario, metadata });
            } else {
                console.warn('Dash clientside不可用，无法更新状态');
            }
        } catch (error) {
            console.error('状态更新失败:', error);
        }
    }
    
    /**
     * 统一的事件触发
     * @param {string} type - 事件类型
     * @param {Object} data - 事件数据
     */
    static triggerEvent(type, data = {}) {
        try {
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('button-event-trigger', {
                    data: { 
                        type, 
                        timestamp: Date.now(),
                        ...data 
                    }
                });
                console.log('事件已触发:', { type, data });
            } else {
                console.warn('Dash clientside不可用，无法触发事件');
            }
        } catch (error) {
            console.error('事件触发失败:', error);
        }
    }
    
    /**
     * 统一的错误处理
     * @param {Error} error - 错误对象
     * @param {string} context - 错误上下文
     */
    static handleError(error, context = '') {
        const errorMessage = `语音系统错误${context}: ${error.message}`;
        console.error(errorMessage, error);
        
        // 统一的错误显示逻辑
        this.showError(errorMessage);
        
        // 触发错误事件
        this.triggerEvent('error', { 
            message: error.message, 
            context,
            timestamp: Date.now() 
        });
    }
    
    /**
     * 统一的错误显示
     * @param {string} message - 错误消息
     */
    static showError(message) {
        try {
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('global-message', {
                    children: message
                });
                console.log('已显示错误消息:', message);
            } else {
                console.warn('语音系统提示:', message);
            }
        } catch (error) {
            console.error('显示错误消息失败:', error);
        }
    }
    
    /**
     * 统一的成功提示
     * @param {string} message - 成功消息
     */
    static showSuccess(message) {
        try {
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('global-message', {
                    children: message
                });
                console.log('已显示成功消息:', message);
            } else {
                console.log('语音系统提示:', message);
            }
        } catch (error) {
            console.error('显示成功消息失败:', error);
        }
    }
    
    /**
     * 防抖函数
     * @param {Function} func - 要防抖的函数
     * @param {number} delay - 延迟时间
     * @returns {Function} 防抖后的函数
     */
    static debounce(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }
    
    /**
     * 节流函数
     * @param {Function} func - 要节流的函数
     * @param {number} limit - 时间间隔
     * @returns {Function} 节流后的函数
     */
    static throttle(func, limit) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    /**
     * 安全的DOM操作
     * @param {string} selector - 选择器
     * @param {Function} callback - 回调函数
     */
    static safeDOMOperation(selector, callback) {
        try {
            const element = document.querySelector(selector);
            if (element && callback) {
                callback(element);
            } else {
                console.warn(`元素未找到: ${selector}`);
            }
        } catch (error) {
            console.error(`DOM操作失败: ${selector}`, error);
        }
    }
    
    /**
     * 批量DOM操作
     * @param {Array} operations - 操作数组
     */
    static batchDOMOperations(operations) {
        requestAnimationFrame(() => {
            operations.forEach(operation => {
                this.safeDOMOperation(operation.selector, operation.callback);
            });
        });
    }
    
    /**
     * 检查浏览器支持
     * @returns {boolean} 是否支持
     */
    static checkBrowserSupport() {
        const requiredFeatures = [
            'WebSocket',
            'AudioContext',
            'MediaRecorder',
            'getUserMedia'
        ];
        
        const missingFeatures = requiredFeatures.filter(feature => {
            switch (feature) {
                case 'WebSocket':
                    return typeof WebSocket === 'undefined';
                case 'AudioContext':
                    return typeof (window.AudioContext || window.webkitAudioContext) === 'undefined';
                case 'MediaRecorder':
                    return typeof MediaRecorder === 'undefined';
                case 'getUserMedia':
                    return !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia;
                default:
                    return false;
            }
        });
        
        if (missingFeatures.length > 0) {
            console.warn('缺少必要的浏览器功能:', missingFeatures);
            return false;
        }
        
        return true;
    }
    
    /**
     * 获取配置值
     * @param {string} key - 配置键
     * @param {*} defaultValue - 默认值
     * @returns {*} 配置值
     */
    static getConfig(key, defaultValue = null) {
        try {
            if (window.voiceConfig && window.voiceConfig[key] !== undefined) {
                return window.voiceConfig[key];
            }
            return defaultValue;
        } catch (error) {
            console.error('获取配置失败:', error);
            return defaultValue;
        }
    }
    
    /**
     * 设置配置值
     * @param {string} key - 配置键
     * @param {*} value - 配置值
     */
    static setConfig(key, value) {
        try {
            if (!window.voiceConfig) {
                window.voiceConfig = {};
            }
            window.voiceConfig[key] = value;
            console.log('配置已更新:', { key, value });
        } catch (error) {
            console.error('设置配置失败:', error);
        }
    }
}

// 导出工具类
window.VoiceUtils = VoiceUtils;
