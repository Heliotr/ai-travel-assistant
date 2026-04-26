"""
JWT Token工具模块
提供JWT令牌的生成和验证功能
"""

from datetime import datetime, timedelta
from typing import Union, Any

from jose import jwt

from config import settings

# Token有效期（分钟），从配置文件读取
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
# JWT加密算法
ALGORITHM = settings.ALGORITHM
# JWT密钥
JWT_SECRET_KEY = settings.JWT_SECRET_KEY


def create_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
    创建JWT Token

    参数:
        subject: 主题（通常为用户ID:用户名格式的字符串）
        expires_delta: 自定义过期时间（秒）

    返回:
        编码后的JWT Token字符串
    """
    if expires_delta:
        # 自定义过期时间
        expires_delta = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        # 默认过期时间
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 生成Token，包含过期时间和主题
    return jwt.encode({'exp': expires_delta, 'sub': str(subject)}, JWT_SECRET_KEY, ALGORITHM)


if __name__ == '__main__':
    # 测试生成Token
    print(create_token('test_user'))