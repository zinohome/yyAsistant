# 添加类型导入
from typing import List, Union, Callable


class BaseConfig:
    """应用基础配置参数"""

    # 添加SSE配置参数
    # 每次动画显示的字符数
    sse_animate_chunk: int = 50
    # 动画显示的延迟时间(毫秒)
    sse_animate_delay: int = 1

    # 应用基础标题
    app_title: str = "研翌助手"

    # 应用版本
    app_version: str = "0.5.4"

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

    # YYChat API配置
    # API基础URL
    yychat_api_base_url: str = "http://192.210.183.125:9800/v1"
    # API密钥配置在环境变量中，默认值仅供开发测试使用
    yychat_api_key: str = "yk-1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4"
    # 默认模型
    yychat_default_model: str = "gpt-4.1"
    # 默认温度参数
    yychat_default_temperature: float = 0.7
    # 默认是否使用流式响应
    yychat_default_stream: bool = True
    # 默认是否使用工具
    yychat_default_use_tools: bool = True
    
    # 语音自动播放配置
    # SSE结束后是否自动触发TTS语音播放
    enable_auto_tts_after_sse: bool = True
    
    # WebSocket配置
    # WebSocket服务器地址
    websocket_url: str = "ws://192.210.183.125:9800/ws/chat"
    # WebSocket重连间隔时间（毫秒）
    websocket_reconnect_interval: int = 1000
    # WebSocket最大重连次数
    websocket_max_reconnect_attempts: int = 5