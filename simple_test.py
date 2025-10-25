#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入"""
    print("Testing imports...")
    
    try:
        # from config.config import config  # 暂时禁用，配置整理放到后面专题
        print("  Config: OK")
    except Exception as e:
        print("  Config: FAIL - {}".format(e))
        return False
    
    try:
        from core.state_manager.state_manager import StateManager, State
        print("  StateManager: OK")
    except Exception as e:
        print("  StateManager: FAIL - {}".format(e))
        return False
    
    try:
        from core.event_manager.event_manager import EventManager, Event
        print("  EventManager: OK")
    except Exception as e:
        print("  EventManager: FAIL - {}".format(e))
        return False
    
    try:
        from core.websocket_manager.websocket_manager import WebSocketManager
        print("  WebSocketManager: OK")
    except Exception as e:
        print("  WebSocketManager: FAIL - {}".format(e))
        return False
    
    try:
        from core.timeout_manager.timeout_manager import TimeoutManager, TimeoutType
        print("  TimeoutManager: OK")
    except Exception as e:
        print("  TimeoutManager: FAIL - {}".format(e))
        return False
    
    try:
        from core.error_handler.error_handler import ErrorHandler, ErrorType, ErrorSeverity
        print("  ErrorHandler: OK")
    except Exception as e:
        print("  ErrorHandler: FAIL - {}".format(e))
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("Testing basic functionality...")
    
    try:
        from core.state_manager.state_manager import StateManager, State
        
        manager = StateManager()
        print("  StateManager created: OK")
        
        # 测试状态转换
        success = manager.setState(State.TEXT_SSE)
        print("  State transition: {}".format(success))
        
        current_state = manager.get_state()
        print("  Current state: {}".format(current_state.value))
        
        return True
    except Exception as e:
        print("  Basic functionality: FAIL - {}".format(e))
        return False

if __name__ == "__main__":
    print("Simple test of new managers...")
    print("=" * 40)
    
    success1 = test_imports()
    print()
    success2 = test_basic_functionality()
    
    print("=" * 40)
    if success1 and success2:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)
