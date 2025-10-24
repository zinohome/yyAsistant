"""
简化的统一聊天回调
专注于核心的文本和语音提交逻辑，避免allow_duplicate冲突
"""

import json
import time
import copy
from datetime import datetime
from dash import Input, Output, State, no_update, ctx
import dash
# 不需要导入SSE相关组件，直接使用字典配置
from utils.log import log

# 获取app实例
from app import app

# 添加用于SSE连接的存储
active_sse_connections = {}

def cleanup_expired_sse_connections():
    """清理过期的SSE连接记录"""
    current_time = time.time()
    expired_connections = []
    
    for message_id, connection_info in active_sse_connections.items():
        if current_time - connection_info.get('start_time', 0) > 300:
            expired_connections.append(message_id)
    
    for message_id in expired_connections:
        del active_sse_connections[message_id]
        log.debug(f"清理过期的SSE连接记录: {message_id}")
    
    return len(expired_connections)

# 核心聊天消息处理回调 - 只处理文本发送和语音转录
@app.callback(
    [
        Output('ai-chat-x-messages-store', 'data'),
        Output('ai-chat-x-input', 'value'),
        Output('ai-chat-x-send-btn', 'loading'),
        Output('ai-chat-x-send-btn', 'disabled'),
        Output('voice-enable-voice', 'data'),
        Output('chat-X-sse', 'url'),
        Output('chat-X-sse', 'options')
    ],
    [
        # 文本发送
        Input('ai-chat-x-send-btn', 'nClicks'),
        # 话题点击
        Input({'type': 'chat-topic', 'index': dash.ALL}, 'nClicks'),
        # 语音转录
        Input('voice-transcription-store-server', 'data'),
        # SSE完成事件
        Input('ai-chat-x-sse-completed-receiver', 'data-completion-event')
    ],
    [
        State('ai-chat-x-input', 'value'),
        State('ai-chat-x-messages-store', 'data'),
        State('ai-chat-x-current-session-id', 'data')
    ],
    prevent_initial_call=True
)
def unified_chat_handler(send_btn_clicks, topic_clicks, transcription_data, sse_completion_event,
                        message_content, messages_store, current_session_id):
    """
    统一的聊天消息处理函数
    处理文本发送、语音转录、SSE完成事件
    """
    
    # 获取触发回调的元素ID
    triggered_id = ctx.triggered_id if ctx.triggered else None
    log.info(f"🔍 统一回调被触发: {triggered_id}")
    
    # 初始化消息存储
    messages = messages_store or []
    
    # 清理过期的SSE连接记录
    cleanup_expired_sse_connections()
    
    # 1. 处理文本消息发送
    if triggered_id == 'ai-chat-x-send-btn' and message_content:
        log.info(f"📝 处理文本消息发送: {message_content[:50]}...")
        return _handle_text_message_send(messages, message_content, current_session_id)
    
    # 2. 处理话题点击
    elif triggered_id and 'chat-topic' in str(triggered_id):
        log.info(f"💬 处理话题点击: {triggered_id}")
        return _handle_topic_click(messages, triggered_id)
    
    # 3. 处理语音转录
    elif triggered_id == 'voice-transcription-store-server' and transcription_data and transcription_data.get('text'):
        log.info(f"🎤 处理语音转录: {transcription_data.get('text', '')[:50]}...")
        return _handle_voice_transcription(messages, transcription_data, current_session_id)
    
    # 4. 处理SSE完成事件
    elif triggered_id == 'ai-chat-x-sse-completed-receiver.data-completion-event':
        log.info(f"✅ 处理SSE完成事件")
        return _handle_sse_completion(messages, sse_completion_event, message_content)
    
    # 默认返回当前状态
    return messages, message_content, False, False, dash.no_update, dash.no_update, dash.no_update


