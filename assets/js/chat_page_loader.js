/**
 * 聊天页面专用JS加载器
 * 只在聊天页面加载，避免其他页面的性能影响
 */

(function() {
    'use strict';
    
    // 防止重复执行
    if (window.chatPageLoaderExecuted) {
        console.log('chat_page_loader.js 已执行过，跳过重复执行');
        return;
    }
    window.chatPageLoaderExecuted = true;
    
    // 检查是否在聊天页面 - 精确匹配
    const currentPath = window.location.pathname;
    
    // 特殊处理：根路径默认不是聊天页面
    if (currentPath === '/') {
        console.log('根路径，跳过聊天相关JS加载:', currentPath);
        return;
    }
    
    // 调试信息
    console.log('页面检测开始:', {
        currentPath: currentPath,
        timestamp: new Date().toISOString()
    });
    
    // 更严格的聊天页面检测
    const chatPagePatterns = [
        '/core/chat',          // 核心聊天页面
        '/core/chat/',         // 核心聊天页面带斜杠
        '/core/chat?',         // 核心聊天页面带查询参数
        '/core/chat#'          // 核心聊天页面带锚点
    ];
    
    const isChatPage = chatPagePatterns.some(pattern => {
        // 精确匹配，避免误匹配
        if (pattern.endsWith('/')) {
            return currentPath === pattern || currentPath.startsWith(pattern);
        } else {
            return currentPath === pattern || currentPath.startsWith(pattern + '/') || currentPath.startsWith(pattern + '?') || currentPath.startsWith(pattern + '#');
        }
    });
    
    // 排除其他页面路径（但保留聊天页面）
    const excludePatterns = [
        '/core/users',         // 用户管理页面
        '/core/admin',         // 管理页面
        '/core/settings',      // 设置页面
        '/admin/',
        '/api/',
        '/static/',
        '/assets/',
        '/login',
        '/logout',
        '/register'
    ];
    
    const isExcludedPage = excludePatterns.some(pattern => currentPath.startsWith(pattern));
    
    // 调试信息
    console.log('页面检测结果:', {
        currentPath: currentPath,
        isChatPage: isChatPage,
        isExcludedPage: isExcludedPage,
        shouldLoad: isChatPage && !isExcludedPage,
        chatPagePatterns: chatPagePatterns,
        excludePatterns: excludePatterns
    });
    
    if (!isChatPage || isExcludedPage) {
        console.log('非聊天页面，跳过聊天相关JS加载:', currentPath);
        return;
    }
    
    console.log('✅ 检测到聊天页面，开始并行加载聊天相关JS...', currentPath);
    
    // 聊天页面专用配置
    window.chatPageConfig = {
        isChatPage: true,
        loadTime: Date.now(),
        version: '1.0.0'
    };
    
    // 注意：即使 Dash 已经自动加载了部分 JS 文件，我们仍然使用并行加载机制
    // 这样可以确保所有文件都加载完成后再初始化，并且可以控制加载顺序
    
    // 动态加载JS文件的函数（支持并行加载）
    function loadScript(src) {
        return new Promise((resolve, reject) => {
            // 检查是否已经加载过
            const existingScript = document.querySelector(`script[src="${src}"]`);
            if (existingScript) {
                console.log('脚本已存在，跳过加载:', src);
                resolve();
                return;
            }
            
            // 检查全局对象是否已存在（防止重复声明）
            const scriptName = src.split('/').pop().replace('.js', '');
            if (window[scriptName] || window[scriptName.charAt(0).toUpperCase() + scriptName.slice(1)]) {
                console.log('脚本类已存在，跳过加载:', src);
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = src;
            script.async = true; // 启用并行下载
            script.onload = () => {
                console.log('✅ 脚本加载成功:', src);
                resolve();
            };
            script.onerror = () => {
                console.error('❌ 脚本加载失败:', src);
                reject(new Error(`Failed to load script: ${src}`));
            };
            document.head.appendChild(script);
        });
    }
    
    // 聊天相关JS文件列表（按依赖关系分组）
    const chatScripts = [
        // 状态管理器相关（可以并行）
        '/assets/js/state_manager.js',
        '/assets/js/state_manager_adapter.js',
        '/assets/js/voice_state_manager.js',
        
        // 语音功能相关（可以并行）
        '/configs/voice_config.js',
        '/assets/js/voice_websocket_manager.js',
        
        // UI优化组件（可以并行）
        '/assets/js/enhanced_audio_visualizer.js',
        '/assets/js/enhanced_playback_status.js',
        '/assets/js/smart_error_handler.js',
        '/assets/js/state_sync_manager.js',
        '/assets/js/smart_state_predictor.js',
        '/assets/js/adaptive_ui.js',
        
        // 语音录制和播放（可以并行）
        '/assets/js/voice_recorder_enhanced.js',
        '/assets/js/voice_player_enhanced.js',
        
        // 实时语音相关（可以并行）
        '/assets/js/realtime_api_client.js',
        '/assets/js/realtime_audio_processor.js',
        '/assets/js/realtime_adapter_client.js',
        '/assets/js/realtime_voice_manager.js',
        '/assets/js/realtime_voice_callbacks.js'
    ];
    
    // 并行加载所有聊天脚本
    async function loadScriptsInParallel(scripts) {
        const startTime = Date.now();
        console.log('🚀 开始并行加载聊天相关JS，共', scripts.length, '个文件');
        
        try {
            // 使用 Promise.all 并行加载所有脚本
            await Promise.all(scripts.map(script => loadScript(script)));
            
            const loadTime = Date.now() - startTime;
            console.log('✅ 所有聊天相关JS加载完成，耗时:', loadTime, 'ms');
            
            // 触发聊天页面初始化事件
            window.dispatchEvent(new CustomEvent('chatPageReady', {
                detail: { 
                    loadTime: Date.now(),
                    duration: loadTime,
                    scriptCount: scripts.length
                }
            }));
        } catch (error) {
            console.error('❌ 聊天相关JS加载失败:', error);
            // 即使部分脚本加载失败，也触发初始化事件（可选）
            window.dispatchEvent(new CustomEvent('chatPageReady', {
                detail: { 
                    loadTime: Date.now(),
                    error: error.message
                }
            }));
        }
    }
    
    // 等待基础配置加载完成后开始加载聊天JS
    function waitForBaseConfig() {
        if (window.config && window.controlledLog) {
            console.log('✅ 基础配置已就绪，开始并行加载聊天相关JS');
            loadScriptsInParallel(chatScripts);
        } else {
            setTimeout(waitForBaseConfig, 100);
        }
    }
    
    // 开始加载流程
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', waitForBaseConfig);
    } else {
        waitForBaseConfig();
    }
    
})();
