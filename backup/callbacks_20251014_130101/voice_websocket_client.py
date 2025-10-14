#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import base64
import time
from typing import Dict, Any, Optional, Callable, List
from configs.voice_config import VoiceConfig
from utils.log import log


class VoiceWebSocketClient:
    """语音WebSocket客户端 - 专门处理语音相关的WebSocket通信"""
    
    def __init__(self):
        self.ws_url = VoiceConfig.WS_URL
        self.reconnect_interval = VoiceConfig.WS_RECONNECT_INTERVAL
        self.max_reconnect_attempts = VoiceConfig.WS_MAX_RECONNECT_ATTEMPTS
        self.websocket = None
        self.client_id = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.message_handlers: Dict[str, Callable] = {}
        self.connection_handlers: List[Callable] = []
        self.disconnection_handlers: List[Callable] = []
        
    async def connect(self) -> bool:
        """建立WebSocket连接"""
        try:
            # 这里需要在前端JavaScript中实现实际的WebSocket连接
            # 这个Python类主要用于配置管理和消息格式定义
            log.info(f"准备连接语音WebSocket: {self.ws_url}")
            return True
        except Exception as e:
            log.error(f"WebSocket连接失败: {e}")
            return False
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
        log.debug(f"注册消息处理器: {message_type}")
    
    def register_connection_handler(self, handler: Callable):
        """注册连接处理器"""
        self.connection_handlers.append(handler)
    
    def register_disconnection_handler(self, handler: Callable):
        """注册断开连接处理器"""
        self.disconnection_handlers.append(handler)
    
    def create_audio_input_message(self, audio_data: bytes, **kwargs) -> Dict[str, Any]:
        """创建音频输入消息"""
        return {
            "type": "audio_input",
            "audio_data": base64.b64encode(audio_data).decode('utf-8'),
            "timestamp": time.time(),
            "client_id": self.client_id,
            **kwargs
        }
    
    def create_audio_stream_message(self, audio_chunk: bytes, **kwargs) -> Dict[str, Any]:
        """创建音频流消息"""
        return {
            "type": "audio_stream",
            "audio_data": base64.b64encode(audio_chunk).decode('utf-8'),
            "timestamp": time.time(),
            "client_id": self.client_id,
            **kwargs
        }
    
    def create_voice_command_message(self, command: str, **kwargs) -> Dict[str, Any]:
        """创建语音命令消息"""
        return {
            "type": "voice_command",
            "command": command,
            "timestamp": time.time(),
            "client_id": self.client_id,
            **kwargs
        }
    
    def create_status_query_message(self, **kwargs) -> Dict[str, Any]:
        """创建状态查询消息"""
        return {
            "type": "status_query",
            "timestamp": time.time(),
            "client_id": self.client_id,
            **kwargs
        }
    
    def create_heartbeat_message(self) -> Dict[str, Any]:
        """创建心跳消息"""
        return {
            "type": "heartbeat",
            "timestamp": time.time(),
            "client_id": self.client_id
        }
    
    def get_connection_config(self) -> Dict[str, Any]:
        """获取连接配置"""
        return {
            "url": self.ws_url,
            "reconnect_interval": self.reconnect_interval,
            "max_reconnect_attempts": self.max_reconnect_attempts,
            "audio_config": {
                "sample_rate": VoiceConfig.AUDIO_SAMPLE_RATE,
                "channels": VoiceConfig.AUDIO_CHANNELS,
                "format": VoiceConfig.AUDIO_FORMAT,
                "mime_type": VoiceConfig.AUDIO_MIME_TYPE
            }
        }
    
    def get_supported_message_types(self) -> List[str]:
        """获取支持的消息类型"""
        return [
            "audio_input",
            "audio_stream", 
            "voice_command",
            "status_query",
            "heartbeat"
        ]
    
    def get_expected_response_types(self) -> List[str]:
        """获取期望的响应类型"""
        return [
            "audio_processing_start",
            "transcription_result",
            "audio_response",
            "voice_command_response",
            "status_response",
            "heartbeat_response",
            "error"
        ]


# 创建全局实例
voice_websocket_client = VoiceWebSocketClient()
