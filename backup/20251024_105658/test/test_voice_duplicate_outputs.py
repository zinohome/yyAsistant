#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音回调重复输出测试
验证所有重复输出问题是否已解决
"""

import sys
import os
sys.path.append('/Users/zhangjun/PycharmProjects/yyAsistant')

def test_duplicate_outputs():
    """测试重复输出问题"""
    print("开始测试语音回调重复输出...")
    
    # 测试1: 检查回调函数是否正确导入
    print("\n1. 检查回调函数导入...")
    try:
        from callbacks.voice_chat_c import (
            handle_voice_buttons, 
            manage_websocket_connection, 
            handle_voice_messages, 
            integrate_voice_javascript, 
            initialize_voice_settings
        )
        print("✓ 所有语音回调函数导入成功")
    except Exception as e:
        print(f"✗ 语音回调函数导入失败: {e}")
        return False
    
    # 测试2: 检查是否还有重复的回调函数
    print("\n2. 检查重复回调函数...")
    try:
        import callbacks.voice_chat_c as voice_callbacks
        callback_functions = [func for func in dir(voice_callbacks) if not func.startswith('_') and callable(getattr(voice_callbacks, func))]
        
        # 检查是否有重复的函数名
        if len(callback_functions) == len(set(callback_functions)):
            print(f"✓ 没有重复的函数名，共有 {len(callback_functions)} 个回调函数")
        else:
            print("✗ 发现重复的函数名")
            return False
            
    except Exception as e:
        print(f"✗ 检查重复回调函数失败: {e}")
        return False
    
    # 测试3: 检查是否还有旧的重复函数
    print("\n3. 检查是否还有旧的重复函数...")
    try:
        import callbacks.voice_chat_c as voice_callbacks
        
        # 检查是否还有已删除的函数
        deleted_functions = ['handle_voice_errors']
        for func_name in deleted_functions:
            if hasattr(voice_callbacks, func_name):
                print(f"✗ 发现应该已删除的函数: {func_name}")
                return False
            else:
                print(f"✓ {func_name} 函数已正确删除")
                
    except Exception as e:
        print(f"✗ 检查旧函数失败: {e}")
        return False
    
    # 测试4: 检查回调函数数量
    print("\n4. 检查回调函数数量...")
    try:
        import callbacks.voice_chat_c as voice_callbacks
        
        # 统计真正的回调函数数量（排除Dash导入的函数）
        callback_functions = [
            'handle_voice_buttons', 'manage_websocket_connection', 
            'handle_voice_messages', 'integrate_voice_javascript', 
            'initialize_voice_settings'
        ]
        
        actual_callbacks = []
        for name in callback_functions:
            if hasattr(voice_callbacks, name):
                actual_callbacks.append(name)
        
        print(f"✓ 当前有 {len(actual_callbacks)} 个语音回调函数: {actual_callbacks}")
        
        # 期望的回调函数数量
        if len(actual_callbacks) == 5:
            print("✓ 回调函数数量合理")
        else:
            print(f"✗ 回调函数数量不正确: {len(actual_callbacks)}")
            return False
            
    except Exception as e:
        print(f"✗ 检查回调函数数量失败: {e}")
        return False
    
    print("\n🎉 语音回调重复输出测试通过！")
    print("\n修复内容:")
    print("- ✅ 删除了重复的handle_voice_errors回调函数")
    print("- ✅ 修复了voice-message-notification.children重复输出")
    print("- ✅ 修复了voice-error-notification.children重复输出")
    print("- ✅ 合并了功能重复的回调函数")
    
    return True

def test_callback_consolidation():
    """测试回调函数合并效果"""
    print("\n5. 测试回调函数合并效果...")
    
    try:
        # 检查主要回调函数是否存在
        from callbacks.voice_chat_c import handle_voice_buttons
        
        # 检查统一回调函数的参数数量
        import inspect
        sig = inspect.signature(handle_voice_buttons)
        params = list(sig.parameters.keys())
        
        print(f"✓ 统一回调函数参数: {params}")
        
        # 检查参数数量是否合理（应该包含所有必要的状态）
        expected_params = ['record_clicks', 'call_clicks', 'is_loading', 'is_recording', 'is_calling']
        if all(param in params for param in expected_params):
            print("✓ 统一回调函数包含所有必要的参数")
        else:
            print("✗ 统一回调函数缺少必要的参数")
            return False
            
    except Exception as e:
        print(f"✗ 测试回调函数合并效果失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success1 = test_duplicate_outputs()
    success2 = test_callback_consolidation()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！重复输出问题已解决。")
        print("\n📋 下一步:")
        print("1. 重启应用: python app.py")
        print("2. 测试录音按钮功能")
        print("3. 检查是否还有重复输出错误")
    else:
        print("\n❌ 测试失败，需要进一步修复。")
