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
            barCount: 64,
            barWidth: 0,
            barSpacing: 2,
            maxBarHeight: 150,
            colorGradient: ['#ff0000', '#ff8800', '#ffff00', '#88ff00', '#00ff00'],
            backgroundColor: '#000000',
            fps: 60,
            smoothing: 0.8
        };
        
        // Animation state
        this.lastFrameTime = 0;
        this.frameInterval = 1000 / this.settings.fps;
        
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
        
        console.log('AudioVisualizer initialized');
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
            
            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Create analyser node
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = this.settings.smoothing;
            
            // Connect microphone to analyser
            this.microphone = this.audioContext.createMediaStreamSource(audioStream);
            this.microphone.connect(this.analyser);
            
            // Set up data array
            this.bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(this.bufferLength);
            
            // Start visualization
            this.isActive = true;
            this.startAnimation();
            
            console.log('AudioVisualizer: Visualization started');
            
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
    
    drawVisualization() {
        if (!this.analyser || !this.dataArray) return;
        
        // Get frequency data
        this.analyser.getByteFrequencyData(this.dataArray);
        
        // Clear canvas
        this.clearCanvas();
        
        // Draw frequency bars
        this.drawFrequencyBars();
        
        // Draw waveform overlay
        this.drawWaveform();
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
            const barHeight = (frequency / 255) * maxHeight;
            
            // Calculate position
            const x = i * (barWidth + barSpacing);
            const y = this.canvas.height - barHeight;
            
            // Create gradient
            const gradient = this.ctx.createLinearGradient(0, this.canvas.height, 0, y);
            const colorIndex = Math.floor((frequency / 255) * (this.settings.colorGradient.length - 1));
            const color = this.settings.colorGradient[colorIndex];
            
            gradient.addColorStop(0, color);
            gradient.addColorStop(1, color + '80'); // Add transparency
            
            // Draw bar
            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(x, y, barWidth, barHeight);
            
            // Add glow effect
            this.ctx.shadowColor = color;
            this.ctx.shadowBlur = 10;
            this.ctx.fillRect(x, y, barWidth, barHeight);
            this.ctx.shadowBlur = 0;
        }
    }
    
    drawWaveform() {
        if (!this.analyser) return;
        
        // Get time domain data for waveform
        const waveformData = new Uint8Array(this.analyser.fftSize);
        this.analyser.getByteTimeDomainData(waveformData);
        
        // Draw waveform
        this.ctx.strokeStyle = '#00ff00';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        
        const sliceWidth = this.canvas.width / waveformData.length;
        let x = 0;
        
        for (let i = 0; i < waveformData.length; i++) {
            const v = waveformData[i] / 128.0;
            const y = v * this.canvas.height / 2;
            
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
