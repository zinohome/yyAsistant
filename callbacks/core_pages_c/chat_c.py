
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
            Output('ai-chat-x-session-rename-input', 'value')
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
            return [dash.no_update, dash.no_update, False, '']
        
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
                        
                        # 返回新的时间戳以触发会话列表刷新
                        return [{'timestamp': time.time()}, dash.no_update, False, '']
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
                        return [dash.no_update, dash.no_update, False, '']
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
                    return [dash.no_update, dash.no_update, False, '']
        
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
                    # 调用Conversations模型的delete_conversation_by_conv_id方法删除会话
                    Conversations.delete_conversation_by_conv_id(conv_id)
                    
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
                    
                    # 返回新的时间戳以触发会话列表刷新
                    return [{'timestamp': time.time()}, dash.no_update, False, '']
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
                    return [dash.no_update, dash.no_update, False, '']
            # 如果点击的是改名按钮
            elif clicked_key == "rename":
                # 存储当前要改名的会话ID并显示改名对话框
                return [dash.no_update, conv_id, True, '']
        
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
                    
                    # 返回新的时间戳以触发会话列表刷新，并清空输入框和关闭对话框
                    return [{'timestamp': time.time()}, None, False, '']
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
                    return [dash.no_update, None, False, '']
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
                return [dash.no_update, current_rename_conv_id, True, '']
        
        # 处理会话改名对话框的取消或关闭按钮点击
        elif triggered_id == 'ai-chat-x-session-rename-modal' and ('cancelCounts' in triggered_prop_id or 'closeCounts' in triggered_prop_id):
            # 清空输入框和关闭对话框，但不刷新列表
            return [dash.no_update, None, False, '']
        
        # 其他情况不刷新列表，不显示对话框，清空输入框
        return [dash.no_update, dash.no_update, False, '']

    # 添加：会话列表刷新回调
    @app.callback(
        Output('ai-chat-x-session-list-container', 'children'),
        Input('ai-chat-x-session-refresh-trigger', 'data'),
        prevent_initial_call=True,
    )
    def refresh_session_list(trigger_data):
        """响应刷新触发器，重新渲染会话列表"""
        # 获取当前用户ID
        from flask_login import current_user
        
        if hasattr(current_user, 'id'):
            # 重新调用render_session_list函数渲染会话列表
            return render_session_list(user_id=current_user.id)
        else:
            # 如果无法获取用户ID，返回默认会话列表
            return render_session_list()

# 注册回调函数
register_chat_callbacks(app)
