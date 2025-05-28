from core.data.weekdays import WEEKDAYS

from core.modules.schedule.messages import schedule_content, schedule_title, week_info


def format_schedule_week(data, week_idx=0):
    if not data or 'schedule' not in data:
        return "Расписание не найдено"

    
    weeks = data['schedule']
    week_types = data['schedule'][-1]
    
    if week_idx >= len(weeks) - 1:
        return "Неделя не найдена"
    
    week = weeks[week_idx]
    week_type = week_types[week_idx] if week_idx < len(week_types) else ""
    
    message = schedule_title(data['title'])


    first_date = list(week.items())[0][1][-1]
    last_date = list(week.items())[-1][1][-1]

    message += week_info(week_type, first_date, last_date)
    
    for day_num, day_data in week.items():
        if day_num.isdigit():
            date = day_data[1]
            weekday_name = WEEKDAYS.get(day_num, f"День {day_num}")
            lessons = day_data[0]
            
            if not lessons:
                message += f"<b>{date} ({weekday_name})</b>\n"
                message += "❌ Занятий нет\n\n"
                continue
            
            message += f"<b>{date} ({weekday_name})</b>\n"
            
            for lesson in lessons:
                message += schedule_content(lesson)
    
    message += week_info(week_type, first_date, last_date)
    message += f"<i>Последнее обновление: {data['last_update']}</i>"
    
    return message