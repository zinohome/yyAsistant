# -*- coding: utf-8 -*-
# 语音功能配置
from typing import Dict, Any
from .app_config import app_config


class VoiceConfig:
    """语音功能配置类 - 使用统一配置"""
    
    # WebSocket配置 - 直连yychat后端的WebSocket端点
    WS_URL = app_config.WS_URL
    WS_RECONNECT_INTERVAL = app_config.WS_RECONNECT_INTERVAL  # 毫秒
    WS_MAX_RECONNECT_ATTEMPTS = app_config.WS_MAX_RECONNECT_ATTEMPTS
    
    # 音频配置
    AUDIO_SAMPLE_RATE = app_config.AUDIO_SAMPLE_RATE
    AUDIO_CHANNELS = app_config.AUDIO_CHANNELS
    AUDIO_BIT_RATE = app_config.AUDIO_BIT_RATE
    
    # 语音活动检测
    VAD_THRESHOLD = app_config.VAD_THRESHOLD
    VAD_SILENCE_DURATION = app_config.VAD_SILENCE_DURATION  # 毫秒
    
    # UI配置
    AUTO_PLAY_DEFAULT = app_config.AUTO_PLAY_DEFAULT
    VOICE_DEFAULT = app_config.VOICE_DEFAULT
    VOLUME_DEFAULT = app_config.VOLUME_DEFAULT
    
    # 音频格式配置
    AUDIO_FORMAT = app_config.AUDIO_FORMAT
    AUDIO_MIME_TYPE = app_config.AUDIO_MIME_TYPE
    
    # 录音配置
    RECORDING_CHUNK_SIZE = app_config.RECORDING_CHUNK_SIZE
    RECORDING_MAX_DURATION = app_config.RECORDING_MAX_DURATION  # 毫秒，最大录音时长30秒
    
    # 播放配置
    PLAYBACK_VOLUME = app_config.PLAYBACK_VOLUME
    PLAYBACK_RATE = app_config.PLAYBACK_RATE
    
    # 错误处理配置
    ERROR_RETRY_ATTEMPTS = app_config.ERROR_RETRY_ATTEMPTS
    ERROR_RETRY_DELAY = app_config.ERROR_RETRY_DELAY  # 毫秒
    
    @classmethod
    def get_voice_options(cls) -> list:
        """获取可用的语音选项"""
        return app_config.get_voice_options()
    
    @classmethod
    def get_default_settings(cls) -> Dict[str, Any]:
        """获取默认语音设置"""
        return app_config.get_default_voice_settings()
    
    @classmethod
    def validate_settings(cls, settings: Dict[str, Any]) -> Dict[str, Any]:
        """验证语音设置参数"""
        validated = {}
        
        # 验证语音类型
        voice_options = [opt["value"] for opt in cls.get_voice_options()]
        validated["voice"] = settings.get("voice", cls.VOICE_DEFAULT)
        if validated["voice"] not in voice_options:
            validated["voice"] = cls.VOICE_DEFAULT
        
        # 验证语速
        rate = settings.get("rate", cls.PLAYBACK_RATE)
        validated["rate"] = max(0.5, min(2.0, float(rate)))
        
        # 验证音量
        volume = settings.get("volume", cls.VOLUME_DEFAULT)
        validated["volume"] = max(0, min(100, int(volume)))
        
        # 验证自动播放
        validated["auto_play"] = bool(settings.get("auto_play", cls.AUTO_PLAY_DEFAULT))
        
        return validated
