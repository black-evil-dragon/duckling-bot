#
# * DB packages ____________________________________________
from . import Database
from sqlalchemy.orm import Session

from db.types.models import BaseModelType


# * Other packages ____________________________________________
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any



T = TypeVar("T", bound=BaseModelType)

class BaseManager(Generic[T]):
    model: Type[T]

    def __init__(self, model: Type[T]) -> None:
        """
        :param model: ORM-модель, унаследованная от BaseModel.
        """
        self.model = model
        print('init base manager')
        

    def create(self, data: Dict[str, Any]) -> T:
        """Создать новый объект."""        
        session: Optional['Session'| None]

        with Database.session_scope() as session:
            obj = self.model(**data)
            session.add(obj)
            session.flush()
            session.refresh(obj)
            return obj

    def get(self, obj_id: int) -> Optional[T]:
        """Получить объект по id."""
        session: Optional['Session'| None]
        
        with Database.session_scope() as session:
            return self.model.get_by_id(obj_id, session)

    def list(self) -> List[T]:
        """Получить все объекты."""
        session: Optional['Session'| None]
        
        with Database.session_scope() as session:
            return self.model.list_all(session)

    def update(self, obj_id: int, data: Dict[str, Any]) -> Optional[T]:
        """Обновить поля объекта."""
        session: Optional['Session'| None]
        
        with Database.session_scope() as session:
            obj = self.model.get_by_id(obj_id, session)
            if obj is None:
                return None
            for key, value in data.items():
                setattr(obj, key, value)
            session.flush()
            session.refresh(obj)
            return obj

    def delete(self, obj_id: int) -> bool:
        """Удалить объект по id."""
        session: Optional['Session'| None]
        
        with Database.session_scope() as session:
            obj = self.model.get_by_id(obj_id, session)
            if obj is None:
                return False
            session.delete(obj)
            return True

    def filter(self, **kwargs: Any) -> List[T]:
        """Фильтрация объектов по параметрам."""
        session: Optional['Session'| None]
        
        with Database.session_scope() as session:
            return self.model.filter_by(session, **kwargs)


class ManagerDescriptor:
    # Дескриптор для доступа к менеджеру как в Django
    def __init__(self, manager_class: Type[BaseManager]):
        self.manager_class = manager_class
        self.manager_instance = None
    
    def __get__(self, instance, owner) -> BaseManager:
        if instance is not None:
            raise AttributeError("Manager isn't accessible via instances")
        
        if self.manager_instance is None:
            self.manager_instance = self.manager_class(owner)
        return self.manager_instance