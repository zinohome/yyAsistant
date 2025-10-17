#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
import time
from dash import callback, Input, Output, State, html, dcc, no_update
import feffery_antd_components as fac
from dash_iconify import DashIconify
from utils.log import log
from utils.voice_websocket_client import voice_websocket_client
from configs.voice_config import VoiceConfig

# 获取app实例
from server import app


# 实时语音对话按钮回调
@app.callback(
    [
        Output("realtime-start-btn", "disabled"),
        Output("realtime-stop-btn", "disabled"),
        Output("realtime-mute-btn", "disabled"),
        Output("realtime-status", "children"),
        Output("realtime-chat-history", "children")
    ],
    [
        Input("realtime-start-btn", "nClicks"),
        Input("realtime-stop-btn", "nClicks"),
        Input("realtime-mute-btn", "nClicks")
    ],
    [
        State("realtime-status", "children"),
        State("realtime-chat-history", "children")
    ],
    prevent_initial_call=True
)
def handle_realtime_voice_buttons(start_clicks, stop_clicks, mute_clicks, current_status, current_history):
    """处理实时语音对话按钮状态"""
    from dash import ctx
    
    # 获取触发回调的元素ID
    triggered_id = ctx.triggered_id if ctx.triggered else None
    
    log.info(f"🔴 实时语音按钮回调触发: {triggered_id}")
    log.info(f"🔴 点击次数: start={start_clicks}, stop={stop_clicks}, mute={mute_clicks}")
    log.info(f"🔴 当前状态: {current_status}")
    print(f"🔴 实时语音按钮回调触发: {triggered_id}")
    
    if triggered_id == "realtime-start-btn":
        log.info("开始实时语音通话")
        
        # 启动实时语音对话 - 使用现有的WebSocket连接
        try:
            # 通过WebSocket发送开始实时对话的消息
            if hasattr(voice_websocket_client, 'send_message'):
                voice_websocket_client.send_message({
                    "type": "start_realtime_dialogue",
                    "timestamp": time.time()
                })
                log.info("✅ 已发送实时语音对话启动消息")
            else:
                log.warning("WebSocket客户端不可用，无法启动实时语音对话")
        except Exception as e:
            log.error(f"启动实时语音对话失败: {e}")
        
        return (
            True,  # start-btn disabled
            False,  # stop-btn enabled
            False,  # mute-btn enabled
            html.Div([
                fac.AntdBadge(
                    dot=True,
                    color="red",
                    children=html.Span("正在监听")
                ),
                html.Span(" 实时语音对话模式", style={"marginLeft": "10px"})
            ]),
            current_history  # 保持历史记录
        )
    
    elif triggered_id == "realtime-stop-btn":
        log.info("结束实时语音通话")
        return (
            False,  # start-btn enabled
            True,   # stop-btn disabled
            True,   # mute-btn disabled
            html.Div([
                fac.AntdBadge(
                    dot=True,
                    color="gray",
                    children=html.Span("等待开始对话")
                ),
                html.Span(" 实时语音对话模式", style={"marginLeft": "10px"})
            ]),
            current_history  # 保持历史记录
        )
    
    elif triggered_id == "realtime-mute-btn":
        log.info("切换静音状态")
        # 这里可以添加静音逻辑
        return no_update
    
    return no_update


# 实时语音对话状态管理回调
@app.callback(
    Output("realtime-status-store", "data"),
    [
        Input("realtime-start-btn", "nClicks"),
        Input("realtime-stop-btn", "nClicks")
    ],
    [State("realtime-status-store", "data")],
    prevent_initial_call=True
)
def update_realtime_voice_status(start_clicks, stop_clicks, current_status):
    """更新实时语音对话状态"""
    from dash import ctx
    import time
    
    triggered_id = ctx.triggered_id if ctx.triggered else None
    
    if triggered_id == "realtime-start-btn":
        return {"status": "active", "timestamp": time.time()}
    elif triggered_id == "realtime-stop-btn":
        return {"status": "idle", "timestamp": time.time()}
    
    return current_status
