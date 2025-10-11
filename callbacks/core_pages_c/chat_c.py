
import dash
from dash import Input, Output, State, ctx, set_props
import feffery_antd_components as fac
from server import app
from feffery_dash_utils.style_utils import style
import dash.html as html
import time  # 确保导入了time模块
from datetime import datetime
from server import app
from components.chat_session_list import render as render_session_list
from components.mobile_session_list import render_mobile_session_list
from models.conversations import Conversations
from utils.log import log as log
# 导入Conversations模型

def register_chat_callbacks(app):
    # 添加自定义折叠按钮的客户端回调函数 - 支持切换本地SVG图标
    app.clientside_callback(
        """(nClicks, collapsed, currentStyle) => {
            // 切换折叠状态并根据状态返回对应的图标路径
            const newCollapsedState = !collapsed;
            const iconSrc = newCollapsedState ? '/assets/imgs/right.svg' : '/assets/imgs/left.svg';
            
            // 控制新建会话按钮的显示/隐藏 - 只更新display属性，保留其他样式
            const updatedStyle = {...currentStyle, display: newCollapsedState ? 'none' : 'flex'};
            
            return [newCollapsedState, iconSrc, updatedStyle];
        }""",
        [
            Output('ai-chat-x-session-container', 'collapsed'),
            Output('ai-chat-x-session-collapse-trigger-icon', 'src'),  # 修改为src属性而不是icon
            Output('ai-chat-x-session-new', 'style')  # 添加对新建会话按钮样式的控制
        ],
        Input('ai-chat-x-session-collapse-trigger', 'nClicks'),
        [
            State('ai-chat-x-session-container', 'collapsed'),
            State('ai-chat-x-session-new', 'style')  # 获取当前样式状态
        ],
        prevent_initial_call=True,
    )

    # 添加处理"我的信息"菜单项点击事件的回调函数
    @app.callback(
        Input("ai-chat-x-user-dropdown", "nClicks"),
        State("ai-chat-x-user-dropdown", "clickedKey"),
        prevent_initial_call=True,
    )
    def handle_my_info_click(nClicks, clickedKey):
        """处理用户下拉菜单中"我的信息"项的点击事件"""
        #log.debug(f"回调被触发，点击的key是: {clickedKey}")
        if clickedKey == "my_info":
            set_props("my-info-drawer", {"visible": True})
        if clickedKey == "preference":
            set_props("preference-drawer", {"visible": True})

    # 修改：处理所有会话相关操作的统一回调函数
    @app.callback(
        [
            Output('ai-chat-x-session-refresh-trigger', 'data'),
            Output('ai-chat-x-current-rename-conv-id', 'data'),
            Output('ai-chat-x-session-rename-modal', 'visible'),
            Output('ai-chat-x-session-rename-input', 'value'),
            Output('ai-chat-x-current-session-id', 'data', allow_duplicate=True),
            Output('ai-chat-x-messages-store', 'data', allow_duplicate=True)
        ],
        [
            Input({'type': 'ai-chat-x-session-dropdown', 'index': dash.ALL}, 'nClicks'),
            Input('ai-chat-x-session-new', 'n_clicks'),
            Input('ai-chat-x-session-rename-modal', 'okCounts'),
            Input('ai-chat-x-session-rename-modal', 'cancelCounts'),
            Input('ai-chat-x-session-rename-modal', 'closeCounts')
        ],
        [
            State({'type': 'ai-chat-x-session-dropdown', 'index': dash.ALL}, 'clickedKey'),
            State({'type': 'ai-chat-x-session-dropdown', 'index': dash.ALL}, 'id'),
            State('ai-chat-x-current-rename-conv-id', 'data'),
            State('ai-chat-x-session-rename-input', 'value')
        ],
        prevent_initial_call=True,  # 确保页面加载时不触发此回调
    )
    def handle_all_session_actions(dropdown_clicks, new_session_clicks, rename_ok_clicks, 
                                   rename_cancel_clicks, rename_close_clicks, clickedKeys_list, 
                                   ids_list, current_rename_conv_id, new_name):
        """处理所有会话相关操作：新建会话、删除会话和修改会话名称"""
        
        # 首先检查是否有任何有效点击
        if not any(trigger['prop_id'].endswith('nClicks') or trigger['prop_id'].endswith('n_clicks') 
                  or trigger['prop_id'].endswith('okCounts') or trigger['prop_id'].endswith('cancelCounts') 
                  or trigger['prop_id'].endswith('closeCounts') for trigger in ctx.triggered):
            # 没有有效点击时，确保对话框是隐藏的
            return [dash.no_update, dash.no_update, False, '', dash.no_update, dash.no_update]
        
        # 获取触发回调的组件ID
        triggered_id = ctx.triggered_id
        triggered_prop_id = ctx.triggered[0]['prop_id']
        
        # 处理新建会话按钮点击
        if triggered_id == 'ai-chat-x-session-new':
            if new_session_clicks and new_session_clicks > 0:
                try:
                    # 获取当前用户ID
                    from flask_login import current_user
                    
                    if hasattr(current_user, 'id'):
                        user_id = current_user.id
                        
                        # 调用Conversations模型的add_conversation方法创建新会话
                        conv_id = Conversations.add_conversation(user_id=user_id)
                        
                        # log.debug(f"=== 创建新会话 ===")
                        # log.debug(f"新会话ID: {conv_id}")
                        log.debug(f"用户ID: {user_id}")
                        
                        # 显示创建成功的消息
                        set_props(
                            "global-message",
                            {
                                "children": fac.AntdMessage(
                                    type="success", 
                                    content="新会话创建成功"
                                )
                            },
                        )
                        
                        # 返回新的时间戳以触发会话列表刷新，同时设置当前会话ID和清空消息列表
                        # log.debug(f"=== 新建会话完成，设置当前会话ID: {conv_id} ===")
                        return [{'timestamp': time.time()}, dash.no_update, False, '', conv_id, []]
                    else:
                        # 用户未登录或无法获取用户ID
                        set_props(
                            "global-message",
                            {
                                "children": fac.AntdMessage(
                                    type="error", 
                                    content="无法创建会话：用户信息无效"
                                )
                            },
                        )
                        return [dash.no_update, dash.no_update, False, '', dash.no_update, dash.no_update]
                except Exception as e:
                    # 显示创建失败的消息
                    set_props(
                        "global-message",
                        {
                            "children": fac.AntdMessage(
                                type="error", 
                                content=f"创建会话失败: {str(e)}"
                            )
                        },
                    )
                    return [dash.no_update, dash.no_update, False, '', dash.no_update, dash.no_update]
        
        # 处理会话下拉菜单点击
        elif isinstance(triggered_id, dict) and triggered_id.get('type') == 'ai-chat-x-session-dropdown':
            # 获取当前会话的conv_id
            conv_id = triggered_id["index"]
            
            # 找到对应的clickedKey
            for i, id_dict in enumerate(ids_list):
                if id_dict["index"] == conv_id:
                    clicked_key = clickedKeys_list[i]
                    break
            
            # 如果点击的是删除按钮
            if clicked_key == "delete":
                try:
                    # log.debug(f"=== 开始删除会话 ===")
                    # log.debug(f"要删除的会话ID: {conv_id}")
                    # 调用Conversations模型的delete_conversation_by_conv_id方法删除会话
                    Conversations.delete_conversation_by_conv_id(conv_id)
                    # log.debug(f"会话删除成功: {conv_id}")
                    
                    # 显示删除成功的消息
                    set_props(
                        "global-message",
                        {
                            "children": fac.AntdMessage(
                                type="success", 
                                content="会话删除成功"
                            )
                        },
                    )
                    
                    # 返回新的时间戳以触发会话列表刷新，不保持当前会话ID（让刷新逻辑智能选择）
                    refresh_timestamp = {'timestamp': time.time()}
                    # log.debug(f"删除会话后触发刷新，时间戳: {refresh_timestamp}")
                    return [refresh_timestamp, dash.no_update, False, '', None, []]
                except Exception as e:
                    # 显示删除失败的消息
                    set_props(
                        "global-message",
                        {
                            "children": fac.AntdMessage(
                                type="error", 
                                content=f"会话删除失败: {str(e)}"
                            )
                        },
                    )
                    # 删除失败时不刷新列表
                    return [dash.no_update, dash.no_update, False, '', dash.no_update, dash.no_update]
            # 如果点击的是改名按钮
            elif clicked_key == "rename":
                # 获取当前会话的名称
                current_conv_name = ""
                try:
                    conv = Conversations.get_conversation_by_conv_id(conv_id)
                    if conv:
                        current_conv_name = conv.conv_name
                except Exception as e:
                    # 如果获取失败，使用空字符串
                    current_conv_name = ""
                
                # 存储当前要改名的会话ID并显示改名对话框，同时显示当前会话名称
                return [dash.no_update, conv_id, True, current_conv_name, dash.no_update, dash.no_update]
        
        # 处理会话改名对话框的确定按钮点击
        elif triggered_id == 'ai-chat-x-session-rename-modal' and 'okCounts' in triggered_prop_id:
            # 检查会话ID和新名称是否有效
            if current_rename_conv_id and new_name and new_name.strip():
                try:
                    # 调用Conversations模型的update_conversation_by_conv_id方法更新会话名称
                    Conversations.update_conversation_by_conv_id(conv_id=current_rename_conv_id, conv_name=new_name.strip())
                    
                    # 显示改名成功的消息
                    set_props(
                        "global-message",
                        {
                            "children": fac.AntdMessage(
                                type="success", 
                                content="会话名称修改成功"
                            )
                        },
                    )
                    
                    # 返回新的时间戳以触发会话列表刷新，保持当前会话ID，并清空输入框和关闭对话框
                    return [{'timestamp': time.time()}, None, False, '', dash.no_update, dash.no_update]
                except Exception as e:
                    # 显示改名失败的消息
                    set_props(
                        "global-message",
                        {
                            "children": fac.AntdMessage(
                                type="error", 
                                content=f"会话名称修改失败: {str(e)}"
                            )
                        },
                    )
                    # 改名失败时不刷新列表，但清空输入框和关闭对话框
                    return [dash.no_update, None, False, '', dash.no_update, dash.no_update]
            else:
                # 新名称不能为空
                set_props(
                    "global-message",
                    {
                        "children": fac.AntdMessage(
                            type="warning", 
                            content="会话名称不能为空"
                        )
                    },
                )
                # 名称为空时不刷新列表，但清空输入框
                return [dash.no_update, current_rename_conv_id, True, '', dash.no_update, dash.no_update]
        
        # 处理会话改名对话框的取消或关闭按钮点击
        elif triggered_id == 'ai-chat-x-session-rename-modal' and ('cancelCounts' in triggered_prop_id or 'closeCounts' in triggered_prop_id):
            # 清空输入框和关闭对话框，但不刷新列表
            return [dash.no_update, None, False, '', dash.no_update, dash.no_update]
        
        # 其他情况不刷新列表，不显示对话框，清空输入框
        return [dash.no_update, dash.no_update, False, '', dash.no_update, dash.no_update]

    # 添加：会话项点击回调 - 处理会话切换
    @app.callback(
        [
            Output('ai-chat-x-current-session-id', 'data'),
            Output('ai-chat-x-messages-store', 'data', allow_duplicate=True),
            Output('ai-chat-x-session-list-container', 'children')
        ],
        [
            Input({'type': 'ai-chat-x-session-item', 'index': dash.ALL}, 'n_clicks'),
            Input('ai-chat-x-session-refresh-trigger', 'data')
        ],
        [
            State('ai-chat-x-current-session-id', 'data'),
            State('ai-chat-x-session-list-container', 'children')
        ],
        prevent_initial_call=True,
    )
    def handle_session_switch(session_clicks, refresh_trigger, current_session_id, current_children):
        """处理会话切换和列表刷新"""
        ctx_triggered = ctx.triggered
        
        # 添加调试信息
        if ctx_triggered:
            # log.debug(f"=== 会话切换回调触发 ===")
            # log.debug(f"触发ID: {ctx_triggered[0]['prop_id']}")
            # log.debug(f"触发值: {ctx_triggered[0]['value']}")
            pass
        
        # 处理会话项点击
        if ctx_triggered and 'ai-chat-x-session-item' in ctx_triggered[0]['prop_id'] and 'n_clicks' in ctx_triggered[0]['prop_id']:
            try:
                # 获取点击的会话ID
                triggered_id = ctx_triggered[0]['prop_id']
                # 解析JSON获取index
                import json
                id_dict = json.loads(triggered_id.split('.')[0])
                clicked_session_id = id_dict['index']
                
                # 添加详细日志
                # log.debug(f"=== 会话切换开始 ===")
                # log.debug(f"点击的会话ID: {clicked_session_id}")
                # log.debug(f"当前会话ID: {current_session_id}")
                
                # 从数据库加载该会话的历史消息
                conv = Conversations.get_conversation_by_conv_id(clicked_session_id)
                if conv:
                    # log.debug(f"找到会话记录: conversation_id={conv.conversation_id}, conv_id={conv.conv_id}")
                    # log.debug(f"会话名称: {conv.conv_name}")
                    # log.debug(f"conv_memory类型: {type(conv.conv_memory)}")
                    # log.debug(f"conv_memory内容: {conv.conv_memory}")
                    
                    if conv.conv_memory and isinstance(conv.conv_memory, dict):
                        # 加载历史消息
                        history_messages = conv.conv_memory.get('messages', [])
                        # log.debug(f"加载会话历史消息: {clicked_session_id}, 消息数量: {len(history_messages)}")
                        # log.debug(f"历史消息内容: {history_messages}")
                    else:
                        # 如果没有历史消息，返回空列表
                        history_messages = []
                        # log.debug(f"会话无历史消息或conv_memory格式错误: {clicked_session_id}")
                else:
                    # 如果没有找到会话，返回空列表
                    history_messages = []
                    # log.debug(f"未找到会话记录: {clicked_session_id}")
                
                # 重新渲染会话列表（更新选中状态）
                from flask_login import current_user
                if hasattr(current_user, 'id'):
                    updated_children = render_session_list(user_id=current_user.id, selected_session_id=clicked_session_id)
                else:
                    updated_children = render_session_list(selected_session_id=clicked_session_id)
                
                # log.debug(f"=== 会话切换完成，返回会话ID: {clicked_session_id} ===")
                return clicked_session_id, history_messages, updated_children
                
            except Exception as e:
                log.error(f"处理会话切换失败: {e}")
                return dash.no_update, dash.no_update, dash.no_update
        
        # 处理列表刷新
        elif ctx_triggered and ctx_triggered[0]['prop_id'] == 'ai-chat-x-session-refresh-trigger.data':
            from flask_login import current_user
            # log.debug(f"=== 会话列表刷新 ===")
            # log.debug(f"当前会话ID: {current_session_id}")
            # log.debug(f"触发原因: {ctx_triggered[0]}")
            
            # 智能选择会话ID
            new_session_id = current_session_id
            history_messages = []
            
            if hasattr(current_user, 'id'):
                # 获取用户的所有会话
                user_sessions = Conversations.get_user_conversations(current_user.id)
                # log.debug(f"用户会话列表: {user_sessions}")
                # log.debug(f"会话数量: {len(user_sessions) if user_sessions else 0}")
                if user_sessions:
                    # 如果当前会话ID仍然存在，保持它
                    if current_session_id and any(session['conv_id'] == current_session_id for session in user_sessions):
                        new_session_id = current_session_id
                        # 加载当前会话的历史消息
                        conv = Conversations.get_conversation_by_conv_id(current_session_id)
                        if conv and conv.conv_memory:
                            history_messages = conv.conv_memory.get('messages', [])
                    else:
                        # 当前会话不存在，选择第一个会话（最新的）
                        new_session_id = user_sessions[0]['conv_id']
                        conv = Conversations.get_conversation_by_conv_id(new_session_id)
                        if conv and conv.conv_memory:
                            history_messages = conv.conv_memory.get('messages', [])
                        # log.debug(f"当前会话不存在，选择第一个会话（最新的）: {new_session_id}")
                else:
                    # 没有会话，创建新会话
                    new_session_id = Conversations.add_conversation(user_id=current_user.id)
                    history_messages = []
                    # log.debug(f"没有会话，创建新会话: {new_session_id}")
                
                updated_children = render_session_list(user_id=current_user.id, selected_session_id=new_session_id)
            else:
                updated_children = render_session_list(selected_session_id=new_session_id)
            
            # log.debug(f"=== 会话列表刷新完成 ===")
            # log.debug(f"新会话ID: {new_session_id}")
            # log.debug(f"历史消息数量: {len(history_messages)}")
            
            return new_session_id, history_messages, updated_children
        
        return dash.no_update, dash.no_update, dash.no_update

    # 会话列表刷新功能已合并到 handle_session_switch 回调中

    # 添加：移动端会话弹出框的回调函数
    @app.callback(
        [
            Output('ai-chat-x-mobile-session-content', 'children'),
            Output('ai-chat-x-session-refresh-trigger', 'data', allow_duplicate=True),
            Output('ai-chat-x-current-session-id', 'data', allow_duplicate=True),
            Output('ai-chat-x-messages-store', 'data', allow_duplicate=True)
        ],
        [
            Input('ai-chat-x-create-alternative-btn', 'nClicks'),
            Input({'type': 'ai-chat-x-mobile-session-item', 'index': dash.ALL}, 'n_clicks'),
            Input({'type': 'ai-chat-x-mobile-session-delete', 'index': dash.ALL}, 'nClicks'),
            Input('ai-chat-x-session-refresh-trigger', 'data')
        ],
        [
            State('ai-chat-x-current-session-id', 'data')
        ],
        prevent_initial_call=True,
    )
    def handle_mobile_session_popup(create_btn_clicks, session_clicks, delete_clicks, 
                                   refresh_trigger, current_session_id):
        """处理移动端会话弹出框的会话管理"""
        
        # 获取触发回调的组件
        triggered = ctx.triggered[0] if ctx.triggered else None
        
        if not triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # 添加调试信息
        # log.debug(f"移动端弹出框回调被触发: {triggered['prop_id']}")
        # log.debug(f"delete_clicks: {delete_clicks}")
        # log.debug(f"session_clicks: {session_clicks}")
        # log.debug(f"create_btn_clicks: {create_btn_clicks}")
        
        # 处理新建会话
        if triggered['prop_id'] == 'ai-chat-x-create-alternative-btn.nClicks' and create_btn_clicks > 0:
            try:
                from flask_login import current_user
                if hasattr(current_user, 'id'):
                    user_id = current_user.id
                    # 调用Conversations模型的add_conversation方法创建新会话
                    conv_id = Conversations.add_conversation(user_id=user_id)
                    
                    # log.debug(f"移动端创建新会话: {conv_id}")
                    
                    # 显示创建成功的消息
                    set_props(
                        "global-message",
                        {
                            "children": fac.AntdMessage(
                                type="success", 
                                content="新会话创建成功"
                            )
                        },
                    )
                    
                    # 刷新弹出框内容并设置当前会话
                    mobile_content = render_mobile_session_list(user_id=user_id, selected_session_id=conv_id)
                    return mobile_content, {'timestamp': time.time()}, conv_id, []
                else:
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update
            except Exception as e:
                log.error(f"创建会话失败: {e}")
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # 处理会话切换
        if triggered['prop_id'].startswith('{"type":"ai-chat-x-mobile-session-item"'):
            if session_clicks and any(click > 0 for click in session_clicks):
                # 获取被点击的会话ID
                import json
                prop_id = triggered['prop_id']
                if '{"type":"ai-chat-x-mobile-session-item"' in prop_id:
                    # 解析JSON格式的ID
                    id_part = prop_id.split('.')[0]  # 获取ID部分
                    id_dict = json.loads(id_part)
                    clicked_index = id_dict['index']
                else:
                    clicked_index = None
                
                # 加载会话历史消息
                history_messages = []
                try:
                    conv = Conversations.get_conversation_by_conv_id(clicked_index)
                    if conv and conv.conv_memory:
                        history_messages = conv.conv_memory.get('messages', [])
                except Exception as e:
                    log.error(f"加载会话历史失败: {e}")
                
                # 刷新弹出框内容
                from flask_login import current_user
                if hasattr(current_user, 'id'):
                    mobile_content = render_mobile_session_list(user_id=current_user.id, selected_session_id=clicked_index)
                else:
                    mobile_content = render_mobile_session_list(selected_session_id=clicked_index)
                
                return mobile_content, dash.no_update, clicked_index, history_messages
        
        # 处理会话删除
        # log.debug(f"检查删除条件: {triggered['prop_id']}")
        delete_pattern = '"type":"ai-chat-x-mobile-session-delete"'
        # log.debug(f"包含检查结果: {delete_pattern in triggered['prop_id']}")
        if delete_pattern in triggered['prop_id']:
            # log.debug(f"删除按钮被点击: {triggered['prop_id']}")
            # log.debug(f"delete_clicks类型: {type(delete_clicks)}")
            # log.debug(f"delete_clicks值: {delete_clicks}")
            if delete_clicks:
                # log.debug(f"any(click > 0): {any(click > 0 for click in delete_clicks)}")
                pass
            else:
                # log.debug("delete_clicks为None或空")
                pass
            
            if delete_clicks and any(click > 0 for click in delete_clicks):
                # log.debug("进入删除逻辑")
                # 获取被删除的会话ID
                import json
                prop_id = triggered['prop_id']
                # log.debug(f"尝试解析prop_id: {prop_id}")
                if '"type":"ai-chat-x-mobile-session-delete"' in prop_id:
                    # 解析JSON格式的ID
                    id_part = prop_id.split('.')[0]  # 获取ID部分
                    # log.debug(f"ID部分: {id_part}")
                    try:
                        id_dict = json.loads(id_part)
                        deleted_index = id_dict['index']
                        # log.debug(f"解析到删除的会话ID: {deleted_index}")
                    except json.JSONDecodeError as e:
                        log.error(f"JSON解析错误: {e}")
                        deleted_index = None
                else:
                    deleted_index = None
                    # log.debug("无法解析删除的会话ID")
                
                try:
                    # 删除会话
                    Conversations.delete_conversation_by_conv_id(deleted_index)
                    
                    # 如果删除的是当前会话，需要切换到其他会话
                    new_session_id = current_session_id
                    if deleted_index == current_session_id:
                        from flask_login import current_user
                        if hasattr(current_user, 'id'):
                            user_sessions = Conversations.get_user_conversations(current_user.id)
                            if user_sessions:
                                new_session_id = user_sessions[0]['conv_id']
                                # 加载新会话的历史消息
                                conv = Conversations.get_conversation_by_conv_id(new_session_id)
                                history_messages = conv.conv_memory.get('messages', []) if conv and conv.conv_memory else []
                            else:
                                # 没有会话了，创建新会话
                                new_session_id = Conversations.add_conversation(user_id=current_user.id)
                                history_messages = []
                        else:
                            new_session_id = ''
                            history_messages = []
                    else:
                        history_messages = dash.no_update
                    
                    # 刷新弹出框内容
                    from flask_login import current_user
                    if hasattr(current_user, 'id'):
                        mobile_content = render_mobile_session_list(user_id=current_user.id, selected_session_id=new_session_id)
                    else:
                        mobile_content = render_mobile_session_list(selected_session_id=new_session_id)
                    
                    # 显示删除成功的消息
                    set_props(
                        "global-message",
                        {
                            "children": fac.AntdMessage(
                                type="success", 
                                content="会话删除成功"
                            )
                        },
                    )
                    
                    return mobile_content, {'timestamp': time.time()}, new_session_id, history_messages
                    
                except Exception as e:
                    log.error(f"删除会话失败: {e}")
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # 处理刷新触发器
        if triggered['prop_id'] == 'ai-chat-x-session-refresh-trigger.data' and refresh_trigger:
            # 刷新弹出框内容
            from flask_login import current_user
            if hasattr(current_user, 'id'):
                mobile_content = render_mobile_session_list(user_id=current_user.id, selected_session_id=current_session_id)
            else:
                mobile_content = render_mobile_session_list(selected_session_id=current_session_id)
            return mobile_content, dash.no_update, dash.no_update, dash.no_update
        
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# 注册回调函数
register_chat_callbacks(app)
