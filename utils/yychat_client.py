#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests
from typing import Dict, List, Any, Optional, Generator
from configs.base_config import BaseConfig
from utils.log import log

class YYChatClient:
    """YYChat API客户端封装"""
    
    def __init__(self):
        """初始化YYChat客户端"""
        self.api_base_url = BaseConfig.yychat_api_base_url
        # 从环境变量获取API密钥
        self.api_key = BaseConfig.yychat_api_key
        if not self.api_key:
            log.warning(f"未找到yychat_api_key，请确保已正确配置API密钥")
        
        # 设置默认请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def chat_completion(self, 
                        messages: List[Dict[str, str]],
                        model: str = None,
                        temperature: float = None,
                        stream: bool = None,
                        conversation_id: str = None,
                        personality_id: str = None,
                        use_tools: bool = None,
                        **kwargs) -> Dict[str, Any]:
        """
        调用聊天完成API
        """
        # 验证并修复消息列表中的角色字段
        validated_messages = []
        for msg in messages:
            # 确保每个消息都有有效的role字段
            if "role" not in msg or not msg["role"]:
                log.warning(f"发现无效消息角色，默认为'user': {msg}")
                validated_msg = {**msg, "role": "user"}
            else:
                validated_msg = msg
            validated_messages.append(validated_msg)
        
        # 设置请求参数
        payload = {
            "model": model or BaseConfig.yychat_default_model,
            "messages": validated_messages,  # 使用验证后的消息列表
            "temperature": temperature if temperature is not None else BaseConfig.yychat_default_temperature,
            "stream": stream if stream is not None else BaseConfig.yychat_default_stream,
        }
        
        # 添加可选参数
        if conversation_id:
            payload["conversation_id"] = conversation_id
        if personality_id:
            payload["personality_id"] = personality_id
        if use_tools is not None:
            payload["use_tools"] = use_tools
        
        # 添加其他自定义参数
        payload.update(kwargs)
        
        # 构建请求URL
        url = f"{self.api_base_url}/chat/completions"
        
        log.debug(f"调用YYChat API: {url}, payload: {payload}")
        
        try:
            # 发送请求
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload,
                stream=payload["stream"]
            )
            
            # 检查响应状态
            if response.status_code != 200:
                log.error(f"YYChat API调用失败: {response.status_code}, {response.text}")
                # 尝试解析错误响应
                try:
                    error_data = response.json()
                    raise Exception(f"API错误: {error_data.get('error', {}).get('message', '未知错误')}")
                except:
                    raise Exception(f"API请求失败: HTTP {response.status_code}")
            
            # 处理流式响应
            if payload["stream"]:
                # 返回流式响应生成器
                return self._process_streaming_response(response)
            else:
                # 处理非流式响应
                try:
                    # 尝试直接解析JSON响应
                    return response.json()
                except Exception as json_error:
                    log.warning(f"直接解析JSON失败，尝试其他方式处理响应: {str(json_error)}")
                    # 尝试以流式方式处理非流式响应（应对服务器可能的行为不一致）
                    return self._process_streaming_response(response)
                    
        except Exception as e:
            log.error(f"YYChat API调用异常: {str(e)}")
            raise
    
    def _process_streaming_response(self, response: requests.Response) -> Generator[Dict[str, Any], None, None]:
        """
        处理流式响应，返回生成器
        """
        for chunk in response.iter_lines():
            if chunk:
                # 去除data:前缀
                data = chunk.decode("utf-8").replace("data: ", "")
                if data == "[DONE]":
                    break
                try:
                    # 解析JSON数据
                    json_data = json.loads(data)
                    yield json_data
                except json.JSONDecodeError:
                    log.warning(f"无法解析流式响应数据: {data}")
                    continue
    
    def list_models(self) -> Dict[str, Any]:
        """列出所有可用模型"""
        url = f"{self.api_base_url}/models"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log.error(f"获取模型列表失败: {str(e)}")
            raise
    
    def list_personalities(self) -> Dict[str, Any]:
        """列出所有可用人格"""
        url = f"{self.api_base_url}/personalities"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log.error(f"获取人格列表失败: {str(e)}")
            raise
    
    def get_conversation_memory(self, conversation_id: str) -> Dict[str, Any]:
        """获取指定会话的记忆"""
        url = f"{self.api_base_url}/conversations/{conversation_id}/memory"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log.error(f"获取会话记忆失败: {str(e)}")
            raise
    
    def clear_conversation_memory(self, conversation_id: str) -> Dict[str, Any]:
        """清除指定会话的记忆"""
        url = f"{self.api_base_url}/conversations/{conversation_id}/memory"
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log.error(f"清除会话记忆失败: {str(e)}")
            raise

# 创建全局实例，方便其他模块直接导入使用
yychat_client = YYChatClient()