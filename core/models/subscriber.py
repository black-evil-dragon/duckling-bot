from sqlalchemy import Boolean, Column, Integer, String
from db.core.models import BaseModel



class Subscriber(BaseModel):
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
    class TimeChoices(BaseModel.TextChoices):
        MORNING_7_40 = 'morning-7-40', '7:40'
        MORNING_9_20 = 'morning-9-20', '9:20'
        MORNING_11_20 = 'morning-11-20', '11:20'
        
        DAY_14_30 = 'day-14-30', '14:30'

        
    user_id = Column(Integer, unique=True)
    username = Column(String, default='')
    is_active = Column(Boolean, default=False)
    
    scheduled_time = Column(String, default=TimeChoices.get_value('morning-7-40'))
    
    def __str__(self):
        return f"Подписчик: {self.username}"
    
    
    def set_scheduled_time(self, time):
        self.scheduled_time = time
        self.save()