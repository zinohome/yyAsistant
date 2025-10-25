import dash
from flask import request, Response, stream_with_context, jsonify
from user_agents import parse
from flask_principal import Principal, Permission, RoleNeed, identity_loaded
from flask_login import LoginManager, UserMixin, current_user, AnonymousUserMixin
import json
import time
import threading

from utils.log import log

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
        '/assets/css/chat.css',
        '/assets/css/mobile_viewport.css'
    ],
    # 添加静态文件配置，避免dash_table字体文件404错误
    serve_locally=True
)
server = app.server

# 添加静态文件路由，提供dash_table字体文件
@app.server.route('/_dash-component-suites/dash/dash_table/<path:filename>')
def serve_dash_table_assets(filename):
    """提供dash_table静态文件，避免404错误"""
    from flask import send_from_directory, abort, Response
    import os
    
    # 静态文件目录
    static_dir = os.path.join(os.path.dirname(__file__), 'static', '_dash-component-suites', 'dash', 'dash_table')
    
    # 如果请求的是字体文件，直接返回空响应（避免404错误）
    if filename.endswith(('.woff', '.woff2')):
        return Response("", status=200, mimetype='font/woff2' if filename.endswith('.woff2') else 'font/woff')
    
    # 如果请求的是bundle.js但版本不匹配，返回现有的bundle.js
    if filename.startswith('bundle.') and filename.endswith('.js'):
        bundle_file = os.path.join(static_dir, 'bundle.js')
        if os.path.exists(bundle_file):
            return send_from_directory(static_dir, 'bundle.js')
    
    try:
        return send_from_directory(static_dir, filename)
    except FileNotFoundError:
        # 如果文件不存在，返回空响应避免404错误
        return Response("", status=200, mimetype='application/octet-stream')

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


# 添加测试页面路由
@app.server.route('/test_audio_visualizer.html')
def test_audio_visualizer():
    """提供音频可视化器测试页面"""
    from flask import send_from_directory
    import os
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(project_root, 'test_audio_visualizer.html')
    
    if os.path.exists(test_file):
        return send_from_directory(project_root, 'test_audio_visualizer.html')
    else:
        return "测试页面不存在", 404

# 添加流式响应端点
@app.server.post('/stream')
def stream():
    log.debug("接收到/stream端点请求")
    try:
        # 获取请求参数（从JSON请求体中）
        data = request.get_json() or {}
        #log.debug(f"/stream端点接收到的请求数据: {data}")
        message_id = data.get('message_id')
        messages_data = data.get('messages', [])
        session_id = data.get('session_id')
        role = data.get('role', 'assistant')
        # 从请求参数中获取personality_id，如果未指定则默认为health_assistant
        personality_id = data.get('personality_id', 'health_assistant')
        
        log.debug(f"/stream端点参数解析完成 - message_id: {message_id}, session_id: {session_id}, personality_id: {personality_id}")
        
        @stream_with_context
        def generate():
            log.debug("开始生成SSE流式响应")
            import time
            start_time = time.time()
            timeout_seconds = 30  # 30秒超时
            last_activity_time = start_time
            
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
                    use_tools=BaseConfig.yychat_default_use_tools,
                    # 透传语音相关上下文到下游，便于后端按方案B并行触发TTS
                    enable_voice=data.get('enable_voice', False),
                    client_id=data.get('client_id'),
                    message_id=message_id
                ):
                    # 检查超时
                    current_time = time.time()
                    if current_time - start_time > timeout_seconds:
                        log.warning(f"SSE流式响应超时: {message_id}")
                        timeout_data = {
                            "message_id": message_id,
                            "status": "timeout",
                            "error": "响应超时，请重试",
                            "role": role
                        }
                        timeout_str = json.dumps(timeout_data)
                        yield f'data: {timeout_str}\n\n'
                        break
                    
                    if chunk:
                        last_activity_time = current_time
                        # 发送数据，包含message_id以识别目标消息
                        # 确保返回的数据格式正确
                        if isinstance(chunk, dict) and 'choices' in chunk and chunk['choices']:
                            content = chunk['choices'][0].get('delta', {}).get('content', '')
                            if content:
                                # 先创建JSON对象，再转换为字符串，避免多线f-string语法问题
                                response_data = {
                                    "message_id": message_id,
                                    "content": content,
                                    "role": role,
                                    "status": "streaming"
                                }
                                response_str = json.dumps(response_data)
                                yield f'data: {response_str}\n\n'
                
                # 检查是否因为超时而退出
                if time.time() - start_time <= timeout_seconds:
                    # 发送结束标志
                    end_data = {
                        "message_id": message_id,
                        "status": "completed",
                        "role": role
                    }
                    end_str = json.dumps(end_data)
                    yield f'data: {end_str}\n\n'
                    
            except Exception as e:
                # 发送错误信息
                error_message = str(e)
                log.error(f"流式响应出错: {error_message}")
                error_data = {
                    "message_id": message_id,
                    "status": "error",
                    "error": error_message,
                    "role": role
                }
                error_str = json.dumps(error_data)
                yield f'data: {error_str}\n\n'
        
        # 设置响应头，返回SSE格式的数据
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={'X-Accel-Buffering': 'no'}
        )
    except Exception as e:
        log.error(f"处理流式请求失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
