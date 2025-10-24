/**
 * Real-time State Manager for Voice Dialogue
 * 
 * Manages the state flow for real-time voice conversations,
 * including conversation history, status tracking, and UI updates.
 */

class RealtimeStateManager {
    constructor() {
        // State definitions
        this.STATES = {
            IDLE: 'idle',
            LISTENING: 'listening',
            PROCESSING: 'processing',
            SPEAKING: 'speaking',
            ERROR: 'error'
        };
        
        // Current state
        this.currentState = this.STATES.IDLE;
        this.previousState = null;
        
        // Conversation history
        this.conversationHistory = [];
        this.maxHistoryItems = 100;
        
        // Statistics
        this.stats = {
            totalMessages: 0,
            totalDuration: 0,
            averageResponseTime: 0,
            startTime: null
        };
        
        // UI elements
        this.statusElement = document.getElementById('realtime-status');
        this.historyElement = document.getElementById('realtime-chat-history');
        this.startButton = document.getElementById('realtime-start-btn');
        this.stopButton = document.getElementById('realtime-stop-btn');
        this.muteButton = document.getElementById('realtime-mute-btn');
        
        // Settings
        this.settings = {
            volume: 80,
            rate: 1.0,
            voice: 'alloy',
            muted: false
        };
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('RealtimeStateManager: Initializing...');
        
        // Bind event listeners
        this.bindEventListeners();
        
        // Register WebSocket message handlers
        this.registerWebSocketHandlers();
        
        // Initialize UI
        this.updateUI();
        
        console.log('RealtimeStateManager: Initialized');
    }
    
