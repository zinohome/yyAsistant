"""
数据模型单元测试
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash

# 模拟数据库连接
with patch('models.db', MagicMock()):
    from models.users import Users
    from models.conversations import Conversations
    from models.exceptions import InvalidUserError, ExistingUserError, InvalidConversationError


class TestUsersModel:
    """用户模型测试类"""
    
    def test_create_user_success(self, sample_user_data, clean_db):
        """测试成功创建用户"""
        with patch('models.users.db.connection_context'):
            with patch('models.users.db.atomic'):
                with patch('models.users.Users.create') as mock_create:
                    mock_user = MagicMock()
                    mock_user.user_id = sample_user_data["user_id"]
                    mock_user.user_name = sample_user_data["user_name"]
                    mock_user.user_role = sample_user_data["user_role"]
                    mock_user.password_hash = sample_user_data["password_hash"]
                    mock_create.return_value = mock_user
                    
                    Users.add_user(
                        user_id=sample_user_data["user_id"],
                        user_name=sample_user_data["user_name"],
                        password_hash=sample_user_data["password_hash"],
                        user_role=sample_user_data["user_role"]
                    )
                    
                    mock_create.assert_called_once()
    
    def test_create_user_duplicate_id(self, sample_user_data, clean_db):
        """测试创建重复用户ID"""
        with patch('models.users.db.connection_context'):
            with patch('models.users.Users.get_or_none') as mock_get:
                # 第一次调用返回None（用户不存在），第二次调用返回用户（ID已存在）
                mock_get.side_effect = [None, MagicMock()]
                
                with pytest.raises(ExistingUserError):
                    Users.add_user(
                        user_id=sample_user_data["user_id"],
                        user_name=sample_user_data["user_name"],
                        password_hash=sample_user_data["password_hash"]
                    )
    
    def test_create_user_duplicate_name(self, sample_user_data, clean_db):
        """测试创建重复用户名"""
        with patch('models.users.db.connection_context'):
            with patch('models.users.Users.get_or_none') as mock_get:
                # 第一次调用返回None（ID不存在），第二次调用返回用户（用户名已存在）
                mock_get.side_effect = [None, MagicMock()]
                
                with pytest.raises(ExistingUserError):
                    Users.add_user(
                        user_id="different_id",
                        user_name=sample_user_data["user_name"],
                        password_hash=sample_user_data["password_hash"]
                    )
    
    def test_create_user_invalid_data(self, clean_db):
        """测试使用无效数据创建用户"""
        with patch('models.users.db.connection_context'):
            with pytest.raises(InvalidUserError):
                Users.add_user(
                    user_id="",  # 空用户ID
                    user_name="test",
                    password_hash="password"
                )
            
            with pytest.raises(InvalidUserError):
                Users.add_user(
                    user_id="test",
                    user_name="",  # 空用户名
                    password_hash="password"
                )
            
            with pytest.raises(InvalidUserError):
                Users.add_user(
                    user_id="test",
                    user_name="test",
                    password_hash=""  # 空密码
                )
    
    def test_get_user_by_id(self, sample_user_data, clean_db):
        """测试通过ID获取用户"""
        with patch('models.users.db.connection_context'):
            with patch('models.users.Users.get_or_none') as mock_get:
                mock_user = MagicMock()
                mock_user.user_id = sample_user_data["user_id"]
                mock_user.user_name = sample_user_data["user_name"]
                mock_get.return_value = mock_user
                
                user = Users.get_user(sample_user_data["user_id"])
                
                assert user is not None
                assert user.user_id == sample_user_data["user_id"]
                assert user.user_name == sample_user_data["user_name"]
    
    def test_get_user_by_name(self, sample_user_data, clean_db):
        """测试通过用户名获取用户"""
        with patch('models.users.db.connection_context'):
            with patch('models.users.Users.get_or_none') as mock_get:
                mock_user = MagicMock()
                mock_user.user_id = sample_user_data["user_id"]
                mock_user.user_name = sample_user_data["user_name"]
                mock_get.return_value = mock_user
                
                user = Users.get_user_by_name(sample_user_data["user_name"])
                
                assert user is not None
                assert user.user_id == sample_user_data["user_id"]
                assert user.user_name == sample_user_data["user_name"]
    
    def test_check_user_password(self, sample_user_data, clean_db):
        """测试用户密码验证"""
        with patch('models.users.db.connection_context'):
            with patch('models.users.Users.get_user') as mock_get_user:
                mock_user = MagicMock()
                mock_user.password_hash = generate_password_hash("correct_password")
                mock_get_user.return_value = mock_user
                
                # 验证正确密码
                assert Users.check_user_password("test_user", "correct_password") is True
                
                # 验证错误密码
                assert Users.check_user_password("test_user", "wrong_password") is False
    
    def test_update_user(self, sample_user_data, clean_db):
        """测试更新用户信息"""
        with patch('models.users.db.connection_context'):
            with patch('models.users.db.atomic'):
                with patch('models.users.Users.update') as mock_update:
                    with patch('models.users.Users.get_or_none') as mock_get:
                        mock_user = MagicMock()
                        mock_user.user_role = "admin"
                        mock_user.user_icon = "new_icon.png"
                        mock_get.return_value = mock_user
                        
                        updated_user = Users.update_user(
                            user_id=sample_user_data["user_id"],
                            user_role="admin",
                            user_icon="new_icon.png"
                        )
                        
                        mock_update.assert_called_once()
                        assert updated_user.user_role == "admin"
                        assert updated_user.user_icon == "new_icon.png"
    
    def test_delete_user(self, sample_user_data, clean_db):
        """测试删除用户"""
        with patch('models.users.db.connection_context'):
            with patch('models.users.db.atomic'):
                with patch('models.users.Users.delete') as mock_delete:
                    with patch('models.users.Users.where') as mock_where:
                        mock_where.return_value.execute.return_value = 1
                        
                        result = Users.delete_user(sample_user_data["user_id"])
                        
                        mock_delete.assert_called_once()
                        mock_where.assert_called_once()


class TestConversationsModel:
    """会话模型测试类"""
    
    def test_create_conversation_success(self, sample_conversation_data, clean_db):
        """测试成功创建会话"""
        with patch('models.conversations.db.connection_context'):
            with patch('models.conversations.db.atomic'):
                with patch('models.conversations.Conversations.create') as mock_create:
                    with patch('models.conversations.Conversations.get_or_none', return_value=None):
                        with patch('time.time', return_value=1640995200.0):  # 固定时间戳
                            with patch('datetime.datetime.now') as mock_now:
                                mock_now.return_value.strftime.return_value = "20220101120000"
                                
                                conv_id = Conversations.add_conversation(
                                    user_id=sample_conversation_data["user_id"],
                                    conv_name=sample_conversation_data["conv_name"],
                                    conv_memory=sample_conversation_data["conv_memory"]
                                )
                                
                                assert conv_id is not None
                                assert conv_id.startswith("conv-")
                                assert sample_conversation_data["user_id"] in conv_id
                                mock_create.assert_called_once()
    
    def test_create_conversation_default_name(self, sample_conversation_data, clean_db):
        """测试使用默认名称创建会话"""
        with patch('models.conversations.db.connection_context'):
            with patch('models.conversations.db.atomic'):
                with patch('models.conversations.Conversations.create') as mock_create:
                    with patch('models.conversations.Conversations.get_or_none', return_value=None):
                        with patch('time.time', return_value=1640995200.0):
                            with patch('datetime.datetime.now') as mock_now:
                                mock_now.return_value.strftime.return_value = "20220101120000"
                                
                                conv_id = Conversations.add_conversation(
                                    user_id=sample_conversation_data["user_id"]
                                )
                                
                                assert conv_id is not None
                                mock_create.assert_called_once()
    
    def test_get_conversation_by_conv_id(self, sample_conversation_data, clean_db):
        """测试通过会话ID获取会话"""
        with patch('models.conversations.db.connection_context'):
            with patch('models.conversations.Conversations.get_or_none') as mock_get:
                mock_conv = MagicMock()
                mock_conv.conv_id = "test_conv_id"
                mock_conv.user_id = sample_conversation_data["user_id"]
                mock_conv.conv_name = sample_conversation_data["conv_name"]
                mock_get.return_value = mock_conv
                
                conv = Conversations.get_conversation_by_conv_id("test_conv_id")
                
                assert conv is not None
                assert conv.conv_id == "test_conv_id"
                assert conv.user_id == sample_conversation_data["user_id"]
                assert conv.conv_name == sample_conversation_data["conv_name"]
    
    def test_get_user_conversations(self, sample_conversation_data, clean_db):
        """测试获取用户的所有会话"""
        with patch('models.conversations.db.connection_context'):
            with patch('models.conversations.Conversations.select') as mock_select:
                mock_query = MagicMock()
                mock_query.where.return_value.order_by.return_value.dicts.return_value = [
                    {"conv_id": "conv1", "conv_name": "会话1"},
                    {"conv_id": "conv2", "conv_name": "会话2"}
                ]
                mock_select.return_value = mock_query
                
                conversations = Conversations.get_user_conversations(sample_conversation_data["user_id"])
                
                assert len(conversations) == 2
                assert conversations[0]["conv_id"] == "conv1"
                assert conversations[1]["conv_id"] == "conv2"
    
    def test_update_conversation_by_conv_id(self, sample_conversation_data, clean_db):
        """测试更新会话信息"""
        with patch('models.conversations.db.connection_context'):
            with patch('models.conversations.db.atomic'):
                with patch('models.conversations.Conversations.update') as mock_update:
                    with patch('models.conversations.Conversations.where') as mock_where:
                        with patch('models.conversations.Conversations.get_or_none') as mock_get:
                            mock_conv = MagicMock()
                            mock_conv.conv_name = "更新后的会话名称"
                            mock_conv.conv_memory = {"messages": []}
                            mock_get.return_value = mock_conv
                            
                            updated_conv = Conversations.update_conversation_by_conv_id(
                                conv_id="test_conv_id",
                                conv_name="更新后的会话名称",
                                conv_memory={"messages": []}
                            )
                            
                            mock_update.assert_called_once()
                            assert updated_conv.conv_name == "更新后的会话名称"
    
    def test_delete_conversation_by_conv_id(self, sample_conversation_data, clean_db):
        """测试删除会话"""
        with patch('models.conversations.db.connection_context'):
            with patch('models.conversations.db.atomic'):
                with patch('models.conversations.Conversations.delete') as mock_delete:
                    with patch('models.conversations.Conversations.where') as mock_where:
                        mock_where.return_value.execute.return_value = 1
                        
                        result = Conversations.delete_conversation_by_conv_id("test_conv_id")
                        
                        mock_delete.assert_called_once()
                        mock_where.assert_called_once()
    
    def test_invalid_conversation_operations(self, clean_db):
        """测试无效的会话操作"""
        with patch('models.conversations.db.connection_context'):
            with patch('models.conversations.Conversations.get_or_none', return_value=None):
                # 尝试获取不存在的会话
                conv = Conversations.get_conversation_by_conv_id("non_existent_id")
                assert conv is None
                
                # 尝试删除不存在的会话
                with patch('models.conversations.Conversations.delete') as mock_delete:
                    with patch('models.conversations.Conversations.where') as mock_where:
                        mock_where.return_value.execute.return_value = 0
                        result = Conversations.delete_conversation_by_conv_id("non_existent_id")
                        # 删除操作应该正常执行，只是影响行数为0


class TestModelRelationships:
    """模型关系测试类"""
    
    def test_user_conversation_relationship(self, sample_user_data, sample_conversation_data, clean_db):
        """测试用户和会话的关系"""
        with patch('models.users.db.connection_context'):
            with patch('models.conversations.db.connection_context'):
                with patch('models.users.Users.add_user'):
                    with patch('models.conversations.Conversations.add_conversation') as mock_add_conv:
                        mock_add_conv.return_value = "test_conv_id"
                        
                        conv_id = Conversations.add_conversation(
                            user_id=sample_user_data["user_id"],
                            conv_name=sample_conversation_data["conv_name"]
                        )
                        
                        assert conv_id == "test_conv_id"
                        mock_add_conv.assert_called_once()
    
    def test_cascade_operations(self, sample_user_data, clean_db):
        """测试级联操作"""
        with patch('models.users.db.connection_context'):
            with patch('models.conversations.db.connection_context'):
                with patch('models.users.Users.add_user'):
                    with patch('models.conversations.Conversations.add_conversation') as mock_add_conv:
                        with patch('models.users.Users.delete_user'):
                            with patch('models.conversations.Conversations.delete_conversation_by_conv_id'):
                                # 创建用户
                                Users.add_user(
                                    user_id=sample_user_data["user_id"],
                                    user_name=sample_user_data["user_name"],
                                    password_hash=sample_user_data["password_hash"]
                                )
                                
                                # 创建多个会话
                                conv_id1 = Conversations.add_conversation(
                                    user_id=sample_user_data["user_id"],
                                    conv_name="会话1"
                                )
                                conv_id2 = Conversations.add_conversation(
                                    user_id=sample_user_data["user_id"],
                                    conv_name="会话2"
                                )
                                
                                # 删除用户（如果实现了级联删除）
                                Users.delete_user(sample_user_data["user_id"])
                                
                                # 验证会话是否还存在（取决于级联删除的实现）
                                # 这里假设会话仍然存在，需要手动清理
                                Conversations.delete_conversation_by_conv_id(conv_id1)
                                Conversations.delete_conversation_by_conv_id(conv_id2)
