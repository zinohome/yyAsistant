import dash
from flask import request, Response, stream_with_context
from user_agents import parse
from flask_principal import Principal, Permission, RoleNeed, identity_loaded
from flask_login import LoginManager, UserMixin, current_user, AnonymousUserMixin
import json
import time
import threading

# 应用基础参数
from models.users import Users
from configs import BaseConfig, AuthConfig

# 导入DashProxy和SSE
from dash_extensions.enrich import DashProxy
from dash_extensions import SSE

app = DashProxy(
    __name__, 
    title=BaseConfig.app_title,
    suppress_callback_exceptions=True,
    compress=True,
    update_title=None,
    external_stylesheets=[
        '/assets/css/responsive_chat.css',
        '/assets/css/chat.css'
    ]
)
server = app.server

# 添加SSE相关导入
from dash_extensions.streaming import sse_message, sse_options
from utils.yychat_client import yychat_client
from configs.base_config import BaseConfig  # 导入配置


# 设置应用密钥
app.server.config["SECRET_KEY"] = BaseConfig.app_secret_key
app.server.config["SESSION_COOKIE_NAME"] = BaseConfig.app_session_cookie_name

# 为当前应用添加flask-login用户登录管理
login_manager = LoginManager()
login_manager.init_app(app.server)

# 为当前应用添加flask-principal权限管理
principals = Principal(app.server)


class User(UserMixin):
    """flask-login专用用户类"""

    def __init__(
        self, id: str, user_name: str, user_role: str, user_icon: str, session_token: str = None
    ) -> None:
        """初始化用户信息"""

        self.id = id
        self.user_name = user_name
        self.user_role = user_role
        self.user_icon = user_icon
        self.session_token = session_token


@login_manager.user_loader
def user_loader(user_id):
    """flask-login内部专用用户加载函数"""

    # 避免非关键请求触发常规用户加载逻辑
    if any(
        [
            request.path in ["/_reload-hash", "/_dash-layout", "/_dash-dependencies"],
            request.path.startswith("/assets/"),
            request.path.startswith("/_dash-component-suites/"),
        ]
    ):
        return AnonymousUserMixin()

    # 根据当前要加载的用户id，从数据库中获取匹配用户信息
    match_user = Users.get_user(user_id)

    # 处理未匹配到有效用户的情况
    if not match_user:
        return AnonymousUserMixin()

    # 当前用户实例化
    user = User(
        id=match_user.user_id,
        user_name=match_user.user_name,
        user_role=match_user.user_role,
        user_icon=match_user.user_icon,
        session_token=match_user.session_token,
    )

    return user


# 定义不同用户角色
user_permissions = {role: Permission(RoleNeed(role)) for role in AuthConfig.roles}


@identity_loaded.connect_via(app.server)
def on_identity_loaded(sender, identity):
    """flask-principal身份加载回调函数"""

    identity.user = current_user

    if hasattr(current_user, "user_role"):
        identity.provides.add(RoleNeed(current_user.user_role))


@app.server.before_request
def check_browser():
    """检查浏览器版本是否符合最低要求"""

    # 提取当前请求对应的浏览器信息
    user_agent = parse(str(request.user_agent))

    # 若浏览器版本信息有效
    if user_agent.browser.version != ():
        # IE相关浏览器直接拦截
        if user_agent.browser.family == "IE":
            return (
                "<div style='font-size: 16px; color: red; position: fixed; top: 40%; left: 50%; transform: translateX(-50%);'>"
                "请不要使用IE浏览器，或开启了IE内核兼容模式的其他浏览器访问本应用</div>"
            )
        # 基于BaseConfig.min_browser_versions配置，对相关浏览器最低版本进行检查
        for rule in BaseConfig.min_browser_versions:
            # 若当前请求对应的浏览器版本，低于声明的最低支持版本
            if (
                user_agent.browser.family == rule["browser"]
                and user_agent.browser.version[0] < rule["version"]
            ):
                return (
                    "<div style='font-size: 16px; color: red; position: fixed; top: 40%; left: 50%; transform: translateX(-50%);'>"
                    "您的{}浏览器版本低于本应用最低支持版本（{}），请升级浏览器后再访问</div>"
                ).format(rule["browser"], rule["version"])

        # 若开启了严格的浏览器类型限制
        if BaseConfig.strict_browser_type_check:
            # 若当前浏览器不在声明的浏览器范围内
            if user_agent.browser.family not in [
                rule["browser"] for rule in BaseConfig.min_browser_versions
            ]:
                return (
                    "<div style='font-size: 16px; color: red; position: fixed; top: 40%; left: 50%; transform: translateX(-50%);'>"
                    "当前浏览器类型不在支持的范围内，支持的浏览器类型有：{}</div>"
                ).format(
                    "、".join(
                        [rule["browser"] for rule in BaseConfig.min_browser_versions]
                    )
                )


# 添加流式响应端点
@app.server.route('/stream')
def stream():
    try:
        # 获取请求参数
        message_id = request.args.get('message_id')
        messages = request.args.get('messages')
        session_id = request.args.get('session_id')
        role = request.args.get('role', 'assistant')
        # 从请求参数中获取personality_id，如果未指定则默认为health_assistant
        personality_id = request.args.get('personality_id', 'health_assistant')
        
        # 解析消息数据
        messages_data = json.loads(messages) if messages else []
        
        @stream_with_context
        def generate():
            try:
                # 使用yychat_client进行流式聊天完成
                # 使用配置中的模型参数，并添加conversation_id和personality_id
                for chunk in yychat_client.chat_completion(
                    messages=messages_data,
                    model=BaseConfig.yychat_default_model,
                    temperature=BaseConfig.yychat_default_temperature,
                    stream=True,
                    conversation_id=session_id,
                    personality_id=personality_id,  # 使用从请求参数中获取的值
                    use_tools=BaseConfig.yychat_default_use_tools
                ):
                    if chunk:
                        # 发送数据，包含message_id以识别目标消息
                        # 确保返回的数据格式正确
                        if isinstance(chunk, dict) and 'choices' in chunk and chunk['choices']:
                            content = chunk['choices'][0].get('delta', {}).get('content', '')
                            if content:
                                yield sse_message({
                                    'message_id': message_id,
                                    'content': content,
                                    'role': role,
                                    'status': 'streaming'
                                })
                # 发送结束标志
                yield sse_message({
                    'message_id': message_id,
                    'status': 'completed',
                    'role': role
                })
            except Exception as e:
                # 发送错误信息
                yield sse_message({
                    'message_id': message_id,
                    'status': 'error',
                    'error': str(e),
                    'role': role
                })
        
        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        return Response(json.dumps({'status': 'error', 'error': str(e)}), status=500, mimetype='application/json')
