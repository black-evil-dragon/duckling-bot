

from core.settings.commands import CommandNames


start_error_register = "Привет! Но что-то пошло не так с сохранением данных 😢"

show_command_keyboard = "Выберите действие 🚀"

reopen_menu = f"Окей! Повторное открытие меню:\n\n***/{CommandNames.MENU}***"
settings_text = (
    "🔧 Настройки: " \
    "\n"
    "<b>Только подгруппа</b> - При установке этого параметра в расписании указаны только общие занятия и с подгруппой указанной пользователем\n\n" \
    f"<b>По умолчанию неделя</b> - При установке этого параметра при вызове /{CommandNames.SCHEDULE} вернется расписание недели\n\n" \
    f"<b>По умолчанию день</b> - При установке этого параметра при вызове /{CommandNames.SCHEDULE} вернется расписание на день\n\n" \
)


def start_hello(name: str) -> str:
    return f"Привет, {name}!"