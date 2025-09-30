from dash import html
from components.chat_agent_message import ChatAgentMessage as render_agent_message
from components.chat_feature_hints import ChatFeatureHints as render_feature_hints
from components.chat_user_message import ChatUserMessage as render_user_message
import datetime

def AiChatMessageHistory(messages=None):
    """
    AI聊天消息历史组件
    :param messages: List[dict]，格式如：{'role': 'user'|'assistant'|'system', 'content': 'xxx', 'timestamp': 'xxx'}
    :return: Dash html.Div，可直接嵌入主聊天页面
    """
    # 获取当前时间并格式化（用于欢迎消息或无消息时）
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
    children = []
    if messages is None or len(messages) == 0:
        # 传递所有必要参数给 render_feature_hints
        children.append(render_feature_hints(
            message="您好！我是智能助手，很高兴为您服务。我可以帮助您解答问题、提供建议或协助您完成工作。",
            sender_name="智能助手",
            timestamp=current_time,
            icon="antd-robot",
            icon_bg_color="#1890ff"
        ))
    else:
        for msg in messages:
            # 统一处理assistant和agent角色
            if msg.get('role') == 'assistant' or msg.get('role') == 'agent':
                # 添加调试日志
                print(f"渲染AI消息 - ID: {msg.get('id')}, 内容: {msg.get('content')}")
                # 传递所有必要参数给 render_agent_message，使用正确的message参数
                children.append(render_agent_message(
                    message=msg.get('content', ''),  # 修改为message参数
                    sender_name="智能助手",
                    timestamp=msg.get('timestamp', current_time),  # 使用消息自带的时间戳
                    icon="antd-robot",
                    icon_bg_color="#1890ff",
                    message_bg_color="#f5f5f5",
                    message_text_color="#000000",
                    message_id=msg.get('id'),  # 传递消息ID
                    is_streaming=msg.get('is_streaming', False)  # 传递流式状态,
                ))
            elif msg.get('role') == 'user':
                # 传递所有必要参数给 render_user_message
                children.append(render_user_message(
                    message=msg.get('content', ''),  # 使用content字段
                    sender_name="我",
                    timestamp=msg.get('timestamp', current_time),  # 使用消息自带的时间戳
                    icon="antd-user",
                    icon_bg_color="#52c41a",
                    message_bg_color="#1890ff",
                    message_text_color="white",
                    message_id=msg.get('id'),  # 传递消息ID
                ))
            elif msg.get('role') == 'system':
                # 系统消息处理
                children.append(render_agent_message(
                    message=msg.get('content', ''),  # 修改为message参数
                    sender_name="系统",
                    timestamp=msg.get('timestamp', current_time),
                    icon="antd-info-circle",
                    icon_bg_color="#faad14"
                ))
    return html.Div(children)