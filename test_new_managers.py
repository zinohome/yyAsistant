#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的核心管理器

验证所有新创建的管理器是否正常工作。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

import sys
import os
import asyncio
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """测试配置管理器"""
    print("🔧 测试配置管理器...")
    try:
        from config.config import config, get_config, set_config
        
        # 测试基本配置
        app_name = get_config('app.name')
        print("   应用名称: {}".format(app_name))
        
        # 测试设置配置
        set_config('test.value', 'test_data')
        test_value = get_config('test.value')
        print("   测试配置: {}".format(test_value))
        
        print("   ✅ 配置管理器测试通过")
        return True
    except Exception as e:
        print("   ❌ 配置管理器测试失败: {}".format(e))
        return False

def test_state_manager():
    """测试状态管理器"""
    print("🔄 测试状态管理器...")
    try:
        from core.state_manager.state_manager import StateManager, State
        
        manager = StateManager()
        
        # 测试初始状态
        initial_state = manager.get_state()
        print(f"   初始状态: {initial_state.value}")
        
        # 测试状态转换
        success = manager.setState(State.TEXT_SSE)
        print("   状态转换到TEXT_SSE: {}".format(success))
        
        current_state = manager.get_state()
        print("   当前状态: {}".format(current_state.value))
        
        # 测试状态信息
        info = manager.get_state_info()
        print("   状态信息: {}".format(info))
        
        print("   ✅ 状态管理器测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 状态管理器测试失败: {e}")
        return False

def test_event_manager():
    """测试事件管理器"""
    print("📡 测试事件管理器...")
    try:
        from core.event_manager.event_manager import EventManager, Event
        
        manager = EventManager()
        
        # 测试事件触发
        manager.emit_event(Event.TEXT_START, {'message': 'test'})
        print("   事件已触发: TEXT_START")
        
        # 测试事件统计
        stats = manager.get_event_stats()
        print(f"   事件统计: {stats}")
        
        # 测试管理器信息
        info = manager.get_manager_info()
        print(f"   管理器信息: {info}")
        
        print("   ✅ 事件管理器测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 事件管理器测试失败: {e}")
        return False

def test_timeout_manager():
    """测试超时管理器"""
    print("⏱️ 测试超时管理器...")
    try:
        from core.timeout_manager.timeout_manager import TimeoutManager, TimeoutType
        
        manager = TimeoutManager()
        
        # 测试超时计算
        timeout = manager.calculate_timeout(100, TimeoutType.SSE)
        print(f"   SSE超时计算 (100字符): {timeout}秒")
        
        # 测试超时处理
        result = manager.handle_timeout('test_id', TimeoutType.TTS, 100)
        print(f"   超时处理结果: {result}")
        
        # 测试管理器信息
        info = manager.get_manager_info()
        print(f"   管理器信息: {info}")
        
        print("   ✅ 超时管理器测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 超时管理器测试失败: {e}")
        return False

def test_error_handler():
    """测试错误处理器"""
    print("🚨 测试错误处理器...")
    try:
        from core.error_handler.error_handler import ErrorHandler, ErrorType, ErrorSeverity
        
        handler = ErrorHandler()
        
        # 测试错误处理
        result = handler.handle_error(ErrorType.WEBSOCKET_CONNECTION, '连接失败', ErrorSeverity.HIGH)
        print(f"   错误处理结果: {result}")
        
        # 测试错误统计
        stats = handler.get_error_stats()
        print(f"   错误统计: {stats}")
        
        # 测试管理器信息
        info = handler.get_manager_info()
        print(f"   管理器信息: {info}")
        
        print("   ✅ 错误处理器测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 错误处理器测试失败: {e}")
        return False

async def test_websocket_manager():
    """测试WebSocket管理器"""
    print("🌐 测试WebSocket管理器...")
    try:
        from core.websocket_manager.websocket_manager import WebSocketManager
        
        manager = WebSocketManager()
        
        # 测试连接信息
        info = manager.get_connection_info()
        print(f"   连接信息: {info}")
        
        # 测试状态
        state = manager.get_connection_state()
        print(f"   连接状态: {state.value}")
        
        print("   ✅ WebSocket管理器测试通过")
        return True
    except Exception as e:
        print(f"   ❌ WebSocket管理器测试失败: {e}")
        return False

def test_event_handlers():
    """测试事件处理器"""
    print("🎯 测试事件处理器...")
    try:
        from core.state_manager.state_manager import StateManager, State
        from core.event_manager.event_manager import EventManager, Event
        from core.event_manager.event_handlers import EventHandlers
        
        state_manager = StateManager()
        event_manager = EventManager()
        handlers = EventHandlers(state_manager, event_manager)
        
        # 测试事件处理
        handlers.handle_text_start({'message': 'test'})
        current_state = state_manager.get_state()
        print(f"   处理TEXT_START事件后状态: {current_state.value}")
        
        # 测试处理器信息
        info = handlers.get_handler_info()
        print(f"   处理器信息: {info}")
        
        print("   ✅ 事件处理器测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 事件处理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试新的核心管理器...")
    print("=" * 50)
    
    tests = [
        test_config,
        test_state_manager,
        test_event_manager,
        test_timeout_manager,
        test_error_handler,
        test_event_handlers,
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ 测试执行失败: {e}")
            results.append(False)
        print()
    
    # 异步测试
    try:
        result = asyncio.run(test_websocket_manager())
        results.append(result)
    except Exception as e:
        print(f"   ❌ WebSocket管理器测试执行失败: {e}")
        results.append(False)
    
    print("=" * 50)
    print("📊 测试结果汇总:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"   通过: {passed}/{total}")
    print(f"   成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！新的核心管理器工作正常。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关模块。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
