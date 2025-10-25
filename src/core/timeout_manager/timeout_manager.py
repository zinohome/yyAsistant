"""
超时管理模块

提供智能超时管理功能，包括动态超时计算、超时处理等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

from typing import Dict, Any, Optional, Callable
from enum import Enum
import time
import logging
from config.config import get_config

logger = logging.getLogger(__name__)


class TimeoutType(Enum):
    """超时类型枚举"""
    SSE = 'sse'          # Server-Sent Events
    TTS = 'tts'          # Text-to-Speech
    STT = 'stt'          # Speech-to-Text


class TimeoutManager:
    """超时管理器"""
    
    def __init__(self):
        """初始化超时管理器"""
        self.timeout_config = {
            TimeoutType.SSE: {
                'base': get_config('timeouts.sse_base', 30),
                'per_char': get_config('timeouts.sse_per_char', 0.1),
                'max': get_config('timeouts.sse_max', 300)
            },
            TimeoutType.TTS: {
                'base': get_config('timeouts.tts_base', 60),
                'per_char': get_config('timeouts.tts_per_char', 0.2),
                'max': get_config('timeouts.tts_max', 600)
            },
            TimeoutType.STT: {
                'base': get_config('timeouts.stt_base', 30),
                'per_char': get_config('timeouts.stt_per_char', 0.05),
                'max': get_config('timeouts.stt_max', 180)
            }
        }
        
        self.active_timeouts: Dict[str, Dict] = {}
        self.timeout_handlers: Dict[TimeoutType, Callable] = {}
        self.warning_threshold = 0.8  # 警告阈值（80%）
        
    def calculate_timeout(self, content_length: int, timeout_type: TimeoutType) -> int:
        """
        计算动态超时时间
        
        Args:
            content_length: 内容长度
            timeout_type: 超时类型
        
        Returns:
            超时时间（秒）
        """
        config = self.timeout_config.get(timeout_type)
        if not config:
            logger.warning(f"未知的超时类型: {timeout_type}")
            return 30
        
        # 计算动态超时
        base_timeout = config['base']
        per_char_timeout = config['per_char'] * content_length
        max_timeout = config['max']
        
        # 总超时时间 = 基础时间 + 每字符时间
        total_timeout = base_timeout + per_char_timeout
        
        # 限制在最大超时时间内
        final_timeout = min(total_timeout, max_timeout)
        
        logger.debug(f"计算超时时间: {timeout_type.value}, 长度: {content_length}, 超时: {final_timeout}s")
        return int(final_timeout)
    
    def start_timeout(self, timeout_id: str, content_length: int, timeout_type: TimeoutType, 
                     callback: Optional[Callable] = None) -> None:
        """
        启动超时
        
        Args:
            timeout_id: 超时ID
            content_length: 内容长度
            timeout_type: 超时类型
            callback: 超时回调函数
        """
        timeout_duration = self.calculate_timeout(content_length, timeout_type)
        warning_time = timeout_duration * self.warning_threshold
        
        timeout_info = {
            'id': timeout_id,
            'type': timeout_type,
            'duration': timeout_duration,
            'warning_time': warning_time,
            'start_time': time.time(),
            'content_length': content_length,
            'callback': callback,
            'warned': False,
            'active': True
        }
        
        self.active_timeouts[timeout_id] = timeout_info
        
        # 启动超时检查
        self._schedule_timeout_check(timeout_id, warning_time, timeout_duration)
        
        logger.info(f"超时已启动: {timeout_id}, 类型: {timeout_type.value}, 时长: {timeout_duration}s")
    
    def _schedule_timeout_check(self, timeout_id: str, warning_time: float, timeout_duration: int) -> None:
        """安排超时检查"""
        import threading
        
        def check_timeout():
            time.sleep(warning_time)
            self._check_warning(timeout_id)
            
            time.sleep(timeout_duration - warning_time)
            self._check_timeout(timeout_id)
        
        thread = threading.Thread(target=check_timeout, daemon=True)
        thread.start()
    
    def _check_warning(self, timeout_id: str) -> None:
        """检查警告"""
        if timeout_id not in self.active_timeouts:
            return
        
        timeout_info = self.active_timeouts[timeout_id]
        if not timeout_info['active'] or timeout_info['warned']:
            return
        
        timeout_info['warned'] = True
        
        # 调用警告处理器
        if timeout_type in self.timeout_handlers:
            try:
                self.timeout_handlers[timeout_type](timeout_id, 'warning', timeout_info)
            except Exception as e:
                logger.error(f"警告处理器执行失败: {e}")
        
        logger.warning(f"超时警告: {timeout_id} 即将超时")
    
    def _check_timeout(self, timeout_id: str) -> None:
        """检查超时"""
        if timeout_id not in self.active_timeouts:
            return
        
        timeout_info = self.active_timeouts[timeout_id]
        if not timeout_info['active']:
            return
        
        # 标记为超时
        timeout_info['active'] = False
        timeout_info['timed_out'] = True
        
        # 调用超时处理器
        timeout_type = timeout_info['type']
        if timeout_type in self.timeout_handlers:
            try:
                self.timeout_handlers[timeout_type](timeout_id, 'timeout', timeout_info)
            except Exception as e:
                logger.error(f"超时处理器执行失败: {e}")
        
        # 调用回调函数
        if timeout_info['callback']:
            try:
                timeout_info['callback'](timeout_id, timeout_info)
            except Exception as e:
                logger.error(f"超时回调执行失败: {e}")
        
        logger.error(f"超时发生: {timeout_id}")
    
    def cancel_timeout(self, timeout_id: str) -> bool:
        """
        取消超时
        
        Args:
            timeout_id: 超时ID
        
        Returns:
            是否取消成功
        """
        if timeout_id not in self.active_timeouts:
            return False
        
        timeout_info = self.active_timeouts[timeout_id]
        timeout_info['active'] = False
        timeout_info['cancelled'] = True
        
        logger.info(f"超时已取消: {timeout_id}")
        return True
    
    def extend_timeout(self, timeout_id: str, additional_time: int) -> bool:
        """
        延长超时时间
        
        Args:
            timeout_id: 超时ID
            additional_time: 额外时间（秒）
        
        Returns:
            是否延长成功
        """
        if timeout_id not in self.active_timeouts:
            return False
        
        timeout_info = self.active_timeouts[timeout_id]
        if not timeout_info['active']:
            return False
        
        # 延长超时时间
        timeout_info['duration'] += additional_time
        timeout_info['warning_time'] = timeout_info['duration'] * self.warning_threshold
        
        logger.info(f"超时已延长: {timeout_id}, 额外时间: {additional_time}s")
        return True
    
    def get_timeout_info(self, timeout_id: str) -> Optional[Dict[str, Any]]:
        """
        获取超时信息
        
        Args:
            timeout_id: 超时ID
        
        Returns:
            超时信息字典
        """
        if timeout_id not in self.active_timeouts:
            return None
        
        timeout_info = self.active_timeouts[timeout_id]
        elapsed_time = time.time() - timeout_info['start_time']
        remaining_time = timeout_info['duration'] - elapsed_time
        
        return {
            'id': timeout_id,
            'type': timeout_info['type'].value,
            'duration': timeout_info['duration'],
            'elapsed': elapsed_time,
            'remaining': max(0, remaining_time),
            'active': timeout_info['active'],
            'warned': timeout_info.get('warned', False),
            'content_length': timeout_info['content_length']
        }
    
    def get_active_timeouts(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有活跃超时
        
        Returns:
            活跃超时字典
        """
        active = {}
        for timeout_id, timeout_info in self.active_timeouts.items():
            if timeout_info['active']:
                active[timeout_id] = self.get_timeout_info(timeout_id)
        
        return active
    
    def clear_timeout(self, timeout_id: str) -> bool:
        """
        清除超时记录
        
        Args:
            timeout_id: 超时ID
        
        Returns:
            是否清除成功
        """
        if timeout_id in self.active_timeouts:
            del self.active_timeouts[timeout_id]
            logger.info(f"超时记录已清除: {timeout_id}")
            return True
        return False
    
    def clear_all_timeouts(self) -> None:
        """清除所有超时记录"""
        self.active_timeouts.clear()
        logger.info("所有超时记录已清除")
    
    def register_timeout_handler(self, timeout_type: TimeoutType, handler: Callable) -> None:
        """
        注册超时处理器
        
        Args:
            timeout_type: 超时类型
            handler: 处理器函数
        """
        self.timeout_handlers[timeout_type] = handler
        logger.info(f"超时处理器已注册: {timeout_type.value}")
    
    def unregister_timeout_handler(self, timeout_type: TimeoutType) -> None:
        """
        注销超时处理器
        
        Args:
            timeout_type: 超时类型
        """
        if timeout_type in self.timeout_handlers:
            del self.timeout_handlers[timeout_type]
            logger.info(f"超时处理器已注销: {timeout_type.value}")
    
    def handle_timeout(self, timeout_id: str, timeout_type: TimeoutType, 
                    content_length: int) -> Dict[str, Any]:
        """
        处理超时
        
        Args:
            timeout_id: 超时ID
            timeout_type: 超时类型
            content_length: 内容长度
        
        Returns:
            处理结果
        """
        timeout_info = self.get_timeout_info(timeout_id)
        if not timeout_info:
            return {'success': False, 'error': '超时不存在'}
        
        # 检查是否为长文本TTS
        if timeout_type == TimeoutType.TTS and content_length > 1000:
            # 长文本TTS显示警告但继续处理
            return {
                'success': True,
                'action': 'continue',
                'message': '长文本TTS处理中，请耐心等待...',
                'timeout_info': timeout_info
            }
        else:
            # 其他超时停止处理
            return {
                'success': True,
                'action': 'stop',
                'message': '处理超时，已停止',
                'timeout_info': timeout_info
            }
    
    def get_manager_info(self) -> Dict[str, Any]:
        """
        获取管理器信息
        
        Returns:
            管理器信息字典
        """
        return {
            'active_timeouts': len(self.active_timeouts),
            'timeout_config': {
                timeout_type.value: config 
                for timeout_type, config in self.timeout_config.items()
            },
            'warning_threshold': self.warning_threshold,
            'registered_handlers': len(self.timeout_handlers)
        }


# 便捷函数
def create_timeout_manager() -> TimeoutManager:
    """
    创建超时管理器
    
    Returns:
        超时管理器实例
    """
    return TimeoutManager()


def get_timeout_type_name(timeout_type: TimeoutType) -> str:
    """
    获取超时类型名称
    
    Args:
        timeout_type: 超时类型枚举
    
    Returns:
        类型名称
    """
    return timeout_type.value


def is_valid_timeout_type(type_name: str) -> bool:
    """
    检查超时类型名称是否有效
    
    Args:
        type_name: 类型名称
    
    Returns:
        是否有效
    """
    try:
        TimeoutType(type_name)
        return True
    except ValueError:
        return False
