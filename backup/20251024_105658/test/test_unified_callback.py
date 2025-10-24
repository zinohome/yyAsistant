#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一回调测试脚本
测试 comprehensive_chat_callback.py 的各项功能
"""

import sys
import os
import json
import time
from datetime import datetime
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_unified_callback_import():
    """测试统一回调导入"""
    print("🔍 测试统一回调导入...")
    try:
        from callbacks.core_pages_c.comprehensive_chat_callback import comprehensive_chat_handler
        print("✅ 统一回调导入成功")
        return True
    except Exception as e:
        print(f"❌ 统一回调导入失败: {e}")
        return False

def test_callback_structure():
    """测试回调结构"""
    print("🔍 测试回调结构...")
    try:
        from callbacks.core_pages_c.comprehensive_chat_callback import comprehensive_chat_handler
        import inspect
        
        # 检查函数签名
        sig = inspect.signature(comprehensive_chat_handler)
        params = list(sig.parameters.keys())
        
        print(f"📋 回调参数数量: {len(params)}")
        print(f"📋 参数列表: {params[:5]}...")  # 显示前5个参数
        
        # 检查是否有必要的参数
        required_params = ['send_btn_clicks', 'topic_clicks', 'transcription_data', 'ws_connection']
        missing_params = [p for p in required_params if p not in params]
        
        if missing_params:
            print(f"❌ 缺少必要参数: {missing_params}")
            return False
        
        print("✅ 回调结构检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 回调结构检查失败: {e}")
        return False

def test_text_message_send():
    """测试文本消息发送功能"""
    print("🔍 测试文本消息发送功能...")
    try:
        from callbacks.core_pages_c.comprehensive_chat_callback import _handle_text_message_send
        
        # 模拟输入数据
        messages = []
        message_content = "测试消息"
        current_session_id = "test-session-001"
        default_returns = [None] * 17  # 17个输出参数
        
        # 调用函数
        result = _handle_text_message_send(messages, message_content, current_session_id, default_returns)
        
        # 验证结果
        if len(result) != 17:
            print(f"❌ 返回值数量错误: 期望17，实际{len(result)}")
            return False
        
        if result[0] is None:  # messages
            print("❌ 消息列表未更新")
            return False
        
        if len(result[0]) != 2:  # 应该有用户消息和AI消息
            print(f"❌ 消息数量错误: 期望2，实际{len(result[0])}")
            return False
        
        # 检查消息结构
        user_msg = result[0][0]
        ai_msg = result[0][1]
        
        if user_msg.get('role') != 'user':
            print("❌ 用户消息角色错误")
            return False
        
        if ai_msg.get('role') != 'assistant':
            print("❌ AI消息角色错误")
            return False
        
        if not ai_msg.get('is_streaming'):
            print("❌ AI消息未设置为流式传输")
            return False
        
        print("✅ 文本消息发送功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 文本消息发送功能测试失败: {e}")
        return False

def test_voice_transcription():
    """测试语音转录功能"""
    print("🔍 测试语音转录功能...")
    try:
        from callbacks.core_pages_c.comprehensive_chat_callback import _handle_voice_transcription
        
        # 模拟输入数据
        messages = []
        transcription_data = {
            'text': '语音转录测试',
            'timestamp': datetime.now().isoformat()
        }
        current_session_id = "test-session-001"
        default_returns = [None] * 17
        
        # 调用函数
        result = _handle_voice_transcription(messages, transcription_data, current_session_id, default_returns)
        
        # 验证结果
        if result[0] is None:  # messages
            print("❌ 消息列表未更新")
            return False
        
        if len(result[0]) != 2:  # 应该有用户消息和AI消息
            print(f"❌ 消息数量错误: 期望2，实际{len(result[0])}")
            return False
        
        # 检查消息内容
        user_msg = result[0][0]
        if user_msg.get('content') != '语音转录测试':
            print("❌ 语音转录内容错误")
            return False
        
        # 检查语音模式
        if result[5] != True:  # enable_voice
            print("❌ 语音模式未启用")
            return False
        
        print("✅ 语音转录功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 语音转录功能测试失败: {e}")
        return False

def test_ai_regenerate():
    """测试AI消息重新生成功能"""
    print("🔍 测试AI消息重新生成功能...")
    try:
        from callbacks.core_pages_c.comprehensive_chat_callback import _handle_ai_regenerate
        
        # 模拟输入数据
        messages = [
            {'role': 'user', 'content': '用户消息', 'id': 'usr-message-0'},
            {'role': 'assistant', 'content': 'AI消息', 'id': 'ai-message-1'},
            {'role': 'user', 'content': '用户消息2', 'id': 'usr-message-2'},
            {'role': 'assistant', 'content': 'AI消息2', 'id': 'ai-message-3'}
        ]
        triggered_id = {'type': 'ai-chat-x-regenerate', 'index': 3}
        current_session_id = "test-session-001"
        default_returns = [None] * 17
        
        # 调用函数
        result = _handle_ai_regenerate(messages, triggered_id, current_session_id, default_returns)
        
        # 验证结果
        if result[0] is None:
            print("❌ 消息列表未更新")
            return False
        
        # 检查消息数量（应该删除目标消息及后续消息）
        # 目标消息是索引3，所以应该保留前3条消息，然后添加新的AI消息
        if len(result[0]) != 4:  # 保留前3条消息 + 新的AI消息
            print(f"❌ 消息数量错误: 期望4，实际{len(result[0])}")
            return False
        
        # 检查最后一条消息是新的AI消息
        last_msg = result[0][-1]
        if last_msg.get('role') != 'assistant':
            print("❌ 最后一条消息不是AI消息")
            return False
        
        if not last_msg.get('is_streaming'):
            print("❌ 新AI消息未设置为流式传输")
            return False
        
        print("✅ AI消息重新生成功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ AI消息重新生成功能测试失败: {e}")
        return False

def test_cancel_send():
    """测试取消发送功能"""
    print("🔍 测试取消发送功能...")
    try:
        from callbacks.core_pages_c.comprehensive_chat_callback import _handle_cancel_send
        
        # 模拟输入数据
        messages = [
            {'role': 'user', 'content': '用户消息', 'id': 'usr-message-0'},
            {'role': 'assistant', 'content': '正在思考中...', 'id': 'ai-message-1', 'is_streaming': True}
        ]
        triggered_id = {'type': 'ai-chat-x-cancel', 'index': 1}
        default_returns = [None] * 17
        
        # 调用函数
        result = _handle_cancel_send(messages, triggered_id, default_returns)
        
        # 验证结果
        if result[0] is None:
            print("❌ 消息列表未更新")
            return False
        
        # 检查消息数量（应该删除正在流式传输的消息）
        if len(result[0]) != 1:  # 只保留用户消息
            print(f"❌ 消息数量错误: 期望1，实际{len(result[0])}")
            return False
        
        # 检查按钮状态
        if result[2] != False:  # loading
            print("❌ 加载状态未重置")
            return False
        
        if result[3] != False:  # disabled
            print("❌ 禁用状态未重置")
            return False
        
        print("✅ 取消发送功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 取消发送功能测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始测试统一回调...")
    print("=" * 50)
    
    tests = [
        ("导入测试", test_unified_callback_import),
        ("结构测试", test_callback_structure),
        ("文本发送测试", test_text_message_send),
        ("语音转录测试", test_voice_transcription),
        ("AI重新生成测试", test_ai_regenerate),
        ("取消发送测试", test_cancel_send)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！统一回调功能正常")
        return True
    else:
        print("⚠️ 部分测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
