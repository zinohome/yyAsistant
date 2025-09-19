import dash
from dash import Input, Output, State, ctx
import feffery_antd_components as fac
from server import app
from feffery_dash_utils.style_utils import style
import dash.html as html
import time
from datetime import datetime
from components.chat_session_list import render as render_session_list

# 添加自定义折叠按钮的客户端回调函数 - 支持切换本地SVG图标
app.clientside_callback(
    """(nClicks, collapsed, currentStyle) => {
        // 切换折叠状态并根据状态返回对应的图标路径
        const newCollapsedState = !collapsed;
        const iconSrc = newCollapsedState ? '/assets/imgs/right.svg' : '/assets/imgs/left.svg';
        
        // 控制新建会话按钮的显示/隐藏 - 只更新display属性，保留其他样式
        const updatedStyle = {...currentStyle, display: newCollapsedState ? 'none' : 'flex'};
        
        return [newCollapsedState, iconSrc, updatedStyle];
    }""",
    [
        Output('ai-chat-x-session-container', 'collapsed'),
        Output('ai-chat-x-session-collapse-trigger-icon', 'src'),  # 修改为src属性而不是icon
        Output('ai-chat-x-session-new', 'style')  # 添加对新建会话按钮样式的控制
    ],
    Input('ai-chat-x-session-collapse-trigger', 'nClicks'),
    [
        State('ai-chat-x-session-container', 'collapsed'),
        State('ai-chat-x-session-new', 'style')  # 获取当前样式状态
    ],
    prevent_initial_call=True,
)

# 添加处理"我的信息"菜单项点击事件的回调函数
@app.callback(
    Output("my-info-drawer", "visible"),
    Input("ai-chat-x-user-dropdown", "recentlyButtonClickedKey"),
    prevent_initial_call=True,
)
def handle_my_info_click(recentlyButtonClickedKey):
    """处理用户下拉菜单中"我的信息"项的点击事件"""
    if recentlyButtonClickedKey == "我的信息":
        return True
    return dash.no_update