/**
 * 音频可视化检查脚本
 * 
 * 专门检查音频可视化Canvas的正确位置和状态
 * 在浏览器控制台中运行此脚本
 */

(function() {
    console.log('🎨 开始检查音频可视化Canvas...');
    
    // 检查结果
    const results = {
        container: { exists: false, visible: false, style: null },
        canvas: { exists: false, visible: false, style: null },
        parent: { exists: false, visible: false, style: null },
        overall: { status: 'pending', score: 0, maxScore: 100 }
    };
    
    // 1. 检查音频可视化容器
    function checkAudioVisualizerContainer() {
        console.log('📦 检查音频可视化容器...');
        
        const container = document.getElementById('audio-visualizer-container');
        if (!container) {
            console.error('❌ 音频可视化容器未找到');
            return false;
        }
        
        results.container.exists = true;
        console.log('✅ 音频可视化容器存在');
        
        // 检查容器样式
        const containerStyle = window.getComputedStyle(container);
        results.container.style = {
            display: containerStyle.display,
            visibility: containerStyle.visibility,
            opacity: containerStyle.opacity,
            position: containerStyle.position,
            width: containerStyle.width,
            height: containerStyle.height
        };
        
        console.log('📦 容器样式:', results.container.style);
        
        // 检查容器是否可见
        const isVisible = containerStyle.display !== 'none' && 
                         containerStyle.visibility !== 'hidden' && 
                         containerStyle.opacity !== '0';
        results.container.visible = isVisible;
        
        console.log(`📦 容器可见性: ${isVisible ? '可见' : '隐藏'}`);
        
        if (!isVisible) {
            console.log('📦 容器当前隐藏，这是正常的（默认状态）');
        }
        
        return true;
    }
    
    // 2. 检查音频可视化Canvas
    function checkAudioVisualizerCanvas() {
        console.log('🎨 检查音频可视化Canvas...');
        
        const canvas = document.getElementById('audio-visualizer');
        if (!canvas) {
            console.error('❌ 音频可视化Canvas未找到');
            return false;
        }
        
        results.canvas.exists = true;
        console.log('✅ 音频可视化Canvas存在');
        
        // 检查Canvas样式
        const canvasStyle = window.getComputedStyle(canvas);
        results.canvas.style = {
            display: canvasStyle.display,
            visibility: canvasStyle.visibility,
            opacity: canvasStyle.opacity,
            position: canvasStyle.position,
            width: canvasStyle.width,
            height: canvasStyle.height,
            border: canvasStyle.border,
            backgroundColor: canvasStyle.backgroundColor
        };
        
        console.log('🎨 Canvas样式:', results.canvas.style);
        
        // 检查Canvas是否可见
        const isVisible = canvasStyle.display !== 'none' && 
                         canvasStyle.visibility !== 'hidden' && 
                         canvasStyle.opacity !== '0';
        results.canvas.visible = isVisible;
        
        console.log(`🎨 Canvas可见性: ${isVisible ? '可见' : '隐藏'}`);
        
        // 检查Canvas尺寸
        console.log(`🎨 Canvas尺寸: ${canvas.width}x${canvas.height}`);
        console.log(`🎨 Canvas显示尺寸: ${canvasStyle.width}x${canvasStyle.height}`);
        
        return true;
    }
    
    // 3. 检查父容器
    function checkParentContainer() {
        console.log('👨‍👩‍👧‍👦 检查父容器...');
        
        const canvas = document.getElementById('audio-visualizer');
        if (!canvas) {
            console.error('❌ Canvas未找到，无法检查父容器');
            return false;
        }
        
        const parent = canvas.parentElement;
        if (!parent) {
            console.error('❌ Canvas父容器未找到');
            return false;
        }
        
        results.parent.exists = true;
        console.log('✅ Canvas父容器存在');
        console.log('👨‍👩‍👧‍👦 父容器ID:', parent.id);
        console.log('👨‍👩‍👧‍👦 父容器标签:', parent.tagName);
        
        // 检查父容器样式
        const parentStyle = window.getComputedStyle(parent);
        results.parent.style = {
            display: parentStyle.display,
            visibility: parentStyle.visibility,
            opacity: parentStyle.opacity,
            position: parentStyle.position,
            width: parentStyle.width,
            height: parentStyle.height
        };
        
        console.log('👨‍👩‍👧‍👦 父容器样式:', results.parent.style);
        
        // 检查父容器是否可见
        const isVisible = parentStyle.display !== 'none' && 
                         parentStyle.visibility !== 'hidden' && 
                         parentStyle.opacity !== '0';
        results.parent.visible = isVisible;
        
        console.log(`👨‍👩‍👧‍👦 父容器可见性: ${isVisible ? '可见' : '隐藏'}`);
        
        return true;
    }
    
    // 4. 检查Canvas上下文
    function checkCanvasContext() {
        console.log('🖼️ 检查Canvas上下文...');
        
        const canvas = document.getElementById('audio-visualizer');
        if (!canvas) {
            console.error('❌ Canvas未找到，无法检查上下文');
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
            
            return true;
        } catch (error) {
            console.error('❌ Canvas上下文检查失败:', error);
            return false;
        }
    }
    
    // 5. 检查音频可视化相关组件
    function checkAudioVisualizerComponents() {
        console.log('🔧 检查音频可视化相关组件...');
        
        const components = [
            { name: 'EnhancedAudioVisualizer', obj: window.EnhancedAudioVisualizer },
            { name: 'enhancedAudioVisualizer', obj: window.enhancedAudioVisualizer },
            { name: 'audioVisualizer', obj: window.audioVisualizer }
        ];
        
        let foundComponents = 0;
        components.forEach(component => {
            if (component.obj) {
                console.log(`✅ ${component.name}存在`);
                foundComponents++;
            } else {
                console.log(`❌ ${component.name}未找到`);
            }
        });
        
        console.log(`🔧 找到的组件: ${foundComponents}/${components.length}`);
        return foundComponents > 0;
    }
    
    // 6. 生成检查报告
    function generateCheckReport() {
        console.log('📋 生成音频可视化检查报告...');
        
        // 计算总分
        let totalScore = 0;
        let maxScore = 0;
        
        // 容器检查 (25分)
        maxScore += 25;
        if (results.container.exists) {
            totalScore += 15;
            if (results.container.visible) {
                totalScore += 10;
            }
        }
        
        // Canvas检查 (35分)
        maxScore += 35;
        if (results.canvas.exists) {
            totalScore += 25;
            if (results.canvas.visible) {
                totalScore += 10;
            }
        }
        
        // 父容器检查 (20分)
        maxScore += 20;
        if (results.parent.exists) {
            totalScore += 15;
            if (results.parent.visible) {
                totalScore += 5;
            }
        }
        
        // 上下文检查 (20分)
        maxScore += 20;
        if (checkCanvasContext()) {
            totalScore += 20;
        }
        
        results.overall.score = totalScore;
        results.overall.maxScore = maxScore;
        results.overall.status = totalScore >= maxScore * 0.8 ? 'excellent' : 
                                totalScore >= maxScore * 0.6 ? 'good' : 
                                totalScore >= maxScore * 0.4 ? 'fair' : 'poor';
        
        console.log('📊 音频可视化检查报告:', results);
        
        // 生成建议
        const suggestions = [];
        if (!results.container.exists) {
            suggestions.push('🔧 音频可视化容器未找到，需要检查HTML结构');
        }
        if (!results.canvas.exists) {
            suggestions.push('🔧 音频可视化Canvas未找到，需要检查HTML结构');
        }
        if (!results.parent.exists) {
            suggestions.push('🔧 Canvas父容器未找到，需要检查HTML结构');
        }
        if (!results.container.visible && !results.canvas.visible) {
            suggestions.push('🔧 音频可视化组件当前隐藏，这是正常的（默认状态）');
        }
        
        if (suggestions.length > 0) {
            console.log('💡 修复建议:', suggestions);
        } else {
            console.log('🎉 音频可视化检查通过！');
        }
        
        return results;
    }
    
    // 执行所有检查
    console.log('🚀 开始执行音频可视化检查...');
    
    checkAudioVisualizerContainer();
    checkAudioVisualizerCanvas();
    checkParentContainer();
    checkAudioVisualizerComponents();
    
    // 生成最终报告
    setTimeout(() => {
        const report = generateCheckReport();
        console.log('✅ 音频可视化检查完成！');
        console.log('📊 最终报告:', report);
        
        // 保存结果到本地存储
        localStorage.setItem('audioVisualizerCheckResults', JSON.stringify(report));
        console.log('💾 检查结果已保存到本地存储');
        
    }, 1000);
    
    // 返回检查函数，供手动调用
    window.checkAudioVisualizer = function() {
        console.log('🎨 手动执行音频可视化检查...');
        checkAudioVisualizerContainer();
        checkAudioVisualizerCanvas();
        checkParentContainer();
        checkAudioVisualizerComponents();
        return generateCheckReport();
    };
    
    console.log('💡 提示: 可以随时调用 window.checkAudioVisualizer() 来手动检查音频可视化');
    
})();
