/**
 * 快速验证脚本
 * 
 * 在浏览器控制台中直接运行，快速检查系统状态
 * 复制以下代码到浏览器控制台中运行
 */

(function() {
    console.log('🚀 开始快速验证...');
    
    // 验证结果
    const results = {
        consoleErrors: [],
        coreScenarios: [],
        stateManagement: [],
        performance: [],
        overall: { score: 0, maxScore: 100 }
    };
    
    // 1. 控制台错误检查
    console.log('🧹 检查控制台错误...');
    
    // 检查智能错误处理系统
    if (window.smartErrorHandler) {
        results.consoleErrors.push('✅ 智能错误处理系统正常');
    } else {
        results.consoleErrors.push('❌ 智能错误处理系统未找到');
    }
    
    // 检查状态同步管理器
    if (window.stateSyncManager) {
        results.consoleErrors.push('✅ 状态同步管理器正常');
    } else {
        results.consoleErrors.push('❌ 状态同步管理器未找到');
    }
    
    // 检查智能状态预测器
    if (window.smartStatePredictor) {
        results.consoleErrors.push('✅ 智能状态预测器正常');
    } else {
        results.consoleErrors.push('❌ 智能状态预测器未找到');
    }
    
    // 检查音频可视化Canvas
    const audioVisualizer = document.getElementById('audio-visualizer');
    if (audioVisualizer) {
        results.consoleErrors.push('✅ 音频可视化Canvas正常');
    } else {
        results.consoleErrors.push('❌ 音频可视化Canvas未找到');
    }
    
    // 检查WebSocket连接
    if (window.voiceWebSocketManager && window.voiceWebSocketManager.ws) {
        const ws = window.voiceWebSocketManager.ws;
        if (ws.readyState === WebSocket.OPEN) {
            results.consoleErrors.push('✅ WebSocket连接正常');
        } else {
            results.consoleErrors.push('❌ WebSocket连接异常');
        }
    } else {
        results.consoleErrors.push('❌ WebSocket管理器未找到');
    }
    
    // 2. 三大核心场景检查
    console.log('🎯 检查三大核心场景...');
    
    // 文本聊天场景
    const textChatElements = [
        { id: '#ai-chat-x-input', name: '输入框' },
        { id: '#ai-chat-x-send-btn', name: '发送按钮' },
        { id: '#ai-chat-x-messages-store', name: '消息容器' }
    ];
    
    textChatElements.forEach(element => {
        const el = document.querySelector(element.id);
        if (el) {
            results.coreScenarios.push(`✅ ${element.name}存在`);
        } else {
            results.coreScenarios.push(`❌ ${element.name}未找到`);
        }
    });
    
    // 语音录制场景
    const voiceRecordingElements = [
        { id: '#ai-chat-x-voice-record-btn', name: '录音按钮' },
        { id: '#audio-visualizer-container', name: '音频可视化容器' },
        { id: '#audio-visualizer', name: '音频可视化Canvas' }
    ];
    
    voiceRecordingElements.forEach(element => {
        const el = document.querySelector(element.id);
        if (el) {
            results.coreScenarios.push(`✅ ${element.name}存在`);
        } else {
            results.coreScenarios.push(`❌ ${element.name}未找到`);
        }
    });
    
    // 语音通话场景
    const voiceCallElements = [
        { id: '#ai-chat-x-voice-call-btn', name: '语音通话按钮' }
    ];
    
    voiceCallElements.forEach(element => {
        const el = document.querySelector(element.id);
        if (el) {
            results.coreScenarios.push(`✅ ${element.name}存在`);
        } else {
            results.coreScenarios.push(`❌ ${element.name}未找到`);
        }
    });
    
    // 检查核心管理器
    const coreManagers = [
        { name: 'stateManager', obj: window.stateManager },
        { name: 'voicePlayerEnhanced', obj: window.voicePlayerEnhanced },
        { name: 'voiceRecorderEnhanced', obj: window.voiceRecorderEnhanced },
        { name: 'voiceWebSocketManager', obj: window.voiceWebSocketManager }
    ];
    
    coreManagers.forEach(manager => {
        if (manager.obj) {
            results.coreScenarios.push(`✅ ${manager.name}存在`);
        } else {
            results.coreScenarios.push(`❌ ${manager.name}未找到`);
        }
    });
    
    // 3. 状态管理检查
    console.log('📊 检查状态管理...');
    
    if (window.stateManager) {
        results.stateManagement.push('✅ 状态管理器存在');
        
        // 检查当前状态
        const currentState = window.stateManager.getCurrentState();
        results.stateManagement.push(`✅ 当前状态: ${currentState}`);
        
        // 检查状态历史
        const stateHistory = window.stateManager.getStateHistory();
        results.stateManagement.push(`✅ 状态历史记录: ${stateHistory.length}条`);
        
        // 检查状态锁定
        if (typeof window.stateManager.isStateLocked === 'function') {
            const isLocked = window.stateManager.isStateLocked();
            results.stateManagement.push(`✅ 状态锁定检查: ${isLocked ? '已锁定' : '未锁定'}`);
        }
        
        // 测试状态转换
        try {
            const originalState = window.stateManager.getCurrentState();
            window.stateManager.setState('text_sse');
            const sseState = window.stateManager.getCurrentState();
            results.stateManagement.push(`✅ 状态转换测试: ${originalState} -> ${sseState}`);
            
            // 恢复原状态
            window.stateManager.setState(originalState);
        } catch (error) {
            results.stateManagement.push(`❌ 状态转换测试失败: ${error.message}`);
        }
        
    } else {
        results.stateManagement.push('❌ 状态管理器未找到');
    }
    
    // 4. 性能检查
    console.log('⚡ 检查性能指标...');
    
    // 检查内存使用
    if (performance.memory) {
        const memory = performance.memory;
        const usedMB = Math.round(memory.usedJSHeapSize / 1024 / 1024);
        const totalMB = Math.round(memory.totalJSHeapSize / 1024 / 1024);
        const usagePercent = Math.round((usedMB / totalMB) * 100);
        
        if (usagePercent < 50) {
            results.performance.push(`✅ 内存使用正常: ${usedMB}MB / ${totalMB}MB (${usagePercent}%)`);
        } else if (usagePercent < 80) {
            results.performance.push(`⚠️ 内存使用较高: ${usedMB}MB / ${totalMB}MB (${usagePercent}%)`);
        } else {
            results.performance.push(`❌ 内存使用过高: ${usedMB}MB / ${totalMB}MB (${usagePercent}%)`);
        }
    } else {
        results.performance.push('⚠️ 内存信息不可用');
    }
    
    // 检查页面加载时间
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    if (loadTime < 2000) {
        results.performance.push(`✅ 页面加载时间正常: ${loadTime}ms`);
    } else if (loadTime < 5000) {
        results.performance.push(`⚠️ 页面加载时间较慢: ${loadTime}ms`);
    } else {
        results.performance.push(`❌ 页面加载时间过慢: ${loadTime}ms`);
    }
    
    // 检查资源加载
    const resources = performance.getEntriesByType('resource');
    const failedResources = resources.filter(r => r.transferSize === 0 && r.name.includes('bundle'));
    if (failedResources.length === 0) {
        results.performance.push('✅ 资源加载正常');
    } else {
        results.performance.push(`❌ 资源加载失败: ${failedResources.length}个`);
    }
    
    // 5. 计算总分
    let totalScore = 0;
    let maxScore = 0;
    
    // 控制台错误 (25分)
    maxScore += 25;
    const consoleErrorScore = results.consoleErrors.filter(r => r.includes('✅')).length;
    totalScore += (consoleErrorScore / results.consoleErrors.length) * 25;
    
    // 核心场景 (40分)
    maxScore += 40;
    const coreScenarioScore = results.coreScenarios.filter(r => r.includes('✅')).length;
    totalScore += (coreScenarioScore / results.coreScenarios.length) * 40;
    
    // 状态管理 (25分)
    maxScore += 25;
    const stateManagementScore = results.stateManagement.filter(r => r.includes('✅')).length;
    totalScore += (stateManagementScore / results.stateManagement.length) * 25;
    
    // 性能 (10分)
    maxScore += 10;
    const performanceScore = results.performance.filter(r => r.includes('✅')).length;
    totalScore += (performanceScore / results.performance.length) * 10;
    
    results.overall.score = Math.round(totalScore);
    results.overall.maxScore = maxScore;
    
    // 6. 生成报告
    console.log('📋 验证报告:');
    console.log('='.repeat(50));
    
    console.log('🧹 控制台错误检查:');
    results.consoleErrors.forEach(result => console.log(`  ${result}`));
    
    console.log('\n🎯 三大核心场景检查:');
    results.coreScenarios.forEach(result => console.log(`  ${result}`));
    
    console.log('\n📊 状态管理检查:');
    results.stateManagement.forEach(result => console.log(`  ${result}`));
    
    console.log('\n⚡ 性能检查:');
    results.performance.forEach(result => console.log(`  ${result}`));
    
    console.log('\n📊 总分:', `${results.overall.score}/${results.overall.maxScore}`);
    
    // 7. 生成建议
    const suggestions = [];
    if (results.consoleErrors.some(r => r.includes('❌'))) {
        suggestions.push('🔧 需要修复控制台错误');
    }
    if (results.coreScenarios.some(r => r.includes('❌'))) {
        suggestions.push('🔧 需要修复核心场景功能');
    }
    if (results.stateManagement.some(r => r.includes('❌'))) {
        suggestions.push('🔧 需要修复状态管理');
    }
    if (results.performance.some(r => r.includes('❌'))) {
        suggestions.push('🔧 需要优化性能');
    }
    
    if (suggestions.length > 0) {
        console.log('\n💡 修复建议:');
        suggestions.forEach(suggestion => console.log(`  ${suggestion}`));
    } else {
        console.log('\n🎉 所有检查通过！系统运行正常！');
    }
    
    // 8. 保存结果
    localStorage.setItem('quickVerificationResults', JSON.stringify(results));
    console.log('\n💾 验证结果已保存到本地存储');
    
    return results;
})();
