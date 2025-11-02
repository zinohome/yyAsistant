#!/usr/bin/env python3
"""
语音实时对话文本显示功能 - 自动化测试脚本
检查代码完整性、配置项、文件存在性等无需人工参与的测试项
"""

import os
import sys
import re
import json
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
YYASISTANT_ROOT = PROJECT_ROOT
YYCHAT_ROOT = PROJECT_ROOT.parent / "yychat"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

# 测试结果
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_passed(name):
    test_results["passed"].append(name)
    print_success(name)

def test_failed(name, reason=""):
    test_results["failed"].append(f"{name}: {reason}")
    print_error(f"{name}: {reason}")

def test_warning(name, reason=""):
    test_results["warnings"].append(f"{name}: {reason}")
    print_warning(f"{name}: {reason}")

# 测试1：文件存在性检查
def test_file_existence():
    print_info("\n=== 测试1：文件存在性检查 ===")
    
    files_to_check = [
        # 前端文件（相对路径）
        ("assets/js/voice_recorder_enhanced.js", "录音器增强文件"),
        ("assets/js/voice_websocket_manager.js", "WebSocket管理器文件"),
        ("configs/voice_config.py", "语音配置文件"),
        ("views/core_pages/chat.py", "聊天页面视图"),
        ("callbacks/voice_call_display_c.py", "语音实时对话显示回调"),
        ("app.py", "应用主文件"),
        ("server.py", "服务器文件"),
        
        # 后端文件（相对路径）
        ("config/realtime_config.py", "实时语音配置文件"),
        ("core/realtime_handler.py", "实时消息处理器"),
        ("core/message_router.py", "消息路由器"),
    ]
    
    for file_path, description in files_to_check:
        if file_path.startswith(("assets/", "configs/", "views/", "callbacks/", "app.py", "server.py")):
            full_path = YYASISTANT_ROOT / file_path
        else:
            full_path = YYCHAT_ROOT / file_path
        if full_path.exists():
            test_passed(f"{description} 存在")
        else:
            test_failed(f"{description} 不存在", str(full_path))

# 测试2：配置项检查
def test_config_items():
    print_info("\n=== 测试2：配置项检查 ===")
    
    # 检查前端配置
    voice_config_file = YYASISTANT_ROOT / "configs" / "voice_config.py"
    if voice_config_file.exists():
        content = voice_config_file.read_text(encoding='utf-8')
        
        config_items = [
            ("VOICE_CALL_SHOW_TRANSCRIPTION", "显示转录文本配置"),
            ("VOICE_CALL_SAVE_TO_DATABASE", "保存到数据库配置"),
            ("VOICE_CALL_AUTO_SAVE_ON_END", "自动保存配置"),
            ("VOICE_CALL_MAX_DISPLAY_MESSAGES", "最大显示消息数配置"),
            ("VOICE_CALL_TRANSCRIPTION_DEBOUNCE", "防抖时间配置"),
            ("VOICE_CALL_STREAMING_DISPLAY", "流式显示配置"),
        ]
        
        for item, description in config_items:
            if item in content:
                test_passed(f"{description} ({item}) 存在")
            else:
                test_failed(f"{description} ({item}) 不存在")
    
    # 检查后端配置
    realtime_config_file = YYCHAT_ROOT / "config" / "realtime_config.py"
    if realtime_config_file.exists():
        content = realtime_config_file.read_text(encoding='utf-8')
        
        config_items = [
            ("VOICE_CALL_SEND_TRANSCRIPTION", "发送转录结果配置"),
            ("VOICE_CALL_INCLUDE_ASSISTANT_TEXT", "包含AI回复文本配置"),
        ]
        
        for item, description in config_items:
            if item in content:
                test_passed(f"{description} ({item}) 存在")
            else:
                test_failed(f"{description} ({item}) 不存在")

# 测试3：代码逻辑检查
def test_code_logic():
    print_info("\n=== 测试3：代码逻辑检查 ===")
    
    # 检查 voice_recorder_enhanced.js
    recorder_file = YYASISTANT_ROOT / "assets" / "js" / "voice_recorder_enhanced.js"
    if recorder_file.exists():
        content = recorder_file.read_text(encoding='utf-8')
        
        checks = [
            ("scenario === 'voice_call'", "场景检查逻辑（voice_recorder_enhanced.js）"),
            ("收到语音实时对话转录结果，跳过录音聊天处理", "场景区分日志"),
        ]
        
        for check, description in checks:
            if check in content:
                test_passed(description)
            else:
                test_failed(description)
    
    # 检查 voice_websocket_manager.js
    manager_file = YYASISTANT_ROOT / "assets" / "js" / "voice_websocket_manager.js"
    if manager_file.exists():
        content = manager_file.read_text(encoding='utf-8')
        
        checks = [
            ("handleVoiceCallTranscription", "处理语音实时对话转录方法"),
            ("debounceUpdateVoiceCallDisplay", "防抖更新方法"),
            ("updateVoiceCallTextDisplay", "更新UI显示方法"),
            ("escapeHtml", "HTML转义方法"),
            ("saveVoiceCallMessages", "保存消息方法"),
            ("pendingVoiceCallMessages", "待更新消息队列"),
            ("registerMessageHandler('transcription_result'", "注册transcription_result处理器"),
            ("scenario === 'voice_call'", "场景检查逻辑（voice_websocket_manager.js）"),
        ]
        
        for check, description in checks:
            if check in content:
                test_passed(description)
            else:
                test_failed(description)

