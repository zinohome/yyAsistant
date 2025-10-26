/**
 * 增强版语音播放器 - 支持文本转语音和流式播放
 * 使用公共工具类优化代码复用和状态管理
 */

class VoicePlayerEnhanced {
    constructor() {
        this.audioContext = null;
        this.audioQueue = [];
        this.isPlaying = false;
        this.currentAudio = null;
        this.websocket = null;
        
        // 增强播放状态指示器
        this.enhancedPlaybackStatus = null;
        
        // 使用配置类获取合成设置
        this.synthesisSettings = {
            voice: window.voiceConfig?.get('voice') || 'shimmer',
            speed: window.voiceConfig?.get('speed') || 1.0,
            volume: window.voiceConfig?.get('volume') || 0.8
        };
        
        // 新增：合成完成与播放队列控制
        this.synthesisDone = false;      // 服务端已完成合成标记
        this.pendingSegments = 0;        // 待播放片段计数
        this.idleDebounceTimer = null;   // 回idle防抖
        
        // 流式播放：无需缓冲，收到音频立即播放
        this.playedMessages = new Set(); // 记录已播放的消息ID，避免重复播放
        this.streamStates = new Map(); // message_id -> { chunks: [{seq, base64}], nextSeq, codec, session_id }
        this.shouldStop = false; // 停止标志
        this.isPlayingVoiceCall = false; // 语音通话播放标志，确保分片按顺序播放
        
        // 异步初始化
        this.init().catch(error => {
            VoiceUtils.handleError(error, '播放器初始化');
        });
    }
    
    async init() {
        // 使用公共工具初始化WebSocket连接
        await this.initWebSocket();
        
        // 绑定事件
        this.bindEvents();
        
        // 初始化音频上下文（需要用户交互）
        this.initAudioContext();
        
        // 初始化增强播放状态指示器
        this.initEnhancedPlaybackStatus();
        
        // 初始化智能错误处理系统
        this.initSmartErrorHandler();
        
        // 初始化状态同步管理器
        this.initStateSyncManager();
        
        // 初始化自适应UI系统
        this.initAdaptiveUI();
        
        // 使用状态协调器监听状态变化
        this.initStateListener();
    }
    
    /**
     * 初始化增强播放状态指示器
     */
    initEnhancedPlaybackStatus() {
        if (window.enhancedPlaybackStatus) {
            this.enhancedPlaybackStatus = window.enhancedPlaybackStatus;
            window.controlledLog?.log('🔊 增强播放状态指示器已初始化');
        } else {
            console.warn('🔊 增强播放状态指示器未找到');
        }
    }
    
    /**
     * 初始化智能错误处理系统
     */
    initSmartErrorHandler() {
        if (window.smartErrorHandler) {
            window.controlledLog?.log('🔧 语音播放器已连接智能错误处理系统');
        } else {
            console.warn('🔧 智能错误处理系统未找到');
        }
    }
    
    /**
     * 初始化状态同步管理器
     */
    initStateSyncManager() {
        if (window.stateSyncManager) {
            // 注册语音合成状态
            window.stateSyncManager.registerState('voice_synthesis', {
                status: 'idle',
                isPlaying: false,
                isProcessing: false,
                error: null
            });
            
            window.controlledLog?.log('🔄 语音播放器已连接状态同步管理器');
        } else {
            console.warn('🔄 状态同步管理器未找到');
        }
    }
    
    /**
     * 初始化自适应UI系统
     */
    initAdaptiveUI() {
        if (window.adaptiveUI) {
            window.controlledLog?.log('🎨 语音播放器已连接自适应UI系统');
            
            // 根据用户偏好调整播放器设置
            this.applyAdaptiveSettings();
        } else {
            console.warn('🎨 自适应UI系统未找到');
        }
    }
    
    /**
     * 应用自适应设置
     */
    applyAdaptiveSettings() {
        if (window.adaptiveUI) {
            const preferences = window.adaptiveUI.getUserPreferences();
            
            // 根据用户偏好调整音频设置
            if (preferences.animationSpeed === 'fast') {
                this.synthesisSettings.speed = Math.min(this.synthesisSettings.speed * 1.2, 2.0);
            } else if (preferences.animationSpeed === 'slow') {
                this.synthesisSettings.speed = Math.max(this.synthesisSettings.speed * 0.8, 0.5);
            }
            
            // 根据视觉密度调整UI
            if (preferences.visualDensity === 'compact') {
                // 紧凑模式：减少动画效果
                this.enableCompactMode();
            } else if (preferences.visualDensity === 'spacious') {
                // 宽松模式：增加动画效果
                this.enableSpaciousMode();
            }
            
            window.controlledLog?.log('🎨 自适应设置已应用:', preferences);
        }
    }
    
    /**
     * 启用紧凑模式
     */
    enableCompactMode() {
        // 减少动画效果，提高性能
        if (this.enhancedPlaybackStatus) {
            this.enhancedPlaybackStatus.setCompactMode(true);
        }
    }
    
    /**
     * 启用宽松模式
     */
    enableSpaciousMode() {
        // 增加动画效果，提升体验
        if (this.enhancedPlaybackStatus) {
            this.enhancedPlaybackStatus.setSpaciousMode(true);
        }
    }
    
    /**
     * 初始化状态监听 - 使用状态协调器
     */
    initStateListener() {
        // 注册到状态协调器
        if (window.voiceStateCoordinator) {
            window.voiceStateCoordinator.registerStateListener('voicePlayer', (oldState, newState, oldScenario, scenario, metadata) => {
                this.onStateChange(oldState, newState, oldScenario, scenario, metadata);
            });
        } else {
            // 回退到原有方式
            window.addEventListener('voiceStateChange', (event) => {
                const { oldState, newState } = event.detail;
                this.onStateChange(oldState, newState);
            });
        }
    }
    
    /**
     * 状态变化处理
     */
    onStateChange(oldState, newState, oldScenario = null, scenario = null, metadata = {}) {
        window.controlledLog?.log(`播放器状态变化: ${oldState} → ${newState} (${scenario})`);
        
        // 如果状态变为中断，停止播放
        if (newState === 'interrupted' && this.isPlaying) {
            this.stopPlayback();
        }
        
        // 🔧 关键修复：只在语音通话场景下才清理资源，避免影响其他场景
        if (newState === 'idle') {
            // 检查是否在语音通话场景中
            const isVoiceCallScenario = scenario === 'voice_call' || 
                                      (window.voiceWebSocketManager && window.voiceWebSocketManager.isVoiceCallActive) ||
                                      (metadata && metadata.scenario === 'voice_call');
            
            if (isVoiceCallScenario) {
                window.controlledLog?.log('🧹 语音通话场景：清理资源');
                this.cleanup();
            } else {
                window.controlledLog?.log('🧹 非语音通话场景：跳过资源清理，保留其他场景状态');
            }
        }
    }
    
    /**
     * 清理资源
     */
    cleanup() {
        // 🔧 关键修复：只清理语音通话相关的状态，保留其他场景的状态
        // 只清理包含 'voice_call' 的流状态
        for (const [messageId, state] of this.streamStates.entries()) {
            if (messageId.includes('voice_call')) {
                this.streamStates.delete(messageId);
                window.controlledLog?.log('🧹 清理语音通话流状态:', messageId);
            }
        }
        
        // 只清理包含 'voice_call' 的播放消息
        for (const messageId of this.playedMessages) {
            if (messageId.includes('voice_call')) {
                this.playedMessages.delete(messageId);
                window.controlledLog?.log('🧹 清理语音通话播放消息:', messageId);
            }
        }
        
        this.shouldStop = false;
        window.controlledLog?.log('播放器资源已清理（保留其他场景状态）');
    }
    
    initAudioContext() {
        // 在用户交互时初始化音频上下文
        const initAudio = () => {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                window.controlledLog?.log('音频上下文已初始化');
            }
        };
        
