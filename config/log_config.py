"""
日志配置模块
配置项目使用的日志系统，使用Python标准logging库
"""

from logging.config import dictConfig
from config import settings


def init_log():
    """
    初始化日志配置
    - 控制台输出：详细格式，包含时间、级别、模块、方法、行号
    - 日志级别从配置文件读取
    """
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            # 简单格式
            'sample': {'format': '%(asctime)s %(levelname)s %(message)s'},
            # 详细格式
            'verbose': {'format': '%(asctime)s %(levelname)s %(name)s %(process)d %(thread)d %(message)s'},
            # 访问日志格式（UVicorn）
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            },
        },
        'handlers': {
            "console": {
                "formatter": 'verbose',
                'level': 'DEBUG',
                "class": "logging.StreamHandler",
            },
        },
        'loggers': {
            '': {'level': settings.LOG_LEVEL, 'handlers': ['console']},
        },
    }

    dictConfig(log_config)