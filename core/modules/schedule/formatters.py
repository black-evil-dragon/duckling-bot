from datetime import datetime, timedelta
from typing import Dict

def get_date_by_weekday(start_date, weekday):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    delta = (weekday - 1) - start.weekday()

    if delta < 0:
        delta += 7

    target_date = start + timedelta(days=delta)
    return target_date.strftime("%d.%m.%Y")

def prepare_schedule_weeks_data(weeks: dict):
    prepared_weeks = {}

    for new_index, week_key in enumerate(weeks):
        week_data = weeks[week_key]
        
        # Сортируем занятия внутри каждого дня по полю 'order'
        for day_key in week_data['days']:
            lessons = week_data['days'][day_key]
            lessons.sort(key=lambda lesson: lesson.get('order', 0))
        
        prepared_weeks[new_index] = week_data

    return prepared_weeks



def prepare_schedule_day_data(data: Dict):
    if 'lessons' in data:
        data['lessons'].sort(key=lambda lesson: lesson.get('order', 0))

    return data

