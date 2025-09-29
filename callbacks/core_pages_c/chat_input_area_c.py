import dash
from dash import ctx, Input, Output, State, callback, no_update, html
import feffery_antd_components as fac
import json
from datetime import datetime

from components.ai_chat_message_history import AiChatMessageHistory
from utils.yychat_client import yychat_client
from utils.log import log
import copy
import threading
import time

# 全局字典用于存储流式响应任务和更新
streaming_tasks = {}
streaming_updates = {}

# 流式响应处理函数
def process_streaming_response(session_id, messages, message_id):
    """处理流式响应并更新聊天历史"""
    global streaming_updates, streaming_tasks
    
    try:
        # 初始化流式响应内容
        full_response = ""
        
        # 将当前任务ID添加到streaming_tasks字典中
        streaming_tasks[message_id] = True
        
        # 准备发送给API的消息格式
        api_messages = []
        for msg in messages:
            # 确保消息格式符合API要求
            api_msg = {
                'role': msg['role'],
                'content': msg['content']
            }
            api_messages.append(api_msg)
        
        log.debug(f"调用YYChat API，消息数: {len(api_messages)}, 会话ID: {session_id}")
        
        # 调用YYChat API获取流式响应
        try:
            # 获取流式响应生成器
            stream_generator = yychat_client.chat_completion(
                messages=api_messages,
                stream=True,
                temperature=0.7
            )
            
            log.debug(f"获取到流式响应生成器，开始处理数据块")
            
            # 遍历流式响应
            for chunk in stream_generator:
                # 检查任务是否被取消
                if message_id not in streaming_tasks:
                    log.debug(f"流式任务已取消，消息ID: {message_id}")
                    break
                
                # 记录原始chunk数据，以便调试
                log.debug(f"接收到原始流式数据块: {str(chunk)[:200]}")
                
                # 处理响应数据 - 根据YYChat API的实际返回格式调整
                if chunk:
                    # 尝试从不同可能的路径提取content
                    content = ""
                    
                    # 检查chunk是否直接包含content字段
                    if isinstance(chunk, dict):
                        if 'content' in chunk:
                            content = chunk['content']
                        # 检查chunk是否包含choices字段
                        elif 'choices' in chunk and chunk['choices']:
                            # 获取第一个choice
                            first_choice = chunk['choices'][0]
                            # 检查message字段
                            if 'message' in first_choice and 'content' in first_choice['message']:
                                content = first_choice['message']['content']
                            # 检查delta字段
                            elif 'delta' in first_choice and 'content' in first_choice['delta']:
                                content = first_choice['delta']['content']
                    
                    # 如果提取到了content，添加到full_response
                    if content:
                        full_response += content
                        
                        # 更新streaming_updates字典，供轮询组件获取
                        streaming_updates[message_id] = full_response
                        
                        log.debug(f"提取到内容: '{content[:50]}'..., 当前完整内容长度: {len(full_response)}, 消息ID: {message_id}")
                    else:
                        log.debug(f"未从数据块中提取到内容")
            
        except Exception as api_error:
            log.error(f"处理流式响应生成器时出错: {str(api_error)}")
            # 出错时，设置错误信息
            error_message = f"处理响应时出错: {str(api_error)}"
            streaming_updates[message_id] = error_message
        
        # 流式响应结束后，记录最终状态
        log.debug(f"流式响应完成，完整内容长度: {len(full_response)}, 消息ID: {message_id}")
        
        # 如果最终没有内容，可能是API没有返回任何数据
        if len(full_response) == 0:
            log.warning(f"流式响应完成但未获取到任何内容，消息ID: {message_id}")
            # 设置一个默认的错误消息
            streaming_updates[message_id] = "抱歉，暂时无法获取响应内容，请稍后再试。"
        else:
            # 确保最终内容被设置到streaming_updates中
            streaming_updates[message_id] = full_response
        
    except Exception as e:
        log.error(f"处理流式响应时出错: {str(e)}")
        # 出错时，设置错误信息
        error_message = f"处理响应时出错: {str(e)}"
        streaming_updates[message_id] = error_message
    finally:
        # 确保无论如何都会清理任务标记，但不立即清理streaming_updates
        # 因为handle_chat_interactions还需要从中获取最终内容
        if message_id in streaming_tasks:
            del streaming_tasks[message_id]
        
        log.debug(f"清理流式任务资源，消息ID: {message_id}")

