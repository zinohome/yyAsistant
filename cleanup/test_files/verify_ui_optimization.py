#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI优化功能验证脚本
检查所有UI优化组件是否正确部署
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (不存在)")
        return False

def check_js_file_content(file_path, key_components):
    """检查JavaScript文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_components = []
        for component in key_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"⚠️  {file_path} 缺少组件: {missing_components}")
            return False
        else:
            print(f"✅ {file_path} 内容完整")
            return True
    except Exception as e:
        print(f"❌ 读取 {file_path} 失败: {e}")
        return False

def main():
    print("🔍 UI优化功能验证")
    print("=" * 50)
    
    # 检查JavaScript文件
    js_files = [
        ("assets/js/enhanced_audio_visualizer.js", "EnhancedAudioVisualizer", ["class EnhancedAudioVisualizer", "updateState", "drawVisualization"]),
        ("assets/js/enhanced_playback_status.js", "EnhancedPlaybackStatus", ["class EnhancedPlaybackStatus", "showStatus", "createContainer"]),
        ("assets/js/smart_error_handler.js", "SmartErrorHandler", ["class SmartErrorHandler", "handleError", "analyzeError"]),
        ("assets/js/state_sync_manager.js", "StateSyncManager", ["class StateSyncManager", "updateState", "addListener"]),
        ("assets/js/smart_state_predictor.js", "SmartStatePredictor", ["class SmartStatePredictor", "predictNextState", "recordUserAction"]),
        ("assets/js/adaptive_ui.js", "AdaptiveUI", ["class AdaptiveUI", "handlePreferenceChange", "getPerformanceReport"])
    ]
    
    js_results = []
    for file_path, description, components in js_files:
        exists = check_file_exists(file_path, description)
        if exists:
            content_ok = check_js_file_content(file_path, components)
            js_results.append(content_ok)
        else:
            js_results.append(False)
    
    # 检查Python文件
    py_files = [
        ("components/smart_message_actions.py", "智能消息操作组件", ["create_smart_message_actions", "create_status_indicator"]),
    ]
    
    py_results = []
    for file_path, description, components in py_files:
        exists = check_file_exists(file_path, description)
        if exists:
            content_ok = check_js_file_content(file_path, components)
            py_results.append(content_ok)
        else:
            py_results.append(False)
    
    # 检查测试文件
    test_files = [
        "tests/unit/test_ui_optimization.py",
        "tests/unit/test_error_handler.py", 
        "tests/unit/test_state_sync.py",
        "tests/unit/test_state_predictor.py",
        "tests/unit/test_adaptive_ui.py",
        "tests/integration/test_ui_integration.py",
        "tests/integration/test_error_recovery.py"
    ]
    
    test_results = []
    for test_file in test_files:
        exists = check_file_exists(test_file, f"测试文件: {test_file}")
        test_results.append(exists)
    
    # 检查chat.py引用
    chat_py_path = "views/core_pages/chat.py"
    if os.path.exists(chat_py_path):
        try:
            with open(chat_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_refs = [
                "enhanced_audio_visualizer.js",
                "enhanced_playback_status.js", 
                "smart_error_handler.js",
                "state_sync_manager.js",
                "smart_state_predictor.js",
                "adaptive_ui.js"
            ]
            
            missing_refs = []
            for ref in required_refs:
                if ref not in content:
                    missing_refs.append(ref)
            
            if missing_refs:
                print(f"⚠️  chat.py 缺少引用: {missing_refs}")
                chat_ok = False
            else:
                print(f"✅ chat.py 引用完整")
                chat_ok = True
        except Exception as e:
            print(f"❌ 读取 chat.py 失败: {e}")
            chat_ok = False
    else:
        print(f"❌ chat.py 不存在")
        chat_ok = False
    
    # 检查文档文件
    doc_files = [
        "docs/refactoring/12-ui-optimization-plan.md",
        "docs/refactoring/13-ui-optimization-implementation.md", 
        "docs/refactoring/15-ui-optimization-deployment.md",
        "docs/refactoring/UI_OPTIMIZATION_SUMMARY.md",
        "UI_OPTIMIZATION_COMPLETE.md"
    ]
    
    doc_results = []
    for doc_file in doc_files:
        exists = check_file_exists(doc_file, f"文档: {doc_file}")
        doc_results.append(exists)
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 验证结果总结")
    print("=" * 50)
    
    js_ok = sum(js_results)
    py_ok = sum(py_results) 
    test_ok = sum(test_results)
    doc_ok = sum(doc_results)
    
    print(f"JavaScript组件: {js_ok}/{len(js_results)} 正常")
    print(f"Python组件: {py_ok}/{len(py_results)} 正常")
    print(f"测试文件: {test_ok}/{len(test_results)} 存在")
    print(f"文档文件: {doc_ok}/{len(doc_files)} 存在")
    print(f"chat.py引用: {'✅' if chat_ok else '❌'}")
    
    total_score = js_ok + py_ok + test_ok + doc_ok + (1 if chat_ok else 0)
    total_possible = len(js_results) + len(py_results) + len(test_results) + len(doc_files) + 1
    
    print(f"\n🎯 总体评分: {total_score}/{total_possible} ({total_score/total_possible*100:.1f}%)")
    
    if total_score == total_possible:
        print("🎉 所有UI优化功能已正确部署！")
        print("\n📋 下一步:")
        print("1. 启动应用: python app.py")
        print("2. 访问: http://localhost:8050")
        print("3. 测试页面: http://localhost:8050/test_ui_optimization.html")
        print("4. 进行语音交互测试功能")
    else:
        print("⚠️  部分功能可能未正确部署，请检查上述错误")
    
    return total_score == total_possible

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
