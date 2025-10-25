# 语音功能配置
from typing import Dict, Any


class VoiceConfig:
    """语音功能配置类"""
    
    # WebSocket配置已移至 base_config.py 中统一管理
    
    # 音频配置
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_BIT_RATE = 128000
    
    # 语音活动检测
    VAD_THRESHOLD = 0.01
    VAD_SILENCE_DURATION = 1000  # 毫秒
    
    # UI配置
    AUTO_PLAY_DEFAULT = True
    VOICE_DEFAULT = "shimmer"
    VOLUME_DEFAULT = 80
    
    # 音频格式配置
    AUDIO_FORMAT = "webm"
    AUDIO_MIME_TYPE = "audio/webm;codecs=opus"
    
    # 录音配置
    RECORDING_CHUNK_SIZE = 1024
    RECORDING_MAX_DURATION = 30000  # 毫秒，最大录音时长30秒
    
    # 播放配置
    PLAYBACK_VOLUME = 0.8
    PLAYBACK_RATE = 1.0
    
    # 错误处理配置
    ERROR_RETRY_ATTEMPTS = 3
    ERROR_RETRY_DELAY = 1000  # 毫秒
    
    @classmethod
    def get_voice_options(cls) -> list:
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
    def get_default_settings(cls) -> Dict[str, Any]:
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
