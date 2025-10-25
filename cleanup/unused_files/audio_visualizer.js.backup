/**
 * Audio Visualizer for Real-time Voice Chat
 * 
 * Provides real-time audio visualization using Canvas and Web Audio API
 * with frequency spectrum analysis and smooth animations.
 */

class AudioVisualizer {
    constructor(canvasId = 'audio-visualizer') {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.warn(`Canvas element with id '${canvasId}' not found. AudioVisualizer will be disabled.`);
            this.ctx = null;
            this.isActive = false;
            return;
        }
        this.ctx = this.canvas.getContext('2d');
        this.animationId = null;
        this.isActive = false;
        
        // Audio context and analysis
        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.dataArray = null;
        this.bufferLength = 0;
        
        // Visualization settings
        this.settings = {
            barCount: 32,  // 减少条数，让每个条更宽
            barWidth: 0,
            barSpacing: 1,  // 减少间距
            maxBarHeight: 18,  // 适应20px画布高度
            colorGradient: ['#ff6b6b', '#ffa726', '#ffeb3b', '#66bb6a', '#42a5f5'],  // 适合白色背景的明亮颜色
            backgroundColor: '#ffffff',  // 白色背景
            fps: 60,
            smoothing: 0.8
        };
        
        // Animation state
        this.lastFrameTime = 0;
        this.frameInterval = 1000 / this.settings.fps;
        
        // Status text
        this.statusText = '';
        this.statusColor = '#333333';  // 深灰色，适合白色背景
        
