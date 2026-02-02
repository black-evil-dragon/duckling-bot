from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from core.settings.commands import CommandNames

from core.modules.schedule.templates.base import BaseTemplate
from core.modules.schedule.templates.default import DefaultTemplate
from core.modules.schedule.templates.minimal import MinimalTemplate
from core.modules.schedule.templates.compact import CompactTemplate

from utils.logger import get_logger
from typing import List, Literal, overload



log = get_logger()



# * KEYBOARDS ___________________________________________________________________
def create_pagination_keyboard(callback_data: str, current_page: int, total_pages: int, entity='страница') -> 'InlineKeyboardMarkup':
    """
    Устаревшая функция
    """
    log.warning('[func - create_pagination_keyboard]: This method is deprecated. Use use_paginator instead')

    keyboard = []

    if current_page > 0:
        keyboard.append(InlineKeyboardButton(f"⬅️ Предыдущая {entity}", callback_data=f"{callback_data}_{current_page-1}"))


    if current_page < total_pages - 1:
        keyboard.append(InlineKeyboardButton(f"Следующая {entity} ➡️", callback_data=f"{callback_data}_{current_page+1}"))

    return InlineKeyboardMarkup([keyboard])



def use_paginator(callback_data: str, prev_key: str = None, next_key: str = None, entity='Страница', additional_buttons: list = None) -> 'InlineKeyboardMarkup':
    """
    Более улучшеная функция
    """
    keyboard = []

    if prev_key is not None:
        keyboard.append(InlineKeyboardButton(f"⬅️ {entity}", callback_data=f"{callback_data}#{prev_key}"))

    keyboard.append(InlineKeyboardButton("📍 Меню", callback_data=f"delegate#{CommandNames.MENU}"))

    if next_key is not None:
        keyboard.append(InlineKeyboardButton(f"{entity} ➡️", callback_data=f"{callback_data}#{next_key}"))

    return InlineKeyboardMarkup([
        keyboard,
        additional_buttons if additional_buttons is not None else [],
    ])


def get_refresh_button(callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton("🔄 Обновить", callback_data=callback_data)

def get_schedule_button(callback: str = None) -> InlineKeyboardButton:
    return InlineKeyboardButton("📅 Сегодня", callback_data=callback or f"delegate#{CommandNames.SCHEDULE}")

def get_target_buttons(additional_buttons: List[InlineKeyboardButton] = None) -> List[List[InlineKeyboardButton]]:
    return [
        [
            InlineKeyboardButton("Установленное", callback_data="ignore")
        ],
        [
            InlineKeyboardButton("📚 Группа", callback_data=f"delegate#{CommandNames.SCHEDULE}?target_type=student"),
            InlineKeyboardButton("💼 Преподаватель", callback_data=f"delegate#{CommandNames.SCHEDULE}?target_type=teacher")
        ],
        [
            InlineKeyboardButton("Другое (выбор нового)", callback_data="ignore")
        ],
        [
            InlineKeyboardButton("📚 Группа", callback_data=f"delegate#{CommandNames.QUICK_GROUP_SCHEDULE}"),
            InlineKeyboardButton("💼 Преподаватель", callback_data=f"delegate#{CommandNames.QUICK_TEACHER_SCHEDULE}"),
        ],
        [InlineKeyboardButton("🏫 Кабинет", callback_data=f"delegate#{CommandNames.QUICK_LOCATION_SCHEDULE}")],

        additional_buttons

    ]


# * TEXT ___________________________________________________________________

# Dialog
schedule_ask_date = "📅 Выберите дату:"
schedule_ask_target_type = "🎯 Выберите тип расписания:"

schedule_not_found = "Расписание пустое"
schedule_without_data = f"Данные расписания отсутствуют. Запросите расписание снова /{CommandNames.SCHEDULE}"



week_not_found = "Неделя не найдена. Обратитесь к администратору"


session_error = "Произошла ошибка при установке сессии\n\nПопробуйте снова позже"
server_error = "Произошла ошибка при запросе к серверу\n\nПопробуйте снова позже"


#! DEPRECATED
schedule_warning_cache = (
    f"⚠️ Данные недели кешируются! В случае изменения расписания необходимо запросить расписание снова /{CommandNames.WEEK}\n"
    f"Также вы можете получить расписание на сегодня /{CommandNames.TODAY} и воспользоваться кнопкой <b>Обновить</b>"
)



# * TEMPLATES ___________________________________________________________________
class TemplateManager:
    TEMPLATES = {
        'default': DefaultTemplate,
        'compact': CompactTemplate,
        'minimal': MinimalTemplate,
    }

    def __init__(self):
        self._instances = {}


    @overload
    def get_template(self, name: Literal['minimal']) -> MinimalTemplate: ...

    @overload
    def get_template(self, name: Literal['compact']) -> CompactTemplate: ...

    @overload
    def get_template(self, name: Literal['default']) -> DefaultTemplate: ...

    @overload
    def get_template(self) -> DefaultTemplate: ...



    def get_template(self, template_name: str = 'default') -> BaseTemplate:
        if template_name not in self.TEMPLATES:
            template_name = 'default'

        if template_name not in self._instances:
            self._instances[template_name] = self.TEMPLATES[template_name]()

        return self._instances[template_name]

    def register_template(self, name: str, template_class):
        if issubclass(template_class, BaseTemplate):
            self.TEMPLATES[name] = template_class