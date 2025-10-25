/**
 * 微信浏览器调试工具
 * 帮助诊断和解决微信浏览器中的问题
 */

class WeChatDebugger {
    constructor() {
        this.isWeChat = this.detectWeChat();
        this.debugInfo = {};
        this.issues = [];
    }

    /**
     * 检测微信浏览器
     */
    detectWeChat() {
        const ua = navigator.userAgent.toLowerCase();
        return ua.includes('micromessenger');
    }

    /**
     * 收集调试信息
     */
    collectDebugInfo() {
        this.debugInfo = {
            userAgent: navigator.userAgent,
            isWeChat: this.isWeChat,
            isSecureContext: window.isSecureContext,
            protocol: window.location.protocol,
            hostname: window.location.hostname,
            features: this.checkFeatures(),
            performance: this.checkPerformance(),
            memory: this.checkMemory(),
            errors: this.collectErrors()
        };

        return this.debugInfo;
    }

    /**
     * 检查功能支持
     */
    checkFeatures() {
        return {
            webSocket: typeof WebSocket !== 'undefined',
            audioContext: !!(window.AudioContext || window.webkitAudioContext),
            mediaRecorder: typeof MediaRecorder !== 'undefined',
            getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
            webRTC: !!(window.RTCPeerConnection || window.webkitRTCPeerConnection),
            localStorage: typeof Storage !== 'undefined',
            sessionStorage: typeof Storage !== 'undefined',
            indexedDB: typeof indexedDB !== 'undefined'
        };
    }

    /**
     * 检查性能指标
     */
    checkPerformance() {
        const perf = {
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            } : null,
            hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
            deviceMemory: navigator.deviceMemory || 'unknown'
        };

        return perf;
    }

    /**
     * 检查内存使用
     */
    checkMemory() {
        if (performance.memory) {
            return {
                usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                jsHeapSizeLimit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
            };
        }
        return null;
    }

    /**
     * 收集错误信息
     */
    collectErrors() {
        const errors = [];
        
        // 监听全局错误
        window.addEventListener('error', (event) => {
            errors.push({
                type: 'error',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                timestamp: Date.now()
            });
        });

        // 监听Promise错误
        window.addEventListener('unhandledrejection', (event) => {
            errors.push({
                type: 'unhandledrejection',
                reason: event.reason,
                timestamp: Date.now()
            });
        });

        return errors;
    }

    /**
     * 诊断问题
     */
    diagnose() {
        this.issues = [];

        // 检查HTTPS
        if (!window.isSecureContext && window.location.hostname !== 'localhost') {
            this.issues.push({
                type: 'security',
                severity: 'high',
                message: '非安全上下文，可能影响某些功能',
                solution: '请使用HTTPS访问'
            });
        }

        // 检查功能支持
        const features = this.checkFeatures();
        if (!features.webSocket) {
            this.issues.push({
                type: 'feature',
                severity: 'critical',
                message: 'WebSocket不支持',
                solution: '请使用现代浏览器'
            });
        }

        if (!features.audioContext) {
            this.issues.push({
                type: 'feature',
                severity: 'high',
                message: 'AudioContext不支持，语音功能受限',
                solution: '请使用Chrome、Safari等现代浏览器'
            });
        }

        if (!features.getUserMedia) {
            this.issues.push({
                type: 'feature',
                severity: 'high',
                message: 'getUserMedia不支持，无法使用麦克风',
                solution: '请使用HTTPS访问并允许麦克风权限'
            });
        }

        // 检查内存
        const memory = this.checkMemory();
        if (memory && memory.usedJSHeapSize > 50) {
            this.issues.push({
                type: 'performance',
                severity: 'medium',
                message: '内存使用较高，可能影响性能',
                solution: '请关闭其他标签页或重启浏览器'
            });
        }

        return this.issues;
    }

    /**
     * 生成调试报告
     */
    generateReport() {
        this.collectDebugInfo();
        this.diagnose();

        const report = {
            timestamp: new Date().toISOString(),
            debugInfo: this.debugInfo,
            issues: this.issues,
            recommendations: this.getRecommendations()
        };

        return report;
    }

    /**
     * 获取建议
     */
    getRecommendations() {
        const recommendations = [];

        if (this.isWeChat) {
            recommendations.push('检测到微信浏览器，建议使用Chrome、Safari等现代浏览器获得最佳体验');
        }

        if (!window.isSecureContext) {
            recommendations.push('请使用HTTPS访问以获得完整功能支持');
        }

        const features = this.checkFeatures();
        if (!features.audioContext || !features.getUserMedia) {
            recommendations.push('语音功能需要现代浏览器支持，建议使用Chrome或Safari');
        }

        return recommendations;
    }

    /**
     * 显示调试面板
     */
    showDebugPanel() {
        const report = this.generateReport();
        
        const panel = document.createElement('div');
        panel.id = 'wechat-debug-panel';
        panel.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 400px;
            max-height: 80vh;
            background: white;
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 15px;
            z-index: 10000;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        `;

        panel.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; color: #333;">微信浏览器调试面板</h3>
                <button onclick="this.parentElement.parentElement.remove()" style="background: #ff4444; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">关闭</button>
            </div>
            
            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 5px 0; color: #666;">问题诊断</h4>
                ${report.issues.length > 0 ? 
                    report.issues.map(issue => `
                        <div style="margin: 5px 0; padding: 8px; background: ${issue.severity === 'critical' ? '#ffebee' : issue.severity === 'high' ? '#fff3e0' : '#f3e5f5'}; border-left: 4px solid ${issue.severity === 'critical' ? '#f44336' : issue.severity === 'high' ? '#ff9800' : '#9c27b0'};">
                            <strong>${issue.type.toUpperCase()}</strong>: ${issue.message}<br>
                            <small>解决方案: ${issue.solution}</small>
                        </div>
                    `).join('') : 
                    '<div style="color: #4caf50;">✅ 未发现问题</div>'
                }
            </div>

            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 5px 0; color: #666;">功能支持</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
                    ${Object.entries(report.debugInfo.features).map(([key, value]) => `
                        <div style="padding: 4px; background: ${value ? '#e8f5e8' : '#ffebee'}; border-radius: 3px;">
                            ${key}: ${value ? '✅' : '❌'}
                        </div>
                    `).join('')}
                </div>
            </div>

            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 5px 0; color: #666;">建议</h4>
                ${report.recommendations.map(rec => `
                    <div style="margin: 3px 0; padding: 5px; background: #e3f2fd; border-radius: 3px;">
                        💡 ${rec}
                    </div>
                `).join('')}
            </div>

            <div>
                <button onclick="navigator.clipboard.writeText(JSON.stringify(window.wechatDebugger.generateReport(), null, 2))" style="background: #2196f3; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; margin-right: 10px;">复制调试信息</button>
                <button onclick="console.log(window.wechatDebugger.generateReport())" style="background: #4caf50; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;">输出到控制台</button>
            </div>
        `;

        document.body.appendChild(panel);
    }

    /**
     * 初始化调试器
     */
    init() {
        if (this.isWeChat) {
            console.log('微信浏览器调试器已启动');
            
            // 添加调试按钮到页面
            const debugButton = document.createElement('button');
            debugButton.innerHTML = '🐛 微信调试';
            debugButton.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #ff9800;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 25px;
                cursor: pointer;
                z-index: 9999;
                font-size: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            `;
            debugButton.onclick = () => this.showDebugPanel();
            document.body.appendChild(debugButton);
        }
    }
}

// 全局调试器实例
window.wechatDebugger = new WeChatDebugger();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    window.wechatDebugger.init();
});