# 测试4：Store组件检查
def test_store_components():
    print_info("\n=== 测试4：Store组件检查 ===")
    
    chat_file = YYASISTANT_ROOT / "views" / "core_pages" / "chat.py"
    if chat_file.exists():
        content = chat_file.read_text(encoding='utf-8')
        
        checks = [
            ("voice-call-transcription-display", "Store ID存在"),
            ("voice_call_transcription_display = dcc.Store", "Store组件定义"),
        ]
        
        for check, description in checks:
            if check in content:
                test_passed(description)
            else:
                test_failed(description)

# 测试5：UI组件检查
def test_ui_components():
    print_info("\n=== 测试5：UI组件检查 ===")
    
    chat_file = YYASISTANT_ROOT / "views" / "core_pages" / "chat.py"
    if chat_file.exists():
        content = chat_file.read_text(encoding='utf-8')
        
        checks = [
            ("voice-call-text-display", "悬浮面板ID"),
            ("voice-call-text-content", "文本内容区域ID"),
            ("voice-call-text-close-btn", "关闭按钮ID"),
            ("position='relative'", "chat_history相对定位"),
        ]
        
        for check, description in checks:
            if check in content:
                test_passed(description)
            else:
                test_failed(description)

# 测试6：回调注册检查
def test_callback_registration():
    print_info("\n=== 测试6：回调注册检查 ===")
    
    app_file = YYASISTANT_ROOT / "app.py"
    if app_file.exists():
        content = app_file.read_text(encoding='utf-8')
        
        if "import callbacks.voice_call_display_c" in content:
            test_passed("回调文件已导入")
        else:
            test_failed("回调文件未导入")
    
    callback_file = YYASISTANT_ROOT / "callbacks" / "voice_call_display_c.py"
    if callback_file.exists():
        content = callback_file.read_text(encoding='utf-8')
        
        checks = [
            ("@callback", "回调装饰器"),
            ("voice-call-text-display", "回调输出ID"),
            ("voice-call-text-close-btn", "回调输入ID"),
        ]
        
        for check, description in checks:
            if check in content:
                test_passed(f"{description} 正确")
            else:
                test_failed(f"{description} 不正确")

# 测试7：后端场景字段检查
def test_backend_scenario_fields():
    print_info("\n=== 测试7：后端场景字段检查 ===")
    
    # 检查 realtime_handler.py
    handler_file = YYCHAT_ROOT / "core" / "realtime_handler.py"
    if handler_file.exists():
        content = handler_file.read_text(encoding='utf-8')
        
        if '"scenario": "voice_call"' in content or "'scenario': 'voice_call'" in content:
            test_passed("realtime_handler.py 包含 scenario: voice_call")
        else:
            test_failed("realtime_handler.py 缺少 scenario: voice_call")
    
    # 检查 message_router.py
    router_file = YYCHAT_ROOT / "core" / "message_router.py"
    if router_file.exists():
        content = router_file.read_text(encoding='utf-8')
        
        if '"scenario": "voice_recording"' in content or "'scenario': 'voice_recording'" in content:
            test_passed("message_router.py 包含 scenario: voice_recording")
        else:
            test_failed("message_router.py 缺少 scenario: voice_recording")

# 测试8：API端点检查
def test_api_endpoint():
    print_info("\n=== 测试8：API端点检查 ===")
    
    server_file = YYASISTANT_ROOT / "server.py"
    if server_file.exists():
        content = server_file.read_text(encoding='utf-8')
        
        checks = [
            ("/api/voice-call/save-messages", "API端点路径"),
            ("@app.server.route('/api/voice-call/save-messages'", "API端点装饰器"),
            ("save_voice_call_messages", "API端点函数"),
        ]
        
        for check, description in checks:
            if check in content:
                test_passed(description)
            else:
                test_failed(description)

