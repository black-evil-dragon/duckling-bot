from sqlalchemy import Boolean, Column, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.orm import Session

from db.core import Database, models

from typing import List, Optional, Union
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
    

    def get_user(self, session: "Session" = None):
        if session is None:
            with Database.session_scope() as session:
                return session.merge(self).user

        return session.merge(self).user
    
    
    def set_scheduled_time(self, time: 'datetime.datetime'):
        self.scheduled_time = time
        self.save()
        
        
    def get_schedule_time(self, to_str: bool = False) -> Optional[Union[str, datetime.time]]:
        self.schedule_time: Optional[datetime.datetime | None]

        if self.schedule_time is None:
            return None
        
        if to_str:
            return self.schedule_time.strftime('%H:%M')

        return self.schedule_time
    
    
    @classmethod
    def get_active_subscribers(cls) -> List['Subscriber']:        
        with Database.session_scope() as session:
            joined_table = session.query(cls).options(joinedload(cls.user))
            return [
                subscriber for subscriber in joined_table.filter(cls.is_active)
                if subscriber.user and subscriber.user.group_id and subscriber.schedule_time
            ]