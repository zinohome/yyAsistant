/**
 * 语音录音器
 * 处理音频录制、格式转换和发送
 */

class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingStartTime = null;
        this.recordingDuration = 0;
        this.durationInterval = null;
        this.stream = null;
        
        // 音频配置
        this.audioConfig = {
            sampleRate: 16000,
            channels: 1,
            format: 'webm',
            mimeType: 'audio/webm;codecs=opus'
        };
        
        // 事件处理器
        this.onRecordingStart = null;
        this.onRecordingStop = null;
        this.onRecordingError = null;
        this.onDurationUpdate = null;
        this.onAudioData = null;
    }
    
    /**
     * 初始化录音器
     */
    async initialize() {
        try {
            // 请求麦克风权限
            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: this.audioConfig.sampleRate,
                    channelCount: this.audioConfig.channels,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // 检查MediaRecorder支持
            if (!MediaRecorder.isTypeSupported(this.audioConfig.mimeType)) {
                console.warn('不支持的音频格式，使用默认格式');
                this.audioConfig.mimeType = 'audio/webm';
            }
            
            // 创建MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: this.audioConfig.mimeType,
                audioBitsPerSecond: 128000
            });
            
            // 设置事件处理器
            this.setupEventHandlers();
            
            console.log('语音录音器初始化成功');
            return true;
        } catch (error) {
            console.error('语音录音器初始化失败:', error);
            this.handleError(error);
            return false;
        }
    }
    
    /**
     * 设置事件处理器
     */
    setupEventHandlers() {
        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
            }
        };
        
        this.mediaRecorder.onstart = () => {
            console.log('开始录音');
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            this.startDurationTimer();
            
            if (this.onRecordingStart) {
                this.onRecordingStart();
            }
        };
        
        this.mediaRecorder.onstop = () => {
            console.log('停止录音');
            this.isRecording = false;
            this.stopDurationTimer();
            
            if (this.onRecordingStop) {
                this.onRecordingStop();
            }
            
            // 处理录音数据
            this.processRecording();
        };
        
        this.mediaRecorder.onerror = (event) => {
            console.error('录音错误:', event.error);
            this.handleError(event.error);
        };
    }
    
    /**
     * 开始录音
     */
    async startRecording() {
        if (!this.mediaRecorder) {
            const initialized = await this.initialize();
            if (!initialized) {
                return false;
            }
        }
        
        if (this.isRecording) {
            console.warn('已经在录音中');
            return false;
        }
        
        try {
            this.audioChunks = [];
            this.recordingDuration = 0;
            
            // 开始录音
            this.mediaRecorder.start(100); // 每100ms收集一次数据
            
            return true;
        } catch (error) {
            console.error('开始录音失败:', error);
            this.handleError(error);
            return false;
        }
    }
    
    /**
     * 停止录音
     */
    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) {
            console.warn('当前没有在录音');
            return false;
        }
        
        try {
            this.mediaRecorder.stop();
            return true;
        } catch (error) {
            console.error('停止录音失败:', error);
            this.handleError(error);
            return false;
        }
    }
    
    /**
     * 处理录音数据
     */
    async processRecording() {
        if (this.audioChunks.length === 0) {
            console.warn('没有录音数据');
            return;
        }
        
        try {
            // 合并音频数据
            const audioBlob = new Blob(this.audioChunks, {
                type: this.audioConfig.mimeType
            });
            
            console.log('录音完成，音频大小:', audioBlob.size, 'bytes');
            
            // 发送音频数据
            if (this.onAudioData) {
                await this.onAudioData(audioBlob);
            }
            
        } catch (error) {
            console.error('处理录音数据失败:', error);
            this.handleError(error);
        }
    }
    
    /**
     * 开始时长计时器
     */
    startDurationTimer() {
        this.durationInterval = setInterval(() => {
            if (this.recordingStartTime) {
                this.recordingDuration = Date.now() - this.recordingStartTime;
                
                if (this.onDurationUpdate) {
                    this.onDurationUpdate(this.recordingDuration);
                }
            }
        }, 100); // 每100ms更新一次
    }
    
    /**
     * 停止时长计时器
     */
    stopDurationTimer() {
        if (this.durationInterval) {
            clearInterval(this.durationInterval);
            this.durationInterval = null;
        }
    }
    
    /**
     * 格式化时长显示
     */
    formatDuration(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    /**
     * 处理错误
     */
    handleError(error) {
        console.error('语音录音器错误:', error);
        
        if (this.onRecordingError) {
            this.onRecordingError(error);
        }
        
        // 停止录音
        this.stopRecording();
    }
    
    /**
     * 清理资源
     */
    cleanup() {
        this.stopRecording();
        
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingStartTime = null;
        this.recordingDuration = 0;
        
        console.log('语音录音器资源已清理');
    }
    
    /**
     * 获取录音状态
     */
    getRecordingStatus() {
        return {
            isRecording: this.isRecording,
            duration: this.recordingDuration,
            formattedDuration: this.formatDuration(this.recordingDuration),
            audioChunksCount: this.audioChunks.length,
            isInitialized: !!this.mediaRecorder
        };
    }
    
    /**
     * 检查浏览器支持
     */
    static checkBrowserSupport() {
        const support = {
            mediaDevices: !!navigator.mediaDevices,
            getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
            mediaRecorder: !!window.MediaRecorder,
            webm: MediaRecorder.isTypeSupported('audio/webm'),
            opus: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        };
        
        return {
            ...support,
            fullySupported: support.mediaDevices && support.getUserMedia && support.mediaRecorder
        };
    }
}

// 创建全局实例
window.voiceRecorder = new VoiceRecorder();
