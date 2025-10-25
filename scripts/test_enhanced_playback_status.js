/**
 * 测试增强播放状态指示器
 * 
 * 验证样式移植是否成功
 * 在浏览器控制台中运行此脚本
 */

(function() {
    console.log('🎨 开始测试增强播放状态指示器...');
    
    // 测试结果
    const testResults = {
        container: { exists: false, style: null, correct: false },
        animation: { exists: false, correct: false },
        functionality: { show: false, hide: false, correct: false },
        integration: { voicePlayer: false, correct: false },
        overall: { status: 'pending', score: 0, maxScore: 100 }
    };
    
    // 1. 测试容器创建和样式
    function testContainerStyle() {
        console.log('📦 测试容器样式...');
        
        // 检查容器是否存在
        const container = document.getElementById('enhanced-playback-status');
        if (!container) {
            console.log('📦 容器不存在，尝试创建...');
            
            // 创建测试容器
            if (window.enhancedPlaybackStatus) {
                window.enhancedPlaybackStatus.showStatus('speaking', '测试播放状态...');
                const testContainer = document.getElementById('enhanced-playback-status');
                if (testContainer) {
                    testResults.container.exists = true;
                    console.log('✅ 容器创建成功');
                } else {
                    console.log('❌ 容器创建失败');
                    return false;
                }
            } else {
                console.log('❌ enhancedPlaybackStatus 未找到');
                return false;
            }
        } else {
            testResults.container.exists = true;
            console.log('✅ 容器已存在');
        }
        
        // 检查样式
        const container = document.getElementById('enhanced-playback-status');
        if (container) {
            const style = window.getComputedStyle(container);
            testResults.container.style = {
                background: style.background,
                borderRadius: style.borderRadius,
                color: style.color,
                padding: style.padding,
                boxShadow: style.boxShadow,
                backdropFilter: style.backdropFilter
            };
            
            // 检查关键样式
            const hasGradient = style.background.includes('linear-gradient');
            const hasRoundedCorners = style.borderRadius === '20px';
            const hasWhiteText = style.color === 'rgb(255, 255, 255)';
            const hasShadow = style.boxShadow.includes('rgba(24, 144, 255, 0.4)');
            const hasBlur = style.backdropFilter.includes('blur');
            
            console.log('📦 样式检查:', {
                gradient: hasGradient,
                rounded: hasRoundedCorners,
                whiteText: hasWhiteText,
                shadow: hasShadow,
                blur: hasBlur
            });
            
            if (hasGradient && hasRoundedCorners && hasWhiteText && hasShadow && hasBlur) {
                testResults.container.correct = true;
                console.log('✅ 容器样式正确');
            } else {
                console.log('❌ 容器样式不正确');
            }
        }
        
        return true;
    }
    
    // 2. 测试旋转动画
    function testSpinAnimation() {
        console.log('🌀 测试旋转动画...');
        
        // 检查动画样式是否存在
        const animationStyle = document.getElementById('enhanced-playback-spin-animation');
        if (animationStyle) {
            testResults.animation.exists = true;
            console.log('✅ 旋转动画样式存在');
            
            // 检查动画内容
            const styleContent = animationStyle.textContent;
            if (styleContent.includes('@keyframes spin') && styleContent.includes('transform: rotate')) {
                testResults.animation.correct = true;
                console.log('✅ 旋转动画内容正确');
            } else {
                console.log('❌ 旋转动画内容不正确');
            }
        } else {
            console.log('❌ 旋转动画样式不存在');
        }
        
        return true;
    }
    
    // 3. 测试功能
    function testFunctionality() {
        console.log('🔧 测试功能...');
        
        if (!window.enhancedPlaybackStatus) {
            console.log('❌ enhancedPlaybackStatus 未找到');
            return false;
        }
        
        // 测试显示功能
        try {
            window.enhancedPlaybackStatus.showStatus('speaking', '测试播放状态...');
            testResults.functionality.show = true;
            console.log('✅ 显示功能正常');
        } catch (error) {
            console.log('❌ 显示功能失败:', error);
        }
        
        // 等待一下再测试隐藏功能
        setTimeout(() => {
            try {
                window.enhancedPlaybackStatus.hide();
                testResults.functionality.hide = true;
                console.log('✅ 隐藏功能正常');
            } catch (error) {
                console.log('❌ 隐藏功能失败:', error);
            }
        }, 1000);
        
        return true;
    }
    
    // 4. 测试与voice_player_enhanced.js的集成
    function testIntegration() {
        console.log('🔗 测试集成...');
        
        // 检查voice_player_enhanced.js是否连接了enhancedPlaybackStatus
        if (window.voicePlayer && window.voicePlayer.enhancedPlaybackStatus) {
            testResults.integration.voicePlayer = true;
            console.log('✅ voice_player_enhanced.js 已连接 enhancedPlaybackStatus');
            
            // 测试通过voice_player_enhanced.js调用
            try {
                window.voicePlayer.enhancedPlaybackStatus.showStatus('speaking', '通过voicePlayer测试...');
                testResults.integration.correct = true;
                console.log('✅ 集成功能正常');
                
                // 延迟隐藏
                setTimeout(() => {
                    window.voicePlayer.enhancedPlaybackStatus.hide();
                }, 2000);
            } catch (error) {
                console.log('❌ 集成功能失败:', error);
            }
        } else {
            console.log('❌ voice_player_enhanced.js 未连接 enhancedPlaybackStatus');
        }
        
        return true;
    }
    
    // 5. 生成测试报告
    function generateTestReport() {
        console.log('📋 生成测试报告...');
        
        // 计算总分
        let totalScore = 0;
        let maxScore = 0;
        
        // 容器样式检查 (30分)
        maxScore += 30;
        if (testResults.container.exists) {
            totalScore += 15;
            if (testResults.container.correct) {
                totalScore += 15;
            }
        }
        
        // 动画检查 (20分)
        maxScore += 20;
        if (testResults.animation.exists) {
            totalScore += 10;
            if (testResults.animation.correct) {
                totalScore += 10;
            }
        }
        
        // 功能检查 (30分)
        maxScore += 30;
        if (testResults.functionality.show) {
            totalScore += 15;
        }
        if (testResults.functionality.hide) {
            totalScore += 15;
        }
        
        // 集成检查 (20分)
        maxScore += 20;
        if (testResults.integration.voicePlayer) {
            totalScore += 10;
            if (testResults.integration.correct) {
                totalScore += 10;
            }
        }
        
        testResults.overall.score = totalScore;
        testResults.overall.maxScore = maxScore;
        testResults.overall.status = totalScore >= maxScore * 0.8 ? 'excellent' : 
                                    totalScore >= maxScore * 0.6 ? 'good' : 
                                    totalScore >= maxScore * 0.4 ? 'fair' : 'poor';
        
        console.log('📊 增强播放状态指示器测试报告:', testResults);
        
        // 生成建议
        const suggestions = [];
        if (!testResults.container.exists) {
            suggestions.push('🔧 容器未创建，需要检查enhancedPlaybackStatus初始化');
        }
        if (!testResults.container.correct) {
            suggestions.push('🔧 容器样式不正确，需要检查样式移植');
        }
        if (!testResults.animation.exists) {
            suggestions.push('🔧 旋转动画样式不存在，需要检查addSpinAnimation方法');
        }
        if (!testResults.functionality.show) {
            suggestions.push('🔧 显示功能失败，需要检查showStatus方法');
        }
        if (!testResults.functionality.hide) {
            suggestions.push('🔧 隐藏功能失败，需要检查hide方法');
        }
        if (!testResults.integration.voicePlayer) {
            suggestions.push('🔧 voice_player_enhanced.js未连接，需要检查初始化');
        }
        
        if (suggestions.length > 0) {
            console.log('💡 修复建议:', suggestions);
        } else {
            console.log('🎉 增强播放状态指示器测试通过！');
        }
        
        return testResults;
    }
    
    // 执行所有测试
    console.log('🚀 开始执行增强播放状态指示器测试...');
    
    testContainerStyle();
    testSpinAnimation();
    testFunctionality();
    testIntegration();
    
    // 生成最终报告
    setTimeout(() => {
        const report = generateTestReport();
        console.log('✅ 增强播放状态指示器测试完成！');
        console.log('📊 最终报告:', report);
        
        // 保存结果到本地存储
        localStorage.setItem('enhancedPlaybackStatusTestResults', JSON.stringify(report));
        console.log('💾 测试结果已保存到本地存储');
        
    }, 2000);
    
    // 返回测试函数，供手动调用
    window.testEnhancedPlaybackStatus = function() {
        console.log('🎨 手动执行增强播放状态指示器测试...');
        testContainerStyle();
        testSpinAnimation();
        testFunctionality();
        testIntegration();
        return generateTestReport();
    };
    
    console.log('💡 提示: 可以随时调用 window.testEnhancedPlaybackStatus() 来手动测试增强播放状态指示器');
    
})();
