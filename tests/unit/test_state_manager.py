"""
状态管理器单元测试

测试状态管理器的各种功能，包括状态转换、锁定、回滚等。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

import unittest
import time
from unittest.mock import Mock, patch
from core.state_manager.state_manager import StateManager, State, create_state_manager, get_state_name, is_valid_state


class TestStateManager(unittest.TestCase):
    """状态管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = StateManager()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.manager.get_state(), State.IDLE)
        self.assertFalse(self.manager.is_state_locked())
    
    def test_set_state_success(self):
        """测试设置状态成功"""
        result = self.manager.set_state(State.TEXT_SSE)
        self.assertTrue(result)
        self.assertEqual(self.manager.get_state(), State.TEXT_SSE)
        self.assertEqual(len(self.manager.get_state_history()), 1)
    
    def test_set_state_invalid_transition(self):
        """测试无效状态转换"""
        # 从IDLE直接转换到ERROR是不允许的
        result = self.manager.set_state(State.ERROR)
        self.assertFalse(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_state_locking(self):
        """测试状态锁定"""
        # 锁定状态
        self.manager.lock_state()
        self.assertTrue(self.manager.is_state_locked())
        
        # 尝试在锁定状态下转换
        result = self.manager.set_state(State.TEXT_SSE)
        self.assertFalse(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
        
        # 解锁状态
        self.manager.unlock_state()
        self.assertFalse(self.manager.is_state_locked())
        
        # 现在可以转换了
        result = self.manager.set_state(State.TEXT_SSE)
        self.assertTrue(result)
    
    def test_state_locking_timeout(self):
        """测试状态锁定超时"""
        # 锁定状态，设置很短的超时时间
        self.manager.lock_state(duration=0.1)  # 0.1秒
        self.assertTrue(self.manager.is_state_locked())
        
        # 等待超时
        time.sleep(0.2)
        
        # 检查锁定状态
        self.assertFalse(self.manager.is_state_locked())
    
    def test_state_rollback(self):
        """测试状态回滚"""
        # 转换到新状态
        self.manager.set_state(State.TEXT_SSE)
        self.assertEqual(self.manager.get_state(), State.TEXT_SSE)
        
        # 回滚状态
        result = self.manager.rollback_state()
        self.assertTrue(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_state_rollback_empty_history(self):
        """测试回滚空历史"""
        result = self.manager.rollback_state()
        self.assertFalse(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_state_history(self):
        """测试状态历史"""
        # 初始状态没有历史
        self.assertEqual(len(self.manager.get_state_history()), 0)
        
        # 转换状态
        self.manager.set_state(State.TEXT_SSE)
        self.manager.set_state(State.TEXT_TTS)
        
        # 检查历史
        history = self.manager.get_state_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['from'], State.IDLE)
        self.assertEqual(history[0]['to'], State.TEXT_SSE)
        self.assertEqual(history[1]['from'], State.TEXT_SSE)
        self.assertEqual(history[1]['to'], State.TEXT_TTS)
    
    def test_clear_state_history(self):
        """测试清空状态历史"""
        # 转换状态产生历史
        self.manager.set_state(State.TEXT_SSE)
        self.assertEqual(len(self.manager.get_state_history()), 1)
        
        # 清空历史
        self.manager.clear_state_history()
        self.assertEqual(len(self.manager.get_state_history()), 0)
    
    def test_state_change_callback(self):
        """测试状态变化回调"""
        callback = Mock()
        self.manager.register_state_change_callback(callback)
        
        # 转换状态
        self.manager.set_state(State.TEXT_SSE)
        
        # 验证回调被调用
        callback.assert_called_once_with(State.IDLE, State.TEXT_SSE)
    
    def test_state_change_callback_exception(self):
        """测试状态变化回调异常处理"""
        def failing_callback(from_state, to_state):
            raise Exception("回调失败")
        
        callback = Mock()
        self.manager.register_state_change_callback(failing_callback)
        self.manager.register_state_change_callback(callback)
        
        # 转换状态（应该不会因为第一个回调失败而停止）
        result = self.manager.set_state(State.TEXT_SSE)
        self.assertTrue(result)
        callback.assert_called_once_with(State.IDLE, State.TEXT_SSE)
    
    def test_unregister_state_change_callback(self):
        """测试注销状态变化回调"""
        callback = Mock()
        self.manager.register_state_change_callback(callback)
        
        # 注销回调
        self.manager.unregister_state_change_callback(callback)
        
        # 转换状态
        self.manager.set_state(State.TEXT_SSE)
        
        # 验证回调未被调用
        callback.assert_not_called()
    
    def test_get_available_transitions(self):
        """测试获取可用转换"""
        # 从IDLE状态可以转换到TEXT_SSE, VOICE_STT, VOICE_CALL
        transitions = self.manager.get_available_transitions()
        expected = [State.TEXT_SSE, State.VOICE_STT, State.VOICE_CALL]
        self.assertEqual(set(transitions), set(expected))
    
    def test_force_set_state(self):
        """测试强制设置状态"""
        # 强制设置到ERROR状态（正常情况下不允许）
        result = self.manager.force_set_state(State.ERROR)
        self.assertTrue(result)
        self.assertEqual(self.manager.get_state(), State.ERROR)
        
        # 检查历史记录
        history = self.manager.get_state_history()
        self.assertEqual(len(history), 1)
        self.assertTrue(history[0]['forced'])
    
    def test_reset_to_idle(self):
        """测试重置到空闲状态"""
        # 转换到其他状态
        self.manager.set_state(State.TEXT_SSE)
        self.manager.set_state(State.TEXT_TTS)
        self.assertEqual(self.manager.get_state(), State.TEXT_TTS)
        
        # 重置到IDLE
        result = self.manager.reset_to_idle()
        self.assertTrue(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
        self.assertEqual(len(self.manager.get_state_history()), 0)
        self.assertFalse(self.manager.is_state_locked())
    
    def test_reset_to_idle_already_idle(self):
        """测试重置到空闲状态（已经是空闲状态）"""
        result = self.manager.reset_to_idle()
        self.assertTrue(result)
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_get_state_info(self):
        """测试获取状态信息"""
        info = self.manager.get_state_info()
        
        self.assertEqual(info['current_state'], 'idle')
        self.assertFalse(info['is_locked'])
        self.assertIsNone(info['lock_time'])
        self.assertEqual(info['history_count'], 0)
        self.assertIn('available_transitions', info)
        self.assertIn('max_lock_duration', info)
    
    def test_state_transitions_workflow(self):
        """测试完整的状态转换工作流"""
        # 文本处理流程
        self.manager.set_state(State.TEXT_SSE)
        self.assertEqual(self.manager.get_state(), State.TEXT_SSE)
        
        self.manager.set_state(State.TEXT_TTS)
        self.assertEqual(self.manager.get_state(), State.TEXT_TTS)
        
        self.manager.set_state(State.IDLE)
        self.assertEqual(self.manager.get_state(), State.IDLE)
        
        # 语音处理流程
        self.manager.set_state(State.VOICE_STT)
        self.assertEqual(self.manager.get_state(), State.VOICE_STT)
        
        self.manager.set_state(State.VOICE_SSE)
        self.assertEqual(self.manager.get_state(), State.VOICE_SSE)
        
        self.manager.set_state(State.VOICE_TTS)
        self.assertEqual(self.manager.get_state(), State.VOICE_TTS)
        
        self.manager.set_state(State.IDLE)
        self.assertEqual(self.manager.get_state(), State.IDLE)
    
    def test_error_state_handling(self):
        """测试错误状态处理"""
        # 转换到错误状态
        self.manager.set_state(State.TEXT_SSE)
        self.manager.set_state(State.ERROR)
        self.assertEqual(self.manager.get_state(), State.ERROR)
        
        # 从错误状态只能转换到IDLE
        transitions = self.manager.get_available_transitions()
        self.assertEqual(transitions, [State.IDLE])
        
        # 转换回IDLE
        self.manager.set_state(State.IDLE)
        self.assertEqual(self.manager.get_state(), State.IDLE)


class TestStateManagerUtilityFunctions(unittest.TestCase):
    """状态管理器工具函数测试"""
    
    def test_create_state_manager(self):
        """测试创建状态管理器"""
        manager = create_state_manager()
        self.assertIsInstance(manager, StateManager)
        self.assertEqual(manager.get_state(), State.IDLE)
    
    def test_get_state_name(self):
        """测试获取状态名称"""
        self.assertEqual(get_state_name(State.IDLE), 'idle')
        self.assertEqual(get_state_name(State.TEXT_SSE), 'text_sse')
        self.assertEqual(get_state_name(State.ERROR), 'error')
    
    def test_is_valid_state(self):
        """测试状态名称有效性检查"""
        self.assertTrue(is_valid_state('idle'))
        self.assertTrue(is_valid_state('text_sse'))
        self.assertTrue(is_valid_state('error'))
        self.assertFalse(is_valid_state('invalid_state'))
        self.assertFalse(is_valid_state(''))
        self.assertFalse(is_valid_state(None))


if __name__ == '__main__':
    # 配置日志
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # 运行测试
    unittest.main(verbosity=2)
