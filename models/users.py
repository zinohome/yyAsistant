from peewee import CharField
from typing import Union, Dict, List
from playhouse.sqlite_ext import JSONField
from werkzeug.security import check_password_hash

from . import db, BaseModel
from configs import AuthConfig
from .exceptions import InvalidUserError, ExistingUserError


class Users(BaseModel):
    """用户信息表模型类"""

    # 用户id，主键
    user_id = CharField(primary_key=True)

    # 用户名，唯一
    user_name = CharField(unique=True)

    # 用户密码散列值
    password_hash = CharField()

    # 用户角色，全部可选项见configs.AuthConfig.roles
    user_role = CharField(default=AuthConfig.normal_role)

    # 用户最近一次登录会话token
    session_token = CharField(null=True)

    # 用户头像图标
    user_icon = CharField(null=True)

    # 用户其他辅助信息，任意JSON格式，允许空值
    other_info = JSONField(null=True)

    @classmethod
    def get_user(cls, user_id: str):
        """根据用户id查询用户信息"""

        with db.connection_context():
            return cls.get_or_none(cls.user_id == user_id)

    @classmethod
    def get_user_by_name(cls, user_name: str):
        """根据用户名查询用户信息"""

        with db.connection_context():
            return cls.get_or_none(cls.user_name == user_name)

    @classmethod
    def get_all_users(cls):
        """获取所有用户信息"""

        with db.connection_context():
            return list(cls.select().dicts())

    @classmethod
    def check_user_password(cls, user_id: str, password: str):
        """校验用户密码"""

        return check_password_hash(cls.get_user(user_id).password_hash, password)

    @classmethod
    def add_user(
        cls,
        user_id: str,
        user_name: str,
        password_hash: str,
        user_role: str = "normal",
        other_info: Union[Dict, List] = None,
        user_icon: str = "👨‍💼",
    ):
        """添加用户"""

        with db.connection_context():
            # 若必要用户信息不完整
            if not (user_id and user_name and password_hash):
                raise InvalidUserError("用户信息不完整")

            # 若用户id已存在
            elif cls.get_or_none(cls.user_id == user_id):
                raise ExistingUserError("用户id已存在")

            # 若用户名存在重复
            elif cls.get_or_none(cls.user_name == user_name):
                raise ExistingUserError("用户名已存在")

            # 执行用户添加操作
            with db.atomic():
                cls.create(
                    user_id=user_id,
                    user_name=user_name,
                    password_hash=password_hash,
                    user_role=user_role,
                    other_info=other_info,
                    user_icon=user_icon,
                )

    @classmethod
    def delete_user(cls, user_id: str):
        """删除用户"""

        with db.connection_context():
            with db.atomic():
                cls.delete().where(cls.user_id == user_id).execute()

    @classmethod
    def truncate_users(cls, execute: bool = False):
        """清空用户，请小心使用"""

        # 若保险参数execute=True
        if execute:
            with db.connection_context():
                with db.atomic():
                    cls.delete().execute()

    @classmethod
    def update_user(cls, user_id: str, **kwargs):
        """更新用户信息"""

        with db.connection_context():
            with db.atomic():
                cls.update(**kwargs).where(cls.user_id == user_id).execute()

            # 返回成功更新后的用户信息
            return cls.get_or_none(cls.user_id == user_id)
