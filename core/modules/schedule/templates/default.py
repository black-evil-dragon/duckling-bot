import datetime
from core.modules.schedule.templates.base import BaseTemplate

# * Default template
class DefaultTemplate(BaseTemplate):
    # 📅 Расписание группы 4Б09 РПС-31
    # | Чётная | 01.10.2025 |

    # Среда
    # * 🕒 09:40 - 11:10  
    # | 📚 Основы теории управления
    # | 🎯 Лекция
    # | 👨‍🏫 доц., Сергушичева Анна Павловна
    # | 📍 к. 4, ауд. 2а

    # * 🕒 11:40 - 13:10  
    # | 📚 Основы программно-информационных систем
    # | 🎯 Лекция
    # | 👨‍🏫 ст.пр., Ковырзина Татьяна Федоровна
    # | 📍 к. 2, ауд. 227/3

    # Последнее обновление: 30.09.2025 15:54:20
    # Получено: 19:17:09.294201
    
    def get_message(self, data: dict, data_type: str = 'day', week_number: int = None) -> str:
        if data_type == 'day':
            return self.format_schedule_day(data)
        
        if data_type == 'weeks':
            return self.format_schedule_weeks(data, week_number)
        
              
           
    
    def format_schedule_day(self, data: dict) -> str:
        # Ininital data
        message = ""
        group = data.get('group', '')
        date = data.get('date', '')
        week_number = data.get('week_number', 0)
        week_day = data.get('week_day', '')
        lessons = data.get('lessons', [])
        
        # Prepare
        week_odd_even = "Нечётная" if week_number % 2 != 0 else "Чётная"
        weekday_name = self.get_weekday_name(week_day)

        # Create message
        message += (
            f"{self.header_component(group, week_odd_even, date)}"
            "\n\n"
            f"{self.weekday_name_component(weekday_name)}"
            "\n"
        )

        if not lessons:
            message += "❌ Занятий нет\n\n"
        else:
            for lesson in lessons:
                message += (
                    f"{self.lesson_component(lesson)}"
                    "\n\n"
                )


        message += self.footer_component(data.get('last_update', ''))
        
        return message
    
    
    
    def format_schedule_weeks(self, data: dict, week_number: int = None) -> str:
        # Prepare data
        message = ""
        group: str = data.get('group', '')
        
        weeks: dict = data.get('data', {})
        if not weeks:
            return "Расписание не найдено"
        
        if week_number is None:
            week_number = list(weeks.keys())[0]
        
        
        week: dict = weeks.get(week_number)
        if not week:
            return "Неделя не найдена"
        
        week_odd_even = "Нечётная" if week['is_odd'] else "Чётная"


        # Create message
        message += (
            f"{self.header_component(
                group,
                week_odd_even,
                week.get('date_start'), week.get('date_end')
            )}"
            "\n\n"
        )
        
        
        # Weekdays
        for day_key in week.get('days', {}):
            # Weekday
            message += self.weekday_component(week.get('date_start'), int(day_key)) + "\n"

            # Lessons
            lessons = week['days'][day_key]
            if not lessons:
                message += "❌ Занятий нет\n\n"
                continue

            for lesson in lessons:
                message += (
                    f"{self.lesson_component(lesson)}"
                    "\n\n"
                )

        message += self.footer_component(data.get('last_update', ''))

        return message
    