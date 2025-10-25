/**
 * 语音状态协调器 - 统一管理所有语音相关状态
 * 提供状态同步、消息分发、事件管理等功能
 */

class VoiceStateCoordinator {
    constructor() {
        this.currentState = 'idle';
        this.currentScenario = null;
        this.currentMetadata = {};
        this.stateListeners = new Map();
        this.messageHandlers = new Map();
        this.eventListeners = new Map();
        
        // 状态定义
        this.STATES = {
            IDLE: 'idle',
            TEXT_PROCESSING: 'text_processing',
            RECORDING: 'recording',
            VOICE_PROCESSING: 'voice_processing',
            CALLING: 'calling',
            INTERRUPTED: 'interrupted'
        };
        
        // 场景定义
        this.SCENARIOS = {
            TEXT_CHAT: 'text_chat',
            VOICE_RECORDING: 'voice_recording',
            VOICE_CALL: 'voice_call'
        };
        
        // 消息类型定义
        this.MESSAGE_TYPES = {
            AUDIO_STREAM: 'audio_stream',
            VOICE_RESPONSE: 'voice_response',
            SYNTHESIS_COMPLETE: 'synthesis_complete',
            TRANSCRIPTION_RESULT: 'transcription_result',
            VOICE_CALL_STARTED: 'voice_call_started',
            VOICE_CALL_STOPPED: 'voice_call_stopped',
            INTERRUPT_CONFIRMED: 'interrupt_confirmed',
            STOP_PLAYBACK: 'stop_playback'
        };
        
        // 事件类型定义
        this.EVENT_TYPES = {
            STATE_CHANGED: 'state_changed',
            MESSAGE_RECEIVED: 'message_received',
            ERROR_OCCURRED: 'error_occurred',
            CONNECTION_CHANGED: 'connection_changed'
        };
        
        this.init();
    }
    
    /**
     * 初始化协调器
     */
    init() {
        window.controlledLog?.log('语音状态协调器已初始化');
        
        // 注册默认消息处理器
        this.registerDefaultHandlers();
        
        // 监听全局事件
        this.setupGlobalEventListeners();
    }
    
    /**
     * 注册默认消息处理器
     */
    registerDefaultHandlers() {
        // 音频流消息处理器
        this.registerMessageHandler(this.MESSAGE_TYPES.AUDIO_STREAM, (data) => {
            this.dispatchEvent(this.EVENT_TYPES.MESSAGE_RECEIVED, {
                type: this.MESSAGE_TYPES.AUDIO_STREAM,
                data
            });
        });
        
        // 语音响应消息处理器
        this.registerMessageHandler(this.MESSAGE_TYPES.VOICE_RESPONSE, (data) => {
            this.dispatchEvent(this.EVENT_TYPES.MESSAGE_RECEIVED, {
                type: this.MESSAGE_TYPES.VOICE_RESPONSE,
                data
            });
        });
        
        // 合成完成消息处理器
        this.registerMessageHandler(this.MESSAGE_TYPES.SYNTHESIS_COMPLETE, (data) => {
            this.dispatchEvent(this.EVENT_TYPES.MESSAGE_RECEIVED, {
                type: this.MESSAGE_TYPES.SYNTHESIS_COMPLETE,
                data
            });
        });
        
        // 转录结果消息处理器
        this.registerMessageHandler(this.MESSAGE_TYPES.TRANSCRIPTION_RESULT, (data) => {
            this.dispatchEvent(this.EVENT_TYPES.MESSAGE_RECEIVED, {
                type: this.MESSAGE_TYPES.TRANSCRIPTION_RESULT,
                data
            });
        });
    }
    
    /**
     * 设置全局事件监听器
     */
    setupGlobalEventListeners() {
        // 监听WebSocket连接状态变化
        document.addEventListener('voiceWebSocketConnecting', (event) => {
            this.dispatchEvent(this.EVENT_TYPES.CONNECTION_CHANGED, event.detail);
        });
        
        // 监听语音状态变化
        document.addEventListener('voiceStateChange', (event) => {
            this.handleStateChange(event.detail.oldState, event.detail.newState);
        });
    }
    
