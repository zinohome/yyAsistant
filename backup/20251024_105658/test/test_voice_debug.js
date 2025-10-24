/**
 * 语音转文本调试工具
 * 用于测试和调试语音转文本功能
 */

class VoiceTranscriptionDebugger {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.messageCount = 0;
    }
    
    /**
     * 初始化调试器
     */
    init() {
        console.log('🎤 语音转文本调试器初始化');
        this.setupEventListeners();
        this.testInputBox();
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 监听录音按钮点击
        document.addEventListener('click', (event) => {
            if (event.target.closest('#voice-record-btn')) {
                console.log('🎤 录音按钮被点击');
                this.logButtonState();
            }
        });
        
        // 监听WebSocket消息
        this.setupWebSocketListener();
    }
    
    /**
     * 设置WebSocket监听器
     */
    setupWebSocketListener() {
        // 监听全局WebSocket管理器的消息
        if (window.voiceWebSocketManager) {
            window.voiceWebSocketManager.registerMessageHandler('transcription_result', (data) => {
                console.log('📝 收到转录结果:', data);
                this.handleTranscriptionResult(data);
            });
            
            window.voiceWebSocketManager.registerMessageHandler('error', (data) => {
                console.log('❌ 收到错误消息:', data);
            });
        }
    }
    
    /**
     * 测试输入框
     */
    testInputBox() {
        const input = document.getElementById('ai-chat-x-input');
        if (input) {
            console.log('✅ 找到输入框:', input);
            console.log('📝 输入框当前值:', input.value);
        } else {
            console.error('❌ 未找到输入框 ai-chat-x-input');
        }
    }
    
    /**
     * 记录按钮状态
     */
    logButtonState() {
        const recordBtn = document.getElementById('voice-record-btn');
        const callBtn = document.getElementById('voice-call-btn');
        const sendBtn = document.getElementById('ai-chat-x-send-btn');
        
        console.log('🔘 按钮状态:');
        console.log('  录音按钮:', recordBtn ? '存在' : '不存在');
        console.log('  通话按钮:', callBtn ? '存在' : '不存在');
        console.log('  发送按钮:', sendBtn ? '存在' : '不存在');
        
        if (recordBtn) {
            console.log('  录音按钮禁用状态:', recordBtn.disabled);
            console.log('  录音按钮样式:', recordBtn.style);
        }
    }
    
    /**
     * 处理转录结果
     */
    handleTranscriptionResult(data) {
        console.log('📝 处理转录结果:', data);
        
        if (data.text && data.text.trim()) {
            const input = document.getElementById('ai-chat-x-input');
            if (input) {
                input.value = data.text.trim();
                input.focus();
                console.log('✅ 文本已填入输入框:', data.text.trim());
            } else {
                console.error('❌ 未找到输入框');
            }
        } else {
            console.log('⚠️ 转录结果为空');
        }
    }
    
    /**
     * 模拟转录结果（用于测试）
     */
    simulateTranscriptionResult() {
        const testText = '这是模拟的转录结果 - ' + new Date().toLocaleTimeString();
        const input = document.getElementById('ai-chat-x-input');
        
        if (input) {
            input.value = testText;
            input.focus();
            console.log('🧪 模拟转录结果已填入:', testText);
        } else {
            console.error('❌ 未找到输入框');
        }
    }
    
    /**
     * 检查WebSocket连接状态
     */
    checkWebSocketStatus() {
        if (window.voiceWebSocketManager) {
            const status = window.voiceWebSocketManager.getConnectionStatus();
            console.log('🔌 WebSocket状态:', status);
            return status.isConnected;
        } else {
            console.error('❌ WebSocket管理器不存在');
            return false;
        }
    }
    
    /**
     * 发送测试音频数据
     */
    sendTestAudioData() {
        if (!this.checkWebSocketStatus()) {
            console.error('❌ WebSocket未连接，无法发送测试数据');
            return;
        }
        
        // 创建一个简单的测试音频数据
        const testAudioData = 'dGVzdF9hdWRpb19kYXRh'; // base64编码的测试数据
        
        const message = {
            type: 'audio_input',
            audio_data: testAudioData,
            audio_format: 'webm',
            sample_rate: 16000
        };
        
        console.log('📤 发送测试音频数据:', message);
        window.voiceWebSocketManager.sendMessage(message);
    }
}

// 创建全局调试器实例
window.voiceDebugger = new VoiceTranscriptionDebugger();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 页面加载完成，初始化语音调试器');
    window.voiceDebugger.init();
});

// 添加全局调试函数
window.testVoiceTranscription = function() {
    console.log('🧪 开始语音转文本测试');
    window.voiceDebugger.simulateTranscriptionResult();
};

window.checkVoiceStatus = function() {
    console.log('🔍 检查语音功能状态');
    window.voiceDebugger.checkWebSocketStatus();
    window.voiceDebugger.logButtonState();
};

window.sendTestAudio = function() {
    console.log('📤 发送测试音频数据');
    window.voiceDebugger.sendTestAudioData();
};

console.log('🎤 语音转文本调试器已加载');
console.log('可用命令:');
console.log('  testVoiceTranscription() - 测试转录结果填入');
console.log('  checkVoiceStatus() - 检查语音功能状态');
console.log('  sendTestAudio() - 发送测试音频数据');
