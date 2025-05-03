from typing import List, Tuple
from telegram import BotCommand

COMMANDS = [
    ("start", "Запуск бота"),
    ("help", "Помощь"),
    ("menu", "Меню"),
    ("schedule", "Расписание группы"),
    ("today", "Получить расписание на сегодня"),
    ("tomorrow", "Получить расписание на завтра"),
    ("set_group", "Установить группу"),
    ("settings", "Настройки бота")
]

async def setup_commands(application, commands: List[Tuple[str, str]]):
    await application.bot.set_my_commands(
        [BotCommand(command, description) for command, description in commands]
    )