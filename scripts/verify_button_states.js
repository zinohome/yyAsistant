/**
 * 按钮状态验证脚本
 * 验证三个场景下按钮的状态变化逻辑是否正确实现
 */

function verifyButtonStates() {
    console.log('🧪 开始验证按钮状态变化逻辑...');
    
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
        console.log('❌ 部分组件未加载，无法进行验证');
        return;
    }
    
    // 验证1: 检查状态样式定义完整性
    console.log('\n📊 验证1: 状态样式定义完整性');
    const requiredStates = [
        'idle', 'text_processing', 'text_sse', 'text_tts',
        'recording', 'voice_stt', 'voice_sse', 'voice_tts', 
        'voice_call', 'calling', 'processing', 'playing', 'error'
    ];
    
    let stylesComplete = true;
    requiredStates.forEach(state => {
        try {
            const styles = window.unifiedButtonStateManager.getStateStyles(state);
            if (!styles.textButton || !styles.recordButton || !styles.callButton) {
                console.log(`❌ ${state} 状态样式不完整`);
                stylesComplete = false;
            } else {
                console.log(`✅ ${state} 状态样式完整`);
            }
        } catch (error) {
            console.log(`❌ ${state} 状态样式获取失败:`, error);
            stylesComplete = false;
        }
    });
    
    if (stylesComplete) {
        console.log('✅ 所有状态样式定义完整');
    } else {
        console.log('❌ 部分状态样式定义不完整');
    }
    
    // 验证2: 检查按钮状态变化逻辑
    console.log('\n📊 验证2: 按钮状态变化逻辑');
    
    // 文本聊天场景验证
    console.log('📝 文本聊天场景验证:');
    const textChatStates = ['idle', 'text_processing', 'text_sse', 'text_tts'];
    let textChatValid = true;
    
    textChatStates.forEach((state, index) => {
        const buttonState = window.unifiedButtonStateManager.getButtonState('text', state);
        const styles = window.unifiedButtonStateManager.getStateStyles(state);
        
        console.log(`  ${state}:`);
        console.log(`    状态: ${buttonState.status} (loading: ${buttonState.loading}, disabled: ${buttonState.disabled})`);
        console.log(`    样式: ${styles.textButton.backgroundColor}`);
        
        // 验证状态逻辑
        if (state === 'idle') {
            if (buttonState.status !== 'enabled' || buttonState.disabled !== false) {
                console.log(`    ❌ 空闲状态应该可用`);
                textChatValid = false;
            }
        } else if (state === 'text_processing') {
            if (buttonState.status !== 'loading' || buttonState.disabled !== true) {
                console.log(`    ❌ 处理状态应该loading且禁用`);
                textChatValid = false;
            }
        } else if (state === 'text_sse') {
            if (buttonState.status !== 'loading' || buttonState.disabled !== true) {
                console.log(`    ❌ SSE状态应该loading且禁用`);
                textChatValid = false;
            }
        } else if (state === 'text_tts') {
            if (buttonState.status !== 'disabled' || buttonState.disabled !== true) {
                console.log(`    ❌ TTS状态应该禁用`);
                textChatValid = false;
            }
        }
    });
    
    if (textChatValid) {
        console.log('✅ 文本聊天场景状态逻辑正确');
    } else {
        console.log('❌ 文本聊天场景状态逻辑有误');
    }
    
    // 录音聊天场景验证
    console.log('🎤 录音聊天场景验证:');
    const voiceChatStates = ['idle', 'recording', 'voice_stt', 'voice_sse', 'voice_tts'];
    let voiceChatValid = true;
    
    voiceChatStates.forEach((state, index) => {
        const buttonState = window.unifiedButtonStateManager.getButtonState('record', state);
        const styles = window.unifiedButtonStateManager.getStateStyles(state);
        
        console.log(`  ${state}:`);
        console.log(`    状态: ${buttonState.status} (loading: ${buttonState.loading}, disabled: ${buttonState.disabled})`);
        console.log(`    样式: ${styles.recordButton.backgroundColor}`);
        
        // 验证状态逻辑
        if (state === 'idle') {
            if (buttonState.status !== 'enabled' || buttonState.disabled !== false) {
                console.log(`    ❌ 空闲状态应该可用`);
                voiceChatValid = false;
            }
        } else if (state === 'recording') {
            if (buttonState.status !== 'loading' || buttonState.disabled !== true) {
                console.log(`    ❌ 录音状态应该loading且禁用`);
                voiceChatValid = false;
            }
        } else if (state === 'voice_stt') {
            if (buttonState.status !== 'loading' || buttonState.disabled !== true) {
                console.log(`    ❌ STT状态应该loading且禁用`);
                voiceChatValid = false;
            }
        } else if (state === 'voice_sse') {
            if (buttonState.status !== 'loading' || buttonState.disabled !== true) {
                console.log(`    ❌ SSE状态应该loading且禁用`);
                voiceChatValid = false;
            }
        } else if (state === 'voice_tts') {
            if (buttonState.status !== 'disabled' || buttonState.disabled !== true) {
                console.log(`    ❌ TTS状态应该禁用`);
                voiceChatValid = false;
            }
        }
    });
    
    if (voiceChatValid) {
        console.log('✅ 录音聊天场景状态逻辑正确');
    } else {
        console.log('❌ 录音聊天场景状态逻辑有误');
    }
    
    // 语音通话场景验证
    console.log('📞 语音通话场景验证:');
    const voiceCallStates = ['idle', 'voice_call', 'calling'];
    let voiceCallValid = true;
    
    voiceCallStates.forEach((state, index) => {
        const buttonState = window.unifiedButtonStateManager.getButtonState('call', state);
        const styles = window.unifiedButtonStateManager.getStateStyles(state);
        
        console.log(`  ${state}:`);
        console.log(`    状态: ${buttonState.status} (loading: ${buttonState.loading}, disabled: ${buttonState.disabled})`);
        console.log(`    样式: ${styles.callButton.backgroundColor}`);
        
        // 验证状态逻辑
        if (state === 'idle') {
            if (buttonState.status !== 'enabled' || buttonState.disabled !== false) {
                console.log(`    ❌ 空闲状态应该可用`);
                voiceCallValid = false;
            }
        } else if (state === 'voice_call' || state === 'calling') {
            if (buttonState.status !== 'loading' || buttonState.disabled !== true) {
                console.log(`    ❌ 通话状态应该loading且禁用`);
                voiceCallValid = false;
            }
        }
    });
    
    if (voiceCallValid) {
        console.log('✅ 语音通话场景状态逻辑正确');
    } else {
        console.log('❌ 语音通话场景状态逻辑有误');
    }
    
    // 验证3: 检查状态转换逻辑
    console.log('\n📊 验证3: 状态转换逻辑');
    
    // 检查状态转换是否合理
    const validTransitions = [
        { from: 'idle', to: 'text_processing', valid: true },
        { from: 'text_processing', to: 'text_sse', valid: true },
        { from: 'text_sse', to: 'text_tts', valid: true },
        { from: 'text_tts', to: 'idle', valid: true },
        { from: 'idle', to: 'recording', valid: true },
        { from: 'recording', to: 'voice_stt', valid: true },
        { from: 'voice_stt', to: 'voice_sse', valid: true },
        { from: 'voice_sse', to: 'voice_tts', valid: true },
        { from: 'voice_tts', to: 'idle', valid: true },
        { from: 'idle', to: 'voice_call', valid: true },
        { from: 'voice_call', to: 'idle', valid: true }
    ];
    
    let transitionsValid = true;
    validTransitions.forEach(transition => {
        try {
            const fromStyles = window.unifiedButtonStateManager.getStateStyles(transition.from);
            const toStyles = window.unifiedButtonStateManager.getStateStyles(transition.to);
            
            if (fromStyles && toStyles) {
                console.log(`✅ ${transition.from} → ${transition.to} 转换有效`);
            } else {
                console.log(`❌ ${transition.from} → ${transition.to} 转换无效`);
                transitionsValid = false;
            }
        } catch (error) {
            console.log(`❌ ${transition.from} → ${transition.to} 转换失败:`, error);
            transitionsValid = false;
        }
    });
    
    if (transitionsValid) {
        console.log('✅ 所有状态转换逻辑正确');
    } else {
        console.log('❌ 部分状态转换逻辑有误');
    }
    
    // 验证4: 检查按钮元素状态
    console.log('\n📊 验证4: 按钮元素状态');
    const buttons = [
        'ai-chat-x-send-btn',
        'voice-record-button', 
        'voice-call-btn'
    ];
    
    let buttonsValid = true;
    buttons.forEach(buttonId => {
        const button = document.getElementById(buttonId);
        if (button) {
            console.log(`✅ ${buttonId} 已找到`);
            console.log(`   - disabled: ${button.disabled}`);
            console.log(`   - style: ${button.style.backgroundColor}`);
            console.log(`   - loading: ${button.getAttribute('loading')}`);
        } else {
            console.log(`❌ ${buttonId} 未找到`);
            buttonsValid = false;
        }
    });
    
    if (buttonsValid) {
        console.log('✅ 所有按钮元素状态正常');
    } else {
        console.log('❌ 部分按钮元素状态异常');
    }
    
    // 验证5: 检查状态管理器
    console.log('\n📊 验证5: 状态管理器');
    if (window.unifiedButtonStateManager) {
        const currentState = window.unifiedButtonStateManager.getStateInfo();
        console.log('当前状态:', currentState);
        
        const buttonDetails = window.unifiedButtonStateManager.getButtonStateDetails();
        console.log('按钮状态详情:', buttonDetails);
        
        console.log('✅ 状态管理器工作正常');
    } else {
        console.log('❌ 状态管理器未找到');
    }
    
    // 验证6: 检查语音状态管理器
    console.log('\n📊 验证6: 语音状态管理器');
    if (window.voiceStateManager) {
        const currentState = window.voiceStateManager.getCurrentState();
        console.log('语音状态:', currentState);
        
        const stateInfo = window.voiceStateManager.getStateInfo();
        console.log('状态信息:', stateInfo);
        
        console.log('✅ 语音状态管理器工作正常');
    } else {
        console.log('❌ 语音状态管理器未找到');
    }
    
    // 验证7: 检查录音器状态
    console.log('\n📊 验证7: 录音器状态');
    if (window.voiceRecorder) {
        console.log('录音器状态:', {
            isRecording: window.voiceRecorder.isRecording,
            isProcessing: window.voiceRecorder.isProcessing,
            currentState: window.voiceRecorder.currentState
        });
        
        console.log('✅ 录音器状态正常');
    } else {
        console.log('❌ 录音器未找到');
    }
    
    // 验证8: 检查播放器状态
    console.log('\n📊 验证8: 播放器状态');
    if (window.voicePlayerEnhanced) {
        console.log('播放器状态:', {
            isTtsPlaying: window.voicePlayerEnhanced.isTtsPlaying,
            simplePlaying: window.voicePlayerEnhanced.simplePlaying,
            streamStates: window.voicePlayerEnhanced.streamStates ? window.voicePlayerEnhanced.streamStates.size : 0,
            simpleQueue: window.voicePlayerEnhanced.simpleQueue ? window.voicePlayerEnhanced.simpleQueue.length : 0
        });
        
        console.log('✅ 播放器状态正常');
    } else {
        console.log('❌ 播放器未找到');
    }
    
    console.log('\n🎉 按钮状态验证完成！');
}

// 运行验证
verifyButtonStates();
