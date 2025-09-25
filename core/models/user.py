from typing import Any
from sqlalchemy import Boolean, Column, Integer, String
from db.core import models


from core.models.subscriber import Subscriber


from utils.logger import get_logger
import json


log = get_logger()

class User(models.BaseModel):
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
        
        
    # * SERIALIZE DATA 
    def get_user_data(self):
        user_data = dict(
            user_id=self.user_id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            
            **self.get_selected_data(),
            user_settings=self.get_user_settings(),
            
            user_model=self,
            
            # Лучше
            instance=self
        )
        
        return user_data    

    def get_selected_data(self):
        # В целом сломалось все из-за этого,
        # Люблю, что я это сделал.
        return dict(
            selected_group=self.group_id,
            selected_subgroup=self.subgroup_id,
        )
    
    
    # * GROUP MANAGEMENT  
    def set_group(self, selected_group):
        self.group_id = selected_group
        self.save()
        
    def set_subgroup(self, selected_subgroup):
        self.subgroup_id = selected_subgroup
        self.save()
  
    
    # * SETTINGS MANAGEMENT
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
        
        
