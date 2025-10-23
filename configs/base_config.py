# -*- coding: utf-8 -*-
# 添加类型导入
from typing import List, Union, Callable
from .app_config import app_config


class BaseConfig:
    """应用基础配置参数 - 使用统一配置"""

    # 添加SSE配置参数
    # 每次动画显示的字符数
    sse_animate_chunk = app_config.SSE_ANIMATE_CHUNK
    # 动画显示的延迟时间(毫秒)
    sse_animate_delay = app_config.SSE_ANIMATE_DELAY

    # 应用基础标题
    app_title = app_config.APP_TITLE

    # 应用版本
    app_version = app_config.APP_VERSION

    # 应用密钥
    app_secret_key = app_config.APP_SECRET_KEY

    # 日志配置参数
    app_log_filename = app_config.APP_LOG_FILENAME
    app_log_level = app_config.APP_LOG_LEVEL
    app_peewee_debug_log = app_config.APP_PEEWEE_DEBUG_LOG

    # 应用会话cookie名称
    # 由于同一主机地址下的不同端口，在浏览器中会
    # 共享cookies，因此在同一主机地址下部署多套基于
    # magic-dash-pro模板开发的独立项目时，请为各个项目
    # 设置不同的app_session_cookie_name
    app_session_cookie_name = app_config.APP_SESSION_COOKIE_NAME

    # 浏览器最低版本限制规则
    min_browser_versions = app_config.get_min_browser_versions()

    # 是否基于min_browser_versions开启严格的浏览器类型限制
    # 不在min_browser_versions规则内的浏览器将被直接拦截
    strict_browser_type_check = app_config.STRICT_BROWSER_TYPE_CHECK

    # 是否启用重复登录辅助检查
    enable_duplicate_login_check = app_config.ENABLE_DUPLICATE_LOGIN_CHECK

    # 重复登录辅助检查轮询间隔时间，单位：秒
    duplicate_login_check_interval = app_config.DUPLICATE_LOGIN_CHECK_INTERVAL

    # 登录会话token对应的cookies项名称
    # 由于同一主机地址下的不同端口，在浏览器中会共享cookies
    # 因此在同一主机地址下部署多套基于magic-dash-pro模板开发的独立项目时
    # 请为各个项目设置不同的session_token_cookie_name
    session_token_cookie_name = app_config.SESSION_TOKEN_COOKIE_NAME

    # 是否开启全屏额外水印功能
    enable_fullscreen_watermark = app_config.ENABLE_FULLSCREEN_WATERMARK

    # 当开启了全屏额外水印功能时，用于动态处理实际水印内容输出
    fullscreen_watermark_generator = app_config.get_fullscreen_watermark_generator()

    # YYChat API配置
    # API基础URL
    yychat_api_base_url = app_config.get_yychat_api_base_url()
    # API密钥配置在环境变量中，默认值仅供开发测试使用
    yychat_api_key = app_config.YYCHAT_API_KEY
    # 默认模型
    yychat_default_model = app_config.YYCHAT_DEFAULT_MODEL
    # 默认温度参数
    yychat_default_temperature = app_config.YYCHAT_DEFAULT_TEMPERATURE
    # 默认是否使用流式响应
    yychat_default_stream = app_config.YYCHAT_DEFAULT_STREAM
    # 默认是否使用工具
    yychat_default_use_tools = app_config.YYCHAT_DEFAULT_USE_TOOLS
    
    # 语音自动播放配置
    # SSE结束后是否自动触发TTS语音播放
    enable_auto_tts_after_sse = app_config.ENABLE_AUTO_TTS_AFTER_SSE
