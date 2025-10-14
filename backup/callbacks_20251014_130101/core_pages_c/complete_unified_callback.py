"""
完整的统一回调 - 一次性解决所有输出冲突
整合所有聊天相关功能，避免allow_duplicate冲突
包含：文本发送、语音转录、消息操作、会话管理、SSE处理
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

def register_complete_unified_callback(app):
    """注册完整的统一回调 - 解决所有输出冲突"""
    
    @app.callback(
        [
            # 消息存储
            Output('ai-chat-x-messages-store', 'data'),
            # 输入框
            Output('ai-chat-x-input', 'value'),
            # 发送按钮状态
            Output('ai-chat-x-send-btn', 'loading'),
            Output('ai-chat-x-send-btn', 'disabled'),
            Output('ai-chat-x-send-btn', 'nClicks'),
            # 语音功能
            Output('voice-enable-voice', 'data'),
            # SSE连接
            Output('chat-X-sse', 'url'),
            Output('chat-X-sse', 'options'),
            # 全局消息
            Output('global-message', 'children'),
            # 会话管理
            Output('ai-chat-x-current-session-id', 'data'),
            Output('ai-chat-x-session-list-container', 'children'),
            Output('ai-chat-x-mobile-session-content', 'children'),
            Output('ai-chat-x-session-rename-modal', 'visible'),
            Output('ai-chat-x-session-rename-input', 'value'),
            Output('ai-chat-x-session-refresh-trigger', 'data'),
            Output('ai-chat-x-current-rename-conv-id', 'data'),
            # 语音通知
            Output('voice-message-notification', 'children')
        ],
        [
            # 文本输入相关
            Input('ai-chat-x-send-btn', 'nClicks'),
            Input({'type': 'chat-topic', 'index': dash.ALL}, 'nClicks'),
            
            # 语音相关
            Input('voice-transcription-store-server', 'data'),
            Input('voice-websocket-connection', 'data'),
            
            # SSE完成事件
            Input('ai-chat-x-sse-completed-receiver', 'data-completion-event'),
            
            # 消息操作
            Input({'type': 'ai-chat-x-regenerate', 'index': dash.ALL}, 'nClicks'),
            Input({'type': 'user-chat-x-regenerate', 'index': dash.ALL}, 'nClicks'),
            Input({'type': 'ai-chat-x-cancel', 'index': dash.ALL}, 'nClicks'),
            
            # 会话管理
            Input('ai-chat-x-session-new', 'n_clicks'),
            Input({'type': 'ai-chat-x-session-item', 'index': dash.ALL}, 'n_clicks'),
            Input({'type': 'ai-chat-x-session-dropdown', 'index': dash.ALL}, 'nClicks'),
            Input('ai-chat-x-session-rename-modal', 'okCounts'),
            Input('ai-chat-x-session-rename-modal', 'cancelCounts'),
            Input('ai-chat-x-session-rename-modal', 'closeCounts'),
            Input('ai-chat-x-session-refresh-trigger', 'data'),
            
            # 移动端会话
            Input('ai-chat-x-mobile-session-trigger', 'nClicks'),
            Input({'type': 'ai-chat-x-mobile-session-item', 'index': dash.ALL}, 'n_clicks'),
            Input('ai-chat-x-mobile-session-close', 'nClicks')
        ],
        [
            State('ai-chat-x-input', 'value'),
            State('ai-chat-x-messages-store', 'data'),
            State('ai-chat-x-current-session-id', 'data'),
            State('ai-chat-x-send-btn', 'nClicks'),
            State('ai-chat-x-session-rename-input', 'value'),
            State('ai-chat-x-current-rename-conv-id', 'data'),
            State('ai-chat-x-session-list-container', 'children'),
            State('ai-chat-x-mobile-session-content', 'children')
        ],
        prevent_initial_call=True
    )
    def complete_unified_handler(
        # 输入参数
        send_btn_clicks, topic_clicks, transcription_data, ws_connection,
        sse_completion_event, ai_regenerate_clicks, user_regenerate_clicks, cancel_clicks,
        session_new_clicks, session_item_clicks, session_dropdown_clicks,
        rename_ok_clicks, rename_cancel_clicks, rename_close_clicks, session_refresh_trigger,
        mobile_session_trigger, mobile_session_item_clicks, mobile_session_close,
        # 状态参数
        message_content, messages_store, current_session_id, send_btn_nclicks,
        rename_input_value, current_rename_conv_id, session_list_children, mobile_session_children
    ):
        """
        完整的统一聊天处理函数
        处理所有聊天相关操作：文本发送、语音转录、消息操作、会话管理、SSE处理
        """
        
        # 获取触发回调的元素ID
        triggered_id = ctx.triggered_id if ctx.triggered else None
        log.info(f"🔍 完整统一回调被触发: {triggered_id}")
        
        # 初始化消息存储
        messages = messages_store or []
        
        # 清理过期的SSE连接记录
        cleanup_expired_sse_connections()
        
        # 默认返回值（所有输出）
        default_returns = [
            messages, message_content, False, False, dash.no_update,  # 消息相关
            dash.no_update, dash.no_update, dash.no_update, dash.no_update,  # SSE和全局消息
            current_session_id, session_list_children, mobile_session_children,  # 会话相关
            False, '', dash.no_update, '',  # 会话管理
            dash.no_update  # 语音通知
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
        
        # 4. 处理语音WebSocket连接
        elif triggered_id == 'voice-websocket-connection':
            log.info(f"🎤 处理语音WebSocket连接")
            return _handle_voice_websocket_connection(messages, ws_connection, default_returns)
        
        # 5. 处理SSE完成事件
        elif triggered_id == 'ai-chat-x-sse-completed-receiver.data-completion-event':
            log.info(f"✅ 处理SSE完成事件")
            return _handle_sse_completion(messages, sse_completion_event, message_content, default_returns)
        
        # 6. 处理消息重新生成
        elif triggered_id and 'ai-chat-x-regenerate' in str(triggered_id):
            log.info(f"🔄 处理AI消息重新生成: {triggered_id}")
            return _handle_ai_regenerate(messages, triggered_id, current_session_id, default_returns)
        
        elif triggered_id and 'user-chat-x-regenerate' in str(triggered_id):
            log.info(f"🔄 处理用户消息重新生成: {triggered_id}")
            return _handle_user_regenerate(messages, triggered_id, current_session_id, default_returns)
        
        # 7. 处理取消发送
        elif triggered_id and 'ai-chat-x-cancel' in str(triggered_id):
            log.info(f"❌ 处理取消发送: {triggered_id}")
            return _handle_cancel_send(messages, triggered_id, default_returns)
        
        # 8. 处理会话管理
        elif triggered_id == 'ai-chat-x-session-new':
            log.info(f"📁 处理新建会话")
            return _handle_new_session(messages, current_session_id, default_returns)
        
        elif triggered_id and 'ai-chat-x-session-item' in str(triggered_id):
            log.info(f"📁 处理会话切换: {triggered_id}")
            return _handle_session_switch(messages, triggered_id, current_session_id, default_returns)
        
        elif triggered_id == 'ai-chat-x-session-rename-modal.okCounts':
            log.info(f"📝 处理会话重命名确认")
            return _handle_session_rename_confirm(messages, rename_input_value, current_rename_conv_id, default_returns)
        
        elif triggered_id in ['ai-chat-x-session-rename-modal.cancelCounts', 'ai-chat-x-session-rename-modal.closeCounts']:
            log.info(f"❌ 处理会话重命名取消")
            return _handle_session_rename_cancel(messages, default_returns)
        
        # 9. 处理移动端会话
        elif triggered_id == 'ai-chat-x-mobile-session-trigger':
            log.info(f"📱 处理移动端会话弹出")
            return _handle_mobile_session_trigger(messages, default_returns)
        
        elif triggered_id and 'ai-chat-x-mobile-session-item' in str(triggered_id):
            log.info(f"📱 处理移动端会话切换: {triggered_id}")
            return _handle_mobile_session_switch(messages, triggered_id, current_session_id, default_returns)
        
        elif triggered_id == 'ai-chat-x-mobile-session-close':
            log.info(f"📱 处理移动端会话关闭")
            return _handle_mobile_session_close(messages, default_returns)
        
        # 默认返回当前状态
        return default_returns


# 核心功能实现
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
        
        # 更新返回值
        result = default_returns.copy()
        result[0] = updated_messages  # messages
        result[1] = ''  # input value
        result[2] = True  # loading
        result[3] = True  # disabled
        result[6] = '/stream'  # SSE url
        result[7] = options  # SSE options
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
        
        # 更新返回值
        result = default_returns.copy()
        result[0] = updated_messages  # messages
        result[1] = ''  # input value
        result[2] = True  # loading
        result[3] = True  # disabled
        result[5] = True  # enable_voice
        result[6] = '/stream'  # SSE url
        result[7] = options  # SSE options
        return result
        
    except Exception as e:
        log.error(f"处理语音转录失败: {e}")
        return default_returns


def _handle_voice_websocket_connection(messages, ws_connection, default_returns):
    """处理语音WebSocket连接"""
    if not ws_connection or not ws_connection.get("connected"):
        return default_returns
    
    # 处理语音WebSocket连接状态
    log.info(f"🎤 语音WebSocket连接状态: {ws_connection}")
    
    # 这里可以添加语音连接相关的处理逻辑
    # 比如更新语音通知等
    
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


# 消息操作功能实现
def _handle_ai_regenerate(messages, triggered_id, current_session_id, default_returns):
    """处理AI消息重新生成"""
    try:
        # 解析触发ID获取消息索引
        if isinstance(triggered_id, dict) and 'index' in triggered_id:
            message_index = triggered_id['index']
        else:
            log.error(f"无法解析AI重新生成触发ID: {triggered_id}")
            return default_returns
        
        # 找到要重新生成的消息
        target_message = None
        target_index = None
        for i, message in enumerate(messages):
            if message.get('id') == f"ai-message-{message_index}":
                target_message = message
                target_index = i
                break
        
        if not target_message:
            log.error(f"未找到要重新生成的消息: ai-message-{message_index}")
            return default_returns
        
        # 删除该消息及其后续消息
        updated_messages = messages[:target_index]
        
        # 创建新的AI消息占位
        ai_message_id = f"ai-message-{len(updated_messages)}"
        ai_message = {
            'role': 'assistant',
            'content': '正在思考中...',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'id': ai_message_id,
            'is_streaming': True
        }
        updated_messages.append(ai_message)
        
        # 构建SSE请求
        try:
            # 获取最后一条用户消息
            last_user_msg = None
            for i in range(len(updated_messages) - 1, -1, -1):
                m = updated_messages[i]
                if m.get('role') == 'user':
                    last_user_msg = m
                    break
            
            if not last_user_msg:
                log.error("未找到用户消息")
                return default_returns
            
            conversation_messages = [{'role': 'user', 'content': last_user_msg.get('content', '')}]
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
            
            log.info(f"✅ AI消息重新生成完成，触发SSE: {ai_message_id}")
            
            # 更新返回值
            result = default_returns.copy()
            result[0] = updated_messages  # messages
            result[2] = True  # loading
            result[3] = True  # disabled
            result[6] = '/stream'  # SSE url
            result[7] = options  # SSE options
            return result
            
        except Exception as e:
            log.error(f"构建SSE请求失败: {e}")
            result = default_returns.copy()
            result[0] = updated_messages
            result[2] = True
            result[3] = True
            return result
            
    except Exception as e:
        log.error(f"处理AI消息重新生成失败: {e}")
        return default_returns


def _handle_user_regenerate(messages, triggered_id, current_session_id, default_returns):
    """处理用户消息重新生成"""
    try:
        # 解析触发ID获取消息索引
        if isinstance(triggered_id, dict) and 'index' in triggered_id:
            message_index = triggered_id['index']
        else:
            log.error(f"无法解析用户重新生成触发ID: {triggered_id}")
            return default_returns
        
        # 找到要重新生成的消息
        target_message = None
        target_index = None
        for i, message in enumerate(messages):
            if message.get('id') == f"usr-message-{message_index}":
                target_message = message
                target_index = i
                break
        
        if not target_message:
            log.error(f"未找到要重新生成的消息: usr-message-{message_index}")
            return default_returns
        
        # 删除该消息及其后续消息
        updated_messages = messages[:target_index]
        
        # 创建新的用户消息占位（保持原内容）
        usr_message_id = f"usr-message-{len(updated_messages)}"
        user_message = {
            'role': 'user',
            'content': target_message.get('content', ''),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'id': usr_message_id
        }
        updated_messages.append(user_message)
        
        # 创建新的AI消息占位
        ai_message_id = f"ai-message-{len(updated_messages)}"
        ai_message = {
            'role': 'assistant',
            'content': '正在思考中...',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'id': ai_message_id,
            'is_streaming': True
        }
        updated_messages.append(ai_message)
        
        # 构建SSE请求
        try:
            conversation_messages = [{'role': 'user', 'content': target_message.get('content', '')}]
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
            
            log.info(f"✅ 用户消息重新生成完成，触发SSE: {ai_message_id}")
            
            # 更新返回值
            result = default_returns.copy()
            result[0] = updated_messages  # messages
            result[2] = True  # loading
            result[3] = True  # disabled
            result[6] = '/stream'  # SSE url
            result[7] = options  # SSE options
            return result
            
        except Exception as e:
            log.error(f"构建SSE请求失败: {e}")
            result = default_returns.copy()
            result[0] = updated_messages
            result[2] = True
            result[3] = True
            return result
            
    except Exception as e:
        log.error(f"处理用户消息重新生成失败: {e}")
        return default_returns


def _handle_cancel_send(messages, triggered_id, default_returns):
    """处理取消发送"""
    try:
        # 解析触发ID获取消息索引
        if isinstance(triggered_id, dict) and 'index' in triggered_id:
            message_index = triggered_id['index']
        else:
            log.error(f"无法解析取消发送触发ID: {triggered_id}")
            return default_returns
        
        # 找到要取消的消息
        target_message = None
        target_index = None
        for i, message in enumerate(messages):
            if message.get('id') == f"ai-message-{message_index}":
                target_message = message
                target_index = i
                break
        
        if not target_message:
            log.error(f"未找到要取消的消息: ai-message-{message_index}")
            return default_returns
        
        # 检查消息是否正在流式传输
        if not target_message.get('is_streaming', False):
            log.warning(f"消息 {message_index} 不在流式传输状态，无需取消")
            return default_returns
        
        # 删除正在流式传输的消息
        updated_messages = messages[:target_index]
        
        # 清理SSE连接
        message_id = target_message.get('id')
        if message_id in active_sse_connections:
            del active_sse_connections[message_id]
        
        log.info(f"✅ 取消发送完成: {message_id}")
        
        # 更新返回值
        result = default_returns.copy()
        result[0] = updated_messages  # messages
        result[2] = False  # loading
        result[3] = False  # disabled
        result[6] = dash.no_update  # SSE url
        result[7] = dash.no_update  # SSE options
        return result
        
    except Exception as e:
        log.error(f"处理取消发送失败: {e}")
        return default_returns


# 会话管理功能实现（占位符）
def _handle_topic_click(messages, triggered_id, default_returns):
    """处理话题点击"""
    log.info(f"💬 话题点击: {triggered_id}")
    return default_returns

def _handle_new_session(messages, current_session_id, default_returns):
    """处理新建会话"""
    log.info(f"📁 新建会话")
    return default_returns

def _handle_session_switch(messages, triggered_id, current_session_id, default_returns):
    """处理会话切换"""
    log.info(f"📁 会话切换: {triggered_id}")
    return default_returns

def _handle_session_rename_confirm(messages, rename_input_value, current_rename_conv_id, default_returns):
    """处理会话重命名确认"""
    log.info(f"📝 会话重命名确认: {rename_input_value}")
    return default_returns

def _handle_session_rename_cancel(messages, default_returns):
    """处理会话重命名取消"""
    log.info(f"❌ 会话重命名取消")
    return default_returns

def _handle_mobile_session_trigger(messages, default_returns):
    """处理移动端会话弹出"""
    log.info(f"📱 移动端会话弹出")
    return default_returns

def _handle_mobile_session_switch(messages, triggered_id, current_session_id, default_returns):
    """处理移动端会话切换"""
    log.info(f"📱 移动端会话切换: {triggered_id}")
    return default_returns

def _handle_mobile_session_close(messages, default_returns):
    """处理移动端会话关闭"""
    log.info(f"📱 移动端会话关闭")
    return default_returns
