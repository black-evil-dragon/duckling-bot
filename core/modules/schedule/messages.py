from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from core.data.weekdays import WEEKDAYS
from core.settings.commands import CommandNames
from core.modules.schedule.formatters import get_date_by_weekday

import logging
import datetime



log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)



# * KEYBOARDS ___________________________________________________________________
def create_pagination_keyboard(callback_data: str, current_page: int, total_pages: int, entity='страница') -> 'InlineKeyboardMarkup':
    """
    Устаревшая функция
    """
    log.warning('[func - create_pagination_keyboard]: This method is deprecated. Use use_paginator instead')

    keyboard = []

    if current_page > 0:
        keyboard.append(InlineKeyboardButton(f"⬅️ Предыдущая {entity}", callback_data=f"{callback_data}_{current_page-1}"))


    if current_page < total_pages - 1:
        keyboard.append(InlineKeyboardButton(f"Следующая {entity} ➡️", callback_data=f"{callback_data}_{current_page+1}"))
    
    return InlineKeyboardMarkup([keyboard])


def use_paginator(callback_data: str, prev_key: str = None, next_key: str = None, entity='Страница', additional_buttons: list = None) -> 'InlineKeyboardMarkup':
    """
    Более улучшеная функция
    """
    keyboard = []

    if prev_key is not None:
        keyboard.append(InlineKeyboardButton(f"⬅️ {entity}", callback_data=f"{callback_data}_{prev_key}"))
    
    keyboard.append(InlineKeyboardButton("📍 Меню", callback_data="delegate#menu"))

    if next_key is not None:
        keyboard.append(InlineKeyboardButton(f"{entity} ➡️", callback_data=f"{callback_data}_{next_key}"))
    
    return InlineKeyboardMarkup([
        keyboard,
        additional_buttons if additional_buttons is not None else [],
    ])



# * TEXT ___________________________________________________________________

schedule_not_found = "Расписание пустое"
schedule_without_data = f"Данные расписания отсутствуют. Запросите расписание снова /{CommandNames.SCHEDULE}"
schedule_warning_cache = f"⚠️ Данные недели кешируются! Для получения актуального расписания необходимо запросить расписание снова /{CommandNames.WEEK}"

week_not_found = "Неделя не найдена. Обратитесь к администратору"


session_error = "Произошла ошибка при установке сессии\n\nПопробуйте снова позже"


server_error = "Произошла ошибка при запросе к серверу\n\nПопробуйте снова позже"



# * TEMPLATES ___________________________________________________________________
def schedule_title(title):
    return f"<b>📅 Расписание группы {title}</b>"


def week_info(week_type, first_date, last_date=None):
    first_date = datetime.datetime.strptime(first_date, "%Y-%m-%d").strftime("%d.%m.%Y")

    if last_date is not None:
        last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        return f"<b>| {week_type} | {first_date} - {last_date} |</b>"
    
    return f"<b>| {week_type} | {first_date} |</b>"


def schedule_content(lesson: dict):
    """
    {
        'title': 'Программирование нейронных сетей',
        'time': '17:15 - 18:45',
        'teacher': 'доц., Истратов Михаил Леонидович',
        'type': 'Лекция',
        'location': 'к. Дистант, ауд. Дистант',
        'order': 30,
        'subgroup': ' '
    }
    """
    title = lesson.get('title')
    time = lesson.get('time')
    teacher = lesson.get('teacher')
    lesson_type = lesson.get('type')
    location = lesson.get('location') if 'Дистант' not in lesson.get('location') else 'Дистант'
    subgroup = lesson.get('subgroup', " ") or " "  # ??????


    return (
        f"* 🕒 <b>{time} {subgroup}</b>\n"
        f"| 📚 {title}\n"
        f"| 🎯 {lesson_type}\n"
        f"| 👨‍🏫 {teacher}\n"
        f"| 📍 {location}\n\n"
    )

def format_schedule_day(data: dict) -> str:
    message = ""

    group: str = data.get('group', '')
    date = data.get('date', '')
    week_number: int = data.get('week_number', 0)
    week_day = data.get('week_day', '')
    lessons: list = data.get('lessons', [])


    week_odd_even = "Нечётная" if week_number % 2 != 0 else "Чётная"
    weekday_name = WEEKDAYS.get(str(week_day), "EMPTY")

    message += schedule_title(group)
    message += '\n'
    message += week_info(week_odd_even, date)
    message += '\n\n'
    message += f"<b>{weekday_name}</b>\n"


    if not lessons:
        message += "❌ Занятий нет\n\n"
        return message


    for lesson in lessons:
        message += schedule_content(lesson)

    message += f"<i>Последнее обновление: {data.get('last_update', '')}</i>"

    
    return message
    

def format_schedule_weeks(data: dict, week_number=None) -> str:
    message = ""

    group: str = data.get('group', '')
    weeks: dict = data.get('data', {})


    if not weeks:
        return schedule_not_found
    
    # Если номер недели не указан, берем первую доступную
    if week_number is None:
        week_number = list(weeks.keys())[0]
    
    week: dict = weeks.get(week_number)


    if not week:
        return week_not_found
    
    week_odd_even = "Нечётная" if week['is_odd'] else "Чётная"

    message += schedule_title(group)
    message += '\n'
    message += week_info(week_odd_even, week.get('date_start'), week.get('date_end'))

    for day_key in week.get('days', {}):
        lessons = week['days'][day_key]

        weekday_date = get_date_by_weekday(week.get('date_start'), int(day_key))
        weekday_name = WEEKDAYS.get(str(day_key), "EMPTY")


        message += f"<b>{weekday_name} ({weekday_date})</b>\n"

        if not lessons:
            message += "❌ Занятий нет\n\n"
            continue

        for lesson in lessons:
            message += schedule_content(lesson)

    message += week_info(week_odd_even, week.get('date_start'), week.get('date_end'))
    message += '\n'
    message += f"<i>Последнее обновление: {data.get('last_update', '')}</i>"

    
    
    return message
    