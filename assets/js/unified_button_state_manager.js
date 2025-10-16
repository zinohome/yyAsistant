/**
 * Unified Button State Manager
 * 
 * Manages the state of text, recording, and call buttons across different chat scenarios.
 * Coordinates button states to prevent conflicts and ensure consistent user experience.
 */

class UnifiedButtonStateManager {
    constructor() {
        // Global states for the entire system
        this.GLOBAL_STATES = {
            IDLE: 'idle',                     // All buttons available
            TEXT_PROCESSING: 'text_processing', // Text processing (SSE)
            RECORDING: 'recording',            // Recording in progress
            VOICE_PROCESSING: 'voice_processing', // Voice processing (STT)
            PREPARING_TTS: 'preparing_tts',   // Preparing TTS (SSE complete)
            PLAYING_TTS: 'playing_tts',       // TTS playing
            CALLING: 'calling'                 // Real-time call in progress
        };
        
        this.currentState = this.GLOBAL_STATES.IDLE;
        this.stateHandlers = new Map();
        this.initStateHandlers();
        
        console.log('UnifiedButtonStateManager initialized');
    }
    
    /**
     * Initialize state handlers for each state
     */
    initStateHandlers() {
        this.stateHandlers.set(this.GLOBAL_STATES.IDLE, () => {
            this.updateTextButton('发送', false, false);
            this.updateRecordButton('录音', '🎤', '#1890ff', true);
            this.updateCallButton('通话', '📞', '#52c41a', true);
        });
        
        this.stateHandlers.set(this.GLOBAL_STATES.TEXT_PROCESSING, () => {
            this.updateTextButton('处理中', true, true);
            this.updateRecordButton('录音', '🎤', '#d9d9d9', false);
            this.updateCallButton('通话', '📞', '#d9d9d9', false);
        });
        
        this.stateHandlers.set(this.GLOBAL_STATES.RECORDING, () => {
            this.updateTextButton('发送', false, false);
            this.updateRecordButton('停止', '⏹️', '#ff4d4f', true);
            this.updateCallButton('通话', '📞', '#d9d9d9', false);
        });
        
        this.stateHandlers.set(this.GLOBAL_STATES.VOICE_PROCESSING, () => {
            this.updateTextButton('处理中', true, true);
            this.updateRecordButton('处理中', '⏳', '#faad14', false);
            this.updateCallButton('通话', '📞', '#d9d9d9', false);
        });
        
        this.stateHandlers.set(this.GLOBAL_STATES.PREPARING_TTS, () => {
            this.updateTextButton('处理中', true, true);
            this.updateRecordButton('准备播放', '⏳', '#faad14', false);
            this.updateCallButton('通话', '📞', '#d9d9d9', false);
        });
        
        this.stateHandlers.set(this.GLOBAL_STATES.PLAYING_TTS, () => {
            this.updateTextButton('处理中', true, true);
            this.updateRecordButton('停止', '⏸️', '#52c41a', true);
            this.updateCallButton('通话', '📞', '#d9d9d9', false);
        });
        
        this.stateHandlers.set(this.GLOBAL_STATES.CALLING, () => {
            this.updateTextButton('发送', false, false);
            this.updateRecordButton('录音', '🎤', '#d9d9d9', false);
            this.updateCallButton('停止', '⏹️', '#ff4d4f', true);
        });
    }
    
    /**
     * Set the current state and update UI
     */
    setState(newState) {
        if (this.currentState === newState) {
            return; // Skip update if state is the same
        }
        
        console.log(`State transition: ${this.currentState} → ${newState}`);
        this.currentState = newState;
        
        // Use requestAnimationFrame for smooth UI updates
        requestAnimationFrame(() => {
            const handler = this.stateHandlers.get(newState);
            if (handler) {
                handler();
            } else {
                console.error(`No handler found for state: ${newState}`);
            }
        });
    }
    
    /**
     * Update text button state
     */
    updateTextButton(label, disabled, loading) {
        const button = document.getElementById('ai-chat-x-send-btn');
        if (button) {
            button.disabled = disabled;
            button.loading = loading;
            if (button.children[0]) {
                button.children[0].textContent = label;
            }
        }
    }
    
    /**
     * Update recording button state
     */
    updateRecordButton(label, icon, color, clickable) {
        const button = document.getElementById('voice-record-button');
        if (button) {
            button.style.backgroundColor = color;
            if (button.children[0]) button.children[0].textContent = icon;
            if (button.children[1]) button.children[1].textContent = label;
            button.disabled = !clickable;
        }
    }
    
    /**
     * Update call button state
     */
    updateCallButton(label, icon, color, clickable) {
        const button = document.getElementById('voice-call-btn');
        if (button) {
            button.style.backgroundColor = color;
            if (button.children[0]) button.children[0].textContent = icon;
            if (button.children[1]) button.children[1].textContent = label;
            button.disabled = !clickable;
        }
    }
    
