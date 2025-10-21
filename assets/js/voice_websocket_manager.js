/**
 * 语音WebSocket管理器
 * 专门处理与yychat后端的语音WebSocket通信
 */

/**
 * 语音WebSocket管理器
 * 使用隐藏div和Dash clientside callback机制来更新Store
 */

class VoiceWebSocketManager {
    constructor() {
        this.ws = null;
        this.clientId = null;
        this.sessionId = null;  // 当前会话ID (conversation_id)
        this.isConnected = false;
        this.isConnecting = false;  // 添加连接中标志
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 1000;
        this.heartbeatInterval = null;
        this.messageHandlers = new Map();
        this.connectionHandlers = [];
        this.disconnectionHandlers = [];
        // 预注册心跳回应为no-op，避免未注册报错
        this.messageHandlers.set('heartbeat_response', () => {});
        // 预注册音频消息处理器占位，避免未注册时报错
        this.messageHandlers.set('audio_stream', () => {});
        this.messageHandlers.set('voice_response', () => {});
        this.messageHandlers.set('synthesis_complete', () => {});
        this.messageHandlers.set('interrupt_confirmed', () => {});
        this.messageHandlers.set('stop_playback', () => {});
        
        // 从配置获取WebSocket URL，并附带持久化client_id
        this.wsUrlBase = window.voiceConfig?.WS_URL || 'ws://192.168.32.156:9800/ws/chat';
        this.persistentClientId = this.ensurePersistentClientId();
        this.wsUrl = this.appendClientId(this.wsUrlBase, this.persistentClientId);
        
        // 初始化全局状态
        this.initGlobalState();

        // 移除复杂的队列机制，直接使用简单的更新方式
    }
    
    /**
     * 确保存在持久化client_id（localStorage）
     */
    ensurePersistentClientId() {
        try {
            const key = 'voiceClientId';
            let cid = localStorage.getItem(key);
            if (!cid) {
                cid = self.crypto?.randomUUID ? self.crypto.randomUUID() : (Date.now().toString(36) + Math.random().toString(36).slice(2));
                localStorage.setItem(key, cid);
            }
            // 初始化到全局状态，便于SSE兜底读取
            if (!window.voiceChatState) {
                window.voiceChatState = {};
            }
            window.voiceChatState.clientId = window.voiceChatState.clientId || cid;
            return cid;
        } catch (e) {
            return Date.now().toString(36) + Math.random().toString(36).slice(2);
        }
    }
    
    /**
     * 追加client_id到WS URL
     */
    appendClientId(url, clientId) {
        try {
            const hasQuery = url.includes('?');
            const sep = hasQuery ? '&' : '?';
            return `${url}${sep}client_id=${encodeURIComponent(clientId)}`;
        } catch (_) {
            return url;
        }
    }
    
    /**
     * 初始化全局状态管理
     */
    initGlobalState() {
        // 创建全局状态对象
        window.voiceChatState = {
            clientId: null,
            sessionId: null,
            isConnected: false,
            activeMessageId: null
        };
        
        // 监听会话切换事件
        document.addEventListener('conversationSwitched', (event) => {
            this.updateSessionId(event.detail.conversationId);
        });
    }

    // 移除有问题的updateDashStore方法，完全使用事件机制

    // 移除复杂的队列机制
    
    /**
     * 更新会话ID
     */
    updateSessionId(conversationId) {
        this.sessionId = conversationId;
        window.voiceChatState.sessionId = conversationId;
        console.log('WebSocket管理器更新会话ID:', conversationId);
    }
    
    /**
     * 建立WebSocket连接
     */
    async connect() {
        // 如果正在连接中，直接返回
        if (this.isConnecting) {
            console.log('WebSocket正在连接中，跳过重复连接');
            return Promise.resolve();
        }
        
        this.isConnecting = true;
        return new Promise((resolve, reject) => {
            try {
                console.log('正在连接语音WebSocket:', this.wsUrl);
                
                this.ws = new WebSocket(this.wsUrl);
                
                this.ws.onopen = (event) => {
                    console.log('语音WebSocket连接已建立');
                    this.isConnected = true;
                    this.isConnecting = false;  // 重置连接中标志
                    // 新连接建立时，清空旧的 clientId，等待服务端下发新的 connection_established 进行绑定
                    this.clientId = null;
                    window.voiceChatState.clientId = null;
                    
                    // 使用事件机制更新连接状态
                    try {
                        const event = new CustomEvent('voiceWebSocketConnecting', {
                            detail: { connected: true, client_id: null, timestamp: Date.now() }
                        });
                        document.dispatchEvent(event);
                        console.log('连接时使用事件机制更新状态');
                    } catch (e) {
                        console.warn('连接时事件机制失败:', e);
                    }
                    // 清理本地存储的旧 client_id，强制重新生成
                    try {
                        localStorage.removeItem('voiceClientId');
                    } catch (_) {}
                    // 重新生成持久化 client_id
                    this.persistentClientId = this.ensurePersistentClientId();
                    this.wsUrl = this.appendClientId(this.wsUrlBase, this.persistentClientId);
                    // 尝试从页面当前会话控件读取会话ID，避免 session 校验期望为 null
                    try {
                        const el = document.getElementById('ai-chat-x-current-session-id');
                        const sid = (el && (el.value || el.textContent)) ? (el.value || el.textContent) : null;
                        if (sid) {
                            this.updateSessionId(sid);
                        }
                    } catch (_) {}
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.startHeartbeat();
                    this.notifyConnectionHandlers(true);
                    resolve(true);
                };
                
                this.ws.onmessage = (event) => {
                    this.handleMessage(event.data);
                };
                
                this.ws.onclose = (event) => {
                    console.log('语音WebSocket连接已关闭:', event.code, event.reason);
                    // 连接关闭时也清理 clientId，避免用旧 id 校验新连接的首条消息
                    this.clientId = null;
                    window.voiceChatState.clientId = null;
                    this.isConnected = false;
                    this.isConnecting = false;  // 重置连接中标志
                    this.stopHeartbeat();
                    this.notifyDisconnectionHandlers();
                    
                    // 自动重连
                    if (this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.scheduleReconnect();
                    }
                };
                
                this.ws.onerror = (error) => {
                    console.error('语音WebSocket连接错误:', error);
                    this.isConnecting = false;  // 重置连接中标志
                    this.notifyConnectionHandlers(false);
                    reject(error);
                };
                
            } catch (error) {
                console.error('语音WebSocket连接失败:', error);
                this.isConnecting = false;  // 重置连接中标志
                reject(error);
            }
        });
    }
    
