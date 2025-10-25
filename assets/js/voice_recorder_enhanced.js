/**
 * 增强版语音录制器 - 支持录音波形显示和语音转文本
 * 使用公共工具类优化代码复用和状态管理
 */

class VoiceRecorderEnhanced {
    constructor() {
        this.mediaRecorder = null;
        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.dataArray = null;
        this.isRecording = false;
        this.audioChunks = [];
        this.websocket = null;
        this.animationId = null;
        
        // 使用配置类获取录音配置
        this.config = {
            sampleRate: window.voiceConfig?.get('sampleRate') || 16000,
            channels: window.voiceConfig?.get('channels') || 1,
            bitRate: window.voiceConfig?.get('bitRate') || 128000
        };
        
        // 异步初始化
        this.init().catch(error => {
            VoiceUtils.handleError(error, '录音器初始化');
        });
    }
    
    async init() {
        // 初始化WebSocket连接
        await this.initWebSocket();
        
        // 绑定事件
        this.bindEvents();
        
        // 监听状态变化
        this.initStateListener();
    }
    
    /**
     * 初始化状态监听 - 使用状态协调器
     */
    initStateListener() {
        // 注册到状态协调器
        if (window.voiceStateCoordinator) {
            window.voiceStateCoordinator.registerStateListener('voiceRecorder', (oldState, newState, oldScenario, scenario, metadata) => {
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
        console.log(`录音器状态变化: ${oldState} → ${newState} (${scenario})`);
        
        // 如果状态变为中断，停止录音
        if (newState === 'interrupted' && this.isRecording) {
            this.stopRecording();
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
        console.log('🎤 开始清理录音器资源...');
        
        // 停止录音
        if (this.isRecording) {
            console.log('🎤 停止录音中...');
            this.stopRecording();
        }
        
        // 停止音频流（如果还存在）
        if (this.audioStream) {
            console.log('🎤 停止音频流，释放麦克风');
            this.audioStream.getTracks().forEach(track => {
                console.log('🎤 停止音频轨道:', track.label, track.readyState);
                track.stop();
                console.log('🎤 音频轨道已停止');
            });
            this.audioStream = null;
        } else {
            console.log('🎤 音频流已为空，无需释放');
        }
        
        // 清理音频块
        this.audioChunks = [];
        
        // 清理MediaRecorder对象
        if (this.mediaRecorder) {
            console.log('🎤 清理MediaRecorder对象');
            this.mediaRecorder = null;
            console.log('🎤 MediaRecorder已清空');
        }
        
        // 清理音频上下文（如果还存在）
        if (this.audioContext && this.audioContext.state !== 'closed') {
            console.log('🎤 关闭音频上下文');
            try {
                this.audioContext.close();
            } catch (error) {
                console.log('🎤 音频上下文已关闭或无法关闭:', error.message);
            }
            this.audioContext = null;
        } else {
            console.log('🎤 音频上下文已关闭或不存在');
        }
        
        // 清理麦克风节点（如果还存在）
        if (this.microphone) {
            console.log('🎤 断开麦克风节点');
            this.microphone.disconnect();
            this.microphone = null;
        }
        
        // 最终检查所有资源状态
        console.log('🎤 最终资源状态检查:');
        console.log('🎤 - audioStream:', this.audioStream ? '存在' : '已清空');
        console.log('🎤 - audioContext:', this.audioContext ? '存在' : '已清空');
        console.log('🎤 - microphone:', this.microphone ? '存在' : '已清空');
        console.log('🎤 - mediaRecorder:', this.mediaRecorder ? '存在' : '已清空');
        console.log('🎤 - isRecording:', this.isRecording);
        
        // 最终强制释放所有资源
        this.forceReleaseMicrophone();
        
        // 最终检查麦克风状态
        this.checkMicrophoneStatus();
        
        console.log('🎤 录音器资源已完全清理，麦克风已释放');
    }
    
    /**
     * 强制释放所有麦克风相关资源
     */
    forceReleaseMicrophone() {
        console.log('🎤 强制释放所有麦克风资源...');
        
        // 1. 停止所有MediaStream tracks
        if (this.audioStream) {
            console.log('🎤 强制停止所有音频轨道');
            this.audioStream.getTracks().forEach(track => {
                console.log('🎤 强制停止轨道:', track.label, '状态:', track.readyState);
                if (track.readyState !== 'ended') {
                    track.stop();
                    console.log('🎤 轨道已强制停止');
                } else {
                    console.log('🎤 轨道已结束，无需停止');
                }
            });
            // 注意：在这里清空audioStream，确保麦克风被释放
            this.audioStream = null;
            console.log('🎤 MediaStream已清空');
        } else {
            console.log('🎤 MediaStream已为空，无需释放');
        }
        
        // 2. 断开所有音频节点
        if (this.microphone) {
            console.log('🎤 强制断开麦克风节点');
            this.microphone.disconnect();
            this.microphone = null;
        }
        
        // 3. 关闭AudioContext
        if (this.audioContext && this.audioContext.state !== 'closed') {
            console.log('🎤 强制关闭音频上下文');
            try {
                this.audioContext.close();
            } catch (error) {
                console.log('🎤 音频上下文关闭错误:', error.message);
            }
            this.audioContext = null;
        }
        
        // 4. 清理MediaRecorder
        if (this.mediaRecorder) {
            console.log('🎤 强制清理MediaRecorder');
            this.mediaRecorder = null;
        }
        
        // 5. 清理其他资源
        this.audioChunks = [];
        this.analyser = null;
        this.dataArray = null;
        
        console.log('🎤 强制释放完成');
    }
    
    /**
     * 检查浏览器麦克风状态
     */
    checkMicrophoneStatus() {
        console.log('🎤 检查浏览器麦克风状态:');
        
        // 检查navigator.mediaDevices
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            console.log('🎤 - navigator.mediaDevices 可用');
        } else {
            console.log('🎤 - navigator.mediaDevices 不可用');
        }
        
        // 检查当前活动的MediaStream
        if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
            navigator.mediaDevices.enumerateDevices().then(devices => {
                const audioInputs = devices.filter(device => device.kind === 'audioinput');
                console.log('🎤 - 音频输入设备数量:', audioInputs.length);
                audioInputs.forEach((device, index) => {
                    console.log(`🎤 - 设备[${index}]:`, {
                        label: device.label,
                        deviceId: device.deviceId
                    });
                });
            }).catch(error => {
                console.log('🎤 - 枚举设备失败:', error);
            });
        }
        
        // 检查是否有全局的MediaStream
        if (window.currentMediaStream) {
            console.log('🎤 - 全局MediaStream存在:', window.currentMediaStream.active);
        } else {
            console.log('🎤 - 全局MediaStream不存在');
        }
    }
    
    async initWebSocket() {
        try {
            // 使用公共工具初始化WebSocket连接
            const messageHandlers = {
                'transcription_result': (data) => this.handleTranscriptionResult(data),
                'audio_processing_start': () => this.showProcessingStatus()
            };
            
            this.websocket = await VoiceUtils.initWebSocket(window.voiceWebSocketManager, messageHandlers);
            console.log('录音器WebSocket连接已建立');
        } catch (error) {
            VoiceUtils.handleError(error, '录音器WebSocket初始化');
        }
    }
    
    setupWebSocketHandlers() {
        if (!this.websocket) return;
        
        this.websocket.onopen = () => {
            console.log('语音WebSocket连接已建立');
        };
        
        this.websocket.onmessage = (event) => {
            this.handleWebSocketMessage(event);
        };
        
        this.websocket.onerror = (error) => {
            console.error('语音WebSocket错误:', error);
        };
        
        this.websocket.onclose = () => {
            console.log('语音WebSocket连接已关闭');
        };
    }
    
    bindEvents() {
        console.log('绑定录音按钮事件监听器...');
        
        // 监听录音按钮点击事件 - 使用新的按钮ID
        document.addEventListener('click', async (event) => {
            // console.log('文档点击事件触发，目标元素:', event.target);
            
            // 检查是否是录音按钮
            if (event.target.closest('#voice-record-button')) {
                console.log('录音按钮被点击');
                event.preventDefault();
                event.stopPropagation();
                await this.toggleRecording();
            }
            // 检查是否是实时语音对话按钮 - 不处理，让Dash回调处理
            else if (event.target.closest('#realtime-start-btn') || 
                     event.target.closest('#realtime-stop-btn') || 
                     event.target.closest('#realtime-mute-btn')) {
                console.log('实时语音对话按钮被点击，让Dash回调处理');
                // 不阻止事件，让Dash的nClicks回调处理
            }
        });
        
        console.log('录音按钮事件监听器绑定完成');
    }
    
    async toggleRecording() {
        // 使用状态管理器处理按钮点击，而不是直接切换录音状态
        if (window.voiceStateManager) {
            const handled = await window.voiceStateManager.handleButtonClick();
            if (handled) {
                return; // 状态管理器已处理
            }
        }
        
        // 如果没有状态管理器，使用原来的逻辑
        if (this.isRecording) {
            await this.stopRecording();
        } else {
            await this.startRecording();
        }
    }
    
    async startRecording() {
        console.log('startRecording 被调用');
        
        // 检查是否已经在录音
        if (this.isRecording) {
            console.warn('已经在录音中，跳过重复开始');
            return true;
        }
        
        console.log('准备开始录音');
        
        try {
            // 使用公共工具触发录音开始事件
            VoiceUtils.triggerEvent('recording_start', { timestamp: Date.now() });
            VoiceUtils.updateState('recording', 'voice_recording', {});
            
            // 触发Dash状态更新
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('button-event-trigger', {
                    data: {type: 'recording_start', timestamp: Date.now()}
                });
                console.log('录音开始，触发状态更新');
            }
            
            // 请求麦克风权限
            console.log('正在请求麦克风权限...');
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: this.config.sampleRate,
                    channelCount: this.config.channels,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            console.log('麦克风权限获取成功，音频流:', stream);
            
            // 保存音频流引用
            this.audioStream = stream;
            
            // 初始化音频上下文
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.microphone = this.audioContext.createMediaStreamSource(stream);
            
            // 配置分析器
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            
            // 连接音频节点
            this.microphone.connect(this.analyser);
            
            // 初始化MediaRecorder
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus',
                audioBitsPerSecond: this.config.bitRate
            });
            
            // 重置音频块
            this.audioChunks = [];
            
            // 监听数据事件
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            // 监听停止事件
            this.mediaRecorder.onstop = () => {
                // 不在这里处理，避免重复调用
                console.log('录音停止事件触发');
            };
            
            // 开始录音
            this.mediaRecorder.start(100); // 每100ms收集一次数据
            this.isRecording = true;
            
            // 显示录音波形
            this.showRecordingWaveform();
            
            // 禁用输入框
            this.disableInput();
            
            console.log('开始录音');
            return true; // 录音开始成功
            
        } catch (error) {
            console.error('开始录音失败:', error);
            
            // 重置状态
            if (window.voiceStateManager) {
                window.voiceStateManager.stopRecording();
            }
            
            // 根据错误类型提供不同的提示
            let errorMessage = '无法访问麦克风，请检查权限设置';
            if (error.name === 'NotAllowedError') {
                errorMessage = '麦克风权限被拒绝，请在浏览器设置中允许麦克风访问';
            } else if (error.name === 'NotFoundError') {
                errorMessage = '未找到麦克风设备，请检查设备连接';
            } else if (error.name === 'NotReadableError') {
                errorMessage = '麦克风被其他应用占用，请关闭其他应用后重试';
            }
            
            this.showError(errorMessage);
            console.error('录音错误详情:', {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
            return false; // 录音开始失败
        }
    }
    
    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // 🔧 停止音频轨道但不立即清空audioStream
            if (this.audioStream) {
                console.log('🎤 录音停止，停止音频轨道');
                this.audioStream.getTracks().forEach(track => {
                    console.log('🎤 停止音频轨道:', track.label, track.readyState);
                    track.stop();
                    console.log('🎤 音频轨道已停止');
                });
                // 注意：不在这里设置 this.audioStream = null，让forceReleaseMicrophone处理
            } else {
                console.log('🎤 录音停止时，音频流已为空');
            }
            
            // 使用公共工具触发录音停止事件
            VoiceUtils.triggerEvent('recording_stop', { timestamp: Date.now() });
            VoiceUtils.updateState('voice_processing', 'voice_recording', {});
            
            // 触发Dash状态更新
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('button-event-trigger', {
                    data: {type: 'recording_stop', timestamp: Date.now()}
                });
                console.log('录音停止，触发状态更新');
            }
            
