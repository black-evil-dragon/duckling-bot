from core.modules.schedule.templates.base import BaseTemplate

from typing import Any, Dict


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
            return self.format_schedule_weeks(data)




    def format_schedule_day(self, data: dict) -> str:
        # Ininital data
        message = ""
        group = data.get('group', '')
        date = data.get('date', '')
        week_day = data.get('week_day', '')
        lessons = data.get('lessons', [])

        # Prepare
        weekday_name = self.get_weekday_name(week_day)

        # Create message
        message += (
            f"{self.header_component(group, date)}"
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



    def format_schedule_weeks(self, data: dict) -> str:
        # Prepare data
        message = ""

        group_name: str = data.get('group', '')

        # Create message
        message += (
            f"{self.header_component(
                group_name,
                data.get('date_start'),
                data.get('date_end')
            )}"
            "\n\n"
        )

        days: dict = data.get('days', {})
        day_key: str
        day_value: Dict[str, Any]


        # # Weekdays
        days_without_lessons = []

        for day_key, day_value in sorted(days.items()):
            current_day_name = self.weekday_component(day_key, day_value.get('week_day'), bold=False)
            lessons = day_value['lessons']

            if not lessons:
                days_without_lessons.append(current_day_name)
                continue

            if days_without_lessons:
                message = self.prepare_days_without_lessons(message, days_without_lessons)
                days_without_lessons = []


            message += f"<b>{current_day_name}</b>\n"
            for lesson in lessons:
                message += f"{self.lesson_component(lesson)}\n\n"


        if days_without_lessons:
            message = self.prepare_days_without_lessons(message, days_without_lessons)

        message += self.footer_component(data.get('last_update', ''))

        return message



    def prepare_days_without_lessons(self, message, days_without_lessons):
        if len(days_without_lessons) == 1:
            message += f"<b>{days_without_lessons[0]}</b>\n"
        else:
            first_day_short = days_without_lessons[0].split(' (')[0]
            last_day_full = days_without_lessons[-1]
            message += f"<b>{first_day_short} - {last_day_full}</b>\n"

        message += "❌ Занятий нет\n\n"

        return message