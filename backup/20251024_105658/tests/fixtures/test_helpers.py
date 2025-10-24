"""
测试辅助工具
"""
import os
import sys
import time
import json
import hashlib
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
import psutil
import threading
from typing import Dict, Any, List, Optional


class TestEnvironment:
    """测试环境管理类"""
    
    @staticmethod
    def setup_test_environment():
        """设置测试环境"""
        # 设置测试环境变量
        os.environ['TESTING'] = 'true'
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix='yyasistant_test_')
        os.environ['TEMP_DIR'] = temp_dir
        
        return temp_dir
    
    @staticmethod
    def cleanup_test_environment(temp_dir: str):
        """清理测试环境"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"清理测试环境时出错: {e}")
        
        # 清理环境变量
        test_env_vars = ['TESTING', 'FLASK_ENV', 'DATABASE_URL', 'TEMP_DIR']
        for var in test_env_vars:
            os.environ.pop(var, None)


class DatabaseHelper:
    """数据库测试辅助类"""
    
    @staticmethod
    def create_test_database():
        """创建测试数据库"""
        from models.init_db import database
        from models.users import Users
        from models.conversations import Conversations
        
        # 创建表
        database.create_tables([Users, Conversations])
        return database
    
    @staticmethod
    def clear_test_database():
        """清空测试数据库"""
        from models.init_db import database
        from models.users import Users
        from models.conversations import Conversations
        
        # 删除所有数据
        Users.delete().execute()
        Conversations.delete().execute()
    
    @staticmethod
    def populate_test_data():
        """填充测试数据"""
        from models.users import Users
        from models.conversations import Conversations
        from fixtures.test_data import TestDataFactory
        
        data_factory = TestDataFactory()
        
        # 创建测试用户
        test_users = [
            data_factory.create_user_data(user_id="test_user_1", user_name="testuser1"),
            data_factory.create_user_data(user_id="test_user_2", user_name="testuser2"),
            data_factory.create_user_data(user_id="admin_user", user_name="admin", user_role="admin")
        ]
        
        for user_data in test_users:
            Users.add_user(**user_data)
        
        # 创建测试会话
        test_conversations = [
            data_factory.create_conversation_data(user_id="test_user_1", conv_name="会话1"),
            data_factory.create_conversation_data(user_id="test_user_1", conv_name="会话2"),
            data_factory.create_conversation_data(user_id="test_user_2", conv_name="会话3")
        ]
        
        for conv_data in test_conversations:
            Conversations.add_conversation(**conv_data)


class MockHelper:
    """模拟对象辅助类"""
    
    @staticmethod
    def create_mock_yychat_client():
        """创建模拟YYChat客户端"""
        mock_client = MagicMock()
        
        # 模拟聊天完成方法
        mock_client.chat_completion.return_value = {
            "status": "success",
            "data": {
                "message": "测试回复",
                "message_id": "test_message_123"
            }
        }
        
        # 模拟流式聊天方法
        mock_client.chat_completion_stream.return_value = [
            {"content": "测试", "is_final": False},
            {"content": "回复", "is_final": False},
            {"content": "完成", "is_final": True}
        ]
        
        # 模拟模型列表方法
        mock_client.list_models.return_value = {
            "models": [
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
                {"id": "gpt-4", "name": "GPT-4"}
            ]
        }
        
        # 模拟人格列表方法
        mock_client.list_personalities.return_value = {
            "personalities": [
                {"id": "friendly", "name": "友好助手"},
                {"id": "professional", "name": "专业助手"}
            ]
        }
        
        return mock_client
    
    @staticmethod
    def create_mock_flask_app():
        """创建模拟Flask应用"""
        mock_app = MagicMock()
        mock_app.config = {
            'TESTING': True,
            'SECRET_KEY': 'test_secret_key',
            'DATABASE_URL': 'sqlite:///:memory:'
        }
        
        # 模拟测试客户端
        mock_client = MagicMock()
        mock_app.test_client.return_value = mock_client
        
        return mock_app
    
    @staticmethod
    def create_mock_dash_app():
        """创建模拟Dash应用"""
        mock_app = MagicMock()
        mock_app.server = MagicMock()
        mock_app.server.config = {
            'TESTING': True,
            'SECRET_KEY': 'test_secret_key'
        }
        
        return mock_app


class PerformanceHelper:
    """性能测试辅助类"""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        return {
            "result": result,
            "execution_time": end_time - start_time
        }
    
    @staticmethod
    def measure_memory_usage():
        """测量当前内存使用量"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss  # 返回RSS内存使用量（字节）
    
    @staticmethod
    def measure_cpu_usage(duration=1.0):
        """测量CPU使用率"""
        process = psutil.Process()
        
        # 获取初始CPU时间
        cpu_times_1 = process.cpu_times()
        time.sleep(duration)
        cpu_times_2 = process.cpu_times()
        
        # 计算CPU使用率
        cpu_usage = (cpu_times_2.user - cpu_times_1.user + 
                    cpu_times_2.system - cpu_times_1.system) / duration * 100
        
        return cpu_usage
    
    @staticmethod
    def create_memory_profiler():
        """创建内存分析器"""
        initial_memory = PerformanceHelper.measure_memory_usage()
        
        def profiler():
            current_memory = PerformanceHelper.measure_memory_usage()
            return current_memory - initial_memory
        
        return profiler


