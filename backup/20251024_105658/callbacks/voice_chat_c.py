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

# 注意：此文件中的语音按钮回调已被统一状态管理器替代
# 统一状态管理器现在完全控制所有按钮的状态和样式
# 这样可以避免多个回调之间的冲突和颜色闪烁问题

# WebSocket连接管理回调
@app.callback(
    [
        Output("voice-websocket-connection", "data"),
        Output("voice-error-notification", "children")
    ],
    [Input("voice-record-button", "n_clicks"), Input("voice-call-btn", "n_clicks")],
    [State("voice-websocket-connection", "data")]
)
def manage_websocket_connection(record_clicks, call_clicks, connection_data):
    """管理WebSocket连接状态"""
    try:
        if record_clicks or call_clicks:
            # 检查WebSocket连接状态
            if not connection_data or not connection_data.get('connected', False):
                # 尝试建立连接
                try:
                    voice_websocket_client.connect()
                    return {
                        'connected': True,
                        'timestamp': time.time()
                    }, None
                except Exception as e:
                    log.error(f"WebSocket连接失败: {e}")
                    return connection_data, f"连接失败: {str(e)}"
            else:
                return connection_data, None
        else:
            return connection_data, None
    except Exception as e:
        log.error(f"WebSocket连接管理失败: {e}")
        return connection_data, f"连接管理错误: {str(e)}"