"""
密码工具模块
使用bcrypt算法进行密码加密和验证
"""

import bcrypt


def get_hashed_password(password: str) -> str:
    """
    密码加密函数

    参数:
        password: 原始明文密码

    返回:
        bcrypt加密后的密码字符串
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_pass: str) -> bool:
    """
    密码验证函数

    参数:
        password: 用户输入的明文密码
        hashed_pass: 数据库中存储的加密密码

    返回:
        密码是否匹配
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_pass.encode('utf-8'))