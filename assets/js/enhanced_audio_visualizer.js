/**
 * 增强的音频可视化器
 * 提供丰富的状态指示和动画效果
 */
class EnhancedAudioVisualizer {
    constructor() {
        this.canvas = document.getElementById('audio-visualizer');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.currentState = 'idle';
        this.animationId = null;
        this.progress = 0;
        
        // 状态配置
        this.stateConfigs = {
            'idle': { 
                color: '#d9d9d9', 
                pattern: 'static',
                text: '就绪'
            },
            'listening': { 
                color: '#52c41a', 
                pattern: 'pulse',
                text: '聆听中'
            },
            'processing': { 
                color: '#faad14', 
                pattern: 'progress',
                text: '处理中'
            },
            'speaking': { 
                color: '#1890ff', 
                pattern: 'wave',
                text: '播放中'
            },
            'error': { 
                color: '#ff4d4f', 
                pattern: 'error',
                text: '错误'
            }
        };
        
        this.init();
    }
    
    init() {
        // 延迟初始化，等待容器显示
        this.initializeWhenReady();
    }
    
    initializeWhenReady() {
        this.canvas = document.getElementById('audio-visualizer');
        if (this.canvas) {
            this.initCanvas();
            console.log('🎨 音频可视化Canvas已找到并初始化');
        } else {
            console.warn('音频可视化Canvas未找到，将在显示时初始化');
            // 设置重试机制
            this.retryCount = 0;
            this.maxRetries = 10;
            this.retryInitialization();
        }
    }
    
    retryInitialization() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            setTimeout(() => {
                this.canvas = document.getElementById('audio-visualizer');
                if (this.canvas) {
                    this.initCanvas();
                    console.log('🎨 音频可视化Canvas已找到并初始化（重试成功）');
                } else {
                    console.log(`🎨 音频可视化Canvas重试 ${this.retryCount}/${this.maxRetries}`);
                    this.retryInitialization();
                }
            }, 500);
        } else {
            console.warn('🎨 音频可视化Canvas重试次数已达上限，将在显示时自动初始化');
        }
    }
    
    initCanvas() {
        // 设置Canvas尺寸
        this.canvas.width = 80;
        this.canvas.height = 20;
        
        // 初始化状态
        this.updateState('idle');
    }
    
    updateState(state, progress = 0) {
        if (!this.canvas || !this.ctx) {
            return;
        }
        
        if (this.currentState === state && this.progress === progress) {
            return; // 避免重复更新
        }
        
        this.currentState = state;
        this.progress = progress;
        
        this.clearCanvas();
        this.drawVisualization();
        
        console.log(`🎨 音频可视化状态更新: ${state} (${progress}%)`);
    }
    
    clearCanvas() {
        if (this.ctx) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }
    
    drawVisualization() {
        const config = this.stateConfigs[this.currentState] || this.stateConfigs['idle'];
        
        switch(config.pattern) {
            case 'pulse':
                this.drawPulseAnimation(config.color);
                break;
            case 'progress':
                this.drawProgressBar(config.color, this.progress);
                break;
            case 'wave':
                this.drawWaveAnimation(config.color);
                break;
            case 'error':
                this.drawErrorIndicator(config.color);
                break;
            default:
                this.drawStaticIndicator(config.color);
        }
    }
    
    drawPulseAnimation(color) {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = 6;
        const time = Date.now() * 0.005;
        
        // 主圆
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        this.ctx.fillStyle = color;
        this.ctx.fill();
        
        // 脉冲效果
        const pulseRadius = radius + Math.sin(time) * 2;
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, pulseRadius, 0, 2 * Math.PI);
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 1;
        this.ctx.globalAlpha = 0.3;
        this.ctx.stroke();
        this.ctx.globalAlpha = 1;
        
        // 启动动画
        if (!this.animationId) {
            this.startAnimation();
        }
    }
    
    drawProgressBar(color, progress) {
        const barWidth = this.canvas.width - 4;
        const barHeight = 4;
        const x = 2;
        const y = (this.canvas.height - barHeight) / 2;
        
        // 背景
        this.ctx.fillStyle = '#f0f0f0';
        this.ctx.fillRect(x, y, barWidth, barHeight);
        
        // 进度条
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x, y, barWidth * (progress / 100), barHeight);
        
        // 进度文字
        this.ctx.fillStyle = color;
        this.ctx.font = '10px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(`${Math.round(progress)}%`, this.canvas.width / 2, this.canvas.height - 2);
    }
    
    drawWaveAnimation(color) {
        const centerY = this.canvas.height / 2;
        const time = Date.now() * 0.01;
        
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        
        for (let x = 0; x < this.canvas.width; x += 2) {
            const y = centerY + Math.sin((x * 0.1) + time) * 3;
            if (x === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        
        this.ctx.stroke();
        
        // 启动动画
        if (!this.animationId) {
            this.startAnimation();
        }
    }
    
    drawErrorIndicator(color) {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const size = 6;
        
        // 绘制X形状
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(centerX - size, centerY - size);
        this.ctx.lineTo(centerX + size, centerY + size);
        this.ctx.moveTo(centerX + size, centerY - size);
        this.ctx.lineTo(centerX - size, centerY + size);
        this.ctx.stroke();
    }
    
    drawStaticIndicator(color) {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = 4;
        
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        this.ctx.fillStyle = color;
        this.ctx.fill();
    }
    
    startAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        const animate = () => {
            this.clearCanvas();
            this.drawVisualization();
            this.animationId = requestAnimationFrame(animate);
        };
        
        this.animationId = requestAnimationFrame(animate);
    }
    
    stopAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
    
    destroy() {
        this.stopAnimation();
        this.clearCanvas();
    }
}

// 全局实例
window.enhancedAudioVisualizer = null;

// 初始化函数
function initEnhancedAudioVisualizer() {
    if (window.enhancedAudioVisualizer) {
        window.enhancedAudioVisualizer.destroy();
    }
    
    window.enhancedAudioVisualizer = new EnhancedAudioVisualizer();
    console.log('🎨 增强音频可视化器已初始化');
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEnhancedAudioVisualizer);
} else {
    // DOM已经加载完成，延迟一点时间确保所有元素都已渲染
    setTimeout(initEnhancedAudioVisualizer, 200);
}

// 添加全局初始化函数，供外部调用
window.initEnhancedAudioVisualizer = initEnhancedAudioVisualizer;