        // Initialize
        this.init();
    }
    
    init() {
        if (!this.canvas) {
            console.error('AudioVisualizer: Canvas element not found');
            return;
        }
        
        // Calculate bar dimensions
        this.settings.barWidth = (this.canvas.width - (this.settings.barCount - 1) * this.settings.barSpacing) / this.settings.barCount;
        
        // Set up canvas
        this.ctx.fillStyle = this.settings.backgroundColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制初始化指示器
        this.ctx.fillStyle = '#42a5f5';
        this.ctx.fillRect(10, 8, 60, 4);
        
        // 设置初始状态文字
        this.statusText = '等待开始';
        this.statusColor = '#333333';
        
        console.log('🎨 音频可视化器已初始化:', {
            canvasId: this.canvas.id,
            canvasWidth: this.canvas.width,
            canvasHeight: this.canvas.height,
            hasContext: !!this.ctx
        });
        
        // 立即绘制一次，确保有内容显示
        this.drawVisualization();
        
        // 启动一个简单的动画循环，即使没有音频流
        this.startSimpleAnimation();
    }
    
    async startVisualization(audioStream) {
        try {
            if (!this.canvas || !this.ctx) {
                console.warn('AudioVisualizer: Canvas not available');
                return;
            }
            
            if (this.isActive) {
                console.warn('AudioVisualizer: Already active');
                return;
            }
            
            console.log('🎨 开始音频可视化，音频流:', audioStream);
            
            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Resume audio context if suspended
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
                console.log('🎨 音频上下文已恢复');
            }
            
            // Create analyser node
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = this.settings.smoothing;
            
            // Connect microphone to analyser
            this.microphone = this.audioContext.createMediaStreamSource(audioStream);
            this.microphone.connect(this.analyser);
            
            console.log('🎨 音频流已连接:', {
                audioContextState: this.audioContext.state,
                hasMicrophone: !!this.microphone,
                hasAnalyser: !!this.analyser
            });
            
            // Set up data array
            this.bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(this.bufferLength);
            
            // Start visualization
            this.isActive = true;
            this.startAnimation();
            
            console.log('🎨 音频可视化已启动:', {
                isActive: this.isActive,
                hasAnalyser: !!this.analyser,
                hasMicrophone: !!this.microphone,
                hasDataArray: !!this.dataArray,
                bufferLength: this.bufferLength
            });
            
        } catch (error) {
            console.error('AudioVisualizer: Failed to start visualization:', error);
            this.stopVisualization();
        }
    }
    
    stopVisualization() {
        try {
            this.isActive = false;
            
            // Stop animation
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
                this.animationId = null;
            }
            
            // Disconnect audio nodes
            if (this.microphone) {
                this.microphone.disconnect();
                this.microphone = null;
            }
            
            if (this.analyser) {
                this.analyser.disconnect();
                this.analyser = null;
            }
            
            if (this.audioContext) {
                this.audioContext.close();
                this.audioContext = null;
            }
            
            // Clear canvas
            this.clearCanvas();
            
            console.log('AudioVisualizer: Visualization stopped');
            
        } catch (error) {
            console.error('AudioVisualizer: Error stopping visualization:', error);
        }
    }
    
    startAnimation() {
        if (!this.isActive) return;
        
        const animate = (currentTime) => {
            if (!this.isActive) return;
            
            // Throttle to target FPS
            if (currentTime - this.lastFrameTime >= this.frameInterval) {
                this.drawVisualization();
                this.lastFrameTime = currentTime;
            }
            
            this.animationId = requestAnimationFrame(animate);
        };
        
        this.animationId = requestAnimationFrame(animate);
    }
    
    startSimpleAnimation() {
        // 简单的动画循环，确保有内容显示
        const animate = () => {
            this.drawVisualization();
            this.animationId = requestAnimationFrame(animate);
        };
        
        this.animationId = requestAnimationFrame(animate);
    }
    
    drawVisualization() {
        // Clear canvas
        this.clearCanvas();
        
        // 检查是否有音频数据
        let hasAudioData = false;
        if (this.analyser && this.dataArray) {
            this.analyser.getByteFrequencyData(this.dataArray);
            hasAudioData = !this.dataArray.every(value => value === 0);
        }
        
        // 只在调试模式下输出日志
        if (window.DEBUG_AUDIO_VISUALIZER) {
            console.log('🎨 绘制可视化:', {
                hasAudioData,
                dataArrayLength: this.dataArray ? this.dataArray.length : 0,
                statusText: this.statusText,
                isActive: this.isActive,
                hasAnalyser: !!this.analyser
            });
        }
        
        if (hasAudioData) {
            // 有音频数据时，绘制波形
            this.drawFrequencyBars();
            this.drawWaveform();
            
            // 只在有状态文字时绘制，且使用半透明背景
            if (this.statusText) {
                this.drawStatusTextOverlay();
            }
        } else {
            // 没有音频数据时，显示状态文字和测试指示器
            if (this.statusText) {
                this.drawStatusText();
            } else {
                // 即使没有状态文字，也显示测试指示器
                this.drawTestIndicator();
            }
        }
    }
    
    drawFrequencyBars() {
        const barCount = this.settings.barCount;
        const barWidth = this.settings.barWidth;
        const barSpacing = this.settings.barSpacing;
        const maxHeight = this.settings.maxBarHeight;
        
        for (let i = 0; i < barCount; i++) {
            // Calculate bar height from frequency data
            const dataIndex = Math.floor((i / barCount) * this.bufferLength);
            const frequency = this.dataArray[dataIndex];
            // 增强频率数据，让波形更明显
            const enhancedFrequency = Math.pow(frequency / 255, 0.5) * 255;
            const barHeight = Math.max(2, (enhancedFrequency / 255) * maxHeight); // 最小高度2px
            
            // Calculate position
            const x = i * (barWidth + barSpacing);
            const y = this.canvas.height - barHeight;
            
            // 使用更亮的颜色，不透明度更高
            const colorIndex = Math.floor((enhancedFrequency / 255) * (this.settings.colorGradient.length - 1));
            const color = this.settings.colorGradient[colorIndex];
            
            // 绘制实心条，不使用渐变
            this.ctx.fillStyle = color;
            this.ctx.fillRect(x, y, barWidth, barHeight);
            
            // 添加发光效果，但减少模糊
            this.ctx.shadowColor = color;
            this.ctx.shadowBlur = 3;
            this.ctx.fillRect(x, y, barWidth, barHeight);
            this.ctx.shadowBlur = 0;
        }
    }
    
    drawWaveform() {
        if (!this.analyser) return;
        
        // Get time domain data for waveform
        const waveformData = new Uint8Array(this.analyser.fftSize);
        this.analyser.getByteTimeDomainData(waveformData);
        
        // 绘制更明显的波形
        this.ctx.strokeStyle = '#00ff88';  // 更亮的绿色
        this.ctx.lineWidth = 1.5;  // 稍微细一点，适应小画布
        this.ctx.beginPath();
        
        const sliceWidth = this.canvas.width / waveformData.length;
        let x = 0;
        
        for (let i = 0; i < waveformData.length; i++) {
            const v = waveformData[i] / 128.0;
            // 增强波形幅度，让变化更明显
            const enhancedV = Math.pow(Math.abs(v - 1), 0.7) * (v > 1 ? 1 : -1);
            const y = this.canvas.height / 2 + enhancedV * (this.canvas.height / 2 - 2);
            
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
            
            x += sliceWidth;
        }
        
        this.ctx.stroke();
    }
    
    clearCanvas() {
        this.ctx.fillStyle = this.settings.backgroundColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
        
        // Recalculate bar dimensions if needed
        if (newSettings.barCount) {
            this.settings.barWidth = (this.canvas.width - (this.settings.barCount - 1) * this.settings.barSpacing) / this.settings.barCount;
        }
        
        console.log('AudioVisualizer: Settings updated', this.settings);
    }
    
    getStatus() {
        return {
            isActive: this.isActive,
            hasAudioContext: !!this.audioContext,
            hasAnalyser: !!this.analyser,
            hasMicrophone: !!this.microphone,
            bufferLength: this.bufferLength,
            settings: this.settings
        };
    }
    
    /**
     * 更新状态文字
     */
    updateStatusText(text, color) {
        this.statusText = text;
        // 统一状态颜色方案，与WebSocket管理器保持一致
        this.statusColor = color === 'green' ? '#52c41a' : 
                          color === 'blue' ? '#1890ff' : 
                          color === 'orange' ? '#fa8c16' :
                          color === 'red' ? '#ff4d4f' : 
                          color === 'gray' ? '#8c8c8c' : '#333333';
        console.log('🎨 音频可视化器状态文字已更新:', {text, color});
    }
    
    /**
     * 绘制状态文字
     */
    drawStatusText() {
        if (!this.ctx || !this.statusText) return;
        
        // 设置文字样式 - 使用更大的字体，占满整个高度
        this.ctx.font = '12px Arial';
        this.ctx.fillStyle = this.statusColor;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        // 绘制半透明背景 - 占满整个画布
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';  // 浅色背景，适合白色画布
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制文字 - 居中显示
        this.ctx.fillStyle = this.statusColor;
        this.ctx.fillText(this.statusText, this.canvas.width / 2, this.canvas.height / 2);
    }
    
    /**
     * 绘制半透明状态文字覆盖层（不覆盖波形）
     */
    drawStatusTextOverlay() {
        if (!this.ctx || !this.statusText) return;
        
        // 设置文字样式
        this.ctx.font = '10px Arial';
        this.ctx.fillStyle = this.statusColor;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'bottom';
        
        // 绘制半透明背景 - 只在底部
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';  // 浅色背景，适合白色画布
        this.ctx.fillRect(0, this.canvas.height - 8, this.canvas.width, 8);
        
        // 绘制文字 - 在底部
        this.ctx.fillStyle = this.statusColor;
        this.ctx.fillText(this.statusText, this.canvas.width / 2, this.canvas.height - 2);
    }
    
    /**
     * 绘制测试指示器
     */
    drawTestIndicator() {
        if (!this.ctx) return;
        
        // 绘制一个简单的指示器，适合白色背景
        this.ctx.fillStyle = '#42a5f5';  // 蓝色，适合白色背景
        this.ctx.fillRect(5, 5, 10, 5);
        this.ctx.fillRect(20, 3, 10, 7);
        this.ctx.fillRect(35, 4, 10, 6);
        this.ctx.fillRect(50, 2, 10, 8);
        this.ctx.fillRect(65, 5, 10, 5);
    }
    
    destroy() {
        this.stopVisualization();
        console.log('AudioVisualizer: Destroyed');
    }
}

// Global instance
window.audioVisualizer = null;

// Initialize when DOM is ready with retry mechanism
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing AudioVisualizer...');
    
    const initAudioVisualizer = () => {
        const canvas = document.getElementById('audio-visualizer');
        if (canvas) {
            window.audioVisualizer = new AudioVisualizer();
            console.log('AudioVisualizer ready');
        } else {
            console.log('Canvas not found, retrying in 500ms...');
            setTimeout(initAudioVisualizer, 500);
        }
    };
    
    initAudioVisualizer();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioVisualizer;
}