        // 监听用户交互事件
        document.addEventListener('click', initAudio, { once: true });
        document.addEventListener('touchstart', initAudio, { once: true });
        document.addEventListener('keydown', initAudio, { once: true });
    }
    
    async initWebSocket() {
        try {
            // 使用公共工具初始化WebSocket连接
            const messageHandlers = {
                'audio_stream': (data) => this.handleAudioStream(data),
                'voice_response': (data) => this.handleVoiceResponse(data),
                'synthesis_complete': (data) => this.handleSynthesisComplete(data)
            };
            
            this.websocket = await VoiceUtils.initWebSocket(window.voiceWebSocketManager, messageHandlers);
            window.controlledLog?.log('播放器WebSocket连接已建立');
        } catch (error) {
            VoiceUtils.handleError(error, '播放器WebSocket初始化');
        }
    }
    
    /**
     * 处理语音响应消息
     */
    handleVoiceResponse(data) {
        window.controlledLog?.log('收到voice_response消息:', data);
        
        // 检查是否已经播放过这个消息
        const messageId = data.message_id;
        if (messageId && this.playedMessages.has(messageId)) {
            window.controlledLog?.log('消息已播放过，跳过:', messageId);
            return;
        }
        
        // 停止当前播放
        this.stopCurrentAudio();
        
        if (data.audio) {
            window.controlledLog?.log('收到voice_response，音频长度:', data.audio.length);
            this.enqueueSingleShot(data.audio, data.message_id, data.session_id, data.codec || 'audio/mpeg');
            if (messageId) {
                this.playedMessages.add(messageId);
            }
        } else if (data.audio_data) {
            window.controlledLog?.log('收到voice_response，音频长度:', data.audio_data.length);
            this.enqueueSingleShot(data.audio_data, data.message_id, data.session_id, data.codec || 'audio/mpeg');
            if (messageId) {
                this.playedMessages.add(messageId);
            }
        } else {
            console.warn('voice_response消息没有audio或audio_data字段:', data);
        }
    }
    
    setupWebSocketHandlers() {
        if (!this.websocket) return;
        
        this.websocket.onopen = () => {
            window.controlledLog?.log('语音播放WebSocket连接已建立');
        };
        
        this.websocket.onmessage = (event) => {
            this.handleWebSocketMessage(event);
        };
        
        this.websocket.onerror = (error) => {
            console.error('语音播放WebSocket错误:', error);
        };
        
        this.websocket.onclose = () => {
            window.controlledLog?.log('语音播放WebSocket连接已关闭');
        };
    }
    
    bindEvents() {
        // 监听SSE完成事件，触发TTS播放
        document.addEventListener('messageCompleted', (event) => {
            try {
                window.controlledLog?.log('🎵 SSE完成事件触发:', event.detail);
                
                // 强制启用TTS播放，确保功能正常
                if (event.detail && event.detail.text) {
                    window.controlledLog?.log('🎵 开始TTS播放:', event.detail.text.substring(0, 50) + '...');
                    
                    // 立即触发TTS播放，不延迟
                    this.synthesizeAndPlay(event.detail.text);
                } else {
                    window.controlledLog?.log('🎵 SSE完成，但没有文本内容');
                }
            } catch (e) {
                console.error('messageCompleted TTS 处理失败:', e);
                // 即使出错也要尝试播放
                if (event.detail && event.detail.text) {
                    this.synthesizeAndPlay(event.detail.text);
                }
            }
        });
    }
    
    async synthesizeAndPlay(text) {
        try {
            if (!text || !text.trim()) {
                window.controlledLog?.log('没有文本需要合成语音');
                return;
            }
            
            // 使用公共工具更新状态
            VoiceUtils.updateState('processing', 'text_chat', { tts_playing: true });
            
            window.controlledLog?.log('🎵 开始语音合成:', text.substring(0, 100) + '...');
            
            // 更新状态为播放中
            if (window.voiceStateManager) {
                window.voiceStateManager.startPlaying();
            }
            
            // 使用EnhancedPlaybackStatus显示语音播放状态
            if (this.enhancedPlaybackStatus) {
                this.enhancedPlaybackStatus.showStatus('speaking', '正在播放语音...');
            }
            
            // 发送文本转语音请求
            await this.requestSpeechSynthesis(text);
            
        } catch (error) {
            VoiceUtils.handleError(error, '语音合成');
            // 使用EnhancedPlaybackStatus隐藏语音播放状态
            if (this.enhancedPlaybackStatus) {
                this.enhancedPlaybackStatus.hide();
            }
            
            // 集成智能错误处理
            if (window.smartErrorHandler) {
                window.smartErrorHandler.handleError(error, 'tts');
            }
            
            // 更新状态同步管理器
            if (window.stateSyncManager) {
                window.stateSyncManager.updateState('voice_synthesis', {
                    status: 'error',
                    isPlaying: false,
                    isProcessing: false,
                    error: error.message || '语音合成失败'
                });
            }
            
            // 使用公共工具重置状态
            VoiceUtils.updateState('idle', null, {});
        }
    }
    
    async requestSpeechSynthesis(text) {
        return new Promise(async (resolve, reject) => {
            // 使用全局WebSocket管理器，避免重复连接
            if (window.voiceWebSocketManager) {
                this.websocket = window.voiceWebSocketManager.ws;
                
                // 检查连接状态
                if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                    window.controlledLog?.log('🔌 WebSocket未连接，等待连接建立...');
                    // 等待连接建立，而不是重新连接
                    const maxWait = 5000; // 最多等待5秒
                    const startTime = Date.now();
                    
                    while ((!this.websocket || this.websocket.readyState !== WebSocket.OPEN) && 
                           (Date.now() - startTime) < maxWait) {
                        await new Promise(resolve => setTimeout(resolve, 100));
                        this.websocket = window.voiceWebSocketManager.ws;
                    }
                    
                    if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                        reject(new Error('语音合成失败: WebSocket连接超时'));
                        return;
                    }
                }
            } else {
                reject(new Error('语音合成失败: WebSocket管理器不可用'));
                return;
            }
            
            // 使用后端支持的text_message类型，并启用语音
            const message = {
                type: 'text_message',
                content: text,
                enable_voice: true,
                voice: this.synthesisSettings.voice,
                speed: this.synthesisSettings.speed,
                volume: this.synthesisSettings.volume,
                stream: true,
                use_tools: true
            };
            
            window.controlledLog?.log('🎵 发送TTS请求:', { type: message.type, content: text.substring(0, 50) + '...', enable_voice: true });
            
            try {
                this.websocket.send(JSON.stringify(message));
                window.controlledLog?.log('🎵 TTS请求发送成功');
                resolve();
            } catch (sendError) {
                console.error('🎵 TTS请求发送失败:', sendError);
                reject(sendError);
            }
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
                        window.controlledLog?.log('收到voice_response，音频长度:', data.audio_data.length);
                        this.playAudioFromBase64(data.audio_data);
                    }
                    break;
                case 'synthesis_complete':
                    this.handleSynthesisComplete(data);
                    break;
                case 'error':
                    // 统一错误消息格式处理
                    if (data && data.error && data.error.message) {
                        data.message = data.error.message;
                    }
                    this.handleError(data);
                    break;
                default:
                    window.controlledLog?.log('收到语音播放WebSocket消息:', data);
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

            // 判断场景类型
            const isRecordingChat = sessionId && sessionId.includes('conv-');
            const isVoiceCall = sessionId && !sessionId.includes('conv-');
            const isTextChat = messageId && messageId.includes('ai-message');
            
            window.controlledLog?.log(`🎵 音频流场景判断: 录音聊天=${isRecordingChat}, 语音通话=${isVoiceCall}, 文本聊天=${isTextChat}`);
            
            if (isRecordingChat || isTextChat) {
                // 录音聊天TTS 或 文本聊天TTS：简单按序播放，不使用分片管理
                window.controlledLog?.log('🎧 聊天TTS（录音/文本），简单按序播放');
                this.playSimpleTTS(base64, messageId, seq);
            } else if (isVoiceCall) {
                // 语音通话TTS：使用复杂分片管理
                window.controlledLog?.log('🎤 语音通话TTS，使用分片管理');
                this.playVoiceCallTTS(base64, messageId, sessionId, codec, seq);
            } else {
                // 未知场景：默认简单播放
                window.controlledLog?.log('❓ 未知场景TTS，默认简单播放');
                this.playSimpleTTS(base64, messageId);
            }
        } catch (error) {
            console.error('处理音频流失败:', error);
        }
    }

    /**
     * 简单TTS播放（录音聊天和文本聊天）
     * 使用简单队列确保按序播放
     */
    async playSimpleTTS(base64, messageId, seq = null) {
        window.controlledLog?.log('🎧 简单TTS播放:', messageId);
        
        try {
            // 确保音频上下文可用
            if (!this.audioContext || this.audioContext.state === 'closed') {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                window.controlledLog?.log('🎧 重新创建音频上下文');
            }
            
            // 恢复音频上下文（如果被暂停）
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
                window.controlledLog?.log('🎧 音频上下文已恢复');
            }
            
            // 解码base64音频数据
            const audioData = atob(base64);
            const audioBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(audioBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            // 解码为AudioBuffer
            const decodedBuffer = await this.audioContext.decodeAudioData(audioBuffer);
            window.controlledLog?.log('🎧 简单TTS音频解码完成，时长:', decodedBuffer.duration.toFixed(2), '秒');
            
            // 添加到简单播放队列，确保按序播放
            this.addToSimpleQueue(decodedBuffer, messageId, seq);
            
        } catch (error) {
            console.error('❌ 简单TTS播放失败:', error);
        }
    }

    /**
     * 简单音频播放（不使用任何状态管理）
     */
    async playSimpleAudioBuffer(audioBuffer, messageId = null) {
        return new Promise((resolve, reject) => {
            try {
                window.controlledLog?.log('🎧 简单音频播放:', messageId);
                
                const source = this.audioContext.createBufferSource();
                const gainNode = this.audioContext.createGain();
                
                source.buffer = audioBuffer;
                gainNode.gain.value = this.synthesisSettings.volume;
                
                // 连接音频节点
                source.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
                
                // 设置播放结束回调
                source.onended = () => {
                    window.controlledLog?.log('🎧 简单音频播放完成:', messageId);
                    
                    // 从队列中移除已播放的音频
                    if (this.simpleQueue && this.simpleQueue.length > 0) {
                        const index = this.simpleQueue.findIndex(item => item.messageId === messageId);
                        if (index !== -1) {
                            this.simpleQueue.splice(index, 1);
                            window.controlledLog?.log('🎧 已从队列中移除:', messageId, '剩余队列长度:', this.simpleQueue.length);
                        }
                    }
                    
                    // 🚀 重置播放标志，允许处理下一个音频
                    this.simplePlaying = false;
                    
                    // 更新状态跟踪
                    if (this.streamStates.has(messageId)) {
                        const state = this.streamStates.get(messageId);
                        state.playingSources = Math.max(0, (state.playingSources || 0) - 1);
                        state.lastChunkTs = Date.now();
                        
                        // 注意：不要在这里设置 synthComplete = true
                        // 因为可能还有更多音频片段在队列中等待播放
                        // synthComplete 应该只在收到 synthesis_complete 消息时设置
                        
                        // 尝试最终收尾
                        this.maybeFinalize(messageId);
                    }
                    
                    resolve();
                };
                
                // 开始播放
                source.start();
                window.controlledLog?.log('🎧 简单音频开始播放:', messageId);
                
                // 显示播放状态指示器（只在第一个片段播放时显示）
                if (!this.isTtsPlaying) {
                    this.isTtsPlaying = true;
                    
                    // 使用EnhancedPlaybackStatus显示播放状态
                    if (this.enhancedPlaybackStatus) {
                        this.enhancedPlaybackStatus.showStatus('speaking', '正在播放语音...');
                    }
                }
                
                // 为简单播放队列创建状态跟踪
                if (!this.streamStates.has(messageId)) {
                    this.streamStates.set(messageId, {
                        synthComplete: false,
                        playingSources: 0,
                        chunks: [],
                        lastChunkTs: Date.now()
                    });
                }
                
                // 增加播放源计数（每个音频片段都要计数）
                const state = this.streamStates.get(messageId);
                state.playingSources = (state.playingSources || 0) + 1;
                
            } catch (error) {
                console.error('❌ 简单音频播放失败:', error);
                reject(error);
            }
        });
    }

    /**
     * 简单播放队列管理（支持序列号排序）
     */
    addToSimpleQueue(audioBuffer, messageId, seq = null) {
        // 初始化简单播放队列
        if (!this.simpleQueue) {
            this.simpleQueue = [];
            this.simplePlaying = false;
        }
        
        // 添加到队列（包含序列号）
        this.simpleQueue.push({
            buffer: audioBuffer,
            messageId: messageId,
            seq: seq,
            timestamp: Date.now()
        });
        
        // 按序列号排序队列
        this.simpleQueue.sort((a, b) => {
            // 如果都有序列号，按序列号排序
            if (a.seq !== null && b.seq !== null) {
                return a.seq - b.seq;
            }
            // 如果只有一个有序列号，有序列号的优先
            if (a.seq !== null && b.seq === null) {
                return -1;
            }
            if (a.seq === null && b.seq !== null) {
                return 1;
            }
            // 都没有序列号，按时间戳排序
            return a.timestamp - b.timestamp;
        });
        
        window.controlledLog?.log('🎧 添加到简单播放队列:', messageId, 'seq:', seq, '队列长度:', this.simpleQueue.length);
        
        // 如果当前没有播放，开始处理队列
        if (!this.simplePlaying) {
            this.processSimpleQueue();
        }
    }

    /**
     * 处理简单播放队列（按序播放，不清空队列）
     */
    async processSimpleQueue() {
        if (this.simplePlaying || this.simpleQueue.length === 0) {
            return;
        }
        
        this.simplePlaying = true;
        
        // 按序列号排序队列
        this.simpleQueue.sort((a, b) => {
            if (a.seq !== null && b.seq !== null) {
                return a.seq - b.seq;
            }
            if (a.seq !== null && b.seq === null) {
                return -1;
            }
            if (a.seq === null && b.seq !== null) {
                return 1;
            }
            return a.timestamp - b.timestamp;
        });
        
        // 找到下一个可播放的音频（按序列号顺序）
        const nextAudio = this.findNextPlayableSimpleAudio();
        if (nextAudio) {
            window.controlledLog?.log('🎧 处理简单播放队列:', nextAudio.messageId, 'seq:', nextAudio.seq);
            
            try {
                await this.playSimpleAudioBuffer(nextAudio.buffer, nextAudio.messageId);
                
                // 播放完成后，继续处理队列中的下一个音频
                if (this.simpleQueue.length > 0) {
                    window.controlledLog?.log('🎧 继续处理队列中的下一个音频，剩余队列长度:', this.simpleQueue.length);
                    // 延迟一点时间再处理下一个音频，避免重叠
                    setTimeout(() => {
                        this.processSimpleQueue();
                    }, 100);
                }
            } catch (error) {
                console.error('❌ 简单播放队列音频失败:', error);
            }
        }
        
        this.simplePlaying = false;
        window.controlledLog?.log('🎧 简单播放队列处理完成');
    }
    
    /**
     * 找到下一个可播放的简单音频
     */
    findNextPlayableSimpleAudio() {
        if (this.simpleQueue.length === 0) {
            return null;
        }
        
        // 按序列号排序
        this.simpleQueue.sort((a, b) => {
            if (a.seq !== null && b.seq !== null) {
                return a.seq - b.seq;
            }
            if (a.seq !== null && b.seq === null) {
                return -1;
            }
            if (a.seq === null && b.seq !== null) {
                return 1;
            }
            return a.timestamp - b.timestamp;
        });
        
        // 返回第一个音频
        return this.simpleQueue[0];
    }

    /**
     * 语音通话TTS播放（使用分片管理）
     */
    playVoiceCallTTS(base64, messageId, sessionId, codec, seq) {
        window.controlledLog?.log('🎤 语音通话TTS播放:', messageId);
        
        // 🔧 关键修复：启动语音通话播放动画
        window.controlledLog?.log('🔍 [语音通话调试] 在playVoiceCallTTS中启动播放动画');
        if (window.voiceWebSocketManager && window.voiceWebSocketManager.startVoiceCallPlaybackAnimation) {
            window.controlledLog?.log('🔍 [语音通话调试] 调用startVoiceCallPlaybackAnimation');
            window.voiceWebSocketManager.startVoiceCallPlaybackAnimation();
        } else {
            console.warn('🔍 [语音通话调试] voiceWebSocketManager或startVoiceCallPlaybackAnimation方法未找到');
        }
        
        // 初始化该消息的流状态
        if (!this.streamStates.has(messageId)) {
            this.streamStates.set(messageId, {
                chunks: [],
                nextSeq: 0,
                codec: codec,
                session_id: sessionId,
                playing: false,
                playingSources: 0,
                synthComplete: false,
                lastChunkTs: 0,
                expectedSeq: 0
            });
        }
        const state = this.streamStates.get(messageId);

        // 确定正确的序列号
        let actualSeq;
        if (seq !== null) {
            actualSeq = seq;
        } else {
            actualSeq = state.expectedSeq;
            state.expectedSeq++;
        }

        // 记录分片并更新时间戳
        state.chunks.push({ seq: actualSeq, base64, timestamp: Date.now() });
        state.lastChunkTs = Date.now();
        
        // 根据seq排序，确保按序播放
        state.chunks.sort((a, b) => a.seq - b.seq);
        
        window.controlledLog?.log(`🎤 语音通话音频分片 seq:${actualSeq}, 总分片:${state.chunks.length}`);

        // 若未在播放该消息，则启动播放循环
        if (!state.playing) {
            state.playing = true;
            this.playStreamState(messageId).catch(err => {
                console.error('语音通话播放流失败:', err);
                state.playing = false;
            });
        }
    }

    async playStreamState(messageId) {
        const state = this.streamStates.get(messageId);
        if (!state) return;

        window.controlledLog?.log(`🎵 开始播放流状态，当前分片数:${state.chunks.length}, 合成完成:${state.synthComplete}`);

        // 持续处理音频分片，直到合成完成且无更多分片
        while (state.chunks.length > 0 || !state.synthComplete) {
            // 检查是否所有分片都已播放完成
            if (state.synthComplete && state.chunks.length === 0) {
                window.controlledLog?.log('🎵 所有分片已播放完成，退出播放循环');
                break;
            }
            if (state.chunks.length > 0) {
                // 检查是否有按序的分片可以播放
                const nextChunk = this.findNextPlayableChunk(state);
                
                if (nextChunk) {
                    // 重置等待时间，因为找到了可播放的分片
                    state.lastWaitTime = null;
                    
                    // 取出并播放下一个分片
                    const chunkIndex = state.chunks.findIndex(c => c.seq === nextChunk.seq);
                    if (chunkIndex !== -1) {
                        const chunk = state.chunks.splice(chunkIndex, 1)[0];
                        window.controlledLog?.log(`🎵 播放分片 seq:${chunk.seq}, 剩余分片:${state.chunks.length}`);
                        
                        try {
                            // 🔧 语音通话音频播放：添加播放间隔，避免一股脑播放
                            await this.playAudioFromBase64(chunk.base64, messageId);
                            
                            // 🔧 添加播放间隔，确保音频分片之间有适当的间隔
                            const playbackDuration = this.estimateAudioDuration(chunk.base64);
                            const minInterval = 50; // 最小间隔50ms（增加间隔）
                            const interval = Math.max(minInterval, playbackDuration * 0.1); // 播放时长的10%作为间隔（增加间隔）
                            
                            window.controlledLog?.log(`🎵 播放间隔: ${interval}ms (播放时长: ${playbackDuration}ms)`);
                            window.controlledLog?.log('🔍 [语音通话调试] 等待播放间隔:', interval, 'ms');
                            await new Promise(resolve => setTimeout(resolve, interval));
                            
                        } catch (e) {
                            console.warn('播放分片失败，跳过该分片:', e);
                        }
                    }
                } else {
                    // 没有可播放的分片，等待新分片
                    await new Promise(resolve => setTimeout(resolve, 50));
                }
            } else {
                // 没有分片但合成未完成，等待新分片
                await new Promise(resolve => setTimeout(resolve, 50));
            }
        }

        state.playing = false;
        window.controlledLog?.log(`🎵 播放流状态完成，messageId:${messageId}`);
        // 播放循环结束后尝试收尾
        this.maybeFinalize(messageId);
    }
    
    /**
     * 估算音频播放时长（基于base64数据大小）
     */
    estimateAudioDuration(base64Audio) {
        try {
            // 解码base64获取实际数据大小
            const binaryString = atob(base64Audio);
            const dataSize = binaryString.length;
            
            // 假设是PCM16格式，采样率24kHz
            const sampleRate = 24000;
            const bytesPerSample = 2; // 16位 = 2字节
            const channels = 1; // 单声道
            
            // 计算播放时长（秒）
            const durationSeconds = dataSize / (sampleRate * bytesPerSample * channels);
            
            // 转换为毫秒
            const durationMs = durationSeconds * 1000;
            
            window.controlledLog?.log(`🎵 音频时长估算: ${durationMs.toFixed(0)}ms (数据大小: ${dataSize} bytes)`);
            return Math.max(50, durationMs); // 最小50ms
        } catch (error) {
            console.warn('音频时长估算失败，使用默认值:', error);
            return 200; // 默认200ms
        }
    }
    
    /**
     * 查找下一个可播放的分片
     * 确保按序播放，避免跳过分片
     */
    findNextPlayableChunk(state) {
        if (state.chunks.length === 0) return null;
        
        // 按序列号排序
        state.chunks.sort((a, b) => a.seq - b.seq);
        
        // 检查是否所有分片都已播放完成
        // 如果合成已完成且没有更多分片，返回null
        if (state.synthComplete && state.chunks.length === 0) {
            window.controlledLog?.log('🎵 所有分片已播放完成，合成完成');
            return null;
        }
        
        // 注意：不能基于maxSeq判断完成，因为：
        // 1. 分片可能还在传输中
        // 2. 分片可能被跳过
        // 3. 无法预知总分片数
        
        // 如果期望序列号为0，直接播放第一个分片
        if (state.nextSeq === 0) {
            const nextChunk = state.chunks[0];
            state.nextSeq = nextChunk.seq + 1;
            return nextChunk;
        }
        
        // 查找期望序列号的分片
        const expectedChunk = state.chunks.find(chunk => chunk.seq === state.nextSeq);
        if (expectedChunk) {
            state.nextSeq = expectedChunk.seq + 1;
            return expectedChunk;
        }
        
        // 如果没有找到期望的分片，采用智能跳跃策略
        // 找到所有seq >= nextSeq的分片
        const availableChunks = state.chunks.filter(chunk => chunk.seq >= state.nextSeq);
        
        if (availableChunks.length > 0) {
            // 找到最小的可用分片
            const nextAvailableChunk = availableChunks[0];
            
            // 检查是否有顺序错乱（下一个分片比期望的大很多）
            if (nextAvailableChunk.seq > state.nextSeq) {
                const skippedRange = nextAvailableChunk.seq - state.nextSeq;
                console.warn(`🎵 检测到分片跳跃: 期望${state.nextSeq}, 实际${nextAvailableChunk.seq}, 跳过分片${state.nextSeq}到${nextAvailableChunk.seq - 1} (共${skippedRange}个分片)`);
                
                // 清理被跳过的分片，避免后续重复播放
                const skippedChunks = state.chunks.filter(chunk => 
                    chunk.seq >= state.nextSeq && chunk.seq < nextAvailableChunk.seq
                );
                if (skippedChunks.length > 0) {
                    console.warn(`🎵 清理被跳过的分片: ${skippedChunks.map(c => c.seq).join(',')}`);
                    state.chunks = state.chunks.filter(chunk => 
                        !(chunk.seq >= state.nextSeq && chunk.seq < nextAvailableChunk.seq)
                    );
                }
            }
            
            // 关键：期望值直接跳到当前分片的下一个值
            // 这样后续的重复分片会被正确识别并跳过
            const oldNextSeq = state.nextSeq;
            state.nextSeq = nextAvailableChunk.seq + 1;
            
            window.controlledLog?.log(`🎵 期望值更新: ${oldNextSeq} → ${state.nextSeq} (播放分片${nextAvailableChunk.seq})`);
            return nextAvailableChunk;
        }
        
        // 如果没有任何可用分片，检查是否有分片在等待
        if (state.chunks.length > 0) {
            const now = Date.now();
            const timeSinceLastChunk = now - state.lastChunkTs;
            
            // 如果等待时间过长，说明可能有分片丢失，强制跳跃
            if (timeSinceLastChunk > 5000) {
                console.warn(`🎵 长时间无分片到达，强制跳跃。等待时间: ${timeSinceLastChunk}ms, 期望:${state.nextSeq}`);
                
                // 找到所有分片，选择最小的
                const allChunks = state.chunks.sort((a, b) => a.seq - b.seq);
                if (allChunks.length > 0) {
                    const nextChunk = allChunks[0];
                    
                    // 清理被跳过的分片
                    if (nextChunk.seq > state.nextSeq) {
                        const skippedChunks = state.chunks.filter(chunk => 
                            chunk.seq >= state.nextSeq && chunk.seq < nextChunk.seq
                        );
                        if (skippedChunks.length > 0) {
                            console.warn(`🎵 强制跳跃清理被跳过的分片: ${skippedChunks.map(c => c.seq).join(',')}`);
                            state.chunks = state.chunks.filter(chunk => 
                                !(chunk.seq >= state.nextSeq && chunk.seq < nextChunk.seq)
                            );
                        }
                    }
                    
                    const oldNextSeq = state.nextSeq;
                    state.nextSeq = nextChunk.seq + 1;
                    
                    window.controlledLog?.log(`🎵 强制跳跃: 期望值${oldNextSeq} → ${state.nextSeq} (播放分片${nextChunk.seq})`);
                    return nextChunk;
                }
            }
        }
        
        // 如果合成已完成且等待时间过长，采用跳跃策略
        const now = Date.now();
        const timeSinceLastChunk = now - state.lastChunkTs;
        
        // 更智能的等待策略：
        // 1. 如果合成完成，等待时间超过1秒就跳跃
        // 2. 如果合成未完成，等待时间超过3秒就跳跃
        const waitThreshold = state.synthComplete ? 1000 : 3000;
        
        if (timeSinceLastChunk > waitThreshold) {
            console.warn(`🎵 等待超时，跳跃到下一个可用分片。等待时间: ${timeSinceLastChunk}ms, 期望:${state.nextSeq}, 合成完成:${state.synthComplete}`);
            
            // 找到所有可用分片
            const allAvailableChunks = state.chunks.filter(chunk => chunk.seq >= state.nextSeq);
            if (allAvailableChunks.length > 0) {
                const nextAvailableChunk = allAvailableChunks[0];
                
                // 清理被跳过的分片
                if (nextAvailableChunk.seq > state.nextSeq) {
                    const skippedChunks = state.chunks.filter(chunk => 
                        chunk.seq >= state.nextSeq && chunk.seq < nextAvailableChunk.seq
                    );
                    if (skippedChunks.length > 0) {
                        console.warn(`🎵 超时跳跃清理被跳过的分片: ${skippedChunks.map(c => c.seq).join(',')}`);
                        state.chunks = state.chunks.filter(chunk => 
                            !(chunk.seq >= state.nextSeq && chunk.seq < nextAvailableChunk.seq)
                        );
                    }
                }
                
                const oldNextSeq = state.nextSeq;
                state.nextSeq = nextAvailableChunk.seq + 1;
                
                window.controlledLog?.log(`🎵 超时跳跃: 期望值${oldNextSeq} → ${state.nextSeq} (播放分片${nextAvailableChunk.seq})`);
                return nextAvailableChunk;
            }
        }
        
        // 没有可用分片，等待
        return null;
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
                window.controlledLog?.log('停止当前音频播放');
            } catch (error) {
                console.warn('停止音频播放失败:', error);
            }
            this.currentAudio = null;
        }
        this.isPlaying = false;
    }
    
    async playAudioFromBase64(base64Audio, messageId = null) {
        try {
            window.controlledLog?.log('🎵 收到音频分片，base64长度:', base64Audio.length);
            window.controlledLog?.log('🔍 [语音通话调试] playAudioFromBase64 开始执行');
            window.controlledLog?.log('🔍 [语音通话调试] 输入参数:', {
                base64Length: base64Audio.length,
                messageId: messageId,
                messageIdType: typeof messageId
            });
            
            // 聊天TTS（录音聊天和文本聊天）：完全独立处理，不受任何状态影响
            const isChatTTSEarly = messageId && (messageId.includes('ai-message') || messageId.includes('usr-message'));
            window.controlledLog?.log('🔍 [语音通话调试] 早期聊天TTS检查:', {
                isChatTTSEarly: isChatTTSEarly,
                messageId: messageId,
                includesAiMessage: messageId ? messageId.includes('ai-message') : false,
                includesUsrMessage: messageId ? messageId.includes('usr-message') : false
            });
            
            if (isChatTTSEarly) {
                window.controlledLog?.log('🎧 聊天TTS播放，完全独立处理');
                this.playStandardAudio(base64Audio, messageId);
                return;
            }
            
            // 🛑 检查是否正在打断，如果是则忽略新的音频
            if (this.shouldStop) {
                window.controlledLog?.log('🛑 正在打断中，忽略新的音频数据');
                return;
            }
            
            // 初始化音频上下文
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 24000, // 明确指定采样率
                    latencyHint: 'interactive' // 低延迟模式
                });
                window.controlledLog?.log('🎧 音频上下文已创建，采样率:', this.audioContext.sampleRate);
            }
            
            // 🚀 检查音频上下文状态，如果被关闭则重新创建
            if (this.audioContext.state === 'closed') {
                window.controlledLog?.log('🔄 音频上下文已关闭，重新创建');
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 24000,
                    latencyHint: 'interactive'
                });
            }
            
            // 恢复音频上下文（如果被暂停）
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
                window.controlledLog?.log('▶️ 音频上下文已恢复');
            }
            
            // 🔧 关键修复：语音通话判断逻辑
            // 语音通话的特征：没有特定的messageId格式，或者messageId为空
            // 录音聊天TTS的特征：messageId包含'ai-message'或'usr-message'
            const isChatTTS = messageId && (messageId.includes('ai-message') || messageId.includes('usr-message'));
            const isVoiceCall = !isChatTTS; // 不是聊天TTS就是语音通话
            
            window.controlledLog?.log('🎧 音频来源判断:', {
                messageId: messageId,
                isChatTTS: isChatTTS,
                isVoiceCall: isVoiceCall
            });
            window.controlledLog?.log('🔍 [语音通话调试] 最终路由决策:', {
                isChatTTS: isChatTTS,
                isVoiceCall: isVoiceCall,
                willUseVoiceCall: isVoiceCall,
                willUseStandard: !isVoiceCall
            });
            
            if (isVoiceCall) {
                // 语音通话：直接流式播放，不显示播放指示器
                window.controlledLog?.log('🎧 语音通话音频，直接流式播放（不显示播放指示器）');
                window.controlledLog?.log('🔍 [语音通话调试] 调用 playVoiceCallAudio');
                await this.playVoiceCallAudio(base64Audio, messageId);
            } else {
                // 录音聊天TTS：使用标准音频格式，显示播放指示器
                window.controlledLog?.log('🎧 录音聊天TTS，使用标准音频格式（显示播放指示器）');
                window.controlledLog?.log('🔍 [语音通话调试] 调用 playStandardAudio');
                await this.playStandardAudio(base64Audio, messageId);
            }
            
        } catch (error) {
            console.error('❌ 处理音频分片失败:', error);
            window.controlledLog?.log('🔍 [语音通话调试] 播放失败详情:', {
                error: error.message,
                stack: error.stack,
                messageId: messageId
            });
        }
    }
    
    // 语音通话音频播放（参考备份中的正确实现）
    async playVoiceCallAudio(base64Audio, messageId = null) {
        try {
            window.controlledLog?.log('🎧 播放语音通话音频，base64长度:', base64Audio.length);
            
            // 解码base64音频数据
            const binaryString = atob(base64Audio);
            const audioBuffer = new ArrayBuffer(binaryString.length);
            const view = new Uint8Array(audioBuffer);
            
            for (let i = 0; i < binaryString.length; i++) {
                view[i] = binaryString.charCodeAt(i);
            }
            
            // 转换为PCM16
            const pcm16Data = new Int16Array(audioBuffer);
            const float32Data = new Float32Array(pcm16Data.length);
            
            // PCM16到Float32转换
            for (let i = 0; i < pcm16Data.length; i++) {
                float32Data[i] = pcm16Data[i] / 32768.0;
            }
            
            // 创建音频缓冲区
            const audioBufferNode = this.audioContext.createBuffer(1, float32Data.length, 24000);
            audioBufferNode.copyToChannel(float32Data, 0);
            
            window.controlledLog?.log('🎵 语音通话音频准备完成，时长:', audioBufferNode.duration.toFixed(2), '秒');
            
            // 🔧 关键修复：使用播放队列管理，确保顺序播放（参考备份实现）
            this.addToPlayQueue(audioBufferNode, messageId);
            
        } catch (error) {
            console.error('❌ 语音通话音频播放失败:', error);
        }
    }
    
    // 标准音频播放（用于录音聊天TTS）
    async playStandardAudio(base64Audio, messageId = null) {
        try {
            window.controlledLog?.log('🎧 播放标准音频格式，base64长度:', base64Audio.length);
            
            // 🚀 检查是否是语音通话的残留音频
            if (messageId && messageId.includes('voice_call_')) {
                console.warn('🚫 跳过语音通话残留音频:', messageId);
                return;
            }
            
            // 检查WebSocket连接状态
            if (!window.voiceWebSocketManager || !window.voiceWebSocketManager.isConnected) {
                console.warn('🎧 WebSocket未连接，跳过音频播放');
                return;
            }
            
            // 初始化录音聊天的流状态
            if (messageId && !this.streamStates.has(messageId)) {
                this.streamStates.set(messageId, {
                    chunks: [],
                    nextSeq: 0,
                    codec: 'audio/mpeg',
                    synthComplete: false,
                    playingSources: 0,
                    lastChunkTs: Date.now()
                });
                window.controlledLog?.log('🎧 录音聊天流状态已初始化:', messageId);
            }
            
            // 检查音频上下文状态
            if (!this.audioContext || this.audioContext.state === 'closed') {
                window.controlledLog?.log('🔄 音频上下文已关闭，重新创建');
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 24000,
                    latencyHint: 'interactive'
                });
            }
            
            // 使用标准的音频解码
            const audioData = atob(base64Audio);
            const audioBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(audioBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            // 解码为AudioBuffer（标准格式）
            const decodedBuffer = await this.audioContext.decodeAudioData(audioBuffer);
            
            window.controlledLog?.log('🎵 标准音频解码完成，时长:', decodedBuffer.duration.toFixed(2), '秒');
            
            // 🚀 录音聊天TTS使用简单播放队列，确保按序播放
            this.addToSimpleQueue(decodedBuffer, messageId);
            
        } catch (error) {
            console.error('❌ 标准音频播放失败:', error);
        }
    }
    
    // 播放队列管理：确保音频顺序播放，避免重叠
    addToPlayQueue(audioBuffer, messageId = null) {
        // 🚀 检查是否应该停止，如果是则忽略新的音频
        if (this.shouldStop) {
            window.controlledLog?.log('🛑 正在停止中，忽略新的音频数据');
            return;
        }
        
        // 添加到播放队列
        this.audioQueue.push({
            buffer: audioBuffer,
            messageId: messageId,
            timestamp: Date.now()
        });
        
        window.controlledLog?.log('📋 音频分片已添加到播放队列，队列长度:', this.audioQueue.length);
        
        // 如果当前没有播放，开始播放队列
        if (!this.isPlaying) {
            this.processPlayQueue();
        }
    }
    
    // 停止当前播放并清空队列（用于打断机制）
    stopCurrentPlayback() {
        window.controlledLog?.log('🛑 立即停止当前播放并清空队列');
        
        // 🚀 设置停止标志 - 不要重置，保持停止状态
        this.shouldStop = true;
        
        // 🚀 立即停止当前播放的音频源（最高优先级）
        if (this.currentAudio) {
            try {
                this.currentAudio.stop(0); // 立即停止，不等待
                this.currentAudio.disconnect();
                window.controlledLog?.log('🛑 当前音频源已立即停止');
            } catch (error) {
                window.controlledLog?.log('当前音频已停止');
            }
            this.currentAudio = null;
        }
        
        // 🚀 立即清空播放队列
        this.playQueue = [];
        this.audioQueue = []; // 清空所有队列
        this.isPlaying = false;
        
        // 强制停止所有音频上下文中的音频源
        if (this.audioContext && this.audioContext.state !== 'closed') {
            try {
                // 断开所有连接
                const destination = this.audioContext.destination;
                if (destination) {
                    destination.disconnect();
                }
                
                // 重新创建音频上下文以确保完全停止
                this.audioContext.close();
                this.audioContext = null;
                window.controlledLog?.log('🛑 音频上下文已强制关闭');
            } catch (error) {
                window.controlledLog?.log('音频上下文清理完成');
            }
        }
        
        // 清空播放队列
        this.audioQueue = [];
        this.isPlaying = false;
        
        // 清空所有流状态
        this.streamStates.clear();
        
        // 不要重置shouldStop标志，保持停止状态直到下次开始播放
        window.controlledLog?.log('✅ 播放已立即停止，队列已清空，状态已重置');
    }
    
    async processPlayQueue() {
        // 检查停止标志
        if (this.shouldStop) {
            window.controlledLog?.log('🛑 检测到停止标志，停止队列处理');
            this.isPlaying = false;
            return;
        }
        
        if (this.audioQueue.length === 0) {
            window.controlledLog?.log('📋 播放队列为空');
            this.isPlaying = false;
            return;
        }
        
        if (this.isPlaying) {
            window.controlledLog?.log('🎵 正在播放中，等待当前音频完成');
            return;
        }
        
        this.isPlaying = true;
        const audioItem = this.audioQueue.shift();
        
        window.controlledLog?.log('🎵 开始播放队列中的音频，剩余队列长度:', this.audioQueue.length);
        
        try {
            await this.playAudioBuffer(audioItem.buffer, audioItem.messageId);
        } catch (error) {
            console.error('❌ 播放队列音频失败:', error);
        }
        
        // 播放完成后，检查停止标志
        this.isPlaying = false;
        window.controlledLog?.log('🎵 音频播放完成，检查队列状态:', {
            shouldStop: this.shouldStop,
            queueLength: this.audioQueue.length
        });
        
        if (!this.shouldStop && this.audioQueue.length > 0) {
            window.controlledLog?.log('🎵 继续播放队列中的下一个音频');
            this.processPlayQueue();
        } else {
            window.controlledLog?.log('🎵 播放队列处理完成');
        }
    }
    
    async playPCM16Audio(audioBuffer, messageId = null) {
        try {
            window.controlledLog?.log('🎧 播放PCM16音频，数据长度:', audioBuffer.byteLength);
            
            // 检查ArrayBuffer是否有效
            if (!audioBuffer || audioBuffer.byteLength === 0) {
                console.error('❌ 无效的音频缓冲区');
                return;
            }
            
            // 直接使用原始ArrayBuffer，避免不必要的拷贝
            const pcm16Data = new Int16Array(audioBuffer);
            const float32Data = new Float32Array(pcm16Data.length);
            
            // 高效的PCM16到Float32转换
            for (let i = 0; i < pcm16Data.length; i++) {
                float32Data[i] = pcm16Data[i] / 32768.0;
            }
            
            // 创建音频缓冲区，使用正确的采样率
            const audioBufferNode = this.audioContext.createBuffer(1, float32Data.length, 24000);
            audioBufferNode.copyToChannel(float32Data, 0);
            
            window.controlledLog?.log('🎵 音频缓冲区创建完成，时长:', audioBufferNode.duration.toFixed(2), '秒');
            
            // 顺序播放：等待当前音频播放完成
            await this.playAudioBuffer(audioBufferNode, messageId);
            
        } catch (error) {
            console.error('❌ PCM16播放失败:', error);
        }
    }
    
    async playAudioBuffer(audioBuffer, messageId = null) {
        return new Promise((resolve, reject) => {
            try {
                // 检查停止标志
                if (this.shouldStop) {
                    window.controlledLog?.log('🛑 播放前检测到停止标志，跳过播放');
                    resolve();
                    return;
                }
                
                const source = this.audioContext.createBufferSource();
                const gainNode = this.audioContext.createGain();
                
                source.buffer = audioBuffer;
                gainNode.gain.value = this.synthesisSettings.volume;
                
                // 连接音频节点
                source.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
                
                // 设置播放结束回调
                source.onended = () => {
                    // 清理定时器
                    clearInterval(stopCheckInterval);
                    
                    // 检查是否被停止
                    if (this.shouldStop) {
                        window.controlledLog?.log('🛑 播放结束回调检测到停止标志');
                        resolve();
                        return;
                    }
                    
                    this.isPlaying = false;
                    window.controlledLog?.log('TTS片段播放完成');
                    
                    // 不在这里隐藏播放状态指示器，让maybeFinalize统一处理
                    // if (this.enhancedPlaybackStatus) {
                    //     this.enhancedPlaybackStatus.hide();
                    // }
                    // 记录声源计数并尝试最终收尾
                    if (messageId && this.streamStates.has(messageId)) {
                        const st = this.streamStates.get(messageId);
                        st.playingSources = Math.max(0, (st.playingSources || 0) - 1);
                        this.maybeFinalize(messageId);
                    }
                    resolve();
                };
                
                // 开始播放
                source.start(0);
                // 注意：isPlaying 标志由 processPlayQueue 管理，这里不重复设置
                this.currentAudio = source;
                
                // 设置定期检查停止标志 - 更频繁的检查
                const stopCheckInterval = setInterval(() => {
                    if (this.shouldStop) {
                        window.controlledLog?.log('🛑 播放过程中检测到停止标志，立即停止');
                        try {
                            source.stop(0);
                            source.disconnect();
                        } catch (error) {
                            window.controlledLog?.log('音频源已停止');
                        }
                        clearInterval(stopCheckInterval);
                        resolve();
                    }
                }, 20); // 每20ms检查一次，提高响应速度
                // 记录声源计数
                if (messageId && this.streamStates.has(messageId)) {
                    const st = this.streamStates.get(messageId);
                    st.playingSources = (st.playingSources || 0) + 1;
                }
                
                // 只在第一个片段播放时显示状态，避免闪烁
                if (!this.isTtsPlaying) {
                    this.isTtsPlaying = true;
                    
                    // 通知统一按钮状态管理器TTS播放开始 (通过dcc.Store) - 只在/core/chat页面
                    const currentPath = window.location.pathname;
                    const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
                    
                    if (isChatPage && window.dash_clientside && window.dash_clientside.set_props) {
                        try {
                            window.dash_clientside.set_props('button-event-trigger', {
                                data: {type: 'tts_start', timestamp: Date.now()}
                            });
                            window.controlledLog?.log('TTS播放开始，触发状态更新');
                        } catch (setPropsError) {
                            console.error('set_props调用失败:', setPropsError);
                        }
                    }
                    
                    // 🔧 关键修复：语音通话时不显示播放指示器，其他场景正常显示
                    const isVoiceCall = messageId && messageId.includes('voice_call');
                    
                    if (isVoiceCall) {
                        // 语音通话：不显示播放指示器
                        window.controlledLog?.log('🎧 语音通话：不显示播放指示器');
                    } else {
                        // 非语音通话场景：正常显示播放指示器
                        if (this.enhancedPlaybackStatus) {
                            this.enhancedPlaybackStatus.showStatus('speaking', '正在播放语音...');
                            window.controlledLog?.log('🎧 非语音通话场景：显示播放指示器');
                        } else if (window.enhancedPlaybackStatus) {
                            window.enhancedPlaybackStatus.showStatus('speaking', '正在播放语音...');
                            window.controlledLog?.log('🎧 非语音通话场景：使用全局实例显示播放指示器');
                        } else {
                            console.warn('🎧 enhancedPlaybackStatus 未找到，无法显示播放指示器');
                        }
                    }
                }
                
                window.controlledLog?.log('开始播放音频');
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    handleSynthesisComplete(data) {
        window.controlledLog?.log('语音合成完成');
        // 注意：不要立即隐藏播放状态指示器
        // 因为TTS播放可能还在进行中，应该等待播放完成后再隐藏
        
        // 标记对应message的合成完成
        const messageId = data.message_id || 'unknown';
        
        // 如果streamStates中没有对应的状态，创建一个（录音聊天TTS的情况）
        if (!this.streamStates.has(messageId)) {
            this.streamStates.set(messageId, {
                chunks: [],
                nextSeq: 0,
                codec: 'audio/mpeg',
                synthComplete: false,
                playingSources: 0,
                lastChunkTs: Date.now()
            });
            window.controlledLog?.log('🎧 录音聊天TTS流状态已创建:', messageId);
        }
        
        if (this.streamStates.has(messageId)) {
            const state = this.streamStates.get(messageId);
            state.synthComplete = true;
            state.synthTs = Date.now();
            // 更新lastChunkTs，确保静默窗口条件满足
            state.lastChunkTs = Date.now();
            window.controlledLog?.log('🎧 录音聊天TTS合成完成，更新lastChunkTs:', messageId);
            
            // 🔧 关键修复：不要立即调用maybeFinalize，等待所有音频播放完成
            // 让音频播放完成事件来触发maybeFinalize
            window.controlledLog?.log('🎧 合成完成，但不立即finalize，等待所有音频播放完成');
        }
        
        // 对于录音聊天，标记为完成，让maybeFinalize处理状态重置
        if (!messageId.includes('voice_call')) {
            window.controlledLog?.log('录音聊天TTS完成，标记为完成状态');
            // 不在这里直接调用returnToIdle，让maybeFinalize统一处理
        }
        
        window.controlledLog?.log('所有TTS数据已发送，等待最后一段播放结束再回idle');
    }
    
    /**
     * 尝试最终收尾：检查是否满足回idle条件
     */
    maybeFinalize(messageId) {
        const state = this.streamStates.get(messageId);
        if (!state) return;
        
        const now = Date.now();
        const silenceWindow = 400; // 400ms静默窗口
        const timeSinceLastChunk = now - (state.lastChunkTs || 0);
        
        // 三个条件同时满足才回idle
        const synthComplete = state.synthComplete === true;
        const noPlayingSources = (state.playingSources || 0) === 0;
        const noPendingChunks = (state.chunks || []).length === 0;
        const silenceElapsed = timeSinceLastChunk > silenceWindow;
        
        window.controlledLog?.log(`maybeFinalize(${messageId}): synthComplete=${synthComplete}, playingSources=${state.playingSources}, chunks=${state.chunks.length}, silence=${timeSinceLastChunk}ms`);
        
        // 🔍 详细打印maybeFinalize的决策过程
        window.controlledLog?.log('🔍 [maybeFinalize调试] 详细状态检查:', {
            messageId: messageId,
            synthComplete: synthComplete,
            noPlayingSources: noPlayingSources,
            noPendingChunks: noPendingChunks,
            silenceElapsed: silenceElapsed,
            audioQueueLength: this.audioQueue?.length,
            playQueueLength: this.playQueue?.length,
            isPlaying: this.isPlaying,
            shouldStop: this.shouldStop
        });
        
        // 🔧 关键修复：检查是否还有音频在播放队列中
        const hasQueuedAudio = this.audioQueue && this.audioQueue.length > 0;
        const hasSimpleQueuedAudio = this.playQueue && this.playQueue.length > 0;
        
        if (synthComplete && noPlayingSources && noPendingChunks && silenceElapsed && !hasQueuedAudio && !hasSimpleQueuedAudio) {
            // 满足条件，回idle
            window.controlledLog?.log(`消息${messageId}播放完成，回idle状态`);
            window.controlledLog?.log('🔍 [maybeFinalize调试] 即将回idle，最终检查:', {
                audioQueueLength: this.audioQueue?.length,
                playQueueLength: this.playQueue?.length,
                isPlaying: this.isPlaying,
                hasQueuedAudio: hasQueuedAudio,
                hasSimpleQueuedAudio: hasSimpleQueuedAudio
            });
            // 立即清理该消息状态，避免内存泄漏
            this.streamStates.delete(messageId);
            // 延迟一点时间确保所有音频都播放完成
            setTimeout(() => {
                this.returnToIdle();
            }, 100);
        } else if (synthComplete && noPlayingSources && noPendingChunks && (hasQueuedAudio || hasSimpleQueuedAudio)) {
            // 🔧 关键修复：合成完成但队列中还有音频，等待播放完成
            window.controlledLog?.log(`消息${messageId}合成完成但队列中还有音频，等待播放完成: audioQueue=${this.audioQueue?.length}, playQueue=${this.playQueue?.length}`);
            // 延迟重试，等待队列中的音频播放完成
            setTimeout(() => this.maybeFinalize(messageId), 200);
        } else if (synthComplete && noPlayingSources && noPendingChunks) {
            // 合成完成且无播放源且无待播放分片，但静默窗口未到，延迟重试
            const remaining = silenceWindow - timeSinceLastChunk;
            if (remaining > 0) {
                window.controlledLog?.log(`消息${messageId}等待静默窗口，${remaining}ms后重试`);
                setTimeout(() => this.maybeFinalize(messageId), Math.min(remaining + 50, 200));
            }
        }
    }
    
    /**
     * 回idle状态 - 使用公共工具优化
     */
    returnToIdle() {
        // 防止重复调用
        if (this.isReturningToIdle) {
            window.controlledLog?.log('正在回idle状态，跳过重复调用');
            return;
        }
        
        this.isReturningToIdle = true;
        
        // 重置TTS播放标志，允许下次播放时重新显示状态
        this.isTtsPlaying = false;
        
        try {
            window.controlledLog?.log('🎵 开始回idle状态');
            
            // 使用EnhancedPlaybackStatus隐藏播放状态指示器
            if (this.enhancedPlaybackStatus) {
                this.enhancedPlaybackStatus.hide();
            }
            
            // 使用公共工具触发事件和更新状态
            VoiceUtils.triggerEvent('tts_complete', { timestamp: Date.now() });
            VoiceUtils.updateState('idle', null, {});
            
            // 更新语音状态管理器
            if (window.voiceStateManager) {
                window.voiceStateManager.finishPlaying();
            }
            
            // 🔧 录音聊天TTS完成后，确保释放麦克风
            window.controlledLog?.log('🎤 检查录音器实例:', window.voiceRecorder, window.voiceRecorderEnhanced);
            if (window.voiceRecorder) {
                window.controlledLog?.log('🎤 录音聊天TTS完成，释放麦克风资源');
                window.controlledLog?.log('🎤 调用录音器cleanup方法...');
                try {
                    window.voiceRecorder.cleanup();
                    window.controlledLog?.log('🎤 录音器cleanup方法调用完成');
                } catch (error) {
                    console.error('🎤 录音器cleanup方法调用失败:', error);
                }
            } else if (window.voiceRecorderEnhanced) {
                window.controlledLog?.log('🎤 使用备用录音器实例');
                try {
                    window.voiceRecorderEnhanced.cleanup();
                    window.controlledLog?.log('🎤 备用录音器cleanup方法调用完成');
                } catch (error) {
                    console.error('🎤 备用录音器cleanup方法调用失败:', error);
                }
            } else {
                window.controlledLog?.log('🎤 录音器实例不存在，检查全局状态');
                // 检查是否有其他方式释放麦克风
                if (window.voiceStateManager) {
                    window.controlledLog?.log('🎤 通过状态管理器释放麦克风');
                    window.voiceStateManager.cleanup();
                }
            }
            
            window.controlledLog?.log('🎵 已回idle状态');
            
            // 触发会话状态更新，确保"当前会话"状态正确
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('ai-chat-x-sse-completed-receiver', { 
                    'data-completion-event': { 
                        type: 'tts_complete', 
                        timestamp: Date.now(),
                        status: 'completed'
                    } 
                });
            }
            window.controlledLog?.log('已回idle状态，会话状态已更新');
        } catch (e) {
            VoiceUtils.handleError(e, '回idle状态');
        } finally {
            // 延迟重置标志，防止重复调用
            setTimeout(() => {
                this.isReturningToIdle = false;
            }, 1000);
        }
    }
    
    handleError(data) {
        VoiceUtils.handleError(new Error(data.message), '语音合成');
        // 使用EnhancedPlaybackStatus隐藏播放状态指示器
        if (this.enhancedPlaybackStatus) {
            this.enhancedPlaybackStatus.hide();
        }
        
        // 使用公共工具重置状态
        VoiceUtils.updateState('idle', null, {});
    }
    
    /**
     * 停止播放
     */
    stopPlayback() {
        window.controlledLog?.log('停止播放');
        
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
        
        // 使用EnhancedPlaybackStatus隐藏播放状态
        if (this.enhancedPlaybackStatus) {
            this.enhancedPlaybackStatus.hide();
        }
        
        // 重置播放状态
        this.isPlaying = false;
    }
    
    // 注意：showPlaybackStatus() 和 hidePlaybackStatus() 方法已被删除
    // 现在使用 enhanced_playback_status.js 作为播放状态指示器
    
    stopPlayback() {
        if (this.currentAudio) {
            try {
                this.currentAudio.stop();
                this.currentAudio = null;
                this.isPlaying = false;
                
                // 通知统一按钮状态管理器播放停止 (通过dcc.Store) - 只在/core/chat页面
                const currentPath = window.location.pathname;
                const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
                
                if (isChatPage && window.dash_clientside && window.dash_clientside.set_props) {
                    try {
                        window.dash_clientside.set_props('button-event-trigger', {
                            data: {type: 'tts_stop', timestamp: Date.now()}
                        });
                        window.controlledLog?.log('TTS播放停止，触发状态更新');
                    } catch (setPropsError) {
                        console.error('set_props调用失败:', setPropsError);
                    }
                }
                
                window.controlledLog?.log('停止语音播放');
            } catch (error) {
                console.error('停止播放失败:', error);
            }
        }
        // 使用EnhancedPlaybackStatus隐藏播放状态
        if (this.enhancedPlaybackStatus) {
            this.enhancedPlaybackStatus.hide();
        }
    }
    
    setVoiceSettings(settings) {
        this.synthesisSettings = { ...this.synthesisSettings, ...settings };
        window.controlledLog?.log('语音设置已更新:', this.synthesisSettings);
    }
    
    // 公共方法：手动触发语音播放
    playText(text) {
        this.synthesizeAndPlay(text);
    }
}

// 初始化语音播放器（仅在聊天页面）
document.addEventListener('DOMContentLoaded', () => {
    // 检查是否在聊天页面
    if (window.chatPageConfig && window.chatPageConfig.isChatPage) {
        window.voicePlayer = new VoicePlayerEnhanced();
        window.voicePlayerEnhanced = window.voicePlayer; // 保持向后兼容
    }
});

// 🚀 专门用于语音通话的停止方法 - 只停止语音通话相关，不影响其他场景
VoicePlayerEnhanced.prototype.forceStopAllAudio = function() {
    window.controlledLog?.log('🛑 语音通话强制停止所有音频');
    
    // 🔍 详细打印停止前的状态
    window.controlledLog?.log('🔍 [forceStopAllAudio调试] 停止前状态:', {
        isPlaying: this.isPlaying,
        audioQueueLength: this.audioQueue?.length,
        playQueueLength: this.playQueue?.length,
        streamStatesSize: this.streamStates?.size,
        playedMessagesSize: this.playedMessages?.size,
        shouldStop: this.shouldStop,
        currentAudio: !!this.currentAudio
    });
    window.controlledLog?.log('🔍 [forceStopAllAudio调试] 流状态详情:', Array.from(this.streamStates.entries()).map(([id, state]) => ({
        messageId: id,
        synthComplete: state.synthComplete,
        playingSources: state.playingSources,
        chunks: state.chunks?.length
    })));
    
    // 设置停止标志
    this.shouldStop = true;
    
    // 🚀 立即停止当前音频
    if (this.currentAudio) {
        try {
            this.currentAudio.stop(0);
            this.currentAudio.disconnect();
            window.controlledLog?.log('🛑 当前音频源已立即停止');
        } catch (error) {
            window.controlledLog?.log('当前音频已停止');
        }
        this.currentAudio = null;
    }
    
    // 清空语音通话相关队列
    this.playQueue = [];
    this.audioQueue = [];
    this.isPlaying = false;
    
    // 🔧 关键修复：只清理语音通话相关的流状态，保留录音聊天TTS的状态
    // 只清理包含 'voice_call' 的流状态
    for (const [messageId, state] of this.streamStates.entries()) {
        if (messageId.includes('voice_call')) {
            this.streamStates.delete(messageId);
            window.controlledLog?.log('🛑 清理语音通话流状态:', messageId);
        }
    }
    
    // 🔧 关键修复：只清理语音通话相关的播放消息，保留录音聊天TTS的消息
    for (const messageId of this.playedMessages) {
        if (messageId.includes('voice_call')) {
            this.playedMessages.delete(messageId);
            window.controlledLog?.log('🛑 清理语音通话播放消息:', messageId);
        }
    }
    
    // 清理定时器
    if (this.idleDebounceTimer) {
        clearTimeout(this.idleDebounceTimer);
        this.idleDebounceTimer = null;
    }
    
    // 清理所有定时器
    if (this.stopCheckInterval) {
        clearInterval(this.stopCheckInterval);
        this.stopCheckInterval = null;
    }
    
    // 🚀 立即重置停止标志，允许后续播放（录音聊天等）
    this.shouldStop = false;
    window.controlledLog?.log('🛑 停止标志已重置，允许后续播放');
    
    // 🔧 关键修复：重置TTS播放标志，确保后续录音聊天和文本聊天能正常显示播放指示器
    this.isTtsPlaying = false;
    window.controlledLog?.log('🔧 TTS播放标志已重置，允许后续播放指示器正常显示');
    
    window.controlledLog?.log('🛑 语音通话强制停止完成，其他场景保持可用');
};

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoicePlayerEnhanced;
}
