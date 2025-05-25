from telegram import BotCommand
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application

from typing import List, Tuple



COMMANDS = [
    # Module Start
    ("start", "Запуск бота"),
    ("help", "Помощь"),
    ("menu", "Меню"),
    ("settings", "Настройки бота"),

    # Module Schedule
    ("schedule", "Расписание группы (в зависимости от выбора)"),
    ("week", "Расписание группы (в зависимости от выбора)"),
    ("today", "Получить расписание на сегодня"),
    ("tomorrow", "Получить расписание на завтра"),

    # Module Group
    ("set_group", "Установить группу"),
    ("set_subgroup", "Установить подгруппу"),

]


def create_command_keyboard(commands: list[tuple[str, str]]) -> ReplyKeyboardMarkup:
    buttons = []
    
    # Группируем кнопки по 2 в ряд
    for i in range(0, len(commands), 2):
        row = [KeyboardButton(f"/{cmd[0]}") for cmd in commands[i:i+2]]
        buttons.append(row)
    
    return buttons


async def setup_commands(application: 'Application', commands: List[Tuple[str, str]]):
    application.bot_data['command_keyboard'] = create_command_keyboard(commands)
    
    await application.bot.set_my_commands(
        [BotCommand(command, description) for command, description in commands]
    )



