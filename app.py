import re
import dash
from flask import request
from dash import html, set_props, dcc
from dash_iconify import DashIconify
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash.dependencies import Input, Output, State
from flask_principal import identity_changed, AnonymousIdentity
from flask_login import current_user, logout_user, AnonymousUserMixin
from feffery_dash_utils.version_utils import (
    check_python_version,
    check_dependencies_version,
)

# 从server.py导入app
from server import app

# 导入回调注册函数
from callbacks.core_pages_c.chat_input_area_c import register_chat_input_callbacks
from views.core_pages.chat import register_voice_transcription_mirror_callback
from models.users import Users
from views import core_pages, login
from views.status_pages import _403, _404, _500
from configs import BaseConfig, RouterConfig, AuthConfig

# 导入数据库初始化
from models.init_db import db
from models.conversations import Conversations
from models.logs import LoginLogs

# 导入新的核心管理器
from core.state_manager.state_manager import StateManager, State as AppState
from core.event_manager.event_manager import EventManager, Event
from core.event_manager.event_handlers import EventHandlers
from core.websocket_manager.websocket_manager import WebSocketManager
from core.timeout_manager.timeout_manager import TimeoutManager, TimeoutType
from core.error_handler.error_handler import ErrorHandler, ErrorType, ErrorSeverity
from core.performance_monitor.performance_monitor import performance_monitor, start_performance_monitoring
from core.resource_manager.resource_manager import resource_manager, start_resource_cleanup
from core.health_checker.health_checker import health_checker, add_health_check, start_health_checking
# from config.config import config  # 暂时禁用，配置整理放到后面专题

# 检查Python版本
check_python_version(min_version="3.8", max_version="3.13")
# 检查关键依赖库版本
check_dependencies_version(
    rules=[
        {"name": "dash", "specifier": ">=3.1.1,<4.0.0"},
        {"name": "feffery_antd_components", "specifier": ">=0.4.0,<0.5.0"},
        {"name": "feffery_utils_components", "specifier": ">=0.3.2,<0.4.0"},
        {"name": "feffery_dash_utils", "specifier": ">=0.2.6"},
    ]
)

# ============================================================================
# 全局核心管理器实例
# ============================================================================

# 创建全局管理器实例
state_manager = StateManager()
event_manager = EventManager()
websocket_manager = WebSocketManager()
timeout_manager = TimeoutManager()
error_handler = ErrorHandler()

# 创建事件处理器
event_handlers = EventHandlers(state_manager, event_manager)

# 将管理器实例添加到app的全局属性中，以便在回调中访问
app.state_manager = state_manager
app.event_manager = event_manager
app.websocket_manager = websocket_manager
app.timeout_manager = timeout_manager
app.error_handler = error_handler
app.event_handlers = event_handlers
app.performance_monitor = performance_monitor
app.resource_manager = resource_manager
app.health_checker = health_checker

print("✅ 核心管理器已初始化")
print(f"   - 状态管理器: {state_manager.get_state().value}")
print(f"   - 事件管理器: {len(event_manager.get_registered_handlers())} 个处理器")
print(f"   - WebSocket管理器: {websocket_manager.get_connection_state().value}")
print(f"   - 超时管理器: {len(timeout_manager.get_manager_info())} 个配置")
print(f"   - 错误处理器: {len(error_handler.get_error_stats())} 个错误类型")
print(f"   - 性能监控器: 已启动")
print(f"   - 资源管理器: 已启动")
print(f"   - 健康检查器: 已启动")

# 注册聊天输入区域回调
register_chat_input_callbacks(app)  # 临时注释，使用新的统一回调
register_voice_transcription_mirror_callback(app)

# 注册语音按钮回调
from views.core_pages.chat import register_voice_button_callback
register_voice_button_callback(app)

# ============================================================================
# 统一按钮状态管理 - Clientside Callbacks (官方推荐的dcc.Store架构)
# ============================================================================

