"""
JWT Token验证中间件模块
验证请求头中的JWT Token，实现接口访问控制
"""

import logging
import re
import traceback
from datetime import datetime
from typing import Callable

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.responses import JSONResponse
from jose import jwt, ExpiredSignatureError
from starlette import status

from config import settings

log = logging.getLogger('emp')

# 硬编码白名单，避免配置缓存问题
WHITE_LIST = [
    '/',
    '^/static/.*',
    '^/assets.*',
    '/api/login',
    '/api/register',
    '/api/auth',
    '/api/workflow/mode',
    '/health',
    '/ready',
    '/docs',
    '/redoc',
    '/openapi.json',
    '^/docs/.*',
    '^/api/new_graph.*',
    '^/api/graph.*',
    '^/api/deep_agent.*',
    '^/api/unified.*',
]


async def verify_token(request: Request, call_next: Callable) -> Response:
    """
    Token验证中间件
    - 检查请求路径是否在白名单中，白名单路径直接放行
    - 非白名单路径验证Authorization请求头中的JWT Token
    - 验证Token有效性、是否过期
    """
    # 认证失败时返回的错误响应
    auth_error = JSONResponse(
        {'detail': '非法的Token，请重新登录！'},
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"}
    )

    # 获取请求路径
    path: str = request.url.path

    # 检查是否在白名单中
    for request_path in WHITE_LIST:
        if request_path.startswith('^') or request_path.endswith('$') or '.*' in request_path or '|' in request_path:
            # 正则匹配
            if re.match(request_path, path):
                return await call_next(request)
        else:
            # 精确匹配或前缀匹配
            if path == request_path or path.startswith(request_path + '/'):
                log.debug(f"Path {path} matched whitelist prefix: {request_path}")
                return await call_next(request)
    else:
        # 非白名单路径，需要验证Token
        log.debug(f"Path {path} NOT in whitelist, requires token")
        authorization: str = request.headers.get('Authorization')
        if not authorization:
            return auth_error

        token: str = authorization.split(' ')[1]
        try:
            # 校验Token
            res_dict = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = res_dict.get('sub').split(':')[1]

            # 检查是否超时
            if not username:
                return auth_error
            if datetime.fromtimestamp(res_dict.get('exp')) < datetime.now():
                return auth_error

            # 将用户名绑定到request对象，供后续使用
            request.state.username = username
            return await call_next(request)
        except ExpiredSignatureError as e:
            log.error('\n' + traceback.format_exc())
            return auth_error
        except Exception as e:
            log.error(e)
            log.error('\n' + traceback.format_exc())
            return JSONResponse({'detail': '服务器接口异常，请检查接口'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def init_middleware(app: FastAPI) -> None:
    """注册Token验证中间件到FastAPI应用"""
    app.middleware('http')(verify_token)