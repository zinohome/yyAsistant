import dash
from dash import ctx, Input, Output, State, callback, no_update, html, ClientsideFunction, ALL, set_props
import feffery_antd_components as fac
import json
from datetime import datetime

from components.ai_chat_message_history import AiChatMessageHistory
from server import app, server  # 确保同时导入了server
from utils.yychat_client import yychat_client
from utils.log import log
from configs.topics_loader import get_random_topic_description_by_category, get_categories
import copy
import threading
import time
from flask import Response, stream_with_context
from dash_extensions.streaming import sse_message, sse_options
from feffery_dash_utils.style_utils import style

# 添加用于SSE连接的存储
active_sse_connections = {}

# 聊天交互处理函数
@app.callback(
    [
        Output('ai-chat-x-messages-store', 'data'),
        Output('ai-chat-x-input', 'value'),
        Output('ai-chat-x-send-btn', 'loading', allow_duplicate=True),
        Output('ai-chat-x-send-btn', 'disabled', allow_duplicate=True),
        Output('voice-enable-voice', 'data')
    ],
    [
        # 话题提示点击输入 - 使用动态模式匹配
        Input({'type': 'chat-topic', 'index': ALL}, 'nClicks'),
        # 消息发送输入（仅按钮点击；Enter 由前端触发按钮点击）
        Input('ai-chat-x-send-btn', 'nClicks'),
        # SSE完成事件
        Input('ai-chat-x-sse-completed-receiver', 'data-completion-event'),
        # 语音转录结果（服务端可见的镜像）
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
def handle_chat_interactions(topic_clicks, send_button_clicks, completion_event_json, transcription_data,
                           message_content, messages_store, current_session_id, ws_connection_data):
    # 获取触发回调的元素ID
    triggered_id = ctx.triggered_id if ctx.triggered else None
    
    # 添加调试日志
    # log.debug(f"回调被触发: {triggered_id}")
    
    # 初始化消息存储（如果为空）
    messages = messages_store or []
    
    # 确保ctx.triggered不为空
    if not ctx.triggered:
        return messages, message_content, False, False, dash.no_update
    
    # 验证输入框内容（仅对发送按钮触发）
    if triggered_id == 'ai-chat-x-send-btn':
        log.info(f"🔍 chat_input_area_c.py: 发送按钮被触发，消息内容: {message_content[:50] if message_content else 'None'}...")
        if not message_content or not message_content.strip():
            log.info('输入框为空，拒绝提交')
            return messages, message_content, False, False, dash.no_update
    
    # 处理话题点击
    if triggered_id and isinstance(triggered_id, dict) and triggered_id.get('type') == 'chat-topic':
        # 获取话题索引
        topic_index = triggered_id.get('index')
        
        if topic_index is not None:
            # 获取分类列表
            categories = get_categories()
            category_list = list(categories.keys())
            
            if 0 <= topic_index < len(category_list):
                # 根据分类随机选择一个话题描述
                category = category_list[topic_index]
                random_description = get_random_topic_description_by_category(category)
                
                if random_description:
                    log.debug(f"分类话题点击: {category}, 索引: {topic_index}, 内容: {random_description}")
                    return messages, random_description, False, False, dash.no_update
        
        # 如果索引无效，返回默认值
        return messages, message_content, False, False, dash.no_update
    
    # 处理SSE完成事件
    elif triggered_id == 'ai-chat-x-sse-completed-receiver.data-completion-event' or 'sse-completed-receiver' in str(triggered_id):
        # log.debug(f"=== SSE完成事件处理 ===")
        # log.debug(f"触发ID: {triggered_id}")
        # log.debug(f"completion_event_json: {completion_event_json}")
        # log.debug(f"messages: {messages}")
        # log.debug(f"current_session_id: {current_session_id}")
        
        # 即使completion_event_json为空，也要处理，因为可能是客户端回调触发的
        if messages:
            try:
                if completion_event_json:
                    # 解析JSON字符串
                    completion_event = json.loads(completion_event_json)
                    
                    # 获取消息ID和完整内容
                    message_id = completion_event.get('messageId')
                    full_content = completion_event.get('content')
                    
                    #log.debug(f"解析的完成事件: message_id={message_id}, content={full_content}")
                else:
                    # 如果没有completion_event_json，尝试从最后一条AI消息获取信息
                    last_message = messages[-1] if messages else None
                    if last_message and last_message.get('role') in ['assistant', 'agent'] and last_message.get('is_streaming', False):
                        message_id = last_message.get('id')
                        # 从DOM中获取完整内容（这里暂时使用占位符）
                        full_content = "SSE完成，但内容需要从DOM获取"
                        # log.debug(f"从最后一条消息获取: message_id={message_id}")
                    else:
                        # log.debug("没有找到需要完成的流式消息")
                        return messages, message_content, False, False, dash.no_update
                
                # 创建消息的深拷贝，避免修改原始数据
                updated_messages = copy.deepcopy(messages)
                
                # 查找并更新对应的AI消息
                for i, message in enumerate(updated_messages):
                    if message.get('id') == message_id:
                        updated_messages[i]['content'] = full_content
                        updated_messages[i]['is_streaming'] = False
                        # log.debug(f"更新AI消息: {message_id} -> {full_content}")
                        break
                
                # 保存AI消息到数据库
                if current_session_id:
                    try:
                        from models.conversations import Conversations
                        conv = Conversations.get_conversation_by_conv_id(current_session_id)
                        if conv:
                            # 获取现有消息
                            existing_messages = conv.conv_memory.get('messages', []) if conv.conv_memory else []
                            # 查找并更新AI消息
                            for i, msg in enumerate(existing_messages):
                                if msg.get('id') == message_id:
                                    existing_messages[i]['content'] = full_content
                                    existing_messages[i]['is_streaming'] = False
                                    break
                            # 更新数据库
                            Conversations.update_conversation_by_conv_id(
                                current_session_id,
                                conv_memory={'messages': existing_messages}
                            )
                            # log.debug(f"AI消息已保存到数据库: {current_session_id}")
                    except Exception as e:
                        log.error(f"保存AI消息到数据库失败: {e}")
                
                # 通知前端SSE完成，准备TTS
                log.info("SSE完成，通知前端准备TTS")
                # 前端会调用 prepareForTTS() 检查 AUTO_PLAY 配置
                
                # 清理活跃的SSE连接
                if message_id in active_sse_connections:
                    del active_sse_connections[message_id]
                    # log.debug(f"清理SSE连接: {message_id}")
                
                # 返回更新后的消息存储和恢复按钮状态
                return updated_messages, message_content, False, False, dash.no_update
            except Exception as e:
                log.error(f"处理SSE完成事件时出错: {e}")
                return messages, message_content, False, False, dash.no_update
        else:
            # log.debug("SSE完成事件数据不完整，跳过处理")
            return messages, message_content, False, False, dash.no_update

    # 处理语音转录触发的发送（镜像Store）
    elif triggered_id == 'voice-transcription-store-server' and transcription_data and transcription_data.get('text'):
        try:
            transcribed_text = transcription_data.get('text', '').strip()
            if not transcribed_text:
                return messages, message_content, False, False

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

            # 添加AI流式消息占位
            ai_message_id = f"ai-message-{len(updated_messages)}"
            ai_message = {
                'role': 'assistant',
                'content': '正在思考中...',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'id': ai_message_id,
                'is_streaming': True
            }
            updated_messages.append(ai_message)

            # 组装语音开关数据，携带client_id用于SSE payload
            enable_voice_payload = True
            try:
                client_id = (ws_connection_data or {}).get('client_id') if isinstance(ws_connection_data, dict) else None
                enable_voice_payload = {
                    'enable': True,
                    'client_id': client_id,
                    'ts': int(time.time() * 1000)
                }
            except Exception:
                pass

            # 返回：更新消息列表，清空输入框，设置按钮loading/disabled，并设置语音开关（含client_id）
            return updated_messages, '', True, True, enable_voice_payload
        except Exception as e:
            log.error(f"处理语音转录发送时出错: {e}")
            return messages, message_content, False, False, dash.no_update
    
    # 处理消息发送
    elif triggered_id in ['ai-chat-x-send-btn'] and message_content:
        log.info(f"🔍 发送按钮被触发，消息内容: {message_content[:50]}...")
        
        # 触发按钮状态更新为text_processing（优先使用服务端set_props，避免dash_clientside依赖问题）
        try:
            from dash import set_props
            set_props('button-event-trigger', {
                'data': {
                    'type': 'text_button_clicked',
                    'timestamp': int(time.time() * 1000),
                    'metadata': {'from_scenario': 'text', 'auto_play': True}
                }
            })
            log.info("🔍 已触发按钮状态更新: text_processing (server set_props)")
        except Exception as e:
            log.error(f"触发按钮状态更新失败(set_props): {e}")
            # 兜底：尝试dash_clientside.set_props（若可用）
            try:
                import dash_clientside
                dash_clientside.set_props('button-event-trigger', {
                    'data': {
                        'type': 'text_button_clicked', 
                        'timestamp': int(time.time() * 1000),
                        'metadata': {'from_scenario': 'text', 'auto_play': True}
                    }
                })
                log.info("🔍 已触发按钮状态更新: text_processing (clientside set_props)")
            except Exception as e2:
                log.error(f"触发按钮状态更新失败(dash_clientside): {e2}")
        
        # 去除消息前后空格
        message_content = message_content.strip()
        
        if message_content:
            # 创建消息的深拷贝，避免修改原始数据
            updated_messages = copy.deepcopy(messages)
                       
            # 添加用户消息到消息列表的副本
            usr_message_id = f"usr-message-{len(updated_messages)}"
            user_message = {
                'role': 'user',
                'content': message_content,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'id': usr_message_id
            }
            updated_messages.append(user_message)
            
            # 创建一个空白的AI消息，用于后续接收流式响应
            ai_message_id = f"ai-message-{len(updated_messages)}"
            ai_message = {
                'role': 'assistant',
                'content': '正在思考中...',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'id': ai_message_id,
                'is_streaming': True
            }
            
            # 添加空白AI消息到消息列表
            updated_messages.append(ai_message)
            
            # 保存用户消息到数据库
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
                            'content': message_content,
                            'timestamp': user_message['timestamp'],
                            'id': usr_message_id
                        })
                        existing_messages.append({
                            'role': 'assistant',
                            'content': '正在思考中...',
                            'timestamp': ai_message['timestamp'],
                            'id': ai_message_id,
                            'is_streaming': True
                        })
                        # 更新数据库
                        Conversations.update_conversation_by_conv_id(
                            current_session_id,
                            conv_memory={'messages': existing_messages}
                        )
                        # log.debug(f"用户消息和AI消息已保存到数据库: {current_session_id}")
                except Exception as e:
                    log.error(f"保存用户消息到数据库失败: {e}")
            
            # log.debug(f"创建用户消息和AI消息: {user_message}, {ai_message}")
            log.info(f"✅ 发送按钮处理完成，更新后消息数量: {len(updated_messages)}, 返回给ai-chat-x-messages-store")
            
            return updated_messages, '', True, True, dash.no_update  # 发送时禁用按钮并显示loading
        # 如果消息内容为空，返回默认值
        return messages, message_content, False, False, dash.no_update
    
    # 默认返回当前状态
    return messages, message_content, False, False, dash.no_update