# 回调 1: 状态更新回调 (多个Input → unified-button-state Store)
app.clientside_callback(
    """
        function(sse_event, recording_event, send_clicks, input_value, current_state) {
        window.controlledLog?.log('🔍 状态管理callback被触发:', {sse_event, recording_event, input_value, current_state});
        const ctx = dash_clientside.callback_context;
        if (!ctx.triggered || !Array.isArray(ctx.triggered) || ctx.triggered.length === 0) {
            window.controlledLog?.log('🔍 没有触发事件，返回no_update');
            return window.dash_clientside.no_update;
        }
        
        // 显示当前状态信息
        if (current_state && window.unifiedButtonStateManager) {
            const stateInfo = window.unifiedButtonStateManager.getStateInfo(current_state.state, current_state.scenario);
            const buttonDetails = window.unifiedButtonStateManager.getButtonStateDetails(current_state.state);
            window.controlledLog?.log('🔍 当前状态:', stateInfo);
            window.controlledLog?.log('🔍 按钮状态详情:', {
                textButton: `${buttonDetails.textButton.status} (loading: ${buttonDetails.textButton.loading}, disabled: ${buttonDetails.textButton.disabled})`,
                recordButton: `${buttonDetails.recordButton.status} (disabled: ${buttonDetails.recordButton.disabled})`,
                callButton: `${buttonDetails.callButton.status} (disabled: ${buttonDetails.callButton.disabled})`
            });
        }
        
        const manager = window.unifiedButtonStateManager;
        if (!manager) {
            console.warn('UnifiedButtonStateManager not initialized');
            return window.dash_clientside.no_update;
        }
        
        const triggered = ctx.triggered[0];
        const triggeredId = triggered.prop_id.split('.')[0];
        const now = Date.now();
        let newState = current_state || {state: 'idle', timestamp: 0};
        
        // 处理文本按钮点击（立即进入text_processing，避免在SSE开始前按钮保持可用）
        if (triggeredId === 'ai-chat-x-send-btn') {
            window.controlledLog?.log('Text button clicked → force state to text_processing');
            newState = {
                state: 'text_processing',
                scenario: 'text_chat',
                timestamp: now,
                metadata: {
                    from_scenario: 'text',
                    auto_play: manager.getAutoPlaySetting()
                }
            };
            window.controlledLog?.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
        }
        // 处理SSE事件（此回调仅用于完成/镜像，不再用来切入text_processing，避免TTS完成后被旧事件拉回S1）
        else if (triggeredId === 'ai-chat-x-sse-completed-receiver' && sse_event) {
            window.controlledLog?.log('🔍 收到SSE事件（镜像/完成），不改变当前状态');
            return window.dash_clientside.no_update;
        }
        // SSE完成 - 不更新状态，继续等待TTS完成
        else if (triggeredId === 'ai-chat-x-sse-completed-receiver') {
            window.controlledLog?.log('🔍 SSE完成事件被忽略，等待TTS完成');
            return window.dash_clientside.no_update;
        }
        // 外部事件 (录音/播放)
        else if (triggeredId === 'button-event-trigger' && recording_event) {
            const type = recording_event.type;
            
            if (type === 'text_button_clicked') {
                window.controlledLog?.log('Text button clicked via event trigger, setting state to text_processing');
                newState = {
                    state: 'text_processing',
                    scenario: 'text_chat',
                    timestamp: now,
                    metadata: recording_event.metadata || {from_scenario: 'text', auto_play: true}
                };
                window.controlledLog?.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'voice_transcription_complete') {
                window.controlledLog?.log('Voice transcription complete, setting state to text_processing');
                newState = {
                    state: 'text_processing',
                    scenario: 'voice_recording',
                    timestamp: now,
                    metadata: {from_scenario: 'voice', auto_play: true}
                };
                window.controlledLog?.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'stt_failed') {
                window.controlledLog?.log('STT failed, returning to idle state');
                newState = {
                    state: 'idle',
                    scenario: null,
                    timestamp: now,
                    metadata: {}
                };
                window.controlledLog?.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            // 语音通话事件
            else if (type === 'voice_call_start') {
                window.controlledLog?.log('Voice call start triggered, starting voice call...');
                // 发送语音通话启动命令到后端
                if (window.voiceWebSocketManager && window.voiceWebSocketManager.sendMessage) {
                    window.voiceWebSocketManager.sendMessage({
                        type: 'voice_command',
                        command: 'start_voice_call',
                        timestamp: Date.now()
                    });
                }
                // 更新状态为场景三：语音通话的S1状态
                newState = {
                    state: 'calling',
                    scenario: 'voice_call',
                    timestamp: Date.now(),
                    metadata: {
                        message: '语音通话已启动'
                    }
                };
                window.controlledLog?.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'voice_call_stop') {
                window.controlledLog?.log('Voice call stop triggered, stopping voice call...');
                // 发送语音通话停止命令到后端
                if (window.voiceWebSocketManager && window.voiceWebSocketManager.sendMessage) {
                    window.voiceWebSocketManager.sendMessage({
                        type: 'voice_command',
                        command: 'stop_voice_call',
                        timestamp: Date.now()
                    });
                }
                // 更新状态为场景三：语音通话的S3状态（回到空闲）
                newState = {
                    state: 'idle',
                    scenario: 'voice_call',
                    timestamp: Date.now(),
                    metadata: {
                        message: '语音通话已停止'
                    }
                };
                window.controlledLog?.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'recording_start') {
                newState = {
                    state: 'recording',
                    scenario: 'voice_recording',
                    timestamp: now,
                    metadata: {from_scenario: 'voice'}
                };
                window.controlledLog?.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'recording_stop') {
                newState = {
                    state: 'voice_processing',
                    scenario: 'voice_recording',
                    timestamp: now,
                    metadata: {from_scenario: 'voice', auto_play: true}
                };
                window.controlledLog?.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'tts_complete' || type === 'tts_stop') {
                newState = {state: 'idle', scenario: null, timestamp: now, metadata: {}};
                window.controlledLog?.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'tts_start') {
                // TTS开始播放，保持当前状态不变
                window.controlledLog?.log('🔍 TTS开始播放，保持当前状态');
                return window.dash_clientside.no_update;
            }
        }
        
        window.controlledLog?.log('State update:', newState);
        return newState;
    }
    """,
    Output('unified-button-state', 'data'),
    [
        Input('ai-chat-x-sse-completed-receiver', 'data-completion-event'),
        Input('button-event-trigger', 'data'),
        Input('ai-chat-x-send-btn', 'n_clicks')
    ],
    [
        State('ai-chat-x-input', 'value'),
        State('unified-button-state', 'data')
    ],
    prevent_initial_call=True
)

