from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from core.modules.base import BaseModule
from core.settings.commands import CommandNames


# * TEXT ___________________________________________________________________
choose_reminder_time_button = "⏰ Выбрать время"
ask_reminder_time = "⏰ Пожалуйста, введите время в формате ЧЧ:ММ (например, 14:30)"
wrong_format_time = "❌ Неверный формат времени. Пожалуйста, используйте ЧЧ:ММ (например, 09:30)"
time_is_not_chosen = (
    "❌ Выбери время для рассылки перед установкой напоминания"
)


group_is_empty = f"❌ Извини, сегодня без рассылки(\nГруппа пуста. Выбери группу с помощью команды /{CommandNames.SET_GROUP}"
group_is_not_chosen = (
    "❌ Выбери группу перед установкой напоминания"
)

reminder_help_text = "<b>На сегодня</b> - расписание на текущий день рассылки\n<b>На завтра</b> - расписание на следующий день рассылки\n<b>Выбрать время</b> - задать время для рассылки"



# * TEMPLATES ___________________________________________________________________
def success_selected_time_template(time):
    return f"✅ Время напоминания установлено на {time}"

def user_scheduled_reminder_template(time=None):
    if not time:
        return f"Напоминание не выбрано. Используйте команду /{CommandNames.SET_REMINDER}"

    return f"🗓 Рассылка в {time}\n\n{reminder_help_text}"


def reminder_say_hello(day_id: int):
    templates = {
        0: "Привет, понедельник! 🌞 Начинаем новую учебную неделю! Удачи в занятиях! 📚",
        1: "Вторник - отличный день для учебы! 📖 Не забывайте про расписание группы",
        2: "Среда - маленькая пятница! 🎉 Учебная неделя в разгаре для группы",
        3: "Четверг - время подвести промежуточные итоги!",
        4: "Пятница! 🎊 Скоро выходные! Завершайте учебные дела",
        5: "Суббота - день для отдыха и саморазвития!",
        6: "Воскресенье - готовимся к новой неделе!"
    }
    
    return templates[day_id]



# * KEYBOARDS
def reminder_keyboard_default(settings: dict):
    return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=f"На сегодня {'✅' if settings.get('reminder_today', True) else '❌'}",
                    callback_data=f"settings#bool${not settings.get('reminder_today', True)}$reminder_today"
                ),
                InlineKeyboardButton(
                    text=f"На завтра {'✅' if not settings.get('reminder_today', True) else '❌'}",
                    callback_data=f"settings#bool${not settings.get('reminder_today', True)}$reminder_today"
                ), 
            ],
            [
                BaseModule.delegate_button_template(
                    choose_reminder_time_button,
                    f"{CommandNames.SET_REMINDER}"
                )
            ],
            [
                BaseModule.menu_button, BaseModule.delegate_button_template(
                    "Настройки",
                    f"{CommandNames.SETTINGS}"
                )
            ]
            ])