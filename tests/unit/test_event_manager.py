"""
事件管理器单元测试

测试事件管理器的各种功能，包括事件注册、触发、处理等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

import unittest
import asyncio
import time
from unittest.mock import Mock, patch
from core.event_manager.event_manager import EventManager, Event, create_event_manager, get_event_name, is_valid_event
from core.event_manager.event_handlers import EventHandlers
from core.state_manager.state_manager import StateManager, State


class TestEventManager(unittest.TestCase):
    """事件管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = EventManager()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.manager.get_queue_size(), 0)
        self.assertFalse(self.manager.event_processing)
        self.assertEqual(len(self.manager.get_event_history()), 0)
    
    def test_register_handler(self):
        """测试注册事件处理器"""
        handler = Mock()
        self.manager.register_handler(Event.TEXT_START, handler)
        
        # 检查处理器已注册
        registered = self.manager.get_registered_handlers()
        self.assertEqual(registered['text_start'], 1)
    
    def test_unregister_handler(self):
        """测试注销事件处理器"""
        handler = Mock()
        self.manager.register_handler(Event.TEXT_START, handler)
        self.manager.unregister_handler(Event.TEXT_START, handler)
        
        # 检查处理器已注销
        registered = self.manager.get_registered_handlers()
        self.assertEqual(registered['text_start'], 0)
    
    def test_emit_event(self):
        """测试触发事件"""
        handler = Mock()
        self.manager.register_handler(Event.TEXT_START, handler)
        
        # 触发事件
        self.manager.emit_event(Event.TEXT_START, {'message': 'test'})
        
        # 检查事件已添加到队列
        self.assertEqual(self.manager.get_queue_size(), 1)
        
        # 检查统计
        stats = self.manager.get_event_stats()
        self.assertEqual(stats['text_start'], 1)
    
    def test_emit_event_sync(self):
        """测试同步触发事件"""
        handler = Mock()
        self.manager.register_handler(Event.TEXT_START, handler)
        
        # 同步触发事件
        self.manager.emit_event_sync(Event.TEXT_START, {'message': 'test'})
        
        # 检查处理器被调用
        handler.assert_called_once_with({'message': 'test'})
        
        # 检查统计
        stats = self.manager.get_event_stats()
        self.assertEqual(stats['text_start'], 1)
    
    def test_event_history(self):
        """测试事件历史"""
        # 触发几个事件
        self.manager.emit_event(Event.TEXT_START, {'data': 'test1'})
        self.manager.emit_event(Event.TEXT_SSE_COMPLETE, {'data': 'test2'})
        
        # 检查历史
        history = self.manager.get_event_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['event_type'], 'text_start')
        self.assertEqual(history[1]['event_type'], 'text_sse_complete')
    
    def test_clear_event_history(self):
        """测试清空事件历史"""
        # 触发事件
        self.manager.emit_event(Event.TEXT_START)
        
        # 清空历史
        self.manager.clear_event_history()
        
        # 检查历史已清空
        self.assertEqual(len(self.manager.get_event_history()), 0)
    
    def test_event_stats(self):
        """测试事件统计"""
        # 触发多个事件
        self.manager.emit_event(Event.TEXT_START)
        self.manager.emit_event(Event.TEXT_START)
        self.manager.emit_event(Event.TEXT_SSE_COMPLETE)
        
        # 检查统计
        stats = self.manager.get_event_stats()
        self.assertEqual(stats['text_start'], 2)
        self.assertEqual(stats['text_sse_complete'], 1)
    
    def test_reset_event_stats(self):
        """测试重置事件统计"""
        # 触发事件
        self.manager.emit_event(Event.TEXT_START)
        
        # 重置统计
        self.manager.reset_event_stats()
        
        # 检查统计已重置
        stats = self.manager.get_event_stats()
        self.assertEqual(stats['text_start'], 0)
    
    def test_queue_size_limit(self):
        """测试队列大小限制"""
        # 设置小的队列大小
        manager = EventManager(max_queue_size=2)
        
        # 触发超过限制的事件
        manager.emit_event(Event.TEXT_START)
        manager.emit_event(Event.TEXT_START)
        manager.emit_event(Event.TEXT_START)  # 这个应该被丢弃
        
        # 检查队列大小
        self.assertEqual(manager.get_queue_size(), 2)
    
    def test_clear_queue(self):
        """测试清空队列"""
        # 触发事件
        self.manager.emit_event(Event.TEXT_START)
        self.manager.emit_event(Event.TEXT_SSE_COMPLETE)
        
        # 清空队列
        self.manager.clear_queue()
        
        # 检查队列已清空
        self.assertEqual(self.manager.get_queue_size(), 0)
    
    def test_wait_for_event(self):
        """测试等待事件"""
        # 在另一个线程中触发事件
        def trigger_event():
            time.sleep(0.1)
            self.manager.emit_event(Event.TEXT_START, {'data': 'test'})
        
        import threading
        thread = threading.Thread(target=trigger_event)
        thread.start()
        
        # 等待事件
        result = self.manager.wait_for_event(Event.TEXT_START, timeout=1.0)
        
        thread.join()
        
        # 检查结果
        self.assertIsNotNone(result)
        self.assertEqual(result['data'], 'test')
    
    def test_wait_for_event_timeout(self):
        """测试等待事件超时"""
        # 等待不存在的事件
        result = self.manager.wait_for_event(Event.TEXT_START, timeout=0.1)
        
        # 检查超时返回None
        self.assertIsNone(result)
    
    def test_get_manager_info(self):
        """测试获取管理器信息"""
        info = self.manager.get_manager_info()
        
        self.assertIn('queue_size', info)
        self.assertIn('processing', info)
        self.assertIn('max_queue_size', info)
        self.assertIn('history_size', info)
        self.assertIn('registered_handlers', info)
        self.assertIn('event_stats', info)
    
    def test_shutdown(self):
        """测试关闭管理器"""
        # 关闭管理器
        self.manager.shutdown()
        
        # 检查执行器已关闭
        self.assertTrue(self.manager.executor._shutdown)


