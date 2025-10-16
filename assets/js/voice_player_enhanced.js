/**
 * 增强版语音播放器 - 支持文本转语音和流式播放
 */

class VoicePlayerEnhanced {
    constructor() {
        this.audioContext = null;
        this.audioQueue = [];
        this.isPlaying = false;
        this.currentAudio = null;
        this.websocket = null;
        this.synthesisSettings = {
            voice: 'alloy',
            speed: 1.0,
            volume: 0.8
        };
        this.playedMessages = new Set(); // 记录已播放的消息ID，避免重复播放
        this.streamStates = new Map(); // message_id -> { chunks: [{seq, base64}], nextSeq, codec, session_id }
        
        // 异步初始化
        this.init().catch(error => {
            console.error('播放器初始化失败:', error);
        });
    }
    
    async init() {
        // 初始化WebSocket连接
        await this.initWebSocket();
        
        // 绑定事件
        this.bindEvents();
        
        // 初始化音频上下文（需要用户交互）
        this.initAudioContext();
        
        // 监听状态变化
        this.initStateListener();
    }
    
    /**
     * 初始化状态监听
     */
    initStateListener() {
        // 监听全局状态变化
        window.addEventListener('voiceStateChange', (event) => {
            const { oldState, newState } = event.detail;
            this.onStateChange(oldState, newState);
        });
    }
    
    /**
     * 状态变化处理
     */
    onStateChange(oldState, newState) {
        console.log(`播放器状态变化: ${oldState} → ${newState}`);
        
        // 如果状态变为中断，停止播放
        if (newState === 'interrupted' && this.isPlaying) {
            this.stopPlayback();
        }
    }
    
    initAudioContext() {
        // 在用户交互时初始化音频上下文
        const initAudio = () => {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                console.log('音频上下文已初始化');
            }
        };
        
