from sqlalchemy import Boolean, Column, Integer, String

from core.models.subscriber import Subscriber
from db.core.models import BaseModel

from utils.logger import get_logger
import json


log = get_logger()

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
            return f"Пользователь {self.first_name} {self.last_name}"
        else:
            return f"Пользователь {self.first_name}"
        
        
    def get_selected_data(self):
        return dict(
            selected_institute=self.group_id,
            selected_group=self.group_id,
            selected_subgroup=self.subgroup_id,
        )
        
    def set_group(self, selected_group):
        self.group_id = selected_group
        self.save()
        
    def set_subgroup(self, selected_subgroup):
        self.subgroup_id = selected_subgroup
        self.save()
        

    def get_scheduled_time_reminder(self):
        subscriber: Subscriber = Subscriber.objects.get(user=self.user_id)
        if not subscriber: return None, None
        
        return subscriber.scheduled_time, Subscriber.TimeChoices.get_label(subscriber.scheduled_time)
    

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
        
        
