import copy
import datetime
import time
from dash import html, dcc, State, clientside_callback, ClientsideFunction
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style

# 导入聊天组件
from components.chat_agent_message import ChatAgentMessage as render_agent_message
from components.chat_feature_hints import ChatFeatureHints as render_feature_hints
from components.chat_user_message import ChatUserMessage as render_user_message
from components.chat_session_list import render as render_session_list
from components.mobile_session_list import render_mobile_session_list
from components.chat_input_area import render as render_chat_input_area
from components.ai_chat_message_history import AiChatMessageHistory
from components.my_info import render_my_info_drawer
from components.preference import render as render_preference_drawer

# 导入配置和用户相关模块
from configs import BaseConfig
from configs.voice_config import VoiceConfig
from flask_login import current_user
from utils.log import log

# 令对当当前页面的回调函数子模块生效
import callbacks.core_pages_c.chat_c  # noqa: F401
from dash import Input, Output, callback, no_update
from dash_extensions import SSE
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
                    ),
                    fac.AntdText(
                        "状态正常",
                        id="ai-chat-x-connection-status",
                        style=style(fontSize="12px", color="#52c41a", marginLeft="8px")
                    )
                ],
                flex="auto"
            ),
            fac.AntdCol(
                fac.AntdSpace(
                    [
                        fac.AntdPopover(
                            fac.AntdButton(
                                icon=fac.AntdIcon(icon="antd-history"),
                                type="text"
                            ),
                            id='ai-chat-x-mobile-session-popup',
                            content=html.Div(
                                id='ai-chat-x-mobile-session-content',
                                children=render_mobile_session_list(user_id=current_user.id),
                                style={
                                    'width': '300px',
                                    'maxHeight': '400px',
                                    'overflowY': 'auto'
                                }
                            ),
                            title='会话列表',
                            placement='bottomRight',
                            trigger='click',
                            open=False
                        ),
                        fac.AntdButton(
                            icon=fac.AntdIcon(icon="antd-plus"),
                            id="ai-chat-x-create-alternative-btn",
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
        [chat_header,
        # 添加SSE组件到布局
        SSE(
            id="chat-X-sse", 
            concat=True, 
            animate_chunk=BaseConfig.sse_animate_chunk, 
            animate_delay=BaseConfig.sse_animate_delay
        ), 
        chat_history],
        style=style(
            height="100%",
            display="flex",
            flexDirection="column",
            minWidth=0,  # 防止flex子元素溢出
            flexShrink=1,  # 确保在小屏幕下可以适当收缩
            width="100%"
        )
    )

def _create_input_content():
    """创建输入区域内容"""
    return html.Div(
        id='ai-chat-x-input-container',
        children=render_chat_input_area()
    )

def _create_state_stores():
    """创建页面所需的状态存储组件"""
    # 状态存储：用于管理会话列表的折叠状态
    session_collapse_store = dcc.Store(
        id='ai-chat-x-session-collapse-state',
        data=False  # 默认不折叠
    )
    
    # 添加消息历史存储
    messages_store = dcc.Store(id='ai-chat-x-messages-store', data=[])
    
    # 添加当前会话ID存储
    current_session_id_store = dcc.Store(id='ai-chat-x-current-session-id', data='')

    # 添加隐藏的div用于接收SSE完成事件
    sse_completed_event_receiver = html.Div(id='ai-chat-x-sse-completed-receiver', style={'display': 'none'})

    # 添加会话列表刷新触发器
    session_refresh_trigger = dcc.Store(id='ai-chat-x-session-refresh-trigger', data=None)

    # 添加：用于存储当前要改名的会话ID的隐藏组件
    current_rename_conv_id_store = dcc.Store(id='ai-chat-x-current-rename-conv-id', data=None)
    
    # 添加：复制结果的虚拟输出组件
    copy_result_store = dcc.Store(id='ai-chat-x-copy-result', data=None)
    
    # 添加语音功能相关的存储组件
    voice_recording_status = dcc.Store(id='voice-recording-status', data=False)
    voice_call_status = dcc.Store(id='voice-call-status', data=False)
    voice_websocket_connection = dcc.Store(id='voice-websocket-connection', data=None)
    voice_settings_store = dcc.Store(id='voice-settings-store', data=None)
    # 语音触发TTS开关（仅语音转写触发的那次SSE需要使能）
    voice_enable_voice_store = dcc.Store(id='voice-enable-voice', data=False)
    voice_transcription_store = dcc.Store(id='voice-transcription-store', data=None)
    voice_transcription_store_server = dcc.Store(id='voice-transcription-store-server', data=None)
    
    # 添加语音功能相关的显示组件
    voice_message_notification = html.Div(id='voice-message-notification')
    voice_error_notification = html.Div(id='voice-error-notification')
    voice_js_integration = html.Div(
        id='voice-js-integration',
        children=[
            # WebSocket管理器（最先加载）
            html.Script(src='/assets/js/voice_websocket_manager.js'),
            # 语音录制器
            html.Script(src='/assets/js/voice_recorder_enhanced.js'),
               # 语音播放器
               html.Script(src='/assets/js/voice_player_enhanced.js'),
               # 语音调试器（开发环境）
               html.Script(src='/test/test_voice_debug.js'),
            # 语音功能初始化脚本 - 动态从Python配置获取
            html.Script('''
                // 语音功能初始化
                document.addEventListener('DOMContentLoaded', function() {{
                    console.log('语音功能已加载');
                    
                    // 从Python配置动态设置全局语音配置
                    window.voiceConfig = {{
                        WS_URL: '''' + VoiceConfig.WS_URL + '''',
                        AUDIO_SAMPLE_RATE: ''' + str(VoiceConfig.AUDIO_SAMPLE_RATE) + ''',
                        AUDIO_CHANNELS: ''' + str(VoiceConfig.AUDIO_CHANNELS) + ''',
                        AUDIO_BIT_RATE: ''' + str(VoiceConfig.AUDIO_BIT_RATE) + ''',
                        VOICE_DEFAULT: '''' + VoiceConfig.VOICE_DEFAULT + '''',
                        VOLUME_DEFAULT: ''' + str(VoiceConfig.VOLUME_DEFAULT) + ''',
                        AUTO_PLAY_DEFAULT: ''' + str(VoiceConfig.AUTO_PLAY_DEFAULT).lower() + '''
                    }};
                    
                    console.log('语音配置已设置:', window.voiceConfig);
                    
                    // 初始化WebSocket管理器
                    if (window.VoiceWebSocketManager) {
                        window.voiceWebSocketManager = new window.VoiceWebSocketManager();
                        console.log('WebSocket管理器已初始化');
                    }
                    
                    // 若已存在clientId，立即同步到Dash Store，避免竞态导致client_id为None
                    try {
                        if (window.voiceWebSocketManager && window.voiceWebSocketManager.clientId && window.dash_clientside && window.dash_clientside.set_props) {
                            window.dash_clientside.set_props('voice-websocket-connection', {
                                data: { connected: true, client_id: window.voiceWebSocketManager.clientId, timestamp: Date.now() }
                            });
                            console.log('已同步现有WS client_id到Store:', window.voiceWebSocketManager.clientId);
                        }
                    } catch (e) { console.warn('初始化同步client_id失败:', e); }

                    // 监听连接成功事件，拿到client_id后写入Store
                    try {
                        if (window.voiceWebSocketManager && window.voiceWebSocketManager.registerConnectionHandler) {
                            window.voiceWebSocketManager.registerConnectionHandler(function(success){
                                if (success && window.voiceWebSocketManager.clientId && window.dash_clientside && window.dash_clientside.set_props) {
                                    window.dash_clientside.set_props('voice-websocket-connection', {
                                        data: { connected: true, client_id: window.voiceWebSocketManager.clientId, timestamp: Date.now() }
                                    });
                                    console.log('连接成功后写入client_id到Store:', window.voiceWebSocketManager.clientId);
                                    
                                    // 手动触发trigger_sse，确保语音功能正常工作
                                    setTimeout(() => {
                                        console.log('手动触发trigger_sse，确保语音功能正常');
                                        // 触发一个小的更新来重新触发trigger_sse
                                        if (window.dash_clientside && window.dash_clientside.set_props) {
                                            window.dash_clientside.set_props('voice-websocket-connection', {
                                                data: { connected: true, client_id: window.voiceWebSocketManager.clientId, timestamp: Date.now() + 1 }
                                            });
                                        }
                                    }, 100);
                                }
                            });
                        }
                    } catch (e) { console.warn('注册连接回调失败:', e); }

                    // 监听消息完成事件，触发语音播放
                    const originalDispatchEvent = window.dispatchEvent;
                    window.dispatchEvent = function(event) {{
                        if (event.type === 'messageCompleted' && event.detail) {{
                            // 触发语音播放
                            if (window.voicePlayer) {{
                                window.voicePlayer.playText(event.detail.text);
                            }}
                        }}
                        return originalDispatchEvent.call(this, event);
                    }};
                    
                    // 监听语音转录完成事件
                    document.addEventListener('voiceTranscriptionComplete', function(event) {{
                        console.log('收到语音转录完成事件:', event.detail);
                        if (event.detail && event.detail.text) {{
                            if (window.dash_clientside && window.dash_clientside.set_props) {{
                                window.dash_clientside.set_props('voice-transcription-store', {{
                                    data: {{ text: event.detail.text, ts: Date.now() }}
                                }});
                                // 同步镜像到服务端可见Store，确保触发服务端回调
                                window.dash_clientside.set_props('voice-transcription-store-server', {{
                                    data: {{ text: event.detail.text, ts: Date.now() }}
                                }});
                            }} else {{
                                console.warn('dash_clientside.set_props 不可用，无法更新 voice-transcription-store');
                            }}
                        }}
                    }});
                }});
            ''')
        ]
    )

    # 添加：会话改名对话框
    session_rename_modal = fac.AntdModal(
        [
            fac.AntdInput(
                id='ai-chat-x-session-rename-input',
                placeholder='请输入新的会话名称',
                maxLength=50,
                style={'marginBottom': '16px'}
            )
        ],
        id='ai-chat-x-session-rename-modal',
        key='ai-chat-x-session-rename-modal-key',
        title='修改会话名称',
        width=400,
        renderFooter=True,
        visible=False,  # 确保初始状态是隐藏的
        okText='确定',
        cancelText='取消'
    )


    return [
        session_collapse_store,
        messages_store,
        current_session_id_store,
        sse_completed_event_receiver,
        session_refresh_trigger,
        copy_result_store,
        current_rename_conv_id_store,
        session_rename_modal,
        
        # 语音功能相关组件
        voice_recording_status,
        voice_call_status,
        voice_websocket_connection,
        voice_settings_store,
        voice_enable_voice_store,
        voice_transcription_store,
        voice_transcription_store_server,
        voice_message_notification,
        voice_error_notification,
        voice_js_integration,
        
        html.Div(id="global-message")  # 全局消息提示组件
    ]


def render():
    """子页面：AntDesign X风格AI聊天界面"""
    # 创建各个部分的内容
    header_content = _create_header_content()
    sider_content = _create_sider_content()
    content_area = _create_content_area()
    footer_content = _create_input_content()
    state_stores = _create_state_stores()

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


# 添加语音转录镜像回调
def register_voice_transcription_mirror_callback(app):
    app.clientside_callback(
        """
        function(data) {
            console.log('镜像转录存储回调被触发:', data);
            return data; // 直接返回数据，实现镜像
        }
        """,
        Output("voice-transcription-store-server", "data"),
        Input("voice-transcription-store", "data"),
        prevent_initial_call=True
    )


def register_voice_button_callback(app):
    """注册语音按钮回调"""
    @app.callback(
        Output("voice-record-button", "n_clicks"),
        Input("voice-record-button", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_voice_button_click(n_clicks):
        """处理语音按钮点击事件"""
        if n_clicks is None:
            return no_update
        
        # 使用JavaScript处理按钮点击
        return no_update
