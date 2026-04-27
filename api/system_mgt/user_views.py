"""
用户管理视图
提供用户登录、注册、认证等接口
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from api.system_mgt.user_schemas import (
    UserLoginSchema,
    UserRegisterSchema,
    UserResponseSchema,
)
from config import settings
from db import sm
from db.system_mgt.models import UserModel
from db.system_mgt.user_dao import UserDao

# 创建路由
router = APIRouter()
log = logging.getLogger('user')

# 密码加密上下文
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# OAuth2 依赖
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/login/')


def get_db():
    """获取数据库会话"""
    session = sm()
    try:
        yield session
    finally:
        session.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserModel]:
    """认证用户"""
    user_dao = UserDao()
    user = user_dao.get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


@router.post('/register/', response_model=dict, description='用户注册', summary='用户注册')
async def register(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    user_dao = UserDao()

    # 检查用户名是否已存在
    existing_user = user_dao.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='用户名已存在'
        )

    # 创建新用户
    from api.system_mgt.user_schemas import CreateOrUpdateUserSchema
    user_obj = CreateOrUpdateUserSchema(
        username=user_data.username,
        password=get_password_hash(user_data.password),
        phone=user_data.phone,
        real_name=user_data.real_name
    )
    new_user = user_dao.create(db, user_obj)

    log.info(f'[User Register] 用户 {user_data.username} 注册成功, id={new_user.id}')
    return {
        'id': new_user.id,
        'username': new_user.username,
        'message': '注册成功'
    }


@router.post('/login/', response_model=dict, description='用户登录', summary='用户登录')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口
    使用 OAuth2 表单格式
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        log.warning(f'[User Login Failed] 用户名或密码错误: {form_data.username}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='用户名或密码错误',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username, 'user_id': user.id},
        expires_delta=access_token_expires
    )

    log.info(f'[User Login Success] 用户 {user.username} 登录成功, id={user.id}')

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'id': user.id,
        'username': user.username,
    }


@router.get('/profile/', response_model=UserResponseSchema, description='获取当前用户信息', summary='获取用户信息')
async def get_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前登录用户信息
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='无效的认证凭据',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_dao = UserDao()
    user = user_dao.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception

    return user