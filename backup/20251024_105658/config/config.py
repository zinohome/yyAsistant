"""
统一配置管理模块

提供统一的配置管理功能，包括应用配置、数据库配置、WebSocket配置、
语音配置、超时配置等。

作者: AI Assistant
创建时间: 2025-01-15
版本: 1.0.0
"""

import os
from typing import Dict, Any, Optional

class Config:
    """统一配置管理"""
    
    def __init__(self):
        """初始化配置"""
        self.config = {
            # 应用配置
            'app': {
                'name': 'yyAsistant',
                'version': '2.0.0',
                'debug': os.getenv('DEBUG', 'False').lower() == 'true',
                'host': os.getenv('HOST', '0.0.0.0'),
                'port': int(os.getenv('PORT', '8050'))
            },
            
            # 数据库配置
            'database': {
                'url': os.getenv('DATABASE_URL', 'sqlite:///yyAsistant.db'),
                'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
                'echo': os.getenv('DB_ECHO', 'False').lower() == 'true'
            },
            
            # WebSocket配置
            'websocket': {
                'url': os.getenv('WEBSOCKET_URL', 'ws://localhost:8000/ws'),
                'reconnect_attempts': int(os.getenv('WS_RECONNECT_ATTEMPTS', '5')),
                'reconnect_interval': int(os.getenv('WS_RECONNECT_INTERVAL', '5000')),
                'heartbeat_interval': int(os.getenv('WS_HEARTBEAT_INTERVAL', '30000')),
                'max_message_size': int(os.getenv('WS_MAX_MESSAGE_SIZE', '1048576'))  # 1MB
            },
            
            # 语音配置
            'voice': {
                'synthesis_voice': os.getenv('VOICE_SYNTHESIS_VOICE', 'zh-CN-XiaoxiaoNeural'),
                'synthesis_speed': float(os.getenv('VOICE_SYNTHESIS_SPEED', '1.0')),
                'synthesis_volume': float(os.getenv('VOICE_SYNTHESIS_VOLUME', '1.0')),
                'recognition_language': os.getenv('VOICE_RECOGNITION_LANGUAGE', 'zh-CN'),
                'recognition_confidence': float(os.getenv('VOICE_RECOGNITION_CONFIDENCE', '0.8'))
            },
            
            # 超时配置
            'timeouts': {
                'sse_base': int(os.getenv('SSE_TIMEOUT_BASE', '30')),
                'sse_per_char': float(os.getenv('SSE_TIMEOUT_PER_CHAR', '0.1')),
                'sse_max': int(os.getenv('SSE_TIMEOUT_MAX', '300')),
                'sse_warning': int(os.getenv('SSE_TIMEOUT_WARNING', '60')),
                'tts_base': int(os.getenv('TTS_TIMEOUT_BASE', '60')),
                'tts_per_char': float(os.getenv('TTS_TIMEOUT_PER_CHAR', '0.2')),
                'tts_max': int(os.getenv('TTS_TIMEOUT_MAX', '600')),
                'tts_warning': int(os.getenv('TTS_TIMEOUT_WARNING', '120')),
                'stt_base': int(os.getenv('STT_TIMEOUT_BASE', '30')),
                'stt_per_char': float(os.getenv('STT_TIMEOUT_PER_CHAR', '0.05')),
                'stt_max': int(os.getenv('STT_TIMEOUT_MAX', '180')),
                'stt_warning': int(os.getenv('STT_TIMEOUT_WARNING', '45'))
            },
            
            # 日志配置
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'format': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
                'file': os.getenv('LOG_FILE', 'logs/app.log'),
                'max_size': int(os.getenv('LOG_MAX_SIZE', '10485760')),  # 10MB
                'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5'))
            },
            
            # 性能配置
            'performance': {
                'max_memory_usage': int(os.getenv('MAX_MEMORY_USAGE', '536870912')),  # 512MB
                'max_cpu_usage': float(os.getenv('MAX_CPU_USAGE', '50.0')),
                'response_timeout': int(os.getenv('RESPONSE_TIMEOUT', '2')),
                'max_concurrent_requests': int(os.getenv('MAX_CONCURRENT_REQUESTS', '100'))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'app.name'
            default: 默认值
        
        Returns:
            配置值或默认值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        # 创建嵌套字典结构
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置最终值
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            完整的配置字典
        """
        return self.config.copy()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        批量更新配置
        
        Args:
            updates: 要更新的配置字典
        """
        for key, value in updates.items():
            self.set(key, value)
    
    def validate(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            配置是否有效
        """
        try:
            # 验证必需的配置项
            required_keys = [
                'app.name',
                'app.version',
                'database.url',
                'websocket.url'
            ]
            
            for key in required_keys:
                if self.get(key) is None:
                    return False
            
            # 验证数值范围
            if self.get('app.port', 0) <= 0 or self.get('app.port', 0) > 65535:
                return False
            
            if self.get('database.pool_size', 0) <= 0:
                return False
            
            if self.get('websocket.reconnect_attempts', 0) < 0:
                return False
            
            return True
        except Exception:
            return False
    
    def reload(self) -> None:
        """重新加载配置"""
        self.__init__()

# 全局配置实例
config = Config()

# 验证配置
if not config.validate():
    raise ValueError("配置验证失败，请检查配置文件")

# 导出配置实例
__all__ = ['Config', 'config']
