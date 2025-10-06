from sqlalchemy import create_engine

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session, declarative_base, DeclarativeBase

from contextlib import contextmanager
from typing import Generator
from utils.logger import get_logger

log = get_logger()


class Database:
    _engine: Engine = None
    _SessionFactory: scoped_session = None

    @classmethod
    def init(
        cls,
        url: str = "sqlite:///db.sqlite3",
        echo=False,
        future=True,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    ) -> None:
        if cls._engine is None:
            cls._engine = create_engine(url, echo=echo, future=future)
            cls._SessionFactory = scoped_session(
                sessionmaker(
                    bind=cls._engine,
                    autoflush=autoflush,
                    autocommit=autocommit,
                    expire_on_commit=expire_on_commit,
                )
            )
            
            Base: "DeclarativeBase" = declarative_base()
            Base.metadata.create_all(cls._engine)

            log.debug(f"+ Инициализировано подключение к базе данных: {url}")

    @classmethod
    def get_engine(cls) -> Engine:
        if cls._engine is None:
            raise RuntimeError(
                "Ядро не инициализировано. Вызовите Database.init() перед использованием."
            )
        return cls._engine

    @classmethod
    def get_session(cls) -> Session:
        if cls._SessionFactory is None:
            raise RuntimeError(
                "Сессия не инициализирована. Вызовите Database.init() перед использованием."
            )
        return cls._SessionFactory()

    @classmethod
    @contextmanager
    def session_scope(cls) -> Generator[Session, None, None]:
        session = cls.get_session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @classmethod
    def close(cls) -> None:
        if cls._SessionFactory is not None:
            try:
                cls._SessionFactory.remove()
                log.debug("+ Сессия scoped_session удалена")
            except Exception as e:
                log.warning(f"Ошибка при удалении scoped_session: {e}")
            finally:
                cls._SessionFactory = None

        if cls._engine is not None:
            try:
                cls._engine.dispose()
                log.debug("+ Двигатель базы данных остановлен")
            except Exception as e:
                log.warning(f"! Ошибка при остановке двигателя: {e}")
            finally:
                cls._engine = None

    @classmethod
    def close_all_sessions(cls) -> None:
        """Закрытие всех активных сессий."""
        if cls._SessionFactory is not None:
            try:
                # Закрываем все сессии в registry
                cls._SessionFactory.close_all()
                log.debug("+ Все активные сессии закрыты")
            except Exception as e:
                log.warning(f"! Ошибка при закрытии сессий: {e}")

    @classmethod
    def __del__(cls) -> None:
        log.debug("+ Деструктор Database вызван")
        cls.close()

    @classmethod
    def is_initialized(cls) -> bool:
        return cls._engine is not None and cls._SessionFactory is not None

    @classmethod
    def get_stats(cls) -> dict:
        stats = {
            "initialized": cls.is_initialized(),
            "engine": str(cls._engine) if cls._engine else None,
            "session_factory": str(cls._SessionFactory)
            if cls._SessionFactory
            else None,
        }
        return stats
