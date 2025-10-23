# -*- coding: utf-8 -*-
from typing import Literal
from .app_config import app_config


class DatabaseConfig:
    """数据库配置参数 - 使用统一配置"""

    # 应用基础数据库类型
    # 当使用postgresql类型时，请使用`pip install psycopg2-binary`安装必要依赖
    # 当使用mysql类型时，请使用`pip install pymysql`安装必要依赖
    database_type: Literal["sqlite", "postgresql", "mysql"] = app_config.DATABASE_TYPE

    # 当database_type为'postgresql'时，对应的数据库连接配置参数，使用时请根据实际情况修改
    postgresql_config = app_config.get_postgresql_config()

    # 当database_type为'mysql'时，对应的数据库连接配置参数，使用时请根据实际情况修改
    mysql_config = app_config.get_mysql_config()