        // 监听用户交互事件
        document.addEventListener('click', initAudio, { once: true });
        document.addEventListener('touchstart', initAudio, { once: true });
        document.addEventListener('keydown', initAudio, { once: true });
    }
    
    async initWebSocket() {
        try {
            // 使用全局WebSocket管理器，避免重复连接
            if (window.voiceWebSocketManager) {
                // 等待连接建立
                this.websocket = await window.voiceWebSocketManager.waitForConnection();
                if (this.websocket) {
                    console.log('播放器使用共享WebSocket连接');
                    // 通过管理器注册播放相关消息处理器，避免被其他模块覆盖onmessage
                    try {
                        window.voiceWebSocketManager.registerMessageHandler('audio_stream', (data) => this.handleAudioStream(data));
                        window.voiceWebSocketManager.registerMessageHandler('voice_response', (data) => {
                            console.log('收到voice_response消息:', data);
                            
                            // 检查是否已经播放过这个消息
                            const messageId = data.message_id;
                            if (messageId && this.playedMessages.has(messageId)) {
                                console.log('消息已播放过，跳过:', messageId);
                                return;
                            }
                            
                            // 停止当前播放
                            this.stopCurrentAudio();
                            
                            if (data.audio) {
                                console.log('收到voice_response，音频长度:', data.audio.length);
                                this.enqueueSingleShot(data.audio, data.message_id, data.session_id, data.codec || 'audio/mpeg');
                                if (messageId) {
                                    this.playedMessages.add(messageId);
                                }
                            } else if (data.audio_data) {
                                console.log('收到voice_response，音频长度:', data.audio_data.length);
                                this.enqueueSingleShot(data.audio_data, data.message_id, data.session_id, data.codec || 'audio/mpeg');
                                if (messageId) {
                                    this.playedMessages.add(messageId);
                                }
                            } else {
                                console.warn('voice_response消息没有audio或audio_data字段:', data);
                            }
                        });
                        window.voiceWebSocketManager.registerMessageHandler('synthesis_complete', (data) => this.handleSynthesisComplete(data));
                    } catch (e) { console.warn('注册播放器消息处理器失败:', e); }
                } else {
                    console.log('WebSocket管理器未连接，等待连接...');
                    // 等待连接建立
                    setTimeout(() => {
                        this.websocket = window.voiceWebSocketManager.getConnection();
                        if (this.websocket) {
                            try {
                                window.voiceWebSocketManager.registerMessageHandler('audio_stream', (data) => this.handleAudioStream(data));
                                window.voiceWebSocketManager.registerMessageHandler('voice_response', (data) => {
                                    console.log('收到voice_response消息（延迟注册）:', data);
                                    
                                    // 检查是否已经播放过这个消息
                                    const messageId = data.message_id;
                                    if (messageId && this.playedMessages.has(messageId)) {
                                        console.log('消息已播放过，跳过:', messageId);
                                        return;
                                    }
                                    
                                    // 停止当前播放
                                    this.stopCurrentAudio();
                                    
                                    if (data.audio) {
                                        console.log('收到voice_response，音频长度:', data.audio.length);
                                        this.enqueueSingleShot(data.audio, data.message_id, data.session_id, data.codec || 'audio/mpeg');
                                        if (messageId) {
                                            this.playedMessages.add(messageId);
                                        }
                                    } else if (data.audio_data) {
                                        console.log('收到voice_response，音频长度:', data.audio_data.length);
                                        this.enqueueSingleShot(data.audio_data, data.message_id, data.session_id, data.codec || 'audio/mpeg');
                                        if (messageId) {
                                            this.playedMessages.add(messageId);
                                        }
                                    } else {
                                        console.warn('voice_response消息没有audio或audio_data字段（延迟注册）:', data);
                                    }
                                });
                                window.voiceWebSocketManager.registerMessageHandler('synthesis_complete', (data) => this.handleSynthesisComplete(data));
                            } catch (e) { console.warn('延迟注册播放器处理器失败:', e); }
                        }
                    }, 1000);
                    return;
                }
            } else {
                // 从全局配置获取WebSocket URL
                const wsUrl = window.voiceConfig?.WS_URL || 'ws://192.168.66.209:9800/ws/chat';
                this.websocket = new WebSocket(wsUrl);
                console.log('创建新的WebSocket连接');
                this.setupWebSocketHandlers();
            }
        } catch (error) {
            console.error('初始化语音播放WebSocket失败:', error);
        }
    }
    
    setupWebSocketHandlers() {
        if (!this.websocket) return;
        
        this.websocket.onopen = () => {
            console.log('语音播放WebSocket连接已建立');
        };
        
        this.websocket.onmessage = (event) => {
            this.handleWebSocketMessage(event);
        };
        
        this.websocket.onerror = (error) => {
            console.error('语音播放WebSocket错误:', error);
        };
        
        this.websocket.onclose = () => {
            console.log('语音播放WebSocket连接已关闭');
        };
    }
    
    bindEvents() {
        // 方案B：默认不再在前端收到messageCompleted后主动TTS
        // 若需回退到前端触发TTS，可设置 window.voiceConfig.FRONTEND_TTS_FALLBACK = true
        document.addEventListener('messageCompleted', (event) => {
            try {
                if (window.voiceConfig && window.voiceConfig.FRONTEND_TTS_FALLBACK === true) {
                    if (event.detail && event.detail.text) {
                        this.synthesizeAndPlay(event.detail.text);
                    }
                }
            } catch (e) {
                console.warn('messageCompleted TTS fallback 失败:', e);
            }
        });
    }
    
    async synthesizeAndPlay(text) {
        try {
            if (!text || !text.trim()) {
                console.log('没有文本需要合成语音');
                return;
            }
            
            // 通知统一按钮状态管理器开始播放
            if (window.unifiedButtonStateManager) {
                window.unifiedButtonStateManager.startPlayingTTS();
            }
            
            console.log('开始语音合成:', text);
            
            // 更新状态为播放中
            if (window.voiceStateManager) {
                window.voiceStateManager.startPlaying();
            }
            
            // 显示语音播放状态
            this.showPlaybackStatus();
            
            // 发送文本转语音请求
            await this.requestSpeechSynthesis(text);
            
        } catch (error) {
            console.error('语音合成失败:', error);
            this.hidePlaybackStatus();
            
            // 播放失败，重置状态
            if (window.voiceStateManager) {
                window.voiceStateManager.setState(window.voiceStateManager.STATES.IDLE);
            }
        }
    }
    
    async requestSpeechSynthesis(text) {
        return new Promise((resolve, reject) => {
            if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                reject(new Error('WebSocket连接不可用'));
                return;
            }
            
            const message = {
                type: 'speech_synthesis',
                text: text,
                voice: this.synthesisSettings.voice,
                speed: this.synthesisSettings.speed,
                volume: this.synthesisSettings.volume
            };
            
            this.websocket.send(JSON.stringify(message));
            resolve();
        });
    }
    
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);

            // 基于session_id过滤，避免串音
            const sessionIdEl = document.getElementById('ai-chat-x-current-session-id');
            const currentSessionId = sessionIdEl?.value || '';
            // 仅当服务端提供了session_id且与当前会话不一致时才丢弃；
            // 若服务端暂未附带session_id，但client_id匹配则允许播放
            if (typeof data.session_id !== 'undefined' && currentSessionId && data.session_id !== currentSessionId) {
                return;
            }
            
            switch (data.type) {
                case 'audio_stream':
                    this.handleAudioStream(data);
                    break;
                case 'voice_response':
                    // 一次性音频响应（base64）
                    if (data.audio_data) {
                        console.log('收到voice_response，音频长度:', data.audio_data.length);
                        this.playAudioFromBase64(data.audio_data);
                    }
                    break;
                case 'synthesis_complete':
                    this.handleSynthesisComplete(data);
                    break;
                case 'error':
                    this.handleError(data);
                    break;
                default:
                    console.log('收到语音播放WebSocket消息:', data);
            }
        } catch (error) {
            console.error('处理语音播放WebSocket消息失败:', error);
        }
    }
    
    handleAudioStream(data) {
        try {
            const messageId = data.message_id || 'unknown';
            const sessionId = data.session_id || null;
            const codec = data.codec || 'audio/mpeg';
            const base64 = data.audio || data.audio_data;
            const seq = typeof data.seq === 'number' ? data.seq : null;

            if (!base64) {
                return;
            }

            // 初始化该消息的流状态
            if (!this.streamStates.has(messageId)) {
                this.streamStates.set(messageId, {
                    chunks: [],
                    nextSeq: (seq !== null ? seq : 0),
                    codec: codec,
                    session_id: sessionId,
                    playing: false
                });
            }
            const state = this.streamStates.get(messageId);

            // 记录分片
            state.chunks.push({ seq: (seq !== null ? seq : state.chunks.length), base64 });
            // 根据seq排序，确保按序播放
            state.chunks.sort((a, b) => a.seq - b.seq);

            // 若未在播放该消息，则启动播放循环
            if (!state.playing) {
                state.playing = true;
                this.playStreamState(messageId).catch(err => {
                    console.error('播放流失败:', err);
                    state.playing = false;
                });
            }
        } catch (error) {
            console.error('处理音频流失败:', error);
        }
    }

    async playStreamState(messageId) {
        const state = this.streamStates.get(messageId);
        if (!state) return;

        while (state.chunks.length > 0) {
            // 取出最小seq的分片
            const chunk = state.chunks.shift();
            try {
                await this.playAudioFromBase64(chunk.base64);
            } catch (e) {
                console.warn('播放分片失败，跳过该分片:', e);
            }
        }

        state.playing = false;
    }

    enqueueSingleShot(base64, messageId, sessionId, codec) {
        try {
            if (!messageId) {
                // 无messageId则直接播放一次
                this.playAudioFromBase64(base64);
                return;
            }
            if (!this.streamStates.has(messageId)) {
                this.streamStates.set(messageId, {
                    chunks: [],
                    nextSeq: 0,
                    codec: codec,
                    session_id: sessionId,
                    playing: false
                });
            }
            const state = this.streamStates.get(messageId);
            state.chunks.push({ seq: state.chunks.length, base64 });
            if (!state.playing) {
                state.playing = true;
                this.playStreamState(messageId).catch(err => {
                    console.error('一次性音频播放失败:', err);
                    state.playing = false;
                });
            }
        } catch (e) {
            console.warn('enqueueSingleShot失败:', e);
        }
    }
    
    stopCurrentAudio() {
        if (this.currentAudio) {
            try {
                this.currentAudio.stop();
                this.currentAudio.disconnect();
                console.log('停止当前音频播放');
            } catch (error) {
                console.warn('停止音频播放失败:', error);
            }
            this.currentAudio = null;
        }
        this.isPlaying = false;
    }
    
    async playAudioFromBase64(base64Audio) {
        try {
            console.log('开始播放音频，base64长度:', base64Audio.length);
            
            // 停止当前播放
            this.stopCurrentAudio();
            
            // 初始化音频上下文
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                console.log('音频上下文已创建');
            }
            
            // 恢复音频上下文（如果被暂停）
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
                console.log('音频上下文已恢复');
            }
            
            console.log('音频上下文状态:', this.audioContext.state);
            
            // 解码base64音频数据
            const audioData = atob(base64Audio);
            const audioBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(audioBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            console.log('音频数据长度:', audioBuffer.byteLength);
            
            // 解码音频
            const decodedAudio = await this.audioContext.decodeAudioData(audioBuffer);
            console.log('音频解码成功，时长:', decodedAudio.duration, '秒');
            
            // 播放音频
            await this.playAudioBuffer(decodedAudio);
            console.log('音频播放完成');
            
        } catch (error) {
            console.error('播放音频失败:', error);
        }
    }
    
    async playAudioBuffer(audioBuffer) {
        return new Promise((resolve, reject) => {
            try {
                const source = this.audioContext.createBufferSource();
                const gainNode = this.audioContext.createGain();
                
                source.buffer = audioBuffer;
                gainNode.gain.value = this.synthesisSettings.volume;
                
                // 连接音频节点
                source.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
                
                // 设置播放结束回调
                source.onended = () => {
                    this.isPlaying = false;
                    
                    // 播放完成，更新状态
                    if (window.voiceStateManager) {
                        window.voiceStateManager.finishPlaying();
                    }
                    
                    // 通知统一按钮状态管理器播放完成 (通过dcc.Store)
                    if (window.dash_clientside && window.dash_clientside.set_props) {
                        window.dash_clientside.set_props('button-event-trigger', {
                            data: {type: 'tts_complete', timestamp: Date.now()}
                        });
                        console.log('TTS播放完成，触发状态更新');
                    }
                    
                    resolve();
                };
                
                // 开始播放
                source.start(0);
                this.isPlaying = true;
                this.currentAudio = source;
                
                // 通知统一按钮状态管理器TTS播放开始 (通过dcc.Store)
                if (window.dash_clientside && window.dash_clientside.set_props) {
                    window.dash_clientside.set_props('button-event-trigger', {
                        data: {type: 'tts_start', timestamp: Date.now()}
                    });
                    console.log('TTS播放开始，触发状态更新');
                }
                
                console.log('开始播放音频');
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    handleSynthesisComplete(data) {
        console.log('语音合成完成');
        this.hidePlaybackStatus();
        
        // 合成完成，如果当前没有播放，则重置状态
        if (!this.isPlaying && window.voiceStateManager) {
            window.voiceStateManager.finishPlaying();
        }
    }
    
    handleError(data) {
        console.error('语音合成错误:', data.message);
        this.hidePlaybackStatus();
        
        // 播放错误，重置状态
        if (window.voiceStateManager) {
            window.voiceStateManager.setState(window.voiceStateManager.STATES.IDLE);
        }
    }
    
    /**
     * 停止播放
     */
    stopPlayback() {
        console.log('停止播放');
        
        // 通知统一按钮状态管理器停止播放
        if (window.unifiedButtonStateManager) {
            window.unifiedButtonStateManager.stopPlayingOrComplete();
        }
        
        // 停止当前音频
        this.stopCurrentAudio();
        
        // 清空音频队列
        this.audioQueue = [];
        
        // 清空流状态
        this.streamStates.clear();
        
        // 隐藏播放状态
        this.hidePlaybackStatus();
        
        // 重置播放状态
        this.isPlaying = false;
    }
    
    showPlaybackStatus() {
        // 创建播放状态指示器
        let statusIndicator = document.getElementById('voice-playback-status');
        if (!statusIndicator) {
            statusIndicator = document.createElement('div');
            statusIndicator.id = 'voice-playback-status';
            statusIndicator.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 25px;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateX(100%);
                transition: transform 0.3s ease;
            `;
            document.body.appendChild(statusIndicator);
        }
        
        statusIndicator.innerHTML = `
            <div style="width: 16px; height: 16px; border: 2px solid white; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            正在播放语音...
        `;
        
        // 显示动画
        setTimeout(() => {
            statusIndicator.style.transform = 'translateX(0)';
        }, 100);
        
        // 添加旋转动画
        if (!document.getElementById('voice-playback-spin-animation')) {
            const style = document.createElement('style');
            style.id = 'voice-playback-spin-animation';
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    hidePlaybackStatus() {
        const statusIndicator = document.getElementById('voice-playback-status');
        if (statusIndicator) {
            statusIndicator.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (statusIndicator.parentNode) {
                    statusIndicator.parentNode.removeChild(statusIndicator);
                }
            }, 300);
        }
    }
    
    stopPlayback() {
        if (this.currentAudio) {
            try {
                this.currentAudio.stop();
                this.currentAudio = null;
                this.isPlaying = false;
                
                // 通知统一按钮状态管理器播放停止 (通过dcc.Store)
                if (window.dash_clientside && window.dash_clientside.set_props) {
                    window.dash_clientside.set_props('button-event-trigger', {
                        data: {type: 'tts_stop', timestamp: Date.now()}
                    });
                    console.log('TTS播放停止，触发状态更新');
                }
                
                console.log('停止语音播放');
            } catch (error) {
                console.error('停止播放失败:', error);
            }
        }
        this.hidePlaybackStatus();
    }
    
    setVoiceSettings(settings) {
        this.synthesisSettings = { ...this.synthesisSettings, ...settings };
        console.log('语音设置已更新:', this.synthesisSettings);
    }
    
    // 公共方法：手动触发语音播放
    playText(text) {
        this.synthesizeAndPlay(text);
    }
}

// 初始化语音播放器
document.addEventListener('DOMContentLoaded', () => {
    window.voicePlayer = new VoicePlayerEnhanced();
});

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoicePlayerEnhanced;
}
