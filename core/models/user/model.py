
#* Core ________________________________________________________________________
from sqlalchemy import Boolean, Column, Engine, Inspector, Integer, String, JSON, inspect, text
from db.core import models
from core.models.user.types import DEFAULT_USER_SETTINGS, UserDataType, UserSelectedDataType, UserSettingsType



#* Utils ________________________________________________________________________
from utils.logger import get_logger
from typing import Any, Literal



log = get_logger()



class User(models.BaseModel):
    user_id = Column(Integer, unique=True)

    is_bot = Column(Boolean, default=False)

    first_name = Column(String, nullable=False)
    last_name = Column(String, default="")
    username = Column(String, default="")

    role: Literal['user', 'admin', 'teacher'] = Column(String, default="user") #* MIGRATION!

    teacher_id = Column(Integer, default=None) #* MIGRATION!
    group_id = Column(Integer, default=None)
    subgroup_id = Column(Integer, default=None)

    user_settings = Column(JSON, default=DEFAULT_USER_SETTINGS)


    def __str__(self):
        if self.last_name:
            return f"Пользователь {self.first_name} {self.last_name}"
        else:
            return f"Пользователь {self.first_name}"



    # * MIGRATIONS FIX --- TEMP
    @classmethod
    def create_all(cls):
        return super().create_all(cls.apply_migration)

    @classmethod
    def apply_migration(cls, engine: Engine):
        """Применяет необходимые миграции для таблицы."""

        inspector: Inspector = inspect(engine)


        if 'users' in inspector.get_table_names():
            try:
                columns = [
                    col['name']
                    for col in inspector.get_columns('users')
                ]

                if 'teacher_id' not in columns:
                    log.info("Applying migration")

                    with engine.connect() as conn:
                        conn.execute(text("ALTER TABLE users ADD COLUMN teacher_id INTEGER DEFAULT NULL"))
                        conn.commit()

                    log.info("Проведена миграция: Add teacher_id")

                if 'role' not in columns:
                    log.info("Applying migration")

                    with engine.connect() as conn:
                        conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT \"user\""))
                        conn.commit()

                    log.info("Проведена миграция: Add role")


            except Exception as e:
                log.error(f"Migration failed: {e}")


    # * SERIALIZE DATA
    def get_user_data(self) -> UserDataType:
        user_data: UserDataType = dict(
            user_id=self.user_id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            role=self.role,

            **self.get_selected_data(),
            user_settings=self.get_user_settings(),

            instance=self, # Лучше
            user_model=self,
        )

        return user_data

    def get_selected_data(self) -> UserSelectedDataType:
        return dict(
            selected_teacher=self.teacher_id,
            selected_group=self.group_id,
            selected_subgroup=self.subgroup_id,
        )


    # * TEACHER MANAGEMENT
    def set_teacher(self, teacher_id: int):
        self.teacher_id = teacher_id
        self.save()


    # * GROUP MANAGEMENT
    def set_group(self, selected_group):
        self.group_id = selected_group
        self.save()

    def set_subgroup(self, selected_subgroup, set_subgroup_lock=False):
        self.subgroup_id = selected_subgroup

        settings = self.get_user_settings()

        if settings.get('subgroup_lock', True):
            settings.update(dict(
                subgroup_lock=set_subgroup_lock
            ))
            self.set_user_settings(settings)
            # * Сохранение происходит в set_user_settings
            # - self.save()
            return

        self.save()


    # * SETTINGS MANAGEMENT
    def get_user_settings(self) -> UserSettingsType:
        try:
            if not self.user_settings:
                return DEFAULT_USER_SETTINGS

            return self.user_settings
        except Exception:
            log.exception('Не удалось получить настройки пользователя')
            return {}

    def set_user_settings(self, user_settings: UserSettingsType | dict):
        self.user_settings = user_settings
        self.save()


    def set_setting(self, setting: str, value: Any, value_type: str = 'default') -> dict:
        _value_type = str

        types = {
            'bool': lambda v: v == 'True',
            'int': int,
            'str': str,
            'default': str
        }
        _value_type = types[value_type]
        _value = _value_type(value)

        settings = self.get_user_settings()
        settings.update({setting: _value})

        self.set_user_settings(settings)

        return settings