    /**
     * 统一状态更新
     * @param {string} newState - 新状态
     * @param {string} scenario - 场景
     * @param {Object} metadata - 元数据
     */
    updateState(newState, scenario = null, metadata = {}) {
        const oldState = this.currentState;
        const oldScenario = this.currentScenario;
        
        // 检查状态是否真的发生了变化
        if (oldState === newState && oldScenario === scenario) {
            return; // 状态没有变化，跳过更新
        }
        
        // 更新状态
        this.currentState = newState;
        this.currentScenario = scenario;
        this.currentMetadata = { ...metadata };
        
        window.controlledLog?.log('状态已更新:', {
            oldState,
            newState,
            oldScenario,
            scenario,
            metadata
        });
        
        // 通知状态变化
        this.notifyStateChange(oldState, newState, oldScenario, scenario, metadata);
        
        // 更新Dash状态
        this.updateDashState(newState, scenario, metadata);
        
        // 触发状态变化事件
        this.dispatchEvent(this.EVENT_TYPES.STATE_CHANGED, {
            oldState,
            newState,
            oldScenario,
            scenario,
            metadata
        });
    }
    
    /**
     * 通知状态变化
     * @param {string} oldState - 旧状态
     * @param {string} newState - 新状态
     * @param {string} oldScenario - 旧场景
     * @param {string} scenario - 新场景
     * @param {Object} metadata - 元数据
     */
    notifyStateChange(oldState, newState, oldScenario, scenario, metadata) {
        // 通知所有状态监听器
        this.stateListeners.forEach((listener, id) => {
            try {
                listener(oldState, newState, oldScenario, scenario, metadata);
            } catch (error) {
                console.error(`状态监听器 ${id} 执行失败:`, error);
            }
        });
    }
    
