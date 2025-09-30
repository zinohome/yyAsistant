import dash
from dash import ctx, Input, Output, State, callback, no_update, html, ClientsideFunction, ALL
import feffery_antd_components as fac
import json
from datetime import datetime

from components.ai_chat_message_history import AiChatMessageHistory
from server import app, server  # 确保同时导入了server
from utils.yychat_client import yychat_client
from utils.log import log
import copy
import threading
import time
from flask import Response, stream_with_context

from components.ai_chat_message_history import AiChatMessageHistory
from server import app, server  # 确保同时导入了server
from utils.log import log
import copy

# 聊天交互处理函数
@app.callback(
    [
        Output('ai-chat-x-messages-store', 'data'),
        Output('ai-chat-x-input', 'value')
    ],
    [
        # 话题提示点击输入
        Input(f'chat-topic-0', 'nClicks'),
        Input(f'chat-topic-1', 'nClicks'),
        Input(f'chat-topic-2', 'nClicks'),
        Input(f'chat-topic-3', 'nClicks'),
        # 消息发送输入
        Input('ai-chat-x-send-btn', 'nClicks'),
        Input('ai-chat-x-input', 'n_submit')
    ],
    [
        State('ai-chat-x-input', 'value'),
        State('ai-chat-x-messages-store', 'data'),
        State('ai-chat-x-current-session-id', 'data')
    ],
    prevent_initial_call=True
)
def handle_chat_interactions(topic_0_clicks, topic_1_clicks, topic_2_clicks, topic_3_clicks, 
                           send_button_clicks, input_submit, 
                           message_content, messages_store, current_session_id):
    # 获取触发回调的元素ID
    triggered_id = ctx.triggered_id if ctx.triggered else None
    
    # 添加调试日志
    log.debug(f"回调被触发: {triggered_id}")
    
    # 初始化消息存储（如果为空）
    messages = messages_store or []
    
    # 确保ctx.triggered不为空
    if not ctx.triggered:
        return messages, message_content
    
    # 处理话题点击
    if triggered_id and triggered_id.startswith('chat-topic-'):
        # 获取话题索引
        topic_index = int(triggered_id.split('-')[-1])
        # 预定义话题列表 - 与chat_input_area.py中的保持一致
        topics = [
            "怎么提高工作效率",
            "有哪些数据分析技巧",
            "有哪些代码优化建议",
            "项目管理方法有哪些"
        ]
        
        if 0 <= topic_index < len(topics):
            # 返回话题内容到输入框
            log.debug(f"话题点击: {topic_index}, 内容: {topics[topic_index]}")
            return messages, topics[topic_index]
        # 如果索引无效，返回默认值
        return messages, message_content
    
    # 处理消息发送
    elif triggered_id in ['ai-chat-x-send-btn', 'ai-chat-x-input'] and message_content:
        # 去除消息前后空格
        message_content = message_content.strip()
        
        if message_content:
            # 创建消息的深拷贝，避免修改原始数据
            updated_messages = copy.deepcopy(messages)
            
            # 创建用户消息对象
            user_message = {
                'role': 'user',
                'content': message_content,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 添加用户消息到消息列表的副本
            updated_messages.append(user_message)
            
            # 创建一个空白的AI消息，用于后续接收流式响应
            ai_message_id = f"ai-message-{len(updated_messages)}"
            ai_message = {
                'role': 'assistant',
                'content': '正在输入 …',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'id': ai_message_id,
                'is_streaming': True
            }
            
            # 添加空白AI消息到消息列表
            updated_messages.append(ai_message)
            
            log.debug(f"创建用户消息和AI消息: {user_message}, {ai_message}")
            
            return updated_messages, ''
        # 如果消息内容为空，返回默认值
        return messages, message_content
    
    # 默认返回当前状态
    return messages, message_content

# 更新聊天历史显示
@app.callback(
    Output('ai-chat-x-history-content', 'children'),
    [Input('ai-chat-x-messages-store', 'data')],
    prevent_initial_call=True
)
def update_chat_history(messages):
    """更新聊天历史显示"""
    log.debug(f"更新聊天历史，消息数量: {len(messages) if messages else 0}")
    # 直接使用消息列表渲染聊天历史
    return AiChatMessageHistory(messages or [])

# 注册函数，供app.py调用

def register_chat_input_callbacks(flask_app):
    """
    注册聊天输入区域的所有回调函数
    这个函数在app.py中被调用以确保所有回调正确注册
    """
    log.debug("正在注册聊天输入区域回调函数")
    # 所有回调函数已经通过@app.callback装饰器注册
    # 这里可以添加一些额外的初始化代码（如果需要）
    pass