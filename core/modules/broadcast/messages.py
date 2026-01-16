from telegram import InlineKeyboardButton, InlineKeyboardMarkup


broadcast_auth_ask_type = "Выберите тип авторизации: "
broadcast_ask_message = "Напишите сообщение, которое будет отправлено адресатам:"

auth_type_buttons = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Администратор", callback_data="ignore"), InlineKeyboardButton("Преподаватель", callback_data="ignore")]]
)
