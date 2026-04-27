"""
用户数据 Schema
定义用户创建和更新的数据模型
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateOrUpdateUserSchema(BaseModel):
    """用户创建/更新 Schema"""
    username: str = Field(..., description='用户名')
    password: str = Field(..., description='密码')
    phone: Optional[str] = Field(None, description='手机号')
    email: Optional[str] = Field(None, description='邮箱')
    real_name: Optional[str] = Field(None, description='真实姓名')


class UserLoginSchema(BaseModel):
    """用户登录 Schema"""
    username: str = Field(..., description='用户名')
    password: str = Field(..., description='密码')


class UserRegisterSchema(BaseModel):
    """用户注册 Schema"""
    username: str = Field(..., description='用户名')
    password: str = Field(..., description='密码')
    phone: Optional[str] = Field(None, description='手机号')
    real_name: Optional[str] = Field(None, description='真实姓名')


class UserResponseSchema(BaseModel):
    """用户响应 Schema"""
    id: int
    username: str
    phone: Optional[str] = None
    email: Optional[str] = None
    real_name: Optional[str] = None
    icon: Optional[str] = None

    class Config:
        from_attributes = True