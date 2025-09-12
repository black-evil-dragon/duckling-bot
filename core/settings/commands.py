from telegram import BotCommand
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application

from typing import List, Tuple


class Command:
    name = ""
    description = ""

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def get_data(self):
        return (self.name, self.description)

    def get_name(self):
        return self.name

    def get_command(self):
        return f"/{self.name}"

    def get_description(self):
        return self.description


class CommandNames:
    START = "start"
    SCHEDULE = "schedule"
    MENU = "menu"
    SET_GROUP = "set_group"
    SET_SUBGROUP = "set_subgroup"
    WEEK = "week"
    TODAY = "today"
    TOMORROW = "tomorrow"
    SETTINGS = "settings"
    HELP = "help"


COMMANDS_LIST = [
    Command(CommandNames.SCHEDULE, "Расписание (в зависимости от выбора)"),
    Command(CommandNames.MENU, "Меню"),
    Command(CommandNames.SET_GROUP, "Установить группу"),
    Command(CommandNames.SET_SUBGROUP, "Установить подгруппу"),
    Command(CommandNames.WEEK, "Получить расписание на неделю"),
    Command(CommandNames.TODAY, "Получить расписание на сегодня"),
    Command(CommandNames.TOMORROW, "Получить расписание на завтра"),
    Command(CommandNames.SETTINGS, "Настройки бота"),
    Command(CommandNames.HELP, "Помощь"),
]

#! Deprecated
COMMANDS = [command.get_data() for command in COMMANDS_LIST]


def create_command_keyboard(commands: list[tuple[str, str]]) -> ReplyKeyboardMarkup:
    buttons = []

    # Группируем кнопки по 2 в ряд
    for i in range(0, len(commands), 2):
        row = [KeyboardButton(f"/{cmd[0]}") for cmd in commands[i : i + 2]]
        buttons.append(row)

    return buttons


async def setup_commands(application: "Application", commands: List[Tuple[str, str]]):
    application.bot_data["command_keyboard"] = create_command_keyboard(commands)

    await application.bot.set_my_commands(
        [BotCommand(command, description) for command, description in commands]
    )
