/**
 * 增强版语音录制器 - 支持录音波形显示和语音转文本
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
        
        // 录音配置
        this.config = {
            sampleRate: 16000,
            channels: 1,
            bitRate: 128000
        };
        
        // 异步初始化
        this.init().catch(error => {
            console.error('录音器初始化失败:', error);
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
        console.log(`录音器状态变化: ${oldState} → ${newState}`);
        
        // 如果状态变为中断，停止录音
        if (newState === 'interrupted' && this.isRecording) {
            this.stopRecording();
        }
    }
    
    async initWebSocket() {
        try {
            // 使用全局WebSocket管理器，避免重复连接
            if (window.voiceWebSocketManager) {
                // 等待连接建立
                this.websocket = await window.voiceWebSocketManager.waitForConnection();
                if (this.websocket) {
                    console.log('录音器使用共享WebSocket连接');
                    // 通过管理器注册消息处理器，避免共享连接相互覆盖 onmessage
                    try {
                        window.voiceWebSocketManager.registerMessageHandler('transcription_result', (data) => this.handleTranscriptionResult(data));
                        window.voiceWebSocketManager.registerMessageHandler('audio_processing_start', () => this.showProcessingStatus());
                        window.voiceWebSocketManager.registerMessageHandler('error', (data) => {
                            if (data && data.message) this.showError(data.message);
                        });
                    } catch (e) { console.warn('注册录音器消息处理器失败:', e); }
                } else {
                    console.warn('录音器无法获取WebSocket连接');
                }
            } else {
                // 从全局配置获取WebSocket URL
                const wsUrl = window.voiceConfig?.WS_URL || 'ws://192.168.66.209:9800/ws/chat';
                this.websocket = new WebSocket(wsUrl);
                console.log('创建新的WebSocket连接');
                // 仅在独立连接时设置本地 onmessage 处理
                this.setupWebSocketHandlers();
            }
        } catch (error) {
            console.error('初始化WebSocket失败:', error);
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
        // 监听录音按钮点击事件 - 使用新的按钮ID
        document.addEventListener('click', (event) => {
            if (event.target.closest('#voice-record-button')) {
                this.toggleRecording();
            }
        });
    }
    
    async toggleRecording() {
        // 使用状态管理器处理按钮点击，而不是直接切换录音状态
        if (window.voiceStateManager) {
            const handled = window.voiceStateManager.handleButtonClick();
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
        // 检查状态管理器是否允许开始录音
        if (window.voiceStateManager && !window.voiceStateManager.canStartRecording()) {
            console.warn('当前状态不允许开始录音:', window.voiceStateManager.getState());
            return;
        }
        
        try {
            // 更新状态为录音中
            if (window.voiceStateManager) {
                window.voiceStateManager.startRecording();
            }
            
            // 通知统一按钮状态管理器
            if (window.unifiedButtonStateManager) {
                window.unifiedButtonStateManager.startRecording();
            }
            
            // 请求麦克风权限
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: this.config.sampleRate,
                    channelCount: this.config.channels,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
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
                this.processRecording();
            };
            
            // 开始录音
            this.mediaRecorder.start(100); // 每100ms收集一次数据
            this.isRecording = true;
            
            // 显示录音波形
            this.showRecordingWaveform();
            
            // 禁用输入框
            this.disableInput();
            
            console.log('开始录音');
            
        } catch (error) {
            console.error('开始录音失败:', error);
            this.showError('无法访问麦克风，请检查权限设置');
        }
    }
    
    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // 通知统一按钮状态管理器
            if (window.unifiedButtonStateManager) {
                window.unifiedButtonStateManager.stopRecording();
            }
            
            // 停止波形动画
            this.stopWaveformAnimation();
            
            // 隐藏录音波形
            this.hideRecordingWaveform();
            
            // 恢复输入框
            this.enableInput();
            
            // 关闭音频流
            if (this.microphone) {
                this.microphone.disconnect();
            }
            if (this.audioContext) {
                this.audioContext.close();
            }
            
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
            
        } catch (error) {
            console.error('处理录音失败:', error);
            this.showError('语音转文本失败');
        }
    }
    
    async sendAudioForTranscription(audioBlob) {
        return new Promise((resolve, reject) => {
            // 使用 voiceWebSocketManager 检查连接状态，支持自动重连
            if (!window.voiceWebSocketManager || !window.voiceWebSocketManager.isConnected) {
                console.warn('WebSocket未连接，尝试重连...');
                window.voiceWebSocketManager.connect().then(() => {
                    // 重连成功后，延迟一点时间再发送
                    setTimeout(() => {
                        this.sendAudioForTranscription(audioBlob).then(resolve).catch(reject);
                    }, 1000);
                }).catch(() => {
                    reject(new Error('WebSocket连接不可用'));
                });
                return;
            }
            
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
                    if (data && data.message) {
                        this.showError(data.message);
                    } else {
                        console.error('语音WebSocket错误(无详情)');
                    }
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
            // 通知统一按钮状态管理器STT完成
            if (window.unifiedButtonStateManager) {
                window.unifiedButtonStateManager.sttCompleted();
            }
            
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
            
            // 转录失败，重置状态为空闲
            if (window.voiceStateManager) {
                window.voiceStateManager.setState(window.voiceStateManager.STATES.IDLE);
            }
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
        // 创建录音波形容器
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
    
    hideRecordingWaveform() {
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
        // 这里可以显示用户友好的错误提示
        alert(`语音功能错误: ${message}`);
    }
}

// 初始化语音录制器
document.addEventListener('DOMContentLoaded', () => {
    window.voiceRecorder = new VoiceRecorderEnhanced();
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
