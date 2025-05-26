from datetime import datetime
import logging


def setup_logger():
    logger = logging.getLogger("duckling")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s]  %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_filename = f"./outputs/logs/duckling_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(
        log_filename, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger():
    logger = logging.getLogger("duckling")
    logger.setLevel(logging.DEBUG)

    return logger