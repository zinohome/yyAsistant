# -*- coding: utf-8 -*-
"""
统一应用配置文件
整合所有硬编码配置，支持环境变量覆盖
"""
import os
import sys
from typing import Dict, Any, List, Union, Callable
from dotenv import load_dotenv, find_dotenv

# 获取当前文件所在目录的绝对路径
base_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(base_dir)
# 构造.env文件的绝对路径
env_path = os.path.join(project_root, '.env')

# 延迟加载环境变量，避免重复加载
_env_loaded = False

def load_env_file():
    """加载.env文件（延迟初始化，避免重复加载）"""
    global _env_loaded
    if _env_loaded:
        return
    
    try:
        # find_dotenv会尝试定位.env文件，fallback到我们指定的路径
        env_file = find_dotenv(usecwd=True) or env_path
        
        # 加载.env文件，如果不存在则尝试创建
        if os.path.exists(env_file):
            load_dotenv(dotenv_path=env_file, override=True)
            print(f"成功加载.env文件: {env_file}")
        else:
            # 如果.env文件不存在，可以选择创建一个默认的
            print(f".env文件不存在: {env_file}")
            # 注意：如果要自动创建.env文件，可以取消下面的注释
            # with open(env_file, 'w') as f:
            #     f.write("# 默认环境变量配置\n")
        
        _env_loaded = True
    except Exception as e:
        print(f"加载.env文件时出错: {str(e)}")

# 在首次导入时加载环境变量
load_env_file()


