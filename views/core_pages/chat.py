import copy
import datetime
import time
from dash import html, dcc
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style

# 导入聊天组件
from components.chat_agent_message import ChatAgentMessage as render_agent_message
from components.chat_feature_hints import ChatFeatureHints as render_feature_hints
from components.chat_user_message import ChatUserMessage as render_user_message
from components.chat_session_list import render as render_session_list
from components.chat_input_area import render as render_chat_input_area
from components.ai_chat_message_history import AiChatMessageHistory
from components.my_info import render_my_info_drawer
from components.preference import render as render_preference_drawer

# 导入配置和用户相关模块
from configs import BaseConfig
from flask_login import current_user
from utils.log import log

# 令对当当前页面的回调函数子模块生效
import callbacks.core_pages_c.chat_c  # noqa: F401
from dash import Input, Output, callback, no_update

# 添加在文件顶部导入ClientsideFunction
from dash import ClientsideFunction


def _create_header_content():
    """创建页面头部内容"""
    return fac.AntdRow(
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
                                ),
                                fac.AntdText(
                                    BaseConfig.app_version,
                                    className="global-help-text",
                                    style=style(fontSize=12),
                                ),
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
                            text=current_user.user_icon if current_user.user_icon else "👨‍💼",
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
                                    "title": "我的信息",
                                    "key": "my_info",
                                    "icon": "antd-user"
                                },
                                {
                                    "title": "偏好设置",
                                    "key": "preference",
                                    "icon": "antd-setting"
                                },
                                {"isDivider": True},
                                {
                                    "title": "退出登录",
                                    "href": "/logout",
                                    "icon": "antd-logout"
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


def _create_sider_content():
    """创建侧边栏内容"""
    return html.Div(
        id='ai-chat-x-session-list-container',
        children=render_session_list(user_id=current_user.id)
    )


def _create_content_area():
    """创建右侧聊天内容区域"""
    # 聊天头部信息
    chat_header = fac.AntdRow(
        [
            fac.AntdCol(
                [
                    # 会话折叠按钮
                    fac.AntdButton(
                        id='ai-chat-x-session-collapse-trigger',
                        className="ai-chat-x-header-session-collapse-hide",
                        icon=html.Img(
                            id='ai-chat-x-session-collapse-trigger-icon',
                            src='/assets/imgs/left.svg',
                            style={
                                'width': '14px',
                                'height': '14px',
                                'margin': '0',
                                'padding': '0'
                            }
                        ),
                        shape='circle',
                        type='text',
                        style={
                            'marginRight': 8
                        }
                    ),
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
                            icon=fac.AntdIcon(icon="antd-history"),
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
                style=style(display='flex', alignItems='center', whiteSpace='nowrap')
            )
        ],
        align="middle",
        className="ai-chat-x-header-row",
        style=style(padding="12px 24px", borderBottom="1px solid #f0f0f0", backgroundColor="#fff")
    )

    # 聊天历史区域
    chat_history = fuc.FefferyDiv(
        id="ai-chat-x-history",
        children=[
            html.Div(
                id="ai-chat-x-history-content",
                children=AiChatMessageHistory(messages=None),
                **{"data-dummy": {}}  # 使用字典展开和引号确保正确的data-*格式
            )
        ],
        scrollbar='simple',
        style=style(
            height="calc(100vh - 240px)",
            maxHeight="calc(100vh - 240px)",
            overflowY="auto",
            backgroundColor="#fafafa",
            minWidth=0
        )
    )

    # 组合内容区域
    return fuc.FefferyDiv(
        [chat_header, chat_history, html.Div(id="dummy-output-for-sse", style={'display': 'none'})],
        style=style(
            height="100%",
            display="flex",
            flexDirection="column",
            minWidth=0,  # 防止flex子元素溢出
            flexShrink=1,  # 确保在小屏幕下可以适当收缩
            width="100%"
        )
    )


def _create_state_stores():
    """创建页面所需的状态存储组件"""
    # 状态存储：用于管理会话列表的折叠状态
    session_collapse_store = dcc.Store(
        id='ai-chat-x-session-collapse-state',
        data=False  # 默认不折叠
    )
    
    # 添加：会话列表刷新触发器
    session_refresh_trigger = dcc.Store(
        id='ai-chat-x-session-refresh-trigger',
        data={'timestamp': time.time()}  # 使用时间戳作为刷新标识
    )
    
    # 添加消息历史存储
    messages_store = dcc.Store(id='ai-chat-x-messages-store', data=[])
    
    # 添加当前会话ID存储
    current_session_id_store = dcc.Store(id='ai-chat-x-current-session-id', data='')
    
    # 添加流式响应状态存储
    streaming_state_store = dcc.Store(id='ai-chat-x-streaming-state', data={
        'is_streaming': False,
        'current_ai_message_id': None,
        'current_ai_content': ''
    })

    return [
        session_collapse_store,
        session_refresh_trigger,
        messages_store,
        current_session_id_store,
        streaming_state_store  # 添加这一行，包含流式状态存储组件
    ]


def render():
    """子页面：AntDesign X风格AI聊天界面"""
    # 创建各个部分的内容
    header_content = _create_header_content()
    sider_content = _create_sider_content()
    content_area = _create_content_area()
    footer_content = render_chat_input_area()
    state_stores = _create_state_stores()

    # 添加轮询组件
    streaming_poll = dcc.Interval(
        id='ai-chat-x-streaming-poll',
        interval=200,  # 每200毫秒轮询一次
        n_intervals=0
    )

    # 添加SSE客户端处理脚本
    sse_client_script = html.Script(id="sse-client-script", children="""
        // 全局变量保存当前的EventSource连接
        let currentEventSource = null;
        let connectionRetryCount = 0;
        const maxRetries = 3;
        
        // 启动SSE连接的函数
        function startSSEConnection(messageId, sessionId, messages) {
            console.log('准备启动SSE连接，消息ID:', messageId, '会话ID:', sessionId, '消息数量:', messages.length);
            
            // 关闭之前的连接（如果存在）
            if (currentEventSource) {
                console.log('关闭现有SSE连接');
                currentEventSource.close();
                currentEventSource = null;
            }
            
            // 重置重试计数
            connectionRetryCount = 0;
            
            try {
                // 创建新的SSE连接，使用正确的URL路径
                const url = `/api/stream?message_id=${encodeURIComponent(messageId)}&session_id=${encodeURIComponent(sessionId || '')}&messages=${encodeURIComponent(JSON.stringify(messages))}`;
                console.log('创建新的SSE连接到:', url);
                
                // 添加时间戳防止缓存
                const timestamp = new Date().getTime();
                const urlWithTimestamp = `${url}&t=${timestamp}`;
                console.log('添加时间戳后的URL:', urlWithTimestamp);
                
                currentEventSource = new EventSource(urlWithTimestamp);
                
                // 监听消息事件
                currentEventSource.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        console.log('收到SSE消息:', data);
                        
                        // 更新消息内容
                        updateMessageContent(data);
                    } catch (error) {
                        console.error('解析SSE消息时出错:', error, '原始消息:', event.data);
                    }
                };
                
                // 监听错误事件
                currentEventSource.onerror = function(error) {
                    console.error('SSE连接错误:', error);
                    // 自动关闭错误连接
                    if (currentEventSource) {
                        currentEventSource.close();
                        currentEventSource = null;
                    }
                    
                    // 添加重试逻辑
                    connectionRetryCount++;
                    if (connectionRetryCount <= maxRetries) {
                        console.log(`尝试重新连接(${connectionRetryCount}/${maxRetries})...`);
                        setTimeout(() => {
                            startSSEConnection(messageId, sessionId, messages);
                        }, 1000 * connectionRetryCount);
                    }
                };
                
                // 监听连接打开事件
                currentEventSource.onopen = function() {
                    console.log('SSE连接已打开');
                    connectionRetryCount = 0; // 重置重试计数
                };
                
            } catch (error) {
                console.error('创建SSE连接时出错:', error);
                
                // 添加重试逻辑
                connectionRetryCount++;
                if (connectionRetryCount <= maxRetries) {
                    console.log(`尝试重新连接(${connectionRetryCount}/${maxRetries})...`);
                    setTimeout(() => {
                        startSSEConnection(messageId, sessionId, messages);
                    }, 1000 * connectionRetryCount);
                }
            }
        }
        
        // 更新消息内容的函数
        function updateMessageContent(data) {
            console.log('进入updateMessageContent，接收到的数据:', data);
            
            // 查找消息元素
            const messageElement = document.getElementById(data.id);
            console.log('查找消息元素结果:', messageElement ? '找到' : '未找到');
            
            if (!messageElement) {
                console.warn('未找到消息元素，ID:', data.id);
                // 尝试查找所有消息容器
                const allMessages = document.querySelectorAll('[id^="ai-message-"]');
                console.log('当前页面中的AI消息元素数量:', allMessages.length);
                // 列出所有找到的消息元素ID
                allMessages.forEach(el => console.log('找到消息元素ID:', el.id));
                return;
            }
            
            console.log('消息元素HTML结构:', messageElement.innerHTML);
            
            // 使用正确的选择器查找内容元素
            // 查找消息内容的AntdText元素
            let contentElement = messageElement.querySelector('div.feffery-div span.ant-typography');
            console.log('尝试选择器1结果:', contentElement ? '找到' : '未找到');
            
            // 如果没找到，尝试更通用的选择器
            if (!contentElement) {
                // 尝试直接查找FefferyDiv中的span
                contentElement = messageElement.querySelector('div.feffery-div span');
                console.log('尝试选择器2结果:', contentElement ? '找到' : '未找到');
            }
            if (!contentElement) {
                // 尝试查找嵌套的AntdText
                contentElement = messageElement.querySelector('span.ant-typography');
                console.log('尝试选择器3结果:', contentElement ? '找到' : '未找到');
            }
            if (!contentElement) {
                // 最后的备选方案：消息元素本身
                contentElement = messageElement;
                console.log('使用备选方案，内容元素:', contentElement);
            }
            
            console.log('最终选择的内容元素:', contentElement);
            console.log('更新前内容:', contentElement.textContent);
            
            // 更新内容
            if (data.complete) {
                contentElement.textContent = data.content;
                messageElement.style.display = 'block';
                // 标记为非流式
                messageElement.setAttribute('data-streaming', 'false');
                console.log('消息完成更新，ID:', data.id, '更新后内容:', data.content);
                
                // 关闭SSE连接
                if (currentEventSource) {
                    currentEventSource.close();
                    currentEventSource = null;
                    console.log('消息完成，关闭SSE连接');
                }
            } else {
                // 累积内容
                contentElement.textContent += data.content;
                messageElement.style.display = 'block';
                console.log('累积更新消息内容，ID:', data.id, '新增内容:', data.content, '累积后内容:', contentElement.textContent);
            }
            
            // 滚动到最新消息
            messageElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
        
        // 注册到window对象，供Dash回调调用
        window.startSSEConnection = startSSEConnection;
        
        // 添加对SSE组件消息的直接监听
        document.addEventListener('DOMContentLoaded', function() {
            // 检查是否有SSE组件
            const sseComponent = document.getElementById('sse');
            if (sseComponent) {
                console.log('SSE组件已加载');
            }
        });
    """)

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
                *state_stores,  # 展开状态存储组件列表
                render_my_info_drawer(),  # 添加我的信息抽屉组件
                render_preference_drawer(),  # 添加偏好设置抽屉组件
                streaming_poll,  # 添加轮询组件到布局中
                sse_client_script  # 添加SSE客户端脚本
            ],
            style={
                'height': '100vh', 
                'backgroundColor': '#fff',
                'display': 'flex',
                'flexDirection': 'column',
                'width': '100%'
            },
            id="ai-chat-x-main-layout"
        )
    ]
