/**
 * 自适应UI系统
 * 根据用户偏好和性能自动调整界面
 */
class AdaptiveUI {
    constructor() {
        this.userPreferences = this.loadUserPreferences();
        this.performanceMetrics = new Map();
        this.adaptations = new Map();
        this.monitoringInterval = null;
        
        // 初始化
        this.init();
    }
    
    /**
     * 初始化
     */
    init() {
        window.controlledLog?.log('🎨 自适应UI系统初始化中...');
        
        // 加载用户偏好
        this.applyUserPreferences();
        
        // 启动性能监控
        this.startPerformanceMonitoring();
        
        // 监听用户交互
        this.setupInteractionListeners();
        
        window.controlledLog?.log('✅ 自适应UI系统已初始化');
    }
    
    /**
     * 获取用户偏好
     */
    getUserPreferences() {
        return this.userPreferences;
    }
    
    /**
     * 加载用户偏好
     */
    loadUserPreferences() {
        const defaultPreferences = {
            animationSpeed: 'normal', // slow, normal, fast
            visualDensity: 'comfortable', // compact, comfortable, spacious
            colorTheme: 'auto', // light, dark, auto
            reducedMotion: false,
            highContrast: false,
            fontSize: 'medium' // small, medium, large
        };
        
        try {
            const stored = localStorage.getItem('ui_preferences');
            if (stored) {
                return { ...defaultPreferences, ...JSON.parse(stored) };
            }
        } catch (error) {
            console.warn('⚠️ 无法加载用户偏好:', error);
        }
        
        return defaultPreferences;
    }
    
    /**
     * 保存用户偏好
     */
    saveUserPreferences() {
        try {
            localStorage.setItem('ui_preferences', JSON.stringify(this.userPreferences));
            window.controlledLog?.log('💾 用户偏好已保存');
        } catch (error) {
            console.error('❌ 保存用户偏好失败:', error);
        }
    }
    
    /**
     * 应用用户偏好
     */
    applyUserPreferences() {
        // 应用动画速度
        this.applyAnimationSpeed(this.userPreferences.animationSpeed);
        
        // 应用视觉密度
        this.applyVisualDensity(this.userPreferences.visualDensity);
        
        // 应用减少动画设置
        if (this.userPreferences.reducedMotion) {
            this.enableReducedMotion();
        }
        
        // 应用高对比度
        if (this.userPreferences.highContrast) {
            this.enableHighContrast();
        }
        
        window.controlledLog?.log('🎨 用户偏好已应用:', this.userPreferences);
    }
    
    /**
     * 应用动画速度
     */
    applyAnimationSpeed(speed) {
        const speedMap = {
            'slow': 1.5,
            'normal': 1.0,
            'fast': 0.5
        };
        
        const factor = speedMap[speed] || 1.0;
        document.documentElement.style.setProperty('--animation-speed-factor', factor);
    }
    
    /**
     * 应用视觉密度
     */
    applyVisualDensity(density) {
        const densityMap = {
            'compact': 0.8,
            'comfortable': 1.0,
            'spacious': 1.2
        };
        
        const factor = densityMap[density] || 1.0;
        document.documentElement.style.setProperty('--visual-density-factor', factor);
    }
    
    /**
     * 启用减少动画
     */
    enableReducedMotion() {
        document.documentElement.classList.add('reduced-motion');
        window.controlledLog?.log('🎬 减少动画模式已启用');
    }
    
    /**
     * 启用高对比度
     */
    enableHighContrast() {
        document.documentElement.classList.add('high-contrast');
        window.controlledLog?.log('🎨 高对比度模式已启用');
    }
    
    /**
     * 启动性能监控
     */
    startPerformanceMonitoring() {
        this.monitoringInterval = setInterval(() => {
            this.collectPerformanceMetrics();
            this.adaptToPerformance();
        }, 5000); // 每5秒检查一次
        
        window.controlledLog?.log('📊 性能监控已启动');
    }
    
