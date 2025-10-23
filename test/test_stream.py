#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import requests
import json
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append('../')

from utils.log import log


def test_stream_endpoint():
    """测试/stream端点"""
    log.info("开始测试/stream端点")
    
    # 准备测试数据
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "请简要介绍一下你自己"}
    ]
    
    # 构建请求参数
    request_data = {
        "messages": messages,
        "session_id": "test_session_123",
        "personality_id": "health_assistant",
        "message_id": "test_message_456",
        "role": "assistant"
    }
    
    try:
        # 发送POST请求到/stream端点
        log.info(f"发送请求到/stream端点: {request_data}")
        response = requests.post(
            "http://localhost:8050/stream",
            json=request_data,
            stream=True  # 启用流式响应
        )
        
        # 检查响应状态
        if response.status_code == 200:
            log.info("成功连接到/stream端点，开始接收流式数据...")
            
            # 处理流式响应
            full_content = ""
            for chunk in response.iter_lines():
                if chunk:
                    # 解码chunk并提取数据
                    try:
                        # 移除SSE格式的前缀
                        chunk_str = chunk.decode('utf-8')
                        if chunk_str.startswith('data: '):
                            chunk_data = json.loads(chunk_str[5:])
                            
                            # 打印接收到的数据
                            log.info(f"接收到的chunk数据: {chunk_data}")
                            
                            # 累计内容
                            if 'content' in chunk_data:
                                full_content += chunk_data['content']
                                log.info(f"当前累计内容: {full_content}")
                            
                            # 检查是否结束
                            if 'status' in chunk_data and chunk_data['status'] == 'end':
                                log.info(f"流式传输结束，完整内容: {full_content}")
                                break
                    except json.JSONDecodeError as e:
                        log.error(f"解析chunk数据失败: {e}, chunk: {chunk_str}")
        else:
            log.error(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
    except Exception as e:
        log.error(f"测试过程中发生错误: {e}")


if __name__ == "__main__":
    test_stream_endpoint()