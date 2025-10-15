/**
 * 语音状态管理器
 * 统一管理录音、播放、按钮的状态流转
 */

class VoiceStateManager {
    constructor() {
        // 状态定义
        this.STATES = {
            IDLE: 'idle',           // 空闲状态，可以开始录音
            RECORDING: 'recording',  // 录音中
            PROCESSING: 'processing', // 处理中（STT+SSE+TTS）
            PLAYING: 'playing',      // 播放中
            INTERRUPTED: 'interrupted' // 被中断
        };
        
        this.currentState = this.STATES.IDLE;
        this.stateHandlers = new Map();
        this.isInterrupted = false;
        
        // 初始化状态处理器
        this.initStateHandlers();
        
        console.log('语音状态管理器已初始化');
    }
    
    /**
     * 初始化状态处理器
     */
    initStateHandlers() {
        // 空闲状态处理器
        this.stateHandlers.set(this.STATES.IDLE, () => {
            this.updateButtonState('mic', '开始录音', true);
            this.isInterrupted = false;
        });
        
        // 录音状态处理器
        this.stateHandlers.set(this.STATES.RECORDING, () => {
            this.updateButtonState('recording', '录音中...', false);
        });
        
        // 处理状态处理器
        this.stateHandlers.set(this.STATES.PROCESSING, () => {
            this.updateButtonState('processing', '处理中...', false);
            // 处理中状态时，不要禁用文本提交按钮
            console.log('语音处理中，保持文本提交按钮可用');
        });
        
        // 播放状态处理器
        this.stateHandlers.set(this.STATES.PLAYING, () => {
            this.updateButtonState('playing', '播放中，点击中断', true);
        });
        
        // 中断状态处理器
        this.stateHandlers.set(this.STATES.INTERRUPTED, () => {
            this.updateButtonState('interrupted', '已中断', false);
            // 延迟重置到空闲状态
            setTimeout(() => {
                this.setState(this.STATES.IDLE);
            }, 1000);
        });
    }
    
    /**
     * 设置状态
     */
    setState(newState) {
        if (this.STATES[newState] || Object.values(this.STATES).includes(newState)) {
            const oldState = this.currentState;
            this.currentState = newState;
            
            console.log(`语音状态变更: ${oldState} → ${newState}`);
            
            // 执行状态处理器
            const handler = this.stateHandlers.get(newState);
            if (handler) {
                handler();
            }
            
            // 通知状态变化
            this.notifyStateChange(oldState, newState);
        } else {
            console.error('无效的语音状态:', newState);
        }
    }
    
    /**
     * 获取当前状态
     */
    getState() {
        return this.currentState;
    }
    
    /**
     * 检查是否处于指定状态
     */
    isState(state) {
        return this.currentState === state;
    }
    
    /**
     * 检查是否可以开始录音
     */
    canStartRecording() {
        return this.currentState === this.STATES.IDLE;
    }
    
    /**
     * 检查是否可以中断
     */
    canInterrupt() {
        return this.currentState === this.STATES.PLAYING;
    }
    
    /**
     * 开始录音
     */
    startRecording() {
        if (this.canStartRecording()) {
            this.setState(this.STATES.RECORDING);
            return true;
        }
        return false;
    }
    
    /**
     * 录音完成，开始处理
     */
    startProcessing() {
        this.setState(this.STATES.PROCESSING);
    }
    
    /**
     * 开始播放
     */
    startPlaying() {
        this.setState(this.STATES.PLAYING);
    }
    
    /**
     * 播放完成
     */
    finishPlaying() {
        if (this.currentState === this.STATES.PLAYING) {
            this.setState(this.STATES.IDLE);
        }
    }
    
    /**
     * 中断播放
     */
    interrupt() {
        if (this.canInterrupt()) {
            this.isInterrupted = true;
            this.setState(this.STATES.INTERRUPTED);
            
            // 停止音频播放
            if (window.voicePlayerEnhanced) {
                window.voicePlayerEnhanced.stopPlayback();
            }
            
            // 发送中断信号到后端
            this.sendInterruptSignal();
            
            return true;
        }
        return false;
    }
    
    /**
     * 发送中断信号到后端
     */
    sendInterruptSignal() {
        if (window.voiceWebSocketManager && window.voiceWebSocketManager.isConnected) {
            window.voiceWebSocketManager.sendMessage({
                type: 'interrupt',
                timestamp: Date.now() / 1000,
                client_id: window.voiceWebSocketManager.clientId,
                session_id: window.voiceWebSocketManager.sessionId
            });
            console.log('已发送中断信号到后端');
        }
    }
    
