"""
智能消息操作组件
提供状态感知的消息操作栏，保留原有的ai-chat-x-regenerate和ai-chat-x-copy按钮
"""
import dash
from dash import html, dcc
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style
from dash_iconify import DashIconify


def create_smart_message_actions(message_id, current_state='SUCCESS', is_streaming=False, error_info=None):
    """
    创建智能状态感知的消息操作栏
    保留原有的ai-chat-x-regenerate和ai-chat-x-copy按钮，添加智能功能
    
    Args:
        message_id: 消息ID
        current_state: 当前状态 (SUCCESS, PROCESSING, ERROR)
        is_streaming: 是否正在流式传输
        error_info: 错误信息
    
    Returns:
        fac.AntdRow: 智能操作栏组件
    """
    
    # 保留原有的核心按钮
    core_actions = [
        # 原有的重新生成按钮
        fac.AntdButton(
            icon=fac.AntdIcon(icon='antd-reload'),
            id={'type': 'ai-chat-x-regenerate', 'index': message_id},
            type="text",
            size="small",
            nClicks=0,
            style=style(
                fontSize=16, 
                color='rgba(0,0,0,0.75)',
                padding='4px 8px',
                minWidth='auto',
                height='auto'
            )
        ),
        # 原有的复制按钮
        fac.AntdButton(
            icon=fac.AntdIcon(icon='antd-copy'),
            id={'type': 'ai-chat-x-copy', 'index': message_id},
            type="text",
            size="small",
            nClicks=0,
            style=style(
                fontSize=16, 
                color='rgba(0,0,0,0.75)',
                padding='4px 8px',
                minWidth='auto',
                height='auto'
            )
        )
    ]
    
    # 智能状态感知操作
    smart_actions = []
    
    # 流式传输时的进度指示器
    if current_state == 'PROCESSING' and is_streaming:
        smart_actions.append(create_progress_indicator())
    elif current_state == 'ERROR' and error_info:
        smart_actions.append(create_error_tooltip(error_info))
    
    # 状态指示器
    smart_actions.append(create_status_indicator(current_state))
    
    # 合并所有操作
    all_actions = core_actions + smart_actions
    
    return fac.AntdRow(
        [
            fac.AntdCol(
                style=style(width="48px", height="0")  # 用于与头像对齐的占位符
            ),
            fac.AntdCol(
                html.Div(
                    fac.AntdSpace(
                        all_actions,
                        size=16
                    ),
                    className="message-actions"
                ),
                style=style(paddingLeft="4px")
            )
        ],
        justify="start"
    )


def create_progress_indicator():
    """创建进度指示器"""
    return html.Div(
        [
            fac.AntdSpin(
                size="small",
                style=style(marginRight="8px")
            ),
            fac.AntdText(
                "处理中...",
                style=style(
                    fontSize=12,
                    color='#666'
                )
            )
        ],
        style=style(
            display="flex",
            alignItems="center"
        )
    )


def create_status_indicator(current_state):
    """创建状态指示器"""
    status_config = {
        'SUCCESS': {'color': '#52c41a', 'text': '✓'},
        'PROCESSING': {'color': '#1890ff', 'text': '⟳'},
        'ERROR': {'color': '#ff4d4f', 'text': '✗'}
    }
    
    config = status_config.get(current_state, status_config['SUCCESS'])
    
    return fac.AntdTag(
        config['text'],
        color=config['color'],
        style=style(
            fontSize=12,
            marginLeft="8px"
        )
    )


def create_error_tooltip(error_info):
    """创建错误提示"""
    return fac.AntdTooltip(
        fac.AntdIcon(
            icon='antd-exclamation-circle',
            style=style(
                fontSize=16,
                color='#ff4d4f'
            )
        ),
        title=error_info,
        placement="top"
    )


def get_button_style(current_state, button_type):
    """获取按钮样式"""
    base_style = {
        'fontSize': 16,
        'padding': '4px 8px',
        'minWidth': 'auto',
        'height': 'auto'
    }
    
    if current_state == 'PROCESSING':
        base_style['color'] = '#1890ff'
        base_style['opacity'] = 0.7
    elif current_state == 'ERROR':
        base_style['color'] = '#ff4d4f'
    else:
        base_style['color'] = 'rgba(0,0,0,0.75)'
    
    return base_style