/**
 * 实时语音回调处理
 * 处理前端JavaScript事件绑定和状态管理
 */

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('实时语音回调初始化...');
    
    // 初始化实时语音管理器
    if (!window.realtimeVoiceManager) {
        window.realtimeVoiceManager = new RealtimeVoiceManager();
    }
    
    // 绑定通话按钮事件
    bindVoiceCallButton();
    
    // 绑定状态更新事件
    bindStatusUpdateEvents();
    
    // 绑定音频可视化事件
    bindAudioVisualizationEvents();
    
    console.log('实时语音回调初始化完成');
});

/**
 * 绑定通话按钮事件
 */
function bindVoiceCallButton() {
    const voiceCallBtn = document.getElementById('voice-call-btn');
    
    if (voiceCallBtn) {
        voiceCallBtn.addEventListener('click', async function() {
            try {
                console.log('通话按钮被点击');
                
                if (window.realtimeVoiceManager.isActive) {
                    // 停止实时语音
                    await window.realtimeVoiceManager.stop();
                } else {
                    // 启动实时语音
                    await window.realtimeVoiceManager.start();
                }
                
            } catch (error) {
                console.error('处理通话按钮点击失败:', error);
                showError('实时语音操作失败: ' + error.message);
            }
        });
    } else {
        console.warn('未找到通话按钮元素');
    }
}

/**
 * 绑定状态更新事件
 */
function bindStatusUpdateEvents() {
    if (window.realtimeVoiceManager) {
        // 监听状态变化
        window.realtimeVoiceManager.on('state_changed', function(data) {
            console.log('状态变化:', data);
            updateStatusDisplay(data.newState);
        });
        
        // 监听错误事件
        window.realtimeVoiceManager.on('error', function(error) {
            console.error('实时语音错误:', error);
            showError('实时语音错误: ' + error.message);
        });
        
        // 监听启动事件
        window.realtimeVoiceManager.on('started', function() {
            console.log('实时语音已启动');
            updateButtonState(true);
        });
        
        // 监听停止事件
        window.realtimeVoiceManager.on('stopped', function() {
            console.log('实时语音已停止');
            updateButtonState(false);
        });
    }
}

/**
 * 绑定音频可视化事件
 */
function bindAudioVisualizationEvents() {
    if (window.realtimeVoiceManager) {
        // 监听音频可视化更新
        window.realtimeVoiceManager.on('audio_visualization', function(data) {
            updateAudioVisualization(data.audioLevel, data.dataArray);
        });
        
        // 监听可视化更新
        window.realtimeVoiceManager.on('visualization_update', function(data) {
            updateVisualizationState(data.state);
        });
    }
}

/**
 * 更新状态显示
 */
function updateStatusDisplay(state) {
    const statusElement = document.getElementById('realtime-voice-status');
    const statusTextElement = document.getElementById('realtime-status-text');
    
    if (!statusElement || !statusTextElement) {
        console.warn('未找到状态元素');
        return;
    }
    
    const statusConfig = getStatusConfig(state);
    
    // 更新状态文本
    statusTextElement.textContent = statusConfig.text;
    
    // 更新状态颜色
    const badgeElement = statusElement.querySelector('.ant-badge');
    if (badgeElement) {
        // 移除旧的颜色类
        badgeElement.className = badgeElement.className.replace(/ant-badge-status-\w+/g, '');
        // 添加新的颜色类
        badgeElement.classList.add(`ant-badge-status-${statusConfig.color}`);
        
        const dotElement = badgeElement.querySelector('.ant-badge-status-dot');
        if (dotElement) {
            dotElement.className = dotElement.className.replace(/ant-badge-status-dot-\w+/g, '');
            dotElement.classList.add(`ant-badge-status-dot-${statusConfig.color}`);
        }
    }
}

/**
 * 获取状态配置
 */
function getStatusConfig(state) {
    const configs = {
        'idle': { text: '等待开始', color: 'gray' },
        'connecting': { text: '正在连接...', color: 'blue' },
        'listening': { text: '正在监听', color: 'red' },
        'processing': { text: '处理中...', color: 'orange' },
        'speaking': { text: 'AI说话中', color: 'green' },
        'error': { text: '连接错误', color: 'red' }
    };
    
    return configs[state] || { text: '未知状态', color: 'gray' };
}