class TestEventManagerAsync(unittest.TestCase):
    """事件管理器异步测试"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = EventManager()
    
    async def test_async_event_processing(self):
        """测试异步事件处理"""
        handler = Mock()
        self.manager.register_handler(Event.TEXT_START, handler)
        
        # 触发事件
        self.manager.emit_event(Event.TEXT_START, {'data': 'test'})
        
        # 等待处理完成
        await asyncio.sleep(0.1)
        
        # 检查处理器被调用
        handler.assert_called_once_with({'data': 'test'})
    
    async def test_async_handler(self):
        """测试异步处理器"""
        async def async_handler(data):
            await asyncio.sleep(0.01)
            return data
        
        self.manager.register_handler(Event.TEXT_START, async_handler)
        
        # 触发事件
        self.manager.emit_event(Event.TEXT_START, {'data': 'test'})
        
        # 等待处理完成
        await asyncio.sleep(0.1)
        
        # 检查事件已处理
        self.assertEqual(self.manager.get_queue_size(), 0)


class TestEventHandlers(unittest.TestCase):
    """事件处理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.state_manager = StateManager()
        self.event_manager = EventManager()
        self.handlers = EventHandlers(self.state_manager, self.event_manager)
    
    def test_handle_text_start(self):
        """测试处理文本开始事件"""
        self.handlers.handle_text_start({'message': 'test'})
        self.assertEqual(self.state_manager.get_state(), State.TEXT_SSE)
    
    def test_handle_text_sse_complete(self):
        """测试处理文本SSE完成事件"""
        # 先设置到TEXT_SSE状态
        self.state_manager.set_state(State.TEXT_SSE)
        self.handlers.handle_text_sse_complete({'result': 'test'})
        self.assertEqual(self.state_manager.get_state(), State.TEXT_TTS)
    
    def test_handle_text_tts_complete(self):
        """测试处理文本TTS完成事件"""
        # 先设置到TEXT_TTS状态
        self.state_manager.set_state(State.TEXT_SSE)
        self.state_manager.set_state(State.TEXT_TTS)
        self.handlers.handle_text_tts_complete({'audio': 'test'})
        self.assertEqual(self.state_manager.get_state(), State.IDLE)
    
    def test_handle_voice_record_start(self):
        """测试处理语音录音开始事件"""
        self.handlers.handle_voice_record_start({'duration': 5})
        self.assertEqual(self.state_manager.get_state(), State.VOICE_STT)
    
    def test_handle_voice_stt_complete(self):
        """测试处理语音STT完成事件"""
        # 先设置到VOICE_STT状态
        self.state_manager.set_state(State.VOICE_STT)
        self.handlers.handle_voice_stt_complete({'text': 'test'})
        self.assertEqual(self.state_manager.get_state(), State.VOICE_SSE)
    
    def test_handle_voice_sse_complete(self):
        """测试处理语音SSE完成事件"""
        # 先设置到VOICE_SSE状态
        self.state_manager.set_state(State.VOICE_STT)
        self.state_manager.set_state(State.VOICE_SSE)
        self.handlers.handle_voice_sse_complete({'response': 'test'})
        self.assertEqual(self.state_manager.get_state(), State.VOICE_TTS)
    
    def test_handle_voice_tts_complete(self):
        """测试处理语音TTS完成事件"""
        # 先设置到VOICE_TTS状态
        self.state_manager.set_state(State.VOICE_STT)
        self.state_manager.set_state(State.VOICE_SSE)
        self.state_manager.set_state(State.VOICE_TTS)
        self.handlers.handle_voice_tts_complete({'audio': 'test'})
        self.assertEqual(self.state_manager.get_state(), State.IDLE)
    
    def test_handle_voice_call_start(self):
        """测试处理语音通话开始事件"""
        self.handlers.handle_voice_call_start({'call_id': 'test'})
        self.assertEqual(self.state_manager.get_state(), State.VOICE_CALL)
    
    def test_handle_voice_call_end(self):
        """测试处理语音通话结束事件"""
        # 先设置到VOICE_CALL状态
        self.state_manager.set_state(State.VOICE_CALL)
        self.handlers.handle_voice_call_end({'duration': 10})
        self.assertEqual(self.state_manager.get_state(), State.IDLE)
    
    def test_handle_error_occurred(self):
        """测试处理错误发生事件"""
        self.handlers.handle_error_occurred({'error': 'test error'})
        self.assertEqual(self.state_manager.get_state(), State.ERROR)
    
    def test_handle_reset_state(self):
        """测试处理重置状态事件"""
        # 先设置到其他状态
        self.state_manager.set_state(State.TEXT_SSE)
        self.handlers.handle_reset_state()
        self.assertEqual(self.state_manager.get_state(), State.IDLE)
    
    def test_unregister_all_handlers(self):
        """测试注销所有处理器"""
        # 检查处理器已注册
        registered = self.event_manager.get_registered_handlers()
        self.assertGreater(registered['text_start'], 0)
        
        # 注销所有处理器
        self.handlers.unregister_all_handlers()
        
        # 检查处理器已注销
        registered = self.event_manager.get_registered_handlers()
        self.assertEqual(registered['text_start'], 0)
    
    def test_get_handler_info(self):
        """测试获取处理器信息"""
        info = self.handlers.get_handler_info()
        
        self.assertIn('state_manager', info)
        self.assertIn('event_manager', info)


class TestEventManagerUtilityFunctions(unittest.TestCase):
    """事件管理器工具函数测试"""
    
    def test_create_event_manager(self):
        """测试创建事件管理器"""
        manager = create_event_manager(max_queue_size=500)
        self.assertIsInstance(manager, EventManager)
        self.assertEqual(manager.max_queue_size, 500)
    
    def test_get_event_name(self):
        """测试获取事件名称"""
        self.assertEqual(get_event_name(Event.TEXT_START), 'text_start')
        self.assertEqual(get_event_name(Event.ERROR_OCCURRED), 'error_occurred')
    
    def test_is_valid_event(self):
        """测试事件名称有效性检查"""
        self.assertTrue(is_valid_event('text_start'))
        self.assertTrue(is_valid_event('error_occurred'))
        self.assertFalse(is_valid_event('invalid_event'))
        self.assertFalse(is_valid_event(''))
        self.assertFalse(is_valid_event(None))


if __name__ == '__main__':
    # 配置日志
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # 运行测试
    unittest.main(verbosity=2)
