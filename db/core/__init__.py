from sqlalchemy import create_engine

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from contextlib import contextmanager
from typing import Generator


class Database:
    _engine: Engine = None
    _SessionFactory: scoped_session = None

    @classmethod
    def init(cls, url: str = "sqlite:///db.sqlite3", echo=False, future=True, autoflush=False, autocommit=False) -> None:
        if cls._engine is None:
            cls._engine = create_engine(url, echo=echo, future=future)
            cls._SessionFactory = scoped_session(sessionmaker(bind=cls._engine, autoflush=autoflush, autocommit=autocommit))

    @classmethod
    def get_engine(cls) -> Engine:
        if cls._engine is None:
            raise RuntimeError("Ядро не инициализировано. Вызовите Database.init() перед использованием.")
        return cls._engine

    @classmethod
    def get_session(cls) -> Session:
        if cls._SessionFactory is None:
            raise RuntimeError("Сессия не инициализирована. Вызовите Database.init() перед использованием.")
        return cls._SessionFactory()

    @classmethod
    @contextmanager
    def session_scope(cls) -> Generator[Session, None, None]:
        """Контекстный менеджер для сессий."""
        session = cls.get_session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
