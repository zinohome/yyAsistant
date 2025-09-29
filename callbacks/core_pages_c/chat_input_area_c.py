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

# 全局字典用于存储流式响应任务
streaming_tasks = {}

# 添加新的流式API端点
@server.route('/streaming/<message_id>')
def stream_response(message_id):
    @stream_with_context
    def generate():
        try:
            # 首先发送一个空消息，确保客户端知道有消息正在处理
            initial_message = {
                'id': message_id,
                'content': '',
                'complete': False
            }
            yield f'data: {json.dumps(initial_message)}'
            
            # 使用模拟数据进行测试
            for i in range(3):
                time.sleep(1)  # 模拟延迟
                content = f"这是测试消息第{i+1}部分，包含中文内容。"
                
                sse_message = {
                    'id': message_id,
                    'content': content,
                    'complete': False
                }
                
                log.debug(f"发送SSE消息: {sse_message}")
                yield f'data: {json.dumps(sse_message)}'
            
            # 发送最终完整消息
            final_message = {
                'id': message_id,
                'content': "这是完整的测试响应消息，能够正确显示中文内容。",
                'complete': True
            }
            log.debug(f"发送最终SSE消息: {final_message}")
            yield f'data: {json.dumps(final_message)}'
            
        except Exception as e:
            log.error(f"处理流式响应时出错: {str(e)}")
            # 发送错误消息
            error_message = {
                'id': message_id,
                'content': f"处理过程中发生错误: {str(e)}",
                'complete': True,
                'error': True
            }
            yield f'data: {json.dumps(error_message)}'
    
    return Response(generate(), mimetype='text/event-stream')

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
            "提高工作效率",
            "数据分析技巧",
            "代码优化建议",
            "项目管理方法"
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
                'content': '',
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

# 处理SSE消息并更新对应的AI消息
@app.callback(
    Output('ai-chat-x-messages-store', 'data', allow_duplicate=True),
    Input('sse', 'message'),
    State('ai-chat-x-messages-store', 'data'),
    State('ai-chat-x-streaming-state', 'data'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def handle_sse_message(message, messages_store, streaming_state):
    """处理SSE消息并更新对应的AI消息"""
    log.debug(f"收到SSE消息: {message}")  # 添加调试日志
    if not message or not messages_store:
        return messages_store
    
    try:
        # 解析SSE消息数据
        data = json.loads(message)
        message_id = data.get('id')
        content = data.get('content', '')
        complete = data.get('complete', False)
        
        # 创建消息的深拷贝
        updated_messages = copy.deepcopy(messages_store)
        
        # 查找对应的AI消息并更新内容
        for msg in updated_messages:
            if msg.get('role') == 'assistant' and msg.get('id') == message_id:
                msg['content'] = content
                if complete:
                    msg['is_streaming'] = False
                break
        
        # 更新流式状态
        if streaming_state:
            streaming_state['is_streaming'] = not complete
        
        return updated_messages
    except Exception as e:
        log.error(f"处理SSE消息时出错: {str(e)}")
        return messages_store

# 客户端回调 - 更新UI显示
app.clientside_callback(
    """function(message) {
        console.log('客户端收到SSE消息:', message);  // 调试日志
        if (message) {
            try {
                const data = JSON.parse(message);
                const messageId = data.id;
                const content = data.content || '';
                const complete = data.complete || false;
                
                console.log('解析后的客户端消息:', {messageId, content, complete});
                
                // 直接使用messageId查找元素
                const messageElement = document.getElementById(messageId);
                console.log('查找元素结果:', messageElement);
                
                if (messageElement) {
                    // 修改选择器以匹配新的组件结构
                    let textElement = messageElement.querySelector('.ant-typography');
                    
                    // 如果没找到，尝试匹配FefferyDiv中的文本
                    if (!textElement) {
                        textElement = messageElement.querySelector('.feffery-div span');
                        console.log('使用FefferyDiv选择器查找:', textElement);
                    }
                    
                    // 如果找到了文本元素，更新内容
                    if (textElement) {
                        // 对于中文内容，确保正确处理
                        const displayText = content || (complete ? '响应完成' : '正在输入...');
                        console.log('准备更新内容为:', displayText);
                        textElement.textContent = displayText;
                        
                        // 确保元素可见
                        textElement.style.display = 'block';
                        messageElement.style.display = 'block';
                        
                        // 滚动到最新消息
                        const historyContainer = document.getElementById('ai-chat-x-history');
                        if (historyContainer) {
                            historyContainer.scrollTop = historyContainer.scrollHeight;
                        }
                    } else {
                        console.warn('未找到文本元素:', messageElement.innerHTML);
                    }
                } else {
                    console.warn('未找到消息元素，ID:', messageId);
                }
            } catch (e) {
                console.error('客户端回调执行错误:', e);
            }
        }
        return window.dash_clientside.no_update;
    }""",
    Output('dummy-output-for-sse', 'children'),  # 虚拟输出
    Input('sse', 'message'),
    prevent_initial_call=True
)

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

# 添加启动SSE连接的客户端回调
@app.callback(
    Output('dummy-output-for-sse', 'children', allow_duplicate=True),
    Input('ai-chat-x-messages-store', 'data'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def trigger_sse_connection(messages):
    try:
        # 检查是否有新的AI消息需要启动SSE连接
        if messages and len(messages) > 0:
            last_message = messages[-1]
            if last_message.get('role') == 'assistant' and last_message.get('is_streaming', False):
                ai_message_id = last_message.get('id')
                if ai_message_id:
                    log.debug(f"触发SSE连接，消息ID: {ai_message_id}")
                    # 创建一个新的消息元素来触发SSE连接
                    return html.Div(
                        id=f'sse-trigger-{ai_message_id}',
                        **{'data-message-id': ai_message_id},
                        style={'display': 'none'}
                    )
        return no_update
    except Exception as e:
        log.error(f"触发SSE连接时出错: {str(e)}")
        return no_update

# 添加新的客户端回调来处理SSE触发元素
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='startSSE'
    ),
    Output('dummy-output-for-sse', 'children', allow_duplicate=True),
    Input({'type': 'sse-trigger', 'id': ALL}, 'id'),
    prevent_initial_call=True
)

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