#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试app.py中的新管理器集成

验证所有新创建的管理器在app.py中是否正常工作。

作者: AI Assistant
创建时间: 2024-10-24
版本: 1.0.0
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_managers():
    """测试app.py中的管理器"""
    print("Testing app.py managers...")
    
    try:
        # 导入app模块
        import app
        print("  App import: OK")
        
        # 检查管理器实例
        if hasattr(app, 'state_manager'):
            print("  StateManager: OK")
            print("    Current state: {}".format(app.state_manager.get_state().value))
        else:
            print("  StateManager: MISSING")
            return False
        
        if hasattr(app, 'event_manager'):
            print("  EventManager: OK")
            handlers = app.event_manager.get_registered_handlers()
            print("    Registered handlers: {}".format(len(handlers)))
        else:
            print("  EventManager: MISSING")
            return False
        
        if hasattr(app, 'websocket_manager'):
            print("  WebSocketManager: OK")
            state = app.websocket_manager.get_connection_state()
            print("    Connection state: {}".format(state.value))
        else:
            print("  WebSocketManager: MISSING")
            return False
        
        if hasattr(app, 'timeout_manager'):
            print("  TimeoutManager: OK")
            info = app.timeout_manager.get_manager_info()
            print("    Manager info: {}".format(info))
        else:
            print("  TimeoutManager: MISSING")
            return False
        
        if hasattr(app, 'error_handler'):
            print("  ErrorHandler: OK")
            stats = app.error_handler.get_error_stats()
            print("    Error stats: {}".format(stats))
        else:
            print("  ErrorHandler: MISSING")
            return False
        
        if hasattr(app, 'event_handlers'):
            print("  EventHandlers: OK")
            info = app.event_handlers.get_handler_info()
            print("    Handler info: {}".format(info))
        else:
            print("  EventHandlers: MISSING")
            return False
        
        return True
        
    except Exception as e:
        print("  App integration: FAIL - {}".format(e))
        return False

def test_state_transitions():
    """测试状态转换"""
    print("Testing state transitions...")
    
    try:
        import app
        
        # 测试状态转换
        success = app.state_manager.set_state(app.AppState.TEXT_SSE)
        print("  State transition to TEXT_SSE: {}".format(success))
        
        current_state = app.state_manager.get_state()
        print("  Current state: {}".format(current_state.value))
        
        # 测试事件触发（使用同步方法）
        app.event_manager.emit_event_sync(app.Event.TEXT_START, {'message': 'test'})
        print("  Event TEXT_START emitted")
        
        # 检查状态是否改变
        new_state = app.state_manager.get_state()
        print("  State after event: {}".format(new_state.value))
        
        return True
        
    except Exception as e:
        print("  State transitions: FAIL - {}".format(e))
        return False

if __name__ == "__main__":
    print("Testing app.py integration...")
    print("=" * 50)
    
    success1 = test_app_managers()
    print()
    success2 = test_state_transitions()
    
    print("=" * 50)
    if success1 and success2:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)
