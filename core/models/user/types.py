from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from core.models import User


__all__ = [
    'UserSettingsType', 'UserSelectedDataType', 'UserDataType',
    'MessageTemplateType', 'TargetType'
]


MessageTemplateType = Literal["default", "compact", "minimal"]
TargetType = Literal["student", "teacher"]


class UserSettingsType(TypedDict):
    """Типизированные настройки пользователя"""

    show_week: bool
    """
    Режим отображения расписания:
    - True: показывать расписание на неделю (7 дней)
    - False: показывать расписание только на текущий день

    """

    subgroup_lock: bool
    """
    Блокировка выбора подгруппы:
    - True: отображение расписания только для выбранной подгруппы, включая потоковые занятия
    - False: отображение расписания для всех подгрупп, включая потоковые занятия

    """

    reminder: bool
    """
    Общие напоминания о занятиях:
    - True: отправлять напоминания
    - False: не отправлять напоминания
    """

    reminder_today: bool
    """
    Напоминания только на сегодня:
    - True: отправлять напоминания на сегодняшнюю дату
    - False: отправлять напоминание на следующую дату
    """

    message_template: MessageTemplateType
    """
    Шаблон для сообщений и уведомлений:
    - "default": стандартный формат (время, предмет, преподаватель, аудитория)
    - "compact": компактный вариант стандартного формата
    - "minimal": минимальный формат
    """

    target_type: TargetType
    """
    Целевой тип пользователя для фильтрации контента:
    - "student": расписание для студентов, т.е группы
    - "teacher": расписание для преподавателей
    """



class UserSelectedDataType(TypedDict):
    selected_target: TargetType
    selected_group: str
    selected_subgroup: str


class UserDataType(UserSelectedDataType):
    instance: 'User'

    user_id: int
    first_name: str
    last_name: str
    username: str
    role: str

    user_settings: UserSettingsType


DEFAULT_USER_SETTINGS: UserSettingsType = dict(
    show_week=False,
    subgroup_lock=True,
    reminder=False,
    reminder_today=False,
    message_template="default",
    target_type="student"
)