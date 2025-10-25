/**
 * 增强的播放状态指示器
 * 提供丰富的状态信息和交互功能
 */
class EnhancedPlaybackStatus {
    constructor() {
        this.container = null;
        this.stateHistory = [];
        this.retryAttempts = 0;
        this.maxRetries = 3;
        
        // 状态配置
        this.stateConfigs = {
            'connecting': { 
                icon: '🔄', 
                color: '#1890ff', 
                bgColor: '#e6f7ff',
                message: '连接语音服务...'
            },
            'listening': { 
                icon: '🎤', 
                color: '#52c41a', 
                bgColor: '#f6ffed',
                message: '正在聆听...'
            },
            'processing': { 
                icon: '⚡', 
                color: '#faad14', 
                bgColor: '#fffbe6',
                message: 'AI思考中...'
            },
            'speaking': { 
                icon: '🔊', 
                color: '#1890ff', 
                bgColor: '#e6f7ff',
                message: '播放回复中...'
            },
            'error': { 
                icon: '❌', 
                color: '#ff4d4f', 
                bgColor: '#fff2f0',
                message: '语音服务异常'
            },
            'retrying': { 
                icon: '🔄', 
                color: '#faad14', 
                bgColor: '#fffbe6',
                message: '重新连接中...'
            }
        };
    }
    
    showStatus(state, customMessage = null, options = {}) {
        if (!this.container) {
            this.createContainer();
        }
        
        const config = this.stateConfigs[state] || this.stateConfigs['error'];
        const message = customMessage || config.message;
        
        this.updateDisplay(config, message, options);
        this.recordState(state, message);
        
        console.log(`🔊 播放状态更新: ${state} - ${message}`);
    }
    
    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'enhanced-playback-status';
        this.container.style.cssText = `
            position: fixed;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10000;
            background: white;
            border: 1px solid #d9d9d9;
            border-radius: 8px;
            padding: 8px 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: none;
            align-items: center;
            gap: 8px;
            min-width: 200px;
            max-width: 400px;
            transition: all 0.3s ease;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        document.body.appendChild(this.container);
    }
    
    updateDisplay(config, message, options) {
        const { icon, color, bgColor } = config;
        
        this.container.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                <div style="color: ${color}; font-size: 16px; flex-shrink: 0;">${icon}</div>
                <div style="flex: 1; color: #333; font-size: 14px; line-height: 1.4;">${message}</div>
                ${options.showProgress ? this.createProgressBar() : ''}
                ${options.showRetry ? this.createRetryButton() : ''}
                ${options.showCancel ? this.createCancelButton() : ''}
            </div>
        `;
        
        this.container.style.backgroundColor = bgColor;
        this.container.style.borderColor = color;
        this.container.style.display = 'flex';
        
        // 显示动画
        setTimeout(() => {
            this.container.style.opacity = '1';
            this.container.style.transform = 'translateX(-50%) translateY(0)';
        }, 100);
    }
    
    createProgressBar() {
        return `
            <div style="flex: 1; height: 4px; background: #f0f0f0; border-radius: 2px; overflow: hidden; margin: 0 8px;">
                <div class="progress-fill" style="
                    height: 100%; 
                    background: linear-gradient(90deg, #1890ff, #40a9ff); 
                    width: 0%; 
                    transition: width 0.3s ease;
                    border-radius: 2px;
                "></div>
            </div>
        `;
    }
    
    createRetryButton() {
        return `
            <button onclick="window.enhancedPlaybackStatus.retryOperation()" style="
                background: #ff4d4f; 
                color: white; 
                border: none; 
                padding: 4px 8px; 
                border-radius: 4px; 
                font-size: 12px;
                cursor: pointer;
                transition: background 0.2s ease;
            " onmouseover="this.style.background='#ff7875'" onmouseout="this.style.background='#ff4d4f'">
                重试
            </button>
        `;
    }
    
    createCancelButton() {
        return `
            <button onclick="window.enhancedPlaybackStatus.cancelOperation()" style="
                background: #f5f5f5; 
                color: #666; 
                border: 1px solid #d9d9d9; 
                padding: 4px 8px; 
                border-radius: 4px; 
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s ease;
            " onmouseover="this.style.background='#e6f7ff'; this.style.borderColor='#1890ff'" onmouseout="this.style.background='#f5f5f5'; this.style.borderColor='#d9d9d9'">
                取消
            </button>
        `;
    }
    
    updateProgress(progress) {
        if (!this.container) return;
        
        const progressBar = this.container.querySelector('.progress-fill');
        if (progressBar) {
            progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
        }
    }
    
    retryOperation() {
        this.retryAttempts++;
        
        if (this.retryAttempts <= this.maxRetries) {
            this.showStatus('retrying', `重试中... (${this.retryAttempts}/${this.maxRetries})`, {
                showProgress: true
            });
            
            // 触发重试事件
            this.triggerRetryEvent();
        } else {
            this.showStatus('error', '重试次数已达上限，请稍后再试', {
                showRetry: false
            });
        }
    }
    
    cancelOperation() {
        this.hide();
        
        // 触发取消事件
        this.triggerCancelEvent();
    }
    
    triggerRetryEvent() {
        const event = new CustomEvent('playbackStatusRetry', {
            detail: { attempts: this.retryAttempts }
        });
        document.dispatchEvent(event);
    }
    
    triggerCancelEvent() {
        const event = new CustomEvent('playbackStatusCancel', {
            detail: { timestamp: Date.now() }
        });
        document.dispatchEvent(event);
    }
    
    recordState(state, message) {
        this.stateHistory.push({
            state: state,
            message: message,
            timestamp: Date.now()
        });
        
        // 保持历史记录在合理范围内
        if (this.stateHistory.length > 10) {
            this.stateHistory.shift();
        }
    }
    
    hide() {
        if (this.container) {
            this.container.style.opacity = '0';
            this.container.style.transform = 'translateX(-50%) translateY(-10px)';
            
            setTimeout(() => {
                this.container.style.display = 'none';
            }, 300);
        }
    }
    
    destroy() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        this.container = null;
        this.stateHistory = [];
    }
}

// 全局实例
window.enhancedPlaybackStatus = null;

// 初始化函数
function initEnhancedPlaybackStatus() {
    if (window.enhancedPlaybackStatus) {
        window.enhancedPlaybackStatus.destroy();
    }
    
    window.enhancedPlaybackStatus = new EnhancedPlaybackStatus();
    console.log('🔊 增强播放状态指示器已初始化');
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEnhancedPlaybackStatus);
} else {
    // DOM已经加载完成，延迟一点时间确保所有元素都已渲染
    setTimeout(initEnhancedPlaybackStatus, 200);
}

