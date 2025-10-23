/**
 * 实时语音音频处理器
 * 处理音频捕获、处理和发送
 */

class RealtimeAudioProcessor {
    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.analyser = null;
        this.dataArray = null;
        this.isCapturing = false;
        this.sampleRate = 24000;
        this.channelCount = 1;
        this.bufferSize = 4096;
        this.audioBuffer = [];
        this.visualizationCallback = null;
        this.speechDetectionCallback = null;
        this.speechThreshold = 0.01;
        this.silenceDuration = 1000; // 1秒
        this.lastSpeechTime = 0;
        this.isSpeaking = false;
    }
    
    /**
     * 开始音频捕获
     */
    async startCapture() {
        try {
            console.log('开始音频捕获...');
            
            // 1. 获取麦克风权限
            await this.getUserMedia();
            
            // 2. 创建音频上下文
            this.createAudioContext();
            
            // 3. 设置音频分析
            this.setupAudioAnalysis();
            
            // 4. 开始音频处理循环
            this.startAudioProcessing();
            
            this.isCapturing = true;
            console.log('音频捕获已启动');
            
        } catch (error) {
            console.error('启动音频捕获失败:', error);
            throw error;
        }
    }
    
    /**
     * 获取用户媒体流
     */
    async getUserMedia() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: this.sampleRate,
                    channelCount: this.channelCount,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            console.log('麦克风权限获取成功');
            
        } catch (error) {
            console.error('获取麦克风权限失败:', error);
            throw new Error('无法访问麦克风，请检查权限设置');
        }
    }
    
    /**
     * 创建音频上下文
     */
    createAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: this.sampleRate
            });
            
            // 创建分析器
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = this.bufferSize;
            this.analyser.smoothingTimeConstant = 0.8;
            
            // 创建数据数组
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            
            // 连接音频流
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            source.connect(this.analyser);
            
            console.log('音频上下文创建成功');
            
        } catch (error) {
            console.error('创建音频上下文失败:', error);
            throw error;
        }
    }
    
    /**
     * 设置音频分析
     */
    setupAudioAnalysis() {
        // 设置音频分析参数
        this.analyser.minDecibels = -90;
        this.analyser.maxDecibels = -10;
    }
    
    /**
     * 开始音频处理循环
     */
    startAudioProcessing() {
        const processAudio = () => {
            if (this.isCapturing) {
                this.analyser.getByteFrequencyData(this.dataArray);
                
                // 计算音频级别
                const audioLevel = this.calculateAudioLevel();
                
                // 语音活动检测
                this.detectSpeechActivity(audioLevel);
                
                // 可视化回调
                if (this.visualizationCallback) {
                    this.visualizationCallback(audioLevel, this.dataArray);
                }
                
                // 继续处理
                requestAnimationFrame(processAudio);
            }
        };
        
        processAudio();
    }
    
    /**
     * 计算音频级别
     */
    calculateAudioLevel() {
        let sum = 0;
        for (let i = 0; i < this.dataArray.length; i++) {
            sum += this.dataArray[i];
        }
        return sum / this.dataArray.length / 255;
    }
    
    /**
     * 语音活动检测
     */
    detectSpeechActivity(audioLevel) {
        const now = Date.now();
        const isCurrentlySpeaking = audioLevel > this.speechThreshold;
        
        if (isCurrentlySpeaking) {
            this.lastSpeechTime = now;
            
            if (!this.isSpeaking) {
                this.isSpeaking = true;
                console.log('检测到语音活动');
                if (this.speechDetectionCallback) {
                    this.speechDetectionCallback('start');
                }
            }
        } else {
            // 检查是否已经静音足够长时间
            if (this.isSpeaking && (now - this.lastSpeechTime) > this.silenceDuration) {
                this.isSpeaking = false;
                console.log('语音活动结束');
                if (this.speechDetectionCallback) {
                    this.speechDetectionCallback('stop');
                }
            }
        }
    }
    
    /**
     * 获取音频数据
     */
    getAudioData() {
        if (!this.analyser || !this.dataArray) {
            return null;
        }
        
        this.analyser.getByteFrequencyData(this.dataArray);
        return new Uint8Array(this.dataArray);
    }
    
    /**
     * 获取音频缓冲区数据
     */
    getAudioBufferData() {
        if (!this.audioContext) {
            return null;
        }
        
        // 这里可以实现更复杂的音频缓冲区处理
        // 暂时返回简单的音频数据
        return this.getAudioData();
    }
    
    /**
     * 设置可视化回调
     */
    setVisualizationCallback(callback) {
        this.visualizationCallback = callback;
    }
    
    /**
     * 设置语音检测回调
     */
    setSpeechDetectionCallback(callback) {
        this.speechDetectionCallback = callback;
    }
    
    /**
     * 设置语音检测阈值
     */
    setSpeechThreshold(threshold) {
        this.speechThreshold = threshold;
    }
    
    /**
     * 设置静音持续时间
     */
    setSilenceDuration(duration) {
        this.silenceDuration = duration;
    }
    
    /**
     * 检查是否正在说话
     */
    isCurrentlySpeaking() {
        return this.isSpeaking;
    }
    
    /**
     * 获取音频级别
     */
    getAudioLevel() {
        if (!this.analyser || !this.dataArray) {
            return 0;
        }
        
        this.analyser.getByteFrequencyData(this.dataArray);
        return this.calculateAudioLevel();
    }
    
    /**
     * 停止音频捕获
     */
    stopCapture() {
        try {
            console.log('停止音频捕获...');
            
            this.isCapturing = false;
            
            // 停止媒体流
            if (this.mediaStream) {
                this.mediaStream.getTracks().forEach(track => track.stop());
                this.mediaStream = null;
            }
            
            // 关闭音频上下文
            if (this.audioContext) {
                this.audioContext.close();
                this.audioContext = null;
            }
            
            // 清理分析器
            this.analyser = null;
            this.dataArray = null;
            
            console.log('音频捕获已停止');
            
        } catch (error) {
            console.error('停止音频捕获失败:', error);
        }
    }
    
    /**
     * 清理资源
     */
    cleanup() {
        this.stopCapture();
        this.visualizationCallback = null;
        this.speechDetectionCallback = null;
        this.audioBuffer = [];
    }
    
    /**
     * 检查浏览器支持
     */
    static isSupported() {
        const hasAPIs = !!(navigator.mediaDevices &&
                 navigator.mediaDevices.getUserMedia &&
                 (window.AudioContext || window.webkitAudioContext));
        // 在非安全上下文中，大多数浏览器不提供getUserMedia
        const isLocalhost = window.appConfig?.isLocalhost() || ['localhost', '127.0.0.1', '::1'].includes(location.hostname);
        const secureOK = (window.isSecureContext === true) || isLocalhost;
        return hasAPIs && secureOK;
    }

    /**
     * 返回不支持的原因（用于用户提示）
     */
    static getUnsupportedReason() {
        const reasons = [];
        if (!(window.AudioContext || window.webkitAudioContext)) {
            reasons.push('缺少 AudioContext 支持');
        }
        if (!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) {
            reasons.push('缺少麦克风 API (getUserMedia) 支持');
        }
        const isLocalhost = window.appConfig?.isLocalhost() || ['localhost', '127.0.0.1', '::1'].includes(location.hostname);
        if (!(window.isSecureContext === true) && !isLocalhost) {
            reasons.push('页面未通过 HTTPS 或 localhost 提供，浏览器禁止麦克风访问');
        }
        return reasons.join('；');
    }
    
    /**
     * 获取支持的音频格式
     */
    static getSupportedFormats() {
        return {
            sampleRate: [8000, 16000, 24000, 44100, 48000],
            channelCount: [1, 2],
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
        };
    }
}

// 导出类
window.RealtimeAudioProcessor = RealtimeAudioProcessor;
