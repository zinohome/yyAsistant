/**
 * 三大核心场景验证脚本
 * 
 * 用于验证文本聊天、语音录制、语音通话三个核心场景
 * 在浏览器控制台中运行此脚本
 */

(function() {
    console.log('🎯 开始验证三大核心场景...');
    
    // 验证结果存储
    const verificationResults = {
        textChat: { status: 'pending', details: [] },
        voiceRecording: { status: 'pending', details: [] },
        voiceCall: { status: 'pending', details: [] },
        overall: { status: 'pending', score: 0, maxScore: 100 }
    };
    
    // 1. 文本聊天场景验证
    function verifyTextChat() {
        console.log('📝 验证文本聊天场景...');
        const results = [];
        
        // 检查输入框
        const inputElement = document.querySelector('#ai-chat-x-input');
        if (inputElement) {
            results.push('✅ 输入框存在');
        } else {
            results.push('❌ 输入框未找到');
        }
        
        // 检查发送按钮
        const sendButton = document.querySelector('#ai-chat-x-send-btn');
        if (sendButton) {
            results.push('✅ 发送按钮存在');
        } else {
            results.push('❌ 发送按钮未找到');
        }
        
        // 检查消息容器
        const messageContainer = document.querySelector('#ai-chat-x-messages-store');
        if (messageContainer) {
            results.push('✅ 消息容器存在');
        } else {
            results.push('❌ 消息容器未找到');
        }
        
        // 检查SSE相关组件
        const sseComponents = document.querySelectorAll('[id*="sse"]');
        if (sseComponents.length > 0) {
            results.push(`✅ SSE组件存在 (${sseComponents.length}个)`);
        } else {
            results.push('❌ SSE组件未找到');
        }
        
        // 检查TTS相关组件
        const ttsComponents = document.querySelectorAll('[id*="tts"]');
        if (ttsComponents.length > 0) {
            results.push(`✅ TTS组件存在 (${ttsComponents.length}个)`);
        } else {
            results.push('❌ TTS组件未找到');
        }
        
        // 检查状态管理器
        if (window.stateManager) {
            results.push('✅ 状态管理器存在');
        } else {
            results.push('❌ 状态管理器未找到');
        }
        
        // 检查语音播放器
        if (window.voicePlayerEnhanced) {
            results.push('✅ 语音播放器存在');
        } else {
            results.push('❌ 语音播放器未找到');
        }
        
        verificationResults.textChat.details = results;
        verificationResults.textChat.status = results.some(r => r.includes('❌')) ? 'failed' : 'passed';
        
        console.log('📝 文本聊天验证结果:', results);
        return results;
    }
    
    // 2. 语音录制场景验证
    function verifyVoiceRecording() {
        console.log('🎤 验证语音录制场景...');
        const results = [];
        
        // 检查录音按钮
        const recordButton = document.querySelector('#ai-chat-x-voice-record-btn');
        if (recordButton) {
            results.push('✅ 录音按钮存在');
        } else {
            results.push('❌ 录音按钮未找到');
        }
        
        // 检查音频可视化容器
        const audioVisualizerContainer = document.querySelector('#audio-visualizer-container');
        if (audioVisualizerContainer) {
            results.push('✅ 音频可视化容器存在');
            
            // 检查容器显示状态
            const containerStyle = window.getComputedStyle(audioVisualizerContainer);
            const isVisible = containerStyle.display !== 'none';
            results.push(`✅ 音频可视化容器状态: ${isVisible ? '可见' : '隐藏'}`);
        } else {
            results.push('❌ 音频可视化容器未找到');
        }
        
        // 检查音频可视化Canvas
        const audioVisualizer = document.querySelector('#audio-visualizer');
        if (audioVisualizer) {
            results.push('✅ 音频可视化Canvas存在');
        } else {
            results.push('❌ 音频可视化Canvas未找到');
        }
        
        // 检查语音录制器
        if (window.voiceRecorderEnhanced) {
            results.push('✅ 增强语音录制器存在');
        } else {
            results.push('❌ 增强语音录制器未找到');
        }
        
        // 检查麦克风权限
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            results.push('✅ 麦克风API可用');
        } else {
            results.push('❌ 麦克风API不可用');
        }
        
        // 检查音频上下文
        if (window.AudioContext || window.webkitAudioContext) {
            results.push('✅ 音频上下文API可用');
        } else {
            results.push('❌ 音频上下文API不可用');
        }
        
        // 检查STT相关组件
        const sttComponents = document.querySelectorAll('[id*="stt"]');
        if (sttComponents.length > 0) {
            results.push(`✅ STT组件存在 (${sttComponents.length}个)`);
        } else {
            results.push('❌ STT组件未找到');
        }
        
        verificationResults.voiceRecording.details = results;
        verificationResults.voiceRecording.status = results.some(r => r.includes('❌')) ? 'failed' : 'passed';
        
        console.log('🎤 语音录制验证结果:', results);
        return results;
    }
    
    // 3. 语音通话场景验证
    function verifyVoiceCall() {
        console.log('📞 验证语音通话场景...');
        const results = [];
        
        // 检查语音通话按钮
        const callButton = document.querySelector('#ai-chat-x-voice-call-btn');
        if (callButton) {
            results.push('✅ 语音通话按钮存在');
        } else {
            results.push('❌ 语音通话按钮未找到');
        }
        
        // 检查WebSocket连接
        if (window.voiceWebSocketManager && window.voiceWebSocketManager.ws) {
            const ws = window.voiceWebSocketManager.ws;
            if (ws.readyState === WebSocket.OPEN) {
                results.push('✅ WebSocket连接正常');
            } else if (ws.readyState === WebSocket.CONNECTING) {
                results.push('⏳ WebSocket正在连接');
            } else {
                results.push('❌ WebSocket连接异常');
            }
        } else {
            results.push('❌ WebSocket管理器未找到');
        }
        
        // 检查实时语音管理器
        if (window.realtimeVoiceManager) {
            results.push('✅ 实时语音管理器存在');
        } else {
            results.push('❌ 实时语音管理器未找到');
        }
        
        // 检查语音状态协调器
        if (window.voiceStateCoordinator) {
            results.push('✅ 语音状态协调器存在');
        } else {
            results.push('❌ 语音状态协调器未找到');
        }
        
        // 检查音频流处理
        if (window.AudioContext || window.webkitAudioContext) {
            results.push('✅ 音频流处理API可用');
        } else {
            results.push('❌ 音频流处理API不可用');
        }
        
        // 检查网络连接
        if (navigator.onLine) {
            results.push('✅ 网络连接正常');
        } else {
            results.push('❌ 网络连接异常');
        }
        
        verificationResults.voiceCall.details = results;
        verificationResults.voiceCall.status = results.some(r => r.includes('❌')) ? 'failed' : 'passed';
        
        console.log('📞 语音通话验证结果:', results);
        return results;
    }
    
    // 4. 状态管理验证
    function verifyStateManagement() {
        console.log('📊 验证状态管理...');
        const results = [];
        
        // 检查状态管理器
        if (window.stateManager) {
            results.push('✅ 状态管理器存在');
            const currentState = window.stateManager.getCurrentState();
            results.push(`✅ 当前状态: ${currentState}`);
        } else {
            results.push('❌ 状态管理器未找到');
        }
        
        // 检查状态同步管理器
        if (window.stateSyncManager) {
            results.push('✅ 状态同步管理器存在');
            const states = window.stateSyncManager.getAllStates();
            results.push(`✅ 已注册状态: ${Object.keys(states).join(', ')}`);
        } else {
            results.push('❌ 状态同步管理器未找到');
        }
        
        // 检查状态转换
        if (window.stateManager) {
            const stateHistory = window.stateManager.getStateHistory();
            if (stateHistory && stateHistory.length > 0) {
                results.push(`✅ 状态历史记录: ${stateHistory.length}条`);
            } else {
                results.push('⚠️ 状态历史记录为空');
            }
        }
        
        // 检查状态锁定机制
        if (window.stateManager && typeof window.stateManager.isStateLocked === 'function') {
            const isLocked = window.stateManager.isStateLocked();
            results.push(`✅ 状态锁定检查: ${isLocked ? '已锁定' : '未锁定'}`);
        }
        
        console.log('📊 状态管理验证结果:', results);
        return results;
    }
    
    // 5. 性能验证
    function verifyPerformance() {
        console.log('⚡ 验证性能指标...');
        const results = [];
        
        // 检查内存使用
        if (performance.memory) {
            const memory = performance.memory;
            const usedMB = Math.round(memory.usedJSHeapSize / 1024 / 1024);
            const totalMB = Math.round(memory.totalJSHeapSize / 1024 / 1024);
            results.push(`✅ 内存使用: ${usedMB}MB / ${totalMB}MB`);
        } else {
            results.push('⚠️ 内存信息不可用');
        }
        
        // 检查页面加载时间
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        results.push(`✅ 页面加载时间: ${loadTime}ms`);
        
        // 检查资源加载
        const resources = performance.getEntriesByType('resource');
        const failedResources = resources.filter(r => r.transferSize === 0 && r.name.includes('bundle'));
        if (failedResources.length === 0) {
            results.push('✅ 资源加载正常');
        } else {
            results.push(`❌ 资源加载失败: ${failedResources.length}个`);
        }
        
        console.log('⚡ 性能验证结果:', results);
        return results;
    }
    
    // 6. 生成综合报告
    function generateReport() {
        console.log('📋 生成综合验证报告...');
        
        // 计算总分
        let totalScore = 0;
        let maxScore = 0;
        
        Object.keys(verificationResults).forEach(key => {
            if (key !== 'overall') {
                const result = verificationResults[key];
                maxScore += 25; // 每个场景25分
                if (result.status === 'passed') {
                    totalScore += 25;
                } else if (result.status === 'failed') {
                    totalScore += 0;
                } else {
                    totalScore += 12.5; // 部分通过
                }
            }
        });
        
        verificationResults.overall.score = totalScore;
        verificationResults.overall.maxScore = maxScore;
        verificationResults.overall.status = totalScore >= maxScore * 0.8 ? 'excellent' : 
                                           totalScore >= maxScore * 0.6 ? 'good' : 
                                           totalScore >= maxScore * 0.4 ? 'fair' : 'poor';
        
        console.log('📊 验证报告:', verificationResults);
        
        // 生成建议
        const suggestions = [];
        if (verificationResults.textChat.status === 'failed') {
            suggestions.push('🔧 文本聊天场景需要修复');
        }
        if (verificationResults.voiceRecording.status === 'failed') {
            suggestions.push('🔧 语音录制场景需要修复');
        }
        if (verificationResults.voiceCall.status === 'failed') {
            suggestions.push('🔧 语音通话场景需要修复');
        }
        
        if (suggestions.length > 0) {
            console.log('💡 修复建议:', suggestions);
        } else {
            console.log('🎉 所有场景验证通过！');
        }
        
        return verificationResults;
    }
    
    // 执行所有验证
    console.log('🚀 开始执行验证...');
    
    verifyTextChat();
    verifyVoiceRecording();
    verifyVoiceCall();
    verifyStateManagement();
    verifyPerformance();
    
    // 生成最终报告
    setTimeout(() => {
        const report = generateReport();
        console.log('✅ 验证完成！');
        console.log('📊 最终报告:', report);
    }, 2000);
    
    // 返回验证函数，供手动调用
    window.verifyCoreScenarios = function() {
        console.log('🎯 手动执行核心场景验证...');
        verifyTextChat();
        verifyVoiceRecording();
        verifyVoiceCall();
        verifyStateManagement();
        verifyPerformance();
        return generateReport();
    };
    
    console.log('💡 提示: 可以随时调用 window.verifyCoreScenarios() 来手动验证场景');
    
})();
