from telegram import BotCommand
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application

from db.core.models.enums import TextChoices

from typing import List, Tuple

class CommandNames(TextChoices):
    START = "start", "Обо мне"
    HELP = "help", "Помощь"
    MENU = "menu", "Меню"
    SETTINGS = "settings", "Настройки"

    SET_GROUP = "group", "Установить группу"
    SET_SUBGROUP = "subgroup", "Установить подгруппу"

    SET_TEACHER = "teacher", "Установить преподавателя"


    SET_REMINDER = "setreminder", "Установить время рассылки"
    SHOW_REMINDER = "myreminder", "Моя рассылка"

    SCHEDULE = "schedule", "Расписание"

    DATE = "date", "Расписание на дату"
    WEEK = "week", "Расписание на неделю"
    TODAY = "today", "Расписание на сегодня"
    TOMORROW = "tomorrow", "Расписание на завтра"

    QUICK_SCHEDULE = "quick", "Расписание с выбором группы или преподавателя"
    QUICK_GROUP_SCHEDULE = "quickgroup", "Расписание c выбором группы"
    QUICK_TEACHER_SCHEDULE = "quickteacher", "Расписание c выбором преподавателя"

    AUTH = "auth", "Авторизоваться"
    BROADCAST = "broadcast", "Создать оповещение"


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
        return self.description or CommandNames.get_label(self.name)


# * Здесь хранятся все команды бота
# отображаются в заданном порядке,
# есть возможность дать краткое описание
COMMANDS_LIST = [
    Command(CommandNames.START),
    Command(CommandNames.SCHEDULE, "Расписание (в зависимости от выбора)"),
    Command(CommandNames.MENU),

    Command(CommandNames.QUICK_SCHEDULE),

    Command(CommandNames.DATE),
    Command(CommandNames.TODAY),
    Command(CommandNames.TOMORROW),
    Command(CommandNames.WEEK),

    # Command(CommandNames.QUICK_GROUP_SCHEDULE),
    # Command(CommandNames.QUICK_TEACHER_SCHEDULE),

    Command(CommandNames.SET_GROUP),
    Command(CommandNames.SET_SUBGROUP),
    Command(CommandNames.SET_TEACHER),

    Command(CommandNames.SET_REMINDER),
    Command(CommandNames.SHOW_REMINDER),

    Command(CommandNames.SETTINGS),
    Command(CommandNames.HELP),

    Command(CommandNames.AUTH),
    Command(CommandNames.BROADCAST),
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
