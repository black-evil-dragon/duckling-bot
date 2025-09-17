from telegram.ext import Application

from core.modules.base import BaseModule
from core.modules.group.module import GroupModule
from core.modules.reminder.module import ReminderModule
from core.modules.schedule import ScheduleModule
from core.modules.start.module import StartModule


from utils.logger import get_logger
from typing import List

log = get_logger()


def setup_modules(application: 'Application'):
    """
    Иницилизация модулей
    """
    log.info('Иницилизация модулей')
    modules: List[BaseModule] = [
        ScheduleModule(),
        GroupModule(),
        StartModule(),
        ReminderModule(),
    ]

    for module in modules:
        try:
            module.setup(application)
            log.info(f'| {module} - установлен')

        except Exception:
            log.error(f"| {module} - ошибка при инициализации модуля")
            log.exception('| Ошибка:')