# 回调 2: UI更新回调 (unified-button-state Store → 按钮样式)
app.clientside_callback(
    """
        function(state_data) {
            if (!state_data || !window.unifiedButtonStateManager) {
                const noupdate = window.dash_clientside.no_update;
                return [noupdate, noupdate, noupdate, noupdate, noupdate, noupdate, noupdate];
            }
            
            const state = state_data.state || 'idle';
            const scenario = state_data.scenario || null;
            const styles = window.unifiedButtonStateManager.getStateStyles(state);
            
            // 显示状态信息
            const stateInfo = window.unifiedButtonStateManager.getStateInfo(state, scenario);
            window.controlledLog?.log('🔍 UI更新:', stateInfo);
            
            
            // 合并样式：保留原有大小/圆角/字体等，完全由状态管理器控制颜色
            function mergeButtonStyle(elId, override) {
                const el = document.getElementById(elId);
                const base = {};
                if (el && el.style) {
                    // 只保留大小、圆角、字体等非颜色属性
                    const computed = window.getComputedStyle(el);
                    ['width','height','padding','borderRadius','fontSize','lineHeight','boxShadow'].forEach(k => {
                        if (computed && computed[k] && computed[k] !== '') {
                            base[k] = computed[k];
                        }
                    });
                }
                // 完全应用状态管理器的颜色样式，包括颜色属性
                const result = Object.assign({}, base, override || {});
                // 确保颜色属性被正确应用
                if (override && override.backgroundColor) {
                    result.backgroundColor = override.backgroundColor;
                }
                if (override && override.borderColor) {
                    result.borderColor = override.borderColor;
                }
                if (override && override.color) {
                    result.color = override.color;
                }
                return result;
            }
            
            // 文本按钮图标映射
            let textButtonIcon = 'material-symbols:send'; // 默认发送图标
            if (state === 'text_processing' || state === 'text_sse') {
                textButtonIcon = 'eos-icons:loading'; // 处理中显示loading旋转图标
            }
            
            // 录音按钮图标映射
            let recordButtonIcon = 'proicons:microphone'; // 默认麦克风
            if (state === 'recording') {
                recordButtonIcon = 'material-symbols:stop'; // 录音中显示停止
            } else if (state === 'processing' || state === 'voice_processing' || state === 'voice_stt' || state === 'voice_sse') {
                recordButtonIcon = 'eos-icons:loading'; // 处理中显示loading
            } else if (state === 'voice_tts') {
                recordButtonIcon = 'material-symbols:play-arrow'; // TTS播放中显示播放
            }
            
            // 通话按钮图标映射
            let callButtonIcon = 'bi:telephone'; // 默认通话图标（话筒方向向左下角）
            if (state === 'voice_call' || state === 'calling') {
                callButtonIcon = 'material-symbols:call-end'; // 通话中显示挂断
            }
            
            const result = [
                mergeButtonStyle('ai-chat-x-send-btn', styles.textButton),
                styles.textLoading || false,
                styles.textDisabled || false,
                textButtonIcon, // 文本按钮图标
                mergeButtonStyle('voice-record-button', styles.recordButton),
                recordButtonIcon, // 录音按钮图标
                styles.recordDisabled || false,
                mergeButtonStyle('voice-call-btn', styles.callButton),
                callButtonIcon, // 通话按钮图标
                styles.callDisabled || false
            ];
            
            return result;
        }
    """,
    [
        Output('ai-chat-x-send-btn', 'style', allow_duplicate=True),
        Output('ai-chat-x-send-btn', 'loading', allow_duplicate=True),
        Output('ai-chat-x-send-btn', 'disabled', allow_duplicate=True),
        Output('ai-chat-x-send-icon-store', 'data', allow_duplicate=True),
        Output('voice-record-button', 'style', allow_duplicate=True),
        Output('voice-record-icon-store', 'data', allow_duplicate=True),
        Output('voice-record-button', 'disabled', allow_duplicate=True),
        Output('voice-call-btn', 'style', allow_duplicate=True),
        Output('voice-call-icon-store', 'data', allow_duplicate=True),
        Output('voice-call-btn', 'disabled', allow_duplicate=True)
    ],
    Input('unified-button-state', 'data'),
    prevent_initial_call=True
)

