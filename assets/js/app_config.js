/**
 * 统一应用配置类 - JavaScript前端配置
 * 整合所有硬编码配置，支持动态配置覆盖
 */

class AppConfig {
    constructor() {
        // 默认配置
        this.defaults = {
            // ==================== 应用基础配置 ====================
            APP_TITLE: '研翌助手',
            APP_VERSION: '0.5.4',
            
            // ==================== 服务器配置 ====================
            APP_HOST: '0.0.0.0',
            APP_PORT: 8050,
            APP_DEBUG: true,
            
            // ==================== 后端服务配置 ====================
            YYCHAT_HOST: '192.168.32.168',
            YYCHAT_PORT: 9800,
            YYCHAT_API_KEY: 'yk-1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4',
            YYCHAT_DEFAULT_MODEL: 'gpt-4.1',
            YYCHAT_DEFAULT_TEMPERATURE: 0.7,
            YYCHAT_DEFAULT_STREAM: true,
            YYCHAT_DEFAULT_USE_TOOLS: true,
            
            // ==================== WebSocket配置 ====================
            WS_URL: 'ws://192.168.32.168:9800/ws/chat',
            WS_RECONNECT_INTERVAL: 1000,
            WS_MAX_RECONNECT_ATTEMPTS: 5,
            WS_HEARTBEAT_INTERVAL: 30000,
            
            // ==================== 音频配置 ====================
            AUDIO_SAMPLE_RATE: 16000,
            AUDIO_CHANNELS: 1,
            AUDIO_BIT_RATE: 128000,
            AUDIO_FORMAT: 'webm',
            AUDIO_MIME_TYPE: 'audio/webm;codecs=opus',
            
            // ==================== 语音配置 ====================
            VOICE_DEFAULT: 'shimmer',
            VOLUME_DEFAULT: 80,
            AUTO_PLAY_DEFAULT: true,
            PLAYBACK_VOLUME: 0.8,
            PLAYBACK_RATE: 1.0,
            
            // ==================== VAD配置 ====================
            VAD_THRESHOLD: 0.01,
            VAD_SILENCE_DURATION: 1000,
            VAD_MAX_SILENCE_DURATION: 800,
            VAD_SILENCE_INCREMENT: 50,
            VAD_NON_ZERO_RATIO_THRESHOLD: 0.05,
            
            // ==================== 录音配置 ====================
            RECORDING_CHUNK_SIZE: 1024,
            RECORDING_MAX_DURATION: 30000,
            AUDIO_CHUNK_SIZE: 12288,
            AUDIO_SEND_INTERVAL: 300,
            
            // ==================== 错误处理配置 ====================
            ERROR_RETRY_ATTEMPTS: 3,
            ERROR_RETRY_DELAY: 1000,
            
            // ==================== UI配置 ====================
            SHOW_VISUALIZER: true,
            VISUALIZER_HEIGHT: 20,
            VISUALIZER_WIDTH: 120,
            
            // ==================== 调试配置 ====================
            DEBUG_MODE: false,
            LOG_LEVEL: 'info',
            
            // ==================== TTS配置 ====================
            FRONTEND_TTS_FALLBACK: true,
            
            // ==================== 测试配置 ====================
            TEST_BASE_URL: 'http://192.168.32.168:8050',
            TEST_BACKEND_URL: 'http://192.168.32.168:9800',
            TEST_LOCALHOST_URL: 'http://localhost:8050',
            
            // ==================== 本地主机检测配置 ====================
            LOCALHOST_HOSTNAMES: ['localhost', '127.0.0.1', '::1'],
            
            // ==================== 麦克风权限提示 ====================
            MICROPHONE_PERMISSION_HINT: '请使用 HTTPS 域名或 localhost 访问，并允许麦克风权限。'
        };
        
        // 配置验证规则
        this.validationRules = {
            APP_PORT: { type: 'number', min: 1, max: 65535 },
            YYCHAT_PORT: { type: 'number', min: 1, max: 65535 },
            AUDIO_SAMPLE_RATE: { type: 'number', values: [8000, 16000, 22050, 44100, 48000] },
            AUDIO_CHANNELS: { type: 'number', min: 1, max: 2 },
            AUDIO_BIT_RATE: { type: 'number', min: 32000, max: 320000 },
            VOLUME_DEFAULT: { type: 'number', min: 0, max: 100 },
            PLAYBACK_VOLUME: { type: 'number', min: 0, max: 1 },
            PLAYBACK_RATE: { type: 'number', min: 0.25, max: 4.0 },
            VAD_THRESHOLD: { type: 'number', min: 0.001, max: 1.0 },
            VOICE_DEFAULT: { type: 'string', values: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'] },
            LOG_LEVEL: { type: 'string', values: ['debug', 'info', 'warn', 'error'] }
        };
        
        this.config = { ...this.defaults };
        this.loadConfig();
    }
    
    /**
     * 加载配置
     */
    loadConfig() {
        try {
            // 从localStorage加载用户自定义配置
            const saved = localStorage.getItem('appConfig');
            if (saved) {
                const parsedConfig = JSON.parse(saved);
                // 合并配置，保留默认值
                this.config = { ...this.defaults, ...parsedConfig };
                console.log('应用配置已加载:', this.config);
            } else {
                console.log('使用默认应用配置');
            }
            
            // 从服务器配置加载（如果可用）
            this.loadServerConfig();
        } catch (error) {
            console.error('加载应用配置失败:', error);
            this.config = { ...this.defaults };
        }
    }
    
    /**
     * 从服务器配置加载
     */
    loadServerConfig() {
        try {
            // 如果服务器提供了配置API，可以在这里加载
            // 例如：fetch('/api/config').then(response => response.json())
            // 暂时跳过，因为需要服务器端支持
        } catch (error) {
            console.warn('无法从服务器加载配置:', error);
        }
    }
    
    /**
     * 保存配置
     */
    saveConfig() {
        try {
            localStorage.setItem('appConfig', JSON.stringify(this.config));
            console.log('应用配置已保存');
        } catch (error) {
            console.error('保存应用配置失败:', error);
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
    
    // ==================== 便捷方法 ====================
    
    /**
     * 获取WebSocket URL
     * @returns {string} WebSocket URL
     */
    getWebSocketUrl() {
        return this.get('WS_URL');
    }
    
    /**
     * 获取后端API URL
     * @returns {string} 后端API URL
     */
    getBackendUrl() {
        const host = this.get('YYCHAT_HOST');
        const port = this.get('YYCHAT_PORT');
        return `http://${host}:${port}`;
    }
    
    /**
     * 获取API密钥
     * @returns {string} API密钥
     */
    getApiKey() {
        return this.get('YYCHAT_API_KEY');
    }
    
    /**
     * 获取音频配置
     * @returns {Object} 音频配置
     */
    getAudioConfig() {
        return {
            sampleRate: this.get('AUDIO_SAMPLE_RATE'),
            channels: this.get('AUDIO_CHANNELS'),
            bitRate: this.get('AUDIO_BIT_RATE'),
            format: this.get('AUDIO_FORMAT'),
            mimeType: this.get('AUDIO_MIME_TYPE')
        };
    }
    
    /**
     * 获取语音配置
     * @returns {Object} 语音配置
     */
    getVoiceConfig() {
        return {
            voice: this.get('VOICE_DEFAULT'),
            volume: this.get('VOLUME_DEFAULT'),
            autoPlay: this.get('AUTO_PLAY_DEFAULT'),
            playbackVolume: this.get('PLAYBACK_VOLUME'),
            playbackRate: this.get('PLAYBACK_RATE')
        };
    }
    
    /**
     * 获取VAD配置
     * @returns {Object} VAD配置
     */
    getVADConfig() {
        return {
            threshold: this.get('VAD_THRESHOLD'),
            silenceDuration: this.get('VAD_SILENCE_DURATION'),
            maxSilenceDuration: this.get('VAD_MAX_SILENCE_DURATION'),
            silenceIncrement: this.get('VAD_SILENCE_INCREMENT'),
            nonZeroRatioThreshold: this.get('VAD_NON_ZERO_RATIO_THRESHOLD')
        };
    }
    
    /**
     * 获取录音配置
     * @returns {Object} 录音配置
     */
    getRecordingConfig() {
        return {
            chunkSize: this.get('RECORDING_CHUNK_SIZE'),
            maxDuration: this.get('RECORDING_MAX_DURATION'),
            audioChunkSize: this.get('AUDIO_CHUNK_SIZE'),
            audioSendInterval: this.get('AUDIO_SEND_INTERVAL')
        };
    }
    
    /**
     * 获取UI配置
     * @returns {Object} UI配置
     */
    getUIConfig() {
        return {
            showVisualizer: this.get('SHOW_VISUALIZER'),
            visualizerHeight: this.get('VISUALIZER_HEIGHT'),
            visualizerWidth: this.get('VISUALIZER_WIDTH')
        };
    }
    
    /**
     * 获取调试配置
     * @returns {Object} 调试配置
     */
    getDebugConfig() {
        return {
            debugMode: this.get('DEBUG_MODE'),
            logLevel: this.get('LOG_LEVEL')
        };
    }
    
    /**
     * 检查是否为本地主机
     * @returns {boolean} 是否为本地主机
     */
    isLocalhost() {
        const hostnames = this.get('LOCALHOST_HOSTNAMES');
        return hostnames.includes(location.hostname);
    }
    
    /**
     * 获取麦克风权限提示
     * @returns {string} 权限提示
     */
    getMicrophonePermissionHint() {
        return this.get('MICROPHONE_PERMISSION_HINT');
    }
}

// 创建全局配置实例
window.appConfig = new AppConfig();

// 兼容性：保持原有的配置访问方式
window.appConfig.getAutoPlaySetting = function() {
    return this.get('AUTO_PLAY_DEFAULT');
};

window.appConfig.getVoiceDefault = function() {
    return this.get('VOICE_DEFAULT');
};

window.appConfig.getPlaybackRate = function() {
    return this.get('PLAYBACK_RATE');
};

console.log('应用配置系统已初始化');