    bindEventListeners() {
        // Start button
        if (this.startButton) {
            this.startButton.addEventListener('click', () => {
                this.startRealtimeDialogue();
            });
        }
        
        // Stop button
        if (this.stopButton) {
            this.stopButton.addEventListener('click', () => {
                this.stopRealtimeDialogue();
            });
        }
        
        // Listen for Dash Store updates
        this.setupDashStoreListener();
        
        // Mute button
        if (this.muteButton) {
            this.muteButton.addEventListener('click', () => {
                this.toggleMute();
            });
        }
        
        // Volume slider
        const volumeSlider = document.getElementById('audio-volume-slider');
        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => {
                this.updateVolume(parseInt(e.target.value));
            });
        }
        
        // Rate slider
        const rateSlider = document.getElementById('audio-rate-slider');
        if (rateSlider) {
            rateSlider.addEventListener('input', (e) => {
                this.updateRate(parseFloat(e.target.value));
            });
        }
    }
    
    registerWebSocketHandlers() {
        console.log('RealtimeStateManager: Registering WebSocket handlers...');
        
        // Wait for WebSocket manager to be available
        const checkWebSocketManager = () => {
            if (window.voiceWebSocketManager) {
                // Register start_audio_stream handler
                window.voiceWebSocketManager.registerMessageHandler('start_audio_stream', (data) => {
                    console.log('RealtimeStateManager: Received start_audio_stream:', data);
                    this.handleStartAudioStream(data);
                });
                
                // Register realtime_dialogue_started handler
                window.voiceWebSocketManager.registerMessageHandler('realtime_dialogue_started', (data) => {
                    console.log('RealtimeStateManager: Received realtime_dialogue_started:', data);
                    this.handleRealtimeDialogueStarted(data);
                });
                
                // Register realtime_dialogue_stopped handler
                window.voiceWebSocketManager.registerMessageHandler('realtime_dialogue_stopped', (data) => {
                    console.log('RealtimeStateManager: Received realtime_dialogue_stopped:', data);
                    this.handleRealtimeDialogueStopped(data);
                });
                
                // Register audio_stream_ack handler
                window.voiceWebSocketManager.registerMessageHandler('audio_stream_ack', (data) => {
                    console.log('RealtimeStateManager: Received audio_stream_ack:', data);
                    // Audio stream acknowledged, continue listening
                });
                
                console.log('RealtimeStateManager: WebSocket handlers registered');
            } else {
                // Retry after 100ms
                setTimeout(checkWebSocketManager, 100);
            }
        };
        
        checkWebSocketManager();
    }
    
    setState(newState, metadata = {}) {
        if (this.STATES[newState] === undefined) {
            console.error(`RealtimeStateManager: Invalid state: ${newState}`);
            return false;
        }
        
        const stateValue = this.STATES[newState];
        
        if (this.currentState === stateValue) {
            console.log(`RealtimeStateManager: Already in state: ${stateValue}`);
            return true;
        }
        
        this.previousState = this.currentState;
        this.currentState = stateValue;
        
        console.log(`RealtimeStateManager: State changed: ${this.previousState} -> ${this.currentState}`);
        
        // Update UI
        this.updateUI();
        
        // Trigger state change event
        this.onStateChange(this.currentState, this.previousState, metadata);
        
        return true;
    }
    
    updateUI() {
        this.updateStatusIndicator();
        this.updateButtons();
        this.updateHistoryDisplay();
    }
    
    updateStatusIndicator() {
        if (!this.statusElement) return;
        
        const statusConfig = {
            [this.STATES.IDLE]: {
                color: 'gray',
                text: '等待开始对话',
                dot: true
            },
            [this.STATES.LISTENING]: {
                color: 'red',
                text: '正在监听语音',
                dot: true
            },
            [this.STATES.PROCESSING]: {
                color: 'orange',
                text: '处理中...',
                dot: true
            },
            [this.STATES.SPEAKING]: {
                color: 'green',
                text: 'AI正在回复',
                dot: true
            },
            [this.STATES.ERROR]: {
                color: 'red',
                text: '发生错误',
                dot: true
            }
        };
        
        const config = statusConfig[this.currentState] || statusConfig[this.STATES.IDLE];
        
        // Update badge
        const badge = this.statusElement.querySelector('.ant-badge');
        if (badge) {
            badge.className = `ant-badge ant-badge-status ant-badge-status-${config.color}`;
        }
        
        // Update text
        const textSpan = this.statusElement.querySelector('span');
        if (textSpan) {
            textSpan.textContent = config.text;
        }
    }
    
    updateButtons() {
        const isActive = this.currentState !== this.STATES.IDLE;
        
        // Start button
        if (this.startButton) {
            this.startButton.disabled = isActive;
            this.startButton.style.opacity = isActive ? '0.5' : '1';
        }
        
        // Stop button
        if (this.stopButton) {
            this.stopButton.disabled = !isActive;
            this.stopButton.style.opacity = !isActive ? '0.5' : '1';
        }
        
        // Mute button
        if (this.muteButton) {
            const muteText = this.settings.muted ? '取消静音' : '静音';
            this.muteButton.children[0].textContent = muteText;
        }
    }
    
    updateHistoryDisplay() {
        if (!this.historyElement) return;
        
        if (this.conversationHistory.length === 0) {
            this.historyElement.innerHTML = `
                <div style="text-align: center; color: #999; font-size: 14px; margin-top: 100px;">
                    暂无对话记录
                </div>
            `;
            return;
        }
        
        // Build history HTML
        const historyHTML = this.conversationHistory.map(item => {
            const timestamp = new Date(item.timestamp).toLocaleTimeString();
            const isUser = item.role === 'user';
            
            return `
                <div class="conversation-item ${isUser ? 'user-message' : 'ai-message'}" 
                     style="margin-bottom: 15px; padding: 10px; border-radius: 6px; 
                            background-color: ${isUser ? '#e6f7ff' : '#f6ffed'}; 
                            border-left: 3px solid ${isUser ? '#1890ff' : '#52c41a'};">
                    <div style="font-weight: 600; color: #666; font-size: 12px; margin-bottom: 5px;">
                        ${isUser ? '用户' : 'AI助手'} - ${timestamp}
                    </div>
                    <div style="font-size: 14px; line-height: 1.5;">
                        ${item.content}
                    </div>
                    ${item.audioUrl ? `
                        <div style="margin-top: 8px;">
                            <audio controls style="width: 100%; height: 30px;">
                                <source src="${item.audioUrl}" type="audio/mpeg">
                            </audio>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        this.historyElement.innerHTML = historyHTML;
        
        // Scroll to bottom
        this.historyElement.scrollTop = this.historyElement.scrollHeight;
    }
    
    startRealtimeDialogue() {
        console.log('RealtimeStateManager: Starting realtime dialogue');
        
        this.setState('LISTENING');
        this.stats.startTime = Date.now();
        
        // Trigger start event
        this.onDialogueStart();
    }
    
    stopRealtimeDialogue() {
        console.log('RealtimeStateManager: Stopping realtime dialogue');
        
        this.setState('IDLE');
        
        // Calculate total duration
        if (this.stats.startTime) {
            this.stats.totalDuration += Date.now() - this.stats.startTime;
            this.stats.startTime = null;
        }
        
        // Trigger stop event
        this.onDialogueStop();
    }
    
    toggleMute() {
        this.settings.muted = !this.settings.muted;
        console.log(`RealtimeStateManager: Mute toggled: ${this.settings.muted}`);
        
        this.updateButtons();
        this.onMuteToggle(this.settings.muted);
    }
    
    updateVolume(volume) {
        this.settings.volume = Math.max(0, Math.min(100, volume));
        console.log(`RealtimeStateManager: Volume updated: ${this.settings.volume}`);
        
        this.onVolumeChange(this.settings.volume);
    }
    
    updateRate(rate) {
        this.settings.rate = Math.max(0.5, Math.min(2.0, rate));
        console.log(`RealtimeStateManager: Rate updated: ${this.settings.rate}`);
        
        this.onRateChange(this.settings.rate);
    }
    
    addToHistory(role, content, audioUrl = null) {
        const historyItem = {
            role,
            content,
            audioUrl,
            timestamp: Date.now()
        };
        
        this.conversationHistory.push(historyItem);
        this.stats.totalMessages++;
        
        // Limit history size
        if (this.conversationHistory.length > this.maxHistoryItems) {
            this.conversationHistory.shift();
        }
        
        // Update display
        this.updateHistoryDisplay();
        
        console.log(`RealtimeStateManager: Added to history: ${role} - ${content.substring(0, 50)}...`);
    }
    
    clearHistory() {
        this.conversationHistory = [];
        this.stats.totalMessages = 0;
        this.updateHistoryDisplay();
        
        console.log('RealtimeStateManager: History cleared');
    }
    
    getCurrentState() {
        return {
            state: this.currentState,
            previousState: this.previousState,
            stats: { ...this.stats },
            settings: { ...this.settings },
            historyCount: this.conversationHistory.length
        };
    }
    
    // Event handlers (to be overridden)
    onStateChange(newState, previousState, metadata) {
        console.log(`RealtimeStateManager: State change event: ${previousState} -> ${newState}`);
    }
    
    onDialogueStart() {
        console.log('RealtimeStateManager: Dialogue start event');
    }
    
    onDialogueStop() {
        console.log('RealtimeStateManager: Dialogue stop event');
    }
    
    onMuteToggle(muted) {
        console.log(`RealtimeStateManager: Mute toggle event: ${muted}`);
    }
    
    onVolumeChange(volume) {
        console.log(`RealtimeStateManager: Volume change event: ${volume}`);
    }
    
    onRateChange(rate) {
        console.log(`RealtimeStateManager: Rate change event: ${rate}`);
    }
    
    setupDashStoreListener() {
        // 使用Dash Clientside Callback监听button-event-trigger store更新
        console.log('RealtimeStateManager: Using Dash Clientside Callback for button-event-trigger');
        console.log('RealtimeStateManager: Dash Store listener setup complete (via clientside callback)');
    }
    
    handleRealtimeTrigger(triggerData) {
        console.log('RealtimeStateManager: Handling trigger:', triggerData);
        
        if (triggerData.action === 'start_realtime_dialogue') {
            console.log('RealtimeStateManager: Starting realtime dialogue...');
            this.startRealtimeDialogue();
        } else if (triggerData.action === 'stop_realtime_dialogue') {
            console.log('RealtimeStateManager: Stopping realtime dialogue...');
            this.stopRealtimeDialogue();
        }
    }
    
    startRealtimeDialogue() {
        console.log('RealtimeStateManager: Starting realtime dialogue...');
        // 这里应该启动实时语音对话
        // 可以通过WebSocket发送消息到后端
        if (window.voiceWebSocketManager && window.voiceWebSocketManager.sendMessage) {
            window.voiceWebSocketManager.sendMessage({
                type: 'start_realtime_dialogue',
                timestamp: Date.now()
            });
            console.log('RealtimeStateManager: Sent start_realtime_dialogue message');
        } else {
            console.warn('RealtimeStateManager: WebSocket manager not available');
        }
    }
    
    stopRealtimeDialogue() {
        console.log('RealtimeStateManager: Stopping realtime dialogue...');
        // 这里应该停止实时语音对话
        if (window.voiceWebSocketManager && window.voiceWebSocketManager.sendMessage) {
            window.voiceWebSocketManager.sendMessage({
                type: 'stop_realtime_dialogue',
                timestamp: Date.now()
            });
            console.log('RealtimeStateManager: Sent stop_realtime_dialogue message');
        } else {
            console.warn('RealtimeStateManager: WebSocket manager not available');
        }
    }
    
    handleStartAudioStream(data) {
        console.log('RealtimeStateManager: Handling start_audio_stream:', data);
        
        // 启动实时音频流处理
        console.log('RealtimeStateManager: Starting real-time audio stream processing...');
        
        // 启动麦克风监听
        this.startMicrophoneListening();
        
        // 更新状态为监听中
        this.setState('IDLE', {
            message: '正在监听，请开始说话...',
            timestamp: Date.now()
        });
    }
    
    startMicrophoneListening() {
        console.log('RealtimeStateManager: Starting microphone listening...');
        
        // 请求麦克风权限并开始监听
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            })
                .then(stream => {
                    console.log('RealtimeStateManager: Microphone access granted');
                    this.microphoneStream = stream;
                    
                    // 使用 MediaRecorder 来录制音频
                    const options = {
                        mimeType: 'audio/webm;codecs=opus', // WebM format with Opus codec
                        audioBitsPerSecond: 128000
                    };
                    
                    try {
                        this.mediaRecorder = new MediaRecorder(stream, options);
                    } catch (e) {
                        console.warn('RealtimeStateManager: Preferred format not supported, using default');
                        this.mediaRecorder = new MediaRecorder(stream);
                    }
                    
                    this.mediaRecorder.ondataavailable = (event) => {
                        if (event.data && event.data.size > 0) {
                            console.log('RealtimeStateManager: Audio data available:', event.data.size, 'bytes');
                            // 将Blob转换为base64并发送
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                const base64data = reader.result.split(',')[1]; // 移除data:audio/webm;base64,前缀
                                if (window.voiceWebSocketManager && window.voiceWebSocketManager.sendMessage) {
                                    window.voiceWebSocketManager.sendMessage({
                                        type: 'audio_stream',
                                        audio_data: base64data,
                                        timestamp: Date.now(),
                                        client_id: window.voiceWebSocketManager.clientId,
                                        format: 'webm'  // 告诉后端这是WebM格式
                                    });
                                    console.log('RealtimeStateManager: Audio data sent (WebM format)');
                                }
                            };
                            reader.readAsDataURL(event.data);
                        }
                    };
                    
                    this.mediaRecorder.onerror = (error) => {
                        console.error('RealtimeStateManager: MediaRecorder error:', error);
                        this.setState('ERROR', {
                            message: '录音失败',
                            timestamp: Date.now()
                        });
                    };
                    
                    // 每1秒发送一次音频数据（调整间隔以平衡实时性和网络负担）
                    this.mediaRecorder.start(1000);
                    
                    console.log('RealtimeStateManager: MediaRecorder started, sending audio every 1 second');
                    
                })
                .catch(error => {
                    console.error('RealtimeStateManager: Microphone access denied:', error);
                    this.setState('ERROR', {
                        message: '麦克风权限被拒绝',
                        timestamp: Date.now()
                    });
                });
        } else {
            console.error('RealtimeStateManager: getUserMedia not supported');
            this.setState('ERROR', {
                message: '浏览器不支持麦克风访问',
                timestamp: Date.now()
            });
        }
    }
    
    startAudioAnalysis() {
        console.log('RealtimeStateManager: Starting audio analysis...');
        
        // 设置音频分析参数
        this.analyser.fftSize = 2048;
        this.bufferLength = this.analyser.frequencyBinCount;
        this.dataArray = new Uint8Array(this.bufferLength);
        
        // 开始音频分析循环
        this.audioAnalysisLoop();
    }
    
    audioAnalysisLoop() {
        if (this.currentState === this.STATES.IDLE && this.analyser && this.dataArray) {
            // 获取音频数据
            this.analyser.getByteFrequencyData(this.dataArray);
            
            // 计算音频强度
            const average = this.dataArray.reduce((a, b) => a + b) / this.bufferLength;
            
            // 检测语音活动 (降低阈值，增加调试信息)
            if (average > 10) { // 降低阈值从30到10
                console.log('RealtimeStateManager: Speech detected, average:', average);
                this.handleSpeechDetected();
            } else if (average > 5) {
                // 添加调试信息，显示音频强度
                console.log('RealtimeStateManager: Audio level:', average);
            }
            
            // 继续分析
            requestAnimationFrame(() => this.audioAnalysisLoop());
        }
    }
    
    handleSpeechDetected() {
        console.log('RealtimeStateManager: Speech detected, processing...');
        
        // 更新状态为处理中
        this.setState('IDLE', {
            message: '正在处理语音...',
            timestamp: Date.now()
        });
        
        // 收集音频数据并发送到后端
        this.collectAndSendAudioData();
    }
    
    collectAndSendAudioData() {
        console.log('RealtimeStateManager: Collecting audio data...');
        
        // 检查是否有有效的音频数据
        if (!this.dataArray || this.dataArray.length === 0) {
            console.warn('RealtimeStateManager: No audio data available');
            this.setState('IDLE', {
                message: '继续监听...',
                timestamp: Date.now()
            });
            return;
        }
        
        // 收集音频数据 (简化版本，实际应该使用MediaRecorder)
        const audioData = this.dataArray;
        
        console.log('RealtimeStateManager: Audio data type:', typeof audioData, 'length:', audioData ? audioData.length : 'null');
        console.log('RealtimeStateManager: Audio data sample:', audioData ? Array.from(audioData.slice(0, 10)) : 'null');
        
        // 检查数据有效性
        if (!audioData || audioData.length === 0) {
            console.warn('RealtimeStateManager: No audio data to send.');
            return;
        }
        
        // 将Uint8Array转换为base64编码的字符串
        const audioBytes = new Uint8Array(audioData);
        // 使用更安全的方式转换大数组
        let binaryString = '';
        for (let i = 0; i < audioBytes.length; i++) {
            binaryString += String.fromCharCode(audioBytes[i]);
        }
        const audioBase64 = btoa(binaryString);
        
        console.log('RealtimeStateManager: Base64 encoded length:', audioBase64.length);
        console.log('RealtimeStateManager: Base64 sample:', audioBase64.substring(0, 50));
        
        console.log('RealtimeStateManager: Base64 audio data length:', audioBase64.length);
        console.log('RealtimeStateManager: Base64 sample:', audioBase64.substring(0, 50));
        
        // 发送音频数据到后端
        if (window.voiceWebSocketManager && window.voiceWebSocketManager.sendMessage) {
            window.voiceWebSocketManager.sendMessage({
                type: 'audio_stream',
                audio_data: audioBase64, // 发送base64编码的音频数据
                timestamp: Date.now(),
                client_id: window.voiceWebSocketManager.clientId
            });
            console.log('RealtimeStateManager: Audio data sent to backend');
        } else {
            console.warn('RealtimeStateManager: WebSocket manager not available');
        }
        
        // 继续监听
        setTimeout(() => {
            this.setState('IDLE', {
                message: '继续监听...',
                timestamp: Date.now()
            });
        }, 1000);
    }
    
    handleRealtimeDialogueStarted(data) {
        console.log('RealtimeStateManager: Handling realtime_dialogue_started:', data);
        
        // 更新UI状态
        this.setState('IDLE', {
            message: data.message || '实时语音对话已启动',
            timestamp: Date.now()
        });
    }
    
    handleRealtimeDialogueStopped(data) {
        console.log('RealtimeStateManager: Handling realtime_dialogue_stopped:', data);
        
        // 停止实时音频流处理
        console.log('RealtimeStateManager: Stopping real-time audio stream processing...');
        
        // 停止麦克风监听
        this.stopMicrophoneListening();
        
        // 更新状态为空闲
        this.setState('IDLE', {
            message: data.message || '实时语音对话已停止',
            timestamp: Date.now()
        });
    }
    
    stopMicrophoneListening() {
        console.log('RealtimeStateManager: Stopping microphone listening...');
        
        // 停止 MediaRecorder
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
            this.mediaRecorder = null;
        }
        
        // 停止音频流
        if (this.microphoneStream) {
            this.microphoneStream.getTracks().forEach(track => track.stop());
            this.microphoneStream = null;
        }
        
        console.log('RealtimeStateManager: Microphone listening stopped');
    }
}

// Global instance
window.realtimeStateManager = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing RealtimeStateManager...');
    window.realtimeStateManager = new RealtimeStateManager();
    console.log('RealtimeStateManager ready');
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealtimeStateManager;
}