class AssertionHelper:
    """断言辅助类"""
    
    @staticmethod
    def assert_response_structure(response_data: Dict[str, Any], expected_fields: List[str]):
        """断言响应结构"""
        for field in expected_fields:
            assert field in response_data, f"响应中缺少字段: {field}"
    
    @staticmethod
    def assert_error_response(response_data: Dict[str, Any], expected_error_code: str = None):
        """断言错误响应"""
        assert "error" in response_data, "响应中缺少error字段"
        
        if expected_error_code:
            assert response_data["error"].get("code") == expected_error_code, \
                f"错误代码不匹配: 期望{expected_error_code}, 实际{response_data['error'].get('code')}"
    
    @staticmethod
    def assert_success_response(response_data: Dict[str, Any]):
        """断言成功响应"""
        assert response_data.get("status") == "success", \
            f"响应状态不是success: {response_data.get('status')}"
    
    @staticmethod
    def assert_performance_metrics(metrics: Dict[str, Any], 
                                 max_response_time: float = 1.0,
                                 max_memory_usage: int = 100 * 1024 * 1024,
                                 max_cpu_usage: float = 50.0):
        """断言性能指标"""
        if "response_time" in metrics:
            assert metrics["response_time"] <= max_response_time, \
                f"响应时间过长: {metrics['response_time']:.3f}s > {max_response_time}s"
        
        if "memory_usage" in metrics:
            assert metrics["memory_usage"] <= max_memory_usage, \
                f"内存使用过高: {metrics['memory_usage'] / 1024 / 1024:.2f}MB > {max_memory_usage / 1024 / 1024:.2f}MB"
        
        if "cpu_usage" in metrics:
            assert metrics["cpu_usage"] <= max_cpu_usage, \
                f"CPU使用率过高: {metrics['cpu_usage']:.2f}% > {max_cpu_usage:.2f}%"


class DataValidationHelper:
    """数据验证辅助类"""
    
    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]):
        """验证用户数据"""
        required_fields = ["user_id", "user_name", "password_hash"]
        
        for field in required_fields:
            assert field in user_data, f"用户数据缺少必需字段: {field}"
        
        assert isinstance(user_data["user_id"], str), "user_id必须是字符串"
        assert isinstance(user_data["user_name"], str), "user_name必须是字符串"
        assert isinstance(user_data["password_hash"], str), "password_hash必须是字符串"
        assert len(user_data["user_id"]) > 0, "user_id不能为空"
        assert len(user_data["user_name"]) > 0, "user_name不能为空"
    
    @staticmethod
    def validate_conversation_data(conv_data: Dict[str, Any]):
        """验证会话数据"""
        required_fields = ["user_id", "conv_name"]
        
        for field in required_fields:
            assert field in conv_data, f"会话数据缺少必需字段: {field}"
        
        assert isinstance(conv_data["user_id"], str), "user_id必须是字符串"
        assert isinstance(conv_data["conv_name"], str), "conv_name必须是字符串"
        assert len(conv_data["user_id"]) > 0, "user_id不能为空"
        assert len(conv_data["conv_name"]) > 0, "conv_name不能为空"
    
    @staticmethod
    def validate_chat_message(message_data: Dict[str, Any]):
        """验证聊天消息数据"""
        required_fields = ["role", "content"]
        
        for field in required_fields:
            assert field in message_data, f"消息数据缺少必需字段: {field}"
        
        assert message_data["role"] in ["user", "assistant", "system"], \
            f"无效的角色: {message_data['role']}"
        assert isinstance(message_data["content"], str), "content必须是字符串"
        assert len(message_data["content"]) > 0, "content不能为空"


class TestDataCleaner:
    """测试数据清理类"""
    
    @staticmethod
    def cleanup_test_files():
        """清理测试文件"""
        test_files = [
            "test_database.db",
            "test_logs.log",
            "test_temp_files"
        ]
        
        for file_path in test_files:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"清理文件{file_path}时出错: {e}")
    
    @staticmethod
    def cleanup_test_database():
        """清理测试数据库"""
        DatabaseHelper.clear_test_database()
    
    @staticmethod
    def cleanup_all():
        """清理所有测试数据"""
        TestDataCleaner.cleanup_test_files()
        TestDataCleaner.cleanup_test_database()


@contextmanager
def temporary_environment(**env_vars):
    """临时环境变量上下文管理器"""
    original_env = {}
    
    try:
        # 设置临时环境变量
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        yield
    finally:
        # 恢复原始环境变量
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


@contextmanager
def temporary_database():
    """临时数据库上下文管理器"""
    from models.init_db import database
    from models.users import Users
    from models.conversations import Conversations
    
    try:
        # 创建临时表
        database.create_tables([Users, Conversations])
        yield database
    finally:
        # 清理临时表
        database.drop_tables([Users, Conversations])


class TestLogger:
    """测试日志类"""
    
    def __init__(self, log_file="test.log"):
        self.log_file = log_file
        self.logs = []
    
    def log(self, level, message):
        """记录日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level.upper()}: {message}"
        self.logs.append(log_entry)
        
        # 写入文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def info(self, message):
        """记录信息日志"""
        self.log("info", message)
    
    def error(self, message):
        """记录错误日志"""
        self.log("error", message)
    
    def warning(self, message):
        """记录警告日志"""
        self.log("warning", message)
    
    def debug(self, message):
        """记录调试日志"""
        self.log("debug", message)
    
    def get_logs(self):
        """获取所有日志"""
        return self.logs
    
    def clear_logs(self):
        """清空日志"""
        self.logs = []
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
