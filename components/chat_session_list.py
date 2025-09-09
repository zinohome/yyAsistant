
import feffery_utils_components as fuc
import feffery_antd_components as fac
from dash import html
from feffery_dash_utils.style_utils import style


def render(sessions=None):
    """渲染聊天会话列表组件
    
    参数:
        sessions (list, optional): 会话数据列表，每个会话包含key, title字段
        search_placeholder (str, optional): 搜索框占位符文本
        collapsed (bool, optional): 是否折叠会话列表，默认为False
    
    返回:
        Dash组件对象
    """
    
    # 默认会话数据 - 只保留key和title
    default_sessions = [
        {"key": "1", "title": "如何使用Dash框架"},
        {"key": "2", "title": "数据可视化最佳实践"},
        {"key": "3", "title": "Python性能优化技巧"}
    ]
    
    # 使用传入的会话数据或默认数据
    session_data = sessions if sessions else default_sessions

    # 修复：使用html.Div作为容器包裹所有组件
    return html.Div(
        [
            
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
                            # 将AntdCard替换为FefferyDiv
                            fuc.FefferyDiv(
                                fac.AntdRow(
                                    [
                                        fac.AntdCol(
                                            fac.AntdText(
                                                item["title"],
                                                strong=True,
                                                ellipsis=True,
                                                style=style(padding="12px 0")
                                            ),
                                            flex="auto"
                                        ),
                                        fac.AntdCol(
                                            # 添加下拉菜单
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
                                            flex="none"
                                        )
                                    ],
                                    align="middle"
                                ),
                                id={"type": "ai-chat-x-session-item", "index": item["key"]},
                                style=style(
                                    # border="1px solid #f0f0f0",
                                    borderRadius="6px",
                                    padding="0 12px",
                                    marginBottom="4px",  # 将间距从8px改为4px
                                    cursor="pointer",
                                    backgroundColor="#fafafa"  # 设置浅灰色背景
                                    # **({"backgroundColor": "#e6f7ff", "borderColor": "#bae7ff"} if item["key"] == "1" else {})
                                ),
                                enableEvents=['click', 'hover'],
                                shadow="hover-shadow"
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