from telegram.ext import Application

from core.modules.base import BaseModule
from core.modules.group.module import GroupModule
from core.modules.reminder.module import ReminderModule
from core.modules.schedule import ScheduleModule
from core.modules.start.module import StartModule


from core.modules.teacher.module import TeacherModule
from utils.logger import get_logger
from typing import Dict, List, Optional, Type
from dataclasses import dataclass, field


log = get_logger()


@dataclass
class ModuleInfo:
    """Информация о модуле"""

    name: str
    module_class: Type[BaseModule]
    instance: Optional[BaseModule] = None
    dependencies: List[str] = field(default_factory=list)
    initialized: bool = False


class ModuleManager:
    """Менеджер для управления модулями"""

    def __init__(self, application: "Application"):
        self.application = application
        self._modules: Dict[str, ModuleInfo] = {}
        self._initialized = False

    def register_module(
        self,
        module_class: Type["BaseModule"],
        name: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """Регистрация модуля"""
        module_name = name or module_class.__name__

        if module_name in self._modules:
            raise ValueError(f"Module '{module_name}' already registered")

        self._modules[module_name] = ModuleInfo(
            name=module_name, module_class=module_class, dependencies=dependencies or []
        )
        log.debug(f"Module '{module_name}' registered")

    def get_module(self, name: str) -> Optional["BaseModule"]:
        """Получение экземпляра модуля по имени"""
        if name not in self._modules:
            return None
        return self._modules[name].instance

    def get_modules(self) -> Dict[str, "BaseModule"]:
        """Получение всех инициализированных модулей"""
        return {
            name: info.instance
            for name, info in self._modules.items()
            if info.instance is not None
        }

    def initialize_modules(self) -> None:
        """Инициализация всех модулей с учетом зависимостей"""
        if self._initialized:
            return

        log.info("Инициализация модулей")

        # Инициализация в порядке зависимостей
        initialized_count = 0
        total_modules = len(self._modules)

        while initialized_count < total_modules:
            for name, info in self._modules.items():
                if info.initialized:
                    continue

                # Проверяем зависимости
                dependencies_ready = all(
                    dep in self._modules and self._modules[dep].initialized
                    for dep in info.dependencies
                )

                if dependencies_ready:
                    try:
                        # Создаем экземпляр модуля
                        info.instance = info.module_class(
                            application=self.application, module_manager=self
                        )
                        info.initialized = True
                        initialized_count += 1
                        log.info(f"| {name} - установлен")

                    except Exception as e:
                        log.error(f"| {name} - ошибка при инициализации модуля: {e}")
                        log.exception("| Ошибка:")

            # Защита от бесконечного цикла
            if initialized_count == 0:
                log.error(
                    "Не удалось инициализировать модули из-за циклических зависимостей"
                )
                break

        self._initialized = True
        log.info(
            f"Инициализация завершена. Установлено модулей: {initialized_count}/{total_modules}"
        )



def setup_modules(application: 'Application') -> ModuleManager:
    """
    Инициализация модулей с менеджером
    """
    log.info('Инициализация модулей')

    manager = ModuleManager(application)


    modules_config = [
        {'module': StartModule, 'name': 'start', 'dependencies': []},
        {'module': GroupModule, 'name': 'group', 'dependencies': []},
        {'module': TeacherModule, 'name': 'teacher', 'dependencies': []},
        {'module': ScheduleModule, 'name': 'schedule', 'dependencies': []},
        {'module': ReminderModule, 'name': 'reminder', 'dependencies': ['schedule']},
    ]

    for config in modules_config:
        manager.register_module(
            module_class=config['module'],
            name=config['name'],
            dependencies=config['dependencies']
        )

    manager.initialize_modules()

    application.module_manager = manager

    return manager