def _handle_text_message_send(messages, message_content, current_session_id):
    """处理文本消息发送"""
    message_content = message_content.strip()
    
    if not message_content:
        return messages, message_content, False, False, dash.no_update, dash.no_update, dash.no_update
    
    # 创建消息的深拷贝
    updated_messages = copy.deepcopy(messages)
    
    # 添加用户消息
    usr_message_id = f"usr-message-{len(updated_messages)}"
    user_message = {
        'role': 'user',
        'content': message_content,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'id': usr_message_id
    }
    updated_messages.append(user_message)
    
    # 添加AI消息占位
    ai_message_id = f"ai-message-{len(updated_messages)}"
    ai_message = {
        'role': 'assistant',
        'content': '正在思考中...',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'id': ai_message_id,
        'is_streaming': True
    }
    updated_messages.append(ai_message)
    
    # 保存到数据库
    if current_session_id:
        try:
            from models.conversations import Conversations
            conv = Conversations.get_conversation_by_conv_id(current_session_id)
            if conv:
                existing_messages = conv.conv_memory.get('messages', []) if conv.conv_memory else []
                existing_messages.append(user_message)
                existing_messages.append(ai_message)
                Conversations.update_conversation_by_conv_id(
                    current_session_id,
                    conv_memory={'messages': existing_messages}
                )
        except Exception as e:
            log.error(f"保存用户消息到数据库失败: {e}")
    
    # 构建SSE请求
    try:
        conversation_messages = [{'role': 'user', 'content': message_content}]
        session_id = current_session_id or 'conversation_0001'
        
        request_data = {
            'messages': conversation_messages,
            'session_id': session_id,
            'personality_id': 'health_assistant',
            'message_id': ai_message_id,
            'role': 'user',
            'enable_voice': False,
            'client_id': None,
            'conversation_id': session_id
        }
        
        options = {
            'payload': json.dumps(request_data, ensure_ascii=False),
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'}
        }
        
        log.info(f"✅ 文本消息发送完成，触发SSE: {ai_message_id}")
        return updated_messages, '', True, True, dash.no_update, '/stream', options
        
    except Exception as e:
        log.error(f"构建SSE请求失败: {e}")
        return updated_messages, '', True, True, dash.no_update, dash.no_update, dash.no_update


def _handle_voice_transcription(messages, transcription_data, current_session_id):
    """处理语音转录"""
    try:
        transcribed_text = transcription_data.get('text', '').strip()
        if not transcribed_text:
            return messages, '', False, False, dash.no_update, dash.no_update, dash.no_update

        updated_messages = copy.deepcopy(messages)

        # 添加用户消息
        usr_message_id = f"usr-message-{len(updated_messages)}"
        user_message = {
            'role': 'user',
            'content': transcribed_text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'id': usr_message_id
        }
        updated_messages.append(user_message)

        # 添加AI消息占位
        ai_message_id = f"ai-message-{len(updated_messages)}"
        ai_message = {
            'role': 'assistant',
            'content': '正在思考中...',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'id': ai_message_id,
            'is_streaming': True
        }
        updated_messages.append(ai_message)

        # 构建SSE请求（语音模式）
        conversation_messages = [{'role': 'user', 'content': transcribed_text}]
        session_id = current_session_id or 'conversation_0001'
        
        request_data = {
            'messages': conversation_messages,
            'session_id': session_id,
            'personality_id': 'health_assistant',
            'message_id': ai_message_id,
            'role': 'user',
            'enable_voice': True,
            'client_id': None,
            'conversation_id': session_id
        }
        
        options = {
            'payload': json.dumps(request_data, ensure_ascii=False),
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'}
        }
        
        log.info(f"✅ 语音转录处理完成，触发SSE: {ai_message_id}")
        return updated_messages, '', True, True, True, '/stream', options
        
    except Exception as e:
        log.error(f"处理语音转录失败: {e}")
        return messages, '', False, False, dash.no_update, dash.no_update, dash.no_update


def _handle_sse_completion(messages, completion_event_json, message_content):
    """处理SSE完成事件"""
    if not messages:
        return messages, message_content, False, False, dash.no_update, dash.no_update, dash.no_update
    
    try:
        if completion_event_json:
            completion_event = json.loads(completion_event_json)
            message_id = completion_event.get('messageId')
            full_content = completion_event.get('content')
        else:
            # 从最后一条AI消息获取信息
            last_message = messages[-1] if messages else None
            if last_message and last_message.get('role') in ['assistant', 'agent'] and last_message.get('is_streaming', False):
                message_id = last_message.get('id')
                full_content = "SSE完成，但内容需要从DOM获取"
            else:
                return messages, message_content, False, False, dash.no_update, dash.no_update, dash.no_update

        # 更新消息
        updated_messages = copy.deepcopy(messages)
        for i, message in enumerate(updated_messages):
            if message.get('id') == message_id:
                updated_messages[i]['content'] = full_content
                updated_messages[i]['is_streaming'] = False
                break

        # 清理SSE连接
        if message_id in active_sse_connections:
            del active_sse_connections[message_id]

        log.info(f"✅ SSE完成事件处理完成: {message_id}")
        return updated_messages, message_content, False, False, dash.no_update, dash.no_update, dash.no_update
        
    except Exception as e:
        log.error(f"处理SSE完成事件失败: {e}")
        return messages, message_content, False, False, dash.no_update, dash.no_update, dash.no_update


def _handle_topic_click(messages, triggered_id):
    """处理话题点击"""
    # TODO: 实现话题点击逻辑
    log.info(f"💬 话题点击: {triggered_id}")
    return messages, '', False, False, dash.no_update, dash.no_update, dash.no_update
