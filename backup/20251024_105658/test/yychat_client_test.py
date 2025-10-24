#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import argparse
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append('../')

from utils.yychat_client import yychat_client
from utils.log import log


def test_chat_completion(non_stream: bool = False):
    """测试聊天完成API"""
    log.info(f"开始测试聊天完成API (流式响应: {not non_stream})")
    
    # 准备测试消息
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "请简要介绍一下你自己"}
    ]
    
    try:
        # 调用聊天完成API
        if non_stream:
            # 非流式调用
            response = yychat_client.chat_completion(
                messages=messages,
                stream=False,
                conversation_id="test_conversation"
            )
            
            log.info("非流式响应结果:")
            if response and "choices" in response:
                assistant_message = response["choices"][0]["message"]["content"]
                log.info(f"助手回复: {assistant_message}")
            else:
                log.warning(f"响应格式异常: {response}")
                
        else:
            # 流式调用
            log.info("流式响应结果:")
            full_response = ""
            
            # 获取流式响应生成器
            response_generator = yychat_client.chat_completion(
                messages=messages,
                stream=True,
                conversation_id="test_conversation"
            )
            
            # 处理流式响应
            for chunk in response_generator:
                if "choices" in chunk:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        content = delta["content"]
                        full_response += content
                        print(content, end="", flush=True)
            
            print()  # 换行
            log.info(f"完整响应: {full_response}")
            
        log.success("聊天完成API测试成功")
        return True
        
    except Exception as e:
        log.error(f"聊天完成API测试失败: {str(e)}")
        return False


def test_list_models():
    """测试列出模型API"""
    log.info("开始测试列出模型API")
    
    try:
        response = yychat_client.list_models()
        log.info(f"模型列表: {response}")
        
        if response and "data" in response:
            log.success(f"成功获取{len(response['data'])}个模型")
        else:
            log.warning("未获取到模型列表")
            
        log.success("列出模型API测试成功")
        return True
        
    except Exception as e:
        log.error(f"列出模型API测试失败: {str(e)}")
        return False


def test_list_personalities():
    """测试列出人格API"""
    log.info("开始测试列出人格API")
    
    try:
        response = yychat_client.list_personalities()
        log.info(f"人格列表: {response}")
        
        if response and "data" in response:
            log.success(f"成功获取{len(response['data'])}个人格")
        else:
            log.warning("未获取到人格列表")
            
        log.success("列出人格API测试成功")
        return True
        
    except Exception as e:
        log.error(f"列出人格API测试失败: {str(e)}")
        return False


def test_conversation_memory():
    """测试会话记忆API"""
    log.info("开始测试会话记忆API")
    
    conversation_id = "test_conversation"
    
    try:
        # 先发送一条消息以创建会话记忆
        yychat_client.chat_completion(
            messages=[{"role": "user", "content": "这是一条测试消息，用于测试会话记忆功能"}],
            conversation_id=conversation_id,
            stream=False
        )
        
        # 获取会话记忆
        log.info(f"获取会话ID {conversation_id} 的记忆")
        response = yychat_client.get_conversation_memory(conversation_id)
        log.info(f"会话记忆: {response}")
        
        if response and "data" in response:
            log.success(f"成功获取{len(response['data'])}条会话记忆")
        else:
            log.warning("未获取到会话记忆")
            
        # 清除会话记忆
        log.info(f"清除会话ID {conversation_id} 的记忆")
        clear_response = yychat_client.clear_conversation_memory(conversation_id)
        log.info(f"清除记忆结果: {clear_response}")
        
        if clear_response and clear_response.get("success"):
            log.success("成功清除会话记忆")
        else:
            log.warning("清除会话记忆失败")
            
        log.success("会话记忆API测试成功")
        return True
        
    except Exception as e:
        log.error(f"会话记忆API测试失败: {str(e)}")
        return False


def run_all_tests():
    """运行所有测试"""
    log.info("开始运行所有YYChat客户端测试")
    
    # 记录开始时间
    start_time = time.time()
    
    # 测试结果统计
    tests = [
        ("聊天完成API (流式)", test_chat_completion, False),
        ("聊天完成API (非流式)", test_chat_completion, True),
        ("列出模型API", test_list_models),
        ("列出人格API", test_list_personalities),
        ("会话记忆API", test_conversation_memory)
    ]
    
    success_count = 0
    
    for name, test_func, *args in tests:
        log.info(f"\n===== 测试: {name} =====")
        if test_func(*args):
            success_count += 1
    
    # 计算总耗时
    elapsed_time = time.time() - start_time
    
    # 输出测试结果汇总
    log.info(f"\n===== 测试结果汇总 =====")
    log.info(f"总测试数: {len(tests)}")
    log.info(f"成功测试数: {success_count}")
    log.info(f"失败测试数: {len(tests) - success_count}")
    log.info(f"总耗时: {elapsed_time:.2f} 秒")
    
    if success_count == len(tests):
        log.success("所有测试均已通过！")
    else:
        log.warning("部分测试未通过，请检查问题。")


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="YYChat API客户端测试工具")
    parser.add_argument("--test", choices=["all", "chat", "models", "personalities", "memory"], 
                        default="all", help="指定要运行的测试类型")
    parser.add_argument("--non-stream", action="store_true", help="使用非流式响应模式测试聊天API")
    
    args = parser.parse_args()
    
    # 根据命令行参数运行相应的测试
    if args.test == "all":
        run_all_tests()
    elif args.test == "chat":
        test_chat_completion(args.non_stream)
    elif args.test == "models":
        test_list_models()
    elif args.test == "personalities":
        test_list_personalities()
    elif args.test == "memory":
        test_conversation_memory()