    /**
     * Check if input field has content
     */
    checkInputContent() {
        const input = document.getElementById('ai-chat-x-input');
        if (!input) {
            console.warn('Input field not found');
            return false;
        }
        const hasContent = input.value && input.value.trim().length > 0;
        console.log(`Input content check: ${hasContent}`);
        return hasContent;
    }
    
    /**
     * Show warning for empty input
     */
    showInputEmptyWarning() {
        console.log('Showing empty input warning');
        // Use Dash clientside to update global message
        if (window.dash_clientside && window.dash_clientside.updateProps) {
            window.dash_clientside.updateProps('global-message', {
                'children': '请输入消息内容',
                'type': 'warning',
                'duration': 3
            });
        }
    }
    
    /**
     * Handle text button click
     */
    handleTextButtonClick() {
        console.log('Text button clicked');
        
        // Check if we're in idle state
        if (this.currentState !== this.GLOBAL_STATES.IDLE) {
            console.log('Not in idle state, rejecting text button click');
            return false;
        }
        
        // Check input content
        if (!this.checkInputContent()) {
            this.showInputEmptyWarning();
            return false;
        }
        
        // Start text processing
        this.startTextProcessing();
        return true;
    }
    
    /**
     * Handle recording button click
     */
    handleRecordButtonClick() {
        console.log('Record button clicked');
        
        switch (this.currentState) {
            case this.GLOBAL_STATES.IDLE:
                this.startRecording();
                return true;
            case this.GLOBAL_STATES.RECORDING:
                this.stopRecording();
                return true;
            case this.GLOBAL_STATES.PLAYING_TTS:
                this.stopPlayingOrComplete();
                return true;
            default:
                console.log(`Record button click rejected in state: ${this.currentState}`);
                return false;
        }
    }
    
    /**
     * Handle call button click
     */
    handleCallButtonClick() {
        console.log('Call button clicked');
        
        switch (this.currentState) {
            case this.GLOBAL_STATES.IDLE:
                this.startCalling();
                return true;
            case this.GLOBAL_STATES.CALLING:
                this.stopCalling();
                return true;
            default:
                console.log(`Call button click rejected in state: ${this.currentState}`);
                return false;
        }
    }
    
    /**
     * Start text processing (SSE)
     */
    startTextProcessing() {
        console.log('Starting text processing');
        this.setState(this.GLOBAL_STATES.TEXT_PROCESSING);
    }
    
    /**
     * Start recording
     */
    startRecording() {
        console.log('Starting recording');
        this.setState(this.GLOBAL_STATES.RECORDING);
    }
    
    /**
     * Stop recording
     */
    stopRecording() {
        console.log('Stopping recording');
        this.setState(this.GLOBAL_STATES.VOICE_PROCESSING);
    }
    
    /**
     * STT completed, enter text processing
     */
    sttCompleted() {
        console.log('STT completed, entering text processing');
        this.setState(this.GLOBAL_STATES.TEXT_PROCESSING);
    }
    
    /**
     * Prepare for TTS (check config)
     */
    prepareForTTS() {
        console.log('Preparing for TTS');
        
        // Check AUTO_PLAY setting
        const autoPlay = this.getAutoPlaySetting();
        if (!autoPlay) {
            console.log('Auto-play disabled, skipping TTS');
            this.resetToIdle();
            return;
        }
        
        this.setState(this.GLOBAL_STATES.PREPARING_TTS);
    }
    
    /**
     * Start playing TTS
     */
    startPlayingTTS() {
        console.log('Starting TTS playback');
        this.setState(this.GLOBAL_STATES.PLAYING_TTS);
    }
    
    /**
     * Stop playing or complete
     */
    stopPlayingOrComplete() {
        console.log('Stopping TTS or completing');
        this.resetToIdle();
    }
    
    /**
     * Start calling (placeholder for future)
     */
    startCalling() {
        console.log('Starting call (future implementation)');
        this.setState(this.GLOBAL_STATES.CALLING);
    }
    
    /**
     * Stop calling
     */
    stopCalling() {
        console.log('Stopping call');
        this.resetToIdle();
    }
    
    /**
     * Reset to idle state
     */
    resetToIdle() {
        console.log('Resetting to idle state');
        this.setState(this.GLOBAL_STATES.IDLE);
    }
    
    /**
     * Get AUTO_PLAY setting from config
     */
    getAutoPlaySetting() {
        // Try to get from global config or default to true
        if (window.voiceConfig) {
            // 检查不同的配置名称
            const autoPlay = window.voiceConfig.AUTO_PLAY_DEFAULT || window.voiceConfig.autoPlay;
            if (typeof autoPlay !== 'undefined') {
                console.log('AUTO_PLAY配置:', autoPlay);
                return autoPlay;
            }
        }
        
        // Default to true if not configured
        console.log('使用默认AUTO_PLAY配置: true');
        return true;
    }
    
    /**
     * Get current state
     */
    getCurrentState() {
        return this.currentState;
    }
}

// Initialize global instance
window.unifiedButtonStateManager = new UnifiedButtonStateManager();