    /**
     * 更新Dash状态
     * @param {string} state - 状态
     * @param {string} scenario - 场景
     * @param {Object} metadata - 元数据
     */
    updateDashState(state, scenario, metadata) {
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
            }
        } catch (error) {
            console.error('更新Dash状态失败:', error);
        }
    }
    
    /**
     * 处理状态变化
     * @param {string} oldState - 旧状态
     * @param {string} newState - 新状态
     */
    handleStateChange(oldState, newState) {
        // 处理特殊状态转换
        if (newState === this.STATES.INTERRUPTED) {
            this.handleInterruption();
        } else if (newState === this.STATES.IDLE) {
            this.handleIdle();
        }
    }
    
    /**
     * 处理中断状态
     */
    handleInterruption() {
        window.controlledLog?.log('处理中断状态');
        // 停止所有音频播放
        if (window.voicePlayerEnhanced) {
            window.voicePlayerEnhanced.forceStopAllAudio();
        }
        // 停止录音
        if (window.voiceRecorderEnhanced && window.voiceRecorderEnhanced.isRecording) {
            window.voiceRecorderEnhanced.stopRecording();
        }
    }
    
    /**
     * 处理空闲状态
     */
    handleIdle() {
        window.controlledLog?.log('处理空闲状态');
        // 清理资源
        this.cleanup();
    }
    
    /**
     * 清理资源
     */
    cleanup() {
        // 🔧 关键修复：只清理语音通话相关的状态，保留其他场景的状态
        if (window.voicePlayerEnhanced && window.voicePlayerEnhanced.audioContext) {
            // 只清理包含 'voice_call' 的流状态
            for (const [messageId, state] of window.voicePlayerEnhanced.streamStates.entries()) {
                if (messageId.includes('voice_call')) {
                    window.voicePlayerEnhanced.streamStates.delete(messageId);
                    window.controlledLog?.log('🧹 状态协调器清理语音通话流状态:', messageId);
                }
            }
            
            // 只清理包含 'voice_call' 的播放消息
            for (const messageId of window.voicePlayerEnhanced.playedMessages) {
                if (messageId.includes('voice_call')) {
                    window.voicePlayerEnhanced.playedMessages.delete(messageId);
                    window.controlledLog?.log('🧹 状态协调器清理语音通话播放消息:', messageId);
                }
            }
        }
    }
    
    /**
     * 统一消息处理
     * @param {string} messageType - 消息类型
     * @param {Object} data - 消息数据
     */
    handleMessage(messageType, data) {
        window.controlledLog?.log('处理消息:', { messageType, data });
        
        const handler = this.messageHandlers.get(messageType);
        if (handler) {
            try {
                handler(data);
            } catch (error) {
                console.error(`消息处理器 ${messageType} 执行失败:`, error);
                this.dispatchEvent(this.EVENT_TYPES.ERROR_OCCURRED, {
                    type: 'message_handler_error',
                    messageType,
                    error: error.message
                });
            }
        } else {
            console.warn('未找到消息处理器:', messageType);
        }
    }
    
    /**
     * 注册状态监听器
     * @param {string} id - 监听器ID
     * @param {Function} listener - 监听器函数
     */
    registerStateListener(id, listener) {
        this.stateListeners.set(id, listener);
        window.controlledLog?.log('状态监听器已注册:', id);
    }
    
    /**
     * 注销状态监听器
     * @param {string} id - 监听器ID
     */
    unregisterStateListener(id) {
        this.stateListeners.delete(id);
        window.controlledLog?.log('状态监听器已注销:', id);
    }
    
    /**
     * 注册消息处理器
     * @param {string} messageType - 消息类型
     * @param {Function} handler - 处理器函数
     */
    registerMessageHandler(messageType, handler) {
        this.messageHandlers.set(messageType, handler);
        window.controlledLog?.log('消息处理器已注册:', messageType);
    }
    
    /**
     * 注销消息处理器
     * @param {string} messageType - 消息类型
     */
    unregisterMessageHandler(messageType) {
        this.messageHandlers.delete(messageType);
        window.controlledLog?.log('消息处理器已注销:', messageType);
    }
    
    /**
     * 注册事件监听器
     * @param {string} eventType - 事件类型
     * @param {Function} listener - 监听器函数
     */
    addEventListener(eventType, listener) {
        if (!this.eventListeners.has(eventType)) {
            this.eventListeners.set(eventType, new Set());
        }
        this.eventListeners.get(eventType).add(listener);
        window.controlledLog?.log('事件监听器已注册:', eventType);
    }
    
    /**
     * 注销事件监听器
     * @param {string} eventType - 事件类型
     * @param {Function} listener - 监听器函数
     */
    removeEventListener(eventType, listener) {
        if (this.eventListeners.has(eventType)) {
            this.eventListeners.get(eventType).delete(listener);
            window.controlledLog?.log('事件监听器已注销:', eventType);
        }
    }
    
    /**
     * 分发事件
     * @param {string} eventType - 事件类型
     * @param {Object} data - 事件数据
     */
    dispatchEvent(eventType, data) {
        if (this.eventListeners.has(eventType)) {
            this.eventListeners.get(eventType).forEach(listener => {
                try {
                    listener(data);
                } catch (error) {
                    console.error(`事件监听器 ${eventType} 执行失败:`, error);
                }
            });
        }
    }
    
    /**
     * 获取当前状态
     * @returns {Object} 当前状态信息
     */
    getCurrentState() {
        return {
            state: this.currentState,
            scenario: this.currentScenario,
            metadata: { ...this.currentMetadata }
        };
    }
    
    /**
     * 检查状态
     * @param {string} state - 状态
     * @returns {boolean} 是否匹配
     */
    isState(state) {
        return this.currentState === state;
    }
    
    /**
     * 检查场景
     * @param {string} scenario - 场景
     * @returns {boolean} 是否匹配
     */
    isScenario(scenario) {
        return this.currentScenario === scenario;
    }
    
    /**
     * 检查是否在特定状态和场景
     * @param {string} state - 状态
     * @param {string} scenario - 场景
     * @returns {boolean} 是否匹配
     */
    isInStateAndScenario(state, scenario) {
        return this.currentState === state && this.currentScenario === scenario;
    }
    
    /**
     * 获取状态信息
     * @returns {string} 状态描述
     */
    getStateInfo() {
        const stateNames = {
            [this.STATES.IDLE]: '空闲',
            [this.STATES.TEXT_PROCESSING]: '文本处理中',
            [this.STATES.RECORDING]: '录音中',
            [this.STATES.VOICE_PROCESSING]: '语音处理中',
            [this.STATES.CALLING]: '通话中',
            [this.STATES.INTERRUPTED]: '已中断'
        };
        
        const scenarioNames = {
            [this.SCENARIOS.TEXT_CHAT]: '文本聊天',
            [this.SCENARIOS.VOICE_RECORDING]: '录音对话',
            [this.SCENARIOS.VOICE_CALL]: '语音通话'
        };
        
        const stateText = stateNames[this.currentState] || this.currentState;
        const scenarioText = scenarioNames[this.currentScenario] || this.currentScenario || '';
        
        return `${scenarioText} - ${stateText}`;
    }
}

// 创建全局实例
window.voiceStateCoordinator = new VoiceStateCoordinator();

window.controlledLog?.log('语音状态协调器已初始化');
