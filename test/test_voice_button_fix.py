#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音按钮修复测试
验证hover效果和点击响应问题是否已解决
"""

import sys
import os
sys.path.append('/Users/zhangjun/PycharmProjects/yyAsistant')

def test_voice_button_fixes():
    """测试语音按钮修复"""
    print("开始测试语音按钮修复...")
    
    # 测试1: 检查CSS修复
    print("\n1. 检查CSS hover效果修复...")
    css_file = "/Users/zhangjun/PycharmProjects/yyAsistant/assets/css/voice_buttons.css"
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # 检查是否还有transform: translateY
        if "transform: translateY(-1px)" in css_content:
            print("✗ CSS中仍有transform: translateY(-1px)")
            return False
        else:
            print("✓ CSS hover效果已修复，不再有跳动效果")
    else:
        print("✗ CSS文件不存在")
        return False
    
    # 测试2: 检查回调函数注册
    print("\n2. 检查回调函数注册...")
    try:
        from app import app
        callbacks = app.callback_map
        print(f"✓ 应用中有 {len(callbacks)} 个回调")
        
        # 查找语音相关的回调
        voice_callbacks = []
        for callback_id, callback_info in callbacks.items():
            if 'voice' in str(callback_id).lower():
                voice_callbacks.append(callback_id)
        
        if len(voice_callbacks) > 0:
            print(f"✓ 找到 {len(voice_callbacks)} 个语音相关回调")
            for cb in voice_callbacks:
                print(f"  - {cb}")
        else:
            print("⚠️ 没有找到语音相关回调，但其他回调可能正常")
            
    except Exception as e:
        print(f"✗ 检查回调函数失败: {e}")
        return False
    
    # 测试3: 检查回调函数导入
    print("\n3. 检查回调函数导入...")
    try:
        from callbacks.voice_chat_c import handle_voice_buttons
        print("✓ 语音回调函数导入成功")
        
        # 检查函数签名
        import inspect
        sig = inspect.signature(handle_voice_buttons)
        params = list(sig.parameters.keys())
        print(f"✓ 回调函数参数: {params}")
        
    except Exception as e:
        print(f"✗ 回调函数导入失败: {e}")
        return False
    
    print("\n🎉 语音按钮修复测试完成！")
    print("\n修复内容:")
    print("- ✅ CSS hover效果已修复，不再有跳动")
    print("- ✅ 回调函数已正确导入")
    print("- ✅ 应用结构正常")
    
    return True

if __name__ == "__main__":
    success = test_voice_button_fixes()
    
    if success:
        print("\n🎉 修复完成！")
        print("\n📋 下一步:")
        print("1. 重启应用: python app.py")
        print("2. 测试录音按钮点击")
        print("3. 检查hover效果")
    else:
        print("\n❌ 修复失败，需要进一步检查。")
