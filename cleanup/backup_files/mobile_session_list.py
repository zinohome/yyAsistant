import feffery_utils_components as fuc
import feffery_antd_components as fac
import dash
from dash import html, dcc
from feffery_dash_utils.style_utils import style

# 导入conversations模型
from models.conversations import Conversations


def render_mobile_session_list(user_id=None, refresh_timestamp=None, selected_session_id=None):
    """渲染移动端聊天会话列表组件
    
    参数:
        user_id (str, optional): 用户ID，用于从数据库获取会话数据
        refresh_timestamp (float, optional): 刷新时间戳，用于触发重新渲染
        selected_session_id (str, optional): 当前选中的会话ID，用于高亮显示
    
    返回:
        Dash组件对象
    """
    
    # 默认会话数据
    default_sessions = [
        {"key": "1", "title": "新会话1", "full_title": "新会话1"},
        {"key": "2", "title": "新会话2", "full_title": "新会话2"},
        {"key": "3", "title": "新会话3", "full_title": "新会话3"}
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
                def truncate_chinese_text(text, max_length=30):
                    """截断中文字符串，如果超过最大长度则添加省略号"""
                    if len(text) > max_length:
                        return text[:max_length] + "..."
                    return text
                    
                session_data = [
                    {
                        "key": session["conv_id"], 
                        "title": truncate_chinese_text(session["conv_name"]),
                        "full_title": session["conv_name"]  # 保存完整的会话名称用于Tooltip
                    }
                    for session in db_sessions
                ]
        except Exception as e:
            # 发生错误时使用默认数据
            session_data = default_sessions
    else:
        # 使用默认数据
        session_data = default_sessions

    # 创建移动端会话列表
    return html.Div(
        [
            # 会话列表区域
            fuc.FefferyDiv(
                [
                    fac.AntdSpace(
                        [
                            # 会话项
                            html.Div(
                                [
                                    # 会话标题部分 - 可点击区域
                                    html.Div(
                                        fac.AntdText(
                                            item["title"],
                                            strong=False,  # 非粗体
                                            ellipsis=True,
                                            style=style(padding="8px 0", fontSize="14px")
                                        ),
                                        id={"type": "ai-chat-x-mobile-session-item", "index": item["key"]},
                                        n_clicks=0,
                                        className="mobile-session-item-clickable",
                                        style={
                                            "flex": "1",
                                            "cursor": "pointer",
                                            "padding": "0 8px",
                                            "minWidth": "0",
                                            "overflow": "hidden"
                                        }
                                    ),
                                    # 删除按钮部分 - 独立区域
                                    html.Div(
                                        fac.AntdButton(
                                            icon=fac.AntdIcon(
                                                icon="antd-delete",
                                                style={'fontSize': '12px', 'color': '#ff4d4f'}
                                            ),
                                            type="text",
                                            size="small",
                                            id={"type": "ai-chat-x-mobile-session-delete", "index": item["key"]},
                                            nClicks=0,
                                            style={
                                                'padding': '2px 4px',
                                                'minWidth': 'auto',
                                                'height': 'auto'
                                            }
                                        ),
                                        style={
                                            "flex": "none",
                                            "padding": "0 4px",
                                            "cursor": "pointer"
                                        }
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "borderRadius": "4px",
                                    "marginBottom": "4px",  # 紧凑间距
                                    "width": "100%",
                                    "boxSizing": "border-box",
                                    "backgroundColor": "#e6f7ff" if item["key"] == selected_session_id else "#fafafa",
                                    "borderLeft": "3px solid #1890ff" if item["key"] == selected_session_id else "3px solid transparent",
                                    "transition": "all 0.3s ease",
                                    "padding": "4px 0"
                                }
                            )
                            for item in session_data
                        ],
                        id="ai-chat-x-mobile-session-list",
                        direction="vertical",
                        style=style(width="100%")
                    )
                ],
                style=style(height="100%", overflow="auto", padding="4px")
            )
        ],
        style={
            'position': 'relative',
            'width': '100%',
            'height': '100%',
            'padding': '8px 0'
        }
    )
