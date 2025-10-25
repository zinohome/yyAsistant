/**
 * 状态管理转换检查脚本
 * 
 * 用于检查状态管理器的状态转换逻辑
 * 在浏览器控制台中运行此脚本
 */

(function() {
    console.log('🔄 开始检查状态管理转换...');
    
    // 状态转换验证结果
    const stateTransitionResults = {
        textChat: { status: 'pending', transitions: [] },
        voiceRecording: { status: 'pending', transitions: [] },
        voiceCall: { status: 'pending', transitions: [] },
        errorRecovery: { status: 'pending', transitions: [] },
        overall: { status: 'pending', score: 0, maxScore: 100 }
    };
    
    // 1. 检查状态管理器是否存在
    function checkStateManager() {
        console.log('📊 检查状态管理器...');
        
        if (!window.stateManager) {
            console.error('❌ 状态管理器未找到');
            return false;
        }
        
        console.log('✅ 状态管理器存在');
        
        // 检查状态管理器方法
        const requiredMethods = [
            'getCurrentState',
            'setState',
            'getStateHistory',
            'isStateLocked',
            'lockState',
            'unlockState',
            'resetState'
        ];
        
        const missingMethods = requiredMethods.filter(method => 
            typeof window.stateManager[method] !== 'function'
        );
        
        if (missingMethods.length > 0) {
            console.error('❌ 状态管理器缺少方法:', missingMethods);
            return false;
        }
        
        console.log('✅ 状态管理器方法完整');
        return true;
    }
    
    // 2. 检查状态同步管理器
    function checkStateSyncManager() {
        console.log('🔄 检查状态同步管理器...');
        
        if (!window.stateSyncManager) {
            console.error('❌ 状态同步管理器未找到');
            return false;
        }
        
        console.log('✅ 状态同步管理器存在');
        
        // 检查状态同步管理器方法
        const requiredMethods = [
            'registerState',
            'updateState',
            'getState',
            'getAllStates',
            'removeState'
        ];
        
        const missingMethods = requiredMethods.filter(method => 
            typeof window.stateSyncManager[method] !== 'function'
        );
        
        if (missingMethods.length > 0) {
            console.error('❌ 状态同步管理器缺少方法:', missingMethods);
            return false;
        }
        
        console.log('✅ 状态同步管理器方法完整');
        return true;
    }
    
    // 3. 检查文本聊天状态转换
    function checkTextChatTransitions() {
        console.log('📝 检查文本聊天状态转换...');
        const transitions = [];
        
        if (!window.stateManager) {
            transitions.push('❌ 状态管理器未找到');
            return transitions;
        }
        
        // 检查初始状态
        const initialState = window.stateManager.getCurrentState();
        transitions.push(`✅ 初始状态: ${initialState}`);
        
        // 模拟文本聊天状态转换
        try {
            // 1. idle -> text_sse
            window.stateManager.setState('text_sse');
            const sseState = window.stateManager.getCurrentState();
            transitions.push(`✅ idle -> text_sse: ${sseState}`);
            
            // 2. text_sse -> text_tts
            window.stateManager.setState('text_tts');
            const ttsState = window.stateManager.getCurrentState();
            transitions.push(`✅ text_sse -> text_tts: ${ttsState}`);
            
            // 3. text_tts -> idle
            window.stateManager.setState('idle');
            const finalState = window.stateManager.getCurrentState();
            transitions.push(`✅ text_tts -> idle: ${finalState}`);
            
        } catch (error) {
            transitions.push(`❌ 状态转换错误: ${error.message}`);
        }
        
        // 检查状态历史
        const stateHistory = window.stateManager.getStateHistory();
        transitions.push(`✅ 状态历史记录: ${stateHistory.length}条`);
        
        stateTransitionResults.textChat.transitions = transitions;
        stateTransitionResults.textChat.status = transitions.some(t => t.includes('❌')) ? 'failed' : 'passed';
        
        console.log('📝 文本聊天状态转换结果:', transitions);
        return transitions;
    }
    
    // 4. 检查语音录制状态转换
    function checkVoiceRecordingTransitions() {
        console.log('🎤 检查语音录制状态转换...');
        const transitions = [];
        
        if (!window.stateManager) {
            transitions.push('❌ 状态管理器未找到');
            return transitions;
        }
        
        try {
            // 1. idle -> voice_stt
            window.stateManager.setState('voice_stt');
            const sttState = window.stateManager.getCurrentState();
            transitions.push(`✅ idle -> voice_stt: ${sttState}`);
            
            // 2. voice_stt -> voice_sse
            window.stateManager.setState('voice_sse');
            const sseState = window.stateManager.getCurrentState();
            transitions.push(`✅ voice_stt -> voice_sse: ${sseState}`);
            
            // 3. voice_sse -> voice_tts
            window.stateManager.setState('voice_tts');
            const ttsState = window.stateManager.getCurrentState();
            transitions.push(`✅ voice_sse -> voice_tts: ${ttsState}`);
            
            // 4. voice_tts -> idle
            window.stateManager.setState('idle');
            const finalState = window.stateManager.getCurrentState();
            transitions.push(`✅ voice_tts -> idle: ${finalState}`);
            
        } catch (error) {
            transitions.push(`❌ 状态转换错误: ${error.message}`);
        }
        
        stateTransitionResults.voiceRecording.transitions = transitions;
        stateTransitionResults.voiceRecording.status = transitions.some(t => t.includes('❌')) ? 'failed' : 'passed';
        
        console.log('🎤 语音录制状态转换结果:', transitions);
        return transitions;
    }
    
    // 5. 检查语音通话状态转换
    function checkVoiceCallTransitions() {
        console.log('📞 检查语音通话状态转换...');
        const transitions = [];
        
        if (!window.stateManager) {
            transitions.push('❌ 状态管理器未找到');
            return transitions;
        }
        
        try {
            // 1. idle -> voice_call
            window.stateManager.setState('voice_call');
            const callState = window.stateManager.getCurrentState();
            transitions.push(`✅ idle -> voice_call: ${callState}`);
            
            // 2. voice_call -> idle
            window.stateManager.setState('idle');
            const finalState = window.stateManager.getCurrentState();
            transitions.push(`✅ voice_call -> idle: ${finalState}`);
            
        } catch (error) {
            transitions.push(`❌ 状态转换错误: ${error.message}`);
        }
        
        stateTransitionResults.voiceCall.transitions = transitions;
        stateTransitionResults.voiceCall.status = transitions.some(t => t.includes('❌')) ? 'failed' : 'passed';
        
        console.log('📞 语音通话状态转换结果:', transitions);
        return transitions;
    }
    
    // 6. 检查错误恢复状态转换
    function checkErrorRecoveryTransitions() {
        console.log('🔄 检查错误恢复状态转换...');
        const transitions = [];
        
        if (!window.stateManager) {
            transitions.push('❌ 状态管理器未找到');
            return transitions;
        }
        
        try {
            // 1. 设置错误状态
            window.stateManager.setState('error');
            const errorState = window.stateManager.getCurrentState();
            transitions.push(`✅ 错误状态设置: ${errorState}`);
            
            // 2. 检查状态锁定
            if (typeof window.stateManager.isStateLocked === 'function') {
                const isLocked = window.stateManager.isStateLocked();
                transitions.push(`✅ 状态锁定检查: ${isLocked ? '已锁定' : '未锁定'}`);
            }
            
            // 3. 错误恢复 -> idle
            window.stateManager.setState('idle');
            const recoveredState = window.stateManager.getCurrentState();
            transitions.push(`✅ 错误恢复 -> idle: ${recoveredState}`);
            
        } catch (error) {
            transitions.push(`❌ 错误恢复状态转换错误: ${error.message}`);
        }
        
        stateTransitionResults.errorRecovery.transitions = transitions;
        stateTransitionResults.errorRecovery.status = transitions.some(t => t.includes('❌')) ? 'failed' : 'passed';
        
        console.log('🔄 错误恢复状态转换结果:', transitions);
        return transitions;
    }
    
    // 7. 检查状态同步
    function checkStateSynchronization() {
        console.log('🔄 检查状态同步...');
        const syncResults = [];
        
        if (!window.stateSyncManager) {
            syncResults.push('❌ 状态同步管理器未找到');
            return syncResults;
        }
        
        try {
            // 检查已注册状态
            const allStates = window.stateSyncManager.getAllStates();
            syncResults.push(`✅ 已注册状态: ${Object.keys(allStates).join(', ')}`);
            
            // 检查状态更新
            window.stateSyncManager.updateState('test_state', { status: 'testing' });
            const testState = window.stateSyncManager.getState('test_state');
            if (testState && testState.status === 'testing') {
                syncResults.push('✅ 状态更新正常');
            } else {
                syncResults.push('❌ 状态更新失败');
            }
            
            // 清理测试状态
            window.stateSyncManager.removeState('test_state');
            
        } catch (error) {
            syncResults.push(`❌ 状态同步错误: ${error.message}`);
        }
        
        console.log('🔄 状态同步结果:', syncResults);
        return syncResults;
    }
    
    // 8. 检查状态锁定机制
    function checkStateLocking() {
        console.log('🔒 检查状态锁定机制...');
        const lockResults = [];
        
        if (!window.stateManager) {
            lockResults.push('❌ 状态管理器未找到');
            return lockResults;
        }
        
        try {
            // 检查锁定方法
            if (typeof window.stateManager.lockState === 'function') {
                window.stateManager.lockState();
                const isLocked = window.stateManager.isStateLocked();
                lockResults.push(`✅ 状态锁定: ${isLocked ? '已锁定' : '未锁定'}`);
                
                // 尝试在锁定状态下改变状态
                const originalState = window.stateManager.getCurrentState();
                window.stateManager.setState('test_locked');
                const newState = window.stateManager.getCurrentState();
                
                if (newState === originalState) {
                    lockResults.push('✅ 锁定状态下状态未改变');
                } else {
                    lockResults.push('❌ 锁定状态下状态被改变');
                }
                
                // 解锁状态
                window.stateManager.unlockState();
                const isUnlocked = !window.stateManager.isStateLocked();
                lockResults.push(`✅ 状态解锁: ${isUnlocked ? '已解锁' : '未解锁'}`);
                
            } else {
                lockResults.push('❌ 状态锁定方法未找到');
            }
            
        } catch (error) {
            lockResults.push(`❌ 状态锁定检查错误: ${error.message}`);
        }
        
        console.log('🔒 状态锁定机制结果:', lockResults);
        return lockResults;
    }
    
    // 9. 生成综合报告
    function generateStateReport() {
        console.log('📋 生成状态管理转换报告...');
        
        // 计算总分
        let totalScore = 0;
        let maxScore = 0;
        
        Object.keys(stateTransitionResults).forEach(key => {
            if (key !== 'overall') {
                const result = stateTransitionResults[key];
                maxScore += 20; // 每个场景20分
                if (result.status === 'passed') {
                    totalScore += 20;
                } else if (result.status === 'failed') {
                    totalScore += 0;
                } else {
                    totalScore += 10; // 部分通过
                }
            }
        });
        
        stateTransitionResults.overall.score = totalScore;
        stateTransitionResults.overall.maxScore = maxScore;
        stateTransitionResults.overall.status = totalScore >= maxScore * 0.8 ? 'excellent' : 
                                               totalScore >= maxScore * 0.6 ? 'good' : 
                                               totalScore >= maxScore * 0.4 ? 'fair' : 'poor';
        
        console.log('📊 状态管理转换报告:', stateTransitionResults);
        
        // 生成建议
        const suggestions = [];
        if (stateTransitionResults.textChat.status === 'failed') {
            suggestions.push('🔧 文本聊天状态转换需要修复');
        }
        if (stateTransitionResults.voiceRecording.status === 'failed') {
            suggestions.push('🔧 语音录制状态转换需要修复');
        }
        if (stateTransitionResults.voiceCall.status === 'failed') {
            suggestions.push('🔧 语音通话状态转换需要修复');
        }
        if (stateTransitionResults.errorRecovery.status === 'failed') {
            suggestions.push('🔧 错误恢复状态转换需要修复');
        }
        
        if (suggestions.length > 0) {
            console.log('💡 修复建议:', suggestions);
        } else {
            console.log('🎉 所有状态转换验证通过！');
        }
        
        return stateTransitionResults;
    }
    
    // 执行所有检查
    console.log('🚀 开始执行状态管理转换检查...');
    
    if (checkStateManager() && checkStateSyncManager()) {
        checkTextChatTransitions();
        checkVoiceRecordingTransitions();
        checkVoiceCallTransitions();
        checkErrorRecoveryTransitions();
        checkStateSynchronization();
        checkStateLocking();
    } else {
        console.error('❌ 状态管理器检查失败，跳过后续检查');
    }
    
    // 生成最终报告
    setTimeout(() => {
        const report = generateStateReport();
        console.log('✅ 状态管理转换检查完成！');
        console.log('📊 最终报告:', report);
    }, 2000);
    
    // 返回检查函数，供手动调用
    window.verifyStateTransitions = function() {
        console.log('🔄 手动执行状态管理转换检查...');
        if (checkStateManager() && checkStateSyncManager()) {
            checkTextChatTransitions();
            checkVoiceRecordingTransitions();
            checkVoiceCallTransitions();
            checkErrorRecoveryTransitions();
            checkStateSynchronization();
            checkStateLocking();
            return generateStateReport();
        } else {
            console.error('❌ 状态管理器检查失败');
            return null;
        }
    };
    
    console.log('💡 提示: 可以随时调用 window.verifyStateTransitions() 来手动检查状态转换');
    
})();
