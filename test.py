from db import Database

from db.core.models import BaseModel
from db.core.manager import BaseManager

from sqlalchemy import Column, String

# Инициализация БД
Database.init(url="sqlite:///test.db", echo=True)

# Описание модели
class User(BaseModel):
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    



# # Создание таблиц
User.create_all()
User.objects.create({"name": "Ivan", "email": "ivan1@example.com"})

# # Менеджер для работы с User
# user_manager = BaseManager(User)

# # Создание пользователя
# new_user = user_manager.create({"name": "Ivan", "email": "ivan@example.com"})

# # Получение списка
# users = user_manager.list()

# # Обновление
# updated = user_manager.update(new_user.id, {"name": "Ivan Petrov"})

# # Удаление
# deleted = user_manager.delete(new_user.id)