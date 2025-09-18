#
# * DB packages ____________________________________________
from ast import Dict
from enum import Enum
from db.core import Database
from db.core.manager import BaseManager, ManagerDescriptor

from sqlalchemy import Column, DateTime, func, Integer

from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.ext.declarative import declared_attr



# * Other packages ____________________________________________
from typing import Tuple, Type, TypeVar, List, Optional, Any
import logging


T = TypeVar("T", bound="BaseModel")
log = logging.getLogger("duckling")

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
        
        
        
    class TextChoices(str, Enum):
        def __new__(cls, value: str, label: str):
            obj = str.__new__(cls, value)
            obj._value_ = value
            obj.label = label
            return obj
        
        def __get__(self, isinstance, owner):
            pass
        
        @classmethod
        def choices(cls) -> List[Tuple[str, str]]:
            return [(member.value, member.label) for member in cls]
        
        @classmethod
        def get_label(cls, value: str) -> str:
            for member in cls:
                if member.value == value:
                    return member.label
        
        
        @classmethod
        def get_value(cls, label: str) -> str:
            for member in cls:
                if member.label == label:
                    return member.value




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
    def __repr__(self):
        cls_name = self.__class__.__name__
        fields = []
    
        if hasattr(self, "__str__"):
            fields.append(f"{self.__str__()}")
            
        fields_str = ", ".join(fields)
        return f"<{cls_name}: {fields_str}>"

    def __str__(self):
        cls_name = self.__class__.__name__
        return f"<{cls_name} object {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        if hasattr(self, "id") and hasattr(other, "id"):
            return self.id == other.id
        return False

    
    
    
    # * _______________________________________________________
    # * |                   Management          
    objects = ManagerDescriptor(BaseManager)
    
    @property
    def pk(self):
        return self.id
    
    
    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def save(self):
        with Database.session_scope() as session:
            merged_obj = session.merge(self)
            session.flush()
            session.refresh(merged_obj)
            return merged_obj
        
    def update(self, **fields) -> Optional[T]:        
        with Database.session_scope() as session:
            for key, value in dict(**fields).items():
                setattr(self, key, value)
                
            merged_obj = session.merge(self)
            session.flush()
            session.refresh(merged_obj)

            return merged_obj

        
    # TRASH ----------
        
    
    @classmethod
    def create_all(cls) -> None:
        """Создать все таблицы в БД."""
        engine = Database.get_engine()
        cls.metadata.create_all(bind=engine)
        
        log.debug(f'+ Созданы таблицы: {cls}')


    @classmethod
    def drop_all(cls) -> None:
        """Удалить все таблицы из БД."""
        engine = Database.get_engine()
        cls.metadata.drop_all(bind=engine)


    @classmethod
    def get_by_id(cls: Type[T], obj_id: int, session: Session) -> Optional[T]:
        """Получить объект по id."""
        return session.get(cls, obj_id)


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
