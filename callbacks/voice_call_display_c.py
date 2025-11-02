"""
语音实时对话文本显示回调处理
处理语音实时对话文本显示相关的Dash回调
"""

from dash import Input, Output, no_update, State, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
from utils.log import log
from server import app


# 🔧 关键修复：Drawer不显示关闭按钮，只通过挂断语音通话来关闭
# Drawer的显示/隐藏直接通过JavaScript的set_props控制（挂断语音通话时自动关闭）
# 已移除关闭按钮回调，因为closable=False


# 🔧 关键修复：添加clientside callback在Drawer显示时自动设置高度和位置（与chat_history对齐）
app.clientside_callback(
    """
    function(visible) {
        // 🔧 关键修复：只在显示时才应用样式，并且使用闭包跟踪previous value避免重复触发
        if (!window._voiceCallDrawerVisible) {
            window._voiceCallDrawerVisible = false;
        }
        
        // 🔧 只在从隐藏变为显示时才应用样式，避免关闭后重新触发
        if (visible && !window._voiceCallDrawerVisible) {
            // 更新previous value
            window._voiceCallDrawerVisible = true;
            // Drawer显示时，动态计算并设置高度和位置，与chat_history完全对齐
            const applyStyles = () => {
                // 获取chat_history元素的位置和高度
                const chatHistory = document.getElementById('ai-chat-x-history');
                if (!chatHistory) {
                    window.controlledLog?.warn('⚠️ [Clientside] 未找到chat_history元素');
                    return;
                }
                
                // 获取chat_history的实际位置
                const chatHistoryRect = chatHistory.getBoundingClientRect();
                const chatHistoryTop = chatHistoryRect.top;
                const chatHistoryHeight = chatHistoryRect.height;
                
                // 查找Drawer元素
                const drawer = document.getElementById('voice-call-text-drawer');
                if (!drawer) {
                    window.controlledLog?.warn('⚠️ [Clientside] 未找到Drawer元素');
                    return;
                }
                
                // 🔧 关键修复：直接查找所有可能的Drawer容器元素并设置样式（与chat_history对齐）
                const drawerContentWrapper = drawer.closest('.ant-drawer-content-wrapper') || 
                                             drawer.querySelector('.ant-drawer-content-wrapper');
                const drawerContent = drawer.closest('.ant-drawer-content') ||
                                      drawer.querySelector('.ant-drawer-content') ||
                                      (drawer.classList && drawer.classList.contains('ant-drawer-content') ? drawer : null);
                
                // 设置Drawer content-wrapper样式（外层容器）
                if (drawerContentWrapper) {
                    drawerContentWrapper.style.setProperty('top', chatHistoryTop + 'px', 'important');
                    drawerContentWrapper.style.setProperty('height', chatHistoryHeight + 'px', 'important');
                    drawerContentWrapper.style.setProperty('max-height', chatHistoryHeight + 'px', 'important');
                    drawerContentWrapper.style.setProperty('position', 'fixed', 'important');
                    drawerContentWrapper.style.setProperty('bottom', 'auto', 'important');
                }
                
                // 设置Drawer content样式（内容容器）
                if (drawerContent) {
                    drawerContent.style.setProperty('top', chatHistoryTop + 'px', 'important');
                    drawerContent.style.setProperty('height', chatHistoryHeight + 'px', 'important');
                    drawerContent.style.setProperty('max-height', chatHistoryHeight + 'px', 'important');
                    drawerContent.style.setProperty('position', 'fixed', 'important');
                    drawerContent.style.setProperty('bottom', 'auto', 'important');
                    drawerContent.style.setProperty('display', 'flex', 'important');
                    drawerContent.style.setProperty('flex-direction', 'column', 'important');
                }
                
                // 🔧 关键修复：强制移除body的固定高度设置，让它自然占据剩余空间（减去header高度）
                const drawerBody = drawer.querySelector('.ant-drawer-body') ||
                                   (drawerContent ? drawerContent.querySelector('.ant-drawer-body') : null);
                if (drawerBody) {
                    // 强制移除所有可能导致占满屏幕的样式
                    drawerBody.style.removeProperty('height');
                    drawerBody.style.removeProperty('max-height');
                    drawerBody.style.removeProperty('min-height');
                    drawerBody.style.removeProperty('top');
                    drawerBody.style.removeProperty('bottom');
                    drawerBody.style.removeProperty('position');
                    // 强制设置flex布局，让body占据剩余空间
                    drawerBody.style.setProperty('overflow', 'hidden', 'important');
                    drawerBody.style.setProperty('display', 'flex', 'important');
                    drawerBody.style.setProperty('flex-direction', 'column', 'important');
                    drawerBody.style.setProperty('height', 'auto', 'important');
                    drawerBody.style.setProperty('flex', '1', 'important');
                    drawerBody.style.setProperty('min-height', '0', 'important');
                }
                
                window.controlledLog?.log('✅ [Clientside] 已设置Drawer高度和位置，与chat_history对齐:', {
                    top: chatHistoryTop,
                    height: chatHistoryHeight
                });
            };
            
            // 立即执行
            applyStyles();
            // 延迟执行（确保DOM已完全渲染）
            setTimeout(applyStyles, 50);
            setTimeout(applyStyles, 200);
            setTimeout(applyStyles, 500);
        } else if (!visible && window._voiceCallDrawerVisible) {
            // 🔧 关键修复：当Drawer隐藏时，更新previous value并确保完全隐藏
            window._voiceCallDrawerVisible = false;
            window.controlledLog?.log('✅ [Clientside] Drawer已隐藏，更新previous value');
        }
        // 🔧 关键修复：返回no_update，避免关闭后重新触发显示
        return window.dash_clientside ? window.dash_clientside.no_update : undefined;
    }
    """,
    Output('voice-call-text-drawer', 'id'),  # 使用id作为输出，实际不更新，只是触发回调
    Input('voice-call-text-drawer', 'visible'),  # 🔧 移除State，使用闭包跟踪previous value
    prevent_initial_call=False
)

