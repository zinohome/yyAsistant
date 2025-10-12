"""
测试配置文件 - 提供全局的测试fixtures和配置
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from peewee import SqliteDatabase

# 设置测试环境
os.environ['TESTING'] = 'true'

@pytest.fixture(scope="session")
def test_db():
    """创建测试数据库"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp()
    
    # 创建测试数据库
    test_database = SqliteDatabase(db_path)
    
    yield test_database
    
    # 清理
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope="function")
def clean_db(test_db):
    """清理数据库状态"""
    # 这里可以添加数据库清理逻辑
    yield
    # 测试后的清理逻辑

@pytest.fixture
def mock_yychat_client():
    """模拟YYChat客户端"""
    with patch('utils.yychat_client.yychat_client') as mock:
        # 配置默认的mock响应
        mock.chat_completion.return_value = {
            "choices": [{
                "message": {
                    "content": "这是一个测试回复"
                }
            }]
        }
        mock.list_models.return_value = {
            "data": [{"id": "test-model", "name": "测试模型"}]
        }
        mock.list_personalities.return_value = {
            "data": [{"id": "test-personality", "name": "测试人格"}]
        }
        yield mock

@pytest.fixture
def mock_flask_login():
    """模拟Flask-Login用户"""
    with patch('flask_login.current_user') as mock_user:
        mock_user.id = "test_user"
        mock_user.is_authenticated = True
        mock_user.is_anonymous = False
        yield mock_user

@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "user_id": "test_user_001",
        "user_name": "testuser",
        "password": "testpassword123",
        "user_role": "normal"
    }

@pytest.fixture
def sample_conversation_data():
    """示例会话数据"""
    return {
        "user_id": "test_user_001",
        "conv_name": "测试会话",
        "conv_memory": {
            "messages": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"}
            ]
        }
    }

@pytest.fixture
def sample_messages():
    """示例消息数据"""
    return [
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "请介绍一下你自己"},
        {"role": "assistant", "content": "我是一个AI助手，可以帮助你解答问题。"}
    ]

@pytest.fixture
def mock_sse_response():
    """模拟SSE响应数据"""
    return [
        {"content": "这是", "status": "streaming"},
        {"content": "一个", "status": "streaming"},
        {"content": "测试", "status": "streaming"},
        {"content": "回复", "status": "end"}
    ]

@pytest.fixture
def test_app():
    """创建测试应用实例"""
    from server import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def authenticated_client(test_app, mock_flask_login):
    """已认证的测试客户端"""
    with test_app.session_transaction() as sess:
        sess['user_id'] = 'test_user_001'
        sess['_fresh'] = True
    
    return test_app

@pytest.fixture(autouse=True)
def setup_test_environment():
    """自动设置测试环境"""
    # 设置测试配置
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    yield
    
    # 清理测试环境
    # 这里可以添加清理逻辑

@pytest.fixture
def temp_directory():
    """创建临时目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_logger():
    """模拟日志记录器"""
    with patch('utils.log.log') as mock_log:
        yield mock_log

@pytest.fixture
def mock_requests():
    """模拟HTTP请求"""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        yield mock_post

# 测试数据生成器
class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def create_user(user_id=None, **kwargs):
        """创建测试用户数据"""
        default_data = {
            "user_id": user_id or f"user_{pytest.current_test_id()}",
            "user_name": f"testuser_{pytest.current_test_id()}",
            "password": "testpassword123",
            "user_role": "normal"
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_conversation(user_id=None, **kwargs):
        """创建测试会话数据"""
        default_data = {
            "user_id": user_id or f"user_{pytest.current_test_id()}",
            "conv_name": f"测试会话_{pytest.current_test_id()}",
            "conv_memory": {"messages": []}
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_message(role="user", content="测试消息", **kwargs):
        """创建测试消息数据"""
        default_data = {
            "role": role,
            "content": content,
            "timestamp": "2024-01-01 12:00:00"
        }
        default_data.update(kwargs)
        return default_data

@pytest.fixture
def data_factory():
    """测试数据工厂fixture"""
    return TestDataFactory

# 参数化测试数据
@pytest.fixture(params=[
    "normal",
    "admin", 
    "guest"
])
def user_role(request):
    """不同用户角色的参数化测试"""
    return request.param

@pytest.fixture(params=[
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
    {"role": "system", "content": "你是一个有帮助的助手"}
])
def message_type(request):
    """不同消息类型的参数化测试"""
    return request.param

# 异步测试支持
@pytest.fixture
def event_loop():
    """创建事件循环用于异步测试"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# 性能测试fixtures
@pytest.fixture
def performance_timer():
    """性能测试计时器"""
    import time
    start_time = time.time()
    yield lambda: time.time() - start_time

@pytest.fixture
def memory_profiler():
    """内存使用分析器"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    yield lambda: process.memory_info().rss - initial_memory
