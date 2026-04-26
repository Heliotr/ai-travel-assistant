"""
文档OAuth2认证模块
重写FastAPI的OAuth2PasswordBearer，支持白名单跳过认证
"""

import re
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request

from config import settings


class MyOAuth2PasswordBearer(OAuth2PasswordBearer):
    """
    自定义OAuth2认证类
    支持白名单机制，白名单中的路径不需要Token认证
    用于Swagger文档中的认证
    """

    def __init__(self, tokenUrl: str, schema: str):
        """
        初始化

        参数:
            tokenUrl: 认证表单提交的路由
            schema: Token方案名称（本项目使用JWT）
        """
        super().__init__(
            tokenUrl=tokenUrl,
            scheme_name=schema,
            scopes=None,
            description=None,
            auto_error=True
        )

    async def __call__(self, request: Request) -> Optional[str]:
        """
        解析请求头中的Token

        参数:
            request: FastAPI请求对象

        返回:
            Token字符串，白名单路径返回空字符串
        """
        path: str = request.url.path
        # 根据白名单过滤
        for request_path in settings.WHITE_LIST:
            if re.match(request_path, path):
                return ''
        # 非白名单路径，正常验证Token
        return super().__call__(request)