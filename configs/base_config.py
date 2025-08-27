from typing import List, Union, Callable


class BaseConfig:
    """应用基础配置参数"""

    # 应用基础标题
    app_title: str = "智能助手"

    # 应用版本
    app_version: str = "0.2.1"

    # 应用密钥
    app_secret_key: str = "yyAsistant-bgt56yhn-passkey"

    # 日志配置参数
    app_log_filename: str = 'app.log'
    app_log_level: str = 'DEBUG'
    app_peewee_debug_log: bool = False

    # 应用会话cookie名称
    # 由于同一主机地址下的不同端口，在浏览器中会
    # 共享cookies，因此在同一主机地址下部署多套基于
    # magic-dash-pro模板开发的独立项目时，请为各个项目
    # 设置不同的app_session_cookie_name
    app_session_cookie_name: str = "yyAsistant_session"

    # 浏览器最低版本限制规则
    min_browser_versions: List[dict] = [
        {"browser": "Chrome", "version": 88},
        {"browser": "Firefox", "version": 78},
        {"browser": "Edge", "version": 100},
    ]

    # 是否基于min_browser_versions开启严格的浏览器类型限制
    # 不在min_browser_versions规则内的浏览器将被直接拦截
    strict_browser_type_check: bool = False

    # 是否启用重复登录辅助检查
    enable_duplicate_login_check: bool = False

    # 重复登录辅助检查轮询间隔时间，单位：秒
    duplicate_login_check_interval: Union[int, float] = 10

    # 登录会话token对应的cookies项名称
    # 由于同一主机地址下的不同端口，在浏览器中会共享cookies
    # 因此在同一主机地址下部署多套基于magic-dash-pro模板开发的独立项目时
    # 请为各个项目设置不同的session_token_cookie_name
    session_token_cookie_name: str = "session_token"

    # 是否开启全屏额外水印功能
    enable_fullscreen_watermark: bool = False

    # 当开启了全屏额外水印功能时，用于动态处理实际水印内容输出
    fullscreen_watermark_generator: Callable = (
        lambda current_user: current_user.user_name
    )
