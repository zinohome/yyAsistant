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
    
    // 文件到全局对象的映射（用于检查是否已加载）
    const scriptGlobalObjects = {
        '/assets/js/state_manager.js': ['StateManager', 'stateManager'],
        '/assets/js/state_manager_adapter.js': ['StateManagerAdapter', 'unifiedButtonStateManager'],
        '/assets/js/voice_state_manager.js': ['VoiceStateManager'],
        '/assets/js/voice_config.js': ['VoiceConfig', 'voiceConfig'],
        '/assets/js/voice_websocket_manager.js': ['VoiceWebSocketManager', 'voiceWebSocketManager'],
        '/assets/js/state_sync_manager.js': ['StateSyncManager', 'stateSyncManager'],
        '/assets/js/enhanced_audio_visualizer.js': ['EnhancedAudioVisualizer', 'enhancedAudioVisualizer'],
        '/assets/js/enhanced_playback_status.js': ['EnhancedPlaybackStatus', 'enhancedPlaybackStatus'],
        '/assets/js/smart_error_handler.js': ['SmartErrorHandler', 'smartErrorHandler'],
        '/assets/js/smart_state_predictor.js': ['SmartStatePredictor', 'smartStatePredictor'],
        '/assets/js/adaptive_ui.js': ['AdaptiveUI', 'adaptiveUI'],
        '/assets/js/voice_recorder_enhanced.js': ['VoiceRecorderEnhanced', 'voiceRecorder'],
        '/assets/js/voice_player_enhanced.js': ['VoicePlayerEnhanced', 'voicePlayer'],
        '/assets/js/realtime_api_client.js': ['RealtimeAPIClient', 'realtimeAPIClient'],
        '/assets/js/realtime_audio_processor.js': ['RealtimeAudioProcessor', 'realtimeAudioProcessor'],
        '/assets/js/realtime_adapter_client.js': ['RealtimeAdapterClient', 'realtimeAdapterClient'],
        '/assets/js/realtime_voice_manager.js': ['RealtimeVoiceManager', 'realtimeVoiceManager'],
        '/assets/js/realtime_voice_callbacks.js': ['DOM_CACHE']
    };
    
    // 检查脚本是否已加载（通过检查全局对象和script标签）
    function isScriptLoaded(src) {
        // 检查全局对象是否已存在（这是最可靠的方法）
        const globalObjects = scriptGlobalObjects[src];
        if (globalObjects) {
            for (const objName of globalObjects) {
                if (window[objName] !== undefined) {
                    console.log(`✅ 检测到全局对象 ${objName} 已存在，跳过加载: ${src}`);
                    return true;
                }
            }
        }
        
        // 检查script标签是否已存在（包括带版本号的路径）
        const fileName = src.split('/').pop();
        const allScripts = document.querySelectorAll('script[src]');
        for (const script of allScripts) {
            const scriptSrc = script.getAttribute('src');
            // 检查是否包含文件名（可能带版本号）
            if (scriptSrc && scriptSrc.includes(fileName)) {
                console.log(`✅ 检测到script标签已存在，跳过加载: ${src} (实际路径: ${scriptSrc})`);
                return true;
            }
        }
        
        return false;
    }
    
    // 动态加载JS文件的函数（支持并行加载）
    function loadScript(src) {
        return new Promise((resolve, reject) => {
            // 检查是否已经加载过
            if (isScriptLoaded(src)) {
                console.log('✅ 脚本已加载，跳过:', src);
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
    // 注意：有依赖关系的文件需要分组加载，组内并行，组间顺序
    const chatScriptGroups = [
        // 第一组：基础状态管理器（可以并行）
        [
            '/assets/js/state_manager.js',
            '/assets/js/state_manager_adapter.js',
            '/assets/js/voice_state_manager.js',
        ],
        // 第二组：语音配置（可以并行）
        [
            '/assets/js/voice_config.js',  // 使用assets路径，而不是configs路径
            '/assets/js/voice_websocket_manager.js',
        ],
        // 第三组：UI优化组件（可以并行，但state_sync_manager需要先加载）
        [
            '/assets/js/state_sync_manager.js',  // 必须先加载，因为smart_state_predictor依赖它
        ],
        // 第四组：依赖state_sync_manager的组件（可以并行）
        [
            '/assets/js/enhanced_audio_visualizer.js',
            '/assets/js/enhanced_playback_status.js',
            '/assets/js/smart_error_handler.js',
            '/assets/js/smart_state_predictor.js',  // 依赖state_sync_manager
            '/assets/js/adaptive_ui.js',
        ],
        // 第五组：语音录制和播放（可以并行）
        [
            '/assets/js/voice_recorder_enhanced.js',
            '/assets/js/voice_player_enhanced.js',
        ],
        // 第六组：实时语音相关（可以并行）
        [
            '/assets/js/realtime_api_client.js',
            '/assets/js/realtime_audio_processor.js',
            '/assets/js/realtime_adapter_client.js',
            '/assets/js/realtime_voice_manager.js',
            '/assets/js/realtime_voice_callbacks.js'
        ]
    ];
    
    // 分组并行加载：组内并行，组间顺序
    async function loadScriptsInGroups(groups) {
        const startTime = Date.now();
        const totalScripts = groups.reduce((sum, group) => sum + group.length, 0);
        console.log('🚀 开始分组并行加载聊天相关JS，共', groups.length, '组，', totalScripts, '个文件');
        
        try {
            // 按组顺序加载，每组内部并行
            for (let i = 0; i < groups.length; i++) {
                const group = groups[i];
                console.log(`📦 加载第 ${i + 1}/${groups.length} 组，共 ${group.length} 个文件`);
                
                // 组内并行加载
                await Promise.all(group.map(script => loadScript(script)));
                
                console.log(`✅ 第 ${i + 1} 组加载完成`);
            }
            
            const loadTime = Date.now() - startTime;
            console.log('✅ 所有聊天相关JS加载完成，耗时:', loadTime, 'ms');
            
            // 触发聊天页面初始化事件
            window.dispatchEvent(new CustomEvent('chatPageReady', {
                detail: { 
                    loadTime: Date.now(),
                    duration: loadTime,
                    scriptCount: totalScripts,
                    groupCount: groups.length
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
            console.log('✅ 基础配置已就绪，开始分组并行加载聊天相关JS');
            loadScriptsInGroups(chatScriptGroups);
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
