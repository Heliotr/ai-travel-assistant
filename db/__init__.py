"""
数据库初始化模块
创建数据库连接引擎和Session工厂，支持MySQL和SQLite
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from sqlalchemy import URL, create_engine, DateTime, func
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase, declared_attr, Mapped, mapped_column

from config import settings

# 从环境变量获取 DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')

# 获取数据库驱动，默认使用pymysql
db_driver = settings.DATABASE.DRIVER if hasattr(settings, 'DATABASE') else 'sqlite'
if db_driver == 'mysql':
    db_driver = 'mysql+pymysql'  # 使用pymysql作为MySQL驱动

# 优先使用环境变量中的DATABASE_URL
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, echo=True, future=True, pool_size=10)
else:
    # 回退到配置文件
    url = URL(
        drivername=db_driver,
        username=settings.DATABASE.get('USERNAME', None) if hasattr(settings, 'DATABASE') else None,
        password=settings.DATABASE.get('PASSWORD', None) if hasattr(settings, 'DATABASE') else None,
        host=settings.DATABASE.get('HOST', None) if hasattr(settings, 'DATABASE') else None,
        port=settings.DATABASE.get('PORT', None) if hasattr(settings, 'DATABASE') else None,
        database=settings.DATABASE.get('NAME', None) if hasattr(settings, 'DATABASE') else None,
        query=settings.DATABASE.get('QUERY', None) if hasattr(settings, 'DATABASE') else None,
    )
    engine = create_engine(url, echo=True, future=True, pool_size=10)

# 创建Session工厂
sm = sessionmaker(bind=engine, autoflush=True, autocommit=False)


class DBModelBase(DeclarativeBase):
    """
    数据库模型基类
    所有数据库模型类都需要继承此类，以获得通用字段和功能
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """自动生成表名：t_模型类名（小写）"""
        return 't_' + cls.__name__.lower()

    __table_args__ = {"mysql_engine": "InnoDB"}
    # 插入或更新后立即获取服务器生成的默认值
    __mapper_args__ = {"eager_defaults": True}

    # 所有模型类都有的公共字段
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), comment='记录创建时间')
    update_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now(),
                                                  comment='记录最后修改时间')