from typing import Dict

import datetime



# * Base template
#  Базовый класс с методами для формирования сообщений
class BaseTemplate:    
    WEEKDAYS = {
        '1': 'Понедельник', '2': 'Вторник', '3': 'Среда',
        '4': 'Четверг', '5': 'Пятница', '6': 'Суббота', '7': 'Воскресенье'
    }
    
    
    def get_message(self, *args, **kwargs):
        raise NotImplementedError('Метод get_message должен быть реализован в классе-наследнике')

    
    # * Компоненты
    def header_component(
        self,
        group_name: str,
        week_type: str,
        first_date: str,
        last_date: str = None
    ) -> str:
    
        first_date = datetime.datetime.strptime(first_date, "%Y-%m-%d").strftime("%d.%m.%Y")

        if last_date is not None:
            last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d").strftime("%d.%m.%Y")

        date_info = f"{first_date} - {last_date}" if last_date else first_date
        

        
        return (
            f"<b>📅 Расписание группы {group_name}</b>\n"
            f"<b>| {week_type} | {date_info} |</b>"
        )
    
    def weekday_name_component(self,
        weekday_name: str
    ):
        return f"<b>{weekday_name}</b>"    
    

    def weekday_component(self,
        date_start: str,
        day_key: int = None
    ):
        weekday = self.get_weekday_name(day_key)
        
        if day_key:
            weekday += f" ({self.get_date_by_weekday(date_start, int(day_key))})"

        return self.weekday_name_component(weekday)
    

    
    def lesson_component(self, lesson: Dict[str, str])  -> str:
        title = lesson.get('title', '')
        time = lesson.get('time', '')
        teacher = lesson.get('teacher', '')
        lesson_type = lesson.get('type', '')
        location = lesson.get('location', '')
        subgroup = lesson.get('subgroup', ' ') or ' '
        
        # Упрощаем локацию для дистанта
        if 'Дистант' in location:
            location = 'Дистант'
            
        return (
            f"┌ 🕒 <b>{time} {subgroup}</b>\n"
            f"├ 📚 {title}\n"
            f"├ 🎯 {lesson_type}\n"
            f"├ 👨‍🏫 {teacher}\n"
            f"└ 📍 {location}"
        )
    
    
    def footer_component(self, last_update: str) -> str:
        result = ""
        
        if last_update:
            result += f"<i>Последнее обновление: {last_update}</i>\n"
            
        result += f"Получено: {datetime.datetime.now().time()}\n"
        

        return result
    
    
    # * Utils
    def get_date_by_weekday(self, start_date: str, weekday: int) -> str:
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        target_date = start + datetime.timedelta(days=weekday-1)
        return target_date.strftime("%d.%m.%Y")

    def get_weekday_name(self, week_day: str) -> str:
        return self.WEEKDAYS.get(str(week_day), "EMPTY")

    def get_short_lesson_type(self, lesson_type: str) -> str:
        lesson_type = lesson_type.replace(' ', '').lower()
        short_lesson_types = {
            'лекция': 'ЛЕК',
            'практика': 'ПРА', 
            'лабораторная': 'ЛАБ',
            'семинар': 'СЕМ',
            'экзамен': 'ЭКЗ',
            'зачет': 'ЗАЧ',
            'диф.зачет': 'ДЗАЧ',
            'консультация': 'КОНС',
        }
        return short_lesson_types.get(lesson_type, lesson_type)

