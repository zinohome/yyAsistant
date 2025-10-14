#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
from dash import callback, Input, Output, State, html, dcc, no_update
import feffery_antd_components as fac
from dash_iconify import DashIconify
from utils.log import log
from utils.voice_websocket_client import voice_websocket_client
from configs.voice_config import VoiceConfig

# 获取app实例
from server import app


# 语音按钮统一回调 - 处理录音和通话按钮的所有状态
@app.callback(
    [
        Output("voice-record-btn", "type"),
        Output("voice-record-btn", "icon"),
        Output("voice-record-btn", "title"),
        Output("voice-record-btn", "style"),
        Output("voice-record-btn", "disabled"),
        Output("voice-call-btn", "type"),
        Output("voice-call-btn", "icon"),
        Output("voice-call-btn", "title"),
        Output("voice-call-btn", "style"),
        Output("voice-call-btn", "disabled"),
        Output("voice-recording-status", "data"),
        Output("voice-call-status", "data"),
        Output("ai-chat-x-send-btn", "disabled", allow_duplicate=True)
    ],
    [
        Input("voice-record-btn", "nClicks"),
        Input("voice-call-btn", "nClicks"),
        Input("ai-chat-x-send-btn", "loading")
    ],
    [
        State("voice-recording-status", "data"),
        State("voice-call-status", "data")
    ],
    prevent_initial_call=True
)
def handle_voice_buttons(record_clicks, call_clicks, is_loading, is_recording, is_calling):
    """统一处理语音按钮的所有状态变化"""
    from dash import ctx
    
    # 获取触发回调的元素ID（与发送按钮保持一致）
    triggered_id = ctx.triggered_id if ctx.triggered else None
    
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    try:
        # 基础样式
        base_style = {
            "padding": "8px",
            "width": "40px",
            "height": "40px",
            "borderRadius": "8px"
        }
        
        # 禁用状态样式
        disabled_style = {**base_style, "backgroundColor": "#d9d9d9", "borderColor": "#d9d9d9", "cursor": "not-allowed"}
        
        # 如果文本聊天正在进行，禁用所有语音按钮
        if is_loading:
            return (
                "primary", DashIconify(icon="proicons:microphone", width=24, height=24), "语音输入", disabled_style, True,
                "primary", DashIconify(icon="bi:telephone", width=24, height=24, rotate=2), "实时语音通话", disabled_style, True,
                is_recording, is_calling, False
            )
        
        # 处理录音按钮点击
        if triggered_id == "voice-record-btn" and record_clicks:
            if not is_recording:
                # 开始录音
                log.info("开始语音录音")
                
                # 触发前端录音功能
                try:
                    # 这里可以添加触发前端录音的JavaScript代码
                    # 由于Dash的限制，我们通过状态变化来触发前端功能
                    pass
                except Exception as e:
                    log.error(f"触发录音功能失败: {e}")
                
                record_style = {**base_style, "backgroundColor": "#ff4d4f", "borderColor": "#ff4d4f", "boxShadow": "0 2px 4px rgba(255, 77, 79, 0.3)"}
                call_style = {**base_style, "backgroundColor": "#52c41a", "borderColor": "#52c41a", "boxShadow": "0 2px 4px rgba(82, 196, 26, 0.2)"}
                return (
                    "primary", DashIconify(icon="mdi:stop", width=24, height=24), "停止录音", record_style, False,
                    "primary", DashIconify(icon="bi:telephone", width=24, height=24, rotate=2), "实时语音通话", disabled_style, True,
                    True, is_calling, True  # 禁用发送按钮
                )
            else:
                # 停止录音
                log.info("停止语音录音")
                record_style = {**base_style, "backgroundColor": "#1890ff", "borderColor": "#1890ff", "boxShadow": "0 2px 4px rgba(24, 144, 255, 0.2)"}
                call_style = {**base_style, "backgroundColor": "#52c41a", "borderColor": "#52c41a", "boxShadow": "0 2px 4px rgba(82, 196, 26, 0.2)"}
                return (
                    "primary", DashIconify(icon="proicons:microphone", width=24, height=24), "语音输入", record_style, False,
                    "primary", DashIconify(icon="bi:telephone", width=24, height=24, rotate=2), "实时语音通话", call_style, False,
                    False, is_calling, False  # 恢复发送按钮
                )
        
        # 处理通话按钮点击
        elif triggered_id == "voice-call-btn" and call_clicks:
            if not is_calling:
                # 开始通话
                log.info("开始实时语音通话")
                record_style = {**base_style, "backgroundColor": "#1890ff", "borderColor": "#1890ff", "boxShadow": "0 2px 4px rgba(24, 144, 255, 0.2)"}
                call_style = {**base_style, "backgroundColor": "#ff4d4f", "borderColor": "#ff4d4f", "boxShadow": "0 2px 4px rgba(255, 77, 79, 0.3)"}
                return (
                    "primary", DashIconify(icon="proicons:microphone", width=24, height=24), "语音输入", disabled_style, True,
                    "primary", DashIconify(icon="mdi:phone-hangup", width=24, height=24), "结束通话", call_style, False,
                    is_recording, True, True  # 禁用发送按钮
                )
            else:
                # 结束通话
                log.info("结束实时语音通话")
                record_style = {**base_style, "backgroundColor": "#1890ff", "borderColor": "#1890ff", "boxShadow": "0 2px 4px rgba(24, 144, 255, 0.2)"}
                call_style = {**base_style, "backgroundColor": "#52c41a", "borderColor": "#52c41a", "boxShadow": "0 2px 4px rgba(82, 196, 26, 0.2)"}
                return (
                    "primary", DashIconify(icon="proicons:microphone", width=24, height=24), "语音输入", record_style, False,
                    "primary", DashIconify(icon="bi:telephone", width=24, height=24, rotate=2), "实时语音通话", call_style, False,
                    is_recording, False, False  # 恢复发送按钮
                )
        
        # 处理加载状态变化
        elif triggered_id == "ai-chat-x-send-btn":
            if is_loading:
                # 禁用按钮
                return (
                    "primary", DashIconify(icon="proicons:microphone", width=24, height=24), "语音输入", disabled_style, True,
                    "primary", DashIconify(icon="bi:telephone", width=24, height=24, rotate=2), "实时语音通话", disabled_style, True,
                    is_recording, is_calling, False
                )
            else:
                # 恢复按钮
                record_style = {**base_style, "backgroundColor": "#1890ff", "borderColor": "#1890ff", "boxShadow": "0 2px 4px rgba(24, 144, 255, 0.2)"}
                call_style = {**base_style, "backgroundColor": "#52c41a", "borderColor": "#52c41a", "boxShadow": "0 2px 4px rgba(82, 196, 26, 0.2)"}
                return (
                    "primary", DashIconify(icon="proicons:microphone", width=24, height=24), "语音输入", record_style, False,
                    "primary", DashIconify(icon="bi:telephone", width=24, height=24, rotate=2), "实时语音通话", call_style, False,
                    is_recording, is_calling, False  # 恢复发送按钮
                )
        
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
    except Exception as e:
        log.error(f"处理语音按钮状态失败: {e}")
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update