# 回调 3: 文本按钮图标更新回调
@app.callback(
    Output('ai-chat-x-send-btn', 'icon', allow_duplicate=True),
    Input('ai-chat-x-send-icon-store', 'data'),
    prevent_initial_call=True
)
def update_text_button_icon(icon_data):
    """更新文本按钮图标"""
    if not icon_data:
        return DashIconify(icon="material-symbols:send", width=20, height=20)
    
    return DashIconify(icon=icon_data, width=20, height=20)

# 回调 4: 录音按钮图标更新回调
@app.callback(
    Output('voice-record-button', 'icon', allow_duplicate=True),
    Input('voice-record-icon-store', 'data'),
    prevent_initial_call=True
)
def update_record_button_icon(icon_data):
    """更新录音按钮图标"""
    if not icon_data:
        return DashIconify(icon="proicons:microphone", width=20, height=20)
    
    return DashIconify(icon=icon_data, width=20, height=20)

# 回调 5: 通话按钮图标更新回调
@app.callback(
    Output('voice-call-btn', 'icon', allow_duplicate=True),
    Input('voice-call-icon-store', 'data'),
    prevent_initial_call=True
)
def update_call_button_icon(icon_data):
    """更新通话按钮图标"""
    if not icon_data:
        return DashIconify(icon="bi:telephone", rotate=2, width=20, height=20)
    
    # 如果是bi:telephone图标，需要旋转180度
    if icon_data == "bi:telephone":
        return DashIconify(icon=icon_data, rotate=2, width=20, height=20)
    
    return DashIconify(icon=icon_data, width=20, height=20)

