/**
 * 语音配置类 - 统一管理所有语音相关配置
 * 提供配置的加载、保存、验证等功能
 */

class VoiceConfig {
    constructor() {
        // 默认配置
        this.defaults = {
            // 语音设置
            voice: 'shimmer',
            speed: 1.0,
            volume: 0.8,
            pitch: 1.0,
            stability: 0.5,
            
            // 音频设置
            sampleRate: 16000,
            channels: 1,
            bitRate: 128000,
            
            // VAD设置
            vadThreshold: 0.05,
            maxSilenceDuration: 800,
            audioChunkSize: 12288,
            audioSendInterval: 300,
            
            // WebSocket设置
            wsUrl: 'ws://192.168.32.168:9800/ws/chat',
            reconnectAttempts: 5,
            reconnectInterval: 1000,
            heartbeatInterval: 30000,
            
            // UI设置
            autoPlay: true,
            showVisualizer: true,
            visualizerHeight: 20,
            visualizerWidth: 120,
            
            // 调试设置
            debugMode: false,
            logLevel: 'info',
            
            // TTS设置
            frontendTtsFallback: true
        };
        
        // 配置验证规则
        this.validationRules = {
            voice: { type: 'string', values: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'] },
            speed: { type: 'number', min: 0.25, max: 4.0 },
            volume: { type: 'number', min: 0.0, max: 1.0 },
            pitch: { type: 'number', min: 0.0, max: 2.0 },
            stability: { type: 'number', min: 0.0, max: 1.0 },
            sampleRate: { type: 'number', values: [8000, 16000, 22050, 44100, 48000] },
            channels: { type: 'number', min: 1, max: 2 },
            bitRate: { type: 'number', min: 32000, max: 320000 },
            vadThreshold: { type: 'number', min: 0.001, max: 1.0 },
            maxSilenceDuration: { type: 'number', min: 100, max: 5000 },
            audioChunkSize: { type: 'number', min: 1024, max: 65536 },
            audioSendInterval: { type: 'number', min: 100, max: 1000 },
            reconnectAttempts: { type: 'number', min: 0, max: 10 },
            reconnectInterval: { type: 'number', min: 500, max: 10000 },
            heartbeatInterval: { type: 'number', min: 5000, max: 300000 },
            autoPlay: { type: 'boolean' },
            showVisualizer: { type: 'boolean' },
            visualizerHeight: { type: 'number', min: 10, max: 100 },
            visualizerWidth: { type: 'number', min: 50, max: 500 },
            debugMode: { type: 'boolean' },
            logLevel: { type: 'string', values: ['debug', 'info', 'warn', 'error'] },
            frontendTtsFallback: { type: 'boolean' }
        };
        
        this.config = { ...this.defaults };
        this.loadConfig();
    }
    
    /**
     * 加载配置
     */
    loadConfig() {
        try {
            const saved = localStorage.getItem('voiceConfig');
            if (saved) {
                const parsedConfig = JSON.parse(saved);
                // 合并配置，保留默认值
                this.config = { ...this.defaults, ...parsedConfig };
                console.log('语音配置已加载:', this.config);
            } else {
                console.log('使用默认语音配置');
            }
        } catch (error) {
            console.error('加载语音配置失败:', error);
            this.config = { ...this.defaults };
        }
    }
    
    /**
     * 保存配置
     */
    saveConfig() {
        try {
            localStorage.setItem('voiceConfig', JSON.stringify(this.config));
            console.log('语音配置已保存');
        } catch (error) {
            console.error('保存语音配置失败:', error);
        }
    }
    
    /**
     * 获取配置值
     * @param {string} key - 配置键
     * @param {*} defaultValue - 默认值
     * @returns {*} 配置值
     */
    get(key, defaultValue = null) {
        if (this.config.hasOwnProperty(key)) {
            return this.config[key];
        }
        return defaultValue !== null ? defaultValue : this.defaults[key];
    }
    
    /**
     * 设置配置值
     * @param {string} key - 配置键
     * @param {*} value - 配置值
     * @returns {boolean} 是否设置成功
     */
    set(key, value) {
        if (this.validateConfig(key, value)) {
            this.config[key] = value;
            this.saveConfig();
            console.log('配置已更新:', { key, value });
            return true;
        } else {
            console.error('配置验证失败:', { key, value });
            return false;
        }
    }
    
    /**
     * 批量设置配置
     * @param {Object} configs - 配置对象
     * @returns {boolean} 是否全部设置成功
     */
    setMultiple(configs) {
        let allValid = true;
        const validConfigs = {};
        
        Object.entries(configs).forEach(([key, value]) => {
            if (this.validateConfig(key, value)) {
                validConfigs[key] = value;
            } else {
                allValid = false;
                console.error('配置验证失败:', { key, value });
            }
        });
        
        if (allValid) {
            Object.assign(this.config, validConfigs);
            this.saveConfig();
            console.log('批量配置已更新:', validConfigs);
        }
        
        return allValid;
    }
    
    /**
     * 验证配置
     * @param {string} key - 配置键
     * @param {*} value - 配置值
     * @returns {boolean} 是否有效
     */
    validateConfig(key, value) {
        const rule = this.validationRules[key];
        if (!rule) {
            console.warn('未知配置项:', key);
            return true; // 允许未知配置项
        }
        
        // 类型检查
        if (rule.type === 'number' && typeof value !== 'number') {
            return false;
        }
        if (rule.type === 'string' && typeof value !== 'string') {
            return false;
        }
        if (rule.type === 'boolean' && typeof value !== 'boolean') {
            return false;
        }
        
        // 数值范围检查
        if (rule.type === 'number') {
            if (rule.min !== undefined && value < rule.min) {
                return false;
            }
            if (rule.max !== undefined && value > rule.max) {
                return false;
            }
        }
        
        // 枚举值检查
        if (rule.values && !rule.values.includes(value)) {
            return false;
        }
        
        return true;
    }
    
    /**
     * 重置配置到默认值
     * @param {string} key - 配置键，不传则重置所有
     */
    reset(key = null) {
        if (key) {
            if (this.defaults.hasOwnProperty(key)) {
                this.config[key] = this.defaults[key];
                this.saveConfig();
                console.log('配置已重置:', key);
            } else {
                console.warn('未知配置项:', key);
            }
        } else {
            this.config = { ...this.defaults };
            this.saveConfig();
            console.log('所有配置已重置为默认值');
        }
    }
    
    /**
     * 获取所有配置
     * @returns {Object} 配置对象
     */
    getAll() {
        return { ...this.config };
    }
    
    /**
     * 获取默认配置
     * @returns {Object} 默认配置对象
     */
    getDefaults() {
        return { ...this.defaults };
    }
    
    /**
     * 检查配置是否有效
     * @returns {boolean} 是否有效
     */
    isValid() {
        for (const [key, value] of Object.entries(this.config)) {
            if (!this.validateConfig(key, value)) {
                return false;
            }
        }
        return true;
    }
    
    /**
     * 获取语音相关配置
     * @returns {Object} 语音配置
     */
    getVoiceSettings() {
        return {
            voice: this.get('voice'),
            speed: this.get('speed'),
            volume: this.get('volume'),
            pitch: this.get('pitch'),
            stability: this.get('stability')
        };
    }
    
    /**
     * 获取音频相关配置
     * @returns {Object} 音频配置
     */
    getAudioSettings() {
        return {
            sampleRate: this.get('sampleRate'),
            channels: this.get('channels'),
            bitRate: this.get('bitRate')
        };
    }
    
    /**
     * 获取VAD相关配置
     * @returns {Object} VAD配置
     */
    getVADSettings() {
        return {
            vadThreshold: this.get('vadThreshold'),
            maxSilenceDuration: this.get('maxSilenceDuration'),
            audioChunkSize: this.get('audioChunkSize'),
            audioSendInterval: this.get('audioSendInterval')
        };
    }
    
    /**
     * 获取WebSocket相关配置
     * @returns {Object} WebSocket配置
     */
    getWebSocketSettings() {
        return {
            wsUrl: this.get('wsUrl'),
            reconnectAttempts: this.get('reconnectAttempts'),
            reconnectInterval: this.get('reconnectInterval'),
            heartbeatInterval: this.get('heartbeatInterval')
        };
    }
    
    /**
     * 获取UI相关配置
     * @returns {Object} UI配置
     */
    getUISettings() {
        return {
            autoPlay: this.get('autoPlay'),
            showVisualizer: this.get('showVisualizer'),
            visualizerHeight: this.get('visualizerHeight'),
            visualizerWidth: this.get('visualizerWidth')
        };
    }
    
    /**
     * 获取调试相关配置
     * @returns {Object} 调试配置
     */
    getDebugSettings() {
        return {
            debugMode: this.get('debugMode'),
            logLevel: this.get('logLevel')
        };
    }
}

// 创建全局实例
window.voiceConfig = new VoiceConfig();

// 兼容性：保持原有的配置访问方式
window.voiceConfig.getAutoPlaySetting = function() {
    return this.get('autoPlay');
};

window.voiceConfig.getVoiceDefault = function() {
    return this.get('voice');
};

window.voiceConfig.getPlaybackRate = function() {
    return this.get('speed');
};

console.log('语音配置系统已初始化');
