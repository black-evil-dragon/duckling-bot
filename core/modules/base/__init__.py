# Вообще по хорошему тут все переделать, но так исторически сложилось


# * Telegram bot framework ________________________________________________________________________
import datetime
from typing import Any, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, BaseHandler, ContextTypes


# * Core ________________________________________________________________________
from core.modules.base import messages
from core.modules.base.decorators import ensure_user_settings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.modules import ModuleManager

strf_time_mask = "%Y-%m-%d"


# * MODULE ___________________________________________________________________
class BaseModule:
    application: Application = None
    manager: 'ModuleManager' = None

    HANDLERS: Tuple[BaseHandler[Any, Any, Any]]

    def __init__(self, application: Application, module_manager: 'ModuleManager') -> None:
        self.application = application
        self.manager = module_manager

        self.setup()

    def __repr__(self):
        return f"<class {self.__class__.__name__}>"

    def __str__(self):
        return f"<{self.__class__.__name__}>"

    def setup(self) -> None:
        raise Exception("Функция не переопределена")

    # * ____________________________________________________________
    # * |                       Utils                               |

    # ? Well
    @staticmethod
    @ensure_user_settings()
    async def update_user_settings(*args, **kwargs):
        pass

    @staticmethod
    def clear_choices(context: 'ContextTypes.DEFAULT_TYPE'):
        for key in ['selected_institute', 'selected_course', 'selected_group']:
            context.user_data[key] = None

    # * |___________________________________________________________|

    # * ____________________________________________________________
    # * |                        UI                                 |
    # * | Buttons
    menu_button = InlineKeyboardButton("📍 Меню", callback_data="delegate#menu")

    @staticmethod
    def delegate_button_template(text, command):
        return InlineKeyboardButton(text=text, callback_data=f"delegate#{command}")

    @staticmethod
    def generate_calendar(year=None, month=None):
        """
        Генерирует inline-клавиатуру в виде календаря.

        Args:
            year: Год (если None, используется текущий)
            month: Месяц (1-12, если None, используется текущий)

        Returns:
            InlineKeyboardMarkup: Клавиатура с календарем
        """
        # Используем текущую дату, если год и месяц не указаны
        now = datetime.datetime.now()
        year = year or now.year
        month = month or now.month

        # Определяем первый день месяца и количество дней
        first_day = datetime.datetime(year, month, 1)
        days_in_month = 31 if month in [1, 3, 5, 7, 8, 10, 12] else 30
        if month == 2:
            days_in_month = (
                29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
            )

        # Получаем день недели для первого дня (0 = понедельник, 6 = воскресенье)
        # Для телеграма часто используют 0 = понедельник
        first_weekday = first_day.weekday()  # 0 = понедельник, 6 = воскресенье

        # Создаем заголовок с месяцем и годом
        month_names = [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь",
        ]

        keyboard = []

        # Заголовок с месяцем и годом
        header_row = [
            InlineKeyboardButton(
                f"{month_names[month - 1]} {year}", callback_data="ignore"
            )
        ]
        keyboard.append(header_row)

        # Дни недели
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        weekdays_row = [
            InlineKeyboardButton(day, callback_data="ignore") for day in weekdays
        ]
        keyboard.append(weekdays_row)

        # Дни месяца
        row = []
        # Пустые кнопки для дней до первого дня месяца
        for _ in range(first_weekday):
            row.append(InlineKeyboardButton(" ", callback_data="ignore"))

        # Кнопки с днями
        for day in range(1, days_in_month + 1):
            # Формируем callback_data в формате "calendar_day_YYYY-MM-DD"
            callback_data = f"calendar_nav#day&{year}-{month:02d}-{day:02d}"
            row.append(InlineKeyboardButton(str(day), callback_data=callback_data))

            # Переход на новую строку после субботы (6 день недели)
            if (day + first_weekday) % 7 == 0 or day == days_in_month:
                keyboard.append(row)
                row = []

        # Добавляем навигационные кнопки
        nav_row = []

        # Предыдущий месяц
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year = year - 1
        nav_row.append(
            InlineKeyboardButton(
                "◀️", callback_data=f"calendar_nav#month&{prev_year}_{prev_month}"
            )
        )

        # Кнопка "Сегодня"
        today = datetime.datetime.now()
        if not (year == today.year and month == today.month):
            nav_row.append(
                InlineKeyboardButton(
                    "Сегодня", callback_data=f"calendar_nav#month&{today.year}_{today.month}"
                )
            )

        # Следующий месяц
        next_month = month + 1
        next_year = year
        if next_month == 13:
            next_month = 1
            next_year = year + 1
        nav_row.append(
            InlineKeyboardButton(
                "▶️", callback_data=f"calendar_nav#month&{next_year}_{next_month}"
            )
        )

        keyboard.append(nav_row)

        return InlineKeyboardMarkup(keyboard)
    # * |___________________________________________________________|



    # * _____________________________________________________________
    # * |               Callback handlers                            |
    @classmethod
    async def handle_calendar_callback(cls, update: Update, context: 'ContextTypes.DEFAULT_TYPE', hide_after=False):
        """Обработчик нажатий на кнопки календаря"""
        query = update.callback_query
        await query.answer()

        _, query_data = query.data.split('#')
        calendar, value = query_data.split('&')

        if calendar == 'day':
            date = datetime.datetime.strptime(value, strf_time_mask).strftime('%d.%m')

            if hide_after:
                await query.edit_message_text(
                    messages.calendar_chosen_text(date)
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=messages.calendar_chosen_text(date)
                )
            return value

        elif calendar == 'month':
            year_str, month_str = value.split("_")
            year, month = int(year_str), int(month_str)

            keyboard = cls.generate_calendar(year, month)
            await query.edit_message_reply_markup(reply_markup=keyboard)

    # * |___________________________________________________________|




    # COMMENT TEMPLATES

    # * ____________________________________________________________
    # * |               Command handlers                            |

    # * |___________________________________________________________|

    # * ____________________________________________________________
    # * |               Message handlers                            |

    # * |___________________________________________________________|

    # * ____________________________________________________________
    # * |               Callback handlers                            |
    # ...
    # * |___________________________________________________________|
