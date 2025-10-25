/**
 * 综合验证脚本
 * 
 * 整合所有验证功能：控制台错误清理、三大核心场景验证、状态管理转换检查
 * 在浏览器控制台中运行此脚本
 */

(function() {
    console.log('🎯 开始综合验证...');
    
    // 验证结果汇总
    const comprehensiveResults = {
        consoleErrors: { status: 'pending', details: [] },
        coreScenarios: { status: 'pending', details: [] },
        stateTransitions: { status: 'pending', details: [] },
        overall: { status: 'pending', score: 0, maxScore: 100 }
    };
    
    // 1. 控制台错误清理
    function cleanupConsoleErrors() {
        console.log('🧹 开始清理控制台错误...');
        const results = [];
        
        // 检查智能错误处理系统
        if (window.smartErrorHandler) {
            results.push('✅ 智能错误处理系统正常');
        } else {
            results.push('❌ 智能错误处理系统未找到');
        }
        
        // 检查状态同步管理器
        if (window.stateSyncManager) {
            results.push('✅ 状态同步管理器正常');
        } else {
            results.push('❌ 状态同步管理器未找到');
        }
        
        // 检查智能状态预测器
        if (window.smartStatePredictor) {
            results.push('✅ 智能状态预测器正常');
        } else {
            results.push('❌ 智能状态预测器未找到');
        }
        
        // 检查音频可视化Canvas
        const audioVisualizer = document.getElementById('audio-visualizer');
        if (audioVisualizer) {
            results.push('✅ 音频可视化Canvas正常');
        } else {
            results.push('❌ 音频可视化Canvas未找到');
        }
        
        // 检查WebSocket连接
        if (window.voiceWebSocketManager && window.voiceWebSocketManager.ws) {
            const ws = window.voiceWebSocketManager.ws;
            if (ws.readyState === WebSocket.OPEN) {
                results.push('✅ WebSocket连接正常');
            } else {
                results.push('❌ WebSocket连接异常');
            }
        } else {
            results.push('❌ WebSocket管理器未找到');
        }
        
        comprehensiveResults.consoleErrors.details = results;
        comprehensiveResults.consoleErrors.status = results.some(r => r.includes('❌')) ? 'failed' : 'passed';
        
        console.log('🧹 控制台错误清理结果:', results);
        return results;
    }
    
    // 2. 三大核心场景验证
    function verifyCoreScenarios() {
        console.log('🎯 开始验证三大核心场景...');
        const results = [];
        
        // 文本聊天场景
        const textChatElements = [
            { id: '#ai-chat-x-input', name: '输入框' },
            { id: '#ai-chat-x-send-btn', name: '发送按钮' },
            { id: '#ai-chat-x-messages-store', name: '消息容器' }
        ];
        
        let textChatScore = 0;
        textChatElements.forEach(element => {
            const el = document.querySelector(element.id);
            if (el) {
                results.push(`✅ ${element.name}存在`);
                textChatScore++;
            } else {
                results.push(`❌ ${element.name}未找到`);
            }
        });
        
        // 语音录制场景
        const voiceRecordingElements = [
            { id: '#ai-chat-x-voice-record-btn', name: '录音按钮' },
            { id: '#audio-visualizer', name: '音频可视化区域' }
        ];
        
        let voiceRecordingScore = 0;
        voiceRecordingElements.forEach(element => {
            const el = document.querySelector(element.id);
            if (el) {
                results.push(`✅ ${element.name}存在`);
                voiceRecordingScore++;
            } else {
                results.push(`❌ ${element.name}未找到`);
            }
        });
        
        // 语音通话场景
        const voiceCallElements = [
            { id: '#ai-chat-x-voice-call-btn', name: '语音通话按钮' }
        ];
        
        let voiceCallScore = 0;
        voiceCallElements.forEach(element => {
            const el = document.querySelector(element.id);
            if (el) {
                results.push(`✅ ${element.name}存在`);
                voiceCallScore++;
            } else {
                results.push(`❌ ${element.name}未找到`);
            }
        });
        
        // 检查核心管理器
        const coreManagers = [
            { name: 'stateManager', obj: window.stateManager },
            { name: 'voicePlayerEnhanced', obj: window.voicePlayerEnhanced },
            { name: 'voiceRecorderEnhanced', obj: window.voiceRecorderEnhanced },
            { name: 'voiceWebSocketManager', obj: window.voiceWebSocketManager }
        ];
        
        let managerScore = 0;
        coreManagers.forEach(manager => {
            if (manager.obj) {
                results.push(`✅ ${manager.name}存在`);
                managerScore++;
            } else {
                results.push(`❌ ${manager.name}未找到`);
            }
        });
        
        // 计算总分
        const totalScore = textChatScore + voiceRecordingScore + voiceCallScore + managerScore;
        const maxScore = textChatElements.length + voiceRecordingElements.length + voiceCallElements.length + coreManagers.length;
        
        comprehensiveResults.coreScenarios.details = results;
        comprehensiveResults.coreScenarios.status = totalScore >= maxScore * 0.8 ? 'passed' : 'failed';
        
        console.log('🎯 三大核心场景验证结果:', results);
        console.log(`📊 场景验证得分: ${totalScore}/${maxScore}`);
        return results;
    }
    
    // 3. 状态管理转换检查
    function verifyStateTransitions() {
        console.log('🔄 开始检查状态管理转换...');
        const results = [];
        
        if (!window.stateManager) {
            results.push('❌ 状态管理器未找到');
            comprehensiveResults.stateTransitions.status = 'failed';
            return results;
        }
        
        try {
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
                results.push(`❌ 状态管理器缺少方法: ${missingMethods.join(', ')}`);
            } else {
                results.push('✅ 状态管理器方法完整');
            }
            
            // 检查状态转换
            const initialState = window.stateManager.getCurrentState();
            results.push(`✅ 当前状态: ${initialState}`);
            
            // 测试状态转换
            const testTransitions = [
                { from: 'idle', to: 'text_sse', name: '文本SSE' },
                { from: 'text_sse', to: 'text_tts', name: '文本TTS' },
                { from: 'text_tts', to: 'idle', name: '返回空闲' }
            ];
            
            let transitionScore = 0;
            testTransitions.forEach(transition => {
                try {
                    window.stateManager.setState(transition.to);
                    const currentState = window.stateManager.getCurrentState();
                    if (currentState === transition.to) {
                        results.push(`✅ ${transition.name}状态转换成功`);
                        transitionScore++;
                    } else {
                        results.push(`❌ ${transition.name}状态转换失败`);
                    }
                } catch (error) {
                    results.push(`❌ ${transition.name}状态转换错误: ${error.message}`);
                }
            });
            
            // 检查状态历史
            const stateHistory = window.stateManager.getStateHistory();
            results.push(`✅ 状态历史记录: ${stateHistory.length}条`);
            
            // 检查状态锁定
            if (typeof window.stateManager.isStateLocked === 'function') {
                const isLocked = window.stateManager.isStateLocked();
                results.push(`✅ 状态锁定检查: ${isLocked ? '已锁定' : '未锁定'}`);
            }
            
            // 计算状态转换得分
            const maxTransitionScore = testTransitions.length;
            const stateTransitionScore = transitionScore / maxTransitionScore;
            
            comprehensiveResults.stateTransitions.details = results;
            comprehensiveResults.stateTransitions.status = stateTransitionScore >= 0.8 ? 'passed' : 'failed';
            
        } catch (error) {
            results.push(`❌ 状态管理转换检查错误: ${error.message}`);
            comprehensiveResults.stateTransitions.status = 'failed';
        }
        
        console.log('🔄 状态管理转换检查结果:', results);
        return results;
    }
    
    // 4. 性能检查
    function checkPerformance() {
        console.log('⚡ 开始性能检查...');
        const results = [];
        
        // 检查内存使用
        if (performance.memory) {
            const memory = performance.memory;
            const usedMB = Math.round(memory.usedJSHeapSize / 1024 / 1024);
            const totalMB = Math.round(memory.totalJSHeapSize / 1024 / 1024);
            const usagePercent = Math.round((usedMB / totalMB) * 100);
            
            if (usagePercent < 50) {
                results.push(`✅ 内存使用正常: ${usedMB}MB / ${totalMB}MB (${usagePercent}%)`);
            } else if (usagePercent < 80) {
                results.push(`⚠️ 内存使用较高: ${usedMB}MB / ${totalMB}MB (${usagePercent}%)`);
            } else {
                results.push(`❌ 内存使用过高: ${usedMB}MB / ${totalMB}MB (${usagePercent}%)`);
            }
        } else {
            results.push('⚠️ 内存信息不可用');
        }
        
        // 检查页面加载时间
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        if (loadTime < 2000) {
            results.push(`✅ 页面加载时间正常: ${loadTime}ms`);
        } else if (loadTime < 5000) {
            results.push(`⚠️ 页面加载时间较慢: ${loadTime}ms`);
        } else {
            results.push(`❌ 页面加载时间过慢: ${loadTime}ms`);
        }
        
        // 检查资源加载
        const resources = performance.getEntriesByType('resource');
        const failedResources = resources.filter(r => r.transferSize === 0 && r.name.includes('bundle'));
        if (failedResources.length === 0) {
            results.push('✅ 资源加载正常');
        } else {
            results.push(`❌ 资源加载失败: ${failedResources.length}个`);
        }
        
        console.log('⚡ 性能检查结果:', results);
        return results;
    }
    
    // 5. 生成综合报告
    function generateComprehensiveReport() {
        console.log('📋 生成综合验证报告...');
        
        // 计算总分
        let totalScore = 0;
        let maxScore = 0;
        
        // 控制台错误清理 (30分)
        maxScore += 30;
        if (comprehensiveResults.consoleErrors.status === 'passed') {
            totalScore += 30;
        } else if (comprehensiveResults.consoleErrors.status === 'failed') {
            totalScore += 0;
        } else {
            totalScore += 15;
        }
        
        // 三大核心场景 (40分)
        maxScore += 40;
        if (comprehensiveResults.coreScenarios.status === 'passed') {
            totalScore += 40;
        } else if (comprehensiveResults.coreScenarios.status === 'failed') {
            totalScore += 0;
        } else {
            totalScore += 20;
        }
        
        // 状态管理转换 (30分)
        maxScore += 30;
        if (comprehensiveResults.stateTransitions.status === 'passed') {
            totalScore += 30;
        } else if (comprehensiveResults.stateTransitions.status === 'failed') {
            totalScore += 0;
        } else {
            totalScore += 15;
        }
        
        comprehensiveResults.overall.score = totalScore;
        comprehensiveResults.overall.maxScore = maxScore;
        comprehensiveResults.overall.status = totalScore >= maxScore * 0.8 ? 'excellent' : 
                                             totalScore >= maxScore * 0.6 ? 'good' : 
                                             totalScore >= maxScore * 0.4 ? 'fair' : 'poor';
        
        console.log('📊 综合验证报告:', comprehensiveResults);
        
        // 生成建议
        const suggestions = [];
        if (comprehensiveResults.consoleErrors.status === 'failed') {
            suggestions.push('🔧 需要修复控制台错误');
        }
        if (comprehensiveResults.coreScenarios.status === 'failed') {
            suggestions.push('🔧 需要修复核心场景功能');
        }
        if (comprehensiveResults.stateTransitions.status === 'failed') {
            suggestions.push('🔧 需要修复状态管理转换');
        }
        
        if (suggestions.length > 0) {
            console.log('💡 修复建议:', suggestions);
        } else {
            console.log('🎉 所有验证通过！系统运行正常！');
        }
        
        return comprehensiveResults;
    }
    
    // 执行所有验证
    console.log('🚀 开始执行综合验证...');
    
    cleanupConsoleErrors();
    verifyCoreScenarios();
    verifyStateTransitions();
    checkPerformance();
    
    // 生成最终报告
    setTimeout(() => {
        const report = generateComprehensiveReport();
        console.log('✅ 综合验证完成！');
        console.log('📊 最终报告:', report);
        
        // 保存报告到本地存储
        localStorage.setItem('verificationReport', JSON.stringify(report));
        console.log('💾 验证报告已保存到本地存储');
        
    }, 3000);
    
    // 返回验证函数，供手动调用
    window.runComprehensiveVerification = function() {
        console.log('🎯 手动执行综合验证...');
        cleanupConsoleErrors();
        verifyCoreScenarios();
        verifyStateTransitions();
        checkPerformance();
        return generateComprehensiveReport();
    };
    
    // 返回单独验证函数
    window.cleanupConsoleErrors = function() {
        return cleanupConsoleErrors();
    };
    
    window.verifyCoreScenarios = function() {
        return verifyCoreScenarios();
    };
    
    window.verifyStateTransitions = function() {
        return verifyStateTransitions();
    };
    
    window.checkPerformance = function() {
        return checkPerformance();
    };
    
    console.log('💡 提示: 可以随时调用以下函数来手动验证:');
    console.log('  - window.runComprehensiveVerification() - 综合验证');
    console.log('  - window.cleanupConsoleErrors() - 控制台错误清理');
    console.log('  - window.verifyCoreScenarios() - 三大核心场景验证');
    console.log('  - window.verifyStateTransitions() - 状态管理转换检查');
    console.log('  - window.checkPerformance() - 性能检查');
    
})();
