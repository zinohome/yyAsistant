// 改造console.error()以隐藏无关痛痒的警告信息
const originalConsoleError = console.error;
console.error = function (...args) {
    // 检查args中是否包含需要过滤的内容
    const shouldFilter = args.some(arg => typeof arg === 'string' && arg.includes('Warning:'));

    if (!shouldFilter) {
        originalConsoleError.apply(console, args);
    }
};

if (!window.dash_clientside) {
    window.dash_clientside = {};
}

// 初始化clientside对象（确保只定义一次）
window.dash_clientside.clientside = {
    // 处理SSE连接启动 - 统一版本
    // 处理SSE连接启动 - 统一版本
startSSE: function(input) {
    // console.log('startSSE函数被调用，输入:', input);
    
    // 兼容两种参数格式：如果是数组则处理为triggerIds，否则处理为divId
    let messageId;
    
    if (Array.isArray(input) && input.length > 0) {
        // 处理triggerIds数组格式
        const lastTriggerId = input[input.length - 1];
        messageId = lastTriggerId.replace('sse-trigger-', '');
    } else if (typeof input === 'string') {
        // 处理divId字符串格式
        messageId = input.replace('sse-trigger-', '');
    }
    
    if (messageId) {
        // console.log('从clientside调用startSSE，消息ID:', messageId);
        
        // 使用正确的ID获取会话ID和消息列表
        const sessionIdEl = document.getElementById('ai-chat-x-current-session-id');
        // console.log('会话ID元素是否存在:', !!sessionIdEl);
        const sessionId = sessionIdEl?.value || '';
        // console.log('获取到的会话ID:', sessionId);
        
        let messages = [];
        try {
            const messagesStore = document.getElementById('ai-chat-x-messages-store');
            // console.log('消息存储元素是否存在:', !!messagesStore);
            if (messagesStore) {
                messages = JSON.parse(messagesStore.value || '[]');
                // console.log('获取到的消息数量:', messages.length);
                // console.log('消息内容示例:', messages.length > 0 ? JSON.stringify(messages[0]) : '无消息');
            }
        } catch (e) {
            console.error('获取消息列表失败:', e);
        }
        
        // 调用全局函数，传递完整参数
        if (window.startSSEConnection) {
            // console.log('准备调用window.startSSEConnection');
            window.startSSEConnection(messageId, sessionId, messages);
        } else {
            console.error('未找到startSSEConnection函数');
            // 如果找不到全局函数，尝试直接在页面中查找并执行
            setTimeout(() => {
                if (window.startSSEConnection) {
                    // console.log('延迟后找到startSSEConnection函数，尝试调用');
                    window.startSSEConnection(messageId, sessionId, messages);
                }
            }, 500);
        }
    }
    return window.dash_clientside.no_update;
}
};

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside_basic: {
        // 处理核心页面侧边栏展开/收起
        handleSideCollapse: (nClicks, originIcon, originHeaderSideStyle, coreConfig) => {
            // 若先前为展开状态
            if (originIcon === 'antd-menu-fold') {
                return [
                    // 更新图标
                    'antd-menu-unfold',
                    // 更新页首侧边容器样式
                    {
                        ...originHeaderSideStyle,
                        width: 110
                    },
                    // 更新页首标题样式
                    {
                        display: 'none'
                    },
                    // 更新侧边菜单容器样式
                    {
                        width: 110
                    },
                    // 更新侧边菜单折叠状态
                    true
                ]
            } else {
                return [
                    // 更新图标
                    'antd-menu-fold',
                    // 更新页首侧边容器样式
                    {
                        ...originHeaderSideStyle,
                        width: coreConfig.core_side_width
                    },
                    // 更新页首标题样式
                    {},
                    // 更新侧边菜单容器样式
                    {
                        width: coreConfig.core_side_width
                    },
                    // 更新侧边菜单折叠状态
                    false
                ]
            }
        },
        // 控制页面搜索切换页面的功能
        handleCorePageSearch: (value) => {
            if (value) {
                let pathname = value.split('|')[0]
                // 更新pathname
                window.location.pathname = pathname
            }
        },
        // 控制ctrl+k快捷键触发页面搜索框聚焦
        handleCorePageSearchFocus: (pressedCounts) => {
            return [true, pressedCounts.toString()]
        },
        // 处理多标签页形式下的标签页关闭操作
        handleCoreTabsClose: (tabCloseCounts, clickedContextMenu, latestDeletePane, items) => {
            // 获取本次回调触发来源信息
            callbackTriggered = window.dash_clientside.callback_context.triggered[0];

            // 若本次回调由标签页标题右键菜单操作触发
            if (callbackTriggered.prop_id.endsWith('clickedContextMenu')) {
                if (clickedContextMenu.menuKey === '关闭当前') {
                    // 计算下一状态对应标签页子项列表
                    let next_items = items.filter(item => item.key !== clickedContextMenu.tabKey);

                    return [
                        next_items,
                        // 默认在下一状态选中末尾的有效标签页
                        next_items[next_items.length - 1].key
                    ];
                } else if (clickedContextMenu.menuKey === '关闭其他') {
                    // 计算下一状态对应标签页子项列表
                    let next_items = items.filter(item => (item.key === clickedContextMenu.tabKey) || (item.key === '/'));

                    return [
                        next_items,
                        // 下一状态激活当前触发源标签页
                        clickedContextMenu.tabKey
                    ];
                } else if (clickedContextMenu.menuKey == '关闭所有') {
                    // 计算下一状态对应标签页子项列表
                    let next_items = items.filter(item => item.key === '/');

                    return [
                        next_items,
                        // 下一状态激活首页标签页
                        '/'
                    ];
                } else if (clickedContextMenu.menuKey === '刷新页面') {

                    // 触发页面刷新
                    window.dash_clientside.set_props(
                        'global-reload',
                        {
                            reload: true
                        }
                    )

                    return window.dash_clientside.no_update;
                }
            }

            // 否则，则本次回调由标签页关闭按钮触发
            // 计算下一状态对应标签页子项列表
            let next_items = items.filter(item => item.key !== latestDeletePane);

            return [
                next_items,
                // 默认在下一状态选中末尾的有效标签页
                next_items[next_items.length - 1].key
            ];
        },
        handleCoreFullscreenToggle: (nClicks, isFullscreen, icon) => {

            let _isFullscreen;

            if (window.dash_clientside.callback_context.triggered_id === 'core-fullscreen') {
                _isFullscreen = isFullscreen
            } else {
                _isFullscreen = icon === 'antd-full-screen'
            }

            return (
                _isFullscreen ?
                    [true, 'antd-full-screen-exit'] :
                    [false, 'antd-full-screen']
            )
        },
        // 处理聊天会话列表折叠
        handleChatSessionMenuCollapse: (nClicks, collapsed) => {
            // 切换折叠状态
            const newCollapsedState = !collapsed;
            // 根据新的折叠状态返回相应的图标
            const newIcon = newCollapsedState ? 'antd-arrow-right' : 'antd-arrow-left';
            
            return [newCollapsedState, newIcon];
        },
        // 在clientside_basic对象末尾添加以下函数
        // 处理健康档案抽屉的响应式宽度
        handleResponsiveDrawerWidth: () => {
            // 获取当前窗口宽度
            const windowWidth = window.innerWidth;
            
            // 判断屏幕尺寸并返回相应的宽度值
            // 小屏幕(≤575px)下使用80vw，其他情况使用65vw
            return windowWidth <= 575 ? "100vw" : "65vw";
        },
        // 新增：SSE自动重连管理
        manageSSEReconnection: (messageId, sessionId, messages, maxRetries = 3) => {
            // 存储重连信息
            if (!window.sseReconnectInfo) {
                window.sseReconnectInfo = {};
            }
            
            const reconnectKey = `${messageId}_${sessionId}`;
            const reconnectInfo = window.sseReconnectInfo[reconnectKey] || {
                retryCount: 0,
                maxRetries: maxRetries,
                baseDelay: 1000, // 基础延迟1秒
                isReconnecting: false
            };
            
            // 如果正在重连或已达到最大重试次数，则不再重连
            if (reconnectInfo.isReconnecting || reconnectInfo.retryCount >= reconnectInfo.maxRetries) {
                // console.log(`SSE重连已达到最大次数或正在重连中: ${reconnectKey}`);
                return;
            }
            
            reconnectInfo.isReconnecting = true;
            reconnectInfo.retryCount++;
            
            // 计算延迟时间（指数退避）
            const delay = reconnectInfo.baseDelay * Math.pow(2, reconnectInfo.retryCount - 1);
            
            // console.log(`SSE连接断开，${delay}ms后进行第${reconnectInfo.retryCount}次重连: ${reconnectKey}`);
            
            setTimeout(() => {
                try {
                    // 重新启动SSE连接
                    if (window.startSSEConnection) {
                        window.startSSEConnection(messageId, sessionId, messages);
                        // console.log(`SSE重连尝试完成: ${reconnectKey}`);
                    }
                } catch (error) {
                    console.error(`SSE重连失败: ${reconnectKey}`, error);
                } finally {
                    reconnectInfo.isReconnecting = false;
                }
            }, delay);
            
            // 更新重连信息
            window.sseReconnectInfo[reconnectKey] = reconnectInfo;
        },
        // 清理SSE重连信息
        clearSSEReconnectInfo: (messageId, sessionId) => {
            if (window.sseReconnectInfo) {
                const reconnectKey = `${messageId}_${sessionId}`;
                delete window.sseReconnectInfo[reconnectKey];
                // console.log(`清理SSE重连信息: ${reconnectKey}`);
            }
        },
        // 新增：SSE超时检测
        startSSETimeoutMonitor: (messageId, timeoutSeconds = 30) => {
            // 清理之前的超时检测器
            if (window.sseTimeoutMonitors) {
                const existingMonitor = window.sseTimeoutMonitors[messageId];
                if (existingMonitor) {
                    clearTimeout(existingMonitor);
                }
            } else {
                window.sseTimeoutMonitors = {};
            }
            
            // 设置新的超时检测器
            const timeoutId = setTimeout(() => {
                console.warn(`SSE连接超时: ${messageId}`);
                
                // 触发超时处理
                const event = new CustomEvent('sseTimeout', {
                    detail: { messageId: messageId }
                });
                document.dispatchEvent(event);
                
                // 清理超时检测器
                if (window.sseTimeoutMonitors) {
                    delete window.sseTimeoutMonitors[messageId];
                }
            }, timeoutSeconds * 1000);
            
            window.sseTimeoutMonitors[messageId] = timeoutId;
            // console.log(`启动SSE超时检测: ${messageId}, 超时时间: ${timeoutSeconds}秒`);
        },
        // 清理SSE超时检测器
        clearSSETimeoutMonitor: (messageId) => {
            if (window.sseTimeoutMonitors && window.sseTimeoutMonitors[messageId]) {
                clearTimeout(window.sseTimeoutMonitors[messageId]);
                delete window.sseTimeoutMonitors[messageId];
                // console.log(`清理SSE超时检测器: ${messageId}`);
            }
        },
        // 新增：优化的自动滚动到底部函数
        autoScrollToBottom: (force = false) => {
            const historyContainer = document.getElementById('ai-chat-x-history');
            if (!historyContainer) {
                console.warn('未找到聊天历史容器');
                return;
            }
            
            // 检查用户是否正在查看历史消息（不在底部）
            let isAtBottom = true;
            if (window.userScrollPosition) {
                isAtBottom = window.userScrollPosition.isAtBottom();
            } else {
                // 如果没有滚动监听器，直接检查当前位置
                isAtBottom = historyContainer.scrollTop + historyContainer.clientHeight >= historyContainer.scrollHeight - 10;
            }
            
            // 如果用户不在底部且不是强制滚动，则不自动滚动
            if (!isAtBottom && !force) {
                // console.log('用户正在查看历史消息，跳过自动滚动');
                return;
            }
            
            // 执行滚动
            const maxScroll = historyContainer.scrollHeight - historyContainer.clientHeight;
            if (maxScroll > 0) {
                // 使用平滑滚动
                historyContainer.scrollTo({
                    top: maxScroll,
                    behavior: 'smooth'
                });
                // console.log('自动滚动到底部');
                
                // 更新用户位置状态
                if (window.userScrollPosition) {
                    window.userScrollPosition.setAtBottom(true);
                }
            }
        },
        // 强制滚动到底部（用于消息完成时）
        forceScrollToBottom: () => {
            if (window.dash_clientside && window.dash_clientside.clientside_basic && window.dash_clientside.clientside_basic.autoScrollToBottom) {
                window.dash_clientside.clientside_basic.autoScrollToBottom(true);
            }
        },
        // 初始化滚动监听器
        initScrollListener: () => {
            const historyContainer = document.getElementById('ai-chat-x-history');
            if (!historyContainer) {
                console.warn('未找到聊天历史容器，无法初始化滚动监听器');
                return;
            }
            
            // 存储用户是否在底部
            let userAtBottom = true;
            let scrollTimeout = null;
            
            // 监听滚动事件
            historyContainer.addEventListener('scroll', () => {
                // 清除之前的超时
                if (scrollTimeout) {
                    clearTimeout(scrollTimeout);
                }
                
                // 检查是否在底部（允许10px的误差）
                const isAtBottom = historyContainer.scrollTop + historyContainer.clientHeight >= historyContainer.scrollHeight - 10;
                userAtBottom = isAtBottom;
                
                // 设置超时，如果用户停止滚动1秒后仍在底部，则恢复自动滚动
                scrollTimeout = setTimeout(() => {
                    if (isAtBottom) {
                        // console.log('用户滚动到底部，恢复自动滚动');
                    }
                }, 1000);
            });
            
            // 将用户位置状态存储到全局，供autoScrollToBottom使用
            window.userScrollPosition = {
                isAtBottom: () => userAtBottom,
                setAtBottom: (value) => { userAtBottom = value; }
            };
            
            // console.log('滚动监听器初始化完成');
        }
    }
});
