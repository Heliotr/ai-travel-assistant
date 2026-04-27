"""
携程旅行助手 - 应用入口文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pathlib import Path

from api.routers import init_routers
from config import settings
from config.log_config import init_log
from utils.cors import init_cors
from utils.middlewares import init_middleware


def validate_env():
    """验证必需的环境变量"""
    required_vars = ['DEEPSEEK_API_KEY', 'ZHIPU_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"[WARN] Missing env vars: {missing}")
    print("[OK] Environment validated")


# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

def custom_openapi(app: FastAPI):
    """自定义 OpenAPI 文档"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI旅行助手 API",
        version="1.0.0",
        description="""
## 智能旅行客服系统

基于 LangGraph 多助理协作架构，提供以下服务：

- ✈️ **航班服务**: 查询、改签、取消航班
- 🏨 **酒店服务**: 搜索、预订、修改、取消酒店
- 🚗 **租车服务**: 搜索、预订、修改、取消租车
- 🎯 **旅行推荐**: 智能推荐旅行产品

### 认证方式
所有接口（除登录/注册外）需要 JWT Token 认证：
```
Authorization: Bearer <token>
```
        """,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    # 初始化日志配置
    init_log()

    # 创建 FastAPI 应用
    app = FastAPI(
        title="AI旅行助手",
        description="智能旅行客服系统",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # 自定义 OpenAPI 文档
    app.openapi = lambda: custom_openapi(app)

    # 初始化 CORS 跨域配置
    init_cors(app)

    # 初始化中间件 (JWT 认证)
    init_middleware(app)

    # 注册路由
    init_routers(app)

    # 添加健康检查接口
    @app.get("/health", tags=["健康检查"])
    async def health_check():
        """健康检查接口"""
        return {"status": "healthy", "service": "ctrip_assistant"}

    @app.get("/ready", tags=["健康检查"])
    async def readiness_check():
        """就绪检查接口"""
        return {"status": "ready", "service": "ctrip_assistant"}

    return app


# 创建应用实例
app = create_app()

# 更新白名单配置，添加深度 Agent API
settings._wrapped.WHITE_LIST = [
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
print(f"[main] WHITE_LIST updated: {settings.WHITE_LIST}")


if __name__ == "__main__":
    validate_env()
    init_log()

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level=settings.LOG_LEVEL.lower(),
    )