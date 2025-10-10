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
from dash_extensions.streaming import sse_message, sse_options

# 添加用于SSE连接的存储
active_sse_connections = {}

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
        # 消息发送输入（仅按钮点击；Enter 由前端触发按钮点击）
        Input('ai-chat-x-send-btn', 'nClicks')
    ],
    [
        State('ai-chat-x-input', 'value'),
        State('ai-chat-x-messages-store', 'data'),
        State('ai-chat-x-current-session-id', 'data')
    ],
    prevent_initial_call=True
)
def handle_chat_interactions(topic_0_clicks, topic_1_clicks, topic_2_clicks, topic_3_clicks, 
                           send_button_clicks,
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
    elif triggered_id in ['ai-chat-x-send-btn'] and message_content:
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
            
            log.debug(f"创建用户消息和AI消息: {user_message}, {ai_message}")
            
            return updated_messages, ''
        # 如果消息内容为空，返回默认值
        return messages, message_content
    
    # 默认返回当前状态
    return messages, message_content

# SSE触发回调 - 用于启动SSE连接
@app.callback(
    [
        Output('chat-X-sse', 'url'),
        Output('chat-X-sse', 'options')
    ],
    [Input('ai-chat-x-messages-store', 'data')],
    [State('ai-chat-x-current-session-id', 'data')],
    prevent_initial_call=True
)
def trigger_sse(messages, current_session_id):
    # 检查是否有新的AI消息正在流式传输
    if messages and len(messages) > 0:
        last_message = messages[-1]
        # 只有当最后一条消息是AI消息并且处于流式传输状态时才触发SSE
        if last_message.get('role') in ['assistant', 'agent'] and last_message.get('is_streaming', False):
            # 获取消息ID
            message_id = last_message.get('id')
            role = last_message.get('role', 'assistant')
            
            # 准备要发送给/stream端点的消息
            # 只包含对话历史，不包含当前正在流式传输的消息
            conversation_messages = []
            for msg in messages:
                if msg.get('role') in ['user', 'assistant', 'agent', 'system'] and \
                   not (msg.get('role') in ['assistant', 'agent'] and msg.get('is_streaming', False)):
                    conversation_messages.append({
                        'role': msg.get('role'),
                        'content': msg.get('content')
                    })
            
            # 处理会话ID - 如果为空，使用默认值
            session_id = current_session_id or 'conversation_0001'
            
            # 构建请求数据
            request_data = {
                'messages': conversation_messages,
                'session_id': session_id,
                'personality_id': 'health_assistant',
                'message_id': message_id,
                'role': role
            }
            
            log.debug(f"触发SSE连接，消息ID: {message_id}, 会话ID: {session_id}")
            log.debug(f"SSE请求数据: {request_data}")
            
            # 使用sse_options函数正确配置SSE连接
            # 注意：这里需要传入正确的请求参数
            options = sse_options(
                payload=json.dumps(request_data),  # 转换为JSON字符串
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            
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
    log.debug(f"更新聊天历史，消息数量: {len(messages) if messages else 0}")
    # 直接使用消息列表渲染聊天历史
    return AiChatMessageHistory(messages or [])

# 注册函数，供app.py调用
def register_chat_input_callbacks(flask_app):
    """
    注册聊天输入区域的所有回调函数
    这个函数在app.py中被调用以确保所有回调正确注册
    """
    log.debug("注册聊天输入区域的所有回调函数")
    # 所有回调函数已经通过@app.callback装饰器注册
    # 这里可以添加一些额外的初始化代码（如果需要）
    
    # 添加SSE状态监控回调
    app.clientside_callback(
        """
        function(status) {
            console.log('SSE连接状态:', status);
            return window.dash_clientside.no_update;
        }
        """,
        Output('chat-X-sse', 'status', allow_duplicate=True),
        [
            Input('chat-X-sse', 'status')
        ],
        prevent_initial_call=True,
        allow_duplicate=True
    )

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
    function(animation) {
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
                    
                    // 4. 使用message_id查找元素并更新完整内容
                    const messageElement = document.getElementById(message_id);
                    if (messageElement) {
                        // 关键修改：适应FefferyMarkdown组件的更新方式
                        // 不再直接操作textContent，而是通过设置React属性来更新
                        if (messageElement.tagName.toLowerCase() === 'div' && messageElement.className.includes('agent-message-markdown-body')) {
                            // 这是FefferyMarkdown组件，查找内部的p标签
                            const contentElement = messageElement.querySelector('p');
                            if (contentElement) {
                                // 更新p标签的内容
                                contentElement.textContent = fullContent;
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

                            // 同步数据到消息存储
                            const event = new CustomEvent('sseCompleted', {
                                detail: {
                                    messageId: message_id,
                                    content: fullContent
                                }
                            });
                            document.dispatchEvent(event);
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
    Output('chat-X-sse', 'status', allow_duplicate=True),
    Input('chat-X-sse', 'animation'),
    prevent_initial_call=True,
    allow_duplicate=True
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



# 添加回调来处理会话完成事件，记录完整会话日志
@app.callback(
    Output('ai-chat-x-messages-store', 'data', allow_duplicate=True),
    [Input('ai-chat-x-sse-completed-receiver', 'data-completion-event')],
    [State('ai-chat-x-messages-store', 'data'),
     State('ai-chat-x-current-session-id', 'data')],
    prevent_initial_call=True,
    allow_duplicate=True
)
def log_complete_conversation(completion_event_json, messages, current_session_id):
    """当会话完成时，记录完整的会话日志"""
    if completion_event_json and messages:
        try:
            # 解析JSON字符串
            completion_event = json.loads(completion_event_json)
            
            # 获取会话ID
            session_id = current_session_id or 'default_session'
            
            # 获取消息ID和完整内容
            message_id = completion_event.get('messageId')
            full_content = completion_event.get('content')
            
            # 创建消息的深拷贝，避免修改原始数据
            updated_messages = copy.deepcopy(messages)
            
            # 查找并更新对应的AI消息
            for i, message in enumerate(updated_messages):
                if message.get('id') == message_id:
                    updated_messages[i]['content'] = full_content
                    updated_messages[i]['is_streaming'] = False
                    break
            
            # 记录完整会话日志
            log.debug(f"会话完成 - 会话ID: {session_id}")
            log.debug(f"更新的消息ID: {message_id}")
            log.debug(f"完整消息内容: {full_content}")
            log.debug(f"完整会话内容: {json.dumps(updated_messages, ensure_ascii=False, indent=2)}")
            
            # 返回更新后的消息存储
            return updated_messages
        except Exception as e:
            log.error(f"记录会话日志时出错: {str(e)}")
    
    # 不修改消息存储
    return no_update