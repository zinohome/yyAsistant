/**
 * Unified Button State Manager
 * 
 * 基于官方推荐的Dash Clientside Callback + dcc.Store架构
 * 不直接操作DOM，而是返回样式数据供clientside callback使用
 * 
 * 架构：
 * - 使用dcc.Store作为单一状态源
 * - clientside callback监听Store变化并更新UI
 * - 状态管理器只负责提供样式数据和辅助方法
 * 
 * 创建日期: 2025-01-15
 * 版本: 2.0 (Store-based architecture)
 */

class UnifiedButtonStateManager {
    constructor() {
        // Global states for the entire system
        this.GLOBAL_STATES = {
            IDLE: 'idle',                           // All buttons available
            TEXT_PROCESSING: 'text_processing',     // Text processing (SSE)
            RECORDING: 'recording',                 // Recording in progress
            VOICE_PROCESSING: 'voice_processing',   // Voice processing (STT)
            PREPARING_TTS: 'preparing_tts',        // Preparing TTS (SSE complete)
            PLAYING_TTS: 'playing_tts',            // TTS playing
            CALLING: 'calling'                      // Real-time call in progress
        };
        
        console.log('UnifiedButtonStateManager v2.0 initialized (Store-based architecture)');
    }
    
    /**
     * Get button styles for all buttons based on state
     * Returns array: [textStyle, textLoading, textDisabled, recordStyle, recordDisabled, callStyle, callDisabled]
     * This method is called by clientside callback
     */
    getButtonStyles(state) {
        const styles = this.getStateStyles(state);
        
        return [
            styles.textButton,      // Text button style {backgroundColor, borderColor}
            styles.textLoading,     // Text button loading (true/false)
            styles.textDisabled,    // Text button disabled (true/false)
            styles.recordButton,    // Record button style {backgroundColor, borderColor}
            styles.recordDisabled,  // Record button disabled (true/false)
            styles.callButton,      // Call button style {backgroundColor, borderColor}
            styles.callDisabled     // Call button disabled (true/false)
        ];
    }
    
