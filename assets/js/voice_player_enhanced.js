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
        
        this.init();
    }
    
    init() {
        // 初始化WebSocket连接
        this.initWebSocket();
        
        // 绑定事件
        this.bindEvents();
    }
    
    initWebSocket() {
        try {
            // 使用全局WebSocket管理器，避免重复连接
            if (window.voiceWebSocketManager) {
                this.websocket = window.voiceWebSocketManager.getConnection();
                if (this.websocket) {
                    console.log('使用全局WebSocket连接');
                    // 通过管理器注册播放相关消息处理器，避免被其他模块覆盖onmessage
                    try {
                        window.voiceWebSocketManager.registerMessageHandler('audio_stream', (data) => this.handleAudioStream(data));
                        window.voiceWebSocketManager.registerMessageHandler('voice_response', (data) => {
                            if (data.audio_data) {
                                console.log('收到voice_response，音频长度:', data.audio_data.length);
                                this.playAudioFromBase64(data.audio_data);
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
                                    if (data.audio_data) {
                                        console.log('收到voice_response，音频长度:', data.audio_data.length);
                                        this.playAudioFromBase64(data.audio_data);
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
            
            console.log('开始语音合成:', text);
            
            // 显示语音播放状态
            this.showPlaybackStatus();
            
            // 发送文本转语音请求
            await this.requestSpeechSynthesis(text);
            
        } catch (error) {
            console.error('语音合成失败:', error);
            this.hidePlaybackStatus();
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
            if (data.audio_data) {
                // 将base64音频数据转换为AudioBuffer
                this.playAudioFromBase64(data.audio_data);
            }
        } catch (error) {
            console.error('处理音频流失败:', error);
        }
    }
    
    async playAudioFromBase64(base64Audio) {
        try {
            // 初始化音频上下文
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            // 恢复音频上下文（如果被暂停）
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            // 解码base64音频数据
            const audioData = atob(base64Audio);
            const audioBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(audioBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            // 解码音频
            const decodedAudio = await this.audioContext.decodeAudioData(audioBuffer);
            
            // 播放音频
            await this.playAudioBuffer(decodedAudio);
            
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
                    resolve();
                };
                
                // 开始播放
                source.start(0);
                this.isPlaying = true;
                this.currentAudio = source;
                
                console.log('开始播放音频');
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    handleSynthesisComplete(data) {
        console.log('语音合成完成');
        this.hidePlaybackStatus();
    }
    
    handleError(data) {
        console.error('语音合成错误:', data.message);
        this.hidePlaybackStatus();
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
