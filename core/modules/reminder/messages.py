from core.settings.commands import CommandNames


# * TEXT ___________________________________________________________________
choose_reminder_time_button = "⏰ Выбрать время"
ask_reminder_time = "⏰ Пожалуйста, введите время в формате ЧЧ:ММ (например, 14:30)"
wrong_format_time = "❌ Неверный формат времени. Пожалуйста, используйте ЧЧ:ММ (например, 09:30)"

# * TEMPLATES ___________________________________________________________________
def success_selected_time_template(time):
    return f"✅ Время напоминания установлено на {time}"

def user_scheduled_reminder_template(time=None):
    if not time:
        return f"Напоминание не выбрано. Используйте команду /{CommandNames.SET_REMINDER}"

    return f"Рассылка в {time}"