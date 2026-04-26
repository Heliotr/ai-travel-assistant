"""
数据库基础DAO类
提供通用的增删改查操作，所有数据库操作DAO类可继承此类
"""

from typing import Generic, List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from api.schemas import ModelType, CreateSchema, UpdateSchema


class BaseDAO(Generic[ModelType, CreateSchema, UpdateSchema]):
    """
    通用数据库访问对象
    使用泛型实现通用的CRUD操作
    """

    model: ModelType  # 具体的数据库模型类

    def get(self, session: Session) -> List[ModelType]:
        """查询所有记录"""
        return session.scalars(select(self.model)).all()

    def get_by_id(self, session: Session, pk: int) -> ModelType:
        """根据主键查询单条记录"""
        return session.get(self.model, pk)

    def create(self, session: Session, obj_in: CreateSchema) -> ModelType:
        """插入一条新记录"""
        obj = self.model(**jsonable_encoder(obj_in))
        session.add(obj)
        session.commit()
        return obj

    def update(self, session: Session, pk: int, obj_in: UpdateSchema) -> ModelType:
        """根据主键更新记录"""
        obj = self.get_by_id(session, pk)
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(obj, key, val)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, pk: int) -> None:
        """根据主键删除单条记录"""
        obj = self.get_by_id(session, pk)
        session.delete(obj)
        session.commit()

    def count(self, session: Session):
        """返回记录总条数"""
        return session.query(self.model).count()

    def deletes(self, session: Session, ids: List[int]):
        """根据主键列表批量删除"""
        stmt = delete(self.model).where(self.model.id.in_(ids))
        session.execute(stmt)
        session.commit()