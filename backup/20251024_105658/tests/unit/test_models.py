"""
数据模型单元测试
"""
import pytest
from datetime import datetime
from models.users import Users
from models.conversations import Conversations
from models.exceptions import InvalidUserError, ExistingUserError, InvalidConversationError


class TestUsersModel:
    """用户模型测试类"""
    
    def test_create_user_success(self, sample_user_data, clean_db):
        """测试成功创建用户"""
        user = Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"],
            user_role=sample_user_data["user_role"]
        )
        
        assert user is not None
        assert user.user_id == sample_user_data["user_id"]
        assert user.user_name == sample_user_data["user_name"]
        assert user.user_role == sample_user_data["user_role"]
        assert user.password_hash is not None
        assert user.password_hash != sample_user_data["password"]  # 密码应该被加密
    
    def test_create_user_duplicate_id(self, sample_user_data, clean_db):
        """测试创建重复用户ID"""
        # 先创建一个用户
        Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"]
        )
        
        # 尝试创建相同ID的用户
        with pytest.raises(ExistingUserError):
            Users.add_user(
                user_id=sample_user_data["user_id"],
                user_name="another_user",
                password="another_password"
            )
    
    def test_create_user_duplicate_name(self, sample_user_data, clean_db):
        """测试创建重复用户名"""
        # 先创建一个用户
        Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"]
        )
        
        # 尝试创建相同用户名的用户
        with pytest.raises(ExistingUserError):
            Users.add_user(
                user_id="another_id",
                user_name=sample_user_data["user_name"],
                password="another_password"
            )
    
    def test_create_user_invalid_data(self, clean_db):
        """测试使用无效数据创建用户"""
        with pytest.raises(InvalidUserError):
            Users.add_user(
                user_id="",  # 空用户ID
                user_name="test",
                password="password"
            )
        
        with pytest.raises(InvalidUserError):
            Users.add_user(
                user_id="test",
                user_name="",  # 空用户名
                password="password"
            )
        
        with pytest.raises(InvalidUserError):
            Users.add_user(
                user_id="test",
                user_name="test",
                password=""  # 空密码
            )
    
    def test_get_user_by_id(self, sample_user_data, clean_db):
        """测试通过ID获取用户"""
        # 创建用户
        Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"]
        )
        
        # 获取用户
        user = Users.get_user(sample_user_data["user_id"])
        assert user is not None
        assert user.user_id == sample_user_data["user_id"]
        assert user.user_name == sample_user_data["user_name"]
    
    def test_get_user_by_name(self, sample_user_data, clean_db):
        """测试通过用户名获取用户"""
        # 创建用户
        Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"]
        )
        
        # 获取用户
        user = Users.get_user_by_name(sample_user_data["user_name"])
        assert user is not None
        assert user.user_id == sample_user_data["user_id"]
        assert user.user_name == sample_user_data["user_name"]
    
    def test_check_user_password(self, sample_user_data, clean_db):
        """测试用户密码验证"""
        # 创建用户
        Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"]
        )
        
        # 验证正确密码
        assert Users.check_user_password(
            sample_user_data["user_name"], 
            sample_user_data["password"]
        ) is True
        
        # 验证错误密码
        assert Users.check_user_password(
            sample_user_data["user_name"], 
            "wrong_password"
        ) is False
    
    def test_update_user(self, sample_user_data, clean_db):
        """测试更新用户信息"""
        # 创建用户
        Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"]
        )
        
        # 更新用户信息
        updated_user = Users.update_user(
            user_id=sample_user_data["user_id"],
            user_role="admin",
            user_icon="new_icon.png"
        )
        
        assert updated_user.user_role == "admin"
        assert updated_user.user_icon == "new_icon.png"
    
    def test_delete_user(self, sample_user_data, clean_db):
        """测试删除用户"""
        # 创建用户
        Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"]
        )
        
        # 删除用户
        result = Users.delete_user(sample_user_data["user_id"])
        assert result is True
        
        # 验证用户已被删除
        user = Users.get_user(sample_user_data["user_id"])
        assert user is None


