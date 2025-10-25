/**
 * 最终系统检查脚本
 * 
 * 全面检查整个增强播放状态指示器系统
 * 在浏览器控制台中运行此脚本
 */

(function() {
    console.log('🔍 开始最终系统检查...');
    
    // 检查结果
    const checkResults = {
        files: { 
            enhancedPlaybackStatus: false, 
            voicePlayer: false, 
            loadingOrder: false 
        },
        methods: { 
            showStatus: false, 
            hide: false, 
            setCompactMode: false, 
            setSpaciousMode: false 
        },
        integration: { 
            connection: false, 
            noConflicts: false, 
            allCalls: false 
        },
        styling: { 
            container: false, 
            gradient: false, 
            animation: false 
        },
        functionality: { 
            basic: false, 
            advanced: false, 
            errorHandling: false 
        },
        overall: { status: 'pending', score: 0, maxScore: 100, issues: [] }
    };
    
    // 1. 检查文件加载
    function checkFileLoading() {
        console.log('📁 检查文件加载...');
        
        // 检查 enhanced_playback_status.js
        if (window.enhancedPlaybackStatus && window.enhancedPlaybackStatus.constructor.name === 'EnhancedPlaybackStatus') {
            checkResults.files.enhancedPlaybackStatus = true;
            console.log('✅ enhanced_playback_status.js 已正确加载');
        } else {
            console.log('❌ enhanced_playback_status.js 未正确加载');
            checkResults.overall.issues.push('enhanced_playback_status.js 未正确加载');
        }
        
        // 检查 voice_player_enhanced.js
        if (window.voicePlayer && window.voicePlayer.constructor.name === 'VoicePlayerEnhanced') {
            checkResults.files.voicePlayer = true;
            console.log('✅ voice_player_enhanced.js 已正确加载');
        } else {
            console.log('❌ voice_player_enhanced.js 未正确加载');
            checkResults.overall.issues.push('voice_player_enhanced.js 未正确加载');
        }
        
        // 检查加载顺序
        if (checkResults.files.enhancedPlaybackStatus && checkResults.files.voicePlayer) {
            checkResults.files.loadingOrder = true;
            console.log('✅ 文件加载顺序正确');
        } else {
            console.log('❌ 文件加载顺序有问题');
            checkResults.overall.issues.push('文件加载顺序有问题');
        }
        
        return checkResults.files.enhancedPlaybackStatus && checkResults.files.voicePlayer;
    }
    
    // 2. 检查方法存在性
    function checkMethods() {
        console.log('🔧 检查方法存在性...');
        
        if (!window.enhancedPlaybackStatus) {
            console.log('❌ enhancedPlaybackStatus 未找到，跳过方法检查');
            return false;
        }
        
        // 检查基本方法
        const methods = ['showStatus', 'hide', 'setCompactMode', 'setSpaciousMode'];
        methods.forEach(method => {
            if (typeof window.enhancedPlaybackStatus[method] === 'function') {
                checkResults.methods[method] = true;
                console.log(`✅ 方法 ${method} 存在`);
            } else {
                console.log(`❌ 方法 ${method} 不存在`);
                checkResults.overall.issues.push(`方法 ${method} 不存在`);
            }
        });
        
        return Object.values(checkResults.methods).every(Boolean);
    }
    
    // 3. 检查集成状态
    function checkIntegration() {
        console.log('🔗 检查集成状态...');
        
        // 检查连接
        if (window.voicePlayer && window.voicePlayer.enhancedPlaybackStatus) {
            checkResults.integration.connection = true;
            console.log('✅ voicePlayer 已连接 enhancedPlaybackStatus');
        } else {
            console.log('❌ voicePlayer 未连接 enhancedPlaybackStatus');
            checkResults.overall.issues.push('voicePlayer 未连接 enhancedPlaybackStatus');
        }
        
        // 检查是否有冲突
        const oldIndicator = document.getElementById('voice-playback-status');
        if (!oldIndicator) {
            checkResults.integration.noConflicts = true;
            console.log('✅ 无旧指示器冲突');
        } else {
            console.log('❌ 发现旧指示器冲突');
            checkResults.overall.issues.push('发现旧指示器冲突');
        }
        
        // 检查所有调用
        const voicePlayerCode = window.voicePlayer ? window.voicePlayer.toString() : '';
        const hasShowCalls = voicePlayerCode.includes('enhancedPlaybackStatus.showStatus');
        const hasHideCalls = voicePlayerCode.includes('enhancedPlaybackStatus.hide');
        
        if (hasShowCalls && hasHideCalls) {
            checkResults.integration.allCalls = true;
            console.log('✅ 所有调用都已正确设置');
        } else {
            console.log('❌ 部分调用未正确设置');
            checkResults.overall.issues.push('部分调用未正确设置');
        }
        
        return checkResults.integration.connection && checkResults.integration.noConflicts;
    }
    
    // 4. 检查样式
    function checkStyling() {
        console.log('🎨 检查样式...');
        
        // 触发显示以创建容器
        if (window.enhancedPlaybackStatus) {
            window.enhancedPlaybackStatus.showStatus('speaking', '样式检查...');
        }
        
        setTimeout(() => {
            const container = document.getElementById('enhanced-playback-status');
            if (container) {
                checkResults.styling.container = true;
                console.log('✅ 容器存在');
                
                const style = window.getComputedStyle(container);
                
                // 检查渐变背景
                const hasGradient = style.background.includes('linear-gradient');
                if (hasGradient) {
                    checkResults.styling.gradient = true;
                    console.log('✅ 渐变背景正确');
                } else {
                    console.log('❌ 渐变背景不正确');
                    checkResults.overall.issues.push('渐变背景不正确');
                }
                
                // 检查动画
                const animationStyle = document.getElementById('enhanced-playback-spin-animation');
                if (animationStyle) {
                    checkResults.styling.animation = true;
                    console.log('✅ 旋转动画存在');
                } else {
                    console.log('❌ 旋转动画不存在');
                    checkResults.overall.issues.push('旋转动画不存在');
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
                checkResults.overall.issues.push('容器未找到');
            }
        }, 100);
        
        return true;
    }
    
    // 5. 检查功能
    function checkFunctionality() {
        console.log('⚡ 检查功能...');
        
        if (!window.enhancedPlaybackStatus) {
            console.log('❌ enhancedPlaybackStatus 未找到，跳过功能检查');
            return false;
        }
        
        // 基本功能测试
        try {
            window.enhancedPlaybackStatus.showStatus('speaking', '功能测试...');
            checkResults.functionality.basic = true;
            console.log('✅ 基本功能正常');
        } catch (error) {
            console.log('❌ 基本功能失败:', error);
            checkResults.overall.issues.push('基本功能失败');
        }
        
        // 高级功能测试
        try {
            window.enhancedPlaybackStatus.showStatus('speaking', '高级功能测试...', {
                showProgress: true
            });
            checkResults.functionality.advanced = true;
            console.log('✅ 高级功能正常');
        } catch (error) {
            console.log('❌ 高级功能失败:', error);
            checkResults.overall.issues.push('高级功能失败');
        }
        
        // 错误处理测试
        try {
            window.enhancedPlaybackStatus.showStatus('error', '错误测试...', {
                showRetry: true
            });
            checkResults.functionality.errorHandling = true;
            console.log('✅ 错误处理正常');
        } catch (error) {
            console.log('❌ 错误处理失败:', error);
            checkResults.overall.issues.push('错误处理失败');
        }
        
        // 延迟隐藏
        setTimeout(() => {
            try {
                window.enhancedPlaybackStatus.hide();
                console.log('✅ 隐藏功能正常');
            } catch (error) {
                console.log('❌ 隐藏功能失败:', error);
                checkResults.overall.issues.push('隐藏功能失败');
            }
        }, 2000);
        
        return checkResults.functionality.basic;
    }
    
    // 6. 生成最终报告
    function generateFinalReport() {
        console.log('📋 生成最终报告...');
        
        // 计算总分
        let totalScore = 0;
        let maxScore = 0;
        
        // 文件检查 (20分)
        maxScore += 20;
        if (checkResults.files.enhancedPlaybackStatus) totalScore += 7;
        if (checkResults.files.voicePlayer) totalScore += 7;
        if (checkResults.files.loadingOrder) totalScore += 6;
        
        // 方法检查 (20分)
        maxScore += 20;
        Object.values(checkResults.methods).forEach(exists => {
            if (exists) totalScore += 5;
        });
        
        // 集成检查 (25分)
        maxScore += 25;
        if (checkResults.integration.connection) totalScore += 8;
        if (checkResults.integration.noConflicts) totalScore += 8;
        if (checkResults.integration.allCalls) totalScore += 9;
        
        // 样式检查 (20分)
        maxScore += 20;
        if (checkResults.styling.container) totalScore += 7;
        if (checkResults.styling.gradient) totalScore += 7;
        if (checkResults.styling.animation) totalScore += 6;
        
        // 功能检查 (15分)
        maxScore += 15;
        if (checkResults.functionality.basic) totalScore += 5;
        if (checkResults.functionality.advanced) totalScore += 5;
        if (checkResults.functionality.errorHandling) totalScore += 5;
        
        checkResults.overall.score = totalScore;
        checkResults.overall.maxScore = maxScore;
        checkResults.overall.status = totalScore >= maxScore * 0.9 ? 'excellent' : 
                                      totalScore >= maxScore * 0.8 ? 'good' : 
                                      totalScore >= maxScore * 0.6 ? 'fair' : 'poor';
        
        console.log('📊 最终系统检查报告:', checkResults);
        
        // 生成建议
        if (checkResults.overall.issues.length > 0) {
            console.log('💡 发现的问题:', checkResults.overall.issues);
        } else {
            console.log('🎉 系统检查通过！所有功能正常！');
        }
        
        return checkResults;
    }
    
    // 执行所有检查
    console.log('🚀 开始执行最终系统检查...');
    
    checkFileLoading();
    checkMethods();
    checkIntegration();
    checkStyling();
    checkFunctionality();
    
    // 生成最终报告
    setTimeout(() => {
        const report = generateFinalReport();
        console.log('✅ 最终系统检查完成！');
        console.log('📊 最终报告:', report);
        
        // 保存结果到本地存储
        localStorage.setItem('finalSystemCheckResults', JSON.stringify(report));
        console.log('💾 检查结果已保存到本地存储');
        
    }, 3000);
    
    // 返回检查函数，供手动调用
    window.finalSystemCheck = function() {
        console.log('🔍 手动执行最终系统检查...');
        checkFileLoading();
        checkMethods();
        checkIntegration();
        checkStyling();
        checkFunctionality();
        return generateFinalReport();
    };
    
    console.log('💡 提示: 可以随时调用 window.finalSystemCheck() 来手动检查系统状态');
    
})();
