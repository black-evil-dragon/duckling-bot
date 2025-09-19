from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, joinedload


from db.core import Database, models


from typing import List



class Subscriber(models.BaseModel):
    class Meta:
        table_name = 'subscribers'

    cron_data = {
        "morning-7-40": dict(
            hour=7,
            minute=40
        ),
        "morning-9-20": dict(
            hour=9,
            minute=20
        ),
        "morning-11-20": dict(
            hour=11,
            minute=20
        ),
        "day-14-30": dict(
            hour=14,
            minute=30
        )
    }
    

    class TimeChoices(models.TextChoices):
        MORNING_7_40 = 'morning-7-40', '7:40'
        MORNING_9_20 = 'morning-9-20', '9:20'
        MORNING_11_20 = 'morning-11-20', '11:20'
        
        DAY_14_30 = 'day-14-30', '14:30'

    is_active = Column(Boolean, default=False)
        
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref=f'{Meta.table_name}')
    
    scheduled_time = Column(String, default=f'{TimeChoices.MORNING_7_40}')
    
    
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