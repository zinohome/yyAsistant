from peewee import AutoField, CharField, DateTimeField
from playhouse.sqlite_ext import JSONField
from datetime import datetime
import time
from typing import Union, Dict, List

from . import db, BaseModel
from .exceptions import InvalidConversationError, ExistingConversationError


class Conversations(BaseModel):
    """用户会话信息表模型类"""

    # 主键自增字段
    conversation_id = AutoField(primary_key=True)

    # 关联用户id
    user_id = CharField(null=False)

    # 创建时生成的会话id，格式为conv-{user_id}-{当前时间毫秒}
    conv_id = CharField(unique=True, null=False)

    # 会话名称，默认为"新会话-{年月日时分秒}"
    conv_name = CharField(null=False)

    # 会话创建时间，格式为YYYY-MM-DD HH:mm:ss
    conv_time = DateTimeField(formats='%Y-%m-%d %H:%M:%S', null=False)

    # 会话记忆，JSON格式，可为空
    conv_memory = JSONField(null=True)

    @classmethod
    def get_conversation(cls, conversation_id: int):
        """根据conversation_id查询会话信息"""
        
        with db.connection_context():
            return cls.get_or_none(cls.conversation_id == conversation_id)

    @classmethod
    def get_conversation_by_conv_id(cls, conv_id: str):
        """根据conv_id查询会话信息"""
        
        with db.connection_context():
            return cls.get_or_none(cls.conv_id == conv_id)

    @classmethod
    def get_user_conversations(cls, user_id: str):
        """获取指定用户的所有会话"""
        
        with db.connection_context():
            return list(cls.select().where(cls.user_id == user_id).order_by(cls.conv_time.desc()).dicts())

    @classmethod
    def get_all_conversations(cls):
        """获取所有会话信息"""
        
        with db.connection_context():
            return list(cls.select().dicts())

    @classmethod
    def add_conversation(
        cls,
        user_id: str,
        conv_name: str = None,
        conv_memory: Union[Dict, List] = None
    ):
        """添加会话"""
        
        with db.connection_context():
            # 若必要用户信息不完整
            if not user_id:
                raise InvalidConversationError("用户ID不能为空")

            # 生成conv_id和默认conv_name
            current_time_ms = int(time.time() * 1000)
            current_time_str = datetime.now().strftime('%Y%m%d%H%M%S')
            conv_id = f"conv-{user_id}-{current_time_ms}"
            
            if not conv_name:
                conv_name = f"新会话-{current_time_str}"
            
            # 获取当前时间，格式化为YYYY-MM-DD HH:mm:ss
            conv_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 若conv_id已存在
            if cls.get_or_none(cls.conv_id == conv_id):
                raise ExistingConversationError("会话ID已存在")

            # 执行会话添加操作
            with db.atomic():
                cls.create(
                    user_id=user_id,
                    conv_id=conv_id,
                    conv_name=conv_name,
                    conv_time=conv_time,
                    conv_memory=conv_memory
                )
                return conv_id

    @classmethod
    def delete_conversation(cls, conversation_id: int):
        """删除会话"""
        
        with db.connection_context():
            with db.atomic():
                cls.delete().where(cls.conversation_id == conversation_id).execute()

    @classmethod
    def delete_conversation_by_conv_id(cls, conv_id: str):
        """根据conv_id删除会话"""
        
        with db.connection_context():
            with db.atomic():
                cls.delete().where(cls.conv_id == conv_id).execute()

    @classmethod
    def delete_user_conversations(cls, user_id: str):
        """删除指定用户的所有会话"""
        
        with db.connection_context():
            with db.atomic():
                cls.delete().where(cls.user_id == user_id).execute()

    @classmethod
    def truncate_conversations(cls, execute: bool = False):
        """清空会话表，请小心使用"""
        
        # 若保险参数execute=True
        if execute:
            with db.connection_context():
                with db.atomic():
                    cls.delete().execute()

    @classmethod
    def update_conversation(cls, conversation_id: int, **kwargs):
        """更新会话信息"""
        
        with db.connection_context():
            with db.atomic():
                cls.update(**kwargs).where(cls.conversation_id == conversation_id).execute()

            # 返回成功更新后的会话信息
            return cls.get_or_none(cls.conversation_id == conversation_id)

    @classmethod
    def update_conversation_by_conv_id(cls, conv_id: str, **kwargs):
        """根据conv_id更新会话信息"""
        
        with db.connection_context():
            with db.atomic():
                cls.update(**kwargs).where(cls.conv_id == conv_id).execute()

            # 返回成功更新后的会话信息
            return cls.get_or_none(cls.conv_id == conv_id)