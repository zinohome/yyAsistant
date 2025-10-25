/**
 * 完整集成测试脚本
 * 
 * 测试 voice_player_enhanced.js 和 enhanced_playback_status.js 的完整集成
 * 在浏览器控制台中运行此脚本
 */

(function() {
    console.log('🔗 开始完整集成测试...');
    
    // 测试结果
    const integrationResults = {
        components: { 
            voicePlayer: false, 
            enhancedPlaybackStatus: false, 
            connection: false 
        },
        functionality: { 
            show: false, 
            hide: false, 
            stateManagement: false 
        },
        styling: { 
            container: false, 
            animation: false, 
            gradient: false 
        },
        integration: { 
            seamless: false, 
            noConflicts: false 
        },
        overall: { status: 'pending', score: 0, maxScore: 100 }
    };
    
    // 1. 测试组件存在性
    function testComponentExistence() {
        console.log('🧩 测试组件存在性...');
        
        // 检查 voice_player_enhanced.js
        if (window.voicePlayer && window.voicePlayerEnhanced) {
            integrationResults.components.voicePlayer = true;
            console.log('✅ voice_player_enhanced.js 已加载');
        } else {
            console.log('❌ voice_player_enhanced.js 未找到');
        }
        
        // 检查 enhanced_playback_status.js
        if (window.enhancedPlaybackStatus) {
            integrationResults.components.enhancedPlaybackStatus = true;
            console.log('✅ enhanced_playback_status.js 已加载');
        } else {
            console.log('❌ enhanced_playback_status.js 未找到');
        }
        
        // 检查连接状态
        if (window.voicePlayer && window.voicePlayer.enhancedPlaybackStatus) {
            integrationResults.components.connection = true;
            console.log('✅ 组件连接正常');
        } else {
            console.log('❌ 组件连接失败');
        }
        
        return integrationResults.components.voicePlayer && 
               integrationResults.components.enhancedPlaybackStatus && 
               integrationResults.components.connection;
    }
    
    // 2. 测试功能完整性
    function testFunctionality() {
        console.log('🔧 测试功能完整性...');
        
        if (!window.voicePlayer || !window.enhancedPlaybackStatus) {
            console.log('❌ 组件未就绪，跳过功能测试');
            return false;
        }
        
        // 测试显示功能
        try {
            window.enhancedPlaybackStatus.showStatus('speaking', '测试播放状态...');
            integrationResults.functionality.show = true;
            console.log('✅ 显示功能正常');
        } catch (error) {
            console.log('❌ 显示功能失败:', error);
        }
        
        // 测试状态管理
        try {
            // 测试不同状态
            const states = ['connecting', 'listening', 'processing', 'speaking', 'error'];
            states.forEach((state, index) => {
                setTimeout(() => {
                    window.enhancedPlaybackStatus.showStatus(state, `测试${state}状态...`);
                }, index * 500);
            });
            integrationResults.functionality.stateManagement = true;
            console.log('✅ 状态管理功能正常');
        } catch (error) {
            console.log('❌ 状态管理功能失败:', error);
        }
        
        // 延迟测试隐藏功能
        setTimeout(() => {
            try {
                window.enhancedPlaybackStatus.hide();
                integrationResults.functionality.hide = true;
                console.log('✅ 隐藏功能正常');
            } catch (error) {
                console.log('❌ 隐藏功能失败:', error);
            }
        }, 3000);
        
        return true;
    }
    
    // 3. 测试样式完整性
    function testStyling() {
        console.log('🎨 测试样式完整性...');
        
        // 触发显示以创建容器
        if (window.enhancedPlaybackStatus) {
            window.enhancedPlaybackStatus.showStatus('speaking', '测试样式...');
        }
        
        setTimeout(() => {
            const container = document.getElementById('enhanced-playback-status');
            if (container) {
                const style = window.getComputedStyle(container);
                
                // 检查容器存在
                integrationResults.styling.container = true;
                console.log('✅ 容器存在');
                
                // 检查渐变背景
                const hasGradient = style.background.includes('linear-gradient');
                if (hasGradient) {
                    integrationResults.styling.gradient = true;
                    console.log('✅ 渐变背景正确');
                } else {
                    console.log('❌ 渐变背景不正确');
                }
                
                // 检查动画
                const animationStyle = document.getElementById('enhanced-playback-spin-animation');
                if (animationStyle) {
                    integrationResults.styling.animation = true;
                    console.log('✅ 旋转动画存在');
                } else {
                    console.log('❌ 旋转动画不存在');
                }
                
                // 显示样式详情
                console.log('🎨 样式详情:', {
                    background: style.background,
                    borderRadius: style.borderRadius,
                    color: style.color,
                    boxShadow: style.boxShadow,
                    backdropFilter: style.backdropFilter
                });
            } else {
                console.log('❌ 容器未找到');
            }
        }, 100);
        
        return true;
    }
    
    // 4. 测试集成完整性
    function testIntegration() {
        console.log('🔗 测试集成完整性...');
        
        if (!window.voicePlayer || !window.enhancedPlaybackStatus) {
            console.log('❌ 组件未就绪，跳过集成测试');
            return false;
        }
        
        // 测试通过 voicePlayer 调用
        try {
            window.voicePlayer.enhancedPlaybackStatus.showStatus('speaking', '通过voicePlayer测试...');
            integrationResults.integration.seamless = true;
            console.log('✅ 无缝集成正常');
        } catch (error) {
            console.log('❌ 无缝集成失败:', error);
        }
        
        // 检查是否有冲突
        const oldIndicator = document.getElementById('voice-playback-status');
        if (!oldIndicator) {
            integrationResults.integration.noConflicts = true;
            console.log('✅ 无冲突检测通过');
        } else {
            console.log('❌ 发现旧指示器冲突');
        }
        
        // 延迟隐藏
        setTimeout(() => {
            if (window.voicePlayer && window.voicePlayer.enhancedPlaybackStatus) {
                window.voicePlayer.enhancedPlaybackStatus.hide();
            }
        }, 2000);
        
        return true;
    }
    
    // 5. 测试实际使用场景
    function testRealWorldScenarios() {
        console.log('🌍 测试实际使用场景...');
        
        if (!window.voicePlayer || !window.enhancedPlaybackStatus) {
            console.log('❌ 组件未就绪，跳过场景测试');
            return false;
        }
        
        // 模拟文本聊天TTS场景
        console.log('📝 模拟文本聊天TTS场景...');
        window.enhancedPlaybackStatus.showStatus('processing', 'AI思考中...');
        
        setTimeout(() => {
            window.enhancedPlaybackStatus.showStatus('speaking', '正在播放语音...');
        }, 1000);
        
        setTimeout(() => {
            window.enhancedPlaybackStatus.hide();
            console.log('✅ 文本聊天TTS场景测试完成');
        }, 3000);
        
        // 模拟语音录制场景
        setTimeout(() => {
            console.log('🎤 模拟语音录制场景...');
            window.enhancedPlaybackStatus.showStatus('listening', '正在聆听...');
            
            setTimeout(() => {
                window.enhancedPlaybackStatus.showStatus('processing', 'AI思考中...');
            }, 1000);
            
            setTimeout(() => {
                window.enhancedPlaybackStatus.showStatus('speaking', '正在播放语音...');
            }, 2000);
            
            setTimeout(() => {
                window.enhancedPlaybackStatus.hide();
                console.log('✅ 语音录制场景测试完成');
            }, 5000);
        }, 4000);
        
        return true;
    }
    
    // 6. 生成集成测试报告
    function generateIntegrationReport() {
        console.log('📋 生成集成测试报告...');
        
        // 计算总分
        let totalScore = 0;
        let maxScore = 0;
        
        // 组件检查 (25分)
        maxScore += 25;
        if (integrationResults.components.voicePlayer) totalScore += 8;
        if (integrationResults.components.enhancedPlaybackStatus) totalScore += 8;
        if (integrationResults.components.connection) totalScore += 9;
        
        // 功能检查 (30分)
        maxScore += 30;
        if (integrationResults.functionality.show) totalScore += 10;
        if (integrationResults.functionality.hide) totalScore += 10;
        if (integrationResults.functionality.stateManagement) totalScore += 10;
        
        // 样式检查 (25分)
        maxScore += 25;
        if (integrationResults.styling.container) totalScore += 8;
        if (integrationResults.styling.animation) totalScore += 8;
        if (integrationResults.styling.gradient) totalScore += 9;
        
        // 集成检查 (20分)
        maxScore += 20;
        if (integrationResults.integration.seamless) totalScore += 10;
        if (integrationResults.integration.noConflicts) totalScore += 10;
        
        integrationResults.overall.score = totalScore;
        integrationResults.overall.maxScore = maxScore;
        integrationResults.overall.status = totalScore >= maxScore * 0.8 ? 'excellent' : 
                                           totalScore >= maxScore * 0.6 ? 'good' : 
                                           totalScore >= maxScore * 0.4 ? 'fair' : 'poor';
        
        console.log('📊 完整集成测试报告:', integrationResults);
        
        // 生成建议
        const suggestions = [];
        if (!integrationResults.components.voicePlayer) {
            suggestions.push('🔧 voice_player_enhanced.js 未加载，检查脚本加载顺序');
        }
        if (!integrationResults.components.enhancedPlaybackStatus) {
            suggestions.push('🔧 enhanced_playback_status.js 未加载，检查脚本加载顺序');
        }
        if (!integrationResults.components.connection) {
            suggestions.push('🔧 组件连接失败，检查初始化代码');
        }
        if (!integrationResults.functionality.show) {
            suggestions.push('🔧 显示功能失败，检查 showStatus 方法');
        }
        if (!integrationResults.functionality.hide) {
            suggestions.push('🔧 隐藏功能失败，检查 hide 方法');
        }
        if (!integrationResults.styling.gradient) {
            suggestions.push('🔧 样式移植失败，检查样式代码');
        }
        if (!integrationResults.integration.seamless) {
            suggestions.push('🔧 集成失败，检查组件连接');
        }
        if (!integrationResults.integration.noConflicts) {
            suggestions.push('🔧 发现冲突，检查旧代码清理');
        }
        
        if (suggestions.length > 0) {
            console.log('💡 修复建议:', suggestions);
        } else {
            console.log('🎉 完整集成测试通过！');
        }
        
        return integrationResults;
    }
    
    // 执行所有测试
    console.log('🚀 开始执行完整集成测试...');
    
    testComponentExistence();
    testFunctionality();
    testStyling();
    testIntegration();
    testRealWorldScenarios();
    
    // 生成最终报告
    setTimeout(() => {
        const report = generateIntegrationReport();
        console.log('✅ 完整集成测试完成！');
        console.log('📊 最终报告:', report);
        
        // 保存结果到本地存储
        localStorage.setItem('completeIntegrationTestResults', JSON.stringify(report));
        console.log('💾 测试结果已保存到本地存储');
        
    }, 8000);
    
    // 返回测试函数，供手动调用
    window.testCompleteIntegration = function() {
        console.log('🔗 手动执行完整集成测试...');
        testComponentExistence();
        testFunctionality();
        testStyling();
        testIntegration();
        testRealWorldScenarios();
        return generateIntegrationReport();
    };
    
    console.log('💡 提示: 可以随时调用 window.testCompleteIntegration() 来手动测试完整集成');
    
})();
