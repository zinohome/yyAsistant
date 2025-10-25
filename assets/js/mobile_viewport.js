/**
 * 移动端视口高度动态处理
 * 解决手机浏览器地址栏动态变化导致的页面高度问题
 */

class MobileViewportHandler {
    constructor() {
        this.isMobile = this.detectMobile();
        this.isWeChat = this.detectWeChat();
        this.initialHeight = window.innerHeight;
        this.currentHeight = window.innerHeight;
        this.resizeTimeout = null;
        this.orientationChangeTimeout = null;
        
        this.init();
    }

    /**
     * 检测移动设备
     */
    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    /**
     * 检测微信浏览器
     */
    detectWeChat() {
        return /micromessenger/i.test(navigator.userAgent);
    }

    /**
     * 初始化
     */
    init() {
        if (!this.isMobile) {
            return; // 非移动设备，不需要处理
        }

        console.log('移动端视口处理器已启动');
        
        // 设置初始视口高度
        this.setViewportHeight();
        
        // 监听窗口大小变化
        window.addEventListener('resize', this.handleResize.bind(this));
        
        // 监听方向变化
        window.addEventListener('orientationchange', this.handleOrientationChange.bind(this));
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        // 监听触摸事件（用于检测地址栏变化）
        this.addTouchListeners();
        
        // 定期检查视口高度变化
        this.startHeightMonitoring();
    }

    /**
     * 设置视口高度
     */
    setViewportHeight() {
        const vh = window.innerHeight * 0.01;
        const vw = window.innerWidth * 0.01;
        
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        document.documentElement.style.setProperty('--vw', `${vw}px`);
        
        this.currentHeight = window.innerHeight;
        
        console.log(`视口高度已更新: ${window.innerHeight}px`);
    }

    /**
     * 处理窗口大小变化
     */
    handleResize() {
        // 防抖处理
        if (this.resizeTimeout) {
            clearTimeout(this.resizeTimeout);
        }
        
        this.resizeTimeout = setTimeout(() => {
            const newHeight = window.innerHeight;
            const heightDiff = Math.abs(newHeight - this.currentHeight);
            
            // 只有当高度变化超过50px时才更新（避免频繁更新）
            if (heightDiff > 50) {
                console.log(`检测到视口高度变化: ${this.currentHeight}px -> ${newHeight}px`);
                this.setViewportHeight();
                this.updateLayout();
            }
        }, 150);
    }

    /**
     * 处理方向变化
     */
    handleOrientationChange() {
        // 延迟处理，等待方向变化完成
        if (this.orientationChangeTimeout) {
            clearTimeout(this.orientationChangeTimeout);
        }
        
        this.orientationChangeTimeout = setTimeout(() => {
            console.log('检测到屏幕方向变化');
            this.setViewportHeight();
            this.updateLayout();
        }, 500);
    }

    /**
     * 处理页面可见性变化
     */
    handleVisibilityChange() {
        if (!document.hidden) {
            // 页面重新可见时，重新计算视口高度
            setTimeout(() => {
                this.setViewportHeight();
                this.updateLayout();
            }, 100);
        }
    }

    /**
     * 添加触摸监听器
     */
    addTouchListeners() {
        let touchStartY = 0;
        let touchEndY = 0;
        
        document.addEventListener('touchstart', (e) => {
            touchStartY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            touchEndY = e.changedTouches[0].clientY;
            
            // 检测滑动方向
            const deltaY = touchEndY - touchStartY;
            
            // 如果向上滑动超过100px，可能是地址栏隐藏
            if (deltaY < -100) {
                setTimeout(() => {
                    this.setViewportHeight();
                    this.updateLayout();
                }, 300);
            }
            
            // 如果向下滑动超过100px，可能是地址栏显示
            if (deltaY > 100) {
                setTimeout(() => {
                    this.setViewportHeight();
                    this.updateLayout();
                }, 300);
            }
        }, { passive: true });
    }

    /**
     * 开始高度监控
     */
    startHeightMonitoring() {
        setInterval(() => {
            const currentHeight = window.innerHeight;
            const heightDiff = Math.abs(currentHeight - this.currentHeight);
            
            // 如果高度变化超过30px，更新视口
            if (heightDiff > 30) {
                console.log(`监控检测到视口高度变化: ${this.currentHeight}px -> ${currentHeight}px`);
                this.setViewportHeight();
                this.updateLayout();
            }
        }, 1000); // 每秒检查一次
    }

    /**
     * 更新布局
     */
    updateLayout() {
        // 触发自定义事件，通知其他组件更新
        const event = new CustomEvent('viewportHeightChanged', {
            detail: {
                height: window.innerHeight,
                vh: window.innerHeight * 0.01
            }
        });
        
        window.dispatchEvent(event);
        
        // 强制重新计算布局
        if (window.voiceWebSocketManager) {
            // 如果WebSocket管理器存在，通知它更新
            if (typeof window.voiceWebSocketManager.updateLayout === 'function') {
                window.voiceWebSocketManager.updateLayout();
            }
        }
    }

    /**
     * 获取当前视口信息
     */
    getViewportInfo() {
        return {
            width: window.innerWidth,
            height: window.innerHeight,
            vh: window.innerHeight * 0.01,
            vw: window.innerWidth * 0.01,
            isMobile: this.isMobile,
            isWeChat: this.isWeChat,
            orientation: window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
        };
    }

    /**
     * 手动更新视口高度
     */
    forceUpdate() {
        console.log('手动更新视口高度');
        this.setViewportHeight();
        this.updateLayout();
    }

    /**
     * 销毁处理器
     */
    destroy() {
        window.removeEventListener('resize', this.handleResize.bind(this));
        window.removeEventListener('orientationchange', this.handleOrientationChange.bind(this));
        document.removeEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        if (this.resizeTimeout) {
            clearTimeout(this.resizeTimeout);
        }
        
        if (this.orientationChangeTimeout) {
            clearTimeout(this.orientationChangeTimeout);
        }
    }
}

// 全局视口处理器
window.mobileViewportHandler = new MobileViewportHandler();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 延迟初始化，确保所有元素都已加载
    setTimeout(() => {
        if (window.mobileViewportHandler) {
            window.mobileViewportHandler.forceUpdate();
        }
    }, 100);
});

// 导出工具函数
window.getViewportInfo = function() {
    return window.mobileViewportHandler ? window.mobileViewportHandler.getViewportInfo() : null;
};

window.updateViewport = function() {
    if (window.mobileViewportHandler) {
        window.mobileViewportHandler.forceUpdate();
    }
};

// 监听视口高度变化事件
window.addEventListener('viewportHeightChanged', function(event) {
    console.log('视口高度已变化:', event.detail);
});

// 在微信浏览器中的特殊处理
if (window.mobileViewportHandler && window.mobileViewportHandler.isWeChat) {
    console.log('微信浏览器检测到，应用特殊视口处理');
    
    // 微信浏览器中，更频繁地检查视口变化
    setInterval(() => {
        if (window.mobileViewportHandler) {
            window.mobileViewportHandler.forceUpdate();
        }
    }, 2000); // 每2秒检查一次
}