            // 停止波形动画
            this.stopWaveformAnimation();
            
            // 隐藏录音波形
            this.hideRecordingWaveform();
            
            // 恢复输入框
            this.enableInput();
            
            // 立即释放所有资源
            if (this.microphone) {
                console.log('🎤 断开麦克风节点');
                console.log('🎤 麦克风节点状态:', this.microphone.context.state);
                this.microphone.disconnect();
                this.microphone = null;
                console.log('🎤 麦克风节点已断开并清空');
            }
            if (this.audioContext && this.audioContext.state !== 'closed') {
                console.log('🎤 关闭音频上下文');
                console.log('🎤 音频上下文状态:', this.audioContext.state);
                try {
                    this.audioContext.close();
                    console.log('🎤 音频上下文关闭成功');
                } catch (error) {
                    console.log('🎤 音频上下文已关闭或无法关闭:', error.message);
                }
                this.audioContext = null;
                console.log('🎤 音频上下文已清空');
            }
            
            // 清理MediaRecorder对象
            if (this.mediaRecorder) {
                console.log('🎤 清理MediaRecorder对象');
                this.mediaRecorder = null;
                console.log('🎤 MediaRecorder已清空');
            }
            
            // 检查MediaStream是否真的被释放
            if (this.audioStream) {
                console.log('🎤 检查MediaStream状态:');
                console.log('🎤 - active:', this.audioStream.active);
                console.log('🎤 - tracks数量:', this.audioStream.getTracks().length);
                this.audioStream.getTracks().forEach((track, index) => {
                    console.log(`🎤 - track[${index}]:`, {
                        label: track.label,
                        readyState: track.readyState,
                        enabled: track.enabled,
                        muted: track.muted
                    });
                });
            } else {
                console.log('🎤 MediaStream已为空');
            }
            
