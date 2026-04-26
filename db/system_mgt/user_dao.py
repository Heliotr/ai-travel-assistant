"""
用户数据访问层（DAO）
封装用户相关的数据库操作
"""

from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from api.system_mgt.user_schemas import CreateOrUpdateUserSchema
from db.dao import BaseDAO
from db.system_mgt.models import UserModel


class UserDao(BaseDAO[UserModel, CreateOrUpdateUserSchema, CreateOrUpdateUserSchema]):
    """
    用户DAO类
    继承BaseDAO，封装用户特有的数据库操作
    """

    model = UserModel

    def get_user_by_username(self, session: Session, username: str):
        """根据用户名查询用户"""
        stmt = select(self.model).where(self.model.username == username)
        return session.execute(stmt).scalars().first()

    def search_user(self, session: Session, uid: int = None, username: str = None, real_name: str = None):
        """
        根据条件搜索用户
        支持按ID、用户名、真实姓名模糊查询
        """
        q = session.query(self.model)
        if uid:
            q = q.filter(self.model.id == uid)
        if username:
            q = q.filter(self.model.username == username)
        if real_name:
            q = q.filter(self.model.real_name.like(f'%{real_name}%'))
        return q

    def deletes(self, session: Session, ids: List[int]):
        """
        批量删除用户
        删除用户前先删除用户关联的角色信息
        """
        session.execute(text('delete from t_user_role where user_id in :ids'), {'ids': ids})
        super().deletes(session, ids)

    def create(self, session: Session, obj_in: CreateOrUpdateUserSchema) -> UserModel:
        """
        创建新用户
        排除roles字段（用户角色关联通过其他表管理）
        """
        data = jsonable_encoder(obj_in)
        data.pop('roles', None)  # 排除不存在的字段
        obj = self.model(**data)
        session.add(obj)
        session.commit()
        return obj

    def update(self, session: Session, pk: int, obj_in: CreateOrUpdateUserSchema) -> UserModel:
        """更新用户信息"""
        obj = self.get_by_id(session, pk)
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(obj, key, val)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj