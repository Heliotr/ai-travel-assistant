"""
错误处理模块
配置全局HTTP异常处理器
"""

from fastapi import FastAPI
from starlette.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器，返回JSON格式的错误信息"""
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})


def init_handler_errors(app: FastAPI):
    """注册全局异常处理器到FastAPI应用"""
    app.add_exception_handler(HTTPException, handler=http_exception_handler)