            // 检查麦克风状态
            this.checkMicrophoneStatus();
            
            console.log('停止录音，开始处理音频');
            
            // 更新状态为处理中
            if (window.voiceStateManager) {
                console.log('录音器调用startProcessing，当前状态:', window.voiceStateManager.getState());
                window.voiceStateManager.startProcessing();
                console.log('录音器调用startProcessing后，状态:', window.voiceStateManager.getState());
            } else {
                console.error('voiceStateManager不存在！');
            }
            
            // 处理录音数据
            await this.processRecording();
        }
    }
    
    async processRecording() {
        try {
            console.log('开始处理录音数据，音频块数量:', this.audioChunks.length);
            
            // 创建音频Blob
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            console.log('音频Blob创建完成，大小:', audioBlob.size, 'bytes');
            
            // 显示处理中状态
            this.showProcessingStatus();
            
            // 发送音频到后端进行语音转文本
            console.log('准备发送音频到后端进行STT...');
            await this.sendAudioForTranscription(audioBlob);
            console.log('STT请求发送完成');
            
            // 音频数据发送完成后，强制释放麦克风资源
            this.forceReleaseMicrophone();
            
        } catch (error) {
            console.error('处理录音失败:', error);
            this.showError('语音转文本失败');
            
            // 即使出错也要释放麦克风资源
            this.forceReleaseMicrophone();
        }
    }
    
    async sendAudioForTranscription(audioBlob) {
        return new Promise((resolve, reject) => {
            // 使用 voiceWebSocketManager 检查连接状态，支持自动重连
            if (!window.voiceWebSocketManager || !window.voiceWebSocketManager.isConnected) {
                console.warn('WebSocket未连接，尝试重连...');
                window.voiceWebSocketManager.connect().then(() => {
                    // 重连成功后，延迟一点时间再发送，避免递归调用
                    setTimeout(() => {
                        this._sendAudioData(audioBlob).then(resolve).catch(reject);
                    }, 1000);
                }).catch(() => {
                    reject(new Error('WebSocket连接不可用'));
                });
                return;
            }
            
            // 直接发送音频数据
            this._sendAudioData(audioBlob).then(resolve).catch(reject);
        });
    }
    
    async _sendAudioData(audioBlob) {
        return new Promise((resolve, reject) => {
            // 将音频转换为base64
            const reader = new FileReader();
            reader.onload = () => {
                const base64Audio = reader.result.split(',')[1];
                
                // 使用 voiceWebSocketManager 发送消息
                window.voiceWebSocketManager.sendAudioInput(base64Audio, {
                    audio_format: 'webm',
                    sample_rate: this.config.sampleRate
                }).then((success) => {
                    if (success) {
                        console.log('发送语音转文本请求成功');
                        resolve();
                    } else {
                        reject(new Error('发送语音转文本请求失败'));
                    }
                }).catch((error) => {
                    console.error('发送语音转文本请求失败:', error);
                    reject(error);
                });
            };
            
            reader.onerror = () => {
                reject(new Error('音频文件读取失败'));
            };
            
            reader.readAsDataURL(audioBlob);
        });
    }
    
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);

            // 若消息中包含client_id，立刻同步到Dash Store，避免SSE触发时client_id为None
            try {
                if (data && data.client_id && window.dash_clientside && window.dash_clientside.set_props) {
                    window.dash_clientside.set_props('voice-websocket-connection', {
                        data: { connected: true, client_id: data.client_id, timestamp: Date.now() }
                    });
                    // console.log('已从WS消息同步client_id到Store:', data.client_id);
                }
            } catch (e) { /* noop */ }
            
            switch (data.type) {
                case 'transcription_result':
                    this.handleTranscriptionResult(data);
                    break;
                // 忽略TTS相关消息，交由播放器处理
                case 'voice_generation_start':
                case 'voice_response':
                case 'audio_stream':
                case 'synthesis_complete':
                /*
                // 过去为避免混淆，这里忽略了WS侧文本流事件；服务端已不再通过WS返回文本，现按需恢复默认逻辑。
                case 'processing_start':
                case 'stream_start':
                case 'stream_chunk':
                case 'stream_end':
                */
                    break;
                case 'error':
                    let errorMessage = '语音处理错误';
                    if (data && data.error && data.error.message) {
                        errorMessage = data.error.message;
                    } else if (data && data.message) {
                        errorMessage = data.message;
                    } else {
                        console.error('语音WebSocket错误(无详情)');
                    }
                    this.showError(errorMessage);
                    break;
                default:
                    console.log('收到WebSocket消息:', data);
            }
        } catch (error) {
            console.error('处理WebSocket消息失败:', error);
        }
    }
    
    handleTranscriptionResult(data) {
        console.log('收到转录结果:', data);
        
        if (data.text && data.text.trim()) {
            // 使用公共工具触发STT完成事件
            VoiceUtils.triggerEvent('voice_transcription_complete', { 
                timestamp: Date.now(),
                text: data.text.trim()
            });
            
            // 立即将 client_id 推送到 Store 与 语音开关，确保随后的 SSE 能带上 client_id
            try {
                const cid = (window.voiceChatState && window.voiceChatState.clientId) || localStorage.getItem('voiceClientId');
                if (cid && window.dash_clientside && window.dash_clientside.set_props) {
                    window.dash_clientside.set_props('voice-websocket-connection', {
                        data: { connected: true, client_id: cid, timestamp: Date.now() }
                    });
                    window.dash_clientside.set_props('voice-enable-voice', {
                        data: { enable: true, client_id: cid, ts: Date.now() }
                    });
                }
            } catch (_) {}

            // 通过Dash回调更新输入框
            this.updateInputBoxViaDash(data.text.trim());
            
            // 交由Dash回调统一发送，避免重复
            
            // 隐藏处理状态
            this.hideProcessingStatus();
            
            // 转录完成，状态保持为处理中，等待SSE和TTS完成
            console.log('语音转文本成功:', data.text);
            console.log('当前状态保持为处理中，等待SSE和TTS完成');
        } else {
            console.log('转录结果为空或无效:', data);
            this.showError('未识别到语音内容');
            
            // 使用公共工具重置状态
            VoiceUtils.updateState('idle', null, {});
            
            // 触发状态更新事件，确保按钮状态回到空闲
            const currentPath = window.location.pathname;
            const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
            
            if (isChatPage && window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props('button-event-trigger', {
                    data: {type: 'stt_failed', timestamp: Date.now()}
                });
                console.log('STT失败，触发状态重置');
            }
            
            // 隐藏处理状态
            this.hideProcessingStatus();
        }
    }
    
    /**
     * 自动发送消息
     */
    autoSendMessage(text) {
        try {
            console.log('自动发送消息:', text);
            
            // 模拟点击发送按钮
            const sendButton = document.getElementById('ai-chat-x-send-btn');
            if (sendButton && !sendButton.disabled) {
                // 确保输入框有值
                const inputElement = document.getElementById('ai-chat-x-input');
                if (inputElement) {
                    inputElement.value = text;
                    // 触发输入事件
                    inputElement.dispatchEvent(new Event('input', { bubbles: true }));
                }
                
                // 点击发送按钮
                sendButton.click();
                console.log('已自动点击发送按钮');
            } else {
                console.warn('发送按钮不可用或已禁用');
            }
        } catch (error) {
            console.error('自动发送消息失败:', error);
        }
    }
    
    /**
     * 通过Dash回调更新输入框
     */
    updateInputBoxViaDash(text) {
        try {
            // 使用Dash的全局回调机制
            if (window.dash_clientside && window.dash_clientside.set_props) {
                try {
                    // 直接设置store数据，并带上时间戳确保变化
                    const ts = Date.now();
                    window.dash_clientside.set_props('voice-transcription-store', {
                        data: { text: text, ts }
                    });
                    // 同步镜像到服务端可见的Store，确保触发服务端回调
                    window.dash_clientside.set_props('voice-transcription-store-server', {
                        data: { text: text, ts }
                    });
                    console.log('已通过set_props更新voice-transcription-store 与 -server:', text);
                } catch (setPropsError) {
                    console.error('set_props调用失败:', setPropsError);
                    // 使用备用方案
                    const event = new CustomEvent('voiceTranscriptionComplete', {
                        detail: { text: text }
                    });
                    document.dispatchEvent(event);
                    console.log('已触发语音转录完成事件:', text);
                }
            } else {
                // 使用简单的事件触发
                const event = new CustomEvent('voiceTranscriptionComplete', {
                    detail: { text: text }
                });
                document.dispatchEvent(event);
                console.log('已触发语音转录完成事件:', text);
            }
        } catch (error) {
            console.error('触发Dash回调失败:', error);
            // 备用方案：直接设置DOM值
            this.updateInputBoxDirectly(text);
        }
    }
    
    /**
     * 直接更新输入框（备用方案）
     */
    updateInputBoxDirectly(text) {
        const inputElement = document.getElementById('ai-chat-x-input');
        console.log('查找输入框:', inputElement);
        
        if (inputElement) {
            // 尝试多种方式设置值
            if (inputElement.value !== undefined) {
                inputElement.value = text;
            }
            if (inputElement.textContent !== undefined) {
                inputElement.textContent = text;
            }
            if (inputElement.innerText !== undefined) {
                inputElement.innerText = text;
            }
            
            // 触发输入事件
            inputElement.dispatchEvent(new Event('input', { bubbles: true }));
            inputElement.dispatchEvent(new Event('change', { bubbles: true }));
            inputElement.focus();
            
            console.log('文本已直接填入输入框:', text);
        } else {
            console.error('未找到输入框元素 ai-chat-x-input');
        }
    }
    
    showRecordingWaveform() {
        // 录音聊天：显示音频可视化区域
        const audioVisualizerContainer = document.getElementById('audio-visualizer-container');
        const audioVisualizer = document.getElementById('audio-visualizer');
        
        if (audioVisualizerContainer && audioVisualizer) {
            // 显示音频可视化区域
            audioVisualizerContainer.style.display = 'inline-block';
            console.log('🎨 录音聊天：显示音频可视化区域');
            
            // 初始化增强的音频可视化器
            if (window.enhancedAudioVisualizer) {
                window.enhancedAudioVisualizer.updateState('recording');
                console.log('🎨 录音聊天：更新音频可视化器状态为录音');
            }
            
            // 开始波形动画
            this.startWaveformAnimation(audioVisualizer);
        } else {
            console.warn('音频可视化区域未找到，使用备用方案');
            // 备用方案：创建录音波形容器
            let waveformContainer = document.getElementById('voice-waveform-container');
            if (!waveformContainer) {
                waveformContainer = document.createElement('div');
                waveformContainer.id = 'voice-waveform-container';
                waveformContainer.style.cssText = `
                    position: absolute;
                    top: -60px;
                    left: 0;
                    right: 0;
                    height: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                `;
                
                // 插入到输入容器中
                const inputContainer = document.querySelector('.chat-input-container');
                if (inputContainer) {
                    inputContainer.style.position = 'relative';
                    inputContainer.appendChild(waveformContainer);
                }
            }
            
            // 创建波形画布
            const canvas = document.createElement('canvas');
            canvas.width = 300;
            canvas.height = 40;
            canvas.style.cssText = `
                border-radius: 4px;
                background: rgba(255,255,255,0.1);
            `;
            
            waveformContainer.innerHTML = '';
            waveformContainer.appendChild(canvas);
            
            // 开始波形动画
            this.startWaveformAnimation(canvas);
            
            waveformContainer.style.display = 'flex';
        }
    }
    
    hideRecordingWaveform() {
        // 隐藏音频可视化区域
        const audioVisualizerContainer = document.getElementById('audio-visualizer-container');
        if (audioVisualizerContainer) {
            audioVisualizerContainer.style.display = 'none';
            console.log('🎨 录音聊天：隐藏音频可视化区域');
        }
        
        // 备用方案：隐藏录音波形容器
        const waveformContainer = document.getElementById('voice-waveform-container');
        if (waveformContainer) {
            waveformContainer.style.display = 'none';
        }
    }
    
    startWaveformAnimation(canvas) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        const draw = () => {
            if (!this.isRecording) return;
            
            // 清除画布
            ctx.clearRect(0, 0, width, height);
            
            // 获取音频数据
            if (this.analyser && this.dataArray) {
                this.analyser.getByteFrequencyData(this.dataArray);
                
                // 绘制波形
                const barWidth = width / this.dataArray.length;
                let x = 0;
                
                for (let i = 0; i < this.dataArray.length; i++) {
                    const barHeight = (this.dataArray[i] / 255) * height;
                    
                    // 创建渐变
                    const gradient = ctx.createLinearGradient(0, height, 0, height - barHeight);
                    gradient.addColorStop(0, '#ff6b6b');
                    gradient.addColorStop(0.5, '#4ecdc4');
                    gradient.addColorStop(1, '#45b7d1');
                    
                    ctx.fillStyle = gradient;
                    ctx.fillRect(x, height - barHeight, barWidth - 1, barHeight);
                    
                    x += barWidth;
                }
            }
            
            this.animationId = requestAnimationFrame(draw);
        };
        
        draw();
    }
    
    stopWaveformAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
    
    showProcessingStatus() {
        const waveformContainer = document.getElementById('voice-waveform-container');
        if (waveformContainer) {
            waveformContainer.innerHTML = `
                <div style="color: white; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; border: 2px solid white; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                    正在转换语音...
                </div>
            `;
            
            // 添加旋转动画
            if (!document.getElementById('voice-spin-animation')) {
                const style = document.createElement('style');
                style.id = 'voice-spin-animation';
                style.textContent = `
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);
            }
        }
    }
    
    hideProcessingStatus() {
        this.hideRecordingWaveform();
    }
    
    disableInput() {
        const inputElement = document.getElementById('ai-chat-x-input');
        if (inputElement) {
            inputElement.disabled = true;
            inputElement.style.opacity = '0.6';
        }
    }
    
    enableInput() {
        const inputElement = document.getElementById('ai-chat-x-input');
        if (inputElement) {
            inputElement.disabled = false;
            inputElement.style.opacity = '1';
        }
    }
    
    showError(message) {
        console.error('语音功能错误:', message);
        
        // 使用toast提示而不是alert弹出框
        const currentPath = window.location.pathname;
        const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
        
        if (isChatPage && window.dash_clientside && window.dash_clientside.set_props) {
            // 使用Dash的global-message组件显示toast提示
            window.dash_clientside.set_props('global-message', {
                children: message
            });
            console.log('已发送toast提示:', message);
        } else {
            // 如果不在聊天页面或Dash不可用，使用console.warn
            console.warn('语音功能提示:', message);
        }
    }
}

// 初始化语音录制器
document.addEventListener('DOMContentLoaded', () => {
    console.log('初始化语音录制器...');
    window.voiceRecorder = new VoiceRecorderEnhanced();
    console.log('语音录制器初始化完成:', window.voiceRecorder);
    
    // 延迟检查录音按钮，因为Dash组件可能还没有渲染
    setTimeout(() => {
        const recordButton = document.getElementById('voice-record-button');
        console.log('延迟检查录音按钮元素:', recordButton);
        
        if (recordButton) {
            console.log('录音按钮找到，直接事件绑定完成');
        } else {
            console.warn('录音按钮仍未找到，将在页面完全加载后重试');
            // 使用MutationObserver监听DOM变化
            const observer = new MutationObserver(() => {
                const button = document.getElementById('voice-record-button');
                if (button) {
                    console.log('录音按钮已渲染，停止观察');
                    observer.disconnect();
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }, 1000);
});

// 导出供其他模块使用
// 添加Dash客户端回调函数
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.voiceTranscription = window.dash_clientside.voiceTranscription || {};

// 镜像转录存储的回调函数
window.dash_clientside.voiceTranscription.mirrorTranscriptionStore = function(data) {
    console.log('镜像转录存储回调被触发:', data);
    return data; // 直接返回数据，实现镜像
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceRecorderEnhanced;
}
