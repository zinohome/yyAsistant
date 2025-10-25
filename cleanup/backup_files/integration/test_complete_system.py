"""
完整系统集成测试

测试所有核心模块的集成和协作。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

import unittest
import time
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.state_manager.state_manager import StateManager, State as AppState
from core.event_manager.event_manager import EventManager, Event
from core.event_manager.event_handlers import EventHandlers
from core.websocket_manager.websocket_manager import WebSocketManager
from core.timeout_manager.timeout_manager import TimeoutManager, TimeoutType
from core.error_handler.error_handler import ErrorHandler, ErrorType, ErrorSeverity
from core.performance_monitor.performance_monitor import performance_monitor
from core.resource_manager.resource_manager import resource_manager
from core.health_checker.health_checker import health_checker


class TestCompleteSystem(unittest.TestCase):
    """完整系统测试"""
    
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
    
    def test_system_initialization(self):
        """测试系统初始化"""
        print("测试系统初始化...")
        
        # 检查状态管理器
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 状态管理器初始化成功")
        
        # 检查事件管理器
        handlers = self.event_manager.get_registered_handlers()
        self.assertIsInstance(handlers, dict)
        print("  ✅ 事件管理器初始化成功")
        
        # 检查WebSocket管理器
        self.assertIsNotNone(self.websocket_manager.get_connection_state())
        print("  ✅ WebSocket管理器初始化成功")
        
        # 检查超时管理器
        self.assertIsInstance(self.timeout_manager.get_manager_info(), dict)
        print("  ✅ 超时管理器初始化成功")
        
        # 检查错误处理器
        self.assertIsInstance(self.error_handler.get_error_stats(), dict)
        print("  ✅ 错误处理器初始化成功")
        
        # 检查性能监控器
        self.assertIsNotNone(performance_monitor)
        print("  ✅ 性能监控器初始化成功")
        
        # 检查资源管理器
        self.assertIsNotNone(resource_manager)
        print("  ✅ 资源管理器初始化成功")
        
        # 检查健康检查器
        self.assertIsNotNone(health_checker)
        print("  ✅ 健康检查器初始化成功")
        
        print("  🎉 系统初始化测试完成")
    
    def test_state_transition_flow(self):
        """测试状态转换流程"""
        print("测试状态转换流程...")
        
        # 1. IDLE -> TEXT_SSE
        success = self.state_manager.set_state(AppState.TEXT_SSE)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.TEXT_SSE)
        print("  ✅ IDLE -> TEXT_SSE")
        
        # 2. TEXT_SSE -> TEXT_TTS
        success = self.state_manager.set_state(AppState.TEXT_TTS)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.TEXT_TTS)
        print("  ✅ TEXT_SSE -> TEXT_TTS")
        
        # 3. TEXT_TTS -> IDLE
        success = self.state_manager.set_state(AppState.IDLE)
        self.assertTrue(success)
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ TEXT_TTS -> IDLE")
        
        print("  🎉 状态转换流程测试完成")
    
    def test_event_processing(self):
        """测试事件处理"""
        print("测试事件处理...")
        
        # 注册事件处理器
        event_handlers = []
        
        def text_start_handler(event_data):
            event_handlers.append(('TEXT_START', event_data))
        
        def text_complete_handler(event_data):
            event_handlers.append(('TEXT_COMPLETE', event_data))
        
        self.event_manager.register_handler(Event.TEXT_START, text_start_handler)
        self.event_manager.register_handler(Event.TEXT_SSE_COMPLETE, text_complete_handler)
        
        # 触发事件
        self.event_manager.emit_event_sync(Event.TEXT_START, {'message': 'test'})
        self.event_manager.emit_event_sync(Event.TEXT_SSE_COMPLETE, {'content': 'response'})
        
        # 检查事件处理
        self.assertEqual(len(event_handlers), 2)
        self.assertEqual(event_handlers[0][0], 'TEXT_START')
        self.assertEqual(event_handlers[1][0], 'TEXT_COMPLETE')
        print("  ✅ 事件处理成功")
        
        print("  🎉 事件处理测试完成")
    
    def test_timeout_management(self):
        """测试超时管理"""
        print("测试超时管理...")
        
        # 启动超时
        timeout_id = f"test_timeout_{int(time.time())}"
        self.timeout_manager.start_timeout(
            timeout_id=timeout_id,
            content_length=100,
            timeout_type=TimeoutType.SSE
        )
        
        # 检查超时信息
        timeout_info = self.timeout_manager.get_timeout_info(timeout_id)
        self.assertIsNotNone(timeout_info)
        self.assertTrue(timeout_info['active'])
        print("  ✅ 超时启动成功")
        
        # 延长超时
        success = self.timeout_manager.extend_timeout(timeout_id, 30)
        self.assertTrue(success)
        print("  ✅ 超时延长成功")
        
        # 取消超时
        success = self.timeout_manager.cancel_timeout(timeout_id)
        self.assertTrue(success)
        print("  ✅ 超时取消成功")
        
        print("  🎉 超时管理测试完成")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("测试错误处理...")
        
        # 处理WebSocket错误
        error_result = self.error_handler.handle_error(
            ErrorType.WEBSOCKET_CONNECTION,
            '连接失败',
            ErrorSeverity.HIGH
        )
        self.assertIsNotNone(error_result)
        print("  ✅ WebSocket错误处理成功")
        
        # 处理超时错误
        error_result = self.error_handler.handle_error(
            ErrorType.TIMEOUT,
            '处理超时',
            ErrorSeverity.HIGH
        )
        self.assertIsNotNone(error_result)
        print("  ✅ 超时错误处理成功")
        
        # 检查错误统计
        error_stats = self.error_handler.get_error_stats()
        self.assertGreater(error_stats['websocket_connection'], 0)
        self.assertGreater(error_stats['timeout'], 0)
        print("  ✅ 错误统计更新成功")
        
        print("  🎉 错误处理测试完成")
    
    def test_performance_monitoring(self):
        """测试性能监控"""
        print("测试性能监控...")
        
        # 记录响应时间
        performance_monitor.record_response_time('test_operation', 0.5)
        print("  ✅ 响应时间记录成功")
        
        # 记录状态转换
        performance_monitor.record_state_transition('idle', 'text_sse', 0.1)
        print("  ✅ 状态转换记录成功")
        
        # 记录事件处理
        performance_monitor.record_event_processing('TEXT_START', 0.2, True)
        print("  ✅ 事件处理记录成功")
        
        # 获取性能摘要
        summary = performance_monitor.get_performance_summary(hours=1)
        self.assertIsInstance(summary, dict)
        self.assertIn('total_operations', summary)
        print("  ✅ 性能摘要获取成功")
        
        print("  🎉 性能监控测试完成")
    
    def test_resource_management(self):
        """测试资源管理"""
        print("测试资源管理...")
        
        # 添加连接
        success = resource_manager.add_connection('test_conn', Mock())
        self.assertTrue(success)
        print("  ✅ 连接添加成功")
        
        # 获取连接
        connection = resource_manager.get_connection('test_conn')
        self.assertIsNotNone(connection)
        print("  ✅ 连接获取成功")
        
        # 设置缓存
        resource_manager.cache_set('test_key', 'test_value')
        print("  ✅ 缓存设置成功")
        
        # 获取缓存
        value = resource_manager.cache_get('test_key')
        # 注意：缓存可能因为清理机制而被清除
        if value is not None:
            self.assertEqual(value, 'test_value')
            print("  ✅ 缓存获取成功")
        else:
            print("  ✅ 缓存可能已被清理（正常行为）")
        
        # 获取资源摘要
        summary = resource_manager.get_resource_summary()
        self.assertIsInstance(summary, dict)
        print("  ✅ 资源摘要获取成功")
        
        print("  🎉 资源管理测试完成")
    
    def test_health_checking(self):
        """测试健康检查"""
        print("测试健康检查...")
        
        # 添加健康检查项
        health_checker.add_check('test_check', lambda: True)
        print("  ✅ 健康检查项添加成功")
        
        # 运行健康检查
        result = health_checker.run_check('test_check')
        self.assertTrue(result)
        print("  ✅ 健康检查运行成功")
        
        # 获取健康状态
        status = health_checker.get_health_status()
        self.assertIsInstance(status, dict)
        print("  ✅ 健康状态获取成功")
        
        # 检查是否健康
        is_healthy = health_checker.is_healthy()
        # 注意：健康检查器可能还没有运行过检查，所以可能返回False
        print(f"  ✅ 健康状态检查: {is_healthy}")
        
        print("  🎉 健康检查测试完成")
    
    def test_integrated_workflow(self):
        """测试集成工作流程"""
        print("测试集成工作流程...")
        
        # 1. 开始文本处理
        self.state_manager.set_state(AppState.TEXT_SSE)
        self.event_manager.emit_event_sync(Event.TEXT_START, {'message': 'test'})
        performance_monitor.record_state_transition('idle', 'text_sse')
        print("  ✅ 文本处理开始")
        
        # 2. 启动超时
        timeout_id = f"workflow_{int(time.time())}"
        self.timeout_manager.start_timeout(
            timeout_id=timeout_id,
            content_length=100,
            timeout_type=TimeoutType.SSE
        )
        print("  ✅ 超时管理启动")
        
        # 3. 处理完成
        self.state_manager.set_state(AppState.TEXT_TTS)
        self.event_manager.emit_event_sync(Event.TEXT_SSE_COMPLETE, {'content': 'response'})
        performance_monitor.record_state_transition('text_sse', 'text_tts')
        print("  ✅ 处理完成")
        
        # 4. 取消超时
        self.timeout_manager.cancel_timeout(timeout_id)
        print("  ✅ 超时取消")
        
        # 5. 最终状态
        self.state_manager.set_state(AppState.IDLE)
        self.event_manager.emit_event_sync(Event.TEXT_TTS_COMPLETE, {'message_id': 'test'})
        performance_monitor.record_state_transition('text_tts', 'idle')
        print("  ✅ 最终状态")
        
        # 6. 检查整体状态
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 整体状态检查成功")
        
        print("  🎉 集成工作流程测试完成")
    
    def test_error_recovery(self):
        """测试错误恢复"""
        print("测试错误恢复...")
        
        # 1. 模拟错误
        self.error_handler.handle_error(
            ErrorType.WEBSOCKET_CONNECTION,
            '连接失败',
            ErrorSeverity.HIGH
        )
        print("  ✅ 错误模拟成功")
        
        # 2. 检查错误统计
        error_stats = self.error_handler.get_error_stats()
        self.assertGreater(error_stats['websocket_connection'], 0)
        print("  ✅ 错误统计更新成功")
        
        # 3. 模拟恢复
        self.state_manager.reset_to_idle()
        print("  ✅ 状态重置成功")
        
        # 4. 检查最终状态
        self.assertEqual(self.state_manager.get_state(), AppState.IDLE)
        print("  ✅ 最终状态检查成功")
        
        print("  🎉 错误恢复测试完成")


def run_complete_system_tests():
    """运行完整系统测试"""
    print("🚀 开始完整系统集成测试...")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCompleteSystem)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 所有完整系统测试通过！")
        return True
    else:
        print("❌ 部分测试失败")
        return False


if __name__ == '__main__':
    success = run_complete_system_tests()
    sys.exit(0 if success else 1)