# 回调 4: 输入验证回调 (显示警告消息) - 暂时禁用以避免与重新生成功能冲突
# app.clientside_callback(
#     """
#     function(n_clicks, input_value) {
#         if (!n_clicks || !window.unifiedButtonStateManager) {
#             return window.dash_clientside.no_update;
#         }
#         
#         if (!window.unifiedButtonStateManager.checkInputContent()) {
#             window.controlledLog?.log('Empty input warning');
#             // 返回Ant Design Message格式
#             return {
#                 'content': '请输入消息内容',
#                 'type': 'warning',
#                 'duration': 2
#             };
#         }
#         
#         return window.dash_clientside.no_update;
#     }
#     """,
#     Output('global-message', 'children'),
#     Input('ai-chat-x-send-btn', 'n_clicks'),
#     State('ai-chat-x-input', 'value'),
#     prevent_initial_call=True
# )

# 导入语音回调函数（在app初始化后导入）
import callbacks.voice_chat_c  # 临时注释，使用新的统一回调
import callbacks.realtime_voice_c  # 导入实时语音对话回调
import callbacks.voice_call_display_c  # 导入语音实时对话文本显示回调

# 注册完整的统一回调（处理所有聊天功能）
#from callbacks.core_pages_c.core_chat_callback import register_core_chat_callback
#register_core_chat_callback(app)

# 修改app.layout，添加SSE组件到布局中
app.layout = lambda: fuc.FefferyTopProgress(
    [
        # 全局消息提示
        fac.Fragment(id="global-message"),
        # 全局重定向
        fac.Fragment(id="global-redirect"),
        # 全局页面刷新
        fuc.FefferyReload(id="global-reload"),
        # 全局文件下载
        dcc.Download(id="global-download"),
        *(
            [
                # 重复登录辅助检查轮询
                dcc.Interval(
                    id="duplicate-login-check-interval",
                    interval=BaseConfig.duplicate_login_check_interval * 1000,
                )
            ]
            # 若开启了重复登录辅助检查
            if BaseConfig.enable_duplicate_login_check
            else []
        ),
        # 根节点url监听
        fuc.FefferyLocation(id="root-url"),
        # 应用根容器
        html.Div(
            id="root-container",
        ),
        # 基础配置文件（所有页面都需要）
        html.Script(src="/assets/js/config.js"),
        # 应用配置运行时
        html.Script(src="/assets/js/app_config_runtime.js"),
        # 微信浏览器兼容性处理
        html.Script(src="/assets/js/wechat_compatibility.js"),
        # 微信浏览器调试工具
        html.Script(src="/assets/js/wechat_debug.js"),
        # 移动端视口处理
        html.Script(src="/assets/js/mobile_viewport_handler.js"),
        # 聊天页面专用JS加载器（条件加载）
        html.Script(src="/assets/js/chat_page_loader.js"),
    ],
    id="layout-top-progress",
    minimum=0.33,
    color="#1677ff",
    manual=True,
)

