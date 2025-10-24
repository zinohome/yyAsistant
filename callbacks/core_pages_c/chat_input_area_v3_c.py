"""
聊天输入区域回调函数 V3

集成超时和错误处理的聊天输入处理回调。

作者: AI Assistant
创建时间: 2024-10-24
版本: 3.0.0
"""

import dash
from dash import ctx, Input, Output, State, callback, no_update, html, ALL, set_props
import feffery_antd_components as fac
import json
from datetime import datetime
import copy
import threading
import time
from flask import Response, stream_with_context
from dash_extensions.streaming import sse_message, sse_options
from feffery_dash_utils.style_utils import style

from components.ai_chat_message_history import AiChatMessageHistory
from server import app, server
from utils.yychat_client import yychat_client
from utils.log import log
from configs.topics_loader import get_random_topic_description_by_category, get_categories

# 导入新的核心管理器
from core.state_manager.state_manager import State as AppState
from core.event_manager.event_manager import Event
from core.timeout_manager.timeout_manager import TimeoutType
from core.error_handler.error_handler import ErrorType, ErrorSeverity

# 添加用于SSE连接的存储
active_sse_connections = {}


def save_messages_to_database(current_session_id, user_message, ai_message):
    """保存用户消息和AI消息到数据库的公共函数"""
    if current_session_id:
        try:
            from models.conversations import Conversations
            conv = Conversations.get_conversation_by_conv_id(current_session_id)
            if conv:
                # 获取现有消息
                existing_messages = conv.conv_memory.get('messages', []) if conv.conv_memory else []
                # 添加用户消息和AI消息
                existing_messages.append({
                    'role': 'user',
                    'content': user_message['content'],
                    'timestamp': user_message['timestamp'],
                    'id': user_message['id']
                })
                existing_messages.append({
                    'role': 'assistant',
                    'content': '正在思考中...',
                    'timestamp': ai_message['timestamp'],
                    'id': ai_message['id'],
                    'is_streaming': True
                })
                # 更新数据库
                Conversations.update_conversation_by_conv_id(
                    current_session_id,
                    conv_memory={'messages': existing_messages}
                )
                log.info(f"✅ 消息已保存到数据库: {current_session_id}")
        except Exception as e:
            log.error(f"❌ 保存消息到数据库失败: {e}")


def handle_text_processing_with_timeout(message_content, current_session_id):
    """处理文本处理开始，集成超时管理"""
    try:
        # 获取全局管理器
        state_manager = app.state_manager
        event_manager = app.event_manager
        timeout_manager = app.timeout_manager
        error_handler = app.error_handler
        
        # 检查当前状态
        current_state = state_manager.get_state()
        if current_state != AppState.IDLE:
            log.warning(f"状态不是IDLE，无法处理新消息，当前状态: {current_state.value}")
            return False, None
        
        # 转换到TEXT_SSE状态
        success = state_manager.set_state(AppState.TEXT_SSE)
        if not success:
            log.error("无法转换到TEXT_SSE状态")
            return False, None
        
        # 启动超时管理
        content_length = len(message_content) if message_content else 0
        timeout_id = f"text_sse_{int(time.time())}"
        
        timeout_manager.start_timeout(
            timeout_id=timeout_id,
            content_length=content_length,
            timeout_type=TimeoutType.SSE
        )
        
        # 触发TEXT_START事件
        event_manager.emit_event_sync(Event.TEXT_START, {
            'message': message_content,
            'session_id': current_session_id,
            'timestamp': datetime.now().isoformat(),
            'timeout_id': timeout_id
        })
        
        log.info(f"✅ 文本处理开始: {message_content[:50]}... (超时ID: {timeout_id})")
        return True, timeout_id
        
    except Exception as e:
        log.error(f"❌ 处理文本开始失败: {e}")
        # 处理错误
        error_handler.handle_error(
            ErrorType.SYSTEM,
            f"文本处理开始失败: {e}",
            ErrorSeverity.HIGH
        )
        return False, None


