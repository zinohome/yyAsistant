/**
 * 音频可视化结构验证脚本
 * 
 * 验证音频可视化Canvas的正确位置和结构
 * 在浏览器控制台中运行此脚本
 */

(function() {
    console.log('🎨 开始验证音频可视化结构...');
    
    // 验证结果
    const verificationResults = {
        container: { exists: false, visible: false, correctId: false, correctStyle: false },
        canvas: { exists: false, visible: false, correctId: false, correctStyle: false, correctParent: false },
        structure: { correct: false, issues: [] },
        overall: { status: 'pending', score: 0, maxScore: 100 }
    };
    
    // 1. 验证音频可视化容器
    function verifyAudioVisualizerContainer() {
        console.log('📦 验证音频可视化容器...');
        
        const container = document.getElementById('audio-visualizer-container');
        if (!container) {
            console.error('❌ 音频可视化容器未找到');
            verificationResults.structure.issues.push('音频可视化容器未找到');
            return false;
        }
        
        verificationResults.container.exists = true;
        verificationResults.container.correctId = true;
        console.log('✅ 音频可视化容器存在，ID正确');
        
        // 检查容器样式
        const containerStyle = window.getComputedStyle(container);
        const expectedDisplay = 'none'; // 默认隐藏
        const actualDisplay = containerStyle.display;
        
        if (actualDisplay === expectedDisplay) {
            verificationResults.container.correctStyle = true;
            console.log('✅ 容器样式正确（默认隐藏）');
        } else {
            console.log(`⚠️ 容器显示状态: ${actualDisplay}，预期: ${expectedDisplay}`);
        }
        
        // 检查容器是否可见
        const isVisible = actualDisplay !== 'none' && 
                         containerStyle.visibility !== 'hidden' && 
                         containerStyle.opacity !== '0';
        verificationResults.container.visible = isVisible;
        
        console.log(`📦 容器可见性: ${isVisible ? '可见' : '隐藏'}`);
        
        return true;
    }
    
    // 2. 验证音频可视化Canvas
    function verifyAudioVisualizerCanvas() {
        console.log('🎨 验证音频可视化Canvas...');
        
        const canvas = document.getElementById('audio-visualizer');
        if (!canvas) {
            console.error('❌ 音频可视化Canvas未找到');
            verificationResults.structure.issues.push('音频可视化Canvas未找到');
            return false;
        }
        
        verificationResults.canvas.exists = true;
        verificationResults.canvas.correctId = true;
        console.log('✅ 音频可视化Canvas存在，ID正确');
        
        // 检查Canvas样式
        const canvasStyle = window.getComputedStyle(canvas);
        const expectedStyles = {
            width: '80px',
            height: '20px',
            border: '1px solid rgb(217, 217, 217)', // #d9d9d9
            borderRadius: '4px',
            backgroundColor: 'rgb(255, 255, 255)', // #fff
            verticalAlign: 'middle',
            display: 'inline-block'
        };
        
        let styleCorrect = true;
        Object.keys(expectedStyles).forEach(property => {
            const expected = expectedStyles[property];
            const actual = canvasStyle[property];
            if (actual !== expected) {
                console.log(`⚠️ Canvas样式不匹配 - ${property}: 实际=${actual}, 预期=${expected}`);
                styleCorrect = false;
            }
        });
        
        if (styleCorrect) {
            verificationResults.canvas.correctStyle = true;
            console.log('✅ Canvas样式正确');
        } else {
            console.log('❌ Canvas样式不匹配');
        }
        
        // 检查Canvas尺寸
        console.log(`🎨 Canvas尺寸: ${canvas.width}x${canvas.height}`);
        console.log(`🎨 Canvas显示尺寸: ${canvasStyle.width}x${canvasStyle.height}`);
        
        // 检查Canvas是否可见
        const isVisible = canvasStyle.display !== 'none' && 
                         canvasStyle.visibility !== 'hidden' && 
                         canvasStyle.opacity !== '0';
        verificationResults.canvas.visible = isVisible;
        
        console.log(`🎨 Canvas可见性: ${isVisible ? '可见' : '隐藏'}`);
        
        return true;
    }
    
    // 3. 验证Canvas父容器关系
    function verifyCanvasParentRelationship() {
        console.log('👨‍👩‍👧‍👦 验证Canvas父容器关系...');
        
        const canvas = document.getElementById('audio-visualizer');
        const container = document.getElementById('audio-visualizer-container');
        
        if (!canvas || !container) {
            console.error('❌ Canvas或容器未找到');
            return false;
        }
        
        const parent = canvas.parentElement;
        if (!parent) {
            console.error('❌ Canvas父元素未找到');
            return false;
        }
        
        if (parent.id === 'audio-visualizer-container') {
            verificationResults.canvas.correctParent = true;
            console.log('✅ Canvas父容器关系正确');
        } else {
            console.error('❌ Canvas父容器关系错误');
            console.log(`   实际父容器ID: ${parent.id}`);
            console.log(`   预期父容器ID: audio-visualizer-container`);
            verificationResults.structure.issues.push('Canvas父容器关系错误');
        }
        
        // 检查父容器的子元素
        const children = Array.from(container.children);
        console.log(`👨‍👩‍👧‍👦 容器子元素数量: ${children.length}`);
        children.forEach((child, index) => {
            console.log(`   子元素${index}: ${child.tagName}#${child.id || 'no-id'}`);
        });
        
        return true;
    }
    
    // 4. 验证完整结构
    function verifyCompleteStructure() {
        console.log('🏗️ 验证完整结构...');
        
        const container = document.getElementById('audio-visualizer-container');
        const canvas = document.getElementById('audio-visualizer');
        
        if (!container || !canvas) {
            console.error('❌ 结构不完整');
            return false;
        }
        
        // 检查容器的完整结构
        const containerChildren = Array.from(container.children);
        console.log('🏗️ 容器结构:');
        console.log(`   容器ID: ${container.id}`);
        console.log(`   容器显示状态: ${window.getComputedStyle(container).display}`);
        console.log(`   子元素数量: ${containerChildren.length}`);
        
        containerChildren.forEach((child, index) => {
            console.log(`   子元素${index}: ${child.tagName}#${child.id || 'no-id'}`);
            if (child.tagName === 'CANVAS') {
                console.log(`     Canvas尺寸: ${child.width}x${child.height}`);
                console.log(`     Canvas样式: ${child.style.cssText}`);
            }
        });
        
        // 检查结构是否正确
        const hasCanvas = containerChildren.some(child => child.tagName === 'CANVAS');
        const hasDivider = containerChildren.some(child => child.tagName === 'DIV');
        
        if (hasCanvas && hasDivider) {
            verificationResults.structure.correct = true;
            console.log('✅ 结构正确：包含Canvas和Divider');
        } else {
            console.log('❌ 结构不完整');
            if (!hasCanvas) {
                verificationResults.structure.issues.push('容器中缺少Canvas');
            }
            if (!hasDivider) {
                verificationResults.structure.issues.push('容器中缺少Divider');
            }
        }
        
        return true;
    }
    
    // 5. 验证Canvas功能
    function verifyCanvasFunctionality() {
        console.log('🔧 验证Canvas功能...');
        
        const canvas = document.getElementById('audio-visualizer');
        if (!canvas) {
            console.error('❌ Canvas未找到，无法验证功能');
            return false;
        }
        
        try {
            const ctx = canvas.getContext('2d');
            if (!ctx) {
                console.error('❌ Canvas 2D上下文未找到');
                return false;
            }
            
            console.log('✅ Canvas 2D上下文正常');
            
            // 测试Canvas绘制
            ctx.fillStyle = '#f0f0f0';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#1890ff';
            ctx.fillRect(10, 5, 10, 10);
            
            console.log('✅ Canvas绘制测试成功');
            
            // 检查Canvas是否在正确的容器中
            const container = document.getElementById('audio-visualizer-container');
            if (canvas.parentElement === container) {
                console.log('✅ Canvas在正确的容器中');
            } else {
                console.log('❌ Canvas不在正确的容器中');
            }
            
            return true;
        } catch (error) {
            console.error('❌ Canvas功能验证失败:', error);
            return false;
        }
    }
    
    // 6. 生成验证报告
    function generateVerificationReport() {
        console.log('📋 生成音频可视化结构验证报告...');
        
        // 计算总分
        let totalScore = 0;
        let maxScore = 0;
        
        // 容器检查 (25分)
        maxScore += 25;
        if (verificationResults.container.exists) {
            totalScore += 10;
            if (verificationResults.container.correctId) {
                totalScore += 10;
            }
            if (verificationResults.container.correctStyle) {
                totalScore += 5;
            }
        }
        
        // Canvas检查 (35分)
        maxScore += 35;
        if (verificationResults.canvas.exists) {
            totalScore += 15;
            if (verificationResults.canvas.correctId) {
                totalScore += 10;
            }
            if (verificationResults.canvas.correctStyle) {
                totalScore += 5;
            }
            if (verificationResults.canvas.correctParent) {
                totalScore += 5;
            }
        }
        
        // 结构检查 (25分)
        maxScore += 25;
        if (verificationResults.structure.correct) {
            totalScore += 25;
        }
        
        // 功能检查 (15分)
        maxScore += 15;
        if (verifyCanvasFunctionality()) {
            totalScore += 15;
        }
        
        verificationResults.overall.score = totalScore;
        verificationResults.overall.maxScore = maxScore;
        verificationResults.overall.status = totalScore >= maxScore * 0.8 ? 'excellent' : 
                                            totalScore >= maxScore * 0.6 ? 'good' : 
                                            totalScore >= maxScore * 0.4 ? 'fair' : 'poor';
        
        console.log('📊 音频可视化结构验证报告:', verificationResults);
        
        // 生成建议
        const suggestions = [];
        if (!verificationResults.container.exists) {
            suggestions.push('🔧 音频可视化容器未找到，需要检查HTML结构');
        }
        if (!verificationResults.canvas.exists) {
            suggestions.push('🔧 音频可视化Canvas未找到，需要检查HTML结构');
        }
        if (!verificationResults.canvas.correctParent) {
            suggestions.push('🔧 Canvas父容器关系错误，需要检查HTML结构');
        }
        if (!verificationResults.structure.correct) {
            suggestions.push('🔧 结构不完整，需要检查HTML结构');
        }
        if (verificationResults.structure.issues.length > 0) {
            suggestions.push('🔧 发现结构问题:', verificationResults.structure.issues);
        }
        
        if (suggestions.length > 0) {
            console.log('💡 修复建议:', suggestions);
        } else {
            console.log('🎉 音频可视化结构验证通过！');
        }
        
        return verificationResults;
    }
    
    // 执行所有验证
    console.log('🚀 开始执行音频可视化结构验证...');
    
    verifyAudioVisualizerContainer();
    verifyAudioVisualizerCanvas();
    verifyCanvasParentRelationship();
    verifyCompleteStructure();
    
    // 生成最终报告
    setTimeout(() => {
        const report = generateVerificationReport();
        console.log('✅ 音频可视化结构验证完成！');
        console.log('📊 最终报告:', report);
        
        // 保存结果到本地存储
        localStorage.setItem('audioVisualizerStructureResults', JSON.stringify(report));
        console.log('💾 验证结果已保存到本地存储');
        
    }, 1000);
    
    // 返回验证函数，供手动调用
    window.verifyAudioVisualizerStructure = function() {
        console.log('🎨 手动执行音频可视化结构验证...');
        verifyAudioVisualizerContainer();
        verifyAudioVisualizerCanvas();
        verifyCanvasParentRelationship();
        verifyCompleteStructure();
        return generateVerificationReport();
    };
    
    console.log('💡 提示: 可以随时调用 window.verifyAudioVisualizerStructure() 来手动验证音频可视化结构');
    
})();
