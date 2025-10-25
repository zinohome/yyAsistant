"""
事件处理器模块

提供统一的事件处理器，负责处理各种事件并更新状态。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

from typing import Any, Optional
import logging
from core.state_manager.state_manager import StateManager, State
from core.event_manager.event_manager import EventManager, Event

logger = logging.getLogger(__name__)


class EventHandlers:
    """事件处理器"""
    
    def __init__(self, state_manager: StateManager, event_manager: EventManager):
        """
        初始化事件处理器
        
        Args:
            state_manager: 状态管理器
            event_manager: 事件管理器
        """
        self.state_manager = state_manager
        self.event_manager = event_manager
        self.register_handlers()
    
    def register_handlers(self) -> None:
        """注册所有事件处理器"""
        # 文本处理事件
        self.event_manager.register_handler(Event.TEXT_START, self.handle_text_start)
        self.event_manager.register_handler(Event.TEXT_SSE_COMPLETE, self.handle_text_sse_complete)
        self.event_manager.register_handler(Event.TEXT_TTS_COMPLETE, self.handle_text_tts_complete)
        
        # 语音处理事件
        self.event_manager.register_handler(Event.VOICE_RECORD_START, self.handle_voice_record_start)
        self.event_manager.register_handler(Event.VOICE_STT_COMPLETE, self.handle_voice_stt_complete)
        self.event_manager.register_handler(Event.VOICE_SSE_COMPLETE, self.handle_voice_sse_complete)
        self.event_manager.register_handler(Event.VOICE_TTS_COMPLETE, self.handle_voice_tts_complete)
        
        # 语音通话事件
        self.event_manager.register_handler(Event.VOICE_CALL_START, self.handle_voice_call_start)
        self.event_manager.register_handler(Event.VOICE_CALL_END, self.handle_voice_call_end)
        
        # 错误和重置事件
        self.event_manager.register_handler(Event.ERROR_OCCURRED, self.handle_error_occurred)
        self.event_manager.register_handler(Event.RESET_STATE, self.handle_reset_state)
        
        logger.info("所有事件处理器已注册")
    
    def handle_text_start(self, data: Any = None) -> None:
        """
        处理文本开始事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理文本开始事件")
        success = self.state_manager.set_state(State.TEXT_SSE)
        if not success:
            logger.warning("无法转换到TEXT_SSE状态")
        else:
            logger.info("状态已转换到TEXT_SSE")
    
    def handle_text_sse_complete(self, data: Any = None) -> None:
        """
        处理文本SSE完成事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理文本SSE完成事件")
        success = self.state_manager.set_state(State.TEXT_TTS)
        if not success:
            logger.warning("无法转换到TEXT_TTS状态")
        else:
            logger.info("状态已转换到TEXT_TTS")
    
    def handle_text_tts_complete(self, data: Any = None) -> None:
        """
        处理文本TTS完成事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理文本TTS完成事件")
        success = self.state_manager.set_state(State.IDLE)
        if not success:
            logger.warning("无法转换到IDLE状态")
        else:
            logger.info("状态已转换到IDLE")
    
    def handle_voice_record_start(self, data: Any = None) -> None:
        """
        处理语音录音开始事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理语音录音开始事件")
        success = self.state_manager.set_state(State.VOICE_STT)
        if not success:
            logger.warning("无法转换到VOICE_STT状态")
        else:
            logger.info("状态已转换到VOICE_STT")
    
    def handle_voice_stt_complete(self, data: Any = None) -> None:
        """
        处理语音STT完成事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理语音STT完成事件")
        success = self.state_manager.set_state(State.VOICE_SSE)
        if not success:
            logger.warning("无法转换到VOICE_SSE状态")
        else:
            logger.info("状态已转换到VOICE_SSE")
    
    def handle_voice_sse_complete(self, data: Any = None) -> None:
        """
        处理语音SSE完成事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理语音SSE完成事件")
        success = self.state_manager.set_state(State.VOICE_TTS)
        if not success:
            logger.warning("无法转换到VOICE_TTS状态")
        else:
            logger.info("状态已转换到VOICE_TTS")
    
    def handle_voice_tts_complete(self, data: Any = None) -> None:
        """
        处理语音TTS完成事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理语音TTS完成事件")
        success = self.state_manager.set_state(State.IDLE)
        if not success:
            logger.warning("无法转换到IDLE状态")
        else:
            logger.info("状态已转换到IDLE")
    
    def handle_voice_call_start(self, data: Any = None) -> None:
        """
        处理语音通话开始事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理语音通话开始事件")
        success = self.state_manager.set_state(State.VOICE_CALL)
        if not success:
            logger.warning("无法转换到VOICE_CALL状态")
        else:
            logger.info("状态已转换到VOICE_CALL")
    
    def handle_voice_call_end(self, data: Any = None) -> None:
        """
        处理语音通话结束事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理语音通话结束事件")
        success = self.state_manager.set_state(State.IDLE)
        if not success:
            logger.warning("无法转换到IDLE状态")
        else:
            logger.info("状态已转换到IDLE")
    
    def handle_error_occurred(self, data: Any = None) -> None:
        """
        处理错误发生事件
        
        Args:
            data: 事件数据，应包含错误信息
        """
        logger.error(f"处理错误发生事件: {data}")
        success = self.state_manager.set_state(State.ERROR)
        if not success:
            logger.warning("无法转换到ERROR状态")
        else:
            logger.info("状态已转换到ERROR")
    
    def handle_reset_state(self, data: Any = None) -> None:
        """
        处理重置状态事件
        
        Args:
            data: 事件数据
        """
        logger.info("处理重置状态事件")
        success = self.state_manager.reset_to_idle()
        if not success:
            logger.warning("无法重置到IDLE状态")
        else:
            logger.info("状态已重置到IDLE")
    
    def unregister_all_handlers(self) -> None:
        """注销所有事件处理器"""
        # 注销所有处理器
        self.event_manager.unregister_handler(Event.TEXT_START, self.handle_text_start)
        self.event_manager.unregister_handler(Event.TEXT_SSE_COMPLETE, self.handle_text_sse_complete)
        self.event_manager.unregister_handler(Event.TEXT_TTS_COMPLETE, self.handle_text_tts_complete)
        self.event_manager.unregister_handler(Event.VOICE_RECORD_START, self.handle_voice_record_start)
        self.event_manager.unregister_handler(Event.VOICE_STT_COMPLETE, self.handle_voice_stt_complete)
        self.event_manager.unregister_handler(Event.VOICE_SSE_COMPLETE, self.handle_voice_sse_complete)
        self.event_manager.unregister_handler(Event.VOICE_TTS_COMPLETE, self.handle_voice_tts_complete)
        self.event_manager.unregister_handler(Event.VOICE_CALL_START, self.handle_voice_call_start)
        self.event_manager.unregister_handler(Event.VOICE_CALL_END, self.handle_voice_call_end)
        self.event_manager.unregister_handler(Event.ERROR_OCCURRED, self.handle_error_occurred)
        self.event_manager.unregister_handler(Event.RESET_STATE, self.handle_reset_state)
        
        logger.info("所有事件处理器已注销")
    
    def get_handler_info(self) -> dict:
        """
        获取处理器信息
        
        Returns:
            处理器信息字典
        """
        return {
            'state_manager': self.state_manager.get_state_info(),
            'event_manager': self.event_manager.get_manager_info()
        }


# 便捷函数
def create_event_handlers(state_manager: StateManager, event_manager: EventManager) -> EventHandlers:
    """
    创建事件处理器
    
    Args:
        state_manager: 状态管理器
        event_manager: 事件管理器
    
    Returns:
        事件处理器实例
    """
    return EventHandlers(state_manager, event_manager)