def handle_text_processing_complete_with_timeout(message_id, full_content, timeout_id):
    """处理文本处理完成，集成超时管理"""
    try:
        # 获取全局管理器
        state_manager = app.state_manager
        event_manager = app.event_manager
        timeout_manager = app.timeout_manager
        
        # 检查当前状态
        current_state = state_manager.get_state()
        if current_state != AppState.TEXT_SSE:
            log.warning(f"状态不是TEXT_SSE，当前状态: {current_state.value}")
            return False
        
        # 转换到TEXT_TTS状态
        success = state_manager.set_state(AppState.TEXT_TTS)
        if not success:
            log.error("无法转换到TEXT_TTS状态")
            return False
        
        # 取消SSE超时，启动TTS超时
        timeout_manager.cancel_timeout(timeout_id)
        content_length = len(full_content) if full_content else 0
        tts_timeout_id = f"text_tts_{message_id}"
        
        timeout_manager.start_timeout(
            timeout_id=tts_timeout_id,
            content_length=content_length,
            timeout_type=TimeoutType.TTS
        )
        
        # 触发TEXT_SSE_COMPLETE事件
        event_manager.emit_event_sync(Event.TEXT_SSE_COMPLETE, {
            'message_id': message_id,
            'content': full_content,
            'timestamp': datetime.now().isoformat(),
            'timeout_id': tts_timeout_id
        })
        
        log.info(f"✅ 文本SSE完成: {message_id} (TTS超时ID: {tts_timeout_id})")
        return True
        
    except Exception as e:
        log.error(f"❌ 处理文本完成失败: {e}")
        # 处理错误
        app.error_handler.handle_error(
            ErrorType.SYSTEM,
            f"文本处理完成失败: {e}",
            ErrorSeverity.HIGH
        )
        return False


def handle_text_tts_complete_with_timeout(message_id, tts_timeout_id):
    """处理文本TTS完成，集成超时管理"""
    try:
        # 获取全局管理器
        state_manager = app.state_manager
        event_manager = app.event_manager
        timeout_manager = app.timeout_manager
        
        # 检查当前状态
        current_state = state_manager.get_state()
        if current_state != AppState.TEXT_TTS:
            log.warning(f"状态不是TEXT_TTS，当前状态: {current_state.value}")
            return False
        
        # 转换到IDLE状态
        success = state_manager.set_state(AppState.IDLE)
        if not success:
            log.error("无法转换到IDLE状态")
            return False
        
        # 取消TTS超时
        timeout_manager.cancel_timeout(tts_timeout_id)
        
        # 触发TEXT_TTS_COMPLETE事件
        event_manager.emit_event_sync(Event.TEXT_TTS_COMPLETE, {
            'message_id': message_id,
            'timestamp': datetime.now().isoformat()
        })
        
        log.info(f"✅ 文本TTS完成: {message_id}")
        return True
        
    except Exception as e:
        log.error(f"❌ 处理文本TTS完成失败: {e}")
        # 处理错误
        app.error_handler.handle_error(
            ErrorType.SYSTEM,
            f"文本TTS完成失败: {e}",
            ErrorSeverity.HIGH
        )
        return False


def handle_timeout_error(timeout_id, timeout_info):
    """处理超时错误"""
    try:
        # 获取全局管理器
        state_manager = app.state_manager
        error_handler = app.error_handler
        
        # 记录超时错误
        error_handler.handle_error(
            ErrorType.TIMEOUT,
            {
                'timeout_id': timeout_id,
                'timeout_info': timeout_info,
                'message': '处理超时'
            },
            ErrorSeverity.HIGH
        )
        
        # 转换到错误状态
        state_manager.set_state(AppState.ERROR, {
            'type': 'timeout',
            'timeout_id': timeout_id,
            'timeout_info': timeout_info
        })
        
        log.error(f"❌ 处理超时: {timeout_id}")
        return True
        
    except Exception as e:
        log.error(f"❌ 处理超时错误失败: {e}")
        return False


