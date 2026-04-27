"""
API路由配置
"""

from fastapi import APIRouter, FastAPI

from api.system_mgt import user_views
from api.graph_api import new_graph_views


def router_v1():
    """创建并配置主路由"""
    root_router = APIRouter()

    # 用户管理
    root_router.include_router(user_views.router, tags=['用户管理'])

    # 工作流接口
    root_router.include_router(new_graph_views.router, tags=['工作流'])

    # 健康检查
    @root_router.get('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'ctrip-assistant'}

    return root_router


def init_routers(app: FastAPI):
    """将主路由注册到FastAPI应用"""
    app.include_router(router_v1(), prefix='/api')