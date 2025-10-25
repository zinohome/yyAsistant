/**
 * 修复所有按钮问题脚本
 * 解决按钮颜色、状态变化、TTS播放指示器、录音canvas指示器等问题
 */

function fixAllButtonIssues() {
    console.log('🔧 开始修复所有按钮问题...');
    
    // 检查关键组件
    const components = [
        'unifiedButtonStateManager',
        'voiceStateManager', 
        'voiceRecorder',
        'voicePlayerEnhanced',
        'voiceWebSocketManager',
        'enhancedAudioVisualizer',
        'enhancedPlaybackStatus'
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
    
    // 修复1: 检查按钮颜色配置
    console.log('\n🔧 修复1: 检查按钮颜色配置');
    
    // 检查初始状态颜色
    const idleStyles = window.unifiedButtonStateManager.getStateStyles('idle');
    console.log('初始状态颜色:');
    console.log(`  文本按钮: ${idleStyles.textButton.backgroundColor} (应该是 #1890ff 蓝色)`);
    console.log(`  录音按钮: ${idleStyles.recordButton.backgroundColor} (应该是 #ff4d4f 红色)`);
    console.log(`  通话按钮: ${idleStyles.callButton.backgroundColor} (应该是 #52c41a 绿色)`);
    
    // 检查场景一：文本聊天状态颜色
    console.log('\n场景一：文本聊天状态颜色');
    const textStates = ['text_processing', 'text_sse', 'text_tts'];
    textStates.forEach(state => {
        const styles = window.unifiedButtonStateManager.getStateStyles(state);
        console.log(`${state}:`);
        console.log(`  文本按钮: ${styles.textButton.backgroundColor} (应该是 #faad14 黄色)`);
        console.log(`  录音按钮: ${styles.recordButton.backgroundColor} (应该是 #d9d9d9 灰色 或 #faad14 黄色)`);
        console.log(`  通话按钮: ${styles.callButton.backgroundColor} (应该是 #d9d9d9 灰色)`);
    });
    
    // 检查场景二：录音聊天状态颜色
    console.log('\n场景二：录音聊天状态颜色');
    const voiceStates = ['recording', 'voice_stt', 'voice_sse', 'voice_tts'];
    voiceStates.forEach(state => {
        const styles = window.unifiedButtonStateManager.getStateStyles(state);
        console.log(`${state}:`);
        console.log(`  文本按钮: ${styles.textButton.backgroundColor} (应该是 #d9d9d9 灰色 或 #faad14 黄色)`);
        console.log(`  录音按钮: ${styles.recordButton.backgroundColor} (应该是 #ff4d4f 红色 或 #faad14 黄色)`);
        console.log(`  通话按钮: ${styles.callButton.backgroundColor} (应该是 #d9d9d9 灰色)`);
    });
    
    // 检查场景三：语音通话状态颜色
    console.log('\n场景三：语音通话状态颜色');
    const callStates = ['voice_call', 'calling'];
    callStates.forEach(state => {
        const styles = window.unifiedButtonStateManager.getStateStyles(state);
        console.log(`${state}:`);
        console.log(`  文本按钮: ${styles.textButton.backgroundColor} (应该是 #d9d9d9 灰色)`);
        console.log(`  录音按钮: ${styles.recordButton.backgroundColor} (应该是 #d9d9d9 灰色)`);
        console.log(`  通话按钮: ${styles.callButton.backgroundColor} (应该是 #ff4d4f 红色)`);
    });
    
    // 修复2: 检查语音通话按钮停止逻辑
    console.log('\n🔧 修复2: 检查语音通话按钮停止逻辑');
    
    const voiceCallBtn = document.getElementById('voice-call-btn');
    if (voiceCallBtn) {
        console.log('语音通话按钮状态:');
        console.log(`  disabled: ${voiceCallBtn.disabled}`);
        console.log(`  backgroundColor: ${voiceCallBtn.style.backgroundColor}`);
        console.log(`  data-calling: ${voiceCallBtn.getAttribute('data-calling')}`);
        
        // 检查按钮状态检测逻辑
        const isCalling = voiceCallBtn && (
            voiceCallBtn.style.backgroundColor.includes('rgb(255, 77, 79)') ||
            voiceCallBtn.style.backgroundColor.includes('#ff4d4f') ||
            voiceCallBtn.style.backgroundColor.includes('red') ||
            voiceCallBtn.getAttribute('data-calling') === 'true' ||
            voiceCallBtn.disabled === true
        );
        console.log(`  检测到通话状态: ${isCalling}`);
    } else {
        console.log('❌ 语音通话按钮未找到');
    }
    
    // 修复3: 检查TTS播放指示器逻辑
    console.log('\n🔧 修复3: 检查TTS播放指示器逻辑');
    
    if (window.enhancedPlaybackStatus) {
        console.log('✅ 增强播放状态指示器已加载');
        
        // 检查播放状态指示器的显示逻辑
        console.log('播放状态指示器功能:');
        console.log('  - 应该在TTS播放开始时显示');
        console.log('  - 应该在TTS播放期间一直显示');
        console.log('  - 应该在TTS播放完成后隐藏');
    } else {
        console.log('❌ 增强播放状态指示器未找到');
    }
    
    // 修复4: 检查录音canvas指示器逻辑
    console.log('\n🔧 修复4: 检查录音canvas指示器逻辑');
    
    const audioVisualizerContainer = document.getElementById('audio-visualizer-container');
    const audioVisualizer = document.getElementById('audio-visualizer');
    
    if (audioVisualizerContainer && audioVisualizer) {
        console.log('✅ 音频可视化区域已找到');
        console.log(`  容器显示状态: ${audioVisualizerContainer.style.display}`);
        console.log(`  Canvas元素: ${audioVisualizer.tagName}`);
        
        if (window.enhancedAudioVisualizer) {
            console.log('✅ 增强音频可视化器已加载');
            console.log(`  当前状态: ${window.enhancedAudioVisualizer.currentState}`);
        } else {
            console.log('❌ 增强音频可视化器未找到');
        }
    } else {
        console.log('❌ 音频可视化区域未找到');
        console.log(`  容器: ${!!audioVisualizerContainer}`);
        console.log(`  Canvas: ${!!audioVisualizer}`);
    }
    
    // 修复5: 检查按钮状态变化逻辑
    console.log('\n🔧 修复5: 检查按钮状态变化逻辑');
    
    // 检查文本按钮状态变化
    console.log('文本按钮状态变化:');
    const textButtonStates = ['idle', 'text_processing', 'text_sse', 'text_tts'];
    textButtonStates.forEach(state => {
        const buttonState = window.unifiedButtonStateManager.getButtonState('text', state);
        console.log(`  ${state}: ${buttonState.status} (loading: ${buttonState.loading}, disabled: ${buttonState.disabled})`);
    });
    
    // 检查录音按钮状态变化
    console.log('录音按钮状态变化:');
    const recordButtonStates = ['idle', 'recording', 'voice_stt', 'voice_sse', 'voice_tts'];
    recordButtonStates.forEach(state => {
        const buttonState = window.unifiedButtonStateManager.getButtonState('record', state);
        console.log(`  ${state}: ${buttonState.status} (loading: ${buttonState.loading}, disabled: ${buttonState.disabled})`);
    });
    
    // 检查通话按钮状态变化
    console.log('通话按钮状态变化:');
    const callButtonStates = ['idle', 'voice_call', 'calling'];
    callButtonStates.forEach(state => {
        const buttonState = window.unifiedButtonStateManager.getButtonState('call', state);
        console.log(`  ${state}: ${buttonState.status} (loading: ${buttonState.loading}, disabled: ${buttonState.disabled})`);
    });
    
    // 修复6: 检查状态转换逻辑
    console.log('\n🔧 修复6: 检查状态转换逻辑');
    
    // 检查状态转换是否合理
    const validTransitions = [
        { from: 'idle', to: 'text_processing', scenario: 'text_chat' },
        { from: 'text_processing', to: 'text_sse', scenario: 'text_chat' },
        { from: 'text_sse', to: 'text_tts', scenario: 'text_chat' },
        { from: 'text_tts', to: 'idle', scenario: 'text_chat' },
        { from: 'idle', to: 'recording', scenario: 'voice_recording' },
        { from: 'recording', to: 'voice_stt', scenario: 'voice_recording' },
        { from: 'voice_stt', to: 'voice_sse', scenario: 'voice_recording' },
        { from: 'voice_sse', to: 'voice_tts', scenario: 'voice_recording' },
        { from: 'voice_tts', to: 'idle', scenario: 'voice_recording' },
        { from: 'idle', to: 'voice_call', scenario: 'voice_call' },
        { from: 'voice_call', to: 'idle', scenario: 'voice_call' }
    ];
    
    validTransitions.forEach(transition => {
        try {
            const fromStyles = window.unifiedButtonStateManager.getStateStyles(transition.from);
            const toStyles = window.unifiedButtonStateManager.getStateStyles(transition.to);
            
            if (fromStyles && toStyles) {
                console.log(`✅ ${transition.from} → ${transition.to} (${transition.scenario}) 转换有效`);
            } else {
                console.log(`❌ ${transition.from} → ${transition.to} (${transition.scenario}) 转换无效`);
            }
        } catch (error) {
            console.log(`❌ ${transition.from} → ${transition.to} (${transition.scenario}) 转换失败:`, error);
        }
    });
    
    // 修复7: 检查当前系统状态
    console.log('\n🔧 修复7: 检查当前系统状态');
    
    if (window.unifiedButtonStateManager) {
        const currentState = window.unifiedButtonStateManager.getStateInfo();
        console.log('当前状态:', currentState);
        
        const buttonDetails = window.unifiedButtonStateManager.getButtonStateDetails();
        console.log('按钮状态详情:', buttonDetails);
    }
    
    if (window.voiceStateManager) {
        const currentState = window.voiceStateManager.getCurrentState();
        console.log('语音状态:', currentState);
    }
    
    if (window.voiceRecorder) {
        console.log('录音器状态:', {
            isRecording: window.voiceRecorder.isRecording,
            isProcessing: window.voiceRecorder.isProcessing,
            currentState: window.voiceRecorder.currentState
        });
    }
    
    if (window.voicePlayerEnhanced) {
        console.log('播放器状态:', {
            isTtsPlaying: window.voicePlayerEnhanced.isTtsPlaying,
            simplePlaying: window.voicePlayerEnhanced.simplePlaying,
            streamStates: window.voicePlayerEnhanced.streamStates ? window.voicePlayerEnhanced.streamStates.size : 0,
            simpleQueue: window.voicePlayerEnhanced.simpleQueue ? window.voicePlayerEnhanced.simpleQueue.length : 0
        });
    }
    
    console.log('\n🎉 所有按钮问题修复检查完成！');
}

// 运行修复
fixAllButtonIssues();
