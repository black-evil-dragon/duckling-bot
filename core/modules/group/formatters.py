from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_schedule_keyboard(current_week=0, total_weeks=0):
    keyboard = []

    if current_week > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Предыдущая неделя", callback_data=f"week_{current_week-1}"))
    
    if current_week < total_weeks - 1:
        keyboard.append(InlineKeyboardButton("Следующая неделя ➡️", callback_data=f"week_{current_week+1}"))
    
    return InlineKeyboardMarkup([keyboard])