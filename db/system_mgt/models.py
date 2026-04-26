"""
用户数据库模型
定义用户表的结构和字段
"""

from typing import Optional

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from db import DBModelBase


class UserModel(DBModelBase):
    """
    用户模型类
    对应数据库中的 t_usermodel 表
    """

    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment='用户名')
    password: Mapped[str] = mapped_column(String(200), nullable=False, comment='加密后的密码')
    phone: Mapped[str] = mapped_column(String(20), nullable=True, comment='用户手机号')
    email: Mapped[str] = mapped_column(String(50), nullable=True, comment='用户邮箱')
    real_name: Mapped[str] = mapped_column(String(50), nullable=True, comment='用户真实姓名')
    icon: Mapped[str] = mapped_column(String(100), default='/static/user_icon/default.jpg', nullable=True,
                                      comment='用户头像路径')
    dept_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='所属部门ID')