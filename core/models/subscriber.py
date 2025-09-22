from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, joinedload


from db.core import Database, models


from typing import List



class Subscriber(models.BaseModel):
    class Meta:
        table_name = 'subscribers'

    cron_data = {
        "today-7-40": dict(
            hour=7,
            minute=40
        ),
        "today-9-20": dict(
            hour=9,
            minute=20
        ),
        "today-11-20": dict(
            hour=11,
            minute=20
        ),
        "today-14-30": dict(
            hour=14,
            minute=30
        )
    }
    

    class TimeChoices(models.TextChoices):
        TODAY_7_40 = 'today-7-40', 'На сегодня в 7:40'
        TODAY_9_20 = 'today-9-20', 'На сегодня в 9:20'
        TODAY_11_20 = 'today-11-20', 'На сегодня в 11:20'
        TODAY_14_30 = 'today-14-30', 'На сегодня в 14:30'
        
        # TOMORROW_7_40 = 'tomorrow-7-40', 'На завтра в 7:40'
        # TOMORROW_9_20 = 'tomorrow-9-20', 'На завтра в 9:20'
        TOMORROW_11_20 = 'tomorrow-11-20', 'На завтра в 11:20'
        TOMORROW_14_30 = 'tomorrow-14-30', 'На завтра в 14:30'
        TOMORROW_17_00 = 'tomorrow-17-00', 'На завтра в 17:00'
        TOMORROW_19_30 = 'tomorrow-19-30', 'На завтра в 19:30'
        

    is_active = Column(Boolean, default=False)
        
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref=f'{Meta.table_name}')
    
    scheduled_time = Column(String, default=f'{TimeChoices.TODAY_7_40}')
    
    
    def __str__(self):
        return f"Подписчик: {self.user_id}"
    
    
    def set_scheduled_time(self, time):
        self.scheduled_time = time
        self.save()
        
    @classmethod
    def get_active_subscribers(cls) -> List['Subscriber']:
        subscribers = []
        
        with Database.session_scope() as session:
            joined_table = session.query(cls).options(joinedload(cls.user))
            subscribers = [subscriber for subscriber in joined_table.filter(cls.is_active) if subscriber.user and subscriber.user.group_id]

        return subscribers