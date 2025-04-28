from typing import List
from telegram.ext import Application

from core.modules.base import BaseModule
from core.modules.group.module import GroupModule
from core.modules.schedule import ScheduleModule

def setup_modules(application: 'Application'):
    """
    Иницилизация модулей
    """
    modules: List[BaseModule] = [
        ScheduleModule(),
        GroupModule()
    ]

    for module in modules:
        module.setup(application)
