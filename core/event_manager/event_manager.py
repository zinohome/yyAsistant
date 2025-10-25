"""
事件管理模块

提供统一的事件管理功能，包括事件定义、事件处理、事件队列等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

from typing import Dict, List, Callable, Any, Optional
from enum import Enum
import asyncio
import time
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class Event(Enum):
    """事件枚举"""
    TEXT_START = 'text_start'                    # 文本处理开始
    TEXT_SSE_COMPLETE = 'text_sse_complete'      # 文本SSE完成
    TEXT_TTS_COMPLETE = 'text_tts_complete'      # 文本TTS完成
    VOICE_RECORD_START = 'voice_record_start'    # 语音录音开始
    VOICE_STT_COMPLETE = 'voice_stt_complete'    # 语音STT完成
    VOICE_SSE_COMPLETE = 'voice_sse_complete'    # 语音SSE完成
    VOICE_TTS_COMPLETE = 'voice_tts_complete'    # 语音TTS完成
    VOICE_CALL_START = 'voice_call_start'        # 语音通话开始
    VOICE_CALL_END = 'voice_call_end'            # 语音通话结束
    ERROR_OCCURRED = 'error_occurred'            # 错误发生
    RESET_STATE = 'reset_state'                   # 重置状态


class EventManager:
    """事件管理器"""
    
    def __init__(self, max_queue_size: int = 1000):
        """
        初始化事件管理器
        
        Args:
            max_queue_size: 最大队列大小
        """
        self.event_handlers: Dict[Event, List[Callable]] = {}
        self.event_queue: List[tuple] = []
        self.event_processing = False
        self.max_queue_size = max_queue_size
        self.event_history: List[Dict] = []
        self.max_history_size = 100
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.event_stats: Dict[Event, int] = {event: 0 for event in Event}
        
    def register_handler(self, event_type: Event, handler: Callable) -> None:
        """
        注册事件处理器
        
        Args:
            event_type: 事件类型
            handler: 处理器函数
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"事件处理器已注册: {event_type.value}")
    
    def unregister_handler(self, event_type: Event, handler: Callable) -> None:
        """
        注销事件处理器
        
        Args:
            event_type: 事件类型
            handler: 要注销的处理器函数
        """
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.info(f"事件处理器已注销: {event_type.value}")
    
    def emit_event(self, event_type: Event, data: Any = None) -> None:
        """
        触发事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        # 检查队列大小
        if len(self.event_queue) >= self.max_queue_size:
            logger.warning(f"事件队列已满，丢弃事件: {event_type.value}")
            return
        
        # 添加到队列
        self.event_queue.append((event_type, data, time.time()))
        
        # 更新统计
        self.event_stats[event_type] += 1
        
        # 记录历史
        self._add_to_history(event_type, data)
        
        # 异步处理事件
        if not self.event_processing:
            try:
                asyncio.create_task(self.process_events())
            except RuntimeError:
                # 如果没有事件循环，使用同步处理
                self._process_events_sync()
        
        logger.debug(f"事件已触发: {event_type.value}")
    
    def _process_events_sync(self) -> None:
        """同步处理事件队列（当没有事件循环时使用）"""
        self.event_processing = True
        
        try:
            while self.event_queue:
                event_type, data, timestamp = self.event_queue.pop(0)
                
                if event_type in self.event_handlers:
                    for handler in self.event_handlers[event_type]:
                        try:
                            # 检查处理器是否为协程函数
                            if asyncio.iscoroutinefunction(handler):
                                logger.warning(f"同步上下文中跳过异步处理器: {handler.__name__}")
                                continue
                            handler(data)
                        except Exception as e:
                            logger.error(f"事件处理器执行失败: {e}")
        finally:
            self.event_processing = False
    
    async def process_events(self) -> None:
        """异步处理事件队列"""
        self.event_processing = True
        
        try:
            while self.event_queue:
                event_type, data, timestamp = self.event_queue.pop(0)
                
                if event_type in self.event_handlers:
                    # 并行处理所有处理器
                    tasks = []
                    for handler in self.event_handlers[event_type]:
                        if asyncio.iscoroutinefunction(handler):
                            tasks.append(self._handle_async_event(handler, data))
                        else:
                            tasks.append(self._handle_sync_event(handler, data))
                    
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理延迟
                await asyncio.sleep(0.001)
        except Exception as e:
            logger.error(f"事件处理过程中发生错误: {e}")
        finally:
            self.event_processing = False
    
    async def _handle_async_event(self, handler: Callable, data: Any) -> None:
        """处理异步事件"""
        try:
            await handler(data)
        except Exception as e:
            logger.error(f"异步事件处理器执行失败: {e}")
    
    async def _handle_sync_event(self, handler: Callable, data: Any) -> None:
        """处理同步事件"""
        try:
            # 在线程池中执行同步函数
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, handler, data)
        except Exception as e:
            logger.error(f"同步事件处理器执行失败: {e}")
    
    def _add_to_history(self, event_type: Event, data: Any) -> None:
        """添加到历史记录"""
        self.event_history.append({
            'event_type': event_type.value,
            'data': data,
            'timestamp': time.time()
        })
        
        # 限制历史记录大小
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
    
    def get_event_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取事件历史
        
        Args:
            limit: 限制返回数量
        
        Returns:
            事件历史列表
        """
        if limit:
            return self.event_history[-limit:]
        return self.event_history.copy()
    
    def clear_event_history(self) -> None:
        """清空事件历史"""
        self.event_history.clear()
        logger.info("事件历史已清空")
    
    def get_event_stats(self) -> Dict[str, int]:
        """
        获取事件统计
        
        Returns:
            事件统计字典
        """
        return {event.value: count for event, count in self.event_stats.items()}
    
    def reset_event_stats(self) -> None:
        """重置事件统计"""
        self.event_stats = {event: 0 for event in Event}
        logger.info("事件统计已重置")
    
    def get_queue_size(self) -> int:
        """
        获取队列大小
        
        Returns:
            队列大小
        """
        return len(self.event_queue)
    
    def clear_queue(self) -> None:
        """清空事件队列"""
        self.event_queue.clear()
        logger.info("事件队列已清空")
    
    def get_registered_handlers(self) -> Dict[str, int]:
        """
        获取已注册的处理器
        
        Returns:
            处理器统计字典
        """
        return {
            event.value: len(handlers) 
            for event, handlers in self.event_handlers.items()
        }
    
    def emit_event_sync(self, event_type: Event, data: Any = None) -> None:
        """
        同步触发事件（立即处理）
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        # 对于异步函数，创建新的事件循环
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(handler(data))
                        finally:
                            loop.close()
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"同步事件处理器执行失败: {e}")
        
        # 更新统计和历史
        self.event_stats[event_type] += 1
        self._add_to_history(event_type, data)
    
    def wait_for_event(self, event_type: Event, timeout: float = 10.0) -> Any:
        """
        等待特定事件
        
        Args:
            event_type: 事件类型
            timeout: 超时时间（秒）
        
        Returns:
            事件数据，超时返回None
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查历史记录中是否有目标事件
            for event_info in reversed(self.event_history):
                if event_info['event_type'] == event_type.value:
                    return event_info['data']
            
            time.sleep(0.1)
        
        return None
    
    def get_manager_info(self) -> Dict:
        """
        获取管理器信息
        
        Returns:
            管理器信息字典
        """
        return {
            'queue_size': self.get_queue_size(),
            'processing': self.event_processing,
            'max_queue_size': self.max_queue_size,
            'history_size': len(self.event_history),
            'max_history_size': self.max_history_size,
            'registered_handlers': self.get_registered_handlers(),
            'event_stats': self.get_event_stats()
        }
    
    def shutdown(self) -> None:
        """关闭事件管理器"""
        self.executor.shutdown(wait=True)
        logger.info("事件管理器已关闭")


# 便捷函数
def create_event_manager(max_queue_size: int = 1000) -> EventManager:
    """
    创建事件管理器
    
    Args:
        max_queue_size: 最大队列大小
    
    Returns:
        事件管理器实例
    """
    return EventManager(max_queue_size)


def get_event_name(event: Event) -> str:
    """
    获取事件名称
    
    Args:
        event: 事件枚举
    
    Returns:
        事件名称
    """
    return event.value


def is_valid_event(event_name: str) -> bool:
    """
    检查事件名称是否有效
    
    Args:
        event_name: 事件名称
    
    Returns:
        是否有效
    """
    try:
        Event(event_name)
        return True
    except ValueError:
        return False


# 全局事件管理器实例
event_manager = EventManager()
