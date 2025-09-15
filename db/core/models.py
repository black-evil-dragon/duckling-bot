#
# * DB packages ____________________________________________
from db.core import Database
from db.core.manager import BaseManager, ManagerDescriptor

from sqlalchemy import Column, DateTime, func, Integer

from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.ext.declarative import declared_attr



# * Other packages ____________________________________________
from typing import Type, TypeVar, List, Optional, Any



T = TypeVar("T", bound="BaseModel")


class BaseModel(DeclarativeBase):
    __abstract__ = True



    @declared_attr.directive
    def __tablename__(cls) -> str:
        if (
            hasattr(cls, "Meta")
            and hasattr(cls.Meta, "table_name")
            and cls.Meta.table_name
        ):
            return cls.Meta.table_name

        name = cls.__name__
        snake_case = "".join(
            ["_" + c.lower() if c.isupper() else c for c in name]
        ).lstrip("_")
        return f"{snake_case}s"
    
    




    # * _______________________________________________________
    # * |                   Class meta              
    class Meta:
        table_name: Optional[str] = None



    # * _______________________________________________________
    # * |                   Base fields

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    

    # * _______________________________________________________
    # * |                   Class methods    


    
    
    
    # * _______________________________________________________
    # * |                   Management          

    objects = ManagerDescriptor(BaseManager)


    @classmethod
    def create_all(cls) -> None:
        """Создать все таблицы в БД."""
        engine = Database.get_engine()
        cls.metadata.create_all(bind=engine)


    @classmethod
    def drop_all(cls) -> None:
        """Удалить все таблицы из БД."""
        engine = Database.get_engine()
        cls.metadata.drop_all(bind=engine)


    @classmethod
    def get_by_id(cls: Type[T], obj_id: int, session: Session) -> Optional[T]:
        """Получить объект по id."""
        return session.query(cls).get(obj_id)


    @classmethod
    def list_all(cls: Type[T], session: Session) -> List[T]:
        """Получить все записи таблицы."""
        return session.query(cls).all()


    @classmethod
    def delete_all(cls: Type[T], session: Session) -> int:
        """Удалить все записи таблицы. Возвращает количество удалённых."""
        count = session.query(cls).delete()
        session.flush()
        return count


    @classmethod
    def filter_by(cls: Type[T], session: Session, **kwargs: Any) -> List[T]:
        """Фильтрация по колонкам."""
        return session.query(cls).filter_by(**kwargs).all()
