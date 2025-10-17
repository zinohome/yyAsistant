"""
核心聊天回调 - 只包含文本发送、语音转录、SSE处理
避免与其他回调的输出冲突
"""

import json
import time
import copy
from datetime import datetime
from dash import Input, Output, State, no_update, ctx
import dash
from utils.log import log

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

def register_core_chat_callback(app):
    """注册核心聊天回调 - 只处理文本发送、语音转录、SSE完成"""
    
    @app.callback(
        [
            # 消息存储
            Output('ai-chat-x-messages-store', 'data'),
            # 输入框
            Output('ai-chat-x-input', 'value'),
            # 发送按钮状态
            Output('ai-chat-x-send-btn', 'loading'),
            Output('ai-chat-x-send-btn', 'disabled'),
            # 语音功能
            Output('voice-enable-voice', 'data'),
            # SSE连接
            Output('chat-X-sse', 'url'),
            Output('chat-X-sse', 'options')
        ],
        [
            # 文本输入相关
            Input('ai-chat-x-send-btn', 'nClicks'),
            Input({'type': 'chat-topic', 'index': dash.ALL}, 'nClicks'),
            
            # 语音相关
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
    def core_chat_handler(
        send_btn_clicks, topic_clicks, transcription_data, sse_completion_event,
        message_content, messages_store, current_session_id
    ):
        """
        核心聊天处理函数
        只处理：文本发送、语音转录、SSE完成事件
        """
        
        # 获取触发回调的元素ID
        triggered_id = ctx.triggered_id if ctx.triggered else None
        log.info(f"🔍 核心聊天回调被触发: {triggered_id}")
        
        # 初始化消息存储
        messages = messages_store or []
        
        # 清理过期的SSE连接记录
        cleanup_expired_sse_connections()
        
        # 默认返回值
        default_returns = [
            messages, message_content, False, False,  # 消息相关
            dash.no_update, dash.no_update, dash.no_update  # 语音和SSE
        ]
        
        # 1. 处理文本消息发送
        if triggered_id == 'ai-chat-x-send-btn' and message_content:
            log.info(f"📝 处理文本消息发送: {message_content[:50]}...")
            return _handle_text_message_send(messages, message_content, current_session_id, default_returns)
        
        # 2. 处理话题点击
        elif triggered_id and 'chat-topic' in str(triggered_id):
            log.info(f"💬 处理话题点击: {triggered_id}")
            return _handle_topic_click(messages, triggered_id, default_returns)
        
        # 3. 处理语音转录
        elif triggered_id == 'voice-transcription-store-server' and transcription_data and transcription_data.get('text'):
            log.info(f"🎤 处理语音转录: {transcription_data.get('text', '')[:50]}...")
            return _handle_voice_transcription(messages, transcription_data, current_session_id, default_returns)
        
        # 4. 处理SSE完成事件
        elif triggered_id == 'ai-chat-x-sse-completed-receiver.data-completion-event':
            log.info(f"✅ 处理SSE完成事件")
            return _handle_sse_completion(messages, sse_completion_event, message_content, default_returns)
        
        # 默认返回当前状态
        return default_returns


def _handle_text_message_send(messages, message_content, current_session_id, default_returns):
    """处理文本消息发送"""
    message_content = message_content.strip()
    
    if not message_content:
        return default_returns
    
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
        
        # 触发按钮状态更新
        try:
            import dash_clientside
            if dash_clientside.set_props:
                dash_clientside.set_props('button-event-trigger', {
                    'data': {'type': 'text_button_clicked', 'timestamp': time.time()}
                })
                log.info("✅ 已触发按钮状态更新事件")
        except Exception as e:
            log.error(f"触发按钮状态更新失败: {e}")
        
        # 更新返回值
        result = default_returns.copy()
        result[0] = updated_messages  # messages
        result[1] = ''  # input value
        result[2] = True  # loading
        result[3] = True  # disabled
        result[5] = '/stream'  # SSE url
        result[6] = options  # SSE options
        return result
        
    except Exception as e:
        log.error(f"构建SSE请求失败: {e}")
        result = default_returns.copy()
        result[0] = updated_messages
        result[1] = ''
        result[2] = True
        result[3] = True
        return result


def _handle_voice_transcription(messages, transcription_data, current_session_id, default_returns):
    """处理语音转录"""
    try:
        transcribed_text = transcription_data.get('text', '').strip()
        if not transcribed_text:
            return default_returns

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
        
        # 触发按钮状态更新
        try:
            import dash_clientside
            if dash_clientside.set_props:
                dash_clientside.set_props('button-event-trigger', {
                    'data': {'type': 'voice_transcription_complete', 'timestamp': time.time()}
                })
                log.info("✅ 已触发语音转录按钮状态更新事件")
        except Exception as e:
            log.error(f"触发语音转录按钮状态更新失败: {e}")
        
        # 更新返回值
        result = default_returns.copy()
        result[0] = updated_messages  # messages
        result[1] = ''  # input value
        result[2] = True  # loading
        result[3] = True  # disabled
        result[4] = True  # enable_voice
        result[5] = '/stream'  # SSE url
        result[6] = options  # SSE options
        return result
        
    except Exception as e:
        log.error(f"处理语音转录失败: {e}")
        return default_returns


def _handle_sse_completion(messages, completion_event_json, message_content, default_returns):
    """处理SSE完成事件"""
    if not messages:
        return default_returns
    
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
                return default_returns

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
        
        # 更新返回值
        result = default_returns.copy()
        result[0] = updated_messages
        result[1] = message_content
        result[2] = False  # loading
        result[3] = False  # disabled
        return result
        
    except Exception as e:
        log.error(f"处理SSE完成事件失败: {e}")
        return default_returns


def _handle_topic_click(messages, triggered_id, default_returns):
    """处理话题点击"""
    log.info(f"💬 话题点击: {triggered_id}")
    return default_returns
