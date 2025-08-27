import dash
from dash import Input, Output, State, ctx
import feffery_antd_components as fac
from server import app
from feffery_dash_utils.style_utils import style
import dash.html as html
import time
from datetime import datetime
from components.chat_session_list import render as render_session_list

@app.callback(
    Output('ai-chat-x-session-container', 'children'),
    Output('ai-chat-x-session-container', 'style'),
    Output('ai-chat-x-session-collapse-state', 'data'),
    Input('ai-chat-x-collapse-sessions', 'nClicks'),
    State('ai-chat-x-session-collapse-state', 'data'),
    prevent_initial_call=True
)
def toggle_session_list(collapse_clicks, is_collapsed):
    """切换会话列表的折叠状态"""
    
    # 检查是否有点击事件触发
    if collapse_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update
    
    # 根据当前状态执行相反操作
    if is_collapsed is False:
        # 当前是展开状态，执行折叠
        return (
            render_session_list(collapsed=True),
            style(width="40px", padding="16px", borderRight="1px solid #f0f0f0"),
            True
        )
    else:
        # 当前是折叠状态，执行展开
        return (
            render_session_list(collapsed=False),
            style(width="280px", padding="16px", borderRight="1px solid #f0f0f0"),
            False
        )
    
    return dash.no_update, dash.no_update, dash.no_update