/**
 * 更新按钮状态
 */
function updateButtonState(isActive) {
    const voiceCallBtn = document.getElementById('voice-call-btn');
    
    if (voiceCallBtn) {
        voiceCallBtn.disabled = isActive;
        voiceCallBtn.textContent = isActive ? '停止实时对话' : '开始实时对话';
    }
}

/**
 * 更新音频可视化
 */
function updateAudioVisualization(audioLevel, dataArray) {
    const canvas = document.getElementById('audio-visualizer');
    
    if (!canvas) {
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // 清除画布
    ctx.clearRect(0, 0, width, height);
    
    // 根据音频级别绘制可视化
    const barWidth = width / dataArray.length;
    const maxBarHeight = height * 0.8;
    
    for (let i = 0; i < dataArray.length; i++) {
        const barHeight = (dataArray[i] / 255) * maxBarHeight;
        const x = i * barWidth;
        const y = height - barHeight;
        
        // 根据音频级别选择颜色
        const intensity = dataArray[i] / 255;
        if (intensity > 0.7) {
            ctx.fillStyle = '#ff4d4f'; // 红色 - 高音量
        } else if (intensity > 0.4) {
            ctx.fillStyle = '#faad14'; // 橙色 - 中音量
        } else if (intensity > 0.1) {
            ctx.fillStyle = '#52c41a'; // 绿色 - 低音量
        } else {
            ctx.fillStyle = '#d9d9d9'; // 灰色 - 静音
        }
        
        ctx.fillRect(x, y, barWidth - 1, barHeight);
    }
}

/**
 * 更新可视化状态
 */
function updateVisualizationState(state) {
    const canvas = document.getElementById('audio-visualizer');
    
    if (!canvas) {
        return;
    }
    
    // 根据状态更新画布样式
    if (state === 'listening' || state === 'speaking') {
        canvas.style.borderColor = '#52c41a';
        canvas.style.backgroundColor = '#f6ffed';
    } else if (state === 'processing') {
        canvas.style.borderColor = '#faad14';
        canvas.style.backgroundColor = '#fffbe6';
    } else if (state === 'error') {
        canvas.style.borderColor = '#ff4d4f';
        canvas.style.backgroundColor = '#fff2f0';
    } else {
        canvas.style.borderColor = '#d9d9d9';
        canvas.style.backgroundColor = '#f5f5f5';
    }
}

/**
 * 显示错误消息
 */
function showError(message) {
    console.error(message);
    
    // 使用toast提示而不是alert弹出框
    const currentPath = window.location.pathname;
    const isChatPage = currentPath === '/core/chat' || currentPath.endsWith('/core/chat');
    
    if (isChatPage && window.dash_clientside && window.dash_clientside.set_props) {
        // 使用Dash的global-message组件显示toast提示
        window.dash_clientside.set_props('global-message', {
            children: {
                'content': message,
                'type': 'error',
                'duration': 3
            }
        });
        console.log('已发送toast提示:', message);
    } else {
        // 如果不在聊天页面或Dash不可用，使用console.warn
        console.warn('实时语音提示:', message);
    }
}

/**
 * 检查浏览器支持
 */
function checkBrowserSupport() {
    if (!RealtimeAudioProcessor.isSupported()) {
        const reason = (typeof RealtimeAudioProcessor.getUnsupportedReason === 'function')
            ? RealtimeAudioProcessor.getUnsupportedReason()
            : '浏览器或运行环境不满足实时语音所需条件';
        const hint = '请使用 HTTPS 域名或 localhost 访问，并允许麦克风权限。';
        showError(`您的环境暂不支持实时语音：${reason}。${hint}`);
        return false;
    }
    
    return true;
}

/**
 * 初始化检查
 */
function initializeChecks() {
    // 检查浏览器支持
    if (!checkBrowserSupport()) {
        return false;
    }
    
    // 检查必要的元素
    const requiredElements = [
        'voice-call-btn',
        'realtime-voice-status',
        'audio-visualizer'
    ];
    
    for (const elementId of requiredElements) {
        if (!document.getElementById(elementId)) {
            console.warn(`未找到必要元素: ${elementId}`);
        }
    }
    
    return true;
}

// 执行初始化检查
if (initializeChecks()) {
    console.log('实时语音功能初始化成功');
} else {
    console.error('实时语音功能初始化失败');
}