# 测试9：配置项传递检查
def test_config_transmission():
    print_info("\n=== 测试9：配置项传递检查 ===")
    
    chat_file = YYASISTANT_ROOT / "views" / "core_pages" / "chat.py"
    if chat_file.exists():
        content = chat_file.read_text(encoding='utf-8')
        
        config_items = [
            "VOICE_CALL_SHOW_TRANSCRIPTION",
            "VOICE_CALL_SAVE_TO_DATABASE",
            "VOICE_CALL_AUTO_SAVE_ON_END",
            "VOICE_CALL_MAX_DISPLAY_MESSAGES",
            "VOICE_CALL_TRANSCRIPTION_DEBOUNCE",
            "VOICE_CALL_STREAMING_DISPLAY",
        ]
        
        for item in config_items:
            if item in content:
                test_passed(f"配置项 {item} 传递到前端")
            else:
                test_warning(f"配置项 {item} 可能未传递到前端")

# 测试10：组件ID一致性检查
def test_component_id_consistency():
    print_info("\n=== 测试10：组件ID一致性检查 ===")
    
    # 收集所有组件ID
    component_ids = {
        "voice-call-text-display": [],
        "voice-call-text-content": [],
        "voice-call-text-close-btn": [],
        "voice-call-transcription-display": [],
    }
    
    # 在Python文件中查找
    for file_path in [
        YYASISTANT_ROOT / "views" / "core_pages" / "chat.py",
        YYASISTANT_ROOT / "callbacks" / "voice_call_display_c.py",
    ]:
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            for component_id in component_ids.keys():
                if component_id in content:
                    component_ids[component_id].append(str(file_path))
    
    # 在JavaScript文件中查找
    for file_path in [
        YYASISTANT_ROOT / "assets" / "js" / "voice_websocket_manager.js",
    ]:
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            for component_id in component_ids.keys():
                if component_id in content:
                    component_ids[component_id].append(str(file_path))
    
    # 检查一致性
    for component_id, files in component_ids.items():
        if len(files) > 0:
            test_passed(f"组件ID '{component_id}' 在 {len(files)} 个文件中使用")
        else:
            test_warning(f"组件ID '{component_id}' 未找到")

# 测试11：语法检查（基础）
def test_basic_syntax():
    print_info("\n=== 测试11：基础语法检查 ===")
    
    python_files = [
        YYASISTANT_ROOT / "configs" / "voice_config.py",
        YYASISTANT_ROOT / "callbacks" / "voice_call_display_c.py",
        YYASISTANT_ROOT / "views" / "core_pages" / "chat.py",
        YYCHAT_ROOT / "config" / "realtime_config.py",
    ]
    
    for file_path in python_files:
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                compile(content, str(file_path), 'exec')
                test_passed(f"{file_path.name} 语法正确")
            except SyntaxError as e:
                test_failed(f"{file_path.name} 语法错误", str(e))

# 测试12：导入关系检查
def test_import_relations():
    print_info("\n=== 测试12：导入关系检查 ===")
    
    app_file = YYASISTANT_ROOT / "app.py"
    if app_file.exists():
        content = app_file.read_text(encoding='utf-8')
        
        if "callbacks.voice_call_display_c" in content:
            # 检查回调文件是否存在
            callback_file = YYASISTANT_ROOT / "callbacks" / "voice_call_display_c.py"
            if callback_file.exists():
                test_passed("回调文件导入关系正确")
            else:
                test_failed("回调文件导入关系错误：文件不存在")
        else:
            test_warning("回调文件未在app.py中导入")

# 主测试函数
def run_all_tests():
    print_info("=" * 60)
    print_info("语音实时对话文本显示功能 - 自动化测试")
    print_info("=" * 60)
    
    test_file_existence()
    test_config_items()
    test_code_logic()
    test_store_components()
    test_ui_components()
    test_callback_registration()
    test_backend_scenario_fields()
    test_api_endpoint()
    test_config_transmission()
    test_component_id_consistency()
    test_basic_syntax()
    test_import_relations()
    
    # 输出测试结果摘要
    print_info("\n" + "=" * 60)
    print_info("测试结果摘要")
    print_info("=" * 60)
    
    print_success(f"通过: {len(test_results['passed'])}")
    print_error(f"失败: {len(test_results['failed'])}")
    print_warning(f"警告: {len(test_results['warnings'])}")
    
    if test_results['failed']:
        print_info("\n失败的测试项:")
        for failed in test_results['failed']:
            print_error(f"  - {failed}")
    
    if test_results['warnings']:
        print_info("\n警告项:")
        for warning in test_results['warnings']:
            print_warning(f"  - {warning}")
    
    # 返回测试结果
    return len(test_results['failed']) == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

