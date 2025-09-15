
#! DEPRECATED FIX
from typing import Optional
from .deprecated import Database
 
from sqlalchemy.orm import DeclarativeBase, declared_attr




class BaseModel(DeclarativeBase):
    __abstract__ = True
    
    class Meta:
        table_name: Optional[str] = None
        
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Если указано кастомное имя в Meta - используем его
        if hasattr(cls, 'Meta') and hasattr(cls.Meta, 'table_name') and cls.Meta.table_name:
            return cls.Meta.table_name
        
        # Иначе генерируем автоматически
        name = cls.__name__
        snake_case = ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
        return f"{snake_case}s"



__all__ = [
    'Database',
    'BaseModel',
]
