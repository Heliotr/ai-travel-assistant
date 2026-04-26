"""
数据库路径配置模块
定义项目使用的SQLite数据库文件路径
"""

from pathlib import Path

# 获取项目根目录
basic_dir = Path(__file__).resolve().parent.parent

# 主数据库文件（当前使用的数据库）
db = f"{basic_dir}/travel_new.sqlite"

# 备份数据库文件（用于重置测试数据）
backup_file = f"{basic_dir}/travel2.sqlite"