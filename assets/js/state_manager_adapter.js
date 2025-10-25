/**
 * 状态管理器兼容性适配器
 * 为新的状态管理器提供与旧unifiedButtonStateManager兼容的接口
 */

class StateManagerAdapter {
    constructor() {
        this.stateManager = window.stateManager;
        this.initializeCompatibility();
    }
    
    /**
     * 初始化兼容性接口
     */
    initializeCompatibility() {
        // 创建兼容性方法
        this.getStateInfo = this.createGetStateInfo();
        this.getButtonStateDetails = this.createGetButtonStateDetails();
        this.getStateStyles = this.createGetStateStyles();
        this.getAutoPlaySetting = this.createGetAutoPlaySetting();
        this.checkInputContent = this.createCheckInputContent();
    }
    
    /**
     * 创建getStateInfo兼容方法
     */
    createGetStateInfo() {
        return (state, scenario) => {
            const stateInfo = this.stateManager.getStateInfo();
            return {
                state: state || this.stateManager.getState(),
                scenario: scenario || null,
                isLocked: stateInfo.isLocked,
                availableTransitions: stateInfo.availableTransitions,
                description: this.getStateDescription(state || this.stateManager.getState())
            };
        };
    }
    
    /**
     * 创建getButtonStateDetails兼容方法
     */
    createGetButtonStateDetails() {
        return (state) => {
            const currentState = state || this.stateManager.getState();
            return {
                textButton: this.getButtonState('text', currentState),
                recordButton: this.getButtonState('record', currentState),
                callButton: this.getButtonState('call', currentState)
            };
        };
    }
    
    /**
     * 创建getStateStyles兼容方法
     */
    createGetStateStyles() {
        return (state) => {
            const currentState = state || this.stateManager.getState();
            return this.getStateStyle(currentState);
        };
    }
    
    /**
     * 创建getAutoPlaySetting兼容方法
     */
    createGetAutoPlaySetting() {
        return () => {
            // 默认自动播放设置
            return true;
        };
    }
    
    /**
     * 创建checkInputContent兼容方法
     */
    createCheckInputContent() {
        return () => {
            const input = document.getElementById('ai-chat-x-input');
            return input && input.value.trim().length > 0;
        };
    }
    
    /**
     * 获取状态描述
     */
    getStateDescription(state) {
        const descriptions = {
            'idle': '空闲状态',
            'text_sse': '文本SSE处理中',
            'text_tts': '文本TTS播放中',
            'text_processing': '文本处理中',
            'voice_stt': '语音识别中',
            'voice_sse': '语音SSE处理中',
            'voice_tts': '语音TTS播放中',
            'voice_processing': '语音处理中',
            'voice_call': '语音通话中',
            'calling': '语音通话中',
            'recording': '录音中',
            'processing': '处理中',
            'playing': '播放中',
            'error': '错误状态'
        };
        return descriptions[state] || '未知状态';
    }
    
    /**
     * 获取按钮状态
     */
    getButtonState(buttonType, state) {
        const buttonStates = {
            'idle': {
                text: { status: 'enabled', loading: false, disabled: false },
                record: { status: 'enabled', loading: false, disabled: false },
                call: { status: 'enabled', loading: false, disabled: false }
            },
            'text_sse': {
                text: { status: 'loading', loading: true, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'text_tts': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'text_processing': {
                text: { status: 'loading', loading: true, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'voice_stt': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'loading', loading: true, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'voice_sse': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'loading', loading: true, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'voice_tts': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'voice_processing': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'voice_call': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'loading', loading: true, disabled: true }
            },
            'calling': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'loading', loading: true, disabled: true }
            },
            'recording': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'loading', loading: true, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'processing': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'playing': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            },
            'error': {
                text: { status: 'disabled', loading: false, disabled: true },
                record: { status: 'disabled', loading: false, disabled: true },
                call: { status: 'disabled', loading: false, disabled: true }
            }
        };
        
        return buttonStates[state]?.[buttonType] || { status: 'disabled', loading: false, disabled: true };
    }
    
    /**
     * 获取状态样式
     */
    getStateStyle(state) {
        const styles = {
            'idle': {
                textButton: { backgroundColor: '#1890ff', color: 'white' },
                recordButton: { backgroundColor: '#52c41a', color: 'white' },
                callButton: { backgroundColor: '#722ed1', color: 'white' }
            },
            'text_sse': {
                textButton: { backgroundColor: '#faad14', color: 'white' },
                recordButton: { backgroundColor: '#d9d9d9', color: '#666' },
                callButton: { backgroundColor: '#d9d9d9', color: '#666' }
            },
            'text_tts': {
                textButton: { backgroundColor: '#d9d9d9', color: '#666' },
                recordButton: { backgroundColor: '#d9d9d9', color: '#666' },
                callButton: { backgroundColor: '#d9d9d9', color: '#666' }
            },
            'voice_stt': {
                textButton: { backgroundColor: '#d9d9d9', color: '#666' },
                recordButton: { backgroundColor: '#faad14', color: 'white' },
                callButton: { backgroundColor: '#d9d9d9', color: '#666' }
            },
            'voice_sse': {
                textButton: { backgroundColor: '#d9d9d9', color: '#666' },
                recordButton: { backgroundColor: '#faad14', color: 'white' },
                callButton: { backgroundColor: '#d9d9d9', color: '#666' }
            },
            'voice_tts': {
                textButton: { backgroundColor: '#d9d9d9', color: '#666' },
                recordButton: { backgroundColor: '#d9d9d9', color: '#666' },
                callButton: { backgroundColor: '#d9d9d9', color: '#666' }
            },
            'voice_call': {
                textButton: { backgroundColor: '#d9d9d9', color: '#666' },
                recordButton: { backgroundColor: '#d9d9d9', color: '#666' },
                callButton: { backgroundColor: '#faad14', color: 'white' }
            },
            'error': {
                textButton: { backgroundColor: '#ff4d4f', color: 'white' },
                recordButton: { backgroundColor: '#ff4d4f', color: 'white' },
                callButton: { backgroundColor: '#ff4d4f', color: 'white' }
            }
        };
        
        return styles[state] || styles['idle'];
    }
}

// 创建全局适配器实例
window.unifiedButtonStateManager = new StateManagerAdapter();

console.log('🔄 状态管理器兼容性适配器已初始化');