class AppConfig:
    """统一应用配置类"""
    
    # ==================== 应用基础配置 ====================
    APP_TITLE: str = os.getenv("APP_TITLE", "研翌助手")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.5.4")
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "yyAsistant-bgt56yhn-passkey")
    
    # ==================== 服务器配置 ====================
    # 应用服务器配置
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8050"))
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "True").lower() == "true"
    
    # ==================== 数据库配置 ====================
    # 数据库类型
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "postgresql")
    
    # PostgreSQL配置
    POSTGRESQL_HOST: str = os.getenv("POSTGRESQL_HOST", "192.168.32.11")
    POSTGRESQL_PORT: int = int(os.getenv("POSTGRESQL_PORT", "5432"))
    POSTGRESQL_USER: str = os.getenv("POSTGRESQL_USER", "yyasistant")
    POSTGRESQL_PASSWORD: str = os.getenv("POSTGRESQL_PASSWORD", "passw0rd")
    POSTGRESQL_DATABASE: str = os.getenv("POSTGRESQL_DATABASE", "yyasistant")
    
    # MySQL配置
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "admin123")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "magic_dash_pro")
    
    # ==================== 后端服务配置 ====================
    # yychat后端服务配置
    YYCHAT_HOST: str = os.getenv("YYCHAT_HOST", "192.168.32.168")
    YYCHAT_PORT: int = int(os.getenv("YYCHAT_PORT", "9800"))
    YYCHAT_API_KEY: str = os.getenv("YYCHAT_API_KEY", "yk-1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4")
    YYCHAT_DEFAULT_MODEL: str = os.getenv("YYCHAT_DEFAULT_MODEL", "gpt-4.1")
    YYCHAT_DEFAULT_TEMPERATURE: float = float(os.getenv("YYCHAT_DEFAULT_TEMPERATURE", "0.7"))
    YYCHAT_DEFAULT_STREAM: bool = os.getenv("YYCHAT_DEFAULT_STREAM", "True").lower() == "true"
    YYCHAT_DEFAULT_USE_TOOLS: bool = os.getenv("YYCHAT_DEFAULT_USE_TOOLS", "True").lower() == "true"
    
    # ==================== WebSocket配置 ====================
    WS_URL: str = os.getenv("WS_URL", f"ws://{YYCHAT_HOST}:{YYCHAT_PORT}/ws/chat")
    WS_RECONNECT_INTERVAL: int = int(os.getenv("WS_RECONNECT_INTERVAL", "1000"))
    WS_MAX_RECONNECT_ATTEMPTS: int = int(os.getenv("WS_MAX_RECONNECT_ATTEMPTS", "5"))
    
    # ==================== 日志配置 ====================
    APP_LOG_FILENAME: str = os.getenv("APP_LOG_FILENAME", "app.log")
    APP_LOG_LEVEL: str = os.getenv("APP_LOG_LEVEL", "DEBUG")
    APP_PEEWEE_DEBUG_LOG: bool = os.getenv("APP_PEEWEE_DEBUG_LOG", "False").lower() == "true"
    
    # ==================== 会话配置 ====================
    APP_SESSION_COOKIE_NAME: str = os.getenv("APP_SESSION_COOKIE_NAME", "yyAsistant_session")
    SESSION_TOKEN_COOKIE_NAME: str = os.getenv("SESSION_TOKEN_COOKIE_NAME", "session_token")
    
    # ==================== 浏览器配置 ====================
    MIN_BROWSER_VERSIONS: List[Dict[str, Union[str, int]]] = [
        {"browser": "Chrome", "version": 88},
        {"browser": "Firefox", "version": 78},
        {"browser": "Edge", "version": 100},
    ]
    STRICT_BROWSER_TYPE_CHECK: bool = os.getenv("STRICT_BROWSER_TYPE_CHECK", "False").lower() == "true"
    
    # ==================== 登录配置 ====================
    ENABLE_DUPLICATE_LOGIN_CHECK: bool = os.getenv("ENABLE_DUPLICATE_LOGIN_CHECK", "False").lower() == "true"
    DUPLICATE_LOGIN_CHECK_INTERVAL: Union[int, float] = float(os.getenv("DUPLICATE_LOGIN_CHECK_INTERVAL", "10"))
    
    # ==================== 水印配置 ====================
    ENABLE_FULLSCREEN_WATERMARK: bool = os.getenv("ENABLE_FULLSCREEN_WATERMARK", "False").lower() == "true"
    
    # ==================== SSE配置 ====================
    SSE_ANIMATE_CHUNK: int = int(os.getenv("SSE_ANIMATE_CHUNK", "50"))
    SSE_ANIMATE_DELAY: int = int(os.getenv("SSE_ANIMATE_DELAY", "1"))
    ENABLE_AUTO_TTS_AFTER_SSE: bool = os.getenv("ENABLE_AUTO_TTS_AFTER_SSE", "True").lower() == "true"
    
    # ==================== 音频配置 ====================
    AUDIO_SAMPLE_RATE: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    AUDIO_CHANNELS: int = int(os.getenv("AUDIO_CHANNELS", "1"))
    AUDIO_BIT_RATE: int = int(os.getenv("AUDIO_BIT_RATE", "128000"))
    AUDIO_FORMAT: str = os.getenv("AUDIO_FORMAT", "webm")
    AUDIO_MIME_TYPE: str = os.getenv("AUDIO_MIME_TYPE", "audio/webm;codecs=opus")
    
    # ==================== 语音配置 ====================
    VOICE_DEFAULT: str = os.getenv("VOICE_DEFAULT", "shimmer")
    VOLUME_DEFAULT: int = int(os.getenv("VOLUME_DEFAULT", "80"))
    AUTO_PLAY_DEFAULT: bool = os.getenv("AUTO_PLAY_DEFAULT", "True").lower() == "true"
    PLAYBACK_VOLUME: float = float(os.getenv("PLAYBACK_VOLUME", "0.8"))
    PLAYBACK_RATE: float = float(os.getenv("PLAYBACK_RATE", "1.0"))
    
    # ==================== VAD配置 ====================
    VAD_THRESHOLD: float = float(os.getenv("VAD_THRESHOLD", "0.01"))
    VAD_SILENCE_DURATION: int = int(os.getenv("VAD_SILENCE_DURATION", "1000"))
    
    # ==================== 录音配置 ====================
    RECORDING_CHUNK_SIZE: int = int(os.getenv("RECORDING_CHUNK_SIZE", "1024"))
    RECORDING_MAX_DURATION: int = int(os.getenv("RECORDING_MAX_DURATION", "30000"))
    
    # ==================== 错误处理配置 ====================
    ERROR_RETRY_ATTEMPTS: int = int(os.getenv("ERROR_RETRY_ATTEMPTS", "3"))
    ERROR_RETRY_DELAY: int = int(os.getenv("ERROR_RETRY_DELAY", "1000"))
    
    # ==================== 测试配置 ====================
    # 测试环境URL配置
    TEST_BASE_URL: str = os.getenv("TEST_BASE_URL", "http://192.168.32.168:8050")
    TEST_BACKEND_URL: str = os.getenv("TEST_BACKEND_URL", "http://192.168.32.168:9800")
    TEST_LOCALHOST_URL: str = os.getenv("TEST_LOCALHOST_URL", "http://localhost:8050")
    
    # ==================== 兼容性方法 ====================
    @classmethod
    def get_yychat_api_base_url(cls) -> str:
        """获取yychat API基础URL"""
        return f"http://{cls.YYCHAT_HOST}:{cls.YYCHAT_PORT}/v1"
    
    @classmethod
    def get_postgresql_config(cls) -> Dict[str, Any]:
        """获取PostgreSQL配置"""
        return {
            "host": cls.POSTGRESQL_HOST,
            "port": cls.POSTGRESQL_PORT,
            "user": cls.POSTGRESQL_USER,
            "password": cls.POSTGRESQL_PASSWORD,
            "database": cls.POSTGRESQL_DATABASE,
        }
    
    @classmethod
    def get_mysql_config(cls) -> Dict[str, Any]:
        """获取MySQL配置"""
        return {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "user": cls.MYSQL_USER,
            "password": cls.MYSQL_PASSWORD,
            "database": cls.MYSQL_DATABASE,
        }
    
    @classmethod
    def get_voice_options(cls) -> List[Dict[str, str]]:
        """获取可用的语音选项"""
        return [
            {"label": "Alloy (中性)", "value": "alloy"},
            {"label": "Echo (男性)", "value": "echo"},
            {"label": "Fable (女性)", "value": "fable"},
            {"label": "Onyx (男性)", "value": "onyx"},
            {"label": "Nova (女性)", "value": "nova"},
            {"label": "Shimmer (女性)", "value": "shimmer"}
        ]
    
    @classmethod
    def get_default_voice_settings(cls) -> Dict[str, Any]:
        """获取默认语音设置"""
        return {
            "voice": cls.VOICE_DEFAULT,
            "rate": cls.PLAYBACK_RATE,
            "volume": cls.VOLUME_DEFAULT,
            "auto_play": cls.AUTO_PLAY_DEFAULT,
            "sample_rate": cls.AUDIO_SAMPLE_RATE,
            "channels": cls.AUDIO_CHANNELS
        }
    
    @classmethod
    def get_fullscreen_watermark_generator(cls) -> Callable:
        """获取全屏水印生成器"""
        return lambda current_user: current_user.user_name
    
    @classmethod
    def get_min_browser_versions(cls) -> List[Dict[str, Union[str, int]]]:
        """获取最低浏览器版本要求"""
        return cls.MIN_BROWSER_VERSIONS


# 创建全局配置实例
app_config = AppConfig()
