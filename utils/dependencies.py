"""
依赖注入模块
提供数据库Session的依赖注入函数
"""

from fastapi import Request
from sqlalchemy.orm import Session

from db import sm


def get_db(request: Request) -> Session:
    """
    数据库Session依赖注入函数
    每次请求都会创建一个新的Session，请求结束后自动关闭
    """
    try:
        session = sm()
        yield session
    finally:
        session.close()