# WebSocket连接管理回调
@app.callback(
    [
        Output("voice-websocket-connection", "data"),
        Output("voice-error-notification", "children")
    ],
    [Input("voice-record-btn", "n_clicks"), Input("voice-call-btn", "n_clicks")],
    [State("voice-websocket-connection", "data")]
)
def manage_websocket_connection(record_clicks, call_clicks, connection_data):
    """管理WebSocket连接"""
    if not record_clicks and not call_clicks:
        return no_update, no_update
    
    try:
        # 检查是否需要连接WebSocket
        if not connection_data or not connection_data.get("connected"):
            log.info("建立语音WebSocket连接")
            connection_data = {
                "connected": True,
                "timestamp": dash.callback_context.timestamp
            }
            return connection_data, no_update  # 连接成功时不显示错误通知
        
        return no_update, no_update
    except Exception as e:
        log.error(f"管理WebSocket连接失败: {e}")
        return no_update, fac.AntdNotification.Notification(
            message="语音连接失败",
            description=f"无法建立语音WebSocket连接: {str(e)}",
            type="error",
            duration=5
        )


# 语音消息处理回调
@app.callback(
    [
        Output("ai-chat-x-messages-store", "data", allow_duplicate=True),
        Output("voice-message-notification", "children")
    ],
    [Input("voice-websocket-connection", "data")],
    [State("ai-chat-x-messages-store", "data")],
    prevent_initial_call=True
)
def handle_voice_messages(connection_data, current_messages):
    """处理语音消息"""
    if not connection_data or not connection_data.get("connected"):
        return no_update, no_update
    
    try:
        # 这里应该接收来自WebSocket的语音消息
        # 暂时返回当前消息，实际实现需要从WebSocket接收数据
        return current_messages, no_update
    except Exception as e:
        log.error(f"处理语音消息失败: {e}")
        return current_messages, no_update


# 语音功能JavaScript集成回调
@app.callback(
    Output("voice-js-integration", "children"),
    [Input("voice-record-btn", "n_clicks"), Input("voice-call-btn", "n_clicks")],
    [State("voice-recording-status", "data"), State("voice-call-status", "data")]
)
def integrate_voice_javascript(record_clicks, call_clicks, is_recording, is_calling):
    """集成语音功能JavaScript"""
    if not record_clicks and not call_clicks:
        return no_update
    
    try:
        # 触发JavaScript语音功能
        return html.Div([
            html.Script(f"""
                // 初始化语音功能
                if (window.voiceWebSocketManager && window.voiceRecorder && window.voicePlayer) {{
                    // 连接WebSocket
                    if (!window.voiceWebSocketManager.isConnected) {{
                        window.voiceWebSocketManager.connect();
                    }}
                    
                    // 处理录音按钮
                    if ({str(is_recording).lower()}) {{
                        window.voiceRecorder.startRecording();
                    }} else {{
                        window.voiceRecorder.stopRecording();
                    }}
                    
                    // 处理通话按钮
                    if ({str(is_calling).lower()}) {{
                        // 开始实时通话模式
                        console.log('开始实时语音通话');
                    }} else {{
                        // 结束实时通话模式
                        console.log('结束实时语音通话');
                    }}
                }}
            """)
        ])
    except Exception as e:
        log.error(f"集成语音JavaScript失败: {e}")
        return no_update


# 语音设置存储组件
@app.callback(
    Output("voice-settings-store", "data"),
    [Input("voice-websocket-connection", "data")],
    prevent_initial_call=True
)
def initialize_voice_settings(connection_data):
    """初始化语音设置"""
    if not connection_data:
        return no_update
    
    try:
        # 获取默认语音设置（来自前端配置，而非WS客户端）
        default_settings = VoiceConfig.get_default_settings()
        log.info("初始化语音设置")
        return default_settings
    except Exception as e:
        log.error(f"初始化语音设置失败: {e}")
        return no_update



