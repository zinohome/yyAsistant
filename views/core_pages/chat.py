import dash
from dash import html, dcc
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style

# 导入聊天组件
from components.chat_agent_message import render as render_agent_message
from components.chat_feature_hints import render as render_feature_hints
from components.chat_user_message import render as render_user_message
from components.chat_session_list import render as render_session_list
from components.chat_input_area import render as render_chat_input_area

# 导入配置和用户相关模块
from configs import BaseConfig, AuthConfig
from flask_login import current_user

# 令对应当前页面的回调函数子模块生效
import callbacks.core_pages_c.chat_c  # noqa: F401


def render():
    """子页面：AntDesign X风格AI聊天界面"""
    
    # 状态存储：用于管理会话列表的折叠状态
    session_collapse_store = dcc.Store(
        id='ai-chat-x-session-collapse-state',
        data=False  # 默认不折叠
    )

    # 页面标题和操作功能区域 - 用于页首
    header_content = fac.AntdRow(
        [
            fac.AntdCol(
                flex='auto',
                children=fac.AntdSpace(
                    [
                        # logo图标
                        html.Img(
                            src="/assets/imgs/logo.svg",
                            height=32,
                            style=style(display="block"),
                        ),
                        # 标题和版本号
                        fac.AntdSpace(
                            [
                                # 标题
                                fac.AntdText(
                                    BaseConfig.app_title,
                                    strong=True,
                                    style=style(fontSize=20),
                                )
                            ],
                            align="baseline",
                            size=3,
                        ),
                    ],
                    size=8
                )
            ),
            # 右侧操作功能区和用户信息
            fac.AntdCol(
                children=fac.AntdSpace(
                    [
                        # 用户头像
                        fac.AntdAvatar(
                            mode="text",
                            text="🤩",
                            size=36,
                            style=style(background="#f4f6f9"),
                        ),
                        # 用户名+角色
                        fac.AntdFlex(
                            [
                                fac.AntdText(
                                    current_user.user_name.capitalize(),
                                    strong=True,
                                )
                            ],
                            vertical=True,
                        ),
                        # 用户管理菜单
                        fac.AntdDropdown(
                            fac.AntdButton(
                                icon=fac.AntdIcon(
                                    icon="antd-more",
                                    className="global-help-text",
                                ),
                                type="text",
                            ),
                            id="ai-chat-x-user-dropdown",
                            menuItems=[
                                {
                                    "title": "个人信息",
                                    "key": "个人信息",
                                },
                                # 若当前用户角色为系统管理员
                                *(
                                    [
                                        {
                                            "title": "用户管理",
                                            "key": "用户管理",
                                        }
                                    ]
                                    if (
                                        current_user.user_role
                                        == AuthConfig.admin_role
                                    )
                                    else []
                                ),
                                {"isDivider": True},
                                {
                                    "title": "退出登录",
                                    "href": "/logout",
                                },
                            ],
                            trigger="click",
                        ),
                    ],
                    size=8
                )
            )
        ],
        gutter=16,
        align='middle',
        style=style(
            height=50,
            width="100%"
        )
    )

    # 左侧会话列表内容
    sider_content = render_session_list()

    # 右侧聊天内容区域
    content_area = fuc.FefferyDiv(
        [
            # 聊天头部信息
            fac.AntdRow(
                [
                    fac.AntdCol(
                        [
                            fac.AntdText("当前会话", strong=True),
                            fac.AntdDivider(direction="vertical", style=style(margin="0 12px")),
                            fac.AntdTag(
                                "ai-chat-x-current-session",
                                color="green",
                                icon=fac.AntdIcon(icon="antd-check-circle", style=style(fontSize="12px"))
                            )
                        ],
                        flex="auto"
                    ),
                    fac.AntdCol(
                        fac.AntdSpace(
                            [
                                fac.AntdButton(
                                    icon=fac.AntdIcon(icon="antd-star"),
                                    id="ai-chat-x-favorite-btn",
                                    type="text"
                                ),
                                fac.AntdButton(
                                    icon=fac.AntdIcon(icon="antd-plus"),
                                    id="ai-chat-x-more-btn",
                                    type="text"
                                )
                            ],
                            size="small",
                        ),
                        flex='none',
                        style=style(display='flex',alignItems='center',whiteSpace='nowrap')
                    )
                ],
                align="middle",
                className="ai-chat-x-header-row",
                style=style(padding="12px 24px", borderBottom="1px solid #f0f0f0", backgroundColor="#fff")
            ),
            
            # 聊天历史区域
            fuc.FefferyDiv(
                id="ai-chat-x-history",
                children=[
                    # 使用欢迎消息组件
                    render_agent_message(),
                    
                    # 使用功能提示卡片组件
                    #render_feature_hints(),
                    
                    # 使用用户消息组件
                    render_user_message(
                        message="如何实现一个AntDesign X风格的聊天界面？需要注意哪些设计要点？"
                    )
                ],
                style=style(
                    height="calc(100% - 110px)",
                    overflowY="auto",
                    backgroundColor="#fafafa",
                    minWidth=0  # 防止在flex容器中溢出
                )
            ),
        ],
        style=style(
            height="100%",
            display="flex",
            flexDirection="column",
            minWidth=0,  # 防止flex子元素溢出
            flexShrink=1,  # 确保在小屏幕下可以适当收缩
            width="100%"
        )
    )

    # 输入区域 - 用于页尾
    footer_content = render_chat_input_area()

    # 完整的AntdLayout布局
    return [
        # 主布局
        fac.AntdLayout(
            [
                # 页首
            fac.AntdHeader(
                header_content,
                style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'backgroundColor': '#fff',
                    'borderBottom': '1px solid #dae0ea',
                    'padding': '0 16px',
                    'zIndex': 1000,  # 确保页首在最上层
                    'minWidth': 0,  # 防止在flex容器中溢出
                    'flexShrink': 0  # 确保页首不被压缩
                },
                id="ai-chat-x-header"
            ),
            # 主体布局
            fac.AntdLayout(
                [
                    # 侧边栏
                    fac.AntdSider(
                        sider_content,
                        id="ai-chat-x-session-container",
                        collapsible=True,
                        collapsedWidth=0,  # 完全折叠
                        breakpoint="sm",  # 在小屏幕下自动折叠（<576px）
                        trigger=None,
                        style={
                            'backgroundColor': 'white',
                            'borderRight': '1px solid #f0f0f0',
                            'position': 'relative',
                            'transition': 'all 0.3s ease'
                        },
                    ),
                    # 内容区和页尾
                    fac.AntdLayout(
                        [
                            # 内容区 - 使用Div包裹来增加额外的响应式保障
                            html.Div(
                                fac.AntdContent(
                                    content_area,
                                    style={
                                        'backgroundColor': 'white',
                                        'padding': '0',
                                        'overflow': 'auto',  # 允许内容区滚动
                                        'minWidth': 0,  # 防止在flex容器中溢出
                                        'flex': 1  # 确保内容区占据剩余空间
                                    },
                                    id="ai-chat-x-right-content"
                                ),
                                style={
                                    'width': '100%',
                                    'minWidth': 0,
                                    'flex': 1,
                                    'display': 'flex',
                                    'flexDirection': 'column'
                                }
                            ),
                            # 页尾（输入区域）
                            fac.AntdFooter(
                                footer_content,
                                style={
                                    'backgroundColor': 'white',
                                    'padding': '0',
                                    'borderTop': '1px solid #f0f0f0',
                                    'flexShrink': 0  # 确保页尾不被压缩
                                },
                            ),
                        ],
                        style={
                            'display': 'flex',  # 确保内容区和页尾使用flex布局
                            'flexDirection': 'column',
                            'minWidth': 0,  # 防止在flex容器中溢出
                            'width': '100%'
                        }
                    ),
                ],
                style={
                    'height': 'calc(100vh - 50px)',
                    'display': 'flex',  # 确保侧边栏和内容区使用flex布局
                    'width': '100%'
                },
            ),
            session_collapse_store  # 状态存储组件
        ],
        style={
            'height': '100vh', 
            'backgroundColor': '#fff',
            'display': 'flex',
            'flexDirection': 'column',
            'width': '100%'
        },
        id="ai-chat-x-main-layout"
    )]