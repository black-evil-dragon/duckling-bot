from optparse import Option
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship, joinedload

from db.core import Database, models

from typing import List, Optional, Tuple, Union
import datetime


class Subscriber(models.BaseModel):
    class Meta:
        table_name = 'subscribers'

    is_active = Column(Boolean, default=False)
        
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref=f'{Meta.table_name}')
    
    schedule_time = Column(Time, default=None, index=True)
    
    
    def __str__(self):
        return f"Подписчик: {self.user_id}"
    
    
    def set_scheduled_time(self, time: 'datetime.datetime'):
        self.scheduled_time = time
        self.save()
        
        
    def get_schedule_time(self, to_str: bool = False) -> Optional[Union[str, datetime.time]]:
        if self.schedule_time is None:
            return None
        
        if to_str:
            return self.schedule_time.strftime('%H:%M')

        return self.schedule_time
    
    
    
    @classmethod
    def get_active_subscribers(cls) -> List['Subscriber']:
        subscribers = []
        
        with Database.session_scope() as session:
            joined_table = session.query(cls).options(joinedload(cls.user))
            subscribers = [subscriber for subscriber in joined_table.filter(cls.is_active) if subscriber.user and subscriber.user.group_id]

        return subscribers
    
    
    @classmethod
    def get_subscriber_by_unique_times(cls) -> List['Subscriber']:
        with Database.session_scope() as session:
            return session.query(cls).filter(cls.is_active).distinct(cls.schedule_time).all()