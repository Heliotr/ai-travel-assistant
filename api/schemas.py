"""
API数据模型基类
定义通用的数据库混入模型，用于将ORM模型转换为Pydantic模型
"""

from typing import TypeVar

from pydantic import BaseModel

from db import DBModelBase

# 定义三种泛型类型，用于数据库操作的通用化处理
ModelType = TypeVar('ModelType', bound=DBModelBase)  # 数据库模型类型
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)  # 创建数据用的Schema
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)  # 更新数据用的Schema


class InDBMixin(BaseModel):
    """
    数据库混入类 - 所有响应模型的基类
    启用ORM模式，将数据库模型对象自动转换为Pydantic模型对象
    """

    class Config:
        # 启用ORM模式，使Pydantic可以读取ORM对象属性
        from_attributes = True
