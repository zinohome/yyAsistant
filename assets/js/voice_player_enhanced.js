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
        // 新增：合成完成与播放队列控制
        this.synthesisDone = false;      // 服务端已完成合成标记
        this.pendingSegments = 0;        // 待播放片段计数
        this.idleDebounceTimer = null;   // 回idle防抖
        
        // 流式播放：无需缓冲，收到音频立即播放
        this.playedMessages = new Set(); // 记录已播放的消息ID，避免重复播放
        this.streamStates = new Map(); // message_id -> { chunks: [{seq, base64}], nextSeq, codec, session_id }
        this.shouldStop = false; // 停止标志
        
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
                            console.log('播放器延迟连接成功，消息处理器已在初始化时注册');
                        } else {
                            console.warn('延迟连接WebSocket管理器失败');
                        }
                    }, 1000);
                    return;
                }
            } else {
                // 从全局配置获取WebSocket URL
                const wsUrl = window.voiceConfig?.WS_URL || 'ws://192.168.32.156:9800/ws/chat';
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
                    // 统一错误消息格式处理
                    if (data && data.error && data.error.message) {
                        data.message = data.error.message;
                    }
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
                    playing: false,
                    playingSources: 0,
                    synthComplete: false,
                    lastChunkTs: 0
                });
            }
            const state = this.streamStates.get(messageId);

            // 记录分片并更新时间戳
            state.chunks.push({ seq: (seq !== null ? seq : state.chunks.length), base64 });
            state.lastChunkTs = Date.now();
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

        // 持续处理音频分片，直到合成完成且无更多分片
        while (state.chunks.length > 0 || !state.synthComplete) {
            if (state.chunks.length > 0) {
                // 取出最小seq的分片
                const chunk = state.chunks.shift();
                try {
                    await this.playAudioFromBase64(chunk.base64, messageId);
                } catch (e) {
                    console.warn('播放分片失败，跳过该分片:', e);
                }
            } else {
                // 没有分片但合成未完成，等待新分片
                await new Promise(resolve => setTimeout(resolve, 50));
            }
        }

        state.playing = false;
        // 播放循环结束后尝试收尾
        this.maybeFinalize(messageId);
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
    
    async playAudioFromBase64(base64Audio, messageId = null) {
        try {
            console.log('🎵 收到音频分片，base64长度:', base64Audio.length);
            
            // 初始化音频上下文
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 24000, // 明确指定采样率
                    latencyHint: 'interactive' // 低延迟模式
                });
                console.log('🎧 音频上下文已创建，采样率:', this.audioContext.sampleRate);
            }
            
            // 恢复音频上下文（如果被暂停）
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
                console.log('▶️ 音频上下文已恢复');
            }
            
            // 判断音频来源：语音通话 vs 录音聊天TTS
            const isVoiceCall = messageId && messageId.includes('voice_call');
            
            if (isVoiceCall) {
                // 语音通话：直接流式播放，参考Chainlit实现
                console.log('🎧 语音通话音频，直接流式播放');
                await this.playVoiceCallAudio(base64Audio, messageId);
            } else {
                // 录音聊天TTS：使用标准音频格式
                console.log('🎧 录音聊天TTS，使用标准音频格式');
                await this.playStandardAudio(base64Audio, messageId);
            }
            
        } catch (error) {
            console.error('❌ 处理音频分片失败:', error);
        }
    }
    
    // 语音通话音频播放（参考Chainlit实现）
    async playVoiceCallAudio(base64Audio, messageId = null) {
        try {
            console.log('🎧 播放语音通话音频，base64长度:', base64Audio.length);
            
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
            
            console.log('🎵 语音通话音频准备完成，时长:', audioBufferNode.duration.toFixed(2), '秒');
            
            // 使用队列管理，避免重叠播放
            this.addToPlayQueue(audioBufferNode, messageId);
            
        } catch (error) {
            console.error('❌ 语音通话音频播放失败:', error);
        }
    }
    
    // 标准音频播放（用于录音聊天TTS）
    async playStandardAudio(base64Audio, messageId = null) {
        try {
            console.log('🎧 播放标准音频格式，base64长度:', base64Audio.length);
            
            // 使用标准的音频解码
            const audioData = atob(base64Audio);
            const audioBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(audioBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            // 解码为AudioBuffer（标准格式）
            const decodedBuffer = await this.audioContext.decodeAudioData(audioBuffer);
            
            console.log('🎵 标准音频解码完成，时长:', decodedBuffer.duration.toFixed(2), '秒');
            
            // 直接播放，不使用队列
            await this.playAudioBuffer(decodedBuffer, messageId);
            
        } catch (error) {
            console.error('❌ 标准音频播放失败:', error);
        }
    }
    
    // 播放队列管理：确保音频顺序播放，避免重叠
    addToPlayQueue(audioBuffer, messageId = null) {
        // 🚀 检查是否应该停止，如果是则忽略新的音频
        if (this.shouldStop) {
            console.log('🛑 正在停止中，忽略新的音频数据');
            return;
        }
        
        // 添加到播放队列
        this.audioQueue.push({
            buffer: audioBuffer,
            messageId: messageId,
            timestamp: Date.now()
        });
        
        console.log('📋 音频分片已添加到播放队列，队列长度:', this.audioQueue.length);
        
        // 如果当前没有播放，开始播放队列
        if (!this.isPlaying) {
            this.processPlayQueue();
        }
    }
    
    // 停止当前播放并清空队列（用于打断机制）
    stopCurrentPlayback() {
        console.log('🛑 立即停止当前播放并清空队列');
        
        // 🚀 设置停止标志 - 不要重置，保持停止状态
        this.shouldStop = true;
        
        // 🚀 立即停止当前播放的音频源（最高优先级）
        if (this.currentAudio) {
            try {
                this.currentAudio.stop(0); // 立即停止，不等待
                this.currentAudio.disconnect();
                console.log('🛑 当前音频源已立即停止');
            } catch (error) {
                console.log('当前音频已停止');
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
                console.log('🛑 音频上下文已强制关闭');
            } catch (error) {
                console.log('音频上下文清理完成');
            }
        }
        
        // 清空播放队列
        this.audioQueue = [];
        this.isPlaying = false;
        
        // 清空所有流状态
        this.streamStates.clear();
        
        // 不要重置shouldStop标志，保持停止状态直到下次开始播放
        console.log('✅ 播放已立即停止，队列已清空，状态已重置');
    }
    
    async processPlayQueue() {
        // 检查停止标志
        if (this.shouldStop) {
            console.log('🛑 检测到停止标志，停止队列处理');
            this.isPlaying = false;
            return;
        }
        
        if (this.audioQueue.length === 0) {
            console.log('📋 播放队列为空');
            this.isPlaying = false;
            return;
        }
        
        if (this.isPlaying) {
            console.log('🎵 正在播放中，等待当前音频完成');
            return;
        }
        
        this.isPlaying = true;
        const audioItem = this.audioQueue.shift();
        
        console.log('🎵 开始播放队列中的音频，剩余队列长度:', this.audioQueue.length);
        
        try {
            await this.playAudioBuffer(audioItem.buffer, audioItem.messageId);
        } catch (error) {
            console.error('❌ 播放队列音频失败:', error);
        }
        
        // 播放完成后，检查停止标志
        this.isPlaying = false;
        if (!this.shouldStop && this.audioQueue.length > 0) {
            this.processPlayQueue();
        }
    }
    
    async playPCM16Audio(audioBuffer, messageId = null) {
        try {
            console.log('🎧 播放PCM16音频，数据长度:', audioBuffer.byteLength);
            
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
            
            console.log('🎵 音频缓冲区创建完成，时长:', audioBufferNode.duration.toFixed(2), '秒');
            
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
                    console.log('🛑 播放前检测到停止标志，跳过播放');
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
                        console.log('🛑 播放结束回调检测到停止标志');
                        resolve();
                        return;
                    }
                    
                    this.isPlaying = false;
                    console.log('TTS片段播放完成');
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
                this.isPlaying = true;
                this.currentAudio = source;
                
                // 设置定期检查停止标志 - 更频繁的检查
                const stopCheckInterval = setInterval(() => {
                    if (this.shouldStop) {
                        console.log('🛑 播放过程中检测到停止标志，立即停止');
                        try {
                            source.stop(0);
                            source.disconnect();
                        } catch (error) {
                            console.log('音频源已停止');
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
                
                // 通知统一按钮状态管理器TTS播放开始 (通过dcc.Store) - 只在/core/chat页面
                const currentPath = window.location.pathname;
                const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
                
                if (isChatPage && window.dash_clientside && window.dash_clientside.set_props) {
                    try {
                        window.dash_clientside.set_props('button-event-trigger', {
                            data: {type: 'tts_start', timestamp: Date.now()}
                        });
                        console.log('TTS播放开始，触发状态更新');
                    } catch (setPropsError) {
                        console.error('set_props调用失败:', setPropsError);
                    }
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
        
        // 标记对应message的合成完成
        const messageId = data.message_id || 'unknown';
        if (this.streamStates.has(messageId)) {
            const state = this.streamStates.get(messageId);
            state.synthComplete = true;
            state.synthTs = Date.now();
            this.maybeFinalize(messageId);
        }
        
        console.log('所有TTS数据已发送，等待最后一段播放结束再回idle');
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
        
        console.log(`maybeFinalize(${messageId}): synthComplete=${synthComplete}, playingSources=${state.playingSources}, chunks=${state.chunks.length}, silence=${timeSinceLastChunk}ms`);
        
        if (synthComplete && noPlayingSources && noPendingChunks && silenceElapsed) {
            // 满足条件，回idle
            console.log(`消息${messageId}播放完成，回idle状态`);
            this.returnToIdle();
            // 清理该消息状态
            this.streamStates.delete(messageId);
        } else if (synthComplete && noPlayingSources && noPendingChunks) {
            // 合成完成且无播放源且无待播放分片，但静默窗口未到，延迟重试
            const remaining = silenceWindow - timeSinceLastChunk;
            if (remaining > 0) {
                console.log(`消息${messageId}等待静默窗口，${remaining}ms后重试`);
                setTimeout(() => this.maybeFinalize(messageId), Math.min(remaining + 50, 200));
            }
        }
    }
    
    /**
     * 回idle状态
     */
    returnToIdle() {
        try {
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('button-event-trigger', { 
                    data: { type: 'tts_complete', timestamp: Date.now() } 
                });
                window.dash_clientside.set_props('unified-button-state', { 
                    data: { state: 'idle', scenario: null, timestamp: Date.now(), metadata: {} } 
                });
                window.dash_clientside.set_props('ai-chat-x-sse-completed-receiver', { 
                    'data-completion-event': null 
                });
                console.log('已回idle状态');
            }
        } catch (e) {
            console.error('回idle失败:', e);
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
                
                // 通知统一按钮状态管理器播放停止 (通过dcc.Store) - 只在/core/chat页面
                const currentPath = window.location.pathname;
                const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
                
                if (isChatPage && window.dash_clientside && window.dash_clientside.set_props) {
                    try {
                        window.dash_clientside.set_props('button-event-trigger', {
                            data: {type: 'tts_stop', timestamp: Date.now()}
                        });
                        console.log('TTS播放停止，触发状态更新');
                    } catch (setPropsError) {
                        console.error('set_props调用失败:', setPropsError);
                    }
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

// 🚀 超级激进的停止方法 - 直接销毁音频上下文
VoicePlayerEnhanced.prototype.forceStopAllAudio = function() {
    console.log('🛑 超级强制停止所有音频');
    
    // 设置停止标志
    this.shouldStop = true;
    
    // 立即停止当前音频
    if (this.currentAudio) {
        try {
            this.currentAudio.stop(0);
            this.currentAudio.disconnect();
        } catch (error) {
            console.log('当前音频已停止');
        }
        this.currentAudio = null;
    }
    
    // 清空所有队列
    this.playQueue = [];
    this.audioQueue = [];
    this.isPlaying = false;
    
    // 🚀 强制销毁音频上下文
    if (this.audioContext) {
        try {
            this.audioContext.close();
            this.audioContext = null;
            console.log('🛑 音频上下文已强制销毁');
        } catch (error) {
            console.log('音频上下文销毁完成');
        }
    }
    
    // 清理所有定时器
    if (this.stopCheckInterval) {
        clearInterval(this.stopCheckInterval);
        this.stopCheckInterval = null;
    }
    
    console.log('🛑 超级强制停止完成');
};

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoicePlayerEnhanced;
}
