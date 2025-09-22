from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, joinedload

from db.core import Database, models

from typing import List
import datetime


class Subscriber(models.BaseModel):
    class Meta:
        table_name = 'subscribers'

    
    class ScheduleTypes(models.TextChoices):
        FOR_TODAY = 'today', 'На сегодня'
        FOR_TOMORROW = 'tomorrow', 'На завтра'
    
        

    is_active = Column(Boolean, default=False)
        
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref=f'{Meta.table_name}')
    
    schedule_type = Column(String, default=f'{ScheduleTypes.FOR_TODAY}')
    schedule_time = Column(DateTime, default=None)
    
    
    def __str__(self):
        return f"Подписчик: {self.user_id}"
    
    
    def set_scheduled_time(self, time: 'datetime.datetime'):
        self.scheduled_time = time
        self.save()
        
    @classmethod
    def get_active_subscribers(cls) -> List['Subscriber']:
        subscribers = []
        
        with Database.session_scope() as session:
            joined_table = session.query(cls).options(joinedload(cls.user))
            subscribers = [subscriber for subscriber in joined_table.filter(cls.is_active) if subscriber.user and subscriber.user.group_id]

        return subscribers