# 此回调假设输入框及按钮已存在页面布局中，回调示意：输入后点击发送按钮，将输入内容存入Store，并清空输入框
# 添加一个专门的轮询组件回调函数
def register_chat_input_callbacks(app):
    # 合并后的回调函数：处理聊天输入相关的所有操作和流式更新
    @callback(
        [
            Output('ai-chat-x-messages-store', 'data'),
            Output('ai-chat-x-input', 'value'),
            Output('ai-chat-x-streaming-state', 'data')
        ],
        [
            # 话题提示点击输入
            Input(f'chat-topic-0', 'nClicks'),
            Input(f'chat-topic-1', 'nClicks'),
            Input(f'chat-topic-2', 'nClicks'),
            Input(f'chat-topic-3', 'nClicks'),
            # 消息发送输入
            Input('ai-chat-x-send-btn', 'nClicks'),
            Input('ai-chat-x-input', 'n_submit'),
            # 轮询更新输入（用于流式响应）
            Input('ai-chat-x-streaming-poll', 'n_intervals')
        ],
        [
            State('ai-chat-x-input', 'value'),
            State('ai-chat-x-messages-store', 'data'),
            State('ai-chat-x-current-session-id', 'data'),
            State('ai-chat-x-streaming-state', 'data')
        ],
        prevent_initial_call=True
    )
    def handle_chat_interactions(topic_0_clicks, topic_1_clicks, topic_2_clicks, topic_3_clicks, 
                               send_button_clicks, input_submit, streaming_poll, 
                               message_content, messages_store, current_session_id, streaming_state):
        # 获取触发回调的元素ID
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        # 初始化消息存储（如果为空）
        messages = messages_store or []
        
        # 初始化流式状态（如果为空）
        streaming_state = streaming_state or {
            'is_streaming': False,
            'current_ai_message_id': None,
            'current_ai_content': ''
        }
        
        # 处理话题点击
        if triggered_id and triggered_id.startswith('chat-topic-'):
            # 获取话题索引
            topic_index = int(triggered_id.split('-')[-1])
            # 预定义话题列表
            topics = [
                "如何提高工作效率？",
                "请帮我总结一下这个文档",
                "编写一个Python函数来处理数据",
                "解释量子计算的基本概念"
            ]
            
            if 0 <= topic_index < len(topics):
                # 返回话题内容到输入框
                return messages, topics[topic_index], streaming_state
            # 如果索引无效，返回默认值
            return messages, message_content, streaming_state
        
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
                
                # 更新流式状态
                streaming_state = {
                    'is_streaming': True,
                    'current_ai_message_id': f"ai-message-{len(updated_messages)}",
                    'current_ai_content': ''
                }
                
                # 启动流式响应处理线程，传递消息副本
                thread = threading.Thread(
                    target=process_streaming_response,
                    args=(current_session_id, updated_messages, streaming_state.get('current_ai_message_id'))
                )
                thread.daemon = True
                thread.start()
                
                return updated_messages, '', streaming_state
            # 如果消息内容为空，返回默认值
            return messages, message_content, streaming_state
        
        # 处理轮询更新（用于流式响应）
        elif triggered_id == 'ai-chat-x-streaming-poll' and streaming_state.get('is_streaming'):
            # 从streaming_updates获取当前AI消息的最新内容
            current_message_id = streaming_state.get('current_ai_message_id')
            if current_message_id and current_message_id in streaming_updates:
                current_ai_content = streaming_updates[current_message_id]
                
                # 更新流式状态
                updated_streaming_state = {
                    'is_streaming': True,
                    'current_ai_message_id': current_message_id,
                    'current_ai_content': current_ai_content
                }
                
                return messages, no_update, updated_streaming_state
            
            # 如果当前没有更新，检查任务是否已完成
            elif current_message_id and current_message_id not in streaming_tasks:
                # 流式任务已完成，但仍在等待更新
                # 检查是否有最终内容
                if current_message_id in streaming_updates:
                    final_content = streaming_updates[current_message_id]
                    
                    # 创建最终的AI消息并添加到消息历史
                    ai_message = {
                        'role': 'assistant',
                        'content': final_content,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # 创建消息副本并添加AI回复
                    updated_messages = copy.deepcopy(messages)
                    updated_messages.append(ai_message)
                    
                    # 从streaming_updates中移除
                    if current_message_id in streaming_updates:
                        del streaming_updates[current_message_id]
                    
                    # 重置流式状态
                    return updated_messages, no_update, {
                        'is_streaming': False,
                        'current_ai_message_id': None,
                        'current_ai_content': ''
                    }
                else:
                    # 如果没有内容，也重置流式状态以避免无限轮询
                    log.warning(f"流式任务已完成但未找到内容，重置状态，消息ID: {current_message_id}")
                    # 确保清理相关资源
                    if current_message_id in streaming_updates:
                        del streaming_updates[current_message_id]
                    return messages, no_update, {
                        'is_streaming': False,
                        'current_ai_message_id': None,
                        'current_ai_content': ''
                    }
            
            # 如果当前没有更新，返回no_update
            return messages, no_update, streaming_state
        
        # 默认返回当前状态，确保总是返回有效的元组
        return messages, message_content, streaming_state

    @callback(
        # 修改输出目标为正确的组件ID
        Output('ai-chat-x-history-content', 'children'),
        [Input('ai-chat-x-messages-store', 'data'),
         Input('ai-chat-x-streaming-state', 'data')],
        prevent_initial_call=False
    )
    def update_chat_history(messages, streaming_state):
        """更新聊天历史显示"""
        log.debug(f"update_chat_history被触发，消息数: {len(messages) if messages else 0}")
        log.debug(f"当前流式状态: {streaming_state}")
        # 深拷贝消息列表以避免修改原始数据
        display_messages = copy.deepcopy(messages or [])
        
        # 如果正在流式传输，添加当前正在生成的AI消息
        if streaming_state and streaming_state.get('is_streaming') and streaming_state.get('current_ai_content'):
            log.debug(f"正在流式传输，添加临时AI消息，内容长度: {len(streaming_state.get('current_ai_content'))}")
            # 创建临时AI消息对象 - 统一使用assistant角色
            streaming_ai_message = {
                'role': 'assistant',
                'content': streaming_state.get('current_ai_content'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_streaming': True
            }
            # 确保不会重复添加临时消息
            if not any(msg.get('is_streaming') for msg in display_messages):
                display_messages.append(streaming_ai_message)
                log.debug(f"添加临时AI消息后，显示消息数: {len(display_messages)}")
            
        log.debug(f"更新聊天历史完成，显示消息数: {len(display_messages)}")
        return AiChatMessageHistory(display_messages)

# 若全局注册，需在app.py或server.py中import并调用 register_chat_input_callbacks(app) 即可