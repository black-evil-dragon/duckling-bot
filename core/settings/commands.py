from telegram import BotCommand
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application

from db.core.models.enums import TextChoices

from typing import List, Tuple

class CommandNames(TextChoices):
    START = "start", "Запуск"
    HELP = "help", "Помощь"
    MENU = "menu", "Меню"
    SETTINGS = "settings", "Настройки"
    
    SET_GROUP = "group", "Установить группу"
    SET_SUBGROUP = "subgroup", "Установить подгруппу"
    
    SET_REMINDER = "reminder", "Установить время рассылки"
    SHOW_REMINDER = "myreminder", "Моя рассылка"
    
    SCHEDULE = "schedule", "Расписание"
    WEEK = "week", "Расписание на неделю"
    TODAY = "today", "Расписание на сегодня"
    TOMORROW = "tomorrow", "Расписание на завтра"
    

class Command:
    name = ""
    description = ""

    def __init__(self, name, description = None):
        self.name = name
        
        if description is None:
            description = CommandNames.get_label(name)

        self.description = description

    def get_data(self):
        return (self.get_name(), self.get_description())

    def get_name(self):
        return self.name

    def get_command(self):
        return f"/{self.name}"

    def get_description(self):
        # print(CommandNames.get_label(self.name))
        return self.description or CommandNames.get_label(self.name)



COMMANDS_LIST = [
    Command(CommandNames.SCHEDULE, "Расписание (в зависимости от выбора)"),
    Command(CommandNames.MENU),
    Command(CommandNames.SET_GROUP),
    Command(CommandNames.SET_SUBGROUP),
    Command(CommandNames.WEEK),
    Command(CommandNames.TODAY),
    
    Command(CommandNames.SET_REMINDER),
    Command(CommandNames.SHOW_REMINDER),
    
    Command(CommandNames.TOMORROW),
    Command(CommandNames.SETTINGS),
    Command(CommandNames.HELP),
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

    await application.bot.set_my_commands([BotCommand(command, description) for command, description in commands])
