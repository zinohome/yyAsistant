/**
 * 按钮状态测试脚本
 * 测试三个场景下按钮的状态变化逻辑
 */

function testButtonStates() {
    console.log('🧪 开始测试按钮状态变化逻辑...');
    
    // 检查关键组件
    const components = [
        'unifiedButtonStateManager',
        'voiceStateManager', 
        'voiceRecorder',
        'voicePlayerEnhanced'
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
        console.log('❌ 部分组件未加载，无法进行测试');
        return;
    }
    
    // 测试1: 检查状态管理器
    console.log('\n📊 测试1: 状态管理器检查');
    if (window.unifiedButtonStateManager) {
        const currentState = window.unifiedButtonStateManager.getStateInfo();
        console.log('当前状态:', currentState);
        
        const buttonDetails = window.unifiedButtonStateManager.getButtonStateDetails();
        console.log('按钮状态详情:', buttonDetails);
    }
    
    // 测试2: 检查按钮元素
    console.log('\n📊 测试2: 按钮元素检查');
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
    
    // 测试3: 检查状态样式定义
    console.log('\n📊 测试3: 状态样式定义检查');
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
    
    // 测试4: 检查录音按钮状态变化
    console.log('\n📊 测试4: 录音按钮状态变化检查');
    if (window.voiceRecorder) {
        console.log('录音器状态:', {
            isRecording: window.voiceRecorder.isRecording,
            isProcessing: window.voiceRecorder.isProcessing,
            currentState: window.voiceRecorder.currentState
        });
    }
    
    // 测试5: 检查语音状态管理器
    console.log('\n📊 测试5: 语音状态管理器检查');
    if (window.voiceStateManager) {
        const currentState = window.voiceStateManager.getCurrentState();
        console.log('语音状态:', currentState);
        
        const stateInfo = window.voiceStateManager.getStateInfo();
        console.log('状态信息:', stateInfo);
    }
    
    // 测试6: 检查状态转换逻辑
    console.log('\n📊 测试6: 状态转换逻辑检查');
    const testTransitions = [
        { from: 'idle', to: 'text_processing', scenario: 'text_chat' },
        { from: 'idle', to: 'recording', scenario: 'voice_recording' },
        { from: 'recording', to: 'voice_stt', scenario: 'voice_recording' },
        { from: 'voice_stt', to: 'voice_sse', scenario: 'voice_recording' },
        { from: 'voice_sse', to: 'voice_tts', scenario: 'voice_recording' },
        { from: 'voice_tts', to: 'idle', scenario: 'voice_recording' }
    ];
    
    testTransitions.forEach(transition => {
        try {
            const fromStyles = window.unifiedButtonStateManager.getStateStyles(transition.from);
            const toStyles = window.unifiedButtonStateManager.getStateStyles(transition.to);
            console.log(`${transition.from} → ${transition.to}:`, {
                from: fromStyles,
                to: toStyles,
                scenario: transition.scenario
            });
        } catch (error) {
            console.log(`❌ 状态转换 ${transition.from} → ${transition.to} 失败:`, error);
        }
    });
    
    console.log('\n🎉 按钮状态测试完成！');
}

// 运行测试
testButtonStates();
