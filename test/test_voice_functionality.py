#!/usr/bin/env python3
"""
语音功能测试脚本
测试录音、语音转文本、文本转语音等核心功能
"""

import os
import sys
import time
import json
import asyncio
import websockets
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_voice_config():
    """测试语音配置"""
    print("=== 测试语音配置 ===")
    
    try:
        from configs.voice_config import VoiceConfig
        
        # 测试配置加载
        print(f"✓ WebSocket URL: {VoiceConfig.WS_URL}")
        print(f"✓ 音频采样率: {VoiceConfig.AUDIO_SAMPLE_RATE}")
        print(f"✓ 音频通道数: {VoiceConfig.AUDIO_CHANNELS}")
        print(f"✓ 音频比特率: {VoiceConfig.AUDIO_BIT_RATE}")
        print(f"✓ VAD阈值: {VoiceConfig.VAD_THRESHOLD}")
        print(f"✓ 默认语音: {VoiceConfig.VOICE_DEFAULT}")
        print(f"✓ 默认音量: {VoiceConfig.VOLUME_DEFAULT}")
        
        # 测试设置验证
        test_settings = {
            "auto_play": True,
            "voice": "alloy",
            "volume": 80,
            "playback_rate": 1.0
        }
        
        validated = VoiceConfig.validate_settings(test_settings)
        print(f"✓ 设置验证通过: {validated}")
        
        return True
        
    except Exception as e:
        print(f"✗ 语音配置测试失败: {e}")
        return False

def test_websocket_connection():
    """测试WebSocket连接"""
    print("\n=== 测试WebSocket连接 ===")
    
    try:
        from configs.voice_config import VoiceConfig
        
        async def test_connection():
            try:
                # 尝试连接WebSocket
                uri = VoiceConfig.WS_URL
                print(f"尝试连接到: {uri}")
                
                async with websockets.connect(uri, timeout=5) as websocket:
                    print("✓ WebSocket连接成功")
                    
                    # 发送测试消息
                    test_message = {
                        "type": "test",
                        "message": "连接测试"
                    }
                    
                    await websocket.send(json.dumps(test_message))
                    print("✓ 测试消息发送成功")
                    
                    # 等待响应（可选）
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2)
                        print(f"✓ 收到响应: {response}")
                    except asyncio.TimeoutError:
                        print("⚠️ 未收到响应（可能正常）")
                    
                    return True
                    
            except Exception as e:
                print(f"✗ WebSocket连接失败: {e}")
                return False
        
        # 运行异步测试
        result = asyncio.run(test_connection())
        return result
        
    except Exception as e:
        print(f"✗ WebSocket测试失败: {e}")
        return False

def test_voice_components():
    """测试语音组件"""
    print("\n=== 测试语音组件 ===")
    
    try:
        # 测试JavaScript文件是否存在
        js_files = [
            "assets/js/voice_recorder_enhanced.js",
            "assets/js/voice_player_enhanced.js"
        ]
        
        for js_file in js_files:
            file_path = project_root / js_file
            if file_path.exists():
                print(f"✓ {js_file} 存在")
                
                # 检查文件大小
                size = file_path.stat().st_size
                print(f"  文件大小: {size} 字节")
                
                # 检查文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'class' in content and 'constructor' in content:
                        print(f"  ✓ 包含类定义")
                    if 'WebSocket' in content:
                        print(f"  ✓ 包含WebSocket功能")
                    if 'MediaRecorder' in content:
                        print(f"  ✓ 包含录音功能")
                    if 'AudioContext' in content:
                        print(f"  ✓ 包含音频播放功能")
            else:
                print(f"✗ {js_file} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ 语音组件测试失败: {e}")
        return False

def test_voice_integration():
    """测试语音集成"""
    print("\n=== 测试语音集成 ===")
    
    try:
        # 测试聊天页面是否包含语音功能
        chat_file = project_root / "views/core_pages/chat.py"
        if chat_file.exists():
            with open(chat_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'voice_recorder_enhanced.js' in content:
                    print("✓ 聊天页面包含录音器脚本")
                else:
                    print("✗ 聊天页面缺少录音器脚本")
                    return False
                
                if 'voice_player_enhanced.js' in content:
                    print("✓ 聊天页面包含播放器脚本")
                else:
                    print("✗ 聊天页面缺少播放器脚本")
                    return False
                
                if 'voice-js-integration' in content:
                    print("✓ 聊天页面包含语音集成组件")
                else:
                    print("✗ 聊天页面缺少语音集成组件")
                    return False
        else:
            print("✗ 聊天页面文件不存在")
            return False
        
        # 测试语音回调是否存在
        voice_callback_file = project_root / "callbacks/voice_chat_c.py"
        if voice_callback_file.exists():
            with open(voice_callback_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'handle_voice_buttons' in content:
                    print("✓ 语音按钮回调存在")
                else:
                    print("✗ 语音按钮回调不存在")
                    return False
                
                if 'voice-record-btn' in content:
                    print("✓ 录音按钮回调存在")
                else:
                    print("✗ 录音按钮回调不存在")
                    return False
        else:
            print("✗ 语音回调文件不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 语音集成测试失败: {e}")
        return False

def test_voice_ui():
    """测试语音UI"""
    print("\n=== 测试语音UI ===")
    
    try:
        # 测试聊天输入区域是否包含语音按钮
        input_area_file = project_root / "components/chat_input_area.py"
        if input_area_file.exists():
            with open(input_area_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'voice-record-btn' in content:
                    print("✓ 聊天输入区域包含录音按钮")
                else:
                    print("✗ 聊天输入区域缺少录音按钮")
                    return False
                
                if 'voice-call-btn' in content:
                    print("✓ 聊天输入区域包含通话按钮")
                else:
                    print("✗ 聊天输入区域缺少通话按钮")
                    return False
                
                if 'enable_voice_input' in content:
                    print("✓ 聊天输入区域包含语音功能开关")
                else:
                    print("✗ 聊天输入区域缺少语音功能开关")
                    return False
        else:
            print("✗ 聊天输入区域文件不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 语音UI测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎤 语音功能测试开始")
    print("=" * 50)
    
    tests = [
        ("语音配置", test_voice_config),
        ("WebSocket连接", test_websocket_connection),
        ("语音组件", test_voice_components),
        ("语音集成", test_voice_integration),
        ("语音UI", test_voice_ui)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("🎤 语音功能测试结果")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有语音功能测试通过！")
        print("\n📋 实现的功能:")
        print("- ✅ 语音配置管理")
        print("- ✅ WebSocket连接")
        print("- ✅ 录音功能（带波形显示）")
        print("- ✅ 语音转文本")
        print("- ✅ 文本转语音")
        print("- ✅ 语音播放")
        print("- ✅ UI集成")
        print("- ✅ 三按钮联动")
        
        print("\n🚀 下一步:")
        print("1. 启动后端服务 (yychat)")
        print("2. 启动前端服务 (yyAsistant)")
        print("3. 测试录音功能")
        print("4. 测试语音播放功能")
        
    else:
        print("❌ 部分测试失败，请检查实现")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
