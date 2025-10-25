/**
 * 麦克风释放测试脚本
 * 用于验证录音聊天结束后麦克风是否正确释放
 */

// 测试麦克风释放状态
function testMicrophoneRelease() {
    console.log('🧪 开始测试麦克风释放状态...');
    
    // 检查录音器状态
    if (window.voiceRecorderEnhanced) {
        console.log('🎤 录音器实例存在');
        console.log('🎤 录音器状态:', {
            isRecording: window.voiceRecorderEnhanced.isRecording,
            audioStream: window.voiceRecorderEnhanced.audioStream,
            audioContext: window.voiceRecorderEnhanced.audioContext,
            microphone: window.voiceRecorderEnhanced.microphone
        });
        
        // 检查音频流状态
        if (window.voiceRecorderEnhanced.audioStream) {
            console.log('🎤 音频流仍然存在，麦克风未释放！');
            console.log('🎤 音频轨道状态:', window.voiceRecorderEnhanced.audioStream.getTracks().map(track => ({
                label: track.label,
                readyState: track.readyState,
                enabled: track.enabled
            })));
        } else {
            console.log('🎤 音频流已释放，麦克风已释放 ✅');
        }
    } else {
        console.log('🎤 录音器实例不存在');
    }
    
    // 检查WebSocket管理器状态
    if (window.voiceWebSocketManager) {
        console.log('🎤 WebSocket管理器状态:', {
            audioStream: window.voiceWebSocketManager.audioStream,
            audioContext: window.voiceWebSocketManager.audioContext
        });
        
        if (window.voiceWebSocketManager.audioStream) {
            console.log('🎤 WebSocket管理器音频流仍然存在！');
        } else {
            console.log('🎤 WebSocket管理器音频流已释放 ✅');
        }
    }
    
    // 检查浏览器麦克风权限状态
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                console.log('🎤 浏览器麦克风权限测试: 可以获取麦克风');
                // 立即释放测试流
                stream.getTracks().forEach(track => track.stop());
                console.log('🎤 测试流已释放');
            })
            .catch(error => {
                console.log('🎤 浏览器麦克风权限测试: 无法获取麦克风', error.message);
            });
    }
}

// 强制释放麦克风
function forceReleaseMicrophone() {
    console.log('🔧 强制释放麦克风...');
    
    // 释放录音器麦克风
    if (window.voiceRecorderEnhanced) {
        console.log('🔧 释放录音器麦克风...');
        window.voiceRecorderEnhanced.cleanup();
    }
    
    // 释放WebSocket管理器麦克风
    if (window.voiceWebSocketManager) {
        console.log('🔧 释放WebSocket管理器麦克风...');
        window.voiceWebSocketManager.stopAudioStreaming();
    }
    
    console.log('🔧 强制释放完成');
}

// 监听麦克风状态变化
function monitorMicrophoneStatus() {
    console.log('👀 开始监听麦克风状态...');
    
    setInterval(() => {
        let hasActiveStreams = false;
        
        // 检查录音器
        if (window.voiceRecorderEnhanced && window.voiceRecorderEnhanced.audioStream) {
            hasActiveStreams = true;
            console.log('🎤 录音器仍有音频流');
        }
        
        // 检查WebSocket管理器
        if (window.voiceWebSocketManager && window.voiceWebSocketManager.audioStream) {
            hasActiveStreams = true;
            console.log('🎤 WebSocket管理器仍有音频流');
        }
        
        if (!hasActiveStreams) {
            console.log('🎤 所有音频流已释放 ✅');
        }
    }, 2000);
}

// 导出测试函数
window.testMicrophoneRelease = testMicrophoneRelease;
window.forceReleaseMicrophone = forceReleaseMicrophone;
window.monitorMicrophoneStatus = monitorMicrophoneStatus;

console.log('🧪 麦克风释放测试脚本已加载');
console.log('🧪 使用方法:');
console.log('🧪 - testMicrophoneRelease() - 测试麦克风释放状态');
console.log('🧪 - forceReleaseMicrophone() - 强制释放麦克风');
console.log('🧪 - monitorMicrophoneStatus() - 监听麦克风状态');
