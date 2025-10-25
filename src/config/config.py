"""
统一配置管理模块

提供统一的配置管理功能，支持从环境变量读取配置。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

import os
from typing import Dict, Any, Optional


class Config:
    """统一配置管理器"""
    
    def __init__(self):
        """初始化配置管理器"""
        self.config = {
            # 应用配置
            'app': {
                'name': 'yyAsistant',
                'version': '2.0.0',
                'debug': os.getenv('DEBUG', 'False').lower() == 'true'
            },
            
            # 数据库配置
            'database': {
                'url': os.getenv('DATABASE_URL', 'sqlite:///yyAsistant.db'),
                'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20'))
            },
            
            # WebSocket配置
            'websocket': {
                'url': os.getenv('WEBSOCKET_URL', 'ws://localhost:8000/ws'),
                'reconnect_attempts': int(os.getenv('WS_RECONNECT_ATTEMPTS', '5')),
                'reconnect_interval': int(os.getenv('WS_RECONNECT_INTERVAL', '5000')),
                'heartbeat_interval': int(os.getenv('WS_HEARTBEAT_INTERVAL', '30000'))
            },
            
            # 语音配置
            'voice': {
                'synthesis_voice': os.getenv('VOICE_SYNTHESIS_VOICE', 'zh-CN-XiaoxiaoNeural'),
                'synthesis_speed': float(os.getenv('VOICE_SYNTHESIS_SPEED', '1.0')),
                'synthesis_volume': float(os.getenv('VOICE_SYNTHESIS_VOLUME', '1.0')),
                'recognition_language': os.getenv('VOICE_RECOGNITION_LANGUAGE', 'zh-CN')
            },
            
            # 超时配置
            'timeouts': {
                'sse_base': int(os.getenv('SSE_TIMEOUT_BASE', '30')),
                'sse_per_char': float(os.getenv('SSE_TIMEOUT_PER_CHAR', '0.1')),
                'sse_max': int(os.getenv('SSE_TIMEOUT_MAX', '300')),
                'tts_base': int(os.getenv('TTS_TIMEOUT_BASE', '60')),
                'tts_per_char': float(os.getenv('TTS_TIMEOUT_PER_CHAR', '0.2')),
                'tts_max': int(os.getenv('TTS_TIMEOUT_MAX', '600')),
                'stt_base': int(os.getenv('STT_TIMEOUT_BASE', '30')),
                'stt_per_char': float(os.getenv('STT_TIMEOUT_PER_CHAR', '0.05')),
                'stt_max': int(os.getenv('STT_TIMEOUT_MAX', '180'))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，使用点号分隔层级，如 'app.name'
            default: 默认值，当配置不存在时返回
        
        Returns:
            配置值
        
        Example:
            >>> config = Config()
            >>> config.get('app.name')
            'yyAsistant'
            >>> config.get('app.debug')
            False
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，使用点号分隔层级，如 'app.name'
            value: 配置值
        
        Example:
            >>> config = Config()
            >>> config.set('app.debug', True)
            >>> config.get('app.debug')
            True
        """
        keys = key.split('.')
        config = self.config
        
        # 遍历到倒数第二层
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置最后一层的值
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            完整的配置字典
        """
        return self.config.copy()
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        批量更新配置
        
        Args:
            config_dict: 配置字典
        """
        def deep_update(target: Dict, source: Dict) -> None:
            """深度更新字典"""
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_update(target[key], value)
                else:
                    target[key] = value
        
        deep_update(self.config, config_dict)


# 全局配置实例
config = Config()


# 便捷函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置值的便捷函数"""
    return config.get(key, default)


def set_config(key: str, value: Any) -> None:
    """设置配置值的便捷函数"""
    config.set(key, value)