# SSE触发回调 - 用于启动SSE连接
@app.callback(
    [
        Output('chat-X-sse', 'url'),
        Output('chat-X-sse', 'options')
    ],
    [
        Input('ai-chat-x-messages-store', 'data'),
        Input('voice-enable-voice', 'data'),
        Input('voice-websocket-connection', 'data')
    ],
    [State('ai-chat-x-current-session-id', 'data')],
    prevent_initial_call=True
)
def trigger_sse(messages, enable_voice, ws_connection, current_session_id):
    log.info(f"🔍 trigger_sse被触发: messages数量={len(messages) if messages else 0}, enable_voice={enable_voice}")
    log.info(f"🔍 参数: ws_connection={ws_connection}")
    if messages:
        log.info(f"🔍 messages最后一条: {messages[-1]}")
    
    # 检查是否有新的AI消息正在流式传输
    if messages and len(messages) > 0:
        last_message = messages[-1]
        # 只有当最后一条消息是AI消息并且处于流式传输状态时才触发SSE
        if last_message.get('role') in ['assistant', 'agent'] and last_message.get('is_streaming', False):
            # 获取消息ID
            message_id = last_message.get('id')
            # 检查是否已经存在相同message_id的SSE连接，避免重复触发
            if message_id in active_sse_connections:
                # log.debug(f"SSE连接已存在，跳过重复触发: {message_id}")
                return no_update, no_update
            role = last_message.get('role', 'assistant')
            
            # 仅发送“最后一条用户消息”到/stream（按需避免提交全量历史）
            conversation_messages = []
            last_user_msg = None
            for i in range(len(messages) - 1, -1, -1):
                m = messages[i]
                if m.get('role') == 'user':
                    last_user_msg = m
                    break
            if last_user_msg:
                conversation_messages.append({
                    'role': 'user',
                    'content': last_user_msg.get('content', '')
                })
            
            # 处理会话ID - 如果为空，使用默认值
            session_id = current_session_id or 'conversation_0001'
            
            # 构建请求数据
            # 从WS连接信息获取client_id
            client_id = None
            try:
                log.debug(f"WS连接数据: {ws_connection}")
                if ws_connection and isinstance(ws_connection, dict):
                    client_id = ws_connection.get('client_id')
                    log.debug(f"从WS连接获取client_id: {client_id}")
                else:
                    log.debug(f"WS连接数据无效: {ws_connection}")
            except Exception as e:
                log.debug(f"获取client_id异常: {e}")
                client_id = None
            
            # 如果client_id为空，记录警告但不阻塞
            if not client_id:
                log.warning("client_id为空，TTS将被禁用")
                log.debug("client_id为空，尝试其他方式获取")

            # 语音联动判定：即使缺少client_id也不要阻断SSE文本
            # 缺少client_id时仅关闭本次TTS（enable_voice=False），待下次再启用
            enable_requested = False
            try:
                if isinstance(enable_voice, dict):
                    enable_requested = bool(enable_voice.get('enable'))
                else:
                    enable_requested = bool(enable_voice)
            except Exception:
                enable_requested = bool(enable_voice)

            request_data = {
                'messages': conversation_messages,
                'session_id': session_id,
                'personality_id': 'health_assistant',
                'message_id': message_id,
                'role': role,
            # 当有client_id时启用TTS（文本聊天和语音聊天都支持）
            'enable_voice': bool(client_id),
                # 后端需要定向推送的client_id（可能为空）
                'client_id': client_id
            }
            # 兼容后端新字段：conversation_id = session_id
            request_data['conversation_id'] = session_id

            try:
                log.debug(f"/stream 请求payload: enable_voice={request_data.get('enable_voice')}, "
                          f"client_id={request_data.get('client_id')}, "
                          f"message_id={request_data.get('message_id')}, "
                          f"conversation_id={request_data.get('conversation_id')}")
            except Exception:
                pass
            
            # log.debug(f"触发SSE连接，消息ID: {message_id}, 会话ID: {session_id}")
            # log.debug(f"SSE请求数据: {request_data}")
            
            # 记录活跃的SSE连接
            active_sse_connections[message_id] = {
                'session_id': session_id,
                'start_time': time.time()
            }
            
            # 使用sse_options函数正确配置SSE连接
            # 注意：这里需要传入正确的请求参数
            options = sse_options(
                payload=json.dumps(request_data, ensure_ascii=False),  # 转换为JSON字符串
                method='POST',
                headers={'Content-Type': 'application/json'}
            )

            try:
                log.debug(f"/stream 请求options已构建，url=/stream")
            except Exception:
                pass
            
            return '/stream', options
    
    # 如果不需要触发SSE，返回no_update
    return no_update, no_update