# 添加移动端视口配置
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="format-detection" content="telephone=no">
        <style>
            /* 移动端视口修复 */
            html, body {
                height: 100%;
                overflow-x: hidden;
                -webkit-overflow-scrolling: touch;
            }
            
            /* 防止iOS Safari缩放 */
            input, textarea, select {
                font-size: 16px !important;
            }
            
            /* 修复iOS Safari地址栏问题 */
            .mobile-viewport-fix {
                height: 100vh;
                height: -webkit-fill-available;
            }
            
            /* 登录页面移动端优化 */
            @media screen and (max-width: 768px) {
                .login-left-side {
                    display: none !important;
                }
                .login-right-side {
                    padding: 20px !important;
                }
                .ant-form {
                    width: 100% !important;
                    max-width: 400px !important;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


def handle_root_router_error(e):
    """处理根节点路由错误"""

    set_props(
        "root-container",
        {
            "children": _500.render(e),
        },
    )


@app.callback(
    Output("root-container", "children"),
    Input("root-url", "pathname"),
    State("root-url", "trigger"),
    prevent_initial_call=True,
    on_error=handle_root_router_error,
    running=[[Output("layout-top-progress", "spinning"), True, False]],
)
def root_router(pathname, trigger):
    """根节点路由控制"""

    # 在动态路由切换时阻止根节点路由更新
    if trigger != "load":
        return dash.no_update

    # 无需校验登录状态的公共页面
    if pathname in RouterConfig.public_pathnames:
        if pathname == "/403-demo":
            return _403.render()

        elif pathname == "/404-demo":
            return _404.render()

        elif pathname == "/500-demo":
            return _500.render()

        elif pathname == "/login":
            return login.render()

        elif pathname == "/logout":
            # 当前用户登出
            logout_user()

            # 重置当前用户身份
            identity_changed.send(
                app.server,
                identity=AnonymousIdentity(),
            )

            # 重定向至登录页面
            set_props(
                "global-redirect",
                {
                    "children": dcc.Location(
                        pathname="/login", id="global-redirect-target"
                    )
                },
            )
            return dash.no_update

    # 登录状态校验：若当前用户未登录
    if not current_user.is_authenticated:
        # 重定向至登录页面
        set_props(
            "global-redirect",
            {"children": dcc.Location(pathname="/login", id="global-redirect-target")},
        )

        return dash.no_update

    # 检查当前访问目标pathname是否为有效页面
    if (
        # 硬编码页面地址
        pathname in RouterConfig.valid_pathnames.keys()
        or
        # 通配模式页面地址
        any(
            pattern.match(pathname)
            for pattern in RouterConfig.valid_pathnames.keys()
            if isinstance(pattern, re.Pattern)
        )
    ):
        # 校验当前用户是否具有针对当前访问目标页面的权限
        current_user_access_rule = AuthConfig.pathname_access_rules.get(
            current_user.user_role
        )

        # 若当前用户页面权限规则类型为'include'
        if current_user_access_rule["type"] == "include":
            # 若当前用户不具有针对当前访问目标页面的权限
            if pathname not in current_user_access_rule["keys"]:
                # 首页不受权限控制影响
                if pathname not in [
                    "/",
                    RouterConfig.index_pathname,
                ]:
                    # 重定向至403页面
                    set_props(
                        "global-redirect",
                        {
                            "children": dcc.Location(
                                pathname="/403-demo", id="global-redirect-target"
                            )
                        },
                    )

                    return dash.no_update

        # 若当前用户页面权限规则类型为'exclude'
        elif current_user_access_rule["type"] == "exclude":
            # 若当前用户不具有针对当前访问目标页面的权限
            if pathname in current_user_access_rule["keys"]:
                # 重定向至403页面
                set_props(
                    "global-redirect",
                    {
                        "children": dcc.Location(
                            pathname="/403-demo", id="global-redirect-target"
                        )
                    },
                )

                return dash.no_update

        # 普通用户页面访问限制：普通用户只能访问配置中允许的页面
        if current_user.user_role == AuthConfig.normal_role:
            # 检查当前访问的页面是否在允许列表中
            if pathname not in AuthConfig.normal_user_allowed_pathnames:
                # 重定向到配置的目标页面
                set_props(
                    "global-redirect",
                    {
                        "children": dcc.Location(
                            pathname=AuthConfig.normal_user_redirect_pathname,
                            id="global-redirect-target"
                        )
                    },
                )
                return dash.no_update

        # 处理核心功能页面渲染
        # 返回带水印的页面内容
        if BaseConfig.enable_fullscreen_watermark:
            return fac.AntdWatermark(
                core_pages.render(
                    current_user_access_rule=current_user_access_rule,
                    current_pathname=pathname,
                ),
                # 处理水印内容生成
                content=BaseConfig.fullscreen_watermark_generator(current_user),
            )

        # 返回不带水印的页面内容
        return core_pages.render(
            current_user_access_rule=current_user_access_rule, current_pathname=pathname
        )

    # 返回404状态页面
    return _404.render()


@app.callback(
    Input("duplicate-login-check-interval", "n_intervals"),
    State("root-url", "pathname"),
)
def duplicate_login_check(n_intervals, pathname):
    """重复登录辅助轮询检查"""

    # 若当前页面属于无需校验登录状态的公共页面，结束检查
    if pathname in RouterConfig.public_pathnames:
        return

    # 若当前用户身份未知
    if isinstance(current_user, AnonymousUserMixin):
        # 重定向到登出页
        set_props(
            "global-redirect",
            {"children": dcc.Location(pathname="/logout", id="global-redirect-target")},
        )

    # 若当前用户已登录
    elif current_user.is_authenticated:
        match_user = Users.get_user(current_user.id)
        # 若当前回调请求携带cookies中的session_token，当前用户数据库中的最新session_token不一致
        if match_user.session_token != request.cookies.get(
            BaseConfig.session_token_cookie_name
        ):
            # 重定向到登出页
            set_props(
                "global-redirect",
                {
                    "children": dcc.Location(
                        pathname="/logout", id="global-redirect-target"
                    )
                },
            )


if __name__ == "__main__":
    # 启动性能监控
    start_performance_monitoring(interval=10.0)
    
    # 启动资源清理
    start_resource_cleanup()
    
    # 添加健康检查项
    add_health_check('state_manager', lambda: state_manager.get_state() is not None)
    add_health_check('event_manager', lambda: len(event_manager.get_registered_handlers()) > 0)
    add_health_check('websocket_manager', lambda: websocket_manager.get_connection_state() is not None)
    add_health_check('timeout_manager', lambda: len(timeout_manager.get_manager_info()) > 0)
    add_health_check('error_handler', lambda: len(error_handler.get_error_stats()) >= 0)
    
    # 启动健康检查
    start_health_checking(interval=30.0)
    
    print("🚀 所有系统已启动")
    print("   - 性能监控: 10秒间隔")
    print("   - 资源清理: 5分钟间隔")
    print("   - 健康检查: 30秒间隔")
    print("   - 自适应UI系统: 已启动")
    
    # 非正式环境下开发调试预览用
    #app.run(debug=True, host='0.0.0.0', port=8050)
    app.run(host='0.0.0.0', port=8050)
    # 生产环境推荐使用gunicorn启动
    #gunicorn -w 4 -b 0.0.0.0:8050 app:server

# 注册完整的统一回调
from callbacks.core_pages_c.core_chat_callback import register_core_chat_callback
register_core_chat_callback(app)

# 数据库初始化 - 确保表存在
try:
    with db.connection_context():
        # 创建所有必要的表
        db.create_tables([Users, Conversations, LoginLogs], safe=True)
        print("✅ 数据库表初始化完成")
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()