    /**
     * 停止性能监控
     */
    stopPerformanceMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
            window.controlledLog?.log('📊 性能监控已停止');
        }
    }
    
    /**
     * 收集性能指标
     */
    collectPerformanceMetrics() {
        const metrics = {
            fps: this.measureFPS(),
            memory: this.measureMemory(),
            renderTime: this.measureRenderTime(),
            timestamp: Date.now()
        };
        
        this.performanceMetrics.set(Date.now(), metrics);
        
        // 保持指标在合理范围内
        if (this.performanceMetrics.size > 20) {
            const oldestKey = Array.from(this.performanceMetrics.keys())[0];
            this.performanceMetrics.delete(oldestKey);
        }
        
        return metrics;
    }
    
    /**
     * 测量FPS
     */
    measureFPS() {
        // 简化的FPS测量
        if (window.performance && window.performance.now) {
            return 60; // 默认假设60fps，实际应该用requestAnimationFrame测量
        }
        return 30;
    }
    
    /**
     * 测量内存使用
     */
    measureMemory() {
        if (window.performance && window.performance.memory) {
            return {
                used: window.performance.memory.usedJSHeapSize,
                total: window.performance.memory.totalJSHeapSize,
                limit: window.performance.memory.jsHeapSizeLimit
            };
        }
        return null;
    }
    
    /**
     * 测量渲染时间
     */
    measureRenderTime() {
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            return timing.domComplete - timing.domLoading;
        }
        return 0;
    }
    
    /**
     * 根据性能自适应
     */
    adaptToPerformance() {
        const recentMetrics = Array.from(this.performanceMetrics.values()).slice(-5);
        
        if (recentMetrics.length === 0) {
            return;
        }
        
        const avgFPS = recentMetrics.reduce((sum, m) => sum + m.fps, 0) / recentMetrics.length;
        
        // 如果FPS低于30，降低动画复杂度
        if (avgFPS < 30 && !this.adaptations.has('low_fps')) {
            this.adaptations.set('low_fps', true);
            this.reduceAnimationComplexity();
            window.controlledLog?.log('⚡ 检测到低FPS，已降低动画复杂度');
        } else if (avgFPS >= 50 && this.adaptations.has('low_fps')) {
            this.adaptations.delete('low_fps');
            this.restoreAnimationComplexity();
            window.controlledLog?.log('✨ FPS恢复正常，已恢复动画复杂度');
        }
    }
    
    /**
     * 降低动画复杂度
     */
    reduceAnimationComplexity() {
        // 禁用复杂动画
        if (window.enhancedAudioVisualizer) {
            window.enhancedAudioVisualizer.stopAnimation();
        }
        
        document.documentElement.classList.add('reduced-animations');
    }
    
    /**
     * 恢复动画复杂度
     */
    restoreAnimationComplexity() {
        document.documentElement.classList.remove('reduced-animations');
    }
    
    /**
     * 设置交互监听器
     */
    setupInteractionListeners() {
        // 监听用户偏好变化
        window.addEventListener('userPreferenceChanged', (event) => {
            this.handlePreferenceChange(event.detail);
        });
        
        // 监听系统主题变化
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (this.userPreferences.colorTheme === 'auto') {
                    window.controlledLog?.log('🎨 系统主题已变化:', e.matches ? 'dark' : 'light');
                }
            });
            
            window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
                if (e.matches) {
                    this.enableReducedMotion();
                }
            });
        }
    }
    
    /**
     * 处理偏好变化
     */
    handlePreferenceChange(preference) {
        this.userPreferences = { ...this.userPreferences, ...preference };
        this.saveUserPreferences();
        this.applyUserPreferences();
        
        window.controlledLog?.log('🔄 用户偏好已更新:', preference);
    }
    
    /**
     * 获取性能报告
     */
    getPerformanceReport() {
        const metrics = Array.from(this.performanceMetrics.values());
        
        if (metrics.length === 0) {
            return null;
        }
        
        const avgFPS = metrics.reduce((sum, m) => sum + m.fps, 0) / metrics.length;
        const avgRenderTime = metrics.reduce((sum, m) => sum + m.renderTime, 0) / metrics.length;
        
        return {
            averageFPS: avgFPS.toFixed(1),
            averageRenderTime: avgRenderTime.toFixed(1),
            totalSamples: metrics.length,
            adaptations: Array.from(this.adaptations.keys())
        };
    }
    
    /**
     * 销毁
     */
    destroy() {
        this.stopPerformanceMonitoring();
        this.performanceMetrics.clear();
        this.adaptations.clear();
        window.controlledLog?.log('🧹 自适应UI系统已销毁');
    }
}

// 全局实例
window.adaptiveUI = null;

// 初始化函数
function initAdaptiveUI() {
    if (window.adaptiveUI) {
        window.adaptiveUI.destroy();
    }
    
    window.adaptiveUI = new AdaptiveUI();
    window.controlledLog?.log('🎨 自适应UI系统已初始化');
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdaptiveUI);
} else {
    initAdaptiveUI();
}