# 消息处理回调 - 已移除，所有更新通过客户端回调完成

# 更新聊天历史显示 - 只在初始加载和非流式场景下更新
@app.callback(
    Output('ai-chat-x-history-content', 'children'),
    [Input('ai-chat-x-messages-store', 'data')],
    prevent_initial_call=True
)
def update_chat_history(messages):
    """更新聊天历史显示 - 只在消息存储初始化或非流式更新时调用"""
    #log.debug(f"更新聊天历史，消息数量: {len(messages) if messages else 0}")
    # 直接使用消息列表渲染聊天历史
    return AiChatMessageHistory(messages or [])

# 注册函数，供app.py调用
def register_chat_input_callbacks(flask_app):
    """
    注册聊天输入区域的所有回调函数
    这个函数在app.py中被调用以确保所有回调正确注册
    """
    #log.debug("注册聊天输入区域的所有回调函数")
    # 所有回调函数已经通过@app.callback装饰器注册
    # 这里可以添加一些额外的初始化代码（如果需要）
    
    # SSE状态监控已合并到下面的回调中

    # 绑定回车/换行行为：Enter 提交、Shift+Enter 换行（使用全局监听，更可靠）
    app.clientside_callback(
        """
        function(_) {
            // 全局回车监听器，避免时机问题
            if (window.__chatEnterHandler) {
                return window.dash_clientside.no_update;
            }

            window.__chatEnterHandler = function(e) {
                // 检查是否在聊天输入框内
                const container = document.getElementById('ai-chat-x-input');
                if (!container || !container.contains(e.target)) {
                    return;
                }

                // 只处理 textarea 的 keydown 事件
                if (e.target.tagName !== 'TEXTAREA') {
                    return;
                }

                if (e.key === 'Enter') {
                    if (e.shiftKey) {
                        // Shift+Enter：允许换行
                        return;
                    }
                    // Enter：提交
                    e.preventDefault();
                    e.stopPropagation();
                    const btn = document.getElementById('ai-chat-x-send-btn');
                    if (btn) { 
                        btn.click(); 
                    }
                }
            };

            // 在 document 上监听，确保捕获所有事件
            document.addEventListener('keydown', window.__chatEnterHandler, { passive: false, capture: true });

            return window.dash_clientside.no_update;
        }
        """,
        Output('ai-chat-x-input', 'placeholder', allow_duplicate=True),
        Input('ai-chat-x-input', 'id'),
        prevent_initial_call=False,
        allow_duplicate=True
    )

