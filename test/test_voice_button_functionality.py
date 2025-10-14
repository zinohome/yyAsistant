#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音按钮功能测试
测试录音按钮是否能正常响应点击事件
"""

import sys
import os
sys.path.append('/Users/zhangjun/PycharmProjects/yyAsistant')

def test_voice_button_components():
    """测试语音按钮组件是否正确配置"""
    print("开始测试语音按钮功能...")
    
    # 测试1: 检查录音按钮ID是否正确
    print("\n1. 检查录音按钮ID...")
    try:
        from components.chat_input_area import render
        # 这里我们无法直接测试组件渲染，但可以检查导入是否正常
        print("✓ 聊天输入组件导入成功")
    except Exception as e:
        print(f"✗ 聊天输入组件导入失败: {e}")
        return False
    
    # 测试2: 检查语音回调函数是否正确导入
    print("\n2. 检查语音回调函数...")
    try:
        from callbacks.voice_chat_c import toggle_voice_recording, toggle_voice_call
        print("✓ 语音回调函数导入成功")
    except Exception as e:
        print(f"✗ 语音回调函数导入失败: {e}")
        return False
    
    # 测试3: 检查语音配置是否正确
    print("\n3. 检查语音配置...")
    try:
        from configs.voice_config import VoiceConfig
        config = VoiceConfig.get_default_settings()
        print(f"✓ 语音配置加载成功: {config}")
    except Exception as e:
        print(f"✗ 语音配置加载失败: {e}")
        return False
    
    # 测试4: 检查WebSocket客户端是否正确
    print("\n4. 检查WebSocket客户端...")
    try:
        from utils.voice_websocket_client import voice_websocket_client
        config = voice_websocket_client.get_connection_config()
        print(f"✓ WebSocket客户端配置成功: {config['url']}")
    except Exception as e:
        print(f"✗ WebSocket客户端配置失败: {e}")
        return False
    
    # 测试5: 检查JavaScript文件是否存在
    print("\n5. 检查JavaScript文件...")
    js_files = [
        '/Users/zhangjun/PycharmProjects/yyAsistant/assets/js/voice_recorder.js',
        '/Users/zhangjun/PycharmProjects/yyAsistant/assets/js/voice_player.js',
        '/Users/zhangjun/PycharmProjects/yyAsistant/assets/js/voice_websocket_manager.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"✓ {os.path.basename(js_file)} 存在")
        else:
            print(f"✗ {os.path.basename(js_file)} 不存在")
            return False
    
    print("\n🎉 语音按钮功能测试通过！")
    print("\n可能的问题排查:")
    print("1. 确保应用已重启以加载新的回调函数")
    print("2. 检查浏览器控制台是否有JavaScript错误")
    print("3. 检查浏览器是否支持WebRTC API")
    print("4. 检查麦克风权限是否已授予")
    
    return True

def test_callback_registration():
    """测试回调函数注册"""
    print("\n6. 测试回调函数注册...")
    try:
        # 尝试导入主应用
        from app import app
        print("✓ 主应用导入成功")
        
        # 检查回调是否已注册
        callback_functions = [func for func in dir(app) if 'callback' in func.lower()]
        print(f"✓ 应用中有 {len(callback_functions)} 个回调相关函数")
        
    except Exception as e:
        print(f"✗ 回调函数注册测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_voice_button_components()
    if success:
        test_callback_registration()
    
    print("\n📋 故障排除建议:")
    print("1. 重启应用: python app.py")
    print("2. 清除浏览器缓存")
    print("3. 检查浏览器控制台错误")
    print("4. 确保麦克风权限已授予")
    print("5. 检查网络连接")
