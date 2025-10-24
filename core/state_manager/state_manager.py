"""
状态管理模块

提供统一的状态管理功能，包括状态定义、状态转换、状态锁定等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

from typing import Dict, List, Optional
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class State(Enum):
    """状态枚举"""
    IDLE = 'idle'                    # 空闲状态
    TEXT_SSE = 'text_sse'           # 文本SSE处理中
    TEXT_TTS = 'text_tts'           # 文本TTS处理中
    VOICE_STT = 'voice_stt'         # 语音STT处理中
    VOICE_SSE = 'voice_sse'         # 语音SSE处理中
    VOICE_TTS = 'voice_tts'         # 语音TTS处理中
    VOICE_CALL = 'voice_call'       # 语音通话中
    ERROR = 'error'                  # 错误状态


class StateManager:
    """统一状态管理器"""
    
    def __init__(self):
        """初始化状态管理器"""
        self.current_state = State.IDLE
        self.state_history = []
        self.state_locked = False
        self.state_transitions = {
            State.IDLE: [State.TEXT_SSE, State.VOICE_STT, State.VOICE_CALL],
            State.TEXT_SSE: [State.TEXT_TTS, State.IDLE, State.ERROR],
            State.TEXT_TTS: [State.IDLE, State.ERROR],
            State.VOICE_STT: [State.VOICE_SSE, State.IDLE, State.ERROR],
            State.VOICE_SSE: [State.VOICE_TTS, State.IDLE, State.ERROR],
            State.VOICE_TTS: [State.IDLE, State.ERROR],
            State.VOICE_CALL: [State.IDLE, State.ERROR],
            State.ERROR: [State.IDLE]
        }
        self.state_change_callbacks = []
        self.state_lock_time = None
        self.max_lock_duration = 300  # 5分钟最大锁定时间
    
    def set_state(self, new_state: State) -> bool:
        """
        设置状态
        
        Args:
            new_state: 新状态
        
        Returns:
            是否设置成功
        """
        if self.state_locked:
            logger.warning(f"状态已锁定，无法从 {self.current_state.value} 转换到 {new_state.value}")
            return False
        
        if not self.can_transition(new_state):
            logger.warning(f"无效的状态转换：从 {self.current_state.value} 到 {new_state.value}")
            return False
        
        # 记录状态历史
        previous_state = self.current_state
        self.state_history.append({
            'from': previous_state,
            'to': new_state,
            'timestamp': time.time()
        })
        
        # 更新状态
        self.current_state = new_state
        
        # 触发状态变化回调
        for callback in self.state_change_callbacks:
            try:
                callback(previous_state, new_state)
            except Exception as e:
                logger.error(f"状态变化回调执行失败: {e}")
        
        logger.info(f"状态转换成功: {previous_state.value} -> {new_state.value}")
        return True
    
    def get_state(self) -> State:
        """
        获取当前状态
        
        Returns:
            当前状态
        """
        return self.current_state
    
    def can_transition(self, new_state: State) -> bool:
        """
        检查状态转换是否合法
        
        Args:
            new_state: 目标状态
        
        Returns:
            是否可以转换
        """
        return new_state in self.state_transitions.get(self.current_state, [])
    
    def lock_state(self, duration: Optional[int] = None) -> None:
        """
        锁定状态
        
        Args:
            duration: 锁定持续时间（秒），None表示永久锁定
        """
        self.state_locked = True
        self.state_lock_time = time.time()
        if duration:
            self.max_lock_duration = duration
        logger.info(f"状态已锁定，持续时间: {duration}秒" if duration else "状态已永久锁定")
    
    def unlock_state(self) -> None:
        """解锁状态"""
        self.state_locked = False
        self.state_lock_time = None
        logger.info("状态已解锁")
    
    def is_state_locked(self) -> bool:
        """
        检查状态是否被锁定
        
        Returns:
            是否被锁定
        """
        if not self.state_locked:
            return False
        
        # 检查锁定是否超时
        if self.state_lock_time and time.time() - self.state_lock_time > self.max_lock_duration:
            logger.warning("状态锁定超时，自动解锁")
            self.unlock_state()
            return False
        
        return True
    
    def rollback_state(self) -> bool:
        """
        回滚状态
        
        Returns:
            是否回滚成功
        """
        if not self.state_history:
            logger.warning("没有状态历史可以回滚")
            return False
        
        previous_state_info = self.state_history.pop()
        previous_state = previous_state_info['from']
        
        # 直接设置状态，不检查转换规则
        self.current_state = previous_state
        
        logger.info(f"状态已回滚到: {previous_state.value}")
        return True
    
    def get_state_history(self) -> List[Dict]:
        """
        获取状态历史
        
        Returns:
            状态历史列表
        """
        return self.state_history.copy()
    
    def clear_state_history(self) -> None:
        """清空状态历史"""
        self.state_history.clear()
        logger.info("状态历史已清空")
    
    def register_state_change_callback(self, callback) -> None:
        """
        注册状态变化回调
        
        Args:
            callback: 回调函数，接收 (from_state, to_state) 参数
        """
        self.state_change_callbacks.append(callback)
        logger.info("状态变化回调已注册")
    
    def unregister_state_change_callback(self, callback) -> None:
        """
        注销状态变化回调
        
        Args:
            callback: 要注销的回调函数
        """
        if callback in self.state_change_callbacks:
            self.state_change_callbacks.remove(callback)
            logger.info("状态变化回调已注销")
    
    def get_available_transitions(self) -> List[State]:
        """
        获取可用的状态转换
        
        Returns:
            可转换的状态列表
        """
        return self.state_transitions.get(self.current_state, [])
    
    def force_set_state(self, new_state: State) -> bool:
        """
        强制设置状态（忽略转换规则和锁定）
        
        Args:
            new_state: 新状态
        
        Returns:
            是否设置成功
        """
        previous_state = self.current_state
        self.current_state = new_state
        
        # 记录强制状态变化
        self.state_history.append({
            'from': previous_state,
            'to': new_state,
            'timestamp': time.time(),
            'forced': True
        })
        
        logger.warning(f"强制状态转换: {previous_state.value} -> {new_state.value}")
        return True
    
    def reset_to_idle(self) -> bool:
        """
        重置到空闲状态
        
        Returns:
            是否重置成功
        """
        if self.current_state == State.IDLE:
            return True
        
        # 清空历史并强制设置为IDLE
        self.state_history.clear()
        self.state_locked = False
        self.current_state = State.IDLE
        
        logger.info("状态已重置到空闲状态")
        return True
    
    def get_state_info(self) -> Dict:
        """
        获取状态信息
        
        Returns:
            状态信息字典
        """
        return {
            'current_state': self.current_state.value,
            'is_locked': self.is_state_locked(),
            'lock_time': self.state_lock_time,
            'available_transitions': [state.value for state in self.get_available_transitions()],
            'history_count': len(self.state_history),
            'max_lock_duration': self.max_lock_duration
        }


# 便捷函数
def create_state_manager() -> StateManager:
    """
    创建状态管理器
    
    Returns:
        状态管理器实例
    """
    return StateManager()


def get_state_name(state: State) -> str:
    """
    获取状态名称
    
    Args:
        state: 状态枚举
    
    Returns:
        状态名称
    """
    return state.value


def is_valid_state(state_name: str) -> bool:
    """
    检查状态名称是否有效
    
    Args:
        state_name: 状态名称
    
    Returns:
        是否有效
    """
    try:
        State(state_name)
        return True
    except ValueError:
        return False