    /**
     * 断开WebSocket连接
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.isConnecting = false;  // 重置连接中标志
        this.stopHeartbeat();
        this.stopAudioStreaming();
    }
    
    /**
     * 启动音频流处理
     */
    startAudioStreaming() {
        console.log('启动音频流处理...');
        
        // 检查是否支持音频流
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.error('浏览器不支持音频流');
            return;
        }
        
        // 获取麦克风权限
        navigator.mediaDevices.getUserMedia({ 
            audio: {
                sampleRate: 24000,  // OpenAI Realtime API使用24kHz
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true
            } 
        })
        .then(stream => {
            console.log('音频流获取成功');
            this.audioStream = stream;
            this.startAudioProcessing();
            // 更新状态指示器
            this.updateStatusIndicator('正在说话', 'blue');
            // 启动音频可视化
            if (window.audioVisualizer) {
                window.audioVisualizer.startVisualization(stream);
            }
        })
        .catch(error => {
            console.error('获取音频流失败:', error);
        });
    }
    
    /**
     * 停止音频流处理
     */
    stopAudioStreaming() {
        console.log('停止音频流处理...');
        
        // 🔧 使用server_vad时，不需要手动提交音频缓冲区
        // 直接停止音频流即可
        
        // 重置语音活动检测状态
        this.isSpeaking = false;
        this.silenceDuration = 0;
        this.audioBuffer = [];
        
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }
        
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        
        // 停止音频可视化
        if (window.audioVisualizer) {
            window.audioVisualizer.stopVisualization();
        }
    }
    
    /**
     * 开始音频处理
     */
    startAudioProcessing() {
        if (!this.audioStream) return;
        
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 24000  // OpenAI Realtime API使用24kHz
            });
            
            const source = this.audioContext.createMediaStreamSource(this.audioStream);
            const processor = this.audioContext.createScriptProcessor(4096, 1, 1);
            
            // 语音活动检测参数 - 从配置文件读取
            this.vadThreshold = window.VoiceConfig?.vad?.threshold || 0.01;
            this.silenceDuration = 0; // 静音持续时间
            this.maxSilenceDuration = window.VoiceConfig?.vad?.maxSilenceDuration || 800;
            this.silenceIncrement = window.VoiceConfig?.vad?.silenceIncrement || 50;
            this.nonZeroRatioThreshold = window.VoiceConfig?.vad?.nonZeroRatioThreshold || 0.05;
            this.isSpeaking = false;
            this.audioBuffer = []; // 音频缓冲区
            this.lastAudioTime = Date.now();
            
            // 音频处理参数 - 从配置文件读取
            this.audioChunkSize = window.VoiceConfig?.audio?.chunkSize || 12288;
            this.audioSendInterval = window.VoiceConfig?.audio?.sendInterval || 300;
            this.gainFactor = window.VoiceConfig?.audio?.gainFactor || 2.0;
            
            console.log('🎛️ VAD参数已加载:', {
                vadThreshold: this.vadThreshold,
                maxSilenceDuration: this.maxSilenceDuration,
                audioChunkSize: this.audioChunkSize,
                audioSendInterval: this.audioSendInterval
            });
            
            processor.onaudioprocess = (event) => {
                const inputBuffer = event.inputBuffer;
                const inputData = inputBuffer.getChannelData(0);
                
                // 🔍 调试：检查音频输入是否正常
                if (Math.random() < 0.01) { // 每100次采样打印一次
                    console.log(`🎤 麦克风输入检测: 样本数=${inputData.length}`);
                }
                
                // 🔧 使用server_vad：直接发送音频数据，让OpenAI服务器端处理VAD
                this.sendAudioDataDirectly(inputData);
            };
            
            source.connect(processor);
            processor.connect(this.audioContext.destination);
            
            console.log('音频处理已启动');
        } catch (error) {
            console.error('启动音频处理失败:', error);
        }
    }
    
    /**
     * 处理音频数据
     */
    processAudioData(audioData) {
        // 🔍 首先验证音频数据是否有效
        const originalVolume = this.calculateVolume(audioData);
        const nonZeroSamples = Array.from(audioData).filter(v => Math.abs(v) > 0.001).length;
        
        // 🚫 暂时禁用静音过滤，确保所有音频数据都能发送
        // 只过滤完全静音的数据（非常宽松的阈值）
        if (false && originalVolume < 0.000001 && nonZeroSamples < 5) {
            if (Math.random() < 0.01) {
                console.log(`🔇 跳过完全静音音频: 音量=${originalVolume.toFixed(8)}, 非零样本=${nonZeroSamples}`);
            }
            return;
        }
        
        // 应用音频增益，提高低音量音频的检测率
        const gainFactor = 2.0; // 2倍增益
        const enhancedAudioData = new Float32Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
            enhancedAudioData[i] = Math.max(-1, Math.min(1, audioData[i] * gainFactor));
        }
        
        // 将Float32Array转换为Int16Array
        const int16Data = new Int16Array(enhancedAudioData.length);
        for (let i = 0; i < enhancedAudioData.length; i++) {
            int16Data[i] = Math.max(-32768, Math.min(32767, enhancedAudioData[i] * 32768));
        }
        
        // 🔍 验证转换后的数据是否有效（非常宽松的阈值）
        const int16NonZero = Array.from(int16Data).filter(v => v !== 0).length;
        if (int16NonZero < 3) {
            if (Math.random() < 0.01) {
                console.log(`🔇 转换后数据仍为静音: 非零样本=${int16NonZero}`);
            }
            return;
        }
        
        // 转换为base64
        const base64 = this.arrayBufferToBase64(int16Data.buffer);
        
        // 每50次发送记录一次（避免日志过多）
        if (Math.random() < 0.02) {
            console.log(`📤 发送有效音频数据: 原始长度=${audioData.length}, 原始音量=${originalVolume.toFixed(6)}, 非零样本=${nonZeroSamples}, base64长度=${base64.length}`);
        }
        
        // 检查音频质量 - 基于OpenAI官方文档，确保满足100ms最小要求
        if (base64.length < 6000) { // 提高最小阈值，确保有足够的音频数据
            console.warn(`⚠️ 音频数据可能太小: ${base64.length}，建议至少6000字节以满足100ms要求`);
        } else if (base64.length > 50000) {
            console.warn(`⚠️ 音频数据可能太大: ${base64.length}`);
        }
        
        // 验证音频数据完整性
        if (audioData.length < 1024) {
            console.warn(`⚠️ 音频采样数据太少: ${audioData.length}`);
        }
        
        // 每50次发送记录一次音频质量
        if (Math.random() < 0.02) {
            const originalVolume = this.calculateVolume(audioData);
            const enhancedVolume = this.calculateVolume(enhancedAudioData);
            // 计算音频时长：PCM16格式，16kHz采样率，2字节/样本
            const audioDurationMs = (audioData.length / 2) / 16000 * 1000;
            console.log(`🎵 音频质量监控: 原始长度=${audioData.length}, base64长度=${base64.length}, 时长=${audioDurationMs.toFixed(1)}ms, 原始音量=${originalVolume.toFixed(4)}, 增强后音量=${enhancedVolume.toFixed(4)}`);
            
            // 如果音量过低，给出警告
            if (originalVolume < 0.01) {
                console.warn(`⚠️ 原始音量过低: ${originalVolume.toFixed(4)}, 已应用2倍增益`);
            }
            
            // 如果音频时长不足，给出警告
            if (audioDurationMs < 100) {
                console.warn(`⚠️ 音频时长不足: ${audioDurationMs.toFixed(1)}ms, 需要至少100ms`);
            }
        }
        
        // 发送音频数据到后端
        this.sendMessage({
            type: 'audio_stream',
            scenario: 'voice_call', // 关键：标识这是语音通话场景
            audio_base64: base64,
            timestamp: Date.now() / 1000,
            client_id: this.clientId
        });
    }
    
    /**
     * 统一的音频处理和VAD逻辑
     */
    processAudioWithVAD(audioData) {
        // 🔍 首先检查原始音频数据是否真的是静音
        const originalVolume = this.calculateVolume(audioData);
        const nonZeroSamples = Array.from(audioData).filter(v => Math.abs(v) > 0.001).length;
        const nonZeroRatio = nonZeroSamples / audioData.length;
        
        // 🚫 暂时禁用静音过滤，确保所有音频数据都能发送
        // 只过滤完全静音的数据（使用配置文件参数）
        const silenceVolumeThreshold = window.VoiceConfig?.silence?.volumeThreshold || 0.000001;
        const silenceNonZeroRatioThreshold = window.VoiceConfig?.silence?.nonZeroRatioThreshold || 0.0001;
        
        // 临时禁用静音过滤，确保音频数据能发送到后端
        if (false && originalVolume < silenceVolumeThreshold && nonZeroRatio < silenceNonZeroRatioThreshold) {
            if (Math.random() < 0.01) {
                console.log(`🔇 检测到完全静音数据: 音量=${originalVolume.toFixed(8)}, 非零样本=${nonZeroSamples}/${audioData.length} (${(nonZeroRatio*100).toFixed(1)}%)`);
            }
            return; // 只过滤完全静音的数据
        }
        
        // 应用音频增益，提高低音量音频的检测率（使用配置文件参数）
        const gainFactor = this.gainFactor;
        const enhancedAudioData = new Float32Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
            enhancedAudioData[i] = Math.max(-1, Math.min(1, audioData[i] * gainFactor));
        }
        
        // 计算音频音量（使用增强后的音频数据）
        const volume = this.calculateVolume(enhancedAudioData);
        const currentTime = Date.now();
        
        // 每100次处理记录一次音量（避免日志过多）
        if (Math.random() < 0.01) {
            console.log(`🔊 客户端VAD: 原始音量=${originalVolume.toFixed(6)}, 增强音量=${volume.toFixed(6)}, 阈值=${this.vadThreshold}, 非零样本=${nonZeroSamples}, 状态=${this.isSpeaking ? '说话中' : '静音'}`);
        }
        
        // 🔍 语音检测：音量必须足够高，且非零样本比例足够大（使用配置文件参数）
        // 更严格的语音检测：需要持续的高音量和足够的非零样本
        const isRealSpeech = volume > this.vadThreshold && 
                           nonZeroRatio > this.nonZeroRatioThreshold && 
                           nonZeroSamples > 100; // 至少100个非零样本
        
        // 检测是否在说话
        if (isRealSpeech) {
            // 有声音，重置静音计时
            this.silenceDuration = 0;
            this.lastAudioTime = currentTime;
            
            if (!this.isSpeaking) {
                console.log(`🎤 开始说话 - 音量: ${volume.toFixed(6)}, 阈值: ${this.vadThreshold}, 非零样本: ${nonZeroSamples}`);
                this.isSpeaking = true;
                this.updateStatusIndicator('正在说话', 'blue');
                
                // 增强打断机制：立即打断AI回复
                if (this.isAIResponding()) {
                    console.log('🛑 AI正在回复，用户开始说话，立即打断');
                    this.interruptAIResponse();
                }
            }
            
            // 🔧 正确逻辑：说话时累积音频数据，不立即发送
            this.audioBuffer.push(audioData);
            
        } else {
            // 静音
            if (this.isSpeaking) {
                // 用户正在说话，但检测到静音
                this.silenceDuration += this.silenceIncrement;
                
                // 如果静音时间超过阈值，认为用户停止说话
                if (this.silenceDuration >= this.maxSilenceDuration) {
                    console.log(`🔇 检测到静音，用户停止说话，提交音频 (静音时长: ${this.silenceDuration}ms, 阈值: ${this.maxSilenceDuration}ms)`);
                    this.submitAudioBuffer();
                    this.isSpeaking = false;
                    this.silenceDuration = 0;
                    this.updateStatusIndicator('处理中', 'orange');
                }
                // 注意：静音期间不添加到音频缓冲区，也不发送数据
            }
            // 如果用户没有在说话，静音期间什么都不做
        }
    }
    
    /**
     * 直接发送音频数据（使用server_vad）
     */
    sendAudioDataDirectly(audioData) {
        // 🔧 使用server_vad：直接发送所有音频数据，不做任何VAD检测
        
        // 🔍 快速检测用户是否在说话（用于打断检测）
        const volume = this.calculateVolume(audioData);
        const isUserSpeaking = volume > 0.005; // 降低阈值，提高敏感度
        
        // 🛑 如果用户开始说话且AI正在回复，立即打断
        if (isUserSpeaking && this.isAIResponding()) {
            console.log('🛑 检测到用户说话，立即打断AI回复');
            this.interruptAIResponse();
        }
        
        // 应用音频增益，提高低音量音频的检测率
        const gainFactor = 2.0; // 2倍增益
        const enhancedAudioData = new Float32Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
            enhancedAudioData[i] = Math.max(-1, Math.min(1, audioData[i] * gainFactor));
        }
        
        // 将Float32Array转换为Int16Array
        const int16Data = new Int16Array(enhancedAudioData.length);
        for (let i = 0; i < enhancedAudioData.length; i++) {
            int16Data[i] = Math.max(-32768, Math.min(32767, enhancedAudioData[i] * 32768));
        }
        
        // 转换为base64
        const base64 = this.arrayBufferToBase64(int16Data.buffer);
        
        // 每50次发送记录一次（避免日志过多）
        if (Math.random() < 0.02) {
            console.log(`📤 发送音频数据: base64长度=${base64.length}, 原始长度=${audioData.length}`);
        }
        
        // 发送音频数据到后端
        this.sendMessage({
            type: 'audio_stream',
            scenario: 'voice_call', // 关键：标识这是语音通话场景
            audio_base64: base64,
            timestamp: Date.now() / 1000,
            client_id: this.clientId
        });
    }
    
    /**
     * 发送音频数据到后端（已废弃，保留兼容性）
     */
    sendAudioData(audioData) {
        // 🔍 首先验证音频数据是否有效
        const originalVolume = this.calculateVolume(audioData);
        const nonZeroSamples = Array.from(audioData).filter(v => Math.abs(v) > 0.001).length;
        
        // 🚫 暂时禁用静音过滤，确保所有音频数据都能发送
        // 只过滤完全静音的数据（非常宽松的阈值）
        if (false && originalVolume < 0.000001 && nonZeroSamples < 5) {
            if (Math.random() < 0.01) {
                console.log(`🔇 跳过完全静音音频: 音量=${originalVolume.toFixed(8)}, 非零样本=${nonZeroSamples}`);
            }
            return;
        }
        
        // 应用音频增益，提高低音量音频的检测率
        const gainFactor = 2.0; // 2倍增益
        const enhancedAudioData = new Float32Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
            enhancedAudioData[i] = Math.max(-1, Math.min(1, audioData[i] * gainFactor));
        }
        
        // 将Float32Array转换为Int16Array
        const int16Data = new Int16Array(enhancedAudioData.length);
        for (let i = 0; i < enhancedAudioData.length; i++) {
            int16Data[i] = Math.max(-32768, Math.min(32767, enhancedAudioData[i] * 32768));
        }
        
        // 🔍 验证转换后的数据是否有效（暂时禁用静音检测）
        const int16NonZero = Array.from(int16Data).filter(v => v !== 0).length;
        if (false && int16NonZero < 10) {
            if (Math.random() < 0.01) {
                console.log(`🔇 转换后数据仍为静音: 非零样本=${int16NonZero}`);
            }
            return;
        }
        
        // 转换为base64
        const base64 = this.arrayBufferToBase64(int16Data.buffer);
        
        // 每50次发送记录一次（避免日志过多）
        if (Math.random() < 0.02) {
            console.log(`📤 发送有效音频数据: 原始长度=${audioData.length}, 原始音量=${originalVolume.toFixed(6)}, 非零样本=${nonZeroSamples}, base64长度=${base64.length}`);
        }
        
        // 检查音频质量 - 基于OpenAI官方文档，确保满足100ms最小要求
        if (base64.length < 6000) { // 提高最小阈值，确保有足够的音频数据
            console.warn(`⚠️ 音频数据可能太小: ${base64.length}，建议至少6000字节以满足100ms要求`);
        } else if (base64.length > 50000) {
            console.warn(`⚠️ 音频数据可能太大: ${base64.length}`);
        }
        
        // 验证音频数据完整性
        if (audioData.length < 1024) {
            console.warn(`⚠️ 音频采样数据太少: ${audioData.length}`);
        }
        
        // 每50次发送记录一次音频质量
        if (Math.random() < 0.02) {
            const originalVolume = this.calculateVolume(audioData);
            const enhancedVolume = this.calculateVolume(enhancedAudioData);
            // 计算音频时长：PCM16格式，16kHz采样率，2字节/样本
            const audioDurationMs = (audioData.length / 2) / 16000 * 1000;
            console.log(`🎵 音频质量监控: 原始长度=${audioData.length}, base64长度=${base64.length}, 时长=${audioDurationMs.toFixed(1)}ms, 原始音量=${originalVolume.toFixed(4)}, 增强后音量=${enhancedVolume.toFixed(4)}`);
            
            // 如果音量过低，给出警告
            if (originalVolume < 0.01) {
                console.warn(`⚠️ 原始音量过低: ${originalVolume.toFixed(4)}, 已应用2倍增益`);
            }
            
            // 如果音频时长不足，给出警告
            if (audioDurationMs < 100) {
                console.warn(`⚠️ 音频时长不足: ${audioDurationMs.toFixed(1)}ms, 需要至少100ms`);
            }
        }
        
        // 发送音频数据到后端
        console.log(`📤 发送音频数据: base64长度=${base64.length}, 原始长度=${audioData.length}, 非零样本=${int16NonZero}`);
        
        // 🔍 最终检查：确保音频数据有效
        if (int16NonZero < 50) {
            console.warn(`⚠️ 音频数据可能无效: 非零样本=${int16NonZero}, 跳过发送`);
            return;
        }
        
        this.sendMessage({
            type: 'audio_stream',
            scenario: 'voice_call', // 关键：标识这是语音通话场景
            audio_base64: base64,
            timestamp: Date.now() / 1000,
            client_id: this.clientId
        });
    }
    
    /**
     * 使用语音活动检测处理音频数据（已废弃，保留兼容性）
     */
    processAudioDataWithVAD(audioData) {
        // 🔍 首先检查原始音频数据是否真的是静音
        const originalVolume = this.calculateVolume(audioData);
        const nonZeroSamples = Array.from(audioData).filter(v => Math.abs(v) > 0.001).length;
        const nonZeroRatio = nonZeroSamples / audioData.length;
        
        // 🚫 暂时禁用静音过滤，确保所有音频数据都能发送
        // 只过滤完全静音的数据（使用配置文件参数）
        const silenceVolumeThreshold = window.VoiceConfig?.silence?.volumeThreshold || 0.000001;
        const silenceNonZeroRatioThreshold = window.VoiceConfig?.silence?.nonZeroRatioThreshold || 0.0001;
        
        // 临时禁用静音过滤，确保音频数据能发送到后端
        if (false && originalVolume < silenceVolumeThreshold && nonZeroRatio < silenceNonZeroRatioThreshold) {
            if (Math.random() < 0.01) {
                console.log(`🔇 检测到完全静音数据: 音量=${originalVolume.toFixed(8)}, 非零样本=${nonZeroSamples}/${audioData.length} (${(nonZeroRatio*100).toFixed(1)}%)`);
            }
            return; // 只过滤完全静音的数据
        }
        
        // 应用音频增益，提高低音量音频的检测率（使用配置文件参数）
        const gainFactor = this.gainFactor;
        const enhancedAudioData = new Float32Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
            enhancedAudioData[i] = Math.max(-1, Math.min(1, audioData[i] * gainFactor));
        }
        
        // 计算音频音量（使用增强后的音频数据）
        const volume = this.calculateVolume(enhancedAudioData);
        const currentTime = Date.now();
        
        // 每100次处理记录一次音量（避免日志过多）
        if (Math.random() < 0.01) {
            console.log(`🔊 客户端VAD: 原始音量=${originalVolume.toFixed(6)}, 增强音量=${volume.toFixed(6)}, 阈值=${this.vadThreshold}, 非零样本=${nonZeroSamples}, 状态=${this.isSpeaking ? '说话中' : '静音'}`);
        }
        
        // 🔍 语音检测：音量必须足够高，且非零样本比例足够大（使用配置文件参数）
        // 更严格的语音检测：需要持续的高音量和足够的非零样本
        const isRealSpeech = volume > this.vadThreshold && 
                           nonZeroRatio > this.nonZeroRatioThreshold && 
                           nonZeroSamples > 100; // 至少100个非零样本
        
        // 检测是否在说话
        if (isRealSpeech) {
            // 有声音，重置静音计时
            this.silenceDuration = 0;
            this.lastAudioTime = currentTime;
            
            if (!this.isSpeaking) {
                console.log(`🎤 开始说话 - 音量: ${volume.toFixed(6)}, 阈值: ${this.vadThreshold}`);
                this.isSpeaking = true;
                this.updateStatusIndicator('正在说话', 'blue');
                
                // 增强打断机制：立即打断AI回复
                if (this.isAIResponding()) {
                    console.log('🛑 AI正在回复，用户开始说话，立即打断');
                    this.interruptAIResponse();
                }
            }
            
            // 添加到音频缓冲区
            this.audioBuffer.push(audioData);
            
            // 实时发送音频数据，提高响应速度
            this.processAudioData(audioData);
            
        } else {
            // 静音
            if (this.isSpeaking) {
                this.silenceDuration += this.silenceIncrement; // 使用配置文件参数
                
                // 如果静音时间超过阈值，提交音频
                if (this.silenceDuration >= this.maxSilenceDuration) {
                    console.log(`🔇 检测到静音，提交音频 (静音时长: ${this.silenceDuration}ms, 阈值: ${this.maxSilenceDuration}ms)`);
                    this.submitAudioBuffer();
                    this.isSpeaking = false;
                    this.silenceDuration = 0;
                    this.updateStatusIndicator('处理中', 'orange');
                } else {
                    // 继续添加到音频缓冲区，直到静音时间达到阈值
                    this.audioBuffer.push(audioData);
                }
            }
        }
    }
    
    /**
     * 计算音频音量
     */
    calculateVolume(audioData) {
        let sum = 0;
        for (let i = 0; i < audioData.length; i++) {
            sum += audioData[i] * audioData[i];
        }
        return Math.sqrt(sum / audioData.length);
    }
    
    /**
     * 检查AI是否正在回复
     */
    isAIResponding() {
        // 检查是否有音频正在播放
        if (window.voicePlayerEnhanced && window.voicePlayerEnhanced.isPlaying) {
            return true;
        }
        
        // 检查播放队列是否有待播放的音频
        if (window.voicePlayerEnhanced && window.voicePlayerEnhanced.audioQueue.length > 0) {
            return true;
        }
        
        return false;
    }
    
    /**
     * 打断AI回复
     */
    interruptAIResponse() {
        console.log('🛑 用户开始说话，立即打断AI回复');
        
        // 🚀 立即停止当前播放的音频（最高优先级）
        if (window.voicePlayerEnhanced) {
            console.log('🛑 强制停止语音播放');
            window.voicePlayerEnhanced.forceStopAllAudio();
        }
        
        // 🚀 立即发送打断信号到后端（异步，不阻塞）
        this.sendMessage({
            type: 'interrupt',
            timestamp: Date.now() / 1000,
            client_id: this.clientId
        });
        
        // 🚀 立即更新状态指示器
        this.updateStatusIndicator('用户打断', 'red');
        
        // 🚀 清空音频缓冲区，准备新的输入
        this.audioBuffer = [];
        this.isSpeaking = true; // 保持说话状态，准备新的输入
        
        // 🚀 设置打断标志，防止重复触发
        this.isInterrupting = true;
        setTimeout(() => {
            this.isInterrupting = false;
        }, 1000); // 1秒后重置
        
        // 强制停止所有音频处理
        if (this.audioContext && this.audioContext.state !== 'closed') {
            try {
                this.audioContext.suspend();
                console.log('🛑 音频上下文已暂停');
            } catch (error) {
                console.log('音频上下文暂停失败:', error);
            }
        }
    }
    
    /**
     * 提交音频缓冲区（已废弃，使用server_vad时不需要）
     */
    submitAudioBuffer() {
        console.log('📤 提交音频缓冲区，长度:', this.audioBuffer.length);
        
        if (this.audioBuffer.length > 0) {
            // 🔧 发送整个音频缓冲区到后端
            this.sendCompleteAudioBuffer();
        }
        
        // 发送音频完成消息，告诉后端用户停止说话
        this.sendMessage({
            type: 'audio_complete',
            scenario: 'voice_call', // 关键：标识这是语音通话场景
            timestamp: Date.now() / 1000,
            client_id: this.clientId
        });
        
        // 清空音频缓冲区
        this.audioBuffer = [];
    }
    
    /**
     * 发送完整的音频缓冲区
     */
    sendCompleteAudioBuffer() {
        if (this.audioBuffer.length === 0) {
            console.log('⚠️ 音频缓冲区为空，无法发送');
            return;
        }
        
        // 合并所有音频数据
        const totalLength = this.audioBuffer.reduce((sum, buffer) => sum + buffer.length, 0);
        const mergedAudioData = new Float32Array(totalLength);
        let offset = 0;
        
        for (const buffer of this.audioBuffer) {
            mergedAudioData.set(buffer, offset);
            offset += buffer.length;
        }
        
        console.log(`🎵 发送完整音频缓冲区: ${this.audioBuffer.length}个片段, 总长度=${totalLength}样本`);
        
        // 发送合并后的音频数据
        this.sendAudioData(mergedAudioData);
    }
    
    /**
     * 处理打断确认消息
     */
    handleInterruptConfirmed(message) {
        console.log('✅ 打断确认收到:', message.message);
        this.updateStatusIndicator('已停止回复，等待新输入', 'green');
    }
    
    /**
     * 处理停止播放消息
     */
    handleStopPlayback(message) {
        console.log('🛑 收到停止播放指令:', message.message);
        
        // 立即停止所有语音播放
        if (window.voicePlayerEnhanced) {
            console.log('🛑 执行停止播放指令');
            window.voicePlayerEnhanced.stopCurrentPlayback();
        }
        
        // 更新状态指示器
        this.updateStatusIndicator('通话已停止', 'gray');
    }
    
    /**
     * 将ArrayBuffer转换为base64
     */
    arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }
    
    /**
     * 更新状态指示器
     */
    updateStatusIndicator(text, color) {
        const statusElement = document.getElementById('realtime-status-text');
        
        if (statusElement) {
            statusElement.textContent = text;
            // 更新颜色
            statusElement.style.color = color === 'green' ? '#52c41a' : 
                                      color === 'blue' ? '#1890ff' : 
                                      color === 'red' ? '#ff4d4f' : '#666666';
        }
    }
    
    /**
     * 发送消息
     */
    sendMessage(message) {
        if (!this.isConnected || !this.ws) {
            console.error('WebSocket未连接，无法发送消息');
            return false;
        }
        
        try {
            const messageStr = JSON.stringify(message);
            this.ws.send(messageStr);
            // 注释掉心跳消息的日志
            if (message.type !== 'heartbeat') {
                console.log('发送语音消息:', message.type);
            }
            return true;
        } catch (error) {
            console.error('发送消息失败:', error);
            return false;
        }
    }
    
    /**
     * 发送音频输入消息
     */
    async sendAudioInput(audioData, options = {}) {
        try {
            const encodedAudio = await this.encodeAudioData(audioData);
            const message = {
                type: 'audio_input',
                // 兼容后端旧STT管线字段：使用 audio_base64
                audio_base64: encodedAudio,
                timestamp: Date.now() / 1000,
                client_id: this.clientId,
                session_id: this.sessionId,
                ...options
            };
            return this.sendMessage(message);
        } catch (error) {
            console.error('编码音频数据失败:', error);
            return false;
        }
    }
    
    /**
     * 发送音频流消息
     */
    sendAudioStream(audioChunk, options = {}) {
        const message = {
            type: 'audio_stream',
            scenario: 'voice_call', // 关键：标识这是语音通话场景
            // 兼容后端旧字段：使用 audio_base64
            audio_base64: this.encodeAudioData(audioChunk),
            timestamp: Date.now() / 1000,
            client_id: this.clientId,
            session_id: this.sessionId,
            ...options
        };
        return this.sendMessage(message);
    }
    
    /**
     * 发送语音命令
     */
    sendVoiceCommand(command, options = {}) {
        const message = {
            type: 'voice_command',
            command: command,
            timestamp: Date.now() / 1000,
            client_id: this.clientId,
            session_id: this.sessionId,
            ...options
        };
        return this.sendMessage(message);
    }
    
    /**
     * 查询状态
     */
    sendStatusQuery() {
        const message = {
            type: 'status_query',
            timestamp: Date.now() / 1000,
            client_id: this.clientId,
            session_id: this.sessionId
        };
        return this.sendMessage(message);
    }
    
    /**
     * 处理接收到的消息
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            // 注释掉心跳消息的日志
            if (message.type !== 'heartbeat_response') {
                console.log('收到语音消息:', message.type);
            }

            // 仅在 connection_established 时绑定 client_id，提高安全性
            if (message.type === 'connection_established' && message.client_id) {
                this.clientId = message.client_id;
                if (!window.voiceChatState) {
                    window.voiceChatState = {};
                }
                window.voiceChatState.clientId = this.clientId;
                window.voiceChatState.isConnected = this.isConnected;
                console.log('首次绑定client_id:', this.clientId);
                
        // 注册连接确认消息处理器
        this.registerMessageHandler('connection_established', (data) => {
            console.log('WebSocket连接已建立:', data);
            // 连接确认消息已处理
        });
        
        // 注册语音通话相关消息处理器
        this.registerMessageHandler('voice_call_started', (data) => {
            console.log('语音通话已启动:', data);
            // 启动音频流处理
            this.startAudioStreaming();
            // 更新状态指示器
            this.updateStatusIndicator('通话中', 'green');
        });
        
        this.registerMessageHandler('voice_call_stopped', (data) => {
            console.log('语音通话已停止:', data);
            // 停止音频流处理
            this.stopAudioStreaming();
            // 更新状态指示器
            this.updateStatusIndicator('等待开始', 'gray');
        });
        
        // 注册AI音频响应处理器
        this.registerMessageHandler('audio_stream', (data) => {
            console.log('🎵 收到AI音频响应:', data);
            
            // 🚀 检查是否正在打断，如果是则忽略新的音频
            if (this.isInterrupting) {
                console.log('🛑 正在打断中，忽略新的音频数据');
                return;
            }
            
            // 播放AI的音频回复
            if (data.audio && window.voicePlayerEnhanced) {
                console.log('🎵 开始播放AI音频，数据长度:', data.audio.length);
                window.voicePlayerEnhanced.playAudioFromBase64(data.audio);
            } else {
                console.warn('🎵 无法播放AI音频：', {
                    hasAudio: !!data.audio,
                    hasPlayer: !!window.voicePlayerEnhanced
                });
            }
        });
        
        // 注册错误消息处理器
        this.registerMessageHandler('error', (data) => {
            console.error('语音通话错误:', data);
            // 显示错误消息给用户
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('global-message', {
                    children: data.message || '语音通话出现错误'
                });
            }
        });
        
        // 注册打断确认消息处理器
        this.registerMessageHandler('interrupt_confirmed', (data) => {
            this.handleInterruptConfirmed(data);
        });
        
        // 注册停止播放消息处理器
        this.registerMessageHandler('stop_playback', (data) => {
            this.handleStopPlayback(data);
        });
                
                // 立即写入 Dash Store，便于 SSE 侧携带一致的 client_id
                const connectionData = { connected: true, client_id: this.clientId, timestamp: Date.now() };
                const enableVoiceData = { enable: true, client_id: this.clientId, ts: Date.now() };
                
            // 使用全局变量存储client_id，避免时机问题
            window.voiceClientId = this.clientId;
            window.voiceWebSocketConnected = true;
            console.log('已设置全局client_id:', this.clientId);
            
            // 添加全局函数来获取client_id
            window.getVoiceClientId = () => {
                return window.voiceClientId || null;
            };
            
            // 添加一个方法来获取当前的client_id
            this.getClientId = () => {
                return this.clientId || window.voiceClientId;
            };
            
            // 使用正确的dash_clientside.set_props语法更新Store
            const updateDashStore = () => {
                try {
                    // 只在/core/chat页面更新WebSocket Store
                    const currentPath = window.location.pathname;
                    const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
                    
                    if (!isChatPage) {
                        console.log('当前页面不需要更新WebSocket Store:', currentPath);
                        return;
                    }
                    
                    if (window.dash_clientside && window.dash_clientside.set_props) {
                        console.log('使用dash_clientside.set_props更新Store，clientId:', this.clientId);
                        
                        try {
                            // 更新WebSocket连接状态 - 使用正确的语法
                            window.dash_clientside.set_props('voice-websocket-connection', {
                                data: { 
                                    connected: true, 
                                    client_id: this.clientId, 
                                    timestamp: Date.now() 
                                }
                            });
                            console.log('voice-websocket-connection 更新成功');
                            
                            // 更新语音开关状态 - 使用正确的语法
                            window.dash_clientside.set_props('voice-enable-voice', {
                                data: { 
                                    enable: true, 
                                    client_id: this.clientId, 
                                    ts: Date.now() 
                                }
                            });
                            console.log('voice-enable-voice 更新成功');
                        } catch (setPropsError) {
                            console.error('set_props调用失败:', setPropsError);
                            // 延迟重试
                            setTimeout(updateDashStore, 200);
                        }
                    } else {
                        console.log('dash_clientside.set_props 不可用，延迟重试');
                        setTimeout(updateDashStore, 200);
                    }
                } catch (e) {
                    console.error('更新Dash Store失败:', e);
                    // 延迟重试
                    setTimeout(updateDashStore, 200);
                }
            };
            
            // 延迟执行，确保Dash完全初始化
            setTimeout(updateDashStore, 500);
            }

            // 消息验证 - 防串台机制（在完成绑定之后再校验）
            if (!this.validateMessage(message)) {
                console.warn('消息验证失败，丢弃消息:', message);
                return;
            }

            // 此处无需再次更新client_id，上面已完成统一绑定
            
            // 调用对应的处理器
            const handler = this.messageHandlers.get(message.type);
            if (handler) {
                // 注释掉心跳消息处理器的日志
                if (message.type !== 'heartbeat_response') {
                    console.log('调用消息处理器:', message.type);
                }
                try {
                    handler(message);
                } catch (error) {
                    console.error('消息处理器执行失败:', message.type, error);
                }
            } else {
                console.warn('未找到消息处理器:', message.type);
            }
        } catch (error) {
            console.error('解析消息失败:', error);
        }
    }
    
    /**
     * 验证消息是否属于当前用户 - 防串台机制
     */
    validateMessage(message) {
        const { client_id, session_id } = message;
        const state = window.voiceChatState;
        
        // 检查client_id
        if (client_id && client_id !== state.clientId) {
            console.warn('消息client_id不匹配，丢弃:', {
                received: client_id,
                expected: state.clientId
            });
            return false;
        }
        
        // 检查session_id (conversation_id)
        // 仅当本地已记录期望的 sessionId 时才严格校验；否则先放行以完成首次绑定
        if (state.sessionId && session_id && session_id !== state.sessionId) {
            console.warn('消息session_id不匹配，丢弃:', {
                received: session_id,
                expected: state.sessionId
            });
            return false;
        }
        
        return true;
    }
    
    /**
     * 注册消息处理器
     */
    registerMessageHandler(messageType, handler) {
        this.messageHandlers.set(messageType, handler);
        console.log('注册消息处理器:', messageType);
    }
    
    /**
     * 注册连接处理器
     */
    registerConnectionHandler(handler) {
        this.connectionHandlers.push(handler);
    }
    
    /**
     * 注册断开连接处理器
     */
    registerDisconnectionHandler(handler) {
        this.disconnectionHandlers.push(handler);
    }
    
    /**
     * 开始心跳
     */
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.sendMessage({
                    type: 'heartbeat',
                    timestamp: Date.now() / 1000,
                    client_id: this.clientId
                });
            }
        }, 30000); // 30秒心跳
    }
    
    /**
     * 停止心跳
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    /**
     * 安排重连
     */
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);
        console.log(`将在 ${delay}ms 后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }
    
    /**
     * 通知连接处理器
     */
    notifyConnectionHandlers(success) {
        this.connectionHandlers.forEach(handler => {
            try {
                handler(success);
            } catch (error) {
                console.error('连接处理器执行失败:', error);
            }
        });
    }
    
    /**
     * 通知断开连接处理器
     */
    notifyDisconnectionHandlers() {
        this.disconnectionHandlers.forEach(handler => {
            try {
                handler();
            } catch (error) {
                console.error('断开连接处理器执行失败:', error);
            }
        });
    }
    
    /**
     * 编码音频数据为base64
     */
    encodeAudioData(audioData) {
        if (audioData instanceof Blob) {
            // 对于Blob对象，需要异步处理
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = () => {
                    const base64 = reader.result.split(',')[1];
                    resolve(base64);
                };
                reader.readAsDataURL(audioData);
            });
        } else if (audioData instanceof ArrayBuffer) {
            // 对于ArrayBuffer，直接转换
            const bytes = new Uint8Array(audioData);
            let binary = '';
            for (let i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
        } else {
            // 假设已经是base64字符串
            return audioData;
        }
    }
    
    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            clientId: this.clientId,
            reconnectAttempts: this.reconnectAttempts,
            maxReconnectAttempts: this.maxReconnectAttempts
        };
    }
    
    /**
     * 获取WebSocket连接对象
     */
    getConnection() {
        // 如果已连接，直接返回连接
        if (this.isConnected && this.ws) {
            return this.ws;
        }
        
        // 如果正在连接中，等待连接完成
        if (this.isConnecting) {
            console.log('WebSocket正在连接中，等待连接完成...');
            return null;
        }
        
        // 如果未连接，尝试连接（只允许一次）
        if (!this.isConnected && !this.isConnecting) {
            console.warn('WebSocket未连接，尝试连接...');
            this.connect();
        }
        
        return null; // 连接中或未连接时返回null
    }
    
    /**
     * 等待连接建立（用于组件初始化）
     */
    async waitForConnection(maxWaitTime = 5000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < maxWaitTime) {
            if (this.isConnected && this.ws) {
                return this.ws;
            }
            if (this.isConnecting) {
                // 等待连接完成
                await new Promise(resolve => setTimeout(resolve, 100));
                continue;
            }
            // 如果既未连接也不在连接中，尝试连接
            if (!this.isConnected && !this.isConnecting) {
                this.connect();
            }
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.warn('等待WebSocket连接超时');
        return null;
    }
}

// 创建全局实例
window.voiceWebSocketManager = new VoiceWebSocketManager();
