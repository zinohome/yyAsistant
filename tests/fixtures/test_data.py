"""
测试数据夹具
"""
import json
import uuid
from datetime import datetime, timedelta


class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def create_user_data(user_id=None, user_name=None, password="testpassword123", 
                        user_role="normal", user_icon="👨‍💼", other_info=None):
        """创建用户测试数据"""
        return {
            "user_id": user_id or f"test_user_{uuid.uuid4().hex[:8]}",
            "user_name": user_name or f"testuser_{uuid.uuid4().hex[:8]}",
            "password": password,
            "password_hash": f"hashed_{password}",
            "user_role": user_role,
            "user_icon": user_icon,
            "other_info": other_info or {"test": True, "created_at": datetime.now().isoformat()}
        }
    
    @staticmethod
    def create_conversation_data(user_id=None, conv_name=None, conv_memory=None):
        """创建会话测试数据"""
        return {
            "user_id": user_id or f"test_user_{uuid.uuid4().hex[:8]}",
            "conv_name": conv_name or f"测试会话_{uuid.uuid4().hex[:8]}",
            "conv_memory": conv_memory or {
                "messages": [
                    {"role": "user", "content": "你好"},
                    {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"}
                ],
                "created_at": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def create_chat_message(role="user", content="测试消息", message_id=None):
        """创建聊天消息测试数据"""
        return {
            "role": role,
            "content": content,
            "message_id": message_id or f"msg_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_chat_request(messages=None, session_id=None, personality_id="test_personality", 
                           message_id=None, role="assistant", use_tools=False):
        """创建聊天请求测试数据"""
        return {
            "messages": messages or [
                {"role": "user", "content": "你好，请介绍一下你自己"}
            ],
            "session_id": session_id or f"session_{uuid.uuid4().hex[:8]}",
            "personality_id": personality_id,
            "message_id": message_id or f"msg_{uuid.uuid4().hex[:8]}",
            "role": role,
            "use_tools": use_tools
        }
    
    @staticmethod
    def create_api_response(status="success", data=None, error=None, message=None):
        """创建API响应测试数据"""
        response = {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        if error is not None:
            response["error"] = error
        if message is not None:
            response["message"] = message
            
        return response
    
    @staticmethod
    def create_stream_response(content="测试回复", message_id=None, is_final=True):
        """创建流式响应测试数据"""
        return {
            "id": message_id or f"msg_{uuid.uuid4().hex[:8]}",
            "object": "chat.completion.chunk",
            "created": int(datetime.now().timestamp()),
            "model": "test-model",
            "choices": [{
                "index": 0,
                "delta": {
                    "content": content
                },
                "finish_reason": "stop" if is_final else None
            }]
        }
    
    @staticmethod
    def create_model_list():
        """创建模型列表测试数据"""
        return {
            "models": [
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "description": "快速且经济的模型",
                    "max_tokens": 4096,
                    "supports_streaming": True
                },
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "description": "最强大的模型",
                    "max_tokens": 8192,
                    "supports_streaming": True
                }
            ]
        }
    
    @staticmethod
    def create_personality_list():
        """创建人格列表测试数据"""
        return {
            "personalities": [
                {
                    "id": "friendly",
                    "name": "友好助手",
                    "description": "友好、热情的AI助手",
                    "system_prompt": "你是一个友好、热情的AI助手。"
                },
                {
                    "id": "professional",
                    "name": "专业助手",
                    "description": "专业、正式的AI助手",
                    "system_prompt": "你是一个专业、正式的AI助手。"
                }
            ]
        }
    
    @staticmethod
    def create_error_response(error_code="INTERNAL_ERROR", error_message="内部服务器错误"):
        """创建错误响应测试数据"""
        return {
            "error": {
                "code": error_code,
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def create_performance_metrics(response_time=0.1, memory_usage=1024*1024, cpu_usage=10.0):
        """创建性能指标测试数据"""
        return {
            "response_time": response_time,
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "timestamp": datetime.now().isoformat()
        }


class TestDataSets:
    """测试数据集类"""
    
    @staticmethod
    def get_sample_users(count=5):
        """获取示例用户数据"""
        return [
            TestDataFactory.create_user_data(
                user_id=f"user_{i}",
                user_name=f"testuser{i}",
                user_role="normal" if i < 4 else "admin"
            )
            for i in range(count)
        ]
    
    @staticmethod
    def get_sample_conversations(count=10, user_id="test_user"):
        """获取示例会话数据"""
        return [
            TestDataFactory.create_conversation_data(
                user_id=user_id,
                conv_name=f"会话_{i}",
                conv_memory={
                    "messages": [
                        {"role": "user", "content": f"这是第{i}个会话的消息"},
                        {"role": "assistant", "content": f"这是第{i}个会话的回复"}
                    ]
                }
            )
            for i in range(count)
        ]
    
    @staticmethod
    def get_sample_messages(count=20):
        """获取示例消息数据"""
        messages = []
        for i in range(count):
            role = "user" if i % 2 == 0 else "assistant"
            content = f"这是第{i+1}条消息" if role == "user" else f"这是第{i+1}条回复"
            messages.append(TestDataFactory.create_chat_message(role=role, content=content))
        return messages
    
    @staticmethod
    def get_stress_test_data():
        """获取压力测试数据"""
        return {
            "large_message": "这是一个非常大的消息。" * 1000,  # 约30KB
            "many_messages": TestDataSets.get_sample_messages(100),
            "concurrent_users": TestDataSets.get_sample_users(50),
            "concurrent_sessions": TestDataSets.get_sample_conversations(100)
        }
    
    @staticmethod
    def get_edge_case_data():
        """获取边界情况测试数据"""
        return {
            "empty_strings": {
                "user_name": "",
                "password": "",
                "content": ""
            },
            "very_long_strings": {
                "user_name": "a" * 1000,
                "content": "b" * 10000
            },
            "special_characters": {
                "user_name": "test@#$%^&*()",
                "content": "特殊字符：!@#$%^&*()_+-=[]{}|;':\",./<>?"
            },
            "unicode_strings": {
                "user_name": "测试用户🚀",
                "content": "你好世界！🌍 这是一个包含emoji的消息。"
            },
            "sql_injection": {
                "user_name": "'; DROP TABLE users; --",
                "content": "SELECT * FROM users WHERE 1=1; --"
            }
        }


class MockDataProvider:
    """模拟数据提供者"""
    
    def __init__(self):
        self.data_factory = TestDataFactory()
        self.data_sets = TestDataSets()
    
    def get_mock_user(self, **kwargs):
        """获取模拟用户"""
        return self.data_factory.create_user_data(**kwargs)
    
    def get_mock_conversation(self, **kwargs):
        """获取模拟会话"""
        return self.data_factory.create_conversation_data(**kwargs)
    
    def get_mock_chat_request(self, **kwargs):
        """获取模拟聊天请求"""
        return self.data_factory.create_chat_request(**kwargs)
    
    def get_mock_api_response(self, **kwargs):
        """获取模拟API响应"""
        return self.data_factory.create_api_response(**kwargs)
    
    def get_mock_stream_response(self, **kwargs):
        """获取模拟流式响应"""
        return self.data_factory.create_stream_response(**kwargs)
    
    def get_mock_error_response(self, **kwargs):
        """获取模拟错误响应"""
        return self.data_factory.create_error_response(**kwargs)
    
    def get_mock_performance_metrics(self, **kwargs):
        """获取模拟性能指标"""
        return self.data_factory.create_performance_metrics(**kwargs)
