"""
工作流API相关的数据模型Schema
用于定义工作流调用的请求参数和响应格式
"""

import uuid
from datetime import datetime
from typing import Union, List

from pydantic import BaseModel, Field

from api.schemas import InDBMixin


class GrapConfigurableSchema(BaseModel):
    """工作流运行时配置"""
    passenger_id: str = Field(description='旅客ID', default="3442 587242")
    thread_id: Union[str, None] = Field(description='会话ID，用于状态保持', default=str(uuid.uuid4()))


class GraphConfigSchema(BaseModel):
    """完整的配置Schema"""
    configurable: Union[GrapConfigurableSchema, None] = Field(description='运行时配置', default=None)


class BaseGraphSchema(BaseModel):
    """调用工作流的请求参数Schema"""
    user_input: str = Field(description='用户输入内容', default=None)
    config: Union[GraphConfigSchema, None] = Field(description='运行配置', default=None)


class GraphRspSchema(BaseModel):
    """工作流执行完成后的响应Schema"""
    assistant: str = Field(description='AI助手的回复内容', default=None)