/**
 * 统一配置管理模块
 * 
 * 提供统一的配置管理功能，支持从环境变量和默认值读取配置。
 * 
 * 作者: AI Assistant
 * 创建时间: 2024-10-24
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
                debug: window.location.hostname === 'localhost',
                show_console_log: false  // 控制台日志显示开关
            },
            
            // WebSocket配置
            websocket: {
                url: 'ws://192.168.32.168:9800/ws/chat',
                reconnectAttempts: 5,
                reconnectInterval: 5000,
                heartbeatInterval: 30000
            },
            
            // 语音配置
            voice: {
                synthesisVoice: 'zh-CN-XiaoxiaoNeural',
                synthesisSpeed: 1.0,
                synthesisVolume: 1.0,
                recognitionLanguage: 'zh-CN'
            },
            
            // 超时配置
            timeouts: {
                sseBase: 30,
                ssePerChar: 0.1,
                sseMax: 300,
                ttsBase: 60,
                ttsPerChar: 0.2,
                ttsMax: 600,
                sttBase: 30,
                sttPerChar: 0.05,
                sttMax: 180
            }
        };
    }
    
    /**
     * 获取WebSocket URL
     * @returns {string} WebSocket URL
     */
    getWebSocketUrl() {
        return this.config.websocket.url;
    }
    
    /**
     * 获取配置值
     * @param {string} key - 配置键，使用点号分隔层级，如 'app.name'
     * @param {*} defaultValue - 默认值，当配置不存在时返回
     * @returns {*} 配置值
     * 
     * @example
     * config.get('app.name') // 'yyAsistant'
     * config.get('app.debug') // false
     */
    get(key, defaultValue = null) {
        const keys = key.split('.');
        let value = this.config;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultValue;
            }
        }
        
        return value;
    }
    
    /**
     * 设置配置值
     * @param {string} key - 配置键，使用点号分隔层级，如 'app.name'
     * @param {*} value - 配置值
     * 
     * @example
     * config.set('app.debug', true)
     * config.get('app.debug') // true
     */
    set(key, value) {
        const keys = key.split('.');
        let config = this.config;
        
        // 遍历到倒数第二层
        for (let i = 0; i < keys.length - 1; i++) {
            const k = keys[i];
            if (!(k in config) || typeof config[k] !== 'object') {
                config[k] = {};
            }
            config = config[k];
        }
        
        // 设置最后一层的值
        config[keys[keys.length - 1]] = value;
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
     * @param {Object} configObj - 配置对象
     */
    update(configObj) {
        /**
         * 深度更新对象
         * @param {Object} target - 目标对象
         * @param {Object} source - 源对象
         */
        const deepUpdate = (target, source) => {
            for (const key in source) {
                if (source.hasOwnProperty(key)) {
                    if (key in target && 
                        typeof target[key] === 'object' && 
                        typeof source[key] === 'object' && 
                        !Array.isArray(target[key]) && 
                        !Array.isArray(source[key])) {
                        deepUpdate(target[key], source[key]);
                    } else {
                        target[key] = source[key];
                    }
                }
            }
        };
        
        deepUpdate(this.config, configObj);
    }
    
    /**
     * 重置配置到默认值
     */
    reset() {
        this.config = {
            app: {
                name: 'yyAsistant',
                version: '2.0.0',
                debug: window.location.hostname === 'localhost'
            },
            websocket: {
                url: 'ws://192.168.32.168:9800/ws/chat',
                reconnectAttempts: 5,
                reconnectInterval: 5000,
                heartbeatInterval: 30000
            },
            voice: {
                synthesisVoice: 'zh-CN-XiaoxiaoNeural',
                synthesisSpeed: 1.0,
                synthesisVolume: 1.0,
                recognitionLanguage: 'zh-CN'
            },
            timeouts: {
                sseBase: 30,
                ssePerChar: 0.1,
                sseMax: 300,
                ttsBase: 60,
                ttsPerChar: 0.2,
                ttsMax: 600,
                sttBase: 30,
                sttPerChar: 0.05,
                sttMax: 180
            }
        };
    }
    
    /**
     * 验证配置完整性
     * @returns {Object} 验证结果
     */
    validate() {
        const requiredKeys = [
            'app.name',
            'app.version',
            'websocket.url',
            'websocket.reconnectAttempts',
            'voice.synthesisVoice',
            'timeouts.sseBase'
        ];
        
        const missing = [];
        const invalid = [];
        
        for (const key of requiredKeys) {
            const value = this.get(key);
            if (value === null || value === undefined) {
                missing.push(key);
            }
        }
        
        // 验证数值范围
        const numericValidations = [
            { key: 'websocket.reconnectAttempts', min: 1, max: 10 },
            { key: 'websocket.reconnectInterval', min: 1000, max: 60000 },
            { key: 'voice.synthesisSpeed', min: 0.1, max: 3.0 },
            { key: 'voice.synthesisVolume', min: 0.0, max: 1.0 }
        ];
        
        for (const validation of numericValidations) {
            const value = this.get(validation.key);
            if (typeof value === 'number') {
                if (value < validation.min || value > validation.max) {
                    invalid.push({
                        key: validation.key,
                        value: value,
                        range: `${validation.min}-${validation.max}`
                    });
                }
            }
        }
        
        return {
            valid: missing.length === 0 && invalid.length === 0,
            missing,
            invalid
        };
    }
}

// 全局配置实例
window.config = new Config();

// 日志控制系统
window.controlledLog = {
    log: function(...args) {
        if (window.config.get('app.show_console_log', true)) {
            window.controlledLog?.log(...args);
        }
    },
    warn: function(...args) {
        if (window.config.get('app.show_console_log', true)) {
            console.warn(...args);
        }
    },
    error: function(...args) {
        if (window.config.get('app.show_console_log', true)) {
            console.error(...args);
        }
    },
    info: function(...args) {
        if (window.config.get('app.show_console_log', true)) {
            console.info(...args);
        }
    },
    debug: function(...args) {
        if (window.config.get('app.show_console_log', true)) {
            console.debug(...args);
        }
    }
};

// 设置控制台日志开关的便捷函数
window.setConsoleLogEnabled = function(enabled) {
    window.config.set('app.show_console_log', enabled);
};

// 便捷函数
/**
 * 获取配置值的便捷函数
 * @param {string} key - 配置键
 * @param {*} defaultValue - 默认值
 * @returns {*} 配置值
 */
window.getConfig = function(key, defaultValue = null) {
    return window.config.get(key, defaultValue);
};

/**
 * 设置配置值的便捷函数
 * @param {string} key - 配置键
 * @param {*} value - 配置值
 */
window.setConfig = function(key, value) {
    window.config.set(key, value);
};

// 页面加载完成后验证配置
document.addEventListener('DOMContentLoaded', function() {
    const validation = window.config.validate();
    if (!validation.valid) {
        window.controlledLog.warn('配置验证失败:', validation);
        if (validation.missing.length > 0) {
            window.controlledLog.error('缺少必需配置:', validation.missing);
        }
        if (validation.invalid.length > 0) {
            window.controlledLog.error('配置值无效:', validation.invalid);
        }
    } else {
        window.controlledLog.log('配置验证通过');
    }
});