    /**
     * Get styles for each button based on current state
     */
    getStateStyles(state) {
        const states = {
            [this.GLOBAL_STATES.IDLE]: {
                textButton: {
                    backgroundColor: '#1890ff',
                    borderColor: '#1890ff'
                },
                textLoading: false,
                textDisabled: false,
                recordButton: {
                    backgroundColor: '#1890ff',
                    borderColor: '#1890ff',
                    boxShadow: '0 2px 4px rgba(24, 144, 255, 0.2)'
                },
                recordDisabled: false,
                callButton: {
                    backgroundColor: '#52c41a',
                    borderColor: '#52c41a',
                    boxShadow: '0 2px 4px rgba(82, 196, 26, 0.2)'
                },
                callDisabled: false
            },
            
            [this.GLOBAL_STATES.TEXT_PROCESSING]: {
                textButton: {
                    backgroundColor: '#1890ff',
                    borderColor: '#1890ff'
                },
                textLoading: true,
                textDisabled: true,
                recordButton: {
                    backgroundColor: '#d9d9d9',
                    borderColor: '#d9d9d9',
                    boxShadow: 'none'
                },
                recordDisabled: true,
                callButton: {
                    backgroundColor: '#d9d9d9',
                    borderColor: '#d9d9d9',
                    boxShadow: 'none'
                },
                callDisabled: true
            },
            
            [this.GLOBAL_STATES.RECORDING]: {
                textButton: {
                    backgroundColor: '#d9d9d9',
                    borderColor: '#d9d9d9'
                },
                textLoading: false,
                textDisabled: true,
                recordButton: {
                    backgroundColor: '#ff4d4f',
                    borderColor: '#ff4d4f',
                    boxShadow: '0 2px 4px rgba(255, 77, 79, 0.2)'
                },
                recordDisabled: false,
                callButton: {
                    backgroundColor: '#d9d9d9',
                    borderColor: '#d9d9d9',
                    boxShadow: 'none'
                },
                callDisabled: true
            },
            
            [this.GLOBAL_STATES.VOICE_PROCESSING]: {
                textButton: {
                    backgroundColor: '#1890ff',
                    borderColor: '#1890ff'
                },
                textLoading: true,
                textDisabled: true,
                recordButton: {
                    backgroundColor: '#faad14',
                    borderColor: '#faad14',
                    boxShadow: '0 2px 4px rgba(250, 173, 20, 0.2)'
                },
                recordDisabled: true,
                callButton: {
                    backgroundColor: '#d9d9d9',
                    borderColor: '#d9d9d9',
                    boxShadow: 'none'
                },
                callDisabled: true
            },
            
            [this.GLOBAL_STATES.PREPARING_TTS]: {
                textButton: {
                    backgroundColor: '#1890ff',
                    borderColor: '#1890ff'
                },
                textLoading: true,
                textDisabled: true,
                recordButton: {
                    backgroundColor: '#faad14',
                    borderColor: '#faad14',
                    boxShadow: '0 2px 4px rgba(250, 173, 20, 0.2)'
                },
                recordDisabled: true,
                callButton: {
                    backgroundColor: '#d9d9d9',
                    borderColor: '#d9d9d9',
                    boxShadow: 'none'
                },
                callDisabled: true
            },
            
            [this.GLOBAL_STATES.PLAYING_TTS]: {
                textButton: {
                    backgroundColor: '#1890ff',
                    borderColor: '#1890ff'
                },
                textLoading: true,
                textDisabled: true,
                recordButton: {
                    backgroundColor: '#52c41a',
                    borderColor: '#52c41a',
                    boxShadow: '0 2px 4px rgba(82, 196, 26, 0.2)'
                },
                recordDisabled: false,  // Can click to stop
                callButton: {
                    backgroundColor: '#d9d9d9',
                    borderColor: '#d9d9d9',
                    boxShadow: 'none'
                },
                callDisabled: true
            },
            
            [this.GLOBAL_STATES.CALLING]: {
                textButton: {
                    backgroundColor: '#d9d9d9',
                    borderColor: '#d9d9d9'
                },
                textLoading: false,
                textDisabled: true,
                recordButton: {
                    backgroundColor: '#d9d9d9',
                    borderColor: '#d9d9d9',
                    boxShadow: 'none'
                },
                recordDisabled: true,
                callButton: {
                    backgroundColor: '#ff4d4f',
                    borderColor: '#ff4d4f',
                    boxShadow: '0 2px 4px rgba(255, 77, 79, 0.2)'
                },
                callDisabled: false
            }
        };
        
        return states[state] || states[this.GLOBAL_STATES.IDLE];
    }
    
    /**
     * Check if input field has content
     * Used by clientside callback for input validation
     */
    checkInputContent() {
        const input = document.getElementById('ai-chat-x-input');
        if (!input) {
            console.warn('Input field not found');
            return false;
        }
        
        const value = input.value || '';
        const hasContent = value.trim().length > 0;
        
        if (!hasContent) {
            console.log('Input validation: empty input');
        }
        
        return hasContent;
    }
    
    /**
     * Get TTS auto-play setting from voice config
     * Used in state update callback to determine TTS behavior
     */
    getAutoPlaySetting() {
        // Check window.voiceConfig.AUTO_PLAY_DEFAULT
        if (window.voiceConfig && typeof window.voiceConfig.AUTO_PLAY_DEFAULT !== 'undefined') {
            return window.voiceConfig.AUTO_PLAY_DEFAULT;
        }
        
        // Fallback: check window.voiceConfig.autoPlay
        if (window.voiceConfig && typeof window.voiceConfig.autoPlay !== 'undefined') {
            return window.voiceConfig.autoPlay;
        }
        
        // Default: enabled
        console.log('TTS auto-play setting not found, defaulting to true');
        return true;
    }
}

// Initialize global instance
window.unifiedButtonStateManager = new UnifiedButtonStateManager();

console.log('Unified Button State Manager loaded successfully');