    /**
     * 更新按钮状态
     */
    updateButtonState(icon, text, clickable) {
        // 更新按钮图标和文本
        const button = document.getElementById('voice-record-button');
        if (button) {
            // 更新图标
            const iconMap = {
                'mic': '🎤',
                'recording': '⏹️', // 录音中显示停止图标
                'processing': '⏳',
                'playing': '⏸️',
                'interrupted': '⏹️'
            };
            
            // 更新按钮内容
            const iconElement = button.querySelector('svg');
            if (iconElement) {
                // 更新图标
                iconElement.innerHTML = iconMap[icon] || '🎤';
            } else {
                // 如果没有SVG元素，直接更新按钮内容
                button.innerHTML = iconMap[icon] || '🎤';
            }
            
            // 更新按钮标题
            button.title = text;
            // 录音中状态应该可以点击停止录音
            if (icon === 'recording') {
                button.disabled = false; // 录音中状态允许点击停止
            } else {
                button.disabled = !clickable;
            }
            
            // 更新按钮样式
            button.className = `voice-button ${icon}`;
            
            // 更新按钮颜色 - 使用更清晰的配色
            if (icon === 'recording') {
                // 录音中：红色背景，白色图标
                button.style.backgroundColor = '#ff4d4f';
                button.style.borderColor = '#ff4d4f';
                button.style.color = '#ffffff';
            } else if (icon === 'playing') {
                // 播放中：绿色背景，白色图标
                button.style.backgroundColor = '#52c41a';
                button.style.borderColor = '#52c41a';
                button.style.color = '#ffffff';
            } else if (icon === 'processing') {
                // 处理中：橙色背景，白色图标
                button.style.backgroundColor = '#faad14';
                button.style.borderColor = '#faad14';
                button.style.color = '#ffffff';
            } else {
                // 空闲状态：蓝色背景，白色图标
                button.style.backgroundColor = '#1890ff';
                button.style.borderColor = '#1890ff';
                button.style.color = '#ffffff';
            }
        }
        
        // 更新全局状态
        if (window.voiceChatState) {
            window.voiceChatState.currentState = this.currentState;
            window.voiceChatState.isInterrupted = this.isInterrupted;
        }
    }
    
    /**
     * 通知状态变化
     */
    notifyStateChange(oldState, newState) {
        // 通知录音器
        if (window.voiceRecorderEnhanced) {
            window.voiceRecorderEnhanced.onStateChange(oldState, newState);
        }
        
        // 通知播放器
        if (window.voicePlayerEnhanced) {
            window.voicePlayerEnhanced.onStateChange(oldState, newState);
        }
        
        // 通知其他组件
        window.dispatchEvent(new CustomEvent('voiceStateChange', {
            detail: { oldState, newState, currentState: this.currentState }
        }));
    }
    
    /**
     * 重置到空闲状态
     */
    reset() {
        this.isInterrupted = false;
        this.setState(this.STATES.IDLE);
    }
    
    /**
     * 获取状态信息
     */
    getStatus() {
        return {
            currentState: this.currentState,
            isInterrupted: this.isInterrupted,
            canStartRecording: this.canStartRecording(),
            canInterrupt: this.canInterrupt()
        };
    }
    
    /**
     * 处理按钮点击事件
     */
    handleButtonClick() {
        console.log('语音按钮被点击，当前状态:', this.currentState);
        
        if (this.currentState === this.STATES.IDLE) {
            // 空闲状态：开始录音
            console.log('开始录音');
            this.startRecording();
            
            // 触发录音器开始录音
            if (window.voiceRecorderEnhanced) {
                window.voiceRecorderEnhanced.startRecording();
            }
            
            return true;
        } else if (this.currentState === this.STATES.RECORDING) {
            // 录音中状态：停止录音
            console.log('停止录音');
            
            // 直接调用录音器的停止录音方法
            if (window.voiceRecorderEnhanced) {
                console.log('状态管理器调用录音器停止录音');
                await window.voiceRecorderEnhanced.stopRecording();
            }
            
            return true;
        } else if (this.canInterrupt()) {
            // 播放中状态：中断播放
            console.log('中断播放');
            this.interrupt();
            return true;
        } else {
            console.log('当前状态不允许操作:', this.currentState);
            return false;
        }
    }
}

// 创建全局实例
window.voiceStateManager = new VoiceStateManager();

// 导出按钮点击处理方法到全局命名空间，供Dash客户端回调使用
window.voiceStateManager.handleButtonClick = window.voiceStateManager.handleButtonClick.bind(window.voiceStateManager);

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceStateManager;
}
