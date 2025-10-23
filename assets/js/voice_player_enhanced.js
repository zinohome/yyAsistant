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
        
        // 使用状态协调器监听状态变化
        this.initStateListener();
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
        console.log(`播放器状态变化: ${oldState} → ${newState} (${scenario})`);
        
        // 如果状态变为中断，停止播放
        if (newState === 'interrupted' && this.isPlaying) {
            this.stopPlayback();
        }
        
        // 如果状态变为空闲，清理资源
        if (newState === 'idle') {
            this.cleanup();
        }
    }
    
    /**
     * 清理资源
     */
    cleanup() {
        // 清理流状态
        this.streamStates.clear();
        this.playedMessages.clear();
        this.shouldStop = false;
        console.log('播放器资源已清理');
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
            // 使用公共工具初始化WebSocket连接
            const messageHandlers = {
                'audio_stream': (data) => this.handleAudioStream(data),
                'voice_response': (data) => this.handleVoiceResponse(data),
                'synthesis_complete': (data) => this.handleSynthesisComplete(data)
            };
            
            this.websocket = await VoiceUtils.initWebSocket(window.voiceWebSocketManager, messageHandlers);
            console.log('播放器WebSocket连接已建立');
        } catch (error) {
            VoiceUtils.handleError(error, '播放器WebSocket初始化');
        }
    }
    
    /**
     * 处理语音响应消息
     */
    handleVoiceResponse(data) {
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
        // 监听SSE完成事件，触发TTS播放
        document.addEventListener('messageCompleted', (event) => {
            try {
                // 检查是否启用前端TTS回退
                const frontendTtsEnabled = window.voiceConfig?.get('frontendTtsFallback', true);
                if (frontendTtsEnabled && event.detail && event.detail.text) {
                    console.log('🎵 SSE完成，开始TTS播放:', event.detail.text.substring(0, 50) + '...');
                    this.synthesizeAndPlay(event.detail.text);
                } else {
                    console.log('🎵 SSE完成，但前端TTS已禁用或没有文本内容');
                }
            } catch (e) {
                console.warn('messageCompleted TTS 处理失败:', e);
            }
        });
    }
    
    async synthesizeAndPlay(text) {
        try {
            if (!text || !text.trim()) {
                console.log('没有文本需要合成语音');
                return;
            }
            
            // 使用公共工具更新状态
            VoiceUtils.updateState('processing', 'voice_recording', { tts_playing: true });
            
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
            VoiceUtils.handleError(error, '语音合成');
            this.hidePlaybackStatus();
            
            // 使用公共工具重置状态
            VoiceUtils.updateState('idle', null, {});
        }
    }
    
    async requestSpeechSynthesis(text) {
        return new Promise((resolve, reject) => {
            if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                reject(new Error('WebSocket连接不可用'));
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
            
            console.log('🎵 发送TTS请求:', { type: message.type, content: text.substring(0, 50) + '...', enable_voice: true });
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

            // 判断场景类型
            const isRecordingChat = sessionId && sessionId.includes('conv-');
            const isVoiceCall = sessionId && !sessionId.includes('conv-');
            const isTextChat = messageId && messageId.includes('ai-message');
            
            console.log(`🎵 音频流场景判断: 录音聊天=${isRecordingChat}, 语音通话=${isVoiceCall}, 文本聊天=${isTextChat}`);
            
            if (isRecordingChat || isTextChat) {
                // 录音聊天TTS 或 文本聊天TTS：简单按序播放，不使用分片管理
                console.log('🎧 聊天TTS（录音/文本），简单按序播放');
                this.playSimpleTTS(base64, messageId, seq);
            } else if (isVoiceCall) {
                // 语音通话TTS：使用复杂分片管理
                console.log('🎤 语音通话TTS，使用分片管理');
                this.playVoiceCallTTS(base64, messageId, sessionId, codec, seq);
            } else {
                // 未知场景：默认简单播放
                console.log('❓ 未知场景TTS，默认简单播放');
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
        console.log('🎧 简单TTS播放:', messageId);
        
        try {
            // 确保音频上下文可用
            if (!this.audioContext || this.audioContext.state === 'closed') {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                console.log('🎧 重新创建音频上下文');
            }
            
            // 恢复音频上下文（如果被暂停）
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
                console.log('🎧 音频上下文已恢复');
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
            console.log('🎧 简单TTS音频解码完成，时长:', decodedBuffer.duration.toFixed(2), '秒');
            
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
                console.log('🎧 简单音频播放:', messageId);
                
                const source = this.audioContext.createBufferSource();
                const gainNode = this.audioContext.createGain();
                
                source.buffer = audioBuffer;
                gainNode.gain.value = this.synthesisSettings.volume;
                
                // 连接音频节点
                source.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
                
                // 设置播放结束回调
                source.onended = () => {
                    console.log('🎧 简单音频播放完成:', messageId);
                    
                    // 从队列中移除已播放的音频
                    if (this.simpleQueue && this.simpleQueue.length > 0) {
                        const index = this.simpleQueue.findIndex(item => item.messageId === messageId);
                        if (index !== -1) {
                            this.simpleQueue.splice(index, 1);
                            console.log('🎧 已从队列中移除:', messageId, '剩余队列长度:', this.simpleQueue.length);
                        }
                    }
                    
                    // 🚀 重置播放标志，允许处理下一个音频
                    this.simplePlaying = false;
                    
                    resolve();
                };
                
                // 开始播放
                source.start();
                console.log('🎧 简单音频开始播放:', messageId);
                
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
        
        console.log('🎧 添加到简单播放队列:', messageId, 'seq:', seq, '队列长度:', this.simpleQueue.length);
        
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
            console.log('🎧 处理简单播放队列:', nextAudio.messageId, 'seq:', nextAudio.seq);
            
            try {
                await this.playSimpleAudioBuffer(nextAudio.buffer, nextAudio.messageId);
                
                // 播放完成后，继续处理队列中的下一个音频
                if (this.simpleQueue.length > 0) {
                    console.log('🎧 继续处理队列中的下一个音频，剩余队列长度:', this.simpleQueue.length);
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
        console.log('🎧 简单播放队列处理完成');
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
        console.log('🎤 语音通话TTS播放:', messageId);
        
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
        
        console.log(`🎤 语音通话音频分片 seq:${actualSeq}, 总分片:${state.chunks.length}`);

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

        console.log(`🎵 开始播放流状态，当前分片数:${state.chunks.length}, 合成完成:${state.synthComplete}`);

        // 持续处理音频分片，直到合成完成且无更多分片
        while (state.chunks.length > 0 || !state.synthComplete) {
            // 检查是否所有分片都已播放完成
            if (state.synthComplete && state.chunks.length === 0) {
                console.log('🎵 所有分片已播放完成，退出播放循环');
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
                        console.log(`🎵 播放分片 seq:${chunk.seq}, 剩余分片:${state.chunks.length}`);
                        
                        try {
                            await this.playAudioFromBase64(chunk.base64, messageId);
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
        console.log(`🎵 播放流状态完成，messageId:${messageId}`);
        // 播放循环结束后尝试收尾
        this.maybeFinalize(messageId);
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
            console.log('🎵 所有分片已播放完成，合成完成');
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
            
            console.log(`🎵 期望值更新: ${oldNextSeq} → ${state.nextSeq} (播放分片${nextAvailableChunk.seq})`);
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
                    
                    console.log(`🎵 强制跳跃: 期望值${oldNextSeq} → ${state.nextSeq} (播放分片${nextChunk.seq})`);
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
                
                console.log(`🎵 超时跳跃: 期望值${oldNextSeq} → ${state.nextSeq} (播放分片${nextAvailableChunk.seq})`);
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
            
            // 聊天TTS（录音聊天和文本聊天）：完全独立处理，不受任何状态影响
            const isChatTTS = messageId && (messageId.includes('ai-message') || messageId.includes('usr-message'));
            if (isChatTTS) {
                console.log('🎧 聊天TTS播放，完全独立处理');
                this.playStandardAudio(base64Audio, messageId);
                return;
            }
            
            // 🛑 检查是否正在打断，如果是则忽略新的音频
            if (this.shouldStop) {
                console.log('🛑 正在打断中，忽略新的音频数据');
                return;
            }
            
            // 初始化音频上下文
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 24000, // 明确指定采样率
                    latencyHint: 'interactive' // 低延迟模式
                });
                console.log('🎧 音频上下文已创建，采样率:', this.audioContext.sampleRate);
            }
            
            // 🚀 检查音频上下文状态，如果被关闭则重新创建
            if (this.audioContext.state === 'closed') {
                console.log('🔄 音频上下文已关闭，重新创建');
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 24000,
                    latencyHint: 'interactive'
                });
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
                console.log('🎧 录音聊天流状态已初始化:', messageId);
            }
            
            // 检查音频上下文状态
            if (!this.audioContext || this.audioContext.state === 'closed') {
                console.log('🔄 音频上下文已关闭，重新创建');
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
            
            console.log('🎵 标准音频解码完成，时长:', decodedBuffer.duration.toFixed(2), '秒');
            
            // 🚀 录音聊天TTS使用队列机制，确保按序播放
            this.addToPlayQueue(decodedBuffer, messageId);
            
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
        console.log('🎵 音频播放完成，检查队列状态:', {
            shouldStop: this.shouldStop,
            queueLength: this.audioQueue.length
        });
        
        if (!this.shouldStop && this.audioQueue.length > 0) {
            console.log('🎵 继续播放队列中的下一个音频');
            this.processPlayQueue();
        } else {
            console.log('🎵 播放队列处理完成');
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
                // 注意：isPlaying 标志由 processPlayQueue 管理，这里不重复设置
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
            console.log('🎧 录音聊天TTS流状态已创建:', messageId);
        }
        
        if (this.streamStates.has(messageId)) {
            const state = this.streamStates.get(messageId);
            state.synthComplete = true;
            state.synthTs = Date.now();
            // 更新lastChunkTs，确保静默窗口条件满足
            state.lastChunkTs = Date.now();
            console.log('🎧 录音聊天TTS合成完成，更新lastChunkTs:', messageId);
            this.maybeFinalize(messageId);
        }
        
        // 对于录音聊天，标记为完成，让maybeFinalize处理状态重置
        if (!messageId.includes('voice_call')) {
            console.log('录音聊天TTS完成，标记为完成状态');
            // 不在这里直接调用returnToIdle，让maybeFinalize统一处理
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
     * 回idle状态 - 使用公共工具优化
     */
    returnToIdle() {
        // 防止重复调用
        if (this.isReturningToIdle) {
            console.log('正在回idle状态，跳过重复调用');
            return;
        }
        
        this.isReturningToIdle = true;
        
        try {
            // 隐藏播放状态指示器
            this.hidePlaybackStatus();
            
            // 使用公共工具触发事件和更新状态
            VoiceUtils.triggerEvent('tts_complete', { timestamp: Date.now() });
            VoiceUtils.updateState('idle', null, {});
            
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
            console.log('已回idle状态，会话状态已更新');
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
        this.hidePlaybackStatus();
        
        // 使用公共工具重置状态
        VoiceUtils.updateState('idle', null, {});
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
                top: 80px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 6px;
                z-index: 10000;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            document.body.appendChild(statusIndicator);
        }
        
        statusIndicator.innerHTML = `
            <div style="width: 12px; height: 12px; border: 2px solid white; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            正在播放语音...
        `;
        
        // 显示动画
        setTimeout(() => {
            statusIndicator.style.opacity = '1';
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
            // 使用淡出动画隐藏
            statusIndicator.style.opacity = '0';
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
    window.voicePlayerEnhanced = window.voicePlayer; // 保持向后兼容
});

// 🚀 超级激进的停止方法 - 停止播放但保持播放器可用
VoicePlayerEnhanced.prototype.forceStopAllAudio = function() {
    console.log('🛑 超级强制停止所有音频');
    
    // 设置停止标志
    this.shouldStop = true;
    
    // 🚀 立即停止当前音频
    if (this.currentAudio) {
        try {
            this.currentAudio.stop(0);
            this.currentAudio.disconnect();
            console.log('🛑 当前音频源已立即停止');
        } catch (error) {
            console.log('当前音频已停止');
        }
        this.currentAudio = null;
    }
    
    // 🚀 强制停止所有正在播放的音频源
    if (this.audioContext && this.audioContext.state !== 'closed') {
        try {
            // 断开所有音频节点连接
            const destination = this.audioContext.destination;
            if (destination) {
                destination.disconnect();
            }
            console.log('🛑 所有音频连接已断开');
        } catch (error) {
            console.log('音频连接断开完成');
        }
    }
    
    // 清空所有队列和状态
    this.playQueue = [];
    this.audioQueue = [];
    this.isPlaying = false;
    
    // 🚀 清理简单播放队列（录音聊天TTS）
    this.simpleQueue = [];
    this.simplePlaying = false;
    
    // 🚀 完全清理所有流状态和播放状态
    this.streamStates.clear();
    this.playedMessages.clear();
    
    // 🚀 重置所有播放相关标志
    this.synthesisDone = false;
    this.pendingSegments = 0;
    this.shouldStop = false;
    
    // 🚀 清理定时器
    if (this.idleDebounceTimer) {
        clearTimeout(this.idleDebounceTimer);
        this.idleDebounceTimer = null;
    }
    
    // 🚀 完全重置音频上下文状态
    if (this.audioContext) {
        try {
            this.audioContext.close();
            console.log('🛑 音频上下文已关闭');
        } catch (error) {
            console.log('音频上下文关闭完成');
        }
        // 强制设置为null，确保重新创建
        this.audioContext = null;
    }
    
    // 🚀 强制停止所有正在播放的音频源
    if (this.audioContext && this.audioContext.state !== 'closed') {
        try {
            // 断开所有音频节点连接
            const destination = this.audioContext.destination;
            if (destination) {
                destination.disconnect();
            }
            console.log('🛑 所有音频连接已断开');
        } catch (error) {
            console.log('音频连接断开完成');
        }
    }
    
    // 🚀 强制停止所有正在播放的音频源
    if (this.audioContext && this.audioContext.state !== 'closed') {
        try {
            // 断开所有音频节点连接
            const destination = this.audioContext.destination;
            if (destination) {
                destination.disconnect();
            }
            console.log('🛑 所有音频连接已断开');
        } catch (error) {
            console.log('音频连接断开完成');
        }
    }
    
    // 重置停止标志，允许后续播放
    this.shouldStop = false;
    
    // 清理所有定时器
    if (this.stopCheckInterval) {
        clearInterval(this.stopCheckInterval);
        this.stopCheckInterval = null;
    }
    
    // 🚀 立即重置停止标志，允许后续播放（录音聊天等）
    // 不需要延迟，因为我们已经清理了所有音频状态
    this.shouldStop = false;
    console.log('🛑 停止标志已重置，允许后续播放');
    
    console.log('🛑 超级强制停止完成，播放器保持可用');
};

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoicePlayerEnhanced;
}
