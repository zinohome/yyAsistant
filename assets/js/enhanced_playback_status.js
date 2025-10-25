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
        
        // 只在调试模式下显示状态更新日志
        if (window.DEBUG_UI_OPTIMIZATION) {
            console.log(`🔊 播放状态更新: ${state} - ${message}`);
        }
    }
    
    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'enhanced-playback-status';
        // 使用 voice_player_enhanced.js 的漂亮样式
        this.container.style.cssText = `
            position: fixed;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 20px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 10000;
            box-shadow: 0 4px 16px rgba(24, 144, 255, 0.4);
            opacity: 0;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            font-weight: 500;
            min-width: 200px;
            max-width: 400px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        document.body.appendChild(this.container);
    }
    
    updateDisplay(config, message, options) {
        const { icon, color, bgColor } = config;
        
        // 使用 voice_player_enhanced.js 的样式风格
        this.container.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px; width: 100%;">
                <div style="width: 16px; height: 16px; border: 2px solid white; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; flex-shrink: 0;"></div>
                <div style="flex: 1; color: white; font-size: 14px; line-height: 1.4; font-weight: 600; letter-spacing: 0.5px;">${message}</div>
                ${options.showProgress ? this.createProgressBar() : ''}
                ${options.showRetry ? this.createRetryButton() : ''}
                ${options.showCancel ? this.createCancelButton() : ''}
            </div>
        `;
        
        // 保持渐变背景，不改变背景色
        this.container.style.display = 'flex';
        
        // 显示动画
        setTimeout(() => {
            this.container.style.opacity = '1';
            this.container.style.transform = 'translateX(-50%) translateY(0)';
        }, 100);
        
        // 添加旋转动画样式
        this.addSpinAnimation();
    }
    
    addSpinAnimation() {
        // 添加旋转动画样式（如果还没有添加）
        if (!document.getElementById('enhanced-playback-spin-animation')) {
            const style = document.createElement('style');
            style.id = 'enhanced-playback-spin-animation';
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
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
            // 使用 voice_player_enhanced.js 的淡出动画
            this.container.style.opacity = '0';
            
            setTimeout(() => {
                if (this.container && this.container.parentNode) {
                    this.container.parentNode.removeChild(this.container);
                }
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
    
    /**
     * 启用紧凑模式
     */
    setCompactMode(enabled) {
        if (this.container) {
            if (enabled) {
                this.container.style.padding = '8px 16px';
                this.container.style.fontSize = '12px';
                this.container.style.minWidth = '150px';
            } else {
                this.container.style.padding = '12px 20px';
                this.container.style.fontSize = '14px';
                this.container.style.minWidth = '200px';
            }
        }
    }
    
    /**
     * 启用宽松模式
     */
    setSpaciousMode(enabled) {
        if (this.container) {
            if (enabled) {
                this.container.style.padding = '16px 24px';
                this.container.style.fontSize = '16px';
                this.container.style.minWidth = '250px';
            } else {
                this.container.style.padding = '12px 20px';
                this.container.style.fontSize = '14px';
                this.container.style.minWidth = '200px';
            }
        }
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

