from core.settings.commands import CommandNames


# * TEXT ___________________________________________________________________
choose_reminder_time_button = "⏰ Выбрать время"
ask_reminder_time = "⏰ Выберите время напоминания:"

# * TEMPLATES ___________________________________________________________________


def user_scheduled_reminder_template(time=None):
    if not time:
        return f"Напоминание не выбрано. Используйте команду /{CommandNames.SET_REMINDER}"

    return f"Выбран режим - {time}"