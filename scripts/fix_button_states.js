/**
 * 按钮状态修复脚本
 * 修复三个场景下按钮的状态变化逻辑
 */

function fixButtonStates() {
    console.log('🔧 开始修复按钮状态变化逻辑...');
    
    // 检查关键组件
    const components = [
        'unifiedButtonStateManager',
        'voiceStateManager', 
        'voiceRecorder',
        'voicePlayerEnhanced',
        'voiceWebSocketManager'
    ];
    
    let allComponentsReady = true;
    components.forEach(component => {
        if (window[component]) {
            console.log(`✅ ${component} 已加载`);
        } else {
            console.log(`❌ ${component} 未找到`);
            allComponentsReady = false;
        }
    });
    
    if (!allComponentsReady) {
        console.log('❌ 部分组件未加载，无法进行修复');
        return;
    }
    
    // 修复1: 检查状态样式定义
    console.log('\n🔧 修复1: 检查状态样式定义');
    const states = [
        'idle', 'text_processing', 'text_sse', 'text_tts',
        'recording', 'voice_stt', 'voice_sse', 'voice_tts', 
        'voice_call', 'calling', 'processing', 'playing', 'error'
    ];
    
    states.forEach(state => {
        try {
            const styles = window.unifiedButtonStateManager.getStateStyles(state);
            console.log(`${state}:`, {
                textButton: styles.textButton,
                recordButton: styles.recordButton,
                callButton: styles.callButton
            });
        } catch (error) {
            console.log(`❌ ${state} 状态样式获取失败:`, error);
        }
    });
    
    // 修复2: 检查按钮状态变化逻辑
    console.log('\n🔧 修复2: 检查按钮状态变化逻辑');
    
    // 检查文本按钮状态变化
    console.log('📝 文本按钮状态变化检查:');
    const textStates = ['idle', 'text_processing', 'text_sse', 'text_tts'];
    textStates.forEach(state => {
        const buttonState = window.unifiedButtonStateManager.getButtonState('text', state);
        console.log(`  ${state}: ${buttonState.status} (loading: ${buttonState.loading}, disabled: ${buttonState.disabled})`);
    });
    
    // 检查录音按钮状态变化
    console.log('🎤 录音按钮状态变化检查:');
    const recordStates = ['idle', 'recording', 'voice_stt', 'voice_sse', 'voice_tts'];
    recordStates.forEach(state => {
        const buttonState = window.unifiedButtonStateManager.getButtonState('record', state);
        console.log(`  ${state}: ${buttonState.status} (loading: ${buttonState.loading}, disabled: ${buttonState.disabled})`);
    });
    
    // 检查通话按钮状态变化
    console.log('📞 通话按钮状态变化检查:');
    const callStates = ['idle', 'voice_call', 'calling'];
    callStates.forEach(state => {
        const buttonState = window.unifiedButtonStateManager.getButtonState('call', state);
        console.log(`  ${state}: ${buttonState.status} (loading: ${buttonState.loading}, disabled: ${buttonState.disabled})`);
    });
    
    // 修复3: 检查状态转换逻辑
    console.log('\n🔧 修复3: 检查状态转换逻辑');
    
    // 文本聊天场景
    console.log('📝 文本聊天场景状态转换:');
    const textChatFlow = [
        { from: 'idle', to: 'text_processing', action: '点击文本按钮' },
        { from: 'text_processing', to: 'text_sse', action: 'SSE开始' },
        { from: 'text_sse', to: 'text_tts', action: 'SSE结束，TTS开始' },
        { from: 'text_tts', to: 'idle', action: 'TTS播放完成' }
    ];
    
    textChatFlow.forEach(transition => {
        const fromStyles = window.unifiedButtonStateManager.getStateStyles(transition.from);
        const toStyles = window.unifiedButtonStateManager.getStateStyles(transition.to);
        console.log(`  ${transition.from} → ${transition.to} (${transition.action}):`);
        console.log(`    文本按钮: ${fromStyles.textButton.backgroundColor} → ${toStyles.textButton.backgroundColor}`);
        console.log(`    录音按钮: ${fromStyles.recordButton.backgroundColor} → ${toStyles.recordButton.backgroundColor}`);
        console.log(`    通话按钮: ${fromStyles.callButton.backgroundColor} → ${toStyles.callButton.backgroundColor}`);
    });
    
    // 录音聊天场景
    console.log('🎤 录音聊天场景状态转换:');
    const voiceChatFlow = [
        { from: 'idle', to: 'recording', action: '点击录音按钮' },
        { from: 'recording', to: 'voice_stt', action: '停止录音，STT开始' },
        { from: 'voice_stt', to: 'voice_sse', action: 'STT完成，SSE开始' },
        { from: 'voice_sse', to: 'voice_tts', action: 'SSE结束，TTS开始' },
        { from: 'voice_tts', to: 'idle', action: 'TTS播放完成' }
    ];
    
    voiceChatFlow.forEach(transition => {
        const fromStyles = window.unifiedButtonStateManager.getStateStyles(transition.from);
        const toStyles = window.unifiedButtonStateManager.getStateStyles(transition.to);
        console.log(`  ${transition.from} → ${transition.to} (${transition.action}):`);
        console.log(`    文本按钮: ${fromStyles.textButton.backgroundColor} → ${toStyles.textButton.backgroundColor}`);
        console.log(`    录音按钮: ${fromStyles.recordButton.backgroundColor} → ${toStyles.recordButton.backgroundColor}`);
        console.log(`    通话按钮: ${fromStyles.callButton.backgroundColor} → ${toStyles.callButton.backgroundColor}`);
    });
    
    // 语音通话场景
    console.log('📞 语音通话场景状态转换:');
    const voiceCallFlow = [
        { from: 'idle', to: 'voice_call', action: '点击通话按钮' },
        { from: 'voice_call', to: 'idle', action: '点击通话按钮停止' }
    ];
    
    voiceCallFlow.forEach(transition => {
        const fromStyles = window.unifiedButtonStateManager.getStateStyles(transition.from);
        const toStyles = window.unifiedButtonStateManager.getStateStyles(transition.to);
        console.log(`  ${transition.from} → ${transition.to} (${transition.action}):`);
        console.log(`    文本按钮: ${fromStyles.textButton.backgroundColor} → ${toStyles.textButton.backgroundColor}`);
        console.log(`    录音按钮: ${fromStyles.recordButton.backgroundColor} → ${toStyles.recordButton.backgroundColor}`);
        console.log(`    通话按钮: ${fromStyles.callButton.backgroundColor} → ${toStyles.callButton.backgroundColor}`);
    });
    
    // 修复4: 检查按钮元素状态
    console.log('\n🔧 修复4: 检查按钮元素状态');
    const buttons = [
        'ai-chat-x-send-btn',
        'voice-record-button', 
        'voice-call-btn'
    ];
    
    buttons.forEach(buttonId => {
        const button = document.getElementById(buttonId);
        if (button) {
            console.log(`✅ ${buttonId} 已找到`);
            console.log(`   - disabled: ${button.disabled}`);
            console.log(`   - style: ${button.style.backgroundColor}`);
            console.log(`   - loading: ${button.getAttribute('loading')}`);
        } else {
            console.log(`❌ ${buttonId} 未找到`);
        }
    });
    
    // 修复5: 检查状态管理器
    console.log('\n🔧 修复5: 检查状态管理器');
    if (window.unifiedButtonStateManager) {
        const currentState = window.unifiedButtonStateManager.getStateInfo();
        console.log('当前状态:', currentState);
        
        const buttonDetails = window.unifiedButtonStateManager.getButtonStateDetails();
        console.log('按钮状态详情:', buttonDetails);
    }
    
    // 修复6: 检查语音状态管理器
    console.log('\n🔧 修复6: 检查语音状态管理器');
    if (window.voiceStateManager) {
        const currentState = window.voiceStateManager.getCurrentState();
        console.log('语音状态:', currentState);
        
        const stateInfo = window.voiceStateManager.getStateInfo();
        console.log('状态信息:', stateInfo);
    }
    
    // 修复7: 检查录音器状态
    console.log('\n🔧 修复7: 检查录音器状态');
    if (window.voiceRecorder) {
        console.log('录音器状态:', {
            isRecording: window.voiceRecorder.isRecording,
            isProcessing: window.voiceRecorder.isProcessing,
            currentState: window.voiceRecorder.currentState
        });
    }
    
    // 修复8: 检查播放器状态
    console.log('\n🔧 修复8: 检查播放器状态');
    if (window.voicePlayerEnhanced) {
        console.log('播放器状态:', {
            isTtsPlaying: window.voicePlayerEnhanced.isTtsPlaying,
            simplePlaying: window.voicePlayerEnhanced.simplePlaying,
            streamStates: window.voicePlayerEnhanced.streamStates ? window.voicePlayerEnhanced.streamStates.size : 0,
            simpleQueue: window.voicePlayerEnhanced.simpleQueue ? window.voicePlayerEnhanced.simpleQueue.length : 0
        });
    }
    
    console.log('\n🎉 按钮状态修复完成！');
}

// 运行修复
fixButtonStates();