class TestConversationsModel:
    """会话模型测试类"""
    
    def test_create_conversation_success(self, sample_conversation_data, clean_db):
        """测试成功创建会话"""
        conv_id = Conversations.add_conversation(
            user_id=sample_conversation_data["user_id"],
            conv_name=sample_conversation_data["conv_name"],
            conv_memory=sample_conversation_data["conv_memory"]
        )
        
        assert conv_id is not None
        assert conv_id.startswith("conv-")
        assert sample_conversation_data["user_id"] in conv_id
    
    def test_create_conversation_default_name(self, sample_conversation_data, clean_db):
        """测试使用默认名称创建会话"""
        conv_id = Conversations.add_conversation(
            user_id=sample_conversation_data["user_id"]
        )
        
        # 获取创建的会话
        conv = Conversations.get_conversation_by_conv_id(conv_id)
        assert conv is not None
        assert conv.conv_name.startswith("新会话-")
    
    def test_get_conversation_by_conv_id(self, sample_conversation_data, clean_db):
        """测试通过会话ID获取会话"""
        # 创建会话
        conv_id = Conversations.add_conversation(
            user_id=sample_conversation_data["user_id"],
            conv_name=sample_conversation_data["conv_name"],
            conv_memory=sample_conversation_data["conv_memory"]
        )
        
        # 获取会话
        conv = Conversations.get_conversation_by_conv_id(conv_id)
        assert conv is not None
        assert conv.conv_id == conv_id
        assert conv.user_id == sample_conversation_data["user_id"]
        assert conv.conv_name == sample_conversation_data["conv_name"]
    
    def test_get_user_conversations(self, sample_conversation_data, clean_db):
        """测试获取用户的所有会话"""
        user_id = sample_conversation_data["user_id"]
        
        # 创建多个会话
        conv_id1 = Conversations.add_conversation(
            user_id=user_id,
            conv_name="会话1"
        )
        conv_id2 = Conversations.add_conversation(
            user_id=user_id,
            conv_name="会话2"
        )
        
        # 获取用户会话列表
        conversations = Conversations.get_user_conversations(user_id)
        assert len(conversations) == 2
        
        # 验证会话ID
        conv_ids = [conv["conv_id"] for conv in conversations]
        assert conv_id1 in conv_ids
        assert conv_id2 in conv_ids
    
    def test_update_conversation(self, sample_conversation_data, clean_db):
        """测试更新会话信息"""
        # 创建会话
        conv_id = Conversations.add_conversation(
            user_id=sample_conversation_data["user_id"],
            conv_name=sample_conversation_data["conv_name"]
        )
        
        # 更新会话
        new_memory = {"messages": [{"role": "user", "content": "更新后的消息"}]}
        updated_conv = Conversations.update_conversation_by_conv_id(
            conv_id=conv_id,
            conv_name="更新后的会话名称",
            conv_memory=new_memory
        )
        
        assert updated_conv.conv_name == "更新后的会话名称"
        assert updated_conv.conv_memory == new_memory
    
    def test_delete_conversation(self, sample_conversation_data, clean_db):
        """测试删除会话"""
        # 创建会话
        conv_id = Conversations.add_conversation(
            user_id=sample_conversation_data["user_id"],
            conv_name=sample_conversation_data["conv_name"]
        )
        
        # 删除会话
        result = Conversations.delete_conversation_by_conv_id(conv_id)
        assert result is True
        
        # 验证会话已被删除
        conv = Conversations.get_conversation_by_conv_id(conv_id)
        assert conv is None
    
    def test_conversation_memory_operations(self, sample_conversation_data, clean_db):
        """测试会话记忆操作"""
        # 创建会话
        conv_id = Conversations.add_conversation(
            user_id=sample_conversation_data["user_id"],
            conv_name=sample_conversation_data["conv_name"]
        )
        
        # 添加消息到记忆
        messages = [
            {"role": "user", "content": "第一条消息"},
            {"role": "assistant", "content": "第一条回复"},
            {"role": "user", "content": "第二条消息"}
        ]
        
        updated_conv = Conversations.update_conversation_by_conv_id(
            conv_id=conv_id,
            conv_memory={"messages": messages}
        )
        
        assert updated_conv.conv_memory["messages"] == messages
        assert len(updated_conv.conv_memory["messages"]) == 3
    
    def test_conversation_timestamp(self, sample_conversation_data, clean_db):
        """测试会话时间戳"""
        before_creation = datetime.now()
        
        # 创建会话
        conv_id = Conversations.add_conversation(
            user_id=sample_conversation_data["user_id"],
            conv_name=sample_conversation_data["conv_name"]
        )
        
        after_creation = datetime.now()
        
        # 获取会话
        conv = Conversations.get_conversation_by_conv_id(conv_id)
        
        # 验证时间戳
        assert conv.conv_time >= before_creation
        assert conv.conv_time <= after_creation
    
    def test_invalid_conversation_operations(self, clean_db):
        """测试无效的会话操作"""
        # 尝试获取不存在的会话
        conv = Conversations.get_conversation_by_conv_id("non_existent_id")
        assert conv is None
        
        # 尝试删除不存在的会话
        result = Conversations.delete_conversation_by_conv_id("non_existent_id")
        assert result is False
        
        # 尝试更新不存在的会话
        with pytest.raises(Exception):  # 根据实际实现调整异常类型
            Conversations.update_conversation_by_conv_id(
                conv_id="non_existent_id",
                conv_name="新名称"
            )


class TestModelRelationships:
    """模型关系测试类"""
    
    def test_user_conversation_relationship(self, sample_user_data, sample_conversation_data, clean_db):
        """测试用户和会话的关系"""
        # 创建用户
        Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"]
        )
        
        # 创建会话
        conv_id = Conversations.add_conversation(
            user_id=sample_user_data["user_id"],
            conv_name=sample_conversation_data["conv_name"]
        )
        
        # 验证关系
        conv = Conversations.get_conversation_by_conv_id(conv_id)
        assert conv.user_id == sample_user_data["user_id"]
        
        # 获取用户的所有会话
        user_conversations = Conversations.get_user_conversations(sample_user_data["user_id"])
        assert len(user_conversations) == 1
        assert user_conversations[0]["conv_id"] == conv_id
    
    def test_cascade_operations(self, sample_user_data, clean_db):
        """测试级联操作"""
        # 创建用户
        Users.add_user(
            user_id=sample_user_data["user_id"],
            user_name=sample_user_data["user_name"],
            password=sample_user_data["password"]
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
        # 注意：根据实际实现，可能需要手动删除相关会话
        Users.delete_user(sample_user_data["user_id"])
        
        # 验证会话是否还存在（取决于级联删除的实现）
        # 这里假设会话仍然存在，需要手动清理
        Conversations.delete_conversation_by_conv_id(conv_id1)
        Conversations.delete_conversation_by_conv_id(conv_id2)
