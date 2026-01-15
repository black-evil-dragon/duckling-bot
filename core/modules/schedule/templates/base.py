from core.modules.base import strf_time_mask


from typing import Dict, Literal

import datetime



# * Base template
#  Базовый класс с методами для формирования сообщений
class BaseTemplate:

    target_type: Literal['student', 'teacher'] = 'student'

    WEEKDAYS = {
        '1': 'Понедельник', '2': 'Вторник', '3': 'Среда',
        '4': 'Четверг', '5': 'Пятница', '6': 'Суббота', '7': 'Воскресенье'
    }


    def get_message(self, *args, **kwargs):
        raise NotImplementedError('Метод get_message должен быть реализован в классе-наследнике')



    # * Компоненты
    def header_component(
        self,
        target_name: str,
        first_date: str,
        last_date: str = None
    ) -> str:
        week_even = datetime.datetime.strptime(first_date, strf_time_mask).isocalendar().week % 2 != 0

        first_date = datetime.datetime.strptime(first_date, strf_time_mask).strftime("%d.%m")

        if last_date is not None:
            last_date = datetime.datetime.strptime(last_date, strf_time_mask).strftime("%d.%m")

        date_info = f"{first_date} - {last_date}" if last_date else first_date


        return (
            f"<b>📅 Расписание: {target_name}</b>\n"
            f"<b>| {'Четная' if week_even else 'Нечетная'} | {date_info} |</b>"
        )


    def weekday_name_component(self,
        weekday_name: str
    ):
        return f"<b>{weekday_name}</b>"


    def weekday_component(self,
        date: str,
        day_key: int = None,
        bold = True
    ):
        weekday = self.get_weekday_name(day_key)
        date = datetime.datetime.strptime(date, strf_time_mask).strftime("%d.%m")

        if day_key:
            weekday += f" ({date})"

        return self.weekday_name_component(weekday) if bold else weekday


    def lesson_component(self, lesson: Dict[str, str])  -> str:
        title = lesson.get('title', '')
        time = lesson.get('time', '')
        teacher = lesson.get('teacher', '')
        teacher_degree = lesson.get('teacher_degree', '')
        lesson_type = lesson.get('type', '')
        location = lesson.get('location', '')
        subgroup = lesson.get('subgroup', ' ') or ' '

        target = f"│ 👨‍🏫 {teacher_degree} {teacher}\n"
        if self.target_type == 'teacher':
            target = f"│ 🙋🏼‍♂️ {lesson.get('group')}\n"

        # Упрощаем локацию для дистанта
        if 'Дистант' in location:
            location = 'Дистант'

        return (
            f"┌ 🕒 <b>{time} {subgroup}</b>\n"
            f"│ 📚 {title}\n"
            f"│ 🎯 {lesson_type}\n"
            f"{target}"
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
            'зачёт': 'ЗАЧ',
            'диф.зачет': 'ДЗАЧ',
            'консультация': 'КОНС',
        }
        return short_lesson_types.get(lesson_type, lesson_type)

    def get_short_lesson_name(self, lesson) -> str:
        short_lesson_names = {
            'Элективные дисциплины по физической культуре и спорту': 'Физкультура (электив)'
        }

        return short_lesson_names.get(lesson, lesson)

