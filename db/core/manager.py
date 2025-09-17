#
# * DB packages ____________________________________________
from . import Database
from sqlalchemy.orm import Session

from db.types.models import BaseModelType


# * Other packages ____________________________________________
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from utils.logger import get_logger


T = TypeVar("T", bound="BaseModelType")


log = get_logger()


class BaseManager(Generic[T]):
    model: Type[T]

    def __init__(self, model: Type[T]) -> None:
        """
        :param model: ORM-модель, унаследованная от BaseModel.
        """
        self.model = model

        log.debug("+ Инициализирован BaseManager")
        
    


    def create(self, **fields) -> "T":
        """Создать новый объект."""
        session: Optional["Session" | None]

        with Database.session_scope() as session:
            obj = self.model(**fields)
            session.add(obj)
            session.flush()
            session.refresh(obj)
            return obj

    def get_by_id(self, obj_id: int) -> Optional[T]:
        """Получить объект по id."""
        session: Optional["Session" | None]

        with Database.session_scope() as session:
            return self.model.get_by_id(obj_id, session)
        
    def get(self, **filters) -> Optional[T]:
        """Получить объект по id."""
        session: Optional["Session" | None]

        with Database.session_scope() as session:
            query = session.query(self.model)
            for field, value in filters.items():
                query = query.filter(getattr(self.model, field) == value)
            return query.first()
        
        
    def get_or_create(self, defaults: Optional[Dict[str, Any]] = None, **filters) -> "T":
        """Получить объект по фильтрам или создать новый с defaults."""

        defaults = defaults or {}

        with Database.session_scope() as session:
            query = session.query(self.model)
            for field, value in filters.items():
                query = query.filter(getattr(self.model, field) == value)
            instance = query.first()

            if instance:
                return instance

            params = {**filters, **defaults}
            instance = self.model(**params)
            session.add(instance)
            session.flush()
            session.refresh(instance)
            return instance

    def all(self) -> List[T]:
        """Получить все объекты."""
        session: Optional["Session" | None]

        with Database.session_scope() as session:
            return self.model.list_all(session)

    def update(self, obj_id: int, data: Dict[str, Any]) -> Optional[T]:
        """Обновить поля объекта."""
        session: Optional["Session" | None]

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
        session: Optional["Session" | None]

        with Database.session_scope() as session:
            obj = self.model.get_by_id(obj_id, session)
            if obj is None:
                return False
            session.delete(obj)
            return True

    def filter(self, **kwargs: Any) -> List[T]:
        """Фильтрация объектов по параметрам."""
        session: Optional["Session" | None]

        with Database.session_scope() as session:
            return self.model.filter_by(session, **kwargs)


# class ManagerDescriptor:
#     # Дескриптор для доступа к менеджеру как в Django
#     def __init__(self, manager_class: Type[BaseManager]):
#         self.manager_class = manager_class
#         self.manager_instance = None

#     def __get__(self, instance, owner) -> BaseManager:
#         if instance is not None:
#             raise AttributeError("Manager isn't accessible via instances")

#         if self.manager_instance is None:
#             self.manager_instance = self.manager_class(owner)
#         return self.manager_instance
class ManagerDescriptor:
    def __init__(self, manager_class: Type[BaseManager]) -> None:
        self.manager_class = manager_class
        self._instances: dict = {}


    def __get__(self, instance, owner) -> BaseManager:
        if instance is not None:
            raise AttributeError("Manager доступен только через класс, не через экземпляр")
        
        if owner not in self._instances:
            self._instances[owner] = self.manager_class(owner)
        
        return self._instances[owner]
