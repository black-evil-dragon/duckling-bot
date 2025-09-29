#
# * DB packages ____________________________________________
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.ext.declarative import declared_attr


# * Other packages ____________________________________________
from typing import List, Optional, Any



class BaseModelType(DeclarativeBase):
    __abstract__ = True


    @declared_attr.directive
    def __tablename__(cls) -> str:
        pass
    
    # * _______________________________________________________
    # * |                   Class meta              
    class Meta:
        table_name: Optional[str] = None
        
        
    @classmethod
    def create_all(cls) -> None:
        pass


    @classmethod
    def drop_all(cls) -> None:
        pass


    @classmethod
    def get_by_id(cls: 'BaseModelType', obj_id: int, session: Session) -> Optional['BaseModelType']:
        pass


    @classmethod
    def list_all(cls: 'BaseModelType', session: Session) -> List['BaseModelType']:
        pass


    @classmethod
    def delete_all(cls: 'BaseModelType', session: Session) -> int:
        pass


    @classmethod
    def filter_by(cls: 'BaseModelType', session: Session, **kwargs: Any) -> List['BaseModelType']:
        pass