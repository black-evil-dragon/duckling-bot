from telegram.ext import Application

from core.modules.base import BaseModule
from core.modules.group.module import GroupModule
from core.modules.reminder.module import ReminderModule
from core.modules.schedule import ScheduleModule
from core.modules.start.module import StartModule


from utils.logger import get_logger
from typing import List

log = get_logger()


def setup_modules(application: 'Application', job_manager=None):
    """
    Иницилизация модулей
    """
    modules: List[BaseModule] = [
        ScheduleModule(),
        GroupModule(),
        StartModule(),
        ReminderModule(job_manager=job_manager),
    ]

    for module in modules:
        try:
            module.setup(application)
        except Exception:
            log.exception(f"Ошибка при инициализации модуля {module}")
