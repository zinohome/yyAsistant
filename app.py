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
        console.log('🔍 状态管理callback被触发:', {sse_event, recording_event, input_value, current_state});
        const ctx = dash_clientside.callback_context;
        if (!ctx.triggered || !Array.isArray(ctx.triggered) || ctx.triggered.length === 0) {
            console.log('🔍 没有触发事件，返回no_update');
            return window.dash_clientside.no_update;
        }
        
        // 显示当前状态信息
        if (current_state && window.unifiedButtonStateManager) {
            const stateInfo = window.unifiedButtonStateManager.getStateInfo(current_state.state, current_state.scenario);
            const buttonDetails = window.unifiedButtonStateManager.getButtonStateDetails(current_state.state);
            console.log('🔍 当前状态:', stateInfo);
            console.log('🔍 按钮状态详情:', {
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
            console.log('Text button clicked → force state to text_processing');
            newState = {
                state: 'text_processing',
                scenario: 'text_chat',
                timestamp: now,
                metadata: {
                    from_scenario: 'text',
                    auto_play: manager.getAutoPlaySetting()
                }
            };
            console.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
        }
        // 处理SSE事件（此回调仅用于完成/镜像，不再用来切入text_processing，避免TTS完成后被旧事件拉回S1）
        else if (triggeredId === 'ai-chat-x-sse-completed-receiver' && sse_event) {
            console.log('🔍 收到SSE事件（镜像/完成），不改变当前状态');
            return window.dash_clientside.no_update;
        }
        // SSE完成 - 不更新状态，继续等待TTS完成
        else if (triggeredId === 'ai-chat-x-sse-completed-receiver') {
            console.log('🔍 SSE完成事件被忽略，等待TTS完成');
            return window.dash_clientside.no_update;
        }
        // 外部事件 (录音/播放)
        else if (triggeredId === 'button-event-trigger' && recording_event) {
            const type = recording_event.type;
            
            if (type === 'text_button_clicked') {
                console.log('Text button clicked via event trigger, setting state to text_processing');
                newState = {
                    state: 'text_processing',
                    scenario: 'text_chat',
                    timestamp: now,
                    metadata: recording_event.metadata || {from_scenario: 'text', auto_play: true}
                };
                console.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'voice_transcription_complete') {
                console.log('Voice transcription complete, setting state to text_processing');
                newState = {
                    state: 'text_processing',
                    scenario: 'voice_recording',
                    timestamp: now,
                    metadata: {from_scenario: 'voice', auto_play: true}
                };
                console.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'stt_failed') {
                console.log('STT failed, returning to idle state');
                newState = {
                    state: 'idle',
                    scenario: null,
                    timestamp: now,
                    metadata: {}
                };
                console.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            // 实时语音对话事件
            else if (type === 'realtime_voice_start') {
                console.log('Realtime voice start triggered, starting realtime dialogue...');
                // 触发前端JavaScript启动实时语音对话
                if (window.realtimeStateManager) {
                    window.realtimeStateManager.startRealtimeDialogue();
                } else {
                    console.warn('RealtimeStateManager not available');
                }
                // 更新状态为场景三：语音实时对话的S1状态
                const newState = {
                    state: 'calling',
                    scenario: 'voice_call',
                    timestamp: Date.now(),
                    metadata: {
                        message: '实时语音对话已启动',
                        button_states: {
                            textButton: 'disabled',
                            recordButton: 'disabled', 
                            callButton: 'calling'
                        }
                    }
                };
                console.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
                return newState;
            }
            else if (type === 'realtime_voice_stop') {
                console.log('Realtime voice stop triggered, stopping realtime dialogue...');
                // 触发前端JavaScript停止实时语音对话
                if (window.realtimeStateManager) {
                    window.realtimeStateManager.stopRealtimeDialogue();
                } else {
                    console.warn('RealtimeStateManager not available');
                }
                // 更新状态为场景三：语音实时对话的S3状态（回到空闲）
                const newState = {
                    state: 'idle',
                    scenario: 'voice_call',
                    timestamp: Date.now(),
                    metadata: {
                        message: '实时语音对话已停止',
                        button_states: {
                            textButton: 'enabled',
                            recordButton: 'enabled',
                            callButton: 'enabled'
                        }
                    }
                };
                console.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
                return newState;
            }
            else if (type === 'recording_start') {
                newState = {
                    state: 'recording',
                    scenario: 'voice_recording',
                    timestamp: now,
                    metadata: {from_scenario: 'voice'}
                };
                console.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'recording_stop') {
                newState = {
                    state: 'voice_processing',
                    scenario: 'voice_recording',
                    timestamp: now,
                    metadata: {from_scenario: 'voice', auto_play: true}
                };
                console.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'tts_complete' || type === 'tts_stop') {
                newState = {state: 'idle', scenario: null, timestamp: now, metadata: {}};
                console.log('🔍 状态转换:', window.unifiedButtonStateManager.getStateInfo(newState.state, newState.scenario));
            }
            else if (type === 'tts_start') {
                // TTS开始播放，保持当前状态不变
                console.log('🔍 TTS开始播放，保持当前状态');
                return window.dash_clientside.no_update;
            }
        }
        
        console.log('State update:', newState);
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
            console.log('🔍 UI更新:', stateInfo);
            
            // 合并样式：仅覆盖颜色，保留原有大小/圆角/字体等
            function mergeButtonStyle(elId, override) {
                const el = document.getElementById(elId);
                const base = {};
                if (el && el.style) {
                    // 读取会影响外观的一些关键属性，保留它们
                    const computed = window.getComputedStyle(el);
                    ['width','height','padding','borderRadius','fontSize','lineHeight','boxShadow'].forEach(k => {
                        if (computed && computed[k] && computed[k] !== '') {
                            base[k] = computed[k];
                        }
                    });
                }
                // 仅覆盖背景色和边框色
                return Object.assign({}, base, override || {});
            }
            
            const result = [
                mergeButtonStyle('ai-chat-x-send-btn', styles.textButton),
                styles.textLoading || false,
                styles.textDisabled || false,
                mergeButtonStyle('voice-record-button', styles.recordButton),
                styles.recordDisabled || false,
                mergeButtonStyle('voice-call-btn', styles.callButton),
                styles.callDisabled || false
            ];
            
            console.log('🔍 返回的样式数组:', result);
            return result;
        }
    """,
    [
        Output('ai-chat-x-send-btn', 'style', allow_duplicate=True),
        Output('ai-chat-x-send-btn', 'loading', allow_duplicate=True),
        Output('ai-chat-x-send-btn', 'disabled', allow_duplicate=True),
        Output('voice-record-button', 'style', allow_duplicate=True),
        Output('voice-record-button', 'disabled', allow_duplicate=True),
        Output('voice-call-btn', 'style', allow_duplicate=True),
        Output('voice-call-btn', 'disabled', allow_duplicate=True)
    ],
    Input('unified-button-state', 'data'),
    prevent_initial_call=True
)

# 回调 3: 输入验证回调 (显示警告消息)
app.clientside_callback(
    """
    function(n_clicks, input_value) {
        if (!n_clicks || !window.unifiedButtonStateManager) {
            return window.dash_clientside.no_update;
        }
        
        if (!window.unifiedButtonStateManager.checkInputContent()) {
            console.log('Empty input warning');
            // 返回Ant Design Message格式
            return {
                'content': '请输入消息内容',
                'type': 'warning',
                'duration': 2
            };
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('global-message', 'children'),
    Input('ai-chat-x-send-btn', 'n_clicks'),
    State('ai-chat-x-input', 'value'),
    prevent_initial_call=True
)

# 导入语音回调函数（在app初始化后导入）
import callbacks.voice_chat_c  # 临时注释，使用新的统一回调
import callbacks.realtime_voice_c  # 导入实时语音对话回调

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
        # 统一按钮状态管理器脚本
        html.Script(src="/assets/js/unified_button_state_manager.js"),
        # 语音状态管理器脚本
        html.Script(src="/assets/js/voice_state_manager.js"),
    ],
    id="layout-top-progress",
    minimum=0.33,
    color="#1677ff",
    manual=True,
)


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
    # 非正式环境下开发调试预览用
    app.run(debug=True, host='0.0.0.0', port=8050)
    #app.run(host='0.0.0.0', port=8050)
    # 生产环境推荐使用gunicorn启动
    #gunicorn -w 4 -b 0.0.0.0:8050 app:server

# 注册完整的统一回调
from callbacks.core_pages_c.core_chat_callback import register_core_chat_callback
register_core_chat_callback(app)