def handle_websocket_error(error_message):
    """处理WebSocket错误"""
    try:
        # 获取全局管理器
        state_manager = app.state_manager
        error_handler = app.error_handler
        
        # 记录WebSocket错误
        error_handler.handle_error(
            ErrorType.WEBSOCKET_CONNECTION,
            {
                'error_message': error_message,
                'message': 'WebSocket连接错误'
            },
            ErrorSeverity.HIGH
        )
        
        # 转换到错误状态
        state_manager.set_state(AppState.ERROR, {
            'type': 'websocket_error',
            'error_message': error_message
        })
        
        log.error(f"❌ WebSocket错误: {error_message}")
        return True
        
    except Exception as e:
        log.error(f"❌ 处理WebSocket错误失败: {e}")
        return False


@app.callback(
    [
        Output('ai-chat-x-messages-store', 'data'),
        Output('ai-chat-x-input', 'value'),
        Output('ai-chat-x-send-btn', 'loading', allow_duplicate=True),
        Output('ai-chat-x-send-btn', 'disabled', allow_duplicate=True),
        Output('voice-enable-voice', 'data')
    ],
    [
        # 话题提示点击输入
        Input({'type': 'chat-topic', 'index': ALL}, 'nClicks'),
        # 消息发送输入
        Input('ai-chat-x-send-btn', 'nClicks'),
        # SSE完成事件
        Input('ai-chat-x-sse-completed-receiver', 'data-completion-event'),
        # 语音转录结果
        Input('voice-transcription-store-server', 'data')
    ],
    [
        State('ai-chat-x-input', 'value'),
        State('ai-chat-x-messages-store', 'data'),
        State('ai-chat-x-current-session-id', 'data'),
        State('voice-websocket-connection', 'data')
    ],
    prevent_initial_call=True
)
def handle_chat_interactions_v3(topic_clicks, send_button_clicks, completion_event_json, transcription_data,
                               message_content, messages_store, current_session_id, ws_connection_data):
    """处理聊天交互 - V3版本，集成超时和错误处理"""
    
    # 获取触发回调的元素ID
    triggered_id = ctx.triggered_id if ctx.triggered else None
    
    # 初始化消息存储
    messages = messages_store or []
    
    # 确保ctx.triggered不为空
    if not ctx.triggered:
        return messages, message_content, False, False, dash.no_update
    
    # 获取全局状态管理器
    state_manager = app.state_manager
    current_state = state_manager.get_state()
    
    log.info(f"🔍 聊天交互V3被触发: {triggered_id}, 当前状态: {current_state.value}")
    
    # 处理话题点击
    if triggered_id and isinstance(triggered_id, dict) and triggered_id.get('type') == 'chat-topic':
        topic_index = triggered_id.get('index')
        
        if topic_index is not None:
            categories = get_categories()
            category_list = list(categories.keys())
            
            if 0 <= topic_index < len(category_list):
                category = category_list[topic_index]
                random_description = get_random_topic_description_by_category(category)
                
                if random_description:
                    log.debug(f"分类话题点击: {category}, 索引: {topic_index}")
                    return messages, random_description, False, False, dash.no_update
        
        return messages, message_content, False, False, dash.no_update
    
    # 处理发送按钮点击
    elif triggered_id == 'ai-chat-x-send-btn':
        log.info(f"🔍 发送按钮被触发，消息内容: {message_content[:50] if message_content else 'None'}...")
        
        # 验证输入内容
        if not message_content or not message_content.strip():
            log.info('输入框为空，拒绝提交')
            return messages, message_content, False, False, dash.no_update
        
        # 检查状态是否允许处理
        if current_state != AppState.IDLE:
            log.warning(f"状态不是IDLE，无法处理新消息，当前状态: {current_state.value}")
            return messages, message_content, False, False, dash.no_update
        
        # 开始文本处理（集成超时管理）
        success, timeout_id = handle_text_processing_with_timeout(message_content, current_session_id)
        if not success:
            return messages, message_content, False, False, dash.no_update
        
        # 创建用户消息
        user_message = {
            'id': f"user_{int(time.time() * 1000)}",
            'role': 'user',
            'content': message_content,
            'timestamp': datetime.now().isoformat()
        }
        
        # 创建AI消息占位符
        ai_message = {
            'id': f"ai_{int(time.time() * 1000)}",
            'role': 'assistant',
            'content': '正在思考中...',
            'timestamp': datetime.now().isoformat(),
            'is_streaming': True,
            'timeout_id': timeout_id
        }
        
        # 更新消息列表
        messages.append(user_message)
        messages.append(ai_message)
        
        # 保存到数据库
        save_messages_to_database(current_session_id, user_message, ai_message)
        
        # 启动SSE流
        try:
            sse_connection = start_sse_stream(ai_message['id'], message_content, current_session_id)
            if sse_connection:
                active_sse_connections[ai_message['id']] = sse_connection
        except Exception as e:
            log.error(f"❌ 启动SSE流失败: {e}")
            # 处理错误并重置状态
            app.error_handler.handle_error(
                ErrorType.SYSTEM,
                f"启动SSE流失败: {e}",
                ErrorSeverity.HIGH
            )
            state_manager.set_state(AppState.IDLE)
            return messages, message_content, False, False, dash.no_update
        
        return messages, "", True, True, dash.no_update
    
    # 处理SSE完成事件
    elif triggered_id == 'ai-chat-x-sse-completed-receiver.data-completion-event':
        log.info("🔍 SSE完成事件处理")
        
        if messages:
            try:
                if completion_event_json:
                    if isinstance(completion_event_json, str):
                        completion_event = json.loads(completion_event_json)
                    else:
                        completion_event = completion_event_json
                    
                    message_id = completion_event.get('messageId')
                    full_content = completion_event.get('content')
                    
                    # 获取超时ID
                    timeout_id = None
                    for message in messages:
                        if message.get('id') == message_id:
                            timeout_id = message.get('timeout_id')
                            break
                    
                    # 处理文本处理完成（集成超时管理）
                    if handle_text_processing_complete_with_timeout(message_id, full_content, timeout_id):
                        # 更新消息内容
                        for message in messages:
                            if message.get('id') == message_id:
                                message['content'] = full_content
                                message['is_streaming'] = False
                                break
                        
                        # 启动TTS（如果需要）
                        # 这里可以添加TTS逻辑
                        
                        return messages, message_content, False, False, dash.no_update
                    else:
                        # 处理失败，重置状态
                        state_manager.set_state(AppState.IDLE)
                        return messages, message_content, False, False, dash.no_update
                else:
                    log.warning("SSE完成事件数据为空")
                    return messages, message_content, False, False, dash.no_update
                    
            except Exception as e:
                log.error(f"❌ 处理SSE完成事件失败: {e}")
                # 处理错误
                app.error_handler.handle_error(
                    ErrorType.SYSTEM,
                    f"处理SSE完成事件失败: {e}",
                    ErrorSeverity.HIGH
                )
                # 重置状态
                state_manager.set_state(AppState.IDLE)
                return messages, message_content, False, False, dash.no_update
    
    # 处理语音转录结果
    elif triggered_id == 'voice-transcription-store-server.data':
        log.info("🔍 语音转录结果处理")
        
        if transcription_data and transcription_data.get('text'):
            # 将转录文本填入输入框
            return messages, transcription_data['text'], False, False, dash.no_update
    
    # 默认返回
    return messages, message_content, False, False, dash.no_update


def start_sse_stream(message_id, user_message, session_id):
    """启动SSE流"""
    try:
        def generate_sse():
            try:
                # 使用yychat_client发送消息
                response = yychat_client.send_message(
                    message=user_message,
                    session_id=session_id,
                    enable_voice=False
                )
                
                # 流式返回响应
                for chunk in response:
                    if chunk:
                        yield sse_message(chunk, event='message')
                
                # 发送完成事件
                yield sse_message({
                    'messageId': message_id,
                    'content': 'SSE完成',
                    'type': 'completion'
                }, event='completion')
                
            except Exception as e:
                log.error(f"❌ SSE流生成失败: {e}")
                yield sse_message({
                    'error': str(e),
                    'type': 'error'
                }, event='error')
        
        return generate_sse()
        
    except Exception as e:
        log.error(f"❌ 启动SSE流失败: {e}")
        return None


# 注册回调函数
def register_chat_input_callbacks_v3(app):
    """注册聊天输入回调函数V3"""
    log.info("✅ 聊天输入回调函数V3已注册")
