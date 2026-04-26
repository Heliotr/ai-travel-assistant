"""
CORS跨域配置模块
配置FastAPI应用的跨域资源共享策略
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings


def init_cors(app: FastAPI) -> None:
    """
    初始化CORS跨域中间件
    允许前端应用跨域访问API
    """
    app.add_middleware(CORSMiddleware,
                       allow_origins=settings.ORIGINS,      # 允许的来源域名
                       allow_credentials=True,              # 允许携带凭证（Cookie等）
                       allow_methods=["*"],                 # 允许所有HTTP方法
                       allow_headers=["*"],                 # 允许所有请求头
                       )