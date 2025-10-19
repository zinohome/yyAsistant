"""
实时语音回调处理
处理实时语音相关的Dash回调
"""

from dash import callback, Input, Output, State, no_update
import feffery_antd_components as fac
from dash import html
from utils.log import log


@callback(
    [
        Output("realtime-voice-status", "style"),
        Output("realtime-status-text", "children"),
        Output("voice-call-btn", "disabled"),
        Output("voice-call-btn", "children")
    ],
    [
        Input("voice-call-btn", "nClicks")
    ],
    [
        State("realtime-voice-status", "style"),
        State("realtime-status-text", "children")
    ],
    prevent_initial_call=True
)
def handle_realtime_voice_toggle(n_clicks, current_style, current_text):
    """
    处理实时语音按钮点击事件
    """
    try:
        if n_clicks is None:
            return no_update, no_update, no_update, no_update
        
        log.info(f"实时语音按钮被点击，点击次数: {n_clicks}")
        
        # 检查是否已经激活
        is_active = current_style.get("display") == "block"
        
        if is_active:
            # 停止实时语音
            log.info("停止实时语音对话")
            return (
                {"marginLeft": "10px", "display": "none"},  # 隐藏状态指示器
                "等待开始",  # 状态文本
                False,  # 启用按钮
                "开始实时对话"  # 按钮文本
            )
        else:
            # 启动实时语音
            log.info("启动实时语音对话")
            return (
                {"marginLeft": "10px", "display": "block"},  # 显示状态指示器
                "正在连接...",  # 状态文本
                True,  # 禁用按钮
                "停止实时对话"  # 按钮文本
            )
            
    except Exception as e:
        log.error(f"处理实时语音按钮事件失败: {e}")
        return no_update, no_update, no_update, no_update


@callback(
    Output("realtime-voice-status", "children", allow_duplicate=True),
    [
        Input("realtime-voice-status", "id")
    ],
    [
        State("realtime-voice-status", "children")
    ],
    prevent_initial_call=True
)
def update_realtime_voice_status(status_id, current_children):
    """
    更新实时语音状态指示器
    """
    try:
        # 这里可以通过JavaScript事件来更新状态
        # 暂时返回当前状态
        return current_children
        
    except Exception as e:
        log.error(f"更新实时语音状态失败: {e}")
        return no_update


@callback(
    Output("audio-visualizer", "style", allow_duplicate=True),
    [
        Input("realtime-voice-status", "style")
    ],
    [
        State("audio-visualizer", "style")
    ],
    prevent_duplicate=True
)
def update_audio_visualizer_style(voice_status_style, current_style):
    """
    根据实时语音状态更新音频可视化器样式
    """
    try:
        if voice_status_style.get("display") == "block":
            # 实时语音激活时，改变音频可视化器样式
            updated_style = current_style.copy()
            updated_style["borderColor"] = "#52c41a"
            updated_style["backgroundColor"] = "#f6ffed"
            return updated_style
        else:
            # 实时语音未激活时，恢复默认样式
            updated_style = current_style.copy()
            updated_style["borderColor"] = "#d9d9d9"
            updated_style["backgroundColor"] = "#f5f5f5"
            return updated_style
            
    except Exception as e:
        log.error(f"更新音频可视化器样式失败: {e}")
        return no_update
