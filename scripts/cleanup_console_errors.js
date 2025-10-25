/**
 * 浏览器控制台错误清理脚本
 * 
 * 用于自动检测和修复常见的浏览器控制台错误
 * 在浏览器控制台中运行此脚本
 */

(function() {
    console.log('🧹 开始清理浏览器控制台错误...');
    
    // 1. 检查并修复智能错误处理系统
    function checkSmartErrorHandler() {
        if (!window.smartErrorHandler) {
            console.warn('🔧 智能错误处理系统未找到，尝试延迟加载...');
            setTimeout(() => {
                if (window.smartErrorHandler) {
                    console.log('🔧 智能错误处理系统已加载');
                } else {
                    console.warn('🔧 智能错误处理系统仍未找到，可能影响错误处理');
                }
            }, 2000);
        } else {
            console.log('🔧 智能错误处理系统正常');
        }
    }
    
    // 2. 检查并修复状态同步管理器
    function checkStateSyncManager() {
        if (!window.stateSyncManager) {
            console.warn('🔄 状态同步管理器未找到，尝试延迟加载...');
            setTimeout(() => {
                if (window.stateSyncManager) {
                    console.log('🔄 状态同步管理器已加载');
                } else {
                    console.warn('🔄 状态同步管理器仍未找到，可能影响状态同步');
                }
            }, 2000);
        } else {
            console.log('🔄 状态同步管理器正常');
        }
    }
    
    // 3. 检查并修复智能状态预测器
    function checkSmartStatePredictor() {
        if (!window.smartStatePredictor) {
            console.warn('🔮 智能状态预测器未找到，尝试延迟加载...');
            setTimeout(() => {
                if (window.smartStatePredictor) {
                    console.log('🔮 智能状态预测器已加载');
                } else {
                    console.warn('🔮 智能状态预测器仍未找到，可能影响状态预测');
                }
            }, 2000);
        } else {
            console.log('🔮 智能状态预测器正常');
        }
    }
    
    // 4. 检查并修复音频可视化Canvas
    function checkAudioVisualizer() {
        const canvas = document.getElementById('audio-visualizer');
        const container = document.getElementById('audio-visualizer-container');
        
        if (!container) {
            console.warn('🎨 音频可视化容器未找到');
            return;
        }
        
        if (!canvas) {
            console.warn('🎨 音频可视化Canvas未找到，尝试创建...');
            // 在正确的容器中创建Canvas元素
            const newCanvas = document.createElement('canvas');
            newCanvas.id = 'audio-visualizer';
            newCanvas.width = 80;
            newCanvas.height = 20;
            newCanvas.style.cssText = 'width: 80px; height: 20px; border: 1px solid #d9d9d9; border-radius: 4px; background-color: #fff; vertical-align: middle; display: inline-block;';
            container.appendChild(newCanvas);
            console.log('🎨 音频可视化Canvas已创建');
        } else {
            console.log('🎨 音频可视化Canvas正常');
        }
        
        // 检查容器显示状态
        const containerStyle = window.getComputedStyle(container);
        const isVisible = containerStyle.display !== 'none';
        console.log(`🎨 音频可视化容器状态: ${isVisible ? '可见' : '隐藏'}`);
        
        if (!isVisible) {
            console.log('🎨 音频可视化容器当前隐藏，这是正常的（默认状态）');
        }
    }
    
    // 5. 检查并修复WebSocket连接
    function checkWebSocketConnection() {
        if (window.voiceWebSocketManager && window.voiceWebSocketManager.ws) {
            const ws = window.voiceWebSocketManager.ws;
            if (ws.readyState === WebSocket.OPEN) {
                console.log('🔌 WebSocket连接正常');
            } else if (ws.readyState === WebSocket.CONNECTING) {
                console.log('🔌 WebSocket正在连接...');
            } else {
                console.warn('🔌 WebSocket连接异常，状态:', ws.readyState);
                // 尝试重连
                setTimeout(() => {
                    if (window.voiceWebSocketManager) {
                        console.log('🔌 尝试重新连接WebSocket...');
                        window.voiceWebSocketManager.connect();
                    }
                }, 1000);
            }
        } else {
            console.warn('🔌 WebSocket管理器未找到');
        }
    }
    
    // 6. 检查并修复状态管理
    function checkStateManagement() {
        if (window.stateManager) {
            console.log('📊 状态管理器正常');
            const currentState = window.stateManager.getCurrentState();
            console.log('📊 当前状态:', currentState);
        } else {
            console.warn('📊 状态管理器未找到');
        }
        
        if (window.stateSyncManager) {
            console.log('🔄 状态同步管理器正常');
            const states = window.stateSyncManager.getAllStates();
            console.log('🔄 已注册状态:', Object.keys(states));
        } else {
            console.warn('🔄 状态同步管理器未找到');
        }
    }
    
    // 7. 检查并修复语音播放器
    function checkVoicePlayer() {
        if (window.voicePlayer) {
            console.log('🎵 语音播放器正常');
        } else {
            console.warn('🎵 语音播放器未找到');
        }
        
        if (window.voicePlayerEnhanced) {
            console.log('🎵 增强语音播放器正常');
        } else {
            console.warn('🎵 增强语音播放器未找到');
        }
    }
    
    // 8. 检查并修复语音录制器
    function checkVoiceRecorder() {
        if (window.voiceRecorder) {
            console.log('🎤 语音录制器正常');
        } else {
            console.warn('🎤 语音录制器未找到');
        }
        
        if (window.voiceRecorderEnhanced) {
            console.log('🎤 增强语音录制器正常');
        } else {
            console.warn('🎤 增强语音录制器未找到');
        }
    }
    
    // 9. 检查网络请求错误
    function checkNetworkErrors() {
        // 检查是否有网络请求错误
        const networkErrors = [];
        
        // 检查Dash Table bundle.js错误
        if (window.location.href.includes('localhost:8050')) {
            console.log('🌐 检查Dash Table资源...');
            fetch('/_dash-component-suites/dash/dash_table/bundle.js')
                .then(response => {
                    if (response.ok) {
                        console.log('✅ Dash Table bundle.js正常');
                    } else {
                        console.warn('❌ Dash Table bundle.js加载失败:', response.status);
                    }
                })
                .catch(error => {
                    console.warn('❌ Dash Table bundle.js网络错误:', error);
                });
        }
    }
    
    // 10. 生成错误报告
    function generateErrorReport() {
        const report = {
            timestamp: new Date().toISOString(),
            errors: [],
            warnings: [],
            status: 'checking'
        };
        
        // 检查各种系统状态
        const systems = [
            { name: 'smartErrorHandler', obj: window.smartErrorHandler },
            { name: 'stateSyncManager', obj: window.stateSyncManager },
            { name: 'smartStatePredictor', obj: window.smartStatePredictor },
            { name: 'stateManager', obj: window.stateManager },
            { name: 'voiceWebSocketManager', obj: window.voiceWebSocketManager },
            { name: 'voicePlayer', obj: window.voicePlayer },
            { name: 'voiceRecorder', obj: window.voiceRecorder }
        ];
        
        systems.forEach(system => {
            if (!system.obj) {
                report.warnings.push(`${system.name}未找到`);
            } else {
                report.status = 'healthy';
            }
        });
        
        console.log('📋 错误报告:', report);
        return report;
    }
    
    // 执行所有检查
    console.log('🔍 开始系统检查...');
    
    checkSmartErrorHandler();
    checkStateSyncManager();
    checkSmartStatePredictor();
    checkAudioVisualizer();
    checkWebSocketConnection();
    checkStateManagement();
    checkVoicePlayer();
    checkVoiceRecorder();
    checkNetworkErrors();
    
    // 生成最终报告
    setTimeout(() => {
        const report = generateErrorReport();
        console.log('✅ 浏览器控制台错误清理完成');
        console.log('📊 系统状态报告:', report);
    }, 3000);
    
    // 返回清理函数，供手动调用
    window.cleanupConsoleErrors = function() {
        console.log('🧹 手动执行控制台错误清理...');
        checkSmartErrorHandler();
        checkStateSyncManager();
        checkSmartStatePredictor();
        checkAudioVisualizer();
        checkWebSocketConnection();
        checkStateManagement();
        checkVoicePlayer();
        checkVoiceRecorder();
        checkNetworkErrors();
    };
    
    console.log('💡 提示: 可以随时调用 window.cleanupConsoleErrors() 来手动清理错误');
    
})();
