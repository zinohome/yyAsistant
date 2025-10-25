/**
 * 微信浏览器兼容性处理
 * 解决微信内置浏览器的各种限制和问题
 */

class WeChatCompatibility {
    constructor() {
        this.isWeChat = this.detectWeChat();
        this.isSupported = this.checkSupport();
        this.fallbackMode = false;
    }

    /**
     * 检测是否为微信浏览器
     */
    detectWeChat() {
        const ua = navigator.userAgent.toLowerCase();
        return ua.includes('micromessenger');
    }

    /**
     * 检查微信浏览器支持情况
     */
    checkSupport() {
        if (!this.isWeChat) {
            return true; // 非微信浏览器，正常支持
        }

        const issues = [];
        
        // 检查WebRTC支持
        if (!this.checkWebRTCSupport()) {
            issues.push('WebRTC支持有限');
        }

        // 检查音频API支持
        if (!this.checkAudioAPISupport()) {
            issues.push('音频API支持有限');
        }

        // 检查WebSocket支持
        if (!this.checkWebSocketSupport()) {
            issues.push('WebSocket支持有限');
        }

        if (issues.length > 0) {
            console.warn('微信浏览器兼容性问题:', issues);
            this.fallbackMode = true;
            return false;
        }

        return true;
    }

    /**
     * 检查WebRTC支持
     */
    checkWebRTCSupport() {
        return !!(navigator.mediaDevices && 
                 navigator.mediaDevices.getUserMedia &&
                 (window.RTCPeerConnection || window.webkitRTCPeerConnection));
    }

    /**
     * 检查音频API支持
     */
    checkAudioAPISupport() {
        return !!(window.AudioContext || window.webkitAudioContext);
    }

    /**
     * 检查WebSocket支持
     */
    checkWebSocketSupport() {
        return typeof WebSocket !== 'undefined';
    }

    /**
     * 获取兼容性建议
     */
    getCompatibilityAdvice() {
        if (!this.isWeChat) {
            return null;
        }

        const advice = [];
        
        if (!this.checkWebRTCSupport()) {
            advice.push('建议使用Chrome、Safari等现代浏览器获得最佳体验');
        }

        if (!this.checkAudioAPISupport()) {
            advice.push('语音功能可能受限，建议使用其他浏览器');
        }

        if (!this.checkWebSocketSupport()) {
            advice.push('实时通信功能可能受限');
        }

        return advice;
    }

    /**
     * 应用兼容性修复
     */
    applyFixes() {
        if (!this.isWeChat) {
            return;
        }

        // 修复1: 禁用某些高级功能
        this.disableAdvancedFeatures();

        // 修复2: 优化内存使用
        this.optimizeMemoryUsage();

        // 修复3: 调整音频处理
        this.adjustAudioProcessing();

        // 修复4: 优化WebSocket连接
        this.optimizeWebSocketConnection();
    }

    /**
     * 禁用高级功能
     */
    disableAdvancedFeatures() {
        // 禁用实时语音功能
        if (window.voiceConfig) {
            window.voiceConfig.ENABLE_REALTIME_VOICE = false;
        }

        // 禁用某些音频效果
        if (window.audioConfig) {
            window.audioConfig.ENABLE_AUDIO_EFFECTS = false;
        }
    }

    /**
     * 优化内存使用
     */
    optimizeMemoryUsage() {
        // 减少音频缓冲区大小
        if (window.audioConfig) {
            window.audioConfig.BUFFER_SIZE = 1024; // 减小缓冲区
            window.audioConfig.MAX_BUFFERS = 2; // 减少最大缓冲区数量
        }

        // 启用内存清理
        setInterval(() => {
            if (window.gc) {
                window.gc();
            }
        }, 30000); // 每30秒清理一次
    }

    /**
     * 调整音频处理
     */
    adjustAudioProcessing() {
        // 使用更简单的音频处理
        if (window.audioConfig) {
            window.audioConfig.USE_SIMPLE_PROCESSING = true;
            window.audioConfig.SAMPLE_RATE = 16000; // 降低采样率
            window.audioConfig.CHANNELS = 1; // 单声道
        }
    }

    /**
     * 优化WebSocket连接
     */
    optimizeWebSocketConnection() {
        // 增加重连间隔
        if (window.websocketConfig) {
            window.websocketConfig.RECONNECT_INTERVAL = 5000; // 5秒
            window.websocketConfig.MAX_RECONNECT_ATTEMPTS = 3; // 减少重连次数
        }
    }

    /**
     * 显示兼容性提示
     */
    showCompatibilityNotice() {
        if (!this.isWeChat || this.isSupported) {
            return;
        }

        const advice = this.getCompatibilityAdvice();
        if (advice && advice.length > 0) {
            const notice = document.createElement('div');
            notice.className = 'wechat-compatibility-notice';
            notice.innerHTML = `
                <div style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    padding: 10px;
                    z-index: 10000;
                    font-size: 14px;
                    text-align: center;
                ">
                    <strong>微信浏览器兼容性提示：</strong>
                    ${advice.join('；')}
                    <button onclick="this.parentElement.style.display='none'" style="margin-left: 10px;">关闭</button>
                </div>
            `;
            document.body.appendChild(notice);
        }
    }

    /**
     * 初始化兼容性处理
     */
    init() {
        if (this.isWeChat) {
            console.log('检测到微信浏览器，应用兼容性处理');
            this.applyFixes();
            this.showCompatibilityNotice();
        }
    }
}

// 全局兼容性管理器
window.wechatCompatibility = new WeChatCompatibility();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    window.wechatCompatibility.init();
});

// 导出兼容性检查函数
window.checkWeChatCompatibility = function() {
    return window.wechatCompatibility.isSupported;
};

window.getWeChatCompatibilityAdvice = function() {
    return window.wechatCompatibility.getCompatibilityAdvice();
};
