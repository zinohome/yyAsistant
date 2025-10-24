/**
 * 统一按钮状态管理器 v2.0
 * 基于 Dash Store 架构，管理所有按钮的状态和样式
 */

class UnifiedButtonStateManager {
    constructor() {
        console.log('UnifiedButtonStateManager v2.0 initialized (Store-based architecture)');
        
        // 全局状态定义
        this.GLOBAL_STATES = {
            IDLE: 'idle',                           // S0: 所有按钮可用
            TEXT_PROCESSING: 'text_processing',     // S1: 文本处理中（SSE+TTS全程）
            RECORDING: 'recording',                 // S1: 录音中
            PROCESSING: 'processing',               // S2: 语音处理中（STT+SSE+TTS全程）
            VOICE_PROCESSING: 'voice_processing',   // S2: 语音处理中（STT+SSE+TTS全程）- 别名
            CALLING: 'calling'                      // S1: 实时通话中
        };
        
        // 场景定义
        this.SCENARIOS = {
            TEXT_CHAT: 'text_chat',
            VOICE_RECORDING: 'voice_recording',
            VOICE_CALL: 'voice_call'
        };
        
        // 颜色定义
        this.COLORS = {
            TEXT: '#1890ff',      // 蓝色
            RECORD: '#dc2626',    // 红色
            CALL: '#52c41a',      // 绿色
            DISABLED: '#d9d9d9',  // 灰色
            PROCESSING: '#faad14' // 橙色
        };
        
        // 状态更新防抖
        this.updateTimer = null;
        this.lastState = null;
        this.lastScenario = null;
        
        this.initializeStateHandlers();
        console.log('Unified Button State Manager loaded successfully');
    }
    
    /**
     * 初始化状态处理器
     */
    initializeStateHandlers() {
        // 可以在这里添加状态变化时的处理逻辑
    }
    
    /**
     * 防抖状态更新
     * @param {string} state - 状态
     * @param {string} scenario - 场景
     * @param {Object} metadata - 元数据
     */
    debouncedStateUpdate(state, scenario, metadata) {
        // 检查状态是否真的发生了变化
        if (this.lastState === state && this.lastScenario === scenario) {
            return; // 状态没有变化，跳过更新
        }
        
        // 清除之前的定时器
        if (this.updateTimer) {
            clearTimeout(this.updateTimer);
        }
        
        // 设置新的定时器
        this.updateTimer = setTimeout(() => {
            this.performStateUpdate(state, scenario, metadata);
        }, 16); // 约60fps
    }
    
