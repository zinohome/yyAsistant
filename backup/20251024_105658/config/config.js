/**
 * 统一配置管理模块
 * 
 * 提供统一的配置管理功能，包括应用配置、WebSocket配置、
 * 语音配置、超时配置等。
 * 
 * 作者: AI Assistant
 * 创建时间: 2025-01-15
 * 版本: 1.0.0
 */

class Config {
    /**
     * 构造函数
     */
    constructor() {
        this.config = {
            // 应用配置
            app: {
                name: 'yyAsistant',
                version: '2.0.0',
                debug: this.isDebugMode(),
                host: window.location.hostname,
                port: window.location.port || (window.location.protocol === 'https:' ? '443' : '80')
            },
            
            // WebSocket配置
            websocket: {
                url: this.getWebSocketUrl(),
                reconnectAttempts: 5,
                reconnectInterval: 5000,
                heartbeatInterval: 30000,
                maxMessageSize: 1048576, // 1MB
                connectionTimeout: 10000 // 10秒
            },
            
            // 语音配置
            voice: {
                synthesisVoice: 'zh-CN-XiaoxiaoNeural',
                synthesisSpeed: 1.0,
                synthesisVolume: 1.0,
                recognitionLanguage: 'zh-CN',
                recognitionConfidence: 0.8,
                audioFormat: 'audio/wav',
                sampleRate: 16000
            },
            
            // 超时配置
            timeouts: {
                sseBase: 30,
                ssePerChar: 0.1,
                sseMax: 300,
                sseWarning: 60,
                ttsBase: 60,
                ttsPerChar: 0.2,
                ttsMax: 600,
                ttsWarning: 120,
                sttBase: 30,
                sttPerChar: 0.05,
                sttMax: 180,
                sttWarning: 45
            },
            
            // 性能配置
            performance: {
                maxMemoryUsage: 536870912, // 512MB
                maxCpuUsage: 50.0,
                responseTimeout: 2000, // 2秒
                maxConcurrentRequests: 100,
                cacheSize: 1000
            },
            
            // UI配置
            ui: {
                theme: 'light',
                language: 'zh-CN',
                animationDuration: 300,
                autoSave: true,
                autoSaveInterval: 30000 // 30秒
            }
        };
    }
    
    /**
     * 检查是否为调试模式
     * @returns {boolean} 是否为调试模式
     */
    isDebugMode() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' ||
               window.location.search.includes('debug=true');
    }
    
    /**
     * 获取WebSocket URL
     * @returns {string} WebSocket URL
     */
    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws`;
    }
    
    /**
     * 获取配置值
     * @param {string} key - 配置键，支持点号分隔的嵌套键
     * @param {*} defaultValue - 默认值
     * @returns {*} 配置值或默认值
     */
    get(key, defaultValue = null) {
        const keys = key.split('.');
        let value = this.config;
        
        try {
            for (const k of keys) {
                if (value && typeof value === 'object' && k in value) {
                    value = value[k];
                } else {
                    return defaultValue;
                }
            }
            return value;
        } catch (error) {
            console.warn(`获取配置失败: ${key}`, error);
            return defaultValue;
        }
    }
    
    /**
     * 设置配置值
     * @param {string} key - 配置键，支持点号分隔的嵌套键
     * @param {*} value - 配置值
     */
    set(key, value) {
        const keys = key.split('.');
        let config = this.config;
        
        try {
            // 创建嵌套对象结构
            for (let i = 0; i < keys.length - 1; i++) {
                const k = keys[i];
                if (!(k in config) || typeof config[k] !== 'object') {
                    config[k] = {};
                }
                config = config[k];
            }
            
            // 设置最终值
            config[keys[keys.length - 1]] = value;
        } catch (error) {
            console.error(`设置配置失败: ${key}`, error);
        }
    }
    
    /**
     * 获取所有配置
     * @returns {Object} 完整的配置对象
     */
    getAll() {
        return JSON.parse(JSON.stringify(this.config));
    }
    
    /**
     * 批量更新配置
     * @param {Object} updates - 要更新的配置对象
     */
    update(updates) {
        for (const [key, value] of Object.entries(updates)) {
            this.set(key, value);
        }
    }
    
    /**
     * 验证配置的有效性
     * @returns {boolean} 配置是否有效
     */
    validate() {
        try {
            // 验证必需的配置项
            const requiredKeys = [
                'app.name',
                'app.version',
                'websocket.url'
            ];
            
            for (const key of requiredKeys) {
                if (this.get(key) === null || this.get(key) === undefined) {
                    console.error(`缺少必需的配置项: ${key}`);
                    return false;
                }
            }
            
            // 验证数值范围
            if (this.get('app.port', 0) <= 0 || this.get('app.port', 0) > 65535) {
                console.error('应用端口配置无效');
                return false;
            }
            
            if (this.get('websocket.reconnectAttempts', 0) < 0) {
                console.error('WebSocket重连次数配置无效');
                return false;
            }
            
            if (this.get('voice.synthesisSpeed', 0) <= 0 || this.get('voice.synthesisSpeed', 0) > 3) {
                console.error('语音合成速度配置无效');
                return false;
            }
            
            return true;
        } catch (error) {
            console.error('配置验证失败:', error);
            return false;
        }
    }
    
    /**
     * 重新加载配置
     */
    reload() {
        this.constructor();
    }
    
    /**
     * 保存配置到本地存储
     */
    saveToLocalStorage() {
        try {
            localStorage.setItem('yyAsistant_config', JSON.stringify(this.config));
        } catch (error) {
            console.warn('保存配置到本地存储失败:', error);
        }
    }
    
    /**
     * 从本地存储加载配置
     */
    loadFromLocalStorage() {
        try {
            const saved = localStorage.getItem('yyAsistant_config');
            if (saved) {
                const savedConfig = JSON.parse(saved);
                this.update(savedConfig);
            }
        } catch (error) {
            console.warn('从本地存储加载配置失败:', error);
        }
    }
    
    /**
     * 重置配置为默认值
     */
    reset() {
        this.constructor();
    }
}

// 创建全局配置实例
window.config = new Config();

// 验证配置
if (!window.config.validate()) {
    console.error('配置验证失败，使用默认配置');
    window.config.reset();
}

// 从本地存储加载用户自定义配置
window.config.loadFromLocalStorage();

// 导出配置类（如果使用模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Config;
}

// 导出配置实例
if (typeof window !== 'undefined') {
    window.Config = Config;
}
