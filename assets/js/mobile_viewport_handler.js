/**
 * 移动端视口高度处理
 * 专门处理小屏幕、微信浏览器和动态视口变化
 */

class MobileViewportHandler {
    constructor() {
        this.isMobile = this.detectMobile();
        this.isWeChat = this.detectWeChat();
        this.isSmallScreen = this.detectSmallScreen();
        this.lastHeight = window.innerHeight;
        this.resizeTimeout = null;
        
        this.init();
    }

    /**
     * 检测移动端
     */
    detectMobile() {
        return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    /**
     * 检测微信浏览器
     */
    detectWeChat() {
        return navigator.userAgent.toLowerCase().includes('micromessenger');
    }

    /**
     * 检测小屏幕
     */
    detectSmallScreen() {
        return window.innerWidth <= 480 || window.innerHeight <= 900;
    }

    /**
     * 获取实际可视高度
     */
    getActualViewportHeight() {
        // 优先使用CSS环境变量支持
        if (CSS.supports('height', '100dvh')) {
            return window.innerHeight;
        }
        
        // 微信浏览器特殊处理
        if (this.isWeChat) {
            // 微信浏览器地址栏会动态变化，使用更保守的计算
            return Math.min(window.innerHeight, window.screen.height * 0.9);
        }
        
        // 移动端处理
        if (this.isMobile) {
            // 考虑地址栏高度
            const addressBarHeight = this.estimateAddressBarHeight();
            return window.innerHeight - addressBarHeight;
        }
        
        return window.innerHeight;
    }

    /**
     * 估算地址栏高度
     */
    estimateAddressBarHeight() {
        if (!this.isMobile) return 0;
        
        // 根据屏幕尺寸估算地址栏高度
        if (window.innerHeight <= 600) {
            return 60; // 小屏幕地址栏较高
        } else if (window.innerHeight <= 800) {
            return 50; // 中等屏幕
        } else {
            return 40; // 大屏幕地址栏较低
        }
    }

    /**
     * 动态调整布局高度
     */
    adjustLayoutHeights() {
        const actualHeight = this.getActualViewportHeight();
        
        // 调整主布局高度
        const mainLayout = document.getElementById('ai-chat-x-main-layout');
        if (mainLayout) {
            mainLayout.style.height = actualHeight + 'px';
            mainLayout.style.maxHeight = actualHeight + 'px';
        }
        
        // 调整主体布局高度
        const bodyLayout = mainLayout?.querySelector('.ant-layout');
        if (bodyLayout) {
            const headerHeight = this.getHeaderHeight();
            const adjustedHeight = actualHeight - headerHeight;
            bodyLayout.style.height = adjustedHeight + 'px';
            bodyLayout.style.maxHeight = adjustedHeight + 'px';
        }
        
        // 调整聊天历史高度
        const chatHistory = document.getElementById('ai-chat-x-history');
        if (chatHistory) {
            const headerHeight = this.getHeaderHeight();
            const footerHeight = this.getFooterHeight();
            const adjustedHeight = actualHeight - headerHeight - footerHeight - 100; // 100px缓冲
            chatHistory.style.height = adjustedHeight + 'px';
            chatHistory.style.maxHeight = adjustedHeight + 'px';
        }
        
        this.lastHeight = actualHeight;
    }

    /**
     * 获取页首高度
     */
    getHeaderHeight() {
        const header = document.getElementById('ai-chat-x-header');
        if (header) {
            return header.offsetHeight;
        }
        return 50; // 默认高度
    }

    /**
     * 获取页尾高度
     */
    getFooterHeight() {
        const footer = document.querySelector('.ant-layout-footer');
        if (footer) {
            return footer.offsetHeight;
        }
        return 100; // 默认高度
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
            const currentHeight = window.innerHeight;
            
            // 只有高度变化超过10px才重新调整
            if (Math.abs(currentHeight - this.lastHeight) > 10) {
                this.adjustLayoutHeights();
            }
        }, 100);
    }

    /**
     * 处理方向变化
     */
    handleOrientationChange() {
        // 延迟处理，等待方向变化完成
        setTimeout(() => {
            this.adjustLayoutHeights();
        }, 500);
    }

    /**
     * 处理微信浏览器特殊事件
     */
    handleWeChatEvents() {
        if (!this.isWeChat) return;
        
        // 监听微信浏览器的页面显示/隐藏事件
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                setTimeout(() => {
                    this.adjustLayoutHeights();
                }, 100);
            }
        });
        
        // 监听微信浏览器的页面滚动事件（可能影响地址栏显示）
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.adjustLayoutHeights();
            }, 150);
        });
    }

    /**
     * 添加CSS类名标识
     */
    addBodyClasses() {
        const body = document.body;
        
        if (this.isMobile) {
            body.classList.add('mobile-device');
        }
        
        if (this.isWeChat) {
            body.classList.add('wechat-browser');
        }
        
        if (this.isSmallScreen) {
            body.classList.add('small-screen');
        }
        
        // 添加视口高度类名
        const height = window.innerHeight;
        if (height <= 600) {
            body.classList.add('viewport-small');
        } else if (height <= 800) {
            body.classList.add('viewport-medium');
        } else {
            body.classList.add('viewport-large');
        }
    }

    /**
     * 初始化
     */
    init() {
        // 添加CSS类名
        this.addBodyClasses();
        
        // 初始调整
        this.adjustLayoutHeights();
        
        // 绑定事件
        window.addEventListener('resize', () => this.handleResize());
        window.addEventListener('orientationchange', () => this.handleOrientationChange());
        
        // 微信浏览器特殊处理
        this.handleWeChatEvents();
        
        // 页面加载完成后再次调整
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                this.adjustLayoutHeights();
            }, 100);
        });
        
        // 页面完全加载后最终调整
        window.addEventListener('load', () => {
            setTimeout(() => {
                this.adjustLayoutHeights();
            }, 200);
        });
        
        console.log('移动端视口处理器已初始化', {
            isMobile: this.isMobile,
            isWeChat: this.isWeChat,
            isSmallScreen: this.isSmallScreen,
            viewportHeight: window.innerHeight
        });
    }
}

// 全局初始化
window.mobileViewportHandler = new MobileViewportHandler();

// 导出供其他模块使用
window.getMobileViewportInfo = function() {
    return {
        isMobile: window.mobileViewportHandler.isMobile,
        isWeChat: window.mobileViewportHandler.isWeChat,
        isSmallScreen: window.mobileViewportHandler.isSmallScreen,
        actualHeight: window.mobileViewportHandler.getActualViewportHeight()
    };
};
