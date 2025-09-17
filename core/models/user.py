from sqlalchemy import Boolean, Column, Integer, String
from db.core.models import BaseModel

import json
import logging


log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)

class User(BaseModel):
    user_id = Column(Integer, unique=True)

    is_bot = Column(Boolean, default=False)

    first_name = Column(String, nullable=False)
    last_name = Column(String, default="")
    username = Column(String, default="")

    group_id = Column(Integer, default=None)
    subgroup_id = Column(Integer, default=None)
    user_settings = Column(String, default=None)

    def __str__(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.first_name

    def get_user_settings(self):
        try:
            if not self.user_settings:
                return {}

            return json.loads(self.user_settings)
        except Exception:
            log.exception('Не удалось получить настройки пользователя')
            return {}
        
        
    def set_user_settings(self, user_settings: dict):
        self.user_settings = json.dumps(user_settings)
        self.save()
        
        
