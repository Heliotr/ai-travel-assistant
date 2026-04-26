"""
配置管理模块
使用Dynaconf库管理多环境配置，支持从YAML文件和環境变量加载配置
"""

from pathlib import Path
from dynaconf import Dynaconf

# 获取项目根目录
_BASE_DIR = Path(__file__).parent.parent

# 配置文件列表
settings_files = [
    Path(__file__).parent / 'development.yml',  # 开发环境配置
    # Path(__file__).parent / 'production.yml'  # 生产环境配置（需要时启用）
]

# 创建配置对象
settings = Dynaconf(
    envvar_prefix="EMP_CONF",      # 环境变量前缀，设置后可用EMP_CONF_xxx读取
    settings_files=settings_files, # 配置文件路径
    env_switcher="EMP_ENV",        # 环境切换变量，EMP_ENV=production切换到生产环境
    lowercase_read=False,          # 禁用小写访问，settings.NAME而非settings.name
    base_dir=_BASE_DIR,            # 项目根目录
)