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
    children = []
    if messages is None or len(messages) == 0:
        # 如果没有消息，显示功能提示
        children.append(render_feature_hints())
    else:
        # 根据消息角色动态渲染不同类型的消息组件
        for msg in messages:
            if msg.get('role') == 'agent':
                children.append(render_agent_message(
                    message=msg.get('message', ''),
                    timestamp=msg.get('timestamp', '')
                ))
            elif msg.get('role') == 'user':
                children.append(render_user_message(
                    message=msg.get('message', ''),
                    timestamp=msg.get('timestamp', '')
                ))
    return html.Div(children)