#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import copy  # 导入copy模块用于深拷贝
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
    
    def _serialize_payload_for_log(self, payload: Dict[str, Any]) -> str:
        """序列化请求载荷用于日志记录，避免loguru处理字典时的问题"""
        try:
            # 使用深拷贝避免修改原始数据和确保嵌套结构正确复制
            payload_copy = copy.deepcopy(payload)
            
            # 特殊处理messages字段，确保角色字段被正确保留
            if "messages" in payload_copy:
                # 确保messages中的每个消息都有正确的role字段
                validated_messages = []
                for msg in payload_copy["messages"]:
                    if isinstance(msg, dict):
                        # 检查msg的键是否都是有效的字符串
                        valid_msg = {}
                        for k, v in msg.items():
                            if isinstance(k, str):  # 确保键是字符串
                                valid_msg[k] = v
                            else:
                                log.warning(f"发现非字符串键: {k}")
                        
                        # 确保有有效的role字段
                        if "role" not in valid_msg or not valid_msg["role"]:
                            validated_messages.append({"role": "user", **valid_msg})
                        else:
                            validated_messages.append(valid_msg)
                    else:
                        # 如果消息不是字典，记录警告并跳过
                        log.warning(f"消息不是有效的字典格式: {msg}")
                payload_copy["messages"] = validated_messages
            
            # 使用json.dumps确保正确序列化
            serialized = json.dumps(payload_copy, ensure_ascii=False)
            return serialized
        except Exception as e:
            log.error(f"序列化日志数据失败: {str(e)}")
            try:
                # 作为备选方案，尝试使用更简单的序列化方式
                return str(payload)
            except:
                return "无法序列化的payload"
    
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
        for i, msg in enumerate(messages):
            # 确保每个消息都有有效的role字段
            if "role" not in msg or not msg["role"]:
                log.warning(f"发现无效消息角色，默认为'user': {msg}")
                validated_msg = {"role": "user", **msg}
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
        
        # 分别记录不同部分的日志，避免单行过长被截断
        log.debug(f"调用YYChat API: {url}")
        log.debug(f"请求参数概览 - model: {payload.get('model')}, personality_id: {payload.get('personality_id')}, conversation_id: {payload.get('conversation_id')}, use_tools: {payload.get('use_tools')}, stream: {payload.get('stream')}")
        
        # 额外添加调试日志，直接打印原始消息列表和修复后的消息列表
        #log.debug(f"原始消息列表: {messages}")
        #log.debug(f"修复后消息列表: {validated_messages}")
        
        # 详细记录payload，但避免单行过长
        '''
        try:
            # 将payload拆分成多行记录，避免被截断
            #payload_str = json.dumps(payload, ensure_ascii=False, indent=2)
            # 由于loguru可能仍会截断长消息，我们可以只记录关键部分
            #log.debug(f"Payload结构 (关键部分):")
            #log.debug(f"- model: {payload.get('model')}")
            #log.debug(f"- stream: {payload.get('stream')}")
            log.debug(f"- conversation_id: {payload.get('conversation_id')}")
            
            # 获取消息列表
            #messages_list = payload.get('messages', [])
            #log.debug(f"- 消息数量: {len(messages_list)}")
        except Exception as e:
            log.warning(f"记录Payload详情失败: {str(e)}")
        '''
        
        try:
            # 发送请求，设置较长的超时时间以支持第一次请求的Memory初始化
            timeout = 30 if payload["stream"] else 60  # 流式请求30秒，非流式请求60秒
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload,
                stream=payload["stream"],
                timeout=timeout
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
                # 处理非流式响应 - 确保始终返回Dict，而不是Generator
                try:
                    # 尝试直接解析JSON响应
                    return response.json()
                except Exception as json_error:
                    log.warning(f"直接解析JSON失败: {str(json_error)}")
                    log.warning(f"响应内容: {response.text[:200]}...")  # 只打印部分内容避免日志过长
                    # 不尝试以流式方式处理，而是抛出异常让调用方处理
                    raise Exception(f"解析非流式响应失败: {str(json_error)}")
            
        except requests.exceptions.Timeout:
            log.error(f"YYChat API调用超时 (超时时间: {timeout}秒)")
            raise Exception(f"API请求超时，请稍后重试。首次请求可能需要更长时间来初始化Memory。")
        except requests.exceptions.ConnectionError:
            log.error(f"YYChat API连接错误")
            raise Exception(f"无法连接到YYChat API服务器，请检查网络连接。")
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