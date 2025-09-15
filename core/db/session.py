from contextlib import contextmanager
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, Session

from . import BaseModel

from typing import Callable, Generator, Any, Type, TypeVar, List, Optional, Dict, cast
from functools import wraps

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class DB:
    def __init__(self, db_url: str = "sqlite:///db.sqlite3"):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def __del__(self):
        self.SessionLocal.close_all()

    def create_tables(self) -> None:
        BaseModel.metadata.create_all(self.engine)

    def init(self):
        self.create_tables()

        return self
    
    def close():
        self.Ses
    
    

    def on_session(func: F) -> F:
        @wraps(func)
        def wrapper(self: "DB", *args: Any, **kwargs: Any) -> Any:
            session = self.SessionLocal()
            try:
                result = func(self, session, *args, **kwargs)
                session.commit()
                return result
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

        return cast(F, wrapper)

    @contextmanager
    def get_session(self) -> Generator[Session, Any, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @on_session
    def create(self, session: "Session", obj: "BaseModel") -> Any:
        """Создать новый объект"""
        session.add(obj)
        session.flush()
        session.refresh(obj)

        return obj

    @on_session
    def get(self, session: "Session", model: Type[T], id: Any) -> Optional[T]:
        """Получить объект по ID"""
        return session.get(model, id)

    def get_or_none(self, model: Type[T], **filters) -> Optional[T]:
        """Получить объект по фильтрам или None если не найден"""
        with self.get_session() as session:
            stmt = select(model).filter_by(**filters)
            return session.scalar(stmt)

    def all(self, model: Type[T]) -> List[T]:
        """Получить все объекты модели"""
        with self.get_session() as session:
            stmt = select(model)
            return list(session.scalars(stmt))

    def filter(self, model: Type[T], **filters) -> List[T]:
        """Фильтрация объектов"""
        with self.get_session() as session:
            stmt = select(model).filter_by(**filters)
            return list(session.scalars(stmt))

    def update(self, obj: Any, **values) -> None:
        """Обновить объект"""
        with self.get_session() as session:
            # Прикрепляем объект к текущей сессии если он еще не в ней
            if obj not in session:
                obj = session.merge(obj)

            for key, value in values.items():
                setattr(obj, key, value)

    def delete(self, obj: Any) -> None:
        """Удалить объект"""
        with self.get_session() as session:
            # Прикрепляем объект к текущей сессии если он еще не в ней
            if obj not in session:
                obj = session.merge(obj)
            session.delete(obj)

    def delete_by_id(self, model: Type[T], id: Any) -> bool:
        """Удалить объект по ID"""
        with self.get_session() as session:
            obj = session.get(model, id)
            if obj:
                session.delete(obj)
                return True
            return False

    def update_or_create(
        self, model: Type[T], defaults: Optional[Dict] = None, **filters
    ) -> T:
        """Обновить или создать объект"""
        if defaults is None:
            defaults = {}

        with self.get_session() as session:
            # Пытаемся найти существующий объект
            stmt = select(model).filter_by(**filters)
            instance = session.scalar(stmt)

            if instance:
                # Обновляем существующий объект
                for key, value in defaults.items():
                    setattr(instance, key, value)
            else:
                # Создаем новый объект
                instance = model(**filters, **defaults)
                session.add(instance)

            session.flush()
            session.refresh(instance)
            return instance

    def count(self, model: Type[T]) -> int:
        """Подсчитать количество объектов"""
        with self.get_session() as session:
            stmt = select(model)
            return session.scalar(select(func.count()).select_from(stmt.subquery()))
