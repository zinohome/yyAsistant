"""
端到端测试 - 聊天场景

测试文本聊天、录音聊天、语音通话三个场景的完整流程。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

import unittest
import time
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.state_manager.state_manager import StateManager, State as AppState
from core.event_manager.event_manager import EventManager, Event
from core.event_manager.event_handlers import EventHandlers
from core.websocket_manager.websocket_manager import WebSocketManager
from core.timeout_manager.timeout_manager import TimeoutManager, TimeoutType
from core.error_handler.error_handler import ErrorHandler, ErrorType, ErrorSeverity


class TestChatScenarios(unittest.TestCase):
    """聊天场景测试"""
    
    def setUp(self):
        """测试前准备"""
        self.state_manager = StateManager()
        self.event_manager = EventManager()
        self.websocket_manager = WebSocketManager()
        self.timeout_manager = TimeoutManager()
        self.error_handler = ErrorHandler()
        self.event_handlers = EventHandlers(self.state_manager, self.event_manager)
        
        # 重置状态
        self.state_manager.reset_to_idle()
    
    def test_text_chat_scenario(self):
        """测试文本聊天场景"""
        print("测试文本聊天场景...")
        
        # 1. 初始状态检查
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 初始状态: IDLE")
        
        # 2. 开始文本处理
        success = self.state_manager.set_state(AppState.TEXT_SSE)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.TEXT_SSE)
        print("  ✅ 状态转换: IDLE -> TEXT_SSE")
        
        # 3. 启动SSE超时
        timeout_id = f"text_sse_{int(time.time())}"
        self.timeout_manager.start_timeout(
            timeout_id=timeout_id,
            content_length=100,
            timeout_type=TimeoutType.SSE
        )
        print("  ✅ SSE超时已启动")
        
        # 4. 触发TEXT_START事件
        self.event_manager.emit_event_sync(Event.TEXT_START, {
            'message': '测试消息',
            'timestamp': time.time()
        })
        print("  ✅ TEXT_START事件已触发")
        
        # 5. SSE完成，转换到TEXT_TTS
        success = self.state_manager.set_state(AppState.TEXT_TTS)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.TEXT_TTS)
        print("  ✅ 状态转换: TEXT_SSE -> TEXT_TTS")
        
        # 6. 取消SSE超时，启动TTS超时
        self.timeout_manager.cancel_timeout(timeout_id)
        tts_timeout_id = f"text_tts_{int(time.time())}"
        self.timeout_manager.start_timeout(
            timeout_id=tts_timeout_id,
            content_length=100,
            timeout_type=TimeoutType.TTS
        )
        print("  ✅ TTS超时已启动")
        
        # 7. 触发TEXT_SSE_COMPLETE事件
        self.event_manager.emit_event_sync(Event.TEXT_SSE_COMPLETE, {
            'message_id': 'test_message',
            'content': '测试响应',
            'timestamp': time.time()
        })
        print("  ✅ TEXT_SSE_COMPLETE事件已触发")
        
        # 8. TTS完成，转换到IDLE
        success = self.state_manager.set_state(AppState.IDLE)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 状态转换: TEXT_TTS -> IDLE")
        
        # 9. 取消TTS超时
        self.timeout_manager.cancel_timeout(tts_timeout_id)
        print("  ✅ TTS超时已取消")
        
        # 10. 触发TEXT_TTS_COMPLETE事件
        self.event_manager.emit_event_sync(Event.TEXT_TTS_COMPLETE, {
            'message_id': 'test_message',
            'timestamp': time.time()
        })
        print("  ✅ TEXT_TTS_COMPLETE事件已触发")
        
        print("  🎉 文本聊天场景测试完成")
    
    def test_voice_recording_scenario(self):
        """测试录音聊天场景"""
        print("测试录音聊天场景...")
        
        # 1. 初始状态检查
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 初始状态: IDLE")
        
        # 2. 开始录音
        success = self.state_manager.set_state(AppState.VOICE_STT)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.VOICE_STT)
        print("  ✅ 状态转换: IDLE -> VOICE_STT")
        
        # 3. 启动STT超时
        timeout_id = f"voice_stt_{int(time.time())}"
        self.timeout_manager.start_timeout(
            timeout_id=timeout_id,
            content_length=50,
            timeout_type=TimeoutType.STT
        )
        print("  ✅ STT超时已启动")
        
        # 4. 触发VOICE_RECORD_START事件
        self.event_manager.emit_event_sync(Event.VOICE_RECORD_START, {
            'duration': 5,
            'timestamp': time.time()
        })
        print("  ✅ VOICE_RECORD_START事件已触发")
        
        # 5. STT完成，转换到VOICE_SSE
        success = self.state_manager.set_state(AppState.VOICE_SSE)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.VOICE_SSE)
        print("  ✅ 状态转换: VOICE_STT -> VOICE_SSE")
        
        # 6. 取消STT超时，启动SSE超时
        self.timeout_manager.cancel_timeout(timeout_id)
        sse_timeout_id = f"voice_sse_{int(time.time())}"
        self.timeout_manager.start_timeout(
            timeout_id=sse_timeout_id,
            content_length=100,
            timeout_type=TimeoutType.SSE
        )
        print("  ✅ SSE超时已启动")
        
        # 7. 触发VOICE_STT_COMPLETE事件
        self.event_manager.emit_event_sync(Event.VOICE_STT_COMPLETE, {
            'text': '测试语音转录',
            'timestamp': time.time()
        })
        print("  ✅ VOICE_STT_COMPLETE事件已触发")
        
        # 8. SSE完成，转换到VOICE_TTS
        success = self.state_manager.set_state(AppState.VOICE_TTS)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.VOICE_TTS)
        print("  ✅ 状态转换: VOICE_SSE -> VOICE_TTS")
        
        # 9. 取消SSE超时，启动TTS超时
        self.timeout_manager.cancel_timeout(sse_timeout_id)
        tts_timeout_id = f"voice_tts_{int(time.time())}"
        self.timeout_manager.start_timeout(
            timeout_id=tts_timeout_id,
            content_length=100,
            timeout_type=TimeoutType.TTS
        )
        print("  ✅ TTS超时已启动")
        
        # 10. 触发VOICE_SSE_COMPLETE事件
        self.event_manager.emit_event_sync(Event.VOICE_SSE_COMPLETE, {
            'message_id': 'test_voice_message',
            'content': '测试语音响应',
            'timestamp': time.time()
        })
        print("  ✅ VOICE_SSE_COMPLETE事件已触发")
        
        # 11. TTS完成，转换到IDLE
        success = self.state_manager.set_state(AppState.IDLE)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 状态转换: VOICE_TTS -> IDLE")
        
        # 12. 取消TTS超时
        self.timeout_manager.cancel_timeout(tts_timeout_id)
        print("  ✅ TTS超时已取消")
        
        # 13. 触发VOICE_TTS_COMPLETE事件
        self.event_manager.emit_event_sync(Event.VOICE_TTS_COMPLETE, {
            'message_id': 'test_voice_message',
            'timestamp': time.time()
        })
        print("  ✅ VOICE_TTS_COMPLETE事件已触发")
        
        print("  🎉 录音聊天场景测试完成")
    
    def test_voice_call_scenario(self):
        """测试语音通话场景"""
        print("测试语音通话场景...")
        
        # 1. 初始状态检查
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 初始状态: IDLE")
        
        # 2. 开始语音通话
        success = self.state_manager.set_state(AppState.VOICE_CALL)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.VOICE_CALL)
        print("  ✅ 状态转换: IDLE -> VOICE_CALL")
        
        # 3. 触发VOICE_CALL_START事件
        self.event_manager.emit_event_sync(Event.VOICE_CALL_START, {
            'call_id': 'test_call',
            'timestamp': time.time()
        })
        print("  ✅ VOICE_CALL_START事件已触发")
        
        # 4. 模拟通话过程
        time.sleep(0.1)  # 模拟通话时间
        
        # 5. 结束语音通话
        success = self.state_manager.set_state(AppState.IDLE)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 状态转换: VOICE_CALL -> IDLE")
        
        # 6. 触发VOICE_CALL_END事件
        self.event_manager.emit_event_sync(Event.VOICE_CALL_END, {
            'call_id': 'test_call',
            'duration': 10,
            'timestamp': time.time()
        })
        print("  ✅ VOICE_CALL_END事件已触发")
        
        print("  🎉 语音通话场景测试完成")
    
    def test_error_handling_scenario(self):
        """测试错误处理场景"""
        print("测试错误处理场景...")
        
        # 1. 初始状态检查
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 初始状态: IDLE")
        
        # 2. 模拟WebSocket连接错误
        error_result = self.error_handler.handle_error(
            ErrorType.WEBSOCKET_CONNECTION,
            '连接失败',
            ErrorSeverity.HIGH
        )
        self.assertIsNotNone(error_result)
        print("  ✅ WebSocket错误已处理")
        
        # 3. 检查错误统计
        error_stats = self.error_handler.get_error_stats()
        self.assertGreater(error_stats['websocket_connection'], 0)
        print("  ✅ 错误统计已更新")
        
        # 4. 模拟超时错误
        error_result = self.error_handler.handle_error(
            ErrorType.TIMEOUT,
            '处理超时',
            ErrorSeverity.HIGH
        )
        self.assertIsNotNone(error_result)
        print("  ✅ 超时错误已处理")
        
        # 5. 模拟状态转换错误
        error_result = self.error_handler.handle_error(
            ErrorType.STATE_TRANSITION,
            '无效状态转换',
            ErrorSeverity.MEDIUM
        )
        self.assertIsNotNone(error_result)
        print("  ✅ 状态转换错误已处理")
        
        # 6. 检查错误历史
        error_history = self.error_handler.get_error_history(limit=3)
        self.assertEqual(len(error_history), 3)
        print("  ✅ 错误历史已记录")
        
        print("  🎉 错误处理场景测试完成")
    
    def test_timeout_handling_scenario(self):
        """测试超时处理场景"""
        print("测试超时处理场景...")
        
        # 1. 启动超时
        timeout_id = f"test_timeout_{int(time.time())}"
        self.timeout_manager.start_timeout(
            timeout_id=timeout_id,
            content_length=100,
            timeout_type=TimeoutType.SSE
        )
        print("  ✅ 超时已启动")
        
        # 2. 检查超时信息
        timeout_info = self.timeout_manager.get_timeout_info(timeout_id)
        self.assertIsNotNone(timeout_info)
        self.assertTrue(timeout_info['active'])
        print("  ✅ 超时信息已获取")
        
        # 3. 延长超时
        success = self.timeout_manager.extend_timeout(timeout_id, 30)
        self.assertTrue(success)
        print("  ✅ 超时已延长")
        
        # 4. 取消超时
        success = self.timeout_manager.cancel_timeout(timeout_id)
        self.assertTrue(success)
        print("  ✅ 超时已取消")
        
        # 5. 检查活跃超时
        active_timeouts = self.timeout_manager.get_active_timeouts()
        self.assertEqual(len(active_timeouts), 0)
        print("  ✅ 活跃超时已清空")
        
        print("  🎉 超时处理场景测试完成")
    
    def test_state_locking_scenario(self):
        """测试状态锁定场景"""
        print("测试状态锁定场景...")
        
        # 1. 初始状态检查
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 初始状态: IDLE")
        
        # 2. 锁定状态
        self.state_manager.lock_state(duration=5000)  # 5秒锁定
        self.assertTrue(self.state_manager.is_state_locked())
        print("  ✅ 状态已锁定")
        
        # 3. 尝试状态转换（应该失败）
        success = self.state_manager.set_state(AppState.TEXT_SSE)
        self.assertFalse(success)
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 状态转换被阻止")
        
        # 4. 解锁状态
        self.state_manager.unlock_state()
        self.assertFalse(self.state_manager.is_state_locked())
        print("  ✅ 状态已解锁")
        
        # 5. 状态转换现在应该成功
        success = self.state_manager.set_state(AppState.TEXT_SSE)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.TEXT_SSE)
        print("  ✅ 状态转换成功")
        
        print("  🎉 状态锁定场景测试完成")
    
    def test_state_rollback_scenario(self):
        """测试状态回滚场景"""
        print("测试状态回滚场景...")
        
        # 1. 初始状态检查
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 初始状态: IDLE")
        
        # 2. 转换到TEXT_SSE
        success = self.state_manager.set_state(AppState.TEXT_SSE)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.TEXT_SSE)
        print("  ✅ 状态转换: IDLE -> TEXT_SSE")
        
        # 3. 转换到TEXT_TTS
        success = self.state_manager.set_state(AppState.TEXT_TTS)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.TEXT_TTS)
        print("  ✅ 状态转换: TEXT_SSE -> TEXT_TTS")
        
        # 4. 检查状态历史
        history = self.state_manager.get_state_history()
        self.assertEqual(len(history), 2)
        print("  ✅ 状态历史已记录")
        
        # 5. 回滚状态
        success = self.state_manager.rollback_state()
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.TEXT_SSE)
        print("  ✅ 状态已回滚")
        
        # 6. 再次回滚
        success = self.state_manager.rollback_state()
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 状态已再次回滚")
        
        print("  🎉 状态回滚场景测试完成")


def run_e2e_tests():
    """运行端到端测试"""
    print("🚀 开始端到端测试...")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChatScenarios)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 所有端到端测试通过！")
        return True
    else:
        print("❌ 部分测试失败")
        return False


if __name__ == '__main__':
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
