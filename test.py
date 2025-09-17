from db import Database
from db.core.models import BaseModel

from sqlalchemy import Column, String


from utils.logger import setup_logger

import os
import pytest

log = setup_logger()


class User(BaseModel):
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)

    def __str__(self):
        return f"Пользователь {self.name} ({self.email})"


@pytest.fixture(autouse=True)
def setup_database():
    Database.init(url="sqlite:///test.db")
    User.create_all()
    test_create_user() # Для 0-го пользователя
    yield
    # Очистка после каждого теста
    Database.dispose()
    if os.path.exists("./test.db"):
        os.remove("./test.db")


# Создание таблиц
def test_create_tables():
    User.create_all()


def test_create_user():
    """Тест создания пользователя"""
    new_user = User.objects.create({"name": "Ivan", "email": "ivan@example.com"})
    assert new_user is not None


def test_get_list():
    """Тест получения списка"""
    users = User.objects.list()
    assert len(users) > 0


def test_update_user():
    """Тест обновления пользователя"""
    user = User.objects.list()[0]

    updated = User.objects.update(user.id, {"name": "Ivan Petrov"})
    assert updated


def test_delete_user():
    """Тест удаления пользователя"""
    user = User.objects.list()[0]
    deleted = User.objects.delete(user.id)
    assert deleted