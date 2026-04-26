"""
API路由配置
只保留深度 Agent 接口
"""

from fastapi import APIRouter, FastAPI

from api.system_mgt import user_views
from api.graph_api import deep_agent_views


def router_v1():
    """创建并配置主路由"""
    root_router = APIRouter()

    # 用户管理
    root_router.include_router(user_views.router, tags=['用户管理'])

    # 深度 Agent 调用（唯一工作流）
    root_router.include_router(deep_agent_views.router, tags=['深度Agent'])

    # 健康检查
    @root_router.get('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'ctrip-assistant'}

    return root_router


def init_routers(app: FastAPI):
    """将主路由注册到FastAPI应用"""
    app.include_router(router_v1(), prefix='/api')