# 添加客户端回调来处理SSE流式响应，直接更新DOM并在完成时同步数据
app.clientside_callback(
    """
    function(animation, status) {
        // 处理SSE状态变化
        if (status !== undefined) {
            // console.log('SSE连接状态:', status);
            
            // 新增：处理SSE连接错误状态
            if (status === 'error' || status === 'closed' || status === 'timeout') {
                // console.log('SSE连接出现错误、关闭或超时，尝试自动重连');
                
                // 获取当前会话和消息信息
                const sessionIdEl = document.getElementById('ai-chat-x-current-session-id');
                const sessionId = sessionIdEl?.value || '';
                
                let messages = [];
                try {
                    const messagesStore = document.getElementById('ai-chat-x-messages-store');
                    if (messagesStore) {
                        messages = JSON.parse(messagesStore.value || '[]');
                    }
                } catch (e) {
                    console.error('获取消息列表失败:', e);
                }
                
                // 查找最后一条正在流式传输的消息
                let lastStreamingMessage = null;
                for (let i = messages.length - 1; i >= 0; i--) {
                    if (messages[i].is_streaming) {
                        lastStreamingMessage = messages[i];
                        break;
                    }
                }
                
                if (lastStreamingMessage && lastStreamingMessage.id) {
                    // 调用自动重连管理函数
                    if (window.dash_clientside && window.dash_clientside.clientside_basic && window.dash_clientside.clientside_basic.manageSSEReconnection) {
                        window.dash_clientside.clientside_basic.manageSSEReconnection(
                            lastStreamingMessage.id, 
                            sessionId, 
                            messages, 
                            3 // 最大重试3次
                        );
                    }
                }
            }
        }
        
        // 处理SSE动画数据
        if (!animation) {
            return window.dash_clientside.no_update;
        }
        
        try {
            //console.log('接收到SSE动画消息:', animation);
            
            // 1. 拆分连续的JSON对象
            let messages = [];
            let currentMessage = '';
            let braceCount = 0;
            
            for (let i = 0; i < animation.length; i++) {
                const char = animation[i];
                currentMessage += char;
                
                if (char === '{') braceCount++;
                if (char === '}') braceCount--;
                
                if (braceCount === 0 && currentMessage.trim() !== '') {
                    try {
                        messages.push(JSON.parse(currentMessage.trim()));
                    } catch (e) {
                        console.warn('解析单条消息失败:', currentMessage, e);
                    }
                    currentMessage = '';
                }
            }
            
            // 2. 处理消息，收集所有内容
            if (messages.length > 0) {
                // 获取第一个消息的message_id（所有消息应该有相同的message_id）
                const message_id = messages[0].message_id;
                
                if (message_id) {
                    // 3. 收集所有消息的content
                    let fullContent = '';
                    let finalStatus = 'streaming';
                    
                    messages.forEach(msg => {
                        if (msg.content) {
                            fullContent += msg.content;
                        }
                        if (msg.status) {
                            finalStatus = msg.status;
                        }
                    });
                    
                    // 新增：处理超时状态
                    if (finalStatus === 'timeout') {
                        fullContent = '响应超时，请重试';
                        console.warn('SSE响应超时:', message_id);
                    }
                    
                    // 4. 使用message_id查找元素并更新完整内容
                    const messageElement = document.getElementById(message_id);
                    if (messageElement) {
                        // 关键修改：适应FefferyMarkdown组件的更新方式
                        // 不再直接操作textContent，而是通过设置React属性来更新
                        if (messageElement.tagName.toLowerCase() === 'div' && messageElement.className.includes('agent-message-markdown-body')) {
                            // 这是FefferyMarkdown组件，查找内部的p标签
                            const contentElement = messageElement.querySelector('p');
                            if (contentElement) {
                                // 处理未完成的Markdown语法
                                let processedContent = fullContent;
                                
                                // 处理未闭合的代码块
                                const codeBlockCount = (fullContent.match(/```/g) || []).length;
                                if (codeBlockCount % 2 === 1) {
                                    processedContent += '\\n```';
                                }
                                
                                // 更新p标签的内容
                                contentElement.textContent = processedContent;
                                
                                // 新增：在流式传输过程中自动滚动
                                if (window.dash_clientside && window.dash_clientside.clientside_basic && window.dash_clientside.clientside_basic.autoScrollToBottom) {
                                    window.dash_clientside.clientside_basic.autoScrollToBottom();
                                }
                            }
                            
                            // 更新流式状态标记
                            const parentMessage = messageElement.closest('.chat-message');
                            if (parentMessage) {
                                parentMessage.setAttribute('data-streaming', 'false');
                            }
                        } else {
                            // 对于传统文本元素，保持原有逻辑
                            messageElement.textContent = fullContent;
                        }
                        
                        // 5. 如果状态是completed，更新流式状态
                        if (finalStatus === 'completed') {
                            const parentMessage = messageElement.closest('.chat-message');
                            if (parentMessage) {
                                parentMessage.setAttribute('data-streaming', 'false');
                            }

                            // 清理重连信息和超时检测器
                            const sessionIdEl = document.getElementById('ai-chat-x-current-session-id');
                            const sessionId = sessionIdEl?.value || '';
                            if (window.dash_clientside && window.dash_clientside.clientside_basic) {
                                if (window.dash_clientside.clientside_basic.clearSSEReconnectInfo) {
                                    window.dash_clientside.clientside_basic.clearSSEReconnectInfo(message_id, sessionId);
                                }
                                if (window.dash_clientside.clientside_basic.clearSSETimeoutMonitor) {
                                    window.dash_clientside.clientside_basic.clearSSETimeoutMonitor(message_id);
                                }
                            }

                            // 同步数据到消息存储
                            const event = new CustomEvent('sseCompleted', {
                                detail: {
                                    messageId: message_id,
                                    content: fullContent
                                }
                            });
                            document.dispatchEvent(event);

                            // 触发TTS播放（voice_player_enhanced.js 会监听 messageCompleted）
                            try {
                                const ttsEvent = new CustomEvent('messageCompleted', {
                                    detail: { text: fullContent }
                                });
                                document.dispatchEvent(ttsEvent);
                            } catch (e) {
                                console.warn('触发TTS事件失败:', e);
                            }
                            
                            // 新增：SSE完成时强制滚动到底部
                            if (window.dash_clientside && window.dash_clientside.clientside_basic && window.dash_clientside.clientside_basic.forceScrollToBottom) {
                                setTimeout(() => {
                                    window.dash_clientside.clientside_basic.forceScrollToBottom();
                                }, 100); // 延迟100ms确保DOM更新完成
                            }
                        }
                        
                        // 新增：处理超时状态
                        if (finalStatus === 'timeout') {
                            const parentMessage = messageElement.closest('.chat-message');
                            if (parentMessage) {
                                parentMessage.setAttribute('data-streaming', 'false');
                            }
                            
                            // 清理超时检测器
                            if (window.dash_clientside && window.dash_clientside.clientside_basic && window.dash_clientside.clientside_basic.clearSSETimeoutMonitor) {
                                window.dash_clientside.clientside_basic.clearSSETimeoutMonitor(message_id);
                            }
                        }
                    } else {
                        console.warn('未找到ID为', message_id, '的消息元素');
                    }
                }
            }
        } catch (e) {
            console.error('处理SSE消息时出错:', e);
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('chat-X-sse', 'status'),
    [Input('chat-X-sse', 'animation'), Input('chat-X-sse', 'status')],
    prevent_initial_call=True
)

app.clientside_callback(
    """
    function() {
        // 监听sseCompleted事件
        document.addEventListener('sseCompleted', function(event) {
            const { messageId, content } = event.detail;
            
            // 使用dash_clientside.set_props设置一个特殊的属性而不是children
            dash_clientside.set_props('ai-chat-x-sse-completed-receiver', {
                'data-completion-event': JSON.stringify({
                    messageId: messageId,
                    content: content
                })
            });
        });
        return window.dash_clientside.no_update;
    }
    """,
    Output('ai-chat-x-sse-completed-receiver', 'id'), # 不会实际修改，仅用于触发
    [Input('ai-chat-x-sse-completed-receiver', 'id')],
    prevent_initial_call=False
)



# SSE完成事件处理已合并到 handle_chat_interactions 回调中

# 添加SSE连接状态管理回调
@app.callback(
    [
        Output('ai-chat-x-current-session', 'color'),
        Output('ai-chat-x-current-session', 'icon'),
        Output('ai-chat-x-connection-status', 'children'),
        Output('ai-chat-x-connection-status', 'style')
    ],
    [
        Input('chat-X-sse', 'url'),
        Input('ai-chat-x-sse-completed-receiver', 'data-completion-event'),
        Input('ai-chat-x-current-session', 'nClicks')
    ],
    prevent_initial_call=True,
    allow_duplicate=True
)
def manage_connection_status(sse_url, completion_event, tag_clicks):
    """管理SSE连接状态显示"""
    ctx_triggered = ctx.triggered
    
    if not ctx_triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    triggered_id = ctx_triggered[0]['prop_id']
    
    # SSE连接开始
    if triggered_id == 'chat-X-sse.url' and sse_url:
        # 启动超时检测
        try:
            # 获取当前消息存储
            from dash import callback_context
            current_messages = callback_context.states.get('ai-chat-x-messages-store.data', [])
            if current_messages:
                last_message = current_messages[-1]
                if last_message.get('is_streaming', False):
                    message_id = last_message.get('id')
                    if message_id:
                        # 在客户端启动超时检测
                        set_props("chat-X-sse", {
                            "url": sse_url,
                            "options": {
                                "onOpen": f"if(window.dash_clientside && window.dash_clientside.clientside_basic && window.dash_clientside.clientside_basic.startSSETimeoutMonitor) {{ window.dash_clientside.clientside_basic.startSSETimeoutMonitor('{message_id}', 30); }}"
                            }
                        })
        except Exception as e:
            log.error(f"启动SSE超时检测失败: {e}")
        
        return (
            "blue",  # 蓝色表示连接中
            fac.AntdIcon(icon="antd-loading", style=style(fontSize="12px")),
            "连接中...",
            style(fontSize="12px", color="#1890ff", marginLeft="8px")
        )
    
    # SSE连接完成
    elif triggered_id == 'ai-chat-x-sse-completed-receiver.data-completion-event' and completion_event:
        return (
            "green",  # 绿色表示正常
            fac.AntdIcon(icon="antd-check-circle", style=style(fontSize="12px")),
            "状态正常",
            style(fontSize="12px", color="#52c41a", marginLeft="8px")
        )
    
    # 点击重试
    elif triggered_id == 'ai-chat-x-current-session.nClicks':
        # 触发重试：重新发送当前消息
        try:
            # 获取当前消息存储
            from dash import callback_context
            current_messages = callback_context.states.get('ai-chat-x-messages-store.data', [])
            if current_messages:
                # 重新触发SSE连接
                set_props("chat-X-sse", {"url": "/stream"})
        except Exception as e:
            log.error(f"重试SSE连接失败: {e}")
        
        return (
            "orange",  # 橙色表示重试中
            fac.AntdIcon(icon="antd-reload", style=style(fontSize="12px")),
            "重试中...",
            style(fontSize="12px", color="#fa8c16", marginLeft="8px")
        )
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


# 合并的自动滚动和初始化回调
app.clientside_callback(
    """
    function(messages, historyId) {
        // 安全检查：确保 dash_clientside 对象存在
        if (typeof window.dash_clientside === 'undefined' || !window.dash_clientside) {
            console.warn('dash_clientside not ready, skipping auto scroll');
            return null;
        }
        
        // 检查触发源
        const triggered = window.dash_clientside.callback_context.triggered[0];
        if (!triggered) {
            return window.dash_clientside.no_update;
        }
        
        const triggeredId = triggered.prop_id;
        
        // 如果是页面加载时触发（historyId输入）
        if (triggeredId === 'ai-chat-x-history.id') {
            // console.log('页面加载，初始化滚动监听器');
            // 初始化滚动监听器
            if (window.dash_clientside.clientside_basic && window.dash_clientside.clientside_basic.initScrollListener) {
                // 延迟初始化，确保DOM完全加载
                setTimeout(() => {
                    window.dash_clientside.clientside_basic.initScrollListener();
                }, 500);
            }
        }
        // 如果是消息存储更新触发
        else if (triggeredId === 'ai-chat-x-messages-store.data' && messages && messages.length > 0) {
            // console.log('消息存储更新，触发自动滚动，消息数量:', messages.length);
            
            // 使用优化的自动滚动函数
            if (window.dash_clientside.clientside_basic && window.dash_clientside.clientside_basic.autoScrollToBottom) {
                // 延迟执行，确保DOM更新完成
                setTimeout(() => {
                    window.dash_clientside.clientside_basic.autoScrollToBottom(true); // 强制滚动
                }, 100);
            }
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('ai-chat-x-history', 'id'),  # 虚拟输出，仅用于触发回调
    [
        Input('ai-chat-x-messages-store', 'data'),
        Input('ai-chat-x-history', 'id')  # 页面加载时触发
    ],
    prevent_initial_call=False
)

# 重新生成AI消息的回调
# 合并的消息操作回调函数
@app.callback(
    [
        Output('ai-chat-x-messages-store', 'data', allow_duplicate=True),
        Output('ai-chat-x-input', 'value', allow_duplicate=True),
        Output('ai-chat-x-send-btn', 'nClicks', allow_duplicate=True),
        Output('global-message', 'children', allow_duplicate=True)
    ],
    [
        Input({'type': 'ai-chat-x-regenerate', 'index': dash.ALL}, 'nClicks'),
        Input({'type': 'user-chat-x-regenerate', 'index': dash.ALL}, 'nClicks'),
        Input({'type': 'ai-chat-x-cancel', 'index': dash.ALL}, 'nClicks')
    ],
    [
        State('ai-chat-x-messages-store', 'data'),
        State('ai-chat-x-current-session-id', 'data'),
        State('ai-chat-x-send-btn', 'nClicks')
    ],
    prevent_initial_call=True
)
def handle_message_operations(ai_regenerate_clicks, user_regenerate_clicks, cancel_clicks, 
                             messages, current_session_id, send_btn_clicks):
    """处理所有消息相关操作：重新生成、取消发送"""
    
    if not ctx.triggered:
        return [dash.no_update] * 4
    
    triggered = ctx.triggered[0]
    if not triggered:
        return [dash.no_update] * 4
    
    # 检查被触发的按钮是否有点击
    if triggered.get('value', 0) <= 0:
        return [dash.no_update] * 4
    
    try:
        # 解析被点击的消息ID
        import json
        prop_id = triggered['prop_id']
        
        # 处理AI消息重新生成
        if '"type":"ai-chat-x-regenerate"' in prop_id:
            id_part = prop_id.split('.')[0]
            id_dict = json.loads(id_part)
            target_message_id = id_dict['index']
            
            if not messages:
                return [dash.no_update] * 3 + [fac.AntdMessage(type="error", content="消息列表为空")]
            
            # 找到目标消息和上一条用户消息
            target_message_index = None
            previous_user_message = None
            
            for i, message in enumerate(messages):
                if message.get('id') == target_message_id:
                    target_message_index = i
                    # 查找上一条用户消息
                    for j in range(i-1, -1, -1):
                        if messages[j].get('role') == 'user':
                            previous_user_message = messages[j]
                            break
                    break
            
            if target_message_index is None:
                return [dash.no_update] * 3 + [fac.AntdMessage(type="error", content="无法重新生成：未找到目标消息")]
            
            if previous_user_message is None:
                return [dash.no_update] * 3 + [fac.AntdMessage(type="error", content="无法重新生成：未找到上一条用户消息")]
            
            # 创建消息的深拷贝
            updated_messages = copy.deepcopy(messages)
            
            # 删除目标AI消息
            del updated_messages[target_message_index]
            
            # 创建新的AI消息（正在思考中...）
            new_ai_message = {
                'role': 'assistant',
                'content': '正在思考中...',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'id': f"ai-message-{int(time.time() * 1000)}",
                'is_streaming': True
            }
            
            # 添加新的AI消息
            updated_messages.append(new_ai_message)
            
            # 返回更新后的消息，SSE会自动通过trigger_sse回调触发
            return updated_messages, dash.no_update, dash.no_update, dash.no_update
        
        # 处理用户消息重新生成
        elif '"type":"user-chat-x-regenerate"' in prop_id:
            id_part = prop_id.split('.')[0]
            id_dict = json.loads(id_part)
            target_message_id = id_dict['index']
            
            if not messages:
                return [dash.no_update] * 4
            
            # 找到目标用户消息
            target_message = None
            for message in messages:
                if message.get('id') == target_message_id and message.get('role') == 'user':
                    target_message = message
                    break
            
            if target_message:
                # 将用户消息内容填入输入框
                user_content = target_message.get('content', '')
                # 触发发送按钮点击
                new_send_clicks = send_btn_clicks + 1 if send_btn_clicks else 1
                
                return dash.no_update, user_content, new_send_clicks, dash.no_update, dash.no_update
            else:
                return [dash.no_update] * 4 + [fac.AntdMessage(type="error", content="无法重新生成：未找到目标用户消息")]
        
        # 处理取消发送消息
        elif '"type":"ai-chat-x-cancel"' in prop_id:
            id_part = prop_id.split('.')[0]
            id_dict = json.loads(id_part)
            target_message_id = id_dict['index']
            
            if not messages:
                return [dash.no_update] * 4
            
            # 创建消息的深拷贝
            updated_messages = copy.deepcopy(messages)
            
            # 找到并删除目标消息
            target_message_index = None
            for i, message in enumerate(updated_messages):
                if message.get('id') == target_message_id and message.get('is_streaming', False):
                    target_message_index = i
                    break
            
            if target_message_index is not None:
                # 删除正在流式传输的消息
                del updated_messages[target_message_index]
                
                # 清理活跃的SSE连接
                if target_message_id in active_sse_connections:
                    del active_sse_connections[target_message_id]
                    log.debug(f"取消发送，清理SSE连接: {target_message_id}")
                
                # 停止SSE连接
                set_props("chat-X-sse", {"url": None})
                
                # 显示取消成功的消息
                success_message = fac.AntdMessage(
                    type="info", 
                    content="消息发送已取消"
                )
                
                log.debug(f"取消发送消息: {target_message_id}")
                return updated_messages, dash.no_update, dash.no_update, None, success_message
            else:
                # 未找到目标消息
                error_message = fac.AntdMessage(
                    type="warning", 
                    content="无法取消：未找到正在发送的消息"
                )
                return [dash.no_update] * 4 + [error_message]
        
        else:
            return [dash.no_update] * 4
        
    except Exception as e:
        log.error(f"消息操作失败: {e}")
        error_message = fac.AntdMessage(
            type="error", 
            content=f"操作失败: {str(e)}"
        )
        return [dash.no_update] * 4 + [error_message]

# 复制消息的客户端回调
app.clientside_callback(
    """
    function(ai_copy_clicks, user_copy_clicks, messages) {
        if (!window.dash_clientside) {
            return window.dash_clientside.no_update;
        }
        
        const triggered = window.dash_clientside.callback_context.triggered[0];
        if (!triggered) {
            return window.dash_clientside.no_update;
        }
        
        // 检查被触发的按钮是否有点击（严格检查，避免初始化时触发）
        if (!triggered.value || triggered.value <= 0) {
            return window.dash_clientside.no_update;
        }
        
        // console.log('复制回调被触发:', triggered);
        
        // 处理复制按钮点击
        if (triggered.prop_id.includes('ai-chat-x-copy') || triggered.prop_id.includes('user-chat-x-copy')) {
            // console.log('处理复制按钮点击');
            try {
                // 解析消息ID
                const propId = triggered.prop_id;
                const idPart = propId.split('.')[0];
                const idDict = JSON.parse(idPart);
                const messageId = idDict.index;
                // console.log('消息ID:', messageId);
                
                // 从消息存储中获取原始内容
                if (messages) {
                    const targetMessage = messages.find(msg => msg.id === messageId);
                    if (targetMessage && targetMessage.content) {
                        // 复制到剪贴板 - 使用fallback方案
                        const content = targetMessage.content;
                        
                        // 尝试使用现代clipboard API
                        if (navigator.clipboard && navigator.clipboard.writeText) {
                            navigator.clipboard.writeText(content).then(() => {
                                // console.log('复制成功');
                            }).catch(() => {
                                // 如果现代API失败，使用fallback
                                fallbackCopyToClipboard(content);
                            });
                        } else {
                            // 使用fallback方案
                            fallbackCopyToClipboard(content);
                        }
                    }
                    
                    // Fallback复制函数
                    function fallbackCopyToClipboard(text) {
                        const textArea = document.createElement('textarea');
                        textArea.value = text;
                        textArea.style.position = 'fixed';
                        textArea.style.left = '-999999px';
                        textArea.style.top = '-999999px';
                        document.body.appendChild(textArea);
                        textArea.focus();
                        textArea.select();
                        
                        try {
                            const successful = document.execCommand('copy');
                            if (successful) {
                                // console.log('复制成功 (fallback)');
                            } else {
                                // console.log('复制失败 (fallback)');
                            }
                        } catch (err) {
                            // console.log('复制失败 (fallback):', err);
                        }
                        
                        document.body.removeChild(textArea);
                    }
                }
            } catch (error) {
                // console.error('复制消息失败:', error);
            }
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('ai-chat-x-copy-result', 'data', allow_duplicate=True),
    [
        Input({'type': 'ai-chat-x-copy', 'index': dash.ALL}, 'nClicks'),
        Input({'type': 'user-chat-x-copy', 'index': dash.ALL}, 'nClicks')
    ],
    State('ai-chat-x-messages-store', 'data'),
    prevent_initial_call=True
)


