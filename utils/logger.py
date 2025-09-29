from logging.handlers import RotatingFileHandler
from dotenv import dotenv_values

import logging


config: dict = dotenv_values(".env")


def setup_logger(max_log_size=10 * 1024 * 1024, backup_count=5):
    """
    Настройка логгера с ротацией логов по размеру.

    Args:
        max_log_size (int): Максимальный размер файла в байтах (по умолчанию 10 МБ).
        backup_count (int): Сколько старых логов хранить (по умолчанию 5).
    """

    logger = logging.getLogger("duckling")

    level = logging.INFO
    if config.get("DEBUG", '0') == '1':
        level = logging.DEBUG
        logger.warning("Установлен режим отладки!")

    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-5s] [%(module)-15s:%(funcName)-20s] %(message)s"
    )

    # Логирование в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Логирование в файл с ротацией
    log_filename = "./outputs/logs/duckling.log"
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=max_log_size,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger():
    """Получение уже настроенного логгера."""
    logger = logging.getLogger("duckling")
    level = logging.INFO

    if config.get("DEBUG", '0') == '1':
        level = logging.DEBUG

    logger.setLevel(level)

    return logger
