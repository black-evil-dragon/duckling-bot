from telegram.ext import Application


from core.session import Session
from utils.logger import setup_logger

import os
import logging


log: 'logging.Logger' = None

class Bot:
    session_manager: 'Session' = None

    def __init__(self, token: str, test_run: bool = False):
        self.token = token
        self.app = Application.builder().token(self.token).build()


        if not test_run:
            #? В Github Actions мы не будем использовать сессии
            self.session_manager: 'Session' = Session()

        self.app.bot_data.update({'session': self.session_manager})

        
    def setup_modules(self, modules_config):
        modules_config(self.app)
        log.info("Модули установлены")
        

    def run(self):
        log.info("Бот запускается...")
        self.app.run_polling()


def main():
    try:
        TOKEN = os.getenv('TOKEN')
        TEST_RUN = os.getenv('TEST_RUN', 'false').lower() == 'true'

        log.debug(f'TEST_RUN: {TEST_RUN}')

        if not TOKEN:
            from utils.config import TOKEN

        bot = Bot(token=TOKEN, test_run=TEST_RUN)
    
        try:
            from core.modules import setup_modules
            bot.setup_modules(setup_modules)

            if TEST_RUN:
                return log.info('Включен режим тестовый запуск')
            
            bot.run()

        except Exception as error:
            return log.error(f'Не удалось загрузить модули: {str(error)}')
        

    except ImportError:
        log.error('Не найден файл конфигурации [./utils/config.py].')
        log.error('| - Создайте файл конфигурации на основе [./utils/config.template.py]')
        return 
    
    


if __name__ == "__main__":
    log = setup_logger()

    main()