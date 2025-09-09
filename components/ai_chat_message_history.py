from dash import html
from components.chat_agent_message import render as render_agent_message
from components.chat_feature_hints import render as render_feature_hints
from components.chat_user_message import render as render_user_message


def AiChatMessageHistory(messages):
    """
    AI聊天消息历史组件
    :param messages: List[dict]，格式如：{'role': 'user'|'agent', 'message': 'xxx'}
    :return: Dash html.Div，可直接嵌入主聊天页面
    """
    """
    children = []
    if messages is None:
        children.append(render_feature_hints())
    for msg in messages:
        if msg.get('role') == 'agent':
            children.append(render_agent_message(message=msg.get('message', '')))
        elif msg.get('role') == 'user':
            children.append(render_user_message(message=msg.get('message', '')))
    return html.Div(children)
    """
    children = []
    children.append(render_feature_hints())
    children.append(render_agent_message())
    children.append(render_user_message())
    return html.Div(children)