    /**
     * 执行状态更新
     * @param {string} state - 状态
     * @param {string} scenario - 场景
     * @param {Object} metadata - 元数据
     */
    performStateUpdate(state, scenario, metadata) {
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
                
                // 更新最后状态
                this.lastState = state;
                this.lastScenario = scenario;
                
                console.log('状态已更新:', { state, scenario, metadata });
            }
        } catch (error) {
            console.error('状态更新失败:', error);
        }
    }
    
    /**
     * 开始播放TTS - 使用公共工具优化
     */
    startPlayingTTS() {
        console.log('🎵 开始播放TTS，更新按钮状态');
        VoiceUtils.updateState('processing', 'voice_recording', { tts_playing: true });
    }
    
    /**
     * 停止播放或完成 - 使用公共工具优化
     */
    stopPlayingOrComplete() {
        console.log('🎵 停止播放TTS，重置按钮状态');
        VoiceUtils.updateState('idle', null, {});
    }
    
    /**
     * 获取按钮状态样式
     */
    getStateStyles(state) {
        const states = {
            [this.GLOBAL_STATES.IDLE]: {
                textButton: { backgroundColor: this.COLORS.TEXT, borderColor: this.COLORS.TEXT },
                textLoading: false, textDisabled: false,
                recordButton: { 
                    backgroundColor: this.COLORS.RECORD, 
                    borderColor: this.COLORS.RECORD, 
                    color: '#ffffff' 
                },
                recordDisabled: false,
                callButton: { backgroundColor: this.COLORS.CALL, borderColor: this.COLORS.CALL },
                callDisabled: false
            },
            
            [this.GLOBAL_STATES.TEXT_PROCESSING]: {
                textButton: { backgroundColor: this.COLORS.TEXT, borderColor: this.COLORS.TEXT },
                textLoading: true, textDisabled: true,
                recordButton: { backgroundColor: this.COLORS.DISABLED, borderColor: this.COLORS.DISABLED },
                recordDisabled: true,
                callButton: { backgroundColor: this.COLORS.DISABLED, borderColor: this.COLORS.DISABLED },
                callDisabled: true
            },
            
            [this.GLOBAL_STATES.RECORDING]: {
                textButton: { backgroundColor: this.COLORS.DISABLED, borderColor: this.COLORS.DISABLED },
                textLoading: false, textDisabled: true,
                recordButton: { 
                    backgroundColor: this.COLORS.RECORD, 
                    borderColor: this.COLORS.RECORD, 
                    color: '#ffffff' 
                },
                recordDisabled: false,
                callButton: { backgroundColor: this.COLORS.DISABLED, borderColor: this.COLORS.DISABLED },
                callDisabled: true
            },
            
            [this.GLOBAL_STATES.PROCESSING]: {
                textButton: { backgroundColor: this.COLORS.TEXT, borderColor: this.COLORS.TEXT },
                textLoading: true, textDisabled: true,
                recordButton: { 
                    backgroundColor: this.COLORS.PROCESSING, 
                    borderColor: this.COLORS.PROCESSING, 
                    color: '#ffffff' 
                },
                recordDisabled: true,
                callButton: { backgroundColor: this.COLORS.DISABLED, borderColor: this.COLORS.DISABLED },
                callDisabled: true
            },
            
            [this.GLOBAL_STATES.VOICE_PROCESSING]: {
                textButton: { backgroundColor: this.COLORS.TEXT, borderColor: this.COLORS.TEXT },
                textLoading: true, textDisabled: true,
                recordButton: { 
                    backgroundColor: this.COLORS.PROCESSING, 
                    borderColor: this.COLORS.PROCESSING, 
                    color: '#ffffff' 
                },
                recordDisabled: true,
                callButton: { backgroundColor: this.COLORS.DISABLED, borderColor: this.COLORS.DISABLED },
                callDisabled: true
            },
            
            [this.GLOBAL_STATES.CALLING]: {
                textButton: { backgroundColor: this.COLORS.DISABLED, borderColor: this.COLORS.DISABLED },
                textLoading: false, textDisabled: true,
                recordButton: { backgroundColor: this.COLORS.DISABLED, borderColor: this.COLORS.DISABLED },
                recordDisabled: true,
                callButton: { 
                    backgroundColor: this.COLORS.RECORD, 
                    borderColor: this.COLORS.RECORD, 
                    color: '#ffffff' 
                },
                callDisabled: false
            }
        };
        
        return states[state] || states[this.GLOBAL_STATES.IDLE];
    }
    
    /**
     * 显示场景和按钮状态信息
     */
    getStateInfo(state, scenario = null) {
        const stateNames = {
            [this.GLOBAL_STATES.IDLE]: 'S0: 所有按钮可用',
            [this.GLOBAL_STATES.TEXT_PROCESSING]: 'S1: 文本处理中（SSE+TTS全程）',
            [this.GLOBAL_STATES.RECORDING]: 'S1: 录音中',
            [this.GLOBAL_STATES.VOICE_PROCESSING]: 'S2: 语音处理中（STT+SSE+TTS全程）',
            [this.GLOBAL_STATES.CALLING]: 'S1: 实时通话中'
        };
    
        const scenarioNames = {
            [this.SCENARIOS.TEXT_CHAT]: '场景一：文本聊天',
            [this.SCENARIOS.VOICE_RECORDING]: '场景二：录音对话',
            [this.SCENARIOS.VOICE_CALL]: '场景三：语音实时对话'
        };
        
        const scenarioText = scenario ? scenarioNames[scenario] || scenario : '';
        const stateText = stateNames[state] || state;
        
        return `${scenarioText} | ${stateText}`;
    }
    
    /**
     * 获取详细的按钮状态信息
     */
    getButtonStateDetails(state) {
        const styles = this.getStateStyles(state);
        return {
            textButton: {
                style: styles.textButton,
                loading: styles.textLoading,
                disabled: styles.textDisabled,
                status: styles.textLoading ? 'loading' : (styles.textDisabled ? 'disabled' : 'enabled')
            },
            recordButton: {
                style: styles.recordButton,
                disabled: styles.recordDisabled,
                status: styles.recordDisabled ? 'disabled' : 'enabled'
            },
            callButton: {
                style: styles.callButton,
                disabled: styles.callDisabled,
                status: styles.callDisabled ? 'disabled' : 'enabled'
            }
        };
    }
}

// 创建全局实例
window.unifiedButtonStateManager = new UnifiedButtonStateManager();