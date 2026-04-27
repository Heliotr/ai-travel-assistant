"""
配置管理模块
使用Dynaconf库管理多环境配置，支持从YAML文件和環境变量加载配置
"""

from pathlib import Path
from dynaconf import Dynaconf

# 获取项目根目录
_BASE_DIR = Path(__file__).parent.parent

# 创建配置对象（从 .env 加载）
settings = Dynaconf(
    envvar_prefix="EMP_CONF",      # 环境变量前缀，设置后可用EMP_CONF_xxx读取
    settings_files=[],              # 不使用YAML文件，从.env加载
    env_switcher="EMP_ENV",        # 环境切换变量，EMP_ENV=production切换到生产环境
    lowercase_read=False,          # 禁用小写访问，settings.NAME而非settings.name
    base_dir=_BASE_DIR,            # 项目根目录
    defaults=True,                  # 启用默认值
)

# 设置默认值（如果 .env 中没有定义）
if not hasattr(settings, 'ORIGINS'):
    settings._wrapped.ORIGINS = ['*']
if not hasattr(settings, 'HOST'):
    settings._wrapped.HOST = '0.0.0.0'
if not hasattr(settings, 'PORT'):
    settings._wrapped.PORT = 8000
if not hasattr(settings, 'LOG_LEVEL'):
    settings._wrapped.LOG_LEVEL = 'INFO'
if not hasattr(settings, 'JWT_SECRET_KEY'):
    settings._wrapped.JWT_SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
if not hasattr(settings, 'JWT_ALGORITHM'):
    settings._wrapped.JWT_ALGORITHM = 'HS256'
if not hasattr(settings, 'JWT_EXPIRE_MINUTES'):
    settings._wrapped.JWT_EXPIRE_MINUTES = 30
if not hasattr(settings, 'WHITE_LIST'):
    settings._wrapped.WHITE_LIST = ['/']