
import feffery_utils_components as fuc
import feffery_antd_components as fac
import dash
from dash import html, dcc
from feffery_dash_utils.style_utils import style

# 导入conversations模型
from models.conversations import Conversations


def render(sessions=None, user_id=None, refresh_timestamp=None, selected_session_id=None):
    """渲染聊天会话列表组件
    
    参数:
        sessions (list, optional): 会话数据列表，每个会话包含key, title字段
        user_id (str, optional): 用户ID，用于从数据库获取会话数据
        refresh_timestamp (float, optional): 刷新时间戳，用于触发重新渲染
        selected_session_id (str, optional): 当前选中的会话ID，用于高亮显示
        search_placeholder (str, optional): 搜索框占位符文本
        collapsed (bool, optional): 是否折叠会话列表，默认为False
    
    返回:
        Dash组件对象
    """
    
    # 添加调试日志
    # print(f"=== 渲染会话列表 ===")
    # print(f"selected_session_id: {selected_session_id}")
    # print(f"user_id: {user_id}")
    
    # 默认会话数据 - 只保留key和title
    default_sessions = [
        {"key": "1", "title": "新会话1"},
        {"key": "2", "title": "新会话2"},
        {"key": "3", "title": "新会话3"}
    ]
    
    # 从数据库获取会话数据
    session_data = []
    if user_id:
        try:
            # 调用get_user_conversations方法获取用户会话
            db_sessions = Conversations.get_user_conversations(user_id=user_id)
            if db_sessions:
                # 转换数据格式：key对应conv_id，title对应conv_name
                # 辅助函数：截断中文字符串
                def truncate_chinese_text(text, max_length=12):
                    """截断中文字符串，如果超过最大长度则添加省略号"""
                    if len(text) > max_length:
                        return text[:max_length] + "..."
                    return text
                    
                session_data = [
                    {"key": session["conv_id"], "title": truncate_chinese_text(session["conv_name"])}
                    for session in db_sessions
                ]
        except Exception as e:
            # print(f"获取会话数据失败: {e}")
            # 发生错误时使用默认数据
            session_data = default_sessions
    elif sessions:
        # 使用传入的会话数据
        session_data = sessions
    else:
        # 使用默认数据
        session_data = default_sessions

    # 修复：使用html.Div作为容器包裹所有组件
    return html.Div(
        [
            # 隐藏的Store用于跟踪点击事件
            dcc.Store(id="session-click-tracker", data=None),
            # 新建会话按钮 - 使用html.Div实现
            html.Div(
                id='ai-chat-x-session-new',  # 设置指定的ID
                children=[
                    # 将文本加号替换为fac.AntdIcon组件
                    fac.AntdIcon(
                        icon='antd-plus',  # 设置加号图标
                        style={
                            'fontSize': '16px',
                            'marginRight': '8px',
                        }
                    ),
                    html.Span(
                        '新建会话',
                        style={
                            'fontSize': '15px',  # 字体比其他菜单项稍大
                            'fontWeight': '500',
                        }
                    )
                ],
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'border': '1px solid #d9d9d9',  # 默认灰色边框
                    'backgroundColor': '#f5f5f5',   # 默认灰色背景
                    'padding': '10px 16px',
                    'margin': '0 12px 16px 12px',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease',
                },
                # 使用内联样式实现悬停效果
                className='ai-chat-x-session-new-button',
                n_clicks=0,  # 添加点击事件计数器
            ),

            # 会话列表区域 - 保持FefferyDiv容器
            fuc.FefferyDiv(
                [
                    fac.AntdSpace(
                        [
                            # 使用html.Div替代FefferyDiv以支持nClicks
                            html.Div(
                                [
                                    # 会话标题部分 - 可点击
                                    html.Div(
                                        fac.AntdText(
                                            item["title"],
                                            strong=True,
                                            ellipsis=True,
                                            style=style(padding="12px 0")
                                        ),
                                        id={"type": "ai-chat-x-session-item", "index": item["key"]},
                                        n_clicks=0,  # 使用n_clicks而不是nClicks
                                        className="session-item-clickable",  # 添加CSS类名
                                        style={
                                            "flex": "1",
                                            "cursor": "pointer",
                                            "padding": "0 12px",
                                            "minWidth": "0",
                                            "overflow": "hidden"
                                        }
                                    ),
                                    # 下拉菜单部分 - 不拦截点击事件
                                    html.Div(
                                        fac.AntdDropdown(
                                            fac.AntdButton(
                                                icon=fac.AntdIcon(
                                                    icon="antd-more",
                                                    className="global-help-text",
                                                ),
                                                type="text",
                                                size="small",
                                                style=style(color="#8c8c8c")  # 设置按钮颜色为灰色
                                            ),
                                            id={"type": "ai-chat-x-session-dropdown", "index": item["key"]},
                                            menuItems=[
                                                {
                                                    "title": "改名",
                                                    "key": "rename",
                                                    "icon": "antd-edit"  # 添加改名图标
                                                },
                                                {
                                                    "title": "删除",
                                                    "key": "delete",
                                                    "icon": "antd-delete"  # 添加删除图标
                                                }
                                            ],
                                            trigger="click",
                                        ),
                                        style={
                                            "flex": "none",
                                            "padding": "0 12px"
                                        }
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "borderRadius": "6px",
                                    "marginBottom": "4px",
                                    "cursor": "pointer",
                                    "width": "100%",
                                    "boxSizing": "border-box",
                                    "backgroundColor": "#e6f7ff" if item["key"] == selected_session_id else "#fafafa",
                                    "borderLeft": "3px solid #1890ff" if item["key"] == selected_session_id else "3px solid transparent",
                                    "transition": "all 0.3s ease"
                                }
                            )
                            for item in session_data
                        ],
                        id="ai-chat-x-session-list",
                        direction="vertical",
                        style=style(width="100%")
                    )
                ],
                style=style(height="calc(100% - 52px)", overflow="auto", padding="8px")
            )

        ],
        style={
            'position': 'relative',
            'width': '100%',
            'height': '100%',
            'padding': '16px 0'
        }
    )